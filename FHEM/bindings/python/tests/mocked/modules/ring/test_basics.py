import asyncio
import datetime
import logging
import os
import re
from urllib.parse import parse_qs

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


@pytest.fixture(autouse=True)
def mock_ring_requests():
    with requests_mock.Mocker() as mock:
        mock.fake_oauth = FakeRingOAuth(mock)
        mock.post(
            "https://api.ring.com/clients_api/session",
            text=load_fixture("ring_session.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/ring_devices",
            text=load_fixture("ring_devices.json"),
        )
        mock.get(
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/chimes\/\d+\/health"),
            text=load_fixture("ring_chime_health_attrs.json"),
        )
        mock.get(
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/doorbots\/\d+\/health"),
            text=load_fixture("ring_doorboot_health_attrs.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/doorbots/987652/history",
            text=load_fixture("ring_doorbots.json"),
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/active",
            text=load_fixture("ring_ding_active.json"),
        )
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/floodlight_light_off",
            text="ok",
        )
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/floodlight_light_on",
            text="ok",
        )
        mock.put("https://api.ring.com/clients_api/doorbots/987652/siren_on", text="ok")
        mock.put(
            "https://api.ring.com/clients_api/doorbots/987652/siren_off", text="ok"
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/987654321/share/play",
            text='{"url":"https://api.ring.com/clients_api/dings/987654321/recording"}',
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/987654321/recording",
            text="ok",
        )
        mock.get(
            "https://api.ring.com/groups/v1/locations/mock-location-id/groups",
            text=load_fixture("ring_groups.json"),
        )
        mock.post(
            "https://api.ring.com/groups/v1/locations/"
            + "mock-location-id/groups/mock-group-id/devices",
            text="ok",
        )
        mock.patch(
            re.compile(
                r"https:\/\/api\.ring\.com\/devices\/v1\/devices\/\d+\/settings"
            ),
            text="ok",
        )
        mock.get(
            re.compile(r"https:\/\/api\.ring\.com\/clients_api\/dings\/\d+\/recording"),
            # "https://api.ring.com/clients_api/dings/987654321/recording",
            status_code=200,
            content=b"123456",
        )
        mock.get(
            "https://api.ring.com/clients_api/dings/9876543212/recording",
            status_code=200,
            content=b"123456",
        )
        mock.patch(
            "https://api.ring.com/clients_api/device",
            status_code=204,
            content=b"",
        )
        yield mock


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

    # wait for the ding
    await asyncio.sleep(1)
    assert mock_fhem.readings["testdevice"]["state"] == "connected"
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
