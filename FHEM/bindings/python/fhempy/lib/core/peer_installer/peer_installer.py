"""
Installs fhempy on a remote peer via SSH:
set fhempy_local installPeer <host> <user> <password>

The peer only needs SSH enabled (e.g. Raspberry Pi Imager) and a user with
sudo rights. install_peer.sh is uploaded and run with sudo, its progress lines
("fhempy-install: 2/5 ...") are shown in the reading peer_install of the
BindingsIo device. The password is only used for this one connection, it's
neither stored nor logged.
"""

import asyncio
import logging
import os
import socket
from pathlib import Path

from fhempy.lib import fhem, pkg_installer

logger = logging.getLogger(__name__)

PORT = 15733
STEP_PREFIX = "fhempy-install: "
SCRIPT = os.path.join(os.path.dirname(__file__), "install_peer.sh")
REMOTE_SCRIPT = "/tmp/fhempy_install_peer.sh"
CONNECT_TIMEOUT = 30
# installing the system packages and Python on a Raspberry Pi takes a while
INSTALL_TIMEOUT = 3600

_running = set()


def peer_device_name(ip):
    """Same name as the zeroconf discovery (discover_fhempy) uses."""
    return "fhempy_peer_" + ip.replace(".", "_")


def parse_args(args):
    """installPeer <host> <user> <password>, user@host <password> works too.
    Returns (host, user, password) or raises ValueError."""
    if len(args) == 2 and "@" in args[0]:
        user, host = args[0].rsplit("@", 1)
        password = args[1]
    elif len(args) == 3:
        host, user, password = args
    else:
        raise ValueError("usage: installPeer <host> <user> <password>")
    if not host or not user or not password:
        raise ValueError("usage: installPeer <host> <user> <password>")
    return host, user, password


class PeerInstallError(Exception):
    pass


class PeerInstaller:
    def __init__(self, hash, host, user, password):
        # hash of the local BindingsIo device, which shows the progress
        self.hash = hash
        self.host = host
        self.user = user
        self.password = password
        self.last_step = ""

    async def report(self, text):
        await fhem.readingsSingleUpdate(
            self.hash, "peer_install", f"{self.host}: {text}", 1
        )

    async def run(self):
        try:
            await self.report("connecting")
            await pkg_installer.check_and_install_dependencies("core/peer_installer")
            ip = await self.install()
            await self.report("connecting FHEM to the peer")
            await self.define_peer(ip)
            await self.report(f"done, {peer_device_name(ip)} is ready")
            logger.info("fhempy installed on peer %s (%s)", self.host, ip)
        except PeerInstallError as err:
            await self.report(f"failed: {err}")
        except Exception:
            logger.exception("Failed to install fhempy on peer %s", self.host)
            await self.report("failed: unexpected error, see fhempy log")
        finally:
            self.password = None

    async def install(self):
        import asyncssh

        try:
            # BindingsIo only connects to IPv4 addresses
            conn = await asyncio.wait_for(
                asyncssh.connect(
                    self.host,
                    username=self.user,
                    password=self.password,
                    known_hosts=None,
                    client_keys=None,
                    family=socket.AF_INET,
                ),
                CONNECT_TIMEOUT,
            )
        except asyncssh.PermissionDenied:
            raise PeerInstallError("wrong user or password")
        except (OSError, asyncio.TimeoutError, asyncssh.Error) as err:
            raise PeerInstallError(
                f"SSH connection failed ({err or type(err).__name__}), "
                "is SSH enabled on the peer?"
            )

        async with conn:
            ip = conn.get_extra_info("peername")[0]
            await self.report(f"connected ({ip}), uploading installer")
            script = await asyncio.to_thread(Path(SCRIPT).read_bytes)
            await conn.run(
                f"cat > {REMOTE_SCRIPT}", input=script, encoding=None, check=True
            )
            # sudo reads the password from stdin, -p '' hides its prompt;
            # the script runs fhempy as the SSH user (SUDO_USER)
            cmd = (
                f"sudo -S -p '' bash {REMOTE_SCRIPT}; ret=$?; "
                f"rm -f {REMOTE_SCRIPT}; exit $ret"
            )
            await self.report("installing (this can take 15 minutes)")
            try:
                await asyncio.wait_for(self.run_installer(conn, cmd), INSTALL_TIMEOUT)
            except asyncio.TimeoutError:
                raise PeerInstallError(
                    f"installation takes too long, last step: {self.last_step}"
                )
        return ip

    async def run_installer(self, conn, cmd):
        import asyncssh

        async with conn.create_process(cmd, stderr=asyncssh.STDOUT) as process:
            process.stdin.write(self.password + "\n")
            process.stdin.write_eof()
            output = []
            async for line in process.stdout:
                line = line.rstrip()
                logger.debug("peer %s: %s", self.host, line)
                output.append(line)
                del output[:-20]
                if line.startswith(STEP_PREFIX):
                    step = line[len(STEP_PREFIX) :]
                    if step.startswith("failed: "):
                        raise PeerInstallError(step[len("failed: ") :])
                    if not step.startswith("done"):
                        self.last_step = step
                        await self.report(step)
            await process.wait()
            if process.exit_status != 0:
                logger.error(
                    "Installation on peer %s failed:\n%s", self.host, "\n".join(output)
                )
                if any(
                    "incorrect password" in line or "not in the sudoers" in line
                    for line in output
                ):
                    raise PeerInstallError(f"user {self.user} has no sudo rights")
                raise PeerInstallError("installation failed, see fhempy log")

    async def define_peer(self, ip):
        name = peer_device_name(ip)
        if await fhem.checkIfDeviceExists(self.hash, "TYPE", "BindingsIo", "IP", ip):
            return
        ret = await fhem.CommandDefine(
            self.hash, f"{name} BindingsIo {ip}:{PORT} fhempy"
        )
        if ret:
            raise PeerInstallError(f"define {name} failed: {ret}")


def start(hash, args):
    """Starts the installation in the background, returns an error message
    for invalid arguments."""
    try:
        host, user, password = parse_args(args)
    except ValueError as err:
        return str(err)
    if host.startswith("-") or any(c.isspace() for c in host):
        return "invalid host"
    if host in _running:
        return f"installation on {host} is already running"
    _running.add(host)
    installer = PeerInstaller(hash, host, user, password)
    task = asyncio.create_task(installer.run())
    task.add_done_callback(lambda _: _running.discard(host))
    return None
