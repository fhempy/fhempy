import asyncio
import logging
import pytest
import os
import json
from fhempy.lib.tuya.tuya import tuya
from ... import mock_fhem

import requests_mock


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fdp:
        return fdp.read()


@pytest.fixture(autouse=True)
def mock_tuya_requests():
    # TODO test exceptions

    with requests_mock.Mocker() as mock:
        mock.get(
            "https://openapi.tuyaeu.com/v1.0/token?grant_type=1",
            text=load_fixture("token.json"),
        )
        mock.get(
            "https://openapi.tuyaeu.com/v1.0/devices/bfdfc0ff3aaecf4559v2jd",
            text=load_fixture("device.json"),
        )
        mock.get(
            "https://openapi.tuyaeu.com/v1.0/users/12345678901234567890/devices",
            text=load_fixture("devices.json"),
        )
        yield mock


@pytest.mark.asyncio
async def test_setup(mocker):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice"}
    fhempy_device = tuya(logging.getLogger(__name__))

    def devicesScan(verbose, maxretry=1, color=None):
        return json.loads(load_fixture("local_devices.json"))

    mocker.patch("tinytuya.deviceScan", devicesScan)

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "PythonModule",
            "tuya",
            "setup",
            "kfce3ayxa8hgdbr4wnq7",
            "26c156d9eecd4f48a1a6f8948c830c96",
            "bfdfc0ff3aaecf4559v2jd",
        ],
        {},
    )
    assert mock_fhem.readings["testdevice"]["state"] == "ready"

    await fhempy_device.Set(testhash, ["testdevice", "scan_devices"], {})

    while True:
        if mock_fhem.readings["testdevice"]["state"] == "found 3 devices":
            break
        else:
            await asyncio.sleep(0.1)
    # await asyncio.gather(*asyncio.all_tasks())

    assert (
        mock_fhem.readings["testdevice"]["239823982398239823_localkey"]
        == "0923092309231234"
    )
    assert (
        mock_fhem.readings["testdevice"]["23424524513414245_localkey"]
        == "0923092309231234"
    )
    assert (
        mock_fhem.readings["testdevice"]["2423425345234234234_localkey"]
        == "0923092309231234"
    )
