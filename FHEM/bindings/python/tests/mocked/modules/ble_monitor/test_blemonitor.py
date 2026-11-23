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
    sensor, _ = parser.parse_raw_data(_hci_adv("AA:BB:CC:DD:EE:03", "Foo123", data))
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
    mocker.patch.object(ble_monitor.fhem, "AttrVal", mocker.AsyncMock())
    dev = ble_monitor.ble_monitor.__new__(ble_monitor.ble_monitor)
    dev.hash = {"NAME": "ble_dev"}
    dev._values = {}
    dev._alias_checked = False
    await dev.received_data({"battery low": 1, "temperature": 20.5})
    names = [call.args[1] for call in update.call_args_list]
    assert names == ["battery_low", "temperature", "state"]


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


def _cmd_complete(opcode, status=0):
    return bytes([0x04, 0x0E, 4, 1, opcode & 0xFF, opcode >> 8, status])


def _dump_with_loop(mocker, hcidump):
    import collections

    dump = mocker.MagicMock(evt_cnt=0)
    for name in (
        "process_local_hci_event",
        "_foreign_command",
        "_rearm",
    ):
        setattr(
            dump,
            name,
            getattr(hcidump.HCIdump, name).__get__(dump),
        )
    dump._own_commands = {
        0: collections.Counter(hcidump.OWN_SCAN_OPCODES[True]),
    }
    dump._rearm_handle = None
    dump._rearms = collections.deque()
    dump._rearm_warned = False
    loop = asyncio.new_event_loop()
    dump._event_loop = loop
    return dump, loop


def _run_loop(loop, seconds):
    loop.call_later(seconds, loop.stop)
    loop.run_forever()


def test_scan_is_set_up_again_after_another_program_resets_the_adapter(
    mocker,
):
    """e.g. the Matter server (noble) sends HCI_Reset, its own LE event mask
    and disables the scan when it starts with Bluetooth"""
    asyncio.run(check_and_install_dependencies("ble_monitor"))
    from fhempy.lib.ble_monitor import hcidump

    mocker.patch.object(hcidump, "REARM_DELAY", 0.05)
    dump, loop = _dump_with_loop(mocker, hcidump)
    stop = mocker.patch.object(loop, "stop", wraps=loop.stop)
    try:
        # command complete of our own scan request: ignored
        dump.process_local_hci_event(0, _cmd_complete(0x2041))
        dump.process_local_hci_event(0, _cmd_complete(0x2042))
        _run_loop(loop, 0.1)
        assert stop.call_count == 1  # only _run_loop's stop

        # another program: Reset, LE event mask, scan disabled
        for opcode in (0x0C03, 0x2001, 0x2042):
            dump.process_local_hci_event(0, _cmd_complete(opcode))
        _run_loop(loop, 0.5)
        # one restart of the scan after the whole sequence, it stops the
        # loop before _run_loop does
        assert stop.call_count == 2
        dump.logger.info.assert_called_once()
        assert len(dump._rearms) == 1
        dump.process_hci_events.assert_not_called()

        # advertisements still go to the parser
        dump.process_local_hci_event(0, b"\x04\x3e\x0c" + bytes(12))
        dump.process_hci_events.assert_called_once()
    finally:
        loop.close()


def test_scan_is_left_alone_while_adapter_is_claimed(mocker):
    asyncio.run(check_and_install_dependencies("ble_monitor"))
    from fhempy.lib.ble_monitor import hcidump
    from fhempy.lib.core import hci_claims

    mocker.patch.object(hcidump, "REARM_DELAY", 0.01)
    dump, loop = _dump_with_loop(mocker, hcidump)
    stop = mocker.patch.object(loop, "stop", wraps=loop.stop)
    hci_claims.claim(0, "test")
    try:
        dump.process_local_hci_event(0, _cmd_complete(0x0C03))
        _run_loop(loop, 0.05)
        assert stop.call_count == 1
    finally:
        hci_claims.release(0, "test")
        loop.close()


