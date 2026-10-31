import asyncio
import json
import logging
import re
import time

import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.timeline import classify, story
from fhempy.lib.timeline.store import Store, day_of, day_start
from fhempy.lib.timeline.timeline import (
    FREQUENT_PER_HOUR,
    SKIP_EVENTS,
    matches,
    parse_rules,
    timeline,
    visible_rows,
)

logger = logging.getLogger(__name__)

INFOS = {
    "door": {"TYPE": "dummy", "room": "Hall", "alias": "Terrace door"},
    "hall": {"TYPE": "MQTT2_DEVICE", "room": "Hall", "alias": "Hallway"},
    "rgr": {"TYPE": "RESIDENTS", "room": "Residents"},
    "light1": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light sofa"},
    "light2": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light table"},
    "light3": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light corner"},
    "smoke": {"TYPE": "dummy", "room": "Hall"},
    "trv": {"TYPE": "MQTT2_DEVICE", "room": "Living", "alias": "Heizung Wohnzimmer"},
}


def test_classify():
    c = classify.classify
    hall = INFOS["hall"]
    assert c(INFOS["door"], "state", "open") == ("story", "security")
    assert c(hall, "contact", "open") == ("story", "security")
    assert c(hall, "occupancy", "true") == ("story", "presence")
    assert c(hall, "linkquality", "120") == ("tech", "devices")
    assert c(hall, "last_seen", "2026-10-26 10:00") == ("tech", "devices")
    assert c(hall, "battery", "87") == ("tech", "devices")
    trv = INFOS["trv"]
    assert c(trv, "desired-temp", "20") == ("story", "climate")
    # the echo of "set trv desired-temp 20" and settings of the thermostat
    assert c(trv, "desired-temp", "set desired-temp 20") == ("tech", "devices")
    assert c(trv, "child_lock", "UNLOCK") == ("tech", "devices")
    assert c(trv, "window", "CLOSED") == ("story", "climate")
    assert c(INFOS["door"], "window", "closed") == ("story", "security")
    assert c(hall, "battery", "low") == ("story", "devices")
    assert c(hall, "temperature", "21.5 °C") == ("trend", "climate")
    assert c(hall, "power", "1,5 W") == ("trend", "energy")
    assert c(hall, "desired-temp", "21") == ("story", "climate")
    # stateFormat summaries and pending commands
    assert c(hall, "state", "T: 21.5 H: 50") == ("tech", "devices")
    assert c(hall, "state", "set_on") == ("tech", "devices")
    assert c(INFOS["light1"], "state", "on") == ("story", "light")
    assert c(INFOS["rgr"], "state", "absent") == ("story", "presence")
    assert c({"TYPE": "notify", "room": "x"}, "state", "active")[0] == "tech"
    # helper dummies without room and devices in room hidden
    assert c({"TYPE": "dummy"}, "state", "on")[0] == "tech"
    assert c({"TYPE": "HUEDevice", "room": "hidden"}, "state", "on")[0] == "tech"
    # unknown text readings are details
    assert c(hall, "action", "single")[0] == "tech"
    generic = {"TYPE": "MQTT2_DEVICE", "room": "x", "genericDeviceType": "light"}
    assert classify.device_category(generic) == "light"


def test_on_change():
    attr = "event-on-change-reading"
    assert classify.on_change({attr: ".*"}, "temperature")
    assert classify.on_change({attr: "battery,temp.*:0.5"}, "temperature")
    assert not classify.on_change({attr: "battery"}, "temperature")
    assert not classify.on_change({attr: "(broken"}, "temperature")
    assert not classify.on_change({}, "temperature")


def test_skip_events_regexp():
    # FHEM uses the same regexp (Perl) for "device:reading: value"
    skip = re.compile(SKIP_EVENTS)
    assert skip.match("hall:linkquality: 120")
    assert skip.match("hall:RSSI: -70")
    assert skip.match("hall:last_seen: 2026-10-26T10:00:00")
    assert not skip.match("hall:state: on")
    assert not skip.match("hall:contact: open")
    # never matches across the reading name
    assert not skip.match("hall:state: T: 21 voltage: 3")


