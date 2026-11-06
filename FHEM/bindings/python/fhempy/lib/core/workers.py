"""Worker processes for fhempy modules.

FHEM is connected to the fhempy process (core) only. Devices of modules which
run in a worker (see worker_groups) are passed through by the core:

FHEM  <-- websocket -->  core  <-- unix socket -->  worker

A worker runs the same binding as the core and sees the core like FHEM:
function calls of its devices and all events come from the core, commands of
the worker (readings, attributes, ...) are sent to FHEM by the core. The core
keeps track of the functions FHEM waits for, so commands of other devices
wait like before.

A crashed worker is started again and gets the Define of its devices again,
like after a reconnect of FHEM.
"""

import asyncio
import functools
import itertools
import logging
import os
import shutil
import sys
import tempfile
import time

import websockets
import websockets.asyncio.client

from .. import fhem, pkg_installer, utils
from ..json_utils import json_dumps, json_loads
from . import child_process, worker_groups

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 120
STOP_TIMEOUT = 70
COMMAND_TIMEOUT = 180
INSTALL_TIMEOUT = 900
# restart delays after a crash (s), the last one is repeated
RESTART_DELAYS = (2, 5, 15, 30, 60, 300)
# a worker which ran this long without crash starts with the first delay again
STABLE_TIME = 600
EVENT_MSGTYPES = ("event", "events", "eventlist")

# ids of Define messages the core sends itself, nobody waits for their reply
_internal_ids = itertools.count(-1, -1)

# router of the current FHEM connection
_router = None


def get_router():
    return _router


def on_loop_blocked(module, duration):
    """Called by the loop watchdog of the core after a blockade."""
    router = _router
    if router is None or module is None:
        return
    router.loop_blocked(module, duration)


def workers_dir():
    return os.path.join(os.getcwd(), ".fhempy", "workers")


def socket_path(group):
    path = os.path.join(workers_dir(), group + ".sock")
    if len(path) < 100:
        return path
    # unix socket paths are limited to ~107 bytes
    return os.path.join(tempfile.gettempdir(), f"fhempy-{os.getuid()}-{group}.sock")


def fhempy_package_dir():
    """Directory which contains the fhempy package"""
    from fhempy import lib

    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(lib.__file__)))
    )


