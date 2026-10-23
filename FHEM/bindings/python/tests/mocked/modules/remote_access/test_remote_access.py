import asyncio
import base64
import io
import json
import logging
import os
import re
import sys
import tarfile

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.remote_access import remote_access as ra
from fhempy.lib.remote_access import sites, tailscale

logger = logging.getLogger(__name__)

NAME = "remote"
DNS = "fhem.tail1234.ts.net"
LOGIN_URL = "https://login.tailscale.com/a/abc123"
ENABLE_URL = "https://login.tailscale.com/f/funnel?node=n1"

# tailscale command line tool: answers from the state file next to it
FAKE_TAILSCALE = r"""
import json, os, sys, time

state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fake.json")

def load():
    with open(state_file) as f:
        return json.load(f)

def save(state):
    with open(state_file + ".tmp", "w") as f:
        json.dump(state, f)
    os.replace(state_file + ".tmp", state_file)

args = [a for a in sys.argv[1:] if not a.startswith("--socket=")]
state = load()
state.setdefault("calls", []).append(args)
save(state)
if args[:1] == ["status"]:
    print(json.dumps({
        "BackendState": state["backend"],
        "AuthURL": state.get("auth_url", ""),
        "Self": {"DNSName": "%s." % state["dns"] if state["backend"] == "Running" else ""},
    }))
elif args[:1] == ["up"]:
    state["auth_url"] = state["login_url"]
    save(state)
    while load()["backend"] != "Running":
        time.sleep(0.05)
elif args[:2] == ["funnel", "status"]:
    allow = {"%s:443" % state["dns"]: True} if state.get("target") else {}
    for port in state.get("ports", {}):
        allow["%s:%s" % (state["dns"], port)] = True
    print(json.dumps({"AllowFunnel": allow}))
elif args[:1] == ["funnel"] and any(a.startswith("--https=") for a in args):
    port = [a for a in args if a.startswith("--https=")][0].split("=")[1]
    ports = state.setdefault("ports", {})
    if args[-1] == "off":
        ports.pop(port, None)
    else:
        ports[port] = args[-1]
    save(state)
elif args[:1] == ["funnel"]:
    if not state.get("funnel_enabled"):
        print("Funnel is not enabled on your tailnet.\nTo enable, visit:\n")
        print("         " + state["enable_url"] + "\n", flush=True)
        while not load().get("funnel_enabled"):
            time.sleep(0.05)
        print("Success.")
    state = load()
    state["target"] = args[-1]
    save(state)
elif args[:2] == ["serve", "reset"]:
    state["target"] = None
    state["ports"] = {}
    save(state)
elif args[:1] == ["logout"]:
    state["backend"] = "NeedsLogin"
    state["auth_url"] = ""
    state["target"] = None
    save(state)
"""

FAKE_TAILSCALED = r"""
import signal, sys, time
signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
while True:
    time.sleep(1)
"""


def write_script(path, code):
    with open(path, "w") as f:
        f.write(f"#!{sys.executable}\n{code}")
    os.chmod(path, 0o755)


class FakeTailscale:
    def __init__(self):
        self.file = os.path.join(tailscale.base_directory(), "fake.json")
        os.makedirs(tailscale.bin_directory(), exist_ok=True)
        write_script(tailscale.binary("tailscale"), FAKE_TAILSCALE)
        write_script(tailscale.binary("tailscaled"), FAKE_TAILSCALED)
        with open(os.path.join(tailscale.bin_directory(), "VERSION"), "w") as f:
            f.write("1.90.0")
        self.save(
            {
                "backend": "NeedsLogin",
                "dns": DNS,
                "login_url": LOGIN_URL,
                "enable_url": ENABLE_URL,
            }
        )

    def load(self):
        with open(self.file) as f:
            return json.load(f)

    def save(self, state):
        with open(self.file + ".tmp", "w") as f:
            json.dump(state, f)
        os.replace(self.file + ".tmp", self.file)

    def update(self, **changes):
        state = self.load()
        state.update(changes)
        self.save(state)


