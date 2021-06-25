import asyncio

from .. import fhem
from ..generic import FhemModule

from aiohttp import ClientSession
from skodaconnect import Connection


class skodaconnect(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.attr_config = {
            "vin": {
                "default": "",
                "help": "VIN of your car you want to connect to.",
            }
        }
        self.set_attr_config(self.attr_config)

        self._update_interval = 30
        self._update_readings = "always"

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 6:
            return (
                "Usage: define my_skoda PythonModule skodaconnect my@account.com "
                " PaSSwOrD SPIN"
            )
        self.username = args[3]
        self.password = args[4]
        self.spin = args[5]
        self.create_async_task(self.start_login())
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)

    async def start_login(self):
        async with ClientSession(headers={"Connection": "keep-alive"}) as session:
            connection = Connection(session, self.username, self.password, False)
            while await connection.doLogin() is False:
                await asyncio.sleep(5)

            self.connection = connection
            if len(connection.vehicles) > 1 and self._attr_vin == "":
                # there is more than one car
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "please set vin attribute", 1
                )
                return

            self.vehicle = None
            for vehicle in connection.vehicles:
                if self._attr_vin != "" and vehicle.vin == self._attr_vin:
                    self.vehicle = vehicle
                elif self._attr_vin == "":
                    self.vehicle = vehicle

            if self.vehicle is None:
                # no car identified
                await fhem.readingsSingleUpdate(self.hash, "state", "no cars found", 1)
                return

            self.prepare_set_commands()

            await self.update_readings()

    def prepare_set_commands(self):
        self.set_config = {
            "timer_1": {"args": ["onoff"], "options": "on,off"},
            "timer_2": {"args": ["onoff"], "options": "on,off"},
            "timer_3": {"args": ["onoff"], "options": "on,off"},
            "timer_1_schedule": {
                "args": ["active", "recurring", "date", "time", "days"],
                "help": (
                    "Parameters: activate(0/1) recurring(0/1) date(yyyymmdd) time(hhmm) weekdays(yyyyynn)<br>"
                    "e.g. set my_skoda timer_1_schedule 1 1 0800 yyyyynn<br>"
                    "recurring timer which is activated mon-fri 08:00<br>"
                    "e.g. set my_skoda timer_1_schedule 1 0 20250101 0800<br>"
                    "timer which is only activated on 1.1.2025 at 08:00"
                ),
            },
            "timer_2_schedule": {
                "args": ["active", "recurring", "date", "time", "days"],
                "help": (
                    "Parameters: activate(0/1) recurring(0/1) date(yyyymmdd) time(hhmm) weekdays(yyyyynn)<br>"
                    "e.g. set my_skoda timer_1_schedule 1 1 0800 yyyyynn<br>"
                    "recurring timer which is activated mon-fri 08:00<br>"
                    "e.g. set my_skoda timer_1_schedule 1 0 20250101 0800<br>"
                    "timer which is only activated on 1.1.2025 at 08:00"
                ),
            },
            "timer_3_schedule": {
                "args": ["active", "recurring", "date", "time", "days"],
                "help": (
                    "Parameters: activate(0/1) recurring(0/1) date(yyyymmdd) time(hhmm) weekdays(yyyyynn)<br>"
                    "e.g. set my_skoda timer_1_schedule 1 1 0800 yyyyynn<br>"
                    "recurring timer which is activated mon-fri 08:00<br>"
                    "e.g. set my_skoda timer_1_schedule 1 0 20250101 0800<br>"
                    "timer which is only activated on 1.1.2025 at 08:00"
                ),
            },
        }
        if self.vehicle.is_charging_supported:
            self.set_config["charger"] = {
                "args": ["onoff"],
                "options": "on,off",
            }
            self.set_config["charger_current"] = {
                "args": ["current"],
                "options": "slider,1,1,254",
            }
            self.set_config["charge_limit"] = {
                "args": ["limit"],
                "options": "0,10,20,30,40,50",
            }
        if self.vehicle.is_electric_climatisation_supported:
            self.set_config["battery_climatisation"] = {
                "args": ["onoff"],
                "options": "on,off",
            }
            self.set_config["climatisation"] = {
                "args": ["mode"],
                "options": "auxilliary,electric,off",
            }
        if (
            self.vehicle.is_auxiliary_climatisation_supported
            or self.vehicle.is_electric_climatisation_supported
        ):
            self.set_config["climatisation_temperature"] = {
                "args": ["temperature"],
                "options": "slider,16,1,30",
            }
        if self.vehicle.is_window_heater_supported:
            self.set_config["window_heating"] = {
                "args": ["startstop"],
                "options": "start,stop",
            }

        self.set_config["lock"] = {
            "args": ["lockunlock"],
            "options": "lock,unlock",
        }

        if self.vehicle.is_pheater_heating_supported:
            self.set_config["pheater"] = {
                "args": ["mode"],
                "options": "heating,ventilation,off",
            }
            self.set_config["pheater_duration"] = {
                "args": ["duration"],
                "options": "slider,10,10,60",
                "params": {"duration": {"format": "int"}},
            }

        self.set_config["force_update"] = {
            "help": (
                "will trigger force update<br>"
                "this command should not be used too often<br>"
                "you might be locked out by Skoda<br>"
                "until next motor start"
            ),
        }

        self.set_config["update_interval"] = {
            "args": ["UpdateInterval"],
            "params": {"UpdateInterval": {"format": "int"}},
            "options": "slider,30,30,300",
        }

        self.set_config["update_readings"] = {
            "args": ["alwaysupdated"],
            "options": "always,onchange",
            "help": (
                "Parameters: always, onchange<br>"
                "`always` will update readings on each intervall<br>"
                "`onchange` will update readings only when new value available"
            ),
        }

        self.set_set_config(self.set_config)

    async def set_pheater(self, hash, params):
        self.create_async_task(self.vehicle.set_pheater(params["mode"], self.spin))

    async def set_pheater_duration(self, hash, params):
        self.vehicle.pheater_duration = params["duration"]
        self.create_async_task(self.update_readings_once())

    async def set_lock(self, hash, params):
        self.create_async_task(self.vehicle.set_lock(params["lockunlock"], self.spin))

    async def set_charger(self, hash, params):
        self.create_async_task(self.vehicle.set_charger(params["onoff"]))

    async def set_charger_current(self, hash, params):
        self.create_async_task(self.vehicle.set_charger_current(params["current"]))

    async def set_charge_limit(self, hash, params):
        self.create_async_task(self.vehicle.set_charger(params["limit"]))

    async def set_battery_climatisation(self, hash, params):
        self.create_async_task(self.vehicle.set_battery_climatisation(params["onoff"]))

    async def set_climatisation_temp(self, hash, params):
        self.create_async_task(
            self.vehicle.set_climatisation_temp(params["temperature"])
        )

    async def set_window_heating(self, hash, params):
        self.create_async_task(self.vehicle.set_window_heating(params["startstop"]))

    async def set_force_update(self, hash, params):
        self.create_async_task(self.vehicle.set_refresh())

    async def set_update_interval(self, hash, params):
        self._update_interval = params["UpdateInterval"]
        await fhem.readingsSingleUpdate(
            self.hash, "update_interval", self._update_interval, 1
        )
        self.create_async_task(self.update_readings_once())

    async def set_update_readings(self, hash, params):
        self._update_readings = params["alwaysupdated"]
        await fhem.readingsSingleUpdate(
            self.hash, "update_readings", self._update_readings, 1
        )
        self.create_async_task(self.update_readings_once())

    async def update_readings(self):
        self.instruments = self.vehicle.dashboard(mutable=True).instruments
        while True:
            await self.update_readings_once()
            await asyncio.sleep(self._update_interval)

    async def update_readings_once(self):
        await self.connection.update()
        try:
            for instrument in self.instruments:
                if hasattr(instrument, "reverse_state") and instrument.reverse_state:
                    val_state = not instrument.state
                else:
                    val_state = instrument.state
                if self._update_readings == "always":
                    await fhem.readingsSingleUpdate(
                        self.hash, instrument.attr, val_state, 1
                    )
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, instrument.attr, val_state, 1
                    )
                if self._update_readings == "always":
                    await fhem.readingsSingleUpdate(
                        self.hash, instrument.attr + "_str", instrument.str_state, 1
                    )
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, instrument.attr + "_str", instrument.str_state, 1
                    )
                if instrument.attr == "fuel_level":
                    if self._update_readings == "always":
                        await fhem.readingsSingleUpdate(
                            self.hash, "state", instrument.str_state, 1
                        )
                    else:
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "state", instrument.str_state, 1
                        )
        except Exception:
            self.logger.exception("Failed to update readings")
