import asyncio
import json
import logging
import socket

import aiohttp
import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.dashboard import dashboard as dash_module
from fhempy.lib.dashboard import go2rtc, model
from fhempy.lib.dashboard.dashboard import clean_layout, dashboard, parse_opener
from fhempy.lib.pkg_installer import check_and_install_dependencies

from . import fake_home
from .fake_home import FakeFhem, set_default_attrs, set_event_devices

logger = logging.getLogger(__name__)

NAME = "tablets"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest_asyncio.fixture
async def module(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes[NAME] = {"port": str(free_port()), "https_port": "0"}
    fake = FakeFhem()
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake.send)
    mocker.patch("fhempy.lib.fhem.setEventDevices", set_event_devices)
    mocker.patch("fhempy.lib.fhem.setDefaultAttrs", set_default_attrs)
    mod = dashboard(logger)
    fake.module = mod
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "dashboard"}, [], {})
    mod.fake = fake
    yield mod
    await mod.Undefine(mod.hash)
    mock_fhem.attributes.pop(NAME, None)


def base(mod):
    return f"http://127.0.0.1:{mod._attr_port}/"


async def pair(mod, code=None):
    code = code or mod.new_pair_code()
    async with aiohttp.ClientSession() as session:
        async with session.post(base(mod) + "api/pair", json={"code": code}) as resp:
            return resp.status, await resp.json()


async def connect(session, mod, token):
    ws = await session.ws_connect(base(mod) + "api/ws")
    await ws.send_json({"type": "hello", "token": token})
    return ws, await ws.receive_json(timeout=5)


async def next_of(ws, kind):
    while True:
        message = await ws.receive_json(timeout=5)
        if message["type"] == kind:
            return message


def test_model_rooms_and_tiles():
    fake = FakeFhem()
    infos = fake.infos(fake.devices)
    data = model.build(infos)
    names = [r["name"] for r in data["rooms"]]
    # the room with most devices first, ROOMMATE and weather have no tiles
    assert names[0] == "Wohnzimmer"
    assert "rr_Anna" not in data["tiles"]
    living = data["rooms"][0]["tiles"]
    # lights first, sensors last
    assert data["tiles"][living[0]]["kind"] in ("light", "dimmer")
    assert data["tiles"]["wz_Deckenlicht"]["name"] == "Deckenlicht"
    assert data["tiles"]["wz_Deckenlicht"]["state"] == {"on": True, "level": 70}
    assert data["tiles"]["wz_Fernseher"]["kind"] == "outlet"
    assert data["tiles"]["bad_Fenster"]["state"]["tilted"] is True
    assert data["tiles"]["bad_Heizung"]["state"]["battery_low"] is True
    assert data["tiles"]["fl_Haustuer"]["kind"] == "lock"
    assert [s["name"] for s in data["scenes"]] == ["Filmabend", "Gemütlich", "Hell"]


def test_display_name():
    assert model.display_name({"NAME": "wz_LampeDecke"}) == "Lampe Decke"
    assert model.display_name({"NAME": "TV_Licht_links"}) == "Licht Links"
    assert (
        model.display_name({"NAME": "Wohnzimmer_Lampe"}, "Wohnzimmer") == "Lampe"
    )
    assert model.display_name({"NAME": "x", "alias": "Mein Licht"}) == "Mein Licht"


def test_header():
    fake = FakeFhem()
    infos = fake.infos(fake.devices)
    data = model.build(infos)
    head = model.header(infos, data["tiles"])
    assert head["weather"]["temperature"] == 9
    assert [p["name"] for p in head["presence"]["home"]] == ["Anna", "Max"]
    assert head["presence"]["total"] == 3
    # the window open longest first
    assert [o["name"] for o in head["open"]] == ["Fenster Bad", "Fenster Garten"]
    assert head["open"][0]["tilted"] is True
    assert head["energy"] == {"solar": 3400, "load": 1200, "battery": 82}
    assert {r["id"] for r in head["running"]} >= {"wz_Deckenlicht", "ku_Kaffeemaschine"}
    assert head["battery"][0]["id"] == "bad_Heizung"


def test_low_batteries_also_without_tile():
    devices = dict(fake_home.DEVICES)
    devices["fl_Rauchmelder"] = fake_home.device(
        "dummy", "Flur", "", {"batteryLevel": "12"}, alias="Rauchmelder"
    )
    fake = FakeFhem(devices)
    infos = fake.infos(fake.devices)
    data = model.build(infos)
    assert "fl_Rauchmelder" not in data["tiles"]
    low = model.header(infos, data["tiles"])["battery"]
    # sorted by room
    assert [b["id"] for b in low] == ["bad_Heizung", "fl_Rauchmelder"]
    assert low[1] == {
        "id": "fl_Rauchmelder",
        "name": "Rauchmelder",
        "room": "Flur",
        "level": 12,
        "since": fake_home.ts(90),
    }
    assert low[0]["level"] is None


