import asyncio
import logging

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.core.bt_pairing_state import PairingState
from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest_asyncio.fixture
async def ble(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("blue_connect")
    from fhempy.lib.core import bluetoothle

    mock_fhem.readings.pop("testble", None)
    mocker.patch.object(bluetoothle, "PAIRING_RETRY", 0)
    conn = bluetoothle.BluetoothLE(
        logging.getLogger(__name__),
        {"NAME": "testble"},
        "AA:BB:CC:DD:EE:FF",
        pairing_required=True,
    )
    # skip the bluetooth.conf check
    conn.conf_checked = True
    yield conn
    await conn.disconnect()


def connect_succeeds(conn, mocker):
    async def connect_once(timeout, max_retries):
        conn._client = mocker.MagicMock(is_connected=True)
        conn._client.write_gatt_char = mocker.AsyncMock()
        conn._client.disconnect = mocker.AsyncMock()
        conn.connected.set()

    return mocker.patch.object(conn, "connect_once", side_effect=connect_once)


@pytest.mark.asyncio
async def test_failed_pairing_is_retried(ble, mocker):
    pair = mocker.patch.object(
        ble, "pair", side_effect=[PairingState.TIMEOUT, PairingState.SUCCESS]
    )
    connect_once = connect_succeeds(ble, mocker)

    await ble.connect()
    await asyncio.wait_for(ble.connected.wait(), 1)

    assert pair.call_count == 2
    assert connect_once.call_count == 1


@pytest.mark.asyncio
async def test_write_restarts_finished_connection_loop(ble, mocker):
    # first connection loop ended without a connection
    ble.paired = True
    ble.connection_task = asyncio.get_running_loop().create_future()
    ble.connection_task.set_result(None)
    connect_succeeds(ble, mocker)

    await ble.write_gatt_char("uuid", b"\x01")

    ble._client.write_gatt_char.assert_awaited_once_with("uuid", b"\x01")


@pytest.mark.asyncio
async def test_no_adapter(ble, mocker):
    ble.paired = True
    mocker.patch.object(ble, "update_adapters", mocker.AsyncMock())
    ble.adapters = []
    find_device = mocker.patch.object(ble, "find_device")

    await ble.connect_once(1, 1)

    find_device.assert_not_called()
    assert mock_fhem.readings["testble"]["connection"] == "no adapter"


@pytest.mark.asyncio
async def test_not_found_backs_off(ble, mocker):
    from fhempy.lib.core import bluetoothle

    mocker.patch.object(bluetoothle, "PAIRING_RETRY", 300)
    mocker.patch.object(bluetoothle, "PAIRING_RETRY_MAX", 1000)
    waits = []

    async def sleep(seconds):
        waits.append(seconds)
        assert mock_fhem.readings["testble"]["connection"] == "not found"

    mocker.patch.object(bluetoothle.asyncio, "sleep", side_effect=sleep)
    mocker.patch.object(
        ble,
        "pair",
        side_effect=[PairingState.NOT_FOUND] * 4 + [PairingState.SUCCESS],
    )
    connect_succeeds(ble, mocker)

    await ble.connect_loop(30, 1)

    assert waits == [300, 600, 1000, 1000]


def test_pair_scans_once_if_not_found(ble, mocker):
    import sys

    bt_mgr = mocker.MagicMock()
    bt_mgr.is_device_paired.return_value = False
    bt_mgr.find_device_path.return_value = None
    bt_mgr.discover_device_path.return_value = None
    bt_manager = mocker.MagicMock()
    bt_manager.BluetoothManager.return_value = bt_mgr
    mocker.patch.dict(sys.modules, {"fhempy.lib.core.bt_manager": bt_manager})

    assert ble._pair("0000") == PairingState.NOT_FOUND
    assert bt_mgr.discover_device_path.call_count == 1
    bt_mgr.unregister_agent.assert_called_once()


async def not_found_with_working_adapter(ble, mocker, stale_result):
    from fhempy.lib.core import bluetoothle

    ble.paired = True
    mocker.patch.object(ble, "update_adapters", mocker.AsyncMock())
    ble.adapters = ["hci0"]
    ble.adapter_details = {"hci0": {"address": "00:11:22:33:44:55"}}
    # other devices seen, but not ours
    mocker.patch.object(ble, "find_device", mocker.AsyncMock(return_value=True))
    mocker.patch.object(bluetoothle.asyncio, "sleep", mocker.AsyncMock())
    drop = mocker.patch.object(
        bluetoothle.bt_recovery,
        "drop_stale_connection",
        mocker.AsyncMock(return_value=stale_result),
    )
    report_failure = mocker.patch.object(
        bluetoothle.bt_recovery, "report_failure", mocker.AsyncMock(return_value=None)
    )
    await ble.connect_once(1, 1)
    return drop, report_failure


@pytest.mark.asyncio
async def test_stale_connection_dropped_when_not_found(ble, mocker):
    drop, report_failure = await not_found_with_working_adapter(
        ble, mocker, "stale connection dropped: ok"
    )
    drop.assert_awaited_once_with("hci0", "AA:BB:CC:DD:EE:FF")
    report_failure.assert_not_called()
    assert (
        mock_fhem.readings["testble"]["connection_recovery"]
        == "hci0 stale connection dropped: ok"
    )


@pytest.mark.asyncio
async def test_stale_connection_not_dropped_counts_as_failure(ble, mocker):
    _, report_failure = await not_found_with_working_adapter(
        ble, mocker, "stale connection dropped: failed"
    )
    report_failure.assert_awaited_once_with("hci0", "00:11:22:33:44:55")


@pytest.mark.asyncio
async def test_not_found_without_stale_connection(ble, mocker):
    drop, report_failure = await not_found_with_working_adapter(ble, mocker, None)
    drop.assert_awaited_once()
    report_failure.assert_not_called()


@pytest.mark.asyncio
async def test_unexpected_disconnect_releases_client(ble, mocker):
    # bleak closes its D-Bus connection only in disconnect() (#761)
    client = mocker.MagicMock(is_connected=False)
    client.disconnect = mocker.AsyncMock()
    ble._client = client
    connect = mocker.patch.object(ble, "connect", mocker.AsyncMock())

    await ble.async_disconnected(client)

    client.disconnect.assert_awaited_once()
    connect.assert_awaited_once()
    assert ble._client is None


@pytest.mark.asyncio
async def test_unexpected_disconnect_keeps_new_client(ble, mocker):
    old_client = mocker.MagicMock(is_connected=False)
    old_client.disconnect = mocker.AsyncMock(side_effect=Exception("dbus"))
    new_client = mocker.MagicMock(is_connected=True)
    new_client.disconnect = mocker.AsyncMock()
    ble._client = new_client
    mocker.patch.object(ble, "connect", mocker.AsyncMock())

    await ble.async_disconnected(old_client)

    old_client.disconnect.assert_awaited_once()
    assert ble._client is new_client


@pytest.mark.asyncio
async def test_connect_loop_imports_backend_in_thread(ble, mocker):
    """the first BleakClient would import bleak's BlueZ backend (dbus_fast)
    on the event loop"""
    from fhempy.lib.core import ble_scanner

    load = mocker.patch.object(ble_scanner, "load_backend", mocker.AsyncMock())
    mocker.patch.object(ble, "pair", return_value=PairingState.SUCCESS)
    connect_succeeds(ble, mocker)

    await ble.connect_loop(30, 1)

    load.assert_awaited_once()


def _proxy_found(ble, mocker, proxy_rssi=-60, local_rssi=-90):
    from fhempy.lib.core import ble_proxy

    mocker.patch.object(ble_proxy, "active", return_value=True)
    found = (mocker.MagicMock(), proxy_rssi, mocker.MagicMock())
    mocker.patch.object(ble_proxy, "best_device", return_value=found)
    mocker.patch.object(ble, "_local_rssi", return_value=local_rssi)
    return found


@pytest.mark.asyncio
async def test_adapter_auto_uses_proxy_with_better_signal(ble, mocker):
    found = _proxy_found(ble, mocker)
    assert ble._proxy_choice() == found


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["local", "hci0"])
async def test_adapter_local_never_uses_proxy(ble, mocker, mode):
    _proxy_found(ble, mocker)
    ble.adapter_mode = mode
    assert ble._proxy_choice() is None


