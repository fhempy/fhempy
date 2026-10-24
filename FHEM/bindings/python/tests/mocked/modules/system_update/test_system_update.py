import asyncio
import json
import logging
import time
from datetime import datetime

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib import fhem_pythonbinding
from fhempy.lib.system_update import helper, system_update

logger = logging.getLogger(__name__)

NAME = "sysupdate"

DEBIAN = """NOTE: This is only a simulation!
Inst libssl3 [3.0.11-1~deb12u1] (3.0.11-1~deb12u2 Debian-Security:12/stable-security [arm64])
Inst vim [2:9.0.1378-2] (2:9.0.1378-2+deb12u1 Debian:12.7/stable [arm64])
Inst linux-image-rpi-v8 [1:6.6.31-1+rpt1] (1:6.6.51-1+rpt3 Raspberry Pi Foundation:stable [arm64])
Inst linux-image-6.6.51+rpt-rpi-v8 (1:6.6.51-1+rpt3 Raspberry Pi Foundation:stable [arm64])
Conf libssl3 (3.0.11-1~deb12u2 Debian-Security:12/stable-security [arm64])
"""
UBUNTU = (
    "Inst zlib1g-dev [1:1.3.dfsg-3.1ubuntu2.2] (1:1.3.dfsg-3.1ubuntu2.3 "
    "Ubuntu:24.04/noble-updates, Ubuntu:24.04/noble-security [amd64]) []\n"
)


def upgrades(mod):
    """upgrade calls of the helper, not the simulations"""
    return [c for c in mod.system.calls if "upgrade" in c and "-s" not in c]


def readings():
    return mock_fhem.readings.get(NAME, {})


async def wait_for(condition, timeout=10):
    for _ in range(int(timeout * 50)):
        if condition():
            return
        await asyncio.sleep(0.02)
    raise AssertionError(f"condition not reached, readings: {readings()}")


def test_parse_simulation():
    updates = system_update.parse_simulation(DEBIAN)
    assert [u["package"] for u in updates] == ["libssl3", "vim", "linux-image-rpi-v8"]
    assert updates[0] == {
        "package": "libssl3",
        "installed": "3.0.11-1~deb12u1",
        "new": "3.0.11-1~deb12u2",
        "security": True,
    }
    assert not updates[1]["security"]
    ubuntu = system_update.parse_simulation(UBUNTU)
    assert ubuntu[0]["package"] == "zlib1g-dev" and ubuntu[0]["security"]
    # the helper finds the same packages
    assert [m.group(1) for m in map(helper.INST.match, DEBIAN.splitlines()) if m] == [
        "libssl3",
        "vim",
        "linux-image-rpi-v8",
    ]


def test_select_packages():
    updates = system_update.parse_simulation(DEBIAN)
    hold = system_update.patterns(system_update.DEFAULT_HOLD)
    assert system_update.select_packages(updates, "security", hold) == ["libssl3"]
    assert system_update.select_packages(updates, "all", hold) == ["libssl3", "vim"]
    assert system_update.select_packages(updates, "everything", hold) == [
        "libssl3",
        "vim",
        "linux-image-rpi-v8",
    ]
    assert system_update.needs_reboot(["linux-image-rpi-v8"])
    assert not system_update.needs_reboot(["vim", "libssl3"])


def test_helpers():
    assert system_update.under_voltage("throttled=0x50005")
    assert not system_update.under_voltage("throttled=0x50000")
    assert not system_update.under_voltage("")
    assert system_update.valid_time("") is None
    assert system_update.valid_time("04:30").hour == 4
    with pytest.raises(ValueError):
        system_update.valid_time("25:99")
    assert helper.PACKAGE.match("libstdc++6:arm64")
    for bad in ("a;b", "-o", "x y", "$(id)", ""):
        assert not helper.PACKAGE.match(bad)


def test_upgrade_finished(monkeypatch):
    now = time.time()
    monkeypatch.setattr(system_update, "pid_alive", lambda pid: pid == 1)
    running = {"running": True, "pid": 1, "started": now}
    assert system_update.upgrade_finished(running, now) is None
    killed = system_update.upgrade_finished(dict(running, pid=2), now)
    assert killed["exit_code"] == -1
    assert system_update.upgrade_finished({"running": True}, now) is None
    old = {"running": False, "exit_code": 0, "started": now - 3600}
    assert system_update.upgrade_finished(old, now) is None
    assert system_update.upgrade_finished(old, now - 600)["not_started"]
    done = {"running": False, "exit_code": 0, "started": now + 1}
    assert system_update.upgrade_finished(done, now) == done


