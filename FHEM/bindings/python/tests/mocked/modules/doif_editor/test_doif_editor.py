import asyncio
import shutil
import subprocess
import datetime
import json
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.doif_editor import evaluate, index, parser, values
from fhempy.lib.doif_editor.doif_editor import (
    decode,
    doif_editor,
    encode,
    parse_sets,
)
from fhempy.lib.doif_editor.history import History
from fhempy.lib.timeline.store import Store

logger = logging.getLogger(__name__)

# definitions in the style of the DOIF commandref, each must come back exactly
DEFINITIONS = [
    '([lamp] eq "on") (set light on) DOELSE (set light off)',
    "([08:00]) (set heating on)\nDOELSEIF ([22:00]) (set heating off)",
    '([06:00-22:00|8] and [motion] eq "motion") (set light on)',
    "## morning\n([07:00|Mo Di Mi Do Fr]) (set blind up)\n"
    "DOELSEIF ## evening\n([{sunset(1800)}]) (set blind down)",
    '([sensor:temperature] > 25 and [?window] eq "closed") (set fan on) DOELSE',
    '([+00:15]) ({Log 3, "every 15 minutes"})',
    '(["^door:open"]) (set push message door, set siren on)',
    '([button:"short"]) (set light toggle)',
    '([#"^window":state:$_ eq "open"] > 0) (set heating eco)'
    " DOELSE (set heating comfort)",
    "([[$SELF:alarm_time]]) (set radio on)",
    "([08:00-20:00,+01:00]) (set pump on-for-timer 300)",
    '([dummy] eq "1")\n  (set a on)\n  (set a off)\nDOELSE\n  (set b on)',
    '(([a] eq "on" or [b] eq "on") and [c:brightness] < 50) (set d on)',
    "(!([07:00-08:00])) (set e off)",
    '{if ([lamp] eq "on") {fhem_set("light on")}}\n'
    'evening {if ([20:00]) {fhem_set("blind down")}}',
    "([lamp]) (setreading $SELF counter 1)",
]


@pytest.mark.parametrize("definition", DEFINITIONS)
def test_round_trip(definition):
    rule = parser.parse_rule(definition, {})
    assert rule["error"] == ""
    assert parser.generate_definition(rule) == definition


def test_parse_leaves():
    tree = parser.parse_condition("[07:30] and [?sensor:temperature:d] >= 20")
    assert tree["items"][0] == {"t": "time", "at": {"k": "clock", "v": "07:30"}}
    leaf = tree["items"][1]
    assert leaf["check"] and leaf["dev"] == "sensor" and leaf["fmt"] == "d"
    assert leaf["op"] == ">=" and leaf["value"] == {"k": "number", "v": "20"}
    assert parser.parse_condition("[08:00-22:00|8]")["days"] == "8"
    assert parser.parse_condition("[+00:15]")["t"] == "every"
    sun = parser.parse_condition("[{sunrise(-600)}]")["at"]
    assert sun["k"] == "sun" and sun["event"] == "sunrise" and sun["offset"] == -600
    # unknown expressions stay code
    assert parser.parse_condition("ReadingsNum('x','y',0) > 3")["t"] == "code"


def test_edit_keeps_untouched_parts():
    definition = (
        '## Licht an\n([motion] eq "on"   and [?lux] < 30) (set light on)\n'
        "DOELSE (set light off)"
    )
    attrs = {"wait": "0:120", "cmdpause": "60", "room": "Hall"}
    rule = parser.parse_rule(definition, attrs)
    assert rule["cases"][1]["blocks"][0]["wait"] == "120"
    assert rule["cases"][0]["attrs"] == {"cmdpause": "60"}
    # change only the command of the second case
    rule["cases"][1]["blocks"][0]["cmds"][0]["cmd"] = "dim"
    rule["cases"][1]["blocks"][0]["cmds"][0]["args"] = "10"
    text = parser.generate_definition(rule)
    assert text.startswith('## Licht an\n([motion] eq "on"   and [?lux] < 30)')
    assert text.endswith("(set light dim 10)")
    generated = parser.generate_attrs(rule)
    assert generated["wait"] == "0:120"
    assert generated["cmdpause"] == "60"
    assert generated["room"] == "Hall"


