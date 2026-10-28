"""Finds the phones of the residents and creates them as ROOMMATE.

Network: every address of the local network gets a small UDP packet, the
kernel then knows the MAC of each device (neighbour table). Phones use a
private MAC (locally administered bit), it stays the same for each WiFi network
on iOS and Android. The name comes from the DNS of the router (DHCP host name)
or from mDNS (iPhones announce "_companion-link._tcp" with their name).

Bluetooth: phones only show up while their Bluetooth settings are open, the
fixed address of classic Bluetooth is found by a classic (BR/EDR) scan.

Tags: the BLE tag with by far the strongest signal is the one held next to
the Raspberry Pi.
"""

import asyncio
import functools
import ipaddress
import re
import socket
import time

import ifaddr

from .. import fhem, utils
from ..arp_presence.arp_presence import Host
from ..core.zeroconf import zeroconf
from .catalog import device_name
from .engine import define_arg

PROBE_PORT = 9
PROBE_WAIT = 3
MAX_HOSTS = 1024
COMPANION_TYPE = "_companion-link._tcp.local."
PHONE_NAMES = re.compile(
    r"iphone|ipad|android|galaxy|pixel|xiaomi|redmi|huawei|oneplus|nokia|"
    r"oppo|realme|motorola|moto-|sm-[a-z]",
    re.IGNORECASE,
)
# a tag held next to the Pi is much stronger than everything else
TAG_MIN_RSSI = -60
TAG_MARGIN = 10


def is_private_mac(mac):
    """Random MACs of phones have the locally administered bit set."""
    try:
        return bool(int(mac.split(":")[0], 16) & 0x02)
    except (ValueError, IndexError, AttributeError):
        return False


def local_networks():
    """IPv4 networks of this host, at most MAX_HOSTS addresses each."""
    networks = []
    for adapter in ifaddr.get_adapters():
        for address in adapter.ips:
            if not isinstance(address.ip, str):
                continue
            ip = ipaddress.ip_address(address.ip)
            if ip.is_loopback or ip.is_link_local:
                continue
            prefix = max(address.network_prefix, 22)
            network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
            if network.num_addresses <= MAX_HOSTS:
                networks.append((network, str(ip)))
    return networks


