import asyncio
import json
import logging
import os
import re
import subprocess
import sys

import pytest
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.matter_bridge import devices, runtime
from fhempy.lib.pkg_installer import check_and_install_dependencies
from fhempy.lib.matter_bridge.matter_bridge import format_manual_code, matter_bridge

logger = logging.getLogger(__name__)


def info(name="Device1", sets="", readings=None, attrs=None, type_="dummy", alias=""):
    return {
        "NAME": name,
        "TYPE": type_,
        "alias": alias,
        "sets": sets,
        "readings": readings or {},
        "attrs": attrs or {},
    }


def test_detect_type():
    assert devices.detect_type(info(sets="on off")) == "switch"
    assert devices.detect_type(info(sets="on off", alias="Licht Küche")) == "light"
    assert devices.detect_type(info(sets="on off pct:slider,0,1,100")) == "dimmer"
    assert devices.detect_type(info(sets="on off pct up down stop")) == "blind"
    assert devices.detect_type(info(sets="desired-temp:4.5,5,30")) == "thermostat"
    assert devices.detect_type(info(sets="lock unlock")) == "lock"
    assert devices.detect_type(info(readings={"contact": "open"})) == "contact"
    assert devices.detect_type(info(readings={"motion": "motion"})) == "motion"
    assert devices.detect_type(info(readings={"temperature": "20"})) == "temperature"
    assert devices.detect_type(info(readings={"humidity": "50"})) == "humidity"
    assert devices.detect_type(info(readings={"battery": "ok"})) is None
    # genericDeviceType from homebridge/alexa/gassistant setups
    generic = {"genericDeviceType": "light"}
    assert devices.detect_type(info(sets="on off", attrs=generic)) == "light"
    assert devices.detect_type(info(sets="on off dim", attrs=generic)) == "dimmer"
    # matterType wins
    attrs = {"matterType": "outlet", "genericDeviceType": "light"}
    assert devices.detect_type(info(sets="on off", attrs=attrs)) == "outlet"


def test_endpoints():
    sensor = info(
        name="clima.bath",
        readings={"temperature": "21.5 °C", "humidity": "55"},
        alias="Bath",
    )
    # one FHEM device is one device in the apps, also with several sensors
    assert devices.endpoints(sensor) == [
        {
            "id": "clima_bath",
            "type": "temperature",
            "name": "Bath",
            "parts": ["humidity"],
        }
    ]
    assert devices.endpoint_state(devices.endpoints(sensor)[0], sensor) == {
        "temperature": 21.5,
        "humidity": 55,
    }
    heating = info(
        sets="desired-temp",
        readings={"measured-temp": "20", "humidity": "40", "contact": "open"},
    )
    assert devices.endpoints(heating)[0]["parts"] == ["contact", "humidity"]
    plug = info(sets="on off", readings={"state": "on", "temperature": "30"})
    assert devices.endpoints(plug)[0]["parts"] == ["temperature"]
    named = info(sets="on off", attrs={"matterName": "Kitchen"}, alias="x")
    assert devices.endpoints(named)[0]["name"] == "Kitchen"
    assert devices.endpoints(info(readings={})) == []


def test_state():
    assert devices.state("switch", info(readings={"state": "on"})) == {"on": True}
    assert devices.state("switch", info(readings={"state": "off"})) == {"on": False}
    assert devices.state("switch", info(readings={"state": "set_on"})) == {"on": None}
    dimmer = info(readings={"state": "dim50%", "pct": "50"})
    assert devices.state("dimmer", dimmer) == {"on": True, "level": 50}
    blind = info(readings={"pct": "30"})
    assert devices.state("blind", blind) == {"position": 30}
    rollo = info(readings={"position": "30"}, type_="ROLLO")
    assert devices.state("blind", rollo) == {"position": 70}
    inverted = info(readings={"pct": "30"}, attrs={"matterInvert": "1"})
    assert devices.state("blind", inverted) == {"position": 70}
    heating = info(readings={"measured-temp": "20.4", "desired-temp": "21.5"})
    assert devices.state("thermostat", heating) == {"current": 20.4, "target": 21.5}
    assert devices.state("lock", info(readings={"lock": "locked"})) == {"locked": True}
    assert devices.state("contact", info(readings={"state": "open"})) == {
        "closed": False
    }
    assert devices.state("contact", info(readings={"contact": "closed"})) == {
        "closed": True
    }
    assert devices.state("motion", info(readings={"motion": "noMotion"})) == {
        "occupied": False
    }
    assert devices.state("temperature", info(readings={"temperature": "-3,5"})) == {
        "temperature": -3.5
    }


def test_fhem_commands():
    lamp = info(sets="on off pct:slider,0,1,100")
    assert devices.fhem_commands("dimmer", lamp, {"on": True, "level": 50}) == [
        "pct 50"
    ]
    assert devices.fhem_commands("dimmer", lamp, {"on": False}) == ["off"]
    assert devices.fhem_commands("dimmer", lamp, {"on": True}) == ["on"]
    assert devices.fhem_commands("switch", lamp, {"on": False}) == ["off"]
    blind = info(sets="pct up down stop", type_="ROLLO")
    assert devices.fhem_commands("blind", blind, {"position": 100}) == ["pct 0"]
    assert devices.fhem_commands("blind", blind, {"stop": True}) == ["stop"]
    heating = info(sets="desired-temp")
    assert devices.fhem_commands("thermostat", heating, {"target": 21.0}) == [
        "desired-temp 21"
    ]
    assert devices.fhem_commands("thermostat", heating, {"target": 21.5}) == [
        "desired-temp 21.5"
    ]
    assert devices.fhem_commands("lock", info(), {"locked": False}) == ["unlock"]


