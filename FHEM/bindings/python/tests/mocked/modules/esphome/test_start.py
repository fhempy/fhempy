import logging
import sys

import pytest
from tests.utils import mock_fhem


@pytest.mark.asyncio
async def test_starts_esphome_device_builder(mocker):
    mock_fhem.mock_module(mocker)
    from fhempy.lib.core import child_process
    from fhempy.lib.esphome.esphome import esphome

    start = mocker.patch.object(child_process, "start")
    mock_fhem.readings.pop("testesphome", None)
    testhash = {"NAME": "testesphome", "FHEMPYTYPE": "esphome"}
    device = esphome(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(testhash, ["testesphome", "fhempy", "esphome"], {})

    # ESPHome 2026.9 removed "esphome dashboard"
    start.assert_called_once_with(
        [
            sys.executable,
            "-m",
            "esphome_device_builder",
            "esphome_config/",
            "--port",
            "6052",
        ]
    )
    assert mock_fhem.readings["testesphome"]["state"] == "running"
