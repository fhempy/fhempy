import asyncio
import struct

from .. import fhem, generic
from ..core import ble_proxy
from ..core.bluetoothle import BluetoothLE

UUID_WRITE = "000084cf-f7e3-55b4-6c4c-9fd140100a16"
UUID_NOTIFY = "000084cf-f7e3-55b4-6c4c-9fd140100a17"

# Protocol (verified with btsnoop traces of the vendor app):
#   app -> device:  CC AA <len> <payload...> <xor>
#   device -> app:  CC DD <len> <payload...> <xor>
#   len = total length incl. header and checksum, xor = XOR of all bytes before
CMD_START = 0xFE  # FE 01: start notifications, the app sends it once
CMD_STATUS = 0x0F  # base status / buzzer alarm
CMD_PROBE = 0xC0  # C1..C4: probe 1..4

# filler bytes exactly as sent by the app (current value fields, ignored)
PROBE_FILL = {
    1: (0x20, 0x20, 0x20, 0x20),
    2: (0x84, 0x80, 0x49, 0x49),
    3: (0x84, 0x80, 0x49, 0x49),
    4: (0x84, 0x80, 0x49, 0x49),
}
TEMP_INVALID_MAX = 40000  # raw values above: no probe
KEEPALIVE_INTERVAL = 30  # s, send FE 01 again
WRITE_GAP = 0.15  # s pause after each write


def _xor(data):
    cs = 0
    for b in data:
        cs ^= b
    return cs


def _ccaa_pkt(payload):
    pkt = bytearray([0xCC, 0xAA, len(payload) + 4]) + bytearray(payload)
    pkt.append(_xor(pkt))
    return pkt


