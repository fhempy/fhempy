from ..generic import FhemModule
import asyncio
import time

from .. import fhem
from ..xiaomi_gateway3 import xiaomi_gateway3
from .. import fhem_pythonbinding as fhepy

attr_settings = {
    "lumi.sensor_magnet.v2": {
        "devStateIcon": "1:fts_door_open\@red 0:fts_door\@green",
        "stateFormat": "contact",
        "icon": "tuer_fenster_kontakt",
    },
    "lumi.sensor_ht.v1": {
        "stateFormat": "temperature °C, humidity %",
        "icon": "temp_temperature",
    },
    "lumi.sensor_ht.v2": {
        "stateFormat": "temperature °C, humidity %, pressure kPa",
        "icon": "temp_temperature",
    },
    "lumi.sensor_motion.v1": {
        "devStateIcon": "motion:motion_detector\@red off:motion_detector\@green no_motion:motion_detector\@green",
        "icon": "people_sensor",
    },
    "lumi.gateway.mgl03": {
        "stateFormat": "presence",
        "devStateIcon": "online:it_wifi\@green offline:it_wifi\@red",
        "icon": "tradfri_gateway",
    },
}


class xiaomi_gateway3_device(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.gateway = None
        self.device_details = None
        self.last_update = 0
        self.loop = asyncio.get_event_loop()
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self.hash = hash

        if len(args) < 5:
            return "Usage: define devname PythonModule xiaomi_gateway3_device <GATEWAY_NAME> <DID>"

        self.gw_name = args[3]
        self.did = args[4]

        hash["GATEWAY"] = self.gw_name
        hash["DID"] = self.did

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)

        self.create_async_task(self.connect_gw())
        self.offline_check_task = self.create_async_task(self.offline_check())

        return ""

    async def offline_check(self):
        while True:
            if time.time() - self.last_update > 3700:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "offline", 1
                )
            await asyncio.sleep(300)

    async def connect_gw(self):
        while self.gateway is None:
            self.gateway = fhepy.getFhemPyDeviceByName(self.gw_name)
            if self.gateway:
                try:
                    await self.gateway.register_device(self, self.update)
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "online", 1
                    )
                except:
                    self.gateway = None
                    pass
            else:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", f"gateway {self.gw_name} not found", 1
                )
            await asyncio.sleep(10)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return

    async def initialize(self, device):
        # first update, set attributes and device readings like model, sid, ...
        if self.device_details is None:
            self.device_details = device
            if self.device_details["model"] in attr_settings:
                for attr in attr_settings[self.device_details["model"]]:
                    if await fhem.AttrVal(self.hash["NAME"], attr, "") == "":
                        await fhem.CommandAttr(
                            self.hash,
                            f"{self.hash['NAME']} {attr} {attr_settings[self.device_details['model']][attr]}",
                        )
            for reading in self.device_details:
                if reading == "init":
                    await self.update(self.device_details["init"])
                    continue
                elif reading == "params":
                    continue
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, reading, self.device_details[reading], 1
                    )

    async def update(self, data):
        self.logger.debug(f"update call {str(data)}")
        self.last_update = time.time()
        if data is None:
            return

        await fhem.readingsBeginUpdate(self.hash)
        # device is online
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "online")
        # update data
        for reading in data:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, reading.replace(" ", "_"), str(data[reading])
            )
        await fhem.readingsEndUpdate(self.hash, 1)
