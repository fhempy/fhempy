
import asyncio
import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import pychromecast
from pychromecast.error import ChromecastConnectionError
from pychromecast.controllers.youtube import YouTubeController
import pychromecast.controllers.dashcast as dashcast

from .. import fhem

class googlecast:

    def __init__(self):
        self.cast = None
        self.loop = asyncio.get_event_loop()
        self.hash = None
        self.currPosTask = None
        self.checkConnectionTask = None
        self.updateReadingsRunning = 0
        self.connectionStateCache = ""

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        if (len(args) > 3):
            hash["CASTNAME"] = args[3]
        self.hash = hash

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "offline")
        await fhem.readingsBulkUpdateIfChanged(hash, "connection", "disconnected")
        await fhem.readingsEndUpdate(hash, 1)

        self.startDiscovery()

        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        try:
            pychromecast.stop_discovery(self.browser)
            if self.cast:
                self.cast.disconnect(blocking=False)
            self.loop.remove_reader(self.socketInLoop)
        except:
            pass

        try:
            self.checkConnectionTask.cancel()
        except:
            pass

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        if (len(args) < 2 or args[1] == "?"):
            return ("Unknown argument ?, choose one of "
                    "stop:noArg pause:noArg rewind:noArg skip:noArg quitApp:noArg "
                    "play playFavorite:1,2,3,4,5 volume:slider,0,1,100 seek "
                    "next:noArg prev:noArg subtitles:on,off "
                    "displayWebsite speak startApp "
                    "volUp:noArg volDown:noArg")
        else:
            action = args[1]
            if (action == "play"):
                if ("url" in argsh):
                    url = argsh['url']
                    videoid = self.extract_video_id(url)
                    if (videoid == None):
                        #get mime type
                        with urllib.request.urlopen(url) as response:
                            mime = response.info()
                            self.cast.play_media(url, mime)
                    else:
                        playlistid = self.extract_playlist_id(url)
                        self.loop.create_task(self.playYoutube(videoid, playlistid))
                else:
                    self.cast.media_controller.play()
            elif (action == "stop"):
                self.cast.media_controller.stop()
            elif (action == "pause"):
                self.cast.media_controller.pause()
            elif (action == "quitApp"):
                self.cast.quit_app()
            elif (action == "startApp"):
                if (len(args) > 2):
                    appId = args[2]
                    self.cast.start_app(appId)
                else:
                    return "Please specify app_id as parameter."
            elif (action == "skip"):
                self.cast.media_controller.skip()
            elif (action == "rewind"):
                self.cast.media_controller.rewind()
            elif (action == "seek"):
                position = 0
                if (len(args) > 2):
                    position = args[2]
                self.cast.media_controller.seek(position)
            elif (action == "next"):
                self.cast.media_controller.queue_next()
            elif (action == "prev"):
                self.cast.media_controller.queue_prev()
            elif (action == "volUp"):
                self.cast.volume_up()
            elif (action == "volDown"):
                self.cast.volume_down()
            elif (action == "subtitles"):
                onoff = "on"
                if (len(args) > 3):
                    onoff = args[2]
                if (onoff == "on"):
                    self.cast.media_controller.enable_subtitle(1)
                else:
                    self.cast.media_controller.disable_subtitle()
            elif (action == "volume"):
                vol = int(args[2])
                self.cast.set_volume(vol/100)
            elif (action == "speak"):
                txt = args[2]
                ttsUrl = "http://translate.google.com/translate_tts?tl=de&client=tw-ob&q=" + urllib.parse.quote(txt)
                self.cast.play_media(ttsUrl, "audio/mpeg")
            elif (action == "displayWebsite"):
                dashUrl = "https://fhem.de/"
                if (len(args) > 2):
                    dashUrl = args[2]
                self.loop.create_task(self.displayWebsite(dashUrl))

    async def displayWebsite(self, url):
        d = dashcast.DashCastController()
        self.cast.register_handler(d)
        d.load_url(url, reload_seconds=60)

    async def playYoutube(self, videoid, playlistid):
        yt = YouTubeController()
        self.cast.register_handler(yt)
        yt.send_message({"type": "getMdxSessionStatus"})
        # wait for mdx session id to be received (max 10s)
        i=0
        while i<10:
            if yt.is_session_ready():
                break
            else:
                await asyncio.sleep(1)
                i += 1
        yt.play_video(videoid, playlistid)

    def extract_video_id(self, url):
        # Examples:
        # - http://youtu.be/SA2iWivDJiE
        # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        # - http://www.youtube.com/embed/SA2iWivDJiE
        # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        query = urlparse(url)
        if query.hostname == 'youtu.be': return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch': return parse_qs(query.query)['v'][0]
            if query.path[:7] == '/embed/': return query.path.split('/')[2]
            if query.path[:3] == '/v/': return query.path.split('/')[2]
        # fail?
        return None

    def extract_playlist_id(self, url):
        query = urlparse(url)
        if "list" in parse_qs(query.query):
            return parse_qs(query.query)['list']
        return None


    def startDiscovery(self):
        self.socketInLoop = 0

        async def checkConnection():
            while True:
                try:
                    ccRunOnce()
                    currSock = self.cast.socket_client.get_socket()
                    if self.socketInLoop != currSock and currSock is not None and self.cast.socket_client.is_connected:
                        self.socketInLoop = currSock
                        self.loop.add_reader(self.socketInLoop, ccRunOnce)
                except ChromecastConnectionError:
                    logger.error("Connection to chromecast failed")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error("RunOnce: " + str(e))
                    traceback.print_exc()
                await asyncio.sleep(2)

        def ccRunOnce():
            self.cast.socket_client.run_once()

        async def initChromecast():
            # add status listener
            self.cast.register_connection_listener(self)
            self.cast.register_status_listener(self)
            # add media controller listener
            self.cast.media_controller.register_status_listener(self)

            if (self.checkConnectionTask):
                self.checkConnectionTask.cancel()
            self.checkConnectionTask = self.loop.create_task(checkConnection())

        def castFound(chromecast):
            if chromecast.name == self.hash["CASTNAME"]:
                logger.info("=> Discovered cast: " + chromecast.name)
                self.cast = chromecast
                self.loop.create_task(initChromecast())

        logger.debug("Start discovery")
        self.browser = pychromecast.get_chromecasts(blocking=False, tries=1, retry_wait=0.01, timeout=0.1, callback=castFound)

    def new_connection_status(self, status):
        # make sure that only one update reading task is running
        # wait for other updateReadingsTask to complete, this is needed due to new_connection_status not awaited
        logger.debug("new_connection_status: " + status.status)

        # prevent to many disconnect events
        if (status.status != self.connectionStateCache):
            self.connectionStateCache = status.status
            updateReadingsTask = self.loop.create_task(self.updateConnectionReadings(self.hash, status))

        if (status.status == "CONNECTED"):
            updateReadingsTask = self.loop.create_task(self.updateDeviceReadings(self.hash))


    def new_cast_status(self, status):
        # async, therefore it needs to be added to mainloop
        # wait for other updateReadingsTask to complete, this is needed due to new_cast_status not awaited
        logger.debug("new_cast_status")
        updateReadingsTask = self.loop.create_task(self.updateStatusReadings(self.hash, status))

    def new_media_status(self, status):
        #if (status.player_state == "PLAYING" and self.currPosTask == None and status.duration > 0):
        #    self.currPosTask = self.loop.create_task(self.updateCurrentPosition())
        #elif (status.player_state != "PLAYING"):
        #    if (self.currPosTask):
        #        self.currPosTask.cancel()
        #        self.currPosTask = None
        # async, therefore it needs to be added to mainloop
        # wait for other updateReadingsTask to complete, this is needed due to new_media_status not awaited
        logger.debug("new_media_status")
        updateReadingsTask = self.loop.create_task(self.updateMediaStatusReadings(self.hash, status))

    # this function is needed due to non asyncio callbacks from pychromecast library
    async def waitForUpdateReadings(self):
        i = 0
        while True:
            if self.updateReadingsRunning == 0:
                logger.debug("updateReadingsRunning = 1")
                self.updateReadingsRunning = 1
                break
            else:
                logger.debug("wait for updateReadingsRunning")
                i += 1
                if (i > 20):
                    logger.warning("waited more than 10s, stop waiting")
                    break
                await asyncio.sleep(0.5)

    async def updateConnectionReadings(self, hash, status):
        await self.waitForUpdateReadings()
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "connection", status.status.lower())
        if (status.status == "CONNECTED"):
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "online")
        else:
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "offline")
        await fhem.readingsEndUpdate(hash, 1)
        self.updateReadingsRunning = 0

    async def updateStatusReadings(self, hash, status):
        await self.waitForUpdateReadings()
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "volume", round(status.volume_level*100))
        await fhem.readingsBulkUpdateIfChanged(hash, "is_active_input", status.is_active_input)
        await fhem.readingsBulkUpdateIfChanged(hash, "is_stand_by", status.is_stand_by)
        await fhem.readingsBulkUpdateIfChanged(hash, "mute", status.volume_muted)
        await fhem.readingsBulkUpdateIfChanged(hash, "display_name", status.display_name)
        #await fhem.readingsBulkUpdateIfChanged(hash, "namespaces", status.namespaces)
        await fhem.readingsBulkUpdateIfChanged(hash, "session_id", status.session_id)
        await fhem.readingsBulkUpdateIfChanged(hash, "transport_id", status.transport_id)
        await fhem.readingsBulkUpdateIfChanged(hash, "status_text", status.status_text)
        await fhem.readingsBulkUpdateIfChanged(hash, "icon_url", status.icon_url)
        await fhem.readingsBulkUpdateIfChanged(hash, "app_id", status.app_id)
        await fhem.readingsEndUpdate(hash, 1)
        self.updateReadingsRunning = 0
        
    async def updateCurrentPosition(self):
        try:
            while True:
                await asyncio.sleep(30)
                currPos = self.cast.media_controller.status.adjusted_current_time
                await self.waitForUpdateReadings()
                await fhem.readingsBeginUpdate(hash)
                await fhem.readingsBulkUpdateIfChanged(self.hash, "mediaCurrentPosition", round(currPos))
                await fhem.readingsBulkUpdateIfChanged(self.hash, "mediaCurrentPosPercent", round(currPos/self.duration*100))
                await fhem.readingsEndUpdate(hash)
                self.updateReadingsRunning = 0
        except Exception as err:
            logger.error(err)

    async def updateMediaStatusReadings(self, hash, status):
        await self.waitForUpdateReadings()
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaPlayerState", status.player_state)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaContentId", status.content_id)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaContentType", status.content_type)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaDuration", status.duration)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaCurrentPosition", round(status.current_time))
        if (status.duration):
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaCurrentPosPercent", round(status.current_time/status.duration*100))
        else:
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaCurrentPosPercent", "")
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaStreamType", status.stream_type)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaTitle", status.title)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaSeriesTitle", status.series_title)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaSeason", status.season)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaEpisode", status.episode)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaArtist", status.artist)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaAlbum", status.album_name)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaAlbumArtist", status.album_artist)
        await fhem.readingsBulkUpdateIfChanged(hash, "mediaTrack", status.track)
        if (len(status.images) > 0):
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageUrl", status.images[0].url)
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageHeight", status.images[0].height)
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageWidth", status.images[0].width)
        else:
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageUrl", "")
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageHeight", "")
            await fhem.readingsBulkUpdateIfChanged(hash, "mediaImageWidth", "")

        if(status.player_state == "PLAYING"):
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "playing")
        elif(status.player_state == "BUFFERING"):
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "buffering")
        elif(status.player_state == "PAUSED"):
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "paused")
        else:
            if (await fhem.ReadingsVal(hash["NAME"], "connection", "failed") == "connected"):
                await fhem.readingsBulkUpdateIfChanged(hash, "state", "online")
            else:
                await fhem.readingsBulkUpdateIfChanged(hash, "state", "offline")
        await fhem.readingsEndUpdate(hash, 1)
        self.updateReadingsRunning = 0

    async def updateDeviceReadings(self, hash):
        await self.waitForUpdateReadings()
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "name", self.cast.name)
        await fhem.readingsBulkUpdateIfChanged(hash, "model_name", self.cast.model_name)
        await fhem.readingsBulkUpdateIfChanged(hash, "uuid", self.cast.uuid)
        await fhem.readingsBulkUpdateIfChanged(hash, "cast_type", self.cast.cast_type)
        #await fhem.readingsBulkUpdateIfChanged(hash, "uri", self.cast.uri)
        await fhem.readingsBulkUpdateIfChanged(hash, "ignore_cec", self.cast.ignore_cec)
        await fhem.readingsEndUpdate(hash, 1)
        self.updateReadingsRunning = 0