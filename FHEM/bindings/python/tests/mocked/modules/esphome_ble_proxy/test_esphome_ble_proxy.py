import asyncio
import logging

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)

THERMOSTAT = "00:1A:22:11:22:33"
# flags + complete local name
ADV_DATA = bytes([2, 1, 6, 10, 9]) + b"CC-RT-BLE"


class FakeCli:
    """The part of aioesphomeapi.APIClient the proxy uses."""

    def __init__(self):
        from aioesphomeapi import APIVersion

        self.api_version = APIVersion(1, 12)
        self.subs = {}
        self.connects = []

    def subscribe_bluetooth_connections_free(self, callback):
        self.subs["free"] = callback

    def subscribe_bluetooth_scanner_state(self, callback):
        self.subs["state"] = callback

    def subscribe_bluetooth_le_raw_advertisements(self, callback):
        self.subs["raw"] = callback

    def subscribe_bluetooth_le_advertisements(self, callback):
        self.subs["adv"] = callback

    async def bluetooth_device_connect(self, address, on_state, **kwargs):
        self.connects.append(address)
        raise asyncio.TimeoutError("no device")

    async def device_info(self):
        return device_info()

    def advertise(self, address=THERMOSTAT, rssi=-60, data=ADV_DATA):
        from aioesphomeapi.api_pb2 import (
            BluetoothLERawAdvertisement,
            BluetoothLERawAdvertisementsResponse,
        )

        self.subs["raw"](
            BluetoothLERawAdvertisementsResponse(
                advertisements=[
                    BluetoothLERawAdvertisement(
                        address=int(address.replace(":", ""), 16),
                        rssi=rssi,
                        address_type=0,
                        data=data,
                    )
                ]
            )
        )


def device_info(active=True):
    from aioesphomeapi import BluetoothProxyFeature, DeviceInfo

    flags = (
        BluetoothProxyFeature.PASSIVE_SCAN
        | BluetoothProxyFeature.RAW_ADVERTISEMENTS
        | BluetoothProxyFeature.FEATURE_STATE_AND_MODE
    )
    if active:
        flags |= BluetoothProxyFeature.ACTIVE_CONNECTIONS
    return DeviceInfo(
        name="bt-proxy",
        friendly_name="BT Proxy",
        mac_address="AA:BB:CC:00:00:01",
        bluetooth_mac_address="AA:BB:CC:00:00:02",
        bluetooth_proxy_feature_flags=flags,
        model="esp32dev",
        esphome_version="2026.10.2",
    )


