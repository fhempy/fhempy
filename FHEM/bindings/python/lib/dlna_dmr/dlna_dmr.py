"""Support for DLNA DMR (Device Media Renderer)."""
import asyncio
import datetime as dt
from datetime import timedelta
import functools
import logging
import sys
import time

import aiohttp
from ipaddress import IPv4Address
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpNotifyServer, AiohttpSessionRequester
from async_upnp_client.profiles.dlna import DeviceState, DmrDevice
from async_upnp_client.aiohttp import get_local_ip
from async_upnp_client.search import async_search as async_ssdp_search
from async_upnp_client.advertisement import UpnpAdvertisementListener

from .. import fhem

SUPPORT_PAUSE = 1
SUPPORT_SEEK = 2
SUPPORT_VOLUME_SET = 4
SUPPORT_VOLUME_MUTE = 8
SUPPORT_PREVIOUS_TRACK = 16
SUPPORT_NEXT_TRACK = 32

SUPPORT_TURN_ON = 128
SUPPORT_TURN_OFF = 256
SUPPORT_PLAY_MEDIA = 512
SUPPORT_VOLUME_STEP = 1024
SUPPORT_SELECT_SOURCE = 2048
SUPPORT_STOP = 4096
SUPPORT_CLEAR_PLAYLIST = 8192
SUPPORT_PLAY = 16384
SUPPORT_SHUFFLE_SET = 32768
SUPPORT_SELECT_SOUND_MODE = 65536

DEFAULT_NAME = "DLNA Digital Media Renderer"
DEFAULT_LISTEN_PORT = 8301


def catch_request_errors():
    """Catch asyncio.TimeoutError, aiohttp.ClientError errors."""

    def call_wrapper(func):
        """Call wrapper for decorator."""

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            """Catch asyncio.TimeoutError, aiohttp.ClientError errors."""
            try:
                return await func(self, *args, **kwargs)
            except (asyncio.TimeoutError, aiohttp.ClientError):
                self.logger.error("Error during call %s", func.__name__)

        return wrapper

    return call_wrapper


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
        self.devices = {}
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
        if self.search_task:
            self.search_task.cancel()
        self.search_task = asyncio.create_task(self.search())

        if self.advertisement_task is None:
            self.advertisement_task = asyncio.create_task(
                self.advertisements())

    async def stop_search(self):
        self.nr_started_searches -= 1
        # stop search only when last client stops it
        if self.nr_started_searches == 0:
            await self.listener.async_stop()
            if self.search_task:
                self.search_task.cancel()
            if self.advertisement_task:
                self.advertisement_task.cancel()

    def register_listener(self, listener, ssdp_filter):
        listenerFilter = {
            "listener": listener,
            "ssdp_filter": ssdp_filter
        }
        self.listeners.append(listenerFilter)

    async def updated_device(self, udn):
        return

    async def search(self):
        while True:
            await self.search_once()
            await asyncio.sleep(300)

    async def search_once(self):
        timeout = 30
        service_type = "ssdp:all"
        source_ip = None
        if sys.platform == 'win32' and not source_ip:
            self.logger.debug(
                'Running on win32 without --bind argument, forcing to "0.0.0.0"')
            source_ip = '0.0.0.0'  # force to IPv4 to prevent asyncio crash/WinError 10022
        if source_ip:
            source_ip = IPv4Address(source_ip)

        async def on_response(data):
            await self.handle_msg("alive", data)

        await async_ssdp_search(service_type=service_type,
                                source_ip=source_ip,
                                timeout=timeout,
                                async_callback=on_response)

    async def create_device(self, msg, data):
        upnp_device = None
        try:
            if msg != "byebye":
                upnp_device = await self.factory.async_create_device(data['location'])
        except:
            # upnp_device remains None
            pass
        return upnp_device

    async def handle_msg(self, msg, data):
        data = {key.lower(): str(value) for key, value in data.items()}
        usn = data['usn']
        arr = usn.split("::")
        udn = arr[0]
        if len(arr) > 1:
            st = arr[1]
        else:
            st = ""
        self.logger.debug("found: " + usn)
        # filter for listeners
        for listenerFilter in self.listeners:
            listener = listenerFilter['listener']
            ssdp_filter = listenerFilter['ssdp_filter']
            filter_udn = None
            filter_st = None
            if "udn" in ssdp_filter:
                filter_udn = ssdp_filter['udn']
            if "service_type" in ssdp_filter:
                filter_st = ssdp_filter['service_type']
            if ((udn == filter_udn or filter_udn is None) and
              (st == filter_st or filter_st is None) and
              (usn not in self.devices)):
                self.logger.debug("create device: " + usn)
                upnp_device = await self.create_device(msg, data)
                if msg == "alive":
                    self.logger.debug("found device: " + usn)
                    self.devices[usn] = upnp_device
                    await listener.found_device(upnp_device)
                elif msg == "byebye":
                    self.logger.debug("removed device: " + usn)
                    del self.devices[usn]
                    await listener.removed_device(upnp_device)

    async def advertisements(self):
        """Listen for advertisements."""
        source_ip = None
        if sys.platform == 'win32' and not source_ip:
            self.logger.debug(
                'Running on win32 without --bind argument, forcing to "0.0.0.0"')
            source_ip = '0.0.0.0'  # force to IPv4 to prevent asyncio crash/WinError 10022
        if source_ip:
            source_ip = IPv4Address(source_ip)

        async def on_alive(data):
            await self.handle_msg("alive", data)

        async def on_byebye(data):
            await self.handle_msg("byebye", data)

        async def on_update(data):
            return

        self.listener = UpnpAdvertisementListener(on_alive=on_alive,
                                                  on_byebye=on_byebye,
                                                  on_update=on_update,
                                                  source_ip=source_ip)
        await self.listener.async_start()


