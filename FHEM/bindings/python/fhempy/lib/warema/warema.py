import asyncio
import functools

from warema_wms import Shade, WmsController

from .. import fhem, utils
from ..generic import FhemModule


class warema(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.hash = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        
        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60.",
            },
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "status": {},
            "up": {},
            "down": {},
            "position": {"args": ["position"], "options": "slider,0,11,100"},
        }
        await self.set_set_config(set_config)

        self.hash = hash
        if len(args) < 5:
            return "Usage: define warema_fhempy fhempy warema <IP> <channel>"

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon fts_window_1w")
        if await fhem.AttrVal(self.hash["NAME"], "devStateIcon", "") == "":
            devStateIcon = "0:fts_shutter_10\@green 100:fts_shutter_100\@green s/[0-9]|1\d.*:fts_shutter_90 s/[0-9]|2\d.*:fts_shutter_80 s/[0-9]|3\d.*:fts_shutter_70 s/[0-9]|4\d.*:fts_shutter_60 s/[0-9]|5\d.*:fts_shutter_50 s/[0-9]|6\d.*:fts_shutter_40 s/[0-9]|7\d.*:fts_shutter_30 s/[0-9]|8\d.*:fts_shutter_20 s/[0-9]|9\d.*:fts_shutter_10 s/[0-9]|99\d.*:fts_shutter_10"
            await fhem.CommandAttr(
                self.hash, self.hash["NAME"] + " devStateIcon " + devStateIcon
            )
        if await fhem.AttrVal(self.hash["NAME"], "webCmd", "") == "":
            await fhem.CommandAttr(
                self.hash, self.hash["NAME"] + " webCmd up:down:status"
            )
        if await fhem.AttrVal(self.hash["NAME"], "stateFormat", "") == "":
            await fhem.CommandAttr(
                self.hash, self.hash["NAME"] + " stateFormat position"
            )
        # if await fhem.AttrVal(self.hash["NAME"], "verbose", "") == "":
        #     await fhem.CommandAttr(self.hash, self.hash["NAME"] + " verbose 5")

        self._warema_ip = args[3]
        hash["IP"] = args[3]

        self._warema_channel = int(args[4])
        self.hash["CHANNEL"] = args[4]

        self.updateTask = self.create_async_task(self.update_task())

    def _connect(self):
        # blocking HTTP requests, runs in a thread
        shades = Shade.get_all_shades(WmsController("http://" + self._warema_ip))
        room = shades[self._warema_channel].get_room_name()
        state = shades[self._warema_channel].get_shade_state()
        return shades, room, state

    async def connect(self):
        while True:
            try:
                (shades, room, state) = await utils.run_blocking(
                    functools.partial(self._connect)
                )
                break
            except Exception:
                self.logger.exception("Failed to connect to WMS gateway")
                await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
                await asyncio.sleep(60)

        self._warema_shades = shades
        self._warema_room = room
        self.hash["ROOM"] = self._warema_room
        (position, ismoving, date) = state

        self._warema_position = str(int(position))
        self.hash["POSITION"] = self._warema_position

        self._warema_ismoving = ismoving
        self.hash["ISMOVING"] = self._warema_ismoving

        if self._warema_position == 0:
            pos = "open"
        elif self._warema_position == 100:
            pos = "closed"
        else:
            pos = self._warema_position

        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "state", pos)
        await fhem.readingsBulkUpdate(self.hash, "room", self._warema_room)
        await fhem.readingsBulkUpdate(self.hash, "channel", self._warema_channel)
        await fhem.readingsBulkUpdate(self.hash, "position", self._warema_position)
        await fhem.readingsBulkUpdate(self.hash, "ismoving", self._warema_ismoving)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_task(self):
        await self.connect()
        await asyncio.sleep(self._attr_interval)
        while True:
            try:
                await self.do_update()
            except Exception:
                self.logger.exception("Failed to update shade state")
            await asyncio.sleep(self._attr_interval)

    async def do_update(self):
        state = await utils.run_blocking(
            functools.partial(
                self._warema_shades[self._warema_channel].get_shade_state
            )
        )
        (position, ismoving, date) = state

        self._warema_position = int(position)
        self._warema_ismoving = ismoving

        await self.updateDeviceReadings()
        return

    async def set_attr_interval(self, hash):
        # update_task reads the interval on each run
        await fhem.readingsSingleUpdate(
            self.hash, "interval", str(self._attr_interval), 1
        )

    # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)
    async def set_status(self, hash, params):
        self.create_async_task(self.do_update())

    async def set_up(self, hash, params):
        self._warema_shades[self._warema_channel].set_shade_position(
            0
        )  # 0=open; 100=closed
        state = self._warema_shades[self._warema_channel].get_shade_state(
            True
        )  # Force update and get shade state
        (position, ismoving, date) = state

        self._warema_position = str(int(position))
        self._warema_ismoving = ismoving

        await self.updateDeviceReadings()

    async def set_down(self, hash, params):
        self._warema_shades[self._warema_channel].set_shade_position(
            100
        )  # 0=open; 100=closed
        state = self._warema_shades[self._warema_channel].get_shade_state(
            True
        )  # Force update and get shade state
        (position, ismoving, date) = state

        self._warema_position = str(int(position))
        self._warema_ismoving = ismoving

        await self.updateDeviceReadings()

    async def set_position(self, hash, params):
        pos = int(params["position"])

        self._warema_shades[self._warema_channel].set_shade_position(
            pos
        )  # 0=open; 100=closed
        state = self._warema_shades[self._warema_channel].get_shade_state(
            True
        )  # Force update and get shade state
        (position, ismoving, date) = state

        self._warema_position = int(position)
        self._warema_ismoving = ismoving

        await self.updateDeviceReadings()

    async def updateDeviceReadings(self):
        self.hash["POSITION"] = self._warema_position
        self.hash["ISMOVING"] = self._warema_ismoving

        if self._warema_position == 0:
            pos = "open"
        elif self._warema_position == 100:
            pos = "closed"
        else:
            pos = self._warema_position

        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "state", pos)
        await fhem.readingsBulkUpdate(self.hash, "position", self._warema_position)
        await fhem.readingsBulkUpdate(self.hash, "ismoving", self._warema_ismoving)
        await fhem.readingsEndUpdate(self.hash, 1)
