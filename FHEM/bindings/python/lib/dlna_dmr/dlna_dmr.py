"""Support for DLNA DMR (Device Media Renderer)."""
import asyncio
import datetime as dt
from datetime import timedelta
import functools
import logging

import aiohttp
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpNotifyServer, AiohttpSessionRequester
from async_upnp_client.profiles.dlna import DeviceState, DmrDevice
from async_upnp_client.aiohttp import get_local_ip

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


class dlna_dmr:

    event_handler = None

    def __init__(self, logger):
        self.logger = logger
        self.server = None
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

    async def Undefine(self, hash):
        if self.server:
            await self.server.stop_server()
        if self.device:
            await self.device.cleanup()
            del self.device
            self.device = None

    async def Define(self, hash, args, argsh):
        """Set up DLNA DMR platform."""
        self.hash = hash
        if argsh.get("url") is not None:
            url = argsh.get("url")
            name = argsh.get("name")
        else:
            name = args[1]
            url = args[2]

        # build upnp/aiohttp requester
        session = aiohttp.ClientSession()
        requester = AiohttpSessionRequester(session, True)

        # ensure event handler has been started
        server_host = get_local_ip()
        server_port = DEFAULT_LISTEN_PORT
        event_handler = await self.async_start_event_handler(
            server_host, server_port, requester
        )

        # create upnp device
        factory = UpnpFactory(
            requester, disable_state_variable_validation=True)
        try:
            upnp_device = await factory.async_create_device(url)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return "Error while UPnP device setup"

        # wrap with DmrDevice
        dlna_device = DmrDevice(upnp_device, event_handler)

        # create our own device
        self.device = DlnaDmrDevice(self.logger, dlna_device, name)
        self.logger.debug("Adding device: %s", self.device)

        # get volume
        service = upnp_device.service('urn:schemas-upnp-org:service:RenderingControl:1')
        get_volume = service.action('GetVolume')
        await get_volume.async_call(InstanceID=0, Channel='Master')

        asyncio.create_task(self.update())

    async def Set(self, hash, args, argsh):
        if (len(args) < 2 or args[1] == "?"):
            return ("Unknown argument ?, choose one of "
                    "play")
        else:
            cmd = args[1]
            url = args[2]
            if cmd == "play" and url is not None:
                asyncio.create_task(self.device.async_play_media("", url))


    async def update(self):
        while True:
            try:
                await self.device.async_update()
                await fhem.readingsBeginUpdate(self.hash)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "volume", round(self.device.volume_level*100))
                await fhem.readingsBulkUpdateIfChanged(self.hash, "media_position", self.device.media_position)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "media_duration", self.device.media_duration)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "media_image_url", self.device.media_image_url)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "media_title", self.device.media_title)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "is_volume_muted", self.device.is_volume_muted)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "color_temperature_level", self.device.color_temperature_level)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "sharpness_level", self.device.sharpness_level)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "contrast_level", self.device.contrast_level)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "brightness_level", self.device.brightness_level)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", self.device.state)

                await fhem.readingsBulkUpdateIfChanged(self.hash, "name", self.device.name)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "friendly_name", self.device.dlna_dmrdevice.friendly_name)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "manufacturer", self.device.dlna_dmrdevice.manufacturer)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "model_description", self.device.dlna_dmrdevice.model_description)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "model_name", self.device.dlna_dmrdevice.model_name)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "model_number", self.device.dlna_dmrdevice.model_number)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "udn", self.device.dlna_dmrdevice.udn)
                # await fhem.readingsBulkUpdateIfChanged(self.hash, "device_url", self.device.dlna_dmrdevice.device_url)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "device_type", self.device.dlna_dmrdevice.device_type)
                await fhem.readingsEndUpdate(self.hash, 1)
            except:
                self.logger.exception("Failed to update")
            await asyncio.sleep(30)


class DlnaDmrDevice:
    """Representation of a DLNA DMR device."""

    def __init__(self, logger, dmr_device, name=None):
        """Initialize DLNA DMR device."""
        self.logger = logger
        self._device = dmr_device
        self._name = name

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
        return

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

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._device.volume_level

    @catch_request_errors()
    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        await self._device.async_set_volume_level(volume)

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._device.is_volume_muted

    @catch_request_errors()
    async def async_mute_volume(self, mute):
        """Mute the volume."""
        desired_mute = bool(mute)
        await self._device.async_mute_volume(desired_mute)

    @catch_request_errors()
    async def async_media_pause(self):
        """Send pause command."""
        if not self._device.can_pause:
            self.logger.debug("Cannot do Pause")
            return

        await self._device.async_pause()

    @catch_request_errors()
    async def async_media_play(self):
        """Send play command."""
        if not self._device.can_play:
            self.logger.debug("Cannot do Play")
            return

        await self._device.async_play()

    @catch_request_errors()
    async def async_media_stop(self):
        """Send stop command."""
        if not self._device.can_stop:
            self.logger.debug("Cannot do Stop")
            return

        await self._device.async_stop()

    @catch_request_errors()
    async def async_media_seek(self, position):
        """Send seek command."""
        if not self._device.can_seek_rel_time:
            self.logger.debug("Cannot do Seek/rel_time")
            return

        time = timedelta(seconds=position)
        await self._device.async_seek_rel_time(time)

    @catch_request_errors()
    async def async_play_media(self, media_type, media_id):
        """Play a piece of media."""
        title = "FHEM"
        mime_type = media_type
        upnp_class = "object.item"

        # Stop current playing media
        if self._device.can_stop:
            await self.async_media_stop()

        # Queue media
        await self._device.async_set_transport_uri(
            media_id, title, mime_type, upnp_class
        )
        await self._device.async_wait_for_can_play()

        # If already playing, no need to call Play
        if self._device.state == DeviceState.PLAYING:
            return

        # Play it
        await self.async_media_play()

    @catch_request_errors()
    async def async_media_previous_track(self):
        """Send previous track command."""
        if not self._device.can_previous:
            self.logger.debug("Cannot do Previous")
            return

        await self._device.async_previous()

    @catch_request_errors()
    async def async_media_next_track(self):
        """Send next track command."""
        if not self._device.can_next:
            self.logger.debug("Cannot do Next")
            return

        await self._device.async_next()

    @property
    def media_title(self):
        """Title of current playing media."""
        return self._device.media_title

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self._device.media_image_url

    @property
    def state(self):
        """State of the player."""
        if not self._available:
            return "off"

        if self._device.state is None:
            return "on"
        if self._device.state == DeviceState.PLAYING:
            return "playing"
        if self._device.state == DeviceState.PAUSED:
            return "paused"

        return "idle"

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._device.media_duration

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._device.media_position

    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid.
        Returns value from homeassistant.util.dt.utcnow().
        """
        return self._device.media_position_updated_at

    @property
    def name(self) -> str:
        """Return the name of the device."""
        if self._name:
            return self._name
        return self._device.name

    @property
    def unique_id(self) -> str:
        """Return an unique ID."""
        return self._device.udn
