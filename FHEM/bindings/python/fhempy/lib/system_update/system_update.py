"""Keeps the operating system (Raspberry Pi OS, Debian, Ubuntu) up to date.

Security updates are installed automatically every night, all other updates
are listed and installed with set update. So that an update doesn't break
FHEM:
- critical packages (kernel, firmware, python3, nodejs, fhem) are held back
  and only installed with set update_all
- before: enough free space, no interrupted installation, no under-voltage,
  github_backup runs, the list of installed packages is saved
- apt never removes packages, keeps changed config files and never upgrades
  to a new Debian release; it runs outside of fhempy, a restart of FHEM or
  fhempy doesn't interrupt it
- after: FHEM answers, fhempy peers are connected again, no service failed;
  on problems the push module sends a notification
- a reboot happens only if needed and only at reboot_time
"""

import asyncio
import fnmatch
import functools
import html
import json
import os
import pwd
import re
import shlex
import shutil
import time
from datetime import datetime

from .. import fhem, generic, utils
from . import helper

ICON = "system_fhem_update"
TOOL_DIRS = ("/usr/bin", "/bin", "/usr/sbin", "/sbin")
DEFAULT_HOLD = ",".join(
    [
        "linux-*",
        "raspberrypi-kernel*",
        "raspberrypi-bootloader*",
        "raspi-firmware",
        "rpi-eeprom*",
        "firmware-*",
        "initramfs-tools*",
        "python3*",
        "libpython3*",
        "nodejs",
        "fhem",
    ]
)
# packages which only take effect after a reboot
REBOOT_PACKAGES = (
    "linux-image*",
    "raspberrypi-kernel*",
    "raspberrypi-bootloader*",
    "raspi-firmware",
    "libc6",
    "systemd",
    "dbus",
)
REBOOT_REQUIRED_FILE = "/run/reboot-required"
MIN_BOOT_FREE_MB = 30
SCHEDULE_INTERVAL = 30
# seconds after the update until the health check, services restart meanwhile
HEALTH_DELAY = 60
HEALTH_RETRIES = 3
REBOOT_CHECK_DELAY = 180
# seconds an update may wait in "queued" until it counts as not started
QUEUED_TIMEOUT = 120
POLL_INTERVAL = 10
REFRESH_TIMEOUT = 900
KEEP_FILES = 10
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SIM_INST = re.compile(r"^Inst (\S+) \[(\S+)\] \((\S+) ([^)]*)\)")


def is_root():
    return os.geteuid() == 0


def current_user():
    try:
        return pwd.getpwuid(os.geteuid()).pw_name
    except KeyError:
        return str(os.geteuid())


def tool(name):
    """absolute path of a system program, fhempy's PATH isn't used"""
    for directory in TOOL_DIRS:
        path = os.path.join(directory, name)
        if os.access(path, os.X_OK):
            return path
    return None


async def run_command(args, timeout=60):
    """(exit code, output) of a program, 127 if it doesn't exist"""
    if args[0] is None:
        return 127, "program not found"
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={"PATH": ":".join(TOOL_DIRS), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
        )
    except OSError as err:
        return 127, str(err)
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, f"{os.path.basename(args[0])} did not finish within {timeout}s"
    return proc.returncode, out.decode("utf-8", "replace")


def last_line(text):
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return lines[-1] if lines else ""


def parse_simulation(text):
    """updates of installed packages in the output of apt-get -s upgrade"""
    updates = []
    for line in text.splitlines():
        match = SIM_INST.match(line)
        if match:
            name, old, new, origins = match.groups()
            updates.append(
                {
                    "package": name,
                    "installed": old,
                    "new": new,
                    "security": "-security" in origins.lower(),
                }
            )
    return updates


def matches(package, patterns):
    return any(fnmatch.fnmatchcase(package, p) for p in patterns)


def patterns(text):
    return [p.strip() for p in str(text or "").split(",") if p.strip()]


def select_packages(updates, mode, hold):
    """packages to install: security (not held), all (not held), everything"""
    selected = []
    for update in updates:
        if mode != "everything" and matches(update["package"], hold):
            continue
        if mode == "security" and not update["security"]:
            continue
        selected.append(update["package"])
    return selected


def needs_reboot(packages):
    return any(matches(p, REBOOT_PACKAGES) for p in packages)


def boot_time():
    try:
        with open("/proc/stat", encoding="utf-8") as f:
            for line in f:
                if line.startswith("btime "):
                    return int(line.split()[1])
    except OSError:
        pass
    return 0


