import asyncio
import html
import json
import logging

import pytest

from fhempy.lib.autodiscovery import catalog, engine as engine_module
from fhempy.lib.autodiscovery.engine import Engine, define_arg


class FakeFrontend:
    def __init__(self):
        self.hash = {"NAME": "fhempy_discovery"}
        self.popups = []
        self.notified = []
        self.changes = 0

    async def candidates_changed(self):
        self.changes += 1

    async def zigbee_changed(self):
        self.zigbee_changes = getattr(self, "zigbee_changes", 0) + 1

    def popup_enabled(self):
        return True

    async def show_popup(self, candidates):
        self.popups.append([c["id"] for c in candidates])

    async def notify_phone(self, candidates):
        self.notified.append([c["id"] for c in candidates])


@pytest.fixture
def fhem_mock(mocker):
    """Answers the Perl commands of the engine: nothing exists in FHEM,
    names are free, the store is empty."""
    commands = []
    defines = []

    async def send(hash, cmd):
        commands.append(cmd)
        if "getKeyValue" in cmd:
            return ""
        if "while (defined" in cmd:
            return cmd.split("my $n = ")[1].split(";;")[0].strip("\"'")
        if "return 0" in cmd:
            return "0"
        return ""

    async def define(hash, definition):
        defines.append(definition)
        return ""

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=send)
    mocker.patch.object(engine_module.fhem, "CommandDefine", side_effect=define)
    return commands, defines


@pytest.fixture
def engine():
    eng = Engine(logging.getLogger(__name__))
    eng.catalog = catalog.load()
    eng.running = True
    frontend = FakeFrontend()
    eng.frontends.append(frontend)
    return eng


def cast_candidate(eng, name="Living Room", id="abc"):
    values = {"name": "x", "ip": "1.2.3.4", "txt": {"fn": name, "id": id}}
    entry, rule = next(
        catalog.match_mdns(eng.catalog, "_googlecast._tcp.local.", values)
    )
    return catalog.candidate(entry, rule, values, "mdns"), rule


@pytest.mark.asyncio
async def test_found_shows_popup_once(engine, fhem_mock, mocker):
    mocker.patch.object(engine_module, "POPUP_DELAY", 0)
    candidate, rule = cast_candidate(engine)
    await engine.found(candidate, rule)
    await engine.found(dict(candidate), rule)
    await engine._popup_task
    frontend = engine.frontends[0]
    assert frontend.popups == [["googlecast:abc"]]
    assert frontend.notified == [["googlecast:abc"]]
    assert engine.shown == {"googlecast:abc"}
    assert [c["id"] for c in engine.open_candidates()] == ["googlecast:abc"]
    # shown is stored for the other fhempy instances
    assert any("setKeyValue" in cmd for cmd in fhem_mock[0])


@pytest.mark.asyncio
async def test_existing_device_is_not_offered(engine, fhem_mock, mocker):
    async def exists(hash, cmd):
        return "1"

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=exists)
    candidate, rule = cast_candidate(engine)
    await engine.found(candidate, rule)
    assert engine.open_candidates() == []
    assert engine._popup_task is None


def fhem_devices(mocker, devices):
    """FHEM with the devices {name: DEF} of the module googlecast"""

    async def send(hash, cmd):
        if "getKeyValue" in cmd or "setKeyValue" in cmd:
            return ""
        if "grep { !defined" in cmd:
            names = [n.strip("'\"") for n in cmd.rsplit(" (", 1)[1][:-2].split(", ")]
            return " ".join(n for n in names if n not in devices)
        if "return '';;" in cmd:
            unique = cmd.split("my $u = (")[1].split(" =~")[0].strip("'\"").lower()
            for name, definition in devices.items():
                if unique in definition.lower():
                    return name
            return ""
        return ""

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=send)


