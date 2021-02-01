import asyncio
import time

from fhempy.lib import fhem
from fhempy.lib.generic import FhemModule

attr_settings = {
    "lumi.sensor_magnet.v2": {
        "devStateIcon": "1:fts_door_open\@red 0:fts_door\@green",
        "stateFormat": "contact",
        "icon": "tuer_fenster_kontakt",
    },
    "lumi.sensor_magnet.aq2": {
        "devStateIcon": "1:fts_door_open\@red 0:fts_door\@green",
        "stateFormat": "contact",
        "icon": "tuer_fenster_kontakt",
    },
    "lumi.sensor_wleak.aq1": {
        "icon": "sani_water_tap",
        "devStateIcon": "0:message_ok 1:humidity@red",
        "stateFormat": "moisture",
    },
    "lumi.sensor_ht.v1": {
        "stateFormat": "temperature °C, humidity %",
        "icon": "temp_temperature",
    },
    "lumi.sensor_ht.v2": {
        "stateFormat": "temperature °C, humidity %, pressure hPa",
        "icon": "temp_temperature",
    },
    "lumi.weather.v1": {
        "stateFormat": "temperature °C, humidity %, pressure hPa",
        "icon": "temp_temperature",
    },
    "lumi.sensor_motion.v1": {
        "stateFormat": "motion",
        "devStateIcon": "1:motion_detector\@red 0:motion_detector\@green",
        "icon": "people_sensor",
    },
    "lumi.sensor_motion.v2": {
        "stateFormat": "motion",
        "devStateIcon": "1:motion_detector\@red 0:motion_detector\@green",
        "icon": "people_sensor",
    },
    "lumi.gateway.mgl03": {
        "devStateIcon": "online:it_wifi\@green offline:it_wifi\@red",
        "icon": "tradfri_gateway",
    },
}


class BaseDevice(FhemModule):
    def __init__(self, logger, gateway):
        super().__init__(logger)
        self._gateway = gateway
        self.last_update = 0
        self.logger = logger
        self.create_async_task(self.offline_check())

    def set_hash(self, hash):
        self.hash = hash

    async def initialize(self, device):
        self._xg3_device = device
        for attr in attr_settings[device["model"]]:
            if await fhem.AttrVal(self.hash["NAME"], attr, "") == "":
                await fhem.CommandAttr(
                    self.hash,
                    f"{self.hash['NAME']} {attr} {attr_settings[self._xg3_device['model']][attr]}",
                )

        for reading in device:
            if reading == "init":
                await self.update(device["init"])
                continue
            elif reading == "params":
                continue
            else:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, reading, device[reading], 1
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
            if reading == "added_device":
                pass
            else:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading.replace(" ", "_"), str(data[reading])
                )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def offline_check(self):
        while True:
            if time.time() - self.last_update > 3700:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "offline", 1
                )
            await asyncio.sleep(300)
