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


@pytest.mark.asyncio
async def test_scan_opens_device_dialog(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.javascript.clear()
    mock_fhem.command_define.clear()
    mock_fhem.command_attr.clear()
    testhash = {"NAME": "tuya_setup", "FHEMPYTYPE": "tuya"}
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import tuya

    fhempy_device = tuya(logging.getLogger(__name__))
    mocker.patch(
        "tinytuya.deviceScan",
        lambda *args, **kwargs: json.loads(load_fixture("local_devices.json")),
    )
    await fhempy_device.Define(
        testhash,
        ["tuya_setup", "fhempy", "tuya", "setup", "key", "secret", "123"],
        {},
    )

    class FakeCloud:
        def getdevices(self, verbose=False):
            return json.loads(load_fixture("devices.json"))

    fhempy_device.tuya_cloud = FakeCloud()
    await fhempy_device._scan_devices()

    # the dialog opens on the detail page of the setup device
    assert len(mock_fhem.javascript) == 1
    detail, js = mock_fhem.javascript[0]
    assert detail == "tuya_setup"
    assert "fhempy/tuya.js" in js
    assert "fhempyTuyaDevices(" in js
    # local keys stay in FHEM
    assert "0923092309231234" not in js
    params = json.loads("[" + js.split("fhempyTuyaDevices(", 1)[1][:-3] + "]")
    assert params[0] == "tuya_setup"
    assert params[2] is None
    found = {dev["id"]: dev for dev in params[1]}
    lamp = found["239823982398239823"]
    assert lamp["online"] is True
    assert lamp["ip"] == "192.168.86.50"
    assert lamp["name"] == "Eingangslampe"
    assert lamp["icon"].startswith("https://images.tuyaeu.com/smart/icon/")
    assert found["23424524513414245"]["online"] is False

    # the dialog creates the device with its id
    assert (
        await fhempy_device.set_create_device(testhash, {"name": "239823982398239823"})
        is None
    )
    assert mock_fhem.command_define[-1].startswith(
        "tuya_local_239823982398239823 fhempy tuya j0zozzoarutv0nu1 "
        "239823982398239823 192.168.86.50 3.3"
    )
    assert "tuya_local_239823982398239823 localkey 0923092309231234" in (
        mock_fhem.command_attr
    )
    assert "not found" in await fhempy_device.set_create_device(
        testhash, {"name": "unknown"}
    )

    # the detail page offers search and the found devices again
    html = fhempy_device._setup_html()
    assert "fhempyTuyaScan" in html
    assert f"Show found devices ({len(params[1])})" in html
    assert "0923092309231234" not in html

    await fhempy_device.Undefine(testhash)


@pytest.mark.asyncio
async def test_scan_error_is_shown_in_dialog(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.javascript.clear()
    testhash = {"NAME": "tuya_setup", "FHEMPYTYPE": "tuya"}
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import tuya

    fhempy_device = tuya(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["tuya_setup", "fhempy", "tuya", "setup", "key", "secret", "123"],
        {},
    )

    class FakeCloud:
        def getdevices(self, verbose=False):
            return {"Error": "Cloud token failed", "Payload": "sign invalid"}

    fhempy_device.tuya_cloud = FakeCloud()
    await fhempy_device._scan_devices()
    assert len(mock_fhem.javascript) == 1
    assert "Cloud token failed sign invalid" in mock_fhem.javascript[0][1]
    assert "Show found devices" not in fhempy_device._setup_html()

    await fhempy_device.Undefine(testhash)
