import logging

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web
from aiohttp.test_utils import TestServer
from tests.utils import mock_fhem

from fhempy.lib.fusionsolar import fusionsolar as fusionsolar_module
from fhempy.lib.fusionsolar.fusionsolar_api import (
    FusionSolarError,
    FusionSolarRestApi,
)


class StopLoop(Exception):
    pass


class FakeApi:
    """Plays a script of login/update results, True = works."""

    captcha_required = False

    logins = []
    updates = []

    def __init__(self, *args):
        self.battery_soc = None
        self.device_signals = {}
        self.data_string = ""

    def __getattr__(self, name):
        return 1

    async def login(self):
        result = FakeApi.logins.pop(0)
        self.captcha_required = result == "captcha"
        return result is True

    async def update(self):
        if not FakeApi.updates.pop(0):
            raise FusionSolarError("Response was no JSON, session expired?")


async def run_update_loop(mocker, logins, updates, sleeps):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("testsolar", None)
    FakeApi.logins = list(logins)
    FakeApi.updates = list(updates)
    mocker.patch.object(fusionsolar_module, "FusionSolarRestApi", FakeApi)

    states = []
    delays = []
    orig_update = mock_fhem.readingsSingleUpdate

    async def single_update(hash, reading, value, trigger):
        if reading == "state":
            states.append(value)
        return await orig_update(hash, reading, value, trigger)

    mocker.patch("fhempy.lib.fhem.readingsSingleUpdate", single_update)

    async def sleep(delay):
        delays.append(round(delay))
        if len(delays) >= sleeps:
            raise StopLoop()

    mocker.patch.object(fusionsolar_module.asyncio, "sleep", sleep)

    device = fusionsolar_module.fusionsolar(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "testsolar", "FHEMPYTYPE": "fusionsolar"},
        ["testsolar", "fhempy", "fusionsolar", "user", "pass"],
        {},
    )
    with pytest.raises(StopLoop):
        await device.update()
    return states, delays


@pytest.mark.asyncio
async def test_reconnects_after_hours_of_maintenance(mocker):
    # works, session expires, server down for 15 logins, back again
    logins = [True] + [False] * 15 + [True]
    updates = [True, False, True]
    states, delays = await run_update_loop(mocker, logins, updates, sleeps=18)

    # never gives up, waits longer and longer up to 15 minutes
    assert "login failed, no more retry" not in states
    assert states[1] == "failed, reconnect in 30s"
    assert states[2:5] == [
        "login failed, reconnect in 60s",
        "login failed, reconnect in 120s",
        "login failed, reconnect in 240s",
    ]
    assert delays[:2] == [300, 30]
    assert delays[2:17] == [60, 120, 240, 480] + [900] * 11
    # reconnected and updates readings with the new session
    assert mock_fhem.readings["testsolar"]["state"] == "connected"
    assert FakeApi.logins == []
    assert delays[17] == 300


@pytest.mark.asyncio
async def test_backoff_resets_after_successful_update(mocker):
    logins = [False, False, True, True]
    updates = [True, False, False]
    states, delays = await run_update_loop(mocker, logins, updates, sleeps=5)

    assert delays == [30, 60, 300, 30, 60]


@pytest.mark.asyncio
async def test_waits_longer_on_captcha(mocker):
    logins = ["captcha", "captcha", "captcha", False, True]
    updates = [True]
    states, delays = await run_update_loop(mocker, logins, updates, sleeps=5)

    assert states[1] == "captcha required, reconnect in 3600s"
    assert delays == [3600, 7200, 7200, 30, 300]


@pytest.mark.asyncio
async def test_login_detects_captcha(mocker):
    api = FusionSolarRestApi(logging.getLogger(__name__), "user", "pass")
    mocker.patch.object(api, "get_jsessionid", mocker.AsyncMock())
    mocker.patch.object(
        api, "get_pubkey", mocker.AsyncMock(return_value={"enableEncrypt": False})
    )
    validate = mocker.patch.object(
        api,
        "validate_user",
        mocker.AsyncMock(
            return_value={
                "errorCode": "411",
                "errorMsg": "Incorrect verification code.",
            }
        ),
    )

    assert await api.login() is False
    assert api.captcha_required is True

    validate.return_value = {"errorCode": "406", "errorMsg": "Incorrect password."}
    assert await api.login() is False
    assert api.captcha_required is False


@pytest_asyncio.fixture
async def server(monkeypatch):
    for var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
        monkeypatch.delenv(var, raising=False)

    async def login_page(request):
        return web.Response(text="<html>login</html>", content_type="text/html")

    async def data(request):
        return web.json_response({"success": True, "data": {"dn": "station"}})

    async def failed(request):
        return web.json_response({"success": False, "failCode": 305})

    async def unauthorized(request):
        return web.Response(status=401)

    app = web.Application()
    app.router.add_get("/login", login_page)
    app.router.add_get("/data", data)
    app.router.add_get("/failed", failed)
    app.router.add_get("/unauthorized", unauthorized)
    server = TestServer(app)
    await server.start_server()
    yield server
    await server.close()


@pytest.mark.asyncio
async def test_get_raises_on_expired_session(server):
    api = FusionSolarRestApi(logging.getLogger(__name__), "user", "pass")
    base = str(server.make_url("/"))

    assert await api._get(base + "data", {}) == {"dn": "station"}
    for path in ("login", "failed", "unauthorized"):
        with pytest.raises(FusionSolarError):
            await api._get(base + path, {})


@pytest.mark.asyncio
async def test_get_raises_if_server_unreachable(server):
    api = FusionSolarRestApi(logging.getLogger(__name__), "user", "pass")
    url = str(server.make_url("/data"))
    await server.close()

    with pytest.raises(aiohttp.ClientError):
        await api._get(url, {})