def test_commands():
    fake = FakeFhem()
    infos = fake.infos(fake.devices)
    tiles = model.build(infos)["tiles"]
    dimmer = tiles["wz_Deckenlicht"]
    assert model.command(dimmer, infos["wz_Deckenlicht"], "toggle") == ["off"]
    assert model.command(dimmer, infos["wz_Deckenlicht"], "level", 35) == ["pct 35"]
    assert model.command(dimmer, infos["wz_Deckenlicht"], "level", 0) == ["off"]
    assert model.command(dimmer, infos["wz_Deckenlicht"], "level", 500) == ["pct 100"]
    blind = tiles["wz_Rollladen"]
    assert model.command(blind, infos["wz_Rollladen"], "toggle") == ["pct 0"]
    assert model.command(blind, infos["wz_Rollladen"], "stop") == ["stop"]
    heat = tiles["wz_Heizung"]
    assert model.command(heat, infos["wz_Heizung"], "target", "21.3") == [
        "desired-temp 21.5"
    ]
    # never anything else than the tile allows
    assert model.command(heat, infos["wz_Heizung"], "delete") == []
    with pytest.raises(ValueError):
        model.command(heat, infos["wz_Heizung"], "target", "x; shutdown")
    contact = tiles["wz_Fenster"]
    assert model.command(contact, infos["wz_Fenster"], "toggle") == []
    lock = tiles["fl_Haustuer"]
    assert model.command(lock, infos["fl_Haustuer"], "unlock") == ["unlock"]


def test_doorbell_and_energy_helpers():
    assert model.is_doorbell({"NAME": "fl_Klingel"})
    assert model.is_doorbell({"NAME": "x", "FHEMPYTYPE": "ring"})
    assert not model.is_doorbell({"NAME": "Licht"})
    assert model.rings("state", "ding")
    assert model.rings("action", "single")
    assert not model.rings("battery", "on")
    assert not model.rings("state", "idle")
    assert model.watts("3.4") == 3400
    assert model.watts("1200 W") == 1200
    assert model.watts("1.5 kW") == 1500
    assert model.watts(None) is None


def test_filter_rooms():
    fake = FakeFhem()
    data = model.build(fake.infos(fake.devices))
    kids = model.filter_rooms(data, ["Bad"])
    assert [r["name"] for r in kids["rooms"]] == ["Bad"]
    assert set(kids["tiles"]) == {"bad_Fenster", "bad_Heizung"}
    assert kids["scenes"] == []
    assert model.filter_rooms(data, []) is data


def test_clean_layout_and_opener():
    layout = clean_layout(
        {
            "hidden_tiles": ["a", 1],
            "room_order": "nope",
            "tile_order": {"Bad": ["x"], "Küche": "y"},
            "theme": "light",
            "evil": ["x"],
        }
    )
    assert layout == {
        "hidden_tiles": ["a", "1"],
        "tile_order": {"Bad": ["x"]},
        "theme": "light",
    }
    assert clean_layout("x") == {}
    assert parse_opener("Opener on") == ("Opener", "on")
    assert parse_opener("Opener") is None


def test_go2rtc_config():
    cameras = go2rtc.parse_cameras(
        "Door=rtsp://u:p@1.2.3.4/s1 b%d=x Garden=onvif://5.6.7.8"
    )
    assert cameras == {"Door": "rtsp://u:p@1.2.3.4/s1", "Garden": "onvif://5.6.7.8"}
    config = json.loads(go2rtc.config_text(cameras))
    assert config["api"]["listen"].startswith("127.0.0.1:")
    assert config["streams"] == cameras


def test_pair_codes(module):
    code = module.new_pair_code()
    assert len(code) == 6
    assert module.check_pair_code(code)
    # only once
    assert not module.check_pair_code(code)
    # too many wrong codes: even a right one is refused for a minute
    good = module.new_pair_code()
    for _ in range(dash_module.PAIR_FAILS_MAX):
        module.check_pair_code("000000x")
    assert not module.check_pair_code(good)


@pytest.mark.asyncio
async def test_pair_and_websocket(module):
    status, answer = await pair(module, "123")
    assert status == 403
    status, answer = await pair(module)
    assert status == 200
    token = answer["token"]
    assert answer["tablet"]["name"] == "Tablet1"
    # only the hash of the token is stored
    stored = json.loads(mock_fhem.readings[NAME][".tablets"])
    assert token not in json.dumps(stored)

    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, "wrong")
        assert welcome["type"] == "unknown"
        await ws.close()

        ws, welcome = await connect(session, module, token)
        assert welcome["type"] == "welcome"
        assert "wz_Deckenlicht" in welcome["tiles"]
        assert welcome["header"]["weather"]["temperature"] == 9

        await ws.send_json(
            {"type": "setup", "place": "door", "room": "Flur", "name": "Flur Tür"}
        )
        tablet = (await next_of(ws, "tablet"))["tablet"]
        assert tablet["place"] == "door" and tablet["name"] == "Flur Tür"

        # tap on the light: FHEM gets set, all tablets get the new state
        await ws.send_json({"type": "action", "id": "wz_Deckenlicht", "action": "toggle"})
        tile = (await next_of(ws, "tile"))["tile"]
        assert tile["id"] == "wz_Deckenlicht" and tile["state"]["on"] is False
        assert "wz_Deckenlicht off" in module.fake.sets

        # nothing else than the commands of the tiles
        await ws.send_json({"type": "action", "id": "global", "action": "toggle"})
        await ws.send_json({"type": "action", "id": "fl_Haustuer", "action": "delete"})
        await asyncio.sleep(0.1)
        assert not any(s.startswith(("global", "fl_Haustuer")) for s in module.fake.sets)

        # per tablet layout
        await ws.send_json({"type": "layout", "layout": {"hidden_rooms": ["Bad"]}})
        tablet = (await next_of(ws, "tablet"))["tablet"]
        assert tablet["layout"] == {"hidden_rooms": ["Bad"]}

        # doorbell
        await module.handle_event("fl_Klingel", "state", "ding")
        ring = await next_of(ws, "ring")
        assert ring["name"] == "Klingel"
        await ws.close()


