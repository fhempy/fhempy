import asyncio
import logging
import secrets
import struct

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)

NAME = "testscooter"
ADDRESS = "AA:BB:CC:DD:EE:FF"
UART_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_RX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
MI_UPNP = "00000010-0000-1000-8000-00805f9b34fb"
MI_AVDTP = "00000019-0000-1000-8000-00805f9b34fb"


def registers():
    """ESC (0x20) and BMS (0x22) register memory, 16 bit words"""
    esc = bytearray(0x200)
    bms = bytearray(0x200)

    def word(mem, reg, data):
        mem[reg * 2 : reg * 2 + len(data)] = data

    word(esc, 0x10, b"N2GSC1234C5678\x00\x00")
    word(esc, 0x1A, struct.pack("<H", 0x0157))
    word(esc, 0x1B, struct.pack("<H", 0))
    word(esc, 0x25, struct.pack("<H", 2350))
    word(esc, 0x29, struct.pack("<I", 1234567))
    word(esc, 0x3E, struct.pack("<h", 215))
    word(esc, 0x68, struct.pack("<H", 0x0160))
    word(bms, 0x17, struct.pack("<H", 0x0130))
    word(bms, 0x18, struct.pack("<H", 15300))
    word(bms, 0x31, struct.pack("<HHhH", 12000, 78, -150, 3950) + bytes([42, 43]))
    word(bms, 0x3B, struct.pack("<H", 99))
    return {0x20: esc, 0x22: bms}


def read_memory(target, register, length):
    return bytes(registers()[target][register * 2 : register * 2 + length])


class FakeClient:
    """BleakClient replacement, the scooter side is implemented by on_write"""

    def __init__(self):
        self.callbacks = {}
        self.is_connected = True

    async def start_notify(self, uuid, callback):
        self.callbacks[uuid] = callback

    def notify(self, uuid, data):
        asyncio.get_running_loop().call_soon(self.callbacks[uuid], None, data)

    def notify_chunked(self, uuid, data):
        for i in range(0, len(data), 20):
            self.notify(uuid, bytearray(data[i : i + 20]))

    async def write_gatt_char(self, uuid, data):
        self.on_write(uuid, bytes(data))

    async def disconnect(self):
        self.is_connected = False


class FakeNinebot(FakeClient):
    def __init__(self, name="NBScooter1234", known_keys=None, button_pressed=True):
        from miauth.nb.nbcrypto import NbCrypto

        super().__init__()
        self.crypto = NbCrypto()
        self.crypto.set_name(name.encode())
        self.ble_key = secrets.token_bytes(16)
        self.serial = b"N2GSC1234C5678"
        self.known_keys = known_keys if known_keys is not None else []
        self.button_pressed = button_pressed
        self.app_key = None
        self.buffer = b""

    def on_write(self, uuid, data):
        assert uuid == UART_TX
        if data[:2] == b"\x5a\xa5":
            self.buffer = data
        else:
            self.buffer += data
        if len(self.buffer) < self.buffer[2] + 13:
            return
        frame = bytes(self.crypto.decrypt(self.buffer))
        self.buffer = b""
        length, src, dst, cmd, arg = frame[2:7]
        payload = frame[7 : 7 + length]
        if cmd == 0x5B:
            self.send(0x21, 0x5B, 1, self.ble_key + self.serial)
            self.crypto.set_ble_data(self.ble_key)
            # use the AES mode of NinebotCrypto from now on
            self.crypto.it = 5
        elif cmd == 0x5C:
            self.app_key = payload
            if payload in self.known_keys:
                self.send(0x21, 0x5C, 1)
                self.crypto.set_app_data(payload)
            else:
                self.send(0x21, 0x5C, 0)
        elif cmd == 0x5D:
            if self.app_key in self.known_keys:
                self.send(0x21, 0x5D, 1)
            elif self.button_pressed:
                self.known_keys.append(self.app_key)
                self.send(0x21, 0x5C, 1)
                self.crypto.set_app_data(self.app_key)
            else:
                self.send(0x21, 0x5C, 0)
        elif cmd == 0x01:
            self.send(dst, 0x04, arg, read_memory(dst, arg, payload[0]))

    def send(self, src, cmd, arg, payload=b""):
        frame = bytes([0x5A, 0xA5, len(payload), src, 0x3D, cmd, arg]) + payload
        self.notify_chunked(UART_RX, bytes(self.crypto.encrypt(frame)))


