
import asyncio
import functools
import time
import re

from bluepy.btle import BTLEDisconnectError, ScanEntry, Scanner

from .. import fhem, utils


class scanner:

    scanner_instance = None

    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self._mac_listener = {}
        self._mac_lastfound = {}
        self._scan_task = None
        self._scan_interval = 10
        self._iface = 0

    def get_instance(logger):
        if scanner.scanner_instance is None:
            scanner.scanner_instance = scanner(logger)
        return scanner.scanner_instance

    def register_mac_listener(self, mac, listener):
        self._mac_listener[mac.lower()] = listener
        if len(self._mac_listener) == 1:
            self._scan_task = asyncio.create_task(self.loop_scan())

    def unregister_mac_listener(self, mac):
        if mac in self._mac_listener:
            del self._mac_listener[mac]
        if len(self._mac_listener) == 0:
            self._scan_task.cancel()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        asyncio.run_coroutine_threadsafe(self.handle_discovery(dev, isNewDev, isNewData), self.loop)

    async def handle_discovery(self, dev, isNewDev, isNewData):
        if dev.addr.lower() in self._mac_listener:
            if isNewDev:
                self._mac_lastfound[dev.addr.lower()] = time.time()
                name = ""
                if dev.getValueText(ScanEntry.SHORT_LOCAL_NAME):
                    name = dev.getValueText(ScanEntry.SHORT_LOCAL_NAME)
                else:
                    name = dev.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)
                await self._mac_listener[dev.addr.lower()]("present", dev.addr.lower(), name, dev.rssi)

    def set_scan_interval(self, scan_interval):
        self._scan_interval = scan_interval

    def set_hci_device(self, hci_nr):
        self._iface = hci_nr

    async def loop_scan(self):
        while True:
            for mac in self._mac_lastfound:
                self._mac_lastfound[mac] = 0
            await utils.run_blocking(functools.partial(self._do_scan))
            for mac in self._mac_lastfound:
                if self._mac_lastfound[mac] == 0:
                    if mac in self._mac_listener:
                        await self._mac_listener[mac]("absent", mac, "", 0)
            await asyncio.sleep(self._scan_interval)

    def _do_scan(self):
        self.scanner = Scanner(self._iface).withDelegate(self)
        try:
            self.scanner.scan(3.0)
        except BTLEDisconnectError:
            pass
        except Exception as ex:
            self.logger.error(f"Failed to scan: {ex}")


class ble_presence:

    scanner = None

    def __init__(self, logger):
        self.logger = logger
        self.hash = None

        self._name = ""
        self._rssi = 0
        self._address = ""
        self._presence = ""
        self._found = False

        self._attr_list = {
            "scan_interval": {"default": 10, "format": "int"},
            "hci_device": {"default": "hci0"}
        }
        return

    async def update_readings(self, presence, address, name, rssi):
        if self._rssi != rssi:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", str(rssi), 1)
            self._rssi = rssi

        if name is not None and self._name != name and presence != "absent" and name != "":
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

        await utils.handle_define_attr(self._attr_list, self, hash)
        self._address = args[3]
        self.hash["MAC"] = args[3]

        scanner.get_instance(self.logger).register_mac_listener(self._address, self.update_readings)

    # FHEM FUNCTION
    async def Attr(self, hash, args, argsh):
        return await utils.handle_attr(self._attr_list, self, hash, args, argsh)

    async def set_attr_scan_interval(self, hash):
        scanner.get_instance(self.logger).set_scan_interval(self._attr_scan_interval)

    async def set_attr_hci_device(self, hash):
        hci_nr = re.search(r'\d+$', self._attr_hci_device)[0]
        scanner.get_instance(self.logger).set_hci_device(hci_nr)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        scanner.get_instance(self.logger).unregister_mac_listener(self._address)