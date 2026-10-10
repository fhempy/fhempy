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

    await fhempy_device.Undefine(testhash)


@pytest.mark.asyncio
async def test_cloud_error_is_reported(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import TuyaCloudError, tuya

    fhempy_device = tuya(logging.getLogger(__name__))
    assert fhempy_device._cloud_result({"result": {"a": 1}}, "getdps") == {"a": 1}
    with pytest.raises(TuyaCloudError, match="permission deny \\(code 1106\\)"):
        fhempy_device._cloud_result(
            {"success": False, "code": 1106, "msg": "permission deny"}, "getdps"
        )
    with pytest.raises(TuyaCloudError, match="Cloud token failed"):
        fhempy_device._cloud_result(
            {"Error": "Cloud token failed", "Err": "907"}, "getdps"
        )