class FakeXiaomi(FakeClient):
    """Xiaomi Mi auth, scooter side"""

    def __init__(self, button_presses=1):
        from miauth.mi.micrypto import MiCrypto

        super().__init__()
        self.crypto = MiCrypto
        self.did = b"blt.3.1234567890ab\x00\x00"
        self.priv_key, self.pub_key = MiCrypto.gen_keypair()
        # register calls ignored until the power button was pressed
        self.ignored_registrations = button_presses
        self.token = None
        self.keys = None
        self.receiving = None
        self.expected = 0
        self.received = b""
        self.sending = []
        self.login_rand = None
        self.remote_key = None

    def on_write(self, uuid, data):
        if uuid == MI_UPNP:
            self.on_upnp(data)
        elif uuid == MI_AVDTP:
            self.on_avdtp(data)
        else:
            self.on_uart(data)

    def on_upnp(self, data):
        if data == b"\xa2\x00\x00\x00":
            if self.ignored_registrations > 0:
                self.ignored_registrations -= 1
                return
            self.send_parcel(b"\x00\x00\x00\x00" + self.did)
        elif data == b"\x13\x00\x00\x00":
            self.notify(MI_UPNP, b"\x11\x00\x00\x00")

    def send_parcel(self, data):
        frames = [data[i : i + 18] for i in range(0, len(data), 18)]
        self.sending = frames
        self.notify(MI_AVDTP, bytes([0, 0, 0, 0x0D, len(frames), 0]))

    def on_avdtp(self, data):
        if data == b"\x00\x00\x01\x01":
            for idx, frame in enumerate(self.sending):
                self.notify(MI_AVDTP, bytes([idx + 1, 0]) + frame)
        elif data == b"\x00\x00\x01\x00":
            self.parcel_sent()
        elif data[:2] == b"\x00\x00":
            # receive a parcel, byte 4 is the number of frames
            self.receiving = data
            self.expected = data[4]
            self.received = b""
            self.notify(MI_AVDTP, b"\x00\x00\x01\x01")
        else:
            self.received += data[2:]
            if data[0] == self.expected:
                self.notify(MI_AVDTP, b"\x00\x00\x01\x00")
                self.parcel_received(self.receiving, self.received)

    def parcel_received(self, cmd, data):
        mc = self.crypto
        if cmd == b"\x00\x00\x00\x03\x04\x00":
            remote = mc.bytes_to_pub_key(data)
            derived = mc.derive_key(mc.generate_secret(self.priv_key, remote))
            self.token = derived[0:12]
            self.send_parcel(mc.pub_key_to_bytes(self.pub_key))
        elif cmd == b"\x00\x00\x00\x0b\x01\x00":
            self.login_rand = data
            self.remote_key = secrets.token_bytes(16)
            derived = mc.derive_key(self.token, salt=self.login_rand + self.remote_key)
            self.keys = {
                "dev_key": derived[:16],
                "app_key": derived[16:32],
                "dev_iv": derived[32:36],
                "app_iv": derived[36:40],
            }
            self.after_parcel = mc.hash(
                self.keys["dev_key"], self.remote_key + self.login_rand
            )
            self.send_parcel(self.remote_key)
        elif cmd == b"\x00\x00\x00\x0a\x02\x00":
            expected = mc.hash(self.keys["app_key"], self.login_rand + self.remote_key)
            self.notify(MI_UPNP, b"\x21\x00\x00\x00" if data == expected else b"\x23")

    def parcel_sent(self):
        if getattr(self, "after_parcel", None):
            data, self.after_parcel = self.after_parcel, None
            self.send_parcel(data)

    def on_uart(self, data):
        mc = self.crypto
        plain = mc.decrypt_uart(self.keys["app_key"], self.keys["app_iv"], data)
        addr, cmd, reg, length = plain[:4]
        payload = read_memory(addr, reg, length)
        reply_addr = {0x20: 0x23, 0x22: 0x25}[addr]
        reply = bytes([0x55, 0xAA, len(payload) + 2, reply_addr, cmd, reg]) + payload
        self.notify_chunked(
            UART_RX,
            mc.encrypt_uart(self.keys["dev_key"], self.keys["dev_iv"], reply),
        )


EXPECTED = {
    "serial_number": "N2GSC1234C5678",
    "firmware_esc": "1.5.7",
    "firmware_ble": "1.6.0",
    "battery_capacity": 15300,
    "battery": 78,
    "battery_remaining_capacity": 12000,
    "battery_current": -1.5,
    "battery_voltage": 39.5,
    "battery_temperature1": 22,
    "battery_temperature2": 23,
    "battery_health": 99,
    "error_code": 0,
    "range": 23.5,
    "mileage": 1234.57,
    "temperature": 21.5,
}


