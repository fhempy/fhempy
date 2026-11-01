"""Checks of the computer for the usual pairing pitfalls.

Pairing brand-new devices via Bluetooth fails silently if Bluetooth is
blocked (rfkill), the adapter doesn't exist or Node.js lacks the rights for
raw Bluetooth sockets. Thread devices can't be reached if Linux ignores the
route to the Thread network which the border router announces. Every check
returns a list of Problem with a short text and the command which fixes it.
All functions only read files, root is "/" except in tests.
"""

import errno
import os
import struct
from dataclasses import dataclass

CAP_NET_ADMIN = 12
CAP_NET_RAW = 13
# vfs_cap_data: magic_etc, then permitted/inheritable per 32 bit word
VFS_CAP_FLAGS_EFFECTIVE = 0x000001
THREAD_SYSCTL_FILE = "/etc/sysctl.d/90-fhempy-thread.conf"


@dataclass(frozen=True)
class Problem:
    text: str
    fix: str = ""

    def __str__(self):
        if self.fix:
            return f"{self.text} Fix: {self.fix}"
        return self.text


def _read(root, path):
    try:
        with open(os.path.join(root, path.lstrip("/")), encoding="utf-8") as f:
            return f.read().strip()
    except (OSError, UnicodeDecodeError):
        return None


def _listdir(root, path):
    try:
        return sorted(os.listdir(os.path.join(root, path.lstrip("/"))))
    except OSError:
        return None


def rfkill_problems(root="/"):
    problems = []
    for entry in _listdir(root, "/sys/class/rfkill") or []:
        base = f"/sys/class/rfkill/{entry}"
        if _read(root, base + "/type") != "bluetooth":
            continue
        if _read(root, base + "/hard") == "1":
            problems.append(
                Problem(
                    "Bluetooth is switched off by a hardware switch (rfkill).",
                    "switch it on at the device",
                )
            )
        elif _read(root, base + "/soft") == "1":
            problems.append(
                Problem(
                    "Bluetooth is blocked (rfkill).",
                    "sudo rfkill unblock bluetooth",
                )
            )
    # several rfkill entries of one adapter give the same text
    return list(dict.fromkeys(problems))


def adapter_problems(adapter, root="/"):
    adapters = _listdir(root, "/sys/class/bluetooth")
    if adapters is None:
        return [
            Problem(
                "No Bluetooth adapter found on this computer.",
                "connect a Bluetooth adapter or remove the attribute "
                "bluetooth_adapter",
            )
        ]
    adapters = [a for a in adapters if a.startswith("hci") and a[3:].isdigit()]
    if f"hci{adapter}" in adapters:
        return []
    if adapters:
        numbers = ", ".join(a[3:] for a in adapters)
        fix = f"set attr bluetooth_adapter to one of: {numbers}"
    else:
        fix = "connect a Bluetooth adapter or remove the attribute bluetooth_adapter"
    return [Problem(f"Bluetooth adapter hci{adapter} not found.", fix)]


def parse_capabilities(data):
    """Returns (permitted capability bits, effective flag) of a
    security.capability extended attribute"""
    if data is None or len(data) < 12:
        return 0, False
    magic_etc, permitted_lo = struct.unpack_from("<II", data, 0)
    permitted = permitted_lo
    if len(data) >= 20:
        (permitted_hi,) = struct.unpack_from("<I", data, 12)
        permitted |= permitted_hi << 32
    return permitted, bool(magic_etc & VFS_CAP_FLAGS_EFFECTIVE)


def _file_capabilities(path):
    """security.capability of the file, b"" if it has none, None if the
    file system can't tell"""
    try:
        return os.getxattr(path, "security.capability")
    except OSError as exc:
        if exc.errno == errno.ENODATA:
            return b""
        return None
    except AttributeError:
        # no extended attributes on this OS
        return None


def node_capability_problems(node, euid=None, read_capabilities=None):
    """Node.js needs cap_net_raw and cap_net_admin for Bluetooth (HCI
    sockets) unless fhempy runs as root"""
    if node is None:
        return []
    if euid is None:
        euid = os.geteuid() if hasattr(os, "geteuid") else 0
    if euid == 0:
        return []
    real = os.path.realpath(node)
    data = (read_capabilities or _file_capabilities)(real)
    if data is None:
        return []
    permitted, effective = parse_capabilities(data)
    needed = (1 << CAP_NET_RAW) | (1 << CAP_NET_ADMIN)
    if effective and permitted & needed == needed:
        return []
    return [
        Problem(
            "Node.js has no rights for Bluetooth (cap_net_raw, cap_net_admin). "
            "They are lost after every Node.js update.",
            f"sudo setcap cap_net_raw,cap_net_admin+eip {real}",
        )
    ]


def bluetooth_problems(adapter, node, root="/", euid=None, read_capabilities=None):
    """All reasons why pairing via Bluetooth won't work, empty if none found"""
    if adapter is None:
        return []
    return (
        rfkill_problems(root)
        + adapter_problems(adapter, root)
        + node_capability_problems(node, euid, read_capabilities)
    )


def default_interface(root="/"):
    """Interface of the IPv4 default route, None if unknown"""
    text = _read(root, "/proc/net/route")
    for line in (text or "").splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 2 and fields[1] == "00000000":
            return fields[0]
    return None


def has_thread_route(root="/"):
    """True if there is a route to a unique local network (fd../..) via a
    router, as border routers announce it for the Thread network. None if
    IPv6 routes can't be read."""
    text = _read(root, "/proc/net/ipv6_route")
    if text is None:
        return None
    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 10:
            continue
        dest, plen, nexthop = fields[0], int(fields[1], 16), fields[4]
        if dest.startswith("fd") and 8 <= plen <= 64 and nexthop.strip("0"):
            return True
    return False


def thread_route_problems(interface=None, root="/"):
    """Problem if no route to a Thread network exists, with the sysctl
    settings Linux needs to accept the route from the border router"""
    if has_thread_route(root) is not False:
        return []
    interface = interface or default_interface(root) or "eth0"
    conf = f"/proc/sys/net/ipv6/conf/{interface}"
    settings = []
    forwarding = _read(root, conf + "/forwarding") == "1"
    accept_ra = _read(root, conf + "/accept_ra")
    if accept_ra == "0" or (forwarding and accept_ra != "2"):
        settings.append(f"net.ipv6.conf.{interface}.accept_ra={2 if forwarding else 1}")
    max_plen = _read(root, conf + "/accept_ra_rt_info_max_plen")
    if max_plen is None or not max_plen.isdigit() or int(max_plen) < 64:
        settings.append(f"net.ipv6.conf.{interface}.accept_ra_rt_info_max_plen=64")
    text = (
        "Thread devices: there is no route to a Thread network (fd../64) on "
        "this computer."
    )
    if not settings:
        return [
            Problem(
                text + f" {interface} accepts the route, but no border router "
                "announces it here.",
                "put the border router into the same network segment as this "
                "computer (router advertisements don't pass most repeaters), "
                "check with 'ip -6 route | grep ^fd'",
            )
        ]
    lines = " ".join(f"'{s}'" for s in settings)
    return [
        Problem(
            text + " Linux ignores the route announced by the border router.",
            f"printf '%s\\n' {lines} | sudo tee {THREAD_SYSCTL_FILE} && "
            "sudo sysctl --system, then check with 'ip -6 route | grep ^fd'",
        )
    ]
