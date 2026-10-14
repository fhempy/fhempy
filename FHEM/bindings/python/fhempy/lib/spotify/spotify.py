import asyncio
import functools

import requests
import spotipy
from spotipy.oauth2 import CacheFileHandler

from .. import fhem, generic, utils


class spotify(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        # Spotipy Spotify instance
        self.spotipy = None
        # Spotipy PKCE authenticator instance
        self.spotipy_pkce = None
        # Available Spotify Connect devices
        self.available_devices = {}
        self._last_data = {}
        self.spotipy_scope = (
            ""
            # Spotify scopes: https://developer.spotify.com/documentation/general/guides/scopes/
            # Listening history
            + "user-read-recently-played "
            + "user-top-read "
            + "user-read-playback-position "
            # Spotify connect
            + "user-read-playback-state "
            + "user-modify-playback-state "
            + "user-read-currently-playing "
            # Playback
            + "streaming "
            # Playlist
            + "playlist-read-private "
            + "playlist-read-collaborative "
            # Follow
            + "user-follow-read "
            # Library
            + "user-library-read "
            # User
            + "user-read-email "
            + "user-read-private"
        )
        self.loggedin = False
        # connection problems are logged once, not on every update interval
        self._connection_error_logged = False

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "update_status_interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60s.",
            },
            "update_devices_interval": {
                "default": 300,
                "format": "int",
                "help": "Change interval, default is 300s.",
            },
            "default_device": {"default": None, "help": "Set default device ID."},
            "spotify_connect": {
                "default": "off",
                "options": "on,off",
                "help": "Activate FHEM Connect Player within FHEM Web. Just open Spotify app and stream to FHEM Web Player.",
            },
        }
        await self.set_attr_config(attr_config)

        self.set_config = {
            "play": {
                "args": ["uri", "deviceid"],
                "function": "set_command",
                "params": {
                    "uri": {"default": None, "optional": False},
                    "deviceid": {"default": None, "optional": True},
                },
            },
            "pause": {
                "args": ["deviceid"],
                "function": "set_command",
                "params": {"deviceid": {"default": None, "optional": True}},
            },
            "next_track": {
                "args": ["deviceid"],
                "function": "set_command",
                "params": {"deviceid": {"default": None, "optional": True}},
            },
            "previous_track": {
                "args": ["deviceid"],
                "function": "set_command",
                "params": {"deviceid": {"default": None, "optional": True}},
            },
            "authcode": {"args": ["code"]},
            "update_devices": {},
            "status": {"function": "set_command"},
            "shuffle": {
                "args": ["onoff"],
                "params": {
                    "onoff": {"default": True, "optional": True},
                },
                "options": "on,off",
                "function": "set_command",
            },
            "volume": {
                "args": ["vol"],
                "params": {
                    "vol": {"optional": False},
                },
                "options": "slider,0,1,100",
                "function": "set_command",
            },
            "transfer_playback": {
                "args": ["deviceid"],
                "function": "set_command",
            },
        }
        await self.set_set_config(self.set_config)

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "disconnected")
        await fhem.readingsEndUpdate(hash, 1)
        await self.set_auth_url()
        self.create_async_task(self.connect_spotipy())

    async def FW_detailFn(self, hash, args, argsh):
        spotify_script = ""
        if self._attr_spotify_connect == "on":
            spotify_script = """
                <script src="https://sdk.scdn.co/spotify-player.js"></script>
                <script>
                    window.onSpotifyWebPlaybackSDKReady = () => {
                    const token = '###SPOTIFY_ACCESS_TOKEN###';
                    const player = new Spotify.Player({
                        name: 'FHEM Web Player',
                        getOAuthToken: cb => { cb(token); }
                    });

                    // Error handling
                    player.addListener('initialization_error', ({ message }) => { console.error(message); });
                    player.addListener('authentication_error', ({ message }) => { console.error(message); });
                    player.addListener('account_error', ({ message }) => { console.error(message); });
                    player.addListener('playback_error', ({ message }) => { console.error(message); });

                    // Playback status updates
                    player.addListener('player_state_changed', state => { 
                        console.log(state);
                        var div = document.getElementsByClassName("makeSelect")[0];
                        var dev = div.getAttribute("dev");
                        FW_cmd(FW_root + '?cmd=set ' + dev + ' status&XHR=1');
                    });

                    // Ready
                    player.addListener('ready', ({ device_id }) => {
                        console.log('Ready with Device ID', device_id);
                        $('<div id="idSpotifyConnect" class="makeTable help"></div>')
                            .insertBefore("div.makeSelect");
                        $("div#idSpotifyConnect").html("Spotify Connect active with device id: " + device_id + "<br>");
                    });

                    // Not Ready
                    player.addListener('not_ready', ({ device_id }) => {
                        console.log('Device ID has gone offline', device_id);
                    });

                    // Connect to the player!
                    player.connect();
                    };
                </script>
            """
            access_token = self.spotipy_pkce.get_cached_token()
            if access_token is not None:
                spotify_script = spotify_script.replace(
                    "###SPOTIFY_ACCESS_TOKEN###", access_token["access_token"]
                )
        detailfn = await super().FW_detailFn(hash, args, argsh)
        return spotify_script + str(detailfn)

    async def set_auth_url(self):
        # not sure if this is useful...
        x = "e92855a009"
        y = "e74eb69ba6609d3bfd7d"
        z = 90 + 6
        handler = CacheFileHandler(cache_path=f".{self.hash['NAME']}_spotify_token")
        self.spotipy_pkce = spotipy.oauth2.SpotifyPKCE(
            f"{x}{y}{str(z)}",
            "https://europe-west1-fhem-ga-connector.cloudfunctions.net/codelanding/start",
            scope=self.spotipy_scope,
            cache_handler=handler,
        )
        url = self.spotipy_pkce.get_authorize_url()
        url = (
            '<html><a href="'
            + url
            + '" target="_blank">Connect Spotify account (new window/tab)</a><br></html>'
        )
        await fhem.readingsSingleUpdate(self.hash, "login", url, 1)

    async def set_authcode(self, hash, params):
        code = params["code"]
        self.create_async_task(self.handle_authcode(code))

    async def handle_authcode(self, code):
        access_token = await utils.run_blocking(
            functools.partial(
                self.spotipy_pkce.get_access_token, code=code, check_cache=False
            )
        )
        await self.connect_spotipy()

    async def connect_spotipy(self):
        if self.spotipy_pkce.get_cached_token() is None:
            await fhem.readingsSingleUpdate(self.hash, "state", "login required", 1)
            return

        if self.spotipy is None:
            self.spotipy = spotipy.Spotify(auth_manager=self.spotipy_pkce)
            user = await utils.run_blocking(
                functools.partial(self.spotipy.current_user)
            )
            if user is not None:
                self.loggedin = True
                await fhem.readingsSingleUpdate(
                    self.hash,
                    "user",
                    user["display_name"] + " (" + user["email"] + ")",
                    1,
                )
                await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
                await self.update_devices()
                self.create_async_task(self.update_playback_loop())
                self.create_async_task(self.update_devices_loop())

    async def update_playback_loop(self):
        while True:
            await self.update_playback()
            await asyncio.sleep(self._attr_update_status_interval)

    async def update_devices_loop(self):
        while True:
            try:
                await self.update_devices()
                self._connection_ok()
            except Exception as exc:
                self._log_update_error("devices", exc)
            await asyncio.sleep(self._attr_update_devices_interval)

    async def set_update_devices(self, hash, params):
        self.create_async_task(self.update_devices())

    async def update_devices(self):
        if not self.loggedin:
            return
        # Query spotify for active devices
        devices_available = await utils.run_blocking(
            functools.partial(self.spotipy.devices)
        )

        self.available_devices = {}
        await fhem.CommandDeleteReading(self.hash, f"{self.hash['NAME']} device_.*")
        # update device list
        await fhem.readingsBeginUpdate(self.hash)
        for device in devices_available["devices"]:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "device_" + device["id"], device["name"]
            )
            self.available_devices[device["id"]] = device
            if self._attr_default_device is None:
                self._attr_default_device = device["id"]
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash,
                    "default_device",
                    device["name"] + " (" + device["id"] + ")",
                )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_attr_default_device(self, hash):
        if self._attr_default_device in self.available_devices:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash,
                "default_device",
                self._attr_default_device
                + " ("
                + self.available_devices[self._attr_default_device]["name"]
                + ")",
                1,
            )

    async def set_command(self, hash, params):
        if not self.loggedin:
            return "Please login first"

        cmd = params["cmd"]
        if cmd == "status":
            self.create_async_task(self.update_playback())
            return

        # without a device id Spotify uses the active device, which fails
        # with NO_ACTIVE_DEVICE if nothing is playing: use default_device
        device_id = params.get("deviceid") or self._attr_default_device

        if cmd == "pause":
            function = functools.partial(self.spotipy.pause_playback, device_id)
        elif cmd == "play":
            uri = params["uri"]
            if ":track:" in uri or ":episode:" in uri:
                function = functools.partial(
                    self.spotipy.start_playback, device_id=device_id, uris=[uri]
                )
            else:
                function = functools.partial(
                    self.spotipy.start_playback, device_id=device_id, context_uri=uri
                )
        elif cmd == "next_track":
            function = functools.partial(self.spotipy.next_track, device_id)
        elif cmd == "previous_track":
            function = functools.partial(self.spotipy.previous_track, device_id)
        elif cmd == "shuffle":
            function = functools.partial(
                self.spotipy.shuffle, params["onoff"] == "on", device_id
            )
        elif cmd == "volume":
            function = functools.partial(
                self.spotipy.volume, int(params["vol"]), device_id
            )
        elif cmd == "transfer_playback":
            function = functools.partial(self.spotipy.transfer_playback, device_id)
        else:
            return

        return await self._run_command(cmd, function)

    async def _run_command(self, cmd, function):
        try:
            await utils.run_blocking(function)
        except Exception as exc:
            msg = self._command_error_message(exc)
            self.logger.warning(f"{cmd} failed: {msg}")
            await fhem.readingsSingleUpdate(self.hash, "last_error", f"{cmd}: {msg}", 1)
            return f"{cmd} failed: {msg}"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "last_error", "none", 1)

    @staticmethod
    def _command_error_message(exc):
        if isinstance(exc, spotipy.SpotifyException):
            msg = exc.msg.split("\n")[-1].strip()
            if exc.reason:
                msg += f" ({exc.reason})"
            return msg
        return f"{type(exc).__name__}: {exc}"

    async def update_playback(self):
        try:
            status = await utils.run_blocking(
                functools.partial(self.spotipy.current_playback)
            )
            flat_status = utils.flatten_json(status)
            if self._last_data:
                del_readings = set(self._last_data) - set(flat_status)
            else:
                del_readings = {}
                await fhem.CommandDeleteReading(
                    self.hash, self.hash["NAME"] + " current_.*"
                )

            await fhem.readingsBeginUpdate(self.hash)
            for status_name in flat_status:
                reading = "current_" + status_name
                if "available_markets" in status_name:
                    continue
                if "device_volume_percent" == status_name:
                    reading = "volume"
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading, flat_status[status_name]
                )
            await fhem.readingsEndUpdate(self.hash, 1)

            # delete old readings which were not updated
            for del_reading in del_readings:
                await fhem.CommandDeleteReading(
                    self.hash, self.hash["NAME"] + " current_" + del_reading
                )
            self._last_data = flat_status
            self._connection_ok()
        except Exception as exc:
            self._log_update_error("status", exc)

    @staticmethod
    def _is_connection_error(exc):
        if isinstance(exc, (requests.exceptions.RequestException, OSError)):
            return True
        # spotipy raises SpotifyException after its retries for 429/5xx
        if isinstance(exc, spotipy.SpotifyException):
            status = exc.http_status or 0
            return status == 429 or status >= 500
        return False

    def _log_update_error(self, what, exc):
        if not self._is_connection_error(exc):
            self.logger.exception(f"Failed to update {what}")
        elif not self._connection_error_logged:
            self.logger.warning(
                f"Spotify not reachable ({type(exc).__name__}: {exc}), "
                "retrying in the background"
            )
            self._connection_error_logged = True
        else:
            self.logger.debug(f"Failed to update {what}: {exc}")

    def _connection_ok(self):
        if self._connection_error_logged:
            self.logger.info("Spotify is reachable again")
            self._connection_error_logged = False
