"""SSH with user and password: the one-time setup on this computer and the
automatic setup of the Raspberry Pi of another site. The password is only
used for the connection, it's neither stored nor logged. SSH host keys are
trusted on first use (same known_hosts as the peer installer).

Every command and its output go live to log (a callable with one line), the
device page shows them like a terminal."""

import asyncio
import ipaddress
import re
import shlex
import socket
from pathlib import Path

from ..core.peer_installer import peer_installer

CONNECT_TIMEOUT = 30
COMMAND_TIMEOUT = 120
DEFAULT_SSH_PORT = 22
# apt-get update + install wireguard-tools on a Raspberry Pi
INSTALL_TIMEOUT = 900
SITE_INTERFACE = "wgfhempy"
# shorter passwords would hide too much of the output
MIN_MASK_LENGTH = 3


class RemoteError(Exception):
    pass


def nolog(line):
    """default log: nothing is shown"""


def mask(text, password):
    if password and len(password) >= MIN_MASK_LENGTH:
        return text.replace(password, "***")
    return text


def known_hosts_name(host, port):
    """host name in known_hosts, [host]:port for other ports than 22"""
    return host if port == DEFAULT_SSH_PORT else f"[{host}]:{port}"


async def trust_host_key(asyncssh, host, port=DEFAULT_SSH_PORT, log=nolog):
    name = known_hosts_name(host, port)
    known = await asyncio.to_thread(peer_installer._known_host_lines)
    if any(line.split(" ", 1)[0] == name for line in known):
        return
    key = await asyncio.wait_for(
        asyncssh.get_server_host_key(host, port=port, family=socket.AF_INET),
        CONNECT_TIMEOUT,
    )
    if key is None:
        raise RemoteError(f"{host} didn't send an SSH host key")
    key_line = key.export_public_key("openssh").decode().strip()
    await asyncio.to_thread(peer_installer._remember_host_key, name, key_line)
    log(f"# new SSH host key of {name} remembered: {key.get_fingerprint()}")


async def connect(host, user, password, port=DEFAULT_SSH_PORT, log=nolog):
    import asyncssh

    log(f"# ssh {user}@{host}" + ("" if port == DEFAULT_SSH_PORT else f" -p {port}"))
    try:
        await trust_host_key(asyncssh, host, port, log)
        conn = await asyncio.wait_for(
            asyncssh.connect(
                host,
                port=port,
                username=user,
                password=password,
                known_hosts=peer_installer.KNOWN_HOSTS,
                client_keys=None,
                family=socket.AF_INET,
            ),
            CONNECT_TIMEOUT,
        )
    except asyncssh.PermissionDenied:
        raise RemoteError("wrong user or password") from None
    except asyncssh.HostKeyNotVerifiable:
        raise RemoteError(
            f"SSH host key of {host} changed, remove it from "
            f"{peer_installer.KNOWN_HOSTS} if the computer was reinstalled"
        ) from None
    except (OSError, asyncio.TimeoutError, asyncssh.Error) as err:
        raise RemoteError(
            f"SSH connection to {host}:{port} failed ({err or type(err).__name__}), "
            "is SSH enabled?"
        ) from None
    log("# connected")
    return conn


async def execute(
    conn,
    command,
    log=nolog,
    show=None,
    stdin=None,
    password=None,
    limit=COMMAND_TIMEOUT,
):
    """runs command, shows "$ show" and each line of the output while it
    runs. Returns exit status and output (stdout and stderr)."""
    import asyncssh

    log(f"$ {show or command}")
    lines = []
    try:
        async with asyncio.timeout(limit):
            process = await conn.create_process(
                command, input=stdin or "", stderr=asyncssh.STDOUT, errors="replace"
            )
            async for line in process.stdout:
                if not line:
                    # end of the output
                    continue
                line = mask(line.rstrip("\r\n"), password)
                lines.append(line)
                log(line)
            result = await process.wait()
    except asyncio.TimeoutError:
        log("# took too long, stopped")
        raise RemoteError("took too long") from None
    return result.exit_status, "\n".join(lines)


