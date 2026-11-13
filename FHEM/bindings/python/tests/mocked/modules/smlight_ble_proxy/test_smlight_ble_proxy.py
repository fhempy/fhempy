import asyncio
import logging
import struct

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)

TAG = "C4:7C:8D:11:22:33"
# flags + complete local name
ADV_DATA = bytes([2, 1, 6, 4, 9]) + b"Tag"
PING, DISCONNECT, ACK, DATA, SET_SCAN_MODE = 0, 1, 2, 3, 4


def data_packet(address=TAG, rssi=-65, data=ADV_DATA):
    mac = bytes(reversed(bytes.fromhex(address.replace(":", ""))))
    return struct.pack("<BB6sBbB", 0, DATA, mac, 0, rssi, len(data)) + data


class FakeSlzb(asyncio.DatagramProtocol):
    """BLE proxy of SLZB-OS: answers the keepalive with ACK."""

    def __init__(self):
        self.client = None
        self.received = []

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        self.received.append(data)
        if data[1] == PING:
            self.client = addr
            self.transport.sendto(bytes([0, ACK]), addr)

    def advertise(self, packet):
        self.transport.sendto(packet, self.client)


@pytest_asyncio.fixture
async def proxy_env(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("smlight_ble_proxy")
    from fhempy.lib.core import ble_proxy, ble_scanner

    mocker.patch.object(ble_proxy, "_proxies", {})
    mocker.patch.object(ble_scanner.BleScanner, "instance", None)
    scanner = ble_scanner.BleScanner.get_instance(logger)
    mocker.patch.object(scanner, "_run", mocker.AsyncMock())
    loop = asyncio.get_running_loop()
    transport, slzb = await loop.create_datagram_endpoint(
        FakeSlzb, local_addr=("127.0.0.1", 0)
    )
    port = transport.get_extra_info("sockname")[1]
    yield ble_proxy, scanner, slzb, port
    for proxy in ble_proxy.proxies():
        ble_proxy.unregister(proxy)
    transport.close()


async def wait_for(condition, timeout=3):
    for _ in range(int(timeout * 20)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("timeout")


@pytest.mark.asyncio
async def test_advertisements_reach_the_shared_scan_and_ble_monitor(proxy_env):
    ble_proxy, scanner, slzb, port = proxy_env
    seen, raw = [], []
    scanner.add_callback(lambda d, a: seen.append((d.address, a.local_name, a.rssi)))
    callback = lambda *args: raw.append(args)  # noqa: E731
    ble_proxy.add_raw_callback(callback)
    try:
        proxy = ble_proxy.register_smlight(
            logger, "127.0.0.1", port, "AA:BB:CC:00:00:09", "slzb"
        )
        await proxy.start()
        await wait_for(lambda: proxy.connected)
        proxy.send_scan_mode()
        await wait_for(lambda: any(p[1] == SET_SCAN_MODE for p in slzb.received))
        # passive scan mode sent to the proxy
        assert [p for p in slzb.received if p[1] == SET_SCAN_MODE][0] == bytes(
            [0, SET_SCAN_MODE, 0]
        )

        # one UDP packet may contain several advertisements
        slzb.advertise(data_packet() + data_packet(rssi=-70))
        await wait_for(lambda: len(seen) == 2)
    finally:
        ble_proxy.remove_raw_callback(callback)

    assert seen == [(TAG, "Tag", -65), (TAG, "Tag", -70)]
    assert raw[0] == (TAG, 0, -65, ADV_DATA, "slzb")
    assert proxy.advertisements == 2
    assert ble_proxy.active()
    # scan only: never used for connections
    assert not ble_proxy.active(connectable=True)
    assert ble_proxy.best_device(TAG) is None
    device, rssi, best = ble_proxy.best_device(TAG, connectable=False)
    assert (device.address, rssi, best) == (TAG, -70, proxy)

    ble_proxy.unregister(proxy)
    assert not ble_proxy.active()
    # the client said goodbye
    await wait_for(lambda: slzb.received[-1] == bytes([0, DISCONNECT]))


@pytest.mark.asyncio
async def test_register_same_source_replaces_proxy(proxy_env):
    ble_proxy, _, _, port = proxy_env
    first = ble_proxy.register_smlight(logger, "127.0.0.1", port, "src", "slzb")
    second = ble_proxy.register_smlight(logger, "127.0.0.1", port, "src", "slzb")
    assert ble_proxy.proxies() == [second]
    assert first is not second


@pytest.mark.asyncio
async def test_module_define(proxy_env, mocker):
    ble_proxy, _, slzb, port = proxy_env
    from fhempy.lib.smlight_ble_proxy import smlight_ble_proxy as module

    mocker.patch.object(
        module,
        "read_info",
        mocker.AsyncMock(
            return_value={
                "mac": "AA:BB:CC:00:00:0A",
                "model": "SLZB-06MU",
                "firmware": "v3.4.5",
                "hostname": "slzb-06mu",
                "ble_proxy": True,
            }
        ),
    )
    mock_fhem.readings.pop("slzb", None)
    hash = {"NAME": "slzb", "FHEMPYTYPE": "smlight_ble_proxy"}
    dev = module.smlight_ble_proxy(logger)
    tasks = []
    mocker.patch.object(
        dev, "create_async_task", lambda c: tasks.append(asyncio.ensure_future(c))
    )
    assert await dev.Define(hash, ["slzb", "fhempy", "smlight_ble_proxy"], {}) == (
        module.USAGE
    )
    await dev.Define(
        hash, ["slzb", "fhempy", "smlight_ble_proxy", f"127.0.0.1:{port}"], {}
    )
    await tasks[0]
    readings = mock_fhem.readings["slzb"]
    assert readings["state"] == "connected"
    assert readings["model"] == "SLZB-06MU"
    assert readings["mac"] == "AA:BB:CC:00:00:0A"
    proxy = ble_proxy.proxies()[0]
    assert proxy.source == "AA:BB:CC:00:00:0A"

    slzb.advertise(data_packet())
    await wait_for(lambda: proxy.advertisements == 1)

    await dev.Undefine(hash)
    assert not ble_proxy.active()
    for task in tasks:
        task.cancel()


@pytest.mark.asyncio
async def test_disabled_ble_proxy_and_silence(proxy_env, mocker):
    ble_proxy, _, _, port = proxy_env
    from fhempy.lib.smlight_ble_proxy import smlight_ble_proxy as module

    dev = module.smlight_ble_proxy(logger)
    dev._proxy = mocker.Mock(connected=True)
    dev._ble_proxy_enabled = False
    assert dev._state() == "BLE proxy disabled in SLZB-OS"
    dev._ble_proxy_enabled = None
    dev._silent_since = asyncio.get_running_loop().time() - module.SILENT_AFTER - 1
    assert dev._state(0).startswith("no advertisements")
    assert dev._state(12) == "connected"
    dev._proxy.connected = False
    assert dev._state() == "connecting"


def test_helpers():
    from fhempy.lib.smlight_ble_proxy import smlight_ble_proxy as module

    assert module._parse_host("slzb.local") == ("slzb.local", 5050)
    assert module._parse_host("192.168.1.2:6000") == ("192.168.1.2", 6000)
    assert module._format_mac("aabbcc001122") == "AA:BB:CC:00:11:22"
    assert module._format_mac("AA:BB:CC:00:11:22") == "AA:BB:CC:00:11:22"
    assert module._format_mac("") is None
    assert module._format_mac("123") is None