def under_voltage(output):
    """vcgencmd get_throttled: bit 0 = under-voltage right now"""
    match = re.search(r"throttled=(0x[0-9a-fA-F]+)", output)
    return bool(match) and int(match.group(1), 16) & 1 == 1


def free_mb(path):
    return shutil.disk_usage(path).free // (1024 * 1024)


def boot_partition():
    for path in ("/boot/firmware", "/boot"):
        if os.path.ismount(path):
            return path
    return None


def valid_time(value):
    """HH:MM or empty (off)"""
    value = str(value or "").strip()
    if value in ("", "off"):
        return None
    return datetime.strptime(value, "%H:%M")


def data_directory():
    return os.path.join(os.getcwd(), ".fhempy", "system_update")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)


def keep_newest(directory, prefix, count=KEEP_FILES):
    files = sorted(f for f in os.listdir(directory) if f.startswith(prefix))
    for name in files[:-count]:
        os.remove(os.path.join(directory, name))


def save_file(prefix, content):
    """writes content to .fhempy/system_update/<prefix><date>.txt"""
    directory = data_directory()
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(
        directory, prefix + datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    keep_newest(directory, prefix)
    return path


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except PermissionError:
        # the helper runs as root
        return True
    except (OSError, ValueError, TypeError):
        return False
    return True


def helper_status():
    return read_json(helper.STATUS_FILE)


def upgrade_finished(status, since):
    """None while running, else the status of the upgrade"""
    if status.get("running"):
        if status.get("pid"):
            if pid_alive(status["pid"]):
                return None
            return dict(status, running=False, exit_code=-1, killed=True)
        if time.time() - since < QUEUED_TIMEOUT:
            return None
        return dict(status, running=False, exit_code=-1, not_started=True)
    if (status.get("started") or 0) < since - 5:
        # status of an older update, this one never started
        if time.time() - since < QUEUED_TIMEOUT:
            return None
        return dict(status, exit_code=-1, not_started=True)
    return status


def read_log():
    try:
        with open(helper.LOG_FILE, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


class system_update(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._lock = asyncio.Lock()
        self._last_run = {}
        self.updates = []
        self.update_state = "up to date"
        self.helper_problem = "not checked yet"
        self.user = current_user()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_attr_config(
            {
                "auto_update": {
                    "default": "security",
                    "options": "security,all,off",
                    "help": "What is installed automatically at update_time:<br>"
                    "security: only security updates (default)<br>"
                    "all: all updates except hold_packages<br>"
                    "off: nothing, the updates are only listed",
                },
                "update_time": {
                    "default": "03:15",
                    "format": valid_time,
                    "help": "Daily check for updates and automatic update, "
                    "HH:MM, default 03:15.",
                },
                "reboot_time": {
                    "default": "",
                    "format": valid_time,
                    "help": "Reboot at this time (HH:MM) when an update needs "
                    "it, e.g. 04:30. Empty (default): never reboot "
                    "automatically, only notify.",
                },
                "hold_packages": {
                    "default": DEFAULT_HOLD,
                    "help": "Critical packages, comma separated, * allowed. "
                    "They are only installed with set update_all.<br>Default: "
                    + DEFAULT_HOLD.replace(",", ", "),
                },
                "backup": {
                    "default": "required",
                    "options": "required,optional,off",
                    "help": "github_backup before each update. required "
                    "(default): no update if the backup fails. optional: "
                    "update anyway. Without github_backup device no backup.",
                },
                "min_free_mb": {
                    "default": 500,
                    "format": "int",
                    "help": "Minimum free space on / in MB for an update, "
                    "default 500.",
                },
                "notify": {
                    "default": "problems",
                    "options": "problems,all,off",
                    "help": "Push notification with the push module: problems "
                    "(default) or all (also after each update and when "
                    "updates wait for you).",
                },
                "notify_device": {
                    "default": "",
                    "help": "push device for notifications, default: all "
                    "push devices.",
                },
            }
        )
        await self.set_set_config(
            {
                "check": {"help": "Check for updates now, nothing is installed."},
                "update": {"help": "Install all updates now, except hold_packages."},
                "update_all": {
                    "help": "Install all updates now, also the critical "
                    "hold_packages (kernel, firmware, python3...)."
                },
                "repair": {
                    "help": "Finish an interrupted installation "
                    "(dpkg --configure -a)."
                },
                "reboot": {"help": "Reboot the computer now."},
            }
        )
        await self.set_icon(ICON)
        self.create_async_task(self.start())

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.detail_html() + str(detail or "")

    # --- readings and state file ---

    async def set_state(self, state, **readings):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state)
        for name, value in readings.items():
            await fhem.readingsBulkUpdate(self.hash, name, value)
        await fhem.readingsEndUpdate(self.hash, 1)

    def state_file(self):
        return os.path.join(data_directory(), self.hash["NAME"] + ".json")

    async def load_state(self):
        return await utils.run_blocking(functools.partial(read_json, self.state_file()))

    async def save_state(self, state):
        await utils.run_blocking(
            functools.partial(write_json, self.state_file(), state)
        )

    # --- helper ---

    @staticmethod
    def helper_source():
        return os.path.abspath(helper.__file__)

    def setup_command(self):
        return (
            f"sudo python3 {shlex.quote(self.helper_source())} install "
            f"{shlex.quote(self.user)}"
        )

    def sudoers_line(self):
        return f"{self.user} ALL=(root) NOPASSWD: {helper.INSTALL_PATH}"

    def helper_command(self, *args):
        if is_root():
            return [tool("python3"), "-I", self.helper_source(), *args]
        return [tool("sudo"), "-n", helper.INSTALL_PATH, *args]

    async def run_helper(self, *args, timeout=60):
        return await run_command(self.helper_command(*args), timeout)

    async def check_helper(self):
        """True if the helper can be used, else the readings explain why"""
        installed = await utils.run_blocking(
            functools.partial(os.path.exists, helper.INSTALL_PATH)
        )
        if not is_root() and not installed:
            self.helper_problem = "helper not installed"
        elif not is_root() and tool("sudo") is None:
            self.helper_problem = "sudo is not installed"
        else:
            code, out = await self.run_helper("version")
            if code != 0:
                self.helper_problem = "no sudo permission: " + last_line(out)
            elif not out.strip().isdigit() or int(out) < helper.HELPER_VERSION:
                self.helper_problem = "helper is outdated"
            else:
                self.helper_problem = ""
        if self.helper_problem:
            await self.set_state(
                "setup needed: run the command shown on the device page",
                setup_problem=self.helper_problem,
            )
            return False
        await fhem.CommandDeleteReading(self.hash, f"{self.hash['NAME']} setup_problem")
        return True

    # --- startup and schedule ---

    async def start(self):
        if await self.check_helper():
            state = await self.load_state()
            if state.get("pending"):
                async with self._lock:
                    await self.finish_update(state["pending"])
            elif self.helper_status_running():
                # the state file is gone, follow the update anyway
                status = helper_status()
                async with self._lock:
                    await self.finish_update(
                        {
                            "packages": status.get("packages") or [],
                            "started": status.get("started") or time.time(),
                        }
                    )
            else:
                await self.list_updates()
            self.create_async_task(self.after_reboot())
        while True:
            await self.schedule(datetime.now())
            await asyncio.sleep(SCHEDULE_INTERVAL)

    @staticmethod
    def helper_status_running():
        status = helper_status()
        return bool(status.get("running") and pid_alive(status.get("pid")))

    def due(self, key, at, now):
        if at is None or (now.hour, now.minute) != (at.hour, at.minute):
            return False
        if self._last_run.get(key) == now.date():
            return False
        self._last_run[key] = now.date()
        return True

    async def schedule(self, now):
        if self.due("update", self._attr_update_time, now):
            self.create_async_task(self.daily())
        if self.due("reboot", self._attr_reboot_time, now):
            if await self.reboot_required() and not self._lock.locked():
                await self.reboot("Rebooting for the last update (reboot_time)")

    async def daily(self):
        if self._attr_auto_update == "off":
            await self.check(refresh=True)
        else:
            await self.update(self._attr_auto_update)
        waiting = [u["package"] for u in self.updates]
        if waiting and self._attr_notify == "all":
            await self.notify(
                f"{len(waiting)} updates wait for you: {', '.join(waiting[:10])}"
            )

    # --- set commands ---

    async def set_check(self, hash, params):
        self.create_async_task(self.check(refresh=True))

    async def set_update(self, hash, params):
        self.create_async_task(self.update("all"))

    async def set_update_all(self, hash, params):
        self.create_async_task(self.update("everything"))

    async def set_repair(self, hash, params):
        self.create_async_task(self.repair())

    async def set_reboot(self, hash, params):
        self.create_async_task(self.reboot("Rebooting (set reboot)"))

    # --- check ---

    async def check(self, refresh):
        if self._lock.locked():
            return
        async with self._lock:
            if await self.check_helper():
                await self.refresh_and_list(refresh)

    async def refresh_and_list(self, refresh):
        if refresh:
            await self.set_state("checking")
            code, out = await self.run_helper("refresh", timeout=REFRESH_TIMEOUT)
            if code != 0:
                await self.failed("apt-get update failed: " + last_line(out))
                return False
        return await self.list_updates()

    async def list_updates(self):
        code, out = await run_command(
            [tool("apt-get"), "-s", "-o", "Debug::NoLocking=1", *helper.UPGRADE[3:]]
        )
        if code != 0:
            await self.failed("can't list updates: " + last_line(out))
            return False
        self.updates = parse_simulation(out)
        hold = patterns(self._attr_hold_packages)
        held = [u["package"] for u in self.updates if matches(u["package"], hold)]
        security = [u for u in self.updates if u["security"]]
        if not self.updates:
            state = "up to date"
        else:
            state = f"{len(self.updates)} updates"
            if security:
                state += f" ({len(security)} security)"
        self.update_state = state
        await self.set_state(
            state,
            updates_available=len(self.updates),
            updates_security=len(security),
            updates_held=", ".join(held) or "-",
            updates=", ".join(u["package"] for u in self.updates) or "-",
            last_check=datetime.now().strftime(TIME_FORMAT),
        )
        return True

    async def failed(self, problem):
        self.logger.error(problem)
        await self.set_state("failed: " + problem, last_error=problem)
        await self.notify(problem, problem=True)

    # --- update ---

    async def update(self, mode):
        if self._lock.locked():
            return
        async with self._lock:
            if not await self.check_helper():
                return
            if not await self.refresh_and_list(refresh=True):
                return
            packages = select_packages(
                self.updates, mode, patterns(self._attr_hold_packages)
            )
            if not packages:
                return
            problem = await self.precheck(packages)
            if problem:
                await self.failed("update skipped: " + problem)
                return
            if not await self.backup():
                return
            installed = await run_command(
                [tool("dpkg-query"), "-W", "-f=${Package}\t${Version}\n"]
            )
            await utils.run_blocking(
                functools.partial(save_file, "packages-", installed[1])
            )
            pending = {
                "packages": packages,
                "started": time.time(),
                "before": await self.health_snapshot(),
            }
            await self.save_state({**await self.load_state(), "pending": pending})
            await self.set_state(f"updating {len(packages)} packages")
            code, out = await self.run_helper("upgrade", *packages, timeout=7200)
            if code != 0:
                await self.save_state(
                    {
                        k: v
                        for k, v in (await self.load_state()).items()
                        if k != "pending"
                    }
                )
                await self.failed("update could not start: " + last_line(out))
                return
            await self.finish_update(pending)

    async def precheck(self, packages):
        """None or why updating now is a bad idea"""
        free = await utils.run_blocking(functools.partial(free_mb, "/"))
        if free < self._attr_min_free_mb:
            return f"only {free} MB free on / (min_free_mb {self._attr_min_free_mb})"
        boot = boot_partition()
        if boot and needs_reboot(packages):
            free = await utils.run_blocking(functools.partial(free_mb, boot))
            if free < MIN_BOOT_FREE_MB:
                return f"only {free} MB free on {boot}"
        code, out = await run_command([tool("dpkg"), "--audit"])
        if out.strip():
            return "an earlier installation was interrupted, use set repair"
        if tool("vcgencmd"):
            code, out = await run_command([tool("vcgencmd"), "get_throttled"])
            if code == 0 and under_voltage(out):
                return (
                    "under-voltage, a weak power supply can damage the SD card "
                    "during an update"
                )
        return None

    def local_devices(self, fhempy_type):
        from .. import fhem_pythonbinding

        return [
            inst
            for inst in list(fhem_pythonbinding.loadedModuleInstances.values())
            if getattr(inst, "hash", {}).get("FHEMPYTYPE") == fhempy_type
            and inst is not self
        ]

    async def backup(self):
        """github_backup before the update, False if the update must stop"""
        if self._attr_backup == "off":
            return True
        devices = self.local_devices("github_backup")
        if not devices:
            await fhem.readingsSingleUpdate(self.hash, "backup", "no github_backup", 1)
            return True
        await self.set_state("backup")
        errors = []
        for device in devices:
            error = await device.backup_and_wait()
            if error:
                errors.append(f"{device.hash['NAME']}: {error}")
        result = "; ".join(errors) or "ok"
        await fhem.readingsSingleUpdate(self.hash, "backup", result, 1)
        if errors and self._attr_backup == "required":
            await self.failed("update skipped, backup failed: " + result)
            return False
        return True

    async def wait_for_upgrade(self, since):
        while True:
            status = await utils.run_blocking(functools.partial(helper_status))
            result = upgrade_finished(status, since)
            if result is not None:
                return result
            await asyncio.sleep(POLL_INTERVAL)

    async def finish_update(self, pending):
        packages = pending["packages"]
        await self.set_state(f"updating {len(packages)} packages")
        status = await self.wait_for_upgrade(pending["started"])
        log = await utils.run_blocking(functools.partial(read_log))
        await utils.run_blocking(functools.partial(save_file, "update-", log))
        await self.list_updates()
        # apt keeps an update back if a held package depends on it
        remaining = {u["package"] for u in self.updates}
        updated = [p for p in packages if p not in remaining]
        kept_back = [p for p in packages if p in remaining]
        state = await self.load_state()
        state.pop("pending", None)
        if needs_reboot(updated):
            state["reboot_required_since"] = time.time()
        await self.save_state(state)
        await self.set_state(
            self.update_state,
            last_update=datetime.now().strftime(TIME_FORMAT),
            packages_updated=", ".join(updated) or "-",
            packages_kept_back=", ".join(kept_back) or "-",
        )
        if status.get("exit_code") != 0:
            reason = last_line(log) or "update was interrupted"
            await self.failed(
                f"update failed: {reason}. Use set repair if it was interrupted."
            )
            return
        await self.report_update(pending, updated)

    async def report_update(self, pending, updated):
        await self.set_state("health check")
        await asyncio.sleep(HEALTH_DELAY)
        problems = await self.health_problems(pending.get("before") or {})
        reboot = await self.reboot_required()
        await self.set_state(
            (
                "problem after update: " + "; ".join(problems)
                if problems
                else self.update_state
            ),
            health="; ".join(problems) or "ok",
            reboot_required="yes" if reboot else "no",
        )
        text = f"{len(updated)} packages updated"
        if reboot:
            text += ", reboot needed" + (
                "" if self._attr_reboot_time else " (set reboot or attr reboot_time)"
            )
        if problems:
            await self.notify(f"{text}, but: " + "; ".join(problems), problem=True)
        else:
            await self.notify(text, important=reboot and not self._attr_reboot_time)

    # --- health check ---

    async def failed_units(self):
        code, out = await run_command(
            [tool("systemctl"), "--failed", "--no-legend", "--plain", "--no-pager"]
        )
        if code != 0:
            return []
        return sorted({line.split()[0] for line in out.splitlines() if line.strip()})

    async def peers(self):
        """state of the BindingsIo devices (connections to fhempy)"""
        result = await asyncio.wait_for(
            fhem.sendCommandHash(
                self.hash,
                "join(' ', map { $_ . '=' . ReadingsVal($_, 'state', '') }"
                " devspec2array('TYPE=BindingsIo'))",
            ),
            30,
        )
        return dict(
            part.split("=", 1) for part in str(result or "").split() if "=" in part
        )

    async def health_snapshot(self):
        try:
            peers = await self.peers()
        except (asyncio.TimeoutError, OSError):
            peers = {}
        return {"failed_units": await self.failed_units(), "peers": peers}

    async def health_problems(self, before):
        """problems which came with the update, retried while services
        are still starting"""
        problems = []
        for attempt in range(HEALTH_RETRIES):
            if attempt:
                await asyncio.sleep(HEALTH_DELAY)
            problems = []
            try:
                peers = await self.peers()
            except (asyncio.TimeoutError, OSError):
                peers = None
                problems.append("FHEM does not answer")
            if peers is not None:
                lost = [
                    name
                    for name, state in (before.get("peers") or {}).items()
                    if state == "opened" and peers.get(name) != "opened"
                ]
                if lost:
                    problems.append("fhempy not connected: " + ", ".join(lost))
            new_failed = sorted(
                set(await self.failed_units()) - set(before.get("failed_units") or [])
            )
            if new_failed:
                problems.append("failed services: " + ", ".join(new_failed))
            if not problems:
                break
        return problems

    # --- reboot ---

    async def reboot_required(self):
        if await utils.run_blocking(
            functools.partial(os.path.exists, REBOOT_REQUIRED_FILE)
        ):
            return True
        since = (await self.load_state()).get("reboot_required_since") or 0
        return since > boot_time()

    async def reboot(self, reason):
        if not await self.check_helper():
            return
        state = await self.load_state()
        state["reboot"] = {"time": time.time(), "before": await self.health_snapshot()}
        await self.save_state(state)
        await self.set_state("rebooting")
        self.logger.warning(reason)
        code, out = await self.run_helper("reboot")
        if code != 0:
            await self.failed("reboot failed: " + last_line(out))

    async def after_reboot(self):
        """health check after a reboot done by this module"""
        state = await self.load_state()
        reboot = state.get("reboot")
        if not reboot or reboot.get("time", 0) > boot_time():
            return
        await asyncio.sleep(REBOOT_CHECK_DELAY)
        state = await self.load_state()
        state.pop("reboot", None)
        state.pop("reboot_required_since", None)
        await self.save_state(state)
        problems = await self.health_problems(reboot.get("before") or {})
        await self.set_state(
            self.update_state,
            last_reboot=datetime.now().strftime(TIME_FORMAT),
            reboot_required="no",
            health="; ".join(problems) or "ok",
        )
        if problems:
            await self.notify("After the reboot: " + "; ".join(problems), problem=True)
        elif self._attr_notify == "all":
            await self.notify("Reboot finished, everything runs")

    # --- repair ---

    async def repair(self):
        if self._lock.locked():
            return
        async with self._lock:
            if not await self.check_helper():
                return
            await self.set_state("repairing")
            code, out = await self.run_helper("repair", timeout=3600)
            if code != 0:
                await self.failed("repair failed: " + last_line(out))
                return
            await self.list_updates()

    # --- notification ---

    async def notify(self, text, problem=False, important=False):
        """problem and important messages are sent with notify problems,
        the others only with notify all"""
        if self._attr_notify == "off" or (
            self._attr_notify == "problems" and not (problem or important)
        ):
            return
        title = f"{self.hash['NAME']}: " + ("problem" if problem else "update")
        names = patterns(self._attr_notify_device)
        local = [
            d
            for d in self.local_devices("push")
            if not names or d.hash["NAME"] in names
        ]
        try:
            # push devices of this fhempy work even if FHEM doesn't answer
            for device in local:
                await device.send_command([text], {"title": title})
            if not local:
                await fhem.sendCommandHash(
                    self.hash,
                    "foreach my $d (devspec2array('FHEMPYTYPE=push')) {"
                    f" next if ({fhem.perlString(','.join(names))} ne '' &&"
                    f" index(',' . {fhem.perlString(','.join(names))} . ',',"
                    " ',' . $d . ',') < 0);"
                    " AnalyzeCommand(undef, 'set ' . $d . ' message ' ."
                    f" {fhem.perlString(f'{text} | {title}')}); }}",
                )
        except Exception:
            self.logger.exception("Notification failed")

    # --- FHEMWEB ---

    def detail_html(self):
        if self.helper_problem and self.helper_problem != "not checked yet":
            return (
                '<div style="border:1px solid #c80;padding:8px;margin:8px 0">'
                f"<b>One-time setup needed</b> ({html.escape(self.helper_problem)})"
                "<br>fhempy needs root rights for apt. Log in to this computer "
                "(e.g. with ssh) and run once:<br><code style='user-select:all'>"
                f"{html.escape(self.setup_command())}</code><br>"
                f"This installs {helper.INSTALL_PATH} and the sudoers line "
                f"<code>{html.escape(self.sudoers_line())}</code>. "
                "fhempy can then only run this helper as root, not apt with "
                "any options. Afterwards: <code>set "
                f"{html.escape(self.hash['NAME'])} check</code></div>"
            )
        if not self.updates:
            return ""
        hold = patterns(self._attr_hold_packages)
        rows = "".join(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(u["package"]),
                html.escape(u["installed"]),
                html.escape(u["new"]),
                (
                    "held (update_all)"
                    if matches(u["package"], hold)
                    else ("security" if u["security"] else "")
                ),
            )
            for u in self.updates
        )
        return (
            "<div style='margin:8px 0'><b>Available updates</b>"
            "<table class='block wide'><tr><th>Package</th><th>Installed</th>"
            f"<th>New</th><th></th></tr>{rows}</table></div>"
        )