@pytest.mark.asyncio
async def test_scan_takeover_is_limited(mocker):
    """two programs must not take the scan from each other endlessly"""
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import hcidump

    mocker.patch.object(hcidump, "REARM_DELAY", 0.001)
    dump, loop = _dump_with_loop(mocker, hcidump)
    stop = mocker.patch.object(loop, "stop")
    try:
        for _ in range(hcidump.MAX_REARMS + 3):
            dump._rearm(0, 0x200C)
        assert stop.call_count == hcidump.MAX_REARMS
        dump.logger.warning.assert_called_once()
    finally:
        loop.close()


@pytest.mark.asyncio
async def test_scan_restarts_when_adapter_is_released(blemonitor, mocker):
    from fhempy.lib.core import hci_claims

    monitor, _ = blemonitor
    monitor.config["hci_interface"] = [0]
    monitor.fhem_devices = {"aabbccddeeff": [mocker.Mock()]}
    restart = mocker.patch.object(monitor, "restart")
    hci_claims.claim(0, "matter")
    restart.assert_not_called()
    hci_claims.claim(1, "matter")
    hci_claims.release(1, "matter")
    restart.assert_not_called()
    hci_claims.release(0, "matter")
    restart.assert_called_once()
    hci_claims.remove_listener(monitor.hci_claim_changed)


def _parsing_dump(mocker):
    from fhempy.lib.ble_monitor import hcidump
    from fhempy.lib.ble_monitor.parser import FhempyBleParser

    dump = mocker.MagicMock(evt_cnt=0)
    dump.ble_parser = FhempyBleParser()
    dump._queue_report = lambda *args: hcidump.HCIdump._queue_report(dump, *args)
    dump._queue_sensor_msg = lambda *args: hcidump.HCIdump._queue_sensor_msg(
        dump, *args
    )
    dump.process_hci_events = lambda data, gateway_id="": (
        hcidump.HCIdump.process_hci_events(dump, data, gateway_id)
    )
    return dump


def _bleak_adv(name, manufacturer_data=None, service_data=None, rssi=-60):
    from types import SimpleNamespace

    return SimpleNamespace(
        local_name=name,
        manufacturer_data=manufacturer_data or {},
        service_data=service_data or {},
        service_uuids=[],
        rssi=rssi,
    )


def _delivered(dump):
    return [
        call.args[0] for call in dump.dataqueue_meas.sync_q.put_nowait.call_args_list
    ]


@pytest.mark.asyncio
async def test_advertisements_of_the_shared_scan_are_parsed(blemonitor, mocker):
    """ble_monitor doesn't scan itself, it parses what the shared BlueZ scan
    of core/ble_scanner receives."""
    from types import SimpleNamespace

    monitor, _ = blemonitor
    monitor.fhem_devices = {"aabbccddee11": [mocker.Mock()]}
    dump = _parsing_dump(mocker)
    monitor.dumpthread = dump
    device = SimpleNamespace(
        address="AA:BB:CC:DD:EE:11", details={"props": {"AddressType": "public"}}
    )
    # 21.5 C, 45 %, like the raw bytes C2 D7 00 2D 22 2C
    first = {0xD7C2: bytes([0x00, 0x2D, 0x22, 0x2C])}
    monitor.shared_advertisement(device, _bleak_adv("TP357 (EE11)", first))
    second = {0xDCC2: bytes([0x00, 0x32, 0x22, 0x2C])}
    # BlueZ merges the advertisements: the old entry is still there
    monitor.shared_advertisement(
        device, _bleak_adv("TP357 (EE11)", {**first, **second})
    )
    delivered = _delivered(dump)
    assert [msg["mac"] for msg in delivered] == ["AABBCCDDEE11"] * 2
    # only the changed entry was parsed the second time
    assert [msg["temperature"] for msg in delivered] == [21.5, 22.0]


