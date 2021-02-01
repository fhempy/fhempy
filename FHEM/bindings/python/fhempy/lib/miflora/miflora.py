import asyncio
import functools
import logging

import bluepy.btle
import btlewrap
from btlewrap import BluetoothBackendException
from fhempy.lib.generic import FhemModule
from miflora import miflora_poller

from .. import fhem, utils


class miflora(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.hash = None
        self.updateTask = None
        self._poller = None
        self._attr_update_interval = 1200
        self._attr_hci_device = "hci0"
        self._attr_list = {
            "update_interval": {"default": 1200, "format": "int"},
            "hci_device": {"default": "hci0"},
            "poll_type": {"default": "interval", "options": "interval,manual"},
        }
        self.set_attr_config(self._attr_list)
        self._set_list = {"update": {}}
        self.set_set_config(self._set_list)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define mi_plant PythonModule miflora <MAC>"

        self._address = args[3]
        hash["MAC"] = args[3]
        self.logger.debug(f"Define miflora: {self._address}")

        self._poller = miflora_poller.MiFloraPoller(
            self._address,
            cache_timeout=60,
            adapter=self._attr_hci_device,
            backend=btlewrap.BluepyBackend,
        )

        if self.updateTask:
            self.updateTask.cancel()
        self.updateTask = self.create_async_task(self.update_task())

    async def update_task(self):
        while True:
            await self.do_update()
            await asyncio.sleep(self._attr_update_interval)

    async def do_update(self):
        self.logger.debug(f"Run update task")
        try:
            await fhem.readingsBeginUpdate(self.hash)
            # name
            name = await utils.run_blocking(functools.partial(self._poller.name))
            await fhem.readingsBulkUpdateIfChanged(self.hash, "name", name)
            # firmware_version
            firmware_version = await utils.run_blocking(
                functools.partial(self._poller.firmware_version)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "firmware", firmware_version
            )
            for param in (
                "temperature",
                "light",
                "moisture",
                "conductivity",
                "battery",
            ):
                # param
                param_val = await utils.run_blocking(
                    functools.partial(self._poller.parameter_value, param)
                )
                await fhem.readingsBulkUpdateIfChanged(self.hash, param, param_val)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "presence", "online")
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "online")
            await fhem.readingsEndUpdate(self.hash, 1)
        except Exception:
            self.logger.error(f"Failed to get updates from miflora {self._address}")
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "presence", "offline", 1
            )
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)

    async def set_update(self, hash, params):
        self.create_async_task(self.do_update())

    async def set_attr_update_interval(self, hash):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "update_interval", str(self._attr_update_interval), 1
        )
        if self.updateTask:
            self.updateTask.cancel()
        self.updateTask = self.create_async_task(self.update_task())

    async def set_attr_poll_type(self, hash):
        if self._attr_poll_type == "manual":
            if self.updateTask:
                self.updateTask.cancel()
                self.updateTask = None
        elif self._attr_poll_type == "interval":
            if self.updateTask is None:
                self.updateTask = self.create_async_task(self.update_task())
        return

    async def set_attr_hci_device(self, hash):
        self.logger.debug(f"attr change of hci device")
        self._poller = miflora_poller.MiFloraPoller(
            self._address,
            cache_timeout=60,
            adapter=self._attr_hci_device,
            backend=btlewrap.BluepyBackend,
        )