@pytest.mark.asyncio
async def test_ninebot_pairing_and_read():
    await check_and_install_dependencies("scooter")
    from fhempy.lib.scooter import protocol

    scooter = FakeNinebot()
    transport = protocol.NinebotTransport(scooter, logger, "NBScooter1234")
    await transport.start()
    await transport.login(pairing_timeout=5)
    assert transport.app_key in scooter.known_keys
    assert await protocol.read_values(transport) == {
        **EXPECTED,
        "firmware_bms": "1.3.0",
    }

    # the stored key is accepted without button press
    scooter = FakeNinebot(known_keys=[transport.app_key], button_pressed=False)
    transport = protocol.NinebotTransport(
        scooter, logger, "NBScooter1234", transport.app_key
    )
    await transport.start()
    await transport.login()
    values = await protocol.read_values(transport, static=False)
    assert values["battery"] == 78
    assert "serial_number" not in values


@pytest.mark.asyncio
async def test_ninebot_unknown_key():
    await check_and_install_dependencies("scooter")
    from fhempy.lib.scooter import protocol

    scooter = FakeNinebot(button_pressed=False)
    transport = protocol.NinebotTransport(scooter, logger, "NBScooter1234")
    await transport.start()
    with pytest.raises(protocol.PairingRequired):
        await transport.login()


@pytest.mark.asyncio
async def test_xiaomi_register_login_read():
    await check_and_install_dependencies("scooter")
    from fhempy.lib.scooter import protocol

    scooter = FakeXiaomi(button_presses=1)
    transport = protocol.XiaomiTransport(scooter, logger)
    await transport.start()
    # first attempt: scooter beeps and waits for the power button
    with pytest.raises(protocol.PairingRequired):
        await transport.register()
    transport = protocol.XiaomiTransport(scooter, logger)
    await transport.start()
    token = await transport.register()
    assert token == scooter.token

    transport = protocol.XiaomiTransport(scooter, logger, token)
    await transport.start()
    await transport.login()
    assert await protocol.read_values(transport) == {
        **EXPECTED,
        "firmware_bms": "1.3.0",
    }

    # wrong token: paired with another app in the meantime
    transport = protocol.XiaomiTransport(scooter, logger, b"\x01" * 12)
    await transport.start()
    with pytest.raises(protocol.PairingRequired):
        await transport.login()


def test_detect_protocol():
    from fhempy.lib.scooter import protocol

    assert protocol.is_scooter("MIScooter1234", {})
    assert protocol.is_scooter(None, {16974: b"\x00"})
    assert not protocol.is_scooter("Phone", {76: b"\x00"})
    assert (
        protocol.detect_protocol("MIScooter1234", {}, {MI_UPNP, MI_AVDTP, UART_RX})
        == protocol.XIAOMI
    )
    assert protocol.detect_protocol("MIScooter1234", {}, {UART_RX}) == (
        protocol.XIAOMI_PLAIN
    )
    assert (
        protocol.detect_protocol("NBScooter1", {16974: b""}, {UART_RX})
        == protocol.NINEBOT
    )


class FakeDevice:
    def __init__(self, address, name):
        self.address = address
        self.name = name


class FakeAdv:
    def __init__(self, name, rssi, manufacturer_data=None):
        self.local_name = name
        self.rssi = rssi
        self.manufacturer_data = manufacturer_data or {}


class FakeEnv:
    """Scooters nearby, Bluetooth scanner and client"""

    def __init__(self, mocker, scooter_module, fake_scooter):
        self.fake_scooter = fake_scooter
        self.connects = 0
        self.nearby = [
            # stronger, but used by another FHEM device already
            (
                FakeDevice("11:22:33:44:55:66", "MIScooter9"),
                FakeAdv("MIScooter9", -30),
            ),
            (
                FakeDevice(ADDRESS, "NBScooter1234"),
                FakeAdv("NBScooter1234", -50, {16974: b"\x00"}),
            ),
            (FakeDevice("00:00:00:00:00:01", "Phone"), FakeAdv("Phone", -40)),
        ]
        env = self

        class FakeScanner:
            def __init__(self, detection_callback):
                self.callback = detection_callback

            async def __aenter__(self):
                for device, adv in env.nearby:
                    self.callback(device, adv)
                return self

            async def __aexit__(self, *args):
                return False

        class FakeBleakClient:
            def __init__(self, device, timeout, disconnected_callback):
                assert device.address == ADDRESS
                env.fake_scooter.is_connected = True
                env.client = self
                self.disconnected_callback = disconnected_callback

            async def connect(self):
                env.connects += 1

            def __getattr__(self, attr):
                return getattr(env.fake_scooter, attr)

            @property
            def services(self):
                return []

        async def send_command(hash, cmd):
            return "1" if "'11:22:33:44:55:66'" in cmd else "0"

        mocker.patch("fhempy.lib.fhem.sendCommandHash", send_command)
        mocker.patch("bleak.BleakScanner", FakeScanner)
        mocker.patch("bleak.BleakClient", FakeBleakClient)
        mocker.patch.object(scooter_module, "SEARCH_TIME", 0.1)
        mocker.patch.object(scooter_module, "SCAN_TIME", 0.1)
        mocker.patch.object(scooter_module, "NB_PAIRING_TIMEOUT", 0.5)


