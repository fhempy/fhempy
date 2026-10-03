import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_update(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("huawei_modbus")

    import huawei_solar
    from huawei_solar import Result, SUN2000Device
    from huawei_solar.register_values import StorageProductModel

    from fhempy.lib.huawei_modbus.huawei_modbus import huawei_modbus

    inverter = MagicMock(spec=SUN2000Device)
    inverter.pv_string_count = 2
    inverter.has_optimizers = False
    inverter.battery_type = StorageProductModel.NONE
    inverter.power_meter_type = None

    async def batch_update(registers):
        return {str(name): Result(1, "W") for name in registers}

    inverter.batch_update = AsyncMock(side_effect=batch_update)
    client = mocker.patch.object(huawei_solar, "create_tcp_client")
    mocker.patch.object(
        huawei_solar, "create_device_instance", AsyncMock(return_value=inverter)
    )

    testhash = {"NAME": "testinverter", "FHEMPYTYPE": "huawei_modbus"}
    mock_fhem.readings.pop("testinverter", None)
    device = huawei_modbus(logging.getLogger(__name__))
    await device.Define(
        testhash,
        ["testinverter", "fhempy", "huawei_modbus", "192.0.2.20", "502", "1"],
        {},
    )
    await asyncio.sleep(1)

    client.assert_called_once_with(host="192.0.2.20", port=502, unit_id=1)
    registers = inverter.batch_update.await_args.args[0]
    assert "pv_02_current" in registers
    assert mock_fhem.readings["testinverter"]["active_power"] == 1
    await device.Undefine(testhash)
