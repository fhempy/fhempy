import asyncio
import json
import logging
import os

import pytest
import requests_mock
from fhempy.lib.pkg_installer import check_and_install_dependencies
from tests.utils import mock_fhem


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
            "https://openapi.tuyaeu.com/v1.0/devices/345678345673456567",
            text=load_fixture("device.json"),
        )
        mock.get(
            "https://openapi.tuyaeu.com/v1.0/users/12345678901234567890/devices",
            text=load_fixture("devices.json"),
        )
        yield mock


@pytest.mark.asyncio
async def test_setup(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice", "FHEMPYTYPE": "tuya"}
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import tuya

    fhempy_device = tuya(logging.getLogger(__name__))

    def devicesScan(verbose, maxretry=1, color=None):
        return json.loads(load_fixture("local_devices.json"))

    mocker.patch("tinytuya.deviceScan", devicesScan)

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "fhempy",
            "tuya",
            "setup",
            "12345678123456",
            "2345678234567",
            "345678345673456567",
        ],
        {},
    )
    assert mock_fhem.readings["testdevice"]["state"] == "ready"

    await fhempy_device.Set(testhash, ["testdevice", "scan_devices"], {})

    await asyncio.sleep(0.2)
    assert mock_fhem.readings["testdevice"]["state"] == "done, created 2 devices"

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

    await fhempy_device.Undefine(testhash)
