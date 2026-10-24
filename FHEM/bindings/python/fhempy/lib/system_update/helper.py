#!/usr/bin/python3 -I
"""Root helper of the fhempy module system_update.

fhempy runs as user fhem, apt needs root. Instead of allowing apt-get for
fhem in sudoers (apt-get with any options is the same as root), fhem may
only run this helper with sudo. It runs a few fixed commands and checks the
package names it gets.

Install it once as root, the device page of system_update shows the command:
    sudo python3 .../system_update/helper.py install fhem
This copies the helper to /usr/local/sbin (owned by root, fhem can't change
it) and allows fhem to run it with sudo without password.

Only the Python standard library is used, it runs with the system Python.
"""

import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile
import time

HELPER_VERSION = 2
INSTALL_PATH = "/usr/local/sbin/fhempy-system-update"
SUDOERS_PATH = "/etc/sudoers.d/fhempy-system-update"
# readable for fhem, written only by this helper
STATE_DIR = "/var/log/fhempy-system-update"
STATUS_FILE = STATE_DIR + "/status.json"
LOG_FILE = STATE_DIR + "/upgrade.log"
# packages held during an upgrade, released again if the upgrade got killed
HOLD_FILE = "/var/lib/fhempy-system-update-holds.json"
UNIT_PREFIX = "fhempy-system-update"

PACKAGE = re.compile(r"^[a-z0-9][a-z0-9+.-]*(:[a-z0-9-]+)?$")
USER = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
INST = re.compile(r"^Inst (\S+) \[(\S+)\] \(")

APT_ENV = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "DEBIAN_FRONTEND": "noninteractive",
    "APT_LISTCHANGES_FRONTEND": "none",
    # needrestart must not restart FHEM or fhempy in the middle of the update
    "NEEDRESTART_SUSPEND": "1",
    "NEEDRESTART_MODE": "l",
}
# keep changed config files, wait up to 10 minutes for another apt to finish
APT_OPTIONS = [
    "-o",
    "Dpkg::Options::=--force-confdef",
    "-o",
    "Dpkg::Options::=--force-confold",
    "-o",
    "DPkg::Lock::Timeout=600",
]
# never removes packages and never changes the Debian release
UPGRADE = ["apt-get", "-y", "-q"] + APT_OPTIONS + ["--with-new-pkgs", "upgrade"]


def run(args, **kwargs):
    return subprocess.run(args, env=APT_ENV, check=False, **kwargs)


def output(args):
    result = run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout.decode("utf-8", "replace")


def write_json(path, data, mode=0o644):
    directory = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


def ensure_state_dir():
    os.makedirs(STATE_DIR, mode=0o755, exist_ok=True)
    os.chmod(STATE_DIR, 0o755)


def upgradable():
    """installed packages which have an update"""
    sim = output(["apt-get", "-s", "-o", "Debug::NoLocking=1"] + UPGRADE[3:])
    return {m.group(1) for m in map(INST.match, sim.splitlines()) if m}


def held():
    return set(output(["apt-mark", "showhold"]).split())


def release_holds():
    """unhold packages of an upgrade which got killed"""
    holds = read_json(HOLD_FILE).get("packages") or []
    holds = [p for p in holds if PACKAGE.match(str(p))]
    if holds:
        run(["apt-mark", "unhold"] + holds, stdout=subprocess.DEVNULL)
    try:
        os.remove(HOLD_FILE)
    except FileNotFoundError:
        pass


def check_packages(packages):
    """the requested packages which have an update: the names passed on
    to apt are the ones of apt itself, never the command line arguments"""
    bad = [p for p in packages if not PACKAGE.match(p)]
    if bad or not packages:
        sys.exit("invalid package names: " + " ".join(bad or ["(none)"]))
    requested = set(packages)
    valid = sorted(p for p in upgradable() if p in requested)
    if not valid:
        sys.exit("no update available for " + " ".join(sorted(requested)))
    return valid


def do_upgrade(packages, log):
    """upgrade only packages, all other updates are held meanwhile"""
    release_holds()
    to_hold = sorted(upgradable() - set(packages) - held())
    if to_hold:
        write_json(HOLD_FILE, {"packages": to_hold}, mode=0o600)
        run(["apt-mark", "hold"] + to_hold, stdout=log, stderr=log)
    try:
        log.write(("$ " + " ".join(UPGRADE) + "\n").encode())
        log.flush()
        return run(UPGRADE, stdout=log, stderr=subprocess.STDOUT).returncode
    finally:
        release_holds()