class Worker:
    """One worker process and its connection."""

    def __init__(self, router, group, venv):
        self.router = router
        self.group = group
        self.venv = venv
        self.proc = None
        self.ws = None
        self.connected = asyncio.Event()
        self.stopping = False
        self._task = None
        self._crashes = 0
        self._started_at = 0
        self._tasks = set()

    def is_connected(self):
        return self.ws is not None and self.connected.is_set()

    def start(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())

    async def _run(self):
        while not self.stopping:
            try:
                await self._start_and_serve()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(f"fhempy worker '{self.group}' failed")
            if self.stopping:
                # stop() waits until the worker undefined its devices
                return
            await self._cleanup()
            if time.monotonic() - self._started_at > STABLE_TIME:
                self._crashes = 0
            delay = RESTART_DELAYS[min(self._crashes, len(RESTART_DELAYS) - 1)]
            self._crashes += 1
            logger.error(f"fhempy worker '{self.group}' stopped, restart in {delay}s")
            await self.router.worker_down(self)
            await asyncio.sleep(delay)

    async def _start_and_serve(self):
        python, env = await self._prepare()
        path = socket_path(self.group)
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        args = [
            python,
            "-m",
            "fhempy.lib.worker_process",
            "--socket",
            path,
            "--group",
            self.group,
        ]
        logger.info(f"Start fhempy worker '{self.group}'")
        self._started_at = time.monotonic()
        # stdout/stderr like fhempy itself, the log lines go to the fhempy log
        self.proc = child_process.start(args, env=env, cwd=os.getcwd())
        self.ws = await self._connect(path)
        self.connected.set()
        logger.info(f"fhempy worker '{self.group}' connected")
        await self.router.worker_up(self)
        async for message in self.ws:
            self.router.from_worker(self, message)

    async def _connect(self, path):
        deadline = time.monotonic() + CONNECT_TIMEOUT
        while True:
            if self.proc.poll() is not None:
                raise ConnectionError(f"worker exited with code {self.proc.returncode}")
            try:
                return await websockets.asyncio.client.unix_connect(
                    path,
                    uri="ws://localhost/",
                    max_size=None,
                    ping_interval=None,
                    ping_timeout=None,
                    compression=None,
                    close_timeout=2,
                )
            except (OSError, websockets.exceptions.InvalidHandshake):
                if time.monotonic() > deadline:
                    raise
                await asyncio.sleep(0.2)

    async def _prepare(self):
        """Interpreter and environment of the worker process."""
        env = os.environ.copy()
        env["FHEMPY_WORKER"] = self.group
        uv = pkg_installer.find_uv()
        if uv is not None:
            env.setdefault("FHEMPY_UV", uv)
        if not self.venv:
            # same environment as the core
            paths = [fhempy_package_dir()]
            if env.get("PYTHONPATH"):
                paths.append(env["PYTHONPATH"])
            env["PYTHONPATH"] = os.pathsep.join(paths)
            return sys.executable, env

        if uv is None:
            raise RuntimeError("uv is needed for a worker with own environment")
        return await self._prepare_venv(uv, env)

    async def _prepare_venv(self, uv, env):
        """Own virtual environment, for requirements which conflict with the core"""
        base = os.path.join(workers_dir(), self.group)
        venv = os.path.join(base, "venv")
        python, exists, reqs, overrides = await utils.run_blocking(
            functools.partial(_venv_state, venv)
        )
        if not exists:
            logger.info(f"Create environment of fhempy worker '{self.group}'")
            await _run_command(
                [uv, "venv", "--quiet", "--python", sys.executable, venv], env
            )
        # fhempy itself comes from the core, only its requirements are installed
        if reqs:
            args = [uv, "pip", "install", "--quiet", "--python", python] + reqs
            if overrides is not None:
                args += ["--override", overrides]
            await _run_command(args + pkg_installer.uv_index_args(), env)
        src = await utils.run_blocking(functools.partial(_link_fhempy, base))
        env["PYTHONPATH"] = src
        env.pop("PYTHONHOME", None)
        env["VIRTUAL_ENV"] = venv
        return python, env

    async def send(self, msg):
        ws = self.ws
        if ws is None:
            raise ConnectionError(f"fhempy worker '{self.group}' not connected")
        await ws.send(msg)

    def send_soon(self, msg):
        """Send without waiting, e.g. events"""
        if not self.is_connected():
            return
        task = asyncio.create_task(self._send_quiet(msg))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _send_quiet(self, msg):
        try:
            await self.send(msg)
        except (ConnectionError, websockets.exceptions.ConnectionClosed):
            pass

    def create_task(self, coro):
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def _cleanup(self):
        self.connected.clear()
        ws, self.ws = self.ws, None
        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass
        proc, self.proc = self.proc, None
        if proc is not None:
            await child_process.stop(proc, timeout=5)

    async def stop(self):
        """Undefine all devices of the worker and stop it."""
        self.stopping = True
        proc = self.proc
        if self.is_connected():
            try:
                await self.send(json_dumps({"msgtype": "worker_stop"}))
            except (ConnectionError, websockets.exceptions.ConnectionClosed):
                pass
            if proc is not None:
                await child_process._wait(proc, STOP_TIMEOUT)
        if self._task is not None:
            self._task.cancel()
            # wait without raising the cancellation of the task in this one
            await asyncio.wait({self._task})
        await self._cleanup()


def _venv_state(venv):
    python = os.path.join(venv, "bin", "python")
    return (
        python,
        os.path.isfile(python),
        list(worker_groups.core_requirements()),
        pkg_installer.uv_overrides_file(),
    )


