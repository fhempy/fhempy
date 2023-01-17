import asyncio
import codecs

from .. import fhem, generic
from ..core import bluetoothle

# handle: 0x0002, char properties: 0x02, char value handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
# handle: 0x0004, char properties: 0x02, char value handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
# handle: 0x0006, char properties: 0x02, char value handle: 0x0007, uuid: 00002a04-0000-1000-8000-00805f9b34fb
# handle: 0x0008, char properties: 0x02, char value handle: 0x0009, uuid: 00002aa6-0000-1000-8000-00805f9b34fb
# handle: 0x000a, char properties: 0x02, char value handle: 0x000b, uuid: 00002ac9-0000-1000-8000-00805f9b34fb
# handle: 0x000d, char properties: 0x20, char value handle: 0x000e, uuid: 00002a05-0000-1000-8000-00805f9b34fb
# handle: 0x0011, char properties: 0x08, char value handle: 0x0012, uuid: f3300002-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0013, char properties: 0x10, char value handle: 0x0014, uuid: f3300003-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0016, char properties: 0x02, char value handle: 0x0017, uuid: f3300004-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0018, char properties: 0x08, char value handle: 0x0019, uuid: f3300005-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x001a, char properties: 0x10, char value handle: 0x001b, uuid: f3300006-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x001d, char properties: 0x08, char value handle: 0x001e, uuid: f3300007-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x001f, char properties: 0x0a, char value handle: 0x0020, uuid: f3300008-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0021, char properties: 0x0a, char value handle: 0x0022, uuid: f3300009-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0023, char properties: 0x0a, char value handle: 0x0024, uuid: f3300010-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0025, char properties: 0x02, char value handle: 0x0026, uuid: f3300011-0a29-b060-c591-bc4763b5c000
# handle: 0x0027, char properties: 0x08, char value handle: 0x0028, uuid: f3300020-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x002a, char properties: 0x02, char value handle: 0x002b, uuid: f3320010-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x002c, char properties: 0x02, char value handle: 0x002d, uuid: f3320011-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x002e, char properties: 0x02, char value handle: 0x002f, uuid: f3320015-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0030, char properties: 0x02, char value handle: 0x0031, uuid: f3320016-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0032, char properties: 0x02, char value handle: 0x0033, uuid: f3320017-f0a2-9b06-0c59-1bc4763b5c00
# handle: 0x0034, char properties: 0x0a, char value handle: 0x0035, uuid: f3320018-f0a2-9b06-0c59-1bc4763b5c00


