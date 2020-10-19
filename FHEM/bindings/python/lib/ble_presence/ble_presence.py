
import asyncio
import logging
from bleak import BleakScanner

from .. import fhem

class ble_presence:

    def __init__(self, logger):
        self.logger = logger
        # disable bleak discovery messages
        logging.getLogger("bleak.backends.bluezdbus.discovery").setLevel(logging.ERROR)
        self.hash = None
        self.blescanTask = None
        return

    async def runBleScan(self):
        while True:
            new_state = "absent"
            try:
                device = await BleakScanner.find_device_by_address(self._address)
                if device:
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "name", device.name, 1)
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", device.rssi, 1)
                    new_state = "present"
            except:
                self.logger.exception("BleakScanner failed")
            await self.update_state(new_state)
            if new_state == "absent":
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(60)

    async def update_state(self, new_state):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", new_state, 1)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", new_state, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define p_mysmartphone PythonModule ble_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]
        await self.update_state("absent")

        if self.blescanTask:
            self.blescanTask.cancel()
        self.blescanTask = asyncio.create_task(self.runBleScan())
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        if self.blescanTask:
            self.blescanTask.cancel()
        return