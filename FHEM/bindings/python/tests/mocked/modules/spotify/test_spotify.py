import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def create_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("spotify")
    from fhempy.lib.spotify import spotify as spotify_module

    mock_fhem.readings.pop("testspotify", None)
    device = spotify_module.spotify(logging.getLogger(__name__))
    device.hash = {"NAME": "testspotify", "FHEMPYTYPE": "spotify"}
    device.loggedin = True
    device.spotipy = mocker.MagicMock()
    return device


@pytest.mark.asyncio
async def test_connection_error_logged_once(mocker, caplog):
    import requests

    device = await create_device(mocker)
    device.spotipy.current_playback.side_effect = requests.exceptions.ConnectionError(
        "Connection aborted."
    )

    with caplog.at_level(logging.DEBUG):
        for _ in range(3):
            await device.update_playback()

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "not reachable" in warnings[0].getMessage()
    # no traceback for a plain connection problem
    assert all(r.exc_info is None for r in caplog.records)
    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]

    caplog.clear()
    device.spotipy.current_playback.side_effect = None
    device.spotipy.current_playback.return_value = {"is_playing": False}
    with caplog.at_level(logging.INFO):
        await device.update_playback()
    assert "reachable again" in caplog.text
    assert mock_fhem.readings["testspotify"]["current_is_playing"] is False


@pytest.mark.asyncio
async def test_server_error_logged_once(mocker, caplog):
    import spotipy

    device = await create_device(mocker)
    device.spotipy.devices.side_effect = spotipy.SpotifyException(
        502, -1, "Bad Gateway"
    )

    with caplog.at_level(logging.WARNING):
        for _ in range(3):
            try:
                await device.update_devices()
            except Exception as exc:
                device._log_update_error("devices", exc)

    assert len(caplog.records) == 1


@pytest.mark.asyncio
async def test_unexpected_error_keeps_traceback(mocker, caplog):
    device = await create_device(mocker)
    device.spotipy.current_playback.side_effect = KeyError("x")

    with caplog.at_level(logging.ERROR):
        await device.update_playback()

    assert len(caplog.records) == 1
    assert caplog.records[0].exc_info is not None


@pytest.mark.asyncio
async def test_command_error_sets_reading(mocker, caplog):
    import spotipy

    device = await create_device(mocker)
    device._attr_default_device = None
    device.spotipy.start_playback.side_effect = spotipy.SpotifyException(
        404,
        -1,
        "https://api.spotify.com/v1/me/player/play:\n"
        " Player command failed: No active device found",
        reason="NO_ACTIVE_DEVICE",
    )

    with caplog.at_level(logging.WARNING):
        ret = await device.set_command(
            device.hash,
            {"cmd": "play", "uri": "spotify:playlist:abc", "deviceid": None},
        )

    expected = "Player command failed: No active device found (NO_ACTIVE_DEVICE)"
    assert ret == "play failed: " + expected
    assert mock_fhem.readings["testspotify"]["last_error"] == "play: " + expected
    # no traceback in the log
    assert all(r.exc_info is None for r in caplog.records)
    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]

    device.spotipy.start_playback.side_effect = None
    ret = await device.set_command(
        device.hash,
        {"cmd": "play", "uri": "spotify:track:xyz", "deviceid": "dev1"},
    )
    assert ret is None
    assert mock_fhem.readings["testspotify"]["last_error"] == "none"
    device.spotipy.start_playback.assert_called_with(
        device_id="dev1", uris=["spotify:track:xyz"]
    )


@pytest.mark.asyncio
async def test_command_uses_default_device(mocker):
    device = await create_device(mocker)
    device._attr_default_device = "default1"

    await device.set_command(
        device.hash,
        {"cmd": "play", "uri": "spotify:album:abc", "deviceid": None},
    )
    device.spotipy.start_playback.assert_called_with(
        device_id="default1", context_uri="spotify:album:abc"
    )

    await device.set_command(device.hash, {"cmd": "volume", "vol": "40"})
    device.spotipy.volume.assert_called_with(40, "default1")