@pytest.mark.asyncio
async def test_restricted_tablet(module):
    _, answer = await pair(module)
    token = answer["token"]
    await module.set_tablet_rooms(module.hash, {"tablet": "Tablet1", "rooms": "Bad"})
    await module.set_tablet_readonly(module.hash, {"tablet": "Tablet1", "readonly": "1"})
    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, token)
        assert set(welcome["tiles"]) == {"bad_Fenster", "bad_Heizung"}
        await ws.send_json(
            {"type": "action", "id": "bad_Heizung", "action": "target", "value": 20}
        )
        await asyncio.sleep(0.1)
        assert module.fake.sets == []
        await module.set_tablet_readonly(
            module.hash, {"tablet": "Tablet1", "readonly": "0"}
        )
        # other rooms stay forbidden
        await ws.send_json({"type": "action", "id": "wz_Deckenlicht", "action": "toggle"})
        await ws.send_json({"type": "action", "action": "all_off", "room": None})
        await asyncio.sleep(0.1)
        assert module.fake.sets == []
        await ws.close()


@pytest.mark.asyncio
async def test_remove_tablet(module):
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await module.set_remove_tablet(module.hash, {"tablet": "Tablet1"})
        await asyncio.sleep(0.1)
        assert ws.closed or (await ws.receive(timeout=2)).type in (
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSING,
        )
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["type"] == "unknown"
        await ws.close()


@pytest.mark.asyncio
async def test_static_and_api_auth(module):
    async with aiohttp.ClientSession() as session:
        async with session.get(base(module)) as resp:
            assert resp.status == 200
            assert "app.js" in await resp.text()
        async with session.get(base(module) + "app.js") as resp:
            assert resp.status == 200
        async with session.get(base(module) + "..%2Fdashboard.py") as resp:
            assert resp.status == 404
        async with session.get(base(module) + "api/timeline") as resp:
            assert resp.status == 401
        async with session.post(
            base(module) + "api/pair",
            json={"code": module.new_pair_code()},
            headers={"Origin": "http://evil.example"},
        ) as resp:
            assert resp.status == 403


@pytest.mark.asyncio
async def test_detail_page(module):
    # segno for the QR code
    await check_and_install_dependencies("dashboard")
    page = module.setup_html()
    assert "data:image/png;base64" in page
    assert str(module._attr_port) in page


@pytest.mark.asyncio
async def test_detail_page_while_starting(mocker):
    # FHEMWEB can ask for the device page before Define is done
    mock_fhem.mock_module(mocker)
    mod = dashboard(logging.getLogger(__name__))
    mod.hash = {"NAME": NAME}
    mocker.patch(
        "fhempy.lib.generic.FhemModule.FW_detailFn", return_value=""
    )
    page = await mod.FW_detailFn({"NAME": NAME}, [], {})
    assert "starting" in page
    assert mod.url().endswith(f":{dash_module.DEFAULT_PORT}/")


@pytest.mark.asyncio
async def test_reload_sends_model_only_on_changes(module, mocker):
    # helper devices come and go in FHEM, the tablets must not redraw for them
    module.tablets["t1"] = {"id": "t1", "name": "Wall"}
    connected = mocker.patch.object(module, "connected", return_value=[("ws", "t1")])
    send = mocker.patch.object(module, "send", mocker.AsyncMock())
    await module.reload()
    send.assert_not_called()
    module.fake.devices["ku_Licht"]["readings"]["state"] = "off"
    await module.reload()
    assert send.await_args.args[1]["type"] == "model"
    connected.return_value = []


def test_sparks_temperature_and_humidity_per_device():
    trends = [
        {"device": "wz_Heizung", "reading": "desired-temp", "points": [20, 21]},
        {"device": "wz_Heizung", "reading": "measured-temp", "points": [20.5, None, 21]},
        {"device": "wz_Heizung", "reading": "humidity", "points": [[0, 48], [3600, 50]]},
        {"device": "kue_Klima", "reading": "temperature", "points": [22, None]},
        {"device": "other", "reading": "temperature", "points": [1, 2]},
    ]
    result = model.sparks(trends, {"wz_Heizung", "kue_Klima"})
    assert result == {"wz_Heizung": {"t": [20.5, None, 21], "h": [48, 50]}}


