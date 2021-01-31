import asyncio
import functools
import logging

from .. import fhem
from .. import utils as fpyutils
from ..generic import FhemModule
from .nespresso import NespressoDetect


class nespresso_ble(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.nespressodetect = None
        self.task = None
        self.auth = None
        logging.getLogger("pygatt.backends.gatttool.gatttool").setLevel(logging.ERROR)
        # logging.getLogger("nespresso_ble").setLevel(logging.DEBUG)
        self.set_conf_list = {
            "authkey": {"args": ["authkey"]},
            "brew": {
                "args": ["coffee_type", "temperature"],
                "params": {
                    "temperature": {"default": "high", "optional": True},
                    "coffee_type": {"default": "lungo", "optional": True},
                },
                "help": "1. parameter: ristretto, espresso, lungo, hotwater, americano<br>2. parameter: Temperature with values low, mid, high",
            },
            "easybrew": {
                "args": ["coffee_type"],
                "options": "ristretto,espresso,lungo,hotwater,americano",
            },
            "recipe": {"help": "Not yet supported"},
            "updateStatus": {},
        }
        self.set_set_config(self.set_conf_list)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return (
                "Usage: define devicename PythonModule nespresso_ble <MAC> [<AUTHKEY>]"
            )
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "offline")
        await fhem.readingsEndUpdate(hash, 1)
        self.mac = args[3]
        hash["MAC"] = args[3]

        # check if there is already an authkey
        if len(args) > 4:
            self.auth = args[4]
        else:
            self.auth = await fhem.ReadingsVal(self.hash["NAME"], "authkey", "")

        if self.auth != "":
            self.auth = args[4]
            self.nespressodetect = NespressoDetect(self.auth, self.mac)
            self.nespressodetect.set_keep_connected(True)
            self.task = self.create_async_task(self.update_status_task())
        return ""

    async def update_status_task(self):
        while True:
            if self.nespressodetect:
                await self.update_status()
            await asyncio.sleep(300)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        if self.auth and "authkey" in self.set_conf_list:
            del self.set_conf_list["authkey"]
            self.set_set_config(self.set_conf_list)
        return await super().Set(hash, args, argsh)

    async def set_authkey(self, hash, params):
        self.auth = params["authkey"]
        self.set_set_config(self.set_conf_list)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "authkey", self.auth, 1)
        if self.task:
            self.task.cancel()
        self.nespressodetect = NespressoDetect(self.auth, self.mac)
        self.nespressodetect.set_keep_connected(True)
        self.task = self.create_async_task(self.update_status_task())

    async def set_easybrew(self, hash, params):
        params["temperature"] = "medium"
        await self.set_brew(hash, params)

    async def set_brew(self, hash, params):
        try:
            coffee_type = params["coffee_type"]
            temp = params["temperature"]
            fpyutils.run_blocking_task(
                functools.partial(
                    self.nespressodetect.make_coffee, self.mac, temp, coffee_type
                )
            )
        except Exception:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)

    async def set_updateStatus(self, hash, params):
        self.create_async_task(self.update_status())

    async def update_status(self):
        await fpyutils.run_blocking(functools.partial(self.blocking_update_status))

        if self.device_info:
            for mac, dev in self.device_info.items():
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "manufacturer", dev.manufacturer, 1
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "serial_nr", dev.serial_nr, 1
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "model_nr", dev.model_nr, 1
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "device_name", dev.device_name, 1
                )
                if dev.device_name:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "online", 1
                    )
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "offline", 1
                    )
        else:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)

        if self.sensors_data:
            for mac, data in self.sensors_data.items():
                for name, val in data.items():
                    await fhem.readingsSingleUpdateIfChanged(self.hash, name, val, 1)

    def blocking_update_status(self):
        self.logger.debug("nespresso_ble updatestatus")
        try:
            self.device_info = self.nespressodetect.get_info()
            self.nespressodetect.get_sensors()
            self.sensors_data = self.nespressodetect.get_sensor_data()

        except Exception:
            self.logger.exception("Failed to update status")
            self.sensors_data = None
            self.device_info = None
