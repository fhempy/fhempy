import asyncio
import calendar
import json
import logging
import math
import random
import time

import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.heating_advisor import (
    advisor,
    discover,
    heating_advisor as module_file,
    model,
    planner,
    render,
    weather,
)
from fhempy.lib.heating_advisor.heating_advisor import heating_advisor, parse_time
from fhempy.lib.heating_advisor.store import Store

logger = logging.getLogger(__name__)
LAT, LON = 48.2, 16.4
SLOT = advisor.SLOT

TRUE = dict(
    model.default_params(),
    cm_ratio=25.0,
    r_ia=1 / 10,
    r_im=1 / 250,
    r_ma=1 / 18,
    g_s=2.0,
    p_heat=2500.0,
)


def synthetic_inputs(start, days, seed=3):
    rng = random.Random(seed)
    rows = []
    for k in range(int(days * 96)):
        ts = start + k * SLOT
        hour = (ts / 3600) % 24
        ta = 2 + 5 * math.sin((hour - 9) / 24 * 2 * math.pi) + 3 * math.sin(k / 480)
        direct, diffuse = weather.clear_sky(ts, LAT, LON)
        cloud = 0.3 + 0.7 * math.sin(k / 288) ** 2
        rows.append(
            {
                "ts": ts,
                "ta": ta,
                "sun": weather.sun_at(ts, LAT, LON, direct * cloud, diffuse),
                "present": 1.0 if hour > 17 or hour < 8 else 0.0,
                "window": 1.0 if k % 96 == 30 and rng.random() < 0.5 else 0.0,
                "direct": direct * cloud,
                "diffuse": diffuse,
            }
        )
    return rows


