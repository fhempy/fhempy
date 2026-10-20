import asyncio
import json
import logging
import time
from types import SimpleNamespace

import pytest
import pytest_asyncio
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

logger = logging.getLogger(__name__)

NAME = "testbmw"
CLIENT_ID = "11111111-2222-3333-4444-555555555555"
VIN = "WBA00000000000001"
GCID = "gcid-1234"

TELEMATIC = {
    "vehicle.drivetrain.batteryManagement.header": {
        "timestamp": "2026-10-20T12:00:00.000Z",
        "unit": "%",
        "value": "74",
    },
    "vehicle.drivetrain.electricEngine.kombiRemainingElectricRange": {
        "timestamp": "2026-10-20T12:00:00.000Z",
        "unit": "km",
        "value": "286",
    },
    "vehicle.cabin.door.row1.driver.isOpen": {
        "timestamp": "2026-10-20T11:00:00.000Z",
        "unit": None,
        "value": "false",
    },
    "vehicle.powertrain.tractionBattery.charging.port.anyPosition.isPlugged": {
        "timestamp": "2026-10-20T11:00:00.000Z",
        "unit": None,
        "value": True,
    },
    "vehicle.status.checkControlMessages": {
        "timestamp": "2026-10-20T11:00:00.000Z",
        "unit": None,
        "value": [{"type": "TIRE_PRESSURE", "severity": "LOW"}],
    },
    "vehicle.body.flap.isLocked": {
        "timestamp": "2026-10-20T11:00:00.000Z",
        "unit": None,
        "value": "true",
    },
    "vehicle.drivetrain.electricEngine.charging.timeRemaining": {
        "timestamp": None,
        "unit": "min",
        "value": None,
    },
}


class FakeBmw:
    """BMW login (gcdm) and CarData API"""

    def __init__(self):
        self.calls = []
        self.pending = 1
        self.refresh_ok = True
        self.reject_descriptors = False
        self.containers = []
        self.token_no = 0
        self.vins = [VIN]

    def tokens(self):
        self.token_no += 1
        return {
            "access_token": f"access{self.token_no}",
            "id_token": f"id{self.token_no}",
            "refresh_token": f"refresh{self.token_no}",
            "gcid": GCID,
            "expires_in": 3600,
            "token_type": "Bearer",
        }

    async def device_code(self, request):
        data = await request.post()
        self.calls.append("device_code")
        assert data["client_id"] == CLIENT_ID
        assert data["code_challenge_method"] == "S256"
        assert "cardata:streaming:read" in data["scope"]
        return web.json_response(
            {
                "device_code": "devcode",
                "user_code": "ABCD1234",
                "verification_uri": "https://customer.bmwgroup.com/oneid/link",
                "verification_uri_complete": (
                    "https://customer.bmwgroup.com/oneid/link?user_code=ABCD1234"
                ),
                "expires_in": 30,
                "interval": 0.05,
            }
        )

    async def token(self, request):
        data = await request.post()
        grant = data["grant_type"]
        self.calls.append(f"token:{grant.split(':')[-1]}")
        if grant == "refresh_token":
            if not self.refresh_ok or not data["refresh_token"].startswith("refresh"):
                return web.json_response(
                    {"error": "invalid_grant", "error_description": "expired"},
                    status=400,
                )
            return web.json_response(self.tokens())
        assert data["device_code"] == "devcode"
        assert data["code_verifier"]
        if self.pending > 0:
            self.pending -= 1
            return web.json_response({"error": "authorization_pending"}, status=400)
        return web.json_response(self.tokens())

    def check_auth(self, request):
        assert request.headers["Authorization"] == f"Bearer access{self.token_no}"
        assert request.headers["x-version"] == "v1"

    async def mappings(self, request):
        self.check_auth(request)
        self.calls.append("mappings")
        return web.json_response(
            [{"vin": v, "mappingType": "PRIMARY"} for v in self.vins]
        )

    async def basic_data(self, request):
        self.check_auth(request)
        self.calls.append("basicData")
        return web.json_response(
            {
                "brand": "BMW",
                "modelName": "iX3 50 xDrive",
                "driveTrain": "BEV",
                "colourDescription": "ALPINWEISS",
                "constructionDate": "2026-03-01T00:00:00.000+0000",
                "seriesDevt": "NA5",
            }
        )

    async def list_containers(self, request):
        self.check_auth(request)
        self.calls.append("containers")
        return web.json_response({"containers": self.containers})

    async def create_container(self, request):
        self.check_auth(request)
        body = await request.json()
        self.calls.append(f"create:{len(body['technicalDescriptors'])}")
        if self.reject_descriptors and len(body["technicalDescriptors"]) > 20:
            return web.json_response({"message": "invalid descriptor"}, status=400)
        container = {
            "containerId": f"container{len(self.containers) + 1}",
            "name": body["name"],
            "state": "ACTIVE",
            "technicalDescriptors": body["technicalDescriptors"],
        }
        self.containers.append(container)
        return web.json_response(container)

    async def telematic(self, request):
        self.check_auth(request)
        self.calls.append("telematic")
        assert request.query["containerId"] == self.containers[-1]["containerId"]
        return web.json_response({"telematicData": TELEMATIC})

    async def start(self):
        app = web.Application()
        app.router.add_post("/gcdm/oauth/device/code", self.device_code)
        app.router.add_post("/gcdm/oauth/token", self.token)
        app.router.add_get("/customers/vehicles/mappings", self.mappings)
        app.router.add_get("/customers/vehicles/{vin}/basicData", self.basic_data)
        app.router.add_get("/customers/containers", self.list_containers)
        app.router.add_post("/customers/containers", self.create_container)
        app.router.add_get("/customers/vehicles/{vin}/telematicData", self.telematic)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        return f"http://127.0.0.1:{port}"

    async def stop(self):
        await self.runner.cleanup()