def test_room_suggestions_and_moves():
    rooms = ["Bad", "Wohnzimmer"]
    assert model.suggest_room({"NAME": "wz_Lampe"}, rooms) == "Wohnzimmer"
    assert model.suggest_room({"NAME": "Licht_Badezimmer"}, rooms) == "Bad"
    assert model.suggest_room({"NAME": "x", "alias": "Lampe Bad"}, rooms) == "Bad"
    assert model.suggest_room({"NAME": "ku_Licht"}, rooms) == "Küche"
    assert model.suggest_room({"NAME": "Steckdose"}, rooms) == ""
    assert model.moved_rooms("Licht,Wohnzimmer,fhempy", "Licht", "Küche") == (
        "Küche,Wohnzimmer,fhempy"
    )
    assert model.moved_rooms("fhempy", "", "Bad") == "Bad,fhempy"
    assert model.moved_rooms("Bad", "Bad", "") == ""
    assert model.moved_rooms("Bad,Flur", "Bad", "Flur") == "Flur"
    assert model.clean_room(" Gäste WC ") == "Gäste WC"
    assert model.clean_room("Bad,Flur") is None
    assert model.clean_room("Bad; delete x") is None
    assert model.clean_room("hidden") is None
    assert model.clean_room("", allow_empty=True) == ""
    layout = {"room_order": ["Bad", "Flur"], "tile_order": {"Bad": ["a"]}}
    assert model.renamed_layout(layout, "Bad", "Badezimmer") == {
        "room_order": ["Badezimmer", "Flur"],
        "tile_order": {"Badezimmer": ["a"]},
    }


@pytest.mark.asyncio
async def test_arrange_rooms(module):
    module.fake.devices["wz_Stehlampe2"] = fake_home.device(
        "dummy", "fhempy", "on off", {"state": "off"}
    )
    module.fake.devices["Lampe_versteckt"] = fake_home.device(
        "dummy", "hidden", "on off", {"state": "off"}
    )
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["tablet"]["arrange"] is True
        await ws.send_json({"type": "rooms_setup"})
        setup = await next_of(ws, "rooms_setup")
        unassigned = {d["id"]: d for d in setup["unassigned"]}
        assert unassigned["wz_Stehlampe2"]["suggestion"] == "Wohnzimmer"
        assert "Lampe_versteckt" not in unassigned
        assert "Bad" in [r["name"] for r in setup["rooms"]]

        move = {"type": "move_device", "id": "wz_Stehlampe2", "from": ""}
        await ws.send_json({**move, "to": "Wohnzimmer"})
        setup = await next_of(ws, "rooms_setup")
        assert module.fake.devices["wz_Stehlampe2"]["room"] == "Wohnzimmer,fhempy"
        assert "wz_Stehlampe2" not in [d["id"] for d in setup["unassigned"]]

        # FHEM commands can't be smuggled in with a room name
        move = {"type": "move_device", "id": "bad_Fenster", "from": "Bad"}
        await ws.send_json({**move, "to": "x;shutdown"})
        await next_of(ws, "rooms_setup")
        assert module.fake.devices["bad_Fenster"]["room"] == "Bad"

        module.tablets[welcome["tablet"]["id"]]["layout"] = {"room_order": ["Bad"]}
        await ws.send_json({"type": "rename_room", "from": "Bad", "to": "Badezimmer"})
        setup = await next_of(ws, "rooms_setup")
        assert module.fake.devices["bad_Fenster"]["room"] == "Badezimmer"
        assert "Badezimmer" in [r["name"] for r in setup["rooms"]]
        tablet = module.tablets[welcome["tablet"]["id"]]
        assert tablet["layout"]["room_order"] == ["Badezimmer"]
        await ws.close()


@pytest.mark.asyncio
async def test_restricted_tablet_cannot_arrange_rooms(module):
    _, answer = await pair(module)
    await module.set_tablet_rooms(module.hash, {"tablet": "Tablet1", "rooms": "Bad"})
    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["tablet"]["arrange"] is False
        await ws.send_json({"type": "rename_room", "from": "Bad", "to": "Badezimmer"})
        await ws.send_json({"type": "rooms_setup"})
        await asyncio.sleep(0.2)
        assert module.fake.devices["bad_Fenster"]["room"] == "Bad"
        await ws.close()


def test_all_off_leaves_heating_on():
    infos = {
        "Heizstab": {"NAME": "Heizstab", "TYPE": "dummy", "room": "Keller",
                     "sets": "on off", "readings": {"state": "on"}},
        "Plug_TV": {"NAME": "Plug_TV", "TYPE": "dummy", "room": "Keller",
                    "sets": "on off", "readings": {"state": "on"}},
        "sw1": {"NAME": "sw1", "TYPE": "dummy", "room": "Keller",
                   "alias": "FRITZ!Box", "sets": "on off", "readings": {"state": "on"}},
        "Heimtheater": {"NAME": "Heimtheater", "TYPE": "dummy", "room": "Keller",
                        "sets": "on off", "readings": {"state": "on"}},
    }
    tiles = model.build(infos)["tiles"]
    assert sorted(model.all_off(tiles)) == ["Heimtheater", "Plug_TV"]
    kept = {r["id"]: r["keep_on"] for r in model.running(tiles)}
    assert kept["Heizstab"] is True and kept["Plug_TV"] is False
    # chosen on a tablet: only these stay on
    tiles = model.build(infos, keep_on={"Plug_TV"})["tiles"]
    assert sorted(model.all_off(tiles)) == ["Heimtheater", "Heizstab", "sw1"]


