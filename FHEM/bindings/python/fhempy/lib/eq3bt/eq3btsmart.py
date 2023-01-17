"""
Support for eq3 Bluetooth Smart thermostats.

All temperatures in Celsius.

To get the current state, update() has to be called for powersaving reasons.
Schedule needs to be requested with query_schedule() before accessing for similar reasons.
"""

# handle: 0x0110, char properties: 0x02, char value handle: 0x0111, uuid: 00002a00-0000-1000-8000-00805f9b34fb
# handle: 0x0120, char properties: 0x02, char value handle: 0x0121, uuid: 00002a01-0000-1000-8000-00805f9b34fb
# handle: 0x0130, char properties: 0x02, char value handle: 0x0131, uuid: 00002a02-0000-1000-8000-00805f9b34fb
# handle: 0x0140, char properties: 0x08, char value handle: 0x0141, uuid: 00002a03-0000-1000-8000-00805f9b34fb
# handle: 0x0150, char properties: 0x02, char value handle: 0x0151, uuid: 00002a04-0000-1000-8000-00805f9b34fb
# handle: 0x0210, char properties: 0x22, char value handle: 0x0211, uuid: 00002a05-0000-1000-8000-00805f9b34fb
# handle: 0x0310, char properties: 0x02, char value handle: 0x0311, uuid: 00002a29-0000-1000-8000-00805f9b34fb
# handle: 0x0320, char properties: 0x02, char value handle: 0x0321, uuid: 00002a24-0000-1000-8000-00805f9b34fb
# handle: 0x0410, char properties: 0x0a, char value handle: 0x0411, uuid: 3fa4585a-ce4a-3bad-db4b-b8df8179ea09
# handle: 0x0420, char properties: 0x1a, char value handle: 0x0421, uuid: d0e8434d-cd29-0996-af41-6c90f4e0eb2a
# handle: 0xff01, char properties: 0x38, char value handle: 0xff02, uuid: e3dd50bf-f7a7-4e99-838e-570a086c666b
# handle: 0xff04, char properties: 0x08, char value handle: 0xff05, uuid: 92e86c7a-d961-4091-b74f-2409e72efe36
# handle: 0xff06, char properties: 0x02, char value handle: 0xff07, uuid: 347f7608-2e2d-47eb-913b-75d4edc4de3b

import asyncio
import codecs
import struct
from datetime import datetime, timedelta
from enum import IntEnum

from construct import Byte

from ..core import bluetoothle
from .structures import AwayDataAdapter, DeviceId, Schedule, Status

PROP_WRITE_HANDLE = "3fa4585a-ce4a-3bad-db4b-b8df8179ea09"
PROP_NTFY_HANDLE = "d0e8434d-cd29-0996-af41-6c90f4e0eb2a"

PROP_ID_QUERY = 0
PROP_ID_RETURN = 1
PROP_INFO_QUERY = 3
PROP_INFO_RETURN = 2
PROP_COMFORT_ECO_CONFIG = 0x11
PROP_OFFSET = 0x13
PROP_WINDOW_OPEN_CONFIG = 0x14
PROP_SCHEDULE_QUERY = 0x20
PROP_SCHEDULE_RETURN = 0x21

PROP_MODE_WRITE = 0x40
PROP_TEMPERATURE_WRITE = 0x41
PROP_COMFORT = 0x43
PROP_ECO = 0x44
PROP_BOOST = 0x45
PROP_LOCK = 0x80

EQ3BT_AWAY_TEMP = 12.0
EQ3BT_MIN_TEMP = 5.0
EQ3BT_MAX_TEMP = 29.5
EQ3BT_OFF_TEMP = 4.5
EQ3BT_ON_TEMP = 30.0


class Mode(IntEnum):
    """Thermostat modes."""

    Unknown = -1
    Closed = 0
    Open = 1
    Auto = 2
    Manual = 3
    Away = 4
    Boost = 5


MODE_NOT_TEMP = [Mode.Unknown, Mode.Closed, Mode.Open]


class TemperatureException(Exception):
    """Temperature out of range error."""

    pass


