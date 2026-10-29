import asyncio
import json
import logging
import re
import time

import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.timeline import classify, story
from fhempy.lib.timeline.store import Store, day_of
from fhempy.lib.timeline.timeline import FREQUENT_PER_HOUR, SKIP_EVENTS, timeline

logger = logging.getLogger(__name__)

INFOS = {
    "door": {"TYPE": "dummy", "room": "Hall", "alias": "Terrace door"},
    "hall": {"TYPE": "MQTT2_DEVICE", "room": "Hall", "alias": "Hallway"},
    "rgr": {"TYPE": "RESIDENTS", "room": "Residents"},
    "light1": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light sofa"},
    "light2": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light table"},
    "light3": {"TYPE": "HUEDevice", "room": "Living", "alias": "Light corner"},
    "smoke": {"TYPE": "dummy", "room": "Hall"},
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


def at(seconds):
    return 1_790_000_000 + seconds


def build(rows, absences=(), now=None):
    return story.build_entries(
        [(at(s), d, r, v, c) for s, d, r, v, c in rows],
        INFOS,
        [(at(s), at(e) if e is not None else None) for s, e in absences],
        now or at(100_000),
    )


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
        {(hour, "hall", "temperature"): ["climate", 20.0, 22.0, 42.0, 2]},
        {day_of(now): 3},
    )
    store.add(
        [(now - 30 * 86400, "hall", "temperature", "1", "trend", "climate")],
        {(hour, "hall", "temperature"): ["climate", 19.0, 21.0, 20.0, 1]},
        {day_of(now): 2},
    )
    assert store.story(now - 10, now + 10) == [
        (now, "door", "state", "open", "security")
    ]
    assert store.hourly(hour, hour + 1) == [
        (hour, "hall", "temperature", "climate", 19.0, 22.0, 62.0, 3)
    ]
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
    assert today["trends"][0]["text"] == "Hallway: temperature"
    assert today["trends"][0]["label"] == "Hallway"

    details = json.loads(await module.Get(hash, ["tl", "details", data["today"]], {}))
    assert [d["text"] for d in details] == [
        "Hallway: action single",
        "Hallway: temperature 21.5",
    ]

    # "Show less" and "Always show"
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

    # "Ignore completely" adds the reading to skip_events
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

    # events only on change, curves which changed
    trend = data["days"][0]["trends"][0]
    assert trend["changed"] is False and trend["on_change"] is False
    mock_fhem.attributes["hall"] = {"event-on-change-reading": "battery"}
    assert await module.Set(hash, ["tl", "on_change", "hall:temperature"], {}) is None
    assert "hall event-on-change-reading battery,temperature" in mock_fhem.command_attr
    data = json.loads(await module.Get(hash, ["tl", "entries"], {}))
    assert data["days"][0]["trends"][0]["on_change"] is True
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