@pytest.mark.asyncio
async def test_adapter_proxy_ignores_better_local_signal(ble, mocker):
    found = _proxy_found(ble, mocker, proxy_rssi=-90, local_rssi=-50)
    assert ble._proxy_choice() is None
    ble.adapter_mode = "proxy"
    assert ble._proxy_choice() == found


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,expected",
    [
        (None, ["hci0", "hci1"]),
        ("local", ["hci0", "hci1"]),
        ("hci1", ["hci1"]),
        ("hci2", []),
        ("proxy", []),
    ],
)
async def test_adapter_mode_filters_local_adapters(ble, mocker, mode, expected):
    from fhempy.lib.core import bluetoothle

    mocker.patch.object(
        bluetoothle.bluetooth_adapters,
        "get_bluetooth_adapters",
        mocker.AsyncMock(return_value=["hci0", "hci1"]),
    )
    adapters = mocker.MagicMock(adapters={})
    adapters.refresh = mocker.AsyncMock()
    mocker.patch.object(
        bluetoothle.bluetooth_adapters, "get_adapters", return_value=adapters
    )
    ble.adapter_mode = mode

    await ble.update_adapters()

    assert ble.adapters == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, None),
        ("", None),
        ("auto", None),
        ("local", "local"),
        ("Proxy", "proxy"),
        ("proxy:Garten_Proxy", "proxy:Garten_Proxy"),
        ("hci1", "hci1"),
        ("1", "hci1"),
    ],
)
def test_adapter_mode_values(value, expected):
    from fhempy.lib.core import bluetoothle

    assert bluetoothle.adapter_mode(value) == expected


