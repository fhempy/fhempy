import asyncio
import functools
import re
import time

from bluepy.btle import (
    ADDR_TYPE_PUBLIC,
    ADDR_TYPE_RANDOM,
    AssignedNumbers,
    BluepyHelper,
    BTLEDisconnectError,
    Peripheral,
    ScanEntry,
)
from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from ..core.ble_scanner import MODE_INTERVAL, BleScanner, paused


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


READING_INTERVAL = 10


class presence_tracker:
    """Presence of the tags from the shared Bluetooth scan (core/ble_scanner).
    A tag is absent if it wasn't seen for absent_timeout seconds."""

    tracker_instance = None

    def __init__(self, logger):
        self.logger = logger
        self._mac_listener = {}
        self._lastfound = {}
        self._lastupdate = {}
        self._check_task = None
        self._scanner = BleScanner.get_instance(logger)

    @staticmethod
    def get_instance(logger):
        if presence_tracker.tracker_instance is None:
            presence_tracker.tracker_instance = presence_tracker(logger)
        return presence_tracker.tracker_instance

    def register_mac_listener(self, mac, listener):
        self._mac_listener[mac.lower()] = listener
        self._scanner.add_callback(self.handle_advertisement)
        if self._check_task is None:
            self._check_task = asyncio.create_task(self.check_loop())

    def unregister_mac_listener(self, mac):
        # registered in lower case
        self._mac_listener.pop(mac.lower(), None)
        if len(self._mac_listener) == 0:
            self._scanner.remove_callback(self.handle_advertisement)
            if self._check_task:
                self._check_task.cancel()
                self._check_task = None

    def handle_advertisement(self, device, advertisement):
        mac = device.address.lower()
        listener = self._mac_listener.get(mac)
        if listener is None:
            return
        now = time.monotonic()
        self._lastfound[mac] = now
        # tags advertise every second, the readings are updated every 10s
        if (
            listener._presence == "present"
            and now - self._lastupdate.get(mac, 0) < READING_INTERVAL
        ):
            return
        self._lastupdate[mac] = now
        listener.create_async_task(
            listener.update_readings(
                "present",
                mac,
                advertisement.local_name or device.name or "",
                advertisement.rssi,
            )
        )

    def absent_after(self, listener):
        timeout = listener._attr_absent_timeout
        if self._scanner.effective_mode == MODE_INTERVAL:
            # a tag can only be seen once per scan
            timeout = max(timeout, self._scanner.interval + 30)
        return timeout

    async def check_loop(self):
        while True:
            await asyncio.sleep(5)
            now = time.monotonic()
            for mac, listener in list(self._mac_listener.items()):
                try:
                    lastfound = self._lastfound.get(mac, 0)
                    if now - lastfound > self.absent_after(listener):
                        await listener.update_readings("absent", mac, "", 0)
                    else:
                        await listener.check_update_characteristics()
                except Exception:
                    self.logger.exception("Failed to update presence")


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
        self._errors = utils.ErrorLogger(logger)

        self._attr_absent_timeout = 60
        self._attr_hci_device = "hci0"
        self._attr_read_characteristics = "battery"

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
                self._errors.success()
            except Exception:
                self._errors.failed("Failed to read characteristics, retry in 10min")
                # don't try to connect on every scan
                self._last_char_update = time.time() - 7200 + 600

    async def update_characteristics(self):
        # the shared scan pauses while connected
        async with paused():
            await self._read_characteristics()

    async def _read_characteristics(self):
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
        except BTLEDisconnectError as exc:
            raise ConnectionError(str(exc)) from exc
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
        finally:
            self._peripheral.disconnect()
            await fhem.readingsEndUpdate(self.hash, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self._attr_list = {
            "absent_timeout": {
                "default": 60,
                "format": "int",
                "help": "Seconds without Bluetooth advertisement until the tag "
                "is absent (default 60). The Bluetooth scan is shared with "
                "autodiscovery, see its attribute ble.",
            },
            "hci_device": {
                "default": "hci0",
                "help": "Adapter used to read the battery level.",
            },
            "read_characteristics": {
                "default": "battery",
                "options": "all,off,battery",
            },
        }
        await self.set_attr_config(self._attr_list)

        if len(args) < 4:
            return "Usage: define p_mysmartphone fhempy ble_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        presence_tracker.get_instance(self.logger).register_mac_listener(
            self._address, self
        )

    async def set_attr_hci_device(self, hash):
        self._hci_nr = re.search(r"\d+$", self._attr_hci_device)[0]

    # FHEM FUNCTION
    async def Undefine(self, hash):
        presence_tracker.get_instance(self.logger).unregister_mac_listener(
            self._address
        )
        await super().Undefine(hash)
