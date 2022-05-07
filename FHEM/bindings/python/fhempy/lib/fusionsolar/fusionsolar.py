import asyncio
import functools
import re
from urllib.parse import urlparse

from fhempy.lib.fusionsolar.fusionsolar_api import (
    FusionSolarKioksApi,
    FusionSolarRestApi,
)

from .. import fhem, utils
from .. import generic


class fusionsolar(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._stationid = None
        self._sessionid = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if not (len(args) == 3 or len(args) == 4 or len(args) == 5) or len(argsh) != 2:
            return (
                "Usage: define my_solar fhempy fusionsolar "
                "KIOSKURL [STATIONID] [SESSIONID] [REGION]"
            )
        self._url = list(argsh)[0] + "=" + argsh[list(argsh)[0]]
        if len(args) >= 4:
            self._stationid = list(argsh)[1] + "=" + argsh[list(argsh)[1]]
            self._sessionid = args[3]
            self._region = args[4] if len(args) > 4 else "region01eu05"
            self.restapi = FusionSolarRestApi(
                self.logger, self._stationid, self._sessionid, self._region
            )

        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.create_async_task(self.update())

    async def update(self):
        self.kiosk = Kiosk(self._url)
        self.kioskapi = FusionSolarKioksApi(self.kiosk.apiUrl())

        await self.update_readings()

    async def update_readings(self):
        while True:
            await fhem.readingsBeginUpdate(self.hash)
            try:
                data = await utils.run_blocking(
                    functools.partial(self.kioskapi.getRealTimeKpi, self.kiosk.id)
                )
                if self._sessionid:
                    await self.restapi.update()

                    await fhem.readingsBulkUpdate(
                        self.hash, "from_grid", self.restapi.from_grid
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash, "to_grid", self.restapi.to_grid
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash, "electrical_load", self.restapi.electrical_load
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash, "grid_power", self.restapi.grid_power
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "inverter_output_power",
                        self.restapi.inverter_output_power,
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
