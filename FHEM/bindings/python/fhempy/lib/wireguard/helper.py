#!/usr/bin/python3 -I
"""Root helper of the fhempy module wireguard.

fhempy runs as user fhem. A WireGuard interface, IP forwarding and NAT need
root. fhem may only run this helper with sudo, it knows a few fixed
commands. The WireGuard configuration is written by the helper itself from
checked values (keys, port, addresses), fhempy never passes config text or
commands, so the PostUp lines can't be used to run something else as root.

Install it once as root, the device page of wireguard shows the command:
    sudo python3 .../wireguard/helper.py install fhem
This installs wireguard-tools (and iptables if missing), copies the helper to
/usr/local/sbin (owned by root, fhem can't change it) and allows fhem to run
it with sudo without password.

Only the Python standard library is used, it runs with the system Python.
"""

import base64
import binascii
import ipaddress
import json
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile

HELPER_VERSION = 2
# networks an "internet only" peer may not reach (home network, other
# peers and sites, the router admin pages)
PRIVATE_NETWORKS = (
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "100.64.0.0/10",
    "169.254.0.0/16",
)
INSTALL_PATH = "/usr/local/sbin/fhempy-wireguard"
SUDOERS_PATH = "/etc/sudoers.d/fhempy-wireguard"
INTERFACE = "wgfhempy"
CONFIG_DIR = "/etc/wireguard"
CONFIG_PATH = CONFIG_DIR + "/" + INTERFACE + ".conf"
SYSCTL_PATH = "/etc/sysctl.d/90-fhempy-wireguard.conf"
UNIT = "wg-quick@" + INTERFACE
PACKAGES = {"wg": "wireguard-tools", "iptables": "iptables"}
MAX_PEERS = 250

USER = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
IFNAME = re.compile(r"^[A-Za-z0-9_.-]{1,15}$")
ENV = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "DEBIAN_FRONTEND": "noninteractive",
}


class Invalid(Exception):
    pass


def run(args, **kwargs):
    # stdin may hold the sudo password line (NOPASSWD): never pass it on
    kwargs.setdefault("stdin", subprocess.DEVNULL)
    return subprocess.run(args, env=ENV, check=False, **kwargs)


