import asyncio
import logging
import socket

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
    mocker.patch.object(dlna_module.dlna_dmr, "notify_server", None)

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


async def prepare_found_device(mocker, port):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("dlna_dmr")
    from fhempy.lib.dlna_dmr import dlna_dmr as dlna_module

    mocker.patch.object(
        dlna_module, "async_get_local_ip", return_value=(2, "127.0.0.1")
    )
    mocker.patch.object(dlna_module, "DEFAULT_LISTEN_PORT", port)
    mocker.patch.object(dlna_module, "DmrDevice")
    mocker.patch.object(dlna_module.dlna_dmr, "event_handler", None)
    mocker.patch.object(dlna_module.dlna_dmr, "notify_server", None)
    return dlna_module


def new_device(mocker, dlna_module, name="dlna_test"):
    device = dlna_module.dlna_dmr(logging.getLogger(name))
    device.hash = {"NAME": name}
    mocker.patch.object(device, "updateDeviceReadings")
    mocker.patch.object(device, "update")
    return device


async def stop_shared_server(dlna_module):
    server = dlna_module.dlna_dmr.notify_server
    if server is not None:
        await server.async_stop_server()
        await server.event_handler._requester._session.close()


@pytest.mark.asyncio
async def test_found_device_twice_at_once_keeps_session_open(mocker):
    # SSDP reported the renderer twice at the same time: the second call
    # replaced self.server, failed to bind and closed the session the shared
    # event handler used -> "Session is closed" on every update
    dlna_module = await prepare_found_device(mocker, 0)
    device = new_device(mocker, dlna_module)
    other = new_device(mocker, dlna_module, "dlna_other")
    try:
        await asyncio.gather(
            device.found_device(mocker.MagicMock()),
            device.found_device(mocker.MagicMock()),
            other.found_device(mocker.MagicMock()),
        )
        server = dlna_module.dlna_dmr.notify_server
        assert device.server is server and other.server is server
        assert not server.event_handler._requester._session.closed
        assert dlna_module.DmrDevice.call_count == 2
    finally:
        await stop_shared_server(dlna_module)


@pytest.mark.asyncio
async def test_port_in_use_falls_back_to_free_port(mocker, caplog):
    blocker = socket.socket()
    blocker.bind(("127.0.0.1", 0))
    blocker.listen()
    port = blocker.getsockname()[1]
    dlna_module = await prepare_found_device(mocker, port)
    device = new_device(mocker, dlna_module)
    try:
        with caplog.at_level(logging.INFO):
            await device.found_device(mocker.MagicMock())
        assert device.device is not None
        assert device.server.listen_port not in (0, port)
        assert not [r for r in caplog.records if r.levelno >= logging.ERROR]
    finally:
        blocker.close()
        await stop_shared_server(dlna_module)


@pytest.mark.asyncio
async def test_server_start_error_is_one_line(mocker, caplog):
    dlna_module = await prepare_found_device(mocker, 0)
    mocker.patch.object(
        dlna_module.AiohttpNotifyServer,
        "async_start_server",
        side_effect=OSError(99, "cannot assign requested address"),
    )
    device = new_device(mocker, dlna_module)
    await device.found_device(mocker.MagicMock())

    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(errors) == 1
    assert "Could not start UPnP event server" in errors[0].getMessage()
    assert errors[0].exc_info is None
    assert device.device is None
    assert dlna_module.dlna_dmr.event_handler is None


@pytest.mark.asyncio
async def test_update_error_without_traceback(mocker, caplog):
    device, _ = await define_offline_device(mocker)
    from fhempy.lib.dlna_dmr import dlna_dmr as dlna_module

    device.device = mocker.MagicMock()
    device.device.async_update = mocker.AsyncMock(
        side_effect=RuntimeError("Session is closed")
    )
    mocker.patch.object(
        dlna_module.asyncio, "sleep", side_effect=asyncio.CancelledError
    )
    with pytest.raises(asyncio.CancelledError):
        await device.update()

    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(errors) == 1
    assert errors[0].exc_info is None