@pytest.mark.asyncio
async def test_keep_on_from_tablet(module):
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json({"type": "keep_on", "id": "ku_Kaffeemaschine", "keep": True})
        model_msg = await next_of(ws, "model")
        assert model_msg["tiles"]["ku_Kaffeemaschine"]["keep_on"] is True
        assert "ku_Kaffeemaschine" in module._attr_keep_on
        await ws.send_json({"type": "action", "action": "all_off", "room": None})
        await asyncio.sleep(0.2)
        assert not any(s.startswith("ku_Kaffeemaschine") for s in module.fake.sets)
        await ws.close()



def test_arrangement_only_offers_devices_shown_on_tablets():
    infos = {
        "di_Licht": {"NAME": "di_Licht", "TYPE": "DOIF", "room": "", "sets": ""},
        "at_Abend": {"NAME": "at_Abend", "TYPE": "at", "room": "", "sets": ""},
        "Lampe": {"NAME": "Lampe", "TYPE": "dummy", "room": "", "sets": "on off"},
    }
    data = model.arrangement(infos)
    assert [d["id"] for d in data["unassigned"]] == ["Lampe"]

def test_idle_devices_when_arranging():
    now = model.datetime.datetime(2026, 11, 2, 12, 0, 0)
    infos = {
        "old": {"NAME": "old", "TYPE": "dummy", "room": "Bad", "sets": "on off",
                "readings": {"state": "off"}, "last": "2026-09-01 10:00:00"},
        "new": {"NAME": "new", "TYPE": "dummy", "room": "Bad", "sets": "on off",
                "readings": {"state": "off"}, "last": "2026-10-30 10:00:00"},
        "none": {"NAME": "none", "TYPE": "dummy", "room": "", "sets": "on off"},
    }
    data = model.arrangement(infos, now)
    devices = {d["id"]: d for d in data["rooms"][0]["devices"]}
    assert devices["old"]["idle"] == 62
    assert "idle" not in devices["new"]
    assert "idle" not in data["unassigned"][0]


@pytest.mark.asyncio
async def test_delete_idle_device(module):
    module.fake.devices["alt_Lampe"] = fake_home.device(
        "dummy", "Bad", "on off", {"state": "off"}
    )
    module.fake.devices["alt_Lampe"]["idle_minutes"] = 60 * 24 * 90
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json({"type": "rooms_setup"})
        setup = await next_of(ws, "rooms_setup")
        bad = next(r for r in setup["rooms"] if r["name"] == "Bad")
        assert next(d for d in bad["devices"] if d["id"] == "alt_Lampe")["idle"] >= 89
        # only devices offered there can be deleted, never the dashboard
        await ws.send_json({"type": "delete_device", "id": NAME})
        await next_of(ws, "rooms_setup")
        await ws.send_json({"type": "delete_device", "id": "alt_Lampe"})
        setup = await next_of(ws, "rooms_setup")
        assert "alt_Lampe" not in module.fake.devices
        bad = next(r for r in setup["rooms"] if r["name"] == "Bad")
        assert "alt_Lampe" not in [d["id"] for d in bad["devices"]]
        await ws.close()


def test_presence_people_with_arrival_and_departure():
    infos = {
        "rr_A": {"NAME": "rr_A", "TYPE": "ROOMMATE", "alias": "Anna",
                 "readings": {"state": "awoken", "lastArrival": "2026-11-02 18:42:00"},
                 "times": {"state": "2026-11-02 20:00:00"}},
        "rr_L": {"NAME": "rr_L", "TYPE": "ROOMMATE", "alias": "Lea",
                 "readings": {"state": "absent"},
                 "times": {"state": "2026-11-01 07:10:00"}},
    }
    people = model.presence(infos)["people"]
    assert [(p["name"], p["home"], p["since"]) for p in people] == [
        ("Anna", True, "2026-11-02 18:42:00"),
        ("Lea", False, "2026-11-01 07:10:00"),
    ]


@pytest.mark.asyncio
async def test_tablet_without_timeline(module):
    async def day(d):
        return {
            "day": d,
            "periods": [{"start": "2026-10-01", "end": "2026-10-05"}],
            "entries": [
                {"ts": 1, "text": "Light on", "room": "Wohnzimmer"},
                {"ts": 2, "text": "Door open", "room": "Flur,Haus"},
            ],
            "trends": [],
        }

    async def history(device):
        return {"activity": [{"segments": []}], "trends": [], "to": 10}

    module.timeline_day = day
    module.timeline_device_history = history
    _, answer = await pair(module)
    auth = {"Authorization": "Bearer " + answer["token"]}
    tile = next(iter(module.data["tiles"]))
    async with aiohttp.ClientSession() as session:
        async with session.get(base(module) + "api/timeline", headers=auth) as resp:
            assert resp.status == 200
            assert len((await resp.json())["entries"]) == 2
        # a tablet for some rooms only sees what happened there
        await module.set_tablet_rooms(
            module.hash, {"tablet": "Tablet1", "rooms": "Wohnzimmer"}
        )
        async with session.get(base(module) + "api/timeline", headers=auth) as resp:
            data = await resp.json()
            assert [e["text"] for e in data["entries"]] == ["Light on"]
            assert data["periods"] == []
        await module.set_tablet_rooms(module.hash, {"tablet": "Tablet1", "rooms": "all"})
        await module.set_tablet_timeline(
            module.hash, {"tablet": "Tablet1", "timeline": "0"}
        )
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["tablet"]["timeline"] is False
        await ws.close()
        async with session.get(base(module) + "api/timeline", headers=auth) as resp:
            assert resp.status == 403
        async with session.get(
            base(module) + "api/history?id=" + tile, headers=auth
        ) as resp:
            data = await resp.json()
            assert "activity" not in data and data["to"] == 10
        assert "(no timeline)" in module.setup_html()
        await module.set_tablet_timeline(
            module.hash, {"tablet": "Tablet1", "timeline": "1"}
        )
        async with session.get(base(module) + "api/timeline", headers=auth) as resp:
            assert resp.status == 200


