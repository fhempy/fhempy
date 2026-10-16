import asyncio
import json
import logging
import os

import aiohttp
import pytest
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.matter import clusters, server
from fhempy.lib.matter.matter import matter
from fhempy.lib.matter.controller import matter_controller

logger = logging.getLogger(__name__)


def light_node(node_id=5, on=True):
    return {
        "node_id": node_id,
        "available": True,
        "is_bridge": False,
        "attributes": {
            "0/29/0": [{"0": 22, "1": 1}],
            "0/40/1": "Signify",
            "0/40/3": "Hue color lamp",
            "0/40/5": "Living room",
            "0/40/10": "1.2.3",
            "1/3/0": 0,
            "1/6/0": on,
            "1/8/0": 127,
            "1/768/7": 370,
            "1/768/65532": 16,
        },
    }


def bridge_node():
    return {
        "node_id": 7,
        "available": True,
        "is_bridge": True,
        "attributes": {
            "0/40/1": "IKEA",
            "0/40/3": "DIRIGERA",
            "1/29/0": [{"0": 14, "1": 1}],
            "1/29/3": [2, 3],
            "2/29/0": [{"0": 19, "1": 1}, {"0": 21, "1": 1}],
            "2/57/5": "Front door",
            "2/57/17": True,
            "2/69/0": False,
            "2/47/12": 100,
            "3/29/0": [{"0": 19, "1": 1}, {"0": 266, "1": 1}],
            "3/29/3": [4],
            "3/57/5": "Power strip",
            "3/57/17": True,
            "3/6/0": False,
            "4/29/0": [{"0": 266, "1": 1}],
            "4/6/0": True,
        },
    }


def test_light_readings_and_sets():
    attrs = light_node()["attributes"]
    model = clusters.DeviceModel(attrs, clusters.device_endpoints(attrs))
    values = dict(model.convert(p, v) for p, v in attrs.items() if model.convert(p, v))
    assert values["onoff"] == "on"
    assert values["pct"] == 50
    assert values["ct"] == 2703
    assert values["model"] == "Hue color lamp"
    # feature map without hue/saturation
    assert {"on", "off", "toggle", "pct", "ct", "identify"} <= set(model.sets)
    assert "hue" not in model.sets
    assert model.state(values) == "on"

    assert model.command_args("pct", "100") == {
        "kind": "command",
        "endpoint_id": 1,
        "cluster_id": 8,
        "command_name": "MoveToLevelWithOnOff",
        "payload": {
            "level": 254,
            "transitionTime": 0,
            "optionsMask": 0,
            "optionsOverride": 0,
        },
        "timed": False,
    }
    assert model.command_args("ct", "2700")["payload"]["colorTemperatureMireds"] == 370


def test_bridge_creates_device_per_bridged_endpoint():
    attrs = bridge_node()["attributes"]
    assert clusters.bridged_endpoints(attrs) == [2, 3]
    # the bridge itself doesn't contain the bridged devices
    assert clusters.device_endpoints(attrs) == [0, 1]

    door = clusters.DeviceModel(attrs, clusters.device_endpoints(attrs, 2))
    assert door.convert("2/69/0", False) == ("contact", "open")
    assert door.convert("2/57/5", "Front door") == ("label", "Front door")
    assert door.convert("2/47/12", 100) == ("batteryPercent", 50)

    strip = clusters.DeviceModel(attrs, clusters.device_endpoints(attrs, 3))
    assert strip.endpoints == [3, 4]
    assert {"on", "off", "on_4", "off_4"} <= set(strip.sets)
    assert strip.convert("4/6/0", True) == ("onoff_4", "on")
    assert strip.command_args("on_4", None)["endpoint_id"] == 4


def test_default_icon():
    attrs = bridge_node()["attributes"]
    assert clusters.default_icon(attrs, clusters.device_endpoints(attrs, 2)) == (
        "fts_window_1w"
    )
    light = light_node()["attributes"]
    assert clusters.default_icon(light, clusters.device_endpoints(light)) == (
        "light_light"
    )
    assert clusters.default_icon(attrs, clusters.device_endpoints(attrs)) == (
        "mqtt_bridge_1"
    )
    sensor = {"1/29/0": [{"0": 770, "1": 1}], "1/1026/0": 2150}
    assert clusters.default_icon(sensor, [1]) == "temp_temperature"
    assert clusters.default_icon({"1/1026/0": 2150, "1/258/14": 0}, [1]) == (
        "fts_shutter"
    )
    assert clusters.default_icon({}, [0]) is None


def test_conversions():
    attrs = {
        "1/29/0": [{"0": 67, "1": 1}],
        "1/69/0": True,
        "1/258/14": 2500,
        "1/513/18": 2150,
        "1/513/28": 4,
        "1/1024/0": 30001,
    }
    model = clusters.DeviceModel(attrs, [1])
    assert model.convert("1/69/0", True) == ("water_leak", "leak")
    assert model.convert("1/258/14", 2500) == ("position", 75)
    assert model.convert("1/513/18", 2150) == ("desired-temp", 21.5)
    assert model.convert("1/513/28", 4) == ("mode", "heat")
    assert model.convert("1/1024/0", 30001) == ("illuminance", 1000.0)
    assert model.convert("1/513/18", None) is None
    assert model.command_args("desired-temp", "21.5")["value"] == 2150
    assert model.command_args("mode", "heat")["value"] == 4
    assert model.command_args("position", "75")["payload"] == {
        "liftPercent100thsValue": 2500
    }
    with pytest.raises(ValueError):
        model.command_args("mode", "dry")


