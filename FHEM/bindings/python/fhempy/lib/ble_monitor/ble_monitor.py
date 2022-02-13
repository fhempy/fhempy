from .. import generic

import janus
from .hcidump import HCIdump

from .const import (
    CONF_DISCOVERY,
    CONF_NAME,
    CONF_MAC,
    CONF_DEVICES,
    CONF_ACTIVE_SCAN,
    CONF_BATT_ENTITIES,
    CONF_BT_AUTO_RESTART,
    CONF_BT_INTERFACE,
    CONF_DECIMALS,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_ENCRYPTION_KEY,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_DEVICE_TRACK,
    CONF_DEVICE_TRACKER_SCAN_INTERVAL,
    CONF_DEVICE_TRACKER_CONSIDER_HOME,
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
    DEFAULT_DEVICE_DECIMALS,
    DEFAULT_DEVICE_ENCRYPTION_KEY,
    DEFAULT_DEVICE_RESET_TIMER,
    DEFAULT_DEVICE_RESTORE_STATE,
    DEFAULT_DEVICE_TRACK,
    DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
    DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
    DEFAULT_DISCOVERY,
    DEFAULT_LOG_SPIKES,
    DEFAULT_PERIOD,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_RESTORE_STATE,
    DEFAULT_USE_MEDIAN,
)

from .bt_helpers import (
    DEFAULT_BT_INTERFACE,
    DEFAULT_HCI_INTERFACE,
)


class ble_monitor(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define miscale fhempy ble_monitor 11:22:33:44:55:66"

        config = {
            CONF_DEVICES: {
                CONF_MAC: args[3],
                CONF_UUID: None,
                CONF_NAME: "",
                CONF_DEVICE_DECIMALS: DEFAULT_DEVICE_DECIMALS,
                CONF_DEVICE_ENCRYPTION_KEY: DEFAULT_DEVICE_ENCRYPTION_KEY,
                CONF_DEVICE_USE_MEDIAN: DEFAULT_USE_MEDIAN,
                CONF_DEVICE_RESTORE_STATE: DEFAULT_DEVICE_RESTORE_STATE,
                CONF_DEVICE_RESET_TIMER: DEFAULT_DEVICE_RESET_TIMER,
                CONF_DEVICE_TRACK: DEFAULT_DEVICE_TRACK,
                CONF_DEVICE_TRACKER_SCAN_INTERVAL: DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
                CONF_DEVICE_TRACKER_CONSIDER_HOME: DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
            },
            CONF_ACTIVE_SCAN: DEFAULT_ACTIVE_SCAN,
            CONF_BATT_ENTITIES: DEFAULT_BATT_ENTITIES,
            CONF_BT_AUTO_RESTART: DEFAULT_BT_AUTO_RESTART,
            CONF_BT_INTERFACE: DEFAULT_BT_INTERFACE,
            CONF_DECIMALS: DEFAULT_DECIMALS,
            CONF_HCI_INTERFACE: DEFAULT_HCI_INTERFACE,
            CONF_GATEWAY_ID: "",
            CONF_PERIOD: DEFAULT_PERIOD,
            CONF_LOG_SPIKES: DEFAULT_LOG_SPIKES,
            CONF_REPORT_UNKNOWN: DEFAULT_REPORT_UNKNOWN,
            CONF_RESTORE_STATE: DEFAULT_RESTORE_STATE,
            CONF_USE_MEDIAN: DEFAULT_USE_MEDIAN,
            CONF_UUID: "",
            CONF_DISCOVERY: DEFAULT_DISCOVERY,
        }

        self.blemonitor = BLEmonitor(self.logger, config)
        self.blemonitor.start()
        self.create_async_task(self.update_readings())

    async def update_readings(self):
        while True:
            measured = await self.blemonitor.dataqueue["measuring"].get()
            self.logger.error(measured)

    async def Undefine(self, hash):
        self.blemonitor.shutdown_handler("Undefine")
        return await super().Undefine(hash)


class BLEmonitor:
    """BLE scanner."""

    def __init__(self, logger, config):
        """Init."""
        self.logger = logger
        self.dataqueue = {
            "binary": janus.Queue(),
            "measuring": janus.Queue(),
            "tracker": janus.Queue(),
        }
        self.config = config
        self.dumpthread = None

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
        self.dataqueue["binary"].sync_q.put_nowait(None)
        self.dataqueue["measuring"].sync_q.put_nowait(None)
        self.dataqueue["tracker"].sync_q.put_nowait(None)
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
        if self.dumpthread.is_alive():
            self.dumpthread.restart()
        else:
            self.start()
