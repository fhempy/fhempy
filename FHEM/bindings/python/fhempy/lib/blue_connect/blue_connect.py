import asyncio
import codecs
import functools
import time

from .. import fhem, generic, utils
from ..core import ble

DEFAULT_TIMEOUT = 1


class blue_connect(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._ble_lock = asyncio.Lock()
        self._conn = None
        self.water_temp = "0"
        self.water_orp = "0"
        self.water_ph = "0"
        self.other_18 = ""
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
        self._conn = ble.BTLEConnection(
            self._mac,
            keep_connected=True,
        )
        self._conn.set_callback("all", self.received_notification)
        self.create_async_task(self.update_loop())
        self.create_async_task(self.keep_connected())

    async def Undefine(self, hash):
        if self._conn:
            self._conn.set_keep_connected(False)
        return await super().Undefine(self.hash)

    async def set_measure(self, hash, params):
        self.create_async_task(self.measure_once())

    def received_notification(self, data):
        self.raw_measurement = codecs.encode(data, "hex")
        raw_temp = int(self.raw_measurement[4:6] + self.raw_measurement[2:4], 16)
        self.water_temp = float(raw_temp) / 100

        raw_ph = int(self.raw_measurement[8:10] + self.raw_measurement[6:8], 16)
        self.water_ph = round((float(0x0800) - float(raw_ph)) / 232 + 7, 2)

        raw_orp = int(self.raw_measurement[12:14] + self.raw_measurement[10:12], 16)
        self.water_orp = round(float(raw_orp) / 4)

        raw_battery = int(self.raw_measurement[20:22] + self.raw_measurement[18:20], 16)
        self.battery = float(raw_battery) / 1000

    def blocking_measure(self):
        for cnt in range(0, 10):
            try:
                # enable notifications
                self._conn.write_characteristic(0x0014, b"\x01\x00")
                # start measuring
                self._conn.write_characteristic(0x0012, b"\x01", 60)
                break
            except Exception:
                self.logger.exception("Failed to write characteristics")
                time.sleep(10)

    def blocking_read_others(self):
        for cnt in range(0, 10):
            try:
                self.other_18 = self._conn.read_characteristic(0x18)
            except Exception:
                self.logger.exception("Failed to read characteristics")
                time.sleep(10)

    async def update_loop(self):
        while True:
            try:
                await self.measure_once()
            except asyncio.CancelledError:
                break
            except Exception:
                self.logger.exception("Failed to update readings")
            await asyncio.sleep(7200)

    async def keep_connected(self):
        while True:
            try:
                async with self._ble_lock:
                    await utils.run_blocking(
                        functools.partial(self.blocking_read_others)
                    )
            except asyncio.CancelledError:
                break
            except Exception:
                self.logger.exception("Failed to update readings")
            await asyncio.sleep(60)

    async def measure_once(self):
        self.water_temp = 0
        self.water_orp = 0
        self.water_ph = 0
        self.battery = 0

        async with self._ble_lock:
            await utils.run_blocking(functools.partial(self.blocking_measure))
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "unknown_handle_18", self.other_18)
        await fhem.readingsBulkUpdate(self.hash, "temperature", self.water_temp)
        await fhem.readingsBulkUpdate(self.hash, "ph", self.water_ph)
        await fhem.readingsBulkUpdate(self.hash, "orp", self.water_orp)
        await fhem.readingsBulkUpdate(self.hash, "raw", self.raw_measurement)
        await fhem.readingsBulkUpdate(self.hash, "battery", self.battery)

        state = []
        if self.water_ph < 7.2:
            state.append(
                f"Ph: {self.water_ph} too low, diff {round(7.2-self.water_ph, 2)}"
            )
            await fhem.readingsBulkUpdate(self.hash, "ph_state", "low")
        elif self.water_ph > 7.7:
            state.append(
                f"Ph: {self.water_ph} too high, diff {round(7.7-self.water_ph, 2)}"
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
