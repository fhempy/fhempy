import asyncio
import importlib
import logging

import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

NAME = "testskoda"
VIN = "TMBTESTVIN0000001"
API_KEY = "testkey"


class FakeSkoda:
    """MyŠkoda Public API."""

    def __init__(self):
        self.base = ""
        self.requests = []
        self.commands = []
        self.rate_limited = False
        app = web.Application()
        app.router.add_get("/api/v1/vehicles/{vin}", self.vehicle)
        app.router.add_route("*", "/api/v1/vehicles/{vin}/{cmd:.+}", self.command)
        self.app = app

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = self.runner.addresses[0][1]
        self.base = f"http://127.0.0.1:{port}"

    async def stop(self):
        await self.runner.cleanup()

    def check(self, request):
        assert request.headers["X-API-Key"] == API_KEY
        assert request.match_info["vin"] == VIN

    async def vehicle(self, request):
        self.check(request)
        self.requests.append(request.query.get("include", ""))
        headers = {"RateLimit-Remaining": "99", "X-API-Key-Expires-At": "2027-01-01"}
        if self.rate_limited:
            return web.json_response(
                {"title": "Too many requests"},
                status=429,
                headers={"Retry-After": "1200"},
            )
        return web.json_response(
            {
                "vehicle": {
                    "name": "Enyaq",
                    "odometer": {"mileageInKm": 12345},
                    "fuelStatus": {
                        "totalRangeInKm": 400,
                        "primaryEngineRange": {"currentSoCInPercent": 80},
                    },
                    "status": {
                        "overall": {"doorsLocked": "YES", "locked": True},
                        "detail": {"trunk": "CLOSED"},
                    },
                    "parkingPosition": {
                        "gpsCoordinates": {"latitude": 48.1, "longitude": 16.3}
                    },
                },
                "errors": [{"type": "AUXILIARY_HEATING_UNSUPPORTED"}],
            },
            headers=headers,
        )

    async def command(self, request):
        self.check(request)
        body = await request.json() if request.can_read_body else None
        self.commands.append((request.method, request.match_info["cmd"], body))
        if request.match_info["cmd"] == "charging/mode":
            return web.json_response({"detail": "Charge mode not allowed"}, status=400)
        return web.Response(status=202)


async def wait_for(condition, timeout=5):
    for _ in range(int(timeout / 0.05)):
        if condition():
            return
        await asyncio.sleep(0.05)
    raise AssertionError("condition not met")


@pytest_asyncio.fixture
async def fake_skoda(mocker):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes.pop(NAME, None)

    # the package exports the class under the module's name
    skoda_module = importlib.import_module("fhempy.lib.skoda_api.skoda_api")

    fake = FakeSkoda()
    await fake.start()
    mocker.patch.object(skoda_module, "API_BASE", fake.base)
    yield fake, skoda_module
    await fake.stop()


async def define(skoda_module, args):
    testhash = {"NAME": NAME, "FHEMPYTYPE": "skoda_api"}
    device = skoda_module.skoda_api(logging.getLogger(__name__))
    ret = await device.Define(testhash, [NAME, "fhempy", "skoda_api"] + args, {})
    assert not ret
    return device, testhash


def readings():
    return mock_fhem.readings.get(NAME, {})


@pytest.mark.asyncio
async def test_readings_and_commands(fake_skoda):
    fake, skoda_module = fake_skoda
    device, testhash = await define(skoda_module, [API_KEY, VIN.lower()])
    try:
        assert await device.Set(testhash, [NAME, "?"], {}) == (
            "Unknown argument ?, choose one of update:noArg"
        )
        await wait_for(lambda: readings().get("state") == "connected")
        assert "airConditioning" in fake.requests[0].split(",")

        r = readings()
        assert r["mileage"] == "12345"
        assert r["fuelLevel"] == "80"
        assert r["totalRange"] == "400"
        assert r["doorsLocked"] == "YES"
        assert r["locked"] == "true"
        assert r["latitude"] == "48.1"
        assert r["api_vehicle_status_detail_trunk"] == "CLOSED"
        assert r["apiErrors"] == "AUXILIARY_HEATING_UNSUPPORTED"
        assert r["rateLimitRemaining"] == "99"
        assert r["apiKeyExpiresAt"] == "2027-01-01"

        setlist = await device.Set(testhash, [NAME, "?"], {})
        assert "start_air_conditioning" in setlist
        assert "charge_limit:slider,50,10,100" in setlist
        assert "start_auxiliary_heating" not in setlist

        assert await device.Set(testhash, [NAME, "start_air_conditioning"], {}) == ""
        assert fake.commands[-1] == (
            "POST",
            "air-conditioning/start",
            {
                "targetTemperature": {"value": 21.0, "unit": "CELSIUS"},
                "airConditioningWithoutExternalPower": True,
            },
        )
        assert readings()["lastCommandStatus"] == "202"

        assert await device.Set(testhash, [NAME, "stop_charging"], {}) == ""
        assert fake.commands[-1] == ("POST", "charging/stop", {})

        assert await device.Set(testhash, [NAME, "charge_limit", "80"], {}) == ""
        assert fake.commands[-1] == (
            "PUT",
            "charging/limit",
            {"targetStateOfChargeInPercent": 80},
        )

        ret = await device.Set(testhash, [NAME, "charge_mode", "manual"], {})
        assert ret == "HTTP 400: Charge mode not allowed"
        assert readings()["lastCommandError"] == ret
        assert (
            "unsupported"
            in (await device.Set(testhash, [NAME, "charge_mode", "FAST"], {})).lower()
        )
    finally:
        await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_rate_limit_waits(fake_skoda):
    fake, skoda_module = fake_skoda
    fake.rate_limited = True
    device, testhash = await define(skoda_module, [API_KEY, VIN])
    try:
        await wait_for(lambda: readings().get("state") == "API error")
        assert readings()["lastApiError"] == "HTTP 429: Too many requests"
        # Retry-After of the server delays the next poll
        device._retry_after = 0
        await device.fetch_once()
        assert device._retry_after == 1200
    finally:
        await device.Undefine(testhash)


@pytest.mark.asyncio
async def test_missing_vin_and_attribute(fake_skoda):
    fake, skoda_module = fake_skoda
    device, testhash = await define(skoda_module, [API_KEY])
    try:
        await wait_for(lambda: readings().get("state") == "API key or VIN missing")
        assert await device.Set(testhash, [NAME, "update"], {}) == (
            "API key or VIN missing."
        )
        await device.Attr(testhash, ["set", NAME, "vin", VIN], {})
        await wait_for(lambda: readings().get("state") == "connected")
    finally:
        await device.Undefine(testhash)
