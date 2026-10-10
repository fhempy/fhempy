import asyncio
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_setup(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    # readings are global, drop the ones other tests wrote for testdevice
    mock_fhem.readings.pop("testdevice", None)
    testhash = {
        "NAME": "testdevice",
        "FHEMPYTYPE": "tibber",
    }
    await check_and_install_dependencies("tibber")

    from tibber.const import DEMO_TOKEN

    from fhempy.lib.tibber.tibber import tibber

    fhempy_device = tibber(logging.getLogger(__name__))

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "fhempy",
            "tibber",
            DEMO_TOKEN,
        ],
        {},
    )
    # wait for home, price and realtime data from the tibber demo api,
    # failed updates are retried after 60s
    for _ in range(90):
        readings = mock_fhem.readings.get("testdevice", {})
        if (
            "home_id" in readings
            and "current_price_total" in readings
            and (
                not readings.get("has_real_time_consumption")
                or "rt_currentL3" in readings
            )
        ):
            break
        await asyncio.sleep(1)

    assert mock_fhem.readings["testdevice"]["tibber_name"] == "Arya Stark"
    # the demo account has two homes, the api returns them in varying order
    assert mock_fhem.readings["testdevice"]["address"] in [
        "Winterfell Castle 1",
        "123 Main St",
    ]
    # current_price_level is not provided in demo data
    # assert len(mock_fhem.readings["testdevice"]["current_price_level"]) > 0
    assert mock_fhem.readings["testdevice"]["current_price_total"] >= 0
    if mock_fhem.readings["testdevice"]["has_real_time_consumption"]:
        assert mock_fhem.readings["testdevice"]["rt_currentL3"] >= 0

    await fhempy_device.Undefine(testhash)


async def _define_with_mocked_tibber(mocker, name, tibber_mock):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(name, None)
    await check_and_install_dependencies("tibber")
    from fhempy.lib.tibber import tibber as tibber_module

    mocker.patch.object(tibber_module, "Tibber", return_value=tibber_mock)
    device = tibber_module.tibber(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": name, "FHEMPYTYPE": "tibber"},
        [name, "fhempy", "tibber", "token"],
        {},
    )
    return device


@pytest.mark.asyncio
async def test_invalid_token(mocker):
    from unittest.mock import AsyncMock, MagicMock

    await check_and_install_dependencies("tibber")
    from tibber.exceptions import InvalidLoginError

    connection = MagicMock()
    connection.update_info = AsyncMock(
        side_effect=InvalidLoginError(400, "invalid token", "UNAUTHENTICATED")
    )
    connection.close_connection = AsyncMock()
    device = await _define_with_mocked_tibber(mocker, "testtibbertoken", connection)
    # returns instead of retrying, no exception
    await asyncio.wait_for(device.setup_connection(), 5)
    assert mock_fhem.readings["testtibbertoken"]["state"] == "invalid token"


@pytest.mark.asyncio
async def test_no_active_home(mocker):
    from unittest.mock import AsyncMock, MagicMock

    connection = MagicMock()
    connection.name = "Test"
    connection.user_id = "1"
    connection.update_info = AsyncMock()
    connection.get_homes.return_value = []
    connection.close_connection = AsyncMock()
    device = await _define_with_mocked_tibber(mocker, "testtibberhome", connection)
    task = asyncio.create_task(device.setup_connection())
    for _ in range(50):
        if "state" in mock_fhem.readings.get("testtibberhome", {}):
            break
        await asyncio.sleep(0.01)
    task.cancel()
    assert (
        mock_fhem.readings["testtibberhome"]["state"]
        == "no home with active subscription"
    )
