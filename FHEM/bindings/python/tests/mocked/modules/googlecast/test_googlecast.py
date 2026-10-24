import asyncio
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def create_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("googlecast")
    from fhempy.lib.googlecast import googlecast as googlecast_module

    device = googlecast_module.googlecast(logging.getLogger(__name__))
    device.hash = {"NAME": "testcast", "FHEMPYTYPE": "googlecast"}
    device._set_conf = {"authcode": {"args": ["code"]}, "pause": {}}
    await device.set_set_config(device._set_conf)
    return device


@pytest.mark.asyncio
async def test_set_without_cast_returns_error(mocker):
    device = await create_device(mocker)
    hash = {"NAME": "testcast", "CASTNAME": "Wohnzimmer"}

    ret = await device.Set(hash, ["testcast", "pause"], {})
    assert "Wohnzimmer not found yet" in ret

    # set list and unknown commands still work without cast
    assert (await device.Set(hash, ["testcast", "?"], {})).startswith("Unknown")
    device.handle_authcode = mocker.AsyncMock()
    device.create_async_task = mocker.MagicMock()
    await device.Set(hash, ["testcast", "authcode", "abc"], {})
    device.handle_authcode.assert_called_once_with("abc")


@pytest.mark.asyncio
async def test_set_not_connected_returns_error(mocker):
    from pychromecast.error import NotConnected

    device = await create_device(mocker)
    device.cast = mocker.MagicMock()
    device.cast.media_controller.pause.side_effect = NotConnected("gone")
    hash = {"NAME": "testcast", "CASTNAME": "Wohnzimmer"}

    ret = await device.Set(hash, ["testcast", "pause"], {})
    assert "Wohnzimmer not connected" in ret


@pytest.mark.asyncio
async def test_failing_reading_update_does_not_block_listener(mocker):
    device = await create_device(mocker)
    status = mocker.MagicMock(status="LOST")
    device.updateConnectionReadings = mocker.AsyncMock(side_effect=Exception("x"))

    # listener runs in pychromecast thread, must survive a failing update and
    # must not keep the lock (a second event would hang the socket thread)
    await asyncio.to_thread(device.new_connection_status, status)
    status.status = "FAILED"
    await asyncio.wait_for(asyncio.to_thread(device.new_connection_status, status), 5)
    assert device.updateConnectionReadings.await_count == 2
