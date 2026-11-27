"""Invalid user input must be rejected before handlers or callbacks run."""
import copy
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fhempy.lib import utils


def positive_integer(value):
    number = int(value)
    if number <= 0:
        raise ValueError("expected a positive integer")
    return number


@pytest.mark.asyncio
@pytest.mark.parametrize("dispatcher", [utils.handle_set, utils.handle_get])
@pytest.mark.parametrize("format,value,reason", [
    ("int", "dsfsdf", "expected int"),
    ("int", None, "expected int"),
    ("int", float("inf"), "expected int"),
    ("float", "bad", "expected float"),
    (positive_integer, "-1", "expected a positive integer"),
])
async def test_conversion_errors_do_not_call_handlers(dispatcher, format, value, reason):
    handler = AsyncMock()
    obj = SimpleNamespace(handle=handler)
    config = {"probe": {
        "args": ["count"], "argsh": ["count"], "function": "handle",
        "params": {"count": {"format": format}},
    }}
    original = copy.deepcopy(config)
    for args, argsh in [(["dev", "probe", value], {}), (["dev", "probe"], {"count": value})]:
        reply = await dispatcher(config, obj, {"NAME": "dev"}, args, argsh)
        assert reply.startswith("Invalid value for count:")
        assert reason in reply
    handler.assert_not_called()
    assert config == original


@pytest.mark.asyncio
@pytest.mark.parametrize("dispatcher", [utils.handle_set, utils.handle_get])
async def test_callable_format_converts_defaults_without_retaining_previous_values(dispatcher):
    obj = SimpleNamespace(handle=AsyncMock())
    config = {"probe": {"args": ["count"], "function": "handle", "params": {
        "count": {"format": positive_integer, "default": "3"},
    }}}
    await dispatcher(config, obj, {"NAME": "dev"}, ["dev", "probe", "5"], {})
    obj.handle.assert_awaited_with({"NAME": "dev"}, {"count": 5, "cmd": "probe"})
    await dispatcher(config, obj, {"NAME": "dev"}, ["dev", "probe"], {})
    obj.handle.assert_awaited_with({"NAME": "dev"}, {"count": 3, "cmd": "probe"})


@pytest.mark.asyncio
@pytest.mark.parametrize("dispatcher", [utils.handle_set, utils.handle_get])
@pytest.mark.parametrize("args,argsh,message", [
    (["dev", "probe"], {"typo": "1"}, "Unknown named argument: typo"),
    (["dev", "probe", "1"], {"count": "2"}, "Argument provided twice: count"),
])
async def test_keyword_errors_do_not_call_handlers(dispatcher, args, argsh, message):
    obj = SimpleNamespace(handle=AsyncMock())
    config = {"probe": {"args": ["count"], "argsh": ["count"], "function": "handle"}}
    assert await dispatcher(config, obj, {"NAME": "dev"}, args, argsh) == message
    obj.handle.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_attribute_preserves_value_and_skips_callback():
    obj = SimpleNamespace(_attr_count=7, set_attr_count=AsyncMock(return_value=None))
    config = {"count": {"format": "int", "default": "3"}}
    reply = await utils.handle_attr(config, obj, {}, ["set", "dev", "count", "bad"], {})
    assert reply.startswith("Invalid value for count:")
    assert obj._attr_count == 7
    obj.set_attr_count.assert_not_called()
    assert await utils.handle_attr(config, obj, {}, ["del", "dev", "count"], {}) is None
    assert obj._attr_count == 3
    obj.set_attr_count.assert_awaited_once_with({})
    del config["count"]["default"]
    await utils.handle_attr(config, obj, {}, ["del", "dev", "count"], {})
    assert obj._attr_count == ""


