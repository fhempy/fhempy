import asyncio
import contextlib
import datetime
import json
import logging
import re

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.heating_control import controller, curve, discover, pumps, schedule
from fhempy.lib.heating_control import heating_control as hc

logger = logging.getLogger(__name__)

NAME = "heizung"


def devices():
    return {
        "th_living": {
            "TYPE": "MQTT2_DEVICE",
            "room": "Living",
            "sets": "desired-temp:slider,5,0.5,30,1 on off",
            "readings": {
                "measured-temp": "19.0",
                "desired-temp": "20.0",
                "valveposition": "40",
            },
        },
        "th_bath": {
            "TYPE": "CUL_HM",
            "room": "Bath",
            "sets": "desired-temp:slider,5,0.5,30,1",
            "readings": {"measured-temp": "22.5", "desired-temp": "22.0"},
        },
        "living_sensor": {
            "TYPE": "MQTT2_DEVICE",
            "room": "Living",
            "sets": "",
            "readings": {"temperature": "18.0", "humidity": "50"},
        },
        "boiler_room": {
            "TYPE": "MQTT2_DEVICE",
            "room": "Technik",
            "sets": "",
            "readings": {
                "temperature_0": "40.0",
                "temperature_1": "33.0",
                "temperature_2": "65.0",
            },
        },
        "mischer": {
            "TYPE": "MQTT2_DEVICE",
            "room": "Technik",
            "sets": "pct:slider,0,1,100 open close stop",
            "readings": {"pct": "30", "state": "stopped"},
        },
        "pumpe": {
            "TYPE": "MQTT2_DEVICE",
            "room": "Technik",
            "sets": "on off toggle",
            "readings": {"state": "off", "apower": "0"},
        },
        "wetter": {
            "TYPE": "fhempy",
            "FHEMPYTYPE": "openmeteo_weather",
            "room": "Wetter",
            "sets": "",
            "readings": {
                "cur_temperature": "2.0",
                **{
                    f"next_hours_{h:02d}_temperature": str(2.0 - h * 0.5)
                    for h in range(25)
                },
            },
        },
    }


class FakeFhem:
    def __init__(self):
        self.devices = devices()
        self.sets = []
        self.sent = []
        self.own = {}
        self.module = None

    async def send(self, hash, code):
        self.sent.append(code)
        if "my %r; my $re" in code:
            return json.dumps(self.devices)
        if "my @r; foreach" in code:
            return json.dumps([[name, ""] for name in sorted(self.devices)])
        match = re.search(
            r"my \$h = \$defs\{'([^']+)'\}; my %r; if \(\$h\) \{ my \$rd", code
        )
        if match:
            device = self.devices.get(match.group(1), {})
            return json.dumps(device.get("readings", {}))
        if "my $h = $defs{" in code:
            return json.dumps(self.own)
        match = re.search(r"CommandSet\(undef, '([^']+)'\)", code)
        if match:
            self.sets.append(match.group(1))
            return ""
        return ""

    def sets_of(self, device):
        return [s for s in self.sets if s.split(" ")[0] == device]


async def set_event_devices(hash, devices):
    return True


async def set_default_attrs(hash, attrs):
    return None


ATTRS = {
    "mixer": "mischer:pct",
    "pump": "pumpe:apower",
    "flow_sensor": "boiler_room:temperature_0",
    "return_sensor": "boiler_room:temperature_1",
    "supply_sensor": "boiler_room:temperature_2",
    "thermometers": "Living=living_sensor:temperature",
    "pump_model": "ALPHA2_25-60",
    "pump_setting": "PP2",
    "mixer_interval": "0",
}


# a device whose setup the user finished and started
STARTED = {"mode": "auto", "setup_done": "2026-11-01 10:00"}


