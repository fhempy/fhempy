import asyncio

import pytest
from fhempy.lib import fhem


@pytest.mark.asyncio
async def test_send_command_name_propagates_cancel(monkeypatch):
    async def hang(*_):
        await asyncio.Event().wait()

    monkeypatch.setattr(fhem, "send_and_wait", hang)
    task = asyncio.create_task(fhem.sendCommandName("dev", "get dev state"))
    await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_send_command_name_returns_exception_text(monkeypatch):
    async def fail(*_):
        await asyncio.sleep(0)
        raise RuntimeError("boom")

    monkeypatch.setattr(fhem, "send_and_wait", fail)
    assert await fhem.sendCommandName("dev", "get dev state") == "boom"


@pytest.mark.asyncio
async def test_bulk_updates_are_sent_in_one_command(monkeypatch):
    sent = []

    async def send(hash, cmd):
        sent.append(cmd)
        return ""

    monkeypatch.setattr(fhem, "sendCommandHash", send)
    hash = {"NAME": "dev"}

    await fhem.readingsBeginUpdate(hash)
    await fhem.readingsBulkUpdate(hash, "a", 1)
    await fhem.readingsBulkUpdateIfChanged(hash, "b", "it's")
    await fhem.readingsEndUpdate(hash, 1)

    assert sent == [
        "readingsBeginUpdate($defs{'dev'});;"
        "readingsBulkUpdate($defs{'dev'},'a','1');;"
        "readingsBulkUpdateIfChanged($defs{'dev'},'b','it\\'s');;"
        "readingsEndUpdate($defs{'dev'},1);;"
    ]
    assert not fhem.update_locks["dev"].locked()


@pytest.mark.asyncio
async def test_end_update_releases_lock_on_error(monkeypatch):
    async def fail(hash, cmd):
        raise RuntimeError("connection lost")

    monkeypatch.setattr(fhem, "sendCommandHash", fail)
    hash = {"NAME": "dev_error"}

    await fhem.readingsBeginUpdate(hash)
    with pytest.raises(RuntimeError):
        await fhem.readingsEndUpdate(hash, 1)

    assert not fhem.update_locks["dev_error"].locked()


def test_escape_value_for_perl_single_quotes():
    assert fhem.escapeValue("it's a\\b") == "it\\'s a\\\\b"