def test_new_rule_and_wait_steps():
    rule = {
        "mode": "fhem",
        "cases": [
            {
                "kind": "if",
                "comment": "Morgens",
                "cond": {
                    "t": "and",
                    "items": [
                        {"t": "time", "at": {"k": "clock", "v": "06:00"}},
                        {
                            "t": "cmp",
                            "check": True,
                            "dev": "regeln",
                            "reading": "Regen",
                            "fmt": "",
                            "op": "<",
                            "value": {"k": "number", "v": "1"},
                        },
                    ],
                },
                "blocks": [
                    {"cmds": [{"t": "set", "dev": "valve", "cmd": "on", "args": ""}]},
                    {
                        "cmds": [
                            {"t": "set", "dev": "valve", "cmd": "off", "args": ""}
                        ],
                        "wait": "[regeln:Dauer_s]",
                    },
                ],
            },
            {"kind": "else", "cond": None, "blocks": [{"cmds": []}], "comment": ""},
        ],
        "attrs": {"do": "always"},
        "tail": "",
    }
    text = parser.generate_definition(rule)
    assert text == (
        "## Morgens\n([06:00] and [?regeln:Regen] < 1) (set valve on) (set valve off)"
        "\nDOELSE ()"
    )
    attrs = parser.generate_attrs(rule)
    assert attrs["wait"] == "0,[regeln:Dauer_s]"
    assert attrs["do"] == "always"
    assert attrs["cmdpause"] is None
    again = parser.parse_rule(text, {k: v for k, v in attrs.items() if v})
    assert again["cases"][0]["blocks"][1]["wait"] == "[regeln:Dauer_s]"


def test_reads_and_writes():
    rule = parser.parse_rule(DEFINITIONS[4], {})
    triggers, checks, writes, _ = parser.reads_and_writes(rule)
    assert triggers == {("sensor", "temperature")}
    assert checks == {("window", "state")}
    assert writes == {"fan": {"on"}}
    perl = parser.parse_rule(DEFINITIONS[14], {})
    _, _, writes, times = parser.reads_and_writes(perl)
    assert writes == {"light": {"on"}, "blind": {"down"}}
    assert times


def test_evaluate():
    now = datetime.datetime(2026, 11, 2, 7, 30)
    ctx = evaluate.Context(
        {("lamp", "state"): (0, "on"), ("sensor", "temperature"): (0, "21.5 °C")}, now
    )
    assert evaluate.eval_tree(ctx, parser.parse_condition('[lamp] eq "on"')) is True
    assert (
        evaluate.eval_tree(ctx, parser.parse_condition("[sensor:temperature] > 25"))
        is False
    )
    assert evaluate.eval_tree(ctx, parser.parse_condition("[07:00-08:00]")) is True
    assert evaluate.eval_tree(ctx, parser.parse_condition("[07:00-08:00|7]")) is False
    rule = parser.parse_rule(DEFINITIONS[0], {})
    assert evaluate.which_case(ctx, rule) == 0
    ctx.values[("lamp", "state")] = (0, "off")
    assert evaluate.which_case(ctx, rule) == 1
    assert evaluate.which_case(ctx, rule, last_case=1) is None


def test_simulate():
    rule = parser.parse_rule(DEFINITIONS[0], {})
    start = datetime.datetime(2026, 11, 1).timestamp()
    events = [
        (start + 10, "lamp", "state", "on"),
        (start + 20, "lamp", "state", "on"),
        (start + 30, "lamp", "state", "off"),
    ]
    executions, unknown = evaluate.simulate(
        rule, events, {}, start, start + 3600, {"latitude": 48.2, "longitude": 16.4}
    )
    assert [e["case"] for e in executions] == [0, 1]
    assert unknown == 0
    timer = parser.parse_rule(DEFINITIONS[1], {})
    executions, _ = evaluate.simulate(
        timer, [], {}, start, start + 2 * 86400, {"latitude": 48.2, "longitude": 16.4}
    )
    assert [e["case"] for e in executions] == [0, 1, 0, 1]