async def define(mocker, own=None, attrs=None):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.javascript.clear()
    mock_fhem.attributes[NAME] = dict(ATTRS if attrs is None else attrs)
    fake = FakeFhem()
    fake.own = dict(STARTED if own is None else own)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake.send)
    mocker.patch("fhempy.lib.fhem.setEventDevices", set_event_devices)
    mocker.patch("fhempy.lib.fhem.setDefaultAttrs", set_default_attrs)
    mocker.patch.object(
        hc.heating_control, "history_path", lambda self: "/nonexistent/x.json"
    )
    mod = hc.heating_control(logger)
    fake.module = mod
    mod.fake = fake
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "heating_control"}, [], {})
    for _ in range(200):
        if mod._ready and mod.house:
            break
        await asyncio.sleep(0.01)
    return mod


@contextlib.asynccontextmanager
async def defined(mocker, own=None, attrs=None):
    mod = await define(mocker, own=own, attrs=attrs)
    try:
        yield mod
    finally:
        await mod.Undefine(mod.hash)
        mock_fhem.attributes.pop(NAME, None)


@pytest_asyncio.fixture
async def module(mocker):
    async with defined(mocker) as mod:
        yield mod


@pytest.fixture
def fhem_calls(mocker):
    """FHEM waits for pages and gets and answers no command of another
    device meanwhile: every call to FHEM there would block until its timeout"""
    calls = []

    async def no_fhem(*args, **kwargs):
        calls.append(args)
        return ""

    for function in (
        "sendCommandHash",
        "sendCommandName",
        "AttrVal",
        "ReadingsVal",
        "InternalVal",
    ):
        mocker.patch("fhempy.lib.fhem." + function, no_fhem)
    return calls


def readings():
    return mock_fhem.readings.get(NAME, {})


# --- pure logic ---


def test_pump_flow_rises_with_power():
    flows = [pumps.estimate_flow("ALPHA2 25-60", "PP2", w) for w in (4, 8, 12, 16, 20)]
    assert flows == sorted(flows)
    assert flows[0] > 0
    assert pumps.estimate_flow("ALPHA2 25-60", "PP2", 2) == pytest.approx(0.0)
    assert pumps.estimate_flow("unknown", "PP2", 10) is None
    assert pumps.normalize_setting("pp 3") == "PP3"
    assert pumps.normalize_setting("Stufe 2") == "II"
    assert pumps.normalize_setting("auto") == "AUTOADAPT"
    assert "AUTOADAPT" not in pumps.settings_of("ALPHA1 L 25-60")
    assert round(pumps.heat_watts(1000, 45, 35)) == 11440


def test_schedule_parse_format_and_switch():
    # the old form: comfort periods, the rest eco
    week = schedule.parse("Mo-Fr 06:00-08:00,16:30-22:00; Sa,So 07:30-23:00")
    assert schedule.to_text(week) == (
        "Mo-Fr 00:00 eco, 06:00 comfort, 08:00 eco, 16:30 comfort, 22:00 eco; "
        "Sa-Su 00:00 eco, 07:30 comfort, 23:00 eco"
    )
    monday = datetime.datetime(2026, 11, 23, 7, 0)
    assert schedule.value_at(week, monday) == "comfort"
    assert schedule.next_switch(week, monday) == monday.replace(hour=8)
    saturday_night = datetime.datetime(2026, 11, 28, 23, 30)
    assert schedule.next_switch(week, saturday_night) == datetime.datetime(
        2026, 11, 29, 7, 30
    )
    assert schedule.to_text(schedule.parse("Mo - ")) == "Mo-Su eco"
    with pytest.raises(ValueError):
        schedule.parse("Mo 08:00-07:00")
    with pytest.raises(ValueError):
        schedule.parse("Xy 08:00-09:00")
    with pytest.raises(ValueError):
        schedule.parse("Mo 06:00 45")
    with pytest.raises(ValueError):
        schedule.parse("Mo 06:00-08:00, 09:00 21")


