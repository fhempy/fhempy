
import asyncio
import logging

import bluepy.btle
import btlewrap
from btlewrap import BluetoothBackendException

from miflora import miflora_poller

from .. import fhem, utils


class miflora:

    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.updateTask = None
        self._poller = None
        self._attr_update_interval = 1200
        self._attr_hci_device = "hci0"
        self._attr_list = {
            "update_interval": {"default": 1200, "format": "int"},
            "hci_device": {"default": "hci0"}
        }
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define mi_plant PythonModule miflora <MAC>"

        await utils.handle_define_attr(self._attr_list, self, hash)
        self._address = args[3]
        self.hash["MAC"] = args[3]

        self._poller = miflora_poller.MiFloraPoller(
                self._address,
                cache_timeout=60,
                adapter=self._attr_hci_device,
                backend=btlewrap.BluepyBackend,
            )

        if self.updateTask:
            self.updateTask.cancel()
        self.updateTask = asyncio.create_task(self.update_task())
        return ""

    async def update_task(self):
        while True:
            await fhem.readingsBeginUpdate(self.hash)
            # name
            name = await utils.run_blocking(self._poller.name())
            await fhem.readingsBulkUpdateIfChanged(self.hash, "name", name)
            # firmware_version
            firmware_version = await utils.run_blocking(self._poller.firmware_version())
            await fhem.readingsBulkUpdateIfChanged(self.hash, "firmware", firmware_version)
            for param in ("temperature", "light", "moisture", "conductivity", "battery"):
                # param
                param_val = await utils.run_blocking(self._poller.parameter_value(param))
                await fhem.readingsBulkUpdateIfChanged(self.hash, param, param_val)
            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self._attr_update_interval)

    # FHEM FUNCTION
    async def Attr(self, hash, args, argsh):
        return await utils.handle_attr(self._attr_list, self, hash, args, argsh)

    async def set_attr_hci_device(self, hash):
        self._poller = miflora_poller.MiFloraPoller(
                self._address,
                cache_timeout=60,
                adapter=self._attr_hci_device,
                backend=btlewrap.BluepyBackend,
            )

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self.updateTask:
            self.updateTask.cancel()
        return
