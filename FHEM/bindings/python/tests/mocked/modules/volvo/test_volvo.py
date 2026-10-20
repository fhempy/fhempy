import asyncio
import logging

import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

NAME = "testvolvo"
VIN = "YV1TESTVIN0000001"
OTP = "123456"


class FakeVolvo:
    """Volvo ID login flow and Volvo Cars API."""

    def __init__(self):
        self.base = ""
        self.refreshes = 0
        self.commands = []
        self.logins = 0
        app = web.Application()
        app.router.add_post("/as/authorization.oauth2", self.authorize)
        app.router.add_post("/pf-ws/authn/flows/flow1", self.flow)
        app.router.add_post("/as/token.oauth2", self.token)
        app.router.add_get("/connected-vehicle/v2/vehicles", self.vehicles)
        app.router.add_get("/connected-vehicle/v2/vehicles/{vin}", self.details)
        app.router.add_get(
            "/connected-vehicle/v2/vehicles/{vin}/commands", self.list_commands
        )
        app.router.add_post(
            "/connected-vehicle/v2/vehicles/{vin}/commands/{cmd}", self.command
        )
        app.router.add_get(
            "/connected-vehicle/v2/vehicles/{vin}/{endpoint}", self.status
        )
        app.router.add_get("/energy/v2/vehicles/{vin}/state", self.energy)
        app.router.add_get("/location/v1/vehicles/{vin}/location", self.location)
        self.app = app

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = self.runner.addresses[0][1]
        self.base = f"http://localhost:{port}"

    async def stop(self):
        await self.runner.cleanup()

    async def authorize(self, request):
        form = await request.post()
        assert form["client_id"] == "h4Yf0b"
        assert form["response_mode"] == "pi.flow"
        self.logins += 1
        resp = web.json_response(
            {
                "status": "USERNAME_PASSWORD_REQUIRED",
                "_links": {
                    "checkUsernamePassword": {
                        "href": f"{self.base}/pf-ws/authn/flows/flow1"
                    }
                },
            }
        )
        resp.set_cookie("PF", "flowcookie")
        return resp

    async def flow(self, request):
        assert request.cookies.get("PF") == "flowcookie"
        assert request.headers["x-xsrf-header"] == "PingFederate"
        action = request.query["action"]
        href = f"{self.base}/pf-ws/authn/flows/flow1"
        if action == "checkUsernamePassword":
            data = await request.json()
            if data != {"username": "user@example.com", "password": "secret"}:
                return web.json_response(
                    {"code": "VALIDATION_ERROR", "message": "wrong"}, status=400
                )
            return web.json_response(
                {"status": "OTP_REQUIRED", "_links": {"checkOtp": {"href": href}}}
            )
        if action == "checkOtp":
            data = await request.json()
            if data["otp"] != OTP:
                return web.json_response({"message": "Invalid OTP"}, status=400)
            return web.json_response(
                {
                    "status": "OTP_VERIFIED",
                    "_links": {"continueAuthentication": {"href": href}},
                }
            )
        if action == "continueAuthentication":
            return web.json_response(
                {"status": "COMPLETED", "authorizeResponse": {"code": "code1"}}
            )
        return web.json_response({}, status=400)

    async def token(self, request):
        assert request.headers["authorization"].startswith("Basic ")
        form = await request.post()
        if form["grant_type"] == "authorization_code":
            assert form["code"] == "code1"
            return web.json_response(
                {
                    "access_token": "access1",
                    "refresh_token": "refresh1",
                    "token_type": "Bearer",
                    "expires_in": 1799,
                }
            )
        if form["grant_type"] == "refresh_token":
            if form["refresh_token"] != "refresh1":
                return web.json_response({"error": "invalid_grant"}, status=400)
            self.refreshes += 1
            return web.json_response(
                {
                    "access_token": f"access-refreshed{self.refreshes}",
                    "token_type": "Bearer",
                    "expires_in": 1799,
                }
            )
        return web.json_response({}, status=400)

    def check_auth(self, request):
        assert request.headers["vcc-api-key"] == "apikey"
        assert request.headers["authorization"].startswith("Bearer access")

    async def vehicles(self, request):
        self.check_auth(request)
        return web.json_response({"data": [{"vin": VIN}]})

    async def details(self, request):
        self.check_auth(request)
        return web.json_response(
            {
                "data": {
                    "vin": VIN,
                    "modelYear": 2024,
                    "gearbox": "AUTOMATIC",
                    "fuelType": "ELECTRIC",
                    "externalColour": "Crystal White",
                    "batteryCapacityKWH": 78.0,
                    "images": {
                        "exteriorImageUrl": "https://example.com/e.png",
                        "internalImageUrl": "https://example.com/i.png",
                    },
                    "descriptions": {"model": "EX30", "steering": "LEFT"},
                }
            }
        )

    async def list_commands(self, request):
        self.check_auth(request)
        return web.json_response(
            {
                "data": [
                    {
                        "command": "LOCK",
                        "href": f"/connected-vehicle/v2/vehicles/{VIN}/commands/lock",
                    },
                    {
                        "command": "CLIMATIZATION_START",
                        "href": f"/connected-vehicle/v2/vehicles/{VIN}"
                        "/commands/climatization-start",
                    },
                ]
            }
        )

    async def command(self, request):
        self.check_auth(request)
        self.commands.append(request.match_info["cmd"])
        return web.json_response(
            {"data": {"vin": VIN, "invokeStatus": "COMPLETED", "message": ""}}
        )

    async def status(self, request):
        self.check_auth(request)
        endpoint = request.match_info["endpoint"]
        if endpoint == "doors":
            return web.json_response(
                {
                    "data": {
                        "centralLock": {
                            "value": "LOCKED",
                            "timestamp": "2026-10-20T10:00:00.000Z",
                        }
                    }
                }
            )
        if endpoint == "odometer":
            return web.json_response(
                {
                    "data": {
                        "odometer": {
                            "value": 12345,
                            "unit": "km",
                            "timestamp": "2026-10-20T10:00:00.000Z",
                        }
                    }
                }
            )
        return web.json_response({"error": {"message": "not found"}}, status=404)

    async def energy(self, request):
        self.check_auth(request)
        return web.json_response(
            {
                "batteryChargeLevel": {
                    "status": "OK",
                    "value": 80,
                    "unit": "percentage",
                    "updatedAt": "2026-10-20T10:00:00Z",
                },
                "chargingCurrentLimit": {
                    "status": "ERROR",
                    "code": "NOT_SUPPORTED",
                    "message": "Resource is not supported for this vehicle",
                },
            }
        )

    async def location(self, request):
        self.check_auth(request)
        return web.json_response(
            {"error": {"message": "Forbidden", "description": "scope"}}, status=403
        )


