import asyncio
import functools

import spotipy
from spotipy.oauth2 import CacheFileHandler
from aiohttp import web
from pyppeteer import launch

from .. import fhem, utils
from .. import generic


class spotify_connect_player(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        # Spotipy PKCE authenticator instance
        self.spotipy_pkce = None
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
        attr_config = {"player_name": {"default": "FHEM Web Player"}}
        self.set_attr_config(attr_config)

        self.set_config = {"start": {}, "stop": {}}
        self.set_set_config(self.set_config)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "disconnected")
        await fhem.readingsEndUpdate(hash, 1)
        await self.set_auth_url()
        self.create_async_task(self.connect_spotipy())

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
            user = self.spotipy.current_user()
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

    async def set_start(self, hash, params):
        self.create_async_task(self.run_spotify())

    async def run_spotify(self):
        async def handle(request):
            spotify_connect_code = """
                <script src="https://sdk.scdn.co/spotify-player.js"></script>
                <script>
                    window.onSpotifyWebPlaybackSDKReady = () => {
                    const token = '###SPOTIFY_ACCESS_TOKEN###';
                    const player = new Spotify.Player({
                        name: '###SPOTIFY_WEB_PLAYER_NAME###',
                        getOAuthToken: cb => { cb(token); }
                    });

                    // Error handling
                    player.addListener('initialization_error', ({ message }) => { console.error(message); });
                    player.addListener('authentication_error', ({ message }) => { console.error(message); });
                    player.addListener('account_error', ({ message }) => { console.error(message); });
                    player.addListener('playback_error', ({ message }) => { console.error(message); });

                    // Playback status updates
                    player.addListener('player_state_changed', state => { console.log(state); });

                    // Ready
                    player.addListener('ready', ({ device_id }) => {
                        console.log('Ready with Device ID', device_id);
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
                spotify_connect_code = spotify_connect_code.replace(
                    "###SPOTIFY_ACCESS_TOKEN###", access_token["access_token"]
                )
                spotify_connect_code = spotify_connect_code.replace(
                    "###SPOTIFY_WEB_PLAYER_NAME###", self._attr_player_name
                )
            return web.Response(text=spotify_connect_code)

        # start aiohttp server and run chrome headless
        self.app = web.Application()
        self.app.add_routes([web.get("/", handle)])

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "localhost", 8080)
        await self.site.start()

        self.browser = launch(
            {
                "ignoreDefaultArgs": ["--mute-audio"],
                "executablePath": "/usr/bin/chromium",
            }
        )
        page = await self.browser.newPage()
        await page.goto("http://localhost:8080/")

    async def set_stop(self, hash, params):
        self.create_async_task(self.stop_spotify())

    async def stop_spotify(self):
        # stop aiohttp server and stop chrome headless
        await self.runner.cleanup()
        await self.browser.close()
