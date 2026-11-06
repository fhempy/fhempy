import asyncio
import json
import time

import pytest
from fhempy.lib import fhem, fhem_pythonbinding, pkg_installer
from fhempy.lib.core import loop_watchdog, worker_groups, workers

MANIFESTS = {
    "core_mod": {"requirements": ["pkg-a==1.0"]},
    "old_mqtt": {"requirements": ["paho-mqtt==1.6.1"]},
    "new_mqtt": {"requirements": ["paho-mqtt==2.1.0"]},
    "new_mqtt_too": {"requirements": ["paho-mqtt==2.1.0", "other==1"]},
    "gateway": {"requirements": ["miio==1"]},
    "gateway_device": {"requirements": ["miio==1"], "worker": {"with": ["gateway"]}},
    "updater": {"requirements": [], "worker": {"core": True}},
    "backup": {"requirements": ["git==1"], "worker": {"with": ["updater"]}},
    "plain": {"requirements": []},
}


def paho_resolver(calls):
    """Conflict if two different paho-mqtt versions are requested."""

    async def resolve(reqs):
        calls.append(list(reqs))
        paho = {r for r in reqs if r.startswith("paho-mqtt")}
        if len(paho) > 1:
            return False, True
        return True, False

    return resolve


def assigner(tmp_path, monkeypatch, calls=None, installed=()):
    monkeypatch.delenv("FHEMPY_WORKERS", raising=False)
    monkeypatch.setattr(pkg_installer, "find_uv", lambda: "/usr/bin/uv")
    monkeypatch.setattr(worker_groups, "core_requirements", lambda: ("websockets==17",))

    async def deps_ok(reqs):
        return all(r in installed for r in reqs)

    return worker_groups.GroupAssigner(
        path=str(tmp_path / "workers.json"),
        manifests=MANIFESTS,
        resolver=paho_resolver([] if calls is None else calls),
        deps_ok=deps_ok,
    )


def test_families_join_modules_which_use_each_other():
    families = worker_groups.Families(MANIFESTS)

    assert families.key("gateway_device") == "gateway"
    assert families.members("gateway") == ["gateway", "gateway_device"]
    assert families.core_only("backup")
    assert not families.core_only("gateway")


@pytest.mark.asyncio
async def test_installed_requirements_stay_in_core(tmp_path, monkeypatch):
    calls = []
    a = assigner(tmp_path, monkeypatch, calls, installed=("pkg-a==1.0",))

    assert await a.group_for("core_mod") == worker_groups.CORE
    assert await a.group_for("plain") == worker_groups.CORE
    # no uv check needed
    assert calls == []


@pytest.mark.asyncio
async def test_conflicting_module_gets_own_worker(tmp_path, monkeypatch):
    a = assigner(tmp_path, monkeypatch)

    assert await a.group_for("old_mqtt") == worker_groups.CORE
    assert await a.group_for("new_mqtt", core_modules={"old_mqtt"}) == "new_mqtt"
    assert a.group_info("new_mqtt") == {"venv": True}
    # a module which fits into the existing worker joins it
    assert await a.group_for("new_mqtt_too", core_modules={"old_mqtt"}) == "new_mqtt"

    stored = json.loads((tmp_path / "workers.json").read_text())
    assert stored["families"]["new_mqtt"]["group"] == "new_mqtt"
    assert stored["families"]["new_mqtt"]["reason"] == "conflict"
    assert stored["families"]["old_mqtt"]["group"] == "core"


@pytest.mark.asyncio
async def test_assignment_is_kept_until_requirements_change(tmp_path, monkeypatch):
    calls = []
    a = assigner(tmp_path, monkeypatch, calls)
    await a.group_for("old_mqtt")
    await a.group_for("new_mqtt")
    count = len(calls)

    # fhempy restart: the stored decision is used without a new check
    b = assigner(tmp_path, monkeypatch, calls)
    assert await b.group_for("new_mqtt") == "new_mqtt"
    assert len(calls) == count

    # fhempy update changed the requirements: decided again
    manifests = dict(MANIFESTS)
    manifests["new_mqtt"] = {"requirements": ["paho-mqtt==1.6.1"]}
    c = assigner(tmp_path, monkeypatch, calls)
    c._manifests = manifests
    assert await c.group_for("new_mqtt") == worker_groups.CORE


@pytest.mark.asyncio
async def test_failed_check_keeps_module_in_core(tmp_path, monkeypatch):
    a = assigner(tmp_path, monkeypatch)

    async def offline(reqs):
        return False, False

    a._resolver = offline
    await a.group_for("old_mqtt")
    assert await a.group_for("new_mqtt") == worker_groups.CORE


