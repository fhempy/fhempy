import base64
import hashlib
import json
import logging

import pytest
from aiohttp import web

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
