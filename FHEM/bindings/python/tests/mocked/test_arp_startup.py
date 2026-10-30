import asyncio
import logging
import re
import socket
import struct
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from fhempy.lib import fhem, fhem_pythonbinding as binding
from fhempy.lib.arp_presence import arp_presence as arp


class Clock:
    now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def neighbour_reply(present):
    done = struct.pack("=IHHIIi", 20, 3, 0, 1, 0, 0)
    if not present:
        return done
    attributes = struct.pack("=HH4s", 8, 1, socket.inet_aton("192.0.2.1"))
    attributes += struct.pack("=HH6s2x", 10, 2, bytes.fromhex("001a2b3c4d5e"))
    neighbour = struct.pack("=B3xiHBB", socket.AF_INET, 2, 2, 0, 1) + attributes
    return struct.pack("=IHHII", 16 + len(neighbour), 28, 0, 1, 0) + neighbour + done


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["192.0.2.1", "00:1a:2b:3c:4d:5e"])
@pytest.mark.parametrize("present", [False, True])
async def test_last_table_query_has_its_own_timeout(monkeypatch, target, present):
    """A small scheduling delay near the scan deadline is not a query failure."""
    clock = Clock()
    device = arp.arp_presence(logging.getLogger("arp_timeout_test"))
    monkeypatch.setattr(arp, "time", clock)

    def probe(*args):
        clock.now = 0.999

    monkeypatch.setattr(device, "ping_device", probe)
    replies = [neighbour_reply(present)]
    if ":" in target:
        replies.insert(0, neighbour_reply(True))

    def open_socket(*args):
        # Simulate being descheduled after starting a fresh table query.
        clock.now += 0.01
        sock = MagicMock()
        sock.__enter__.return_value = sock
        sock.recvmsg.return_value = (replies.pop(0), [], 0, (0, 0))
        return sock

    monkeypatch.setattr(arp.socket, "socket", open_socket)
    assert device.scan_device(target) is present
    assert clock.now < arp.SCAN_TIMEOUT + arp.NETLINK_TIMEOUT


@pytest.fixture
def device_setup(monkeypatch):
    readings = {"presence": "present", "state": "present"}
    device_hash = {"NAME": "presence_test", "FHEMPYTYPE": "arp_presence"}

    async def command(hash, text):
        for reading, value in re.findall(
            r"readings(?:Single|Bulk)Update\(\$defs\{'presence_test'\},"
            r"'([^']+)','([^']*)'", text
        ):
            # hidden readings like .defaultAttrs aren't part of these tests
            if not reading.startswith("."):
                readings[reading] = value
        return ""

    async def info(name, attrs, *args):
        return {"init_done": 1, "attr": dict(attrs)}

    monkeypatch.setattr(fhem, "sendCommandHash", command)
    monkeypatch.setattr(fhem, "getDeviceInfo", info)
    monkeypatch.setattr(fhem, "AttrVal", AsyncMock(return_value="people_sensor"))
    monkeypatch.setattr(fhem, "send_default_response", AsyncMock())
    monkeypatch.setattr(fhem, "update_locks", {})
    monkeypatch.setattr(fhem, "bulk_updates", {})
    monkeypatch.setattr(fhem, "function_active", [])
    monkeypatch.setattr(binding, "loadedModuleInstances", {})
    monkeypatch.setattr(binding, "moduleLoadingRunning", {})
    monkeypatch.setattr(binding, "stop_event", asyncio.Event())
    # These tests drive scans explicitly instead of starting periodic workers.
    monkeypatch.setattr(
        arp.arp_presence, "create_async_task", lambda self, coro: coro.close()
    )
    return device_hash, readings