@pytest.mark.asyncio
async def test_event_filter_and_global_events(module):
    import re

    flt = re.compile(module.event_filter())
    assert flt.search("wz_Deckenlicht:state: on")
    assert flt.search("global:DEFINED at_1")
    assert not flt.search("wz_Deckenlicht:linkquality: 120")
    assert not flt.search("wz_Deckenlicht:state_x: 1")

    reloads = []
    module.schedule_reload = lambda: reloads.append(1)
    # helper devices FHEM defines and deletes all the time: no reading again
    await module.handle_global_event("global", "state", "DEFINED at_123")
    await module.handle_global_event("global", "state", "DELETED at_123")
    await module.handle_global_event("global", "state", "MODIFIED at_7")
    assert reloads == []
    await module.handle_global_event("global", "state", "DELETED wz_Deckenlicht")
    await module.handle_global_event("global", "state", "ATTR wz_Deckenlicht room Bad")
    assert len(reloads) == 2


@pytest.mark.asyncio
async def test_all_off_only_devices_the_tablet_shows(module):
    _, answer = await pair(module)
    on = model.all_off(module.data["tiles"])
    assert len(on) >= 2
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json(
            {"type": "action", "action": "all_off", "room": None, "ids": on[:1]}
        )
        await asyncio.sleep(0.2)
        switched = [s.split(" ")[0] for s in module.fake.sets]
        assert switched == on[:1]
        await ws.close()


BOSE_SETS = (
    "on off play pause stop playpause nextTrack prevTrack channel:1,2,3,4,5,6"
    " volume:slider,0,1,100 mute:on,off"
)


def bose(**readings):
    values = {
        "state": "playing",
        "playStatus": "PLAY_STATE",
        "artStatus": "IMAGE_PRESENT",
        "art": "http://speaker.local/art/station.png",
        "artist": "Artist",
        "track": "Track",
        "stationName": "Station Two",
        "channel": "2",
        "volume": "24",
        "channel_01": "Station One",
        "channel_02": "Station Two",
        "channel_03": "-",
    }
    values.update(readings)
    return fake_home.device("BOSEST", "Wohnzimmer", BOSE_SETS, values)


def test_media_players():
    from fhempy.lib.dashboard import media

    cast = fake_home.device(
        "fhempy",
        "Küche",
        "play pause stop next prev volume:slider,0,1,100 playFavorite:1,2,3",
        {
            "state": "paused",
            "mediaTitle": "Song",
            "mediaArtist": "Band",
            "mediaImageUrl": "https://img.example/cover.jpg",
        },
        fhempytype="googlecast",
    )
    cast["NAME"] = "cast"
    speaker = bose()
    speaker["NAME"] = "speaker"
    assert model.kind_of(cast) == "media" and model.kind_of(speaker) == "media"
    # a plain switch with on/off stays a switch
    assert model.kind_of({"NAME": "x", "sets": "on off", "readings": {}}) == "switch"
    # play and pause plus next is enough without a known type
    assert media.is_media({"TYPE": "dummy", "sets": "play pause next", "attrs": {}})

    state = model.tile_state("media", speaker)
    assert state["playing"] and state["on"] and state["channel"] == 2
    assert state["title"] == "Track" and state["station"] == "Station Two"
    assert [p["n"] for p in state["presets"]] == [1, 2]
    assert state["art"] == media.art_key("http://speaker.local/art/station.png")
    # BOSEST: 'online' is switched off
    off = bose(state="online", playStatus="STANDBY")
    off["NAME"] = "speaker"
    assert model.tile_state("media", off)["on"] is False
    assert media.command(off, "toggle") == ["on"]

    cast_state = model.tile_state("media", cast)
    assert cast_state["paused"] and not cast_state["playing"]
    assert cast_state["title"] == "Song" and cast_state["artist"] == "Band"

    item = model.tile(speaker, "Wohnzimmer")
    assert item["media"] == {"next": True, "prev": True, "volume": True, "power": True}
    assert model.command(item, speaker, "toggle") == ["pause"]
    assert model.command(item, speaker, "next") == ["nextTrack"]
    assert model.command(item, speaker, "prev") == ["prevTrack"]
    assert model.command(item, speaker, "volume", 130) == ["volume 100"]
    assert model.command(item, speaker, "preset", 1) == ["channel 1"]
    # empty presets and free commands are not allowed
    assert model.command(item, speaker, "preset", 3) == []
    assert model.command(item, speaker, "preset", "1; shutdown") == ["channel 1"]
    assert model.command(item, speaker, "shutdown") == []
    cast_item = model.tile(cast, "Küche")
    assert model.command(cast_item, cast, "toggle") == ["play"]
    assert model.command(cast_item, cast, "next") == ["next"]
    assert model.command(cast_item, cast, "preset", 2) == ["playFavorite 2"]

    # only http(s) covers
    bad = bose(art="javascript:alert(1)")
    assert media.art_url(bad) is None
    assert media.art_url(bose(artStatus="SHOW_DEFAULT_IMAGE")) is None


