import json
import logging
import re
import socket

import aiohttp
import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib import fhem
from fhempy.lib.mcp_server import protocol, tools
from fhempy.lib.mcp_server.mcp_server import mcp_server

logger = logging.getLogger(__name__)

NAME = "testmcp"

DEVICES = {
    "Lamp_kitchen": {
        "type": "dummy",
        "alias": "Küchenlampe",
        "room": "Küche",
        "genericDeviceType": "light",
        "state": "on",
        "readings": {
            "state": {"value": "on", "time": "2026-10-18 10:00:00"},
            "password": {"value": "geheim", "time": "2026-10-18 10:00:00"},
            "url": {
                "value": "https://user:geheim@example.com/x",
                "time": "2026-10-18 10:00:00",
            },
        },
        "attributes": {"alias": "Küchenlampe", "room": "Küche"},
        "commands": "on off",
    },
    "Lamp_living": {
        "type": "HUEDevice",
        "alias": "Wohnzimmerlicht",
        "room": "Wohnzimmer,Licht",
        "state": "off",
    },
    "Residents": {"type": "dummy", "room": "Haus", "state": "home"},
}


class FakeFhem:
    """Answers the Perl commands of the module like FHEM would"""

    def __init__(self):
        self.commands = []
        self.defs = {}

    @staticmethod
    def arg(code, var):
        match = re.search(r"my \$" + var + r" = '((?:[^'\\]|\\.)*)'", code)
        return match.group(1).replace("\\'", "'").replace("\\\\", "\\")

    async def send(self, hash, code):
        self.commands.append(code)
        if "readings => \\%rd" in code:
            name = self.arg(code, "d")
            if name not in DEVICES:
                return "not_found"
            dev = DEVICES[name]
            return json.dumps(
                {
                    "name": name,
                    "type": dev["type"],
                    "state": dev["state"],
                    "definition": None,
                    "readings": dev.get("readings", {}),
                    "attributes": dev.get("attributes", {}),
                    "commands": dev.get("commands", ""),
                }
            )
        if "alias => AttrVal($d, 'alias', '')" in code:
            return json.dumps(
                [
                    {
                        "name": name,
                        "type": dev["type"],
                        "alias": dev.get("alias", ""),
                        "room": dev.get("room", ""),
                        "genericDeviceType": dev.get("genericDeviceType", ""),
                        "state": dev["state"],
                    }
                    for name, dev in DEVICES.items()
                ]
            )
        if "definition => ($x->{DEF} // '')" in code:
            return json.dumps(
                [
                    {
                        "name": name,
                        "type": d["type"],
                        "definition": d["definition"],
                        "state": "initialized",
                        "disabled": d["disable"],
                        "room": "AI",
                        "comment": d["comment"],
                    }
                    for name, d in self.defs.items()
                ]
            )
        if "CommandSet(" in code:
            if self.arg(code, "d") not in DEVICES:
                return "not_found"
            return json.dumps({"error": None, "state": "off"})
        if "CommandDefine(" in code:
            name = self.arg(code, "n")
            if name in self.defs:
                return json.dumps({"error": "A device with this name already exists"})
            definition = re.search(r"CommandDefine\(undef, '((?:[^'\\]|\\.)*)'", code)
            _, type_, definition = definition.group(1).split(" ", 2)
            self.defs[name] = {
                "type": type_,
                "definition": definition.replace("\\'", "'"),
                "disable": "1" if f"'{name} disable 1'" in code else "0",
                "comment": "",
            }
            return json.dumps({"error": None})
        if "value => AttrVal($n," in code:
            name = self.arg(code, "n")
            if name not in self.defs:
                return json.dumps({"error": "not found"})
            d = self.defs[name]
            if f"'{name} disable 1'" in code:
                d["disable"] = "1"
            attrs = d.setdefault("attrs", {})
            match = re.search(
                r"my \$e = CommandAttr\(undef, '(\S+) (\S+) ((?:[^'\\]|\\.)*)'\)", code
            )
            if match:
                attrs[match.group(2)] = match.group(3)
                value = match.group(3)
            else:
                attr = re.search(r"CommandDeleteAttr\(undef, '\S+ (\S+)'\)", code)
                attrs.pop(attr.group(1), None)
                value = None
            return json.dumps({"error": None, "value": value})
        if "CommandModify(" in code:
            name = self.arg(code, "n")
            if name not in self.defs:
                return json.dumps({"error": "not found"})
            self.defs[name]["definition"] = "changed"
            return json.dumps({"error": None})
        if "CommandDelete(" in code:
            if self.defs.pop(self.arg(code, "n"), None) is None:
                return "missing"
            return ""
        if "to_json([map {" in code:
            names = re.findall(r"'([A-Za-z0-9._]+)'", code.split("grep", 1)[1])
            return json.dumps(
                [
                    {
                        "name": n,
                        "type": d["type"],
                        "definition": d["definition"],
                        "attributes": dict(d.get("attrs", {}), disable="1"),
                    }
                    for n, d in self.defs.items()
                    if n in names
                ]
            )
        if code.startswith("join(',', grep { defined($defs{$_}) }"):
            names = re.findall(r"'([A-Za-z0-9._]+)'", code)
            return ",".join(n for n in names if n in self.defs)
        return ""

    async def delete_attr(self, hash, deldef):
        name, attr = deldef.split(" ")
        if attr == "disable" and name in self.defs:
            self.defs[name]["disable"] = "0"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest_asyncio.fixture
