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
