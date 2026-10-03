import asyncio
import logging
import socket

import pytest
from fhempy.lib.pkg_installer import check_and_install_dependencies
from tests.utils import mock_fhem

DEVICE_NAME = "tuya_monitor_test"


class FakeDevice:
    """Replaces tinytuya.Device, keeps one end of a socketpair as connection."""

    instances = []

    def __init__(self, dev_id, address=None, local_key="", version=3.1, **kwargs):
        self.id = dev_id
        self.address = address
        self.local_key = local_key
        self.version = version
        self.socketPersistent = kwargs.get("persist", False)
        self.socketRetryLimit = kwargs.get("connection_retry_limit", 5)
        self.children = {}
        self.socket, self.remote = socket.socketpair()
        self.sent = []
        FakeDevice.instances.append(self)

    def _get_socket(self, renew):
        return True

    def detect_available_dps(self):
        return {"1": None, "2": None, "8": None}

    def status(self, nowait=False):
        self.sent.append(("status",))
        return {"dps": {"1": True, "8": 1234}}

    def set_value(self, index, value, nowait=False):
        self.sent.append(("set_value", index, value, nowait))

    def heartbeat(self, nowait=True):
        pass

    def close(self):
        if self.socket:
            self.socket.close()
        self.socket = None


async def wait_for(condition, timeout=5):
    for _ in range(int(timeout / 0.05)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("condition not met")


@pytest.mark.asyncio
async def test_local_device_monitor(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(DEVICE_NAME, None)
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya.tuya import tuya

    FakeDevice.instances = []
    mocker.patch("tinytuya.Device", FakeDevice)

    fhempy_device = tuya(logging.getLogger(__name__))
    testhash = {"NAME": DEVICE_NAME, "FHEMPYTYPE": "tuya"}
    await fhempy_device.Define(
        testhash,
        [
            DEVICE_NAME,
            "fhempy",
            "tuya",
            "PaYQNcPunOhPeS1X",
            "345678345673456567",
            "192.168.1.10",
            "0123456789abcdef",
            "3.3",
        ],
        {},
    )

    readings = mock_fhem.readings
    await wait_for(lambda: readings.get(DEVICE_NAME, {}).get("state") == "on")
    assert readings[DEVICE_NAME]["cur_power"] == 123.4
    # detected dp without value doesn't create a reading
    assert "switch_2" not in readings[DEVICE_NAME]
    await wait_for(lambda: readings[DEVICE_NAME].get("online") == "1")

    dev = FakeDevice.instances[0]
    assert dev.socketPersistent is True
    # status is requested once the monitor runs (fallback after (re)connect)
    await wait_for(lambda: ("status",) in dev.sent[1:])

    # device pushes a status change
    fhempy_device._monitor_status(dev, {"dps": {"1": False}})
    await wait_for(lambda: readings[DEVICE_NAME]["state"] == "off")
    # heartbeat ack or error messages are ignored
    fhempy_device._monitor_status(dev, {"Error": "Network Error", "Err": "905"})

    # commands are sent through the monitor thread
    await fhempy_device.set_boolean(
        testhash, {"cmd": "on", "function_param": {"id": 1}}
    )
    await wait_for(lambda: ("set_value", 1, True, True) in dev.sent)

    # connection closed by the device
    dev.remote.close()
    await wait_for(lambda: readings[DEVICE_NAME]["online"] == "0")

    await fhempy_device.Undefine(testhash)
    assert fhempy_device._monitor is None
    assert dev.socket is None
