import asyncio

from aiohttp import ClientSession
from skodaconnect import Connection
from skodaconnect.vehicle import Vehicle

from .. import fhem, generic

# If you wish to use stored tokens, this is an example on how to format data sent to restore_tokens method:
TOKENS = {
    "technical": {"access_token": "...", "refresh_token": "...", "id_token": "..."},
    "connect": {"access_token": "...", "refresh_token": "...", "id_token": "..."},
    "vwg": {"access_token": "...", "refresh_token": "..."},
    "cabs": None,  # Could be populated with access_token, refresh_token, id_token
    "dcs": None,  # Could be populated with access_token, refresh_token, id_token
}
# Comment out the following line to use stored tokens above, set TOKENS=None to do fresh login
TOKENS = None


class skodaconnect(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        
        self.attr_config = {
            "vin": {
                "default": "",
                "help": "VIN of your car you want to connect to.",
            },
            "update_interval": {
                "default": 300,
                "format": "int",
                "help": (
                    "Readings update intervall in seconds (default 300s).<br>"
                    "do not poll to often due to API rate limits.<br>"
                    "You might be banned from VAG also on your offical APP<br>"
                    "until reset at 2 am."
                ),
            },
            "update_readings": {
                "default": "always",
                "options": "always,onchange",
                "help": "Update readings only on value change or always (default onchange).",
            },
            "EV_Type": {
                "default": "none",
                "options": "EV,other",
                "help": "Type of vehicle. Electriv Vehicle or other.",
            },
        }
        await self.set_attr_config(self.attr_config)

        if len(args) != 6:
            return (
                "Usage: define my_skoda fhempy skodaconnect my@account.com "
                " PaSSwOrD SPIN"
            )
        self.username = args[3]
        self.password = args[4]
        self.spin = args[5]
        self.create_async_task(self.start_login())
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)

    async def start_login(self):
        login_success = False
        async with ClientSession(headers={"Connection": "keep-alive"}) as session:
            connection = Connection(session, self.username, self.password, False)
            if TOKENS is not None:
                print("Attempting restore of tokens")
                if await connection.restore_tokens(TOKENS):
                    print("Token restore succeeded")
                    login_success = True
            if not login_success:
                print("Attempting to login to the Skoda Connect service")
                while await connection.doLogin() is False:
                    await asyncio.sleep(5)

            await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)            
            await connection.get_vehicles()
            await connection.update_all()

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

            await self.prepare_set_commands()

            await self.update_readings()

    async def prepare_set_commands(self):
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
            if self._attr_EV_Type == "EV":
                self.set_config["charger"] = {
                    "args": ["onoff"],
                    "options": "start,stop",
                }
                self.set_config["charge_limit"] = {
                    "args": ["limit"],
                    "options": "50,60,70,80,90,100",
                }
                self.set_config["charger_current"] = {
                    "args": ["current"],
                    "options": "Reduced,Maximum",
                }
                
            else:
                self.set_config["charger"] = {
                    "args": ["onoff"],
                    "options": "on,off",
                }
                self.set_config["charge_limit"] = {
                    "args": ["limit"],
                    "options": "0,10,20,30,40,50",
                }
                self.set_config["charger_current"] = {
                    "args": ["current"],
                    "options": "252,254",
                }

        if self.vehicle.is_electric_climatisation_supported:
            self.set_config["battery_climatisation"] = {
                "args": ["onoff"],
                "options": "on,off",
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
                "args": ["temperature"],
                "params": {"temperature": {"format": "float"}},
                "options": "slider,16,0.5,30,1",
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
                "you might be locked out by Skoda<br>"
                "until next motor start"
            ),
        }

        await self.set_set_config(self.set_config)

    async def set_pheater(self, hash, params):
        self.create_async_task(self.vehicle.set_pheater(params["mode"], self.spin))

    async def set_pheater_duration(self, hash, params):
        self.vehicle.pheater_duration = params["duration"]
        self.create_async_task(self.update_readings_once())

    async def set_lock(self, hash, params):
        self.create_async_task(self.vehicle.set_lock(params["lockunlock"], self.spin))

    async def set_honkandflash(self, hash, params):
        self.create_async_task(self.vehicle.set_honkandflash(params["honkandflash"]))

    async def set_charger(self, hash, params):
        self.create_async_task(self.vehicle.set_charger(params["onoff"]))

    async def set_charger_current(self, hash, params):
        self.create_async_task(self.vehicle.set_charger_current(params["current"]))

    async def set_charge_limit(self, hash, params):
        self.create_async_task(self.vehicle.set_charge_limit(int(params["limit"])))

    async def set_battery_climatisation(self, hash, params):
        self.create_async_task(self.vehicle.set_battery_climatisation(params["onoff"]))

    async def set_climatisation(self, hash, params):
        self.create_async_task(
            self.vehicle.set_climatisation(params["mode"], spin=self.spin)
        )

    async def set_climatisation_target_temperature(self, hash, params):
        self.create_async_task(
            self.vehicle.set_climatisation_temp(params["temperature"])
        )

    async def set_window_heating(self, hash, params):
        self.create_async_task(self.vehicle.set_window_heating(params["startstop"]))

    async def set_force_update(self, hash, params):
        self.create_async_task(self.vehicle.set_refresh())

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
                if instrument.attr == "fuel_level":
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
