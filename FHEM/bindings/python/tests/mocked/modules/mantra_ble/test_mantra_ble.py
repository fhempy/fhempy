import asyncio
import logging
from unittest.mock import AsyncMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.mantra_ble.mantra_ble import mantra_ble


async def define_device(mocker, keep_readings=False):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testmantra", "FHEMPYTYPE": "mantra_ble"}
    if not keep_readings:
        mock_fhem.readings.pop("testmantra", None)
    device = mantra_ble(logging.getLogger(__name__))
    mocker.patch.object(device, "_run_os_cmd", AsyncMock())
    await device.Define(testhash, ["testmantra", "fhempy", "mantra_ble", "1F42"], {})
    return device, testhash


@pytest.mark.asyncio
async def test_brightness_and_ct_survive_redefine(mocker):
    device, testhash = await define_device(mocker)
    assert mock_fhem.readings["testmantra"]["brightness"] == 100
    assert mock_fhem.readings["testmantra"]["ct"] == 4000

    mocker.patch("asyncio.sleep", AsyncMock())
    await device.Set(testhash, ["testmantra", "brightness", "40"], {})
    await device.Set(testhash, ["testmantra", "ct", "3000"], {})
    await asyncio.sleep(0)

    await define_device(mocker, keep_readings=True)
    assert mock_fhem.readings["testmantra"]["brightness"] == 40
    assert mock_fhem.readings["testmantra"]["ct"] == 3000


@pytest.mark.asyncio
async def test_transmissions_do_not_overlap(mocker):
    device, _ = await define_device(mocker)
    active = 0
    max_active = 0

    async def run_os_cmd(cmd):
        nonlocal active, max_active
        if cmd.endswith("0x000a 01"):
            active += 1
            max_active = max(max_active, active)
        elif cmd.endswith("0x000a 00"):
            active -= 1
        await asyncio.sleep(0)

    device._run_os_cmd = run_os_cmd
    await asyncio.gather(
        device._transmit_light_ct(50, 4000),
        device._transmit_light_ct(60, 5000),
        device._transmit_light_ct(70, 6000),
    )
    assert max_active == 1


async def define_mode(mocker, mode):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testmantra", "FHEMPYTYPE": "mantra_ble"}
    mock_fhem.readings.pop("testmantra", None)
    device = mantra_ble(logging.getLogger(__name__))
    mocker.patch.object(device, "_run_os_cmd", AsyncMock())
    args = ["testmantra", "fhempy", "mantra_ble", "1F42"] + ([mode] if mode else [])
    assert await device.Define(testhash, args, {}) is None
    mocker.patch("asyncio.sleep", AsyncMock())
    return device, testhash


def test_validate_define():
    args = ["testmantra", "fhempy", "mantra_ble", "1F42"]
    assert mantra_ble.validate_define(args, {}) is None
    assert mantra_ble.validate_define(args + ["only-fan"], {}) is None
    assert mantra_ble.validate_define(args + ["only-light"], {}) is None
    assert "only-fan" in mantra_ble.validate_define(args + ["fan"], {})
    assert mantra_ble.validate_define(args + ["only-fan", "x"], {})


@pytest.mark.asyncio
async def test_fan_pct_and_mode(mocker):
    device, testhash = await define_mode(mocker, None)
    readings = mock_fhem.readings["testmantra"]
    assert readings["fan_pct"] == 0
    assert readings["fan_mode"] == "off"
    for name in ("on", "brightness", "fan", "fan_speed", "fan_pct", "fan_mode"):
        assert name in device._conf_set

    await device.set_fan_pct(testhash, {"pct": 50})
    assert readings["fan_speed"] == 16
    assert readings["fan_pct"] == 50
    assert readings["fan_mode"] == "medium"
    assert readings["fan"] == "on"
    # the light is not touched
    assert readings["state"] == "off"

    await device.set_fan_mode(testhash, {"mode": "high"})
    assert readings["fan_speed"] == 31
    assert readings["fan_pct"] == 100

    await device.set_fan_speed(testhash, {"speed": 3})
    assert readings["fan_pct"] == 10
    assert readings["fan_mode"] == "low"

    await device.set_fan(testhash, {"state": "off"})
    assert readings["fan_pct"] == 0
    assert readings["fan_mode"] == "off"
    assert readings["fan_speed"] == 3
    # on again with the last speed
    await device.set_fan(testhash, {"state": "on"})
    assert readings["fan_pct"] == 10

    await device.set_fan_pct(testhash, {"pct": 0})
    assert readings["fan"] == "off"


@pytest.mark.asyncio
async def test_only_fan(mocker):
    device, testhash = await define_mode(mocker, "only-fan")
    readings = mock_fhem.readings["testmantra"]
    assert "brightness" not in device._conf_set
    assert "light" not in readings
    await device.set_on(testhash, {})
    assert readings["fan"] == "on"
    assert readings["state"] == "on"
    await device.set_fan_mode(testhash, {"mode": "low"})
    assert readings["fan_pct"] == 33
    await device.set_off(testhash, {})
    assert readings["state"] == "off"
    assert readings["fan_mode"] == "off"


@pytest.mark.asyncio
async def test_only_light(mocker):
    device, testhash = await define_mode(mocker, "only-light")
    readings = mock_fhem.readings["testmantra"]
    assert "fan" not in device._conf_set
    assert "fan_pct" not in readings
    await device.set_on(testhash, {})
    assert readings["light"] == "on"
    assert readings["state"] == "on"