@pytest.mark.asyncio
async def test_fixed_proxy_only_uses_that_proxy(ble, mocker):
    from fhempy.lib.core import ble_proxy

    near = mocker.MagicMock(connectable=True, source="11:22", recent_device=None)
    near.name = "Garten Proxy"
    near.recent_device = mocker.MagicMock(return_value=(mocker.MagicMock(), -50))
    far = mocker.MagicMock(connectable=True, source="33:44")
    far.name = "Keller"
    far.recent_device = mocker.MagicMock(return_value=(mocker.MagicMock(), -80))
    mocker.patch.dict(ble_proxy._proxies, {"11:22": near, "33:44": far}, clear=True)

    ble.adapter_mode = "proxy:Keller"
    assert ble._proxy_choice()[2] is far
    ble.adapter_mode = "proxy:garten_proxy"
    assert ble._proxy_choice()[2] is near
    ble.adapter_mode = "proxy:33:44"
    assert ble._proxy_choice()[2] is far
    ble.adapter_mode = "proxy:unknown"
    assert ble._proxy_choice() is None
    assert ble_proxy.option_name(near) == "Garten_Proxy"


@pytest.mark.asyncio
async def test_fixed_adapter_registers_at_shared_scan(ble, mocker):
    from fhempy.lib.core import ble_scanner

    scanner = mocker.MagicMock()
    mocker.patch.object(ble_scanner.BleScanner, "get_instance", return_value=scanner)
    mocker.patch.object(ble_scanner.BleScanner, "instance", scanner)
    connect_succeeds(ble, mocker)
    ble.paired = True
    ble.adapter_mode = "hci1"

    await ble.connect()
    await asyncio.wait_for(ble.connected.wait(), 1)
    scanner.add_callback.assert_called_once_with(
        ble._scan_callback, proxies=False, adapter="hci1"
    )

    await ble.disconnect()
    scanner.remove_callback.assert_called_once_with(ble._scan_callback)


@pytest.mark.asyncio
async def test_auto_doesnt_register_at_shared_scan(ble, mocker):
    from fhempy.lib.core import ble_scanner

    get_instance = mocker.patch.object(ble_scanner.BleScanner, "get_instance")
    connect_succeeds(ble, mocker)
    ble.paired = True

    await ble.connect()
    await asyncio.wait_for(ble.connected.wait(), 1)
    get_instance.assert_not_called()


@pytest.mark.asyncio
async def test_find_device_waits_for_shared_scan(ble, mocker):
    from fhempy.lib.core import bluetoothle, ble_scanner

    dev = mocker.MagicMock()
    scanner = mocker.MagicMock()
    scanner.recent_device.return_value = None
    scanner.listens_on.return_value = True
    scanner.wait_for_device = mocker.AsyncMock(return_value=((dev, -55), False))
    mocker.patch.object(
        ble_scanner.BleScanner, "running_instance", return_value=scanner
    )
    own_scan = mocker.patch.object(
        bluetoothle.BleakScanner, "find_device_by_filter", mocker.AsyncMock()
    )

    assert await ble.find_device(timeout=5, adapter="hci1")
    assert ble._device is dev and ble._rssi == -55
    scanner.recent_device.assert_called_once_with(ble.addr, adapter="hci1")
    scanner.wait_for_device.assert_awaited_once_with(
        ble.addr, adapter="hci1", timeout=5
    )
    own_scan.assert_not_called()


@pytest.mark.asyncio
async def test_find_device_quiet_adapter_reported(ble, mocker):
    from fhempy.lib.core import ble_scanner

    scanner = mocker.MagicMock()
    scanner.recent_device.return_value = None
    scanner.listens_on.return_value = True
    scanner.wait_for_device = mocker.AsyncMock(return_value=(None, True))
    mocker.patch.object(
        ble_scanner.BleScanner, "running_instance", return_value=scanner
    )

    assert not await ble.find_device(timeout=5, adapter="hci0")
    assert ble._device is None


@pytest.mark.asyncio
async def test_own_scan_pauses_shared_scan_on_same_adapter(ble, mocker):
    import contextlib

    from fhempy.lib.core import bluetoothle, ble_scanner

    events = []

    @contextlib.asynccontextmanager
    async def paused():
        events.append("pause")
        yield
        events.append("resume")

    async def own_scan(*args, **kwargs):
        events.append("scan")
        return None

    scanner = mocker.MagicMock()
    scanner.recent_device.return_value = None
    # e.g. interval mode: the shared scan doesn't listen right now
    scanner.listens_on.return_value = False
    scanner.scans_adapter.return_value = True
    scanner.paused = paused
    mocker.patch.object(
        ble_scanner.BleScanner, "running_instance", return_value=scanner
    )
    mocker.patch.object(
        bluetoothle.BleakScanner, "find_device_by_filter", side_effect=own_scan
    )

    await ble.find_device(timeout=5, adapter="hci0")
    assert events == ["pause", "scan", "resume"]

    # an adapter the shared scan doesn't use: no pause
    events.clear()
    scanner.scans_adapter.return_value = False
    await ble.find_device(timeout=5, adapter="hci2")
    assert events == ["scan"]