class blue_connect(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._ble_lock = asyncio.Lock()
        self.task_update_loop = None
        self.ble_dev = None

        self.water_temp = "0"
        self.water_orp = "0"
        self.water_ph = "0"
        self.water_salt = "0"
        self.water_conductivity = "0"
        self.rssi = ""
        set_conf = {
            "measure": {"help": "Send signal to start measuring"},
            "restart": {"help": "Restart blue connect"},
        }
        self.set_set_config(set_conf)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define my_blueconnect fhempy blue_connect MAC"
        self._mac = args[3]
        self.hash["MAC"] = self._mac

        self.ble_dev = bluetoothle.BluetoothLE(self.logger, self.hash, self._mac)
        self.ble_dev.register_notification_listener(self.received_notification)

        self.task_update_loop = self.create_async_task(self.update_loop())

    async def Undefine(self, hash):
        if self.task_update_loop:
            self.task_update_loop.cancel()
        if self.ble_dev:
            await self.ble_dev.disconnect()
        return await super().Undefine(self.hash)

    async def set_measure(self, hash, params):
        self.create_async_task(self.measure_once())

    async def set_restart(self, hash, params):
        self.create_async_task(self.restart())

    def received_notification(self, uuid, data):
        self.raw_measurement = codecs.encode(data, "hex")
        raw_temp = int(self.raw_measurement[4:6] + self.raw_measurement[2:4], 16)
        self.water_temp = float(raw_temp) / 100

        raw_ph = int(self.raw_measurement[8:10] + self.raw_measurement[6:8], 16)
        self.water_ph = round((float(0x0800) - float(raw_ph)) / 232 + 7, 2)

        raw_orp = int(self.raw_measurement[12:14] + self.raw_measurement[10:12], 16)
        self.water_orp = round(float(raw_orp) / 4)

        raw_salt = int(self.raw_measurement[16:18] + self.raw_measurement[14:16], 16)
        self.water_salt = round(float(raw_salt) / 25, 2)

        raw_conductivity = int(
            self.raw_measurement[20:22] + self.raw_measurement[18:20], 16
        )
        self.water_conductivity = round(float(raw_conductivity) / 0.4134)
        self.rssi = self.ble_dev.device.rssi

        self.create_async_task(self.update_readings())

    async def measure(self):
        # start measure
        await self.ble_dev.write_gatt_char(
            "F3300002-F0A2-9B06-0C59-1BC4763B5C00", b"\x01"
        )

    async def restart(self):
        # start measure
        await self.ble_dev.write_gatt_char(
            "f3300020-f0a2-9b06-0c59-1bc4763b5c00", b"\x31"
        )
        await self.ble_dev.disconnect()
        await asyncio.sleep(1)
        await self.ble_dev.connect()

    async def update_loop(self):
        if not self.ble_dev.is_connected:
            await self.ble_dev.connect()
        await self.ble_dev.connected.wait()

        while True:
            try:
                await self.measure_once()
            except asyncio.CancelledError:
                self.logger.info("Stopping update loop")
                return
            except Exception:
                self.logger.exception("Failed to update readings")
            await asyncio.sleep(7200)

    async def measure_once(self):
        async with self._ble_lock:
            self.water_temp = 0
            self.water_orp = 0
            self.water_ph = 0
            self.water_conductivity = 0
            self.water_salt = 0

            await self.measure()

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "rssi", self.rssi)
        await fhem.readingsBulkUpdate(self.hash, "temperature", self.water_temp)
        await fhem.readingsBulkUpdate(self.hash, "ph", self.water_ph)
        await fhem.readingsBulkUpdate(self.hash, "orp", self.water_orp)
        await fhem.readingsBulkUpdate(self.hash, "raw", self.raw_measurement)
        await fhem.readingsBulkUpdate(
            self.hash, "conductivity", self.water_conductivity
        )
        await fhem.readingsBulkUpdate(self.hash, "salinity", self.water_salt)

        state = []
        if self.water_ph < 7.2:
            state.append(
                f"Ph: {self.water_ph} too low, diff {round(7.2-self.water_ph, 2)}"
            )
            await fhem.readingsBulkUpdate(self.hash, "ph_state", "low")
        elif self.water_ph > 7.6:
            state.append(
                f"Ph: {self.water_ph} too high, diff {round(7.6-self.water_ph, 2)}"
            )
            await fhem.readingsBulkUpdate(self.hash, "ph_state", "high")
        else:
            await fhem.readingsBulkUpdate(self.hash, "ph_state", "ok")

        if self.water_orp < 550:
            state.append(
                f"ORP: {self.water_orp} too low, diff {round(550-self.water_orp)}"
            )
            await fhem.readingsBulkUpdate(self.hash, "orp_state", "low")
        elif self.water_orp > 650:
            state.append(
                f"ORP: {self.water_orp} too high, diff {round(650-self.water_orp)}"
            )
            await fhem.readingsBulkUpdate(self.hash, "orp_state", "high")
        else:
            await fhem.readingsBulkUpdate(self.hash, "orp_state", "ok")

        if len(state) == 0:
            state = ["ok"]

        await fhem.readingsBulkUpdate(self.hash, "state", ", ".join(state))

        await fhem.readingsEndUpdate(self.hash, 1)
