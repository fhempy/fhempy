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


@pytest.mark.asyncio
async def test_other_devices_are_released_when_fhem_stops_waiting(monkeypatch):
    sent = []

    async def send_and_wait(name, cmd):
        sent.append(name)
        return {"result": ""}

    monkeypatch.setattr(fhem, "send_and_wait", send_and_wait)
    monkeypatch.setattr(fhem, "function_active", [])
    slow = {"NAME": "slow", "id": 1, "function": "Set", "timeout": 50}
    fhem.setFunctionActive(slow)

    task = asyncio.create_task(fhem.sendCommandName("other", "cmd"))
    await asyncio.sleep(0.01)
    assert sent == []

    # FHEM gave up waiting for "slow", other devices must not wait any longer
    await asyncio.wait_for(task, 1)
    assert sent == ["other"]
    assert fhem.function_active == []

    # the late reply of the slow function doesn't touch the list anymore
    fhem.setFunctionInactive(slow)
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_functions_finishing_out_of_order(monkeypatch):
    monkeypatch.setattr(fhem, "function_active", [])
    first = {"NAME": "dev1", "id": 1, "function": "Set"}
    second = {"NAME": "dev2", "id": 2, "function": "Set"}
    fhem.setFunctionActive(first)
    fhem.setFunctionActive(second)

    fhem.setFunctionInactive(first)
    assert [f["NAME"] for f in fhem.function_active] == ["dev2"]

    fhem.setFunctionInactive(second)
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_error_reply_for_non_function_message_keeps_active_function(
    monkeypatch,
):
    monkeypatch.setattr(fhem, "function_active", [])
    fhem.setFunctionActive({"NAME": "dev1", "id": 1, "function": "Set"})

    # e.g. sendBackError for a failed event, which never was active
    fhem.setFunctionInactive({"NAME": "dev2", "id": 99})
    assert [f["NAME"] for f in fhem.function_active] == ["dev1"]
    fhem.setFunctionInactive({"NAME": "dev1", "id": 1})


@pytest.mark.asyncio
async def test_function_timeout_defaults(monkeypatch):
    # older 10_BindingsIo.pm doesn't send its timeout
    monkeypatch.setattr(fhem, "function_active", [])
    fhem.setFunctionActive({"NAME": "d", "id": 1, "function": "Set"})
    fhem.setFunctionActive({"NAME": "e", "id": 2, "function": "Define"})
    now = asyncio.get_running_loop().time()
    set_entry, define_entry = fhem.function_active
    assert set_entry["timer"].when() - now == pytest.approx(3, abs=0.1)
    assert define_entry["timer"].when() - now == pytest.approx(30, abs=0.1)

    fhem.setFunctionInactive({"NAME": "e", "id": 2})
    fhem.setFunctionInactive({"NAME": "d", "id": 1})
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_get_device_info_in_one_command(monkeypatch):
    sent = []

    async def send(name, cmd):
        sent.append(cmd)
        # FHEM's JSON encoder might send numbers for numeric attribute values
        return '{"init_done":1,"attr":{"verbose":5,"disable":"0"}}'

    monkeypatch.setattr(fhem, "sendCommandName", send)
    info = await fhem.getDeviceInfo("dev'x", {"verbose": "3", "disable": "0"})

    assert sent == [
        "to_json({init_done=>$init_done,attr=>{"
        "'verbose'=>AttrVal('dev\\'x','verbose','3'),"
        "'disable'=>AttrVal('dev\\'x','disable','0')}})"
    ]
    assert info == {"init_done": 1, "attr": {"verbose": "5", "disable": "0"}}


@pytest.mark.asyncio
async def test_get_device_info_uses_defaults_without_reply(monkeypatch):
    async def send(name, cmd):
        # sendCommandName returns "" on timeout
        return ""

    monkeypatch.setattr(fhem, "sendCommandName", send)
    info = await fhem.getDeviceInfo("dev", {"verbose": "3", "room": ""})

    assert info == {"init_done": 0, "attr": {"verbose": "3", "room": ""}}
