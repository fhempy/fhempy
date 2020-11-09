
import asyncio
import functools
import logging
import time

from bluepy.btle import Scanner, DefaultDelegate, BTLEException, ScanEntry

from .. import fhem,utils

class ble_presence:

    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.loop = asyncio.get_event_loop()

        self._scan_task = None

        self._name = ""
        self._rssi = 0
        self._address = ""
        self._presence = ""
        self._found = False
        return

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr.lower() == self._address.lower() and self._found is False:
            self._found = True
            if dev.getValueText(ScanEntry.SHORT_LOCAL_NAME):
                name = dev.getValueText(ScanEntry.SHORT_LOCAL_NAME)
            else:
                name = dev.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)
            asyncio.run_coroutine_threadsafe(self.task_update_reading(dev.addr, name, dev.rssi), self.loop)

    def thread_do_scan(self):
        self._found = False
        scanner = Scanner().withDelegate(self)
        try:
            scanner.scan(3.0)
        except Exception as ex:
            self.logger.error(f"Failed to scan: {ex}")
        if self._found is False:
            asyncio.run_coroutine_threadsafe(self.task_update_reading(self._address, "", 0))

    async def task_update_reading(self, address, name, rssi):
        if rssi == 0 and name == "":
            presence = "offline"
        else:
            presence = "online"
        
        if self._address != address:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "address", address, 1)
            self._address = address

        if self._rssi != rssi:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", str(rssi), 1)
            self._rssi = rssi

        if self._name != name and name is not None:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "name", name, 1)
            self._name = name

        if self._presence != presence:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", presence, 1)
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", presence, 1)
            self._presence = presence

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define p_mysmartphone PythonModule ble_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        self._scan_task = asyncio.create_task(self.scan_loop())

    async def scan_loop(self):
        while True:
            await utils.run_blocking(functools.partial(self.thread_do_scan))
            await asyncio.sleep(10)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self._scan_task:
            self._scan_task.cancel()