def _probe(networks):
    """One UDP packet to every address, the kernel resolves their MACs."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setblocking(False)
        for network, own_ip in networks:
            for host in network.hosts():
                if str(host) == own_ip:
                    continue
                try:
                    sock.sendto(b"fhempy", (str(host), PROBE_PORT))
                except OSError:
                    pass


def _hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0].split(".")[0]
    except OSError:
        return ""


class _CompanionListener:
    def __init__(self):
        self.names = []

    def add_service(self, zc, service_type, name):
        self.names.append(name)

    def update_service(self, zc, service_type, name):
        return

    def remove_service(self, zc, service_type, name):
        return


async def companion_names(logger, wait=3):
    """ip -> name of iPhones, iPads and Macs"""
    from zeroconf import IPVersion
    from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo

    names = {}
    try:
        azc = zeroconf.get_instance(logger).get_async_zeroconf()
        listener = _CompanionListener()
        browser = AsyncServiceBrowser(azc.zeroconf, [COMPANION_TYPE], listener)
        await asyncio.sleep(wait)
        await browser.async_cancel()
        for name in listener.names:
            info = AsyncServiceInfo(COMPANION_TYPE, name)
            if not await info.async_request(azc.zeroconf, 2000):
                continue
            for ip in info.parsed_addresses(IPVersion.V4Only):
                names[ip] = name.split("." + COMPANION_TYPE)[0]
    except Exception:
        logger.debug("mDNS name search failed", exc_info=True)
    return names


async def used_addresses(hash):
    """MACs, IPs and Bluetooth addresses of the existing presence devices"""
    cmd = (
        "join(' ', map { lc($main::defs{$_}{DEF} // '') } grep { "
        "($main::defs{$_}{FHEMPYTYPE} // '') =~ "
        "/^(arp_presence|bt_presence|ble_presence)$/ } keys %main::defs)"
    )
    return set(str(await fhem.sendCommandHash(hash, cmd) or "").split())


async def find_phones(hash, logger):
    """Phones in the local network: [{mac, ip, name, used}]"""
    networks = await utils.run_blocking(functools.partial(local_networks))
    await utils.run_blocking(functools.partial(_probe, networks))
    names_task = asyncio.create_task(companion_names(logger))
    await asyncio.sleep(PROBE_WAIT)
    neighbours = await utils.run_blocking(functools.partial(Host.find_with_netlink))
    mdns_names = await names_task
    used = await used_addresses(hash)

    phones = {}
    for (ip, _), (mac, state) in neighbours.items():
        if not mac or mac == "00:00:00:00:00:00" or state not in (2, 8, 4):
            continue
        phones[mac] = {"mac": mac, "ip": ip}
    hostnames = await asyncio.gather(
        *(
            asyncio.wait_for(
                utils.run_blocking(functools.partial(_hostname, p["ip"])), 3
            )
            for p in phones.values()
        ),
        return_exceptions=True,
    )
    result = []
    for phone, hostname in zip(phones.values(), hostnames):
        hostname = hostname if isinstance(hostname, str) else ""
        name = mdns_names.get(phone["ip"]) or hostname
        if not (is_private_mac(phone["mac"]) or PHONE_NAMES.search(name)):
            continue
        result.append(
            {
                **phone,
                "name": name or phone["ip"],
                "phone": bool(PHONE_NAMES.search(name)),
                "used": phone["mac"] in used or phone["ip"] in used,
            }
        )
    # most likely phones first
    result.sort(key=lambda p: (p["used"], not p["phone"], p["name"].lower()))
    return result


async def find_bluetooth_phones(hash, logger, scanner, seconds=20):
    """Classic Bluetooth devices which are visible right now:
    [{address, name, used}]"""
    from bleak import BleakScanner

    found = {}

    def detected(device, advertisement):
        name = advertisement.local_name or device.name or ""
        if name and not re.fullmatch(r"[0-9A-F]{2}([-:][0-9A-F]{2}){5}", name):
            found[device.address.upper()] = name

    async def scan():
        async with BleakScanner(
            detected, bluez={"filters": {"Transport": "bredr"}}
        ):
            await asyncio.sleep(seconds)

    if scanner is not None:
        async with scanner.paused():
            await scan()
    else:
        await scan()
    used = await used_addresses(hash)
    return [
        {"address": address, "name": name, "used": address.lower() in used}
        for address, name in sorted(found.items(), key=lambda x: x[1].lower())
    ]


async def find_tag(hash, scanner, seconds=15):
    """The BLE device with by far the strongest signal: {address, name, rssi}
    or None. Uses the shared scan."""
    strongest = {}

    def detected(device, advertisement):
        rssi = advertisement.rssi
        address = device.address.upper()
        if rssi > strongest.get(address, (-200, ""))[0]:
            strongest[address] = (
                rssi,
                advertisement.local_name or device.name or "",
            )

    scanner.add_callback(detected)
    try:
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            await asyncio.sleep(1)
    finally:
        scanner.remove_callback(detected)
    ranked = sorted(
        ((rssi, address, name) for address, (rssi, name) in strongest.items()),
        reverse=True,
    )
    if not ranked or ranked[0][0] < TAG_MIN_RSSI:
        return None
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < TAG_MARGIN:
        return None
    rssi, address, name = ranked[0]
    used = await used_addresses(hash)
    return {"address": address, "name": name, "rssi": rssi, "used": address.lower() in used}


async def residents_device(hash):
    """Name of the RESIDENTS device, created if there is none."""
    cmd = 'my @r = devspec2array("TYPE=RESIDENTS");; @r && defined($main::defs{$r[0]}) ? $r[0] : ""'
    name = str(await fhem.sendCommandHash(hash, cmd) or "").strip()
    if name:
        return name, None
    ret = await fhem.sendCommandHash(
        hash, "CommandDefine(undef, 'rgr_Residents RESIDENTS')"
    )
    return "rgr_Residents", ret


async def free_name(hash, name):
    cmd = (
        f"my $n = {fhem.perlString(name)};; my $c = $n;; my $i = 2;; "
        "while (defined($main::defs{$c})) { $c = $n . '_' . $i++ } $c"
    )
    return str(await fhem.sendCommandHash(hash, cmd) or name).strip()


async def create_resident(hash, person, mac="", bt_address=""):
    """ROOMMATE with the phone in the network (arp_presence) and via
    Bluetooth (bt_presence). Home if any of both sees the phone.
    Returns (error text or '', name of the ROOMMATE)."""
    if not mac and not bt_address:
        return "Choose the phone in the network or via Bluetooth", ""
    base = device_name(person, "")
    if not base:
        return "Please enter a name", ""
    residents, error = await residents_device(hash)
    if error:
        return str(error), ""
    presence = []
    if mac:
        name = await free_name(hash, f"presence_{base}_phone")
        ret = await fhem.CommandDefine(
            hash, f"{name} fhempy arp_presence {define_arg(mac)}"
        )
        if ret:
            return str(ret), ""
        presence.append(name)
    if bt_address:
        name = await free_name(hash, f"presence_{base}_bluetooth")
        ret = await fhem.CommandDefine(
            hash, f"{name} fhempy bt_presence {define_arg(bt_address)}"
        )
        if ret:
            return str(ret), ""
        presence.append(name)
    roommate = await free_name(hash, f"rr_{base}")
    ret = await fhem.sendCommandHash(
        hash,
        f"CommandDefine(undef, {fhem.perlString(f'{roommate} ROOMMATE {residents}')})",
    )
    if ret:
        return str(ret), ""
    commands = [
        f"{roommate} rr_presenceDevices {','.join(presence)}",
        f"{roommate} alias {person}",
    ]
    for command in commands:
        await fhem.CommandAttr(hash, command)
    return "", roommate


async def create_tag(hash, title, address):
    """Returns (error text or '', name of the ble_presence device)."""
    base = device_name(title, "tag")
    name = await free_name(hash, f"presence_{base}")
    ret = await fhem.CommandDefine(
        hash, f"{name} fhempy ble_presence {define_arg(address)}"
    )
    if ret:
        return str(ret), ""
    await fhem.CommandAttr(hash, f"{name} alias {title}")
    return "", name
