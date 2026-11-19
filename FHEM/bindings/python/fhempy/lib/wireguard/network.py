"""Finds out what the user would otherwise have to know about the network:
home network, router, public IP address, VPN network without conflicts and
the port forwarding in the router (UPnP)."""

import asyncio
import ipaddress
import socket
import struct

import aiohttp

PUBLIC_IP_URLS = ("https://api.ipify.org", "https://ipv4.icanhazip.com")
# VPN networks, the first one which doesn't overlap a local network is used
VPN_NETWORKS = [f"10.{a}.{b}.0/24" for a in (99, 123, 209) for b in (7, 42, 77)]
IGD_TYPES = (
    "urn:schemas-upnp-org:device:InternetGatewayDevice:2",
    "urn:schemas-upnp-org:device:InternetGatewayDevice:1",
)
UPNP_TIMEOUT = 4
# routers which don't accept unlimited leases get this one and it's renewed
UPNP_LEASE = 24 * 3600
# carrier grade NAT (shared address space of the provider) and private
# networks: the router itself is behind another NAT
NOT_PUBLIC = [
    ipaddress.IPv4Network(n)
    for n in ("100.64.0.0/10", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
]


def local_ip():
    """IPv4 address used to reach the internet, no packet is sent"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("192.0.2.1", 9))
            return sock.getsockname()[0]
        except OSError:
            return None


def local_networks():
    """all IPv4 networks of this computer"""
    import ifaddr

    networks = []
    for adapter in ifaddr.get_adapters():
        for ip in adapter.ips:
            if isinstance(ip.ip, str):
                try:
                    networks.append(
                        ipaddress.IPv4Interface(f"{ip.ip}/{ip.network_prefix}")
                    )
                except ValueError:
                    pass
    return networks


def default_gateway(path="/proc/net/route"):
    try:
        with open(path, encoding="ascii") as f:
            for line in f.readlines()[1:]:
                fields = line.split()
                if len(fields) > 3 and fields[1] == "00000000":
                    if int(fields[3], 16) & 2:
                        raw = struct.pack("<L", int(fields[2], 16))
                        return socket.inet_ntoa(raw)
    except (OSError, ValueError):
        pass
    return None


def home_network(ip, networks):
    """the network (e.g. 192.168.178.0/24) of the local IP address"""
    for interface in networks:
        if str(interface.ip) == ip and not interface.ip.is_loopback:
            return interface.network
    return None


def choose_vpn_network(networks):
    used = [n.network for n in networks]
    for candidate in VPN_NETWORKS:
        net = ipaddress.IPv4Network(candidate)
        if not any(net.overlaps(n) for n in used):
            return net
    return ipaddress.IPv4Network(VPN_NETWORKS[0])


def detect():
    """blocking, call with run_blocking"""
    ip = local_ip()
    networks = local_networks()
    home = home_network(ip, networks) if ip else None
    return {
        "local_ip": ip,
        "home_network": str(home) if home else None,
        "gateway": default_gateway(),
        "vpn_network": str(choose_vpn_network(networks)),
    }


def public_address_problem(router_ip):
    """why the router's internet address can't be reached from outside"""
    try:
        ip = ipaddress.IPv4Address(router_ip)
    except ValueError:
        return None
    if any(ip in net for net in NOT_PUBLIC):
        return (
            "your internet connection has no public IPv4 address "
            "(carrier grade NAT / DS-Lite)"
        )
    return None


async def public_ip(session):
    for url in PUBLIC_IP_URLS:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    text = (await resp.text()).strip()
                    return str(ipaddress.IPv4Address(text))
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            continue
    return None


class Router:
    """port forwarding with UPnP IGD (e.g. FRITZ!Box: "Permit independent
    port sharing for this device")"""

    SERVICES = (
        "urn:schemas-upnp-org:service:WANIPConnection:2",
        "urn:schemas-upnp-org:service:WANIPConnection:1",
        "urn:schemas-upnp-org:service:WANPPPConnection:1",
    )

    def __init__(self, logger):
        self.logger = logger
        self.service = None

    async def find(self, session):
        from async_upnp_client.aiohttp import AiohttpSessionRequester
        from async_upnp_client.client_factory import UpnpFactory
        from async_upnp_client.search import async_search

        locations = []

        async def found(headers):
            location = headers.get("location")
            if headers.get("st") in IGD_TYPES and location not in locations:
                locations.append(location)

        for search_target in IGD_TYPES:
            try:
                await async_search(
                    found, timeout=UPNP_TIMEOUT, search_target=search_target
                )
            except OSError as err:
                self.logger.debug(f"UPnP search failed: {err}")
            if locations:
                break
        factory = UpnpFactory(AiohttpSessionRequester(session, True))
        self.service = None
        for location in filter(None, locations):
            try:
                device = await factory.async_create_device(location)
            except Exception as err:  # noqa: BLE001 any broken router answer
                self.logger.debug(f"UPnP device {location}: {err}")
                continue
            for service_type in self.SERVICES:
                self.service = device.find_service(service_type)
                if self.service is not None:
                    return True
        return False

    async def call(self, name, **args):
        action = self.service.action(name)
        return await action.async_call(**args)

    async def external_ip(self):
        if self.service is None:
            return None
        try:
            result = await self.call("GetExternalIPAddress")
            return result.get("NewExternalIPAddress") or None
        except Exception as err:  # noqa: BLE001
            self.logger.debug(f"UPnP external IP: {err}")
            return None

    async def forward(self, port, ip, description):
        """forwards UDP port to ip:port, True if the router accepted it"""
        if self.service is None:
            return False
        for lease in (0, UPNP_LEASE):
            try:
                await self.call(
                    "AddPortMapping",
                    NewRemoteHost="",
                    NewExternalPort=port,
                    NewProtocol="UDP",
                    NewInternalPort=port,
                    NewInternalClient=ip,
                    NewEnabled=True,
                    NewPortMappingDescription=description,
                    NewLeaseDuration=lease,
                )
                return True
            except Exception as err:  # noqa: BLE001 routers answer in many ways
                self.logger.debug(f"UPnP port mapping (lease {lease}): {err}")
        return False

    async def remove(self, port):
        if self.service is None:
            return
        try:
            await self.call(
                "DeletePortMapping",
                NewRemoteHost="",
                NewExternalPort=port,
                NewProtocol="UDP",
            )
        except Exception as err:  # noqa: BLE001
            self.logger.debug(f"UPnP remove port mapping: {err}")