@pytest.mark.asyncio
async def test_core_only_family_never_moves(tmp_path, monkeypatch):
    a = assigner(tmp_path, monkeypatch)

    assert await a.group_for("backup") == worker_groups.CORE
    assert a.record_blocking("backup", 5, now=1) is None
    assert a.record_blocking("backup", 5, now=2) is None
    assert a.record_blocking("backup", 5, now=3) is None


@pytest.mark.asyncio
async def test_workers_can_be_disabled(tmp_path, monkeypatch):
    a = assigner(tmp_path, monkeypatch)
    monkeypatch.setenv("FHEMPY_WORKERS", "0")

    await a.group_for("old_mqtt")
    assert await a.group_for("new_mqtt") == worker_groups.CORE


def test_module_blocking_again_and_again_gets_a_worker(tmp_path, monkeypatch):
    a = assigner(tmp_path, monkeypatch)

    # short blockades don't count
    assert a.record_blocking("gateway_device", 0.6, now=100) is None
    assert a.record_blocking("gateway_device", 2, now=100) is None
    assert a.record_blocking("gateway_device", 2, now=200) is None
    # the first one is too old
    assert a.record_blocking("gateway_device", 2, now=3750) is None
    assert a.record_blocking("gateway_device", 2, now=3780) == "gateway"
    assert a.assigned_group("gateway") == "gateway"
    assert a.group_info("gateway") == {"venv": False}
    # already in a worker
    assert a.record_blocking("gateway", 2, now=3800) is None
    # unknown code (e.g. fhempy itself) doesn't move anything
    assert a.record_blocking(None, 5) is None


def test_watchdog_reports_the_blocking_module(monkeypatch):
    reported = []
    wd = loop_watchdog.LoopWatchdog(asyncio.new_event_loop())
    wd.on_blocked = lambda module, duration: reported.append((module, duration))
    monkeypatch.setattr(wd, "_report", lambda *args, **kwargs: None)
    frame = type("F", (), {"filename": "/x/fhempy/lib/tuya/tuya.py"})()
    wd._seen = (1.0, [frame])

    wd.finished(1.0, 0.8)

    assert [module for module, _ in reported] == ["tuya"]
    assert reported[0][1] == pytest.approx(0.8)


class FakeFHEM:
    """Websocket of the core's FHEM connection, answers commands."""

    def __init__(self):
        self.sent = []
        self.pb = None

    async def send(self, msg):
        m = json.loads(msg)
        self.sent.append(m)
        if m.get("msgtype") == "command":
            cmd = m.get("command") or ""
            result = ""
            if "to_json({init_done" in cmd:
                result = '{"init_done":1,"attr":{}}'
            reply = {"awaitId": m["awaitId"], "error": 0, "result": result}
            asyncio.get_running_loop().call_soon(self.pb.dispatch_without_task, reply)


async def wait_for(condition, timeout=60):
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError("timeout")
        await asyncio.sleep(0.05)


def function_msg(function, args, msg_id, name="hello"):
    return {
        "id": msg_id,
        "msgtype": "function",
        "NAME": name,
        "function": function,
        "args": args,
        "argsh": {},
        "defargs": [name, "fhempy", "helloworld"],
        "defargsh": {},
        "FHEMPYTYPE": "helloworld",
        "timeout": 3000,
    }


