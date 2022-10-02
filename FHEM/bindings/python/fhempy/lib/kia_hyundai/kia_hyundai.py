import asyncio
import functools

from fhempy.lib.kia_hyundai.const import VEHICLE_LOCK_ACTION

from .. import fhem, generic, utils
from .utils import get_implementation_by_region_brand
from .Vehicle import Vehicle


class kia_hyundai(generic.FhemModule):

    CAR_BRANDS = {"kia": 1, "hyundai": 2}
    REGION_CODE = {"eu": 1, "us": 2, "ca": 3}

    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "update_interval": {
                "default": 30,
                "format": "int",
                "help": "Change interval in minutes, default is 30.",
            }
        }
        self.set_attr_config(attr_config)

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
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 8:
            return (
                "Usage: define my_car fhempy kia_hyundai "
                + "USERNAME PASSWORD PIN CAR_BRAND REGION_CODE"
            )
        self.username = args[3]
        self.password = args[4]
        self.pin = args[5]
        self.car_brand = kia_hyundai.CAR_BRANDS[args[6].lower()]
        self.region_code = kia_hyundai.REGION_CODE[args[7].lower()]
        self.create_async_task(self.connect_to_car())

    async def connect_to_car(self):
        self.token = None
        kh_impl = get_implementation_by_region_brand(
            self.region_code, self.car_brand, self.username, self.password
        )
        while self.token is None:
            self.token = await utils.run_blocking(functools.partial(kh_impl.login))
            if self.token is not None:
                self.vehicle = Vehicle(
                    self.token, kh_impl, "km", False, str(self.region_code)
                )
                self.create_async_task(self.update_loop())
                break
            await asyncio.sleep(60)

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_update_interval * 60)

    async def update_once(self):
        try:
            await self.vehicle.update()
            await self.update_readings()
        except Exception:
            self.logger.exception("Failed to update car data")
            await fhem.readingsSingleUpdate(self.hash, "state", "error", 1)

    async def update_readings(self):
        flat_json = utils.flatten_json(self.vehicle.vehicle_data)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in flat_json:
                await fhem.readingsBulkUpdate(self.hash, name, flat_json[name])
            await fhem.readingsBulkUpdate(self.hash, "state", "online")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)
    async def set_update_data(self, hash, params):
        self.create_async_task(self.update_once())

    async def set_lock(self, hash, params):
        self.create_async_task(self.vehicle.lock_action(VEHICLE_LOCK_ACTION.LOCK))

    async def set_unlock(self, hash, params):
        self.create_async_task(self.vehicle.lock_action(VEHICLE_LOCK_ACTION.UNLOCK))

    async def set_start_climate(self, hash, params):
        self.create_async_task(
            self.vehicle.start_climate(
                params["set_temp"],
                params["duration"],
                params["defrost"],
                params["climate"],
                params["heating"],
            )
        )

    async def set_stop_climate(self, hash, params):
        self.create_async_task(self.vehicle.stop_climate())

    async def set_start_charge(self, hash, params):
        self.create_async_task(self.vehicle.start_charge())

    async def set_stop_charge(self, hash, params):
        self.create_async_task(self.vehicle.stop_charge())

    async def set_charge_limits(self, hash, params):
        self.create_async_task(
            self.vehicle.set_charge_limits(params["ac_limit"], params["dc_limit"])
        )