def test_hidden_rules_with_values():
    rules = parse_rules("Router:status:booting|reconnecting Sensor.*:* door:state")
    assert matches(rules, "Router", "status", "booting")
    assert matches(rules, "Router", "status", " Reconnecting ")
    assert not matches(rules, "Router", "status", "online")
    assert not matches(rules, "Router", "uptime", "booting")
    assert matches(rules, "Sensor1", "battery", "ok")
    assert matches(rules, "door", "state", "open")
    assert not matches(rules, "door2", "state", "open")
    # a value may contain ":", an invalid regexp is taken literally
    assert matches(parse_rules("clock:time:12:30"), "clock", "time", "12:30")
    assert matches(parse_rules("dev:r:a(b"), "dev", "r", "a(b")
    story_rows = [
        (1, "Router", "status", "booting", "devices"),
        (2, "Router", "status", "online", "devices"),
        (3, "Router", "status", "booting", "devices"),
    ]
    assert visible_rows(rules, story_rows) == [story_rows[1]]
    assert visible_rows([], story_rows) is story_rows
    # the rule the "only this value" buttons build
    assert matches(parse_rules("d:r:set\\sto\\s21\\.5\\x3b"), "d", "r", "set to 21.5;")


def at(seconds):
    return 1_790_000_000 + seconds


def build(rows, absences=(), now=None):
    return story.build_entries(
        [(at(s), d, r, v, c) for s, d, r, v, c in rows],
        INFOS,
        [(at(s), at(e) if e is not None else None) for s, e in absences],
        now or at(100_000),
    )


def test_curve_changed():
    # GPS coordinates moving in the 4th decimal, a reading staying the same
    assert not story.changed(47.5012, 47.5018)
    assert not story.changed(21.0, 21.0)
    assert not story.changed(1013.2, 1013.6)
    assert story.changed(20.4, 20.6)
    assert story.changed(1013, 1015)
    # small values still count
    assert story.changed(0.012, 0.018)
    assert story.changed(-0.5, 0.5)
    assert not story.changed(None, None)


def test_story_durations_and_bundling():
    entries = build(
        [
            (0, "door", "state", "open", "security"),
            (300, "door", "state", "closed", "security"),
            (400, "hall", "occupancy", "true", "presence"),
            (460, "hall", "occupancy", "false", "presence"),
            (600, "hall", "occupancy", "true", "presence"),
            (660, "hall", "occupancy", "false", "presence"),
            (900, "hall", "motion", "nomotion", "presence"),
        ]
    )
    assert [e["text"] for e in entries] == ["Terrace door open", "Hallway true"]
    door, hall = entries
    assert door["end"] == at(300) and door["count"] == 1 and not door["running"]
    assert hall["count"] == 2 and hall["end"] == at(660)
    assert not door["alert"]


def test_story_repeated_states():
    # devices which report their state again (e.g. Alexa) don't split entries
    entries = build(
        [
            (0, "light1", "state", "off", "light"),
            (0, "light1", "state", "on", "light"),
            (2760, "light1", "state", "on", "light"),
            (2760, "light1", "state", "off", "light"),
            (11_640, "light1", "state", "off", "light"),
            (11_640, "light1", "state", "on", "light"),
            (15_240, "light1", "state", "on", "light"),
        ],
        now=at(20_000),
    )
    assert [(e["value"], e["ts"], e["end"], e["running"]) for e in entries] == [
        ("off", at(0), None, False),
        ("on", at(0), at(2760), False),
        ("on", at(11_640), None, True),
    ]
    assert entries[1]["count"] == 1 and entries[2]["count"] == 1


def test_story_off_again_is_no_change():
    # off, a hidden or ignored "initializing" after a reconnect, off again
    entries = build(
        [
            (0, "light1", "state", "Off", "light"),
            (300, "light1", "state", "Off", "light"),
            (4000, "light1", "state", "Off", "light"),
            (90_000, "light1", "state", "off", "light"),
        ],
        now=at(100_000),
    )
    assert [(e["value"], e["count"], e["end"]) for e in entries] == [
        ("Off", 1, None)
    ]
    # a button pressed twice still is pressed twice
    entries = build(
        [
            (0, "hall", "action", "single", "devices"),
            (4000, "hall", "action", "single", "devices"),
        ],
        now=at(5000),
    )
    assert len(entries) == 2