class FakeSystem:
    """apt, dpkg, systemctl and the helper"""

    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.simulation = DEBIAN
        self.after_upgrade = (
            "Inst linux-image-rpi-v8 [1:6.6.31-1+rpt1] (1:6.6.51-1+rpt3 "
            "Raspberry Pi Foundation:stable [arm64])\n"
        )
        self.audit = ""
        self.throttled = "throttled=0x0"
        self.failed_units = ""
        self.upgrade_code = 0
        self.helper_version = str(helper.HELPER_VERSION)
        self.calls = []

    async def run(self, args, timeout=60):
        args = [str(a) for a in args]
        self.calls.append(args)
        name = args[0].rsplit("/", 1)[-1]
        if helper.INSTALL_PATH in args:
            return self.run_helper(args[args.index(helper.INSTALL_PATH) + 1 :])
        if name == "apt-get":
            return 0, self.simulation
        if name == "dpkg":
            return 0, self.audit
        if name == "dpkg-query":
            return 0, "vim\t2:9.0.1378-2\n"
        if name == "systemctl":
            return 0, self.failed_units
        if name == "vcgencmd":
            return 0, self.throttled
        return 127, "program not found"

    def run_helper(self, args):
        if args[0] == "version":
            return 0, self.helper_version + "\n"
        if args[0] == "refresh":
            return 0, "Reading package lists..."
        if args[0] == "upgrade":
            packages = args[1:]
            (self.tmp_path / "upgrade.log").write_text("Setting up vim ...\nE: boom\n")
            status = {
                "running": False,
                "pid": 4711,
                "packages": packages,
                "started": time.time(),
                "finished": time.time(),
                "exit_code": self.upgrade_code,
            }
            (self.tmp_path / "status.json").write_text(json.dumps(status))
            if self.upgrade_code == 0:
                self.simulation = self.after_upgrade
            return 0, ""
        if args[0] in ("repair", "reboot"):
            return 0, ""
        return 1, "unknown"


class FakeDevice:
    def __init__(self, name, fhempy_type, error=None):
        self.hash = {"NAME": name, "FHEMPYTYPE": fhempy_type}
        self.error = error
        self.sent = []
        self.backups = 0

    async def send_command(self, args, argsh):
        self.sent.append((" ".join(args), argsh.get("title")))

    async def backup_and_wait(self):
        self.backups += 1
        return self.error


class FakeFhem:
    def __init__(self):
        self.peers = "fhempy_local=opened"
        self.commands = []

    async def send(self, hash, cmd):
        self.commands.append(cmd)
        if "TYPE=BindingsIo" in cmd:
            return self.peers
        return ""


@pytest_asyncio.fixture
async def module(mocker, tmp_path, monkeypatch):
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop(NAME, None)
    mock_fhem.attributes.pop(NAME, None)
    monkeypatch.chdir(tmp_path)
    system = FakeSystem(tmp_path)
    fake_fhem = FakeFhem()
    installed = tmp_path / "fhempy-system-update"
    installed.write_text("")
    mocker.patch.object(helper, "INSTALL_PATH", str(installed))
    mocker.patch.object(helper, "STATUS_FILE", str(tmp_path / "status.json"))
    mocker.patch.object(helper, "LOG_FILE", str(tmp_path / "upgrade.log"))
    mocker.patch.object(system_update, "run_command", system.run)
    mocker.patch.object(system_update, "is_root", lambda: False)
    mocker.patch.object(system_update, "tool", lambda name: "/usr/bin/" + name)
    mocker.patch.object(system_update, "boot_partition", lambda: None)
    mocker.patch.object(system_update, "REBOOT_REQUIRED_FILE", str(tmp_path / "rr"))
    mocker.patch.object(system_update, "HEALTH_DELAY", 0)
    mocker.patch.object(system_update, "POLL_INTERVAL", 0.01)
    mocker.patch("fhempy.lib.fhem.sendCommandHash", fake_fhem.send)
    push = FakeDevice("push", "push")
    backup = FakeDevice("backup", "github_backup")
    mocker.patch.dict(
        fhem_pythonbinding.loadedModuleInstances,
        {"push": push, "backup": backup},
        clear=True,
    )
    mod = system_update.system_update(logger)
    mod.system = system
    mod.fake_fhem = fake_fhem
    mod.push = push
    mod.backup_device = backup
    await mod.Define({"NAME": NAME, "FHEMPYTYPE": "system_update"}, [], {})
    await wait_for(lambda: readings().get("state") == "3 updates (1 security)")
    yield mod
    await mod.Undefine(mod.hash)


@pytest.mark.asyncio
async def test_lists_updates(module):
    assert readings()["updates_available"] == 3
    assert readings()["updates_security"] == 1
    assert readings()["updates_held"] == "linux-image-rpi-v8"
    page = module.detail_html()
    assert "libssl3" in page and "held (update_all)" in page and "security" in page
    # nothing was installed
    assert not upgrades(module)


