"""Bluetooth protocols of Xiaomi and Ninebot (Segway) scooters.

All scooters use a serial protocol over the Nordic UART service, newer BLE
firmwares encrypt it:
- Xiaomi (M365, Pro, 1S, Pro 2, Mi 3...): 55 AA frames, encrypted with the
  Xiaomi Mi auth (ECDH registration, token, AES-CCM)
- Ninebot (G30, F, ES, Xiaomi 4...): 5A A5 frames, encrypted with NinebotCrypto

The crypto is done by miauth, which is also used by the Scooter Hacking
Utility community.
"""

import asyncio
import secrets
import struct

UART_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # write
UART_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # notify
MI_UPNP = "00000010-0000-1000-8000-00805f9b34fb"
MI_AVDTP = "00000019-0000-1000-8000-00805f9b34fb"

NINEBOT_MANUFACTURER_ID = 16974
SCOOTER_NAME_PREFIXES = ("MIScooter", "NBScooter")

XIAOMI = "xiaomi"
XIAOMI_PLAIN = "xiaomi_plain"
NINEBOT = "ninebot"

ESC = 0x20
BMS = 0x22

# Mi auth commands
MI_CMD_GET_INFO = b"\xa2\x00\x00\x00"
MI_CMD_SET_KEY = b"\x15\x00\x00\x00"
MI_CMD_LOGIN = b"\x24\x00\x00\x00"
MI_CMD_AUTH = b"\x13\x00\x00\x00"
MI_CMD_SEND_DATA = b"\x00\x00\x00\x03\x04\x00"
MI_CMD_SEND_DID = b"\x00\x00\x00\x00\x02\x00"
MI_CMD_SEND_KEY = b"\x00\x00\x00\x0b\x01\x00"
MI_CMD_SEND_INFO = b"\x00\x00\x00\x0a\x02\x00"
MI_RCV_RDY = b"\x00\x00\x01\x01"
MI_RCV_OK = b"\x00\x00\x01\x00"
MI_RCV_TOUT = b"\x00\x00\x01\x05\x01\x00"
MI_RCV_ERR = b"\x00\x00\x01\x05\x03\x00"
MI_REGISTER_OK = 0x11
MI_LOGIN_OK = 0x21

# Ninebot commands
NB_PC = 0x3D
NB_BLE = 0x21
NB_READ = 0x01
NB_READ_ACK = 0x04
NB_INIT = 0x5B
NB_PING = 0x5C
NB_PAIR = 0x5D


class ScooterError(Exception):
    pass


class PairingRequired(ScooterError):
    """The scooter doesn't know us, the power button has to be pressed."""


def is_scooter(name, manufacturer_data):
    if NINEBOT_MANUFACTURER_ID in (manufacturer_data or {}):
        return True
    return bool(name) and name.startswith(SCOOTER_NAME_PREFIXES)


def detect_protocol(name, manufacturer_data, characteristics):
    """characteristics: lowercase UUIDs of the connected scooter"""
    if MI_UPNP in characteristics and MI_AVDTP in characteristics:
        return XIAOMI
    if NINEBOT_MANUFACTURER_ID in (manufacturer_data or {}):
        return NINEBOT
    if name and name.startswith("MIScooter"):
        return XIAOMI_PLAIN
    return NINEBOT


def _u16(data):
    return struct.unpack_from("<H", data)[0]


def _s16(data):
    return struct.unpack_from("<h", data)[0]


def _version(data):
    val = _u16(data)
    return f"{val >> 8}.{(val >> 4) & 0x0F}.{val & 0x0F}"


def _serial(data):
    return bytes(data).split(b"\x00")[0].decode("ascii", "replace").strip()


def _battery(data):
    # 0x31 remaining mAh, 0x32 %, 0x33 current, 0x34 voltage, 0x35 temperatures
    return {
        "battery_remaining_capacity": _u16(data[0:2]),
        "battery": _u16(data[2:4]),
        "battery_current": round(_s16(data[4:6]) / 100, 2),
        "battery_voltage": round(_u16(data[6:8]) / 100, 2),
        "battery_temperature1": data[8] - 20,
        "battery_temperature2": data[9] - 20,
    }