async def module(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes[NAME] = {"port": str(free_port())}
    fake = FakeFhem()
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake.send)
    mocker.patch("fhempy.lib.fhem.CommandDeleteAttr", fake.delete_attr)
    mod = mcp_server(logger)
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "mcp_server"}, [], {})
    mod.fake = fake
    yield mod
    await mod.Undefine(mod.hash)
    mock_fhem.attributes.pop(NAME, None)


async def post(url, message, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=message, headers=headers or {}) as resp:
            text = await resp.text()
            return resp.status, (json.loads(text) if text else None)


async def call(mod, tool, **arguments):
    status, answer = await post(
        mod.url().replace(mod.ip, "127.0.0.1"),
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        },
    )
    assert status == 200
    result = answer["result"]
    text = result["content"][0]["text"]
    try:
        return result["isError"], json.loads(text)
    except ValueError:
        return result["isError"], text


def test_mask():
    assert tools.mask_value("password", "x") == "***"
    assert tools.mask_value("apiKey", "x") == "***"
    assert tools.mask_value("pin", "1234") == "***"
    assert tools.mask_value("pinCode", "1234") == "***"
    assert tools.mask_value("spinning", "yes") == "yes"
    assert tools.mask_value("temperature", "21") == "21"
    assert (
        tools.mask_text("set x https://user:pw@host/a")
        == "set x https://***:***@host/a"
    )
    assert tools.mask_text("{curl('token=abc123')}") == "{curl('token=***')}"
    assert tools.mask_text("password: 'abc'") == "password: '***'"
    assert tools.mask_value("x", "a" * 600).endswith("...")


def test_check_name():
    assert tools.check_name("Lamp_1.a") == "Lamp_1.a"
    for bad in ("TYPE=dummy", "a b", "a;b", "", "x'y", "a,b"):
        with pytest.raises(protocol.ToolError):
            tools.check_name(bad)


@pytest.mark.asyncio
async def test_protocol():
    async def echo(text):
        if text == "fail":
            raise protocol.ToolError("failed")
        return {"echo": text}

    tool = protocol.Tool("echo", "Echo", echo, {"text": {"type": "string"}}, ["text"])
    server = protocol.McpServer("fhem", "help", lambda: [tool])
    init = await server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26"},
        }
    )
    assert init["result"]["protocolVersion"] == "2025-03-26"
    assert init["result"]["instructions"] == "help"
    init = await server.handle(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    )
    assert init["result"]["protocolVersion"] == protocol.PROTOCOL_VERSIONS[0]
    assert await server.handle({"jsonrpc": "2.0", "method": "notifications/x"}) is None
    assert (await server.handle({"jsonrpc": "2.0", "id": 2, "method": "ping"}))[
        "result"
    ] == {}
    listed = await server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    assert listed["result"]["tools"][0]["inputSchema"]["required"] == ["text"]
    unknown = await server.handle({"jsonrpc": "2.0", "id": 4, "method": "x"})
    assert unknown["error"]["code"] == protocol.METHOD_NOT_FOUND
    invalid = await server.handle({"id": 4, "method": "ping"})
    assert invalid["error"]["code"] == protocol.INVALID_REQUEST

    async def call_echo(arguments):
        answer = await server.handle(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "echo", "arguments": arguments},
            }
        )
        return answer["result"]

    assert json.loads((await call_echo({"text": "hi"}))["content"][0]["text"]) == {
        "echo": "hi"
    }
    assert (await call_echo({}))["isError"] is True
    assert (await call_echo({"text": "a", "other": 1}))["isError"] is True
    failed = await call_echo({"text": "fail"})
    assert failed["isError"] is True and failed["content"][0]["text"] == "failed"