def test_values_receipt():
    value = {
        "title": "Bewässerung",
        "unit": "min",
        "min": "5",
        "max": "40",
        "round": "1",
        "rows": [
            {"op": "start", "amount": {"k": "fixed", "v": 20}},
            {
                "op": "mul",
                "amount": {
                    "k": "source",
                    "source": {
                        "k": "reading",
                        "dev": "weather",
                        "reading": "condition",
                    },
                    "map": {
                        "mode": "values",
                        "values": [
                            {"value": "sunny", "v": 100},
                            {"value": "cloudy", "v": 80},
                        ],
                        "else": 90,
                    },
                },
            },
            {
                "op": "add",
                "amount": {
                    "k": "source",
                    "source": {
                        "k": "reading",
                        "dev": "weather",
                        "reading": "temperature",
                    },
                    "map": {
                        "mode": "steps",
                        "steps": [
                            {"from": "", "to": "15", "v": -5},
                            {"from": "28", "to": "", "v": 10},
                        ],
                        "else": 0,
                    },
                },
            },
            {
                "op": "add",
                "amount": {
                    "k": "source",
                    "source": {
                        "k": "history",
                        "dev": "rain",
                        "reading": "amount",
                        "func": "sum",
                        "hours": 48,
                    },
                    "map": {"mode": "per", "v": -2},
                },
            },
        ],
    }
    readings = {("weather", "condition"): "cloudy", ("weather", "temperature"): "30.2"}
    ctx = {
        "reading": lambda d, r: readings.get((d, r)),
        "now": datetime.datetime(2026, 7, 1, 6, 0),
        "history": lambda d, r, f, h: 1.5,
        "input": lambda name: None,
        "value": lambda name: None,
    }
    result, steps = values.compute(value, ctx)
    # 20 × 80 % = 16, + 10 = 26, - 2 × 1.5 = 23
    assert result == 23
    assert [step["result"] for step in steps] == [20, 16, 26, 23]
    assert values.readings_of(value, result) == {
        "Bewaesserung": "23",
        "Bewaesserung_s": "1380",
    }
    readings[("weather", "condition")] = "sunny"
    readings[("weather", "temperature")] = "40"
    assert values.compute(value, ctx)[0] == 27
    del readings[("weather", "temperature")]
    assert values.compute(value, ctx)[0] is None
    linear = {"mode": "linear", "points": [[10, 0], [30, 100]]}
    assert values.map_value(linear, "20") == 50
    assert values.map_value(linear, "40") == 100
    assert values._in_step(23, {"from": "22", "to": "6"})


def doif(name, definition, attrs=None, readings=None, times=None):
    return {
        "NAME": name,
        "TYPE": "DOIF",
        "DEF": definition,
        "attrs": attrs or {},
        "readings": readings or {},
        "times": times or {},
    }


def test_index_health_and_box():
    rules = [
        doif(
            "di_on",
            '([motion] eq "on") (set light on)',
            times={"cmd": "2026-11-02 08:00:00"},
        ),
        doif(
            "di_off",
            "([22:00]) (set light off)",
            readings={"timer_01_c01": "02.11.2026 22:00:00"},
            times={"cmd": "2026-11-01 22:00:00"},
        ),
        doif("di_a", '([x] eq "on") (set y on) DOELSE (set y off)'),
        doif("di_b", '([y] eq "on") (set x off) DOELSE (set x on)'),
        doif("di_c", '([missing_dev] eq "on") (set light on) DOELSE (set light off)'),
        {
            "NAME": "n_door",
            "TYPE": "notify",
            "DEF": "door:open set siren on",
            "attrs": {},
        },
        {
            "NAME": "n_door2",
            "TYPE": "notify",
            "DEF": "door:open set siren on",
            "attrs": {},
        },
    ]
    devices = [
        {"NAME": n, "TYPE": "dummy", "attrs": {"room": "Hall"}}
        for n in ("motion", "light", "x", "y", "door", "siren")
    ]
    idx = index.Index(
        rules, devices, editor="regeln", values=[{"name": "Unused", "title": "Unused"}]
    )
    now = datetime.datetime(2026, 11, 2, 12, 0).timestamp()
    findings = idx.health(now=now)
    kinds = {(f["kind"], tuple(f["rules"])) for f in findings}
    assert ("conflict", ("di_c", "di_off", "di_on")) in kinds
    assert ("loop", ("di_a", "di_b")) in kinds
    assert ("missing", ("di_c",)) in kinds
    assert ("duplicate", ("n_door", "n_door2")) in kinds
    assert any(f["kind"] == "unused_value" for f in findings)
    box = idx.device_box("light")
    assert [c["rule"] for c in box["controls"]] == ["di_c", "di_off", "di_on"]
    assert box["conflict"]
    assert [u["rule"] for u in idx.device_box("door")["uses"]] == ["n_door", "n_door2"]
    graph = idx.graph("device", "light")
    assert {n["id"] for n in graph["nodes"]} >= {
        "rule:di_on",
        "dev:light",
        "dev:motion",
    }
    plan = idx.plan(datetime.datetime(2026, 11, 2, 12, 0))
    assert plan[0]["rule"] == "di_off" and plan[0]["future"]
    assert plan[0]["writes"] == ["set light off"]


