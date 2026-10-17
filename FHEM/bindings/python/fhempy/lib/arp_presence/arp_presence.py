"""
Based on iphonedetect from Home Assistant
From : https://community.home-assistant.io/t/iphone-device-tracker-on-linux/13698
Tracks iPhones by sending a udp message to port 5353.
Linux neighbour states are read directly via Netlink (no external commands).
"""

import asyncio
import errno
import ipaddress
import os
import re
import socket
import struct
import time

from .. import fhem, generic

HOME_STATES = {
    2: "REACHABLE",
    8: "DELAY",
    # 4: "STALE",
}

DEBUG = 0                   # set to 1 to enable debug logging
SCAN_INTERVAL = 60          # default scan interval for new devices
USAGE = "Usage: define presence_my_device fhempy arp_presence IP_OR_MAC"
MAC_PATTERN = re.compile(
    r"(?:[0-9a-f]{12}|[0-9a-f]{4}(?:\.[0-9a-f]{4}){2}|"
    r"[0-9a-f]{2}([:-])(?:[0-9a-f]{2}\1){4}[0-9a-f]{2})",
    re.IGNORECASE,
)

CONST_MESSAGE = b"Marco"
CONST_MESSAGE_PORT = 5353
SCAN_TIMEOUT = 1.0
SCAN_POLL_INTERVAL = 0.1
NETLINK_TIMEOUT = 1.0

# Linux UAPI: linux/netlink.h, linux/rtnetlink.h, linux/neighbour.h.
NLMSG_ERROR = 2
NLMSG_DONE = 3
NLMSG_OVERRUN = 4
NLM_F_REQUEST = 0x01
NLM_F_DUMP_INTR = 0x10
NLM_F_DUMP = 0x300
RTM_NEWNEIGH = 28
RTM_GETNEIGH = 30
NDA_DST = 1
NDA_LLADDR = 2
IP_PKTINFO = 8  # Linux UAPI: linux/in.h; not exposed by all Python versions.
NLMSG_HEADER = struct.Struct("=IHHII")
NEIGH_HEADER = struct.Struct("=B3xiHBB")
ATTR_HEADER = struct.Struct("=HH")


class Host:
    """Host object with arp detection."""

    @staticmethod
    def find_with_netlink(timeout=NETLINK_TIMEOUT):
        """Read (IPv4, interface) -> (MAC, state), including stale entries.

        /proc/net/arp cannot distinguish REACHABLE/DELAY from stale entries.
        RTM_GETNEIGH only reads the table and needs no elevated privileges.
        """
        deadline = time.monotonic() + timeout
        for attempt in range(3):
            with socket.socket(
                socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE
            ) as sock:
                sock.settimeout(max(0.001, deadline - time.monotonic()))
                sock.bind((0, 0))
                payload = NEIGH_HEADER.pack(socket.AF_INET, 0, 0, 0, 0)
                request = NLMSG_HEADER.pack(
                    NLMSG_HEADER.size + len(payload),
                    RTM_GETNEIGH,
                    NLM_F_REQUEST | NLM_F_DUMP,
                    1,
                    0,
                ) + payload
                sock.sendto(request, (0, 0))
                try:
                    return Host._read_neighbours(sock, deadline)
                except OSError as exc:
                    # Table changes during a dump can make it incomplete.
                    if exc.errno != errno.EAGAIN or attempt == 2:
                        raise
        raise OSError(errno.EAGAIN, "Neighbour table dump interrupted")

    @staticmethod
    def _read_neighbours(sock, deadline):
        """Consume a complete multipart dump; never use a partial result."""
        neighbours = {}
        interrupted = False
        for kind, flags, payload in Host._dump_messages(sock, deadline):
            interrupted |= bool(flags & NLM_F_DUMP_INTR)
            if kind in (NLMSG_ERROR, NLMSG_DONE):
                Host._check_dump_reply(kind, payload, interrupted)
                if kind == NLMSG_DONE:
                    return neighbours
            elif kind == NLMSG_OVERRUN:
                raise OSError(errno.ENOBUFS, "Neighbour table dump overrun")
            elif kind == RTM_NEWNEIGH:
                entry = Host._decode_neighbour(payload)
                if entry is not None:
                    key, value = entry
                    neighbours[key] = value

    @staticmethod
    def _dump_messages(sock, deadline):
        """Receive complete kernel datagrams within the dump's deadline."""
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Neighbour table query timed out")
            sock.settimeout(remaining)
            data, _, flags, peer = sock.recvmsg(65536)
            if flags & socket.MSG_TRUNC:
                raise OSError(errno.ENOBUFS, "Neighbour table reply truncated")
            if peer[0] != 0:
                continue
            if not data:
                raise OSError(errno.EIO, "Empty neighbour table reply")
            yield from Host._netlink_messages(data)

    @staticmethod
    def _netlink_messages(data):
        """Decode aligned message frames belonging to this dump request."""
        offset = 0
        while offset < len(data):
            if len(data) - offset < NLMSG_HEADER.size:
                raise OSError(errno.EPROTO, "Invalid Netlink header")
            length, kind, flags, seq, _ = NLMSG_HEADER.unpack_from(data, offset)
            if length < NLMSG_HEADER.size or offset + length > len(data):
                raise OSError(errno.EPROTO, "Invalid Netlink message length")
            payload = data[offset + NLMSG_HEADER.size : offset + length]
            offset += (length + 3) & ~3
            if seq == 1:
                yield kind, flags, payload

    @staticmethod
    def _check_dump_reply(kind, payload, interrupted):
        """Validate ACK/DONE status before accepting a completed dump."""
        if len(payload) < 4 and (payload or kind == NLMSG_ERROR):
            raise OSError(errno.EPROTO, "Invalid Netlink error reply")
        error = struct.unpack_from("=i", payload)[0] if payload else 0
        if error:
            raise OSError(-error, os.strerror(-error))
        if kind == NLMSG_DONE and interrupted:
            raise OSError(errno.EAGAIN, "Neighbour table dump interrupted")

    @staticmethod
    def _decode_neighbour(payload):
        """Decode one IPv4 entry as (address, interface), (MAC, state)."""
        if len(payload) < NEIGH_HEADER.size:
            raise OSError(errno.EPROTO, "Invalid neighbour header")
        family, interface, state, _, _ = NEIGH_HEADER.unpack_from(payload)
        if family != socket.AF_INET:
            return None
        address = None
        mac = None
        for kind, value in Host._neighbour_attributes(payload):
            if kind == NDA_DST:
                if len(value) != 4:
                    raise OSError(errno.EPROTO, "Invalid IPv4 neighbour address")
                address = socket.inet_ntoa(value)
            elif kind == NDA_LLADDR and len(value) == 6:
                mac = value.hex(":")
        if address is None:
            return None
        return (address, interface), (mac, state)

    @staticmethod
    def _neighbour_attributes(payload):
        """Decode aligned attributes, excluding the attribute type flags."""
        offset = NEIGH_HEADER.size
        while offset < len(payload):
            if len(payload) - offset < ATTR_HEADER.size:
                raise OSError(errno.EPROTO, "Invalid neighbour attribute")
            length, kind = ATTR_HEADER.unpack_from(payload, offset)
            if length < ATTR_HEADER.size or offset + length > len(payload):
                raise OSError(errno.EPROTO, "Invalid neighbour attribute length")
            value = payload[offset + ATTR_HEADER.size : offset + length]
            offset += (length + 3) & ~3
            yield kind & 0x3FFF, value


