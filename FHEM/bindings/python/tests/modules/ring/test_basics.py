import asyncio
import logging
import pytest
import os
from fhempy.lib.ring.ring import ring
from ... import mock_fhem


@pytest.mark.asyncio
async def test_login(mocker):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice"}
    fhempy_device = ring(logging.getLogger(__name__))

    # await fhempy_device.Define(
    #     testhash,
    #     [
    #         "testdevice",
    #         "PythonModule",
    #         "ring",
    #         os.environ["RING_USERNAME"],
    #         os.environ["RING_DEVICE_NAME"],
    #     ],
    #     {},
    # )

    # set password

    # check for 2facode file and delete afterwards