@pytest_asyncio.fixture
async def proxy_env(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("esphome_ble_proxy")
    from fhempy.lib.core import ble_proxy, ble_scanner

    mocker.patch.object(ble_proxy, "_proxies", {})
    mocker.patch.object(ble_scanner.BleScanner, "instance", None)
    scanner = ble_scanner.BleScanner.get_instance(logger)
    # no real scan task
    mocker.patch.object(scanner, "_run", mocker.AsyncMock())
    yield ble_proxy, scanner
    for proxy in ble_proxy.proxies():
        ble_proxy.unregister(proxy)


@pytest.mark.asyncio
async def test_advertisements_reach_the_shared_scan_callbacks(proxy_env):
    ble_proxy, scanner = proxy_env
    seen, local = [], []
    scanner.add_callback(lambda d, a: seen.append((d.address, a.local_name, a.rssi)))
    scanner.add_callback(lambda d, a: local.append(d.address), proxies=False)
    cli = FakeCli()
    proxy = ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.subs["free"](3, 3, [])

    # repeated advertisements are delivered too (presence)
    for _ in range(3):
        cli.advertise()

    assert seen == [(THERMOSTAT, "CC-RT-BLE", -60)] * 3
    assert local == []
    assert proxy.advertisements == 3
    assert proxy.connections_free == 3
    # not mixed into the devices of the local adapters
    assert scanner.recent_device(THERMOSTAT) is None
    device, rssi, best = ble_proxy.best_device(THERMOSTAT)
    assert (device.address, rssi, best) == (THERMOSTAT, -60, proxy)
    assert ble_proxy.is_proxy_device(device)

    ble_proxy.unregister(proxy)
    assert not ble_proxy.active()
    assert ble_proxy.best_device(THERMOSTAT) is None


@pytest.mark.asyncio
async def test_passive_proxy_is_not_used_for_connections(proxy_env):
    ble_proxy, _ = proxy_env
    cli = FakeCli()
    ble_proxy.register(logger, cli, device_info(active=False), "BT Proxy")
    cli.advertise()

    assert ble_proxy.best_device(THERMOSTAT) is None
    assert ble_proxy.best_device(THERMOSTAT, connectable=False) is not None


@pytest.mark.asyncio
async def test_client_connects_through_the_proxy(proxy_env):
    ble_proxy, _ = proxy_env
    cli = FakeCli()
    ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.subs["free"](3, 3, [])
    cli.advertise()
    device, _, _ = ble_proxy.best_device(THERMOSTAT)

    client = ble_proxy.bleak_client(device, timeout=1)
    with pytest.raises(asyncio.TimeoutError):
        await client.connect()

    assert cli.connects == [int(THERMOSTAT.replace(":", ""), 16)]
    await client.disconnect()


def test_proxy_or_local_adapter():
    from fhempy.lib.core import ble_proxy

    # not seen locally
    assert ble_proxy.use_proxy(-90, None)
    # local adapter is preferred unless the proxy is clearly better
    assert not ble_proxy.use_proxy(-70, -75)
    assert ble_proxy.use_proxy(-60, -80)


@pytest.mark.asyncio
async def test_bluetoothle_connects_via_proxy_without_local_adapter(proxy_env, mocker):
    ble_proxy, _ = proxy_env
    await check_and_install_dependencies("blue_connect")
    from fhempy.lib.core import bluetoothle

    mock_fhem.readings.pop("testble", None)
    cli = FakeCli()
    proxy = ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.advertise(rssi=-70)

    conn = bluetoothle.BluetoothLE(
        logger, {"NAME": "testble"}, THERMOSTAT, pairing_required=True, pin="1234"
    )
    conn.conf_checked = True
    mocker.patch.object(conn, "update_adapters", mocker.AsyncMock())
    conn.adapters = []
    client = mocker.MagicMock(is_connected=True)
    client.connect = mocker.AsyncMock()
    client.disconnect = mocker.AsyncMock()
    proxy_client = mocker.patch.object(ble_proxy, "client", return_value=client)
    pair = mocker.patch.object(conn, "pair")
    mocker.patch.object(conn, "_subscribe_notifies", mocker.AsyncMock())

    await conn.connect_loop(1, 1)

    pair.assert_not_called()
    assert proxy_client.call_args.args[0].address == THERMOSTAT
    readings = mock_fhem.readings["testble"]
    assert readings["connection"] == "connected"
    assert readings["connection_adapter"] == "BT Proxy"
    assert readings["connection_adapter_details"] == f"ESPHome proxy ({proxy.source})"
    assert readings["rssi"] == -70
    assert conn.connected.is_set()
    await conn.disconnect()


@pytest.mark.asyncio
async def test_bluetoothle_pin_device_falls_back_to_local_pairing(proxy_env, mocker):
    ble_proxy, _ = proxy_env
    await check_and_install_dependencies("blue_connect")
    from bleak.exc import BleakError

    from fhempy.lib.core import bluetoothle

    mock_fhem.readings.pop("testble", None)
    cli = FakeCli()
    ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.advertise(rssi=-70)

    conn = bluetoothle.BluetoothLE(
        logger, {"NAME": "testble"}, THERMOSTAT, pairing_required=True, pin="1234"
    )
    conn.conf_checked = True
    mocker.patch.object(conn, "update_adapters", mocker.AsyncMock())
    conn.adapters = ["hci0"]
    client = mocker.MagicMock(is_connected=True)
    client.connect = mocker.AsyncMock()
    client.disconnect = mocker.AsyncMock()
    client.pair = mocker.AsyncMock(side_effect=BleakError("not supported"))
    mocker.patch.object(ble_proxy, "client", return_value=client)
    mocker.patch.object(
        conn,
        "_subscribe_notifies",
        mocker.AsyncMock(
            side_effect=BleakError(
                "Bluetooth GATT Error handle=1072 error=5 "
                "description=Insufficient authentication"
            )
        ),
    )
    find_device = mocker.patch.object(conn, "find_device")

    await conn.connect_once(1, 1)

    client.pair.assert_awaited_once()
    client.disconnect.assert_awaited()
    # back to connect_loop, which pairs via the local adapter
    find_device.assert_not_called()
    assert conn._client is None
    assert not conn.connected.is_set()
    assert mock_fhem.readings["testble"]["connection_proxy"] == ("pairing failed (PIN)")
    assert conn._proxy_choice() is None

    # local pairing fails (e.g. out of range): the proxy is tried again
    assert conn._retry_proxy()
    assert conn._proxy_choice() is not None
    # no proxy failure, nothing to retry
    assert not conn._retry_proxy()


@pytest.mark.asyncio
async def test_bluetoothle_pin_device_pairs_via_proxy(proxy_env, mocker):
    ble_proxy, _ = proxy_env
    await check_and_install_dependencies("blue_connect")
    from fhempy.lib.core import bluetoothle

    mock_fhem.readings.pop("testble", None)
    cli = FakeCli()
    ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.advertise(rssi=-60)

    conn = bluetoothle.BluetoothLE(
        logger, {"NAME": "testble"}, THERMOSTAT, pairing_required=True, pin="1234"
    )
    conn.conf_checked = True
    mocker.patch.object(conn, "update_adapters", mocker.AsyncMock())
    conn.adapters = ["hci0"]
    client = mocker.MagicMock(is_connected=True)
    client.connect = mocker.AsyncMock()
    client.disconnect = mocker.AsyncMock()
    # the proxy's YAML answers the PIN request
    client.pair = mocker.AsyncMock()
    mocker.patch.object(ble_proxy, "client", return_value=client)
    mocker.patch.object(conn, "_subscribe_notifies", mocker.AsyncMock())

    await conn.connect_once(1, 1)

    client.pair.assert_awaited_once()
    assert conn.connected.is_set()
    assert mock_fhem.readings["testble"]["connection"] == "connected"
    assert mock_fhem.readings["testble"]["connection_adapter"] == "BT Proxy"
    await conn.disconnect()


@pytest.mark.asyncio
async def test_bluetoothle_prefers_local_adapter(proxy_env, mocker):
    ble_proxy, scanner = proxy_env
    await check_and_install_dependencies("blue_connect")
    from fhempy.lib.core import bluetoothle

    cli = FakeCli()
    ble_proxy.register(logger, cli, device_info(), "BT Proxy")
    cli.advertise(rssi=-70)
    scanner.add_callback(lambda d, a: None)
    local_device = mocker.MagicMock(address=THERMOSTAT)
    scanner._detection(local_device, mocker.MagicMock(rssi=-72))

    conn = bluetoothle.BluetoothLE(logger, {"NAME": "testble"}, THERMOSTAT)
    assert conn._proxy_choice() is None

    scanner._recent.clear()
    assert conn._proxy_choice() is not None


@pytest.mark.asyncio
async def test_ble_monitor_parses_proxy_advertisements(mocker):
    await check_and_install_dependencies("ble_monitor")
    from bleparser import BleParser

    from fhempy.lib.ble_monitor.blemonitor import hci_packet

    # ATC thermometer: 21.5 °C, 55 %, 80 % battery
    payload = (
        bytes.fromhex("a4c138112233")
        + (215).to_bytes(2, "big")
        + bytes([55, 80])
        + (2950).to_bytes(2, "big")
        + bytes([7])
    )
    data = bytes([2, 1, 6, len(payload) + 3, 0x16, 0x1A, 0x18]) + payload
    packet = hci_packet("A4:C1:38:11:22:33", 0, -70, data)

    sensor, _ = BleParser(discovery=True).parse_raw_data(packet)

    assert sensor["mac"] == "A4C138112233"
    assert sensor["temperature"] == 21.5
    assert sensor["humidity"] == 55
    assert sensor["rssi"] == -70


@pytest.mark.asyncio
async def test_define_registers_proxy(proxy_env, mocker):
    ble_proxy, _ = proxy_env
    from fhempy.lib.esphome_ble_proxy import esphome_ble_proxy as module

    mock_fhem.readings.pop("testproxy", None)
    cli = FakeCli()
    mocker.patch.object(module, "APIClient", return_value=cli)
    reconnect = mocker.MagicMock()
    reconnect.start = mocker.AsyncMock()
    reconnect.stop = mocker.AsyncMock()
    logic = mocker.patch.object(module, "ReconnectLogic", return_value=reconnect)
    mocker.patch.object(module.zeroconf, "get_instance")
    hash = {"NAME": "testproxy", "FHEMPYTYPE": "esphome_ble_proxy"}
    device = module.esphome_ble_proxy(logger)

    await device.Define(
        hash, ["testproxy", "fhempy", "esphome_ble_proxy", "bt-proxy.local"], {}
    )
    await asyncio.sleep(0)
    await logic.call_args.kwargs["on_connect"]()

    readings = mock_fhem.readings["testproxy"]
    assert readings["state"] == "connected"
    assert readings["active_connections"] == "yes"
    assert readings["bluetooth_mac"] == "AA:BB:CC:00:00:02"
    assert ble_proxy.active()

    await logic.call_args.kwargs["on_disconnect"](False)
    assert mock_fhem.readings["testproxy"]["state"] == "disconnected"
    assert not ble_proxy.active()

    from aioesphomeapi.core import InvalidEncryptionKeyAPIError

    await logic.call_args.kwargs["on_connect_error"](
        InvalidEncryptionKeyAPIError("wrong")
    )
    assert mock_fhem.readings["testproxy"]["state"] == "wrong encryption key"

    await device.Undefine(hash)
    reconnect.stop.assert_awaited_once()


def test_define_usage():
    from fhempy.lib.esphome_ble_proxy.esphome_ble_proxy import (
        _parse_host,
        esphome_ble_proxy,
    )

    assert esphome_ble_proxy.validate_define(["a", "fhempy", "x"], {})
    assert esphome_ble_proxy.validate_define(["a", "fhempy", "x", "host"], {}) is None
    assert _parse_host("bt-proxy.local") == ("bt-proxy.local", 6053)
    assert _parse_host("192.168.1.5:6054") == ("192.168.1.5", 6054)