def test_pairing_settings(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = runtime.pairing_settings("bridge")
    assert runtime.pairing_settings("bridge") == settings
    assert 0 <= settings["discriminator"] <= 4095
    assert settings["passcode"] not in runtime.INVALID_PASSCODES
    assert 0 < settings["passcode"] < 99999999
    runtime.erase("bridge")
    assert not os.path.exists(runtime.bridge_directory("bridge"))
    assert format_manual_code("34970112332") == "3497-011-2332"


def test_readme_exists():
    path = os.path.join(os.path.dirname(devices.__file__), "README.md")
    with open(path, encoding="utf-8") as f:
        assert "matterType" in f.read()


class FakeFhem:
    """Answers the Perl commands of the bridge like FHEM"""

    def __init__(self, infos):
        self.infos = infos
        self.commands = []
        self.event_devices = None

    async def send(self, hash, cmd):
        if "fhempy_setEventDevices" in cmd:
            self.event_devices = re.findall(r"'([^']*)'\) // 'ok'", cmd)[0]
            return "ok"
        if cmd.startswith("CommandSet"):
            self.commands.append(re.findall(r"'(.*)'", cmd)[0])
            return None
        if "devspec2array" in cmd:
            spec = re.findall(r"devspec2array\('([^']*)'\)", cmd)[0]
            return ",".join(n for n in spec.split(",") if n in self.infos)
        if "to_json" in cmd:
            names = re.findall(r"foreach my \$d \(([^)]*)\)", cmd)[0]
            names = [n.strip("'") for n in names.split(",")]
            return json.dumps({n: self.infos[n] for n in names if n in self.infos})
        if "sort keys %defs" in cmd:
            return ",".join(sorted(self.infos))
        return ""


async def wait_for(condition, timeout=10):
    for _ in range(int(timeout * 50)):
        if condition():
            return
        await asyncio.sleep(0.02)
    raise AssertionError("condition not met")


def received(path):
    try:
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except OSError:
        return []


@pytest.mark.asyncio
async def test_bridge_module(mocker, tmp_path):
    # segno for the QR code
    await check_and_install_dependencies("matter_bridge")
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("bridge", None)
    mock_fhem.attributes["bridge"] = {"devices": "Lamp,Plug"}
    fake = FakeFhem(
        {
            "Lamp": info(
                "Lamp",
                sets="on off pct:slider,0,1,100",
                readings={"state": "off", "pct": "0"},
                alias="Living room",
            ),
            "Plug": info("Plug", sets="on off", readings={"state": "on"}),
            "Logfile": info("Logfile"),
        }
    )
    mocker.patch.object(fhem, "sendCommandHash", fake.send)
    mocker.patch.object(fhem, "CommandAttr", mock_fhem.CommandAttr)
    mocker.patch(
        "fhempy.lib.matter.server.prepare_node",
        mocker.AsyncMock(return_value=("node", (22, 13), {})),
    )
    mocker.patch.object(
        runtime, "installed_version", return_value=runtime.MATTER_JS_VERSION
    )
    log = str(tmp_path / "received.jsonl")
    script = os.path.join(os.path.dirname(__file__), "fake_bridge.py")

    def start(node, env, name, port, bridge_name, log_level="notice"):
        assert port == 5550 and bridge_name == "FHEM"
        return subprocess.Popen(
            [sys.executable, script, log],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    mocker.patch.object(runtime, "start", start)

    bridge = matter_bridge(logger)
    hash = {"NAME": "bridge", "FHEMPYTYPE": "matter_bridge"}
    try:
        assert (
            await bridge.Define(hash, ["bridge", "fhempy", "matter_bridge"], {}) is None
        )
        readings = mock_fhem.readings["bridge"]
        await wait_for(lambda: readings.get("state") == "ready for pairing")
        assert readings["pairing_code"] == "3497-011-2332"
        assert readings["devices"] == "Lamp:dimmer,Plug:switch"
        assert fake.event_devices == "Lamp,Plug,global"

        devices_msg = received(log)[0]
        assert devices_msg["cmd"] == "devices"
        assert devices_msg["devices"][0] == {
            "id": "Lamp",
            "type": "dimmer",
            "name": "Living room",
            "state": {"on": False, "level": 0},
            "parts": [],
        }

        # the Matter app switched the lamp on
        await wait_for(lambda: fake.commands)
        assert fake.commands == ["Lamp on"]

        # FHEM event -> Matter state
        await fhem.dispatch_event("Lamp", "pct: 40")
        await fhem.dispatch_event("Lamp", "on")
        await wait_for(lambda: len(received(log)) >= 3)
        assert received(log)[1:3] == [
            {"cmd": "state", "id": "Lamp", "state": {"level": 40}},
            {"cmd": "state", "id": "Lamp", "state": {"on": True}},
        ]
        # unchanged values aren't sent again
        count = len(received(log))
        await fhem.dispatch_event("Lamp", "pct: 40")
        await asyncio.sleep(0.2)
        assert len(received(log)) == count

        # set add only offers devices which aren't used yet
        assert bridge._conf_set["add"]["options"] == "Logfile"
        assert "Can't detect" in await bridge.set_add(hash, {"device": "Logfile"})
        await bridge.set_remove(hash, {"device": "Plug"})
        assert "bridge devices Lamp" in mock_fhem.command_attr

        await bridge.set_pairing_mode(hash, {})
        await wait_for(lambda: readings.get("state", "").startswith("pairing mode"))

        html = bridge.pairing_html()
        assert '<img src="data:image/png;base64,' in html and "3497-011-2332" in html
    finally:
        await bridge.Undefine(hash)
    assert "Lamp" not in fhem.event_listeners
