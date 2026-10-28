import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock

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
    assert pb._last_msg_cleanup >= now

    # Message 4 is stale, but cleanup shouldn't run again immediately (< 30s)
    pb.msg_received_time[4] = {"time": now - 120, "desc": "stale2"}
    pb.msg_handling_completed({"id": 3})
    assert list(pb.msg_received_time) == [4]

    # After 31 seconds elapsed, cleanup runs again
    pb._last_msg_cleanup = now - 35
    pb.msg_received_time[5] = {"time": now, "desc": "done2"}
    pb.msg_handling_completed({"id": 5})
    assert list(pb.msg_received_time) == []


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


class SetModule:
    calls = []

    def __init__(self, logger):
        pass

    async def Define(self, hash, args, argsh):
        self.hash = hash

    async def Set(self, hash, args, argsh):
        cmd = args[1]
        SetModule.calls.append(f"start {cmd}")
        if cmd.startswith("slow"):
            await asyncio.sleep(0.2)
        if cmd == "slowfail":
            raise RuntimeError("cloud not reachable")
        SetModule.calls.append(f"end {cmd}")
        if cmd == "usage":
            return "Usage: set counting_dev usage <value>"
        return ""


def set_binding(monkeypatch, module_class=SetModule):
    pb = counting_binding(monkeypatch, {"value": "0"})
    SetModule.calls = []
    module = type("module", (), {"counting": module_class})

    async def import_module(hash):
        return module

    replies = []
    send_back_return = pb.sendBackReturn

    async def record_reply(hash, ret):
        replies.append((hash["args"][1] if len(hash["args"]) > 1 else None, ret))
        await send_back_return(hash, ret)

    monkeypatch.setattr(pb, "import_module", import_module)
    monkeypatch.setattr(pb, "sendBackReturn", record_reply)
    return pb, replies


def set_hash(cmd, msg_id):
    hash = function_hash("Set", ["counting_dev", cmd, "secret"])
    hash["id"] = msg_id
    return hash


@pytest.mark.asyncio
async def test_slow_set_replies_before_it_finishes(monkeypatch):
    pb, replies = set_binding(monkeypatch)
    await pb.handle_function(function_hash("Define"), "")
    replies.clear()

    start = time.monotonic()
    await pb.handle_function(set_hash("slow", 2), "")
    duration = time.monotonic() - start

    assert duration < 0.15
    assert replies == [("slow", "")]
    assert SetModule.calls == ["start slow"]
    await asyncio.sleep(0.3)
    assert SetModule.calls == ["start slow", "end slow"]


@pytest.mark.asyncio
async def test_fast_set_returns_its_result(monkeypatch):
    pb, replies = set_binding(monkeypatch)
    await pb.handle_function(function_hash("Define"), "")
    replies.clear()

    await pb.handle_function(set_hash("usage", 2), "")

    assert replies == [("usage", "Usage: set counting_dev usage <value>")]


def test_set_question_mark_is_not_run_in_background():
    assert not fhem_pythonbinding.is_backgroundable_set(set_hash("?", 2))
    assert not fhem_pythonbinding.is_backgroundable_set(function_hash("Set"))
    assert not fhem_pythonbinding.is_backgroundable_set(attr_disable("1"))
    assert fhem_pythonbinding.is_backgroundable_set(set_hash("on", 2))


@pytest.mark.asyncio
async def test_sets_of_a_device_keep_their_order(monkeypatch):
    pb, replies = set_binding(monkeypatch)
    await pb.handle_function(function_hash("Define"), "")
    replies.clear()

    await pb.handle_function(set_hash("slow_on", 2), "")
    await pb.handle_function(set_hash("slow_off", 3), "")
    assert replies == [("slow_on", ""), ("slow_off", "")]
    await asyncio.sleep(0.6)

    assert SetModule.calls == [
        "start slow_on",
        "end slow_on",
        "start slow_off",
        "end slow_off",
    ]


@pytest.mark.asyncio
async def test_late_set_error_is_logged_without_arguments(monkeypatch, caplog):
    pb, _ = set_binding(monkeypatch)
    await pb.handle_function(function_hash("Define"), "")

    await pb.handle_function(set_hash("slowfail", 2), "")
    await asyncio.sleep(0.3)

    errors = [r for r in caplog.records if r.name == "counting_dev"]
    assert len(errors) == 1
    assert errors[0].getMessage() == "set slowfail failed"
    assert "secret" not in caplog.text


@pytest.mark.asyncio
async def test_undefine_cancels_running_set(monkeypatch):
    from fhempy.lib import generic

    class GenericSetModule(generic.FhemModule):
        async def Define(self, hash, args, argsh):
            self.hash = hash

        async def Set(self, hash, args, argsh):
            SetModule.calls.append("start")
            await asyncio.sleep(3600)

    pb, _ = set_binding(monkeypatch, GenericSetModule)
    await pb.handle_function(function_hash("Define"), "")
    instance = fhem_pythonbinding.loadedModuleInstances["counting_dev"]

    await pb.handle_function(set_hash("on", 2), "")
    assert len(instance._tasks) == 1
    task = instance._tasks[0]
    await pb.handle_function(function_hash("Undefine"), "")
    await asyncio.sleep(0)

    assert task.cancelled()
    assert instance._tasks == []


DEFINE_USAGE = "Usage: define NAME fhempy counting VALUE"


def validating_binding(monkeypatch):
    pb = counting_binding(monkeypatch, {"value": "0"})
    monkeypatch.setattr(fhem_pythonbinding, "moduleLoadingRunning", {})

    def validate(args, argsh):
        if len(args) != 4 or argsh:
            return DEFINE_USAGE
        return None

    monkeypatch.setattr(
        CountingModule, "validate_define", staticmethod(validate), raising=False
    )
    pb.wsconnection.send = AsyncMock()
    return pb