def test_learn_preset_art():
    from fhempy.lib.dashboard import media

    known = {}
    info = bose()
    assert media.learn_preset_art(known, info, True)
    assert known == {"2": "http://speaker.local/art/station.png"}
    # later covers of a playlist on the preset don't replace the logo
    info = bose(art="http://speaker.local/art/song.png")
    assert not media.learn_preset_art(known, info, False)
    assert media.learn_preset_art(known, info, True)
    info["preset_art"] = known
    presets = media.presets(info)
    assert presets[1]["art"] == media.art_key("http://speaker.local/art/song.png")
    assert "art" not in presets[0]
    # paused or no preset: nothing is learned
    assert not media.learn_preset_art({}, bose(playStatus="PAUSE_STATE", state="paused"), True)
    assert not media.learn_preset_art({}, bose(channel=""), True)


@pytest.mark.asyncio
async def test_media_cover_through_fhempy(module):
    module.fake.devices["wz_Radio"] = bose()
    await module.reload()
    assert module.data["tiles"]["wz_Radio"]["kind"] == "media"
    loaded = []

    async def fetch(url):
        loaded.append(url)
        return "image/png", b"png"

    module.fetch_image = fetch
    _, answer = await pair(module)
    auth = {"Authorization": "Bearer " + answer["token"]}
    async with aiohttp.ClientSession() as session:
        url = base(module) + "api/image?id=wz_Radio"
        async with session.get(url) as resp:
            assert resp.status == 401
        async with session.get(url, headers=auth) as resp:
            assert resp.status == 200 and await resp.read() == b"png"
        # no covers of other devices, no URLs from the tablet
        async with session.get(
            base(module) + "api/image?id=wz_Deckenlicht", headers=auth
        ) as resp:
            assert resp.status == 404
        async with session.get(url + "&preset=1", headers=auth) as resp:
            assert resp.status == 404
        # the cover of a preset is learned while it plays
        await module.handle_event("wz_Radio", "channel", "1")
        await module.handle_event("wz_Radio", "art", "http://speaker.local/art/one.png")
        assert module.preset_art["wz_Radio"]["1"] == "http://speaker.local/art/one.png"
        assert "wz_Radio" in mock_fhem.readings[NAME][".preset_art"]
        async with session.get(url + "&preset=1", headers=auth) as resp:
            assert resp.status == 200
        presets = module.data["tiles"]["wz_Radio"]["state"]["presets"]
        assert "art" in presets[0]
        # a tablet for other rooms gets nothing
        await module.set_tablet_rooms(module.hash, {"tablet": "Tablet1", "rooms": "Küche"})
        async with session.get(url, headers=auth) as resp:
            assert resp.status == 404
    assert loaded == [
        "http://speaker.local/art/station.png",
        "http://speaker.local/art/one.png",
    ]


FAN_SETS = "fan_pct:slider,0,1,100 fan_mode:off,low,medium,high"


def test_fans():
    fan = fake_home.device(
        "dummy",
        "Schlafzimmer",
        "on off " + FAN_SETS,
        {"state": "on", "fan_pct": "66", "fan_mode": "medium"},
        attrs={"genericDeviceType": "fan"},
    )
    fan["NAME"] = "fan"
    item = model.tile(fan, "Schlafzimmer")
    assert item["kind"] == "fan" and item["fan"] is True
    assert item["state"]["on"] and item["state"]["mode"] == "medium"
    assert model.command(item, fan, "toggle") == ["fan_mode off"]
    assert model.command(item, fan, "fan_percent", 120) == ["fan_pct 100"]
    assert model.command(item, fan, "fan_mode", "low") == ["fan_mode low"]
    with pytest.raises(ValueError):
        model.command(item, fan, "fan_mode", "turbo; shutdown")
    off = dict(fan, readings={"state": "off", "fan_pct": "0", "fan_mode": "off"})
    off_item = model.tile(off, "Schlafzimmer")
    assert not off_item["state"]["on"]
    assert model.command(off_item, off, "toggle") == ["fan_mode medium"]
    assert "fan_pct" in model.READINGS and "fan_mode" in model.READINGS

    # a ceiling fan with light stays a light, the fan is a part of it
    ceiling = fake_home.device(
        "mantra_ble",
        "Wohnzimmer",
        "on off pct:slider,0,1,100 " + FAN_SETS,
        {"state": "on", "pct": "40", "fan_pct": "33", "fan_mode": "low"},
    )
    ceiling["NAME"] = "ceiling"
    light = model.tile(ceiling, "Wohnzimmer")
    assert light["kind"] == "dimmer" and light["fan"] is True
    assert light["state"]["fan"]["mode"] == "low"
    assert model.command(light, ceiling, "fan_mode", "high") == ["fan_mode high"]
    assert model.command(light, ceiling, "level", 60) == ["pct 60"]
    # lights without fan know no fan commands
    plain = model.tile(fake_home.DEVICES["wz_Deckenlicht"] | {"NAME": "x"}, "Wohnzimmer")
    assert "fan" not in plain
    assert model.command(plain, {"sets": "on off pct"}, "fan_mode", "high") == []


