
import asyncio
import logging
import bluetooth
import functools
from bt_proximity import BluetoothRSSI

from .. import fhem
from .. import utils

class bt_presence:

    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.btscan_task = None
        return

    def lookup_name(self, mac):
        return bluetooth.lookup_name(mac, timeout=5)

    async def run_bt_scan(self):
        while True:
            new_state = "absent"
            try:
                # check max 3 times for device_name
                for i in range(0,2):
                    device_name = await utils.run_blocking(functools.partial(self.lookup_name, self._address))
                    if device_name:
                        break

                if device_name:
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "name", device_name, 1)
                    self._btrssi = BluetoothRSSI(self._address)
                    rssi = await utils.run_blocking(functools.partial(self._btrssi.request_rssi))
                    self._btrssi.close()
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", rssi[0], 1)
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
            return "Usage: define p_mysmartphone PythonModule bt_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]
        await self.update_state("absent")

        if self.btscan_task:
            self.btscan_task.cancel()
        self.btscan_task = asyncio.create_task(self.run_bt_scan())
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        if self.btscan_task:
            self.btscan_task.cancel()