def _link_fhempy(base):
    """src directory with a link to the fhempy package of the core"""
    src = os.path.join(base, "src")
    os.makedirs(src, exist_ok=True)
    link = os.path.join(src, "fhempy")
    target = os.path.join(fhempy_package_dir(), "fhempy")
    if os.path.realpath(link) != os.path.realpath(target):
        if os.path.islink(link) or os.path.isfile(link):
            os.unlink(link)
        elif os.path.isdir(link):
            shutil.rmtree(link)
        os.symlink(target, link)
    return src


async def _run_command(args, env):
    proc = await asyncio.create_subprocess_exec(
        *args,
        env=env,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(proc.communicate(), INSTALL_TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"{args[0]} {args[1]} took too long")
    if proc.returncode != 0:
        raise RuntimeError(
            f"{' '.join(args[1:3])} failed: {stderr.decode('utf-8', 'replace')}"
        )


class Router:
    """Passes the messages of devices in workers between FHEM and the workers."""

    def __init__(self, binding, assigner=None):
        # fhempy instance of the FHEM connection
        self.binding = binding
        self.assigner = assigner or worker_groups.GroupAssigner()
        self.workers = {}
        # NAME -> {"group": group, "type": FHEMPYTYPE, "define": Define message}
        self.devices = {}
        # function id -> message, FHEM waits for the reply of the worker
        self._forwarded = {}
        # ids of Define messages sent by the core, their replies are dropped
        self._internal = set()
        self._isolating = set()
        # FHEMPYTYPE -> group, decided once per connection
        self._type_group = {}

    def activate(self):
        global _router
        _router = self

    def deactivate(self):
        global _router
        if _router is self:
            _router = None

    # --- FHEM -> worker ---

    def has_workers(self):
        return bool(self.workers)

    def runs_type(self, fhempy_type):
        return any(d["type"] == fhempy_type for d in self.devices.values())

    def forward_event(self, message):
        for worker in self.workers.values():
            worker.send_soon(message)

    def core_types(self):
        from .. import fhem_pythonbinding

        types = set()
        for instance in list(fhem_pythonbinding.loadedModuleInstances.values()):
            dev_hash = getattr(instance, "hash", None) or {}
            if dev_hash.get("FHEMPYTYPE"):
                types.add(dev_hash["FHEMPYTYPE"])
        return types

    async def route_function(self, hash, msg):
        """True if a worker handles the function, False for the core."""
        name = hash.get("NAME")
        fhempy_type = hash.get("FHEMPYTYPE")
        if name is None or fhempy_type is None:
            return False
        function = hash.get("function")
        if function == "Rename":
            return await self._route_rename(hash, msg)
        if function == "Undefine":
            device = self.devices.pop(name, None)
            if device is None:
                return False
            return await self._forward(device["group"], hash, msg)

        group = await self._target_group(hash)
        if group == worker_groups.CORE:
            return False
        self._remember(group, hash)
        return await self._forward(group, hash, msg)

    async def route_after_reply(self, hash):
        """Define of a new module type, FHEM already got the reply. True if a
        worker handles the device."""
        group = await self.group_for(hash["FHEMPYTYPE"])
        if group == worker_groups.CORE:
            return False
        self._remember(group, hash)
        worker = self._worker(group)
        if worker.is_connected():
            await self._send_define(worker, self.devices[hash["NAME"]])
        # otherwise the worker gets the Define when it's connected
        return True

    async def _send_define(self, worker, device):
        msg = dict(device["define"])
        msg["function"] = "Define"
        msg["msgtype"] = "function"
        msg["id"] = next(_internal_ids)
        self._internal.add(msg["id"])
        try:
            await worker.send(json_dumps(msg))
        except (ConnectionError, websockets.exceptions.ConnectionClosed):
            self._internal.discard(msg["id"])
            return False
        return True

    async def _route_rename(self, hash, msg):
        old_name = hash["args"][1]
        device = self.devices.pop(old_name, None)
        if device is None:
            return False
        device["define"]["NAME"] = hash["NAME"]
        self.devices[hash["NAME"]] = device
        return await self._forward(device["group"], hash, msg)

    async def _target_group(self, hash):
        """Group of the device, moves it if Define changed its type."""
        from .. import fhem_pythonbinding

        name = hash["NAME"]
        fhempy_type = hash["FHEMPYTYPE"]
        is_define = hash.get("function") == "Define"
        device = self.devices.get(name)
        in_core = name in fhem_pythonbinding.loadedModuleInstances
        if device is None and in_core and not is_define:
            return worker_groups.CORE
        if device is not None and (not is_define or device["type"] == fhempy_type):
            return device["group"]

        if device is None and is_define and fhempy_type not in self._type_group:
            # checking the requirements might take a while, the core answers
            # FHEM first and calls route_after_reply
            return worker_groups.CORE
        group = await self.group_for(fhempy_type)
        if device is not None and device["group"] != group:
            # type changed with defmod, the old worker drops the device
            await self._undefine_in_worker(device)
            self.devices.pop(name, None)
        if group != worker_groups.CORE and in_core:
            # defmod with another type, the core drops the device
            await fhem_pythonbinding.undefine_local(name)
        return group

    def _remember(self, group, hash):
        """Keep the Define of the device, the worker gets it after a restart."""
        name = hash["NAME"]
        if hash.get("function") == "Define":
            define = dict(hash)
        elif name in self.devices:
            return
        else:
            # e.g. Attr of a disabled device, loads the module in the worker
            define = dict(hash)
            define.update(
                {
                    "function": "Define",
                    "args": hash.get("defargs", []),
                    "argsh": hash.get("defargsh", {}),
                }
            )
        self.devices[name] = {
            "group": group,
            "type": hash["FHEMPYTYPE"],
            "define": define,
        }

    async def group_for(self, fhempy_type):
        group = self._type_group.get(fhempy_type)
        if group is None:
            await self.assigner.load()
            group = await self.assigner.group_for(fhempy_type, self.core_types())
            self._type_group[fhempy_type] = group
        return group

    def _worker(self, group):
        worker = self.workers.get(group)
        if worker is None:
            venv = self.assigner.group_info(group)["venv"]
            worker = Worker(self, group, venv)
            self.workers[group] = worker
        worker.start()
        return worker

    async def _forward(self, group, hash, msg):
        worker = self._worker(group)
        if not worker.is_connected():
            # the worker gets the Define when it's connected
            await self.binding.sendBackReturn(hash, _not_connected_reply(hash, group))
            return True
        fhem.setFunctionActive(hash)
        if "id" in hash:
            self._forwarded[hash["id"]] = hash
        try:
            await worker.send(msg)
        except (ConnectionError, websockets.exceptions.ConnectionClosed):
            self._forwarded.pop(hash.get("id"), None)
            await self.binding.sendBackReturn(hash, "")
        return True

    async def _undefine_in_worker(self, device):
        worker = self.workers.get(device["group"])
        if worker is None or not worker.is_connected():
            return
        msg = dict(device["define"])
        msg["function"] = "Undefine"
        msg["id"] = next(_internal_ids)
        self._internal.add(msg["id"])
        try:
            await worker.send(json_dumps(msg))
        except (ConnectionError, websockets.exceptions.ConnectionClosed):
            self._internal.discard(msg["id"])

    # --- worker -> FHEM ---

    def from_worker(self, worker, message):
        try:
            msg = json_loads(message)
        except Exception:
            logger.error(f"fhempy worker '{worker.group}' sent invalid JSON")
            return
        if not isinstance(msg, dict):
            return
        if msg.get("msgtype") == "command" and "awaitId" in msg:
            worker.create_task(self._command(worker, msg))
            return
        if "finished" in msg and "id" in msg:
            msg_id = msg["id"]
            if msg_id in self._internal:
                self._internal.discard(msg_id)
                return
            forwarded = self._forwarded.pop(msg_id, None)
            if forwarded is not None:
                from .. import fhem_pythonbinding

                fhem_pythonbinding.id_received_timestamp.pop(msg_id, None)
                self.binding.msg_handling_completed(forwarded)
                fhem.setFunctionInactive(forwarded)
        worker.create_task(self.binding._send_reply(_as_text(message)))

    async def _command(self, worker, msg):
        worker_id = msg.pop("awaitId")
        name = msg.pop("NAME", None)
        msg.pop("msgtype", None)
        cmd = msg.pop("command", None)
        try:
            await fhem.waitForFunction(name)
            reply = await asyncio.wait_for(
                fhem.send_and_wait(name, cmd, msg or None), COMMAND_TIMEOUT
            )
            reply = dict(reply)
        except asyncio.TimeoutError:
            reply = {"error": 1, "errorText": "no response from FHEM", "result": ""}
        except ConnectionError:
            reply = {"error": 1, "errorText": "FHEM connection closed", "result": ""}
        reply["awaitId"] = worker_id
        try:
            await worker.send(json_dumps(reply))
        except (ConnectionError, websockets.exceptions.ConnectionClosed):
            pass

    # --- worker lifecycle ---

    async def worker_up(self, worker):
        """Define all devices of the worker, like FHEM does after connecting."""
        for device in list(self.devices.values()):
            if device["group"] != worker.group:
                continue
            if not await self._send_define(worker, device):
                return

    async def worker_down(self, worker):
        # FHEM doesn't get replies of this worker anymore
        for msg_id, hash in list(self._forwarded.items()):
            if self.devices.get(hash.get("NAME"), {}).get("group") == worker.group:
                self._forwarded.pop(msg_id, None)
                await self.binding.sendBackReturn(hash, "")
        if worker.stopping or self.binding.is_closed():
            return
        for name, device in list(self.devices.items()):
            if device["group"] != worker.group:
                continue
            await fhem.readingsSingleUpdate(
                {"NAME": name}, "state", "fhempy worker restarting", 1
            )

    def loop_blocked(self, module, duration):
        group = self.assigner.record_blocking(module, duration)
        if group is None or module in self._isolating:
            return
        self._isolating.add(module)
        task = asyncio.create_task(self._isolate(module, group))
        task.add_done_callback(lambda _t: self._isolating.discard(module))
        self.binding._background_tasks.add(task)
        task.add_done_callback(self.binding._background_tasks.discard)

    async def _isolate(self, module, group):
        """Move the running devices of module's family into the worker."""
        from .. import fhem_pythonbinding

        members = set(self.assigner.families().members(module))
        for member in members:
            self._type_group[member] = group
        for name, instance in list(fhem_pythonbinding.loadedModuleInstances.items()):
            dev_hash = getattr(instance, "hash", None)
            if dev_hash is None or dev_hash.get("FHEMPYTYPE") not in members:
                continue
            define = dict(dev_hash)
            define.update(
                {
                    "msgtype": "function",
                    "function": "Define",
                    "args": getattr(instance, "_defargs", dev_hash.get("args", [])),
                    "argsh": getattr(instance, "_defargsh", dev_hash.get("argsh", {})),
                }
            )
            await fhem_pythonbinding.undefine_local(name)
            self.devices[name] = {
                "group": group,
                "type": dev_hash["FHEMPYTYPE"],
                "define": define,
            }
            logger.info(f"{name} moved to fhempy worker '{group}'")
        if any(d["group"] == group for d in self.devices.values()):
            worker = self._worker(group)
            if worker.is_connected():
                await self.worker_up(worker)

    async def stop_all(self):
        workers = list(self.workers.values())
        if workers:
            await asyncio.gather(*(w.stop() for w in workers), return_exceptions=True)
            logger.info("All fhempy workers stopped")


def _not_connected_reply(hash, group):
    args = hash.get("args") or []
    if hash.get("function") == "Set" and len(args) > 1 and args[1] != "?":
        return f"fhempy worker '{group}' is starting, please try again"
    return ""


def _as_text(message):
    if isinstance(message, bytes):
        return message.decode("utf-8")
    return message