@pytest.mark.asyncio
async def test_security_update(module):
    await module.update("security")
    upgrade = upgrades(module)[-1]
    assert upgrade[-2:] == ["upgrade", "libssl3"]
    assert module.backup_device.backups == 1
    assert readings()["backup"] == "ok"
    assert readings()["packages_updated"] == "libssl3"
    assert readings()["health"] == "ok"
    assert readings()["reboot_required"] == "no"
    assert readings()["state"] == "1 updates"
    # package list and log are kept
    files = sorted(
        p.name for p in (module.system.tmp_path / ".fhempy" / "system_update").iterdir()
    )
    assert any(f.startswith("packages-") for f in files)
    assert any(f.startswith("update-") for f in files)
    # notify problems: no message for a good update
    assert module.push.sent == []


@pytest.mark.asyncio
async def test_update_all_and_reboot(module):
    module._attr_notify = "all"
    module.system.after_upgrade = ""
    await module.update("everything")
    assert readings()["packages_updated"] == "libssl3, vim, linux-image-rpi-v8"
    assert readings()["reboot_required"] == "yes"
    assert "reboot needed" in module.push.sent[-1][0]
    # reboot only at reboot_time
    module._attr_reboot_time = datetime.strptime("04:30", "%H:%M")
    await module.schedule(datetime(2026, 10, 25, 4, 29))
    assert not [c for c in module.system.calls if "reboot" in c]
    await module.schedule(datetime(2026, 10, 25, 4, 30))
    assert [c for c in module.system.calls if "reboot" in c]
    assert readings()["state"] == "rebooting"
    # only once a day
    module.system.calls.clear()
    await module.schedule(datetime(2026, 10, 25, 4, 30))
    assert not [c for c in module.system.calls if "reboot" in c]


@pytest.mark.asyncio
async def test_kept_back(module):
    # apt kept vim back, it's still listed afterwards
    module.system.after_upgrade = DEBIAN
    await module.update("all")
    assert readings()["packages_updated"] == "-"
    assert readings()["packages_kept_back"] == "libssl3, vim"


@pytest.mark.asyncio
async def test_problem_after_update(module):
    async def peers_lost():
        module.fake_fhem.peers = "fhempy_local=disconnected"
        module.system.failed_units = "mosquitto.service loaded failed failed\n"

    real_finish = module.report_update

    async def finish(pending, updated):
        await peers_lost()
        await real_finish(pending, updated)

    module.report_update = finish
    await module.update("all")
    assert readings()["state"].startswith("problem after update")
    assert "fhempy not connected: fhempy_local" in readings()["health"]
    assert "failed services: mosquitto.service" in readings()["health"]
    text, title = module.push.sent[-1]
    assert "but:" in text and title == f"{NAME}: problem"


@pytest.mark.asyncio
async def test_failed_upgrade(module):
    module.system.upgrade_code = 100
    await module.update("all")
    assert readings()["state"].startswith("failed: update failed: E: boom")
    assert "set repair" in module.push.sent[-1][0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change, reason",
    [
        ({"audit": "The following packages are only half configured"}, "set repair"),
        ({"throttled": "throttled=0x50005"}, "under-voltage"),
    ],
)
async def test_precheck(module, change, reason):
    for key, value in change.items():
        setattr(module.system, key, value)
    await module.update("all")
    assert reason in readings()["state"]
    assert not upgrades(module)
    assert module.push.sent


@pytest.mark.asyncio
async def test_backup_required(module):
    module.backup_device.error = "github_token is invalid"
    await module.update("all")
    assert "backup failed" in readings()["state"]
    assert not upgrades(module)
    module._attr_backup = "optional"
    await module.update("all")
    assert readings()["packages_updated"] == "libssl3, vim"


@pytest.mark.asyncio
async def test_setup_needed(module, mocker, tmp_path):
    mocker.patch.object(helper, "INSTALL_PATH", str(tmp_path / "missing"))
    await module.check(refresh=True)
    assert readings()["state"].startswith("setup needed")
    assert readings()["setup_problem"] == "helper not installed"
    page = module.detail_html()
    assert "helper.py install" in page
    assert "NOPASSWD: " + str(tmp_path / "missing") in page
    # sudo not allowed
    mocker.patch.object(helper, "INSTALL_PATH", str(tmp_path / "fhempy-system-update"))
    module.system.run_helper = lambda args: (1, "sudo: a password is required")
    await module.check(refresh=True)
    assert readings()["setup_problem"].startswith("no sudo permission")
    module.system.run_helper = lambda args: (0, "0")
    await module.check(refresh=True)
    assert readings()["setup_problem"] == "helper is outdated"


@pytest.mark.asyncio
async def test_resume_after_restart(module, tmp_path):
    """fhempy restarted during the update: the new instance waits for it"""
    status = {
        "running": True,
        "pid": 999999999,
        "packages": ["vim"],
        "started": time.time(),
    }
    (tmp_path / "status.json").write_text(json.dumps(status))
    pending = {"packages": ["vim"], "started": time.time() - 10, "before": {}}
    await module.save_state({"pending": pending})
    await module.finish_update(pending)
    # pid is gone without result: killed
    assert readings()["state"].startswith("failed: update failed")
    assert "pending" not in await module.load_state()