class FakeMessages:
    def __init__(self, queue):
        self.queue = queue

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        payload = await self.queue.get()
        return SimpleNamespace(payload=payload)


class FakeMqtt:
    instances = []

    def __init__(self, hostname, port, **kwargs):
        self.hostname = hostname
        self.port = port
        self.kwargs = kwargs
        self.queue = asyncio.Queue()
        self.subscribed = []
        FakeMqtt.instances.append(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def messages(self):
        return FakeMessages(self.queue)

    async def subscribe(self, topic):
        self.subscribed.append(topic)

    def send(self, message):
        self.queue.put_nowait(json.dumps(message).encode())


async def wait_for(check, name=NAME):
    for _ in range(200):
        await asyncio.sleep(0.02)
        if check(mock_fhem.readings.get(name, {})):
            return
    raise AssertionError(f"Timeout, readings: {mock_fhem.readings.get(name)}")


@pytest_asyncio.fixture
async def env(mocker):
    await check_and_install_dependencies("bmw")
    from fhempy.lib.bmw import cardata

    server = FakeBmw()
    url = await server.start()
    mocker.patch.object(cardata, "AUTH_URL", f"{url}/gcdm/oauth")
    mocker.patch.object(cardata, "API_URL", url)
    mocker.patch("aiomqtt.Client", FakeMqtt)
    FakeMqtt.instances = []
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes[NAME] = {}
    modules = []

    async def define(*args):
        from fhempy.lib.bmw import bmw

        hash = {"NAME": NAME, "FHEMPYTYPE": "bmw"}
        module = bmw.bmw(logger)
        modules.append(module)
        await module.Define(hash, [NAME, "fhempy", "bmw", *args], {})
        return hash, module

    yield SimpleNamespace(server=server, define=define)
    for module in modules:
        await module.Undefine(module.hash)
    await server.stop()


@pytest.mark.asyncio
async def test_setup_login_and_data(env):
    hash, module = await env.define()
    await wait_for(lambda r: r.get("state", "").startswith("set client_id"))
    page = module.setup_html()
    assert "CarData Client erstellen" in page and "bmwClientId" in page

    assert await module.Set(hash, [NAME, "client_id", CLIENT_ID], {}) is None
    await wait_for(lambda r: "login_code" in r)
    readings = mock_fhem.readings[NAME]
    assert readings["login_code"] == "ABCD1234"
    assert "ABCD1234" in readings["state"]
    assert "user_code=ABCD1234" in module.setup_html()

    await wait_for(lambda r: r.get("state") == "74% 286 km")
    readings = mock_fhem.readings[NAME]
    assert "login_code" not in readings
    assert readings["vin"] == VIN
    assert readings["model"] == "iX3 50 xDrive"
    assert readings["construction_date"] == "2026-03-01"
    assert readings["soc"] == "74"
    assert readings["range"] == "286"
    assert readings["door_front_driver"] == "closed"
    assert readings["plugged"] == "yes"
    assert readings["body_flap_isLocked"] == "1"
    assert json.loads(readings["check_control_messages"])[0]["severity"] == "LOW"
    assert "charging_time_remaining" not in readings
    assert readings[".refresh_token"].startswith("crypt-aes:")
    assert "refresh1" not in readings[".refresh_token"]
    assert readings[".container_id"] == "container1"
    assert hash["MODEL"] == "iX3 50 xDrive"
    assert "Datenauswahl" in module.setup_html()
    assert env.server.calls == [
        "device_code",
        "token:device_code",
        "token:device_code",
        "mappings",
        "basicData",
        "containers",
        "create:45",
        "telematic",
    ]
    await wait_for(lambda r: r.get("api_requests_24h") == 5)

    # live data from the stream
    await wait_for(lambda r: r.get("stream") == "connected")
    mqtt = FakeMqtt.instances[-1]
    assert (mqtt.hostname, mqtt.port) == (
        "customer.streaming-cardata.bmwgroup.com",
        9000,
    )
    assert mqtt.kwargs["username"] == GCID
    assert mqtt.kwargs["password"] == "id1"
    assert mqtt.kwargs["tls_context"] is not None
    assert mqtt.subscribed == [f"{GCID}/{VIN}"]
    mqtt.send(
        {
            "vin": "OTHER",
            "data": {
                "vehicle.drivetrain.batteryManagement.header": {"value": 10},
            },
        }
    )
    mqtt.send(
        {
            "vin": VIN,
            "data": {
                "vehicle.drivetrain.batteryManagement.header": {
                    "value": 75,
                    "timestamp": "2026-10-20T12:05:00Z",
                },
                "vehicle.cabin.infotainment.navigation.currentLocation.latitude": {
                    "value": 48.17
                },
            },
        }
    )
    await wait_for(lambda r: r.get("state") == "75% 286 km")
    assert mock_fhem.readings[NAME]["latitude"] == "48.17"
    assert module.setup_html() == ""

    # set update requests the values again
    await module.Set(hash, [NAME, "update"], {})
    await wait_for(lambda _: env.server.calls.count("telematic") == 2)


@pytest.mark.asyncio
async def test_restart_uses_stored_login(env):
    hash, module = await env.define(CLIENT_ID)
    await wait_for(lambda r: r.get("state") == "74% 286 km")
    await module.Undefine(hash)
    env.server.calls.clear()

    hash, module = await env.define()
    await wait_for(
        lambda r: r.get("state") == "74% 286 km" and "telematic" in env.server.calls
    )
    # no new login and the container is reused
    assert env.server.calls == ["token:refresh_token", "telematic"]
    assert hash["MODEL"] == "iX3 50 xDrive"


@pytest.mark.asyncio
async def test_expired_login_shows_link_again(env):
    hash, module = await env.define(CLIENT_ID)
    await wait_for(lambda r: r.get("state") == "74% 286 km")
    await module.Undefine(hash)

    env.server.refresh_ok = False
    env.server.pending = 0
    hash, module = await env.define()
    await wait_for(lambda r: env.server.calls.count("device_code") == 2)
    env.server.refresh_ok = True
    await wait_for(lambda r: r.get("state") == "74% 286 km")
    assert mock_fhem.readings[NAME][".refresh_token"].startswith("crypt-aes:")


@pytest.mark.asyncio
async def test_rejected_descriptors_use_battery_values(env):
    env.server.reject_descriptors = True
    hash, module = await env.define(CLIENT_ID)
    await wait_for(lambda r: r.get("state") == "74% 286 km")
    assert "create:45" in env.server.calls
    assert "create:14" in env.server.calls


@pytest.mark.asyncio
async def test_quota_is_respected(env):
    mock_fhem.readings[NAME] = {".api_calls": ",".join([str(time.time())] * 45)}
    hash, module = await env.define(CLIENT_ID)
    await wait_for(
        lambda r: r.get("state") == "logged in"
        and "telematic" not in env.server.calls
        and len(env.server.calls) >= 6
    )
    await asyncio.sleep(0.2)
    assert "telematic" not in env.server.calls
    # set update may use the remaining requests
    await module.Set(hash, [NAME, "update"], {})
    await wait_for(lambda r: r.get("state") == "74% 286 km")


@pytest.mark.asyncio
async def test_vin_attribute(env):
    env.server.vins = ["WBA0000000000000X", VIN]
    mock_fhem.attributes[NAME] = {"vin": VIN.lower()}
    hash, module = await env.define(CLIENT_ID)
    await wait_for(lambda r: r.get("state") == "74% 286 km")
    readings = mock_fhem.readings[NAME]
    assert readings["vin"] == VIN
    assert readings["vehicles"] == f"WBA0000000000000X,{VIN}"