async def wait_for(condition, timeout=5):
    for _ in range(int(timeout / 0.05)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("condition not met")


@pytest_asyncio.fixture
async def fake_volvo(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    await check_and_install_dependencies("volvo")

    from fhempy.lib.volvo import volvo as volvo_module

    fake = FakeVolvo()
    await fake.start()
    mocker.patch.object(
        volvo_module, "AUTH_URL", f"{fake.base}/as/authorization.oauth2"
    )
    mocker.patch.object(volvo_module, "TOKEN_URL", f"{fake.base}/as/token.oauth2")
    mocker.patch("volvocarsapi.api._API_URL", fake.base)
    yield fake, volvo_module
    await fake.stop()


async def define(volvo_module):
    testhash = {"NAME": NAME, "FHEMPYTYPE": "volvo"}
    device = volvo_module.volvo(logging.getLogger(__name__))
    await device.Define(
        testhash,
        [NAME, "fhempy", "volvo", "apikey", "user@example.com", "secret"],
        {},
    )
    return device, testhash


def readings():
    return mock_fhem.readings.get(NAME, {})


@pytest.mark.asyncio
async def test_otp_login_and_readings(fake_volvo):
    fake, volvo_module = fake_volvo
    device, testhash = await define(volvo_module)
    try:
        await wait_for(lambda: readings().get("state", "").startswith("one-time"))

        await device.Set(testhash, [NAME, "otp", "000000"], {})
        await wait_for(lambda: "failed" in readings().get("state", ""))

        await device.Set(testhash, [NAME, "login"], {})
        await wait_for(lambda: fake.logins == 2)
        await wait_for(lambda: readings().get("state", "").startswith("one-time"))
        await device.Set(testhash, [NAME, "otp", OTP], {})
        await wait_for(lambda: "doors_centralLock" in readings())

        r = readings()
        assert r["doors_centralLock"] == "LOCKED"
        assert r["doors_centralLock_timestamp"].startswith("2026-10-20T10:00:00")
        assert r["odometer_odometer"] == 12345
        assert r["odometer_odometer_unit"] == "km"
        assert r["car_model"] == "EX30"
        assert r["car_fuelType"] == "ELECTRIC"
        assert r["car_vin"] == VIN
        await wait_for(lambda: "energy_batteryChargeLevel" in readings())
        assert readings()["energy_batteryChargeLevel"] == 80
        assert readings()["energy_batteryChargeLevel_unit"] == "percentage"
        assert "energy_chargingCurrentLimit" not in readings()
        assert "location_latitude" not in readings()
        assert r["login_valid_until"] != ""
        # token is stored encrypted
        assert "refresh1" not in r[volvo_module.TOKEN_READING]

        setlist = await device.Set(testhash, [NAME, "?"], {})
        assert "lock:noArg" in setlist
        assert "climatization_start:noArg" in setlist
        assert "otp" in setlist

        await device.Set(testhash, [NAME, "climatization_start"], {})
        await wait_for(lambda: fake.commands == ["climatization-start"])
        await wait_for(lambda: readings().get("lastcommand") == "COMPLETED")
        assert readings()["lastcommand_name"] == "climatization_start"
    finally:
        await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_stored_token_is_refreshed(fake_volvo):
    fake, volvo_module = fake_volvo
    device, testhash = await define(volvo_module)
    try:
        await wait_for(lambda: readings().get("state", "").startswith("one-time"))
        await device.Set(testhash, [NAME, "otp", OTP], {})
        await wait_for(lambda: "doors_centralLock" in readings())
    finally:
        await device.Undefine(testhash)

    # restart: stored refresh token is used, no new one-time password
    mock_fhem.readings[NAME].pop("doors_centralLock")
    device, testhash = await define(volvo_module)
    try:
        await wait_for(lambda: "doors_centralLock" in readings())
        assert fake.logins == 1
    finally:
        await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_expired_refresh_token_starts_login(fake_volvo):
    fake, volvo_module = fake_volvo
    device, testhash = await define(volvo_module)
    try:
        await wait_for(lambda: readings().get("state", "").startswith("one-time"))
        await device.Set(testhash, [NAME, "otp", OTP], {})
        await wait_for(lambda: "doors_centralLock" in readings())

        # expired access token is refreshed
        device.auth.invalidate_access_token()
        mock_fhem.readings[NAME].pop("doors_centralLock")
        await device.Set(testhash, [NAME, "update"], {})
        await wait_for(lambda: "doors_centralLock" in readings())
        assert fake.refreshes == 1
        assert fake.logins == 1

        # expired refresh token starts a new login
        device.auth.token["refresh_token"] = "expired"
        device.auth.invalidate_access_token()
        await device.Set(testhash, [NAME, "update"], {})
        await wait_for(lambda: fake.logins == 2)
        await wait_for(lambda: readings().get("state", "").startswith("one-time"))
    finally:
        await device.Undefine(testhash)