@pytest.mark.asyncio
async def test_deleted_device_is_offered_again(engine, mocker):
    devices = {"Living_Room": "Living Room"}
    fhem_devices(mocker, devices)
    candidate, rule = cast_candidate(engine)
    await engine.found(candidate, rule)
    assert candidate["status"] == engine_module.STATUS_EXISTS
    assert candidate["device"] == "Living_Room"
    assert engine.open_candidates() == []

    # still there
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_EXISTS

    # renamed in FHEM
    devices["Wohnzimmer"] = devices.pop("Living_Room")
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_EXISTS
    assert candidate["device"] == "Wohnzimmer"

    # deleted: new again, in the list but without popup
    devices.clear()
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_NEW
    assert candidate["deleted"] is True
    assert "device" not in candidate
    assert [c["id"] for c in engine.open_candidates()] == [candidate["id"]]
    assert engine._popup_task is None
    assert engine.frontends[0].changes == 1

    # created again
    mocker.patch.object(
        engine_module.fhem, "CommandDefine", mocker.AsyncMock(return_value="")
    )
    assert await engine.create({"NAME": "x"}, candidate["id"], "", {}) == ""
    assert candidate["status"] == engine_module.STATUS_CREATED
    assert "deleted" not in candidate
    devices[candidate["device"]] = "Living Room"
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_CREATED

    # deleted again
    devices.clear()
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_NEW


@pytest.mark.asyncio
async def test_deleted_ignored_device_stays_ignored(engine, mocker):
    devices = {"Living_Room": "Living Room"}
    fhem_devices(mocker, devices)
    candidate, rule = cast_candidate(engine)
    await engine.found(candidate, rule)
    engine.ignored.add(candidate["id"])
    devices.clear()
    await engine.recheck()
    assert candidate["status"] == engine_module.STATUS_IGNORED


@pytest.mark.asyncio
async def test_get_candidates_lists_all_but_checking(mocker):
    from fhempy.lib.autodiscovery.autodiscovery import autodiscovery
    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("autodiscovery")
    device = autodiscovery(logging.getLogger(__name__))
    device.engine = mocker.MagicMock()
    device.engine.recheck = mocker.AsyncMock()
    device.engine.candidates = {
        s: {"id": s, "status": s, "device": "d", "create": print}
        for s in ("new", "ignored", "exists", "created", "checking")
    }
    listed = json.loads(await device.get_candidates({}, {}))
    device.engine.recheck.assert_awaited_once()
    assert [c["id"] for c in listed] == ["new", "ignored", "exists", "created"]
    assert listed[2] == {"id": "exists", "status": "exists", "device": "d"}


@pytest.mark.asyncio
async def test_ignore_and_unignore(engine, fhem_mock):
    candidate, rule = cast_candidate(engine)
    engine.shown.add(candidate["id"])
    await engine.found(candidate, rule)
    await engine.ignore(candidate["id"])
    assert engine.open_candidates() == []
    assert candidate["id"] in engine.ignored
    await engine.unignore(candidate["id"])
    assert [c["id"] for c in engine.open_candidates()] == [candidate["id"]]


@pytest.mark.asyncio
async def test_create_quotes_define_arguments(engine, fhem_mock):
    candidate, rule = cast_candidate(engine)
    engine.shown.add(candidate["id"])
    await engine.found(candidate, rule)
    ret = await engine.create({"NAME": "x"}, candidate["id"], "", {})
    assert ret == ""
    assert fhem_mock[1] == ['Living_Room fhempy googlecast "Living Room"']
    assert candidate["status"] == engine_module.STATUS_CREATED
    # the popup links to the new device
    assert candidate["device"] == "Living_Room"


@pytest.mark.asyncio
async def test_get_device_of_created_candidate(mocker):
    from fhempy.lib.autodiscovery.autodiscovery import autodiscovery
    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("autodiscovery")
    device = autodiscovery(logging.getLogger(__name__))
    device.engine = mocker.MagicMock()
    device.engine.candidates = {"mqtt:x": {"device": "MQTT2_Lamp"}, "mqtt:y": {}}
    assert await device.get_device({}, {"id": "mqtt:x"}) == "MQTT2_Lamp"
    assert await device.get_device({}, {"id": "mqtt:y"}) == ""
    assert await device.get_device({}, {"id": "unknown"}) == ""


