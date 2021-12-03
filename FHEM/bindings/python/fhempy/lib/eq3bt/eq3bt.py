import asyncio
import concurrent.futures
import functools
import random
import time
from datetime import datetime
from enum import IntEnum

from dbus import DBusException

from .. import fhem, utils
from .. import generic
from . import eq3btsmart as eq3
from .connection import BTLEConnection


class Mode(IntEnum):
    """Thermostat modes."""

    Unknown = -1
    Closed = 0
    Open = 1
    Auto = 2
    Manual = 3
    Away = 4
    Boost = 5


# TODO set schedules
# TODO set windowOpen, windowOpenTime, eco/comfortTemperature


class eq3bt(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_list = {
            "keep_connected": {
                "default": "on",
                "format": "str",
                "options": "on,off",
                "help": "On...keeps bluetooth low energy connection active which makes commands to be executed immediately",
            }
        }
        self.set_attr_config(attr_list)

        set_list_conf = {
            "on": {},
            "off": {},
            "desiredTemperature": {
                "args": ["target_temp"],
                "options": "slider,4.5,0.5,30,1",
            },
            "updateStatus": {},
            "boost": {
                "args": ["target_state"],
                "options": "on,off",
                "help": "Activate boost for 300s",
            },
            "mode": {"args": ["target_mode"], "options": "manual,automatic"},
            "eco": {},
            "comfort": {},
            "childlock": {"args": ["target_state"], "options": "on,off"},
            "resetConsumption": {
                "args": ["cons_var"],
                "options": "all,consumption,consumptionToday,consumptionYesterday",
            },
            "temperatureOffset": {
                "args": ["offset"],
                "params": {"offset": {"format": "float"}},
                "options": "slider,-3.5,0.5,3.5,1",
            },
            "windowOpenTemperature": {
                "args": ["temp"],
                "params": {"temp": {"format": "float"}},
                "options": "slider,5,0.5,30,1",
            },
            "windowOpenTime": {
                "args": ["minutes"],
                "params": {"minutes": {"format": "int"}},
                "options": "slider,0,5,60",
            },
            "ecoTemperature": {
                "args": ["temp"],
                "params": {"temp": {"format": "float"}},
                "options": "slider,4.5,0.5,30,1",
            },
            "comfortTemperature": {
                "args": ["temp"],
                "params": {"temp": {"format": "float"}},
                "options": "slider,4.5,0.5,30,1",
            },
        }
        self.set_set_config(set_list_conf)

        self._last_update = 0
        self._mac = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self.hash = hash
        if len(args) < 4:
            return "Usage: define eq3_livingroom fhempy eq3bt <MAC>"
        self._mac = args[3]
        self.hash["MAC"] = self._mac
        self.logger.info(f"Define: eq3bt {self._mac}")

        icon = await fhem.AttrVal(self.hash["NAME"], "icon", "noicon")
        if icon == "noicon":
            await fhem.CommandAttr(
                self.hash, self.hash["NAME"] + " icon sani_heating_temp"
            )
        await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", "offline", 1)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connecting", 1)

        # handle missing dbus configuration
        try:
            self.thermostat = FhemThermostat(
                self.logger,
                self._mac,
                keep_connection=self._attr_keep_connected == "on",
            )
        except DBusException:
            dbus_conf_err = (
                "Please add following configuration to /etc/dbus-1/system.d/bluetooth.conf:\n"
                '<policy user="fhem">\n'
                '    <allow own="org.bluez"/>\n'
                '    <allow send_destination="org.bluez"/>\n'
                '    <allow send_interface="org.bluez.GattCharacteristic1"/>\n'
                '    <allow send_interface="org.bluez.GattDescriptor1"/>\n'
                '    <allow send_interface="org.freedesktop.DBus.ObjectManager"/>\n'
                '    <allow send_interface="org.freedesktop.DBus.Properties"/>\n'
                "</policy>\n\n"
                "ATTENTION: On remote device change the user account above to the one which runs fhempy (e.g. pi)\n\n"
                "Restart dbus afterwards: sudo systemctl restart dbus"
            )
            self.logger.error(dbus_conf_err)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "state", dbus_conf_err, 1
            )
            return dbus_conf_err

        self.create_async_task(self.check_online())
        self.create_async_task(self.consumption_rotate())
        return ""

    def seconds_till_midnight(self):
        """Get the number of seconds until midnight."""
        n = datetime.now()
        return (
            ((24 - n.hour - 1) * 60 * 60) + ((60 - n.minute - 1) * 60) + (60 - n.second)
        )

    async def consumption_rotate(self):
        while True:
            await asyncio.sleep(self.seconds_till_midnight())
            consumption = float(
                await fhem.ReadingsVal(self.hash["NAME"], "consumptionToday", "0")
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "consumptionYesterday", consumption, 1
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "consumptionToday", "0", 1
            )

    async def set_resetConsumption(self, hash, params):
        cons_var = params["cons_var"]
        if cons_var == "all":
            await fhem.readingsSingleUpdateIfChanged(self.hash, "consumption", 0, 1)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "consumptionYesterday", 0, 1
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "consumptionToday", 0, 1
            )
        else:
            await fhem.readingsSingleUpdateIfChanged(self.hash, cons_var, 0, 1)

    async def set_attr_keep_connected(self, hash):
        self.thermostat.set_keep_connected(self._attr_keep_connected == "on")

    async def check_online(self):
        waittime = 300
        if self._attr_keep_connected == "on":
            waittime = 60
        await asyncio.sleep(int(random.random() * 100))
        while True:
            try:
                if time.time() - self._last_update > (waittime * 4):
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "presence", "offline", 1
                    )
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "update", 1
                    )
                await self.update_all()
            except Exception:
                self.logger.error(f"Failed to update, retry in {waittime}s")
            await asyncio.sleep(waittime)

    async def update_all(self):
        self.logger.debug("start update_all")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await asyncio.get_event_loop().run_in_executor(
                pool, functools.partial(self.thermostat.update_all)
            )
        await self.update_all_readings()

    async def update_all_readings(self):
        await self.update_readings()
        await self.update_id_readings()
        await self.update_schedule_readings()

    async def update_readings(self):
        old_valve_pos = float(
            await fhem.ReadingsVal(self.hash["NAME"], "valvePosition", "0")
        )
        old_consumption = float(
            await fhem.ReadingsVal(self.hash["NAME"], "consumption", "0")
        )
        old_consumption_today = float(
            await fhem.ReadingsVal(self.hash["NAME"], "consumptionToday", "0")
        )
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "battery", self.thermostat.battery
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "boost", self.thermostat.boost
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "childlock", self.thermostat.locked
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "desiredTemperature", self.thermostat.target_temperature
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "ecoTemperature", self.thermostat.eco_temperature
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "temperatureOffset", self.thermostat.temperature_offset
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "comfortTemperature", self.thermostat.comfort_temperature
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "mode", self.thermostat.fhem_mode
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "state", self.thermostat.state
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "completeState", self.thermostat.mode_readable
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "valvePosition", self.thermostat.valve_state
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "awayEnd", self.thermostat.away_end
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "windowOpen", self.thermostat.window_open
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "windowOpenTemperature", self.thermostat.window_open_temperature
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "windowOpenTime", self.thermostat.window_open_time
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, "presence", "online")
        if (time.time() - self._last_update) < 400:
            consumption_diff = (
                (old_valve_pos + self.thermostat.valve_state)
                / 2
                / 100
                * (time.time() - self._last_update)
                / 60
            )
        else:
            consumption_diff = 0
        new_consumption = round(old_consumption + consumption_diff, 2)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "consumption", new_consumption
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "consumptionToday",
            round(old_consumption_today + consumption_diff, 2),
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        self._last_update = time.time()

    async def update_id_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "firmware", self.thermostat.firmware_version
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "serialNumber", self.thermostat.device_serial
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_schedule_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        for day in self.thermostat.schedule.keys():
            reading = f"schedule_{day}_1"
            if self.thermostat.schedule[day].base_temp == 0 or isinstance(
                self.thermostat.schedule[day].next_change_at, int
            ):
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, "-")
                last_change = "00:00"
            else:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash,
                    reading,
                    f"00:00 - {self.thermostat.schedule[day].next_change_at.strftime('%H:%M')}: {self.thermostat.schedule[day].base_temp}",
                )
                last_change = self.thermostat.schedule[day].next_change_at.strftime(
                    "%H:%M"
                )
            last_schedule = False
            for h in range(0, 6):
                reading = f"schedule_{day}_{h+2}"
                if (
                    h == 6
                    or self.thermostat.schedule[day].hours[h].target_temp == 0
                    or isinstance(
                        self.thermostat.schedule[day].hours[h].next_change_at, int
                    )
                    or last_schedule
                ):
                    if last_schedule:
                        await fhem.readingsBulkUpdateIfChanged(self.hash, reading, "-")
                    else:
                        value = f"{last_change} - 00:00: {self.thermostat.schedule[day].base_temp}"
                        await fhem.readingsBulkUpdateIfChanged(
                            self.hash, reading, value
                        )
                    last_schedule = True
                else:
                    value = f"{last_change} - {self.thermostat.schedule[day].hours[h].next_change_at.strftime('%H:%M')}: {self.thermostat.schedule[day].hours[h].target_temp}"
                    last_change = (
                        self.thermostat.schedule[day]
                        .hours[h]
                        .next_change_at.strftime("%H:%M")
                    )
                    await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_and_update(self, fct):
        await utils.run_blocking(fct)
        await self.update_readings()

    def string_to_seconds(self, timestr):
        ftr = [3600, 60, 1]
        return sum([a * b for a, b in zip(ftr, map(int, timestr.split(":")))])

    # SET Functions BEGIN
    async def set_on(self, hash, params):
        self.create_async_task(
            self.set_and_update(
                functools.partial(self.thermostat.set_target_temperature, 30)
            )
        )

    async def set_off(self, hash, params):
        self.create_async_task(
            self.set_and_update(
                functools.partial(self.thermostat.set_target_temperature, 4.5)
            )
        )

    async def set_desiredTemperature(self, hash, params):
        temp = float(params["target_temp"])
        self.create_async_task(
            self.set_and_update(
                functools.partial(self.thermostat.set_target_temperature, temp)
            )
        )

    async def set_ecoTemperature(self, hash, params):
        comfort_temp = float(
            await fhem.ReadingsVal(self.hash["NAME"], "comfortTemperature", "17.0")
        )
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_temperature_presets,
                    comfort_temp,
                    params["temp"],
                )
            )
        )

    async def set_comfortTemperature(self, hash, params):
        eco_temp = float(
            await fhem.ReadingsVal(self.hash["NAME"], "ecoTemperature", "15.0")
        )
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_temperature_presets, params["temp"], eco_temp
                )
            )
        )

    async def set_temperatureOffset(self, hash, params):
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_temperature_offset, params["offset"]
                )
            )
        )

    async def set_windowOpenTemperature(self, hash, params):
        duration = await fhem.ReadingsVal(
            self.hash["NAME"], "windowOpenTime", "0:15:00"
        )
        duration_sec = self.string_to_seconds(duration)
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_window_open_config,
                    params["temp"],
                    duration_sec,
                )
            )
        )

    async def set_windowOpenTime(self, hash, params):
        temp = await fhem.ReadingsVal(self.hash["NAME"], "windowOpenTemperature", "5")
        temp = float(temp)
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_window_open_config, temp, params["minutes"] * 60
                )
            )
        )

    async def set_updateStatus(self, hash, params):
        self.create_async_task(self.update_all())

    async def set_boost(self, hash, params):
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_boost, params["target_state"] == "on"
                )
            )
        )

    async def set_mode(self, hash, params):
        target_mode = params["target_mode"]
        if target_mode == "automatic":
            target_mode = eq3.Mode.Auto
        else:
            target_mode = eq3.Mode.Manual
        self.create_async_task(
            self.set_and_update(
                functools.partial(self.thermostat.set_fhem_mode, target_mode)
            )
        )

    async def set_eco(self, hash, params):
        self.create_async_task(
            self.set_and_update(functools.partial(self.thermostat.activate_eco))
        )

    async def set_comfort(self, hash, params):
        self.create_async_task(
            self.set_and_update(functools.partial(self.thermostat.activate_comfort))
        )

    async def set_childlock(self, hash, params):
        self.create_async_task(
            self.set_and_update(
                functools.partial(
                    self.thermostat.set_locked, params["target_state"] == "on"
                )
            )
        )

    # SET Functions END


