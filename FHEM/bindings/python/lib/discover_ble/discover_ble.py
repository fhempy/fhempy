
import asyncio
import logging
from bleak import discover

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .. import fhem

class discover_ble:

    def __init__(self):
        self.hash = None
        self.blescanTask = None
        return

    async def runBleScan(self):
        while True:
            try:
                devices = await discover()
                for d in devices:
                    if d.name == "GfBT Project":
                        if not await fhem.checkIfDeviceExists(self.hash, "TYPE", "GFPROBT", "MAC", d.address):
                            logger.debug("create device: " + d.name + " / " + d.address + " / rssi: " + d.rssi)
                            await fhem.CommandDefine(self.hash, d.name + "_" d.address.replace(":", "") +  " GFPROBT '" + d.address + "'")
                    else if d.name == "CC-RT-BLE":
                        if not await fhem.checkIfDeviceExists(self.hash, "TYPE", "EQ3BT", "MAC", d.address):
                            logger.debug("create device: " + d.name + " / " + d.address + " / rssi: " + d.rssi)
                            await fhem.CommandDefine(self.hash, d.name + "_" d.address.replace(":", "") +  " EQ3BT '" + d.address + "'")
            except:
                logger.error("BLE Scan failed, retry in 300s", exc_info=True)
            await asyncio.sleep(300)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "active")
        await fhem.readingsEndUpdate(hash, 1)

        if self.blescanTask:
            self.blescanTask.cancel()

        self.blescanTask = asyncio.create_task(self.runBleScan())

        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        if self.blescanTask:
            self.blescanTask.cancel()
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return ("Unknown argument ?, choose one of ")