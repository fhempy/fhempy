import asyncio

from .. import fhem
from .. import fhem_pythonbinding as fhepy
from .. import generic

# imports for dynamical usage, do NOT remove
from .devices.gateway import Gateway  # noqa: F401
from .devices.sensor import (  # noqa: F401
    ContactSensor,
    HTSensor,
    MotionSensor,
    WaterLeakSensor,
)

device_type_mapping = {
    "lumi.sensor_magnet": "ContactSensor",
    "lumi.sensor_magnet.v2": "ContactSensor",
    "lumi.sensor_magnet.aq2": "ContactSensor",
    "lumi.sensor_wleak": "WaterLeakSensor",
    "lumi.sensor_wleak.aq1": "WaterLeakSensor",
    "lumi.sensor_ht": "HTSensor",
    "lumi.sensor_ht.v1": "HTSensor",
    "lumi.sensor_ht.v2": "HTSensor",
    "lumi.weather": "HTSensor",
    "lumi.weather.v1": "HTSensor",
    "lumi.sensor_motion": "MotionSensor",
    "lumi.sensor_motion.v1": "MotionSensor",
    "lumi.sensor_motion.v2": "MotionSensor",
    "lumi.gateway": "Gateway",
    "lumi.gateway.mgl03": "Gateway",
}


class xiaomi_gateway3_device(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._fhempy_gateway = None
        self._fhempy_device = None
        self.loop = asyncio.get_event_loop()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        if len(args) < 5:
            return (
                "Usage: define devname fhempy xiaomi_gateway3_device"
                " <GATEWAY_NAME> <DID>"
            )

        self.gw_name = args[3]
        self.did = args[4]

        hash["GATEWAY"] = self.gw_name
        hash["DID"] = self.did

        # change gateway did to 0, we just needed it for DID internals
        if self.did.find("0x") >= 0:
            self.did = "lumi.0"

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)

        self.create_async_task(self.connect_gw())

    async def connect_gw(self):
        while self._fhempy_gateway is None:
            self._fhempy_gateway = fhepy.getFhemPyDeviceByName(self.gw_name)
            if self._fhempy_gateway:
                try:
                    await self._fhempy_gateway.register_device(self, self.update)
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "online", 1
                    )
                except Exception:
                    self._fhempy_gateway = None
                    pass
            else:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", f"gateway {self.gw_name} not found", 1
                )
            await asyncio.sleep(10)

    async def initialize(self, device):
        if self._fhempy_gateway is None:
            return

        # first update, set attributes and device readings like model, sid, ...
        if device["model"] not in device_type_mapping:
            self.logger.error(
                f"{device['model']} not yet supported, please report an issue here: "
                f"https://github.com/dominikkarall/fhempy/issues"
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "state", f"unsupported device: {device['model']}", 1
            )
            return
        # create device based on device model
        self._fhempy_device = globals()[device_type_mapping[device["model"]]](
            self.logger, self._fhempy_gateway
        )
        self._fhempy_device.set_hash(self.hash)
        await self._fhempy_device.initialize(device)
        self._fhempy_gateway.gateway3.set_entity(self._fhempy_device)
        self._fhempy_gateway.gateway3.set_stats(self._fhempy_device)

    def update(self, data):
        if self._fhempy_device is not None:
            self._fhempy_device.update(data)

    # FHEM functions which will be redirected to device type class
    async def FW_detailFn(self, hash, args, argsh):
        if self._fhempy_device is None:
            return await super().FW_detailFn(hash, args, argsh)
        return await self._fhempy_device.FW_detailFn(hash, args, argsh)

    async def Set(self, hash, args, argsh):
        if self._fhempy_device is None:
            return await super().Set(hash, args, argsh)
        return await self._fhempy_device.Set(hash, args, argsh)

    async def Attr(self, hash, args, argsh):
        if self._fhempy_device is None:
            return await super().Attr(hash, args, argsh)
        return await self._fhempy_device.Attr(hash, args, argsh)

    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self._fhempy_device is not None:
            await self._fhempy_device.Undefine(hash)
