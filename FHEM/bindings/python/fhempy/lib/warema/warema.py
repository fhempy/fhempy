import asyncio

from warema_wms import WmsController, Shade

from .. import fhem, utils
from ..generic import FhemModule


class warema(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.hash = None

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60.",
            },
        }
        self.set_attr_config(attr_config)

        set_config = {
            "status": {},
            "up": {},
            "down": {},
            "position": {"args": ["position"], "options": "slider,0,11,100"},
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
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

        self._warema_shades = Shade.get_all_shades(
            WmsController("http://" + self._warema_ip)
        )

        self._warema_room = self._warema_shades[self._warema_channel].get_room_name()
        self.hash["ROOM"] = self._warema_room

        state = self._warema_shades[self._warema_channel].get_shade_state()
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

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdate(hash, "state", pos)
        await fhem.readingsBulkUpdate(hash, "room", self._warema_room)
        await fhem.readingsBulkUpdate(hash, "channel", self._warema_channel)
        await fhem.readingsBulkUpdate(hash, "position", self._warema_position)
        await fhem.readingsBulkUpdate(hash, "ismoving", self._warema_ismoving)
        await fhem.readingsEndUpdate(hash, 1)

        self.updateTask = self.create_async_task(self.update_task())

    async def update_task(self):
        while True:
            await self.do_update()
            await asyncio.sleep(self._attr_interval)

    async def do_update(self):
        state = self._warema_shades[self._warema_channel].get_shade_state()
        (position, ismoving, date) = state

        self._warema_position = int(position)
        self._warema_ismoving = ismoving

        await self.updateDeviceReadings()
        return

    async def set_attr_interval(self, hash):
        await fhem.readingsSingleUpdate(
            self.hash, "interval", str(self._attr_interval), 1
        )
        self.updateTask = self.create_async_task(self.update_task())

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
