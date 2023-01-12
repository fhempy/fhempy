import asyncio
import codecs

from bleak import BleakClient

from .. import fhem, generic
from ..core import bluetoothle


class blue_connect(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._ble_lock = asyncio.Lock()
        self.task_update_loop = None

        self.water_temp = "0"
        self.water_orp = "0"
        self.water_ph = "0"
        self.water_salt = "0"
        self.water_conductivity = "0"
        self.rssi = ""
        set_conf = {
            "measure": {"help": "Send signal to start measuring"},
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

        self.ble_dev = bluetoothle.BluetoothLE(
            self.logger, self._mac, keep_connected=True
        )
        self.ble_dev.register_disconnect_listener(self.handle_disconnect())

        self.task_update_loop = self.create_async_task(self.update_loop())

    async def Undefine(self, hash):
        if self.task_update_loop:
            self.task_update_loop.cancel()
        if self.ble_dev:
            await self.ble_dev.disconnect()
        return await super().Undefine(self.hash)

    async def set_measure(self, hash, params):
        self.create_async_task(self.measure_once())

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

    def handle_disconnect(self, _: BleakClient):
        self.create_async_task(
            fhem.readingsSingleUpdate(self.hash, "connection", "disconnected", 1)
        )

    async def measure(self):
        await fhem.readingsSingleUpdate(self.hash, "connection", "connecting", 1)
        await self.ble_dev.connect()

        if self.ble_dev.is_connected:
            # register notify
            await self.ble_dev.client.start_notify(
                "F3300003-F0A2-9B06-0C59-1BC4763B5C00",
                self.received_notification,
            )
            # start measure
            await self.ble_dev.client.write_gatt_char(
                "F3300002-F0A2-9B06-0C59-1BC4763B5C00", b"\x01"
            )
            await fhem.readingsSingleUpdate(self.hash, "connection", "connected", 1)

    async def update_loop(self):
        while True:
            try:
                await self.measure_once()
            except asyncio.CancelledError:
                break
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