def test_sensor_state():
    model = clusters.DeviceModel({}, [1])
    assert model.state({"temperature": 21.5, "humidity": 40.0}) == "T: 21.5 H: 40.0"
    assert model.state({"position": 100}) == "open"
    assert model.state({}) == "online"


def test_node_version(tmp_path):
    assert server.parse_node_version("v22.13.1\n") == (22, 13)
    assert server.parse_node_version("") is None
    assert server.needs_install(None)
    assert server.needs_install("1.3.9")
    assert not server.needs_install(server.MATTER_SERVER_VERSION)
    # a newer version installed with "set update" is kept
    assert not server.needs_install("99.0.0")

    node = tmp_path / "node"
    node.write_text("#!/bin/sh\necho v20.11.0\n")
    node.chmod(0o755)
    env = {"PATH": str(tmp_path)}
    with pytest.raises(server.NodeNotFound) as exc:
        server.find_node(env)
    assert exc.value.args[0] == (20, 11)

    node.write_text("#!/bin/sh\necho v24.1.0\n")
    assert server.find_node(env) == (str(node), (24, 1))
    assert server.env_for(str(node), env)["PATH"].startswith(str(tmp_path))


class FakeMatterServer:
    """Speaks the WebSocket API of the OHF Matter server"""

    def __init__(self, nodes):
        self.nodes = nodes
        self.commands = []
        self.clients = []

    async def handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.clients.append(ws)
        await ws.send_json(
            {
                "fabric_id": 1,
                "compressed_fabric_id": 1234,
                "schema_version": 11,
                "min_supported_schema_version": 9,
                "sdk_version": "matter.js 0.17.9",
                "wifi_credentials_set": False,
                "thread_credentials_set": False,
                "bluetooth_enabled": False,
            }
        )
        async for msg in ws:
            request_msg = json.loads(msg.data)
            self.commands.append(request_msg)
            command = request_msg["command"]
            args = request_msg["args"]
            if command == "start_listening":
                result = self.nodes
            elif command == "commission_with_code":
                if args["code"] != "34970112332":
                    await ws.send_json(
                        {
                            "message_id": request_msg["message_id"],
                            "error_code": 1,
                            "details": "Commissioning failed",
                        }
                    )
                    continue
                result = light_node(node_id=9, on=False)
                self.nodes.append(result)
            elif command == "open_commissioning_window":
                result = {
                    "setup_pin_code": 1234,
                    "setup_manual_code": "1234-567-8901",
                    "setup_qr_code": "MT:ABC",
                }
            else:
                result = None
            await ws.send_json(
                {"message_id": request_msg["message_id"], "result": result}
            )
        return ws

    async def send_event(self, event, data):
        for ws in self.clients:
            await ws.send_json({"event": event, "data": data})


async def wait_for(condition, timeout=5):
    for _ in range(int(timeout * 50)):
        if condition():
            return
        await asyncio.sleep(0.02)
    raise AssertionError("condition not met")


