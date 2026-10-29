import logging

from aiohomekit.controller.ble.controller import BleController

from ..core.ble_scanner import BleScanner

logger = logging.getLogger(__name__)


class SharedScanBleController(BleController):
    """aiohomekit's HAP-BLE controller on the Bluetooth scan all fhempy
    modules share. Its own BleakScanner would compete with that scan, an
    adapter only runs one discovery at a time."""

    async def async_start(self):
        self._shared_scanner = BleScanner.get_instance(logger)
        self._shared_scanner.add_callback(self._device_detected)

    async def async_stop(self, *args):
        self._shared_scanner.remove_callback(self._device_detected)