def doif_with_inputs():
    doif = fake_home.device(
        "DOIF",
        "Garten",
        "Dauer Modus Start Notiz Los disable enable checkall cmd_1",
        {"state": "cmd_1", "Dauer": "15", "Modus": "auto", "Start": "06:30"},
        attrs={
            "readingList": "Dauer Modus Start Notiz",
            "setList": "Dauer:slider,5,5,60 Modus:auto,an,aus Start:time"
            " Notiz:textField Los:noArg disable:noArg Licht:on,off",
        },
    )
    doif["NAME"] = "di_Garten"
    return doif


def test_doif_inputs():
    from fhempy.lib.dashboard import inputs

    doif = doif_with_inputs()
    item = model.tile(doif, "Garten")
    assert item["kind"] == "inputs"
    assert [(i["name"], i["type"]) for i in item["inputs"]] == [
        ("Dauer", "slider"),
        ("Modus", "select"),
        ("Start", "time"),
        ("Notiz", "text"),
        ("Los", "button"),
        ("Licht", "switch"),
    ]
    assert item["state"]["values"] == {"Dauer": "15", "Modus": "auto", "Start": "06:30"}
    assert {"Dauer", "Modus", "Notiz"} <= model.device_readings(doif)

    def run(name, value):
        return model.command(item, doif, "input", {"name": name, "value": value})

    assert run("Dauer", 33) == ["Dauer 35"]
    assert run("Dauer", 500) == ["Dauer 60"]
    assert run("Modus", "an") == ["Modus an"]
    assert run("Start", "7:05") == ["Start 7:05"]
    assert run("Notiz", "Tomaten") == ["Notiz Tomaten"]
    assert run("Los", None) == ["Los"]
    for name, value in (
        ("Modus", "kaputt"),
        ("Start", "25:00"),
        ("Dauer", "viel"),
        ("Notiz", "a\nb"),
    ):
        with pytest.raises(ValueError):
            run(name, value)
    # only the inputs, no DOIF commands or other actions
    assert run("disable", None) == []
    assert run("cmd_1", None) == []
    assert model.command(item, doif, "toggle") == []
    # a DOIF without setList is no tile
    plain = dict(doif, attrs={})
    assert not inputs.has_inputs(plain)


@pytest.mark.asyncio
async def test_doif_inputs_live(module):
    module.fake.devices["di_Garten"] = doif_with_inputs()
    await module.reload()
    assert module.data["tiles"]["di_Garten"]["kind"] == "inputs"
    assert "di_Garten" in module.event_filter()
    await module.handle_event("di_Garten", "Dauer", "40")
    assert module.data["tiles"]["di_Garten"]["state"]["values"]["Dauer"] == "40"
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json(
            {
                "type": "action",
                "action": "input",
                "id": "di_Garten",
                "value": {"name": "Modus", "value": "aus"},
            }
        )
        await asyncio.sleep(0.2)
        assert module.fake.sets[-1] == "di_Garten Modus aus"
        await ws.close()


@pytest.mark.asyncio
async def test_header_built_once_for_many_events(module, mocker):
    built = []
    make = module.make_header

    def counting():
        built.append(1)
        return make()

    module.make_header = counting
    mocker.patch.object(dash_module, "HEADER_DELAY", 0.05)
    # only devices for weather, energy, people and batteries, not all
    assert len(module._head_infos) < len(module.infos)
    for value in range(50):
        await module.handle_event("wz_Fernseher", "power", str(value))
    await module.handle_event("wz_Fenster", "contact", "open")
    assert built == []
    await asyncio.sleep(0.2)
    assert len(built) == 1
    assert "wz_Fenster" in [c["id"] for c in module.head["open"]]
    # a battery which becomes low is in the header too
    await module.handle_event("wz_Deckenlicht", "battery", "low")
    await asyncio.sleep(0.2)
    assert "wz_Deckenlicht" in [b["id"] for b in module.head["battery"]]


async def chunked_image_server(body, chunk=1000):
    """serves body in small pieces with pauses, like a slow music player"""
    from aiohttp import web

    async def handler(request):
        resp = web.StreamResponse(headers={"Content-Type": "image/jpeg"})
        await resp.prepare(request)
        for start in range(0, len(body), chunk):
            await resp.write(body[start : start + chunk])
            await asyncio.sleep(0.01)
        await resp.write_eof()
        return resp

    app = web.Application()
    app.router.add_get("/cover.jpg", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = free_port()
    await web.TCPSite(runner, "127.0.0.1", port).start()
    return runner, f"http://127.0.0.1:{port}/cover.jpg"


@pytest.mark.asyncio
async def test_cover_is_loaded_completely(module):
    body = bytes(range(256)) * 200
    runner, url = await chunked_image_server(body)
    try:
        content_type, loaded = await module.fetch_image(url)
    finally:
        await runner.cleanup()
    assert content_type == "image/jpeg"
    assert loaded == body


@pytest.mark.asyncio
async def test_too_big_cover_is_refused(module, mocker):
    mocker.patch.object(dash_module, "MAX_IMAGE_SIZE", 5000)
    runner, url = await chunked_image_server(b"x" * 6000)
    try:
        with pytest.raises(ValueError):
            await module.fetch_image(url)
    finally:
        await runner.cleanup()
    assert url not in module._images
