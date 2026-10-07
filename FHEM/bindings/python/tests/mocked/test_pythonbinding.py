import asyncio
import json
import time

import pytest
import websockets
from fhempy.lib import fhem, fhem_pythonbinding


@pytest.mark.asyncio
async def test_reply_without_waiting_listener_is_ignored():
    pb = fhempy_instance()
    reply = {"awaitId": 12345678, "error": 0, "result": ""}

    # must not be handled as function call (which needs "id" and "msgtype")
    await pb.handle_message(json.dumps(reply), reply)

    assert pb._msg_listeners == {}


@pytest.mark.asyncio
async def test_reply_is_passed_to_waiting_listener():
    pb = fhempy_instance()
    received = []
    pb.register_msg_listener(received.append, 12345678)
    msg = json.dumps({"awaitId": 12345678, "error": 0, "result": "ok"})

    await pb.handle_message(msg, json.loads(msg))

    assert received == [json.loads(msg)]
    assert pb._msg_listeners == {}


def test_msg_handling_completed_removes_stale_messages():
    pb = fhempy_instance()
    now = time.time()
    pb.msg_received_time = {
        1: {"time": now, "desc": "done"},
        2: {"time": now - 120, "desc": "stale"},
        3: {"time": now, "desc": "running"},
    }

    pb.msg_handling_completed({"id": 1})

    assert list(pb.msg_received_time) == [3]


@pytest.mark.asyncio
async def test_send_back_error_without_received_timestamp(monkeypatch):
    monkeypatch.setattr(fhem, "function_active", [])
    pb = fhempy_instance()
    sent = []

    async def send(msg):
        sent.append(msg)

    pb.wsconnection.send = send
    await pb.sendBackError({"id": 4711, "NAME": "dev"}, "failed")

    assert len(sent) == 1


class FakeWebsocket:
    async def send(self, msg):
        pass


def fhempy_instance():
    return fhem_pythonbinding.fhempy(FakeWebsocket())


@pytest.mark.asyncio
async def test_define_is_retried_after_module_loading_failed(monkeypatch):
    pb = fhempy_instance()
    attempts = []

    async def fail_install(hash):
        attempts.append(hash["id"])
        raise ModuleNotFoundError("network not ready")

    async def readings_update(*args):
        pass

    monkeypatch.setattr(pb, "check_and_install_dependencies", fail_install)
    monkeypatch.setattr(fhem, "readingsSingleUpdate", readings_update)
    monkeypatch.setattr(fhem, "function_active", [])

    for msg_id in (1, 2):
        hash = {
            "id": msg_id,
            "NAME": "retry_dev",
            "function": "Define",
            "FHEMPYTYPE": "helloworld",
            "args": [],
            "argsh": {},
            "defargs": [],
            "defargsh": {},
        }
        await pb.handle_function(hash, "")

    assert attempts == [1, 2]
    assert "retry_dev" not in fhem_pythonbinding.moduleLoadingRunning


@pytest.mark.asyncio
async def test_version_request_sends_version(monkeypatch):
    pb = fhempy_instance()
    sent = []

    async def send(msg):
        sent.append(json.loads(msg))

    monkeypatch.setattr(pb, "send", send)
    monkeypatch.setattr(fhem, "wsconnection", pb)
    msg = {"id": 4711, "msgtype": "version", "NAME": "fhempy_local"}

    await pb.handle_message(json.dumps(msg), msg)

    assert len(sent) == 1
    assert sent[0]["msgtype"] == "version"
    assert sent[0]["version"] == fhem.__version__
    assert 4711 not in fhem_pythonbinding.id_received_timestamp


class ClosedWebsocket:
    async def send(self, msg):
        raise AssertionError("must not send on a closed connection")


class UndefineModule:
    def __init__(self, name, error=None):
        self.hash = {"NAME": name}
        self.error = error
        self.undefined = False

    async def Undefine(self, hash):
        self.undefined = True
        if self.error:
            raise self.error


