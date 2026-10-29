"""Tailscale for the remote access module.

fhempy downloads the official Tailscale binaries to .fhempy/tailscale and
runs its own tailscaled in userspace networking mode: no root, no TUN device,
no changes to the network of the computer. An installed system Tailscale is
not touched. tailscaled keeps running when fhempy restarts (e.g. for an
update), the next fhempy takes it over with the pid file.
"""

import asyncio
import functools
import io
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import tarfile

from .. import utils
from ..core import child_process

PKGS_URL = "https://pkgs.tailscale.com/stable/"
# platform.machine() -> architecture of the Tailscale downloads
ARCHITECTURES = {
    "aarch64": "arm64",
    "arm64": "arm64",
    "armv6l": "arm",
    "armv7l": "arm",
    "armv8l": "arm",
    "x86_64": "amd64",
    "amd64": "amd64",
    "i386": "386",
    "i686": "386",
}
BINARIES = ("tailscale", "tailscaled")
VERSION = re.compile(r"\d+\.\d+\.\d+")
# seconds until the tailscaled of a previous fhempy is killed
STOP_TIMEOUT = 10
LOGIN_URL = re.compile(r"https://login\.tailscale\.com/\S+")


def base_directory():
    return os.path.join(os.getcwd(), ".fhempy", "tailscale")


def bin_directory():
    return os.path.join(base_directory(), "bin")


def state_directory():
    return os.path.join(base_directory(), "state")


def socket_path():
    return os.path.join(base_directory(), "tailscaled.sock")


def binary(name):
    return os.path.join(bin_directory(), name)


def installed_version():
    try:
        with open(os.path.join(bin_directory(), "VERSION"), encoding="utf-8") as f:
            version = f.read().strip()
    except OSError:
        return None
    if not all(os.access(binary(b), os.X_OK) for b in BINARIES):
        return None
    return version or None


def architecture():
    if platform.system() != "Linux":
        raise RuntimeError("Remote access with Tailscale only works on Linux")
    machine = platform.machine().lower()
    if machine not in ARCHITECTURES:
        raise RuntimeError(f"Tailscale is not available for {machine}")
    return ARCHITECTURES[machine]


def version_of(tarball):
    """tailscale_1.90.6_arm64.tgz -> 1.90.6"""
    parts = tarball.split("_")
    return parts[1] if len(parts) >= 3 else tarball


