import asyncio
import copy
import json
import logging
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from fhempy.lib import generic


@pytest_asyncio.fixture
async def device():
    module = generic.FhemModule(logging.getLogger("get_test"))
    module.hash = {"NAME": "get_test", "FHEMPYTYPE": "example"}
    return module


@pytest.mark.asyncio
async def test_get_list_dispatch_and_usage(device):
    device.get_status = AsyncMock(return_value="online")
    device.get_value = AsyncMock(return_value="42")
    await device.set_get_config({
        "status": {"help": "<b>Status</b>"},
        "value": {"args": ["name"], "options": "temperature,humidity"},
    })
    assert await device.Get(device.hash, ["get_test", "?"], {}) == (
        "Unknown argument ?, choose one of status:noArg value:temperature,humidity"
    )
    assert await device.Get(device.hash, ["get_test", "status"], {}) == "online"
    device.get_status.assert_awaited_once_with(device.hash, {})
    assert await device.Get(device.hash, ["get_test", "value", "temperature"], {}) == "42"
    device.get_value.assert_awaited_once_with(device.hash, {"name": "temperature"})
    assert await device.Get(device.hash, ["get_test", "value", "?"], {}) == "Usage: get get_test value name"
    assert (await device.Get(device.hash, ["get_test", "status", "?"], {})).strip() == "Usage: get get_test status"
    assert await device.Get(device.hash, ["get_test", "unknown"], {}) == "Command not available for this device."


@pytest.mark.asyncio
@pytest.mark.parametrize("command_type", ["set", "get"])
async def test_shared_parameters_defaults_and_custom_handler(device, command_type):
    config = {"history": {
        "args": ["count"], "argsh": ["kind"], "function": "history",
        "function_param": "daily",
        "params": {
            "count": {"format": "int"},
            "kind": {"default": "temperature"},
            "since": {"optional": True},
        },
    }}
    original = copy.deepcopy(config)
    setattr(device, "_conf_" + command_type, config)
    device.history = AsyncMock(return_value="result")
    handler = getattr(device, command_type.capitalize())
    keywords = {"kind": "humidity"}
    assert await handler(device.hash, ["get_test", "history", "3"], keywords) == "result"
    device.history.assert_awaited_with(device.hash, {
        "count": 3, "kind": "humidity", "cmd": "history", "function_param": "daily",
    })
    assert await handler(device.hash, ["get_test", "history"], {}) == "Required argument count missing."
    await handler(device.hash, ["get_test", "history", "5"], {})
    device.history.assert_awaited_with(device.hash, {
        "count": 5, "kind": "temperature", "cmd": "history", "function_param": "daily",
    })
    assert config == original
    assert keywords == {"kind": "humidity"}


@pytest.mark.asyncio
async def test_no_get_config_and_existing_get_override(device):
    assert await device.Get(device.hash, ["get_test", "?"], {}) == ""

    class LegacyModule(generic.FhemModule):
        async def Get(self, hash, args, argsh):
            return "legacy reply"

    legacy = LegacyModule(device.logger)
    await legacy.set_get_config({"status": {"help": "Status help"}})
    assert await legacy.Get(device.hash, ["get_test", "status"], {}) == "legacy reply"


@pytest.mark.asyncio
@pytest.mark.parametrize("command_type", ["set", "get"])
@pytest.mark.parametrize("kind,result", [
    ("sync", None), ("sync", "ready"), ("async", "ready"), ("future", "ready"),
])
async def test_sync_and_awaitable_command_results(device, command_type, kind, result):
    returned = result
    if kind == "future":
        returned = asyncio.get_running_loop().create_future()
        returned.set_result(result)
    mock_type = AsyncMock if kind == "async" else Mock
    device.handle_value = mock_type(return_value=returned)
    setattr(device, "_conf_" + command_type, {"value": {
        "args": ["count"], "params": {"count": {"format": "int"}},
        "function": "handle_value", "function_param": "marker",
    }})

    call = getattr(device, command_type.capitalize())
    assert await call(device.hash, ["get_test", "value", "3"], {}) == result
    expected = {"count": 3, "cmd": "value", "function_param": "marker"}
    device.handle_value.assert_called_once_with(device.hash, expected)
    if kind == "async":
        device.handle_value.assert_awaited_once_with(device.hash, expected)


@pytest.mark.asyncio
@pytest.mark.parametrize("command_type", ["set", "get"])
@pytest.mark.parametrize("mock_type", [Mock, AsyncMock])
async def test_command_handler_errors_propagate(device, command_type, mock_type):
    handler = mock_type(side_effect=ValueError("device rejected command"))
    setattr(device, command_type + "_probe", handler)
    setattr(device, "_conf_" + command_type, {"probe": {}})
    call = getattr(device, command_type.capitalize())
    with pytest.raises(ValueError, match="device rejected command"):
        await call(device.hash, ["get_test", "probe"], {})
    handler.assert_called_once_with(device.hash, {})


@pytest.mark.asyncio
async def test_all_command_help_is_serialized_without_changing_quotes(device, monkeypatch):
    help_text = "<b>Device's status</b>\nUse \"quotes\", \\ and </script>."
    device._conf_set = {"update": {"help": help_text}}
    device._conf_attr = {"interval": {"help": help_text}}
    await device.set_get_config({"status": {"help": help_text, "function": lambda: None}, "quiet": {}})
    monkeypatch.setattr(device, "_get_readme_content", lambda: "<p>README</p>")
    output = await device.FW_detailFn(device.hash, ["", "", "", ""], {})
    value = output.split("var helpConfig = ", 1)[1]
    config, _ = json.JSONDecoder().raw_decode(value)
    expected = help_text.replace("\n", "<br>")
    assert config == {"set": {"update": expected}, "get": {"status": expected}, "attr": {"interval": expected}}
    assert output.lower().count("</script>") == 1
    assert 'bindHelp("get", "idGetHelp")' in output


@pytest.mark.asyncio
async def test_readme_still_reloads_on_each_detail_request(device, monkeypatch, tmp_path):
    directory = tmp_path / "example"
    directory.mkdir()
    readme = directory / "README.md"
    monkeypatch.setattr(generic.inspect, "getfile", lambda module: str(tmp_path / "__init__.py"))
    for heading in ("Before", "After"):
        readme.write_text(f"# {heading}\n\n```\na\n\n  b\n```\n")
        output = await device.FW_detailFn(device.hash, ["", "", "", ""], {})
        value = output.split('$("#fhempyReadme").html(', 1)[1]
        html, _ = json.JSONDecoder().raw_decode(value)
        assert f"<h1>{heading}</h1>" in html
        assert "a\n\n  b\n" in html
        assert "<br>" not in html
