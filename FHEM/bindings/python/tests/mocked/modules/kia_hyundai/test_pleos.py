import asyncio
import logging

import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

NAME = "testkia"
CLIENT_ID = "client-1234"
CLIENT_SECRET = "secret-5678"
VIN = "KNA00000000000001"

BATTERY = {
    "charge": {
        "plugin": "connected",
        "status": "charging",
        "charging": True,
        "stateOfCharge": 63,
        "targetStateOfCharge": {"standard": 80, "quick": 90},
        "remainTime": 95,
    },
    "timestamp": "2026-10-20T12:00:00Z",
}
POWERTRAIN = {
    "distanceToEmpties": [
        {"type": "EV", "value": "250", "unit": "km"},
        {"type": "TOTAL", "value": "-", "unit": "km"},
    ]
}
DRIVING = {"odometer": {"value": 10000, "unit": "mile"}}
LOCATION = {"location": {"latitude": 48.2, "longitude": 16.37}}


class FakePleos:
    def __init__(self):
        self.calls = []
        self.brand = "kia"
        self.tokens = 0
        self.rate_limited = False

    def check_auth(self, request):
        assert request.headers["Brand"] == self.brand
        if request.headers.get("Authorization") != f"Bearer token{self.tokens}":
            raise web.HTTPUnauthorized()

    async def token(self, request):
        body = await request.json()
        self.calls.append(f"token:{request.headers['Brand']}")
        if (
            request.headers["Brand"] != self.brand
            or body["clientId"] != CLIENT_ID
            or body["clientSecret"] != CLIENT_SECRET
        ):
            return web.json_response(
                {"code": "4010", "message": "invalid client"}, status=401
            )
        self.tokens += 1
        return web.json_response(
            {
                "data": {
                    "accessToken": f"token{self.tokens}",
                    "tokenType": "Bearer",
                    "expiresIn": 3600,
                }
            }
        )

    async def consent(self, request):
        self.check_auth(request)
        self.calls.append("consent")
        if self.rate_limited:
            return web.json_response(
                {"code": "4290", "message": "too many requests"}, status=429
            )
        return web.json_response(
            {
                "data": {
                    "vehicles": [
                        {
                            "vin": VIN,
                            "nickname": "",
                            "name": "EV6",
                            "type": "EV",
                            "sellname": "Kia EV6",
                        }
                    ]
                }
            }
        )

    async def vehicle(self, request):
        self.check_auth(request)
        endpoint = request.match_info["endpoint"]
        assert request.match_info["vin"] == VIN
        self.calls.append(endpoint)
        data = {
            "batteries": BATTERY,
            "powertrains": POWERTRAIN,
            "driving": DRIVING,
            "locations": LOCATION,
        }.get(endpoint)
        if data is None:
            return web.json_response({"code": "4045", "message": "No Data"}, status=400)
        return web.json_response({"data": data})

    async def start(self):
        app = web.Application()
        app.router.add_post("/v1/auth/personal-token", self.token)
        app.router.add_get("/v1/vehicles/consent", self.consent)
        app.router.add_get("/v1/vehicles/{vin}/{endpoint}", self.vehicle)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        return f"http://127.0.0.1:{port}/v1"

    async def stop(self):
        await self.runner.cleanup()


async def wait_for(check):
    for _ in range(200):
        await asyncio.sleep(0.02)
        if check(mock_fhem.readings.get(NAME, {})):
            return
    raise AssertionError(f"Timeout, readings: {mock_fhem.readings.get(NAME)}")


@pytest_asyncio.fixture
async def env(mocker):
    await check_and_install_dependencies("kia_hyundai")
    from fhempy.lib.kia_hyundai import pleos
    from fhempy.lib.kia_hyundai.kia_hyundai import kia_hyundai

    server = FakePleos()
    url = await server.start()
    mocker.patch.object(pleos, "API_URL", url)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes[NAME] = {}
    modules = []

    async def define():
        testhash = {"NAME": NAME, "FHEMPYTYPE": "kia_hyundai"}
        device = kia_hyundai(logging.getLogger(__name__))
        modules.append(device)
        assert await device.Define(testhash, [NAME, "fhempy", "kia_hyundai"], {}) is None
        return device, testhash

    yield server, define
    for device in modules:
        await device.Undefine(device.hash)
    await server.stop()


@pytest.mark.asyncio
async def test_setup_and_readings(env):
    server, define = env
    device, testhash = await define()
    await wait_for(lambda r: r.get("state") == "credentials missing")
    assert "Pleos Playground" in device.setup_html()
    assert "credentials" in await device.Set(testhash, [NAME, "?"], {})
    assert f"{NAME} icon car" in mock_fhem.command_attr

    await device.Set(testhash, [NAME, "credentials", CLIENT_ID, CLIENT_SECRET], {})
    await wait_for(lambda r: r.get("state") == "63% 250 km")
    readings = mock_fhem.readings[NAME]
    # brand found out automatically
    assert server.calls[:2] == ["token:kia", "consent"]
    assert readings["brand"] == "kia"
    assert readings["vin"] == VIN
    assert readings["model"] == "Kia EV6"
    assert readings["soc"] == 63
    assert readings["charging"] == "on"
    assert readings["plugged"] == "connected"
    assert readings["charge_limit_ac"] == 80
    assert readings["charge_limit_dc"] == 90
    assert readings["charging_time_remaining"] == 95
    assert readings["range"] == 250
    assert "range_total" not in readings
    assert readings["odometer"] == 16093
    assert readings["latitude"] == 48.2
    assert readings["battery_charge_stateOfCharge"] == 63
    assert readings["last_update"] == "2026-10-20T12:00:00Z"
    assert device.setup_html() == ""
    # secret is stored encrypted
    assert CLIENT_SECRET not in str(readings[".client_secret"])


@pytest.mark.asyncio
async def test_hyundai_brand_detection_and_restart(env):
    server, define = env
    server.brand = "hyundai"
    device, testhash = await define()
    await device.Set(testhash, [NAME, "credentials", CLIENT_ID, CLIENT_SECRET], {})
    await wait_for(lambda r: r.get("state") == "63% 250 km")
    assert server.calls[:3] == ["token:kia", "token:hyundai", "consent"]
    assert mock_fhem.readings[NAME]["brand"] == "hyundai"
    await device.Undefine(testhash)

    # after a restart the stored credentials and brand are used
    server.calls = []
    mock_fhem.readings[NAME]["state"] = "restarting"
    await define()
    await wait_for(lambda r: r.get("state") == "63% 250 km")
    assert server.calls[:2] == ["token:hyundai", "consent"]


@pytest.mark.asyncio
async def test_wrong_credentials(env):
    server, define = env
    device, testhash = await define()
    await device.Set(testhash, [NAME, "credentials", CLIENT_ID, "wrong"], {})
    await wait_for(lambda r: r.get("state", "").startswith("login failed"))
    assert server.calls == ["token:kia", "token:hyundai", "token:genesis"]
    assert "login failed" in device.setup_html()


@pytest.mark.asyncio
async def test_rate_limit(env):
    server, define = env
    server.rate_limited = True
    device, testhash = await define()
    await device.Set(testhash, [NAME, "credentials", CLIENT_ID, CLIENT_SECRET], {})
    await wait_for(lambda r: r.get("state") == "rate limit reached")
