"""Install and start the matter.js based bridge (bridge.mjs).

Node.js is found or installed like for the matter module, matter.js is
installed with npm into .fhempy/matter_bridge.
"""

import json
import os
import re
import secrets
import shutil
import subprocess

from ..core import child_process
from ..matter import server

MATTER_JS_PACKAGE = "@matter/main"
MATTER_JS_VERSION = "0.17.9"
SCRIPT = os.path.join(os.path.dirname(__file__), "bridge.mjs")

# Matter doesn't allow these passcodes
INVALID_PASSCODES = {
    0,
    11111111,
    22222222,
    33333333,
    44444444,
    55555555,
    66666666,
    77777777,
    88888888,
    99999999,
    12345678,
    87654321,
}


def base_directory():
    return os.path.join(os.getcwd(), ".fhempy", "matter_bridge")


def bridge_directory(name):
    # contains the pairings of this bridge (keys), keep it!
    return os.path.join(base_directory(), name)


def log_file(name):
    return os.path.join(bridge_directory(name), "bridge.log")


def installed_version():
    try:
        with open(
            os.path.join(
                base_directory(), "node_modules", "@matter", "main", "package.json"
            ),
            encoding="utf-8",
        ) as f:
            data = f.read()
    except OSError:
        return None
    m = re.search(r'"version"\s*:\s*"([^"]+)"', data)
    return m.group(1) if m else None


def needs_install(installed):
    return installed != MATTER_JS_VERSION


def install(node, env):
    """npm install @matter/main into .fhempy/matter_bridge"""
    os.makedirs(base_directory(), exist_ok=True)
    package_json = os.path.join(base_directory(), "package.json")
    if not os.path.exists(package_json):
        with open(package_json, "w", encoding="utf-8") as f:
            f.write('{"name": "fhempy-matter-bridge", "private": true}\n')
    proc = subprocess.run(
        server.npm_command(node)
        + [
            "install",
            "--no-audit",
            "--no-fund",
            "--omit=dev",
            f"{MATTER_JS_PACKAGE}@{MATTER_JS_VERSION}",
        ],
        cwd=base_directory(),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.decode(errors="replace")[-2000:])


def new_passcode():
    while True:
        passcode = secrets.randbelow(99999998) + 1
        if passcode not in INVALID_PASSCODES:
            return passcode


def pairing_settings(name):
    """Passcode and discriminator of the bridge, created once and kept,
    apps which are already paired don't need them."""
    path = os.path.join(bridge_directory(name), "pairing.json")
    try:
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
        if (
            settings.get("passcode") not in INVALID_PASSCODES
            and 0 <= int(settings.get("discriminator", -1)) <= 4095
        ):
            return settings
    except (OSError, ValueError, TypeError):
        pass
    settings = {"passcode": new_passcode(), "discriminator": secrets.randbelow(4096)}
    os.makedirs(bridge_directory(name), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f)
    return settings


def erase(name):
    """Remove all pairings, the bridge gets a new pairing code"""
    shutil.rmtree(bridge_directory(name), ignore_errors=True)


def _rotate_log(name, max_size=5 * 1024 * 1024):
    path = log_file(name)
    try:
        if os.path.getsize(path) > max_size:
            os.replace(path, path + ".1")
    except OSError:
        pass


def start(node, env, name, port, bridge_name, log_level="notice"):
    directory = bridge_directory(name)
    os.makedirs(directory, exist_ok=True)
    _rotate_log(name)
    # node resolves @matter/main next to the script
    script = os.path.join(base_directory(), "bridge.mjs")
    shutil.copyfile(SCRIPT, script)
    settings = pairing_settings(name)
    env = dict(env)
    env["MATTER_STORAGE_PATH"] = os.path.join(directory, "data")
    env["MATTER_LOG_LEVEL"] = log_level
    # matter.js interprets command line arguments itself
    env["FHEMPY_BRIDGE"] = json.dumps(
        {
            "port": int(port),
            "name": bridge_name,
            "passcode": settings["passcode"],
            "discriminator": settings["discriminator"],
        }
    )
    log = open(log_file(name), "ab")
    try:
        return child_process.start(
            [node, script],
            cwd=base_directory(),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=log,
        )
    finally:
        log.close()