def test_precedence():
    loser = parser.parse_rule(
        '([motion] eq "on") (set light on) DOELSE (set light off)', {}
    )
    winner = parser.parse_rule("([22:00]) (set light off)", {})
    numbers = index.cases_writing(winner, "light")
    assert numbers == [1]
    assert index.add_precedence(loser, "di_night", numbers, "light") == 1
    assert parser.generate_definition(loser) == (
        '([motion] eq "on" and [?di_night:cmd_nr] != 1) (set light on)'
        " DOELSE (set light off)"
    )


def test_history(tmp_path):
    path = str(tmp_path / "tl.db")
    store = Store(path)
    store.open()
    now = datetime.datetime.now().timestamp()
    hour = int(now // 3600 * 3600)
    store.add(
        [
            (now - 7200, "lamp", "state", "on", "story", "light"),
            (now - 3600, "lamp", "state", "off", "story", "light"),
        ],
        {(hour - 3600, "rain", "amount"): ["climate", 1.0, 2.0, 3.0, 2, "2"]},
        {},
    )
    store.close()
    history = History(path)
    assert history.available()
    rows = history.events([("lamp", "state")], now - 86400, now)
    assert [row[3] for row in rows] == ["on", "off"]
    before = history.values_before([("lamp", "state")], now - 3000)
    assert before[("lamp", "state")][1] == "off"
    assert history.aggregate("lamp", "state", "count", 24, now) == 2
    assert history.aggregate("rain", "amount", "sum", 24, now) == 3.0
    assert 3500 < history.aggregate("lamp", "state", "since", 24, now) < 3700
    history.close()


def test_helpers():
    assert parse_sets("on:noArg off:noArg dim:slider,0,1,100 ?") == [
        {"cmd": "on", "options": "noArg"},
        {"cmd": "off", "options": "noArg"},
        {"cmd": "dim", "options": "slider,0,1,100"},
    ]
    token = encode({"a": "ä?>"})
    assert "=" not in token and "+" not in token and "/" not in token
    assert decode(token) == {"a": "ä?>"}
    with pytest.raises(ValueError):
        decode("not base64!")
    assert values.reading_name("Kochzeit Eier") == "Kochzeit_Eier"
    assert values.reading_name("Bewässerung") == "Bewaesserung"


class FakeFhem:
    def __init__(self):
        self.commands = []
        self.rules = {
            "di_light": doif(
                "di_light",
                '([motion] eq "on") (set light on) DOELSE (set light off)',
                attrs={"wait": "0:120", "room": "Hall"},
                readings={"cmd": "cmd_2", "state": "cmd_2"},
            )
        }

    async def send(self, hash, cmd):
        self.commands.append(cmd)
        if "my %t = map" in cmd:
            return json.dumps(
                {
                    k: v
                    for k, v in self.rules.items()
                    if f"'{k}'" in cmd or "keys %defs" in cmd
                }
            )
        if "getAllSets" in cmd or "'webCmd'" in cmd:
            return json.dumps(
                {
                    "motion": {
                        "NAME": "motion",
                        "TYPE": "dummy",
                        "readings": {"state": "off"},
                        "attrs": {},
                    },
                    "light": {
                        "NAME": "light",
                        "TYPE": "dummy",
                        "readings": {"state": "off"},
                        "attrs": {},
                        "sets": "on off",
                    },
                }
            )
        if "my @r" in cmd:
            return json.dumps([["motion", "state", "on", 0]])
        if "-temporary" in cmd:
            return "ok"
        if "FHEMPYTYPE} // '') eq 'timeline'" in cmd:
            return ""
        if "while (defined($defs{$n}))" in cmd:
            return "di_new"
        return ""


def b64(data):
    return encode(data)


@pytest.mark.asyncio
async def test_module(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("regeln", None)
    mock_fhem.attributes["regeln"] = {}
    fake = FakeFhem()
    mocker.patch.object(fhem, "sendCommandHash", fake.send)
    mocker.patch.object(fhem, "setEventDevices", mocker.AsyncMock(return_value=True))
    mocker.patch.object(fhem, "CommandDeleteReading", mocker.AsyncMock())
    module = doif_editor(logger)
    hash = {"NAME": "regeln", "FHEMPYTYPE": "doif_editor"}
    assert await module.Define(hash, ["regeln", "fhempy", "doif_editor"], {}) is None
    for _ in range(100):
        if mock_fhem.readings["regeln"].get("state") == "ready":
            break
        await asyncio.sleep(0.05)
    assert mock_fhem.readings["regeln"]["state"] == "ready"
    assert any(
        "FWEXT" in c and "doif_editor_inject.js?editor=regeln" in c
        for c in fake.commands
    )

    overview = json.loads(await module.get_overview(hash, {}))
    assert [r["name"] for r in overview["rules"]] == ["di_light"]
    rule = json.loads(await module.get_rule(hash, {"rule": "di_light"}))
    model = rule["model"]
    assert model["cases"][1]["blocks"][0]["wait"] == "120"

    now = json.loads(await module.get_now(hash, {"data": b64({"model": model})}))
    assert now["case"] == 0
    assert now["last_case"] == 1

    model["cases"][0]["blocks"][0]["cmds"][0]["args"] = "60"
    model["cases"][0]["blocks"][0]["cmds"][0]["cmd"] = "dim"
    result = json.loads(
        await module.set_save(
            hash,
            {
                "data": b64(
                    {"name": "di_light", "type": "DOIF", "model": model, "rid": "r1"}
                )
            },
        )
    )
    reply = json.loads(await module.get_reply(hash, {"rid": "r1"}))
    assert json.loads(reply["reply"]) == result
    assert json.loads(await module.get_reply(hash, {"rid": "r1"})) == {"pending": True}
    assert result == {"ok": True, "name": "di_light"}
    save = [c for c in fake.commands if "-temporary" in c][-1]
    assert "(set light dim 60) DOELSE (set light off)" in save
    # attributes are only written when they differ, room is not managed
    assert "if (AttrVal('di_light', 'wait', '\\x00') ne '0:120')" in save
    assert "di_light room" not in save
    if shutil.which("perl"):
        # the generated Perl must compile
        check = subprocess.run(
            ["perl", "-c", "-e", save], capture_output=True, text=True
        )
        assert check.returncode == 0, check.stderr
    versions = json.loads(await module.get_versions(hash, {"rule": "di_light"}))[
        "versions"
    ]
    assert [v["note"] for v in versions] == ["before", "editor"]

    value = {
        "title": "Kochzeit",
        "unit": "min",
        "rows": [
            {"op": "start", "amount": {"k": "fixed", "v": 8}},
            {
                "op": "add",
                "amount": {
                    "k": "source",
                    "source": {"k": "input", "name": "Extra"},
                    "map": {"mode": "direct"},
                },
            },
        ],
    }
    assert json.loads(
        await module.set_input_save(
            hash,
            {
                "data": b64(
                    {"input": {"title": "Extra", "kind": "number", "default": "2"}}
                )
            },
        )
    )["ok"]
    assert json.loads(
        await module.set_value_save(hash, {"data": b64({"value": value})})
    )["ok"]
    assert mock_fhem.readings["regeln"]["Kochzeit"] == "10"
    assert mock_fhem.readings["regeln"]["Kochzeit_s"] == "600"
    await module.set_input(hash, {"name": "Extra", "value": "4"})
    assert mock_fhem.readings["regeln"]["Kochzeit"] == "12"
    preview = json.loads(
        await module.get_value_preview(hash, {"data": b64({"value": value})})
    )
    assert preview["text"] == "12"
    stored = json.loads(
        (tmp_path / ".fhempy" / "doif_editor" / "regeln.json").read_text()
    )
    assert stored["values"][0]["name"] == "Kochzeit"

    simulate = json.loads(
        await module.get_simulate(hash, {"data": b64({"model": model})})
    )
    assert simulate["error"] == "no_history"
    await module.Undefine(hash)
    if shutil.which("perl"):
        for cmd in set(fake.commands):
            check = subprocess.run(
                ["perl", "-c", "-e", cmd], capture_output=True, text=True
            )
            assert check.returncode == 0, cmd + "\n" + check.stderr
