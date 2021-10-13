import asyncio
import functools
import struct
import time

from .. import fhem, utils
from ..core.ble import BTLEConnection
from .. import generic

DEFAULT_TIMEOUT = 1

HANDLE_RW_PASSWORD = 0x0048
HANDLE_R_WATERING = 0x0015
HANDLE_W_WATERING = 0x0013
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
    0x0017,
    0x0019,
    0x001B,
    0x001D,
    0x001F,
    0x0021,
    0x0023,
    0x0031,
    0x0025,
    0x0027,
    0x0029,
    0x002B,
    0x002D,
    0x002F,
]


class gfprobt(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        set_conf = {
            "update": {"help": "Retrieve values from GF Pro BT"},
            "off": {"help": "Turn off watering"},
            "toggle": {"help": "Toggle on/off"},
            "on": {
                "args": ["onseconds"],
                "params": {
                    "onseconds": {"default": 0, "format": "int", "optional": True}
                },
                "help": (
                    "Turn on watering. You can use seconds as parameter to define the duration.<br>"
                    "Duration will be set directly on the device to have a safe switch off even if connectivity is broken"
                ),
            },
            "devicename": {"help": "Set the devicename of the irrigation control"},
            "adjust": {
                "help": "Adjust the timings with parameters:<br>percent<br>duration in minutes"
            },
            "eco": {"help": "Activate/decactivate eco mode"},
        }
        self.set_set_config(set_conf)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define irrigation_control fhempy gfprobt <MAC>"
        self._mac = args[3]
        self.hash["MAC"] = self._mac
        self._conn = BTLEConnection(
            self._mac,
            keep_connected=True,
            connection_established_callback=self.write_password,
        )
        self.create_async_task(self.update_loop())

    # write_password is running in another thread
    def write_password(self, mac):
        self._conn.write_characteristic(HANDLE_RW_PASSWORD, b"123456")

    async def set_update(self, hash, params):
        self.create_async_task(self.update_once())

    async def set_on(self, hash, params):
        onseconds = params["onseconds"]
        utils.run_blocking_task(functools.partial(self.blocking_on, onseconds))

    async def set_off(self, hash, params):
        utils.run_blocking_task(functools.partial(self.blocking_off))

    async def set_toggle(self, hash, params):
        utils.run_blocking_task(functools.partial(self.blocking_toggle))

    def blocking_on(self, onseconds):
        self.blocking_update_watering()
        if self._watering == 0:
            self.blocking_toggle()

    def blocking_off(self):
        self.blocking_update_watering()
        if self._watering == 1:
            self.blocking_toggle()

    def blocking_toggle(self):
        self._conn.write_characteristic(HANDLE_W_WATERING, b"\x00")
        self._conn.write_characteristic(HANDLE_W_WATERING, b"\x01")

    async def update_loop(self):
        while True:
            try:
                await self.update_once()
            except Exception:
                self.logger.exception("Failed to update readings")
            await asyncio.sleep(60)

    async def update_once(self):
        await utils.run_blocking(functools.partial(self.blocking_update))
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self._watering)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "watering", self._watering)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "batteryVoltage", self._battery
        )
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

    def blocking_update_watering(self):
        self._watering = struct.unpack(
            "<b", self._conn.read_characteristic(HANDLE_R_WATERING)
        )[0]

    def blocking_update(self):
        self.blocking_update_watering()
        self._battery = struct.unpack(
            "<h", self._conn.read_characteristic(HANDLE_R_BATTERY)
        )[0]
        self._temperature = struct.unpack(
            "<h", self._conn.read_characteristic(HANDLE_R_TEMPERATURE)
        )[0]
        self._min_temp = struct.unpack(
            "<h", self._conn.read_characteristic(HANDLE_R_MIN_TEMP)
        )[0]
        self._max_temp = struct.unpack(
            "<h", self._conn.read_characteristic(HANDLE_R_MAX_TEMP)
        )[0]
        self._firmware = self._conn.read_characteristic(HANDLE_R_FIRMWARE)
        self._firmware = str(self._firmware[1]) + "." + str(self._firmware[0])
        self._devname = self._conn.read_characteristic(HANDLE_RW_DEVNAME).decode(
            "utf-8"
        )
        self._eco = str(self._conn.read_characteristic(HANDLE_RW_ECO_PART1))
        self._eco += " " + str(self._conn.read_characteristic(HANDLE_RW_ECO_PART2))
        self._timeoffset = struct.unpack(
            "<I", self._conn.read_characteristic(HANDLE_RW_TIME_OFFSET)
        )[0]
        self._devmac = str(self._conn.read_characteristic(HANDLE_R_MAC))
        self._increasereduce = self._conn.read_characteristic(HANDLE_RW_INCREASEREDUCE)
        self._raw_timers = {}
        for handle_timer in HANDLE_RW_TIMERS:
            self._raw_timers[handle_timer] = self._conn.read_characteristic(
                handle_timer
            )
            self.logger.debug(self._raw_timers[handle_timer])

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