def setpoints_of(inputs):
    points = []
    for k, row in enumerate(inputs):
        hour = (row["ts"] / 3600) % 24
        off = hour >= 22 or hour < 6 or (k // 96) % 7 == 3
        points.append(None if off else 21.0)
    return points


def test_discretization_matches_euler():
    params = model.default_params()
    d = model.Discrete(params, 0.15)
    x = (20.0, 18.0)
    qa, qm = d.heat(1000.0)
    exact = d.step(x, 0.0, qa, qm)
    # Euler with tiny steps
    cm = model.CI * params["cm_ratio"]
    ti, tm = x
    n = 9000
    h = model.DT / n
    for _ in range(n):
        dti = ((tm - ti) / params["r_im"] + (0.0 - ti) / params["r_ia"] + qa) / model.CI
        dtm = ((ti - tm) / params["r_im"] + (0.0 - tm) / params["r_ma"] + qm) / cm
        ti, tm = ti + dti * h, tm + dtm * h
    assert exact[0] == pytest.approx(ti, abs=1e-3)
    assert exact[1] == pytest.approx(tm, abs=1e-3)


def test_operative_temperature():
    # warm air with cold walls feels much colder
    assert model.operative_temp(23.0, 15.0, 0.5) == pytest.approx(21.0)
    assert model.surface_temp(23.0, 15.0, 0.5) == pytest.approx(19.0)
    assert model.operative_temp(21.0, 21.0) == pytest.approx(21.0)


@pytest.mark.asyncio
async def test_fit_recovers_synthetic_house():
    inputs = synthetic_inputs(1790000000, 21)
    rows = model.simulate_house(TRUE, inputs, 0.15, (20.0, 19.0), setpoints_of(inputs))
    result = await asyncio.to_thread(advisor.fit_room, rows, 0.15)
    params = result["params"]
    for name in ("cm_ratio", "r_ia", "r_im", "r_ma", "p_heat", "g_s"):
        assert params[name] == pytest.approx(TRUE[name], rel=0.3), name
    assert result["rmse"] < 0.3
    assert advisor.state_of(result) == "good"
    air_h, mass_h = advisor.time_constants_h(params)
    assert air_h < 5 < 50 < mass_h
    # surface share is learned from a wall sensor
    assert result["surface_k"] == pytest.approx(model.SURFACE_K, abs=0.1)


def test_planner_floor_heating_pays_off_later():
    results = {}
    for emitter, heating in (("radiator", "gas"), ("floor", "heatpump")):
        room = planner.Room(
            "r", TRUE, model.HEAT_TO_MASS[emitter], 0.35, None, 21.0, emitter
        )
        room.x0 = planner.steady_state(room, 0.0)
        res = planner.savings_by_duration(
            [room],
            lambda n: planner.constant_inputs(0.0, n),
            None,
            12.0,
            heating,
            1.0,
        )
        results[emitter] = planner.worth_from(res, 5, 0.5)
        # savings grow with the absence
        pcts = [r["saving_pct"] for r in res]
        assert pcts[-1] > pcts[0]
    assert results["radiator"] is not None
    assert results["floor"] is None or results["floor"] > results["radiator"]


def test_reheat_takes_longer_for_walls():
    room = planner.Room("r", TRUE, 0.15, 0.35, None, 21.0, "radiator")
    air, felt = planner.reheat_hours(room, 0.0, 15.0, "gas")
    assert air is not None and felt is not None
    assert felt > air
    air2, felt2 = planner.reheat_hours(room, 0.0, 15.0, "gas", basis="air")
    assert felt2 == pytest.approx(air2, abs=0.3)


def test_heat_pump_efficiency():
    assert planner.efficiency("heatpump", 0, 1.0) < planner.efficiency(
        "heatpump", 0, 0.3
    )
    assert planner.efficiency("heatpump", 10, 0.5) > planner.efficiency(
        "heatpump", -10, 0.5
    )
    assert planner.efficiency("gas", 0, 1.0) == 0.92


def test_sun_position():
    # Vienna, midsummer noon: high in the south
    ts = calendar.timegm((2026, 6, 21, 10, 56, 0))
    elevation, azimuth = weather.sun_position(ts, LAT, LON)
    assert 60 < elevation < 70
    assert 160 < azimuth < 200
    east, south, west = weather.facade_sun(300, 100, 30, 120)
    assert east > south > west


def test_parse_time():
    now = 1790000000.0
    assert parse_time("36h", now) == now + 36 * 3600
    assert parse_time("2d", now) == now + 2 * 86400
    assert parse_time("1,5", now) == now + 1.5 * 3600
    assert parse_time("07:30", now) > now
    with pytest.raises(ValueError):
        parse_time("tomorrow", now)


INFOS = {
    "wz_temp": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Living",
        "alias": "Living temperature",
        "readings": {"temperature": "21.3", "humidity": "45"},
    },
    "wz_trv": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Living,Heating",
        "alias": "Living radiator",
        "readings": {
            "local_temperature": "22.0",
            "current_heating_setpoint": "21",
            "pi_heating_demand": "30",
        },
    },
    "wz_window": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Living",
        "alias": "Window living",
        "readings": {"contact": "true"},
    },
    "bath_fbh": {
        "TYPE": "HMCCU",
        "room": "Bath",
        "alias": "Bath FBH",
        "readings": {"measured-temp": "23.5", "desired-temp": "23"},
    },
    "outdoor": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Garden",
        "alias": "Aussentemperatur",
        "readings": {"temperature": "3.1"},
    },
    "fridge": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Kitchen",
        "alias": "Fridge",
        "readings": {"temperature": "5"},
    },
    "rgr": {"TYPE": "RESIDENTS", "room": "Residents", "readings": {"state": "home"}},
    "heatpump": {
        "TYPE": "MQTT2_DEVICE",
        "room": "Cellar",
        "alias": "Wärmepumpe",
        "readings": {"state": "on"},
    },
    "nowhere": {"TYPE": "dummy", "readings": {"temperature": "20"}},
}


