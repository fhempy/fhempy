import asyncio
import time

import janus
from fhempy.lib.ble_monitor.bt_helpers import (
    BT_INTERFACES,
    DEFAULT_BT_INTERFACE,
    DEFAULT_HCI_INTERFACE,
)
from fhempy.lib.ble_monitor.hcidump import HCIdump

from ..core import ble_proxy, ble_scanner, hci_claims
from .advertisement import (  # noqa: F401 (used by other modules)
    MAX_AD_LEN,
    _advertisement_data,
    advertisement_data,
    hci_packet,
)
from .const import (
    CONF_DEVICE_ENCRYPTION_KEY,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_DEVICES,
    CONF_ACTIVE_SCAN,
    CONF_BATT_ENTITIES,
    CONF_BT_AUTO_RESTART,
    CONF_BT_INTERFACE,
    CONF_DECIMALS,
    CONF_HCI_INTERFACE,
    CONF_GATEWAY_ID,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_USE_MEDIAN,
    CONF_UUID,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_BATT_ENTITIES,
    DEFAULT_BT_AUTO_RESTART,
    DEFAULT_DECIMALS,
    DEFAULT_DISCOVERY,
    DEFAULT_LOG_SPIKES,
    DEFAULT_PERIOD,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_RESTORE_STATE,
    DEFAULT_USE_MEDIAN,
)

# devices register one after another at startup, restart the scan only once
RESTART_DELAY = 3
# scan attribute: the shared scan of core/ble_scanner (BlueZ) or an own raw
# HCI scan, only for systems without BlueZ
SCAN_SHARED = "shared"
SCAN_HCI = "hci"
# warn if the shared scan doesn't work after this time (s)
SHARED_CHECK_DELAY = 120


