import asyncio
import datetime
import json
import logging
import os
import re
import time
from urllib.parse import parse_qs

import aiohttp
import pytest
import requests_mock
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fdp:
        return fdp.read()


class FakeRingOAuth:
    """Ring OAuth v2 sign-in (authorize page, signin, 2fa, code exchange)."""

    CSRF = "csrf-mock-token"
    CODE = "mock-auth-code"
    TWO_FA_CODE = "123456"

    def __init__(self, mock, require_2fa=False, password="asdfasdfasdf"):
        self.require_2fa = require_2fa
        self.password = password
        self.state = None
        self.signed_in = False
        self.token_requests = []
        mock.get("https://oauth.ring.com/oauth/v2/authorize", text=self._authorize)
        mock.post("https://oauth.ring.com/oauth/v2/signin", text=self._signin)
        mock.post("https://oauth.ring.com/oauth/v2/2fa/verify", text=self._verify)
        mock.post("https://oauth.ring.com/oauth/token", text=self._token)

    def _authorize(self, request, context):
        if "state" in request.qs:
            self.state = request.qs["state"][0]
            self.signed_in = False
            return (
                '<html><form><input type="hidden" name="csrf-token" value="'
                + self.CSRF
                + '"/></form></html>'
            )
        if not self.signed_in:
            context.status_code = 200
            return "<html>sign in</html>"
        context.status_code = 302
        context.headers["location"] = (
            "https://ring.com/signin/callback?code="
            + self.CODE
            + "&state="
            + self.state
        )
        return ""

    def _signin(self, request, context):
        form = parse_qs(request.text)
        assert form["csrf-token"] == [self.CSRF]
        if form["password"] != [self.password]:
            context.status_code = 401
            return '{"error": "invalid_grant"}'
        if self.require_2fa:
            context.status_code = 412
            return '{"tsv_state": "sms", "phone": "+1xxxxxx00"}'
        self.signed_in = True
        return "{}"

    def _verify(self, request, context):
        form = parse_qs(request.text)
        if form["2fa_code"] != [self.TWO_FA_CODE]:
            context.status_code = 400
            return "{}"
        self.signed_in = True
        return '{"redirect_url": "/oauth/v2/authorize"}'

    def _token(self, request, context):
        form = parse_qs(request.text)
        self.token_requests.append((form, request.headers))
        if form["grant_type"] == ["password"]:
            # Ring blocks the old password grant
            context.status_code = 406
            return "406 Not Acceptable"
        if form["grant_type"] == ["authorization_code"]:
            assert form["code"] == [self.CODE]
            assert "code_verifier" in form
        return load_fixture("ring_oauth.json")


def api(path):
    return re.compile(r"^https://api\.ring\.com/" + path + r"(\?.*)?$")


class FakeListener:
    """Replaces RingEventListener (Firebase push)."""

    instances = []
    start_result = True

    def __init__(self, ring, credentials=None, credentials_updated_callback=None):
        self.ring = ring
        self.credentials = credentials
        self.credentials_updated_callback = credentials_updated_callback
        self.callbacks = []
        self.stopped = False
        FakeListener.instances.append(self)

    async def start(self, *, timeout=10):
        if FakeListener.start_result:
            self.credentials_updated_callback({"fcm": "credentials"})
        return FakeListener.start_result

    def add_notification_callback(self, callback):
        self.callbacks.append(callback)
        return len(self.callbacks)

    async def stop(self):
        self.stopped = True

    def push(self, event):
        for callback in self.callbacks:
            callback(event)


class FakeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = body.encode() if isinstance(body, str) else body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(None, (), status=self.status)

    async def read(self):
        return self._body

    async def text(self):
        return self._body.decode()