def test_thermostat_story():
    entries = build(
        [
            (0, "trv", "desired-temp", "21", "climate"),
            (100, "trv", "desired-temp", "20", "climate"),
            # FHEM reports the same target again
            (5000, "trv", "desired-temp", "20", "climate"),
            (6000, "trv", "window", "CLOSED", "climate"),
        ]
    )
    assert [(e["text"], e["short"]) for e in entries] == [
        ("Heizung Wohnzimmer set to 21 °C", "Set to 21 °C"),
        ("Heizung Wohnzimmer set to 20 °C", "Set to 20 °C"),
        ("Heizung Wohnzimmer: window closed", "Window closed"),
    ]
    assert entries[1]["count"] == 1
    assert story.reading_label("boost_heating_countdown") == "boost heating countdown"
    assert story.reading_label("measured-temp") == "temperature"


def test_device_activity():
    rows = [
        (at(0), "door", "state", "open", "security"),
        (at(300), "door", "state", "closed", "security"),
        (at(5000), "door", "state", "open", "security"),
        (at(5060), "door", "state", "closed", "security"),
    ]
    (state,) = story.build_activity(rows, INFOS, at(9000))
    assert state["name"] == "" and state["what"] == "Open"
    assert state["count"] == 2 and state["total"] == 360 and state["longest"] == 300
    assert state["segments"][0] == [at(0), at(300), "Open"]
    assert state["current"] == {"text": "closed", "since": at(5060)}
    rows = [
        (at(6000), "hall", "action", "single", "devices"),
        (at(7000), "hall", "action", "double", "devices"),
    ]
    (action,) = story.build_activity(rows, INFOS, at(9000))
    assert action["name"] == "action" and action["count"] == 2
    assert [s[1:] for s in action["segments"]] == [
        [None, "Action single"],
        [None, "Action double"],
    ]
    assert action["current"] == {"text": "double", "since": at(7000)}


def test_device_activity_mixed_state():
    # a gate opener: relay pulses (on/off) and the contact (open/closed)
    # both as state, "ready" in between
    rows = [
        (at(0), "gate", "state", "on", "security"),
        (at(1), "gate", "state", "off", "security"),
        (at(20), "gate", "state", "open", "security"),
        (at(25), "gate", "state", "ready", "security"),
        (at(600), "gate", "state", "on", "security"),
        (at(601), "gate", "state", "off", "security"),
        (at(620), "gate", "state", "closed", "security"),
        (at(700), "gate", "state", "closed", "security"),
        (at(3000), "gate", "state", "open", "security"),
    ]
    opened, relay = story.build_activity(rows, INFOS, at(3600))
    assert opened["what"] == "Open"
    # how often and how long the door was open, not the relay
    assert opened["count"] == 2 and opened["total"] == 600 + 600
    assert opened["segments"] == [
        [at(20), at(620), "Open"],
        [at(3000), at(3600), "Open"],
    ]
    assert opened["current"] == {"text": "open", "since": at(3000)}
    # one second relay pulses are moments
    assert relay["what"] == "On" and relay["count"] == 2 and relay["total"] == 0
    assert [s[1] for s in relay["segments"]] == [None, None]
    assert relay["current"] == {"text": "off", "since": at(601)}
    # a command "close" ends "open", a closing event lost a day ago ends at it
    rows = [
        (at(0), "gate", "control", "open", "security"),
        (at(100), "gate", "control", "close", "security"),
        (at(200), "gate", "control", "open", "security"),
    ]
    (control,) = story.build_activity(rows, INFOS, at(200 + 2 * 86400))
    assert control["count"] == 2
    # the name of the reading is shown in front, "close" reads "closed"
    assert control["name"] == "control" and control["what"] == "Open"
    assert control["current"]["text"] == "open"
    assert story.value_text("control", "close") == "closed"
    # a doorbell only rings
    rows = [
        (at(0), "bell", "state", "ring", "security"),
        (at(60), "bell", "state", "ring", "security"),
    ]
    (bell,) = story.build_activity(rows, INFOS, at(100))
    assert bell["count"] == 2 and [s[1] for s in bell["segments"]] == [None, None]
    assert control["segments"][0][:2] == [at(0), at(100)]
    assert control["segments"][1][:2] == [at(200), None]


