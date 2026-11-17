import asyncio
import logging
import threading
import time

import pytest
import pytest_asyncio

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest_asyncio.fixture
async def blemonitor(mocker):
    # janus, aioblescan and bleparser are installed with the module
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import blemonitor

    started = []

    class FakeThread:
        def __init__(self, logger, config, dataqueue):
            started.append(threading.get_ident())
            self.alive = False

        def start(self):
            self.alive = True

        def is_alive(self):
            return self.alive

        def join(self):
            self.alive = False

    mocker.patch.object(blemonitor, "HCIdump", FakeThread)
    mocker.patch.object(blemonitor, "RESTART_DELAY", 0.05)
    monitor = blemonitor.BLEmonitor(logging.getLogger("test"))
    yield monitor, started
    monitor.task_measuring.cancel()
    monitor.task_tracker.cancel()


@pytest.mark.asyncio
async def test_many_restarts_start_the_scan_once(blemonitor):
    monitor, started = blemonitor
    for _ in range(10):
        monitor.restart()
        await asyncio.sleep(0.01)
    assert started == []
    await asyncio.wait_for(monitor._restart_task, 2)
    assert len(started) == 1
    # stop/start (joins the old thread) doesn't run on the event loop
    assert started[0] != threading.get_ident()


@pytest.mark.asyncio
async def test_restart_requested_while_restarting_runs_again(blemonitor, mocker):
    monitor, started = blemonitor
    original = monitor._restart_now

    def restart_now():
        original()
        if len(started) == 1:
            # a device registered while the old thread was joined
            monitor._restart_requested = time.monotonic()

    mocker.patch.object(monitor, "_restart_now", restart_now)
    monitor.restart()
    await asyncio.wait_for(monitor._restart_task, 5)
    assert len(started) == 2


@pytest.mark.asyncio
async def test_malformed_advertisement_is_skipped(mocker):
    """bleparser raises on malformed payloads (e.g. struct.error for a too
    short service data), the packet is skipped instead of logged as error."""
    import struct

    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import hcidump

    dump = mocker.MagicMock(evt_cnt=0)
    dump.ble_parser.parse_raw_data_reports.side_effect = struct.error(
        "unpack requires a buffer of 6 bytes"
    )
    hcidump.HCIdump.process_hci_events(dump, b"\x00" * 20, gateway_id="proxy")
    dump.logger.debug.assert_called_once()
    dump.dataqueue_tracker.sync_q.put_nowait.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("device_type", ["TP357", "Some new bleparser sensor"])
async def test_sensor_type_missing_in_measurement_dict(mocker, device_type):
    """bleparser returns sensor types (e.g. ThermoPro TP357) that must not
    crash the scanner with a KeyError, the readings are delivered."""
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import hcidump

    msg = {"type": device_type, "mac": "AA:BB:CC:DD:EE:FF", "temperature": 21.5}
    dump = mocker.MagicMock(evt_cnt=0)
    dump.ble_parser.parse_raw_data_reports.return_value = [(msg, None)]
    dump._queue_report = lambda *args: hcidump.HCIdump._queue_report(dump, *args)
    dump._queue_sensor_msg = lambda *args: hcidump.HCIdump._queue_sensor_msg(
        dump, *args
    )
    hcidump.HCIdump.process_hci_events(dump, b"\x00" * 20)
    dump.dataqueue_meas.sync_q.put_nowait.assert_called_once_with(msg)


def _hci_adv(mac, name, man_spec_data, rssi=-60):
    """Build a raw HCI LE advertising report like the scanner receives it."""
    name_bytes = name.encode()
    payload = bytes([len(name_bytes) + 1, 0x09]) + name_bytes
    payload += bytes([len(man_spec_data) + 1, 0xFF]) + man_spec_data
    body = (
        bytes([0x02, 0x01, 0x00, 0x00])
        + bytes.fromhex(mac.replace(":", ""))[::-1]
        + bytes([len(payload)])
        + payload
        + bytes([rssi & 0xFF])
    )
    return bytes([0x04, 0x3E, len(body)]) + body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "battery_byte, battery",
    [(0x22, 100), (0x21, 50), (0x20, 0)],
)
async def test_thermopro_tp357s_with_battery(battery_byte, battery):
    """TP357S sends one manufacturer data byte more than the TP357, it
    carries a 2 bit battery level (ble_monitor reports it as always low)."""
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor.parser import FhempyBleParser

    parser = FhempyBleParser()
    # temperature 21.5 C, humidity 45 %, battery
    data = bytes([0xC2, 0xD7, 0x00, 0x2D, battery_byte, 0x2C, 0x01])
    sensor, _ = parser.parse_raw_data(
        _hci_adv("AA:BB:CC:DD:EE:01", "TP357S (EE01)", data)
    )
    assert sensor["type"] == "TP357"
    assert sensor["temperature"] == 21.5
    assert sensor["humidity"] == 45
    assert sensor["battery"] == battery
    assert "battery low" not in sensor
    assert sensor["rssi"] == -60


@pytest.mark.asyncio
async def test_thermopro_tp357_unchanged():
    """The 7 byte TP357 advertisement is parsed like ble_monitor does it."""
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor.parser import FhempyBleParser

    parser = FhempyBleParser()
    data = bytes([0xC2, 0xD7, 0x00, 0x2D, 0x22, 0x2C])
    sensor, _ = parser.parse_raw_data(
        _hci_adv("AA:BB:CC:DD:EE:02", "TP357 (EE02)", data)
    )
    assert sensor["temperature"] == 21.5
    assert sensor["humidity"] == 45
    assert "battery" not in sensor


