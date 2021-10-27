import functools
import time
import asyncio

from fhempy.lib import fhem, utils
from fhempy.lib.xiaomi_gateway3_device.devices.base import BaseDevice


class Gateway(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
        set_config = {
            "start_pairing": {},
            "stop_pairing": {},
            "firmware_update": {"args": ["block"], "options": "block,allow"},
            "start_model_pairing": {"args": ["model"]},
        }
        self.set_set_config(set_config)

    async def set_firmware_update(self, hash, params):
        self.create_async_task(self.lock_firmware(params["block"] == "block"))

    async def lock_firmware(self, enable):
        locked = await utils.run_blocking(
            functools.partial(self._gateway.gateway3.lock_firmware, enable)
        )
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "firmware_lock", str(locked), 1
        )

    async def set_start_model_pairing(self, hash, params):
        model = params["model"]
        self._gateway.gateway3.pair_model = (
            model[:-3] if model.endswith(".v1") else model
        )
        await self.set_start_pairing(hash, params)

    async def set_start_pairing(self, hash, params):
        self._gateway.gateway3.miio.send(
            "miIO.zb_start_provision",
            {
                "dev_type": 0,
                "duration": 60,
                "method": 0,
                "model": "lumi.sensor_switch.v2",
                "pid": 62,
            },
        )

    async def set_stop_pairing(self, hash, params):
        self._gateway.gateway3.miio.send("miIO.zb_end_provision", {"code": -1})

    def update(self, data):
        asyncio.run_coroutine_threadsafe(self.async_update(data), self.loop).result()

    async def async_update(self, data):
        self.last_update = time.time()
        if data is None:
            return

        await fhem.readingsBeginUpdate(self.hash)
        # device is online
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "online")
        # update data
        for reading in data:
            if reading == "pairing_start":
                await fhem.readingsBulkUpdateIfChanged(self.hash, "pairing", "on")
            elif reading == "pairing_stop":
                await fhem.readingsBulkUpdateIfChanged(self.hash, "pairing", "off")
            else:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading.replace(" ", "_"), str(data[reading])
                )
        await fhem.readingsEndUpdate(self.hash, 1)