def output(args):
    result = run(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.returncode, result.stdout.decode("utf-8", "replace")


def has_systemd():
    return shutil.which("systemctl") is not None and os.path.isdir(
        "/run/systemd/system"
    )


def check_key(value):
    """a WireGuard key: 32 bytes base64"""
    value = str(value or "")
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        raise Invalid("invalid key") from None
    if len(raw) != 32 or base64.b64encode(raw).decode() != value:
        raise Invalid("invalid key")
    return value


def check_peer_networks(values, vpn, used):
    """home networks of other sites behind a peer (site to site)"""
    if values is None:
        return []
    if not isinstance(values, list) or len(values) > 8:
        raise Invalid("invalid peer networks")
    networks = []
    for value in values:
        try:
            net = ipaddress.IPv4Network(str(value))
        except ValueError:
            raise Invalid("invalid peer network") from None
        if not net.is_private or net.prefixlen < 8 or net.overlaps(vpn):
            raise Invalid(f"invalid peer network {net}")
        if any(net.overlaps(other) for other in used):
            raise Invalid(f"peer network {net} overlaps another network")
        used.append(net)
        networks.append(str(net))
    return networks


def check_config(data):
    """the checked values of the configuration fhempy sends"""
    if not isinstance(data, dict):
        raise Invalid("configuration must be an object")
    port = data.get("port")
    if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
        raise Invalid("invalid port")
    try:
        address = ipaddress.IPv4Interface(str(data.get("address")))
    except ValueError:
        raise Invalid("invalid address") from None
    network = address.network
    if not network.is_private or not 16 <= network.prefixlen <= 29:
        raise Invalid("address must be in a private network /16 to /29")
    if address.ip in (network.network_address, network.broadcast_address):
        raise Invalid("invalid address")
    peers = data.get("peers") or []
    if not isinstance(peers, list) or len(peers) > MAX_PEERS:
        raise Invalid("invalid peers")
    checked, ips, keys, used = [], {address.ip}, set(), [network]
    for peer in peers:
        if not isinstance(peer, dict):
            raise Invalid("invalid peer")
        try:
            ip = ipaddress.IPv4Address(str(peer.get("ip")))
        except ValueError:
            raise Invalid("invalid peer address") from None
        if (
            ip not in network
            or ip in ips
            or ip in (network.network_address, network.broadcast_address)
        ):
            raise Invalid(f"invalid peer address {ip}")
        networks = check_peer_networks(peer.get("networks"), network, used)
        public = check_key(peer.get("public_key"))
        if public in keys:
            raise Invalid("duplicate peer key")
        isolated = peer.get("isolated", False)
        if not isinstance(isolated, bool):
            raise Invalid("invalid peer isolated")
        ips.add(ip)
        keys.add(public)
        checked.append(
            {
                "public_key": public,
                "preshared_key": check_key(peer.get("preshared_key")),
                "ip": str(ip),
                "networks": networks,
                "isolated": isolated,
            }
        )
    return {
        "private_key": check_key(data.get("private_key")),
        "port": port,
        "address": str(address),
        "network": str(network),
        "peers": checked,
    }


def default_route():
    """network interface (NAT goes out there) and router of the default
    route, the router is None if unknown"""
    code, out = output(["ip", "-4", "route", "show", "default"])
    if code == 0:
        for line in out.splitlines():
            words = line.split()
            if "dev" in words[:-1]:
                name = words[words.index("dev") + 1]
                if IFNAME.match(name) and name != INTERFACE:
                    return name, router_address(words)
    raise Invalid("no default route, is this computer connected to the router?")


def router_address(words):
    if "via" not in words[:-1]:
        return None
    try:
        ip = ipaddress.IPv4Address(words[words.index("via") + 1])
    except ValueError:
        return None
    return str(ip) if ip.is_private else None


def nat_rules(action, networks, out):
    """iptables commands of PostUp (-I) / PostDown (-D): forwarding between
    VPN and home network, NAT so that the home network needs no route to the
    VPN, MSS clamping against hanging connections (smaller MTU of the VPN)"""
    rules = [
        f"iptables -{action} FORWARD -i %i -j ACCEPT",
        f"iptables -{action} FORWARD -o %i -j ACCEPT",
    ]
    rules += [
        f"iptables -t nat -{action} POSTROUTING -s {net} -o {out} -j MASQUERADE"
        for net in networks
    ]
    rules.append(
        f"iptables -t mangle -{action} FORWARD -p tcp --tcp-flags SYN,RST SYN "
        "-j TCPMSS --clamp-mss-to-pmtu"
    )
    return rules


def isolation_rules(action, peer, router):
    """iptables commands for an "internet only" peer: it may go to the
    internet, but not to private networks (home, other peers, sites) and not
    to this computer, only DNS of the router. Nobody may open connections to
    it. -I puts later rules first: the DNS exception before the drops."""
    sources = [f"{peer['ip']}/32"] + peer["networks"]
    rules = []
    for src in sources:
        rules += [
            f"iptables -{action} FORWARD -i %i -s {src} -d {net} -j DROP"
            for net in PRIVATE_NETWORKS
        ]
        rules += [
            f"iptables -{action} INPUT -i %i -s {src} -j DROP",
            f"iptables -{action} FORWARD -o %i -d {src} -m conntrack "
            "--ctstate NEW -j DROP",
        ]
        if router:
            rules += [
                f"iptables -{action} FORWARD -i %i -s {src} -d {router} "
                f"-p {proto} --dport 53 -j ACCEPT"
                for proto in ("udp", "tcp")
            ]
    return rules


def render(config, out, router=None):
    """wg-quick configuration, only from checked values"""
    lines = [
        "# written by fhempy (module wireguard), changes are overwritten",
        "[Interface]",
        f"Address = {config['address']}",
        f"ListenPort = {config['port']}",
        f"PrivateKey = {config['private_key']}",
        "PostUp = sysctl -q -w net.ipv4.ip_forward=1",
    ]
    networks = [config["network"]]
    for peer in config["peers"]:
        networks += peer["networks"]
    lines += ["PostUp = " + r for r in nat_rules("I", networks, out)]
    lines += ["PostDown = " + r for r in nat_rules("D", networks, out)]
    for peer in config["peers"]:
        if peer.get("isolated"):
            lines += ["PostUp = " + r for r in isolation_rules("I", peer, router)]
            lines += ["PostDown = " + r for r in isolation_rules("D", peer, router)]
    for peer in config["peers"]:
        lines += [
            "",
            "[Peer]",
            f"PublicKey = {peer['public_key']}",
            f"PresharedKey = {peer['preshared_key']}",
            "AllowedIPs = " + ", ".join([f"{peer['ip']}/32"] + peer["networks"]),
        ]
    return "\n".join(lines) + "\n"


def interface_section(text):
    return text.split("[Peer]", 1)[0]


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def write_private(path, text):
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".fhempy")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def interface_up():
    return output(["wg", "show", INTERFACE])[0] == 0


