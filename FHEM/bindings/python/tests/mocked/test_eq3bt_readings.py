import importlib
import sys

import pytest


@pytest.fixture
def eq3bt_module(mocker):
    # eq3btsmart/structures need construct and bleak, which the mocked tests
    # don't install
    mocker.patch.dict(
        sys.modules,
        {
            "fhempy.lib.eq3bt.eq3btsmart": mocker.MagicMock(),
            "fhempy.lib.eq3bt.structures": mocker.MagicMock(),
        },
    )
    sys.modules.pop("fhempy.lib.eq3bt.eq3bt", None)
    return importlib.import_module("fhempy.lib.eq3bt.eq3bt")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected", [("", 0.0), ("abc", 0.0), (None, 0.0), ("42.5", 42.5)]
)
async def test_reading_float(mocker, eq3bt_module, value, expected):
    mocker.patch.object(
        eq3bt_module.fhem, "ReadingsVal", mocker.AsyncMock(return_value=value)
    )
    module = eq3bt_module.eq3bt(mocker.MagicMock())
    module.hash = {"NAME": "thermostat"}
    assert await module.reading_float("valvePosition") == expected