@pytest.mark.asyncio
async def test_http_auth(module):
    url = module.url().replace(module.ip, "127.0.0.1")
    base = url.rsplit("/", 1)[0]
    ping = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    assert (await post(url, ping)) == (200, {"jsonrpc": "2.0", "id": 1, "result": {}})
    assert (await post(base, ping))[0] == 401
    assert (await post(base + "/wrong", ping))[0] == 401
    header = {"Authorization": f"Bearer {module.token}"}
    assert (await post(base, ping, header))[0] == 200
    evil = {"Origin": "http://evil.example.com"}  # NOSONAR
    assert (await post(url, ping, evil))[0] == 403
    local = {"Origin": "http://localhost:3000"}  # NOSONAR
    assert (await post(url, ping, local))[0] == 200
    notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert (await post(url, notification)) == (202, None)
    status, batch = await post(url, [ping, notification])
    assert status == 200 and len(batch) == 1
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
        async with session.get(url, headers={"Accept": "text/event-stream"}) as resp:
            assert resp.status == 405
        async with session.post(url, data="{") as resp:
            assert resp.status == 400
    old = url
    await module.set_new_token(module.hash, {})
    assert (await post(old, ping))[0] == 401
    # the token is stored encrypted
    assert mock_fhem.readings[NAME][".token"] != module.token


@pytest.mark.asyncio
async def test_read_tools(module):
    error, rooms = await call(module, "list_rooms")
    assert not error
    assert {"room": "Licht", "devices": 1} in rooms["rooms"]
    error, devices = await call(module, "list_devices", room="küche")
    assert [d["name"] for d in devices["devices"]] == ["Lamp_kitchen"]
    error, devices = await call(module, "list_devices", type="light")
    assert [d["name"] for d in devices["devices"]] == ["Lamp_kitchen"]
    error, devices = await call(module, "list_devices", search="WOHNZIMMER")
    assert [d["name"] for d in devices["devices"]] == ["Lamp_living"]
    error, device = await call(module, "get_device", name="Lamp_kitchen")
    assert device["readings"]["password"]["value"] == "***"
    assert device["readings"]["url"]["value"] == "https://***:***@example.com/x"
    assert device["commands"] == "on off"
    assert "definition" not in device
    error, text = await call(module, "get_device", name="Nope")
    assert error and "not found" in text
    error, text = await call(module, "get_device", name="TYPE=dummy")
    assert error
    # the AI's input only reaches FHEM as quoted Perl string
    await call(module, "get_device", name="Lamp_kitchen")
    assert "my $d = 'Lamp_kitchen';" in module.fake.commands[-1]


@pytest.mark.asyncio
async def test_set_device(module):
    error, result = await call(module, "set_device", name="Lamp_kitchen", command="off")
    assert not error and result["state_now"] == "off"
    assert "CommandSet(undef, $d . ' ' . 'off')" in module.fake.commands[-1]
    assert mock_fhem.readings[NAME]["last_action"] == "set Lamp_kitchen off"
    error, result = await call(
        module, "set_device", name="Lamp_kitchen", command="off'); system('x"
    )
    assert "'off\\'); system(\\'x'" in module.fake.commands[-1]
    error, text = await call(module, "set_device", name="Nope", command="on")
    assert error
    module._attr_allow_set = 0
    status, answer = await post(
        module.url().replace(module.ip, "127.0.0.1"),
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "set_device", "arguments": {}},
        },
    )
    assert answer["error"]["code"] == protocol.INVALID_PARAMS