def test_schedule_with_own_temperatures():
    week = schedule.parse(
        "Mo-Fr 00:00 17, 06:00 21,5, 08:00 18, 12:00 20, 16:00 21, 22:00 17; Sa-So 15"
    )
    assert schedule.to_text(week) == (
        "Mo-Fr 00:00 17, 06:00 21.5, 08:00 18, 12:00 20, 16:00 21, 22:00 17; Sa-Su 15"
    )
    monday = datetime.datetime(2026, 11, 23, 7, 0)
    assert schedule.value_at(week, monday) == pytest.approx(21.5)
    assert schedule.next_switch(week, monday) == monday.replace(hour=8)
    sunday = datetime.datetime(2026, 11, 29, 12, 0)
    assert schedule.value_at(week, sunday) == pytest.approx(15)
    assert schedule.next_switch(week, sunday) == datetime.datetime(2026, 11, 30, 0, 0)
    # a day without 00:00 keeps the last temperature of the day before
    week = schedule.parse("Mo-Su 06:00 21, 22:00 16")
    assert schedule.value_at(week, monday.replace(hour=3)) == pytest.approx(16)
    # always the same: no switch at all
    assert schedule.next_switch(schedule.parse("Mo-Su 15"), monday) is None


def test_curve_learns_per_outdoor_temperature():
    learned = curve.Learned()
    base = curve.flow_target(0, 21, {}, learned)
    learned.learn(0, 1.0, 2)
    assert learned.offset(0) == pytest.approx(1.0)
    assert curve.flow_target(0, 21, {}, learned) == pytest.approx(base + 1.0)
    # a mild day is not affected
    assert learned.offset(10) == pytest.approx(0)
    text = learned.to_text()
    again = curve.Learned()
    again.from_text(text)
    assert again.offset(0) == pytest.approx(1.0)
    assert curve.base_flow(-12, 20, 55, -12) == pytest.approx(55)
    assert curve.base_flow(25, 20) == 20


def test_mixer_feedforward_and_integral():
    mixer = controller.Mixer()
    # 50 % supply + 50 % return gives the target
    assert mixer.position(45, 45, 60, 30, 0) == pytest.approx(50.0)
    first = mixer.position(45, 40, 60, 30, 60)
    second = mixer.position(45, 40, 60, 30, 60)
    assert second > first > 50
    assert mixer.position(70, 40, 60, 30, 60) == pytest.approx(100.0)


def test_pump_decision():
    cold = [{"target": 21, "actual": 20, "valve": 50}]
    warm = [{"target": 21, "actual": 21.5, "valve": 0}]
    assert controller.pump_decision(False, cold, 5, {}, (30, 30)) == (True, "heating")
    assert controller.pump_decision(True, warm, 5, {}, (30, 30)) == (False, "warm")
    assert controller.pump_decision(True, warm, 20, {}, (30, 30))[0] is False
    assert controller.pump_decision(False, warm, 20, {}, (3, 30)) == (True, "frost")
    middle = [{"target": 21, "actual": 21.1, "valve": 10}]
    assert controller.pump_decision(True, middle, 5, {}, (30, 30))[0] is True
    assert controller.pump_decision(False, middle, 5, {}, (30, 30))[0] is False


def test_discover_finds_thermostats_and_suggests():
    infos = devices()
    found = discover.discover(infos)
    assert set(found["thermostats"]) == {"th_living", "th_bath"}
    assert found["thermostats"]["th_living"]["valve"] == "valveposition"
    assert found["weather"] == ["wetter"]
    assert ("mischer", "pct") in found["mixers"]
    assert ("pumpe", "apower") in found["pumps"]
    assert discover.suggest("mixer", found["mixers"], infos) == ("mischer", "pct")
    assert discover.suggest("pump", found["pumps"], infos) == ("pumpe", "apower")
    # names alone don't tell which sensor is the flow: no suggestion
    assert discover.suggest("flow", found["temperatures"], infos) is None
    assert discover.room_thermometers("Living", found, infos) == [
        ("living_sensor", "temperature")
    ]
    forecast = discover.forecast(infos["wetter"])
    assert forecast[0] == (0, 2.0)