class FhemThermostat(eq3.Thermostat):
    def __init__(self, logger, mac, keep_connection):
        self.logger = logger
        self._keep_conection = keep_connection
        super(FhemThermostat, self).__init__(mac, BTLEConnection, keep_connection=True)

    def set_keep_connection(self, new_state):
        self.set_keep_connected(new_state)

    def update_all(self):
        super().update()
        super().query_id()
        for day in range(0, 6):
            super().query_schedule(day)

    def set_temperature_presets(self, comfort_temp, eco_temp):
        self.temperature_presets(comfort_temp, eco_temp)

    def set_temperature_offset(self, temp):
        self.temperature_offset = temp

    def set_window_open_config(self, temperature, duration):
        self.window_open_config(temperature, duration)

    def set_target_temperature(self, temp):
        self.target_temperature = temp

    def set_boost(self, state):
        self.boost = state

    def set_locked(self, state):
        self.locked = state

    def set_fhem_mode(self, mode):
        self.mode = mode

    @property
    def fhem_mode(self):
        if self._mode == Mode.Boost:
            return "boost"
        elif self._mode == Mode.Away:
            return "away"
        elif self._mode == Mode.Closed:
            return "manual"
        elif self._mode == Mode.Open:
            return "manual"
        elif self._mode == Mode.Manual:
            return "manual"
        elif self._mode == Mode.Auto:
            return "automatic"

    @property
    def state(self):
        if self._mode == Mode.Boost:
            return "boost"
        elif self._mode == Mode.Away:
            return "away"
        elif self._mode == Mode.Closed:
            return "off"
        elif self._mode == Mode.Open:
            return "on"
        elif self._mode == Mode.Manual:
            return "manual"
        elif self._mode == Mode.Auto:
            return "automatic"

    @property
    def battery(self):
        if self.low_battery:
            return "low"
        return "ok"
