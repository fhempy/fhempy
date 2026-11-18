"""Bluetooth fitness devices with the standard profiles: heart rate straps
(Polar, Garmin, Wahoo, ...), power meters, speed/cadence sensors and smart
trainers, treadmills and rowers with the Fitness Machine Service (Wahoo KICKR,
Elite, Tacx, ...).

The device is only connected while it advertises: a chest strap only when it
is worn, a trainer while it's awake. No scanning of its own, the shared
Bluetooth scan (local adapters and ESPHome Bluetooth proxies) reports the
advertisements.
"""

import asyncio
import re
import time

from bleak.exc import BleakError

from .. import fhem, generic
from ..core import ble_scanner, bluetoothle
from . import parser
from .workout import Workout, heart_rate_zone

USAGE = "Usage: define polar_h10 fhempy ble_fitness <MAC>"
MAC_PATTERN = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")

# don't try again right away after a failed connection attempt
CONNECT_RETRY = 30
CONNECT_TIMEOUT = 20
# at most one reading update per second, power meters send up to 4 per second
UPDATE_INTERVAL = 1.0
# a workout ends this long after the device disconnected ...
WORKOUT_END_DISCONNECTED = 120
# ... or this long without heart rate, power or cadence
WORKOUT_END_IDLE = 300
# readings set to 0 when the device disconnects
LIVE_READINGS = ("heart_rate", "power", "cadence", "speed")
DEFAULT_WHEEL_CIRCUMFERENCE = 2105
# decimals of the readings: the same value always has the same text, FHEM
# would see 0 and 0.0 as a change and trigger an event
DECIMALS = {
    "heart_rate": 0,
    "power": 0,
    "cadence": 0,
    "speed": 1,
    "resistance": 0,
    "incline": 1,
    "stroke_rate": 1,
    "balance": 1,
}
# values of the parsers which become readings (calories only for the workout)
MEASUREMENTS = (
    "heart_rate",
    "power",
    "cadence",
    "speed",
    "distance",
    "resistance",
    "incline",
    "stroke_rate",
    "strokes",
    "balance",
    "calories",
)


