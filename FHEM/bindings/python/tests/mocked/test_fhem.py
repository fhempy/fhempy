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
