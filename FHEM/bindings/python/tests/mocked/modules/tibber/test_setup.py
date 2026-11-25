import asyncio
import datetime
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


def _demo_home():
    """a home like the one of the Tibber demo account, without network"""
    from unittest.mock import AsyncMock, MagicMock

    home = MagicMock()
    today = datetime.datetime.now().astimezone().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    home.price_total = {
        (today + datetime.timedelta(minutes=15 * i)).isoformat(): 0.2
        + (i % 96) / 1000
        for i in range(2 * 96)
    }
    home.current_price_data.return_value = (0.25, today, 3)
    home.info = {
        "viewer": {
            "home": {
                "currentSubscription": {
                    "priceInfo": {
                        "current": {
                            "energy": 0.15,
                            "tax": 0.1,
                            "total": 0.25,
                            "startsAt": today.isoformat(),
                            "level": "NORMAL",
                        }
                    }
                }
            }
        }
    }
    home.address1 = "Winterfell Castle 1"
    home.has_active_subscription = True
    home.has_production = False
    home.has_real_time_consumption = True
    home.home_id = "68e6938b-91a6-4199-a0d4-f24c22be87bb"
    home.month_cons = 100.0
    home.month_cost = 25.0
    home.name = "Winterfell"
    home.peak_hour = 3.0
    home.update_info = AsyncMock()
    home.fetch_consumption_data = AsyncMock()

    async def rt_subscribe(callback):
        callback(
            {
                "data": {
                    "liveMeasurement": {
                        "power": 1200,
                        "powerProduction": 0,
                        "currentL3": 2.5,
                    }
                }
            }
        )

    home.rt_subscribe = rt_subscribe
    return home


@pytest.mark.asyncio
async def test_setup(mocker):
    """the whole setup with a connection like the demo account; the live
    demo api isn't used, it fails now and then (html instead of json)"""
    from unittest.mock import AsyncMock, MagicMock

    mock_fhem.mock_module(mocker)
    # readings are global, drop the ones other tests wrote for testdevice
    mock_fhem.readings.pop("testdevice", None)
    testhash = {
        "NAME": "testdevice",
        "FHEMPYTYPE": "tibber",
    }
    await check_and_install_dependencies("tibber")
    from fhempy.lib.tibber import tibber as tibber_module

    connection = MagicMock()
    connection.name = "Arya Stark"
    connection.user_id = "1"
    connection.update_info = AsyncMock()
    connection.close_connection = AsyncMock()
    connection.get_homes.return_value = [_demo_home()]
    mocker.patch.object(tibber_module, "Tibber", return_value=connection)

    fhempy_device = tibber_module.tibber(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["testdevice", "fhempy", "tibber", "token"],
        {},
    )
    for _ in range(100):
        readings = mock_fhem.readings.get("testdevice", {})
        if (
            "home_id" in readings
            and "current_price_total" in readings
            and "rt_currentL3" in readings
            and "cheapest_price_today" in readings
        ):
            break
        await asyncio.sleep(0.02)

    readings = mock_fhem.readings["testdevice"]
    assert readings["tibber_name"] == "Arya Stark"
    assert readings["address"] == "Winterfell Castle 1"
    assert readings["state"] == "connected"
    assert readings["current_price_total"] == pytest.approx(0.25)
    assert readings["rt_currentL3"] >= 0
    assert readings["rt_powerNet"] == 1200
    assert readings["today_0000"] == pytest.approx(0.2015)
    assert "cheapest_price_today" in readings

    await fhempy_device.Undefine(testhash)
    connection.close_connection.assert_awaited()


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
