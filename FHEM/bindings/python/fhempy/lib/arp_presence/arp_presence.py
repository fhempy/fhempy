"""
Based on iphonedetect from Home Assistant
From : https://community.home-assistant.io/t/iphone-device-tracker-on-linux/13698
Tracks iPhones by sending a udp message to port 5353.
An entry in the arp cache is then made and checked.
"""

import asyncio
import functools
import socket
import subprocess

from .. import fhem, generic, utils

HOME_STATES = {
    2: "REACHABLE",
    8: "DELAY",
    # 4: "STALE",
}

CONST_MESSAGE = b"Marco"
CONST_MESSAGE_PORT = 5353


class Host:
    """Host object with arp detection."""

    @staticmethod
    def find_with_ip():
        """Queries the network neighbours and lists found IP's"""
        state_filter = " nud " + " nud ".join(HOME_STATES.values()).lower()
        cmd = f"ip neigh show {state_filter}".split()
        neighbours = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        neighbours_ip = [_.split()[0] for _ in neighbours.stdout.splitlines()]
        return neighbours_ip

    @staticmethod
    def find_with_arp():
        """Queries the arp table and lists found IP's"""
        cmd = "arp -na"
        neighbours = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        neighbours_ip = [
            _.split()[1][1:-1]
            for _ in neighbours.stdout.splitlines()
            if _.count(":") == 5
        ]
        return neighbours_ip


class arp_presence(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval in seconds, default is 60s.",
            }
        }
        self.set_attr_config(attr_config)

        set_config = {"update": {}}
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define presence_my_iphone fhempy arp_presence IP"
        self.dev_ip = args[3]
        await self.setup_scanner()
        self.create_async_task(self.update_loop())

    async def set_update(self, hash, params):
        await self.update_once()

    def ping_device(self):
        """Send UDP message to probe device."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(1)
            s.sendto(CONST_MESSAGE, (self.dev_ip, CONST_MESSAGE_PORT))
        self.logger.debug(f"Probe sent to {self.dev_ip}")

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_interval)

    async def setup_scanner(self):
        """Set up the Host objects and return the update function."""

        if (
            subprocess.run("which ip", shell=True, stdout=subprocess.DEVNULL).returncode
            == 0
        ):
            self.logger.debug("Using 'IP' to find tracked devices")
            self._use_cmd_ip = True
        elif (
            subprocess.run(
                "which arp", shell=True, stdout=subprocess.DEVNULL
            ).returncode
            == 0
        ):
            self.logger.warn("Using 'ARP' to find tracked devices")
            self._use_cmd_ip = False
        else:
            self.logger.fatal("Can't get neighbours from host OS!")
            await fhem.readingsSingleUpdate(
                self.hash, "state", "no command arp and ip", 1
            )

    async def update_once(self):
        """Update all the hosts on every interval time."""
        await utils.run_blocking(functools.partial(self.ping_device))

        if self._use_cmd_ip:
            device_ips = Host.find_with_ip()
        else:
            device_ips = Host.find_with_arp()

        if self.dev_ip in device_ips:
            await fhem.readingsSingleUpdate(self.hash, "presence", "present", 1)
            await fhem.readingsSingleUpdate(self.hash, "state", "present", 1)
        else:
            await fhem.readingsSingleUpdate(self.hash, "presence", "absent", 1)
            await fhem.readingsSingleUpdate(self.hash, "state", "absent", 1)
