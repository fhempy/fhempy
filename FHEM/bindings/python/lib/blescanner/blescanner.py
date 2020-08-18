
import asyncio
import logging
from bleak import discover

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .. import fhem

class blescanner:

    def __init__(self):
        self.hash = None
        self.blescanTask = None
        return

    async def runBleScan(self):
        while True:
            try:
                devices = await discover()
                await fhem.readingsBeginUpdate(self.hash)
                for d in devices:
                    await fhem.readingsBulkUpdateIfChanged(self.hash, d.address + "_rssi", d.rssi)
                    await fhem.readingsBulkUpdateIfChanged(self.hash, d.address + "_name", d.name)
                await fhem.readingsEndUpdate(self.hash, 1)
            except:
                logger.error("BLE Scan failed, retry in 30s", exc_info=True)
            await asyncio.sleep(30)

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