def test_battery_and_reachability():
    assert discover.battery({"battery": "low"}) == (True, None)
    assert discover.battery({"battery": "ok"}) == (False, None)
    assert discover.battery({"battery": "15"}) == (True, 15.0)
    assert discover.battery({"battery": "80"}) == (False, 80.0)
    assert discover.battery({"battery_low": "false", "battery": "90"}) == (False, 90.0)
    assert discover.battery({"batteryLow": "true"}) == (True, None)
    # a voltage is no percent
    assert discover.battery({"battery": "2.9"}) == (False, None)
    assert discover.unreachable({"Activity": "dead"})
    assert not discover.unreachable({"Activity": "alive"})
    assert discover.unreachable({"availability": "offline"})
    assert discover.unreachable({"state": "UNREACHABLE"})
    assert not discover.unreachable({"state": "21.0"})


def test_parse_until():
    now = datetime.datetime(2026, 11, 23, 15, 0)
    assert hc.parse_until("7d", now) == datetime.datetime(2026, 11, 30)
    assert hc.parse_until("2026-12-27", now) == datetime.datetime(2026, 12, 27)
    assert hc.parse_until("2.1.", now) == datetime.datetime(2027, 1, 2)
    with pytest.raises(ValueError):
        hc.parse_until("soon", now)
    assert hc.room_key("Küche Süd") == "Kueche_Sued"


# --- the module ---


@pytest.mark.asyncio
async def test_module_controls_mixer_pump_and_thermostats(module):
    r = readings()
    assert set(module.rooms) == {"Bath", "Living"}
    living = module.rooms["Living"]
    # the room thermometer replaces the thermostat temperature
    assert living.actual == pytest.approx(18.0)
    assert r["room_Living_temperature"] == "18.0"
    fake = module.fake
    assert "pumpe on" in fake.sets
    mixer = fake.sets_of("mischer")
    assert mixer and mixer[-1].startswith("mischer pct ")
    target = float(r["flow_target"])
    assert 30 < target <= 60
    # thermostat at the radiator measures 1 K more than the room: setpoint + 1
    assert any(s.startswith("th_living desired-temp ") for s in fake.sets)
    assert r["outdoor_temp"] == "2.0"
    assert float(r["outdoor_effective"]) < 2.0


@pytest.mark.asyncio
async def test_events_drive_mixer_and_heat(module):
    fake = module.fake
    module.handle_event("pumpe", "apower", "15")
    module.handle_event("boiler_room", "temperature_0", "64.0")
    await asyncio.sleep(1.3)
    r = readings()
    assert float(r["flow_rate"]) > 0
    # flow 64, return 33 at the estimated flow
    assert float(r["heat_power"]) > 1000
    before = int(fake.sets_of("mischer")[-1].split()[-1])
    assert before < 100
    module.handle_event("boiler_room", "temperature_0", "30.0")
    await asyncio.sleep(1.3)
    after = int(fake.sets_of("mischer")[-1].split()[-1])
    assert after > before
    assert mock_fhem.javascript and "fhcLive" in mock_fhem.javascript[-1][1]


