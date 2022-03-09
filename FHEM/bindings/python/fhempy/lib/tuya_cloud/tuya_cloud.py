#!/usr/bin/env python3
"""Support for Tuya Smart devices."""

import logging
from fhempy.lib import fhem
from fhempy.lib.generic import FhemModule
import fhempy.lib.tuya_cloud.tuya_cloud_device as tcd
import fhempy.lib.tuya_cloud.tuya_cloud_setup as tcs


class tuya_cloud(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.device = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 5 or (len(args) < 8 and args[3] == "setup"):
            return (
                "Usage: define tuya_cloud fhempy tuya_cloud"
                " setup <API_KEY> <API_SECRET> <USERNAME> <PASSWORD>"
                " [<APPTYPE=smartlife>] [<REGION>=Europe]<br>"
                "OR if you want to define only one device<br>"
                " <TUYA_SETUP_DEVICE> <DEVICEID>"
            )

        if args[3] == "setup":
            self.device = tcs.tuya_cloud_setup(self.logger, self)
            if await fhem.AttrVal(self.hash["NAME"], "verbose", "3") == "5":
                logging.getLogger("tuya_iot").setLevel(logging.DEBUG)
            else:
                logging.getLogger("tuya_iot").setLevel(logging.ERROR)
        else:
            self.device = tcd.tuya_cloud_device(self.logger, self)

        await self.device.Define(self.hash, args, argsh)

    async def set_boolean(self, hash, params):
        await self.device.set_boolean(hash, params)

    async def set_enum(self, hash, params):
        await self.device.set_enum(hash, params)

    async def set_json(self, hash, params):
        await self.device.set_json(hash, params)

    async def set_string(self, hash, params):
        await self.device.set_string(hash, params)

    async def set_integer(self, hash, params):
        await self.device.set_integer(hash, params)

    async def set_colour_data(self, hash, params):
        await self.device.set_colour_data(hash, params)

    async def set_colour_data_v2(self, hash, params):
        await self.device.set_colour_data_v2(hash, params)

    @property
    def tuya_cloud_device(self):
        return self.device
