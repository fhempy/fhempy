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