@pytest.mark.asyncio
async def test_invalid_stored_attribute_uses_validated_default(monkeypatch, caplog):
    monkeypatch.setattr(utils.fhem, "getDeviceInfo", AsyncMock(return_value={
        "init_done": 1, "attr": {"count": "invalid"},
    }))
    obj = SimpleNamespace(logger=logging.getLogger("validation"))
    config = {"count": {"format": positive_integer, "default": "3"}}
    await utils.handle_define_attr(config, obj, {"NAME": "dev"})
    assert obj._attr_count == 3
    assert "Using default 3" in caplog.text
    assert all(record.exc_info is None for record in caplog.records)


@pytest.mark.asyncio
async def test_unexpected_converter_errors_are_not_hidden():
    def broken(value):
        raise RuntimeError("implementation bug")

    obj = SimpleNamespace(handle=AsyncMock())
    config = {"probe": {"args": ["count"], "function": "handle", "params": {
        "count": {"format": broken},
    }}}
    with pytest.raises(RuntimeError, match="implementation bug"):
        await utils.handle_set(config, obj, {"NAME": "dev"}, ["dev", "probe", "3"], {})
    obj.handle.assert_not_called()


@pytest.mark.asyncio
async def test_plain_function_attribute_callback():
    calls = []
    obj = SimpleNamespace(_attr_count=1, set_attr_count=calls.append)
    config = {"count": {"format": "int", "default": "3"}}
    assert await utils.handle_attr(config, obj, {}, ["set", "dev", "count", "5"], {}) is None
    assert obj._attr_count == 5
    assert calls == [{}]


@pytest.mark.asyncio
async def test_plain_function_event_listener():
    from fhempy.lib import fhem

    events = []

    def listener(device, reading, value):
        events.append((device, reading, value))

    fhem.register_event_listener("plain_dev", listener)
    try:
        await fhem.dispatch_event("plain_dev", "temperature: 21")
    finally:
        fhem.unregister_event_listener("plain_dev", listener)
    assert events == [("plain_dev", "temperature", "21")]


@pytest.mark.asyncio
@pytest.mark.parametrize("args,params", [
    (["dev", "speak", "Hello", "world"], {"text": "Hello world"}),
    (["dev", "speak", "Hello world"], {"text": "Hello world"}),
    (["dev", "speak", "Hello"], {"text": "Hello"}),
])
async def test_text_argument_takes_all_remaining_words(args, params):
    obj = SimpleNamespace(set_speak=AsyncMock(return_value=None))
    config = {"speak": {"args": ["text"], "text": True}}
    reply = await utils.handle_set(config, obj, {"NAME": "dev"}, args, {})
    assert reply is None
    obj.set_speak.assert_awaited_once_with({"NAME": "dev"}, params)


@pytest.mark.asyncio
async def test_text_argument_is_the_last_one():
    obj = SimpleNamespace(set_show=AsyncMock(return_value=None))
    config = {"show": {"args": ["text", "display"], "text": True}}
    await utils.handle_set(
        config, obj, {"NAME": "dev"}, ["dev", "show", "Long text", "short", "one"], {}
    )
    obj.set_show.assert_awaited_once_with(
        {"NAME": "dev"}, {"text": "Long text", "display": "short one"}
    )


@pytest.mark.asyncio
async def test_without_text_extra_words_are_rejected():
    obj = SimpleNamespace(set_speak=AsyncMock())
    config = {"speak": {"args": ["text"]}}
    reply = await utils.handle_set(
        config, obj, {"NAME": "dev"}, ["dev", "speak", "Hello", "world"], {}
    )
    assert reply == "Usage: set dev speak text"
    obj.set_speak.assert_not_called()


@pytest.mark.asyncio
async def test_text_argument_with_named_arguments():
    obj = SimpleNamespace(set_alarm=AsyncMock(return_value=None))
    config = {"alarm": {
        "args": ["text"], "text": True, "argsh": ["text", "duration"],
        "params": {"text": {"default": "Alarm"}, "duration": {"format": "int"}},
    }}
    await utils.handle_set(
        config, obj, {"NAME": "dev"}, ["dev", "alarm", "Door", "open"], {"duration": "5"}
    )
    obj.set_alarm.assert_awaited_once_with(
        {"NAME": "dev"}, {"text": "Door open", "duration": 5}
    )
