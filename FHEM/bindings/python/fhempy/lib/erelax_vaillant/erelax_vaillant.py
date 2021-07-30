from __future__ import annotations

import asyncio
import functools

from .. import fhem, utils
from ..generic import FhemModule

from pyvaillant import ClientAuth, VaillantThermostatData


class erelax_vaillant(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        unknown_key = "thisisnotmagic012345678901234567"
        self.unknown_code = utils.decrypt_string(
            (
                "eJwVwdsOgiAAANAvalNLrEcJM5chh"
                "RvOF6dZaBcCLBG/vnUOD/8gr1RNJ"
                "iNsgTOZrebk5njuM7Es\nlo4SBja"
                "S+yoZ+YHh61CIsF/qvE6Fsmr30sh"
                "FXeCt+WNoiAZ9R++EGRmXZ5pH+zh"
                "tWbjxzZa+JwjQ\nFGFEmvJ7vFgI3"
                "NYLPgs869OIiU9/UCcvrg==\n"
            ),
            unknown_key,
        )

        attr_config = {
            "update_interval": {
                "default": 300,
                "format": "int",
                "help": "Change interval, default is 300.",
            }
        }
        self.set_attr_config(attr_config)

        set_config = {
            "away": {},
            "home": {},
            "desiredTemperature": {
                "args": ["temperature"],
                "options": "slider,7,0.5,30",
            },
            "system_mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "options": "winter,summer,frostguard",
            },
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return (
                "Usage: define erelax_vaillant PythonModule USERNAME PASSWORD [STATION]"
            )
        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.create_async_task(self.do_update_loop(args[3], args[4]))

    async def set_away(self, hash, params):
        self.create_async_task(self.v_station.get_modules()[0].set_mode("away"))

    async def set_home(self, hash, params):
        self.create_async_task(self.v_station.get_modules()[0].disable_mode("away"))

    async def set_desiredTemperature(self, hash, params):
        self.create_async_task(
            self.v_station.get_modules()[0].set_setpoint_temp(params["temperature"])
        )

    async def set_system_mode(self, hash, params):
        self.create_async_task(
            self.v_station.get_modules()[0].set_system_mode(params["mode"])
        )

    async def do_update_loop(self, username, password):
        await self.do_login(username, password)

        self.v_station = VaillantStation(self.logger, self.v_auth)
        await self.v_station.init_device()
        await self.update_readings()

        self.v_station.register_update_readings(self.update_readings)

        while True:
            await asyncio.sleep(self._attr_update_interval)
            try:
                await self.v_station.update()
            except Exception as ex:
                self.logger.exception(ex)

    async def do_login(self, username, password):
        try:
            self.v_auth = await utils.run_blocking(
                functools.partial(
                    ClientAuth,
                    "na_client_android_vaillant",
                    self.unknown_code,
                    username,
                    password,
                    (
                        "read_station read_camera access_camera read_thermostat "
                        "write_thermostat read_presence access_presence"
                    ),
                    "1.0.4.0",
                    "vaillant",
                )
            )
        except Exception as ex:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "Failed to login to netatmo API", 1
            )
            self.logger.exception(ex)
            return

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        v_station = self.v_station
        await fhem.readingsBulkUpdate(self.hash, "station_name", v_station.station_name)
        await fhem.readingsBulkUpdate(self.hash, "system_mode", v_station.system_mode)
        await fhem.readingsBulkUpdate(self.hash, "station_mac", v_station.mac)
        await fhem.readingsBulkUpdate(self.hash, "station_type", v_station.model_type)
        await fhem.readingsBulkUpdate(
            self.hash, "place_altitude", v_station.place_altitude
        )
        await fhem.readingsBulkUpdate(self.hash, "place_city", v_station.place_city)
        await fhem.readingsBulkUpdate(
            self.hash, "place_continent", v_station.place_continent
        )
        await fhem.readingsBulkUpdate(
            self.hash, "place_country_name", v_station.place_country_name
        )
        await fhem.readingsBulkUpdate(self.hash, "place_street", v_station.place_street)
        await fhem.readingsBulkUpdate(
            self.hash, "place_timezone", v_station.place_timezone
        )
        await fhem.readingsBulkUpdate(
            self.hash, "place_location", v_station.place_location
        )
        await fhem.readingsBulkUpdate(self.hash, "dhw", v_station.dhw)
        await fhem.readingsBulkUpdate(self.hash, "station_firmware", v_station.firmware)
        await fhem.readingsBulkUpdate(self.hash, "oem_serial", v_station.oem_serial)
        await fhem.readingsBulkUpdate(
            self.hash, "hot_water_anticipating", v_station.hot_water_anticipating
        )
        await fhem.readingsBulkUpdate(self.hash, "wifi_status", v_station.wifi_status)
        await fhem.readingsBulkUpdate(self.hash, "station_firmware", v_station.firmware)
        await fhem.readingsBulkUpdate(
            self.hash, "boiler_oem_serial", v_station.boiler_oem_serial
        )
        await fhem.readingsBulkUpdate(
            self.hash, "outdoor_temperature", v_station.outdoor_temperatur
        )
        await fhem.readingsBulkUpdate(
            self.hash, "refill_water", v_station.ebus_refill_water
        )
        # currently only one thermostat (module) is supported
        v_module = self.v_station.get_modules()[0]
        await fhem.readingsBulkUpdate(self.hash, "thermostat_name", v_module.name)
        await fhem.readingsBulkUpdate(self.hash, "temperature", v_module.temperature)
        await fhem.readingsBulkUpdate(self.hash, "thermostat_mac", v_module.mac)
        await fhem.readingsBulkUpdate(
            self.hash, "thermostat_firmware", v_module.firmware
        )
        await fhem.readingsBulkUpdate(self.hash, "rf_status", v_module.rf_status)
        await fhem.readingsBulkUpdate(
            self.hash, "battery_percent", v_module.battery_percent
        )
        await fhem.readingsBulkUpdate(
            self.hash, "est_setpoint_temp", v_module.est_setpoint_temp
        )
        await fhem.readingsBulkUpdate(
            self.hash, "desiredTemperature", v_module.setpoint_temp
        )
        await fhem.readingsEndUpdate(self.hash, 1)


