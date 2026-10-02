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
