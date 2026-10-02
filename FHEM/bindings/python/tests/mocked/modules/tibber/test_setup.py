import asyncio
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_setup(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    # readings are global, drop the ones other tests wrote for testdevice
    mock_fhem.readings.pop("testdevice", None)
    testhash = {
        "NAME": "testdevice",
        "FHEMPYTYPE": "tibber",
    }
    await check_and_install_dependencies("tibber")

    from tibber.const import DEMO_TOKEN

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
    # wait for home, price and realtime data from the tibber demo api,
    # failed updates are retried after 60s
    for _ in range(90):
        readings = mock_fhem.readings.get("testdevice", {})
        if "home_id" in readings and "current_price_total" in readings and (
            not readings.get("has_real_time_consumption")
            or "rt_currentL3" in readings
        ):
            break
        await asyncio.sleep(1)

    assert mock_fhem.readings["testdevice"]["tibber_name"] == "Arya Stark"
    # the demo account has two homes, the api returns them in varying order
    assert mock_fhem.readings["testdevice"]["address"] in [
        "Winterfell Castle 1",
        "123 Main St",
    ]
    # current_price_level is not provided in demo data
    # assert len(mock_fhem.readings["testdevice"]["current_price_level"]) > 0
    assert mock_fhem.readings["testdevice"]["current_price_total"] >= 0
    if mock_fhem.readings["testdevice"]["has_real_time_consumption"]:
        assert mock_fhem.readings["testdevice"]["rt_currentL3"] >= 0

    await fhempy_device.Undefine(testhash)
