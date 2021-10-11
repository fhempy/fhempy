import asyncio
import logging
import os

import pytest
from fhempy.lib.pkg_installer import check_and_install_dependencies
from tests.utils import mock_fhem


@pytest.mark.asyncio
async def test_everything(mocker):
    # prepare
    mock_fhem.mock_module(mocker)
    testhash = {"NAME": "testdevice"}
    await check_and_install_dependencies("googlecast")
    from fhempy.lib.googlecast.googlecast import googlecast

    fhempy_device = googlecast(logging.getLogger(__name__))
    await fhempy_device.Define(
        testhash,
        ["testdevice", "fhempy", "googlecast", os.environ["CAST_DEVICE_NAME"]],
        {},
    )
    assert mock_fhem.readings["testdevice"]["state"] == "offline"

    while fhempy_device.cast is None:
        await asyncio.sleep(1)

    # quitApp
    await fhempy_device.Set(
        testhash,
        ["testdevice", "quitApp"],
        {},
    )
    await asyncio.sleep(10)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Backdrop"

    # check if readings are there
    assert "state" in mock_fhem.readings["testdevice"]

    # set spotify attributes
    await fhempy_device.Attr(
        testhash, ["set", "testdevice", "spotify_sp_dc", os.environ["SP_DC"]], {}
    )
    await fhempy_device.Attr(
        testhash, ["set", "testdevice", "spotify_sp_key", os.environ["SP_KEY"]], {}
    )
    await asyncio.sleep(10)
    assert (
        mock_fhem.readings["testdevice"]["spotify_user"]
        != "attr spotify_sp... required"
    )

    # play spotify
    await fhempy_device.Set(
        testhash,
        [
            "testdevice",
            "play",
            "https://open.spotify.com/artist/4PBCFEjR4a3OGdOZ6jeKKM",
        ],
        {},
    )
    await asyncio.sleep(40)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Spotify"

    # quitApp
    await fhempy_device.Set(
        testhash,
        ["testdevice", "quitApp"],
        {},
    )
    await asyncio.sleep(10)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Backdrop"

    # display website
    await fhempy_device.Set(testhash, ["testdevice", "displayWebsite"], {})
    await asyncio.sleep(15)
    assert mock_fhem.readings["testdevice"]["display_name"] == "DashCast"
    assert mock_fhem.readings["testdevice"]["status_text"] == "Home of FHEM"

    # play youtube
    await fhempy_device.Set(
        testhash,
        ["testdevice", "play", "https://www.youtube.com/watch?v=fCZVL_8D048"],
        {},
    )
    await asyncio.sleep(30)
    assert mock_fhem.readings["testdevice"]["display_name"] == "YouTube"
    assert mock_fhem.readings["testdevice"]["mediaPlayerState"] == "PLAYING"

    # check if position is updated
    await asyncio.sleep(45)
    assert mock_fhem.readings["testdevice"]["mediaCurrentPosition"] >= 30

    # pause
    await fhempy_device.Set(
        testhash,
        ["testdevice", "pause"],
        {},
    )
    await asyncio.sleep(5)
    assert mock_fhem.readings["testdevice"]["mediaPlayerState"] == "PAUSED"

    # play
    await fhempy_device.Set(
        testhash,
        ["testdevice", "play"],
        {},
    )
    await asyncio.sleep(5)
    assert mock_fhem.readings["testdevice"]["mediaPlayerState"] == "PLAYING"

    # quitApp
    await fhempy_device.Set(
        testhash,
        ["testdevice", "quitApp"],
        {},
    )
    await asyncio.sleep(10)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Backdrop"

    # play servustv stream
    await fhempy_device.Set(
        testhash,
        [
            "testdevice",
            "play",
            "https://rbmn-live.akamaized.net/hls/live/2002830/geoSTVDEweb/master_6692.m3u8",
        ],
        {},
    )
    await asyncio.sleep(20)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Default Media Receiver"
    assert mock_fhem.readings["testdevice"]["mediaPlayerState"] == "PLAYING"

    # volume
    await fhempy_device.Set(
        testhash,
        [
            "testdevice",
            "volume",
            "30",
        ],
        {},
    )
    await asyncio.sleep(2)
    assert mock_fhem.readings["testdevice"]["volume"] == 30

    # volume
    await fhempy_device.Set(
        testhash,
        [
            "testdevice",
            "volume",
            "20",
        ],
        {},
    )
    await asyncio.sleep(2)
    assert mock_fhem.readings["testdevice"]["volume"] == 20

    # quitApp
    await fhempy_device.Set(
        testhash,
        ["testdevice", "quitApp"],
        {},
    )
    await asyncio.sleep(10)
    assert mock_fhem.readings["testdevice"]["display_name"] == "Backdrop"
