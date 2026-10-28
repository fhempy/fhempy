"""Helpers for the search() of a module's discovery.py.

    async def search(ctx):
        for data, ip in await ctx.udp_broadcast(48899, b"WIFIKIT-214028-READ"):
            ctx.found(ip=ip, name=data.decode())

search() may only import packages fhempy itself needs (asyncio, zeroconf,
pycryptodomex...), the requirements of the module aren't installed yet when
autodiscovery searches. ctx.found() takes the values for the templates of the
module's discovery rule.
"""

import asyncio
import functools
import socket

from .. import utils

BROADCAST = "255.255.255.255"


class _Collector(asyncio.DatagramProtocol):
    def __init__(self, ignore_payload=None):
        self.received = []
        self.ignore_payload = ignore_payload

    def datagram_received(self, data, addr):
        # our own broadcast comes back as well
        if self.ignore_payload is not None and data == self.ignore_payload:
            return
        self.received.append((data, addr[0], addr[1]))

    def error_received(self, exc):
        pass


def _udp_socket(port=0, broadcast=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        # the module itself might listen on the same port (e.g. tuya)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if broadcast:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)
    sock.bind(("", port))
    return sock


class SearchContext:
    def __init__(self, logger, found_callback):
        self.logger = logger
        self._found = found_callback

    def found(self, **values):
        """Reports a found device, values fill the templates of the rule."""
        self._found(values)

    async def udp_broadcast(self, port, payload, wait=3.0, listen_port=0):
        """Sends payload as broadcast, returns the answers [(data, ip)]."""
        loop = asyncio.get_running_loop()
        sock = _udp_socket(listen_port, broadcast=True)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _Collector(payload), sock=sock
        )
        try:
            transport.sendto(payload, (BROADCAST, port))
            await asyncio.sleep(wait)
        finally:
            transport.close()
        return [(data, ip) for data, ip, _ in protocol.received]

    async def udp_listen(self, ports, wait=8.0):
        """Listens for broadcasts devices send on their own,
        returns [(data, ip, port)]."""
        loop = asyncio.get_running_loop()
        transports = []
        protocols = []
        try:
            for port in ports:
                transport, protocol = await loop.create_datagram_endpoint(
                    _Collector, sock=_udp_socket(port)
                )
                transports.append(transport)
                protocols.append((port, protocol))
            await asyncio.sleep(wait)
        finally:
            for transport in transports:
                transport.close()
        return [
            (data, ip, port)
            for port, protocol in protocols
            for data, ip, _ in protocol.received
        ]

    async def hostname(self, ip):
        """Name of the device from the DNS of the router, '' if unknown."""
        try:
            name = await asyncio.wait_for(
                utils.run_blocking(functools.partial(socket.gethostbyaddr, ip)), 3
            )
        except (OSError, asyncio.TimeoutError):
            return ""
        return name[0].split(".")[0]
