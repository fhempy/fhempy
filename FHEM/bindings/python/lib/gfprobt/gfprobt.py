
import asyncio
import codecs
import functools
import binascii
import time

from bluepy import btle

from .. import fhem
from .. import utils

DEFAULT_TIMEOUT = 1

HANDLE_READWRITE_PASSWORD = 0x0048
HANDLE_READ_WATERING = 0x0015
HANDLE_READ_BATTERY = 0x0039
HANDLE_READ_TEMPERATURE = 0x003b
HANDLE_READ_MIN_TEMP = 0x003d
HANDLE_READ_MAX_TEMP = 0x003f
HANDLE_READ_FIRMWARE = 0x004e
HANDLE_READ_DEVNAME = 0x0052
HANDLE_READ_ECO_PART1 = 0x0033
HANDLE_READ_ECO_PART2 = 0x0045
HANDLE_READWRITE_TIME_OFFSET = 0x0035
HANDLE_READ_MAC = 0x004a
HANDLE_READ_INCREASEREDUCE = 0x0043
HANDLE_WRITE_COMMITCODE = 0x0037
HANDLE_READ_TIMERS = ["0x0017", "0x0019", "0x001b", "0x001d", "0x001f", "0x0021", "0x0023",
                    "0x0031", "0x0025", "0x0027", "0x0029", "0x002b", "0x002d", "0x002f"]

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
        await fhem.readingsSingleUpdate(self.hash, "state", self._watering, 1)

    def blocking_connect(self):
        self._conn.connect()

    def blocking_update(self):
        self._conn.connect(self._mac, addrType=btle.ADDR_TYPE_RANDOM)
        value = binascii.hexlify(b"123456")
        self._conn.writeCharacteristic(HANDLE_READWRITE_PASSWORD, value)
        self._watering = self._conn.readCharacteristic(HANDLE_READ_WATERING)
        self.logger.debug(self._watering)
        self._battery = self._conn.readCharacteristic(HANDLE_READ_BATTERY)
        self.logger.debug(self._battery)
        self._temperature = self._conn.readCharacteristic(HANDLE_READ_TEMPERATURE)
        self.logger.debug(self._temperature)
        self._min_temp = self._conn.readCharacteristic(HANDLE_READ_MIN_TEMP)
        self._max_temp = self._conn.readCharacteristic(HANDLE_READ_MAX_TEMP)
        self._firmware = self._conn.readCharacteristic(HANDLE_READ_FIRMWARE)
        self._devname = self._conn.readCharacteristic(HANDLE_READ_DEVNAME)
        self._eco = self._conn.readCharacteristic(HANDLE_READ_ECO_PART1)
        self._eco += " " + self._conn.readCharacteristic(HANDLE_READ_ECO_PART2)
        self._timeoffset = self._conn.readCharacteristic(HANDLE_READWRITE_TIME_OFFSET)
        self._devmac = self._conn.readCharacteristic(HANDLE_READ_MAC)
        self._increasereduce = self._conn.readCharacteristic(HANDLE_READ_INCREASEREDUCE)
        self._raw_timers = {}
        for handle_timer in HANDLE_READ_TIMERS:
            self._raw_timers[handle_timer] = self._conn.readCharacteristic(handle_timer)
            self.logger.debug(self._raw_timers[handle_timer])
        self._conn.disconnect()

    def write_offset(self):
        now = time.localtime()
        sec_since_mon = now.tm_wday * 3600 * 24 + now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
        sec_since_mon = struct.pack("<I", sec_since_mon)
        self._conn.writeCharacteristic(HANDLE_READWRITE_TIME_OFFSET, sec_since_mon)

    def commit_code(self):
        self._conn.writeCharacteristic(HANDLE_WRITE_COMMITCODE, b'00')
        self._conn.writeCharacteristic(HANDLE_WRITE_COMMITCODE, b'01')