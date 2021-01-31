import asyncio

import aiohttp
from fhempy.lib.generic import FhemModule

from .. import fhem, utils

BASE_URL = "http://www.wienerlinien.at/ogd_realtime/monitor?rbl={}"

DEPARTURES = {
    "first": {"key": 0, "name": "{} first departure"},
    "next": {"key": 1, "name": "{} next departure"},
}


class wienerlinien(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.firstnext = "first"
        self._updateloop = None
        self._last_data = None
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        set_list_conf = {"update": {}}
        self.set_set_config(set_list_conf)
        if len(args) < 4:
            return "Usage: define devname PythonModule wienerlinien <STOPID>"
        self._stopid = args[3]
        self.api = WienerlinienAPI(self._stopid)
        self._updateloop = self.create_async_task(self.update_loop())
        # delete all readings on define
        self.create_async_task(fhem.CommandDeleteReading(hash, hash["NAME"] + " .*"))

    async def set_update(self, hash, params):
        self.create_async_task(self.update())
        return ""

    async def update_loop(self):
        while True:
            await self.update()
            await asyncio.sleep(30)

    async def update(self):
        try:
            data = await self.api.get_json()
            self.logger.debug(data)
            if data is None:
                return
            message = data.get("message", {})
            data = data.get("data", {})
        except Exception:
            self.logger.debug("Could not get new state")
            return

        if data is None:
            return
        try:
            if len(data["monitors"]) == 0:
                flat_data = {}
                flat_data_location = {}
                state_text = "no departures"
            else:
                flat_data = utils.flatten_json(data["monitors"][0]["lines"][0])
                flat_data_location = utils.flatten_json(
                    data["monitors"][0]["locationStop"]
                )
                state_text = (
                    flat_data["towards"]
                    + ": "
                    + str(flat_data["departures_departure_0_departureTime_countdown"])
                )

            if self._last_data:
                del_readings = set(self._last_data) - set(flat_data)
            else:
                del_readings = {}

            await fhem.readingsBeginUpdate(self.hash)
            for msg in message:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "msg_" + msg, message[msg]
                )
            for data_name in flat_data:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "line_" + data_name, flat_data[data_name]
                )
            for data_name in flat_data_location:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "loc_" + data_name, flat_data_location[data_name]
                )

            if "trafficjam" in flat_data and flat_data["trafficjam"] == 1:
                state_text += " (traffic jam)"
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state_text)
            await fhem.readingsEndUpdate(self.hash, 1)

            # delete old readings which were not updated
            for del_reading in del_readings:
                await fhem.CommandDeleteReading(
                    self.hash, self.hash["NAME"] + " line_" + del_reading
                )

            self._last_data = flat_data

        except Exception:
            self.logger.exception("Failed...")
            pass


class WienerlinienAPI:
    """Call API."""

    def __init__(self, stopid):
        """Initialize."""
        self.session = aiohttp.ClientSession()
        self.stopid = stopid

    async def get_json(self):
        """Get json from API endpoint."""
        value = None
        url = BASE_URL.format(self.stopid)
        try:
            response = await self.session.get(url)
            value = await response.json()
        except Exception:
            self.logger.exception("Failed...")
            pass

        return value
