import base64
import hashlib
import logging

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

USERNAME = "margit.musterfrau@example.com"
PASSWORD = "Margit1234!"
CODE = "b04c44f7-55c6-4c0e-b2af-e9d9408ded2b.949e0f0d"
B2C_KEY = "afb0be74-6455-44f5-a34d-6994223020ba"

CONSUMPTIONS = {
    "consumptionYesterday": {"value": 4711, "validated": True},
    "consumptionDayBeforeYesterday": {"value": 815, "validated": True},
}
METER_READINGS = {"meterReadings": [{"value": 1234567, "validated": True}]}
BASE_INFORMATION = {
    "hasSmartMeter": True,
    "zaehlpunkt": {"zaehlpunktnummer": "AT0010000000000000001000004392265"},
}


class FakeWienerNetze:
    """Minimal log.wien (Keycloak) + smartmeter API server."""

    def __init__(self, password=PASSWORD):
        self.password = password
        self.code_challenge = None
        self.tokens_issued = 0
        self.api_calls = []
        self.expire_next_api_call = False

    def app(self):
        from aiohttp import web

        app = web.Application()
        app.router.add_get("/auth/auth", self.login_page)
        app.router.add_post("/auth/username", self.username_step)
        app.router.add_post("/auth/password", self.password_step)
        app.router.add_post("/auth/token", self.token)
        app.router.add_get("/assets/app-config.json", self.app_config)
        app.router.add_get("/b2c/1.0/{endpoint:.*}", self.api)
        return app

    def url(self, path):
        return str(self.server.make_url(path))

    async def login_page(self, request):
        from aiohttp import web

        assert request.query["code_challenge_method"] == "S256"
        self.code_challenge = request.query["code_challenge"]
        resp = web.Response(
            text=f'<html><form action="{self.url("/auth/username")}?a=1&amp;b=2">'
            "</form></html>",
            content_type="text/html",
        )
        resp.set_cookie("AUTH_SESSION_ID", "session1")
        return resp

    async def username_step(self, request):
        from aiohttp import web

        assert request.cookies.get("AUTH_SESSION_ID") == "session1"
        assert request.query["b"] == "2"
        data = await request.post()
        assert data["username"] == USERNAME
        assert "password" not in data
        return web.Response(
            text=f'<html><form action="{self.url("/auth/password")}"></form></html>',
            content_type="text/html",
        )

    async def password_step(self, request):
        from aiohttp import web

        assert request.cookies.get("AUTH_SESSION_ID") == "session1"
        data = await request.post()
        if data["password"] != self.password:
            return web.Response(
                text='<html><form action="/auth/password"></form>Invalid</html>',
                content_type="text/html",
            )
        return web.Response(
            status=302,
            headers={
                "Location": "https://smartmeter-web.wienernetze.at/"
                f"#state=abc&session_state=def&code={CODE}&iss=https%3A%2F%2Flog.wien"
            },
        )

    async def token(self, request):
        from aiohttp import web

        data = await request.post()
        assert data["grant_type"] == "authorization_code"
        assert data["code"] == CODE
        challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(data["code_verifier"].encode()).digest()
            )
            .decode()
            .rstrip("=")
        )
        if challenge != self.code_challenge:
            return web.json_response({"error": "invalid_grant"}, status=400)
        self.tokens_issued += 1
        return web.json_response(
            {
                "access_token": f"token{self.tokens_issued}",
                "refresh_token": "refresh",
                "token_type": "Bearer",
                "expires_in": 300,
                "refresh_expires_in": 1800,
            }
        )

    async def app_config(self, request):
        from aiohttp import web

        return web.json_response(
            {
                "b2cApiUrl": self.url("/b2c/1.0"),
                "b2cApiKey": B2C_KEY,
                "b2bApiUrl": self.url("/b2b/1.0"),
                "b2bApiKey": "b2bkey",
            }
        )

    async def api(self, request):
        from aiohttp import web

        endpoint = request.match_info["endpoint"]
        self.api_calls.append(endpoint)
        if self.expire_next_api_call:
            self.expire_next_api_call = False
            return web.Response(status=401)
        assert request.headers["Authorization"] == f"Bearer token{self.tokens_issued}"
        assert request.headers["X-Gateway-APIKey"] == B2C_KEY
        data = {
            "zaehlpunkt/consumptions": CONSUMPTIONS,
            "zaehlpunkt/meterReadings": METER_READINGS,
            "zaehlpunkt/baseInformation": BASE_INFORMATION,
        }
        if endpoint not in data:
            return web.json_response({"Exception": "not found"}, status=404)
        return web.json_response(data[endpoint])


