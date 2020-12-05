import asyncio
import codecs
import functools
import binascii
import time
import struct

from bluepy import btle

from .. import fhem
from .. import utils

DEFAULT_TIMEOUT = 1

HANDLE_RW_PASSWORD = 0x0048
HANDLE_RW_WATERING = 0x0015
HANDLE_R_BATTERY = 0x0039
HANDLE_R_TEMPERATURE = 0x003B
HANDLE_R_MIN_TEMP = 0x003D
HANDLE_R_MAX_TEMP = 0x003F
HANDLE_R_FIRMWARE = 0x004E
HANDLE_RW_DEVNAME = 0x0052
HANDLE_RW_ECO_PART1 = 0x0033
HANDLE_RW_ECO_PART2 = 0x0045
HANDLE_RW_TIME_OFFSET = 0x0035
HANDLE_R_MAC = 0x004A
HANDLE_RW_INCREASEREDUCE = 0x0043
HANDLE_W_COMMITCODE = 0x0037
HANDLE_RW_TIMERS = [
    "0x0017",
    "0x0019",
    "0x001b",
    "0x001d",
    "0x001f",
    "0x0021",
    "0x0023",
    "0x0031",
    "0x0025",
    "0x0027",
    "0x0029",
    "0x002b",
    "0x002d",
    "0x002f",
]


class gfprobt:
    def __init__(self, logger):
        self.logger = logger
        self._conn = btle.Peripheral()
        self._conn.withDelegate(self)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._mac = args[3]
        self.hash["MAC"] = self._mac
        asyncio.create_task(self.update())
        return "Module not ready yet"

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return

    async def update(self):
        await utils.run_blocking(functools.partial(self.blocking_update))
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self._watering)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "watering", self._watering)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "battery", self._battery)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "temperature", self._temperature
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "min_temperature", self._min_temp
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "max_temperature", self._max_temp
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, "firmware", self._firmware)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "devname", self._devname)
        await fhem.readingsEndUpdate(self.hash, 1)

    def blocking_connect(self):
        self._conn.connect()

    def blocking_update(self):
        self._conn.connect(self._mac)
        self._conn.writeCharacteristic(HANDLE_RW_PASSWORD, b"123456")
        self._watering = struct.unpack(
            "<b", self._conn.readCharacteristic(HANDLE_RW_WATERING)
        )[0]
        self._battery = struct.unpack(
            "<h", self._conn.readCharacteristic(HANDLE_R_BATTERY)
        )[0]
        self._temperature = struct.unpack(
            "<h", self._conn.readCharacteristic(HANDLE_R_TEMPERATURE)
        )[0]
        self._min_temp = struct.unpack(
            "<h", self._conn.readCharacteristic(HANDLE_R_MIN_TEMP)
        )[0]
        self._max_temp = struct.unpack(
            "<h", self._conn.readCharacteristic(HANDLE_R_MAX_TEMP)
        )[0]
        self._firmware = self._conn.readCharacteristic(HANDLE_R_FIRMWARE)
        self._firmware = self._firmware[1] + "." + self._firmware[0]
        self._devname = self._conn.readCharacteristic(HANDLE_RW_DEVNAME).decode("utf-8")
        self._eco = self._conn.readCharacteristic(HANDLE_RW_ECO_PART1)
        self._eco += " " + self._conn.readCharacteristic(HANDLE_RW_ECO_PART2)
        self._timeoffset = struct.unpack(
            "<I", self._conn.readCharacteristic(HANDLE_RW_TIME_OFFSET)
        )[0]
        self._devmac = self._conn.readCharacteristic(HANDLE_R_MAC)
        self._increasereduce = self._conn.readCharacteristic(HANDLE_RW_INCREASEREDUCE)
        self._raw_timers = {}
        for handle_timer in HANDLE_RW_TIMERS:
            self._raw_timers[handle_timer] = self._conn.readCharacteristic(handle_timer)
            self.logger.debug(self._raw_timers[handle_timer])
        self._conn.disconnect()

    def write_offset(self):
        now = time.localtime()
        sec_since_mon = (
            now.tm_wday * 3600 * 24 + now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
        )
        sec_since_mon = struct.pack("<I", sec_since_mon)
        self._conn.writeCharacteristic(HANDLE_RW_TIME_OFFSET, sec_since_mon)

    def commit_code(self):
        self._conn.writeCharacteristic(HANDLE_W_COMMITCODE, b"00")
        self._conn.writeCharacteristic(HANDLE_W_COMMITCODE, b"01")
