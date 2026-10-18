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
    assert mock_fhem.readings["hello_test"]["desiredTemp"] == 22


@pytest.mark.asyncio
@pytest.mark.parametrize("command,arguments,parameter", [
    ("on", ["dsfsdf"], "seconds"),
    ("on", ["-1"], "seconds"),
    ("on", ["1.5"], "seconds"),
    ("mode", ["turbo"], "mode"),
    ("desiredTemp", [], "temperature"),
    ("desiredTemp", ["nope"], "temperature"),
    ("desiredTemp", ["9"], "temperature"),
    ("desiredTemp", ["31"], "temperature"),
    ("desiredTemp", ["20.5"], "temperature"),
    ("desiredTemp", ["nan"], "temperature"),
    ("holidayMode", ["sadadasd", "asdasdasdasd", "yxcyxcyx"], "endday"),
    ("holidayMode", ["sadadasd", "18:30", "19"], "endday"),
    ("holidayMode", ["1.1.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["01.1.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["1.01.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["01.01.30", "18:30", "19"], "endday"),
    ("holidayMode", ["01.01.2030 ", "18:30", "19"], "endday"),
    ("holidayMode", ["٠١.٠١.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["31.04.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["29.02.2030", "18:30", "19"], "endday"),
    ("holidayMode", ["29.02.1900", "18:30", "19"], "endday"),
    ("holidayMode", ["24.12.2030", "asdasdasdasd", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "1:2", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "01:2", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "1:02", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "01:02:00", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "01:02\n", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "٠١:٠٢", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "24:00", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "23:60", "19"], "endtime"),
    ("holidayMode", ["24.12.2030", "18:30", "yxcyxcyx"], "temperature"),
    ("holidayMode", ["24.12.2030", "18:30", "9"], "temperature"),
    ("holidayMode", ["24.12.2030", "18:30", "31"], "temperature"),
])
async def test_invalid_input_preserves_all_readings(device, command, arguments, parameter):
    # Existing values expose partial updates as well as newly created readings.
    await device.Set(device.hash, ["hello_test", "holidayMode"], {})
    before = copy.deepcopy(mock_fhem.readings)
    config = copy.deepcopy(device._conf_set)
    result = await device.Set(device.hash, ["hello_test", command, *arguments], {})
    assert isinstance(result, str) and parameter in result
    assert mock_fhem.readings == before
    assert device._conf_set == config


@pytest.mark.asyncio
@pytest.mark.parametrize("command,arguments,reading,expected", [
    ("on", [], "state", "on"),
    ("on", ["0"], "state", "on"),
    ("on", ["1"], "state", "on 1"),
    ("mode", [], "mode", "eco"),
    ("desiredTemp", ["10"], "desiredTemp", 10),
    ("desiredTemp", ["30"], "desiredTemp", 30),
    ("holidayMode", ["29.02.2000", "00:00", "10"], "temperature", 10),
    ("holidayMode", ["29.02.2032", "23:59", "30"], "endday", "29.02.2032"),
    ("holidayMode", ["01.01.2030", "01:02", "21"], "endtime", "01:02"),
])
async def test_valid_boundaries(device, command, arguments, reading, expected):
    assert await device.Set(device.hash, ["hello_test", command, *arguments], {}) is None
    assert mock_fhem.readings["hello_test"][reading] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["nope", "0", "-1", "1.5"])
async def test_invalid_interval_keeps_previous_value(device, value):
    await device.Attr(device.hash, ["set", "hello_test", "interval", "250"], {})
    result = await device.Attr(device.hash, ["set", "hello_test", "interval", value], {})
    assert result.startswith("Invalid value for interval:")
    assert device._attr_interval == 250
    assert await device.Attr(device.hash, ["del", "hello_test", "interval"], {}) is None
    assert device._attr_interval == 100


@pytest.mark.asyncio
async def test_invalid_saved_interval_uses_default(device, caplog):
    mock_fhem.attributes["hello_test"] = {"interval": "bad"}
    await device.Define(device.hash, ["hello_test", "fhempy", "helloworld"], {})
    assert device._attr_interval == 100
    assert "Invalid value for interval" in caplog.text
    assert "Using default 100" in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


@pytest.mark.asyncio
async def test_named_mode_and_unexpected_parameters(device):
    assert await device.Set(device.hash, ["hello_test", "mode"], {"mode": "comfort"}) is None
    before = copy.deepcopy(mock_fhem.readings)
    for command, args, keywords in [
        ("mode", [], {"mode": "bad"}),
        ("mode", [], {"typo": "eco"}),
        ("mode", ["eco"], {"mode": "comfort"}),
        ("on", [], {"seconds": "5"}),
        ("off", [], {"extra": "1"}),
    ]:
        assert await device.Set(device.hash, ["hello_test", command, *args], keywords)
        assert mock_fhem.readings == before
    for command in ("info", "help"):
        assert "Unknown named argument" in await device.Get(
            device.hash, ["hello_test", command], {"extra": "1"}
        )