def test_thermostat_trends():
    start = day_start("2026-01-05")
    hour = int(start)

    def row(h, reading, value):
        return (
            hour + h * 3600,
            "trv",
            reading,
            "climate",
            value,
            value,
            value,
            1,
            value,
        )

    rows = [row(0, "temperature", 20.0), row(1, "temperature", 20.5)]
    rows += [row(5, "temperature", 21.0), row(2, "desired-temp", 22.0)]
    carry = [row(-30, "desired-temp", 21.0)]
    days = story.build_trends(rows, INFOS, carry, now=start + 86400)
    (trend,) = days["2026-01-05"]
    assert trend["reading"] == "temperature" and trend["unit"] == "°C"
    # hours without an event keep the last value
    assert trend["points"][:6] == [20.0, 20.5, 20.5, 20.5, 20.5, 21.0]
    assert trend["points"][23] == 21.0
    assert trend["target"]["points"][:3] == [21.0, 21.0, 22.0]
    assert trend["target"]["points"][23] == 22.0
    assert trend["target"]["name"] == "target temperature"
    # no new target the next day: the curve still shows the one set before
    rows = [row(24, "temperature", 19.0)]
    days = story.build_trends(rows, INFOS, carry + [row(2, "desired-temp", 22.0)])
    (trend,) = days["2026-01-06"]
    assert trend["target"]["points"][0] == 22.0

    trends = story.build_device_trends(
        rows, INFOS, carry + [row(5, "temperature", 21.0)], start, start + 2 * 86400
    )
    assert [t["reading"] for t in trends] == ["temperature"]
    assert trends[0]["points"][0] == [hour, 21.0]
    assert trends[0]["target"]["points"][0] == [hour, 21.0]
    assert story.curve_readings("desired-temp", {"desired-temp", "temperature"}) == [
        "temperature",
        "desired-temp",
    ]


def test_story_groups_scenes():
    entries = build(
        [
            (0, "light1", "state", "on", "light"),
            (0.5, "light2", "state", "on", "light"),
            (1, "light3", "state", "on", "light"),
            (60, "door", "state", "open", "security"),
        ],
        now=at(120),
    )
    assert entries[0]["text"] == "3 lights on"
    assert [c["text"] for c in entries[0]["children"]] == [
        "Light sofa on",
        "Light table on",
        "Light corner on",
    ]
    assert entries[1]["text"] == "Terrace door open"
    assert entries[1]["running"]


def test_story_alerts_while_away():
    absences = [(0, 10_000)]
    entries = build(
        [
            (0, "rgr", "state", "absent", "presence"),
            (500, "door", "state", "open", "security"),
            (600, "door", "state", "closed", "security"),
            # 5 minutes before somebody is detected at home: no alert
            (9_700, "hall", "motion", "motion", "presence"),
            (20_000, "smoke", "smoke", "smoke", "security"),
        ],
        absences,
    )
    texts = {e["text"]: e["alert"] for e in entries}
    assert texts == {
        "Everybody left": False,
        "Terrace door open": True,
        "Hallway motion": False,
        "smoke: smoke smoke": True,
    }


