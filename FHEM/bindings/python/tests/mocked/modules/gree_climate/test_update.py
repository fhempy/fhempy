import asyncio
import logging
from unittest.mock import AsyncMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def setup_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("gree_climate")

    from greeclimate.cipher import CipherV1
    from greeclimate.device import Device
    from greeclimate.deviceinfo import DeviceInfo

    from fhempy.lib.gree_climate.gree_climate import gree_climate

    gree = Device(DeviceInfo("192.0.2.10", 7000, "aabbccddeeff", "testac"))
    gree.device_cipher = CipherV1(b"0123456789abcdef")
    gree.send = AsyncMock()

    testhash = {"NAME": "testac", "FHEMPYTYPE": "gree_climate"}
    mock_fhem.readings.pop("testac", None)
    device = gree_climate(logging.getLogger(__name__))
    mocker.patch.object(device, "scan_devices", AsyncMock(return_value=gree))
    await device.Define(testhash, ["testac", "fhempy", "gree_climate", "testac"], {})
    await asyncio.sleep(0.5)
    return device, testhash, gree


def state_packet(**props):
    return {"pack": {"t": "dat", "cols": list(props), "dat": list(props.values())}}


@pytest.mark.asyncio
async def test_state_update(mocker):
    device, testhash, gree = await setup_device(mocker)

    # update_state only sends the request, the answer arrives as a packet
    assert gree.send.await_count >= 1
    gree.packet_received(
        state_packet(Pow=1, Mod=1, SetTem=22, TemRec=0, TemUn=0, WdSpd=0, SwingLfRig=0, SwUpDn=0),
        ("192.0.2.10", 7000),
    )
    await asyncio.sleep(0.5)

    readings = mock_fhem.readings["testac"]
    assert readings["state"] == "on"
    assert readings["mode"] == "Cool"
    assert readings["desiredTemp"] == 22
    assert readings["fan_speed"] == "Auto"


@pytest.mark.asyncio
async def test_set_mode(mocker):
    device, testhash, gree = await setup_device(mocker)

    await device.Set(testhash, ["testac", "mode", "Heat"], {})
    await asyncio.sleep(0.5)

    sent = gree.send.await_args.args[0]
    assert "Mod" in sent["pack"]["opt"] if "pack" in sent else True
    assert gree.power is True
    assert gree.mode == 4