@pytest_asyncio.fixture
async def fake_server(mocker):
    await check_and_install_dependencies("wienernetze_smartmeter")
    from aiohttp.test_utils import TestServer

    from fhempy.lib.wienernetze_smartmeter.api import constants as const

    fake = FakeWienerNetze()
    server = TestServer(fake.app())
    await server.start_server()
    fake.server = server
    mocker.patch.object(const, "AUTH_URL", fake.url("/auth/"))
    mocker.patch.object(const, "API_CONFIG_URL", fake.url("/assets/app-config.json"))
    yield fake
    await server.close()


@pytest_asyncio.fixture
async def session():
    import aiohttp

    # cookies for IP addresses (test server) are only stored with unsafe=True
    async with aiohttp.ClientSession(
        cookie_jar=aiohttp.CookieJar(unsafe=True)
    ) as session:
        yield session


@pytest.mark.asyncio
async def test_login_and_api_calls(fake_server, session):
    from fhempy.lib.wienernetze_smartmeter.api.client import AsyncSmartmeter

    client = AsyncSmartmeter(USERNAME, PASSWORD, session)
    await client.login()
    assert client.is_logged_in()
    assert client.api_url == fake_server.url("/b2c/1.0")

    assert await client.consumptions() == CONSUMPTIONS
    assert await client.meter_readings() == METER_READINGS
    assert fake_server.api_calls == [
        "zaehlpunkt/consumptions",
        "zaehlpunkt/meterReadings",
    ]
    # still logged in, no second login
    assert fake_server.tokens_issued == 1


@pytest.mark.asyncio
async def test_relogin_on_401(fake_server, session):
    from fhempy.lib.wienernetze_smartmeter.api.client import AsyncSmartmeter

    client = AsyncSmartmeter(USERNAME, PASSWORD, session)
    fake_server.expire_next_api_call = True
    assert await client.base_information() == BASE_INFORMATION
    assert fake_server.tokens_issued == 2


@pytest.mark.asyncio
async def test_wrong_password(fake_server, session):
    from fhempy.lib.wienernetze_smartmeter.api.client import AsyncSmartmeter
    from fhempy.lib.wienernetze_smartmeter.api.errors import SmartmeterLoginError

    client = AsyncSmartmeter(USERNAME, "wrong", session)
    with pytest.raises(SmartmeterLoginError):
        await client.login()
    assert not client.is_logged_in()


@pytest.mark.asyncio
async def test_api_error_raises(fake_server, session):
    from fhempy.lib.wienernetze_smartmeter.api.client import AsyncSmartmeter
    from fhempy.lib.wienernetze_smartmeter.api.errors import SmartmeterQueryError

    client = AsyncSmartmeter(USERNAME, PASSWORD, session)
    with pytest.raises(SmartmeterQueryError):
        await client._request("unknown")


@pytest.mark.asyncio
async def test_module_readings(mocker, fake_server, session):
    mock_fhem.mock_module(mocker)
    from fhempy.lib.wienernetze_smartmeter.api.client import AsyncSmartmeter
    from fhempy.lib.wienernetze_smartmeter.wienernetze_smartmeter import (
        wienernetze_smartmeter,
    )

    mock_fhem.readings.pop("testsmartmeter", None)
    testhash = {"NAME": "testsmartmeter", "FHEMPYTYPE": "wienernetze_smartmeter"}
    device = wienernetze_smartmeter(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        testhash,
        ["testsmartmeter", "fhempy", "wienernetze_smartmeter", USERNAME, PASSWORD],
        {},
    )

    client = AsyncSmartmeter(USERNAME, PASSWORD, session)
    await device.login(client)
    await device.update(client)

    readings = mock_fhem.readings["testsmartmeter"]
    assert readings["consumptionYesterday_value"] == 4711
    assert readings["meterReadings_0_value"] == 1234567
    assert readings["state"] == "online"
