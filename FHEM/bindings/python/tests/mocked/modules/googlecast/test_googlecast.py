import asyncio
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def create_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("googlecast")
    from fhempy.lib.googlecast import googlecast as googlecast_module

    device = googlecast_module.googlecast(logging.getLogger(__name__))
    device.hash = {"NAME": "testcast", "FHEMPYTYPE": "googlecast"}
    device._set_conf = {"authcode": {"args": ["code"]}, "pause": {}}
    await device.set_set_config(device._set_conf)
    return device


@pytest.mark.asyncio
async def test_set_without_cast_returns_error(mocker):
    device = await create_device(mocker)
    hash = {"NAME": "testcast", "CASTNAME": "Wohnzimmer"}

    ret = await device.Set(hash, ["testcast", "pause"], {})
    assert "Wohnzimmer not found yet" in ret

    # set list and unknown commands still work without cast
    assert (await device.Set(hash, ["testcast", "?"], {})).startswith("Unknown")
    device.handle_authcode = mocker.AsyncMock()
    device.create_async_task = mocker.MagicMock()
    await device.Set(hash, ["testcast", "authcode", "abc"], {})
    device.handle_authcode.assert_called_once_with("abc")


@pytest.mark.asyncio
async def test_set_not_connected_returns_error(mocker):
    from pychromecast.error import NotConnected

    device = await create_device(mocker)
    device.cast = mocker.MagicMock()
    device.cast.media_controller.pause.side_effect = NotConnected("gone")
    hash = {"NAME": "testcast", "CASTNAME": "Wohnzimmer"}

    ret = await device.Set(hash, ["testcast", "pause"], {})
    assert "Wohnzimmer not connected" in ret


@pytest.mark.asyncio
async def test_failing_reading_update_does_not_block_listener(mocker):
    device = await create_device(mocker)
    status = mocker.MagicMock(status="LOST")
    device.updateConnectionReadings = mocker.AsyncMock(side_effect=Exception("x"))

    # listener runs in pychromecast thread, must survive a failing update and
    # must not keep the lock (a second event would hang the socket thread)
    await asyncio.to_thread(device.new_connection_status, status)
    status.status = "FAILED"
    await asyncio.wait_for(asyncio.to_thread(device.new_connection_status, status), 5)
    assert device.updateConnectionReadings.await_count == 2


@pytest.mark.asyncio
async def test_set_before_define_finished(mocker):
    # FHEM can send a Set while Define still waits for FHEM
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("googlecast")
    from fhempy.lib.googlecast import googlecast as googlecast_module

    device = googlecast_module.googlecast(logging.getLogger(__name__))
    hash = {"NAME": "testcast", "CASTNAME": "Living Room"}

    ret = await device.Set(hash, ["testcast", "pause"], {})
    assert "Living Room not found yet" in ret


@pytest.mark.asyncio
async def test_alarm_plays_sound_with_display_metadata(mocker):
    device = await create_device(mocker)
    device._set_conf = googlecast_conf(device)
    await device.set_set_config(device._set_conf)
    device.cast = mocker.MagicMock()
    device.cast.status.volume_level = 0.3
    device.start_tts_server = mocker.AsyncMock(return_value="http://192.0.2.1:8080")
    device.tts_server = mocker.MagicMock()
    device.tts_server.add.return_value = "/tts/abc.wav"
    tasks = []
    device.create_async_task = lambda coro: tasks.append(coro)
    hash = {"NAME": "testcast"}

    assert (
        await device.Set(hash, ["testcast", "alarm", "Water in the basement"], {})
        is None
    )
    await tasks.pop(0)
    wav = device.tts_server.add.call_args.args[0]
    assert wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"
    assert device.tts_server.add.call_args.args[1] == ".wav"
    args, kwargs = device.cast.play_media.call_args
    assert args == ("http://192.0.2.1:8080/tts/abc.wav", "audio/wav")
    assert kwargs["metadata"]["title"] == "Water in the basement"
    assert kwargs["metadata"]["subtitle"].startswith("Alarm · ")
    assert kwargs["metadata"]["images"] == [
        {"url": "http://192.0.2.1:8080/static/alarm.png"}
    ]
    # volume untouched without volume parameter
    device.cast.set_volume.assert_not_called()


@pytest.mark.asyncio
async def test_alarm_defaults_volume_and_restore(mocker):
    device = await create_device(mocker)
    device._set_conf = googlecast_conf(device)
    await device.set_set_config(device._set_conf)
    device.cast = mocker.MagicMock()
    device.cast.status.volume_level = 0.3
    device.start_tts_server = mocker.AsyncMock(return_value="http://192.0.2.1:8080")
    device.tts_server = mocker.MagicMock()
    device.tts_server.add.return_value = "/tts/abc.wav"
    tasks = []
    device.create_async_task = lambda coro: tasks.append(coro)
    hash = {"NAME": "testcast"}

    await device.Set(hash, ["testcast", "alarm"], {"volume": "80", "duration": "5"})
    await tasks.pop(0)
    assert device.cast.play_media.call_args.kwargs["metadata"]["title"] == "Alarm"
    device.cast.set_volume.assert_called_once_with(0.8)
    # restore task is scheduled, stop restores the old volume right away
    restore = asyncio.ensure_future(tasks.pop(0))
    device._alarm_volume_task = restore
    await device.Set(hash, ["testcast", "stop"], {})
    assert device.cast.set_volume.call_args.args == (0.3,)
    assert restore.cancelled() or restore.done()

    assert "volume must be" in await device.Set(
        hash, ["testcast", "alarm"], {"volume": "120"}
    )
    assert "duration must be" in await device.Set(
        hash, ["testcast", "alarm"], {"duration": "0"}
    )


def googlecast_conf(device):
    conf = dict(device._set_conf)
    conf.update(type(device)(logging.getLogger(__name__))._set_conf)
    return conf


def test_alarm_wav():
    from fhempy.lib.googlecast import alarm

    wav = alarm.make_wav(10)
    assert wav[:4] == b"RIFF" and wav[8:16] == b"WAVEfmt "
    seconds = (len(wav) - 44) / 2 / alarm.SAMPLE_RATE
    assert abs(seconds - 10) <= alarm.cycle_length()
    # out of range durations are clamped
    assert len(alarm.make_wav(10000)) <= 44 + 2 * alarm.SAMPLE_RATE * (
        alarm.MAX_DURATION + 1
    )
