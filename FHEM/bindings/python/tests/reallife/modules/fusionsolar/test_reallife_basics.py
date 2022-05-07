import asyncio
import logging
import os

import pytest
from fhempy.lib.pkg_installer import check_and_install_dependencies
from tests.utils import mock_fhem


@pytest.mark.asyncio
async def test_everything(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice", "FHEMPYTYPE": "fusionsolar"}
    await check_and_install_dependencies("fusionsolar")
    from fhempy.lib.fusionsolar.fusionsolar import fusionsolar

    fhempy_device = fusionsolar(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "fhempy",
            "fusionsolar",
            os.environ["FUSIONSOLAR_SESSIONID"],
            os.environ["FUSIONSOLAR_REGION"],
        ],
        {os.environ["FUSIONSOLAR_STATIONID1"]: os.environ["FUSIONSOLAR_STATIONID2"]},
    )

    # send command
    # await fhempy_device.Set(
    #    testhash,
    #    ["testdevice", "lock"],
    #    {},
    # )
    await asyncio.sleep(10)

    assert mock_fhem.readings["testdevice"]["state"] == "connected"

    await asyncio.sleep(30)
