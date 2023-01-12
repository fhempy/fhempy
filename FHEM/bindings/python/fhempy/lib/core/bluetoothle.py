"""
A simple wrapper for bleak
Handles reconnection
"""
import asyncio

import bluetooth_adapters
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


class BluetoothLE:
    # keep connected (get manuf uuid every x seconds)
    # reset hci devices on errors
    # find by name
    # add bluetooth-auto-recovery
    def __init__(self, logger, address=None, name=None, keep_connected=True) -> None:
        self._disconnect_called = False

        self.logger = logger
        self.addr = address
        self.name = name
        self.device = None
        self.client = None
        self.keep_connected = keep_connected

    async def update_adapters(self):
        self.adapters = await bluetooth_adapters.get_bluetooth_adapters()
        adapters = bluetooth_adapters.get_adapters()
        await adapters.refresh()
        self.adapter_details = adapters.adapters

    async def find_device(self, timeout=30):
        await self.update_adapters()

        self.device = None
        for adapter in self.adapters:
            for i in range(1, 21):
                try:
                    self.device = await BleakScanner.find_device_by_address(
                        self.addr, timeout=timeout, adapter=adapter
                    )
                    self.logger.info(f"Device found via adapter {adapter}")
                    return adapter
                except asyncio.TimeoutError:
                    # nothing found
                    pass

                if not self.device:
                    await asyncio.sleep(20)

            else:
                self.logger.warning(f"Device not found via adapter {adapter}")

    def register_disconnect_listener(self, disconnect_listener):
        self.disconnect_listener = disconnect_listener

    async def connect(self, timeout=30):
        self._disconnect_called = True
        if self.client is None or not self.client.is_connected:
            adapter = await self.find_device(timeout=timeout)

            if self.device is None:
                if self.keep_connected:
                    return await self.connect()
                else:
                    self.logger.error("Device couldn't be found")
                    return

            self.client = BleakClient(
                self.device,
                disconnected_callback=self._disconnect_callback,
                timeout=timeout,
                adapter=adapter,
            )
            await self.client.connect()

        return self.client

    async def start_notify(self, uuid, callback):
        return await self.client.start_notify(uuid, callback)

    async def disconnect(self):
        self._disconnect_called = True
        await self.client.disconnect()

    def _disconnect_callback(self, client: BleakClient):
        if self.disconnect_listener:
            self.disconnect_listener(client)

        self.client = None
        self.device = None

        if self.keep_connected and not self._disconnect_called:
            self.logger.error("Device disconnected, reconnect now")
            asyncio.create_task(self.connect())
        else:
            self.logger.info("Device disconnected")

    @property
    def is_connected(self) -> bool:
        return self.client is not None and self.client.is_connected

    @property
    def device(self) -> BLEDevice:
        return self.device

    @property
    def client(self) -> BleakClient:
        return self.client
