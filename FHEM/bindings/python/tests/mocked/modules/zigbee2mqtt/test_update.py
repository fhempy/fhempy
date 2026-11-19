import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


def z2m_module():
    from fhempy.lib.zigbee2mqtt import zigbee2mqtt

    return zigbee2mqtt


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
    mocker.patch.object(device, "_get_shell_env", mocker.AsyncMock(return_value={}))
    commands = []

    def run(args, cwd, **kwargs):
        commands.append(args[-1])
        assert kwargs["env"]["CI"] == "true"
        return mocker.Mock(returncode=0, stdout=b"done\n")

    run_mock = mocker.patch.object(z2m_module.subprocess, "run", side_effect=run)
    device.commands = commands
    device.run_mock = run_mock
    return device, calls, repo


def z2m_dir(tmp_path):
    return tmp_path / ".fhempy/zigbee2mqtt"


@pytest.mark.asyncio
async def test_update_waits_for_port_before_start(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)

    await device.update_z2m()

    assert calls == ["stop", "wait", "start"]
    repo.return_value.remotes.origin.pull.assert_called_once()
    assert mock_fhem.readings["testz2m"]["update"] == "successful"


@pytest.mark.asyncio
async def test_update_reinstalls_node_modules_and_builds(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    (z2m_dir(tmp_path) / "node_modules").mkdir()
    (z2m_dir(tmp_path) / "pnpm-lock.yaml").write_text("lock: 1\n")

    await device.update_z2m()

    assert device.commands == [
        z2m_module().PNPM_INSTALL,
        z2m_module().PNPM_BUILD,
    ]
    assert z2m_module().dependencies_up_to_date(str(z2m_dir(tmp_path)))
    assert mock_fhem.readings["testz2m"]["update"] == "successful"


@pytest.mark.asyncio
async def test_failed_pnpm_install_retries_with_fresh_node_modules(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    node_modules = z2m_dir(tmp_path) / "node_modules"
    node_modules.mkdir()
    (node_modules / "old").write_text("x")
    results = iter([1, 0, 0])

    def run(args, cwd, **kwargs):
        device.commands.append(args[-1])
        return mocker.Mock(returncode=next(results), stdout=b"ERR_PNPM\n")

    device.run_mock.side_effect = run

    await device.update_z2m()

    install = z2m_module().PNPM_INSTALL
    assert device.commands == [install, install, z2m_module().PNPM_BUILD]
    assert not (node_modules / "old").exists()
    assert mock_fhem.readings["testz2m"]["update"] == "successful"


@pytest.mark.asyncio
async def test_failed_build_is_reported(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    (z2m_dir(tmp_path) / "node_modules").mkdir()

    def run(args, cwd, **kwargs):
        device.commands.append(args[-1])
        failed = args[-1] == z2m_module().PNPM_BUILD
        return mocker.Mock(returncode=2 if failed else 0, stdout=b"tsc error\n")

    device.run_mock.side_effect = run

    await device.update_z2m()

    assert calls == ["stop", "wait", "start"]
    assert mock_fhem.readings["testz2m"]["update"] == "failed to update, check log"
    # the next start installs again
    assert not z2m_module().dependencies_up_to_date(str(z2m_dir(tmp_path)))


@pytest.mark.asyncio
async def test_pull_blocked_by_local_changes_resets_to_remote(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    (z2m_dir(tmp_path) / "node_modules").mkdir()
    rep = repo.return_value
    rep.remotes.origin.pull.side_effect = Exception("local changes")

    await device.update_z2m()

    rep.remotes.origin.fetch.assert_called_once()
    rep.git.reset.assert_called_once_with("--hard", "@{u}")
    assert mock_fhem.readings["testz2m"]["update"] == "successful"


@pytest.mark.asyncio
async def test_start_reinstalls_outdated_node_modules(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, repo = await create_device(mocker, tmp_path)
    mocker.patch.object(device, "create_weblink", mocker.AsyncMock())
    directory = z2m_dir(tmp_path)
    (directory / "node_modules").mkdir()
    (directory / "pnpm-lock.yaml").write_text("lock: 1\n")
    z2m_module().write_install_marker(str(directory))
    mock_fhem.readings["testz2m"] = {"installation": "successful"}

    # node_modules fits the checkout: nothing to do
    assert await device.install_z2m()
    assert device.commands == []

    # checkout changed without installing (e.g. interrupted update)
    (directory / "pnpm-lock.yaml").write_text("lock: 2\n")
    assert await device.install_z2m()
    assert device.commands == [
        z2m_module().PNPM_INSTALL,
        z2m_module().PNPM_BUILD,
    ]


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
    repo.return_value.remotes.origin.fetch.side_effect = Exception("no network")

    await device.update_z2m()

    assert calls == ["stop", "wait", "start"]
    assert mock_fhem.readings["testz2m"]["update"] == "failed to update, check log"


@pytest.mark.asyncio
async def test_restart_does_not_start_second_instance(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    device, calls, _ = await create_device(mocker, tmp_path, stop_result=False)

    await device._restart()

    assert calls == ["stop"]