class FakeFhemweb:
    """FHEMWEB with an allowed device: 401 without the right password"""

    def __init__(self):
        self.credentials = None
        self.protected = True
        self.runner = None
        self.port = None

    def token(self):
        return base64.b64encode(self.credentials.encode()).decode()

    async def handle(self, request):
        if not self.protected:
            return web.Response(text="FHEM")
        header = request.headers.get("Authorization", "")
        if header.startswith("Basic ") and self.credentials:
            if header[6:] == self.token():
                return web.Response(text="FHEM")
        if self.credentials and f"AuthToken={self.token()}" in request.headers.get(
            "Cookie", ""
        ):
            return web.Response(status=404)
        return web.Response(status=401, headers={"WWW-Authenticate": "Basic"})

    async def start(self):
        app = web.Application()
        app.router.add_get("/{path:.*}", self.handle)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        self.port = site._server.sockets[0].getsockname()[1]

    async def stop(self):
        await self.runner.cleanup()


class FakeFhem:
    def __init__(self, fhemweb):
        self.fhemweb = fhemweb
        self.commands = []
        self.weblinks = {}
        self.rewrites = []

    async def send(self, hash, code):
        self.commands.append(code)
        if "TYPE=weblink" in code:
            return json.dumps(self.weblinks)
        if "fhempy_remote_access" in code:
            self.rewrites.append(code)
            return ""
        if "FHEMWEB $p" in code:
            return f"port {self.fhemweb.port}"
        if "'basicAuth', '')" in code:
            return "yes" if self.fhemweb.credentials else "no"
        match = re.search(r"CommandSet\(undef, '(\S+) basicAuth (\S+) (\S+)'\)", code)
        if match:
            self.fhemweb.credentials = f"{match.group(2)}:{match.group(3)}"
            return ""
        return ""


async def wait_for(condition, timeout=15):
    for _ in range(int(timeout * 20)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("condition not reached")


def state():
    return mock_fhem.readings.get(NAME, {}).get("state")


@pytest_asyncio.fixture
async def module(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes.pop(NAME, None)
    mocker.patch.object(ra, "WAIT_INTERVAL", 0.05)
    mocker.patch.object(ra, "ONLINE_INTERVAL", 0.1)
    fake_ts = FakeTailscale()

    async def install(logger):
        return "1.90.0"

    mocker.patch.object(tailscale, "install", install)
    fhemweb = FakeFhemweb()
    await fhemweb.start()
    fake = FakeFhem(fhemweb)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake.send)
    mod = ra.remote_access(logger)
    mod.fake_ts = fake_ts
    mod.fake = fake
    mod.fhemweb = fhemweb
    yield mod
    await mod.Undefine(mod.hash)
    await fhemweb.stop()


async def define(mod):
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "remote_access"}, [], {})


@pytest.mark.asyncio
async def test_setup_flow(module):
    await define(module)
    await wait_for(lambda: state() == "login required" and module.login_url)
    assert module.login_url == LOGIN_URL
    html = module.setup_html()
    assert "Log in to Tailscale" in html and LOGIN_URL in html

    # password protection is set before anything is reachable
    assert module.fhemweb.credentials == f"fhem:{module.password}"
    assert len(module.password) >= ra.MIN_PASSWORD_LENGTH
    calls = module.fake_ts.load()["calls"]
    assert ["up", "--hostname=fhem", "--json"] in calls
    assert not any(c[:1] == ["funnel"] and c[1] != "status" for c in calls)

    module.fake_ts.update(backend="Running")
    await wait_for(lambda: state() == "enable funnel")
    assert module.enable_url == ENABLE_URL
    html = module.setup_html()
    assert "Allow Funnel" in html and "funnel?node=n1" in html

    module.fake_ts.update(funnel_enabled=True)
    await wait_for(lambda: state() == f"online: https://{DNS}")
    assert mock_fhem.readings[NAME]["url"] == f"https://{DNS}"
    target = module.fake_ts.load()["target"]
    assert target == f"http://127.0.0.1:{module.fhemweb.port}"
    html = module.setup_html()
    assert f"https://{DNS}" in html and "data:image/png;base64" in html
    assert module.password in html
    # same look as the FHEMWEB WEB
    setup = next(c for c in module.fake.commands if "FHEMWEB $p" in c)
    assert "roomIcons" in setup and "HTTPS" not in setup
    # the detail page reloads for every step
    assert any("location.reload()" in js for _, js in mock_fhem.javascript)


