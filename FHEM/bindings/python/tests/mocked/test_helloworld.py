import copy
import logging

import pytest
import pytest_asyncio
from fhempy.lib.helloworld.helloworld import USAGE, helloworld

from ..utils import mock_fhem


@pytest_asyncio.fixture
async def device(mocker):
    mock_fhem.mock_module(mocker)
    mocker.patch.object(mock_fhem, "readings", {})
    mocker.patch.object(mock_fhem, "attributes", {})
    module = helloworld(logging.getLogger("hello_test"))
    hash = {"NAME": "hello_test", "FHEMPYTYPE": "helloworld"}
    assert await module.Define(hash, ["hello_test", "fhempy", "helloworld"], {}) is None
    yield module
    await module.Undefine(hash)


@pytest.mark.parametrize("args,argsh,expected", [
    (["hello_test", "fhempy", "helloworld"], {}, None),
    (["hello_test", "fhempy", "helloworld", "extra"], {}, USAGE),
    (["hello_test", "fhempy", "helloworld"], {"extra": "value"}, USAGE),
    (["hello_test", "fhempy"], {}, USAGE),
])
def test_define_validation(args, argsh, expected):
    assert helloworld.validate_define(args, argsh) == expected


@pytest.mark.asyncio
async def test_invalid_direct_define_preserves_running_device(device):
    await device.Set(device.hash, ["hello_test", "on", "15"], {})
    readings = copy.deepcopy(mock_fhem.readings)
    config = device._conf_set
    original_hash = device.hash
    original_args = device._defargs.copy()

    result = await device.Define(
        device.hash.copy(), [*original_args, "extra"], {}
    )

    assert result == USAGE
    assert device.hash is original_hash
    assert device._defargs == original_args
    assert device._conf_set is config
    assert mock_fhem.readings == readings


@pytest.mark.asyncio
async def test_get_examples_use_current_state_and_configuration(device):
    assert await device.Get(device.hash, ["hello_test", "?"], {}) == (
        "Unknown argument ?, choose one of info:noArg help:noArg"
    )
    await device.Set(device.hash, ["hello_test", "on", "15"], {})
    await device.Attr(device.hash, ["set", "hello_test", "interval", "250"], {})
    assert await device.Get(device.hash, ["hello_test", "info"], {}) == (
        "Device: hello_test\nState: on 15\nInterval: 250 seconds"
    )
    # The synchronous help handler must also work through the shared dispatcher.
    device._conf_set["extra_example"] = {}
    help_text = await device.Get(device.hash, ["hello_test", "help"], {})
    assert USAGE in help_text
    assert "extra_example" in help_text
    assert "Get commands: info, help" in help_text
    assert "Attributes: interval" in help_text


@pytest.mark.asyncio
@pytest.mark.parametrize("arguments,expected", [
    (["24.12.2030", "18:30", "19"], ("24.12.2030", "18:30", 19)),
    (["24.12.2030", "18:30"], ("24.12.2030", "18:30", 21)),
    (["24.12.2030"], ("24.12.2030", "23:59", 21)),
    ([], ("31.12.2030", "23:59", 21)),
])
async def test_holiday_parameters_and_defaults(device, arguments, expected):
    result = await device.Set(
        device.hash, ["hello_test", "holidayMode", *arguments], {}
    )
    assert result is None
    readings = mock_fhem.readings["hello_test"]
    assert (readings["endday"], readings["endtime"], readings["temperature"]) == expected
    assert readings["state"] == "on"


@pytest.mark.asyncio
async def test_holiday_defaults_are_not_previous_arguments(device):
    config = copy.deepcopy(device._conf_set)
    await device.Set(
        device.hash, ["hello_test", "holidayMode", "24.12.2030", "18:30", "19"], {}
    )
    await device.Set(device.hash, ["hello_test", "holidayMode"], {})
    readings = mock_fhem.readings["hello_test"]
    assert readings["endday"] == "31.12.2030"
    assert readings["endtime"] == "23:59"
    assert readings["temperature"] == 21
    assert device._conf_set == config


@pytest.mark.asyncio
async def test_holiday_usage_does_not_change_readings(device):
    readings = copy.deepcopy(mock_fhem.readings)
    for arguments in (["?"], ["24.12.2030", "18:30", "19", "extra"]):
        result = await device.Set(
            device.hash, ["hello_test", "holidayMode", *arguments], {}
        )
        assert result == "Usage: set hello_test holidayMode endday endtime temperature"
    assert mock_fhem.readings == readings


@pytest.mark.asyncio
async def test_desired_temperature_does_not_overwrite_mode(device):
    await device.Set(device.hash, ["hello_test", "mode", "comfort"], {})
    await device.Set(device.hash, ["hello_test", "desiredTemp", "22"], {})
    assert mock_fhem.readings["hello_test"]["mode"] == "comfort"
    assert mock_fhem.readings["hello_test"]["desiredTemp"] == "22"
