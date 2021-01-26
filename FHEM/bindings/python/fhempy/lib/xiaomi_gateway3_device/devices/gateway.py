from fhempy.lib.xiaomi_gateway3_device.devices.base import BaseDevice
from fhempy.lib import fhem, utils
import functools


class Gateway(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
        set_config = {
            "start_pairing": {},
            "stop_pairing": {},
            "firmware_update": {"args": ["block"], "options": "block,allow"},
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
