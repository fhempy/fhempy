import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def define_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("nefit")
    from fhempy.lib.nefit.nefit import nefit

    testhash = {"NAME": "testnefit", "FHEMPYTYPE": "nefit"}
    mock_fhem.readings.pop("testnefit", None)
    device = nefit(logging.getLogger(__name__))
    await device.Define(testhash, ["testnefit", "fhempy", "nefit", "123456789"], {})
    return device, testhash


@pytest.mark.asyncio
async def test_set_without_credentials(mocker):
    # sets crashed with AttributeError ('nefit' object has no attribute
    # '_nefit_client') before access_key and password were set
    device, testhash = await define_device(mocker)

    for cmd in (["desiredTemp", "21"], ["mode", "manual"], ["todayAsSunday", "on"]):
        ret = await device.Set(testhash, ["testnefit"] + cmd, {})
        assert ret == "Please set attributes access_key and password first"


@pytest.mark.asyncio
async def test_set_while_disconnected(mocker):
    device, testhash = await define_device(mocker)
    client = MagicMock()
    device._nefit_client = client
    mocker.patch("asyncio.sleep", AsyncMock())
    mocker.patch.object(device, "nefit_connect", AsyncMock())

    await device.session_end_callback()
    ret = await device.Set(testhash, ["testnefit", "desiredTemp", "21"], {})

    assert "Not connected to Nefit Easy yet" in ret
    client.set_temperature.assert_not_called()

    device._connected = True
    await device.Set(testhash, ["testnefit", "desiredTemp", "21"], {})
    client.set_temperature.assert_called_once_with(21.0)
