from __future__ import annotations

import asyncio
import datetime

from .. import fhem, utils
from .. import generic

from httpx import AsyncClient

from vaillant_netatmo_api import (
    AuthClient,
    SystemMode,
    ThermostatClient,
    TokenStore,
    SetpointMode,
)


class erelax_vaillant(generic.FhemModule):
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
                "params": {"temperature": {"format": "float"}},
                "options": "slider,7,0.5,30",
            },
            "desiredTemperatureDuration": {
                "args": ["temperature", "duration"],
                "params": {
                    "duration": {"format": "int"},
                    "temperature": {"format": "float"},
                },
                "help": (
                    "Set temperature for a specific duration in minutes<br>"
                    "set vaillant TEMPERATURE DURATION"
                ),
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
            return "Usage: define erelax_vaillant fhempy USERNAME PASSWORD [STATION]"
        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.username = args[3]
        self.password = args[4]
        self.create_async_task(self.do_update_loop())

    async def set_away(self, hash, params):
        self.create_async_task(
            self.thermostat_client.async_set_minor_mode(
                self.devices[0].id,
                self.devices[0].modules[0].id,
                SetpointMode.AWAY,
                True,
                None,
                None,
            )
        )

    async def set_home(self, hash, params):
        self.create_async_task(
            self.thermostat_client.async_set_minor_mode(
                self.devices[0].id,
                self.devices[0].modules[0].id,
                SetpointMode.HWB,
                True,
                None,
                None,
            )
        )

    async def set_desiredTemperature(self, hash, params):
        endtime = datetime.datetime.now() + datetime.timedelta(
            minutes=self.devices[0].setpoint_default_duration
        )
        self.create_async_task(
            self.thermostat_client.async_set_minor_mode(
                self.devices[0].id,
                self.devices[0].modules[0].id,
                SetpointMode.MANUAL,
                True,
                endtime,
                params["temperature"],
            )
        )

    async def set_desiredTemperatureDuration(self, hash, params):
        endtime = datetime.datetime.now() + datetime.timedelta(
            minutes=params["duration"]
        )
        self.create_async_task(
            self.thermostat_client.async_set_minor_mode(
                self.devices[0].id,
                self.devices[0].modules[0].id,
                SetpointMode.MANUAL,
                True,
                endtime,
                params["temperature"],
            )
        )

    async def set_system_mode(self, hash, params):
        if params["mode"] == "winter":
            set_mode = SystemMode.WINTER
        elif params["mode"] == "summer":
            set_mode = SystemMode.SUMMER
        else:
            set_mode = SystemMode.FROSTGUARD
        self.create_async_task(
            self.thermostat_client.async_set_system_mode(
                self.devices[0].id, self.devices[0].modules[0].id, set_mode
            )
        )

    async def do_update_loop(self):
        async with AsyncClient() as client:
            token_store = TokenStore(
                "na_client_android_vaillant",
                self.unknown_code,
                None,
                None,
            )
            await self.async_get_token(client, token_store)
            self.thermostat_client = ThermostatClient(client, token_store)

            while True:
                try:
                    self.devices = (
                        await self.thermostat_client.async_get_thermostats_data()
                    )

                    await self.update_readings()
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "connected", 1
                    )
                except Exception as ex:
                    self.logger.exception(ex)
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "error", 1
                    )

                await asyncio.sleep(self._attr_update_interval)

    async def async_get_token(self, client, token_store):
        client = AuthClient(client, token_store)

        await client.async_token(self.username, self.password, "vaillant", "1.0.4.0")

    async def update_readings(self):
        if len(self.devices) == 0:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "no stations found for this account", 1
            )
            return

        # currently only one thermostat (module) is supported
        v_station = self.devices[0]
        v_module = self.devices[0].modules[0]
        await fhem.readingsBeginUpdate(self.hash)

        # station
        await fhem.readingsBulkUpdate(self.hash, "station_name", v_station.station_name)
        await fhem.readingsBulkUpdate(self.hash, "system_mode", v_station.system_mode)
        await fhem.readingsBulkUpdate(self.hash, "station_mac", v_station.id)
        await fhem.readingsBulkUpdate(self.hash, "station_type", v_station.type)
        await fhem.readingsBulkUpdate(self.hash, "station_firmware", v_station.firmware)
        await fhem.readingsBulkUpdate(
            self.hash,
            "station_setpoint_default_duration",
            v_station.setpoint_default_duration,
        )
        await fhem.readingsBulkUpdate(
            self.hash,
            "station_setpoint_hwb",
            v_station.setpoint_hwb.setpoint_activate,
        )

        # module
        await fhem.readingsBulkUpdate(self.hash, "thermostat_mac", v_module.id)
        await fhem.readingsBulkUpdate(self.hash, "thermostat_type", v_module.type)
        await fhem.readingsBulkUpdate(
            self.hash, "thermostat_name", v_module.module_name
        )
        await fhem.readingsBulkUpdate(
            self.hash, "thermostat_firmware", v_module.firmware
        )
        await fhem.readingsBulkUpdate(
            self.hash, "thermostat_battery_percent", v_module.battery_percent
        )

        # setpoint_manual
        await fhem.readingsBulkUpdate(
            self.hash, "setpoint_manual", v_module.setpoint_manual.setpoint_activate
        )
        if v_module.setpoint_manual.setpoint_activate:
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_manual_endtime",
                v_module.setpoint_manual.setpoint_endtime,
            )
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_manual_endtime_epoch",
                v_module.setpoint_manual.setpoint_endtime.timestamp(),
            )
        else:
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_manual_endtime",
                "0",
            )

        # setpoint_away
        await fhem.readingsBulkUpdate(
            self.hash, "setpoint_away", v_module.setpoint_away.setpoint_activate
        )
        if v_module.setpoint_away.setpoint_activate:
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_away_endtime",
                v_module.setpoint_away.setpoint_endtime,
            )
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_away_endtime_epoch",
                v_module.setpoint_away.setpoint_endtime.timestamp(),
            )
        else:
            await fhem.readingsBulkUpdate(
                self.hash,
                "setpoint_away_endtime",
                "0",
            )

        # measured
        await fhem.readingsBulkUpdate(
            self.hash, "temperature", v_module.measured.temperature
        )
        await fhem.readingsBulkUpdate(
            self.hash, "est_setpoint_temp", v_module.measured.est_setpoint_temp
        )
        await fhem.readingsBulkUpdate(
            self.hash, "desiredTemperature", v_module.measured.setpoint_temp
        )
        await fhem.readingsBulkUpdate(
            self.hash, "outdoor_temperature", v_station.outdoor_temperature.temperature
        )
        await fhem.readingsBulkUpdate(
            self.hash,
            "outdoor_temperature_updated",
            v_station.outdoor_temperature.date_updated,
        )

        """ await fhem.readingsBulkUpdate(
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
        await fhem.readingsBulkUpdate(self.hash, "oem_serial", v_station.oem_serial)
        await fhem.readingsBulkUpdate(
            self.hash, "hot_water_anticipating", v_station.hot_water_anticipating
        )
        await fhem.readingsBulkUpdate(self.hash, "wifi_status", v_station.wifi_status)
        await fhem.readingsBulkUpdate(
            self.hash, "boiler_oem_serial", v_station.boiler_oem_serial
        )
        await fhem.readingsBulkUpdate(
            self.hash, "refill_water", v_station.ebus_refill_water
        )

        await fhem.readingsBulkUpdate(self.hash, "rf_status", v_module.rf_status)
        """
        await fhem.readingsEndUpdate(self.hash, 1)
