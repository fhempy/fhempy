import asyncio
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
async def test_mapping_ctrl(mocker):
    # prepare
    mock_fhem.mock_module(mocker)

    testval = None
    testindex = None

    def set_status(instance, value, switch):
        nonlocal testval, testindex
        testval = value
        testindex = switch

    def set_value(instance, index, value):
        nonlocal testval, testindex
        testval = value
        testindex = index

    def status(instance):
        return {
            "dps": {
                "1": False,
                "9": 0,
                "17": 2,
                "18": 0,
                "19": 0,
                "20": 2371,
                "21": 1,
                "22": 691,
                "23": 30757,
                "24": 18008,
                "25": 2320,
                "26": 0,
                "38": "off",
                "41": "",
                "42": "",
                "46": False,
            }
        }

    mocker.patch("tinytuya.Device.set_status", set_status)
    mocker.patch("tinytuya.Device.set_value", set_value)
    mocker.patch("tinytuya.Device.status", status)

    testhash = {"NAME": "testdevice"}
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import tuya

    fhempy_device = tuya(logging.getLogger(__name__))

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "PythonModule",
            "tuya",
            "j0zozzoarutv0nu1",
            "34567adf13165",
            "192.168.86.35",
            "345678345678",
            "3.3",
            "12345678123456",
            "2345678234567",
        ],
        {},
    )
    assert mock_fhem.readings["testdevice"]["state"] == "offline"

    new_set = await fhempy_device.Set(testhash, ["testdevice", "?"], {})
    assert new_set == (
        "Unknown argument ?, choose one of on:noArg off:noArg "
        "countdown_1:slider,0,1,86400 relay_status:off,on,memory "
        "cycle_time random_time switch_overcharge:on,off"
    )

    # wait for readings
    await asyncio.sleep(0.1)

    assert mock_fhem.readings["testdevice"]["cur_voltage"] == 237.1

    await fhempy_device.Set(testhash, ["testdevice", "on"], {})
    # sleep to make sure that task started
    await asyncio.sleep(0.01)
    assert testval is True
    assert testindex == 1

    await fhempy_device.Set(testhash, ["testdevice", "off"], {})
    # sleep to make sure that task started
    await asyncio.sleep(0.01)
    assert testval is False
    assert testindex == 1

    await fhempy_device.Set(testhash, ["testdevice", "countdown_1", "1000"], {})
    # sleep to make sure that task started
    await asyncio.sleep(0.01)
    assert testval == 1000
    assert testindex == 9

    await fhempy_device.Set(testhash, ["testdevice", "relay_status", "memory"], {})
    # sleep to make sure that task started
    await asyncio.sleep(0.01)
    assert testval == "memory"
    assert testindex == 38

    await fhempy_device.Undefine(testhash)