@pytest.mark.asyncio
async def test_many_merged_entries_fit_into_one_hci_report(blemonitor, mocker):
    """BlueZ keeps every manufacturer id a ThermoPro ever sent: the rebuilt
    report must still fit into one HCI event and contain the newest value,
    also when the same advertisement is received again."""
    from types import SimpleNamespace

    from fhempy.lib.ble_monitor.blemonitor import hci_packet

    monitor, _ = blemonitor
    monitor.fhem_devices = {"aabbccddee11": [mocker.Mock()]}
    dump = _parsing_dump(mocker)
    packets = []
    parse = dump.process_hci_events

    def process(data, gateway_id=""):
        packets.append(data)
        parse(data, gateway_id)

    dump.process_hci_events = process
    monitor.dumpthread = dump
    device = SimpleNamespace(
        address="AA:BB:CC:DD:EE:11", details={"props": {"AddressType": "public"}}
    )
    # 40 old values, 8 bytes each in the report
    merged = {
        0xC2 | (temp << 8): bytes([0x00, 0x2D, 0x22, 0x2C])
        for temp in range(0x90, 0xB8)
    }
    monitor.shared_advertisement(device, _bleak_adv("TP357 (EE11)", merged))
    # 22.0 C
    newest = {0xDCC2: bytes([0x00, 0x32, 0x22, 0x2C])}
    merged.update(newest)
    monitor.shared_advertisement(device, _bleak_adv("TP357 (EE11)", merged))
    # received again, nothing changed
    monitor.shared_advertisement(device, _bleak_adv("TP357 (EE11)", merged))
    assert all(packet[2] == len(packet) - 3 <= 255 for packet in packets)
    assert [msg["temperature"] for msg in _delivered(dump)][-2:] == [22.0, 22.0]
    # too long data is cut to one HCI event
    assert len(hci_packet("AA:BB:CC:DD:EE:11", 0, -60, bytes(300))) == 258


def test_advertisement_data_is_rebuilt():
    asyncio.run(check_and_install_dependencies("ble_monitor"))
    from fhempy.lib.ble_monitor.blemonitor import advertisement_data

    adv = _bleak_adv(
        "LYWSD03MMC",
        manufacturer_data={0x0059: b"\x01\x02"},
        service_data={
            "0000fe95-0000-1000-8000-00805f9b34fb": b"\x30\x58",
            "12345678-1234-5678-1234-56789abcdef0": b"\x07",
        },
    )
    adv.service_uuids = ["0000181a-0000-1000-8000-00805f9b34fb"]
    raw = advertisement_data(adv)
    assert raw == (
        bytes([11, 0x09])
        + b"LYWSD03MMC"
        + bytes([3, 0x03, 0x1A, 0x18])
        + bytes([5, 0x16, 0x95, 0xFE, 0x30, 0x58])
        + bytes([18, 0x21])
        + bytes.fromhex("123456781234567812345678 9abcdef0".replace(" ", ""))[::-1]
        + b"\x07"
        + bytes([5, 0xFF, 0x59, 0x00, 0x01, 0x02])
    )
    # unchanged: everything again (presence of trackers)
    previous = (dict(adv.service_data), dict(adv.manufacturer_data))
    assert advertisement_data(adv, previous) == raw


@pytest.mark.asyncio
async def test_registers_at_the_shared_scan(blemonitor, mocker):
    from fhempy.lib.core import ble_scanner

    monitor, _ = blemonitor
    scanner = mocker.Mock()
    mocker.patch.object(ble_scanner.BleScanner, "get_instance", return_value=scanner)
    mocker.patch.object(ble_scanner.BleScanner, "instance", scanner)
    mocker.patch.object(monitor, "_check_shared", mocker.AsyncMock())
    monitor.fhem_devices = {"aabbccddeeff": [mocker.Mock()]}
    monitor.config["hci_interface"] = [0, 1]
    monitor.start()
    await asyncio.sleep(0)
    assert monitor._shared
    calls = scanner.add_callback.call_args_list
    assert calls[0].args == (monitor.shared_advertisement,)
    assert calls[0].kwargs == {"proxies": False}
    # hci1 is scanned as well
    assert calls[1].kwargs == {"proxies": False, "adapter": "hci1"}
    monitor.stop()
    await asyncio.sleep(0)
    assert not monitor._shared
    removed = [call.args[0] for call in scanner.remove_callback.call_args_list]
    assert monitor.shared_advertisement in removed
    assert len(removed) == 2


@pytest.mark.asyncio
async def test_own_hci_scan_only_on_request(blemonitor, mocker):
    monitor, _ = blemonitor
    device = mocker.Mock()
    device.scan.return_value = "hci"
    monitor.fhem_devices = {"aabbccddeeff": [device]}
    attach = mocker.patch.object(monitor, "_attach_shared")
    monitor.start()
    await asyncio.sleep(0)
    attach.assert_not_called()
    assert monitor.dumpthread.is_alive()
    assert not monitor._shared