class VaillantStation:
    def __init__(self, logger, auth: ClientAuth, name: str = None) -> VaillantStation:
        self.auth = auth
        self.name = name
        self.logger = logger
        self.raw_device = None
        self.modules = []
        self._update_reading_function = None

    async def init_device(self):
        try:
            self._vaillant = await utils.run_blocking(
                functools.partial(VaillantThermostatData, self.auth)
            )
            self.raw_device = self.get_station_by_name(self.name)
            for raw_module in self.raw_device["modules"]:
                self.modules.append(VaillantModule(self.logger, self, raw_module))
        except Exception as ex:
            self.logger.exception(ex)

    def register_update_readings(self, update_reading_function):
        self._update_reading_function = update_reading_function

    def update_token(self):
        self._vaillant.token = self.auth.accessToken

    async def update(self):
        await utils.run_blocking(functools.partial(self.update_token))
        await utils.run_blocking(functools.partial(self._vaillant.update))
        self.raw_device = self.get_station_by_name(self.name)
        for module in self.modules:
            module.update(self.raw_device)
        if self._update_reading_function is not None:
            await self._update_reading_function()

    def get_station_by_name(self, name: str = None):
        if name is None:
            return self._vaillant.devList[0]
        for key, value in self._vaillant.devList.items():
            if value["station_name"] == name:
                return self._vaillant.devList[key]

    def get_modules(self) -> list[VaillantModule]:
        return self.modules

    @property
    def vaillant(self) -> VaillantThermostatData:
        return self._vaillant

    @vaillant.setter
    def vaillant(self, vaillant: VaillantThermostatData):
        self._vaillant = vaillant

    @property
    def station_name(self):
        if self.raw_device is not None:
            return self.raw_device["station_name"]
        return ""

    @property
    def system_mode(self):
        if self.raw_device is not None:
            return self.raw_device["system_mode"]
        return ""

    @property
    def mac(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["_id"]

    @property
    def model_type(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["type"]

    @property
    def place_altitude(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["altitude"]

    @property
    def place_city(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["city"]

    @property
    def place_continent(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["continent"]

    @property
    def place_country_name(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["country_name"]

    @property
    def place_street(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["street"]

    @property
    def place_timezone(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["place"]["timezone"]

    @property
    def place_location(self):
        if self.raw_device is None:
            return ""
        return (
            str(self.raw_device["place"]["location"][1])
            + ","
            + str(self.raw_device["place"]["location"][0])
        )

    @property
    def dhw(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["dhw"]

    @property
    def firmware(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["firmware"]

    @property
    def oem_serial(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["oem_serial"]

    @property
    def hot_water_anticipating(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["hot_water_anticipating"]

    @property
    def wifi_status(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["wifi_status"]

    @property
    def boiler_oem_serial(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["boiler_oem_serial"]

    @property
    def outdoor_temperatur(self):
        if self.raw_device is None:
            return 0.0
        return self.raw_device["outdoor_temperature"]["te"]

    @property
    def ebus_refill_water(self):
        if self.raw_device is None:
            return False
        return self.raw_device["ebus_status"]["refill_water"]

    @property
    def setpoint_hwb(self):
        if self.raw_device is None:
            return ""
        return self.raw_device["setpoint_hwb"]


class VaillantModule:
    def __init__(self, logger, station: VaillantStation, raw_module):
        self.logger = logger
        self.station = station
        self.module_name = raw_module["module_name"]
        self.raw_module = raw_module

    def update(self, data):
        for module in data["modules"]:
            if module["module_name"] == self.module_name:
                self.raw_module = module

    @property
    def name(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["module_name"]

    @property
    def firmware(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["firmware"]

    @property
    def rf_status(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["rf_status"]

    @property
    def battery_percent(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["battery_percent"]

    @property
    def setpoint_away(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["setpoint_away"]

    @property
    def setpoint_manual(self) -> str:
        if self.raw_module is None:
            return ""
        return self.raw_module["setpoint_manual"]

    @property
    def temperature(self) -> float:
        if self.raw_module is None:
            return 0.0
        return self.raw_module["measured"]["temperature"]

    @property
    def mac(self):
        if self.raw_module is None:
            return ""
        return self.raw_module["_id"]

    @property
    def setpoint_temp(self):
        if self.raw_module is None:
            return 0.0
        return self.raw_module["measured"]["setpoint_temp"]

    async def set_setpoint_temp(self, temp):
        try:
            await utils.run_blocking_task(
                functools.partial(self.station.vaillant.activate, "manual", temp)
            )
            # wait for update at netatmo
            await asyncio.sleep(1)
            await self.station.update()
        except Exception as ex:
            self.logger.exception(ex)

    async def set_mode(self, mode):
        try:
            # this is not handled but a required parameter within the function
            settemp = 15
            await utils.run_blocking_task(
                functools.partial(self.station.vaillant.activate, mode, settemp)
            )
            # wait for update at netatmo
            await asyncio.sleep(1)
            await self.station.update()
        except Exception as ex:
            self.logger.exception(ex)

    async def disable_mode(self, mode):
        try:
            await utils.run_blocking_task(
                functools.partial(self.station.vaillant.disable, mode)
            )
            # wait for update at netatmo
            await asyncio.sleep(1)
            await self.station.update()
        except Exception as ex:
            self.logger.exception(ex)

    async def set_system_mode(self, mode):
        try:
            await utils.run_blocking_task(
                functools.partial(self.station.vaillant.setSystemMode, mode)
            )
            # wait for update at netatmo
            await asyncio.sleep(1)
            await self.station.update()
        except Exception as ex:
            self.logger.exception(ex)

    @property
    def est_setpoint_temp(self):
        if self.raw_module is None:
            return 0.0
        return self.raw_module["measured"]["est_setpoint_temp"]
