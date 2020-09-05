"""
Starts a service to scan in intervals for new devices.

ATTENTION: This one should only be used for DLNA_DMR devices as netdisco is deprecated!!!
"""
from datetime import timedelta
import json
import logging
import concurrent.futures
import functools
import asyncio

from netdisco.discovery import NetworkDiscovery
from .. import fhem

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class discover_upnp:

    def __init__(self):
        self.hash = None
        self.loop = asyncio.get_event_loop()

    # dlna_dmr
    async def dlna_dmr_exist_check(self, service, info):
        return True #await fhem.checkIfDeviceExists(self.hash, "PYTHONTYPE", "googlecast", "CASTNAME", info['properties']['fn'])

    async def dlna_dmr_define(self, service, info):
        return True #await fhem.CommandDefine(self.hash, info['properties']['md'].replace(" ", "_") + "_" + info['properties']['fn'].replace(" ", "_") +  " PythonModule googlecast '" + info['properties']['fn'] + "'")

    # FHEM Define
    async def Define(self, hash, args, argsh):
        """Start a discovery service."""
        self.hash = hash
        self.netdisco = NetworkDiscovery()
        self.already_discovered = set()
        asyncio.create_task(self.scan_devices())
        await fhem.readingsSingleUpdate(hash, "state", "active", 0)
        return ""


    async def new_service_found(self, service, info):
        """Handle a new service if one is found."""
        discovery_hash = json.dumps([service, info], sort_keys=True)
        if discovery_hash in self.already_discovered:
            logger.debug("Already discovered service %s %s.", service, info)
            return

        self.already_discovered.add(discovery_hash)

        exists = True
        try:
            exist_check_fct = service + "_exist_check"
            exists = await getattr(self, exist_check_fct)(service, info)
        except AttributeError:
            logger.info("Unknown service discovered: %s %s", service, info)
            return

        if exists is False:
            logger.info("Found new service: %s %s", service, info)
            define_fct = service + "_define"
            await getattr(self, define_fct)(service, info)


    async def scan_devices(self):
        """Scan for devices."""
        while True:
            try:
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    results = await self.loop.run_in_executor(
                        pool, functools.partial(self._discover))

                    for result in results:
                        asyncio.create_task(self.new_service_found(*result))
            except OSError:
                logger.error("Network is unreachable")

            # scan every 300s
            await asyncio.sleep(300)


    def _discover(self):
        """Discover devices."""
        results = []
        try:
            self.netdisco.scan()

            for disc in self.netdisco.discover():
                for service in self.netdisco.get_info(disc):
                    results.append((disc, service))

        finally:
            self.netdisco.stop()

        return results