@pytest.mark.asyncio
async def test_automation_approval(module):
    definition = '([Residents] eq "absent") (set Lamp_kitchen off, set Lamp_living off)'
    error, result = await call(
        module,
        "create_automation",
        name="ai_lights_off",
        type="DOIF",
        definition=definition,
        description="Lights off",
    )
    assert not error and "waiting for approval" in result["note"]
    assert module.fake.defs["ai_lights_off"]["disable"] == "1"
    assert module.fake.defs["ai_lights_off"]["definition"] == definition
    assert module.pending == ["ai_lights_off"]
    assert mock_fhem.readings[NAME]["state"] == "waiting for approval: ai_lights_off"
    assert module._conf_set["approve"]["options"] == "ai_lights_off,all"
    html = module.setup_html([module.pending_info["ai_lights_off"]])
    assert "([Residents] eq &quot;absent&quot;)" in html

    error, text = await call(
        module, "create_automation", name="ai_lights_off", type="DOIF", definition="x"
    )
    assert error and "already exists" in text
    error, text = await call(
        module, "create_automation", name="x", type="perl", definition="x"
    )
    assert error

    error, automations = await call(module, "list_automations")
    assert automations["automations"][0]["waiting_for_approval"] is True
    assert automations["automations"][0]["created_by_you"] is True

    await module.Set(module.hash, [NAME, "approve", "ai_lights_off"], {})
    assert module.fake.defs["ai_lights_off"]["disable"] == "0"
    assert module.pending == []
    assert mock_fhem.readings[NAME]["state"] == "ready"
    assert "approve" not in module._conf_set

    error, result = await call(
        module, "change_automation", name="ai_lights_off", definition="y"
    )
    assert not error and module.pending == ["ai_lights_off"]

    # foreign automations can't be changed or deleted
    module.fake.defs["user_doif"] = {
        "type": "DOIF",
        "definition": "z",
        "disable": "0",
        "comment": "",
    }
    error, text = await call(
        module, "change_automation", name="user_doif", definition="a"
    )
    assert error and "not created by you" in text
    error, text = await call(module, "delete_automation", name="user_doif")
    assert error and "user_doif" in module.fake.defs

    await module.Set(module.hash, [NAME, "reject", "ai_lights_off"], {})
    assert "ai_lights_off" not in module.fake.defs
    assert module.created == [] and module.pending == []


@pytest.mark.asyncio
async def test_without_approval(module):
    module._attr_require_approval = 0
    error, result = await call(
        module,
        "create_automation",
        name="ai_at",
        type="at",
        definition="*08:00 set x on",
    )
    assert not error and "is active" in result["note"]
    assert module.fake.defs["ai_at"]["disable"] == "0"
    assert module.pending == [] and module.created == ["ai_at"]
    error, result = await call(module, "delete_automation", name="ai_at")
    assert not error and module.created == []


@pytest.mark.asyncio
async def test_tool_attributes(module):
    names = [tool.name for tool in module.tools.tools()]
    assert "set_device" in names and "create_automation" in names
    assert "fhem_command" not in names
    module._attr_allow_set = 0
    module._attr_allow_automations = 0
    module._attr_allow_fhem_command = 1
    names = [tool.name for tool in module.tools.tools()]
    assert "set_device" not in names and "create_automation" not in names
    assert "fhem_command" in names


def attr_command(module):
    return [c for c in module.fake.commands if "value => AttrVal($n," in c][-1]


@pytest.mark.asyncio
async def test_automation_attributes(module):
    await call(
        module,
        "create_automation",
        name="ai_doif",
        type="DOIF",
        definition='([Residents] eq "absent") (set Lamp_kitchen off)',
    )
    await module.Set(module.hash, [NAME, "approve", "ai_doif"], {})
    assert module.pending == []

    error, result = await call(
        module,
        "set_automation_attribute",
        name="ai_doif",
        attribute="do",
        value="always",
    )
    assert not error and result["value_now"] == "always"
    # disabled before the attribute is set, waits for approval again
    code = attr_command(module)
    assert code.index("'ai_doif disable 1'") < code.index("'ai_doif do always'")
    assert module.fake.defs["ai_doif"]["disable"] == "1"
    assert module.pending == ["ai_doif"]
    html = module.setup_html([module.pending_info["ai_doif"]])
    assert "attr do always" in html and "attr disable" not in html

    error, result = await call(
        module, "set_automation_attribute", name="ai_doif", attribute="do"
    )
    assert not error and "do" not in module.fake.defs["ai_doif"]["attrs"]

    for attribute in ("disable", "userReadings", "stateFormat", "devStateIcon"):
        error, text = await call(
            module,
            "set_automation_attribute",
            name="ai_doif",
            attribute=attribute,
            value="x",
        )
        assert error and "only be set by the user" in text
    error, text = await call(
        module, "set_automation_attribute", name="ai_doif", attribute="a b", value="x"
    )
    assert error and "Invalid attribute" in text
    error, text = await call(
        module, "set_automation_attribute", name="Residents", attribute="do", value="x"
    )
    assert error and "not created by you" in text
    # the value only reaches FHEM as quoted Perl string
    await call(
        module,
        "set_automation_attribute",
        name="ai_doif",
        attribute="wait",
        value="1'); system('x",
    )
    assert "'ai_doif wait 1\\'); system(\\'x'" in attr_command(module)
