from fhempy.lib.xiaomi_gateway3_device.devices.base import BaseDevice


class Gateway(BaseDevice):
    def __init__(self, logger, gateway):
        super().__init__(logger, gateway)
        set_config = {"start_pairing": {}, "stop_pairing": {}}
        self.set_set_config(set_config)

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
