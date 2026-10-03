import json
import logging
import pathlib

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


async def create_device(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("zigbee2mqtt")
    from fhempy.lib.zigbee2mqtt import zigbee2mqtt as z2m_module

    mock_fhem.readings.pop("testz2m", None)
    device = z2m_module.zigbee2mqtt(logging.getLogger(__name__))
    device.hash = {"NAME": "testz2m", "FHEMPYTYPE": "zigbee2mqtt"}
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    for check in [
        "check_node_installation",
        "check_npm_installation",
        "check_pnpm_installation",
    ]:
        mocker.patch.object(device, check, mocker.AsyncMock(return_value=True))
    started = []

    def start(args, cwd):
        # remember the configuration zigbee2mqtt is started with
        started.append((pathlib.Path(cwd) / "data/configuration.yaml").read_text())
        return mocker.Mock()

    mocker.patch.object(z2m_module.child_process, "start", start)
    return device, started


def write_pending_restore(tmp_path):
    pending = tmp_path / ".fhempy/zigbee2mqtt_restore/data"
    pending.mkdir(parents=True)
    (pending / "configuration.yaml").write_text("restored: true\n")
    (pending / "database.db").write_text("restored database\n")


async def fake_install(tmp_path):
    # what install_z2m does: clone and write a default configuration
    data = tmp_path / ".fhempy/zigbee2mqtt/data"
    data.mkdir(parents=True, exist_ok=True)
    (data.parent / "package.json").write_text(json.dumps({"version": "2.0.0"}))
    (data / "configuration.yaml").write_text("default: true\n")
    return True


@pytest.mark.asyncio
async def test_restored_backup_is_applied_after_install_before_start(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    device, started = await create_device(mocker)

    async def install():
        return await fake_install(tmp_path)

    mocker.patch.object(device, "install_z2m", install)
    write_pending_restore(tmp_path)

    await device.run_z2m()

    data = tmp_path / ".fhempy/zigbee2mqtt/data"
    assert started == ["restored: true\n"]
    assert (data / "configuration.yaml").read_text() == "restored: true\n"
    assert (data / "database.db").read_text() == "restored database\n"
    # consumed, must not be applied again
    assert not (tmp_path / ".fhempy/zigbee2mqtt_restore").exists()
    assert mock_fhem.readings["testz2m"]["restore"].startswith("backup applied")

    # zigbee2mqtt changed its configuration, a restart must keep it
    (data / "configuration.yaml").write_text("changed: true\n")
    await device.start_process()
    assert started[-1] == "changed: true\n"


@pytest.mark.asyncio
async def test_start_without_pending_restore(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, started = await create_device(mocker)
    await fake_install(tmp_path)

    await device.start_process()

    assert started == ["default: true\n"]
    assert "restore" not in mock_fhem.readings["testz2m"]


@pytest.mark.asyncio
async def test_fresh_clone_installs_even_if_restored_reading_says_successful(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    device, _ = await create_device(mocker)
    from fhempy.lib.zigbee2mqtt import zigbee2mqtt as z2m_module

    # fhem.save from the backup contains installation: successful
    mock_fhem.readings["testz2m"] = {"installation": "successful"}

    def clone(url, path):
        (tmp_path / ".fhempy/zigbee2mqtt/data").mkdir(parents=True, exist_ok=True)

    # no git repository yet
    repo = mocker.patch.object(z2m_module, "Repo", side_effect=Exception)
    repo.clone_from = clone
    calls = mocker.patch.object(z2m_module.subprocess, "call")
    mocker.patch.object(device, "create_weblink", mocker.AsyncMock())

    assert await device.install_z2m()

    assert calls.call_count == 2
    data = tmp_path / ".fhempy/zigbee2mqtt/data"
    assert (data / "configuration.yaml").exists()