@pytest.mark.asyncio
async def test_no_funnel_without_password(module):
    module.fhemweb.protected = False
    module.fake_ts.update(backend="Running", funnel_enabled=True)
    await define(module)
    await wait_for(lambda: (state() or "").startswith("error"))
    assert "doesn't ask for a password" in state()
    await asyncio.sleep(0.3)
    assert module.fake_ts.load().get("target") is None

    # fixed by the user, set restart starts again
    module.fhemweb.protected = True
    await module.set_restart(module.hash, {})
    await wait_for(lambda: state() == f"online: https://{DNS}")


@pytest.mark.asyncio
async def test_password_and_logout(module):
    module.fake_ts.update(backend="Running", funnel_enabled=True)
    await define(module)
    await wait_for(lambda: state() == f"online: https://{DNS}")

    assert "at least" in await module.set_password(module.hash, {"password": "short"})
    assert await module.set_password(module.hash, {"password": "my secret pw"})
    assert await module.set_password(module.hash, {"password": "longenough1"}) is None
    assert module.fhemweb.credentials == "fhem:longenough1"

    old = module.password
    await module.set_new_password(module.hash, {})
    assert module.password != old
    assert module.fhemweb.credentials == f"fhem:{module.password}"

    # the password survives a restart of fhempy
    stored = mock_fhem.readings[NAME][".password"]
    assert module.password not in stored
    second = ra.remote_access(logger)
    second.hash = module.hash
    second._unique_id = module._unique_id
    await second.load_password()
    assert second.password == module.password

    await module.logout()
    await wait_for(lambda: state() == "login required")
    assert module.fake_ts.load()["target"] is None


