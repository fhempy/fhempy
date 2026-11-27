import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

NAME = "testtuyacloud"


async def create_setup(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("tuya_cloud")
    from fhempy.lib.tuya_cloud import tuya_cloud_setup

    mock_fhem.readings.pop(NAME, None)
    fhemdev = mocker.MagicMock()
    fhemdev.hash = {"NAME": NAME, "FHEMPYTYPE": "tuya_cloud"}
    setup = tuya_cloud_setup.tuya_cloud_setup(logging.getLogger(__name__), fhemdev)
    sleeps = []

    async def no_sleep(delay):
        sleeps.append(delay)

    mocker.patch.object(tuya_cloud_setup.asyncio, "sleep", no_sleep)
    mocker.patch.object(setup, "_init_devices", mocker.AsyncMock())
    return setup, sleeps


@pytest.mark.asyncio
async def test_setup_retries_without_internet(mocker):
    import requests

    setup, sleeps = await create_setup(mocker)
    pulsar = mocker.MagicMock()

    async def offline():
        # a client of the failed attempt has to be stopped before the retry
        setup.tuya_pulsar = pulsar
        raise requests.exceptions.ConnectionError("Name or service not known")

    attempts = [offline, offline]

    async def init_sdk():
        if attempts:
            return await attempts.pop(0)()
        return True

    mocker.patch.object(setup, "_init_tuya_sdk", init_sdk)

    await setup.run_setup()

    assert len(sleeps) == 2
    # backoff: about 10s, then about 20s
    assert 9 <= sleeps[0] <= 11
    assert 18 <= sleeps[1] <= 22
    assert pulsar.stop.call_count == 2
    assert setup.ready is True
    assert mock_fhem.readings[NAME]["state"] == "connected"
    setup._init_devices.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_login_is_not_retried(mocker):
    setup, sleeps = await create_setup(mocker)
    mocker.patch.object(setup, "_init_tuya_sdk", mocker.AsyncMock(return_value=False))

    await setup.run_setup()

    assert sleeps == []
    assert setup.ready is False
    setup._init_devices.assert_not_awaited()