def finished_returns(pb):
    messages = [json.loads(call.args[0]) for call in pb.wsconnection.send.call_args_list]
    return [msg["returnval"] for msg in messages if msg.get("finished")]


@pytest.mark.asyncio
@pytest.mark.parametrize("function", ["Define", "Set"])
async def test_first_load_validation_error_is_state_not_a_second_reply(
    monkeypatch, function
):
    pb = validating_binding(monkeypatch)
    readings = AsyncMock()
    constructor = Mock(return_value=None)
    monkeypatch.setattr(fhem, "readingsSingleUpdate", readings)
    monkeypatch.setattr(CountingModule, "__init__", constructor)
    request = function_hash(function, ["counting_dev", "update"])

    await pb.handle_function(request, "")

    assert finished_returns(pb) == [""]
    readings.assert_awaited_once_with(request, "state", DEFINE_USAGE, 1)
    constructor.assert_not_called()
    assert CountingModule.calls == []
    assert fhem_pythonbinding.loadedModuleInstances == {}
    assert fhem_pythonbinding.moduleLoadingRunning == {}
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_rejected_redefine_keeps_the_running_instance(monkeypatch):
    pb = validating_binding(monkeypatch)
    old = CountingModule(None)
    old.hash = function_hash("Define", ["counting_dev", "fhempy", "counting", "old"])
    fhem_pythonbinding.loadedModuleInstances["counting_dev"] = old
    pb.check_and_install_dependencies = AsyncMock()
    pb.import_module = AsyncMock()
    request = function_hash("Define", ["counting_dev", "fhempy", "counting"])

    await pb.handle_function(request, "")

    assert finished_returns(pb) == [DEFINE_USAGE]
    assert fhem_pythonbinding.loadedModuleInstances["counting_dev"] is old
    assert old.hash["args"][-1] == "old"
    assert CountingModule.calls == []  # neither Undefine nor Define was called
    pb.check_and_install_dependencies.assert_not_awaited()
    pb.import_module.assert_not_awaited()
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_valid_redefine_replies_before_slow_initialization(monkeypatch):
    pb = validating_binding(monkeypatch)
    old = CountingModule(None)
    old.hash = function_hash("Define")
    fhem_pythonbinding.loadedModuleInstances["counting_dev"] = old
    entered, finish = asyncio.Event(), asyncio.Event()

    async def slow_define(self, hash, args, argsh):
        self.hash = hash
        entered.set()
        await finish.wait()
        CountingModule.calls.append("Define")

    monkeypatch.setattr(CountingModule, "Define", slow_define)
    request = function_hash("Define", ["counting_dev", "fhempy", "counting", "new"])
    task = asyncio.create_task(pb.handle_function(request, ""))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        assert finished_returns(pb) == [""]
        assert not task.done()
        assert fhem.function_active == []
    finally:
        finish.set()
        await task
    assert CountingModule.calls == ["Undefine", "Define"]
    assert finished_returns(pb) == [""]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function,args",
    [
        ("Undefine", []),
        ("Rename", ["counting_new", "counting_dev"]),
        ("Attr", ["set", "counting_dev", "disable", "1"]),
        ("Set", ["counting_dev", "update"]),
        ("Get", ["counting_dev", "status"]),
    ],
)
async def test_control_calls_are_not_refused_during_dependency_install(
    monkeypatch, function, args
):
    pb = validating_binding(monkeypatch)
    entered = asyncio.Event()

    async def install(hash):
        entered.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(pb, "check_and_install_dependencies", install)
    request = function_hash("Define", ["counting_dev", "fhempy", "counting", "value"])
    task = asyncio.create_task(pb.handle_function(request, ""))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        assert finished_returns(pb) == [""]
        control = function_hash(function, args)
        control["id"] = 2
        await asyncio.wait_for(pb.handle_function(control, ""), 1)
        assert finished_returns(pb) == ["", ""]
        assert not task.done()
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert fhem_pythonbinding.moduleLoadingRunning == {}
    assert fhem.function_active == []


@pytest.mark.asyncio
async def test_changing_module_type_does_not_call_the_old_validator(monkeypatch):
    pb = counting_binding(monkeypatch, {"value": "0"})
    pb.wsconnection.send = AsyncMock()

    class OldModule(CountingModule):
        validate_define = Mock(return_value="Only valid for the old module type")

    old = OldModule(None)
    old.hash = dict(function_hash("Define"), FHEMPYTYPE="old_module")
    fhem_pythonbinding.loadedModuleInstances["counting_dev"] = old

    await pb.handle_function(function_hash("Define"), "")

    OldModule.validate_define.assert_not_called()
    assert finished_returns(pb) == [""]
    assert CountingModule.calls == ["Undefine", "Define"]


@pytest.mark.asyncio
async def test_orphaned_tailscale_is_stopped_without_remote_access(monkeypatch):
    from fhempy.lib.remote_access import tailscale

    monkeypatch.setattr(fhem_pythonbinding, "ORPHAN_CHECK_DELAY", 0)
    stop_orphan = AsyncMock()
    monkeypatch.setattr(tailscale, "stop_orphan", stop_orphan)
    instance = Mock(hash={"NAME": "remote", "FHEMPYTYPE": "remote_access"})
    monkeypatch.setattr(fhem_pythonbinding, "loadedModuleInstances", {})

    fhem_pythonbinding.loadedModuleInstances["remote"] = instance
    await fhem_pythonbinding.stop_orphans()
    stop_orphan.assert_not_called()

    del fhem_pythonbinding.loadedModuleInstances["remote"]
    await fhem_pythonbinding.stop_orphans()
    stop_orphan.assert_called_once()
