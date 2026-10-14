"""Start the ESPHome Device Builder with a fixed MQTT client id.

The Device Builder connects to the MQTT broker of every device which uses
``mqtt:`` (device discovery) with the client id
``esphome-dashboard-<random>``, which changes with every start. FHEM's
MQTT2_SERVER autocreates one MQTT2_DEVICE per client id, so each restart of
the dashboard created a new device in FHEM.

Usage: python device_builder_launcher.py <client id suffix> <builder args>

Runs as a standalone script in the child process, no fhempy imports.
"""

import os
import runpy
import sys

# Python puts this directory first on sys.path, its esphome.py (the fhempy
# module) would shadow the esphome package.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p or os.curdir) != _HERE]


class _FixedTokenSecrets:
    def __init__(self, token):
        self._token = token

    def token_hex(self, nbytes=None):
        return self._token


def _fix_mqtt_client_id(suffix):
    try:
        from esphome_device_builder.controllers import _device_mqtt_monitor
    except Exception as err:  # noqa: BLE001 - never block the dashboard start
        print(f"fhempy: MQTT client id not fixed: {err}", file=sys.stderr)
        return
    # secrets.token_hex is only used for the MQTT client id in this module
    _device_mqtt_monitor.secrets = _FixedTokenSecrets(suffix)


def main():
    suffix = sys.argv[1]
    sys.argv = ["esphome_device_builder"] + sys.argv[2:]
    _fix_mqtt_client_id(suffix)
    runpy.run_module("esphome_device_builder", run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
