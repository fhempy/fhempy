"""Device name, alias and state of ble_monitor devices."""

import json
from types import SimpleNamespace

import pytest

from fhempy.lib.pkg_installer import check_and_install_dependencies

# Oral-B IO Series 7: running, normal pressure, gum care, sector 1 of 6
ORALB_DATA = bytes([0x06, 0x32, 0x6B, 3, 114, 0, 10, 2, 1, 0, 6])


def advertisement(manufacturer_data, local_name="", rssi=-60):
    return SimpleNamespace(
        local_name=local_name,
        service_uuids=[],
        service_data={},
        manufacturer_data=manufacturer_data,
        rssi=rssi,
    )


@pytest.mark.parametrize(
    "values, label, kind",
    [
        (
            {"type": "IO Series 7", "firmware": "Oral-B"},
            "Oral-B IO Series 7",
            "Toothbrush",
        ),
        (
            {"type": "LYWSD03MMC", "firmware": "Xiaomi (MiBeacon V3 encrypted)"},
            "Xiaomi LYWSD03MMC",
            "Thermometer",
        ),
        # model not in the upstream table: maker from the parser name
        ({"type": "Foo 1", "firmware": "Acme V2"}, "Acme Foo 1", ""),
        ({"firmware": "Oral-B"}, "", ""),
        ({}, "", ""),
    ],
)
def test_label_and_kind(values, label, kind):
    from fhempy.lib.ble_monitor import describe

    assert describe.label(values) == label
    assert describe.kind(values) == kind


@pytest.mark.parametrize(
    "values, state",
    [
        ({}, "waiting for data"),
        ({"state": "fhempy server offline"}, "waiting for data"),
        ({"toothbrush state": "running", "pressure": "normal"}, "running"),
        ({"toothbrush_state": "charging", "rssi": "-80"}, "charging"),
        ({"temperature": 21.5, "humidity": 45.0, "battery": 80}, "T: 21.5 H: 45"),
        # restored readings are text
        ({"temperature": "21.5", "humidity": "45"}, "T: 21.5 H: 45"),
        ({"weight": 70.2, "weight unit": "kg"}, "W: 70.2"),
        ({"opening": 1}, "open"),
        ({"motion": 0}, "no motion"),
        ({"button": "single press"}, "single press"),
        ({"rssi": -70, "firmware": "Acme"}, "active"),
    ],
)
def test_state(values, state):
    from fhempy.lib.ble_monitor import describe

    assert describe.state(values) == state


@pytest.mark.asyncio
async def test_describe_ble_recognizes_the_model_from_the_data():
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import discovery

    values = discovery.describe_ble(
        "AA:BB:CC:DD:EE:01", advertisement({220: ORALB_DATA}, "Some name")
    )
    assert values["label"] == "Oral-B IO Series 7"
    assert values["manufacturer"] == "Oral-B"
    assert values["model"] == "IO Series 7"
    assert values["kind"] == "Toothbrush"
    assert values["described"] is True


@pytest.mark.asyncio
async def test_describe_ble_falls_back_to_the_sent_name():
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import discovery

    # Oral-B company id, but not the data of a known model
    values = discovery.describe_ble(
        "AA:BB:CC:DD:EE:02", advertisement({220: b"\x01\x02"}, "Some brush")
    )
    assert values["label"] == "Some brush"
    assert values["described"] is False


@pytest.fixture
def fhem_calls(mocker):
    from fhempy.lib.ble_monitor import ble_monitor

    calls = {"readings": {}, "attr": [], "single": [], "bulk": []}

    async def send(hash, cmd):
        return json.dumps(calls["readings"])

    async def attr_val(name, attr, default):
        return calls.get("alias", default)

    async def command_attr(hash, cmd):
        calls["attr"].append(cmd)

    async def single(hash, reading, value, trigger):
        calls["single"].append((reading, value))

    async def bulk(hash, reading, value):
        calls["bulk"].append((reading, value))

    fhem = ble_monitor.fhem
    mocker.patch.object(fhem, "sendCommandHash", side_effect=send)
    mocker.patch.object(fhem, "AttrVal", side_effect=attr_val)
    mocker.patch.object(fhem, "CommandAttr", side_effect=command_attr)
    mocker.patch.object(fhem, "readingsSingleUpdateIfChanged", side_effect=single)
    mocker.patch.object(fhem, "readingsBulkUpdateIfChanged", side_effect=bulk)
    mocker.patch.object(fhem, "readingsBeginUpdate", mocker.AsyncMock())
    mocker.patch.object(fhem, "readingsEndUpdate", mocker.AsyncMock())
    return calls


def new_device():
    from fhempy.lib.ble_monitor import ble_monitor

    dev = ble_monitor.ble_monitor.__new__(ble_monitor.ble_monitor)
    dev.hash = {"NAME": "ble_dev"}
    dev._values = {}
    dev._alias_checked = False
    return dev


@pytest.mark.asyncio
async def test_state_and_alias_restored_after_restart(fhem_calls):
    """After a restart (or reconnect) nothing is received until the device
    sends again: state comes from the readings, not 'server offline'."""
    fhem_calls["readings"] = {
        "state": "fhempy server offline",
        "toothbrush_state": "charging",
        "type": "IO Series 7",
        "firmware": "Oral-B",
    }
    dev = new_device()
    await dev._restore_state()
    assert fhem_calls["single"] == [("state", "charging")]
    assert fhem_calls["attr"] == ["ble_dev alias Oral-B IO Series 7"]


@pytest.mark.asyncio
async def test_new_device_waits_for_data(fhem_calls):
    dev = new_device()
    await dev._restore_state()
    assert fhem_calls["single"] == [("state", "waiting for data")]
    assert fhem_calls["attr"] == []


@pytest.mark.asyncio
async def test_received_data_sets_state_and_alias_once(fhem_calls):
    dev = new_device()
    data = {
        "type": "IO Series 7",
        "firmware": "Oral-B",
        "toothbrush state": "running",
    }
    await dev.received_data(data)
    await dev.received_data({**data, "toothbrush state": "idle"})
    states = [value for reading, value in fhem_calls["bulk"] if reading == "state"]
    assert states == ["running", "idle"]
    assert fhem_calls["attr"] == ["ble_dev alias Oral-B IO Series 7"]


@pytest.mark.asyncio
async def test_alias_of_the_user_is_kept(fhem_calls):
    fhem_calls["alias"] = "My toothbrush"
    dev = new_device()
    await dev.received_data({"type": "IO Series 7", "firmware": "Oral-B"})
    assert fhem_calls["attr"] == []
