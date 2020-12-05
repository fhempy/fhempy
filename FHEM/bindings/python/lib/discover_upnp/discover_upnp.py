"""
Starts a service to scan in intervals for new devices.

ATTENTION: This one should only be used for DLNA_DMR devices as the used library netdisco is deprecated!!!
"""
from datetime import timedelta
import json
import logging
import concurrent.futures
import functools
import asyncio
import aiohttp
import sys

from async_upnp_client.aiohttp import AiohttpNotifyServer, AiohttpSessionRequester
from async_upnp_client.advertisement import UpnpAdvertisementListener
from async_upnp_client import UpnpFactory
from async_upnp_client.search import async_search as async_ssdp_search
from ipaddress import IPv4Address

from .. import fhem

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
        self.search_task = None
        self.advertisement_task = None
        self.nr_started_searches = 0

        # build upnp/aiohttp requester
        session = aiohttp.ClientSession()
        self.requester = AiohttpSessionRequester(session, True)
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
            await self.listener.async_stop()
            if self.search_task:
                self.search_task.cancel()
            if self.advertisement_task:
                self.advertisement_task.cancel()

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
        except:
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
        except:
            self.logger.exception("Error in handle_msg")

    async def search(self):
        await self.search_once()

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
        except:
            self.logger.exception("Error in advertisements listener")


class discover_upnp:
    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.loop = asyncio.get_event_loop()
        self.create_devs = {}

    async def found_device(self, upnp_device):
        if upnp_device and upnp_device.udn:
            await fhem.readingsSingleUpdate(
                self.hash,
                upnp_device.udn.replace(":", ".")
                + "_"
                + upnp_device.device_type.replace(":", "."),
                upnp_device.friendly_name,
                0,
            )
            if upnp_device.device_type == "urn:schemas-upnp-org:device:MediaRenderer:1":
                self.create_devs[upnp_device.udn] = {
                    "name": "".join(filter(str.isalnum, upnp_device.friendly_name))
                    + "_"
                    + upnp_device.device_type.split(":")[-2],
                    "devname": "".join(filter(str.isalnum, upnp_device.friendly_name))
                    + "_"
                    + upnp_device.device_type.split(":")[-2],
                }
        # if upnp_device.device_type == "urn:schemas-upnp-org:device:MediaRenderer:1":
        #     if not (await fhem.checkIfDeviceExists(self.hash, "PYTHONTYPE", "dlna_dmr", "UDN", upnp_device.udn)):
        #         devname = devname = upnp_device.friendly_name + "_" + upnp_device.model_name
        #         devname = ''.join(filter(str.isalnum, devname))
        #         await fhem.CommandDefine(self.hash, devname + " PythonModule dlna_dmr " + upnp_device.udn)

    async def removed_device(self, upnp_device):
        return

    # FHEM Define
    async def Define(self, hash, args, argsh):
        """Start a discovery service."""
        self.hash = hash
        ssdp.getInstance(self.logger).register_listener(self)
        await ssdp.getInstance(self.logger).start_search()
        await fhem.readingsSingleUpdate(hash, "state", "active", 0)

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon rc_SEARCH")

        return ""

    # FHEM Set
    async def Set(self, hash, args, argsh):
        if len(args) < 2 or args[1] == "?":
            set_devs = []
            for dev in self.create_devs:
                set_devs.append(self.create_devs[dev]["name"])
            set_list = ""
            if len(set_devs) > 0:
                set_list = "create:" + ",".join(set_devs)
            return "Unknown argument ?, choose one of " + set_list
        else:
            cmd = args[1]
            if cmd == "create":
                for udn in self.create_devs:
                    if self.create_devs[udn]["name"] == args[2]:
                        await fhem.CommandDefine(
                            self.hash,
                            self.create_devs[udn]["devname"]
                            + " PythonModule dlna_dmr "
                            + udn,
                        )

    # FHEM Undefine
    async def Undefine(self, hash):
        ssdp.getInstance(self.logger).stop_search()
