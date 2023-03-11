import asyncio
import functools

import hyundai_kia_connect_api as api

from .. import fhem, generic, utils


class kia_hyundai(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "update_interval": {
                "default": 30,
                "format": "int",
                "help": "Change interval in minutes, default is 30.",
            }
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "lock": {},
            "unlock": {},
            "start_climate": {
                "args": ["set_temp", "duration", "defrost", "climate", "heating"],
                "help": "Params: Temperature Duration Defrost(on/off) Climate(on/off) Heating(on/off)",
                "params": {
                    "set_temp": {"default": 21, "format": "int"},
                    "duration": {"default": 5, "format": "int"},
                    "defrost": {"default": False, "format": "bool"},
                    "climate": {"default": True, "format": "bool"},
                    "heating": {"default": False, "format": "bool"},
                },
            },
            "stop_climate": {},
            "start_charge": {},
            "stop_charge": {},
            "charge_limits": {
                "args": ["ac_limit", "dc_limit"],
                "help": "Params AC Limit DC Limit",
                "params": {
                    "ac_limit": {"default": 90, "format": "int"},
                    "dc_limit": {"default": 90, "format": "int"},
                },
            },
            "update_data": {},
        }
        await self.set_set_config(set_config)

        if len(args) != 8:
            return (
                "Usage: define my_car fhempy kia_hyundai "
                + "USERNAME PASSWORD PIN CAR_BRAND REGION_CODE"
            )
        self.username = args[3]
        self.password = args[4]
        self.pin = args[5]
        self.car_brand = [
            k for k, v in api.const.BRANDS.items() if v.lower() == args[6].lower()
        ][0]
        if args[7].lower() == "eu":
            args[7] = "Europe"
        self.region_code = [
            k for k, v in api.const.REGIONS.items() if v.lower() == args[7].lower()
        ][0]
        self.create_async_task(self.connect_to_car())

    async def connect_to_car(self):
        self.vm = api.VehicleManager(
            self.region_code,
            self.car_brand,
            self.username,
            self.password,
            self.pin,
            geocode_api_enable=True,
            geocode_api_use_email=True,
        )
        while True:
            try:
                await utils.run_blocking(
                    functools.partial(self.vm.check_and_refresh_token)
                )
                self.create_async_task(self.update_loop())
                break
            except Exception:
                self.logger.exception("Failed to login to server, retry in 120s")
                await asyncio.sleep(120)

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_update_interval * 60)

    async def update_once(self):
        try:
            await utils.run_blocking(functools.partial(self.vm.check_and_refresh_token))
            await utils.run_blocking(
                functools.partial(self.vm.update_all_vehicles_with_cached_state)
            )
            await self.update_readings()
        except Exception:
            self.logger.exception("Failed to update car data")
            await fhem.readingsSingleUpdate(self.hash, "state", "error", 1)

    async def update_readings(self):
        # use only first vehicle
        self.vehicle = self.vm.vehicles[list(self.vm.vehicles)[0]]
        flat_json = utils.flatten_json(self.vehicle.data)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in flat_json:
                await fhem.readingsBulkUpdate(self.hash, name, flat_json[name])
            await fhem.readingsBulkUpdate(
                self.hash, "geolocation", self.vehicle.geocode[0]
            )
            await fhem.readingsBulkUpdate(self.hash, "state", "online")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)
    async def set_update_data(self, hash, params):
        self.create_async_task(self.update_once())

    async def set_lock(self, hash, params):
        self.create_async_task(self.execute_command(self.vm.lock, self.vehicle.id))

    async def set_unlock(self, hash, params):
        self.create_async_task(self.execute_command(self.vm.unlock, self.vehicle.id))

    async def set_start_climate(self, hash, params):
        self.create_async_task(
            self.execute_command(
                self.vm.start_climate,
                self.vehicle.id,
                params["set_temp"],
                params["duration"],
                params["defrost"],
                params["climate"],
                params["heating"],
            )
        )

    async def set_stop_climate(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.stop_climate, self.vehicle.id)
        )

    async def set_start_charge(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.start_charge, self.vehicle.id)
        )

    async def set_stop_charge(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.stop_charge, self.vehicle.id)
        )

    async def set_charge_limits(self, hash, params):
        utils.run_blocking_task(
            functools.partial(
                self.vm.set_charge_limits,
                self.vehicle.id,
                params["ac_limit"],
                params["dc_limit"],
            )
        )

    async def execute_command(self, command, *kwargs):
        # check token
        await utils.run_blocking(functools.partial(self.vm.check_and_refresh_token))

        # execute function
        await utils.run_blocking(functools.partial(command, *kwargs))