class BLEmonitor:
    """BLE scanner."""

    __instance = None

    @staticmethod
    def getInstance(logger):
        """Static access method."""
        if BLEmonitor.__instance is None:
            BLEmonitor.__instance = BLEmonitor(logger)
        return BLEmonitor.__instance

    def __init__(self, logger):
        """Init."""
        self.logger = logger
        self.dataqueue = {
            "binary": janus.Queue(),
            "measuring": janus.Queue(),
            "tracker": janus.Queue(),
        }
        self.config = {
            CONF_DEVICES: [],
            CONF_ACTIVE_SCAN: DEFAULT_ACTIVE_SCAN,
            CONF_BATT_ENTITIES: DEFAULT_BATT_ENTITIES,
            CONF_BT_AUTO_RESTART: DEFAULT_BT_AUTO_RESTART,
            CONF_BT_INTERFACE: [],
            CONF_DECIMALS: DEFAULT_DECIMALS,
            CONF_HCI_INTERFACE: [],
            CONF_GATEWAY_ID: "",
            CONF_PERIOD: DEFAULT_PERIOD,
            CONF_LOG_SPIKES: DEFAULT_LOG_SPIKES,
            CONF_REPORT_UNKNOWN: DEFAULT_REPORT_UNKNOWN,
            CONF_RESTORE_STATE: DEFAULT_RESTORE_STATE,
            CONF_USE_MEDIAN: DEFAULT_USE_MEDIAN,
            CONF_UUID: "",
            CONF_DISCOVERY: DEFAULT_DISCOVERY,
        }
        self.dumpthread = None
        self._loop = asyncio.get_running_loop()
        # shared scan: (service_data, manufacturer_data) per address
        self._previous = {}
        self._shared = False
        self._shared_adapters = {}
        self._shared_check = None
        self.fhem_devices = {}
        self._restart_requested = 0
        self._restart_task = None
        self.receive_from_queues()
        # advertisements of ESPHome Bluetooth proxies
        ble_proxy.add_raw_callback(self.proxy_advertisement)
        # e.g. Matter pairing via Bluetooth resets the adapter
        hci_claims.add_listener(self.hci_claim_changed)

    def hci_claim_changed(self, adapter, claimed):
        if claimed or adapter not in self.config[CONF_HCI_INTERFACE]:
            return
        if not self.fhem_devices:
            return
        self.logger.info(f"hci{adapter} is free again, restarting the scan")
        self.restart()

    def scan_mode(self):
        """SCAN_HCI if a device asks for the own raw HCI scan."""
        for devices in self.fhem_devices.values():
            for device in devices:
                scan = getattr(device, "scan", None)
                if scan is not None and scan() == SCAN_HCI:
                    return SCAN_HCI
        return SCAN_SHARED

    def shared_advertisement(self, device, advertisement):
        """Advertisement of a local adapter from the shared scan."""
        dumpthread = self.dumpthread
        if dumpthread is None or not self.fhem_devices:
            return
        address = device.address.upper()
        previous = self._previous.get(address)
        data, sent_service, sent_manufacturer = _advertisement_data(
            advertisement, previous
        )
        self._previous[address] = (
            dict(advertisement.service_data or {}),
            dict(advertisement.manufacturer_data or {}),
            sent_service,
            sent_manufacturer,
        )
        rssi = advertisement.rssi if advertisement.rssi is not None else -127
        dumpthread.process_hci_events(
            hci_packet(address, ble_scanner.address_type(device), rssi, data)
        )

    def _attach_shared(self):
        """Registers at the shared scan, in the event loop."""
        scanner = ble_scanner.BleScanner.get_instance(self.logger)
        # proxies send their raw advertisements to proxy_advertisement
        scanner.add_callback(self.shared_advertisement, proxies=False)
        adapters = {
            ble_scanner.normalize_adapter(hci)
            for hci in self.config[CONF_HCI_INTERFACE]
        }
        adapters.discard(None)
        for adapter in list(self._shared_adapters):
            if adapter not in adapters:
                scanner.remove_callback(self._shared_adapters.pop(adapter))
        for adapter in adapters:
            if adapter not in self._shared_adapters:
                # only keeps the scan of the adapter running, the
                # advertisements of all adapters go to shared_advertisement
                def keep(device, advertisement):
                    return None

                self._shared_adapters[adapter] = keep
                scanner.add_callback(keep, proxies=False, adapter=adapter)
        if self._shared_check is None or self._shared_check.done():
            self._shared_check = asyncio.create_task(self._check_shared())

    def _detach_shared(self):
        scanner = ble_scanner.BleScanner.instance
        if scanner is None:
            return
        scanner.remove_callback(self.shared_advertisement)
        for keep in self._shared_adapters.values():
            scanner.remove_callback(keep)
        self._shared_adapters.clear()
        self._previous.clear()

    async def _check_shared(self):
        await asyncio.sleep(SHARED_CHECK_DELAY)
        scanner = ble_scanner.BleScanner.instance
        if not self._shared or scanner is None:
            return
        if scanner.scanning in ("no adapter", "failed") and not ble_proxy.active():
            self.logger.warning(
                "ble_monitor uses the shared Bluetooth scan of fhempy, which "
                f"doesn't work ({scanner.scanning}). Without BlueZ set "
                "attr <device> scan hci for an own HCI scan."
            )

    def proxy_advertisement(self, address, address_type, rssi, data, proxy_name):
        dumpthread = self.dumpthread
        if dumpthread is None or not self.fhem_devices:
            return
        dumpthread.process_hci_events(
            hci_packet(address, address_type, rssi, data), gateway_id=proxy_name
        )

    def receive_from_queues(self):
        self.task_measuring = asyncio.create_task(self.receive_from_measuring())
        self.task_tracker = asyncio.create_task(self.receive_from_tracker())

    async def receive_from_measuring(self):
        while True:
            try:
                measuring = await self.dataqueue["measuring"].async_q.get()
                if "mac" in measuring and measuring["mac"].lower() in self.fhem_devices:
                    for fhem_dev in self.fhem_devices[measuring["mac"].lower()]:
                        await fhem_dev.received_data(measuring)
            except Exception:
                self.logger.exception("Failed to receive_from_measuring")
                await asyncio.sleep(10)

    async def receive_from_tracker(self):
        while True:
            try:
                tracker = await self.dataqueue["tracker"].async_q.get()
                if "mac" in tracker and tracker["mac"].lower() in self.fhem_devices:
                    for fhem_dev in self.fhem_devices[tracker["mac"].lower()]:
                        await fhem_dev.received_data(tracker)
            except Exception:
                self.logger.exception("Failed to receive_from_tracker")
                await asyncio.sleep(10)

    def register_device(self, fhemdevice):
        simple_mac = fhemdevice.mac().replace(":", "").lower()
        if simple_mac not in self.fhem_devices:
            self.fhem_devices[simple_mac] = []
        self.fhem_devices[simple_mac].append(fhemdevice)
        self.config[CONF_DEVICES].append(
            {
                CONF_MAC: fhemdevice.mac(),
                CONF_DEVICE_ENCRYPTION_KEY: fhemdevice.encryption_key(),
            }
        )

        self.update_hci_interface(fhemdevice.hci())

        self.restart()

    def update_hci_interface(self, intf):
        self.config[CONF_HCI_INTERFACE] = []
        self.config[CONF_BT_INTERFACE] = []
        for fhem_mac in self.fhem_devices:
            for fhem_dev in self.fhem_devices[fhem_mac]:
                self.config[CONF_HCI_INTERFACE].append(fhem_dev.hci())
                self.config[CONF_BT_INTERFACE].append(BT_INTERFACES[fhem_dev.hci()])

    def unregister_device(self, fhemdevice):
        simple_mac = fhemdevice.mac().replace(":", "").lower()
        try:
            self.fhem_devices[simple_mac].remove(fhemdevice)
        except Exception:
            pass
        try:
            self.config[CONF_DEVICES].remove(
                {
                    CONF_MAC: fhemdevice.mac(),
                    CONF_DEVICE_ENCRYPTION_KEY: fhemdevice.encryption_key(),
                }
            )
        except Exception:
            pass

        self.update_hci_interface(fhemdevice.hci())

        self.restart()

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        self.logger.debug("Shutdown event fired: %s", event)
        self.stop()

    def start(self):
        """Start receiving broadcasts. Can run in a thread (restart)."""
        self.dumpthread = HCIdump(
            self.logger,
            config=self.config,
            dataqueue=self.dataqueue,
        )
        if self.scan_mode() == SCAN_HCI:
            self.logger.debug("Spawning HCIdump thread")
            self.dumpthread.start()
        elif self.fhem_devices:
            # the HCIdump only parses, the shared scan delivers
            self._shared = True
            self._loop.call_soon_threadsafe(self._attach_shared)

    def stop(self):
        """Stop HCIdump thread(s)."""
        result = True
        if self._shared:
            self._shared = False
            self._loop.call_soon_threadsafe(self._detach_shared)
        if self.dumpthread is None:
            self.logger.debug("BLE monitor stopped")
            return True
        if self.dumpthread.is_alive():
            self.dumpthread.join()
            if self.dumpthread.is_alive():
                result = False
                self.logger.error(
                    "Waiting for the HCIdump thread to finish took too long! (>10s)"
                )
        self.logger.debug("BLE monitor stopped")
        return result

    def restart(self):
        """Restart scanning RESTART_DELAY seconds after the last request.

        Every registered device requests a restart. Restarting right away
        stopped the scan thread while it was still starting ('Event loop
        stopped before Future completed') and joining the thread blocked
        the event loop each time."""
        self._restart_requested = time.monotonic()
        if self._restart_task is None or self._restart_task.done():
            self._restart_task = asyncio.create_task(
                self._delayed_restart(), name="ble_monitor_restart"
            )

    async def _delayed_restart(self):
        while True:
            wait = self._restart_requested + RESTART_DELAY - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
                continue
            started = time.monotonic()
            await asyncio.to_thread(self._restart_now)
            if self._restart_requested <= started:
                return

    def _restart_now(self):
        self.stop()
        self.start()
