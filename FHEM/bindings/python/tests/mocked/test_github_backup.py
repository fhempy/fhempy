import asyncio
import base64
import hashlib
import json
import logging

import pytest
from aiohttp import web
from tests.utils import mock_fhem

from fhempy.lib.github_backup import github_backup as gb


def test_read_file_for_github_matches_git(tmp_path):
    # not a multiple of the chunk size, so the last chunk gets padding
    data = bytes(range(256)) * 3000 + b"x"
    f = tmp_path / "fhem.cfg"
    f.write_bytes(data)

    content, sha = gb.read_file_for_github(f)

    assert content == base64.b64encode(data)
    blob = f"blob {len(data)}\0".encode() + data
    # git's blob id, not used for security
    assert sha == hashlib.sha1(blob, usedforsecurity=False).hexdigest()  # NOSONAR


def test_json_body_is_valid_json():
    body = gb.json_body({"message": 'a "quoted" msg', "sha": "abc"}, b"Zm9v")
    assert json.loads(body) == {
        "message": 'a "quoted" msg',
        "sha": "abc",
        "content": "Zm9v",
    }
    assert json.loads(gb.json_body({}, b"Zm9v")) == {"content": "Zm9v"}


@pytest.mark.asyncio
async def test_github_put_sends_json_body(tmp_path):
    received = []

    async def handler(request):
        received.append(
            (request.headers.get("Content-Type"), json.loads(await request.read()))
        )
        return web.json_response({})

    app = web.Application(client_max_size=10_000_000)
    app.router.add_put("/contents/fhem.cfg", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    try:
        f = tmp_path / "fhem.cfg"
        f.write_bytes(b"define WEB FHEMWEB 8083 global\n" * 50000)
        module = gb.github_backup(logging.getLogger("github_backup_test"))
        content, sha = await module.b64encode_file(f)

        ok = await module.github_put(
            # local test server without TLS
            f"http://127.0.0.1:{port}/contents/fhem.cfg",  # NOSONAR
            {"message": "backup", "sha": "123"},
            content,
        )
    finally:
        await runner.cleanup()

    assert ok
    content_type, data = received[0]
    assert content_type == "application/json"
    assert data["message"] == "backup"
    assert data["sha"] == "123"
    assert base64.b64decode(data["content"]) == f.read_bytes()


async def define_backup(mocker, name="testbackup"):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(name, None)
    module = gb.github_backup(logging.getLogger("github_backup_test"))
    mocker.patch.object(module, "create_async_task", lambda coro: coro.close())
    await module.Define(
        {"NAME": name, "FHEMPYTYPE": "github_backup"},
        [name, "fhempy", "github_backup", "https://github.com/user/repo", "rpi"],
        {},
    )
    module._attr_github_token = "token"
    return module


def write(path, data=b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@pytest.mark.asyncio
async def test_default_files(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    module = await define_backup(mocker)
    expected = [
        "fhem.cfg",
        "FHEM/FhemUtils/uniqueID",
        ".fhempy/zigbee2mqtt/data/configuration.yaml",
        ".fhempy/zigbee2mqtt/data/devices.yaml",
        ".fhempy/zigbee2mqtt/data/coordinator_backup.json",
        ".fhempy/zigbee2mqtt/data/database.db",
        "esphome_config/garden.yaml",
        "esphome_config/secrets.yaml",
        ".fhempy/matter_server/data/server.json",
        ".fhempy/matter_server/data/fabric/node.1",
    ]
    for f in expected:
        write(tmp_path / f)
    # logs and build files aren't backed up
    write(tmp_path / ".fhempy/zigbee2mqtt/data/log/2026-10-16/log.log")
    write(tmp_path / "esphome_config/.esphome/build/garden/main.cpp")
    write(tmp_path / ".fhempy/matter_server/matter_server.log")

    files = {str(f) for f in module.files_to_backup()}

    assert files == set(expected)


@pytest.mark.asyncio
async def test_readings_after_failed_and_successful_backup(
    mocker, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    module = await define_backup(mocker)
    write(tmp_path / "fhem.cfg", b"new")
    write(tmp_path / "log/fhem.save", b"same")
    _, same_sha = gb.read_file_for_github(tmp_path / "log/fhem.save")
    readings = mock_fhem.readings["testbackup"]
    # reading of an older version
    readings["fhem.cfg_backup"] = "failed"
    readings["last_backup"] = "2026-10-15 03:38:00"

    async def get_401(url):
        raise gb.GithubError(401, url)

    mocker.patch.object(module, "github_get", side_effect=get_401)
    await module.do_backup()

    assert readings["state"] == "failed"
    assert "github_token is invalid" in readings["error"]
    assert readings["failed_files"] == "fhem.cfg,log/fhem.save"
    assert readings["files_failed"] == 2
    assert "last_successful_backup" not in readings

    async def get(url):
        if url.endswith("fhem.save"):
            return {"sha": same_sha}
        return None

    put = mocker.AsyncMock(return_value=True)
    mocker.patch.object(module, "github_get", side_effect=get)
    mocker.patch.object(module, "github_put", put)
    await module.do_backup()

    assert readings["state"] == "ok"
    assert "error" not in readings
    assert "failed_files" not in readings
    assert readings["files_failed"] == 0
    assert readings["files_uploaded"] == 1
    assert readings["files_unchanged"] == 1
    assert readings["last_successful_backup"] == readings["last_backup"]
    put.assert_awaited_once()


@pytest.mark.asyncio
async def test_old_failed_readings_are_removed(mocker):
    module = await define_backup(mocker)
    readings = mock_fhem.readings["testbackup"]
    readings.update(
        {
            "fhem.cfg_backup": "failed",
            "log/fhem.save_backup": "failed",
            "last_backup": "2026-10-15 03:38:00",
        }
    )
    module.gh_token_ready.set()
    mocker.patch.object(module, "do_backup", mocker.AsyncMock())

    async def stop(seconds):
        raise asyncio.CancelledError

    mocker.patch.object(gb.asyncio, "sleep", stop)
    with pytest.raises(asyncio.CancelledError):
        await module.backup_loop()

    assert "fhem.cfg_backup" not in readings
    assert "log/fhem.save_backup" not in readings
    assert readings["last_backup"] == "2026-10-15 03:38:00"
    assert "next_backup" in readings


@pytest.mark.asyncio
async def test_no_files_found(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    module = await define_backup(mocker)
    await module.do_backup()
    readings = mock_fhem.readings["testbackup"]
    assert readings["state"] == "failed"
    assert "backup_files" in readings["error"]


@pytest.mark.asyncio
async def test_github_get_404_is_new_file_and_401_raises():
    async def missing(request):
        return web.Response(status=404)

    async def unauthorized(request):
        return web.Response(status=401)

    app = web.Application()
    app.router.add_get("/missing", missing)
    app.router.add_get("/unauthorized", unauthorized)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    module = gb.github_backup(logging.getLogger("github_backup_test"))
    # local test server without TLS
    base = f"http://127.0.0.1:{port}"  # NOSONAR
    try:
        assert await module.github_get(f"{base}/missing") is None
        with pytest.raises(gb.GithubError) as err:
            await module.github_get(f"{base}/unauthorized")
    finally:
        await runner.cleanup()
    assert "HTTP 401" in str(err.value)