# pylint: disable=too-many-instance-attributes
class Thermostat:
    """Representation of a EQ3 Bluetooth Smart thermostat."""

    def __init__(
        self, logger, hash, _mac, keep_connection=True, notification_callback=None
    ):
        """Initialize the thermostat."""
        self.logger = logger

        self._target_temperature = 0
        self._mode = Mode.Unknown
        self._valve_state = 0
        self._raw_mode = None

        self._schedule = {}

        self._window_open_temperature = None
        self._window_open_time = None
        self._comfort_temperature = None
        self._eco_temperature = None
        self._temperature_offset = None

        self._away_temp = EQ3BT_AWAY_TEMP
        self._away_duration = timedelta(days=30)
        self._away_end = None

        self._firmware_version = None
        self._device_serial = None

        self._notification_callback = notification_callback

        self._conn = bluetoothle.BluetoothLE(
            self.logger,
            hash,
            _mac,
        )
        self._conn.register_notification_listener(self.handle_notification)

    async def connect(self):
        await self._conn.connect()

    def __str__(self):
        away_end = "no"
        if self.away_end:
            away_end = "end: %s" % self._away_end

        return "[%s] Target %s (mode: %s, away: %s)" % (
            self._conn.mac,
            self.target_temperature,
            self.mode_readable,
            away_end,
        )

    def _verify_temperature(self, temp):
        """Verifies that the temperature is valid.
        :raises TemperatureException: On invalid temperature.
        """
        if temp < self.min_temp or temp > self.max_temp:
            raise TemperatureException(
                "Temperature {} out of range [{}, {}]".format(
                    temp, self.min_temp, self.max_temp
                )
            )

    def parse_schedule(self, data):
        """Parses the device sent schedule."""
        sched = Schedule.parse(data)
        self.logger.debug("Got schedule data for day '%s'", sched.day)

        return sched

    async def disconnect(self):
        await self._conn.disconnect()

    def handle_notification(self, uuid, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        self.logger.debug("Received notification from the device..")

        if data[0] == PROP_INFO_RETURN and data[1] == 1:
            self.logger.debug("Got status: %s" % codecs.encode(data, "hex"))
            status = Status.parse(data)
            self.logger.debug("Parsed status: %s", status)

            self._raw_mode = status.mode
            self._valve_state = status.valve
            self._target_temperature = status.target_temp

            if status.mode.BOOST:
                self._mode = Mode.Boost
            elif status.mode.AWAY:
                self._mode = Mode.Away
                self._away_end = status.away
            elif status.mode.MANUAL:
                if status.target_temp == EQ3BT_OFF_TEMP:
                    self._mode = Mode.Closed
                elif status.target_temp == EQ3BT_ON_TEMP:
                    self._mode = Mode.Open
                else:
                    self._mode = Mode.Manual
            else:
                self._mode = Mode.Auto

            presets = status.presets
            if presets:
                self._window_open_temperature = presets.window_open_temp
                self._window_open_time = presets.window_open_time
                self._comfort_temperature = presets.comfort_temp
                self._eco_temperature = presets.eco_temp
                self._temperature_offset = presets.offset
            else:
                self._window_open_temperature = None
                self._window_open_time = None
                self._comfort_temperature = None
                self._eco_temperature = None
                self._temperature_offset = None

            self.logger.debug("Valve state:      %s", self._valve_state)
            self.logger.debug("Mode:             %s", self.mode_readable)
            self.logger.debug("Target temp:      %s", self._target_temperature)
            self.logger.debug("Away end:         %s", self._away_end)
            self.logger.debug("Window open temp: %s", self._window_open_temperature)
            self.logger.debug("Window open time: %s", self._window_open_time)
            self.logger.debug("Comfort temp:     %s", self._comfort_temperature)
            self.logger.debug("Eco temp:         %s", self._eco_temperature)
            self.logger.debug("Temp offset:      %s", self._temperature_offset)

        elif data[0] == PROP_SCHEDULE_RETURN:
            parsed = self.parse_schedule(data)
            self._schedule[parsed.day] = parsed

        elif data[0] == PROP_ID_RETURN:
            parsed = DeviceId.parse(data)
            self.logger.debug("Parsed device data: %s", parsed)
            self._firmware_version = parsed.version
            self._device_serial = parsed.serial

        else:
            self.logger.debug(
                "Unknown notification %s (%s)", data[0], codecs.encode(data, "hex")
            )
        if self._notification_callback:
            asyncio.create_task(self._notification_callback())

    async def query_id(self):
        """Query device identification information, e.g. the serial number."""
        self.logger.debug("Querying id..")
        value = struct.pack("B", PROP_ID_QUERY)
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    async def update(self):
        """Update the data from the thermostat. Always sets the current time."""
        self.logger.debug("Querying the device..")
        time = datetime.now()
        value = struct.pack(
            "BBBBBBB",
            PROP_INFO_QUERY,
            time.year % 100,
            time.month,
            time.day,
            time.hour,
            time.minute,
            time.second,
        )

        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    async def query_schedule(self, day):
        self.logger.debug("Querying schedule..")

        if day < 0 or day > 6:
            self.logger.error("Invalid day: %s", day)

        value = struct.pack("BB", PROP_SCHEDULE_QUERY, day)

        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def schedule(self):
        """Returns previously fetched schedule.
        :return: Schedule structure or None if not fetched.
        """
        return self._schedule

    async def set_schedule(self, data):
        """Sets the schedule for the given day."""
        value = Schedule.build(data)
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    async def set_target_temperature(self, temperature):
        """Set new target temperature."""
        dev_temp = int(temperature * 2)
        if temperature == EQ3BT_OFF_TEMP or temperature == EQ3BT_ON_TEMP:
            dev_temp |= 0x40
            value = struct.pack("BB", PROP_MODE_WRITE, dev_temp)
        else:
            self._verify_temperature(temperature)
            value = struct.pack("BB", PROP_TEMPERATURE_WRITE, dev_temp)

        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def mode(self):
        """Return the current operation mode"""
        return self._mode

    async def set_mode(self, mode):
        """Set the operation mode."""
        self.logger.debug("Setting new mode: %s", mode)

        if self.mode == Mode.Boost and mode != Mode.Boost:
            self.boost = False

        if mode == Mode.Boost:
            self.boost = True
            return
        elif mode == Mode.Away:
            end = datetime.now() + self._away_duration
            return self.set_away(end, self._away_temp)
        elif mode == Mode.Closed:
            return await self.send_mode(0x40 | int(EQ3BT_OFF_TEMP * 2))
        elif mode == Mode.Open:
            return await self.send_mode(0x40 | int(EQ3BT_ON_TEMP * 2))

        if mode == Mode.Manual:
            temperature = max(
                min(self._target_temperature, self.max_temp), self.min_temp
            )
            return await self.send_mode(0x40 | int(temperature * 2))
        else:
            return await self.send_mode(0)

    @property
    def away_end(self):
        return self._away_end

    async def set_away(self, away_end=None, temperature=EQ3BT_AWAY_TEMP):
        """Sets away mode with target temperature.
        When called without parameters disables away mode."""
        if not away_end:
            self.logger.debug("Disabling away, going to auto mode.")
            return await self.send_mode(0x00)

        self.logger.debug("Setting away until %s, temp %s", away_end, temperature)
        adapter = AwayDataAdapter(Byte[4])
        packed = adapter.build(away_end)

        await self.send_mode(0x80 | int(temperature * 2), packed)

    async def send_mode(self, mode, payload=None):
        value = struct.pack("BB", PROP_MODE_WRITE, mode)
        if payload:
            value += payload
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def mode_readable(self):
        """Return a readable representation of the mode.."""
        ret = ""
        mode = self._raw_mode
        if mode is None:
            return "unknown"

        if mode.MANUAL:
            ret = "manual"
            if self.target_temperature < self.min_temp:
                ret += " off"
            elif self.target_temperature >= self.max_temp:
                ret += " on"
            else:
                ret += " (%sC)" % self.target_temperature
        else:
            ret = "auto"

        if mode.AWAY:
            ret += " holiday"
        if mode.BOOST:
            ret += " boost"
        if mode.DST:
            ret += " dst"
        if mode.WINDOW:
            ret += " window"
        if mode.LOCKED:
            ret += " locked"
        if mode.LOW_BATTERY:
            ret += " low battery"

        return ret

    @property
    def boost(self):
        """Returns True if the thermostat is in boost mode."""
        return self.mode == Mode.Boost

    async def set_boost(self, boost):
        """Sets boost mode."""
        self.logger.debug("Setting boost mode: %s", boost)
        value = struct.pack("BB", PROP_BOOST, bool(boost))
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def valve_state(self):
        """Returns the valve state. Probably reported as percent open."""
        return self._valve_state

    @property
    def window_open(self):
        """Returns True if the thermostat reports a open window
        (detected by sudden drop of temperature)"""
        return self._raw_mode and self._raw_mode.WINDOW

    async def window_open_config(self, temperature, duration):
        """Configures the window open behavior. The duration is specified in
        5 minute increments."""
        self.logger.debug(
            "Window open config, temperature: %s duration: %s", temperature, duration
        )
        self._verify_temperature(temperature)
        if duration < 0 and duration > 3600:
            raise ValueError

        value = struct.pack(
            "BBB",
            PROP_WINDOW_OPEN_CONFIG,
            int(temperature * 2),
            int(duration / 300),
        )
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def window_open_temperature(self):
        """The temperature to set when an open window is detected."""
        return self._window_open_temperature

    @property
    def window_open_time(self):
        """Timeout to reset the thermostat after an open window is detected."""
        return self._window_open_time

    @property
    def locked(self):
        """Returns True if the thermostat is locked."""
        return self._raw_mode and self._raw_mode.LOCKED

    async def set_locked(self, lock):
        """Locks or unlocks the thermostat."""
        self.logger.debug("Setting the lock: %s", lock)
        value = struct.pack("BB", PROP_LOCK, bool(lock))
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def low_battery(self):
        """Returns True if the thermostat reports a low battery."""
        return self._raw_mode and self._raw_mode.LOW_BATTERY

    async def temperature_presets(self, comfort, eco):
        """Set the thermostats preset temperatures comfort (sun) and
        eco (moon)."""
        self.logger.debug(
            "Setting temperature presets, comfort: %s eco: %s", comfort, eco
        )
        self._verify_temperature(comfort)
        self._verify_temperature(eco)
        value = struct.pack(
            "BBB", PROP_COMFORT_ECO_CONFIG, int(comfort * 2), int(eco * 2)
        )
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def comfort_temperature(self):
        """Returns the comfort temperature preset of the thermostat."""
        return self._comfort_temperature

    @property
    def eco_temperature(self):
        """Returns the eco temperature preset of the thermostat."""
        return self._eco_temperature

    @property
    def temperature_offset(self):
        """Returns the thermostat's temperature offset."""
        return self._temperature_offset

    async def set_temperature_offset(self, offset):
        """Sets the thermostat's temperature offset."""
        self.logger.debug("Setting offset: %s", offset)
        # [-3,5 .. 0  .. 3,5 ]
        # [00   .. 07 .. 0e ]
        if offset < -3.5 or offset > 3.5:
            raise TemperatureException("Invalid value: %s" % offset)

        current = -3.5
        values = {}
        for i in range(15):
            values[current] = i
            current += 0.5

        value = struct.pack("BB", PROP_OFFSET, values[offset])
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    async def activate_comfort(self):
        """Activates the comfort temperature."""
        value = struct.pack("B", PROP_COMFORT)
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    async def activate_eco(self):
        """Activates the comfort temperature."""
        value = struct.pack("B", PROP_ECO)
        await self._conn.write_gatt_char(PROP_WRITE_HANDLE, value)

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return EQ3BT_MIN_TEMP

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return EQ3BT_MAX_TEMP

    @property
    def firmware_version(self):
        """Return the firmware version."""
        return self._firmware_version

    @property
    def device_serial(self):
        """Return the device serial number."""
        return self._device_serial
