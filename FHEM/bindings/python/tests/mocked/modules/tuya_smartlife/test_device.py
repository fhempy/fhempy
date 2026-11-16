import logging
from types import SimpleNamespace

import pytest

from fhempy.lib.tuya_smartlife import tuya_smartlife_device as tsd


def make_device(mocker, category):
    fhemdev = mocker.Mock()
    fhemdev.hash = {"NAME": "testtuya"}
    dev = tsd.tuya_smartlife_device(logging.getLogger(__name__), fhemdev)
    # CustomerDevice from tuya_sharing is an object, not a dict
    dev.device = SimpleNamespace(category=category)
    dev._t_info = dev.device
    dev._t_deviceid = "abc"
    dev.default_code = None
    dev.tuyaiot = mocker.Mock()
    dev.tuyaiot.send_commands = mocker.AsyncMock()
    return dev


@pytest.mark.asyncio
async def test_set_colour_data_v1_light(mocker):
    dev = make_device(mocker, "dj")
    params = {"new_val": "ff0000", "function_param": {"code": "colour_data"}}

    await dev.set_colour_data(dev.hash, params)

    dev.tuyaiot.send_commands.assert_awaited_once_with(
        "abc", [{"code": "colour_data", "value": {"h": 0, "s": 255, "v": 255}}]
    )


@pytest.mark.asyncio
async def test_set_colour_data_v1_other_category(mocker):
    dev = make_device(mocker, "kg")
    params = {"new_val": "ff0000", "function_param": {"code": "colour_data"}}

    await dev.set_colour_data(dev.hash, params)

    dev.tuyaiot.send_commands.assert_awaited_once_with(
        "abc", [{"code": "colour_data", "value": {"h": 0, "s": 1000, "v": 1000}}]
    )


def test_pir_code_maps_to_state(mocker):
    dev = make_device(mocker, "pir")
    assert dev._convert_code2fhem("pir") == "state"
    dev = make_device(mocker, "dj")
    assert dev._convert_code2fhem("pir") == "pir"