# (target, register, length, decoder returning a dict of readings)
STATIC_REGISTERS = [
    (ESC, 0x10, 14, lambda d: {"serial_number": _serial(d)}),
    (ESC, 0x1A, 2, lambda d: {"firmware_esc": _version(d)}),
    (ESC, 0x68, 2, lambda d: {"firmware_ble": _version(d)}),
    (BMS, 0x17, 2, lambda d: {"firmware_bms": _version(d)}),
    (BMS, 0x18, 2, lambda d: {"battery_capacity": _u16(d)}),
]
REGISTERS = [
    (BMS, 0x31, 10, _battery),
    (BMS, 0x3B, 2, lambda d: {"battery_health": _u16(d)}),
    (ESC, 0x1B, 2, lambda d: {"error_code": _u16(d)}),
    (ESC, 0x25, 2, lambda d: {"range": round(_u16(d) / 100, 2)}),
    (ESC, 0x29, 4, lambda d: {"mileage": round(struct.unpack("<I", d)[0] / 1000, 2)}),
    (ESC, 0x3E, 2, lambda d: {"temperature": round(_s16(d) / 10, 1)}),
]


def crc16(data):
    return struct.pack("<H", ~sum(data) & 0xFFFF)


class Transport:
    """Request/response over the UART characteristics of a connected
    BleakClient-like object (write_gatt_char, start_notify)."""

    def __init__(self, client, logger):
        self.client = client
        self.logger = logger
        self._buffer = bytearray()
        self._frames = asyncio.Queue()

    async def start(self):
        await self.client.start_notify(UART_RX, self._on_uart)

    def _on_uart(self, _char, data):
        if data[:2] in (b"\x55\xaa", b"\x55\xab", b"\x5a\xa5"):
            self._buffer = bytearray(data)
        else:
            self._buffer += data
        if len(self._buffer) >= 3 and len(self._buffer) >= self._frame_length(
            self._buffer
        ):
            frame = bytes(self._buffer)
            self._buffer = bytearray()
            self._frames.put_nowait(frame)

    async def _write(self, data, chunk=20):
        for i in range(0, len(data), chunk):
            await self.client.write_gatt_char(UART_TX, data[i : i + chunk])

    async def _receive(self, timeout):
        return await asyncio.wait_for(self._frames.get(), timeout)

    async def read(self, target, register, length, timeout=3, retries=3):
        for _ in range(retries):
            while not self._frames.empty():
                self._frames.get_nowait()
            await self._write(self._encode_read(target, register, length))
            try:
                async with asyncio.timeout(timeout):
                    while True:
                        reply = self._decode(await self._receive(timeout))
                        if reply is None:
                            continue
                        source, reg, payload = reply
                        if source == target and reg == register:
                            return payload[:length]
            except TimeoutError:
                self.logger.debug(f"No reply for register {register:#x}, retry")
        raise ScooterError(f"No reply for register {register:#x} of {target:#x}")


class XiaomiPlainTransport(Transport):
    """Old Xiaomi BLE firmware, unencrypted 55 AA frames"""

    @staticmethod
    def _frame_length(buf):
        return buf[2] + 6

    @staticmethod
    def _request(target, register, length):
        return bytes([0x55, 0xAA, 3, target, NB_READ, register, length])

    def _encode_read(self, target, register, length):
        frame = self._request(target, register, length)
        return frame + crc16(frame[2:])

    @staticmethod
    def _decode(frame):
        if frame[:2] != b"\x55\xaa" or crc16(frame[2:-2]) != frame[-2:]:
            return None
        # replies come from target + 1 (ESC 0x23, BMS 0x25... e.g. 0x22 -> 0x25)
        return _xiaomi_source(frame[3]), frame[5], frame[6:-2]


def _xiaomi_source(addr):
    return {0x23: ESC, 0x25: BMS}.get(addr, addr)


