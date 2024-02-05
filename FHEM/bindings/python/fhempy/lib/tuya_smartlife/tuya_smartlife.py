#!/usr/bin/env python3
"""Support for Tuya Smart devices."""

import fhempy.lib.tuya_smartlife.tuya_smartlife_device as tsd
import fhempy.lib.tuya_smartlife.tuya_smartlife_setup as tss
from fhempy.lib import fhem, utils
from fhempy.lib.generic import FhemModule


class tuya_smartlife(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.device = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        # initialize set commands
        set_conf = {
            "scan_done": {},
            "relogin": {},
        }
        await self.set_set_config(set_conf)

        # define my_tuya_smartlife fhempy tuya_smartlife USERCODE
        # check if len(args) is between 4 and 5
        if not (4 <= len(args) <= 5):
            return (
                "Usage: define my_tuya_smartlife fhempy tuya_smartlife setup USERCODE"
            )

        if args[3] == "setup":
            self.usercode = args[4]

            self.setup_device = tss.tuya_smartlife_setup(self.logger, self)

            # start login procedure asynchron
            self.create_async_task(self.setup_device.login())
        else:
            self.device = tsd.tuya_smartlife_device(self.logger, self)
            await self.device.Define(self.hash, args, argsh)

    async def Undefine(self, hash):
        if self.device:
            await self.device.Undefine(hash)
        return await super().Undefine(hash)

    async def set_scan_done(self, hash, params):
        self.create_async_task(self.setup_device.set_scan_done(hash, params))

    async def set_relogin(self, hash, params):
        # clear token_info, terminal_id and endpoint
        await fhem.readingsSingleUpdate(self.hash, "token_info", "{}", 1)
        await fhem.readingsSingleUpdate(self.hash, "terminal_id", "", 1)
        await fhem.readingsSingleUpdate(self.hash, "endpoint", "", 1)
        self.create_async_task(self.setup_device.login())

    async def set_reset_energy(self, hash, params):
        await self.device.set_reset_energy(hash, params)

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