def extract(data, version):
    """Write tailscale and tailscaled of the tarball to bin_directory().
    The files are written to fixed paths, names in the tarball are only
    compared, never used as path."""
    os.makedirs(bin_directory(), exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = {m.name.rsplit("/", 1)[-1]: m for m in tar.getmembers() if m.isfile()}
        if any(b not in members for b in BINARIES):
            raise RuntimeError("Tailscale download is incomplete")
        for b in BINARIES:
            path = binary(b)
            with open(path + ".new", "wb") as dst:
                dst.write(tar.extractfile(members[b]).read())
            os.chmod(path + ".new", 0o700)
            os.replace(path + ".new", path)
    with open(os.path.join(bin_directory(), "VERSION"), "w", encoding="utf-8") as f:
        f.write(version)


async def latest_version(session, arch):
    """Version of the newest stable Tailscale for arch"""
    async with session.get(PKGS_URL, params={"mode": "json"}) as resp:
        resp.raise_for_status()
        data = json.loads(await resp.text())
    match = VERSION.fullmatch(version_of(data["Tarballs"][arch]))
    if match is None:
        raise ValueError("unexpected Tailscale version")
    return match.group(0)


async def install(logger):
    """Download Tailscale if it's missing or outdated, returns the version.
    Without internet the installed version is used."""
    import aiohttp

    arch = architecture()
    installed = await utils.run_blocking(functools.partial(installed_version))
    timeout = aiohttp.ClientTimeout(total=600, sock_read=60)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            version = await latest_version(session, arch)
            if version == installed:
                return installed
            logger.info(f"Downloading Tailscale {version} ({arch})")
            tarball = f"tailscale_{version}_{arch}.tgz"
            async with session.get(PKGS_URL + tarball) as resp:
                resp.raise_for_status()
                data = await resp.read()
    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as err:
        if installed:
            logger.warning(f"Can't check for a new Tailscale version: {err}")
            return installed
        raise RuntimeError(f"Tailscale download failed: {err}") from err
    await utils.run_blocking(functools.partial(extract, data, version))
    return version


def find_login_url(text):
    match = LOGIN_URL.search(text or "")
    return match.group(0) if match else None


def funnel_ports(serve_config):
    """Ports of this computer which Funnel forwards to the internet"""
    allow = (serve_config or {}).get("AllowFunnel") or {}
    return {int(k.rsplit(":", 1)[1]) for k, v in allow.items() if v and ":" in k}


def funnel_active(serve_config):
    """True if Funnel forwards port 443 of this computer to the internet"""
    return 443 in funnel_ports(serve_config)


def pid_path():
    return os.path.join(base_directory(), "tailscaled.pid")


def write_pid_file(pid, version):
    with open(pid_path() + ".new", "w", encoding="utf-8") as f:
        json.dump({"pid": pid, "version": version}, f)
    os.replace(pid_path() + ".new", pid_path())


def read_pid_file():
    try:
        with open(pid_path(), encoding="utf-8") as f:
            info = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(info, dict) or not isinstance(info.get("pid"), int):
        return None
    return info


def remove_pid_file(pid):
    """removes the pid file if it belongs to pid (or pid is None)"""
    info = read_pid_file()
    if info is not None and pid is not None and info["pid"] != pid:
        return
    try:
        os.remove(pid_path())
    except OSError:
        pass


def daemon_alive(pid):
    """True if pid is the tailscaled of fhempy (pids are reused)"""
    # int(): the pid of the pid file is never used as path
    proc_dir = os.path.join("/proc", str(int(pid)))
    try:
        with open(os.path.join(proc_dir, "cmdline"), "rb") as f:
            args = f.read().decode(errors="replace").split("\0")
        with open(os.path.join(proc_dir, "stat"), "rb") as f:
            stat = f.read().decode(errors="replace")
    except OSError:
        return False
    # Z = exited, not reaped yet
    if stat.rsplit(")", 1)[-1].split()[:1] == ["Z"]:
        return False
    # args[1]: script started by an interpreter (tests)
    return binary("tailscaled") in args[:2]


async def stop_pid(pid):
    """stop the tailscaled of a previous fhempy, it's not our child"""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            # own session, stops the whole process group
            os.killpg(pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        for _ in range(STOP_TIMEOUT * 10):
            if not daemon_alive(pid):
                return
            await asyncio.sleep(0.1)


async def stop_orphan(logger):
    """stop tailscaled if the remote access device doesn't exist anymore,
    e.g. deleted while fhempy wasn't running"""
    info = await utils.run_blocking(functools.partial(read_pid_file))
    if info is None:
        return
    if daemon_alive(info["pid"]):
        logger.info("Stop Tailscale, no remote_access device is defined")
        await stop_pid(info["pid"])
    remove_pid_file(info["pid"])


def rotate_log(max_bytes=5 * 1024 * 1024):
    """tailscaled writes to the log itself: copy and truncate, it keeps
    writing at the (new) end of the file"""
    path = child_process.log_path("tailscale")
    try:
        if os.path.getsize(path) <= max_bytes:
            return
        if os.path.exists(path + ".1"):
            os.replace(path + ".1", path + ".2")
        shutil.copyfile(path, path + ".1")
        os.truncate(path, 0)
    except OSError:
        pass


class Tailscale:
    """tailscaled of fhempy and its command line tool"""

    def __init__(self, logger):
        self.logger = logger
        # Popen if this fhempy started tailscaled
        self.daemon = None
        self.daemon_pid = None
        self.daemon_version = None
        self.login_proc = None
        self.funnel_proc = None
        self.funnel_output = ""
        self._reader = None

    def cli_args(self, *args):
        return [binary("tailscale"), f"--socket={socket_path()}", *args]

    # --- tailscaled ---

    def daemon_running(self):
        if self.daemon is not None:
            # started by this fhempy, poll() also reaps the exited process
            if self.daemon.poll() is None:
                return True
            self.daemon = None
            remove_pid_file(self.daemon_pid)
            self.daemon_pid = None
            return False
        if self.daemon_pid is None:
            # tailscaled of the previous fhempy (update, restart)
            info = read_pid_file()
            if info is None:
                return False
            self.daemon_pid = info["pid"]
            self.daemon_version = info.get("version")
            self.logger.info(f"Tailscale is running already (pid {self.daemon_pid})")
        if daemon_alive(self.daemon_pid):
            return True
        remove_pid_file(self.daemon_pid)
        self.daemon_pid = None
        return False

    def start_daemon(self, version):
        os.makedirs(state_directory(), exist_ok=True)
        path = child_process.log_path("tailscale")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "ab") as log:
            self.daemon = child_process.start(
                [
                    binary("tailscaled"),
                    "--tun=userspace-networking",
                    f"--statedir={state_directory()}",
                    f"--socket={socket_path()}",
                    # random UDP port, a system Tailscale uses 41641
                    "--port=0",
                ],
                cwd=base_directory(),
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                # keeps running when fhempy restarts for an update, the
                # remote access stays online, see detach()
                preexec_fn=None,
                output_log=child_process.OutputLog(path, self.logger, capture=False),
            )
        self.daemon_pid = self.daemon.pid
        self.daemon_version = version
        write_pid_file(self.daemon_pid, version)

    async def stop_daemon(self):
        daemon, self.daemon = self.daemon, None
        pid, self.daemon_pid = self.daemon_pid, None
        if daemon is not None:
            await child_process.stop(daemon)
        elif pid is not None:
            await stop_pid(pid)
        remove_pid_file(pid)

    async def _stop_cli(self):
        for attr in ("login_proc", "funnel_proc"):
            proc = getattr(self, attr)
            setattr(self, attr, None)
            if proc is not None and proc.returncode is None:
                proc.kill()
                await proc.wait()

    async def stop(self):
        await self._stop_cli()
        await self.stop_daemon()

    async def detach(self):
        """fhempy stops (update, restart): tailscaled keeps running and the
        next fhempy takes it over, FHEMWEB stays reachable meanwhile"""
        await self._stop_cli()
        self.daemon = None
        self.daemon_pid = None

    # --- command line tool ---

    async def run(self, *args, timeout=30):
        """Run tailscale with args, returns exit code and output"""
        proc = await asyncio.create_subprocess_exec(
            *self.cli_args(*args),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return -1, "timeout"
        return proc.returncode, out.decode(errors="replace")

    async def run_json(self, *args):
        code, out = await self.run(*args, "--json")
        if code != 0:
            return None
        try:
            return json.loads(out)
        except ValueError:
            return None

    async def status(self):
        return await self.run_json("status")

    async def funnel_status(self):
        return await self.run_json("funnel", "status")

    async def start_login(self, hostname):
        """`tailscale up` waits until the user logged in, the login link
        appears in status()["AuthURL"]."""
        if self.login_proc is not None and self.login_proc.returncode is None:
            return
        self.login_proc = await asyncio.create_subprocess_exec(
            *self.cli_args("up", f"--hostname={hostname}", "--json"),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    async def set_hostname(self, hostname):
        return await self.run("set", f"--hostname={hostname}")

    async def logout(self):
        return await self.run("logout")

    # --- funnel ---

    def funnel_busy(self):
        return self.funnel_proc is not None and self.funnel_proc.returncode is None

    async def start_funnel(self, target):
        """Forward https://<name>.ts.net to target. If Funnel isn't enabled
        in the tailnet yet, the command prints a link to enable it and waits
        until the user did that, see funnel_enable_url()."""
        await self.run("serve", "reset")
        self.funnel_output = ""
        self.funnel_proc = await asyncio.create_subprocess_exec(
            *self.cli_args("funnel", "--bg", "--yes", target),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self._reader = asyncio.create_task(self._read_funnel_output(self.funnel_proc))

    async def _read_funnel_output(self, proc):
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            if proc is self.funnel_proc:
                self.funnel_output += line.decode(errors="replace")
        await proc.wait()

    async def funnel_port(self, port, target):
        """Forward https://<name>.ts.net:<port> to target, port 8443 or
        10000. Funnel is enabled already (start_funnel)."""
        return await self.run("funnel", "--bg", "--yes", f"--https={port}", target)

    async def funnel_port_off(self, port):
        return await self.run("funnel", f"--https={port}", "off")

    def funnel_enable_url(self):
        return find_login_url(self.funnel_output)

    async def stop_funnel(self):
        proc, self.funnel_proc = self.funnel_proc, None
        if proc is not None and proc.returncode is None:
            proc.kill()
            await proc.wait()
        if self.daemon_running():
            await self.run("serve", "reset")