def cmd_upgrade_now(packages):
    """runs the upgrade, the status file tells fhempy the result"""
    packages = check_packages(packages)
    ensure_state_dir()
    status = {
        "running": True,
        "pid": os.getpid(),
        "packages": packages,
        "started": time.time(),
    }
    write_json(STATUS_FILE, status)
    code = 1
    with open(LOG_FILE, "wb") as log:
        os.chmod(LOG_FILE, 0o644)
        try:
            code = do_upgrade(packages, log)
        except Exception as exc:  # status must be written in any case
            log.write(f"\nupgrade failed: {exc}\n".encode())
        finally:
            status.update(running=False, exit_code=code, finished=time.time())
            write_json(STATUS_FILE, status)
    return code


def cmd_upgrade(packages):
    """starts the upgrade outside of fhempy: a restart of fhempy or FHEM
    (e.g. by the update itself) must not kill apt in the middle"""
    packages = check_packages(packages)
    status = read_json(STATUS_FILE)
    if status.get("running") and pid_alive(status.get("pid")):
        sys.exit("an update is already running")
    ensure_state_dir()
    write_json(STATUS_FILE, {"running": True, "packages": packages, "queued": True})
    if shutil.which("systemd-run") and os.path.isdir("/run/systemd/system"):
        unit = f"{UNIT_PREFIX}-{int(time.time())}"
        result = run(
            ["systemd-run", "--quiet", "--collect", "--unit", unit, INSTALL_PATH]
            + ["upgrade-now"]
            + packages
        )
        if result.returncode == 0:
            print("started " + unit)
            return 0
    # no systemd: run it here
    return cmd_upgrade_now(packages)


def cmd_refresh():
    return run(["apt-get", "-q"] + APT_OPTIONS + ["update"]).returncode


def cmd_repair():
    code = run(["dpkg", "--configure", "-a"]).returncode
    if code == 0:
        code = run(["apt-get", "-y", "-q"] + APT_OPTIONS + ["-f", "install"]).returncode
    return code


def cmd_reboot():
    if shutil.which("systemctl"):
        return run(["systemctl", "reboot"]).returncode
    return run(["reboot"]).returncode


def cmd_install(user):
    if not USER.match(user):
        sys.exit(f"invalid user name {user}")
    try:
        user = pwd.getpwnam(user).pw_name
    except KeyError:
        sys.exit(f"user {user} does not exist")
    source = os.path.realpath(__file__)
    if source != INSTALL_PATH:
        tmp = INSTALL_PATH + ".new"
        shutil.copyfile(source, tmp)
        os.chown(tmp, 0, 0)
        os.chmod(tmp, 0o755)
        os.replace(tmp, INSTALL_PATH)
    line = f"{user} ALL=(root) NOPASSWD: {INSTALL_PATH}\n"
    fd, tmp = tempfile.mkstemp(dir="/etc/sudoers.d", prefix=".fhempy")
    with os.fdopen(fd, "w") as f:
        f.write(line)
    os.chmod(tmp, 0o440)
    if run(["visudo", "-cqf", tmp]).returncode != 0:
        os.remove(tmp)
        sys.exit("visudo rejected the sudoers line, nothing changed")
    os.replace(tmp, SUDOERS_PATH)
    ensure_state_dir()
    print(f"Installed {INSTALL_PATH}, {user} may run it with sudo.")
    return 0


def cmd_uninstall():
    for path in (SUDOERS_PATH, INSTALL_PATH):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    print("Removed the system_update helper.")
    return 0


def main(argv):
    if not argv:
        sys.exit("usage: version|refresh|upgrade PKG...|repair|reboot|install USER")
    cmd, args = argv[0], argv[1:]
    if cmd == "version":
        print(HELPER_VERSION)
        return 0
    if os.geteuid() != 0:
        sys.exit("must run as root (sudo)")
    commands = {
        "refresh": cmd_refresh,
        "repair": cmd_repair,
        "reboot": cmd_reboot,
        "uninstall": cmd_uninstall,
    }
    if cmd in commands and not args:
        return commands[cmd]()
    if cmd == "upgrade":
        return cmd_upgrade(args)
    if cmd == "upgrade-now":
        return cmd_upgrade_now(args)
    if cmd == "install" and len(args) == 1:
        return cmd_install(args[0])
    sys.exit(f"unknown command {' '.join(argv)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