class arp_presence(generic.FhemModule):
    """Track an IPv4 address or MAC using UDP probes and Linux neighbours."""

    def __init__(self, logger):
        """Initialize scan ownership and the default interval."""
        super().__init__(logger)
        self._scan_lock = asyncio.Lock()
        self._generation = 0
        self._target = None
        self._definition_error = "error: not initialized"
        self._attr_interval = SCAN_INTERVAL
        if DEBUG:
            self.logger.setLevel("DEBUG")

    @staticmethod
    def _parse_target(value):
        """Normalize one IPv4 or MAC address, without accessing the network."""
        try:
            return str(ipaddress.IPv4Address(value))
        except (ipaddress.AddressValueError, TypeError):
            if not MAC_PATTERN.fullmatch(value):
                raise ValueError("error: invalid IPv4 or MAC address") from None
            return bytes.fromhex(re.sub(r"[:.\-]", "", value)).hex(":")

    @staticmethod
    def validate_define(args, argsh):
        """Share argument validation with the binding's optional preflight hook."""
        if (
            len(args) != 4 or argsh
            or not isinstance(args[3], str) or not args[3].strip()
        ):
            return USAGE
        try:
            arp_presence._parse_target(args[3])
        except ValueError as exc:
            return str(exc)
        if not hasattr(socket, "AF_NETLINK") or not hasattr(socket, "NETLINK_ROUTE"):
            return "error: Linux Netlink required"
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        """Reset the device, validate one IP or MAC and start periodic scans."""
        redefined = getattr(self, "_is_redefine", False) or (
            self._target is not None
            and (args != self._defargs or argsh != self._defargsh)
        )
        self._is_redefine = False
        # A direct redefinition can reuse this instance. Cancel old tasks before
        # resetting readings; an old worker must not publish into the new DEF.
        await self.Undefine(hash)
        await super().Define(hash, args, argsh)
        if redefined:
            await self._update_readings("initialized")
        else:
            await fhem.readingsSingleUpdate(self.hash, "state", "initialized", 1)
        attr_config = {
            "interval": {
                "default": SCAN_INTERVAL,
                "format": "int",
                "help": f"Change interval in seconds, default is {SCAN_INTERVAL}s.",
            }
        }
        await self.set_attr_config(attr_config)
        await self.set_icon("people_sensor")

        set_config = {"update": {}}
        await self.set_set_config(set_config)

        error = self.validate_define(args, argsh)
        if error:
            self._definition_error = (
                "error: expected one IPv4 or MAC address" if error == USAGE else error
            )
            await self._publish_error(self._definition_error)
            return error
        self._target = self._parse_target(args[3])
        self._definition_error = None
        self.logger.debug("ARP presence initialized for %s", self._target)
        self.create_async_task(self.update_loop())

    async def Undefine(self, hash):
        """Invalidate outstanding results and cancel active module tasks."""
        self._generation += 1
        self._target = None
        self._definition_error = "error: not initialized"
        tasks = [task for task in self._tasks if not task.done()]
        if tasks:
            self.logger.debug("Stopping %s ARP presence tasks", len(tasks))
        await super().Undefine(hash)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _update_readings(self, state):
        """Publish presence and state in a single, safely closed transaction."""
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdate(self.hash, "presence", state)
            await fhem.readingsBulkUpdate(self.hash, "state", state)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def _publish_error(self, error):
        """Log an error and update state without changing presence."""
        self.logger.error("%s", error)
        await fhem.readingsSingleUpdate(self.hash, "state", error, 1)
        return error

    async def set_update(self, hash, params):
        """Schedule a manual scan only after a valid definition."""
        if self._target is None:
            return await self._publish_error(self._definition_error)
        # Do not keep the FHEM command waiting for ARP resolution.
        self.create_async_task(self.update_once())

    def ping_device(self, dev_ip, interface=0, timeout=SCAN_TIMEOUT):
        """Send UDP, selecting the neighbour's interface for a MAC probe."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            if interface:
                pktinfo = struct.pack("=I4s4s", interface, b"\0" * 4, b"\0" * 4)
                s.sendmsg(
                    [CONST_MESSAGE], [(socket.IPPROTO_IP, IP_PKTINFO, pktinfo)],
                    0, (dev_ip, CONST_MESSAGE_PORT),
                )
            else:
                s.sendto(CONST_MESSAGE, (dev_ip, CONST_MESSAGE_PORT))
        self.logger.debug("Probe sent to %s (interface %s)", dev_ip, interface)

    def scan_device(self, target=None):
        """Probe known addresses and confirm the target in a fresh table dump."""
        if target is None:
            target = self._target
        is_mac = ":" in target
        deadline = time.monotonic() + SCAN_TIMEOUT
        probed = set()
        if not is_mac:
            self.ping_device(target)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            matches = self._find_target_neighbours(target, is_mac)
            if is_mac:
                matches = self._probe_mac_neighbours(target, matches, probed, deadline)
                if not matches:
                    return False
            if any(state & home for state in matches.values() for home in HOME_STATES):
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(SCAN_POLL_INTERVAL, remaining))

    @staticmethod
    def _find_target_neighbours(target, is_mac):
        """Read a fresh table and select only entries for the IP or MAC."""
        # A started dump needs its own budget, even near the scan deadline.
        neighbours = Host.find_with_netlink()
        return {
            key: state for key, (mac, state) in neighbours.items()
            if (mac if is_mac else key[0]) == target
        }

    def _probe_mac_neighbours(self, target, matches, probed, deadline):
        """Probe each new MAC mapping, then read its state from a fresh dump."""
        while matches:
            unprobed = matches.keys() - probed
            if not unprobed:
                return matches
            for address, interface in unprobed:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return {}
                self.logger.debug("MAC %s maps to %s", target, address)
                self.ping_device(address, interface, remaining)
                probed.add((address, interface))
            # Do not accept a cached state/MAC from before the probe.
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return {}
            matches = self._find_target_neighbours(target, True)
        self.logger.debug("No IPv4 neighbour mapping for MAC %s", target)
        return {}

    async def update_loop(self):
        """Scan repeatedly using the currently configured interval."""
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_interval)

    async def update_once(self):
        """Scan off the event loop and coalesce overlapping updates."""
        if self._target is None:
            return await self._publish_error(self._definition_error)
        if self._scan_lock.locked():
            return
        async with self._scan_lock:
            target = self._target
            generation = self._generation
            try:
                self.logger.debug("scanning %s for presence ...", target)
                present = await asyncio.get_running_loop().run_in_executor(
                    None, self.scan_device, target
                )
            except OSError as exc:
                if generation != self._generation:
                    return
                self.logger.debug("Presence scan failed for %s: %s", target, exc)
                # A failed query says nothing about the device's presence.
                error = exc.strerror or str(exc) or "network scan failed"
                return await self._publish_error(f"error: {error}")
            if generation != self._generation:
                return
            state = "present" if present else "absent"
            self.logger.debug("%s is %s", target, state)
            await self._update_readings(state)
