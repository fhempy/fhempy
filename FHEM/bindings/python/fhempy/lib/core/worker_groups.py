"""Automatic assignment of fhempy modules to worker processes.

All modules run in the fhempy process ("core") as long as their requirements
fit together. A module whose requirements conflict with the modules already
running in the core (e.g. paho-mqtt 1.x and 2.x) gets a worker process with
its own virtual environment. A module which blocks the event loop again and
again gets a worker process with the core's environment, so it doesn't freeze
the other devices anymore.

Nothing has to be configured. The assignment is stored in
.fhempy/workers.json and checked again when the requirements of a module
change (fhempy update).

Modules which use other fhempy devices directly (e.g. tuya_cloud_device uses
its tuya_cloud setup device) have to run in the same process. Their
manifest.json declares this with "worker": {"with": ["tuya_cloud"]}. A module
which must stay in the core declares "worker": {"core": true}.
"""

import asyncio
import functools
import hashlib
import json
import logging
import os
import sys
import tempfile
import time
from importlib.metadata import PackageNotFoundError, distribution, version

from packaging.requirements import InvalidRequirement, Requirement

from .. import pkg_installer, utils

logger = logging.getLogger(__name__)

CORE = "core"
STATE_VERSION = 1

# conflicting requirements, the worker gets its own virtual environment
REASON_CONFLICT = "conflict"
# blocks the event loop, the worker uses the environment of the core
REASON_BLOCKING = "blocking"
# set by the user in workers.json, never changed by fhempy
REASON_MANUAL = "manual"

# a module is moved to a worker if it blocked the loop this often ...
BLOCKING_COUNT = 3
# ... for at least this long (s) ...
BLOCKING_MIN_DURATION = 1.0
# ... within this time (s)
BLOCKING_WINDOW = 3600

RESOLVE_TIMEOUT = 180

# used if the fhempy distribution metadata isn't available (e.g. tests)
CORE_PACKAGES = (
    "websockets",
    "orjson",
    "aiohttp",
    "aiofiles",
    "zeroconf",
    "ifaddr",
    "packaging",
    "requests",
    "pexpect",
    "markdown2",
    "pycryptodomex",
    "async-upnp-client",
    "importlib_metadata",
)


def workers_disabled():
    """FHEMPY_WORKERS=0 runs all modules in the fhempy process like before."""
    if os.environ.get("FHEMPY_WORKERS", "1").strip().lower() in ("0", "off", "no"):
        return True
    # workers are connected via unix sockets
    return os.name != "posix"


def state_path():
    return os.path.join(os.getcwd(), ".fhempy", "workers.json")


@functools.cache
def core_requirements():
    """Requirements of fhempy itself, every worker environment needs them."""
    try:
        requires = distribution("fhempy").requires or []
    except PackageNotFoundError:
        requires = None
    if requires:
        reqs = []
        for req in requires:
            try:
                parsed = Requirement(req)
            except InvalidRequirement:
                continue
            if parsed.marker is not None and "extra" in str(parsed.marker):
                continue
            reqs.append(req)
        return tuple(reqs)
    # not installed as package, take the installed versions
    reqs = []
    for name in CORE_PACKAGES:
        try:
            reqs.append(f"{name}=={version(name)}")
        except PackageNotFoundError:
            continue
    return tuple(reqs)


