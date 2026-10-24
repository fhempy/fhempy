import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def setup_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("goodwe")
    from fhempy.lib.goodwe.goodwe import goodwe

    testhash = {"NAME": "testinverter", "FHEMPYTYPE": "goodwe"}
    mock_fhem.readings.pop("testinverter", None)
    device = goodwe(logging.getLogger(__name__))
    mocker.patch.object(device, "update_loop", AsyncMock())
    await device.Define(
        testhash, ["testinverter", "fhempy", "goodwe", "192.0.2.20"], {}
    )
    return device, testhash


@pytest.mark.asyncio
async def test_set_before_connected(mocker):
    # set operation_mode failed with AttributeError in the background while
    # the inverter was not connected yet
    device, testhash = await setup_device(mocker)

    ret = await device.Set(testhash, ["testinverter", "operation_mode", "eco"], {})

    assert "Not connected to the inverter yet" in ret
    assert "192.0.2.20" in ret


@pytest.mark.asyncio
async def test_set_operation_mode(mocker):
    from goodwe.inverter import OperationMode

    device, testhash = await setup_device(mocker)
    device.inverter = MagicMock()
    device.inverter.set_operation_mode = AsyncMock()

    await device.Set(testhash, ["testinverter", "operation_mode", "eco"], {})
    await asyncio.sleep(0.1)

    device.inverter.set_operation_mode.assert_awaited_once_with(OperationMode.ECO)
    assert mock_fhem.readings["testinverter"]["operation_mode"] == "ECO"


@pytest.mark.asyncio
async def test_set_operation_mode_error(mocker):
    device, testhash = await setup_device(mocker)
    device.inverter = MagicMock()
    device.inverter.set_operation_mode = AsyncMock(side_effect=TimeoutError())
    error = mocker.patch.object(device.logger, "error")

    await device.Set(testhash, ["testinverter", "operation_mode", "eco"], {})
    await asyncio.sleep(0.1)

    error.assert_called_once_with("Failed to set operation mode: TimeoutError")