@pytest.mark.asyncio
async def test_get_device_of_added_resident_and_tag(mocker):
    from fhempy.lib.autodiscovery import residents
    from fhempy.lib.autodiscovery.autodiscovery import autodiscovery
    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("autodiscovery")
    device = autodiscovery(logging.getLogger(__name__))
    device.hash = {"NAME": "autodiscovery"}
    device.engine = mocker.MagicMock()
    device.engine.candidates = {}
    mocker.patch.object(
        residents, "create_resident", mocker.AsyncMock(return_value=("", "rr_Anna"))
    )
    mocker.patch.object(
        residents,
        "create_tag",
        mocker.AsyncMock(return_value=("", "presence_Keys")),
    )
    assert await device.set_addResident({}, {"person": "Anna", "mac": "x"}) == ""
    assert await device.set_addTag({}, {"title": "Keys", "address": "y"}) == ""
    # the dialogs link to the new devices
    assert await device.get_device({}, {"id": "resident"}) == "rr_Anna"
    assert await device.get_device({}, {"id": "tag"}) == "presence_Keys"


@pytest.mark.asyncio
async def test_create_requires_params(engine, fhem_mock):
    values = {"txt": {"sf": "1", "id": "AA:BB"}, "name": "Velux"}
    entry, rule = next(catalog.match_mdns(engine.catalog, "_hap._tcp.local.", values))
    candidate = catalog.candidate(entry, rule, values, "mdns")
    engine.shown.add(candidate["id"])
    await engine.found(candidate, rule)
    ret = await engine.create({"NAME": "x"}, candidate["id"], "", {})
    assert ret.startswith("Please fill in")
    ret = await engine.create({"NAME": "x"}, candidate["id"], "", {0: "123-45-678"})
    assert ret == ""
    assert fhem_mock[1] == ["Velux fhempy homekit AA:BB 123-45-678"]


@pytest.mark.asyncio
async def test_create_with_set_uses_existing_controller(engine, fhem_mock, mocker):
    commands = fhem_mock[0]

    async def send(hash, cmd):
        commands.append(cmd)
        if "FHEMPYTYPE} // '') eq" in cmd:
            return "matter_ctrl"
        return ""

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=send)
    values = {"address": "AA:BB"}
    entry, rule = next(
        catalog.match_ble(
            engine.catalog,
            "",
            {},
            {"0000fff6-0000-1000-8000-00805f9b34fb"},
            -50,
        )
    )
    candidate = catalog.candidate(entry, rule, values, "ble")
    engine.shown.add(candidate["id"])
    await engine.found(candidate, rule)
    ret = await engine.create({"NAME": "x"}, candidate["id"], "", {0: "3497-011-2332"})
    assert ret == ""
    assert "set matter_ctrl pair_new_device 3497-011-2332" in commands[-1]
    assert fhem_mock[1] == []


@pytest.mark.asyncio
async def test_report_calls_create_callback(engine, fhem_mock):
    created = []

    async def create():
        created.append(True)
        return ""

    await engine.report("mqtt_ha_discovery", "0x1234", "Kitchen plug", "MQTT", create)
    candidate = engine.candidates["mqtt_ha_discovery:0x1234"]
    assert candidate["status"] == engine_module.STATUS_NEW
    assert await engine.create({"NAME": "x"}, candidate["id"], "", {}) == ""
    assert created == [True]


@pytest.mark.asyncio
async def test_not_running_ignores_found(engine, fhem_mock):
    engine.running = False
    candidate, rule = cast_candidate(engine)
    await engine.found(candidate, rule)
    assert engine.candidates == {}


def test_define_arg():
    assert define_arg("abc") == "abc"
    assert define_arg("Living Room") == '"Living Room"'
    assert define_arg('a"b') == '"a\\"b"'


