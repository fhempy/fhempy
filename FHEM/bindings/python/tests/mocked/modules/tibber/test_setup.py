import asyncio
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

# demo token from pyTibber >= 0.38, the token shipped with pyTibber 0.29 is no longer valid
DEMO_TOKEN = "3A77EECF61BD445F47241A5A36202185C35AF3AF58609E19B53F3A8872AD7BE1-1"


@pytest.mark.asyncio
async def test_setup(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    testhash = {
        "NAME": "testdevice",
        "FHEMPYTYPE": "tibber",
    }
    await check_and_install_dependencies("tibber")

    from fhempy.lib.tibber.tibber import tibber

    fhempy_device = tibber(logging.getLogger(__name__))

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "fhempy",
            "tibber",
            DEMO_TOKEN,
        ],
        {},
    )
    # wait for realtime data 10s
    await asyncio.sleep(10)

    assert mock_fhem.readings["testdevice"]["tibber_name"] == "Arya Stark"
    assert mock_fhem.readings["testdevice"]["address"] == "Winterfell Castle 1"
    # current_price_level is not provided in demo data
    # assert len(mock_fhem.readings["testdevice"]["current_price_level"]) > 0
    assert mock_fhem.readings["testdevice"]["current_price_total"] >= 0
    assert mock_fhem.readings["testdevice"]["rt_currentL3"] >= 0

    await fhempy_device.Undefine(testhash)
