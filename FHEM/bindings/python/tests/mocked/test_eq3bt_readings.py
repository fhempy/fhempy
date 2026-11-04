import asyncio
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


def make_module(mocker, eq3bt_module, valve=0):
    fhem = eq3bt_module.fhem
    mocker.patch.object(fhem, "ReadingsVal", mocker.AsyncMock(return_value="1.5"))
    mocker.patch.object(fhem, "readingsBeginUpdate", mocker.AsyncMock())
    mocker.patch.object(fhem, "readingsBulkUpdateIfChanged", mocker.AsyncMock())
    mocker.patch.object(fhem, "readingsEndUpdate", mocker.AsyncMock())
    mocker.patch.object(fhem, "readingsSingleUpdateIfChanged", mocker.AsyncMock())
    module = eq3bt_module.eq3bt(mocker.MagicMock())
    module.hash = {"NAME": "thermostat"}
    module.thermostat = mocker.MagicMock()
    module.thermostat.valve_state = valve
    module.thermostat.schedule = {}
    return module, fhem


@pytest.mark.asyncio
async def test_unchanged_values_are_not_sent_again(mocker, eq3bt_module):
    module, fhem = make_module(mocker, eq3bt_module)
    await module.update_all_readings()
    await module.update_all_readings()
    await module.update_all_readings()
    # valve position and consumption are read from FHEM only once
    assert fhem.ReadingsVal.await_count == 3
    # status, id and schedule written once, nothing changed afterwards
    assert fhem.readingsEndUpdate.await_count == 3
    module.thermostat.target_temperature = 21.5
    await module.update_all_readings()
    assert fhem.readingsEndUpdate.await_count == 4
    fhem.readingsBulkUpdateIfChanged.assert_any_await(
        module.hash, "desiredTemperature", 21.5
    )


@pytest.mark.asyncio
async def test_offline_state_is_replaced_again(mocker, eq3bt_module):
    module, fhem = make_module(mocker, eq3bt_module)
    await module.update_readings()
    await module._set_offline()
    await module.update_readings()
    assert fhem.readingsEndUpdate.await_count == 2


@pytest.mark.asyncio
async def test_consumption_reset_reads_fhem_again(mocker, eq3bt_module):
    module, fhem = make_module(mocker, eq3bt_module)
    await module.update_readings()
    await module.set_resetConsumption(module.hash, {"cons_var": "all"})
    fhem.ReadingsVal.return_value = "0"
    await module.update_readings()
    assert fhem.ReadingsVal.await_count == 6
    fhem.readingsBulkUpdateIfChanged.assert_any_await(
        module.hash, "consumptionToday", 0.0
    )


@pytest.mark.asyncio
async def test_notifications_are_written_together(mocker, eq3bt_module):
    module, fhem = make_module(mocker, eq3bt_module)
    mocker.patch.object(eq3bt_module, "NOTIFY_DELAY", 0.05)
    update = mocker.patch.object(module, "update_all_readings", mocker.AsyncMock())
    for _ in range(9):
        await module.notification_received()
    await asyncio.sleep(0.2)
    assert update.await_count == 1
    await module.notification_received()
    await asyncio.sleep(0.2)
    assert update.await_count == 2