@pytest.mark.asyncio
async def test_frontend_update_while_checking_if_device_exists(engine, mocker):
    # the frontend reads the candidates while FHEM answers the exists check
    started = asyncio.Event()
    answer = asyncio.Event()

    async def send(hash, cmd):
        if "return '';;" in cmd:
            started.set()
            await answer.wait()
            return ""
        return ""

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=send)
    candidate, rule = cast_candidate(engine)
    engine.shown.add(candidate["id"])
    task = asyncio.create_task(engine.found(candidate, rule))
    await started.wait()
    assert engine.open_candidates() == []
    answer.set()
    await task
    assert [c["id"] for c in engine.open_candidates()] == [candidate["id"]]


@pytest.mark.asyncio
async def test_failed_exists_check_is_retried(engine, mocker):
    async def send(hash, cmd):
        raise ConnectionError("FHEM gone")

    mocker.patch.object(engine_module.fhem, "sendCommandHash", side_effect=send)
    candidate, rule = cast_candidate(engine)
    with pytest.raises(ConnectionError):
        await engine.found(candidate, rule)
    assert engine.candidates == {}


@pytest.mark.asyncio
async def test_detail_page_shows_bluez_command(mocker):
    from fhempy.lib.autodiscovery.autodiscovery import autodiscovery
    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("autodiscovery")
    from fhempy.lib.core import ble_scanner

    device = autodiscovery(logging.getLogger(__name__))
    device.engine = mocker.MagicMock()
    device.engine.ble_scanner.passive_problem = ""
    assert device.ble_warning_html() == ""
    device.engine.ble_scanner.passive_problem = "experimental"
    warning = device.ble_warning_html()
    assert "--experimental" in device.ble_warning()
    assert "Copy command" in warning
    assert "fhempy-experimental.conf" in warning
    assert html.escape(ble_scanner.EXPERIMENTAL_COMMAND) in warning
    device.engine.ble_scanner.passive_problem = "kernel"
    assert "Copy command" not in device.ble_warning_html()


@pytest.mark.asyncio
async def test_create_tag_returns_device_name(fhem_mock, mocker):
    from fhempy.lib.autodiscovery import residents

    mocker.patch.object(residents.fhem, "CommandAttr", mocker.AsyncMock())
    ret = await residents.create_tag({"NAME": "x"}, "Keys", "AA:BB")
    assert ret == ("", "presence_Keys")
    assert fhem_mock[1] == ["presence_Keys fhempy ble_presence AA:BB"]


# runs the exists command like BindingsIo: the command comes as JSON from
# fhempy (decoded in non-utf8 mode), DEF are UTF-8 bytes like in FHEM
_PERL_EXISTS_HARNESS = r"""
use strict; use warnings; use JSON;
our %defs = (
  cast1 => { FHEMPYTYPE => 'googlecast', DEF => "googlecast K\xc3\xbcche" },
  cast2 => { FHEMPYTYPE => 'googlecast', DEF => 'googlecast "Living Room"' },
);
sub main::ReadingsVal { return "" }
%main::defs = %defs;
local $/; my $msg = JSON->new->allow_nonref->decode(<STDIN>);
my $ret = eval $msg->{command}; die $@ if $@;
print $ret;
"""


