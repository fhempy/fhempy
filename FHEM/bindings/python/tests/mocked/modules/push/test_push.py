import asyncio
import base64
import json
import logging
import os
import ssl

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)

NAME = "push"


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class Phone:
    """browser side of Web Push: keys of the subscription"""

    def __init__(self, endpoint):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        self.key = ec.generate_private_key(ec.SECP256R1())
        self.auth = os.urandom(16)
        public = self.key.public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
        self.sub = {
            "endpoint": endpoint,
            "expirationTime": None,
            "keys": {"p256dh": b64url(public), "auth": b64url(self.auth)},
        }

    def decrypt(self, body):
        import http_ece

        return json.loads(
            http_ece.decrypt(
                body, private_key=self.key, auth_secret=self.auth, version="aes128gcm"
            )
        )


class PushService:
    """push service of the browser (like FCM or Apple), https with own CA"""

    def __init__(self):
        self.received = []
        self.status = {}
        self.runner = None
        self.port = None

    async def handle(self, request):
        self.received.append(
            (request.match_info["id"], request.headers.copy(), await request.read())
        )
        return web.Response(status=self.status.get(request.match_info["id"], 201))

    async def start(self, tmp_path):
        from fhempy.lib.push import certs

        ca_key, ca_cert = certs.create_ca("test")
        key, cert = certs.create_server_cert(ca_key, ca_cert, ["127.0.0.1"])
        (tmp_path / "key.pem").write_text(certs.key_pem(key))
        (tmp_path / "cert.pem").write_text(certs.cert_pem(cert))
        server_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        server_ctx.load_cert_chain(tmp_path / "cert.pem", tmp_path / "key.pem")
        self.client_ctx = ssl.create_default_context(cadata=certs.cert_pem(ca_cert))
        app = web.Application()
        app.router.add_post("/push/{id}", self.handle)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0, ssl_context=server_ctx)
        await site.start()
        self.port = site._server.sockets[0].getsockname()[1]

    def endpoint(self, phone_id):
        return f"https://127.0.0.1:{self.port}/push/{phone_id}"

    async def stop(self):
        await self.runner.cleanup()


class FakeFhem:
    def __init__(self):
        self.commands = []
        self.remote = "0"

    async def send(self, hash, cmd):
        self.commands.append(cmd)
        if "FHEMPYTYPE=remote_access" in cmd:
            return self.remote
        if "AnalyzeCommandChain" in cmd:
            return ""
        if "open(my $fh, '>'" in cmd:
            return "ok"
        if "FHEMWEB $p$global" in cmd:
            return "port 8443"
        return ""


async def wait_for(condition, timeout=10):
    for _ in range(int(timeout * 20)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("condition not reached")


def readings():
    return mock_fhem.readings.get(NAME, {})


@pytest_asyncio.fixture
async def module(mocker, tmp_path):
    await check_and_install_dependencies("push")
    from fhempy.lib.push import push

    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes.pop(NAME, None)
    fake = FakeFhem()
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake.send)
    service = PushService()
    await service.start(tmp_path)
    mod = push.push(logger)

    async def http_session():
        if mod._session is None:
            mod._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=service.client_ctx)
            )
        return mod._session

    mod.http_session = http_session
    mod.fake = fake
    mod.service = service
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "push"}, [], {})
    yield mod
    await mod.Undefine(mod.hash)
    await service.stop()


async def register(mod, phone_id, name):
    phone = Phone(mod.service.endpoint(phone_id))
    data = b64url(json.dumps({"name": name, "sub": phone.sub}).encode())
    assert await mod.Set(mod.hash, [NAME, "register", data], {}) is None
    return phone


def messages(mod, phone, phone_id):
    return [
        phone.decrypt(body) for pid, _, body in mod.service.received if pid == phone_id
    ]


@pytest.mark.asyncio
async def test_register_and_send(module):
    assert readings()["state"] == "no phone yet"
    error = await module.Set(module.hash, [NAME, "message", "Hello"], {})
    assert "No phone" in error

    phone = await register(module, "p1", "Pixel, 7")
    assert readings()["devices"] == "Pixel 7"
    assert readings()["state"] == "ready, 1 phone"
    # welcome message right after enabling
    assert "Notifications work on Pixel 7" in messages(module, phone, "p1")[0]["body"]
    headers = module.service.received[0][1]
    assert headers["Authorization"].startswith("vapid t=")
    assert headers["TTL"] == str(24 * 3600)
    assert headers["Content-Encoding"] == "aes128gcm"

    tablet = await register(module, "p2", "Pixel 7")
    assert readings()["devices"] == "Pixel 7, Pixel 7 2"

    ret = await module.Set(
        module.hash,
        [NAME, "message", "Washing", "machine", "is", "done"],
        {"title": "Laundry", "image": "https://example.com/cam.jpg"},
    )
    assert ret is None
    await wait_for(lambda: readings().get("delivered") == "2 of 2")
    msg = messages(module, phone, "p1")[-1]
    assert msg["title"] == "Laundry"
    assert msg["body"] == "Washing machine is done"
    assert msg["image"] == "https://example.com/cam.jpg"
    assert msg["dev"] == NAME
    assert messages(module, tablet, "p2")[-1]["body"] == "Washing machine is done"
    assert readings()["message"] == "Washing machine is done"

    # only to one phone
    count = len(module.service.received)
    await module.Set(module.hash, [NAME, "msg", "Only", "tablet"], {"to": "pixel 7 2"})
    await wait_for(lambda: len(module.service.received) == count + 1)
    assert module.service.received[-1][0] == "p2"
    error = await module.Set(module.hash, [NAME, "message", "x"], {"to": "iPhone"})
    assert error == "No phone named iphone"

    # the stored key and phones survive a restart
    from fhempy.lib.push import push

    again = push.push(logger)
    again.http_session = module.http_session
    await again.Define({"NAME": NAME, "FHEMPYTYPE": "push"}, [], {})
    assert again.public_key == module.public_key
    assert len(again._devices) == 2