def test_store(tmp_path):
    store = Store(str(tmp_path / "timeline" / "t.db"))
    store.open()
    now = time.time()
    hour = int(now // 3600 * 3600)
    store.add(
        [(now, "door", "state", "open", "story", "security")],
        {(hour, "hall", "temperature"): ["climate", 20.0, 22.0, 42.0, 2, 22.0]},
        {day_of(now): 3},
    )
    store.add(
        [(now - 30 * 86400, "hall", "temperature", "1", "trend", "climate")],
        {(hour, "hall", "temperature"): ["climate", 19.0, 21.0, 20.0, 1, 20.0]},
        {day_of(now): 2},
    )
    assert store.story(now - 10, now + 10) == [
        (now, "door", "state", "open", "security")
    ]
    assert store.hourly(hour, hour + 1) == [
        (hour, "hall", "temperature", "climate", 19.0, 22.0, 62.0, 3, 20.0)
    ]
    # the value a reading still has after its last event
    assert store.values_before(hour + 7200) == store.hourly(hour, hour + 1)
    assert store.values_before(hour + 7200, "door") == []
    # looked up per device and reading: the same rows as for all devices
    store.add(
        [],
        {
            (hour - 3600, "hall", "humidity"): ["climate", 50.0, 50.0, 50.0, 1, 50.0],
            (hour - 7200, "hall", "humidity"): ["climate", 40.0, 40.0, 40.0, 1, 40.0],
            (hour - 10800, "cellar", "temperature"): ["climate", 9.0, 9.0, 9.0, 1, 9.0],
        },
        {},
    )
    assert sorted(store.values_before(hour + 7200, {"hall", "cellar"})) == sorted(
        store.values_before(hour + 7200)
    )
    assert [row[2] for row in store.values_before(hour, {"hall"})] == ["humidity"]
    assert store.values_before(hour - 7200, {"hall"}) == []
    assert store.first_ts() == now - 30 * 86400
    assert store.hidden(day_of(now), day_of(now)) == {day_of(now): 5}
    store.absence_changed(now - 100_000, True)
    store.absence_changed(now - 100_000 + 50, True)
    store.absence_changed(now - 10, False)
    assert store.long_absences(3600) == [(now - 100_000, now - 10)]
    assert store.absences(now - 1000, now) == [(now - 100_000, now - 10)]
    store.add_frequent("hall", "action")
    assert store.frequent() == {("hall", "action")}
    store.cleanup(14, 730)
    assert store.first_ts() == now
    store.add(
        [
            (now, "router", "status", "booting", "story", "devices"),
            (now, "router", "status", "online", "story", "devices"),
        ],
        {},
        {},
    )
    # a rule with a value deletes only these events, not the curves
    skip = re.compile("^router:status: (?:booting)$|^hall:temperature:")
    assert store.prune(skip) == (1, 1)
    assert [row[3] for row in store.story(now - 10, now + 10)] == ["open", "online"]
    assert store.hourly(hour, hour + 1) == []
    assert store.prune(skip) == (0, 0)
    store.close()


class FakeFhem:
    def __init__(self):
        self.recorder = None
        self.residents_state = "absent"

    async def send(self, hash, cmd):
        if "fhempy_setEventRecorder" in cmd:
            self.recorder = cmd
            return "ok"
        if "to_json" in cmd:
            return json.dumps(INFOS)
        return ""


@pytest.mark.asyncio
async def test_timeline_module(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("tl", None)
    mock_fhem.attributes["tl"] = {}
    mock_fhem.readings["rgr"] = {"state": "absent"}
    fake = FakeFhem()
    mocker.patch.object(fhem, "sendCommandHash", fake.send)
    mocker.patch.object(fhem, "CommandAttr", mock_fhem.CommandAttr)
    mocker.patch.object(fhem, "CommandDeleteAttr", mocker.AsyncMock())
    mock_fhem.command_attr.clear()

    module = timeline(logger)
    hash = {"NAME": "tl", "FHEMPYTYPE": "timeline"}
    assert await module.Define(hash, ["tl", "fhempy", "timeline"], {}) is None
    for _ in range(100):
        if mock_fhem.readings["tl"].get("state") == "recording":
            break
        await asyncio.sleep(0.05)
    assert mock_fhem.readings["tl"]["state"] == "recording"
    assert "'tl', 1, " in fake.recorder
    assert (tmp_path / ".fhempy" / "timeline" / "tl.db").exists()

    now = time.time()
    batch = [
        [f"{now - 60:.3f}", "door", "state: open"],
        [f"{now - 50:.3f}", "hall", "temperature: 21.5"],
        [f"{now - 40:.3f}", "hall", "action: single"],
        [f"{now - 30:.3f}", "global", "ATTR door alias Front door"],
    ]
    await fhem.dispatch_recorded_events("tl", [batch, {"hall": 7}])
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    today = data["days"][0]
    assert today["day"] == data["today"]
    assert [e["text"] for e in today["entries"]] == ["Terrace door open"]
    # RESIDENTS was absent at the start
    assert len(module.store.absences(now - 100, now)) == 1
    # temperature, action and the 7 events FHEM only counted
    assert today["hidden"] == 9
    # the curves are loaded separately per day
    assert "trends" not in today
    curves = json.loads(await module.Get(hash, ["tl", "trends", data["today"]], {}))
    assert curves["day"] == data["today"]
    assert curves["trends"][0]["text"] == "Hallway: temperature"
    assert curves["trends"][0]["label"] == "Hallway"
    assert "error" in json.loads(await module.Get(hash, ["tl", "trends", "x"], {}))

    details = json.loads(await module.Get(hash, ["tl", "details", data["today"]], {}))
    assert [d["text"] for d in details] == [
        "Hallway: action single",
        "Hallway: temperature 21.5 °C",
    ]

    # "Hide from story" and "Always show"
    assert await module.Set(hash, ["tl", "hide", "door:state"], {}) is None
    assert "tl hidden door:state" in mock_fhem.command_attr
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    assert data["days"][0]["entries"] == []
    assert await module.Set(hash, ["tl", "show", "hall:action"], {}) is None
    assert "tl always_show hall:action" in mock_fhem.command_attr
    await fhem.dispatch_recorded_events(
        "tl", [[[f"{time.time():.3f}", "hall", "action: double"]], {}]
    )
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    assert [e["text"] for e in data["days"][0]["entries"]] == ["Hallway: action double"]

    # "Stop recording" adds the reading to skip_events
    assert await module.Set(hash, ["tl", "ignore", "hall:link-quality"], {}) is None
    assert "tl skip_events ^hall:link\\-quality:" in mock_fhem.command_attr
    assert await module.Set(hash, ["tl", "ignore", "smoke:*"], {}) is None
    assert "tl skip_events ^hall:link\\-quality:|^smoke:" in mock_fhem.command_attr
    mock_fhem.command_attr.clear()
    assert await module.Set(hash, ["tl", "ignore", "smoke:*"], {}) is None
    assert mock_fhem.command_attr == []
    skip = re.compile(f"{SKIP_EVENTS}|{module._attr_skip_events}")
    assert skip.match("hall:link-quality: 80")
    assert not skip.match("hall:link-quality2: 80")
    assert skip.match("smoke:state: alarm")
    assert not skip.match("smoker:state: alarm")

    # history of one device for the popup
    history = json.loads(await module.Get(hash, ["tl", "device", "hall"], {}))
    assert history["text"] == "Hallway"
    # action single came before "Always show"
    assert [e["text"] for e in history["entries"]] == ["Hallway: action double"]
    assert [t["reading"] for t in history["trends"]] == ["temperature"]
    assert history["trends"][0]["points"][0][1] == 21.5
    assert history["to"] - history["from"] == 7 * 86400
    history = json.loads(await module.Get(hash, ["tl", "device", "hall", "99"], {}))
    assert history["to"] - history["from"] == 31 * 86400
    assert json.loads(await module.Get(hash, ["tl", "device", "nodevice"], {})) == {
        "error": "Unknown device nodevice"
    }

    # one curve for the curve popup
    curve = json.loads(await module.Get(hash, ["tl", "curve", "hall:temperature"], {}))
    assert curve["label"] == "Hallway" and curve["category"] == "climate"
    assert [p[1:] for p in curve["points"]] == [[21.5, 21.5, 21.5]]
    assert curve["min"] == curve["max"] == curve["avg"] == 21.5
    assert curve["day"] == curve["today"]
    assert curve["to"] - curve["from"] in (82800, 86400, 90000)
    week = json.loads(
        await module.Get(
            hash, ["tl", "curve", "hall:temperature", "2000-01-07", "7"], {}
        )
    )
    assert week["points"] == [] and week["avg"] is None and week["day"] == "2000-01-07"
    assert json.loads(await module.Get(hash, ["tl", "curve", "hall:a;b"], {})) == {
        "error": "Use device:reading of an existing device"
    }

    # thermostat: target temperature as story and as curve with the temperature
    t = time.time()
    await fhem.dispatch_recorded_events(
        "tl",
        [
            [
                [f"{t:.3f}", "trv", "desired-temp: set desired-temp 21"],
                [f"{t:.3f}", "trv", "desired-temp: 21"],
                [f"{t:.3f}", "trv", "temperature: 20.5"],
            ],
            {},
        ],
    )
    history = json.loads(await module.Get(hash, ["tl", "device", "trv"], {}))
    assert [e["short"] for e in history["entries"]] == ["Set to 21 °C"]
    (trend,) = history["trends"]
    assert trend["reading"] == "temperature" and trend["target"]["max"] == 21
    curve = json.loads(await module.Get(hash, ["tl", "curve", "trv:desired-temp"], {}))
    assert curve["reading"] == "temperature" and curve["name"] == "temperature"
    assert curve["target"]["points"][-1][1] == 21

    # events only on change, curves which changed
    trend = json.loads(await module.Get(hash, ["tl", "trends", data["today"]], {}))[
        "trends"
    ][0]
    assert trend["changed"] is False and trend["on_change"] is False
    mock_fhem.attributes["hall"] = {"event-on-change-reading": "battery"}
    assert await module.Set(hash, ["tl", "on_change", "hall:temperature"], {}) is None
    assert "hall event-on-change-reading battery,temperature" in mock_fhem.command_attr
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    curves = json.loads(await module.Get(hash, ["tl", "trends", data["today"]], {}))
    assert curves["trends"][0]["on_change"] is True
    assert data["days"][0]["entries"][0]["on_change"] is False
    assert await module.Set(hash, ["tl", "on_change", "hall:action"], {}) is None
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    assert data["days"][0]["entries"][0]["on_change"] is True
    mock_fhem.command_attr.clear()
    mock_fhem.attributes["hall"] = {"event-on-change-reading": "battery,temperature"}
    assert await module.Set(hash, ["tl", "on_change", "hall:temperature"], {}) is None
    assert mock_fhem.command_attr == []
    assert await module.Set(hash, ["tl", "on_change", "hall:a;b"], {}) == (
        "Use device:reading of an existing device"
    )
    assert await module.Set(hash, ["tl", "on_change", "nodevice:state"], {}) == (
        "Use device:reading of an existing device"
    )

    # "Hide from story" and "Stop recording" for one value only
    assert await module.Set(hash, ["tl", "auto", "door:state"], {}) is None
    assert await module.Set(hash, ["tl", "hide", "door:state:open"], {}) is None
    assert module._attr_hidden == "door:state:open"
    await fhem.dispatch_recorded_events(
        "tl", [[[f"{time.time():.3f}", "door", "state: closed"]], {}]
    )
    history = json.loads(await module.Get(hash, ["tl", "device", "door"], {}))
    assert [e["text"] for e in history["entries"]] == ["Terrace door closed"]
    assert await module.Set(hash, ["tl", "ignore", "door:state:open"], {}) is None
    assert module._attr_skip_events.endswith("|^door:state: (?:open)$")
    skip = re.compile(module._attr_skip_events)
    assert skip.search("door:state: open") and not skip.search("door:state: opened")
    assert await module.Set(hash, ["tl", "ignore", "door:state:a("], {}) == (
        "Invalid regexp a("
    )
    message = await module.Set(hash, ["tl", "prune"], {})
    assert message.startswith("Deleted 1 events")
    assert mock_fhem.readings["tl"]["last_prune"] == message
    rows = module.store.story(0, time.time() + 10)
    assert ("door", "state", "open") not in [row[1:4] for row in rows]

    mock_fhem.attributes.pop("hall")
    assert await module.Get(hash, ["tl", "entries", "26.10.2026"], {}) == (
        "Use YYYY-MM-DD for from and to"
    )
    await module.Undefine(hash)
    assert "'tl', 0, " in fake.recorder


@pytest.mark.asyncio
async def test_frequent_readings_are_hidden(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.attributes["tl2"] = {}
    fake = FakeFhem()
    mocker.patch.object(fhem, "sendCommandHash", fake.send)
    module = timeline(logger)
    hash = {"NAME": "tl2", "FHEMPYTYPE": "timeline"}
    await module.Define(hash, ["tl2", "fhempy", "timeline"], {})
    for _ in range(100):
        if mock_fhem.readings["tl2"].get("state") == "recording":
            break
        await asyncio.sleep(0.05)
    now = time.time()
    batch = [
        [f"{now - 1000 + i:.3f}", "light1", "state: " + ("on" if i % 2 else "off")]
        for i in range(70)
    ]
    await fhem.dispatch_recorded_events("tl2", [batch, {}])
    assert ("light1", "state") in module._frequent
    data = json.loads(await module.Get(hash, ["tl2", "entries"], {}))
    # stored as story (bundled) until the limit was reached
    assert max(e["count"] for e in data["days"][0]["entries"]) > 1
    assert data["days"][0]["hidden"] == 70 - FREQUENT_PER_HOUR
    await module.Undefine(hash)