def _positive(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("expected a number") from None
    if number <= 0:
        raise ValueError("expected a positive number")
    return number


def _optional_positive(value):
    if value in (None, ""):
        return None
    return _positive(value)


def _target_power(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError("expected watts (whole number)") from None
    if not 0 <= number <= 2000:
        raise ValueError("expected 0 to 2000 W")
    return number


def _grade(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("expected a grade in %") from None
    if not -20 <= number <= 20:
        raise ValueError("expected -20 to 20 %")
    return number


TRAINER_SETS = {
    "target_power": {
        "args": ["watts"],
        "params": {"watts": {"format": _target_power}},
        "options": "slider,0,5,500",
        "help": "<b>target_power</b><br>ERG mode: the trainer holds this power (W).",
    },
    "grade": {
        "args": ["grade"],
        "params": {"grade": {"format": _grade}},
        "options": "slider,-10,0.5,15,1",
        "help": "<b>grade</b><br>Simulation mode: ride a slope of this grade (%).",
    },
    "release_control": {
        "help": "<b>release_control</b><br>Ends ERG/simulation mode, other apps "
        "(Zwift, ...) can control the trainer again.",
    },
}


def normalize(values):
    """Rounds the live values to their fixed number of decimals."""
    for reading, decimals in DECIMALS.items():
        value = values.get(reading)
        if value is None:
            continue
        if decimals:
            values[reading] = round(float(value), decimals)
        else:
            values[reading] = int(round(value))
    return values


class ble_fitness(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._conn = None
        self._mac = None
        self._scanner = None
        self._connect_task = None
        self._retry_after = 0
        self._subscribed = set()
        self._has_control = False
        self._control_granted = False
        self._control_lock = asyncio.Lock()
        self._pending = {}
        self._last_flush = 0
        self._flush_handle = None
        self._crank = parser.RevolutionRate(16, 1024)
        self._wheel = None
        self._workout = None
        self._last_active = 0
        self._workout_end_handle = None
        self._readings = {}

    @staticmethod
    def validate_define(args, argsh):
        if len(args) != 4 or not MAC_PATTERN.match(args[3]):
            return USAGE
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        error = self.validate_define(args, argsh)
        if error:
            return error
        await super().Define(hash, args, argsh)

        attr_config = {
            "max_heart_rate": {
                "default": "",
                "format": _optional_positive,
                "help": "Maximum heart rate for the zones, default 208 - 0.7 * age.",
            },
            "age": {
                "default": "",
                "format": _optional_positive,
                "help": "Age in years, for the maximum heart rate and the calories.",
            },
            "weight": {
                "default": "",
                "format": _optional_positive,
                "help": "Weight in kg, for the calories from the heart rate.",
            },
            "sex": {
                "default": "male",
                "options": "male,female",
                "help": "For the calories from the heart rate.",
            },
            "wheel_circumference": {
                "default": DEFAULT_WHEEL_CIRCUMFERENCE,
                "format": _positive,
                "help": "Wheel circumference in mm for the speed of speed sensors "
                "and power meters, default 2105 (700x25C).",
            },
        }
        await self.set_attr_config(attr_config)

        self._mac = args[3].upper()
        self.hash["MAC"] = self._mac
        # remembered: the trainer sets are there before it is connected
        trainer = await fhem.ReadingsVal(self.hash["NAME"], "trainer_control", "")
        await self._update_sets(trainer not in ("", "none"))

        self._conn = bluetoothle.BluetoothLE(
            self.logger, self.hash, self._mac, reconnect=False
        )
        self._conn.register_connection_established_listener(self._connected)
        self._conn.register_disconnect_listener(self._disconnected)

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "off", 1)
        self._scanner = ble_scanner.BleScanner.get_instance(self.logger)
        self._scanner.add_callback(self._advertisement)

    async def Undefine(self, hash):
        if self._scanner is not None:
            self._scanner.remove_callback(self._advertisement)
            self._scanner = None
        for handle in (self._flush_handle, self._workout_end_handle):
            if handle is not None:
                handle.cancel()
        self._flush_handle = self._workout_end_handle = None
        await super().Undefine(hash)
        if self._conn is not None:
            try:
                await self._conn.disconnect()
            except Exception:
                self.logger.exception("Failed to disconnect")

    async def _update_sets(self, trainer):
        self._has_control = trainer
        await self.set_set_config(dict(TRAINER_SETS) if trainer else {})

    # --- connection ---

    def _advertisement(self, device, advertisement):
        if device.address.upper() != self._mac or self._conn is None:
            return
        if self._conn.is_connected:
            return
        if self._connect_task is not None and not self._connect_task.done():
            return
        if time.monotonic() < self._retry_after:
            return
        self._connect_task = self.create_async_task(self._connect())

    async def _connect(self):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connecting", 1)
        try:
            await self._conn.connect_once(CONNECT_TIMEOUT, max_retries=1)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.logger.debug("Connection failed", exc_info=True)
        if not self._conn.is_connected:
            self._retry_after = time.monotonic() + CONNECT_RETRY
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "off", 1)

    async def _connected(self):
        client = self._conn.client
        self._subscribed = set()
        self._control_granted = False
        characteristics = {}
        for service in client.services:
            for characteristic in service.characteristics:
                characteristics[characteristic.uuid.lower()] = characteristic

        for uuid in self._measurement_sources(characteristics):
            await self._start_notify(client, uuid)

        await self._setup_battery(client, characteristics.get(parser.BATTERY_LEVEL))
        control = self._can_notify(
            characteristics.get(parser.FITNESS_MACHINE_CONTROL_POINT)
        )
        if control:
            await self._start_notify(client, parser.FITNESS_MACHINE_CONTROL_POINT)
        if control != self._has_control:
            await self._update_sets(control)
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "trainer_control",
            "available" if control else "none",
            1,
        )
        if self._workout_end_handle is not None:
            # back within WORKOUT_END_DISCONNECTED, the workout goes on
            self._workout_end_handle.cancel()
            self._workout_end_handle = None
        await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)

    def _measurement_sources(self, characteristics):
        """The measurement characteristics to subscribe. Trainers like the
        KICKR send power and cadence via Cycling Power and the Fitness
        Machine Service at the same time, the values differ slightly (cadence
        from the crank revolutions vs. the trainer's own cadence): only the
        Fitness Machine data is used then, otherwise the readings alternate."""
        available = [
            uuid
            for uuid in parser.PARSERS
            if self._can_notify(characteristics.get(uuid))
        ]
        if any(uuid in parser.FITNESS_MACHINE_DATA for uuid in available):
            available = [
                uuid for uuid in available if uuid not in parser.CYCLING_SENSOR_DATA
            ]
        return available

    async def _setup_battery(self, client, battery):
        if battery is None:
            return
        try:
            data = await client.read_gatt_char(parser.BATTERY_LEVEL)
            await self._battery(data)
        except (BleakError, asyncio.TimeoutError):
            self.logger.debug("Failed to read the battery", exc_info=True)
        if self._can_notify(battery):
            await self._start_notify(client, parser.BATTERY_LEVEL)

    @staticmethod
    def _can_notify(characteristic):
        if characteristic is None:
            return False
        properties = characteristic.properties
        return "notify" in properties or "indicate" in properties

    async def _start_notify(self, client, uuid):
        try:
            await client.start_notify(uuid, self._notification)
            self._subscribed.add(uuid)
        except (BleakError, asyncio.TimeoutError):
            self.logger.warning(f"Failed to subscribe to {uuid}", exc_info=True)

    async def _disconnected(self, client):
        self._control_granted = False
        self._retry_after = 0
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "off")
            for reading in LIVE_READINGS:
                if reading in self._readings:
                    value = normalize({reading: 0})[reading]
                    self._readings[reading] = value
                    await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)
        if self._workout is not None and self._workout_end_handle is None:
            loop = asyncio.get_running_loop()
            self._workout_end_handle = loop.call_later(
                WORKOUT_END_DISCONNECTED, self._workout_timeout
            )

    # --- measurements ---

    def _notification(self, sender, data):
        uuid = str(getattr(sender, "uuid", sender)).lower()
        try:
            if uuid == parser.BATTERY_LEVEL:
                self.create_async_task(self._battery(data))
                return
            if uuid == parser.FITNESS_MACHINE_CONTROL_POINT:
                self._control_indication(data)
                return
            measurement = parser.PARSERS.get(uuid)
            if measurement is None:
                return
            self._measurement(uuid, measurement(data))
        except ValueError as exc:
            self.logger.debug(f"Ignored notification of {uuid}: {exc}")

    async def _battery(self, data):
        if not data:
            return
        level = data[0]
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "batteryPercent", level)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "battery", "low" if level <= 15 else "ok"
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    def _wheel_rate(self, uuid):
        # power meters count the wheel time in 1/2048 s, CSC sensors in 1/1024 s
        unit = 2048 if uuid == parser.CYCLING_POWER_MEASUREMENT else 1024
        if self._wheel is None or self._wheel[0] != unit:
            self._wheel = (unit, parser.RevolutionRate(32, unit))
        return self._wheel[1]

    def _measurement(self, uuid, data):
        now = time.monotonic()
        values = {key: data[key] for key in MEASUREMENTS if key in data}
        self._revolutions(uuid, data, values, now)
        if uuid == parser.HEART_RATE_MEASUREMENT:
            self._heart_rate_details(data, values)
        normalize(values)
        self._track_workout(now, values)
        self._pending.update(values)
        self._schedule_flush(now)

    def _revolutions(self, uuid, data, values, now):
        """Cadence and speed of power meters and speed/cadence sensors."""
        if "crank_revolutions" in data and "cadence" not in values:
            rpm = self._crank.update(data["crank_revolutions"], data["crank_time"], now)
            if rpm is not None:
                values["cadence"] = round(rpm)
        if "wheel_revolutions" in data and "speed" not in values:
            rpm = self._wheel_rate(uuid).update(
                data["wheel_revolutions"], data["wheel_time"], now
            )
            if rpm is not None:
                circumference = getattr(
                    self, "_attr_wheel_circumference", DEFAULT_WHEEL_CIRCUMFERENCE
                )
                values["speed"] = round(rpm * circumference * 60 / 1e6, 1)

    @staticmethod
    def _heart_rate_details(data, values):
        if "sensor_contact" in data:
            values["sensor_contact"] = "yes" if data["sensor_contact"] else "no"
            if not data["sensor_contact"]:
                # the strap sends 0 or old values without skin contact
                values["heart_rate"] = 0
        if data.get("rr"):
            values["rr"] = data["rr"]
            values["rr_interval"] = data["rr"][-1]

    def _profile(self):
        age = getattr(self, "_attr_age", None)
        max_heart_rate = getattr(self, "_attr_max_heart_rate", None)
        if not max_heart_rate and age:
            max_heart_rate = round(208 - 0.7 * age)
        return {
            "max_heart_rate": max_heart_rate,
            "age": age,
            "weight": getattr(self, "_attr_weight", None),
            "sex": getattr(self, "_attr_sex", "male"),
        }

    def _track_workout(self, now, values):
        active = any(values.get(key) for key in ("heart_rate", "power", "cadence"))
        if active:
            self._last_active = now
        if self._workout is None:
            if not active:
                return
            self._workout = Workout(now)
            self._pending["workout"] = "active"
        profile = self._profile()
        self._workout.add(now, values, profile)
        hrv = self._workout.hrv
        if hrv is not None:
            values["hrv"] = hrv
        if values.get("heart_rate") and profile["max_heart_rate"]:
            values["heart_rate_zone"] = heart_rate_zone(
                values["heart_rate"], profile["max_heart_rate"]
            )
        if not active and now - self._last_active >= WORKOUT_END_IDLE:
            self.create_async_task(self._finish_workout())

    def _schedule_flush(self, now):
        if self._flush_handle is not None:
            return
        wait = self._last_flush + UPDATE_INTERVAL - now
        if wait <= 0:
            self._flush()
            return
        self._flush_handle = asyncio.get_running_loop().call_later(wait, self._flush)

    def _flush(self):
        self._flush_handle = None
        self._last_flush = time.monotonic()
        values, self._pending = self._pending, {}
        if values:
            self.create_async_task(self._write(values))

    def _state(self):
        parts = []
        if "power" in self._readings:
            parts.append(f"{self._readings['power']} W")
        if self._readings.get("heart_rate"):
            parts.append(f"{self._readings['heart_rate']} bpm")
        if not parts and self._readings.get("speed"):
            parts.append(f"{self._readings['speed']} km/h")
        return ", ".join(parts) if parts else "connected"

    async def _write(self, values):
        values.pop("rr", None)
        values.pop("calories", None)
        if "distance" in values:
            values["distance"] = round(values["distance"] / 1000, 2)
        self._readings.update(values)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for reading, value in values.items():
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
            if self._conn is not None and self._conn.is_connected:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "state", self._state()
                )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    # --- workout ---

    def _workout_timeout(self):
        self._workout_end_handle = None
        self.create_async_task(self._finish_workout())

    async def _finish_workout(self):
        workout, self._workout = self._workout, None
        if workout is None:
            return
        summary = workout.summary()
        summary["workout"] = "finished"
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for reading, value in summary.items():
                await fhem.readingsBulkUpdate(self.hash, reading, value)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    # --- trainer control (Fitness Machine Control Point) ---

    def _control_indication(self, data):
        response = parser.control_response(data)
        if response is None:
            return
        request, result = response
        if request == parser.CONTROL_REQUEST[0]:
            self._control_granted = result == "ok"
        self.create_async_task(
            fhem.readingsSingleUpdateIfChanged(self.hash, "trainer_control", result, 1)
        )

    async def _control(self, command):
        if not self._has_control:
            return "This device has no Fitness Machine control point"
        if self._conn is None or not self._conn.is_connected:
            return "Not connected, wake the trainer up (pedal) and try again"
        client = self._conn.client
        uuid = parser.FITNESS_MACHINE_CONTROL_POINT
        try:
            async with self._control_lock:
                if not self._control_granted:
                    await client.write_gatt_char(
                        uuid, parser.CONTROL_REQUEST, response=True
                    )
                    self._control_granted = True
                await client.write_gatt_char(uuid, command, response=True)
        except (BleakError, asyncio.TimeoutError) as exc:
            self._control_granted = False
            return f"Failed to control the trainer: {exc}"
        return None

    async def set_target_power(self, hash, params):
        error = await self._control(parser.control_target_power(params["watts"]))
        if error:
            return error
        await fhem.readingsSingleUpdate(hash, "target_power", params["watts"], 1)
        return None

    async def set_grade(self, hash, params):
        error = await self._control(parser.control_simulation(params["grade"]))
        if error:
            return error
        await fhem.readingsSingleUpdate(hash, "grade", params["grade"], 1)
        return None

    async def set_release_control(self, hash, params):
        error = await self._control(parser.CONTROL_RESET)
        self._control_granted = False
        if error:
            return error
        await fhem.readingsBeginUpdate(hash)
        try:
            await fhem.readingsBulkUpdate(hash, "target_power", "-")
            await fhem.readingsBulkUpdate(hash, "grade", "-")
        finally:
            await fhem.readingsEndUpdate(hash, 1)
        return None