@pytest.mark.asyncio
async def test_action_buttons(module):
    phone = await register(module, "p1", "Pixel 7")
    await module.Set(
        module.hash,
        [NAME, "message", "Somebody", "rings"],
        {"action": "Light on:set light on", "action2": "Open:set door open"},
    )
    await wait_for(lambda: len(messages(module, phone, "p1")) == 2)
    msg = messages(module, phone, "p1")[-1]
    assert [a["title"] for a in msg["actions"]] == ["Light on", "Open"]
    # the command itself never leaves FHEM
    assert "set light on" not in json.dumps(msg)

    token = msg["actions"][0]["action"]
    assert await module.Set(module.hash, [NAME, "action", token], {}) is None
    assert (
        module.fake.commands[-1] == "AnalyzeCommandChain(undef, 'set light on') // ''"
    )
    assert readings()["last_action"] == "set light on"
    # one use only
    again = await module.Set(module.hash, [NAME, "action", token], {})
    assert "already used" in again

    error = await module.Set(
        module.hash, [NAME, "message", "x"], {"action": "no command"}
    )
    assert "Label:FHEM command" in error


@pytest.mark.asyncio
async def test_gone_phone_is_removed(module):
    await register(module, "p1", "Pixel 7")
    await register(module, "p2", "iPhone")
    module.service.status["p1"] = 410
    module.service.status["p2"] = 500
    await module.Set(module.hash, [NAME, "message", "Hi"], {})
    await wait_for(lambda: readings().get("delivered") == "0 of 2")
    assert readings()["devices"] == "iPhone"
    assert readings()["last_error"].startswith("iPhone: Push failed: 500")

    assert await module.Set(module.hash, [NAME, "remove_device", "iPhone"], {}) is None
    assert readings()["devices"] == "-"


@pytest.mark.asyncio
async def test_unregister_and_invalid(module):
    await register(module, "p1", "Pixel 7")
    key = next(iter(module._devices))
    assert await module.Set(module.hash, [NAME, "unregister", key], {}) is None
    assert module._devices == {}

    bad = b64url(json.dumps({"name": "x", "sub": {"endpoint": "ftp://x"}}).encode())
    assert await module.Set(module.hash, [NAME, "register", bad], {}) == (
        "Invalid registration"
    )
    assert await module.Set(module.hash, [NAME, "register", "%%%"], {}) == (
        "Invalid registration"
    )


@pytest.mark.asyncio
async def test_detail_page(module):
    await register(module, "p1", "Pixel 7")
    module.fake.remote = "1 https://fhem.tail1234.ts.net"
    page = await module.setup_html()
    assert "fhempy/push.js" in page
    start = page.index("fhempyPush(") + len("fhempyPush(")
    config = json.loads(page[start : page.index("})", start) + 1])
    assert config["key"] == module.public_key
    assert config["devices"][0]["name"] == "Pixel 7"
    assert config["addresses"][0]["url"] == (
        "https://fhem.tail1234.ts.net/fhem?detail=push"
    )
    assert config["addresses"][0]["qr"].startswith("<img")
    assert config["remote_access"] is True


@pytest.mark.asyncio
async def test_local_https(module):
    from fhempy.lib.push import certs

    assert await module.Set(module.hash, [NAME, "local_https", "bad host!"], {}) == (
        "Invalid hostname bad host!"
    )
    ret = await module.Set(module.hash, [NAME, "local_https", "192.168.1.20"], {})
    assert ret is None
    assert readings()["local_https"] == "https://192.168.1.20:8443"
    written = next(c for c in module.fake.commands if "open(my $fh, '>'" in c)
    assert "certs/fhempy-push-" in written and "fhempy/push-ca.crt" in written
    setup = next(c for c in module.fake.commands if "FHEMWEB $p$global" in c)
    assert "HTTPS 1" in setup and "validFor" in setup

    # server certificate of FHEMWEB is signed by the CA of the phone
    ca = certs.load_cert(readings()[".ca_cert"].replace("\\n", "\n"))
    pem = written.split("'cert.pem' => '")[1].split("'")[0]
    cert = certs.load_cert(pem)
    assert cert.issuer == ca.subject
    assert not certs.needs_renewal(cert, ["192.168.1.20"])
    assert certs.needs_renewal(cert, ["192.168.1.21"])
    page = await module.setup_html()
    assert "https://192.168.1.20:8443/fhem?detail=push" in page
    assert "push-ca.crt" in page


def test_split_message():
    from fhempy.lib.push import push

    assert push.split_message(["Hello", "world"], {}) == ("Hello world", {})
    # the Pushbullet way: text | title
    assert push.split_message(["Door", "open", "|", "Alarm"], {}) == (
        "Door open",
        {"title": "Alarm"},
    )
    # words with = which are no option stay in the text
    assert push.split_message(["Temperature"], {"inside": "20"}) == (
        "Temperature inside=20",
        {},
    )
    assert push.parse_action("Light on: set a on;set b on") == (
        "Light on",
        "set a on;set b on",
    )


def test_hostnames():
    from fhempy.lib.push import certs

    assert certs.valid_hostname("FHEM.local") == "fhem.local"
    assert certs.valid_hostname("[fe80::1]") == "fe80::1"
    assert certs.valid_hostname("bad host") is None
    assert certs.valid_hostname("") is None
    assert all(certs.valid_hostname(n) for n in certs.local_names())
