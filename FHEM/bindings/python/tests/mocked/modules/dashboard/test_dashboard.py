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
    assert data["tiles"]["wz_Deckenlicht"]["state"] == {
        "on": True,
        "level": 70,
        "rgb": "#ffb070",
        "ct": 2703,
    }
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


def test_zigbee2mqtt_dimmer_channel():
    # MQTT2_DEVICE of the second channel of a zigbee2mqtt dimmer: brightness
    # 0..254 stays when the light is off
    info = {
        "NAME": "light_ch2",
        "TYPE": "MQTT2_DEVICE",
        "room": "Wohnzimmer",
        "sets": "on:noArg off:noArg toggle:noArg brightness:colorpicker,BRI,0,1,254",
        "readings": {"state": "off", "brightness": "254", "action": "off_l1"},
        "attrs": {"genericDeviceType": "light"},
    }
    item = model.tile(info)
    assert item["kind"] == "dimmer"
    assert item["state"]["on"] is False
    # until the device confirms the command of the tablet: unknown, not on
    # because of the brightness
    info["readings"]["state"] = "set_off"
    assert "on" not in model.tile(info)["state"]
    # 127 of 254 is half
    info["readings"].update(state="on", brightness="127")
    assert model.tile(info)["state"] == {"on": True, "level": 50}
    assert model.command(item, info, "level", 50) == ["brightness 127"]
    assert model.command(item, info, "level", 100) == ["brightness 254"]
    assert model.command(item, info, "level", 0) == ["off"]


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
    # state events without "state: "
    assert flt.search("wz_Deckenlicht:off")
    assert flt.search("wz_Deckenlicht:on-for-timer 12:30")
    # set_off until the device confirms: the tile stays as it was
    await module.handle_event("wz_Deckenlicht", "state", "set_off")
    assert module.data["tiles"]["wz_Deckenlicht"]["state"]["on"] is True
    await module.handle_event("wz_Deckenlicht", "state", "off")
    assert module.data["tiles"]["wz_Deckenlicht"]["state"]["on"] is False

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

    old = "http://speaker.local/art/old.png"
    one = "http://speaker.local/art/one.png"
    song = "http://speaker.local/art/song.png"
    known = {}
    learner = media.PresetArtLearner()
    # first event since the start: the cover may still be the old station's
    assert not learner.update(known, bose(channel="1", art=old), 0)
    assert learner.update(known, bose(channel="1", art=one), 1)
    assert known == {"1": one}
    # later covers of a playlist on the preset don't replace the logo
    assert not learner.update(known, bose(channel="1", art=song), 100)
    assert known == {"1": one}
    # after a restart a known logo isn't replaced by the next song
    learner = media.PresetArtLearner()
    assert not learner.update(known, bose(channel="1", art=one), 200)
    assert not learner.update(known, bose(channel="1", art=song), 210)
    assert known == {"1": one}
    info = bose(channel="1", art=one)
    info["preset_art"] = known
    presets = media.presets(info)
    assert presets[0]["art"] == media.art_key(one)
    assert "art" not in presets[1]
    # paused or no preset: nothing is learned
    paused = bose(playStatus="PAUSE_STATE", state="paused")
    assert not media.PresetArtLearner().update({}, paused, 0)
    assert not media.PresetArtLearner().update({}, bose(channel=""), 0)


