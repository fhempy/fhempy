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
