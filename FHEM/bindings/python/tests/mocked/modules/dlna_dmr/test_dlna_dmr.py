import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_found_device_starts_notify_server(mocker):
    # async-upnp-client changed the AiohttpNotifyServer arguments, the module
    # failed with TypeError on every discovered renderer
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("dlna_dmr")
    from fhempy.lib.dlna_dmr import dlna_dmr as dlna_module

    mocker.patch.object(
        dlna_module, "async_get_local_ip", return_value=(2, "127.0.0.1")
    )
    # port 0: let the OS pick a free port
    mocker.patch.object(dlna_module, "DEFAULT_LISTEN_PORT", 0)
    dmr_device = mocker.patch.object(dlna_module, "DmrDevice")
    mocker.patch.object(dlna_module.dlna_dmr, "event_handler", None)

    device = dlna_module.dlna_dmr(logging.getLogger(__name__))
    device.hash = {"NAME": "dlna_test"}
    mocker.patch.object(device, "updateDeviceReadings")
    mocker.patch.object(device, "update")
    try:
        await device.found_device(mocker.MagicMock())

        assert dlna_module.dlna_dmr.event_handler is not None
        assert device.server.callback_url.startswith("http://127.0.0.1:")
        dmr_device.assert_called_once()
        assert dmr_device.call_args.args[1] is dlna_module.dlna_dmr.event_handler
    finally:
        if device.server is not None:
            await device.server.async_stop_server()
        await device.server.event_handler._requester._session.close()


async def define_offline_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("dlna_dmr")
    from fhempy.lib.dlna_dmr import dlna_dmr as dlna_module

    ssdp = mocker.MagicMock()
    ssdp.start_search = mocker.AsyncMock()
    ssdp.stop_search = mocker.AsyncMock()
    mocker.patch.object(dlna_module.ssdp, "getInstance", return_value=ssdp)
    testhash = {"NAME": "dlna_test", "FHEMPYTYPE": "dlna_dmr"}
    device = dlna_module.dlna_dmr(logging.getLogger(__name__))
    await device.Define(testhash, ["dlna_test", "fhempy", "dlna_dmr", "uuid:1"], {})
    return device, testhash


@pytest.mark.asyncio
async def test_set_while_offline(mocker):
    # sets crashed with AttributeError ('NoneType' object has no attribute
    # 'dlna_dmrdevice') while the renderer was not found
    device, testhash = await define_offline_device(mocker)

    for cmd in (["pause"], ["volume", "20"], ["play"], ["speak", "hallo"]):
        ret = await device.Set(testhash, ["dlna_test"] + cmd, {})
        assert "Renderer is offline" in ret
    assert "pause:noArg" in await device.Set(testhash, ["dlna_test", "?"], {})


@pytest.mark.asyncio
async def test_removed_device_twice(mocker):
    device, testhash = await define_offline_device(mocker)
    dmr = mocker.MagicMock()
    dmr.cleanup = mocker.AsyncMock()
    device.device = dmr
    device.update_task = mocker.MagicMock()

    await device.removed_device(None)
    await device.removed_device(None)

    dmr.cleanup.assert_awaited_once()
    assert device.device is None
    assert mock_fhem.readings["dlna_test"]["state"] == "offline"
