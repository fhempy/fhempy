"""Install and run the matter.js based Matter server (npm package matter-server).

Node.js >= 22.13 is needed. If the system has no suitable Node.js, the
Node.js binaries from PyPI (nodejs-wheel-binaries) are installed into the
fhempy environment, they exist for 64-bit Linux (x86_64, aarch64).
"""

import functools
import importlib
import importlib.util
import os
import platform
import re
import shutil
import subprocess

from .. import pkg_installer, utils
from ..core import child_process
from ..core.shell_env import interactive_shell_env

MATTER_SERVER_PACKAGE = "matter-server"
MATTER_SERVER_VERSION = "1.4.0"
NODE_WHEEL = "nodejs-wheel-binaries==24.19.0"
NODE_MIN_VERSION = (22, 13)
# name of the controller in other apps, set by the controller after connect
# (--default-fabric-label of matter-server 1.4.0 isn't used for pairing)
FABRIC_LABEL = "FHEM"
NODE_WHEEL_MACHINES = ("x86_64", "amd64", "aarch64", "arm64")


class NodeNotFound(Exception):
    pass


def base_directory():
    return os.path.join(os.getcwd(), ".fhempy", "matter_server")


def storage_directory():
    # contains the Matter fabric (keys of all paired devices), keep it!
    return os.path.join(base_directory(), "data")


def server_script():
    return os.path.join(
        base_directory(),
        "node_modules",
        MATTER_SERVER_PACKAGE,
        "dist",
        "esm",
        "MatterServer.js",
    )


def installed_version():
    try:
        with open(
            os.path.join(
                base_directory(), "node_modules", MATTER_SERVER_PACKAGE, "package.json"
            ),
            encoding="utf-8",
        ) as f:
            data = f.read()
    except OSError:
        return None
    m = re.search(r'"version"\s*:\s*"([^"]+)"', data)
    return m.group(1) if m else None


def _version_tuple(version):
    return tuple(int(part) for part in re.findall(r"\d+", version or "")[:3])


def needs_install(installed):
    """True if the Matter server is missing or older than the tested version.
    A newer version (set update) is kept."""
    if installed is None:
        return True
    return _version_tuple(installed) < _version_tuple(MATTER_SERVER_VERSION)


def parse_node_version(text):
    m = re.search(r"v?+(\d++)\.(\d++)", text or "")
    if m is None:
        return None
    return (int(m.group(1)), int(m.group(2)))


def _node_version(node, env):
    try:
        out = subprocess.run(
            [node, "--version"],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        ).stdout.decode(errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    return parse_node_version(out)


def _wheel_node():
    # the wheel might have been installed while fhempy is running
    importlib.invalidate_caches()
    spec = importlib.util.find_spec("nodejs_wheel")
    if spec is None or spec.origin is None:
        return None
    node = os.path.join(os.path.dirname(spec.origin), "bin", "node")
    return node if os.path.exists(node) else None


def find_node(env):
    """Returns (node binary, version) of a Node.js >= 22.13 or raises NodeNotFound"""
    candidates = [shutil.which("node", path=env.get("PATH")), _wheel_node()]
    found = None
    for node in candidates:
        if node is None:
            continue
        version = _node_version(node, env)
        if version is not None and version >= NODE_MIN_VERSION:
            return node, version
        found = found or version
    raise NodeNotFound(found)


def node_wheel_supported():
    return (
        platform.system() == "Linux"
        and platform.machine().lower() in NODE_WHEEL_MACHINES
    )


def npm_command(node):
    """npm next to the node binary, works for system node and the wheel"""
    bindir = os.path.dirname(node)
    npm_cli = os.path.join(
        bindir, "..", "lib", "node_modules", "npm", "bin", "npm-cli.js"
    )
    if os.path.exists(npm_cli):
        return [node, os.path.normpath(npm_cli)]
    npm = os.path.join(bindir, "npm")
    if os.path.exists(npm):
        return [npm]
    return ["npm"]


def env_for(node, env):
    env = dict(env)
    # npm scripts call "node", use the one we found
    env["PATH"] = os.path.dirname(node) + os.pathsep + env.get("PATH", "")
    return env


async def prepare_node(logger):
    """Find or install Node.js, returns (node, version, env)"""
    env = await utils.run_blocking(functools.partial(interactive_shell_env))
    try:
        node, version = await utils.run_blocking(functools.partial(find_node, env))
    except NodeNotFound:
        if not node_wheel_supported():
            raise
        logger.info("No Node.js >= 22.13 found, installing it from PyPI")
        await pkg_installer.force_update_package(NODE_WHEEL)
        pkg_installer.invalidate_dependency_cache()
        node, version = await utils.run_blocking(functools.partial(find_node, env))
    return node, version, env_for(node, env)


def install(node, env, version):
    """npm install matter-server@version into .fhempy/matter_server"""
    os.makedirs(storage_directory(), exist_ok=True)
    package_json = os.path.join(base_directory(), "package.json")
    if not os.path.exists(package_json):
        with open(package_json, "w", encoding="utf-8") as f:
            f.write('{"name": "fhempy-matter-server", "private": true}\n')
    proc = subprocess.run(
        npm_command(node)
        + [
            "install",
            "--no-audit",
            "--no-fund",
            "--omit=dev",
            f"{MATTER_SERVER_PACKAGE}@{version}",
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


def start(
    node,
    env,
    port,
    bluetooth_adapter=None,
    primary_interface=None,
    test_dcl=False,
    logger=None,
):
    args = [
        node,
        server_script(),
        "--storage-path",
        storage_directory(),
        "--port",
        str(port),
        "--listen-address",
        "127.0.0.1",
        "--log-file",
        log_file(),
    ]
    if bluetooth_adapter is not None:
        args += ["--bluetooth-adapter", str(bluetooth_adapter)]
    if primary_interface:
        args += ["--primary-interface", primary_interface]
    if test_dcl:
        # accept devices with test/development certificates (beta firmware)
        args += ["--enable-test-net-dcl", "true"]
    return child_process.start(
        args,
        cwd=base_directory(),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        output_log=child_process.OutputLog(log_file(), logger, capture=False),
    )


def log_file():
    return os.path.join(base_directory(), "matter_server.log")


def log_size():
    try:
        return os.path.getsize(log_file())
    except OSError:
        return 0


def startup_error(offset=0):
    """Explains why the server failed to start, None if there is no error.
    Only the log written after offset (log_size() before the start) is used."""
    try:
        with open(log_file(), "rb") as f:
            if offset <= os.fstat(f.fileno()).st_size:
                f.seek(offset)
            data = f.read()
    except OSError:
        return None
    lines = data.decode("utf-8", errors="replace").splitlines(True)[-300:]
    fatal = [i for i, line in enumerate(lines) if " FATAL " in line]
    if not fatal:
        return None
    lines = lines[fatal[-1] :]
    text = "".join(lines)
    if "EAFNOSUPPORT" in text:
        return (
            "IPv6 is disabled on this computer, Matter needs IPv6. "
            "Enable it (e.g. remove ipv6.disable=1 / disable_ipv6=1) and restart."
        )
    if "EADDRINUSE" in text:
        return (
            "A port is already used by another program, " "change the attribute port."
        )
    causes = [line.strip() for line in lines if line.strip().startswith("Caused by")]
    if causes:
        return causes[-1]
    return lines[0].strip()