class dlna_dmr:

    event_handler = None

    def __init__(self, logger):
        self.logger = logger
        self.server = None
        self.device = None
        # set log level to ERROR for aiohttp.access to avoid INFO notify msgs
        logging.getLogger("aiohttp.access").setLevel(logging.ERROR)

    async def found_device(self, upnp_device):
        if self.device:
            self.logger.error("Device exists already, do not create a new one")
            return

        self.upnp_device = upnp_device
        # build upnp/aiohttp requester
        session = aiohttp.ClientSession()
        requester = AiohttpSessionRequester(session, True)
        # ensure event handler has been started
        server_host = get_local_ip()
        server_port = DEFAULT_LISTEN_PORT
        event_handler = await self.async_start_event_handler(
            server_host, server_port, requester
        )

        # wrap with DmrDevice
        dlna_device = DmrDevice(self.upnp_device, event_handler)

        # create our own device
        self.device = DlnaDmrDevice(self, dlna_device)
        self.logger.debug("Adding device: %s", self.device)

        await self.updateDeviceReadings()
        await fhem.readingsSingleUpdate(self.hash, "state", "online", 1)
        self.update_task = asyncio.create_task(self.update())

    async def removed_device(self, upnp_device):
        await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
        self.update_task.cancel()
        self.device.cleanup()
        self.device = None

    async def async_start_event_handler(
        self,
        server_host: str,
        server_port: int,
        requester
    ):
        """Register notify view."""
        if dlna_dmr.event_handler:
            return dlna_dmr.event_handler
        # start event handler
        self.server = AiohttpNotifyServer(
            requester,
            listen_port=server_port,
            listen_host=server_host,
        )
        await self.server.start_server()
        self.logger.info("UPNP/DLNA event handler listening, url: %s",
                         self.server.callback_url)
        dlna_dmr.event_handler = self.server.event_handler
        return dlna_dmr.event_handler

    # FHEM Function
    async def Undefine(self, hash):
        self.logger.error("UNDEFINE CALLED")
        ssdp.getInstance(self.logger).stop_search()
        if self.server:
            await self.server.stop_server()
        if self.device:
            await self.device.cleanup()
            del self.device
            self.device = None

    # FHEM Function
    async def Define(self, hash, args, argsh):
        """Set up DLNA DMR platform."""
        self.hash = hash
        if len(args) < 4:
            return "define device PythonModule dlna_dmr <uuid>"

        await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
        udn = args[3]
        ssdp_filter = {
            "udn": udn,
            "service_type": "urn:schemas-upnp-org:device:MediaRenderer:1"
        }
        ssdp.getInstance(self.logger).register_listener(self, ssdp_filter)
        await ssdp.getInstance(self.logger).start_search()

    # FHEM Function
    async def Set(self, hash, args, argsh):
        if (len(args) < 2 or args[1] == "?"):
            return ("Unknown argument ?, choose one of "
                    "play volume:slider,0,1,100 mute:on,off,toggle pause:noArgs next:noArgs previous:noArgs "
                    "off:noArgs stop:noArgs seek")
        else:
            cmd = args[1]
            if cmd == "play":
                url = args[2]
                if url is None:
                    await self.device.dlna_dmrdevice.async_media_play()
                else:
                    asyncio.create_task(self.device.async_play_media("", url))
            elif cmd == "volume":
                new_vol = int(args[2])
                asyncio.create_task(
                    self.device.dlna_dmrdevice.async_set_volume_level(new_vol/100))
            elif cmd == "mute":
                onoff = args[2]
                if onoff == "on":
                    onoff = True
                elif onoff == "off":
                    onoff = False
                else:
                    onoff = not self.device.dlna_dmrdevice.is_volume_muted()
                self.device.dlna_dmrdevice.async_mute_volume(onoff)
            elif cmd == "pause":
                self.device.dlna_dmrdevice.async_pause()
            elif cmd == "next":
                self.device.dlna_dmrdevice.async_next()
            elif cmd == "previous":
                self.device.dlna_dmrdevice.async_previous()
            elif cmd == "off" or cmd == "stop":
                self.device.dlna_dmrdevice.async_stop()
            elif cmd == "seek":
                t = args[2]
                tdiff = time.gmtime(t)
                self.device.dlna_dmrdevice.async_seek_rel_time(tdiff)

    async def update(self):
        # get volume
        # service = self.upnp_device.service(
        #     'urn:schemas-upnp-org:service:RenderingControl:1')
        # get_volume = service.action('GetVolume')
        # await get_volume.async_call(InstanceID=0, Channel='Master')

        while True:
            try:
                await self.device.async_update()
                if self.device.available:
                    await self.updateReadings()
                else:
                    await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
            except:
                self.logger.exception("Failed to update")
            await asyncio.sleep(30)

    async def updateReadings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            if self.device.dlna_dmrdevice.volume_level:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "volume", round(self.device.dlna_dmrdevice.volume_level*100))
            await fhem.readingsBulkUpdateIfChanged(self.hash, "media_position", self.device.dlna_dmrdevice.media_position)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "media_duration", self.device.dlna_dmrdevice.media_duration)
            # await fhem.readingsBulkUpdateIfChanged(self.hash, "media_image_url", self.device.dlna_dmrdevice.media_image_url)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "media_title", self.device.dlna_dmrdevice.media_title)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "is_volume_muted", self.device.dlna_dmrdevice.is_volume_muted)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self.device.state)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def updateDeviceReadings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "name", self.upnp_device.name)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "friendly_name", self.upnp_device.friendly_name)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "manufacturer", self.upnp_device.manufacturer)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "model_description", self.upnp_device.model_description)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "model_name", self.upnp_device.model_name)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "model_number", self.upnp_device.model_number)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "udn", self.upnp_device.udn)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "device_url", self.upnp_device.device_url)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "device_type", self.upnp_device.device_type)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)