class FakeCall:
    def __init__(self, method, url, kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs


class FakeApi:
    """Replaces aiohttp.ClientSession for the Ring API."""

    def __init__(self):
        self.routes = []
        self.calls = []

    def add(self, method, path, body, status=200):
        # newer routes win
        self.routes.insert(0, (method, api(path), status, body))

    def session(self, headers=None, **kwargs):
        fake_api = self

        class FakeSession:
            def __init__(self):
                self.headers = dict(headers or {})
                self.closed = False

            async def request(self, method, url, **kwargs):
                fake_api.calls.append(FakeCall(method, str(url), kwargs))
                for route_method, pattern, status, body in fake_api.routes:
                    if route_method == method and pattern.match(str(url)):
                        return FakeResponse(status, body)
                return FakeResponse(404, "not found")

            async def close(self):
                self.closed = True

        return FakeSession()


@pytest.fixture(autouse=True)
def mock_ring_requests(mocker):
    FakeListener.instances = []
    FakeListener.start_result = True
    mocker.patch("fhempy.lib.ring.ring.RingEventListener", FakeListener)
    fake_api = FakeApi()
    mocker.patch("fhempy.lib.ring.ring.aiohttp.ClientSession", fake_api.session)
    with requests_mock.Mocker() as mock:
        mock.fake_oauth = FakeRingOAuth(mock)
        mock.api = fake_api
        fake_api.add("POST", "clients_api/session", load_fixture("ring_session.json"))
        fake_api.add(
            "GET", "clients_api/ring_devices", load_fixture("ring_devices.json")
        )
        fake_api.add(
            "GET",
            r"clients_api/chimes/\d+/health",
            load_fixture("ring_chime_health_attrs.json"),
        )
        fake_api.add(
            "GET",
            r"clients_api/doorbots/\d+/health",
            load_fixture("ring_doorboot_health_attrs.json"),
        )
        fake_api.add(
            "GET",
            "clients_api/doorbots/987652/history",
            load_fixture("ring_doorbots.json"),
        )
        fake_api.add(
            "GET", "clients_api/dings/active", load_fixture("ring_ding_active.json")
        )
        fake_api.add(
            "GET",
            "clients_api/dings/987654321/share/play",
            '{"url":"https://api.ring.com/clients_api/dings/987654321/recording"}',
        )
        fake_api.add(
            "GET",
            "groups/v1/locations/mock-location-id/groups",
            load_fixture("ring_groups.json"),
        )
        fake_api.add("PUT", r"clients_api/doorbots/\d+", "")
        yield mock


def api_requests(mock, method, path):
    pattern = api(path)
    return [
        call
        for call in mock.api.calls
        if call.method == method and pattern.match(call.url)
    ]


@pytest.mark.asyncio
async def test_login(mocker, mock_ring_requests):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice", "FHEMPYTYPE": "ring"}
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import ring

    fhempy_device = ring(logging.getLogger(__name__))

    await fhempy_device.Define(
        testhash,
        [
            "testdevice",
            "fhempy",
            "ring",
            "test@test.com",
            "Front Door",
        ],
        {},
    )
    await wait_for_state("testdevice", "please set password")

    await fhempy_device.Set(
        testhash,
        [
            "testdevice",
            "password",
            "asdfasdfasdf",
        ],
        {},
    )

    count = 0
    while True:
        if (
            "state" in mock_fhem.readings["testdevice"]
            and mock_fhem.readings["testdevice"]["state"] == "connected"
        ):
            break
        if count > 10:
            break
        count += 1
        await asyncio.sleep(0.1)

    assert mock_fhem.readings["testdevice"]["state"] == "connected"
    assert fhempy_device._http_session.headers["Accept"] == "application/json"
    assert mock_fhem.readings["testdevice"]["address"] == "123 Main St"
    assert mock_fhem.readings["testdevice"]["family"] == "doorbots"
    assert mock_fhem.readings["testdevice"]["device_id"] == "aacdef123"
    assert mock_fhem.readings["testdevice"]["id"] == 987652
    assert mock_fhem.readings["testdevice"]["model"] == "Doorbell Pro"
    assert mock_fhem.readings["testdevice"]["firmware"] == "1.4.26"
    assert mock_fhem.readings["testdevice"]["latitude"] == 12.0
    assert mock_fhem.readings["testdevice"]["longitude"] == -70.12345
    assert mock_fhem.readings["testdevice"]["kind"] == "lpd_v1"
    assert mock_fhem.readings["testdevice"]["name"] == "Front Door"
    assert mock_fhem.readings["testdevice"]["timezone"] == "America/New_York"
    assert mock_fhem.readings["testdevice"]["wifi_name"] == "ring_mock_wifi"
    assert mock_fhem.readings["testdevice"]["wifi_signal_strength"] == -58
    assert mock_fhem.readings["testdevice"]["wifi_signal_category"] == "good"
    assert mock_fhem.readings["testdevice"]["battery_life"] == 100
    assert mock_fhem.readings["testdevice"]["existing_doorbell_type"] == "Mechanical"
    assert mock_fhem.readings["testdevice"]["existing_doorbell_type_enabled"] == True
    assert mock_fhem.readings["testdevice"]["existing_doorbell_type_duration"] == None
    assert mock_fhem.readings["testdevice"]["subscribed"] == True
    assert mock_fhem.readings["testdevice"]["subscribed_motion"] == True
    assert mock_fhem.readings["testdevice"]["has_subscription"] == True
    assert mock_fhem.readings["testdevice"]["volume"] == 1
    assert mock_fhem.readings["testdevice"]["connection_status"] == "online"
    assert mock_fhem.readings["testdevice"]["last_recording_id"] == 987654321
    assert (
        mock_fhem.readings["testdevice"]["last_recording_url"]
        == "https://api.ring.com/clients_api/dings/987654321/recording"
    )
    assert mock_fhem.readings["testdevice"]["history_1_id"] == 987654321
    assert mock_fhem.readings["testdevice"]["history_1_kind"] == "motion"
    assert mock_fhem.readings["testdevice"]["history_1_answered"] == False
    assert mock_fhem.readings["testdevice"][
        "history_1_created_at"
    ] == datetime.datetime(2017, 3, 5, 15, 3, 40, tzinfo=datetime.timezone.utc)

    await fhempy_device.Undefine(testhash)

    token_form, token_headers = mock_ring_requests.fake_oauth.token_requests[0]
    assert token_form["grant_type"] == ["authorization_code"]
    assert token_headers["User-Agent"] == "android:com.ringapp"
    assert "hardware_id" in token_headers
    session_requests = api_requests(mock_ring_requests, "POST", "clients_api/session")
    assert len(session_requests) == 1
    headers = session_requests[0].kwargs["headers"]
    assert headers["User-Agent"] == "android:com.ringapp"
    assert headers["hardware_id"] == token_headers["hardware_id"]
    assert headers["Authorization"].startswith("Bearer ")
    # push events instead of polling dings
    assert mock_fhem.readings["testdevice"]["events"] == "push"
    assert api_requests(mock_ring_requests, "GET", "clients_api/dings/active") == [
        api_requests(mock_ring_requests, "GET", "clients_api/dings/active")[0]
    ]
    assert FakeListener.instances[0].stopped
    assert "fcm_credentials" in mock_fhem.readings["testdevice"]
    # identifier is stored, so the hardware id stays the same after restart
    assert len(mock_fhem.readings["testdevice"]["identifier"]) == 20


async def wait_for_state(name, expected):
    for _ in range(50):
        if mock_fhem.readings.get(name, {}).get("state") == expected:
            return
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_login_2fa(mocker, mock_ring_requests):
    mock_fhem.mock_module(mocker)
    mock_ring_requests.fake_oauth.require_2fa = True
    testhash = {"NAME": "testdevice2fa", "FHEMPYTYPE": "ring"}
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import ring

    fhempy_device = ring(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["testdevice2fa", "fhempy", "ring", "test@test.com", "Front Door", "abc"],
        {},
    )
    await fhempy_device.Set(testhash, ["testdevice2fa", "password", "asdfasdfasdf"], {})
    await wait_for_state("testdevice2fa", "please set 2fa_code")
    assert mock_fhem.readings["testdevice2fa"]["state"] == "please set 2fa_code"

    await fhempy_device.Set(testhash, ["testdevice2fa", "2fa_code", "000000"], {})
    await wait_for_state("testdevice2fa", "invalid 2fa_code, please set 2fa_code again")
    assert (
        mock_fhem.readings["testdevice2fa"]["state"]
        == "invalid 2fa_code, please set 2fa_code again"
    )

    await fhempy_device.Set(
        testhash,
        ["testdevice2fa", "2fa_code", FakeRingOAuth.TWO_FA_CODE],
        {},
    )
    await wait_for_state("testdevice2fa", "connected")
    assert mock_fhem.readings["testdevice2fa"]["state"] == "connected"
    assert "token" in mock_fhem.readings["testdevice2fa"]
    await fhempy_device.Undefine(testhash)


@pytest.mark.asyncio
async def test_login_wrong_password(mocker, mock_ring_requests):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevicepw", "FHEMPYTYPE": "ring"}
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import ring

    fhempy_device = ring(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["testdevicepw", "fhempy", "ring", "test@test.com", "Front Door", "abc"],
        {},
    )
    await fhempy_device.Set(testhash, ["testdevicepw", "password", "wrong"], {})
    await wait_for_state("testdevicepw", "AccessDenied: wrong username or password")
    assert (
        mock_fhem.readings["testdevicepw"]["state"]
        == "AccessDenied: wrong username or password"
    )
    await fhempy_device.Undefine(testhash)


async def define_connected(mocker, name, connected_state="connected"):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": name, "FHEMPYTYPE": "ring"}
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import ring

    fhempy_device = ring(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        [name, "fhempy", "ring", "test@test.com", "Front Door", "abc"],
        {},
    )
    await wait_for_state(name, "please set password")
    await fhempy_device.Set(testhash, [name, "password", "asdfasdfasdf"], {})
    await wait_for_state(name, connected_state)
    assert mock_fhem.readings[name]["state"] == connected_state
    return fhempy_device, testhash


@pytest.mark.asyncio
async def test_push_event(mocker, mock_ring_requests):
    """A push event for the device updates the alert readings."""
    from ring_doorbell import RingEvent

    fhempy_device, testhash = await define_connected(mocker, "testdevicepush")
    listener = FakeListener.instances[-1]
    event = RingEvent(
        id=555,
        doorbot_id=987652,
        device_name="Front Door",
        device_kind="lpd_v1",
        now=time.time(),
        expires_in=180,
        kind="ding",
        state="ringing",
    )
    # events of other devices are ignored
    listener.push(
        RingEvent(
            id=556,
            doorbot_id=1,
            device_name="Other",
            device_kind="lpd_v1",
            now=time.time(),
            expires_in=180,
            kind="motion",
            state="human",
        )
    )
    listener.push(event)
    await wait_for_state("testdevicepush", "ding")
    readings = mock_fhem.readings["testdevicepush"]
    assert readings["state"] == "ding"
    assert readings["alert_id"] == 555
    assert readings["alert_kind"] == "ding"
    assert readings["alert_state"] == "ringing"
    assert "alert_sip_to" not in readings
    assert len(api_requests(mock_ring_requests, "POST", "clients_api/session")) == 1
    await fhempy_device.Undefine(testhash)


@pytest.mark.asyncio
async def test_polling_fallback(mocker, mock_ring_requests):
    """Without push events, dings are polled; no new session on each ding."""
    FakeListener.start_result = False
    ding = {
        "id": 777,
        "id_str": "777",
        "state": "ringing",
        "doorbot_id": 987652,
        "doorbot_description": "Front Door",
        "device_kind": "lpd_v1",
        "motion": False,
        "kind": "ding",
        "expires_in": 180,
        "now": time.time(),
    }
    mock_ring_requests.api.add("GET", "clients_api/dings/active", json.dumps([ding]))
    fhempy_device, testhash = await define_connected(
        mocker, "testdevicepoll", connected_state="ding"
    )
    readings = mock_fhem.readings["testdevicepoll"]
    assert readings["events"] == "polling"
    assert readings["state"] == "ding"
    assert readings["alert_id"] == 777
    assert len(api_requests(mock_ring_requests, "POST", "clients_api/session")) == 1
    await fhempy_device.Undefine(testhash)


@pytest.mark.asyncio
async def test_token_refresh_headers(mock_ring_requests):
    """Token refresh sends the headers of the Ring app."""
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import RingAuth

    fake_api = mock_ring_requests.api
    fake_api.routes.insert(
        0,
        (
            "POST",
            re.compile(r"^https://oauth\.ring\.com/oauth/token$"),
            200,
            load_fixture("ring_oauth.json"),
        ),
    )
    updated = []
    token = json.loads(load_fixture("ring_oauth.json"))
    token["expires_at"] = time.time() - 10
    auth = RingAuth(
        "android:com.ringapp",
        token,
        updated.append,
        "hw-id",
        http_client_session=fake_api.session(),
    )
    await auth.async_query("https://api.ring.com/clients_api/ring_devices")
    refresh = [c for c in fake_api.calls if "oauth.ring.com" in c.url]
    assert len(refresh) == 1
    headers = refresh[0].kwargs["headers"]
    assert headers["User-Agent"] == "android:com.ringapp"
    assert headers["hardware_id"] == "hw-id"
    assert headers["Accept"] == "application/json"
    assert updated and updated[0]["access_token"]


@pytest.mark.asyncio
async def test_device_not_found(mocker, mock_ring_requests):
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevicenf", "FHEMPYTYPE": "ring"}
    await check_and_install_dependencies("ring")
    from fhempy.lib.ring.ring import ring

    fhempy_device = ring(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["testdevicenf", "fhempy", "ring", "test@test.com", "Unknown Door", "abc"],
        {},
    )
    await wait_for_state("testdevicenf", "please set password")
    await fhempy_device.Set(testhash, ["testdevicenf", "password", "asdfasdfasdf"], {})
    await wait_for_state("testdevicenf", "device not found")
    assert mock_fhem.readings["testdevicenf"]["state"] == "device not found"
    assert fhempy_device._http_session is None
    await fhempy_device.Undefine(testhash)