def test_discover():
    found = discover.discover(INFOS)
    assert set(found["rooms"]) == {"Living", "Bath"}
    living = found["rooms"]["Living"]
    assert living["sensors"] == [("wz_temp", "temperature")]
    assert living["thermostats"][0]["target"] == "current_heating_setpoint"
    assert living["thermostats"][0]["valve"] == "pi_heating_demand"
    assert living["contacts"] == [("wz_window", "contact")]
    assert found["outdoor"] == ("outdoor", "temperature")
    assert found["residents"] == ["rgr"]
    assert found["heating_type"] == "heatpump"
    assert found["floor_rooms"] == {"Bath"}
    values = {d: i["readings"] for d, i in INFOS.items()}
    sample = discover.sample_room(living, values)
    # the room sensor is used, not the thermostat on the radiator
    assert sample["y"] == 21.3
    assert sample["setp"] == 21
    assert sample["valve"] == 0.3
    # zigbee2mqtt: contact true = closed
    assert sample["window"] == 0.0
    assert discover.present(values, ["rgr"]) == 1.0
    assert discover.present({"rgr": {"state": "absent"}}, ["rgr"]) == 0.0
    assert "wz_trv" in discover.devices_of(found)


def test_heating_inferred_from_setpoint():
    assert advisor.heating_of({"valve": 0.4}, None) == 0.4
    assert advisor.heating_of({"setp": 5, "y": 18}, None) == 0.0
    assert advisor.heating_of({"setp": 21, "y": 22}, None) == 0.0
    assert advisor.heating_of({"setp": 21, "y": 19}, None) == 1.0
    assert advisor.heating_of({"setp": 21, "y": 20.8}, None) is None
    assert advisor.heating_of({"y": 20}, 18.0) == 0.0


def test_render():
    view = {
        "headline": "Setback worth it from 6 h of absence",
        "subline": "Heating: gas",
        "explain": ["<b>x</b>"],
        "curve": {"hours": 48, "felt": [20, 19.5], "air": [20, 19], "wall": [20, 19.8]},
        "savings": [
            {"hours": 2, "saving_pct": 1, "saving_kwh": 0.1},
            {"hours": 24, "saving_pct": 20, "saving_kwh": 8},
        ],
        "threshold_pct": 5,
        "threshold_kwh": 0.5,
        "rooms": [{"name": "Living", "air": 21, "wall": 19, "felt": 20}],
        "devices": [("Living", ["wz_temp"])],
    }
    page = render.page(view)
    assert "<svg" in page and "polyline" in page
    assert "&lt;b&gt;x&lt;/b&gt;" in page
    assert "starting" in render.page(None)


class FakeFhem:
    def __init__(self, values):
        self.values = values
        self.sets = []

    async def send(self, hash, cmd):
        if "readings => \\%rd" in cmd:
            infos = {
                name: dict(info, readings=self.values.get(name, {}))
                for name, info in INFOS.items()
            }
            return json.dumps(infos)
        if "my %w = (" in cmd:
            return json.dumps(self.values)
        if cmd.startswith("CommandSet"):
            self.sets.append(cmd)
            return ""
        return ""


def weather_rows(start, hours):
    rows = []
    for h in range(hours):
        ts = start + h * 3600
        hour = (ts / 3600) % 24
        direct, diffuse = weather.clear_sky(ts, LAT, LON)
        rows.append(
            (ts, 2 + 5 * math.sin((hour - 9) / 24 * 2 * math.pi), direct * 0.5, diffuse)
        )
    return rows