class DlnaDmrDevice:
    """Representation of a DLNA DMR device."""

    def __init__(self, dlna_dmrinstance, dmr_device):
        """Initialize DLNA DMR device."""
        self.dlna_dmrinstance = dlna_dmrinstance
        self.logger = self.dlna_dmrinstance.logger
        self._device = dmr_device

        self._available = False
        self._subscription_renew_time = None
        self._device.on_event = self._on_event

    async def cleanup(self):
        await self._device.async_unsubscribe_services()

    @property
    def available(self):
        """Device is available."""
        return self._available

    async def async_update(self):
        """Retrieve the latest data."""
        was_available = self._available

        try:
            await self._device.async_update()
            self._available = True
            self.logger.debug("Device available")
        except (asyncio.TimeoutError, aiohttp.ClientError):
            self._available = False
            self.logger.debug("Device unavailable")
            return

        # do we need to (re-)subscribe?
        now = dt.datetime.now()
        should_renew = (
            self._subscription_renew_time and now >= self._subscription_renew_time
        )
        if should_renew or not was_available and self._available:
            try:
                timeout = await self._device.async_subscribe_services()
                self.logger.debug(
                    "Subscription done, resubscribe in: " + str(timeout))
                self._subscription_renew_time = dt.datetime.now() + timeout / 2
            except (asyncio.TimeoutError, aiohttp.ClientError):
                self._available = False
                self.logger.debug("Could not (re)subscribe")

    def _on_event(self, service, state_variables):
        """State variable(s) changed, update readings."""
        self.logger.debug("event received")
        # create event as it is not async
        asyncio.create_task(self.dlna_dmrinstance.updateReadings())

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        supported_features = 0

        if self._device.has_volume_level:
            supported_features |= SUPPORT_VOLUME_SET
        if self._device.has_volume_mute:
            supported_features |= SUPPORT_VOLUME_MUTE
        if self._device.has_play:
            supported_features |= SUPPORT_PLAY
        if self._device.has_pause:
            supported_features |= SUPPORT_PAUSE
        if self._device.has_stop:
            supported_features |= SUPPORT_STOP
        if self._device.has_previous:
            supported_features |= SUPPORT_PREVIOUS_TRACK
        if self._device.has_next:
            supported_features |= SUPPORT_NEXT_TRACK
        if self._device.has_play_media:
            supported_features |= SUPPORT_PLAY_MEDIA
        if self._device.has_seek_rel_time:
            supported_features |= SUPPORT_SEEK

        return supported_features

    @property
    def dlna_dmrdevice(self):
        return self._device

    @catch_request_errors()
    async def async_play_media(self, media_type, media_id):
        """Play a piece of media."""
        title = "FHEM"
        mime_type = media_type
        upnp_class = "object.item"

        # Stop current playing media
        if self._device.can_stop:
            await self._device.async_media_stop()

        # Queue media
        await self._device.async_set_transport_uri(
            media_id, title, mime_type, upnp_class
        )
        await self._device.async_wait_for_can_play()

        # If already playing, no need to call Play
        if self._device.state == DeviceState.PLAYING:
            return

        # Play it
        await self._device.async_media_play()

    @property
    def state(self):
        """State of the player."""
        if not self._available:
            return "offline"

        if self._device.state is None:
            return "online"
        if self._device.state == DeviceState.PLAYING:
            return "playing"
        if self._device.state == DeviceState.PAUSED:
            return "paused"

        return "online"