def sync_peers():
    """new peers without restart: open connections stay"""
    code, stripped = output(["wg-quick", "strip", INTERFACE])
    if code != 0:
        return code
    fd, tmp = tempfile.mkstemp(prefix="fhempy-wg")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(stripped)
        return run(["wg", "syncconf", INTERFACE, tmp]).returncode
    finally:
        os.remove(tmp)


def start(restart):
    if has_systemd():
        run(["systemctl", "enable", "--quiet", UNIT])
        action = "restart" if restart else "start"
        return run(["systemctl", action, UNIT]).returncode
    if restart:
        run(["wg-quick", "down", INTERFACE], stderr=subprocess.DEVNULL)
    return run(["wg-quick", "up", INTERFACE]).returncode


def cmd_apply(stdin):
    """writes the configuration and starts or updates the interface"""
    try:
        config = check_config(json.loads(stdin.read() or "null"))
        out, router = default_route()
    except (Invalid, ValueError) as exc:
        sys.exit(f"invalid configuration: {exc}")
    for tool in PACKAGES:
        if shutil.which(tool, path=ENV["PATH"]) is None:
            sys.exit(f"{tool} is missing, run the install command again")
    old = read(CONFIG_PATH)
    new = render(config, out, router)
    write_private(CONFIG_PATH, new)
    if interface_up():
        if interface_section(old) != interface_section(new):
            return start(restart=True)
        if old != new:
            return sync_peers()
        return 0
    return start(restart=False)


def cmd_status():
    """wg show dump of the interface, exit code 3 if it isn't running"""
    code, out = output(["wg", "show", INTERFACE, "dump"])
    if code != 0:
        print("not running")
        return 3
    print(out, end="")
    return 0


def cmd_stop():
    if has_systemd():
        run(["systemctl", "disable", "--quiet", UNIT])
        run(["systemctl", "stop", UNIT])
    if interface_up():
        run(["wg-quick", "down", INTERFACE])
    return 0


def install_packages():
    missing = [
        package
        for tool, package in PACKAGES.items()
        if shutil.which(tool, path=ENV["PATH"]) is None
    ]
    if not missing:
        return
    if shutil.which("apt-get", path=ENV["PATH"]) is None:
        sys.exit("please install " + " ".join(missing) + " first")
    print("Installing " + " ".join(missing) + " ...")
    run(["apt-get", "-q", "update"], stdout=subprocess.DEVNULL)
    if run(["apt-get", "-y", "-q", "install"] + missing).returncode != 0:
        sys.exit("apt-get install " + " ".join(missing) + " failed")


def cmd_install(user):
    if not USER.match(user):
        sys.exit(f"invalid user name {user}")
    try:
        user = pwd.getpwnam(user).pw_name
    except KeyError:
        sys.exit(f"user {user} does not exist")
    install_packages()
    source = os.path.realpath(__file__)
    if source != INSTALL_PATH:
        tmp = INSTALL_PATH + ".new"
        shutil.copyfile(source, tmp)
        os.chown(tmp, 0, 0)
        os.chmod(tmp, 0o700)
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
    # IP forwarding also after a reboot before the interface is up
    with open(SYSCTL_PATH, "w", encoding="utf-8") as f:
        f.write("# fhempy module wireguard\nnet.ipv4.ip_forward = 1\n")
    print(f"Installed {INSTALL_PATH}, {user} may run it with sudo.")
    return 0


def cmd_uninstall():
    cmd_stop()
    for path in (CONFIG_PATH, SYSCTL_PATH, SUDOERS_PATH, INSTALL_PATH):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    print("Removed the WireGuard server of fhempy and its helper.")
    return 0


def main(argv):
    if not argv:
        sys.exit("usage: version|apply|status|stop|install USER|uninstall")
    cmd, args = argv[0], argv[1:]
    if cmd == "version":
        print(HELPER_VERSION)
        return 0
    if os.geteuid() != 0:
        sys.exit("must run as root (sudo)")
    commands = {
        "apply": lambda: cmd_apply(sys.stdin),
        "status": cmd_status,
        "stop": cmd_stop,
        "uninstall": cmd_uninstall,
    }
    if cmd in commands and not args:
        return commands[cmd]()
    if cmd == "install" and len(args) == 1:
        return cmd_install(args[0])
    sys.exit(f"unknown command {' '.join(argv)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
