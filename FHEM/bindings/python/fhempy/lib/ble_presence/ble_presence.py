import asyncio
import functools
import re
import time

from bluepy.btle import (ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM, AssignedNumbers,
                         BluepyHelper, BTLEDisconnectError, Peripheral,
                         ScanEntry, Scanner)
from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class PeripheralTimeout(Peripheral):
    def __init__(
        self, deviceAddr=None, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None
    ):
        BluepyHelper.__init__(self)
        self._serviceMap = None  # Indexed by UUID
        (self.deviceAddr, self.addrType, self.iface) = (None, None, None)

        if isinstance(deviceAddr, ScanEntry):
            self._connect(
                deviceAddr.addr, deviceAddr.addrType, deviceAddr.iface, timeout
            )
        elif deviceAddr is not None:
            self._connect(deviceAddr, addrType, iface, timeout)

    def _connect(self, addr, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if len(addr.split(":")) != 6:
            raise ValueError("Expected MAC address, got %s" % repr(addr))
        if addrType not in (ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM):
            raise ValueError(
                "Expected address type public or random, got {}".format(addrType)
            )
        self._startHelper(iface)
        self.addr = addr
        self.addrType = addrType
        self.iface = iface
        if iface is not None:
            self._writeCmd("conn %s %s %s\n" % (addr, addrType, "hci" + str(iface)))
        else:
            self._writeCmd("conn %s %s\n" % (addr, addrType))
        rsp = self._getResp("stat", timeout)
        if rsp is None:
            raise BTLEDisconnectError(
                "Timed out while trying to connect to peripheral %s, addr type: %s"
                % (addr, addrType),
                rsp,
            )
        while rsp["state"][0] == "tryconn":
            rsp = self._getResp("stat", timeout)
        if rsp["state"][0] != "conn":
            self._stopHelper()
            raise BTLEDisconnectError(
                "Failed to connect to peripheral %s, addr type: %s" % (addr, addrType),
                rsp,
            )

    def connect(self, addr, addrType=ADDR_TYPE_PUBLIC, iface=None, timeout=None):
        if isinstance(addr, ScanEntry):
            self._connect(addr.addr, addr.addrType, addr.iface, timeout)
        elif addr is not None:
            self._connect(addr, addrType, iface, timeout)


class scanner:

    scanner_instance = None

    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self._mac_listener = {}
        self._mac_lastfound = {}
        self._scan_task = None
        self._scan_interval = 10
        self._scan_duration = 10
        self._iface = 0

    @staticmethod
    def get_instance(logger):
        if scanner.scanner_instance is None:
            scanner.scanner_instance = scanner(logger)
        return scanner.scanner_instance

    def register_mac_listener(self, mac, listener):
        self._mac_listener[mac.lower()] = listener
        if self._scan_task is None:
            self._scan_task = asyncio.create_task(self.loop_scan())

    def unregister_mac_listener(self, mac):
        if mac in self._mac_listener:
            del self._mac_listener[mac]
        if len(self._mac_listener) == 0:
            if self._scan_task:
                self._scan_task.cancel()
                self._scan_task = None

    def handleDiscovery(self, dev, isNewDev, isNewData):
        asyncio.run_coroutine_threadsafe(
            self.handle_discovery(dev, isNewDev, isNewData), self.loop
        ).result()

    async def handle_discovery(self, dev, isNewDev, isNewData):
        if dev.addr.lower() in self._mac_listener:
            self.logger.debug(f"found {dev.addr.lower()}")
            if isNewDev:
                self._mac_lastfound[dev.addr.lower()] = time.time()
                name = ""
                if dev.getValueText(ScanEntry.SHORT_LOCAL_NAME):
                    name = dev.getValueText(ScanEntry.SHORT_LOCAL_NAME)
                else:
                    name = dev.getValueText(ScanEntry.COMPLETE_LOCAL_NAME)
                await getattr(self._mac_listener[dev.addr.lower()], "update_readings")(
                    "present", dev.addr.lower(), name, dev.rssi
                )

    def set_scan_interval(self, scan_interval):
        self._scan_interval = scan_interval

    def set_scan_duration(self, scan_duration):
        self._scan_duration = scan_duration

    def set_hci_device(self, hci_nr):
        self._iface = hci_nr

    async def loop_scan(self):
        while True:
            for mac in self._mac_lastfound:
                self._mac_lastfound[mac] = 0
            try:
                await utils.run_blocking(functools.partial(self._do_scan))
            except Exception:
                self.logger.error("Failed to do scan")
            for mac in self._mac_listener:
                try:
                    if mac not in self._mac_lastfound or self._mac_lastfound[mac] == 0:
                        await getattr(self._mac_listener[mac], "update_readings")(
                            "absent", mac, "", 0
                        )
                    else:
                        await getattr(
                            self._mac_listener[mac], "check_update_characteristics"
                        )()
                except Exception:
                    self.logger.exception("Failed to handle updates after scan")
            await asyncio.sleep(self._scan_interval)

    def _do_scan(self):
        self.scanner = Scanner(self._iface).withDelegate(self)
        try:
            self.scanner.scan(self._scan_duration)
        except BTLEDisconnectError:
            return
        except Exception as ex:
            self.logger.error(f"Failed to scan: {ex}")


class ble_presence(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.hash = None

        self._name = ""
        self._rssi = 0
        self._address = ""
        self._presence = ""
        self._found = False
        self._peripheral = PeripheralTimeout()
        self._last_char_update = 0
        self._hci_nr = 0

        self._attr_scan_interval = 10
        self._attr_hci_device = "hci0"
        self._attr_scan_duration = 10
        self._attr_read_characteristics = "battery"

        self._attr_list = {
            "scan_interval": {"default": 10, "format": "int"},
            "hci_device": {"default": "hci0"},
            "scan_duration": {"default": 10, "format": "int"},
            "read_characteristics": {
                "default": "battery",
                "options": "all,off,battery",
            },
        }
        self.set_attr_config(self._attr_list)

    async def update_readings(self, presence, address, name, rssi):
        if self._rssi != rssi:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", str(rssi), 1)
            self._rssi = rssi

        if (
            name is not None
            and self._name != name
            and presence != "absent"
            and name != ""
        ):
            await fhem.readingsSingleUpdateIfChanged(self.hash, "name", name, 1)
            self._name = name

        if self._presence != presence:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", presence, 1)
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", presence, 1)
            self._presence = presence

    async def check_update_characteristics(self):
        if self._attr_read_characteristics == "off":
            return

        if time.time() - self._last_char_update > 7200 and self._presence == "present":
            try:
                await self.update_characteristics()
            except Exception:
                self.logger.error("Failed to update characteristics")

    async def update_characteristics(self):
        try:
            await utils.run_blocking(
                functools.partial(
                    self._peripheral.connect,
                    self._address,
                    ADDR_TYPE_PUBLIC,
                    self._hci_nr,
                    5,
                )
            )
        except Exception:
            return
        services = await utils.run_blocking(
            functools.partial(self._peripheral.getServices)
        )
        await fhem.readingsBeginUpdate(self.hash)
        try:
            if self._attr_read_characteristics == "all":
                for service in services:
                    for char in service.getCharacteristics():
                        if char.supportsRead():
                            reading = (
                                service.uuid.getCommonName().replace(" ", "")
                                + "_"
                                + char.uuid.getCommonName().replace(" ", "")
                            )
                            if char.uuid.getCommonName() == "Battery Level":
                                reading = "battery"
                            try:
                                val = await utils.run_blocking(
                                    functools.partial(char.read)
                                )
                            except Exception:
                                val = "failed"
                            try:
                                if len(val) == 1:
                                    val = ord(val)
                                else:
                                    val = val.decode("ascii")
                            except Exception:
                                val = val.hex()
                                pass
                            await fhem.readingsBulkUpdateIfChanged(
                                self.hash, reading, val
                            )
            else:
                service = self._peripheral.getServiceByUUID(
                    AssignedNumbers.batteryService
                )
                char = service.getCharacteristics(AssignedNumbers.batteryLevel)
                batt = ord(char[0].read())
                await fhem.readingsBulkUpdateIfChanged(self.hash, "battery", batt)
            self._last_char_update = time.time()
        except Exception:
            self.logger.error("Failed to get charachteristics")
        self._peripheral.disconnect()
        await fhem.readingsEndUpdate(self.hash, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define p_mysmartphone PythonModule ble_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        scanner.get_instance(self.logger).register_mac_listener(self._address, self)

    async def set_attr_scan_interval(self, hash):
        scanner.get_instance(self.logger).set_scan_interval(self._attr_scan_interval)

    async def set_attr_scan_duration(self, hash):
        scanner.get_instance(self.logger).set_scan_duration(self._attr_scan_duration)

    async def set_attr_hci_device(self, hash):
        self._hci_nr = re.search(r"\d+$", self._attr_hci_device)[0]
        scanner.get_instance(self.logger).set_hci_device(self._hci_nr)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        scanner.get_instance(self.logger).unregister_mac_listener(self._address)
        await super().Undefine(hash)