@pytest.mark.asyncio
async def test_other_devices_untouched():
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor.parser import FhempyBleParser

    parser = FhempyBleParser()
    data = bytes([0xC2, 0xD7, 0x00, 0x2D, 0x22, 0x2C, 0x01])
    sensor, _ = parser.parse_raw_data(
        _hci_adv("AA:BB:CC:DD:EE:03", "Foo123", data)
    )
    assert sensor is None


def test_copied_parser_has_no_home_assistant_imports():
    """tools/sync_ble_parser.py copies ble_parser from ble_monitor, which is
    a Home Assistant component: the copy must run without Home Assistant."""
    from pathlib import Path

    import fhempy.lib.ble_monitor as module

    folder = Path(module.__file__).parent / "ble_parser"
    assert (folder / "UPSTREAM").is_file()
    assert (folder / "LICENSE").is_file()
    for path in folder.glob("*.py"):
        assert "homeassistant" not in path.read_text(encoding="utf-8"), path


@pytest.mark.asyncio
async def test_readings_without_spaces(mocker):
    from fhempy.lib.ble_monitor import ble_monitor

    update = mocker.patch.object(
        ble_monitor.fhem, "readingsBulkUpdateIfChanged", mocker.AsyncMock()
    )
    mocker.patch.object(ble_monitor.fhem, "readingsBeginUpdate", mocker.AsyncMock())
    mocker.patch.object(ble_monitor.fhem, "readingsEndUpdate", mocker.AsyncMock())
    dev = ble_monitor.ble_monitor.__new__(ble_monitor.ble_monitor)
    dev.hash = {}
    await dev.received_data({"battery low": 1, "temperature": 20.5})
    names = [call.args[1] for call in update.call_args_list]
    assert names == ["battery_low", "temperature"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cap_eff, euid, hint",
    [
        ("0000000000000000", 1000, True),
        ("0000000000001000", 1000, True),  # only CAP_NET_ADMIN
        ("0000000000003000", 1000, False),  # CAP_NET_RAW + CAP_NET_ADMIN
        ("0000000000000000", 0, False),  # root
    ],
)
async def test_hint_for_missing_net_raw(tmp_path, cap_eff, euid, hint):
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor.hcidump import missing_net_raw_hint

    status = tmp_path / "status"
    status.write_text(f"Name:\tpython3\nCapEff:\t{cap_eff}\n", encoding="ascii")
    text = missing_net_raw_hint(str(status), euid, "/usr/bin/python3")
    assert bool(text) is hint
    if hint:
        assert "CAP_NET_RAW" in text
        assert "setcap 'cap_net_raw,cap_net_admin+eip' /usr/bin/python3" in text


@pytest.mark.asyncio
async def test_no_hint_if_capabilities_unknown(tmp_path):
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor.hcidump import missing_net_raw_hint

    assert missing_net_raw_hint(str(tmp_path / "missing"), 1000) == ""
    status = tmp_path / "status"
    status.write_text("Name:\tpython3\n", encoding="ascii")
    assert missing_net_raw_hint(str(status), 1000) == ""


def _ext_report(mac, name, man_spec_data, rssi=-60):
    """One report of an HCI LE extended advertising report event."""
    name_bytes = name.encode()
    payload = bytes([len(name_bytes) + 1, 0x09]) + name_bytes
    payload += bytes([len(man_spec_data) + 1, 0xFF]) + man_spec_data
    return (
        bytes([0x13, 0x00, 0x00])  # legacy ADV_IND, public address
        + bytes.fromhex(mac.replace(":", ""))[::-1]
        + bytes([0x01, 0x00, 0xFF, 0x7F, rssi & 0xFF, 0x00, 0x00, 0x00])
        + bytes(6)
        + bytes([len(payload)])
        + payload
    )


@pytest.mark.asyncio
async def test_all_reports_of_an_extended_event_are_delivered(mocker):
    """Adapters with extended scanning put several advertisements (of
    different devices) into one HCI event, each of them is delivered."""
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import hcidump
    from fhempy.lib.ble_monitor.parser import FhempyBleParser

    first = bytes([0xC2, 0xD7, 0x00, 0x2D, 0x22, 0x2C])
    second = bytes([0xC2, 0xDC, 0x00, 0x32, 0x22, 0x2C])
    reports = _ext_report("AA:BB:CC:DD:EE:11", "TP357 (EE11)", first)
    reports += _ext_report("AA:BB:CC:DD:EE:12", "TP357 (EE12)", second)
    body = bytes([0x0D, 2]) + reports
    event = bytes([0x04, 0x3E, len(body)]) + body

    dump = mocker.MagicMock(evt_cnt=0)
    dump.ble_parser = FhempyBleParser()
    dump._queue_report = lambda *args: hcidump.HCIdump._queue_report(dump, *args)
    dump._queue_sensor_msg = lambda *args: hcidump.HCIdump._queue_sensor_msg(
        dump, *args
    )
    hcidump.HCIdump.process_hci_events(dump, event)
    delivered = [
        call.args[0] for call in dump.dataqueue_meas.sync_q.put_nowait.call_args_list
    ]
    assert [msg["mac"] for msg in delivered] == ["AABBCCDDEE11", "AABBCCDDEE12"]
    assert [msg["temperature"] for msg in delivered] == [21.5, 22.0]
