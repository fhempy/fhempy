import asyncio
import logging
from unittest.mock import AsyncMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_setters_use_homes_api(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("erelax_vaillant")

    from vaillant_netatmo_api import (
        AuthClient,
        Device,
        Home,
        TemperatureControlMode,
        ThermMode,
        ThermostatClient,
        ThermSetpointMode,
    )

    from fhempy.lib.erelax_vaillant.erelax_vaillant import erelax_vaillant

    mocker.patch.object(AuthClient, "async_token", AsyncMock())
    mocker.patch.object(
        ThermostatClient,
        "async_get_homes_data",
        AsyncMock(return_value=[Home(id="home1", rooms=[{"id": "room1"}])]),
    )
    device_data = Device(
        _id="station1",
        system_mode="winter",
        setpoint_default_duration=60,
        modules=[{"_id": "module1", "measured": {"temperature": 20.5}}],
    )
    mocker.patch.object(
        ThermostatClient,
        "async_get_thermostats_data",
        AsyncMock(return_value=[device_data]),
    )
    set_home_data = mocker.patch.object(
        ThermostatClient, "async_set_home_data", AsyncMock()
    )
    set_room = mocker.patch.object(
        ThermostatClient, "async_set_state_for_room", AsyncMock()
    )

    testhash = {"NAME": "vaillant", "FHEMPYTYPE": "erelax_vaillant"}
    mock_fhem.readings.pop("vaillant", None)
    device = erelax_vaillant(logging.getLogger(__name__))
    await device.Define(
        testhash,
        ["vaillant", "fhempy", "erelax_vaillant", "user", "pass"],
        {},
    )
    await asyncio.sleep(1)
    assert mock_fhem.readings["vaillant"]["state"] == "connected"
    assert mock_fhem.readings["vaillant"]["temperature"] == 20.5

    await device.set_away(testhash, {})
    await device.set_home(testhash, {})
    await device.set_system_mode(testhash, {"mode": "summer"})
    await device.set_system_mode(testhash, {"mode": "frostguard"})
    await device.set_desiredTemperatureDuration(
        testhash, {"temperature": 21.5, "duration": 30}
    )
    await asyncio.sleep(0.1)

    assert [c.args for c in set_home_data.await_args_list] == [
        ("home1", TemperatureControlMode.HEATING, ThermMode.AWAY),
        ("home1", TemperatureControlMode.HEATING, ThermMode.SCHEDULE),
        ("home1", TemperatureControlMode.COOLING, None),
        ("home1", TemperatureControlMode.HEATING, ThermMode.HG),
    ]
    call = set_room.await_args
    assert call.args == ("home1", "room1", ThermSetpointMode.MANUAL)
    assert call.kwargs["therm_setpoint_temperature"] == 21.5
    await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_set_before_login(mocker):
    # sets failed with AttributeError in the background before the login
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("erelax_vaillant")

    from vaillant_netatmo_api import AuthClient

    from fhempy.lib.erelax_vaillant.erelax_vaillant import erelax_vaillant

    mocker.patch.object(
        AuthClient, "async_token", AsyncMock(side_effect=RuntimeError("login"))
    )
    testhash = {"NAME": "vaillant", "FHEMPYTYPE": "erelax_vaillant"}
    mock_fhem.readings.pop("vaillant", None)
    device = erelax_vaillant(logging.getLogger(__name__))
    await device.Define(
        testhash,
        ["vaillant", "fhempy", "erelax_vaillant", "user", "pass"],
        {},
    )
    await asyncio.sleep(0.1)
    try:
        for cmd in (["away"], ["system_mode", "summer"], ["desiredTemperature", "21"]):
            ret = await device.Set(testhash, ["vaillant"] + cmd, {})
            assert "Not connected to Vaillant yet" in ret
    finally:
        await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_send_error_is_logged(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("erelax_vaillant")
    from fhempy.lib.erelax_vaillant.erelax_vaillant import erelax_vaillant

    device = erelax_vaillant(logging.getLogger(__name__))
    error = mocker.patch.object(device.logger, "error")

    await device._send(AsyncMock(side_effect=TimeoutError())())

    error.assert_called_once_with("Failed to send command to Vaillant: TimeoutError")
