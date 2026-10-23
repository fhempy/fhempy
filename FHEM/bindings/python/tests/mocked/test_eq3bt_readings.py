import pytest

from fhempy.lib.eq3bt import eq3bt as eq3bt_module


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected", [("", 0.0), ("abc", 0.0), (None, 0.0), ("42.5", 42.5)]
)
async def test_reading_float(mocker, value, expected):
    mocker.patch.object(
        eq3bt_module.fhem, "ReadingsVal", mocker.AsyncMock(return_value=value)
    )
    module = eq3bt_module.eq3bt(mocker.MagicMock())
    module.hash = {"NAME": "thermostat"}
    assert await module.reading_float("valvePosition") == expected