class XiaomiTransport(XiaomiPlainTransport):
    """Xiaomi BLE firmware with Mi auth"""

    def __init__(self, client, logger, token=None):
        super().__init__(client, logger)
        self.token = token
        self._auth = asyncio.Queue()
        self._keys = None
        self._it = 0

    async def start(self):
        await super().start()
        await self.client.start_notify(MI_UPNP, self._on_auth)
        await self.client.start_notify(MI_AVDTP, self._on_auth)

    def _on_auth(self, _char, data):
        if data:
            self._auth.put_nowait(bytes(data))

    async def _next(self, timeout=5):
        return await asyncio.wait_for(self._auth.get(), timeout)

    async def _recv_parcel(self):
        header = await self._next()
        if header[:2] != b"\x00\x00" or len(header) < 6:
            raise ScooterError(f"Unexpected Mi auth data {header.hex()}")
        frames = header[4] + 0x100 * header[5]
        await self.client.write_gatt_char(MI_AVDTP, MI_RCV_RDY)
        data = b""
        for _ in range(frames):
            frame = await self._next()
            data += frame[2:]
        await self.client.write_gatt_char(MI_AVDTP, MI_RCV_OK)
        return data

    async def _send_parcel(self, data):
        await self._expect(MI_RCV_RDY)
        for i in range(0, len(data), 18):
            chunk = bytes([i // 18 + 1, 0]) + data[i : i + 18]
            await self.client.write_gatt_char(MI_AVDTP, chunk)
        await self._expect(MI_RCV_OK)

    async def _expect(self, expected):
        data = await self._next()
        if data in (MI_RCV_TOUT, MI_RCV_ERR):
            raise ScooterError("Scooter rejected Mi auth data")
        if data != expected:
            raise ScooterError(f"Unexpected Mi auth reply {data.hex()}")

    async def register(self):
        """Pair with the scooter. It only answers if the power button was
        pressed after it beeped, PairingRequired is raised otherwise.
        Returns the token which has to be stored for login."""
        try:
            return await self._register()
        except TimeoutError as exc:
            raise PairingRequired() from exc

    async def _register(self):
        from miauth.mi.micrypto import MiCrypto

        priv_key, pub_key = MiCrypto.gen_keypair()
        await self.client.write_gatt_char(MI_UPNP, MI_CMD_GET_INFO)
        remote_info = (await self._recv_parcel())[4:]
        if len(remote_info) != 20:
            raise ScooterError("Scooter sent no device id, pair it with an app first")

        await self.client.write_gatt_char(MI_UPNP, MI_CMD_SET_KEY)
        await self.client.write_gatt_char(MI_AVDTP, MI_CMD_SEND_DATA)
        await self._send_parcel(MiCrypto.pub_key_to_bytes(pub_key))
        remote_key = await self._recv_parcel()

        shared = MiCrypto.generate_secret(
            priv_key, MiCrypto.bytes_to_pub_key(remote_key)
        )
        derived = MiCrypto.derive_key(shared)
        token = derived[0:12]
        did_ct = MiCrypto.encrypt_did(derived[28:44], remote_info)
        await self.client.write_gatt_char(MI_AVDTP, MI_CMD_SEND_DID)
        await self._send_parcel(did_ct)
        await self.client.write_gatt_char(MI_UPNP, MI_CMD_AUTH)
        if (await self._next())[0] != MI_REGISTER_OK:
            raise ScooterError("Mi registration failed")
        self.token = token
        return token

    async def login(self):
        from miauth.mi.micrypto import MiCrypto

        if not self.token:
            raise PairingRequired()
        rand_key = MiCrypto.gen_rand_key()
        await self.client.write_gatt_char(MI_UPNP, MI_CMD_LOGIN)
        await self.client.write_gatt_char(MI_AVDTP, MI_CMD_SEND_KEY)
        await self._send_parcel(rand_key)
        remote_key = await self._recv_parcel()
        remote_info = await self._recv_parcel()

        salt = rand_key + remote_key
        derived = MiCrypto.derive_key(self.token, salt=salt)
        keys = {
            "dev_key": derived[:16],
            "app_key": derived[16:32],
            "dev_iv": derived[32:36],
            "app_iv": derived[36:40],
        }
        expected = MiCrypto.hash(keys["dev_key"], remote_key + rand_key)
        if remote_info != expected:
            # the scooter was paired with another app in the meantime
            raise PairingRequired()
        await self.client.write_gatt_char(MI_AVDTP, MI_CMD_SEND_INFO)
        await self._send_parcel(MiCrypto.hash(keys["app_key"], salt))
        reply = await self._next()
        if reply[0] != MI_LOGIN_OK:
            raise PairingRequired()
        self._keys = keys
        self._it = 0

    @staticmethod
    def _frame_length(buf):
        if buf[:2] == b"\x55\xab":
            return buf[2] + 16
        return buf[2] + 6

    def _encode_read(self, target, register, length):
        from miauth.mi.micrypto import MiCrypto

        frame = MiCrypto.encrypt_uart(
            self._keys["app_key"],
            self._keys["app_iv"],
            self._request(target, register, length),
            it=self._it,
            rand=secrets.token_bytes(4),
        )
        self._it += 1
        return frame

    def _decode(self, frame):
        from miauth.mi.micrypto import MiCrypto

        try:
            data = MiCrypto.decrypt_uart(
                self._keys["dev_key"], self._keys["dev_iv"], frame
            )
        except Exception:
            self.logger.debug(f"Failed to decrypt {frame.hex()}")
            return None
        # addr, cmd, register, payload, 4 random bytes
        return _xiaomi_source(data[0]), data[2], data[3:-4]


class NinebotTransport(Transport):
    """Ninebot BLE firmware with NinebotCrypto"""

    def __init__(self, client, logger, name, app_key=None):
        from miauth.nb.nbcrypto import NbCrypto

        super().__init__(client, logger)
        self.crypto = NbCrypto()
        self.crypto.set_name((name or "Unnamed").encode())
        self.app_key = app_key or secrets.token_bytes(16)

    @staticmethod
    def _frame_length(buf):
        return buf[2] + 13

    async def _send(self, dst, cmd, arg, payload=b""):
        frame = bytes([0x5A, 0xA5, len(payload), NB_PC, dst, cmd, arg]) + payload
        await self._write(bytes(self.crypto.encrypt(frame)))

    def _unpack(self, frame):
        data = bytes(self.crypto.decrypt(frame))
        if data[:2] != b"\x5a\xa5" or len(data) < data[2] + 7:
            return None
        # src, dst, cmd, arg, payload
        return data[3], data[4], data[5], data[6], data[7 : 7 + data[2]]

    async def _command(self, cmd, payload=b"", timeout=5):
        await self._send(NB_BLE, cmd, 0, payload)
        async with asyncio.timeout(timeout):
            while True:
                packet = self._unpack(await self._receive(timeout))
                if packet and packet[2] == cmd:
                    return packet

    async def login(self, pairing_timeout=0):
        """Authenticate with the stored app key. If the scooter doesn't know
        the key, wait pairing_timeout seconds for the power button."""
        _, _, _, _, payload = await self._command(NB_INIT)
        self.crypto.set_ble_data(payload[:16])
        serial = payload[16:]

        _, _, _, arg, _ = await self._command(NB_PING, self.app_key)
        if arg == 1:
            self.crypto.set_app_data(self.app_key)
        else:
            await self._wait_for_button(serial, pairing_timeout)

        await self._command(NB_PAIR, serial)

    async def _wait_for_button(self, serial, pairing_timeout):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + pairing_timeout
        while loop.time() < deadline:
            await self._send(NB_BLE, NB_PAIR, 0, serial)
            try:
                packet = self._unpack(await self._receive(1.5))
            except TimeoutError:
                continue
            if packet is None:
                continue
            _, _, cmd, arg, _ = packet
            if cmd == NB_PING and arg == 1:
                self.crypto.set_app_data(self.app_key)
                return
            if cmd == NB_PAIR and arg == 1:
                return
        raise PairingRequired()

    def _encode_read(self, target, register, length):
        frame = bytes([0x5A, 0xA5, 1, NB_PC, target, NB_READ, register, length])
        return bytes(self.crypto.encrypt(frame))

    def _decode(self, frame):
        packet = self._unpack(frame)
        if packet is None or packet[2] != NB_READ_ACK:
            return None
        src, _, _, register, payload = packet
        return src, register, payload


async def read_values(transport, static=True):
    readings = {}
    registers = (STATIC_REGISTERS if static else []) + REGISTERS
    for target, register, length, decoder in registers:
        payload = await transport.read(target, register, length)
        if len(payload) < length:
            raise ScooterError(f"Register {register:#x}: short reply {payload.hex()}")
        readings.update(decoder(payload))
    return readings
