"""Matter Level Control: continuous dimming and per-device dimRate."""

import logging
from types import SimpleNamespace

import pytest

from fhempy.lib.matter import clusters
from fhempy.lib.matter.device import _dim_rate, matter_device


def level_model():
    return clusters.DeviceModel({"1/8/0": 127}, [1])


@pytest.mark.parametrize(
    "command,wire_command,move_mode",
    [
        ("dim_up", "Move", 0),
        ("dim_down", "Move", 1),
        ("dim_stop", "Stop", None),
    ],
)
def test_continuous_dim_commands(command, wire_command, move_mode):
    args = level_model().command_args(command, None)
    assert args["kind"] == "command"
    assert args["endpoint_id"] == 1
    assert args["cluster_id"] == clusters.LEVEL_CONTROL
    assert args["command_name"] == wire_command
    assert args["payload"]["optionsMask"] == 0
    assert args["payload"]["optionsOverride"] == 0
    if move_mode is None:
        assert "rate" not in args["payload"]
    else:
        assert args["payload"]["moveMode"] == move_mode
        assert args["payload"]["rate"] == 30


@pytest.mark.parametrize("rate", ["1", "12", "30", "50", "254"])
def test_valid_dim_rate(rate):
    assert _dim_rate(rate) == int(rate)


@pytest.mark.parametrize("rate", ["0", "-1", "255", "abc", "10.5"])
def test_invalid_dim_rate(rate):
    with pytest.raises(ValueError):
        _dim_rate(rate)


@pytest.mark.asyncio
async def test_dimming_uses_each_device_attribute_and_does_not_affect_stop():
    outputs = []
    for speed in (12, 50):
        own_commands = []
        fhemdev = SimpleNamespace(
            _attr_dimRate=speed,
            create_async_task=own_commands.append,
        )
        device = matter_device(logging.getLogger(__name__), fhemdev)
        device.model = level_model()
        device._run = lambda args: args
        for cmd in ("dim_up", "dim_down", "dim_stop"):
            assert await device.set_matter({}, {"cmd": cmd}) is None
        outputs.append(own_commands)

    assert [cmd["payload"].get("rate") for cmd in outputs[0]] == [
        12, 12, None
    ]
    assert [cmd["payload"].get("rate") for cmd in outputs[1]] == [
        50, 50, None
    ]


@pytest.mark.asyncio
async def test_rate_change_applies_to_next_command():
    commands = []
    fhemdev = SimpleNamespace(_attr_dimRate=30, create_async_task=commands.append)
    device = matter_device(logging.getLogger(__name__), fhemdev)
    device.model = level_model()
    device._run = lambda args: args

    await device.set_matter({}, {"cmd": "dim_up"})
    fhemdev._attr_dimRate = 60
    await device.set_matter({}, {"cmd": "dim_up"})

    assert [item["payload"]["rate"] for item in commands] == [30, 60]
