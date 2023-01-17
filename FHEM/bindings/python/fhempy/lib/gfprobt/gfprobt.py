import asyncio
import struct
import time

from .. import fhem, generic
from ..core import bluetoothle

DEFAULT_TIMEOUT = 1

HANDLE_RW_PASSWORD = 0x0048 - 1
HANDLE_R_WATERING = 0x0015 - 1
HANDLE_W_WATERING = 0x0013 - 1
HANDLE_R_BATTERY = 0x0039 - 1
HANDLE_R_TEMPERATURE = 0x003B - 1
HANDLE_R_MIN_TEMP = 0x003D - 1
HANDLE_R_MAX_TEMP = 0x003F - 1
HANDLE_R_FIRMWARE = 0x004E - 1
HANDLE_RW_DEVNAME = 0x0052 - 1
HANDLE_RW_ECO_PART1 = 0x0033 - 1
HANDLE_RW_ECO_PART2 = 0x0045 - 1
HANDLE_RW_TIME_OFFSET = 0x0035 - 1
HANDLE_R_MAC = 0x004A - 1
HANDLE_RW_INCREASEREDUCE = 0x0043 - 1
HANDLE_W_COMMITCODE = 0x0037 - 1
HANDLE_RW_TIMERS = [
    0x0017 - 1,
    0x0019 - 1,
    0x001B - 1,
    0x001D - 1,
    0x001F - 1,
    0x0021 - 1,
    0x0023 - 1,
    0x0031 - 1,
    0x0025 - 1,
    0x0027 - 1,
    0x0029 - 1,
    0x002B - 1,
    0x002D - 1,
    0x002F - 1,
]


class gfprobt(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._ble_lock = asyncio.Lock()
        self._conn = None
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
                    "Turn on watering. You can use seconds as parameter to set the duration.<br>"
                    "Duration will be set directly on the device to have a safe switch off even if connectivity is broken"
                ),
            },
            "devicename": {"help": "Set the devicename of the irrigation control"},
            "adjust": {
                "args": ["percentage", "duration"],
                "params": {
                    "percentage": {"default": 0, "format": "int"},
                    "duration": {"default": 360, "format": " int", "optional": True},
                },
                "help": "Adjust the timings with parameters:<br>percentage<br>duration in hours",
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
        self._conn = bluetoothle.BluetoothLE(
            self.logger,
            self.hash,
            self._mac,
        )
        self.create_async_task(self.update_loop())

    async def Undefine(self, hash):
        if self._conn:
            await self._conn.disconnect()
        return await super().Undefine(self.hash)

    # write_password is running in another thread
    async def write_password(self):
        await self._conn.write_gatt_char(HANDLE_RW_PASSWORD, b"123456")

    async def set_update(self, hash, params):
        self.create_async_task(self.update_once())

    async def set_on(self, hash, params):
        onseconds = params["onseconds"]
        self.create_async_task(self._ble_set(self.async_on(onseconds)))

    async def set_off(self, hash, params):
        self.create_async_task(self._ble_set(self.async_off()))

    async def set_toggle(self, hash, params):
        self.create_async_task(self._ble_set(self.async_toggle()))

    async def set_adjust(self, hash, params):
        self.create_async_task(
            self._ble_set((self.async_adjust(params["percentage"], params["duration"])))
        )

    async def _ble_set(self, fct):
        async with self._ble_lock:
            await fct

    async def async_on(self, onseconds):
        await self.async_update_watering()
        if self._watering == 0:
            await self.async_toggle()

    async def async_off(self):
        await self.async_update_watering()
        if self._watering == 1:
            await self.async_toggle()

    async def async_toggle(self):
        await self._conn.write_gatt_char(HANDLE_W_WATERING, b"\x00")
        await self._conn.write_gatt_char(HANDLE_W_WATERING, b"\x01")

    async def async_adjust(self, percentage, duration):
        duration_sec = duration * 60 * 60

        duration_hex = duration_sec.to_bytes(6, "little")
        percentage_hex = percentage.to_bytes(2, "little")
        await self._conn.write_gatt_char(
            HANDLE_RW_INCREASEREDUCE, duration_hex + percentage_hex
        )

        await self.write_offset()
        await self.commit_code()

    async def update_loop(self):
        self._conn.register_connection_established_listener(self.write_password())
        await self._conn.connect()
        while True:
            try:
                await self.update_once()
            except asyncio.CancelledError:
                break
            except Exception:
                self.logger.exception("Failed to update readings")
            await asyncio.sleep(60)

    async def update_once(self):
        async with self._ble_lock:
            await self.async_update()
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "state", "on" if self._watering == 1 else "off"
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, "watering", self._watering)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "adjust_hours", self._adjust_hours
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "adjust_percentage", self._adjust_perc
        )
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

    async def async_update_watering(self):
        self._watering = struct.unpack(
            "<b", await self._conn.read_gatt_char(HANDLE_R_WATERING)
        )[0]

    async def async_update(self):
        await self.async_update_watering()
        self._battery = struct.unpack(
            "<h", await self._conn.read_gatt_char(HANDLE_R_BATTERY)
        )[0]
        self._temperature = struct.unpack(
            "<h", await self._conn.read_gatt_char(HANDLE_R_TEMPERATURE)
        )[0]
        self._min_temp = struct.unpack(
            "<h", await self._conn.read_gatt_char(HANDLE_R_MIN_TEMP)
        )[0]
        self._max_temp = struct.unpack(
            "<h", await self._conn.read_gatt_char(HANDLE_R_MAX_TEMP)
        )[0]
        self._firmware = await self._conn.read_gatt_char(HANDLE_R_FIRMWARE)
        self._firmware = str(self._firmware[1]) + "." + str(self._firmware[0])
        self._devname = await self._conn.read_gatt_char(HANDLE_RW_DEVNAME).decode(
            "utf-8"
        )
        self._eco = await self._conn.read_gatt_char(HANDLE_RW_ECO_PART1)
        self._eco += await self._conn.read_gatt_char(HANDLE_RW_ECO_PART2)
        self._timeoffset = struct.unpack(
            "<I", await self._conn.read_gatt_char(HANDLE_RW_TIME_OFFSET)
        )[0]
        self._devmac = str(await self._conn.read_gatt_char(HANDLE_R_MAC))
        self._increasereduce = await self._conn.read_gatt_char(HANDLE_RW_INCREASEREDUCE)
        self._adjust_hours = struct.unpack("<I", self._increasereduce[0:4])[0] / 3600
        self._adjust_perc = struct.unpack("<h", self._increasereduce[4:])[0]
        self._raw_timers = {}
        for handle_timer in HANDLE_RW_TIMERS:
            self._raw_timers[handle_timer] = await self._conn.read_gatt_char(
                handle_timer
            )
            self.logger.debug(self._raw_timers[handle_timer])

    async def write_offset(self):
        now = time.localtime()
        sec_since_mon = (
            now.tm_wday * 3600 * 24 + now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
        )
        sec_since_mon = sec_since_mon.to_byte(4, "little")
        await self._conn.write_gatt_char(HANDLE_RW_TIME_OFFSET, sec_since_mon)

    async def commit_code(self):
        await self._conn.write_gatt_char(HANDLE_W_COMMITCODE, b"\x00")
        await self._conn.write_gatt_char(HANDLE_W_COMMITCODE, b"\x01")
