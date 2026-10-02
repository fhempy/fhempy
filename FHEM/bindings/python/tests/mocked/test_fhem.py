import asyncio
import json

import pytest
from fhempy.lib import fhem, fhem_pythonbinding


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


class FakeWebsocket:
    def __init__(self):
        self.sent = []

    async def send(self, msg):
        self.sent.append(json.loads(msg))


@pytest.mark.asyncio
async def test_send_and_wait_gets_reply_by_await_id(monkeypatch):
    pb = fhem_pythonbinding.fhempy(FakeWebsocket())
    monkeypatch.setattr(fhem, "wsconnection", pb)

    task = asyncio.create_task(fhem.send_and_wait("dev", "1+1"))
    await asyncio.sleep(0)
    await_id = pb.wsconnection.sent[0]["awaitId"]
    reply = {"awaitId": await_id, "error": 0, "result": "2"}
    await pb.handle_message(json.dumps(reply), reply)

    assert (await task)["result"] == "2"
    assert pb._msg_listeners == {}


@pytest.mark.asyncio
async def test_send_and_wait_removes_listener_on_timeout(monkeypatch):
    pb = fhem_pythonbinding.fhempy(FakeWebsocket())
    monkeypatch.setattr(fhem, "wsconnection", pb)

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(fhem.send_and_wait("dev", "1+1"), 0.01)

    assert pb._msg_listeners == {}


@pytest.mark.asyncio
async def test_command_waits_for_active_function_of_other_device(monkeypatch):
    sent = []

    async def send_and_wait(name, cmd):
        sent.append(name)
        return {"result": ""}

    monkeypatch.setattr(fhem, "send_and_wait", send_and_wait)
    fhem.setFunctionActive({"NAME": "busy"})
    try:
        task = asyncio.create_task(fhem.sendCommandName("other", "cmd"))
        await asyncio.sleep(0.01)
        assert sent == []

        # commands of the device with the active function are sent right away
        await fhem.sendCommandName("busy", "cmd")
        assert sent == ["busy"]
    finally:
        fhem.setFunctionInactive({"NAME": "busy"})

    await asyncio.wait_for(task, 1)
    assert sent == ["busy", "other"]
    assert fhem.function_waiters == []
