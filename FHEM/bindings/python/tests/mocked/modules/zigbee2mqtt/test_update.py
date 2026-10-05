import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def create_device(mocker, tmp_path, stop_result=True):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("zigbee2mqtt")
    from fhempy.lib.zigbee2mqtt import zigbee2mqtt as z2m_module

    mock_fhem.readings.pop("testz2m", None)
    device = z2m_module.zigbee2mqtt(logging.getLogger(__name__))
    device.hash = {"NAME": "testz2m", "FHEMPYTYPE": "zigbee2mqtt"}
    (tmp_path / ".fhempy/zigbee2mqtt/data").mkdir(parents=True)
    (tmp_path / ".fhempy/zigbee2mqtt/data/configuration.yaml").write_text("a: 1\n")

    calls = []

    async def stop(proc, sig, timeout):
        calls.append("stop")
        return stop_result

    async def wait():
        calls.append("wait")

    async def start_process():
        calls.append("start")

    device.proc = mocker.Mock()
    mocker.patch.object(z2m_module.child_process, "stop", stop)
    mocker.patch.object(device, "start_process", start_process)
    mocker.patch.object(device, "_wait_for_port_release", wait)
    repo = mocker.patch.object(z2m_module, "Repo")
    mocker.patch.object(z2m_module.subprocess, "call")
    return device, calls, repo


@pytest.mark.asyncio
async def test_update_waits_for_port_before_start(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)

    await device.update_z2m()

    assert calls == ["stop", "wait", "start"]
    repo.return_value.remotes.origin.pull.assert_called_once()
    assert mock_fhem.readings["testz2m"]["update"] == "successful"


@pytest.mark.asyncio
async def test_update_aborts_if_zigbee2mqtt_does_not_stop(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path, stop_result=False)

    await device.update_z2m()

    # a second instance would fail with "Cannot lock port"
    assert calls == ["stop"]
    repo.assert_not_called()
    assert "did not stop" in mock_fhem.readings["testz2m"]["update"]


@pytest.mark.asyncio
async def test_failed_update_starts_zigbee2mqtt_again(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    repo.return_value.remotes.origin.pull.side_effect = Exception("no network")

    await device.update_z2m()

    assert calls == ["stop", "wait", "start"]
    assert mock_fhem.readings["testz2m"]["update"] == "failed to update, check log"


@pytest.mark.asyncio
async def test_restart_does_not_start_second_instance(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, _ = await create_device(mocker, tmp_path, stop_result=False)

    await device._restart()

    assert calls == ["stop"]
