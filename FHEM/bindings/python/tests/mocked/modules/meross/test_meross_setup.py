import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

NAME = "testmeross"


async def create_setup(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("meross")
    from fhempy.lib.meross import meross_setup

    mock_fhem.readings.pop(NAME, None)
    fhemdev = mocker.MagicMock()
    fhemdev.hash = {"NAME": NAME, "FHEMPYTYPE": "meross"}
    setup = meross_setup.meross_setup(logging.getLogger(__name__), fhemdev)
    setup._username = "user@example.com"
    setup._password = "secret"
    sleeps = []

    async def no_sleep(delay):
        sleeps.append(delay)

    mocker.patch.object(meross_setup.asyncio, "sleep", no_sleep)
    mocker.patch.object(setup, "_init_devices", mocker.AsyncMock())
    return setup, sleeps, meross_setup


@pytest.mark.asyncio
async def test_setup_retries_without_internet(mocker):
    setup, sleeps, module = await create_setup(mocker)
    client = mocker.MagicMock()
    client.async_logout = mocker.AsyncMock()
    mocker.patch.object(
        module.MerossHttpClient,
        "async_from_user_password",
        mocker.AsyncMock(side_effect=[OSError("Network is unreachable"), client]),
    )
    manager = mocker.MagicMock()
    manager.async_init = mocker.AsyncMock()
    manager.async_device_discovery = mocker.AsyncMock()
    manager.find_devices.return_value = [mocker.MagicMock()]
    mocker.patch.object(module, "MerossManager", return_value=manager)

    await setup.run_setup()

    assert len(sleeps) == 1
    assert setup.ready is True
    assert mock_fhem.readings[NAME]["state"] == "connected"
    setup._init_devices.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_attempt_closes_connection(mocker):
    setup, sleeps, module = await create_setup(mocker)
    client = mocker.MagicMock()
    client.async_logout = mocker.AsyncMock()
    mocker.patch.object(
        module.MerossHttpClient,
        "async_from_user_password",
        mocker.AsyncMock(return_value=client),
    )
    broken = mocker.MagicMock()
    broken.async_init = mocker.AsyncMock(side_effect=TimeoutError())
    working = mocker.MagicMock()
    working.async_init = mocker.AsyncMock()
    working.async_device_discovery = mocker.AsyncMock()
    working.find_devices.return_value = [mocker.MagicMock()]
    mocker.patch.object(module, "MerossManager", side_effect=[broken, working])

    await setup.run_setup()

    broken.close.assert_called_once()
    client.async_logout.assert_awaited_once()
    assert setup.ready is True


@pytest.mark.asyncio
async def test_wrong_password_is_not_retried(mocker):
    setup, sleeps, module = await create_setup(mocker)

    class BadLoginException(Exception):
        pass

    mocker.patch.object(
        module.MerossHttpClient,
        "async_from_user_password",
        mocker.AsyncMock(side_effect=BadLoginException("wrong password")),
    )

    await setup.run_setup()

    assert sleeps == []
    assert setup.ready is False
    assert "check username/password" in mock_fhem.readings[NAME]["state"]
