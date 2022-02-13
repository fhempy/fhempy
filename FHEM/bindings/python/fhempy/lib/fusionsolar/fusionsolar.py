import asyncio
import functools
import re
from urllib.parse import urlparse

from fhempy.lib.fusionsolar.fusionsolar_api import FusionSolarKioksApi

from .. import fhem, utils
from .. import generic


class fusionsolar(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 3 or len(argsh) != 1:
            return "Usage: define my_solar fhempy fusionsolar KIOSKURL"
        self._url = list(argsh)[0] + "=" + argsh[list(argsh)[0]]
        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.create_async_task(self.update())

    async def update(self):
        self.kiosk = Kiosk(self._url)
        self.api = FusionSolarKioksApi(self.kiosk.apiUrl())

        await self.update_readings()

    async def update_readings(self):
        while True:
            await fhem.readingsBeginUpdate(self.hash)
            try:
                data = await utils.run_blocking(
                    functools.partial(self.api.getRealTimeKpi, self.kiosk.id)
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "realtime_power", data["realTimePower"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "total_current_day_energy", data["dailyEnergy"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "total_current_month_energy", data["monthEnergy"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "total_current_year_energy", data["yearEnergy"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "total_lifetime_energy", data["cumulativeEnergy"]
                )
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")
            except Exception:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "failed")
                self.logger.exception("Failed to update readings")
            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(300)


class Kiosk:
    def __init__(self, url):
        self.url = url
        self._parseId()

    def _parseId(self):
        id = re.search("\?kk=(.*)", self.url).group(1)
        self.id = id

    def apiUrl(self):
        url = urlparse(self.url)
        apiUrl = url.scheme + "://" + url.netloc
        return apiUrl
