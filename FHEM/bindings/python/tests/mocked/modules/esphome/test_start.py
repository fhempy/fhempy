import logging
import os
import subprocess
import sys

import pytest
from tests.utils import mock_fhem


@pytest.mark.asyncio
async def test_starts_esphome_device_builder(mocker):
    mock_fhem.mock_module(mocker)
    from fhempy.lib.core import child_process
    from fhempy.lib.esphome import esphome as esphome_module
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
            os.path.join(
                os.path.dirname(esphome_module.__file__), "device_builder_launcher.py"
            ),
            "fhempy-testesphome",
            "esphome_config/",
            "--port",
            "6052",
        ]
    )
    assert mock_fhem.readings["testesphome"]["state"] == "running"


def test_launcher_fixes_mqtt_client_id(tmp_path):
    # fake esphome_device_builder which prints the MQTT client id and argv
    pkg = tmp_path / "esphome_device_builder"
    (pkg / "controllers").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "controllers" / "__init__.py").write_text("")
    (pkg / "controllers" / "_device_mqtt_monitor.py").write_text(
        "import secrets\n"
        "def client_id():\n"
        "    return f'esphome-dashboard-{secrets.token_hex(6)}'\n"
    )
    (pkg / "__main__.py").write_text(
        "import sys\n"
        "from esphome_device_builder.controllers import _device_mqtt_monitor\n"
        "if __name__ == '__main__':\n"
        "    print(_device_mqtt_monitor.client_id(), sys.argv[1:])\n"
    )
    from fhempy.lib.esphome import esphome as esphome_module

    launcher = os.path.join(
        os.path.dirname(esphome_module.__file__), "device_builder_launcher.py"
    )
    env = dict(os.environ, PYTHONPATH=str(tmp_path))
    out = subprocess.run(
        [sys.executable, launcher, "fhempy-esp", "esphome_config/", "--port", "6052"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert out.strip() == (
        "esphome-dashboard-fhempy-esp ['esphome_config/', '--port', '6052']"
    )