def _perl_exists(value):
    import shutil
    import subprocess

    if shutil.which("perl") is None:
        pytest.skip("perl not installed")
    msg = json.dumps(
        {"command": engine_module.exists_cmd("googlecast", value)},
        ensure_ascii=False,
    ).encode("utf-8")
    return subprocess.run(
        ["perl", "-e", _PERL_EXISTS_HARNESS],
        input=msg,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")


def test_exists_finds_device_with_umlaut_in_definition():
    assert _perl_exists("Küche") == "cast1"
    assert _perl_exists("KüCHE") == "cast1"


def test_exists_is_case_insensitive():
    assert _perl_exists("living room") == "cast2"
    assert _perl_exists("Bedroom") == ""


@pytest.mark.asyncio
async def test_ble_monitor_device_named_after_its_model(engine, fhem_mock, mocker):
    """The suggested name comes from the model the BLE parser recognizes in
    the advertisement's data, not from a generic name."""
    from types import SimpleNamespace

    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("ble_monitor")
    mocker.patch.object(engine_module, "POPUP_DELAY", 0)
    await engine._load_describers()
    assert "ble_monitor" in engine._describers

    def adv(data):
        return SimpleNamespace(
            local_name="Some name",
            service_uuids=[],
            service_data={},
            manufacturer_data={220: data},
            rssi=-50,
        )

    device = SimpleNamespace(address="aa:bb:cc:dd:ee:01", name="")
    # not the data of a known model yet: the sent name
    engine._ble_advertisement(device, adv(b"\x01\x02"))
    await asyncio.sleep(0.05)
    candidate = engine.candidates["ble_monitor:AA:BB:CC:DD:EE:01"]
    assert candidate["name"] == "Some_name"
    assert candidate["described"] is False
    # the model is recognized from a later advertisement
    oralb = bytes([0x06, 0x32, 0x6B, 3, 114, 0, 10, 2, 1, 0, 6])
    engine._ble_advertisement(device, adv(oralb))
    await asyncio.sleep(0.05)
    assert candidate["name"] == "Oral_B_IO_Series_7"
    assert candidate["title"] == "Oral-B IO Series 7"
    assert candidate["model"] == "Toothbrush"
    assert candidate["described"] is True


def _ble_adv(local_name, manufacturer_data, rssi=-50):
    from types import SimpleNamespace

    return SimpleNamespace(
        local_name=local_name,
        service_uuids=[],
        service_data={},
        manufacturer_data=manufacturer_data,
        rssi=rssi,
    )


@pytest.mark.asyncio
async def test_ble_monitor_offers_every_device_its_parser_knows(
    engine, fhem_mock, mocker
):
    """Not only the few devices with an own matcher: every device the BLE
    parser recognizes from its data is offered, others are not."""
    from types import SimpleNamespace

    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("ble_monitor")
    mocker.patch.object(engine_module, "POPUP_DELAY", 0)
    await engine._load_describers()
    # ThermoPro TP357: 21.5 C, 45 %
    thermopro = SimpleNamespace(address="aa:bb:cc:dd:ee:02", name="")
    data = {0xD7C2: bytes([0x00, 0x2D, 0x22, 0x2C])}
    engine._ble_advertisement(thermopro, _ble_adv("TP357 (EE02)", data))
    # a device the parser doesn't know
    other = SimpleNamespace(address="aa:bb:cc:dd:ee:03", name="")
    engine._ble_advertisement(other, _ble_adv("Phone", {0x1234: b"\x01\x02\x03"}))
    await asyncio.sleep(0.05)
    candidate = engine.candidates["ble_monitor:AA:BB:CC:DD:EE:02"]
    assert candidate["name"] == "Thermopro_TP357"
    assert candidate["model"] == "Thermometer"
    assert "ble_monitor:AA:BB:CC:DD:EE:03" not in engine.candidates
    # the unknown device is checked again only after DESCRIBE_RETRY
    assert engine._may_describe("ble_monitor:AA:BB:CC:DD:EE:03") is False


@pytest.mark.asyncio
async def test_ble_monitor_steps_back_for_modules_with_own_rule(engine, fhem_mock):
    """A device another module has a rule for isn't offered by ble_monitor."""
    from types import SimpleNamespace

    from fhempy.lib.pkg_installer import check_and_install_dependencies

    await check_and_install_dependencies("ble_monitor")
    await engine._load_describers()
    device = SimpleNamespace(address="aa:bb:cc:dd:ee:04", name="")
    engine._ble_advertisement(device, _ble_adv("CHEFBBQ", {}))
    await asyncio.sleep(0.05)
    modules = {c["module"] for c in engine.candidates.values()}
    assert modules == {"chefbbq"}