def _read_manifest(module):
    path = os.path.join(utils.get_fhempy_root(), module, "manifest.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def requirements_hash(reqs):
    return hashlib.sha256("\n".join(sorted(reqs)).encode("utf-8")).hexdigest()[:16]


class Families:
    """Modules which have to run in the same process."""

    def __init__(self, manifests):
        self._parent = {}
        self._core = set()
        for module, manifest in manifests.items():
            self._find(module)
            worker = manifest.get("worker") or {}
            if worker.get("core"):
                self._core.add(module)
            for other in worker.get("with", []):
                self._union(module, other)

    def _find(self, module):
        parent = self._parent.setdefault(module, module)
        if parent != module:
            parent = self._find(parent)
            self._parent[module] = parent
        return parent

    def _union(self, a, b):
        ra, rb = self._find(a), self._find(b)
        if ra == rb:
            return
        # the alphabetically first module names the family
        if rb < ra:
            ra, rb = rb, ra
        self._parent[rb] = ra

    def key(self, module):
        return self._find(module)

    def members(self, module):
        key = self.key(module)
        return sorted(m for m in self._parent if self._find(m) == key)

    def core_only(self, module):
        return any(m in self._core for m in self.members(module))


class GroupAssigner:
    """Decides in which process (CORE or a worker group) a module runs."""

    def __init__(self, path=None, manifests=None, resolver=None, deps_ok=None):
        self.path = path or state_path()
        self._manifests = manifests
        self._families = None
        # (requirements) -> (ok, conflict): ok True if the requirements can be
        # installed together, conflict True if they can't (not a network error)
        self._resolver = resolver or resolve_requirements
        self._deps_ok = deps_ok or _deps_installed
        self._locks = {}
        self.state = self._load()

    # --- state ---

    def _load(self):
        try:
            with open(self.path, "r") as f:
                state = json.load(f)
            if state.get("version") == STATE_VERSION:
                state.setdefault("families", {})
                state.setdefault("blocking", {})
                return state
        except FileNotFoundError:
            pass
        except (OSError, ValueError):
            logger.warning(f"{self.path} is invalid, workers are assigned again")
        return {"version": STATE_VERSION, "families": {}, "blocking": {}}

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.path))
            with os.fdopen(fd, "w") as f:
                json.dump(self.state, f, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        except OSError:
            logger.exception(f"Failed to write {self.path}")

    # --- manifests ---

    def manifests(self):
        if self._manifests is None:
            root = utils.get_fhempy_root()
            manifests = {}
            for entry in sorted(os.listdir(root)):
                if os.path.isfile(os.path.join(root, entry, "manifest.json")):
                    manifests[entry] = _read_manifest(entry)
            self._manifests = manifests
        return self._manifests

    async def load(self):
        """Read the manifests of all modules without blocking the loop."""
        if self._manifests is None:
            await utils.run_blocking(functools.partial(self.manifests))

    def families(self):
        if self._families is None:
            self._families = Families(self.manifests())
        return self._families

    def module_requirements(self, module):
        manifest = self.manifests().get(module)
        if manifest is None:
            manifest = _read_manifest(module)
        return [
            pkg_installer.platform_requirement(req)
            for req in manifest.get("requirements", [])
        ]

    def family_requirements(self, family_key):
        reqs = []
        for member in self.families().members(family_key):
            for req in self.module_requirements(member):
                if req not in reqs:
                    reqs.append(req)
        return reqs

    # --- queries ---

    def group_info(self, group):
        """{"venv": bool} of a worker group"""
        venv = any(
            entry.get("group") == group and entry.get("venv", False)
            for entry in self.state["families"].values()
        )
        return {"venv": venv}

    def families_in(self, group):
        return sorted(
            key
            for key, entry in self.state["families"].items()
            if entry.get("group") == group
        )

    def assigned_group(self, module):
        entry = self.state["families"].get(self.families().key(module))
        return entry.get("group") if entry else None

    # --- assignment ---

    async def group_for(self, module, core_modules=()):
        """The group in which module runs, CORE for the fhempy process.

        core_modules: module types which run in the core right now."""
        if workers_disabled():
            return CORE
        families = self.families()
        key = families.key(module)
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            return await self._group_for(key, core_modules)

    async def _group_for(self, key, core_modules):
        families = self.families()
        if families.core_only(key):
            return CORE
        reqs = self.family_requirements(key)
        req_hash = requirements_hash(reqs)
        entry = self.state["families"].get(key)
        if entry is not None:
            if entry.get("reason") in (REASON_MANUAL, REASON_BLOCKING):
                return entry["group"]
            if entry.get("requirements") == req_hash:
                return entry["group"]

        group, reason = await self._decide(key, reqs, core_modules)
        new_entry = {"group": group, "requirements": req_hash}
        if group != CORE:
            new_entry.update({"reason": reason, "venv": True})
        if entry != new_entry:
            if group != CORE:
                logger.warning(
                    f"{key} runs in its own fhempy worker '{group}', "
                    "its requirements conflict with other modules"
                )
            elif entry is not None and entry.get("group") != CORE:
                logger.info(f"{key} runs in the fhempy process again")
            self.state["families"][key] = new_entry
            self.save()
        return group

    async def _decide(self, key, reqs, core_modules):
        if not reqs:
            return CORE, None
        if await self._deps_ok(reqs):
            # already installed, nothing changes in the environment of the core
            return CORE, None
        if pkg_installer.find_uv() is None:
            # without uv no check and no own environment, like before
            return CORE, None

        core_reqs = list(core_requirements())
        families = self.families()
        core_keys = {families.key(m) for m in core_modules}
        core_keys.update(
            k for k, e in self.state["families"].items() if e.get("group") == CORE
        )
        core_keys.discard(key)
        for other in sorted(core_keys):
            core_reqs += self.family_requirements(other)
        ok, conflict = await self._resolver(core_reqs + reqs)
        if ok or not conflict:
            # also if the check failed (e.g. no network): install as before
            return CORE, None

        # try the existing workers with their own environment
        groups = sorted(
            {
                e["group"]
                for k, e in self.state["families"].items()
                if e.get("group") != CORE and e.get("venv") and k != key
            }
        )
        for group in groups:
            group_reqs = list(core_requirements())
            for other in self.families_in(group):
                if other != key:
                    group_reqs += self.family_requirements(other)
            ok, _ = await self._resolver(group_reqs + reqs)
            if ok:
                return group, REASON_CONFLICT
        return key, REASON_CONFLICT

    def record_blocking(self, module, duration, now=None):
        """Count a blockade of the event loop by module. Returns the new
        worker group if module has to leave the core, None otherwise."""
        if workers_disabled() or module is None:
            return None
        if duration < BLOCKING_MIN_DURATION:
            return None
        families = self.families()
        if module not in self.manifests() or families.core_only(module):
            return None
        key = families.key(module)
        entry = self.state["families"].get(key)
        if entry is not None and entry.get("group") != CORE:
            # already in a worker
            return None
        now = time.time() if now is None else now
        times = [
            t for t in self.state["blocking"].get(key, []) if now - t < BLOCKING_WINDOW
        ]
        times.append(now)
        self.state["blocking"][key] = times
        if len(times) < BLOCKING_COUNT:
            self.save()
            return None
        self.state["blocking"].pop(key, None)
        self.state["families"][key] = {
            "group": key,
            "reason": REASON_BLOCKING,
            "venv": False,
            "requirements": requirements_hash(self.family_requirements(key)),
        }
        self.save()
        logger.warning(
            f"{key} blocked fhempy {BLOCKING_COUNT} times, it runs in its own "
            "fhempy worker from now on"
        )
        return key


async def _deps_installed(reqs):
    def check():
        return all(pkg_installer.is_installed(req) for req in reqs)

    return await utils.run_blocking(functools.partial(check))


async def resolve_requirements(reqs):
    """Check with uv if reqs can be installed together.

    Returns (ok, conflict): conflict is True if uv found no solution, False if
    the check itself failed (e.g. no network)."""
    uv = pkg_installer.find_uv()
    if uv is None:
        return False, False
    fd, path = tempfile.mkstemp(prefix="fhempy_resolve_", suffix=".txt")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(reqs) + "\n")
        args = [
            uv,
            "pip",
            "compile",
            "--quiet",
            "--no-header",
            "--python",
            sys.executable,
            path,
        ]
        overrides = pkg_installer.uv_overrides_file()
        if overrides is not None:
            args += ["--override", overrides]
        args += pkg_installer.uv_index_args()
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), RESOLVE_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            logger.warning("Checking module requirements took too long")
            return False, False
        if proc.returncode == 0:
            return True, False
        error = stderr.decode("utf-8", "replace")
        if "No solution found" in error:
            logger.info("Conflicting requirements:\n" + error.strip())
            return False, True
        logger.warning("Failed to check module requirements: " + error.strip())
        return False, False
    except OSError:
        logger.exception("Failed to check module requirements")
        return False, False
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