class chefbbq(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._ble = None
        self._mac = None
        self._poll_task = None
        self._write_lock = asyncio.Lock()
        self._attr_adapter = "auto"
        self._attr_widget = "slider"
        self._attr_tempMin = 30
        self._attr_tempMax = 250
        self._attr_batteryRawEmpty = 100
        self._attr_batteryRawFull = 158

    # ------------------------------------------------------------------ FHEM

    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define <name> fhempy chefbbq <MAC>"
        self._mac = str(args[3]).upper()
        self.hash["MAC"] = self._mac
        await self.set_icon("temp_temperature")
        await self._update_attr_config()
        await self._update_set_config()
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connecting", 1)
        await self._init_ble()
        return ""

    async def _adapter_options(self):
        """auto, local, proxy, the local adapters and the Bluetooth proxies"""
        options = ["auto", "local", "proxy"]
        try:
            import bluetooth_adapters

            options += sorted(await bluetooth_adapters.get_bluetooth_adapters())
        except Exception:
            self.logger.debug("Failed to list Bluetooth adapters", exc_info=True)
        options += [
            f"proxy:{ble_proxy.option_name(proxy)}"
            for proxy in ble_proxy.proxies()
            if proxy.connectable
        ]
        if self._attr_adapter not in options:
            # e.g. a proxy which isn't connected yet
            options.append(self._attr_adapter)
        return ",".join(options)

    async def _update_attr_config(self):
        await self.set_attr_config(
            {
                "adapter": {
                    "default": "auto",
                    "options": await self._adapter_options(),
                    "help": "Bluetooth adapter: auto (best signal), local "
                    "adapters only, proxy (any Bluetooth proxy), a fixed "
                    "proxy (proxy:<name>) or a fixed local adapter (hci0, ...)",
                },
                "widget": {
                    "default": "slider",
                    "options": "slider,knob",
                    "help": "UI control for target temperatures: slider or knob",
                },
                "tempMin": {
                    "default": "30",
                    "format": "int",
                    "help": "Minimum target temperature (C)",
                },
                "tempMax": {
                    "default": "250",
                    "format": "int",
                    "help": "Maximum target temperature (C)",
                },
                "batteryRawEmpty": {
                    "default": "100",
                    "format": "int",
                    "help": "Raw battery value for 0 %",
                },
                "batteryRawFull": {
                    "default": "158",
                    "format": "int",
                    "help": "Raw battery value for 100 %",
                },
            }
        )

    async def Undefine(self, hash):
        await self._stop_poll()
        if self._ble is not None:
            try:
                await self._ble.disconnect()
            except Exception:
                self.logger.exception("Failed to disconnect")
        await super().Undefine(hash)

    def _widget_options(self):
        try:
            tmin, tmax = int(self._attr_tempMin), int(self._attr_tempMax)
        except (TypeError, ValueError):
            tmin, tmax = 30, 250
        if self._attr_widget == "knob":
            return (
                f"knob,min:{tmin},max:{tmax},step:1,angleArc:270,angleOffset:-135,"
                f"width:70,height:70,fgColor:#c33,bgColor:#ddd,thickness:0.3"
            )
        return f"slider,{tmin},1,{tmax}"

    async def _update_set_config(self):
        set_conf = {
            "alarm": {
                "args": ["state"],
                "options": "on,off",
                "help": "Buzzer alarm on/off",
            },
            "reconnect": {"help": "Reconnect to the device"},
        }
        opts = self._widget_options()
        for ch in range(1, 5):
            set_conf[f"target_{ch}"] = {
                "args": ["temperature"],
                "params": {"temperature": {"default": 60, "format": "int"}},
                "options": opts,
                "help": f"Target temperature probe {ch} in C",
            }
        await self.set_set_config(set_conf)

    async def set_attr_adapter(self, hash):
        if self._mac is not None:
            await self._init_ble()

    async def set_attr_widget(self, hash):
        await self._update_set_config()

    async def set_attr_tempMin(self, hash):
        await self._update_set_config()

    async def set_attr_tempMax(self, hash):
        await self._update_set_config()

    async def set_reconnect(self, hash, params):
        # proxies which connected later appear in the adapter options
        await self._update_attr_config()
        await self._init_ble()
        return ""

    async def set_alarm(self, hash, params):
        st = str(params.get("state")).lower()
        if st not in ("on", "off"):
            return "Usage: set <name> alarm on|off"
        pkt = _ccaa_pkt(
            [CMD_STATUS, 0x01, 0x2C, 0x00, 0x02 if st == "on" else 0x00, 0x00]
        )
        if not await self._write_cmd(pkt):
            return "Write failed"
        # the reading is confirmed by the next status notification
        return ""

    async def set_target_1(self, hash, params):
        return await self._send_target(1, params.get("temperature"))

    async def set_target_2(self, hash, params):
        return await self._send_target(2, params.get("temperature"))

    async def set_target_3(self, hash, params):
        return await self._send_target(3, params.get("temperature"))

    async def set_target_4(self, hash, params):
        return await self._send_target(4, params.get("temperature"))

    # ------------------------------------------------------------------ BLE

    async def _init_ble(self):
        await self._stop_poll()
        if self._ble is not None:
            await self._ble.disconnect()
        self._ble = BluetoothLE(
            self.logger, self.hash, address=self._mac, adapter=self._attr_adapter
        )
        self._ble.register_connection_established_listener(self._on_connected)
        self._ble.register_disconnect_listener(self._on_disconnected)
        # BluetoothLE subscribes all notify characteristics with this listener
        self._ble.register_notification_listener(self._received_notification)
        self.create_async_task(self._ble.connect())

    def _client(self):
        if self._ble is None or not self._ble.is_connected:
            return None
        return self._ble.client

    async def _write_cmd(self, pkt):
        c = self._client()
        if c is None:
            self.logger.warning("write: not connected")
            return False
        async with self._write_lock:
            try:
                self.logger.debug(f"TX {bytes(pkt).hex(' ')}")
                await c.write_gatt_char(UUID_WRITE, pkt, response=False)
                await asyncio.sleep(WRITE_GAP)
                return True
            except Exception as e:
                self.logger.error(f"write failed: {e}")
                return False

    async def _send_target(self, ch, temp_c):
        try:
            t = int(round(float(temp_c)))  # the device works in whole degrees
        except (TypeError, ValueError):
            return f"Usage: set <name> target_{ch} <temperature>"
        raw = t * 100
        if not 0 < raw <= TEMP_INVALID_MAX:
            return "Temperature out of range"
        f1, f2, f3, f4 = PROBE_FILL[ch]
        lo, hi = raw & 0xFF, (raw >> 8) & 0xFF
        # like the app: only the changed probe is sent
        pkt = _ccaa_pkt(
            [CMD_PROBE + ch, 0x18, 0x00, 0x40, f1, f2, lo, hi, f3, f4, 0x68, 0x42]
        )
        if not await self._write_cmd(pkt):
            return "Write failed"
        # the reading is confirmed by the next probe notification
        return ""

    async def _on_connected(self):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected", 1)
        await self._stop_poll()
        self._poll_task = self.create_async_task(self._poll_loop())

    async def _poll_loop(self):
        while self._ble and self._ble.connected.is_set():
            await self._write_cmd(_ccaa_pkt([CMD_START, 0x01]))
            await asyncio.sleep(KEEPALIVE_INTERVAL)

    async def _stop_poll(self):
        if self._poll_task is not None:
            self.cancel_async_task(self._poll_task)
            self._poll_task = None

    async def _on_disconnected(self, client=None):
        await self._stop_poll()
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "disconnected", 1)

    # ------------------------------------------------------------------ RX

    def _received_notification(self, uuid, data):
        self.create_async_task(self._on_notification(data))

    async def _on_notification(self, data):
        d = bytes(data)
        if len(d) < 5 or d[0] != 0xCC or d[1] != 0xDD:
            return
        if d[2] != len(d) or _xor(d[:-1]) != d[-1]:
            self.logger.debug(f"RX invalid {d.hex(' ')}")
            return
        pkt_type = d[3]
        if pkt_type == CMD_STATUS and len(d) >= 10:
            await self._handle_status(d)
        elif CMD_PROBE + 1 <= pkt_type <= CMD_PROBE + 4 and len(d) >= 16:
            await self._handle_probe(pkt_type - CMD_PROBE, d)

    def _bat_pct(self, raw):
        try:
            empty = int(self._attr_batteryRawEmpty)
            full = int(self._attr_batteryRawFull)
        except (TypeError, ValueError):
            empty, full = 100, 158
        if full <= empty:
            return raw
        return min(100, max(0, round((raw - empty) * 100 / (full - empty))))

    async def _handle_status(self, d):
        # CC DD 0A 0F 01 2C <bat> <alarm> 01 <xor>
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "alarm", "on" if d[7] != 0 else "off"
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "battery", self._bat_pct(d[6])
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, "battery_raw", d[6])
        await fhem.readingsEndUpdate(self.hash, 1)

    async def _handle_probe(self, ch, d):
        # CC DD 10 Cx <bat> <flags> <flags> <temp> <target> <temp2> <limit2> <xor>
        # values uint16 LE in 1/100 C, battery same scale as the base (full 0x9e)
        temp, target, temp2 = struct.unpack_from("<HHH", d, 7)
        await fhem.readingsBeginUpdate(self.hash)
        if temp == 0 or temp > TEMP_INVALID_MAX:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"temperature_{ch}", "unplugged"
            )
        else:
            t1 = int(round(temp / 100.0))
            await fhem.readingsBulkUpdateIfChanged(self.hash, f"temperature_{ch}", t1)
            if ch == 1:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", f"{t1} C")
        if 0 < target <= TEMP_INVALID_MAX:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"target_{ch}", int(round(target / 100.0))
            )
        if 0 < temp2 <= TEMP_INVALID_MAX:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"ambient_{ch}", int(round(temp2 / 100.0))
            )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, f"battery_{ch}", self._bat_pct(d[4])
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, f"battery_{ch}_raw", d[4])
        await fhem.readingsEndUpdate(self.hash, 1)
