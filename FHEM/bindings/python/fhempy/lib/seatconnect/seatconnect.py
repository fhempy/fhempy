import asyncio

from .. import fhem
from ..generic import FhemModule

from aiohttp import ClientSession
from seatconnect import Connection
from seatconnect.vehicle import Vehicle


class seatconnect(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.attr_config = {
            "vin": {
                "default": "",
                "help": "VIN of your car you want to connect to.",
            },
            "update_interval": {
                "default": 3600,
                "format": "int",
                "help": "Readings update intervall in seconds (default 3600s).",
            },
            "update_readings": {
                "default": "onchange",
                "options": "always,onchange",
                "help": "Update readings only on value change or always (default onchange).",
            },
        }
        self.set_attr_config(self.attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 6:
            return (
                "Usage: define my_seat fhempy seatconnect my@account.com "
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

            await connection.get_vehicles()

            self.connection = connection
            if len(connection.vehicles) > 1 and self._attr_vin == "":
                # there is more than one car
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "please set vin attribute", 1
                )
                return

            self.vehicle: Vehicle = None
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
            "timer_1_schedule_reccuring": {
                "args": ["time", "days"],
                "help": (
                    "Parameters: time(hh:mm) weekdays(yyyyynn)<br>"
                    "e.g. set my_seat timer_1_schedule_reccuring 08:00 yyyyynn<br>"
                    "recurring timer for climatisation which is activated mon-fri 08:00<br>"
                ),
            },
            "timer_1_schedule_date": {
                "args": ["date", "time"],
                "help": (
                    "Parameters: date(yyyy-mm-dd) time(hh:mm)<br>"
                    "e.g. set my_seat timer_1_schedule_date 2025-01-01 08:00<br>"
                    "timer for climatisation which is only activated on 1.1.2025 at 08:00"
                ),
            },
            "timer_2_schedule_reccuring": {
                "args": ["time", "days"],
                "help": (
                    "Parameters: time(hh:mm) weekdays(yyyyynn)<br>"
                    "e.g. set my_seat timer_2_schedule_reccuring 08:00 yyyyynn<br>"
                    "recurring timer for climatisation which is activated mon-fri 08:00<br>"
                ),
            },
            "timer_2_schedule_date": {
                "args": ["date", "time"],
                "help": (
                    "Parameters: date(yyyy-mm-dd) time(hh:mm)<br>"
                    "e.g. set my_seat timer_2_schedule_date 2025-01-01 08:00<br>"
                    "timer for climatisation which is only activated on 1.1.2025 at 08:00"
                ),
            },
            "timer_3_schedule_reccuring": {
                "args": ["time", "days"],
                "help": (
                    "Parameters: time(hh:mm) weekdays(yyyyynn)<br>"
                    "e.g. set my_seat timer_3_schedule_reccuring 08:00 yyyyynn<br>"
                    "recurring timer for climatisation which is activated mon-fri 08:00<br>"
                ),
            },
            "timer_3_schedule_date": {
                "args": ["date", "time"],
                "help": (
                    "Parameters: date(yyyy-mm-dd) time(hh:mm)<br>"
                    "e.g. set my_seat timer_3_schedule_date 2025-01-01 08:00<br>"
                    "timer for climatisation which is only activated on 1.1.2025 at 08:00"
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
                "params": {"current": {"format": "int"}},
            }
            self.set_config["charge_limit"] = {
                "args": ["limit"],
                "options": "0,10,20,30,40,50",
            }
        if self.vehicle.is_electric_climatisation_supported:
            self.set_config["battery_climatisation"] = {
                "args": ["onoff"],
                "options": "on,off",
                "params": {"onoff": {"format": "bool"}},
            }
            self.set_config["climatisation"] = {
                "args": ["mode"],
                "options": "auxiliary,electric,off",
            }
        if (
            self.vehicle.is_auxiliary_climatisation_supported
            or self.vehicle.is_electric_climatisation_supported
        ):
            self.set_config["climatisation_target_temperature"] = {
                "args": ["climatisation_target_temperature"],
                "params": {"climatisation_target_temperature": {"format": "float"}},
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

        self.set_config["honkandflash"] = {
            "args": ["honkandflash"],
            "options": "flash,honkandflash",
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
                "you might be locked out by seat<br>"
                "until next motor start"
            ),
        }

        self.set_set_config(self.set_config)

    async def set_pheater(self, hash, params):
        self.create_async_task(
            self.vehicle.set_pheater(mode=params["mode"], spin=self.spin)
        )

    async def set_pheater_duration(self, hash, params):
        self.vehicle.pheater_duration = params["duration"]

    async def set_lock(self, hash, params):
        self.create_async_task(
            self.vehicle.set_lock(action=params["lockunlock"], spin=self.spin)
        )

    async def set_honkandflash(self, hash, params):
        self.create_async_task(self.vehicle.set_honkandflash(params["honkandflash"]))

    async def set_charger(self, hash, params):
        self.create_async_task(self.vehicle.set_charger(action=params["onoff"]))

    async def set_charger_current(self, hash, params):
        self.create_async_task(self.vehicle.set_charger_current(params["current"]))

    async def set_charge_limit(self, hash, params):
        self.create_async_task(self.vehicle.set_charge_limit(limit=params["limit"]))

    async def set_battery_climatisation(self, hash, params):
        self.create_async_task(
            self.vehicle.set_battery_climatisation(mode=params["onoff"])
        )

    async def set_climatisation(self, hash, params):
        self.create_async_task(
            self.vehicle.set_climatisation(mode=params["mode"], spin=self.spin)
        )

    async def set_climatisation_target_temperature(self, hash, params):
        self.create_async_task(
            self.vehicle.set_climatisation_temp(
                temperature=params["climatisation_target_temperature"]
            )
        )

    async def set_window_heating(self, hash, params):
        self.create_async_task(
            self.vehicle.set_window_heating(action=params["startstop"])
        )

    async def set_timer_1(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_active(id=1, action=params["onoff"])
        )

    async def set_timer_2(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_active(id=2, action=params["onoff"])
        )

    async def set_timer_3(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_active(id=3, action=params["onoff"])
        )

    async def set_timer_1_schedule_reccuring(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=1,
                schedule={
                    "enabled": True,
                    "recurring": True,
                    "time": params["time"],
                    "days": params["days"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_timer_1_schedule_date(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=1,
                schedule={
                    "enabled": True,
                    "recurring": False,
                    "date": params["date"],
                    "time": params["time"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_timer_2_schedule_reccuring(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=2,
                schedule={
                    "enabled": True,
                    "recurring": True,
                    "time": params["time"],
                    "days": params["days"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_timer_2_schedule_date(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=2,
                schedule={
                    "enabled": True,
                    "recurring": False,
                    "date": params["date"],
                    "time": params["time"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_timer_3_schedule_reccuring(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=3,
                schedule={
                    "enabled": True,
                    "recurring": True,
                    "time": params["time"],
                    "days": params["days"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_timer_3_schedule_date(self, hash, params):
        self.create_async_task(
            self.vehicle.set_timer_schedule(
                id=3,
                schedule={
                    "enabled": True,
                    "recurring": False,
                    "date": params["date"],
                    "time": params["time"],
                    "operationClimatisation": True,
                    "operationCharging": False,
                },
            )
        )

    async def set_force_update(self, hash, params):
        self.create_async_task(self.update_readings_once())

    async def update_readings(self):
        self.instruments = self.vehicle.dashboard(mutable=True).instruments
        while True:
            await self.update_readings_once()
            await asyncio.sleep(self._attr_update_interval)

    async def update_readings_once(self):
        await self.connection.update_all()
        try:
            for instrument in self.instruments:
                if hasattr(instrument, "reverse_state") and instrument.reverse_state:
                    val_state = not instrument.state
                else:
                    val_state = instrument.state
                if self._attr_update_readings == "always":
                    await fhem.readingsSingleUpdate(
                        self.hash, instrument.attr, val_state, 1
                    )
                    await fhem.readingsSingleUpdate(
                        self.hash, instrument.attr + "_str", instrument.str_state, 1
                    )
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, instrument.attr, val_state, 1
                    )
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, instrument.attr + "_str", instrument.str_state, 1
                    )
                if instrument.attr == "battery_level":
                    if self._attr_update_readings == "always":
                        await fhem.readingsSingleUpdate(
                            self.hash, "state", instrument.str_state, 1
                        )
                    else:
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "state", instrument.str_state, 1
                        )
        except Exception:
            self.logger.exception("Failed to update readings")
