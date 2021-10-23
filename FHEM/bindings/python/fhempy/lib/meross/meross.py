#!/usr/bin/env python3

import logging
from fhempy.lib.generic import FhemModule
from fhempy.lib.meross.meross_device import meross_device
from fhempy.lib.meross.meross_setup import meross_setup


class meross(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        logging.getLogger("meross_iot.manager").setLevel(logging.ERROR)
        logging.getLogger("meross_iot.controller").setLevel(logging.ERROR)
        self.device = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 5:
            return (
                "Usage: define meross_integration fhempy meross"
                " setup <USERNAME> <PASSWORD>"
            )

        if args[3] == "setup":
            self.device = meross_setup(self.logger, self)
        else:
            self.device = meross_device(self.logger, self)

        await self.device.Define(self.hash, args, argsh)

    async def set_on(self, hash, params):
        self.create_async_task(self.device.set_on(hash, params))

    async def set_off(self, hash, params):
        self.create_async_task(self.device.set_off(hash, params))

    async def set_toggle(self, hash, params):
        self.create_async_task(self.device.set_toggle(hash, params))

    async def set_open(self, hash, params):
        self.create_async_task(self.device.set_open(hash, params))

    async def set_close(self, hash, params):
        self.create_async_task(self.device.set_close(hash, params))

    async def set_rgb(self, hash, params):
        self.create_async_task(self.device.set_rgb(hash, params))

    async def set_brightness(self, hash, params):
        self.create_async_task(self.device.set_brightness(hash, params))

    async def set_ct(self, hash, params):
        self.create_async_task(self.device.set_ct(hash, params))

    @property
    def meross_device(self):
        return self.device