def test_preset_art_not_taken_from_previous_station():
    from fhempy.lib.dashboard import media

    one = "http://speaker.local/art/one.png"
    two = "http://speaker.local/art/two.png"
    song = "http://speaker.local/art/song.png"
    known = {"1": one}
    learner = media.PresetArtLearner()
    learner.update(known, bose(channel="1", art=one), 0)
    # switch to preset 2: the channel comes first, the old cover is still there
    assert not learner.update(known, bose(channel="2", art=one), 100)
    assert "2" not in known
    # then the logo of the new station: learned, a later song cover is not
    assert learner.update(known, bose(channel="2", art=two), 101)
    assert not learner.update(known, bose(channel="2", art=song), 110)
    assert known == {"1": one, "2": two}

    # cover first, channel a moment later: the new cover is still the logo
    known = {}
    learner = media.PresetArtLearner()
    learner.update(known, bose(channel="1", art=one), 0)
    learner.update(known, bose(channel="1", art=two), 100)
    assert learner.update(known, bose(channel="2", art=two), 100.5)
    assert known["2"] == two

    # a wrong logo learned earlier is corrected when the preset is chosen again
    known = {"1": one, "2": one}
    learner = media.PresetArtLearner()
    learner.update(known, bose(channel="1", art=one), 0)
    assert not learner.update(known, bose(channel="2", art=one), 100)
    assert learner.update(known, bose(channel="2", art=two), 102)
    assert known["2"] == two


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
        # a song cover: the tile also gets the station logo, served as preset=logo
        await module.handle_event("wz_Radio", "art", "http://speaker.local/album/song.jpg")
        state = module.data["tiles"]["wz_Radio"]["state"]
        assert state["logo"] == presets[0]["art"] != state["art"]
        async with session.get(url + "&preset=logo", headers=auth) as resp:
            assert resp.status == 200
        # a tablet for other rooms gets nothing
        await module.set_tablet_rooms(module.hash, {"tablet": "Tablet1", "rooms": "Küche"})
        async with session.get(url, headers=auth) as resp:
            assert resp.status == 404
    assert loaded == [
        "http://speaker.local/art/station.png",
        "http://speaker.local/art/one.png",
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


def test_station_logo_and_song_cover():
    from fhempy.lib.dashboard import media

    logo = "http://cdn-profiles.example.com/s1/images/logog.png"
    other = "http://cdn-profiles.example.com/s2/images/logog.png"
    song = "http://cdn-albums.example.com/1234.jpg"
    assert media.image_kind(logo) == "logo"
    assert media.image_kind(song) == "cover"
    assert media.image_kind("http://speaker.local/art/x.png") is None

    known = {"2": song}
    learner = media.PresetArtLearner()
    learner.update(known, bose(channel="1", art=other), 0)
    # switch to preset 2: the old logo and song covers are never learned
    assert not learner.update(known, bose(channel="2", art=other), 100)
    assert not learner.update(known, bose(channel="2", art=song), 101)
    assert known["2"] == song
    # the station logo is learned whenever it shows, also after 30 s
    assert learner.update(known, bose(channel="2", art=logo), 200)
    assert known["2"] == logo and learner.logo == logo
    assert not learner.update(known, bose(channel="2", art=song), 210)
    assert known["2"] == logo

    # while a song plays, the tile shows its cover and the station logo
    info = bose(channel="2", art=song)
    info["preset_art"] = known
    info["station_logo"] = learner.logo
    state = media.state(info)
    assert state["art"] == media.art_key(song)
    assert state["logo"] == media.art_key(logo)
    # no extra logo when the logo itself is the cover
    info = bose(channel="2", art=logo)
    info["preset_art"] = known
    assert media.state(info)["logo"] is None
    # without a logo seen since the switch: the one learned for the preset
    info = bose(channel="2", art=song)
    info["preset_art"] = known
    assert media.logo_url(info) == logo
    assert media.logo_url(bose(channel="", art=song)) is None


def test_short_error():
    assert model.short_error("Unknown argument foo, choose one of on off") == (
        "Unknown argument foo"
    )
    assert model.short_error("x" * 300).endswith("…")
    assert len(model.short_error("x" * 300)) == 120


@pytest.mark.asyncio
async def test_failed_set_is_told_to_the_tablet(module):
    _, answer = await pair(module)
    switch = next(
        t for t in module.data["tiles"].values() if t["kind"] in ("switch", "outlet")
    )
    module.fake.fail[switch["id"]] = "No answer from the device, choose one of on off"
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json({"type": "action", "action": "toggle", "id": switch["id"]})
        message = await next_of(ws, "failed")
        assert message["id"] == switch["id"]
        assert message["name"] == switch["name"]
        assert message["reason"] == "No answer from the device"
        # the real state follows
        assert (await next_of(ws, "tile"))["tile"]["id"] == switch["id"]


def test_timer_definition():
    assert model.timer_name("wz.Lamp-1") == "dashboard_timer_wz.Lamp_1"
    assert model.timer_definition("lamp", 90, ["off"]) == (
        "dashboard_timer_lamp at +01:30:00 set lamp off"
    )
    assert model.timer_definition("fan", 15, ["fan_mode off", "off"]).endswith(
        "set fan fan_mode off; set fan off"
    )
    assert model.timer_minutes("30") == 30
    assert model.timer_minutes("x") == 0
    assert model.timer_minutes(99999) == 1440
    assert model.running_timers({"a": 10, "b": 30, "c": "x"}, 20) == {"b": 30}


@pytest.mark.asyncio
async def test_timer_switches_off_later(module, mocker):
    _, answer = await pair(module)
    lamp = next(
        t
        for t in module.data["tiles"].values()
        if t["kind"] == "light" and not t["state"].get("on")
    )
    sent = []
    send = module.fake.send

    async def spy(hash, code):
        sent.append(code)
        return await send(hash, code)

    mocker.patch("fhempy.lib.fhem.sendCommandHash", spy)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json(
            {"type": "action", "action": "timer", "id": lamp["id"], "value": 30}
        )
        while True:
            tile = (await next_of(ws, "tile"))["tile"]
            if tile["id"] == lamp["id"] and tile.get("timer"):
                break
        # off before: "on for 30 min" switches it on first
        assert f"{lamp['id']} on" in module.fake.sets
        assert any(
            f"dashboard_timer_{lamp['id']} at +00:30:00 set {lamp['id']} off" in c
            for c in sent
        )
        assert lamp["id"] in json.loads(mock_fhem.readings[NAME][".timers"])
        # switching off by hand ends the timer
        await ws.send_json({"type": "action", "action": "off", "id": lamp["id"]})
        while True:
            tile = (await next_of(ws, "tile"))["tile"]
            if tile["id"] == lamp["id"] and not tile["state"].get("on"):
                break
        assert "timer" not in tile
        assert lamp["id"] not in module.timers
        assert any(
            f"'dashboard_timer_{lamp['id']}'; CommandDelete" in c for c in sent
        )
        await ws.close()


def light(sets, readings=None):
    info = fake_home.device("dummy", "Wohnzimmer", "on off pct:slider,0,1,100 " + sets)
    info.update({"NAME": "lamp", "readings": readings or {"state": "on", "pct": "50"}})
    return info


def test_colour_lights():
    hue = light(
        "rgb:colorpicker,RGB ct:colorpicker,CT,154,1,500 hue:colorpicker,HUE,0,1,65535",
        {"state": "on", "pct": "50", "rgb": "FF8800", "ct": "250"},
    )
    item = model.tile(hue)
    assert item["kind"] == "dimmer"
    assert item["color"] == {"rgb": True, "ct": [2000, 6494]}
    assert item["state"]["rgb"] == "#ff8800"
    assert item["state"]["ct"] == 4000
    assert model.command(item, hue, "rgb", "#00ff00") == ["rgb 00FF00"]
    # kelvin to mired, within the range of the lamp
    assert model.command(item, hue, "ct", 2700) == ["ct 370"]
    assert model.command(item, hue, "ct", 10000) == ["ct 154"]
    with pytest.raises(ValueError):
        model.command(item, hue, "rgb", "red; set x")

    # zigbee2mqtt: hex and color_temp in mired
    z2m = light("hex:colorpicker,RGB color_temp:colorpicker,CT,250,1,454")
    assert model.color_caps(z2m)["ct"] == [2203, 4000]
    assert model.command(model.tile(z2m), z2m, "rgb", "123abc") == ["hex 123ABC"]

    # Shelly: colour temperature in kelvin
    shelly = light("ct:slider,3000,100,6500", {"state": "on", "ct": "4000"})
    item = model.tile(shelly)
    assert item["color"] == {"ct": [3000, 6500]}
    assert item["state"]["ct"] == 4000
    assert model.command(item, shelly, "ct", 2700) == ["ct 3000"]

    # a plain dimmer has no colour
    plain = light("")
    assert "color" not in model.tile(plain)
    assert model.command(model.tile(plain), plain, "rgb", "ffffff") == []


def test_maintenance_and_co2():
    fake = FakeFhem()
    tiles = model.build(fake.infos(fake.devices))["tiles"]
    assert tiles["ku_Klima"]["state"]["co2"] == 1650
    assert tiles["ga_Steckdose"]["state"]["unreachable"] is True
    assert "unreachable" not in tiles["ku_Licht"]["state"]
    # the hour of the newest value of a sensor
    seen = tiles["ga_Aussen"]["state"]["seen"]
    assert len(seen) == 13 and seen == fake_home.ts(3 * 24 * 60)[:13]
    assert "seen" not in tiles["ku_Licht"]["state"]
    for readings in ({"Activity": "dead"}, {"state": "unreachable"}, {"availability": "offline"}):
        assert model.unreachable({"readings": readings})
    assert not model.unreachable({"readings": {"Activity": "alive", "state": "on"}})


@pytest.mark.asyncio
async def test_build_of_the_app_files(module):
    build = module.build
    assert len(build) == 12 and build == dash_module.www_build()
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        async with session.get(base(module) + "app.js") as resp:
            code = await resp.text()
        assert f'var BUILD = "{build}";' in code
        assert "__DASHBOARD_BUILD__" not in code
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["build"] == build
        await ws.close()


@pytest.mark.asyncio
async def test_all_off_in_groups_tells_what_stayed_on(module, mocker):
    mocker.patch.object(dash_module, "ALL_OFF_CHECK", 0.1)
    mocker.patch.object(dash_module, "ALL_OFF_PAUSE", 0.01)
    mocker.patch.object(dash_module, "ALL_OFF_GROUP", 2)
    sleeps = []
    real_sleep = asyncio.sleep

    async def spy(delay, *args):
        sleeps.append(delay)
        await real_sleep(delay, *args)

    mocker.patch.object(dash_module.asyncio, "sleep", spy)
    _, answer = await pair(module)
    on = model.all_off(module.data["tiles"])
    assert len(on) >= 4
    module.fake.fail[on[0]] = "No answer, choose one of on off"
    module.fake.silent.add(on[1])
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json({"type": "action", "action": "all_off", "room": None})
        result = await next_of(ws, "all_off")
    assert sorted(x["id"] for x in result["left"]) == sorted(on[:2])
    assert result["done"] == len(on) - 2
    # groups of two with a pause between them
    assert sleeps.count(0.01) == (len(on) + 1) // 2 - 1


def test_clean_pin():
    assert model.clean_pin(" 1234 ") == "1234"
    assert model.clean_pin("12345678") == "12345678"
    assert model.clean_pin("123") is None
    assert model.clean_pin("12a4") is None
    assert model.clean_pin("") is None


@pytest.mark.asyncio
async def test_settings_pin(module):
    _, answer = await pair(module)
    tablet = next(iter(module.tablets.values()))
    tablet["place"] = "wall"
    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["tablet"]["pin"] is False
        module._attr_settings_pin = "4711"
        module.set_attr_settings_pin(module.hash)
        assert (await next_of(ws, "tablet"))["tablet"]["pin"] is True
        # locked: the layout does not change
        await ws.send_json({"type": "layout", "layout": {"theme": "light"}})
        await next_of(ws, "locked")
        assert (tablet.get("layout") or {}).get("theme") != "light"
        await ws.send_json({"type": "unlock", "pin": "0000"})
        wrong = await next_of(ws, "unlocked")
        assert wrong["ok"] is False and wrong["wait"] is False
        await ws.send_json({"type": "unlock", "pin": "4711"})
        assert (await next_of(ws, "unlocked"))["ok"] is True
        await ws.send_json({"type": "layout", "layout": {"theme": "light"}})
        assert (await next_of(ws, "tablet"))["tablet"]["layout"]["theme"] == "light"
        # too many wrong PINs: even the right one waits
        module.unlocked = {}
        for _ in range(dash_module.PIN_TRIES):
            await ws.send_json({"type": "unlock", "pin": "0000"})
            last = await next_of(ws, "unlocked")
        assert last["wait"] is True
        await ws.send_json({"type": "unlock", "pin": "4711"})
        assert (await next_of(ws, "unlocked"))["ok"] is False


def test_bins_and_calendar():
    assert model.is_bin("Gelbe Tonne")
    assert model.is_bin("Biotonne") and model.is_bin("Restmüll")
    assert model.is_bin("Altpapier") and model.is_bin("Gelber Sack")
    assert model.is_bin("Recycling bin")
    assert not model.is_bin("Biologie Nachhilfe")
    assert not model.is_bin("Zahnarzt")
    fake = FakeFhem()
    text = "\n".join(f"{c}|{e[0]}|{e[1]}|{e[2]}" for c, e in fake.calendar)
    events = model.parse_calendar(text + "\nbroken line\nX|a|b|c")
    assert len(events) == 7
    # "Gelb" alone is a pickup: most entries of its calendar are
    assert model.bin_calendars(events) == {"Muell"}
    result = model.calendar(events, fake_home.NOW)
    assert result["bins"] == [{"what": "Gelb", "day": 1}]
    names = [(e["summary"], e["day"]) for e in result["entries"]]
    assert ("Geburtstag Oma", 0) in names and ("Zahnarzt", 1) in names
    assert ("Elternabend", 0) in names and ("Urlaub", 5) not in names
    oma = next(e for e in result["entries"] if e["summary"] == "Geburtstag Oma")
    assert oma["allday"] and oma["at"] == ""


def test_bin_devices():
    infos = {
        "abfall": {"NAME": "abfall", "TYPE": "ABFALL", "readings": {"next_text": "Biotonne", "next_days": "1"}},
        "later": {"NAME": "later", "TYPE": "ABFALL", "readings": {"next_text": "Papier", "next_days": "4"}},
    }
    assert model.in_header(infos["abfall"])
    assert model.bin_devices(infos) == [{"what": "Biotonne", "day": 1}]


@pytest.mark.asyncio
async def test_calendar_in_header(module):
    module.calendar_events = await module.fetch_calendars()
    head = module.make_header()
    assert head["calendar"]["bins"] == [{"what": "Gelb", "day": 1}]
    assert any(e["summary"] == "Zahnarzt" for e in head["calendar"]["entries"])


def test_weather_warning():
    def forecast(**hours):
        readings = {}
        for i, values in hours.items():
            prefix = f"next_hours_{int(i[1:]):02d}_"
            readings[prefix + "time"] = f"Di {values.get('at', '18:00')}"
            for key in ("condition", "precipitation", "temperature", "windspeed"):
                if key in values:
                    readings[prefix + key] = values[key]
        return {"readings": readings}

    assert model.weather_warning({"readings": {}}) is None
    assert model.weather_warning(
        forecast(h0={"precipitation": "10", "temperature": "5"})
    ) is None
    assert model.weather_warning(
        forecast(
            h0={"precipitation": "10", "temperature": "5"},
            h1={"at": "19:00", "precipitation": "70", "temperature": "5"},
        )
    ) == {"kind": "rain", "at": "19:00"}
    assert model.weather_warning(forecast(h0={"temperature": "-1"}))["kind"] == "frost"
    assert model.weather_warning(forecast(h0={"windspeed": "75"}))["kind"] == "storm"
    assert (
        model.weather_warning(forecast(h0={"condition": "Leichtes Gewitter"}))["kind"]
        == "storm"
    )


def test_weather_warning_in_header():
    infos = FakeFhem().infos(["Wetter"])
    assert model.weather(infos)["warn"] == {"kind": "rain", "at": "20:00"}


def test_routine_steps():
    tiles = {
        "lamp": {"id": "lamp", "kind": "light", "state": {"on": True}},
        "fridge": {"id": "fridge", "kind": "outlet", "state": {"on": True}, "keep_on": True},
        "dark": {"id": "dark", "kind": "light", "state": {"on": False}},
        "blind": {"id": "blind", "kind": "blind", "state": {"position": 60}},
        "shut": {"id": "shut", "kind": "blind", "state": {"position": 0}},
    }
    off, close = ["lamp", "fridge", "dark", "gone"], ["blind", "shut"]
    steps, undo = model.routine_steps(tiles, "away", off, close)
    assert steps == [("lamp", "off", None)]
    assert undo == [("lamp", "on", None)]
    steps, undo = model.routine_steps(tiles, "night", off, close)
    assert steps == [("lamp", "off", None), ("blind", "position", 0)]
    assert undo == [("lamp", "on", None), ("blind", "position", 60)]


@pytest.mark.asyncio
async def test_good_night_and_undo(module):
    _, answer = await pair(module)
    tiles = module.data["tiles"]
    on = [i for i, t in tiles.items() if t["kind"] in model.SWITCHABLE and t["state"].get("on")]
    blinds = [i for i, t in tiles.items() if t["kind"] == "blind"]
    open_blind = next(i for i in blinds if tiles[i]["state"].get("position"))
    position = tiles[open_blind]["state"]["position"]
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        module.fake.sets.clear()
        await ws.send_json(
            {"type": "action", "action": "routine", "mode": "night", "off": on, "close": blinds}
        )
        done = await next_of(ws, "routine")
        assert done["mode"] == "night" and done["undo"] and done["failed"] == []
        assert f"{on[0]} off" in module.fake.sets
        assert f"{open_blind} pct 0" in module.fake.sets
        module.fake.sets.clear()
        await ws.send_json({"type": "action", "action": "undo"})
        assert (await next_of(ws, "undone"))["failed"] == []
        assert f"{on[0]} on" in module.fake.sets
        assert f"{open_blind} pct {position}" in module.fake.sets
        # only once
        module.fake.sets.clear()
        await ws.send_json({"type": "action", "action": "undo"})
        await asyncio.sleep(0.2)
        assert module.fake.sets == []


def test_weather_forecast():
    weather = model.weather(FakeFhem().infos(["Wetter"]))
    assert len(weather["hours"]) == 24
    assert weather["hours"][0] == {
        "at": "17:00",
        "temp": 9,
        "rain": 10,
        "condition": "Bewölkt",
    }
    assert len(weather["days"]) == 7
    assert weather["days"][1] == {
        "name": "Dienstag",
        "condition": "Regen",
        "high": 11,
        "low": 6,
        "rain": 90,
    }
    # the FHEM Weather module, here counting from fc1
    info = {
        "TYPE": "Weather",
        "NAME": "w",
        "readings": {
            "fc1_day_of_week": "Mo",
            "fc1_condition": "sonnig",
            "fc1_high_c": "12",
            "fc1_low_c": "3",
            "fc2_day_of_week": "Di",
            "fc2_high_c": "10",
            "fc2_low_c": "2",
        },
    }
    days = model.weather({"w": info})["days"]
    assert [d["name"] for d in days] == ["Mo", "Di"]
    assert days[0]["rain"] is None


def test_parse_notices():
    notices = model.parse_notices(
        "Briefkasten Post ist da; Keller:water=wet Wasser im Keller\nGarage"
    )
    assert notices == [
        {"device": "Briefkasten", "reading": "state", "value": None, "text": "Post ist da"},
        {"device": "Keller", "reading": "water", "value": "wet", "text": "Wasser im Keller"},
        {"device": "Garage", "reading": "state", "value": None, "text": ""},
    ]
    assert model.parse_notices(model.format_notices(notices)) == notices

    def info(readings, sets=""):
        return {"NAME": "x", "sets": sets, "readings": readings, "times": {}}

    assert model.notice_active(notices[0], info({"state": "on"}))
    assert not model.notice_active(notices[0], info({"state": "off"}))
    assert model.notice_active(notices[1], info({"water": "WET"}))
    assert not model.notice_active(notices[1], info({"water": "on"}))
    assert model.notice_reset(notices[0], info({}, "on off")) == "off"
    assert model.notice_reset(notices[0], info({}, "")) is None
    assert model.notice_reset(notices[1], info({}, "on off")) is None


@pytest.mark.asyncio
async def test_notice_shown_and_ticked_off(module):
    module._attr_notices = "Briefkasten Post ist da; wz_Fenster:contact=open Fenster zu!"
    await module.reload()
    texts = [n["text"] for n in module.head["notices"]]
    assert sorted(texts) == ["Fenster zu!", "Post ist da"]
    mail = next(n for n in module.head["notices"] if n["id"] == "Briefkasten")
    assert mail["reset"] is True
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        # the tick sets the dummy off, its event takes the notice away
        module.fake.sets.clear()
        await ws.send_json({"type": "action", "action": "notice_done", "id": "Briefkasten"})
        await asyncio.sleep(0.1)
        assert module.fake.sets == ["Briefkasten off"]
        await module.handle_event("Briefkasten", "state", "off")
        await module.update_header()
        assert [n["id"] for n in module.head["notices"]] == ["wz_Fenster"]
        # no command to reset a window: hidden until it reports again
        await ws.send_json({"type": "action", "action": "notice_done", "id": "wz_Fenster"})
        await asyncio.sleep(0.1)
        assert module.head["notices"] == []
        # a tablet adds a notice in the details of a device
        await ws.send_json({"type": "notice", "id": "wz_Stehlampe", "on": True, "text": "Lampe an"})
        await asyncio.sleep(0.1)
        assert module.head["notice_setup"]["wz_Stehlampe"] == "Lampe an"
        assert any(n["id"] == "wz_Stehlampe" for n in module.head["notices"])
        await ws.send_json({"type": "notice", "id": "wz_Stehlampe", "on": False})
        await asyncio.sleep(0.1)
        assert "wz_Stehlampe" not in module.head["notice_setup"]


def test_thermostat_heats_and_range():
    fake = FakeFhem()
    tiles = model.build(fake.infos(fake.devices))["tiles"]
    living = tiles["wz_Heizung"]
    assert living["state"]["valve"] == 35 and living["state"]["heating"] is True
    assert (living["min"], living["max"], living["step"]) == (4.5, 30, 0.5)
    # no valve, no action: the tablets guess from the temperatures
    assert "heating" not in tiles["bad_Heizung"]["state"]

    def thermostat(readings, sets="desired-temp:slider,5,0.5,29"):
        return {"NAME": "t", "TYPE": "x", "sets": sets, "readings": readings}

    assert model.heating_state(thermostat({"actuator": "0 %"})) == {
        "valve": 0,
        "heating": False,
    }
    assert model.heating_state(thermostat({"hvac_action": "heating"})) == {"heating": True}
    assert model.heating_state(thermostat({"running_state": "idle"})) == {"heating": False}
    assert model.heating_state(thermostat({})) == {}
    assert model.target_range(thermostat({})) == (5, 29, 0.5)
    assert model.target_range(thermostat({}, "desired-temp:4.5,5.0,6.0,30.5")) == (
        4.5,
        30.5,
        0.5,
    )
    assert model.target_range(thermostat({}, "desired-temp")) == (4.5, 30.0, 0.5)


def test_appliance_watch():
    watch = model.ApplianceWatch()
    minute = 60
    assert watch.feed(2, 0) is None
    assert watch.feed(2100, 0) == "start"
    assert watch.feed(150, 30 * minute) is None
    assert watch.feed(3, 45 * minute) is None
    assert watch.tick(50 * minute) is None
    # still running: plugs report changes only
    assert watch.tick(44 * minute) is None
    assert watch.tick(56 * minute) == "done" and watch.seconds == 45 * minute
    # a coffee machine: high power, but short
    assert watch.feed(1200, 0) == "start"
    assert watch.feed(1200, 4 * minute) is None
    assert watch.feed(1, 6 * minute) is None
    assert watch.tick(20 * minute) == "short"
    # a TV: long, but never much power
    watch.feed(90, 0)
    watch.feed(110, 120 * minute)
    watch.feed(2, 125 * minute)
    assert watch.tick(140 * minute) == "short"
    assert model.parse_appliances("A:washer, B:none,C:toaster") == {"A": "washer", "B": "none"}
    assert model.format_appliances({"B": "none", "A": "washer"}) == "A:washer,B:none"
    assert model.typical_seconds([3000, 3600, 4000]) == 3600
    assert model.typical_seconds([]) is None
    assert model.appliance_guess("Steckdose Waschmaschine") == "washer"
    assert model.appliance_guess("Plug 3") is None


@pytest.mark.asyncio
async def test_appliance_asked_then_done(module, mocker):
    clock = [100000.0]
    mocker.patch.object(dash_module.time, "time", lambda: clock[0])
    minute = 60

    async def power(value, minutes):
        clock[0] = 100000.0 + minutes * minute
        await module.handle_event("wz_Fernseher", "power", str(value))

    async def tick(minutes):
        clock[0] = 100000.0 + minutes * minute
        for name, watch in list(module.watches.items()):
            await module.appliance_result(name, watch, watch.tick(clock[0]))

    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        # the first long program with a peak: the tablets ask
        await power(2000, 0)
        await power(400, 30)
        await power(2, 40)
        await tick(52)
        ask = module.make_header()["appliances"]["ask"]
        assert [a["id"] for a in ask] == ["wz_Fernseher"]
        await ws.send_json({"type": "appliance", "id": "wz_Fernseher", "what": "washer"})
        head = (await next_of(ws, "header"))["header"]
        assert head["appliances"]["ask"] == []
        assert module._attr_appliances == "wz_Fernseher:washer"
        # the next program runs with "about ... left", then it is done
        await power(1800, 100)
        await power(300, 110)
        running = module.make_header()["appliances"]["running"][0]
        assert running["what"] == "washer" and running["typical"] == 40 * minute
        await power(1, 135)
        await tick(146)
        done = await next_of(ws, "appliance_done")
        assert done["what"] == "washer" and done["id"] == "wz_Fernseher"
        while not (await next_of(ws, "header"))["header"]["appliances"]["done"]:
            pass
        await ws.send_json({"type": "appliance_seen", "id": "wz_Fernseher"})
        head = (await next_of(ws, "header"))["header"]
        assert head["appliances"]["done"] == []


def test_smoke_and_water_detectors():
    fake = FakeFhem()
    tiles = model.build(fake.infos(fake.devices))["tiles"]
    assert tiles["ku_Rauchmelder"]["kind"] == "smoke"
    assert tiles["ku_Rauchmelder"]["state"]["alarm"] is False
    assert tiles["ku_Wasser"]["kind"] == "water"
    assert model.alarms(tiles) == []

    def detector(readings, sets=""):
        return {"NAME": "d", "TYPE": "dummy", "sets": sets, "readings": readings}

    for readings in (
        {"smoke": "true"},
        {"smoke_detect": "Melder_Flur"},
        {"fire": "ALARM"},
        {"smoke": "on", "temperature": "21"},
    ):
        info = detector(readings)
        assert model.kind_of(info) == "smoke"
        assert model.hazard_alarm("smoke", info) is True
    assert model.hazard_alarm("smoke", detector({"smoke_detect": "none"})) is False
    assert model.hazard_alarm("water", detector({"water_leak": "wet"})) is True
    assert model.hazard_alarm("water", detector({"moistureDetected": "no"})) is False
    # a valve with a leak reading is no detector
    assert model.kind_of(detector({"leak": "false"}, "on off")) != "water"


def test_alarm_system_modes():
    def system(state, sets="armAway armHome disarm"):
        return {"NAME": "a", "TYPE": "dummy", "sets": sets, "readings": {"state": state}}

    assert model.alarm_mode(system("disarmed")) == "off"
    assert model.alarm_mode(system("armed_away")) == "away"
    assert model.alarm_mode(system("armed home")) == "home"
    assert model.alarm_mode(system("triggered")) == "triggered"
    assert model.alarm_mode(system("Alarm")) == "triggered"
    assert model.alarm_mode(system("on", "on off")) == "away"
    assert model.alarm_commands(system("off")) == {
        "away": "armAway",
        "home": "armHome",
        "off": "disarm",
    }
    assert model.alarm_commands(system("off", "on off")) == {"away": "on", "off": "off"}
    found = model.alarm_system(system("triggered"))
    assert found["modes"] == ["away", "home", "off"]
    assert model.alarms({}, found)[0]["kind"] == "intrusion"
    assert model.alarm_system(None) is None


@pytest.mark.asyncio
async def test_alarm_on_all_tablets(module):
    _, answer = await pair(module)
    tablet = next(iter(module.tablets.values()))
    # a tablet of another room also gets the alarm
    tablet["rooms"] = ["Bad"]
    async with aiohttp.ClientSession() as session:
        ws, welcome = await connect(session, module, answer["token"])
        assert welcome["header"]["alarm"]["alarms"] == []
        await module.handle_event("ku_Rauchmelder", "smoke", "true")
        head = (await next_of(ws, "header"))["header"]
        alarm = head["alarm"]["alarms"][0]
        assert alarm["id"] == "ku_Rauchmelder" and alarm["kind"] == "smoke"
        assert alarm["room"] == "Küche"
        await module.handle_event("ku_Rauchmelder", "smoke", "false")
        assert (await next_of(ws, "header"))["header"]["alarm"]["alarms"] == []
        await ws.close()


@pytest.mark.asyncio
async def test_arm_and_disarm_with_pin(module):
    module._attr_alarm_system = "Alarmanlage"
    module._attr_alarm_pin = "2580"
    await module.reload()
    # no tile, "All off" must never disarm it
    assert "Alarmanlage" not in module.data["tiles"]
    system = module.head["alarm"]["system"]
    assert system["mode"] == "off" and system["pin"] is True
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        module.fake.sets.clear()
        await ws.send_json({"type": "action", "action": "alarm_mode", "mode": "away"})
        assert (await next_of(ws, "alarm_mode"))["ok"] is True
        assert module.fake.sets == ["Alarmanlage armAway"]
        await module.handle_event("Alarmanlage", "state", "triggered")
        head = (await next_of(ws, "header"))["header"]
        assert head["alarm"]["alarms"][0]["kind"] == "intrusion"
        # disarming needs the PIN
        module.fake.sets.clear()
        await ws.send_json({"type": "action", "action": "alarm_mode", "mode": "off"})
        wrong = await next_of(ws, "alarm_mode")
        assert wrong["ok"] is False and wrong["wrong"] is True
        await ws.send_json(
            {"type": "action", "action": "alarm_mode", "mode": "off", "pin": "2580"}
        )
        assert (await next_of(ws, "alarm_mode"))["ok"] is True
        assert module.fake.sets == ["Alarmanlage disarm"]
        await ws.close()


def test_layout_simple_display():
    for value in ("auto", "on", "off"):
        assert clean_layout({"lite": value}) == {"lite": value}
    assert clean_layout({"lite": "fast"}) == {}


def test_layout_screensaver_minutes():
    assert clean_layout({"saver": 10}) == {"saver": 10}
    assert clean_layout({"saver": 0}) == {"saver": 0}
    for bad in (7, "5", False, True, None, 300):
        assert clean_layout({"saver": bad}) == {}


def test_motion_tile_knows_since_when():
    fake = FakeFhem()
    tiles = model.build(fake.infos(fake.devices))["tiles"]
    motion = next(t for t in tiles.values() if t["kind"] == "motion")
    assert motion["state"]["occupied"] is False
    assert motion["state"]["since"]


def test_may_open_windows():
    assert model.clean_window("7:00-20:00") == "07:00-20:00"
    assert model.clean_window("22:00 - 6:30") == "22:00-06:30"
    for bad in ("", "7-20", "25:00-06:00", "08:00-08:00", "08:61-09:00", None):
        assert model.clean_window(bad) is None
    windows = model.parse_may_open("Hoftor=07:00-20:00, Garage=8:00-18:00,Tor=x")
    assert windows == {"Hoftor": "07:00-20:00", "Garage": "08:00-18:00"}
    assert model.parse_may_open(model.format_may_open(windows)) == windows
    assert model.may_open_now("07:00-20:00", 7 * 60)
    assert not model.may_open_now("07:00-20:00", 20 * 60)
    # over midnight
    assert model.may_open_now("22:00-06:00", 23 * 60)
    assert model.may_open_now("22:00-06:00", 60)
    assert not model.may_open_now("22:00-06:00", 12 * 60)


@pytest.mark.asyncio
async def test_may_open_set_on_tablet(module):
    module._attr_may_open = "wz_Fenster=07:00-20:00,wz_Stehlampe=07:00-20:00"
    await module.reload()
    assert module.data["tiles"]["wz_Fenster"]["may_open"] == "07:00-20:00"
    # only doors and windows
    assert "may_open" not in module.data["tiles"]["wz_Stehlampe"]
    window = next(o for o in module.head["open"] if o["id"] == "wz_Fenster")
    assert window["may_open"] == "07:00-20:00"
    _, answer = await pair(module)
    async with aiohttp.ClientSession() as session:
        ws, _ = await connect(session, module, answer["token"])
        await ws.send_json({"type": "may_open", "id": "bad_Fenster", "window": "9:00-17:30"})
        await asyncio.sleep(0.1)
        assert module.data["tiles"]["bad_Fenster"]["may_open"] == "09:00-17:30"
        await ws.send_json({"type": "may_open", "id": "wz_Fenster", "window": ""})
        await asyncio.sleep(0.1)
        assert "may_open" not in module.data["tiles"]["wz_Fenster"]
        assert module.may_open() == {
            "bad_Fenster": "09:00-17:30",
            "wz_Stehlampe": "07:00-20:00",
        }
        await ws.close()
