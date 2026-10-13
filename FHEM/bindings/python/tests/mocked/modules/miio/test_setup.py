import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_define_creates_set_commands(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("miio")
    from fhempy.lib.miio.miio import miio

    mock_fhem.readings.pop("testmiio", None)
    testhash = {"NAME": "testmiio", "FHEMPYTYPE": "miio"}
    device = miio(logging.getLogger(__name__))
    # avoid starting the endless update loops
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    ret = await device.Define(
        testhash,
        [
            "testmiio",
            "fhempy",
            "miio",
            "roborockvacuum",
            "127.0.0.1",
            "00112233445566778899aabbccddeeff",
        ],
        {},
    )

    assert ret is None
    assert "status" in device._set_list
    assert "start" in device._set_list
    assert mock_fhem.readings["testmiio"]["state"] == "active"


@pytest.mark.asyncio
async def test_define_unknown_type(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("miio")
    from fhempy.lib.miio.miio import miio

    device = miio(logging.getLogger(__name__))
    ret = await device.Define(
        {"NAME": "testmiio2", "FHEMPYTYPE": "miio"},
        ["testmiio2", "fhempy", "miio", "nodevice", "127.0.0.1", "00" * 16],
        {},
    )
    assert ret == "Device nodevice not found."


@pytest.mark.asyncio
async def test_send_command_without_params(mocker):
    # update_functions call send_command with params=None
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("miio")
    from fhempy.lib.miio.miio import miio

    device = miio(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "testmiio3", "FHEMPYTYPE": "miio"},
        ["testmiio3", "fhempy", "miio", "roborockvacuum", "127.0.0.1", "00" * 16],
        {},
    )
    info = mocker.patch.object(device._device, "info", return_value="ok")
    await device.send_command("info", None, raise_exc=True)
    info.assert_called_once_with()


@pytest.mark.asyncio
async def test_unreachable_device_logged_once(mocker, caplog):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("miio")
    from fhempy.lib.miio import miio as miio_module
    from fhempy.lib.miio.miio import miio

    device = miio(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "testmiio4", "FHEMPYTYPE": "miio"},
        ["testmiio4", "fhempy", "miio", "roborockvacuum", "127.0.0.1", "00" * 16],
        {},
    )
    calls = 0

    async def send_command(fct_name, params, raise_exc=False):
        nonlocal calls
        calls += 1
        if calls <= 3:
            raise Exception("Unable to discover the device")

    mocker.patch.object(device, "send_command", send_command)

    async def sleep(sec):
        # stop after the first successful update
        if sec == 600:
            raise StopAsyncIteration

    mocker.patch.object(miio_module.asyncio, "sleep", sleep)
    caplog.set_level(logging.DEBUG)
    with pytest.raises(StopAsyncIteration):
        await device.fct_update_loop("info", 600)

    warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert len(warnings) == 1
    assert "not reachable" in warnings[0].getMessage()
    assert any("reachable again" in r.getMessage() for r in caplog.records)
    assert mock_fhem.readings["testmiio4"]["presence"] == "online"


@pytest.mark.asyncio
async def test_library_receive_errors_are_filtered(mocker, caplog):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("miio")
    import fhempy.lib.miio.miio  # noqa: F401 (installs the filter)

    caplog.set_level(logging.DEBUG)
    lib_logger = logging.getLogger("miio.miioprotocol")
    lib_logger.error("Got error when receiving: %s", "timed out")
    lib_logger.error("failed to send msg: %s", "x")
    messages = [r.getMessage() for r in caplog.records]
    assert "Got error when receiving: timed out" not in messages
    assert "failed to send msg: x" in messages
