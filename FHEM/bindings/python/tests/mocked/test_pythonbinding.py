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


class CountingModule:
    calls = []

    def __init__(self, logger):
        pass

    async def Define(self, hash, args, argsh):
        self.hash = hash
        CountingModule.calls.append("Define")

    async def Undefine(self, hash):
        # fails like modules which use attributes set in Define
        self.hash
        CountingModule.calls.append("Undefine")


def counting_binding(monkeypatch, disable_attr):
    pb = fhempy_instance()
    CountingModule.calls = []
    module = type("module", (), {"counting": CountingModule})

    async def no_install(hash):
        pass

    async def import_module(hash):
        return module

    async def get_device_info(name, attrs):
        # FHEM calls the Attr function before it stores the new value
        return {"attr": {"verbose": "3", "disable": disable_attr["value"]}}

    async def readings_update(*args):
        pass

    monkeypatch.setattr(pb, "check_and_install_dependencies", no_install)
    monkeypatch.setattr(pb, "import_module", import_module)
    monkeypatch.setattr(fhem, "getDeviceInfo", get_device_info)
    monkeypatch.setattr(fhem, "readingsSingleUpdate", readings_update)
    monkeypatch.setattr(fhem, "function_active", [])
    monkeypatch.setattr(fhem_pythonbinding, "loadedModuleInstances", {})
    return pb


def function_hash(function, args=None):
    return {
        "id": 1,
        "NAME": "counting_dev",
        "function": function,
        "FHEMPYTYPE": "counting",
        "args": args or [],
        "argsh": {},
        "defargs": ["counting_dev", "fhempy", "counting"],
        "defargsh": {},
    }


def attr_disable(value):
    return function_hash("Attr", ["set", "counting_dev", "disable", value])


@pytest.mark.asyncio
async def test_disable_toggle_calls_define_and_undefine_once(monkeypatch):
    disable_attr = {"value": "0"}
    pb = counting_binding(monkeypatch, disable_attr)

    await pb.handle_function(function_hash("Define"), "")
    # running device, disable 0 must not call Define a second time
    await pb.handle_function(attr_disable("0"), "")
    await pb.handle_function(attr_disable("1"), "")
    disable_attr["value"] = "1"
    await pb.handle_function(attr_disable("0"), "")

    assert CountingModule.calls == ["Define", "Undefine", "Define"]
    assert "counting_dev" in fhem_pythonbinding.loadedModuleInstances


@pytest.mark.asyncio
async def test_disabled_device_is_not_undefined(monkeypatch):
    pb = counting_binding(monkeypatch, {"value": "1"})

    await pb.handle_function(function_hash("Define"), "")
    assert "counting_dev" in fhem_pythonbinding.loadedModuleInstances
    await pb.handle_function(
        function_hash("Rename", ["counting_new", "counting_dev"]), ""
    )
    hash = function_hash("Undefine")
    hash["NAME"] = "counting_new"
    await pb.handle_function(hash, "")

    assert CountingModule.calls == []
    assert fhem_pythonbinding.loadedModuleInstances == {}


@pytest.mark.asyncio
async def test_tasks_are_cancelled_when_undefine_fails(monkeypatch):
    from fhempy.lib import generic

    class BrokenUndefine(generic.FhemModule):
        async def Define(self, hash, args, argsh):
            self.hash = hash
            self.loop_task = self.create_async_task(asyncio.sleep(3600))

        async def Undefine(self, hash):
            raise RuntimeError("connection close failed")

    pb = counting_binding(monkeypatch, {"value": "0"})
    module = type("module", (), {"counting": BrokenUndefine})

    async def import_module(hash):
        return module

    monkeypatch.setattr(pb, "import_module", import_module)

    await pb.handle_function(function_hash("Define"), "")
    instance = fhem_pythonbinding.loadedModuleInstances["counting_dev"]
    # let the task start
    await asyncio.sleep(0)
    await pb.handle_function(function_hash("Undefine"), "")
    await asyncio.sleep(0)

    assert instance.loop_task.done()
    assert instance._tasks == []


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
