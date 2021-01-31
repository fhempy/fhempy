import asyncio
import sys
from ipaddress import IPv4Address

import aiohttp
from async_upnp_client import UpnpFactory
from async_upnp_client.advertisement import UpnpAdvertisementListener
from async_upnp_client.aiohttp import AiohttpSessionRequester
from async_upnp_client.search import async_search as async_ssdp_search


# ssdp search class can be used by other modules as well
class ssdp:

    __instance = None

    @staticmethod
    def getInstance(logger):
        if ssdp.__instance is None:
            ssdp.__instance = ssdp(logger)
        return ssdp.__instance

    def __init__(self, logger):
        if ssdp.__instance is not None:
            raise Exception("ssdp already defined, use getInstance")
        self.logger = logger
        self.listeners = []
        self.listener = None
        self.search_task = None
        self.advertisement_task = None
        self.nr_started_searches = 0

        # build upnp/aiohttp requester
        self.session = aiohttp.ClientSession()
        self.requester = AiohttpSessionRequester(self.session, True)
        # create upnp device
        self.factory = UpnpFactory(self.requester)

    async def start_search(self):
        self.nr_started_searches += 1
        self.search_task = asyncio.create_task(self.search())

        if self.advertisement_task is None:
            self.advertisement_task = asyncio.create_task(self.advertisements())

    async def stop_search(self):
        self.nr_started_searches -= 1
        # stop search only when last client stops it
        if self.nr_started_searches == 0:
            await self.session.close()
            if self.search_task is not None:
                self.search_task.cancel()
            if self.advertisement_task is not None:
                self.advertisement_task.cancel()
            if self.listener is not None:
                await self.listener.async_stop()

    def register_listener(self, listener, ssdp_filter={"service_type": "ssdp:all"}):
        listenerFilter = {
            "listener": listener,
            "ssdp_filter": ssdp_filter,
            "found_devices": {},
        }
        self.listeners.append(listenerFilter)

    async def updated_device(self, udn):
        return

    async def create_device(self, msg, data):
        upnp_device = None
        try:
            if msg != "byebye":
                upnp_device = await self.factory.async_create_device(data["location"])
        except Exception:
            # upnp_device remains None
            pass
        return upnp_device

    async def handle_msg(self, msg, data):
        try:
            data = {key.lower(): str(value) for key, value in data.items()}
            usn = data["usn"]
            arr = usn.split("::")
            udn = arr[0]
            if len(arr) > 1:
                st = arr[1]
            else:
                st = ""
            self.logger.debug("found: " + usn)
            # filter for listeners
            for listenerFilter in self.listeners:
                listener = listenerFilter["listener"]
                ssdp_filter = listenerFilter["ssdp_filter"]
                filter_udn = None
                filter_st = None
                if "udn" in ssdp_filter:
                    filter_udn = ssdp_filter["udn"]
                if "service_type" in ssdp_filter:
                    filter_st = ssdp_filter["service_type"]
                if (udn == filter_udn or filter_udn is None) and (
                    st == filter_st or filter_st == "ssdp:all"
                ):
                    if usn not in listenerFilter["found_devices"] and msg == "alive":
                        self.logger.debug("create device: " + usn)
                        listenerFilter["found_devices"][usn] = await self.create_device(
                            msg, data
                        )
                        if listenerFilter["found_devices"][usn]:
                            self.logger.debug("found device: " + usn)
                            await listener.found_device(
                                listenerFilter["found_devices"][usn]
                            )
                    elif usn in listenerFilter["found_devices"] and msg == "byebye":
                        self.logger.debug("removed device: " + usn)
                        await listener.removed_device(
                            listenerFilter["found_devices"][usn]
                        )
                        del listenerFilter["found_devices"][usn]
        except Exception:
            self.logger.exception("Error in handle_msg")

    async def search(self):
        try:
            await self.search_once()
        except asyncio.CancelledError:
            pass

    async def search_once(self):
        timeout = 30
        service_type = "ssdp:all"
        source_ip = None
        if sys.platform == "win32" and not source_ip:
            self.logger.debug(
                'Running on win32 without --bind argument, forcing to "0.0.0.0"'
            )
            source_ip = (
                "0.0.0.0"  # force to IPv4 to prevent asyncio crash/WinError 10022
            )
        if source_ip:
            source_ip = IPv4Address(source_ip)

        async def on_response(data):
            await self.handle_msg("alive", data)

        try:
            await async_ssdp_search(
                service_type=service_type,
                source_ip=source_ip,
                timeout=timeout,
                async_callback=on_response,
            )
        except asyncio.CancelledError:
            self.logger.debug("search cancelled")

    async def advertisements(self):
        """Listen for advertisements."""
        try:
            source_ip = None
            if sys.platform == "win32" and not source_ip:
                self.logger.debug(
                    'Running on win32 without --bind argument, forcing to "0.0.0.0"'
                )
                source_ip = (
                    "0.0.0.0"  # force to IPv4 to prevent asyncio crash/WinError 10022
                )
            if source_ip:
                source_ip = IPv4Address(source_ip)

            async def on_alive(data):
                await self.handle_msg("alive", data)

            async def on_byebye(data):
                await self.handle_msg("byebye", data)

            async def on_update(data):
                return

            self.listener = UpnpAdvertisementListener(
                on_alive=on_alive,
                on_byebye=on_byebye,
                on_update=on_update,
                source_ip=source_ip,
            )
            await self.listener.async_start()
        except Exception:
            self.logger.error("Error in advertisements listener")
