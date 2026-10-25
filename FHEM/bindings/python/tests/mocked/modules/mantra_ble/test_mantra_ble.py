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