def define_request(device_hash, address):
    args = [device_hash["NAME"], "fhempy", "arp_presence", address]
    return dict(
        device_hash, id=1, function="Define", args=args, argsh={},
        defargs=args, defargsh={},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("previous", [None, "present", "absent"])
async def test_start_preserves_presence(device_setup, previous):
    device_hash, readings = device_setup
    if previous is None:
        readings.pop("presence")
    else:
        readings["presence"] = previous
    device = arp.arp_presence(logging.getLogger("arp_start_test"))
    request = define_request(device_hash, "192.0.2.1")
    await device.Define(request, request["args"], {})
    assert readings["state"] == "initialized"
    assert readings.get("presence") == previous


@pytest.mark.asyncio
@pytest.mark.parametrize("changed", [False, True])
async def test_direct_redefine_resets_presence_only_for_changed_definition(
    device_setup, changed
):
    device_hash, readings = device_setup
    device = arp.arp_presence(logging.getLogger("arp_redefine_test"))
    for address in ("192.0.2.1", "192.0.2.2" if changed else "192.0.2.1"):
        request = define_request(device_hash, address)
        await device.Define(request, request["args"], {})
    assert readings["state"] == "initialized"
    assert readings["presence"] == ("initialized" if changed else "present")


@pytest.mark.asyncio
async def test_binding_distinguishes_redefine_from_restart(device_setup):
    device_hash, readings = device_setup
    client = binding.fhempy(SimpleNamespace(send=AsyncMock()))
    client.check_and_install_dependencies = AsyncMock()
    client.import_module = AsyncMock(return_value=arp)
    client.sendBackReturn = AsyncMock()
    client.updateHash = AsyncMock()
    for address, expected in (
        ("192.0.2.1", "present"), ("192.0.2.1", "present"),
        ("192.0.2.2", "initialized"),
    ):
        await client.handle_function(define_request(device_hash, address), "")
        assert readings == {"state": "initialized", "presence": expected}
    readings["presence"] = "absent"
    binding.loadedModuleInstances.clear()  # The next Define follows a restart.
    await client.handle_function(define_request(device_hash, "192.0.2.2"), "")
    assert readings == {"state": "initialized", "presence": "absent"}


@pytest.mark.asyncio
async def test_real_query_failure_keeps_presence_and_logs_error(
    device_setup, monkeypatch, caplog
):
    device_hash, readings = device_setup
    device = arp.arp_presence(logging.getLogger("arp_error_test"))
    request = define_request(device_hash, "192.0.2.1")
    await device.Define(request, request["args"], {})
    monkeypatch.setattr(
        device, "scan_device",
        Mock(side_effect=TimeoutError("Neighbour table query timed out")),
    )
    with caplog.at_level(logging.ERROR):
        await device.update_once()
    assert readings["presence"] == "present"
    assert readings["state"] == "error: Neighbour table query timed out"
    assert caplog.records[-1].levelno == logging.ERROR


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid", [None, "not-an-ip", "999.1.2.3"])
async def test_rejected_arp_def_keeps_running_device(device_setup, invalid):
    device_hash, readings = device_setup
    client = binding.fhempy(SimpleNamespace(send=AsyncMock()))
    client.check_and_install_dependencies = AsyncMock()
    client.import_module = AsyncMock(return_value=arp)
    client.sendBackReturn = AsyncMock()
    client.updateHash = AsyncMock()
    await client.handle_function(define_request(device_hash, "192.0.2.1"), "")
    previous = binding.loadedModuleInstances[device_hash["NAME"]]
    readings.update(state="present", presence="present")
    client.sendBackReturn.reset_mock()
    client.check_and_install_dependencies.reset_mock()
    client.import_module.reset_mock()
    request = define_request(device_hash, invalid)
    if invalid is None:
        request["args"].pop()
    await client.handle_function(request, "")
    client.sendBackReturn.assert_awaited_once()
    expected = (
        arp.USAGE if invalid is None else "error: invalid IPv4 or MAC address"
    )
    assert client.sendBackReturn.await_args.args[1] == expected
    assert binding.loadedModuleInstances[device_hash["NAME"]] is previous
    assert previous._target == "192.0.2.1"
    assert readings == {"state": "present", "presence": "present"}
    client.check_and_install_dependencies.assert_not_awaited()
    client.import_module.assert_not_awaited()


@pytest.mark.asyncio
async def test_valid_arp_def_replaces_running_device(device_setup):
    device_hash, readings = device_setup
    client = binding.fhempy(SimpleNamespace(send=AsyncMock()))
    client.check_and_install_dependencies = AsyncMock()
    client.import_module = AsyncMock(return_value=arp)
    client.sendBackReturn = AsyncMock()
    client.updateHash = AsyncMock()
    await client.handle_function(define_request(device_hash, "192.0.2.1"), "")
    previous = binding.loadedModuleInstances[device_hash["NAME"]]
    await client.handle_function(define_request(device_hash, "192.0.2.2"), "")
    current = binding.loadedModuleInstances[device_hash["NAME"]]
    assert current is not previous
    assert current._target == "192.0.2.2"
    assert readings == {"state": "initialized", "presence": "initialized"}
