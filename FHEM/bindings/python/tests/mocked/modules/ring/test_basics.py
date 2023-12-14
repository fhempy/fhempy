import asyncio
import datetime
import logging
import os
import re

import pytest
import requests_mock
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path) as fdp:
        return fdp.read()


@pytest.fixture(autouse=True)
def mock_ring_requests():
    with requests_mock.Mocker() as mock:
        mock.post(
            "https://oauth.ring.com/oauth/token", text=load_fixture("ring_oauth.json")
        )
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
async def test_login(mocker):
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
