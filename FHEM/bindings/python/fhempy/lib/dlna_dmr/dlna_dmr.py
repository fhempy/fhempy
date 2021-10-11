"""Support for DLNA DMR (Device Media Renderer)."""
import asyncio
import datetime as dt
import functools
import logging
import time
from datetime import timedelta

import aiohttp
from async_upnp_client.aiohttp import AiohttpNotifyServer, AiohttpSessionRequester
from async_upnp_client.utils import async_get_local_ip
from async_upnp_client.profiles.dlna import DeviceState, DmrDevice
from fhempy.lib.generic import FhemModule

from .. import fhem
from ..discover_upnp.discover_upnp import ssdp

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


class dlna_dmr(FhemModule):

    event_handler = None

    def __init__(self, logger):
        super().__init__(logger)
        self.server = None
        self.device = None
        # set log level to ERROR for aiohttp.access to avoid INFO notify msgs
        logging.getLogger("aiohttp.access").setLevel(logging.ERROR)

        set_config = {
            "play": {
                "args": ["url"],
                "params": {"url": {"optional": True, "default": ""}},
            },
            "volume": {
                "args": ["volume"],
                "params": {"volume": {"format": "int"}},
                "options": "slider,0,1,100",
            },
            "mute": {"args": ["onoff"], "options": "on,off,toggle"},
            "pause": {},
            "next": {},
            "previous": {},
            "off": {},
            "stop": {},
            "seek": {"args": ["position"], "params": {"position": {"format": "int"}}},
            "speak": {
                "args": ["text"],
                "help": "Please use double quotes for the text to speak",
            },
        }
        self.set_set_config(set_config)

    async def found_device(self, upnp_device):
        if self.device:
            self.logger.error("Device exists already, do not create a new one")
            return

        self.upnp_device = upnp_device
        # build upnp/aiohttp requester
        session = aiohttp.ClientSession()
        requester = AiohttpSessionRequester(session, True)
        # ensure event handler has been started
        server_host = await async_get_local_ip()
        if server_host:
            server_host = server_host[1]
        else:
            self.logger.error(f"Failed to add device {self.device}")
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
        self.update_task = self.create_async_task(self.update())

    async def removed_device(self, upnp_device):
        await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
        self.update_task.cancel()
        await self.device.cleanup()
        self.device = None

    async def async_start_event_handler(
        self, server_host: str, server_port: int, requester
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
        self.logger.info(
            "UPNP/DLNA event handler listening, url: %s", self.server.callback_url
        )
        dlna_dmr.event_handler = self.server.event_handler
        return dlna_dmr.event_handler

    # FHEM Function
    async def Undefine(self, hash):
        await super().Undefine(hash)
        await ssdp.getInstance(self.logger).stop_search()
        if self.server:
            await self.server.stop_server()
        if self.device:
            await self.device.cleanup()
            del self.device
            self.device = None

    # FHEM Function
    async def Define(self, hash, args, argsh):
        """Set up DLNA DMR platform."""
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define device fhempy dlna_dmr <UUID>"

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon scene_scene")

        await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
        udn = args[3]
        self.hash["UDN"] = udn
        ssdp_filter = {
            "udn": udn,
            "service_type": "urn:schemas-upnp-org:device:MediaRenderer:1",
        }
        ssdp.getInstance(self.logger).register_listener(self, ssdp_filter)
        await ssdp.getInstance(self.logger).start_search()

    async def set_play(self, hash, params):
        if params["url"] == "":
            await self.device.dlna_dmrdevice.async_play()
        else:
            self.create_async_task(self.device.async_play_media(params["url"]))

    async def set_speak(self, hash, params):
        tts_url = (
            "http://translate.google.com/translate_tts?tl=de&client=tw-ob&q="
            + params["text"].replace(" ", "%20")
        )
        self.create_async_task(self.device.async_play_media(tts_url))

    async def set_volume(self, hash, params):
        self.create_async_task(
            self.device.dlna_dmrdevice.async_set_volume_level(params["volume"] / 100)
        )

    async def set_mute(self, hash, params):
        onoff = params["onoff"]
        if onoff == "on":
            onoff = True
        elif onoff == "off":
            onoff = False
        else:
            onoff = not (self.device.dlna_dmrdevice.is_volume_muted())
        await self.device.dlna_dmrdevice.async_mute_volume(onoff)

    async def set_pause(self, hash, params):
        await self.device.dlna_dmrdevice.async_pause()

    async def set_next(self, hash, params):
        await self.device.dlna_dmrdevice.async_next()

    async def set_previous(self, hash, params):
        await self.device.dlna_dmrdevice.async_previous()

    async def set_off(self, hash, params):
        await self.device.dlna_dmrdevice.async_stop()

    async def set_stop(self, hash, params):
        await self.device.dlna_dmrdevice.async_stop()

    async def set_seek(self, hash, params):
        t = params["position"]
        tdiff = time.gmtime(t)
        await self.device.dlna_dmrdevice.async_seek_rel_time(tdiff)

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
            except Exception:
                self.logger.exception("Failed to update")
            await asyncio.sleep(30)

    async def updateReadings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            if self.device.dlna_dmrdevice.volume_level:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash,
                    "volume",
                    round(self.device.dlna_dmrdevice.volume_level * 100),
                )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "media_position", self.device.dlna_dmrdevice.media_position
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "media_duration", self.device.dlna_dmrdevice.media_duration
            )
            # await fhem.readingsBulkUpdateIfChanged(self.hash, "media_image_url", self.device.dlna_dmrdevice.media_image_url)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "media_title", self.device.dlna_dmrdevice.media_title
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "is_volume_muted", self.device.dlna_dmrdevice.is_volume_muted
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", self.device.state
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def updateDeviceReadings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "name", self.upnp_device.name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "friendly_name", self.upnp_device.friendly_name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "manufacturer", self.upnp_device.manufacturer
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model_description", self.upnp_device.model_description
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model_name", self.upnp_device.model_name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model_number", self.upnp_device.model_number
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "udn", self.upnp_device.udn
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "device_url", self.upnp_device.device_url
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "device_type", self.upnp_device.device_type
            )
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
        try:
            await self._device.async_unsubscribe_services()
        except Exception:
            pass

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
                self.logger.debug("Subscription done, resubscribe in: " + str(timeout))
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
    def dlna_dmrdevice(self):
        return self._device

    @catch_request_errors()
    async def async_play_media(self, media_id, media_type=""):
        """Play a piece of media."""
        title = "FHEM"
        mime_type = media_type
        upnp_class = "object.item"

        # Stop current playing media
        if self._device.can_stop:
            await self._device.async_stop()

        # Queue media
        await self._device.async_set_transport_uri(
            media_id, title, mime_type, upnp_class
        )
        await self._device.async_wait_for_can_play()

        # If already playing, no need to call Play
        if self._device.state == DeviceState.PLAYING:
            return

        # Play it
        await self._device.async_play()

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