async def wait_for(check):
    for _ in range(100):
        await asyncio.sleep(0.05)
        if check(mock_fhem.readings.get(NAME, {})):
            return
    raise AssertionError(f"Timeout, readings: {mock_fhem.readings.get(NAME)}")


async def define(mocker, fake_scooter, attrs=None):
    await check_and_install_dependencies("scooter")
    from fhempy.lib.scooter import scooter as scooter_module

    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes[NAME] = attrs or {}
    env = FakeEnv(mocker, scooter_module, fake_scooter)
    hash = {"NAME": NAME, "FHEMPYTYPE": "scooter"}
    module = scooter_module.scooter(logger)
    return env, hash, module


@pytest.mark.asyncio
async def test_module_search_pair_read(mocker):
    env, hash, module = await define(mocker, FakeNinebot())
    await module.Define(hash, [NAME, "fhempy", "scooter"], {})
    try:
        await wait_for(lambda r: r.get("battery") is not None)
        readings = mock_fhem.readings[NAME]
        assert readings["address"] == ADDRESS
        assert readings["name"] == "NBScooter1234"
        assert hash["MAC"] == ADDRESS
        assert readings["presence"] == "present"
        assert readings["protocol"] == "ninebot"
        assert readings["battery"] == 78
        assert readings["mileage"] == 1234.57
        assert readings["state"] == "78%"
        assert readings["connection"] == "disconnected"
        assert bytes.fromhex(readings[".pairing_key"]) in env.fake_scooter.known_keys

        # scooter is gone
        env.nearby.clear()
        await module.set_update(hash, {})
        await wait_for(lambda r: r["presence"] == "absent")
        assert mock_fhem.readings[NAME]["state"] == "absent"
    finally:
        await module.Undefine(hash)


@pytest.mark.asyncio
async def test_module_keeps_connection(mocker):
    env, hash, module = await define(
        mocker, FakeNinebot(), {"keep_connected": "1", "interval": "1"}
    )
    await module.Define(hash, [NAME, "fhempy", "scooter"], {})
    try:
        await wait_for(lambda r: r.get("connection") == "connected")
        mock_fhem.readings[NAME]["battery"] = None
        await module.set_update(hash, {})
        await wait_for(lambda r: r.get("battery") == 78)
        assert env.connects == 1

        # connection lost: connects again
        env.fake_scooter.is_connected = False
        env.client.disconnected_callback(env.client)
        await wait_for(lambda r: env.connects == 2)

        # attribute switched off
        await module.Attr(hash, ["set", NAME, "keep_connected", "0"], {})
        await wait_for(lambda r: r.get("connection") == "disconnected")
        assert not env.fake_scooter.is_connected
    finally:
        await module.Undefine(hash)


@pytest.mark.asyncio
async def test_module_stays_bound_to_first_scooter(mocker):
    """After the first scooter was found, no other scooter is used, even if
    the pairing wasn't confirmed or the scooter is away"""
    env, hash, module = await define(mocker, FakeNinebot(button_pressed=False))
    await module.Define(hash, [NAME, "fhempy", "scooter"], {})
    try:
        await wait_for(lambda r: r.get("state", "").startswith("pairing failed"))
        assert mock_fhem.readings[NAME]["address"] == ADDRESS

        # own scooter away, only another scooter nearby
        env.nearby[:] = [
            (
                FakeDevice("22:22:22:22:22:22", "NBScooter9999"),
                FakeAdv("NBScooter9999", -20, {16974: b"\x00"}),
            )
        ]
        await module.set_update(hash, {})
        await wait_for(lambda r: r.get("state") == "absent")
        assert mock_fhem.readings[NAME]["address"] == ADDRESS
        assert mock_fhem.readings[NAME]["name"] == "NBScooter1234"
    finally:
        await module.Undefine(hash)


@pytest.mark.asyncio
async def test_module_migrates_hidden_address(mocker):
    env, hash, module = await define(
        mocker, FakeNinebot(known_keys=[b"k" * 16], button_pressed=False)
    )
    mock_fhem.readings[NAME] = {".address": ADDRESS, ".pairing_key": "6b" * 16}
    await module.Define(hash, [NAME, "fhempy", "scooter"], {})
    try:
        await wait_for(lambda r: r.get("battery") == 78)
        readings = mock_fhem.readings[NAME]
        assert readings["address"] == ADDRESS
        assert ".address" not in readings
    finally:
        await module.Undefine(hash)