@pytest.mark.asyncio
async def test_undefine_all_skips_devices_without_define(monkeypatch, caplog):
    working = UndefineModule("working")
    failing = UndefineModule("failing", ValueError("list.remove(x): x not in list"))
    disabled = UndefineModule("disabled")
    del disabled.hash
    monkeypatch.setattr(
        fhem_pythonbinding,
        "loadedModuleInstances",
        {"working": working, "failing": failing, "disabled": disabled},
    )
    monkeypatch.setattr(fhem_pythonbinding, "exit_code", 1)
    pb = fhempy_instance()

    await pb.undefine_all()

    assert working.undefined and failing.undefined
    assert not disabled.undefined
    assert fhem_pythonbinding.exit_code == 1
    errors = [r for r in caplog.records if r.levelname == "ERROR"]
    assert errors == []
    assert any("Undefine of failing failed" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_undefine_all_cancels_hanging_undefine(monkeypatch, caplog):
    class Hanging(UndefineModule):
        async def Undefine(self, hash):
            await asyncio.sleep(10)

    monkeypatch.setattr(
        fhem_pythonbinding, "loadedModuleInstances", {"hanging": Hanging("hanging")}
    )
    monkeypatch.setattr(fhem_pythonbinding, "UNDEFINE_TIMEOUT", 0.01)
    pb = fhempy_instance()

    await pb.undefine_all()

    assert any("Undefine of hanging didn't finish" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_function_call_while_stopping_is_not_passed_to_module(monkeypatch):
    class Module:
        async def Set(self, hash, args, argsh):
            raise AssertionError("module must not be called")

    monkeypatch.setattr(fhem, "function_active", [])
    monkeypatch.setattr(fhem_pythonbinding, "loadedModuleInstances", {"dev": Module()})
    pb = fhempy_instance()
    sent = []

    async def send(msg):
        sent.append(json.loads(msg))

    pb.wsconnection.send = send
    pb._stopping = True
    for msg_id, arg in ((1, "?"), (2, "on")):
        hash = {"id": msg_id, "NAME": "dev", "function": "Set"}
        hash["args"] = ["dev", arg]
        hash["argsh"] = {}
        await pb.handle_function(hash, "")

    assert [s["returnval"] for s in sent] == [
        "",
        "fhempy is restarting, command ignored",
    ]
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_reply_on_closed_connection_is_dropped(monkeypatch, caplog):
    monkeypatch.setattr(fhem, "function_active", [])
    pb = fhempy_instance()
    pb.wsconnection = ClosedWebsocket()
    hash = {"id": 4712, "NAME": "dev", "function": "Set"}
    fhem.setFunctionActive(hash)
    pb.connection_closed()

    await pb.sendBackReturn(hash, "")
    await pb.sendBackError(hash, "failed")

    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_reply_after_connection_closed_by_peer(monkeypatch):
    monkeypatch.setattr(fhem, "function_active", [])
    pb = fhempy_instance()

    async def send(msg):
        raise websockets.exceptions.ConnectionClosedError(None, None)

    pb.wsconnection.send = send
    hash = {"id": 4713, "NAME": "dev", "function": "Set"}
    fhem.setFunctionActive(hash)

    await pb.sendBackReturn(hash, "")

    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_send_back_error_does_not_log_define_arguments(monkeypatch, caplog):
    monkeypatch.setattr(fhem, "function_active", [])
    pb = fhempy_instance()
    hash = {
        "id": 4714,
        "NAME": "dev",
        "function": "Set",
        "defargs": ["dev", "fhempy", "volvo", "secret-password"],
    }

    await pb.sendBackError(hash, "failed")

    assert "secret-password" not in caplog.text
    assert "dev Set" in caplog.text


@pytest.mark.asyncio
async def test_expired_function_is_quiet_after_connection_closed(monkeypatch, caplog):
    monkeypatch.setattr(fhem, "function_active", [])
    pb = fhempy_instance()
    monkeypatch.setattr(fhem, "wsconnection", pb)
    entry = {"NAME": "dev", "id": 1, "timer": None}
    fhem.function_active.append(entry)
    pb._closed = True

    fhem.expireFunction(entry)

    assert fhem.function_active == []
    assert "stopped waiting" not in caplog.text
