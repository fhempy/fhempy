import asyncio
import janus
from fhempy.lib.ble_monitor.bt_helpers import (
    BT_INTERFACES,
    DEFAULT_BT_INTERFACE,
    DEFAULT_HCI_INTERFACE,
)
from fhempy.lib.ble_monitor.hcidump import HCIdump


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
        self.fhem_devices = {}
        self.receive_from_queues()

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
                asyncio.sleep(10)

    async def receive_from_tracker(self):
        while True:
            try:
                tracker = await self.dataqueue["tracker"].async_q.get()
                if "mac" in tracker and tracker["mac"].lower() in self.fhem_devices:
                    for fhem_dev in self.fhem_devices[tracker["mac"].lower()]:
                        await fhem_dev.received_data(tracker)
            except Exception:
                self.logger.exception("Failed to receive_from_tracker")
                asyncio.sleep(10)

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
        """Start receiving broadcasts."""
        self.logger.debug("Spawning HCIdump thread")
        self.dumpthread = HCIdump(
            self.logger,
            config=self.config,
            dataqueue=self.dataqueue,
        )
        self.dumpthread.start()

    def stop(self):
        """Stop HCIdump thread(s)."""
        result = True
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
        """Restart scanning."""
        # wait 3s for other restarts and restart only once
        self.stop()
        self.start()