@pytest.mark.asyncio
async def test_module(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("ha", None)
    mock_fhem.attributes["ha"] = {}
    mock_fhem.attributes["global"] = {"latitude": str(LAT), "longitude": str(LON)}
    values = {d: dict(i["readings"]) for d, i in INFOS.items()}
    fake = FakeFhem(values)
    mocker.patch.object(fhem, "sendCommandHash", fake.send)
    now = time.time()
    first_hour = int(now // 3600 * 3600) - 14 * 86400

    async def fake_fetch(lat, lon, past_days=2, forecast_days=7):
        return weather_rows(first_hour, 14 * 24 + 8 * 24)

    mocker.patch.object(weather, "fetch", fake_fetch)
    # learning is tested above, keep the module test fast
    original_fit = advisor.fit_room
    mocker.patch.object(
        advisor,
        "fit_room",
        lambda rows, htm, old=None: original_fit(rows, htm, old, max_evals=150),
    )

    ha = heating_advisor(logger)
    hash = {"NAME": "ha", "FHEMPYTYPE": "heating_advisor"}
    assert await ha.Define(hash, ["ha", "fhempy", "heating_advisor"], {}) is None
    for _ in range(100):
        if mock_fhem.readings["ha"].get("state") not in (None, "starting"):
            break
        await asyncio.sleep(0.05)
    assert mock_fhem.readings["ha"]["rooms"] == "Bath,Living"
    assert mock_fhem.readings["ha"]["outdoor_source"] == "outdoor:temperature"
    assert mock_fhem.readings["ha"]["heating_type"] == "heatpump"
    assert (tmp_path / ".fhempy" / "heating_advisor" / "ha.db").exists()

    # 10 days of simulated measurements of both rooms
    start = advisor.slot_of(now) - 10 * 86400
    inputs = synthetic_inputs(start, 10)
    rows = model.simulate_house(TRUE, inputs, 0.15, (20.0, 19.0), setpoints_of(inputs))
    grid = [
        {
            "ts": i["ts"],
            "y": r["y"],
            "setp": 21.0 if s else 5.0,
            "valve": r["h"],
            "window": i["window"],
            "detected": 0,
            "surface": None,
            "present": i["present"],
            "ta": i["ta"],
        }
        for i, r, s in zip(inputs, rows, setpoints_of(inputs))
    ]
    for room in ("Living", "Bath"):
        ha.store.add_grid(room, grid)
    await ha.fit_all()
    readings = mock_fhem.readings["ha"]
    assert readings["model_state"] in ("ready", "good", "learning")
    assert "Living_heat_loss_W_per_K" in readings
    assert "setback_worth_from_h" in readings
    assert "forecast_off_24h" in readings
    assert readings["state"].startswith("setback")
    page = await ha.FW_detailFn(hash, ["WEB", "ha", "", {}], {})
    assert "<svg" in page and "Living" in page

    # live sampling: a new slot updates the felt temperature
    await ha.sample(now)
    await ha.sample(now + SLOT)
    assert "Living_operative_temp" in mock_fhem.readings["ha"]
    assert "Living_wall_temp" in mock_fhem.readings["ha"]

    # forecast as JSON
    data = json.loads(await ha.Get(hash, ["ha", "forecast", "6"], {}))
    assert len(data["Living"]) == 6

    # absence with apply sets the thermostats back and heats up in time
    assert await ha.Set(hash, ["ha", "absence", "72h", "apply"], {}) == ""
    assert mock_fhem.readings["ha"]["plan_state"] == "set back"
    plan = ha._plan
    living = plan["rooms"]["Living"]
    assert plan["worth"] and living["worth"]
    assert mock_fhem.readings["ha"]["plan_worth"] == "yes"
    assert any("wz_trv current_heating_setpoint 12" in s for s in fake.sets)
    fake.sets.clear()
    await ha.run_plan(living["reheat"] + 1)
    assert mock_fhem.readings["ha"]["plan_state"] == "heating up"
    assert any(f"{living['normal'] + living['boost']:g}" in s for s in fake.sets)
    await ha.Set(hash, ["ha", "cancel"], {})
    assert mock_fhem.readings["ha"]["plan_state"] == "none"
    assert "unknown time" in await ha.Set(hash, ["ha", "absence", "soon"], {})
    await ha.Undefine(hash)


def test_store(tmp_path):
    store = Store(str(tmp_path / "x.db"))
    store.open()
    store.add_grid("Living", [{"ts": 900, "y": 20.0}, {"ts": 1800, "y": 20.5}])
    assert [r["y"] for r in store.grid("Living", 0)] == [20.0, 20.5]
    store.put("fits", {"a": 1})
    assert store.get("fits") == {"a": 1}
    store.add_weather([(3600, 1.0, 2.0, 3.0)])
    assert store.weather(0) == [(3600, 1.0, 2.0, 3.0)]
    store.cleanup(1000)
    assert store.first_ts("Living") == 1800
    store.close()
