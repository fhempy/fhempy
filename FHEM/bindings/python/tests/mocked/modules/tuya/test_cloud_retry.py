import asyncio
import logging

import pytest
from fhempy.lib.pkg_installer import check_and_install_dependencies
from tests.utils import mock_fhem

NAME = "tuya_local"


async def create_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("tuya")
    from fhempy.lib.tuya import tuya as tuya_module

    mock_fhem.readings.pop(NAME, None)
    device = tuya_module.tuya(logging.getLogger(__name__))
    device.hash = {"NAME": NAME, "FHEMPYTYPE": "tuya"}
    device.tt_region = "eu"
    device.tt_key = "key"
    device.tt_secret = "secret"
    device.tt_did = "123"
    sleeps = []

    async def no_sleep(delay):
        sleeps.append(delay)

    mocker.patch.object(tuya_module.asyncio, "sleep", no_sleep)
    return tuya_module, device, sleeps


class FakeCloud:
    def __init__(self, token="token", error=None):
        self.token = token
        self.error = error


@pytest.mark.asyncio
async def test_cloud_login_is_retried_on_connection_reset(mocker):
    import requests

    tuya_module, device, sleeps = await create_device(mocker)
    results = [
        requests.exceptions.ConnectionError(
            ("Connection aborted.", ConnectionResetError(104, "reset by peer"))
        ),
        requests.exceptions.ConnectionError("Name or service not known"),
    ]
    cloud = FakeCloud()

    def fake_cloud(*args):
        if results:
            raise results.pop(0)
        return cloud

    mocker.patch.object(tuya_module.tt, "Cloud", fake_cloud)

    await device.setup_cloud()

    assert device.tuya_cloud is cloud
    # backoff: about 10s, then about 20s
    assert len(sleeps) == 2
    assert 9 <= sleeps[0] <= 11
    assert 18 <= sleeps[1] <= 22


@pytest.mark.asyncio
async def test_wrong_credentials_are_not_retried(mocker):
    tuya_module, device, sleeps = await create_device(mocker)
    mocker.patch.object(
        tuya_module.tt,
        "Cloud",
        lambda *args: FakeCloud(token=None, error="sign invalid"),
    )

    with pytest.raises(tuya_module.TuyaCloudError, match="sign invalid"):
        await device.setup_cloud()
    assert sleeps == []
    assert device.tuya_cloud is None


@pytest.mark.asyncio
async def test_define_does_not_fail_when_cloud_is_unreachable(mocker):
    import requests

    tuya_module, device, sleeps = await create_device(mocker)
    calls = []

    def unreachable(*args):
        calls.append(args)
        raise requests.exceptions.ConnectionError("reset by peer")

    mocker.patch.object(tuya_module.tt, "Cloud", unreachable)
    stop = asyncio.Event()

    async def stop_after_two(delay):
        sleeps.append(delay)
        if len(sleeps) >= 2:
            stop.set()
            await asyncio.Event().wait()

    mocker.patch.object(tuya_module.asyncio, "sleep", stop_after_two)
    testhash = {"NAME": NAME, "FHEMPYTYPE": "tuya"}

    ret = await device.Define(
        testhash,
        [
            NAME,
            "fhempy",
            "tuya",
            "productid",
            "123",
            "192.168.1.2",
            "0123456789abcdef",
            "3.3",
            "key",
            "secret",
        ],
        {},
    )

    # Define returns right away, the cloud login is retried in the background
    assert ret is None
    await asyncio.wait_for(stop.wait(), 5)
    assert len(calls) == 2
    assert mock_fhem.readings[NAME]["state"].startswith(
        "cloud connection failed, retry in"
    )
    await device.Undefine(testhash)
