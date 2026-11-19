"""SSH with user and password: the one-time setup on this computer and the
automatic setup of the Raspberry Pi of another site. The password is only
used for the connection, it's neither stored nor logged. SSH host keys are
trusted on first use (same known_hosts as the peer installer)."""

import asyncio
import ipaddress
import shlex
import socket
from pathlib import Path

from ..core.peer_installer import peer_installer

CONNECT_TIMEOUT = 30
DEFAULT_SSH_PORT = 22
# apt-get update + install wireguard-tools on a Raspberry Pi
INSTALL_TIMEOUT = 900
SITE_INTERFACE = "wgfhempy"


class RemoteError(Exception):
    pass


def known_hosts_name(host, port):
    """host name in known_hosts, [host]:port for other ports than 22"""
    return host if port == DEFAULT_SSH_PORT else f"[{host}]:{port}"


async def trust_host_key(asyncssh, host, port=DEFAULT_SSH_PORT):
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


async def connect(host, user, password, port=DEFAULT_SSH_PORT):
    import asyncssh

    try:
        await trust_host_key(asyncssh, host, port)
        return await asyncio.wait_for(
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


async def upload(conn, data):
    """private temporary file on the remote computer, returns its path"""
    result = await conn.run("umask 077; mktemp", check=True)
    path = result.stdout.strip()
    await conn.run(
        f"umask 077; cat > {shlex.quote(path)}", input=data, encoding=None, check=True
    )
    return path


async def sudo(conn, user, password, command, limit=INSTALL_TIMEOUT):
    """runs command (a list) as root, output of the command. Nothing else is
    sent to stdin: with NOPASSWD sudo doesn't read the password line."""
    import asyncssh

    line = " ".join(shlex.quote(str(a)) for a in command)
    try:
        async with asyncio.timeout(limit):
            result = await conn.run(
                f"sudo -S -p '' {line}",
                input=password + "\n",
                stderr=asyncssh.STDOUT,
            )
    except asyncio.TimeoutError:
        raise RemoteError("took too long") from None
    out = str(result.stdout or "")
    if result.exit_status != 0:
        if "incorrect password" in out or "not in the sudoers" in out:
            raise RemoteError(f"user {user} has no sudo rights")
        lines = [x for x in out.splitlines() if x.strip()]
        raise RemoteError(lines[-1] if lines else f"exit code {result.exit_status}")
    return out


async def install_helper(host, user, password, helper_path, fhempy_user):
    """one-time setup on this computer via SSH to itself"""
    conn = await connect(host, user, password)
    async with conn:
        source = await asyncio.to_thread(Path(helper_path).read_bytes)
        path = await upload(conn, source)
        try:
            return await sudo(
                conn, user, password, ["python3", "-I", path, "install", fhempy_user]
            )
        finally:
            await conn.run(f"rm -f {shlex.quote(path)}")


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
            return {"network": str(iface.network), "ip": str(iface.ip)}
    return {}


async def site_info(conn):
    route = await conn.run("ip -4 -o route show default")
    addresses = await conn.run("ip -4 -o addr show")
    return parse_site(str(route.stdout or ""), str(addresses.stdout or ""))


async def setup_site(conn, user, password, config):
    """installs WireGuard on the other site and starts the tunnel"""
    path = await upload(conn, config.encode())
    target = f"/etc/wireguard/{SITE_INTERFACE}.conf"
    unit = f"wg-quick@{SITE_INTERFACE}"
    script = (
        # with NOPASSWD sudo leaves the password line on stdin
        "exec </dev/null; set -e; "
        "if ! command -v wg >/dev/null || ! command -v iptables >/dev/null; then "
        "export DEBIAN_FRONTEND=noninteractive; apt-get -q update >/dev/null; "
        "apt-get -y -q install wireguard-tools iptables >/dev/null; fi; "
        f"mkdir -p -m 700 /etc/wireguard; install -m 600 {shlex.quote(path)} "
        f"{target}; rm -f {shlex.quote(path)}; "
        f"systemctl enable --quiet {unit}; systemctl restart {unit}; "
        "echo started"
    )
    try:
        return await sudo(conn, user, password, ["sh", "-c", script])
    finally:
        await conn.run(f"rm -f {shlex.quote(path)}")