@pytest.mark.asyncio
async def test_set_commands(module):
    r = readings()
    assert await module.Set(module.hash, [NAME, "room_temp", "Bath", "23"], {}) == ""
    assert module.rooms["Bath"].state == "manual"
    assert module.rooms["Bath"].target == pytest.approx(23)
    assert await module.Set(module.hash, [NAME, "room_temp", "Bath", "auto"], {}) == ""
    assert module.rooms["Bath"].state != "manual"
    ret = await module.Set(
        module.hash,
        [NAME, "schedule", "Living", "Mo-Fr", "05:30-07:00;", "Sa-So", "-"],
        {},
    )
    assert ret == ""
    assert (
        r["room_Living_schedule"]
        == "Mo-Fr 00:00 eco, 05:30 comfort, 07:00 eco; Sa-Su eco"
    )
    assert "invalid" in await module.Set(
        module.hash, [NAME, "schedule", "Living", "Mo", "6-7"], {}
    )
    assert (
        await module.Set(module.hash, [NAME, "copy_schedule", "Living", "all"], {})
        == ""
    )
    assert schedule.to_text(module.rooms["Bath"].week) == schedule.to_text(
        module.rooms["Living"].week
    )
    # own temperatures per time
    ret = await module.Set(
        module.hash,
        [
            NAME,
            "schedule",
            "Bath",
            "Mo-So",
            "00:00",
            "16,",
            "06:00",
            "22.5,",
            "09:00",
            "16",
        ],
        {},
    )
    assert ret == ""
    assert r["room_Bath_schedule"] == "Mo-Su 00:00 16, 06:00 22.5, 09:00 16"
    view = module.rooms["Bath"].view()
    assert view["week"]["0"] == [[0, 16.0], [360, 22.5], [540, 16.0]]
    assert (
        await module.Set(module.hash, [NAME, "comfort_temp", "all", "21.5"], {}) == ""
    )
    assert module.rooms["Bath"].comfort == pytest.approx(21.5)
    assert "Unknown room" in await module.Set(
        module.hash, [NAME, "eco_temp", "x", "17"], {}
    )
    assert await module.Set(module.hash, [NAME, "vacation", "7d", "15"], {}) == ""
    assert module.rooms["Living"].state == "vacation"
    assert module.rooms["Living"].target == pytest.approx(15)
    assert r["vacation"].endswith(" 15")
    assert r["state"] == "vacation"
    assert await module.Set(module.hash, [NAME, "vacation_off"], {}) == ""
    assert r["vacation"] == "off"
    assert await module.Set(module.hash, [NAME, "mode", "off"], {}) == ""
    count = len(module.fake.sets)
    module.handle_event("boiler_room", "temperature_0", "20.0")
    await asyncio.sleep(1.3)
    assert len(module.fake.sets) == count
    assert r["state"] == "off"


@pytest.mark.asyncio
async def test_turning_the_thermostat_is_a_manual_override(module):
    module.handle_event("th_bath", "desired-temp", "24.0")
    await asyncio.sleep(1.3)
    bath = module.rooms["Bath"]
    assert bath.state == "manual"
    assert bath.target == pytest.approx(24.0)
    assert readings()["room_Bath_override"].startswith("24 ")


@pytest.mark.asyncio
async def test_saved_state_is_restored(mocker):
    async with defined(
        mocker,
        own={
            "room_Bath_schedule": "Mo-Su 00:00-24:00",
            "room_Bath_comfort": "23",
            "vacation": "off",
            "learned_curve": "0:+2.00:5.0",
            **STARTED,
        },
    ) as mod:
        assert mod.rooms["Bath"].target == pytest.approx(23)
        assert mod.rooms["Bath"].state == "comfort"
        assert mod.learned.offset(0) == pytest.approx(2.0)


@pytest.mark.asyncio
async def test_detail_page(module, fhem_calls):
    html = await module.FW_detailFn(module.hash, ["WEB", NAME, "", {}], {})
    assert fhem_calls == []
    assert "window.FHC_ROOM=false" in html
    assert 'id="fhc"' in html
    assert "window.FHC_DATA=" in html
    data = json.loads(html.split("window.FHC_DATA=", 1)[1].split(";</script>", 1)[0])
    assert data["name"] == NAME
    assert {r["key"] for r in data["rooms"]} == {"Bath", "Living"}
    assert data["setup"]["roles"]["mixer"]["suggestion"] == "mischer:pct"
    assert (
        data["setup"]["thermometers"]["Living"]["suggestion"]
        == "living_sensor:temperature"
    )
    assert len(data["curve"]["points"]) == 36
    assert "<script>" not in json.dumps(data)
    assert (
        data["setup"]["sensors"]["flow_sensor"]["value"] == "boiler_room:temperature_0"
    )
    devices = [d[0] for d in data["setup"]["devices"]]
    # devices with a temperature reading first
    assert devices.index("boiler_room") < devices.index("pumpe")


@pytest.mark.asyncio
async def test_get_readings_of_a_device(module):
    # any reading name, e.g. one device with all temperatures named freely
    module.fake.devices["boiler_room"]["readings"]["Vorlauf"] = "41.5"
    result = await module.Get(module.hash, [NAME, "readings", "boiler_room"], {})
    readings = dict(json.loads(result))
    assert readings["Vorlauf"] == "41.5"
    assert readings["temperature_0"] == "40.0"


