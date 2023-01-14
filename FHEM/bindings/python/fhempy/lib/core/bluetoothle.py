"""
A simple wrapper for bleak
Handles reconnection
"""
import asyncio

import bluetooth_adapters
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from .. import fhem


class BluetoothLE:
    # keep connected (get manuf uuid every x seconds)
    # reset hci devices on errors
    # find by name
    # add bluetooth-auto-recovery
    def __init__(
        self, logger, device_hash, address=None, name=None, keep_connected=True
    ) -> None:
        self._disconnect_called = False
        self._device = None
        self._client = None
        self._dev_hash = device_hash

        self.disconnect_listener = None
        self.connected_listener = None

        self.logger = logger
        self.addr = address
        self.name = name
        self.keep_connected = keep_connected

    async def update_adapters(self):
        self.adapters = await bluetooth_adapters.get_bluetooth_adapters()
        adapters = bluetooth_adapters.get_adapters()
        await adapters.refresh()
        self.adapter_details = adapters.adapters

    async def find_device(self, timeout=30, adapter=None):
        self._device = None

        try:
            self._device = await BleakScanner.find_device_by_address(
                self.addr, timeout=timeout, adapter=adapter
            )
            self.logger.info(f"Device found via adapter {adapter}")
        except (asyncio.TimeoutError, BleakError):
            # nothing found
            self._device = None

    def register_disconnect_listener(self, disconnect_listener):
        self.disconnect_listener = disconnect_listener

    def register_connection_established_listener(self, connected_listener):
        self.connected_listener = connected_listener

    async def connect(self, timeout=30, max_retries=20):
        # get latest adapter list
        await self.update_adapters()

        await fhem.readingsSingleUpdate(self._dev_hash, "connection", "connecting", 1)
        self._disconnect_called = False

        if self._client and self._client.is_connected:
            return

        for i in range(0, max_retries):
            for adapter in self.adapters:
                await self.find_device(timeout=timeout, adapter=adapter)
                if not self._device:
                    # device not found
                    await asyncio.sleep(20)
                    continue

                await fhem.readingsSingleUpdateIfChanged(
                    self._dev_hash, "connection_adapter", adapter, 1
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self._dev_hash,
                    "connection_adapter_details",
                    self.adapter_details[adapter]["manufacturer"]
                    + ": "
                    + self.adapter_details[adapter]["address"],
                    1,
                )

                self._client = BleakClient(
                    self._device,
                    disconnected_callback=self._disconnect_callback,
                    timeout=timeout,
                    adapter=adapter,
                )
                try:
                    await self._client.connect()
                except (asyncio.TimeoutError, BleakError):
                    pass
                if self._client.is_connected:
                    await fhem.readingsSingleUpdate(
                        self._dev_hash, "connection", "connected", 1
                    )
                    if self.connected_listener:
                        await self.connected_listener()
                    return
                else:
                    await asyncio.sleep(20)
                    continue

        # connection failed
        if self.keep_connected:
            return await self.connect()
        else:
            self.logger.error("Device couldn't be found")
            await fhem.readingsSingleUpdate(self._dev_hash, "connection", "failed", 1)
        return

    async def write_gatt_char(self, uuid, data):
        if not self.is_connected:
            await self.connect()
        await self._client.write_gatt_char(uuid, data)

    async def read_gatt_char(self, uuid):
        if not self.is_connected:
            await self.connect()
        return await self._client.read_gatt_char(uuid)

    async def disconnect(self):
        self._disconnect_called = True
        await self._client.disconnect()

    def _disconnect_callback(self, client: BleakClient):
        asyncio.create_task(self.async_disconnected(client))

    async def async_disconnected(self, client: BleakClient):
        await fhem.readingsSingleUpdate(self._dev_hash, "connection", "disconnected", 1)
        if self.disconnect_listener:
            await self.disconnect_listener(client)

        self._client = None
        self._device = None

        if self.keep_connected and not self._disconnect_called:
            self.logger.error("Device disconnected, reconnect now")
            await self.connect()
        else:
            self.logger.info("Device disconnected")

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected

    @property
    def device(self) -> BLEDevice:
        return self._device

    @property
    def client(self) -> BleakClient:
        return self._client