@pytest.mark.asyncio
async def test_device_runs_in_worker_process(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FHEMPY_WORKERS", raising=False)
    (tmp_path / ".fhempy").mkdir()
    (tmp_path / ".fhempy" / "workers.json").write_text(
        json.dumps(
            {
                "version": 1,
                "blocking": {},
                "families": {
                    "helloworld": {"group": "hello", "reason": "manual", "venv": False}
                },
            }
        )
    )
    ws = FakeFHEM()
    pb = fhem_pythonbinding.fhempy(ws)
    ws.pb = pb
    fhem.updateConnection(pb)
    router = workers.Router(pb)
    pb.router = router
    try:
        define = function_msg("Define", ["hello", "fhempy", "helloworld"], 1)
        # the core answers FHEM before the requirements are checked
        await pb.handle_function(define, json.dumps(define))
        assert any(m.get("id") == 1 and m.get("finished") for m in ws.sent)
        assert "hello" not in fhem_pythonbinding.loadedModuleInstances
        assert router.devices["hello"]["group"] == "hello"

        worker = router.workers["hello"]
        await asyncio.wait_for(worker.connected.wait(), 60)
        # the worker defines the device and sets its readings via the core
        await wait_for(
            lambda: any(
                m.get("msgtype") == "command" and m.get("NAME") == "hello"
                for m in ws.sent
            )
        )

        get = function_msg("Set", ["hello", "?"], 2)
        assert await router.route_function(get, json.dumps(get))
        await wait_for(
            lambda: any(m.get("id") == 2 and m.get("finished") for m in ws.sent)
        )
        reply = next(m for m in ws.sent if m.get("id") == 2 and m.get("finished"))
        assert "mode" in reply["returnval"]
        # FHEM doesn't wait for the device anymore
        assert fhem.function_active == []

        # devices of the core aren't passed to the worker
        assert router.runs_type("helloworld")
        assert not router.runs_type("tuya")

        # a crashed worker is started again and gets its devices again
        monkeypatch.setattr(workers, "RESTART_DELAYS", (0.1,))
        ws.sent.clear()
        worker.proc.kill()
        await wait_for(
            lambda: any(
                m.get("command", "").startswith("readingsSingleUpdate")
                and "fhempy worker restarting" in m.get("command", "")
                for m in ws.sent
                if m.get("msgtype") == "command"
            )
        )
        await asyncio.wait_for(worker.connected.wait(), 60)
        ws.sent.clear()
        await wait_for(
            lambda: any(
                m.get("msgtype") == "command" and m.get("NAME") == "hello"
                for m in ws.sent
            )
        )
    finally:
        await router.stop_all()
        fhem_instance_cleanup(pb)
    assert worker.proc is None


def fhem_instance_cleanup(pb):
    pb.connection_closed()
    fhem.function_active.clear()


@pytest.mark.asyncio
async def test_rename_and_undefine_follow_the_device(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ws = FakeFHEM()
    pb = fhem_pythonbinding.fhempy(ws)
    ws.pb = pb
    fhem.updateConnection(pb)
    router = workers.Router(pb, assigner=assigner(tmp_path, monkeypatch))
    router._type_group["helloworld"] = "hello"
    started = []
    monkeypatch.setattr(workers.Worker, "start", lambda self: started.append(self))
    try:
        define = function_msg("Define", ["hello", "fhempy", "helloworld"], 1)
        assert await router.route_function(define, json.dumps(define))
        rename = function_msg("Rename", ["hello2", "hello"], 2, name="hello2")
        assert await router.route_function(rename, json.dumps(rename))
        assert list(router.devices) == ["hello2"]
        assert router.devices["hello2"]["define"]["NAME"] == "hello2"

        undefine = function_msg("Undefine", [], 3, name="hello2")
        assert await router.route_function(undefine, json.dumps(undefine))
        assert router.devices == {}
        # unknown device of a core module
        router._type_group["plain"] = "core"
        other = function_msg("Define", ["x", "fhempy", "plain"], 4, name="x")
        other["FHEMPYTYPE"] = "plain"
        assert not await router.route_function(other, json.dumps(other))
        # FHEM got a reply for each function
        assert sorted(m["id"] for m in ws.sent if m.get("finished")) == [1, 2, 3]
    finally:
        fhem_instance_cleanup(pb)


class StubRouter:
    def __init__(self, handled):
        self.handled = handled
        self.routed = []
        self.events = []

    async def route_function(self, hash, msg):
        self.routed.append(hash["function"])
        return self.handled

    def has_workers(self):
        return True

    def forward_event(self, message):
        self.events.append(message)


@pytest.mark.asyncio
async def test_core_passes_devices_of_workers_to_the_router(monkeypatch):
    pb = fhem_pythonbinding.fhempy(FakeFHEM())
    pb.router = StubRouter(handled=True)
    imported = []

    async def import_module(hash):
        imported.append(hash)

    monkeypatch.setattr(pb, "import_module", import_module)
    define = function_msg("Define", ["hello", "fhempy", "helloworld"], 1)

    await pb.handle_function(define, json.dumps(define))

    assert pb.router.routed == ["Define"]
    assert imported == []
    assert "hello" not in fhem_pythonbinding.loadedModuleInstances


class ListWebsocket:
    def __init__(self, messages):
        self.messages = messages

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for message in self.messages:
            yield message


@pytest.mark.asyncio
async def test_events_are_passed_to_workers():
    pb = fhem_pythonbinding.fhempy(FakeFHEM())
    pb.router = StubRouter(handled=True)
    event = json.dumps({"msgtype": "event", "NAME": "lamp", "args": ["on"]})
    reply = json.dumps({"awaitId": 5, "result": ""})

    await fhem_pythonbinding.read_messages(pb, ListWebsocket([event, reply]))

    assert pb.router.events == [event]


def test_autodiscovery_frontends_run_with_autodiscovery():
    """discover_* devices and mqtt_ha_discovery use the autodiscovery engine of
    their process, they have to run where autodiscovery runs"""
    assigner = worker_groups.GroupAssigner(path="/nonexistent/workers.json")
    families = assigner.families()
    for module in ("discover_mdns", "discover_upnp", "discover_ble"):
        assert families.key(module) == "autodiscovery"
        assert assigner.module_requirements(module) == assigner.module_requirements(
            "autodiscovery"
        )
    assert families.key("mqtt_ha_discovery") == "autodiscovery"