@pytest.mark.asyncio
async def test_new_device_controls_nothing_until_started(mocker):
    # all devices are set, but the user didn't start the control yet
    async with defined(mocker, own={}) as mod:
        await asyncio.sleep(1.3)
        assert mod.mode == "setup"
        assert mod.fake.sets == []
        assert readings()["state"] == "setup: ready to start"
        mod.handle_event("boiler_room", "temperature_0", "20.0")
        mod.handle_event("th_bath", "desired-temp", "24.0")
        await asyncio.sleep(1.3)
        assert mod.fake.sets == []
        assert mod.rooms["Bath"].state != "manual"
        # the user starts the control
        assert await mod.Set(mod.hash, [NAME, "mode", "auto"], {}) == ""
        assert "pumpe on" in mod.fake.sets
        assert readings()["setup_done"]


@pytest.mark.asyncio
async def test_control_starts_only_with_finished_setup(mocker):
    attrs = {k: v for k, v in ATTRS.items() if k not in ("mixer", "pump")}
    # also a device saved before the setup step existed waits for its start
    async with defined(mocker, own={"mode": "auto"}, attrs=attrs) as mod:
        assert mod.mode == "setup"
        assert readings()["state"] == "setup: mixer,pump"
        ret = await mod.Set(mod.hash, [NAME, "mode", "auto"], {})
        assert "mixer" in ret and "pump" in ret
        assert mod.mode == "setup"
        assert mod.fake.sets == []


@pytest.mark.asyncio
async def test_own_rooms_for_thermostats(mocker):
    attrs = dict(ATTRS, thermostat_rooms="th_bath=Erdgeschoss,th_living=Erdgeschoss")
    async with defined(mocker, attrs=attrs) as mod:
        assert list(mod.rooms) == ["Erdgeschoss"]
        assert sorted(mod.rooms["Erdgeschoss"].thermostats) == ["th_bath", "th_living"]
        view = mod.setup_view()
        rooms = {t["name"]: (t["room"], t["fhem_room"]) for t in view["thermostats"]}
        assert rooms["th_bath"] == ("Erdgeschoss", "Bath")
        assert view["room_thermometers"]["Living"] == "living_sensor:temperature"


@pytest.mark.asyncio
async def test_page_of_its_own_room(module, fhem_calls):
    page = await module.Get(module.hash, [NAME, "page"], {})
    assert "window.FHC_ROOM=true" in page and 'id="fhc"' in page
    # no README and no FHEM command while FHEM waits for the page
    assert "fhempyReadme" not in page
    live = json.loads(await module.Get(module.hash, [NAME, "live"], {}))
    assert live["name"] == NAME and "history" not in live
    assert fhem_calls == []


@pytest.mark.asyncio
async def test_create_room(module):
    assert await module.Set(module.hash, [NAME, "create_room"], {}) == ""
    await asyncio.sleep(0.1)
    sent = [c for c in module.fake.sent if "roomIcons" in c]
    assert sent and "Heating" in sent[-1]
    assert readings()[".control_room"] == "Heating"


@pytest.mark.asyncio
async def test_room_shows_unreachable_thermostat_and_low_battery(module):
    module.handle_event("th_bath", "Activity", "dead")
    module.handle_event("living_sensor", "battery", "10")
    await asyncio.sleep(1.3)
    bath = module.rooms["Bath"].view()
    assert bath["alerts"] == [
        {"device": "th_bath", "label": "th_bath", "kind": "unreachable"}
    ]
    # its old temperature isn't used
    assert bath["actual"] is None
    living = module.rooms["Living"].view()
    assert living["alerts"] == [
        {
            "device": "living_sensor",
            "label": "living_sensor",
            "kind": "battery",
            "battery": 10.0,
        }
    ]
    r = readings()
    assert "th_bath: unreachable" in r["alerts"]
    assert "living_sensor: battery low" in r["alerts"]
    module.handle_event("th_bath", "Activity", "alive")
    await asyncio.sleep(1.3)
    assert module.rooms["Bath"].view()["alerts"] == []