async def upload(conn, data, log=nolog, what="file"):
    """private temporary file on the remote computer, returns its path"""
    result = await conn.run("umask 077; mktemp", check=True)
    path = result.stdout.strip()
    await conn.run(
        f"umask 077; cat > {shlex.quote(path)}", input=data, encoding=None, check=True
    )
    log(f"# {what} copied to {path} ({len(data)} bytes)")
    return path


async def sudo(conn, user, password, command, log=nolog, limit=INSTALL_TIMEOUT):
    """runs command (a list) as root, output of the command. stdin of the
    command is /dev/null: with NOPASSWD sudo doesn't read the password line."""
    line = " ".join(shlex.quote(str(a)) for a in command)
    inner = shlex.quote(f"exec </dev/null; {line}")
    status, out = await execute(
        conn,
        f"sudo -S -p '' sh -c {inner}",
        log,
        show=f"sudo {line}",
        stdin=password + "\n",
        password=password,
        limit=limit,
    )
    if status != 0:
        if "incorrect password" in out or "not in the sudoers" in out:
            raise RemoteError(f"user {user} has no sudo rights")
        lines = [x for x in out.splitlines() if x.strip()]
        raise RemoteError(lines[-1] if lines else f"exit code {status}")
    return out


async def install_helper(host, user, password, helper_path, fhempy_user, log=nolog):
    """one-time setup on this computer via SSH to itself"""
    conn = await connect(host, user, password, log=log)
    async with conn:
        source = await asyncio.to_thread(Path(helper_path).read_bytes)
        path = await upload(conn, source, log, "helper")
        try:
            return await sudo(
                conn,
                user,
                password,
                ["python3", "-I", path, "install", fhempy_user],
                log,
            )
        finally:
            await conn.run(f"rm -f {shlex.quote(path)}")


INTERFACE_NAME = re.compile(r"^[A-Za-z0-9_.@-]{1,15}$")


def parse_site(route, addresses):
    """home network and address of a computer from ip -4 -o route show
    default and ip -4 -o addr show"""
    dev = None
    for line in route.splitlines():
        words = line.split()
        if "dev" in words[:-1]:
            dev = words[words.index("dev") + 1]
            break
    for line in addresses.splitlines():
        words = line.split()
        if len(words) > 3 and words[1] == dev and "inet" in words:
            try:
                iface = ipaddress.IPv4Interface(words[words.index("inet") + 1])
            except ValueError:
                continue
            found = {"network": str(iface.network), "ip": str(iface.ip)}
            if INTERFACE_NAME.match(dev):
                # goes into the PostUp lines of the configuration
                found["dev"] = dev
            return found
    return {}


async def site_info(conn, log=nolog):
    _, route = await execute(conn, "ip -4 -o route show default", log)
    _, addresses = await execute(conn, "ip -4 -o addr show", log)
    return parse_site(route, addresses)


async def setup_site(conn, user, password, config, log=nolog):
    """installs WireGuard on the other site and starts the tunnel"""
    status, _ = await execute(conn, "command -v wg && command -v iptables", log)
    path = await upload(conn, config.encode(), log, "configuration")
    target = f"/etc/wireguard/{SITE_INTERFACE}.conf"
    unit = f"wg-quick@{SITE_INTERFACE}"
    steps = []
    if status != 0:
        steps += [
            ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "-q", "update"],
            [
                "env",
                "DEBIAN_FRONTEND=noninteractive",
                "apt-get",
                "-y",
                "-q",
                "install",
                "wireguard-tools",
                "iptables",
            ],
        ]
    steps += [
        ["mkdir", "-p", "-m", "700", "/etc/wireguard"],
        ["install", "-m", "600", path, target],
        ["systemctl", "enable", "--quiet", unit],
        ["systemctl", "restart", unit],
        ["wg", "show", SITE_INTERFACE],
    ]
    try:
        for step in steps:
            await sudo(conn, user, password, step, log)
    finally:
        await conn.run(f"rm -f {shlex.quote(path)}")
    return "started"