class FakeEsphome:
    """web page in the home network with a websocket"""

    async def page(self, request):
        return web.Response(
            text=f"ESPHome {request.headers.get('Origin', '-')} "
            f"{request.headers.get('Cookie', '-')}"
        )

    async def events(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            await ws.send_str("echo " + msg.data)
        return ws

    async def start(self):
        app = web.Application()
        app.router.add_get("/events", self.events)
        app.router.add_get("/{path:.*}", self.page)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        return site._server.sockets[0].getsockname()[1]


@pytest.mark.asyncio
async def test_web_pages(module):
    esphome = FakeEsphome()
    port = await esphome.start()
    module.fake.weblinks = {
        "other": "http://10.0.0.3:1234/",
        "z2m_frontend": "http://192.168.1.20:8080/",
        "esphome_dashboard": f"http://127.0.0.1:{port}/",
        "google": "https://www.google.com/",
    }
    module.fake_ts.update(backend="Running", funnel_enabled=True)
    await define(module)
    await wait_for(
        lambda: module.fake_ts.load().get("ports", {}).keys() == {"8443", "10000"}
    )
    await wait_for(lambda: "web_pages" in mock_fhem.readings.get(NAME, {}))
    assert mock_fhem.readings[NAME]["web_pages"] == (
        f"esphome_dashboard: https://{DNS}:8443/, z2m_frontend: https://{DNS}:10000/"
    )
    rewrite = module.fake.rewrites[-1]
    assert f"'http://127.0.0.1:{port}' => 'https://{DNS}:8443'" in rewrite
    assert (
        "'http://192.168.1.20:8080' => 'https://{DNS}:10000'".format(DNS=DNS) in rewrite
    )
    assert "esphome_dashboard" in module.setup_html()

    proxy_url = module.fake_ts.load()["ports"]["8443"]
    async with aiohttp.ClientSession() as session:
        # no password: no access
        async with session.get(proxy_url + "/devices") as resp:
            assert resp.status == 401
        async with session.get(
            proxy_url + "/", headers={"Cookie": "AuthToken=wrong"}
        ) as resp:
            assert resp.status == 401
        # the login cookie of FHEMWEB
        cookie = {"Cookie": f"AuthToken={module.fhemweb.token()}; theme=dark"}
        async with session.get(
            proxy_url + "/x?a=1", headers=dict(cookie, Origin=f"https://{DNS}:8443")
        ) as resp:
            assert resp.status == 200
            text = await resp.text()
        assert text == f"ESPHome http://127.0.0.1:{port} theme=dark"
        async with session.ws_connect(proxy_url + "/events", headers=cookie) as ws:
            await ws.send_str("hi")
            msg = await ws.receive(timeout=5)
            assert msg.data == "echo hi"

    # FHEMWEB without password: the pages are closed too
    module.fhemweb.protected = False
    module.sites.login._protected_until = 0
    async with aiohttp.ClientSession() as session:
        async with session.get(proxy_url + "/", headers=cookie) as resp:
            assert resp.status == 401
    module.fhemweb.protected = True

    # weblink deleted: its port is closed
    del module.fake.weblinks["z2m_frontend"]
    await wait_for(lambda: module.sites.shared[-1].startswith("other:"))
    assert module.fake_ts.load()["ports"].keys() == {"8443", "10000"}
    await esphome.runner.cleanup()


def make_tarball(names):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name in names:
            data = f"#!/bin/sh\necho {name}\n".encode()
            info = tarfile.TarInfo(f"tailscale_1.90.6_arm64/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_extract(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert tailscale.installed_version() is None
    tailscale.extract(
        make_tarball(["tailscale", "tailscaled", "systemd/tailscaled.service"]),
        "1.90.6",
    )
    assert tailscale.installed_version() == "1.90.6"
    assert os.access(tailscale.binary("tailscaled"), os.X_OK)
    with pytest.raises(RuntimeError):
        tailscale.extract(make_tarball(["tailscale"]), "1.90.7")


def test_helpers():
    assert tailscale.version_of("tailscale_1.90.6_arm64.tgz") == "1.90.6"
    assert tailscale.funnel_active({"AllowFunnel": {"a.ts.net:443": True}})
    assert not tailscale.funnel_active({"AllowFunnel": {}})
    assert not tailscale.funnel_active(None)
    assert tailscale.find_login_url(f"To enable, visit:\n\n  {ENABLE_URL}\n") == (
        ENABLE_URL
    )
    assert ra.valid_hostname("My FHEM!") == "my-fhem"
    assert ra.valid_hostname("") == "fhem"
    assert ra.fhem_address() is None
    assert sites.home_origin("http://192.168.1.5:6052/x") == "http://192.168.1.5:6052"
    assert sites.home_origin("http://raspberrypi:8080") == "http://raspberrypi:8080"
    assert sites.home_origin("http://8.8.8.8:80/") is None
    assert sites.home_origin("https://192.168.1.5/") is None
    assert sites.home_origin("http://example.com/") is None
    assert sites.home_origin("http://u:p@192.168.1.5/") is None
    ports = sites.assign_ports(
        {
            "a": "http://10.0.0.1:1/",
            "z2m_frontend": "http://10.0.0.2:8080/",
            "b": "http://10.0.0.2:8080/x",
        }
    )
    assert ports == {
        8443: ("http://10.0.0.2:8080", ["z2m_frontend", "b"]),
        10000: ("http://10.0.0.1:1", ["a"]),
    }
