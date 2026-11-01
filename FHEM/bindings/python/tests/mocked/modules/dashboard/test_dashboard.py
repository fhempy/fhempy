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