@pytest.mark.asyncio
async def test_controller_and_device(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.command_define.clear()
    for name in ("testmatter", "matter_5"):
        mock_fhem.readings.pop(name, None)

    fake = FakeMatterServer([light_node()])
    app = web.Application()
    app.router.add_get("/ws", fake.handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    controller = matter(logger)
    devices = {"testmatter": controller}
    mocker.patch("fhempy.lib.fhem_pythonbinding.getFhemPyDeviceByName", devices.get)
    try:
        ret = await controller.Define(
            {"NAME": "testmatter", "FHEMPYTYPE": "matter"},
            ["testmatter", "fhempy", "matter", f"ws://127.0.0.1:{port}/ws"],
            {},
        )
        assert ret is None
        readings = mock_fhem.readings["testmatter"]
        await wait_for(lambda: readings.get("state") == "connected")
        assert readings["nodes"] == "1" or readings["nodes"] == 1
        await wait_for(lambda: mock_fhem.command_define)
        assert mock_fhem.command_define[0] == "matter_5 fhempy matter testmatter 5"
        assert "matter_5 alias Living room" in mock_fhem.command_attr
        assert "matter_5 webCmd on:off:pct" in mock_fhem.command_attr
        # all Matter devices are in room Matter, with an icon of their type
        assert "matter_5 room Matter" in mock_fhem.command_attr
        assert "matter_5 icon light_light" in mock_fhem.command_attr

        # the FHEM device created by the controller
        dev = matter(logger)
        devices["matter_5"] = dev
        devhash = {"NAME": "matter_5", "FHEMPYTYPE": "matter"}
        await dev.Define(
            devhash, ["matter_5", "fhempy", "matter", "testmatter", "5"], {}
        )
        assert devhash["MATTER_ID"] == "5"
        devreadings = mock_fhem.readings["matter_5"]
        await wait_for(lambda: devreadings.get("state") == "on")
        assert devreadings["pct"] == 50
        assert "pct" in dev._conf_set and "on" in dev._conf_set

        # set command -> Matter command
        await dev.Set(devhash, ["matter_5", "off"], {})
        await wait_for(
            lambda: any(c["command"] == "device_command" for c in fake.commands)
        )
        cmd = [c for c in fake.commands if c["command"] == "device_command"][0]
        assert cmd["args"]["node_id"] == 5
        assert cmd["args"]["endpoint_id"] == 1
        assert cmd["args"]["cluster_id"] == 6
        assert cmd["args"]["command_name"] == "Off"

        # attribute update from the device
        await fake.send_event("attribute_updated", [5, "1/6/0", False])
        await wait_for(lambda: devreadings.get("state") == "off")

        # device not reachable
        offline = light_node()
        offline["available"] = False
        await fake.send_event("node_updated", offline)
        await wait_for(lambda: devreadings.get("state") == "offline")

        # share with another app
        await dev.Set(devhash, ["matter_5", "share"], {})
        await wait_for(lambda: devreadings.get("share_code") == "1234-567-8901")

        # pairing with a wrong and a correct code
        await controller.Set(
            {"NAME": "testmatter"}, ["testmatter", "pair", "1111-111-1111"], {}
        )
        await wait_for(lambda: readings.get("pairing", "").startswith("failed"))
        assert "Commissioning failed" in readings["pairing"]
        await controller.Set(
            {"NAME": "testmatter"}, ["testmatter", "pair", "3497-011-2332"], {}
        )
        await wait_for(lambda: readings.get("pairing") == "successful, node 9")
        assert "matter_9 fhempy matter testmatter 9" in mock_fhem.command_define
        assert readings["nodes"] in (2, "2")

        await dev.Undefine(devhash)
        await controller.Undefine({"NAME": "testmatter"})
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_button_events(mocker):
    mock_fhem.mock_module(mocker)
    from fhempy.lib.matter.device import matter_device

    node = {
        "node_id": 3,
        "available": True,
        "attributes": {"1/59/0": 0, "2/59/0": 0},
    }
    controller = mocker.Mock()
    controller.nodes = {3: node}
    fhemdev = mocker.Mock()
    fhemdev._attr_rawReadings = 0
    fhemdev._conf_set = {}
    fhemdev.set_set_config = mocker.AsyncMock()
    device = matter_device(logger, fhemdev)
    device.hash = {"NAME": "testbutton"}
    device.node_id = 3
    device.controller = controller
    mock_fhem.readings.pop("testbutton", None)
    await device.node_updated()

    await device.node_event(
        {"node_id": 3, "endpoint_id": 1, "cluster_id": 59, "event_id": 3, "data": {}}
    )
    assert mock_fhem.readings["testbutton"]["button"] == "short"
    await device.node_event(
        {
            "node_id": 3,
            "endpoint_id": 2,
            "cluster_id": 59,
            "event_id": 6,
            "data": {"totalNumberOfPressesCounted": 2},
        }
    )
    assert mock_fhem.readings["testbutton"]["button_2"] == "double"


def test_readme_exists():
    readme = os.path.join(os.path.dirname(clusters.__file__), "README.md")
    with open(readme, encoding="utf-8") as f:
        assert "set matter pair" in f.read()


@pytest.mark.asyncio
async def test_client_rejects_pending_commands_on_close():
    from fhempy.lib.matter.client import MatterClient

    async def handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_json({"fabric_id": 1})
        async for msg in ws:
            # never answer, close instead
            await ws.close()
        return ws

    app = web.Application()
    app.router.add_get("/ws", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        client = MatterClient(f"ws://127.0.0.1:{port}/ws", logger, None)
        await client.connect()
        assert client.server_info == {"fabric_id": 1}
        listen = asyncio.create_task(client.listen())
        with pytest.raises((ConnectionError, aiohttp.ClientError)):
            await client.send_command("get_nodes", timeout=5)
        await listen
        assert not client.connected
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_controller_shows_fhem_in_other_apps(mocker):
    # matter-server 1.4.0 pins --default-fabric-label but still pairs with
    # "HomeAssistant", set_default_fabric_label works and renames old pairings
    start = mocker.patch.object(server.child_process, "start")
    server.start("/usr/bin/node", {}, 5580)
    assert "--default-fabric-label" not in start.call_args[0][0]

    client = mocker.Mock()
    client.send_command = mocker.AsyncMock(
        side_effect=[{"fabric_label": "HomeAssistant"}, None]
    )
    await matter_controller.set_fabric_label(
        mocker.Mock(logger=logger, external_url=None), client
    )
    client.send_command.assert_called_with("set_default_fabric_label", label="FHEM")

    client.send_command = mocker.AsyncMock(return_value={"fabric_label": "FHEM"})
    await matter_controller.set_fabric_label(
        mocker.Mock(logger=logger, external_url=None), client
    )
    client.send_command.assert_called_once_with("get_fabric_label")
