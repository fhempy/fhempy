import asyncio

import aiohttp

from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from .api.client import AsyncSmartmeter
from .api.errors import SmartmeterLoginError

LOGIN_RETRY_INTERVAL = 300
UPDATE_INTERVAL = 3600


class wienernetze_smartmeter(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 5:
            return (
                "Usage: define devname fhempy wienernetze_smartmeter USERNAME PASSWORD"
            )
        self.username = args[3]
        self.password = args[4]

        self._updateloop = self.create_async_task(self.update_loop())

    async def update_loop(self):
        async with aiohttp.ClientSession() as session:
            client = AsyncSmartmeter(
                self.username, self.password, session, logger=self.logger
            )
            await self.login(client)
            await self.update_endpoint(client.base_information, "baseInformation")
            while True:
                await self.update(client)
                await asyncio.sleep(UPDATE_INTERVAL)

    async def login(self, client):
        while True:
            try:
                await client.login()
                return
            except SmartmeterLoginError as err:
                self.logger.error(f"Login failed: {err}, retry in 5 minutes")
                await fhem.readingsSingleUpdate(self.hash, "state", "login failed", 1)
            except Exception as err:
                self.logger.error(f"Login not possible: {err!r}, retry in 5 minutes")
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "connection error", 1
                )
            await asyncio.sleep(LOGIN_RETRY_INTERVAL)

    async def update(self, client):
        ok = await self.update_endpoint(client.consumptions, "consumptions")
        ok = await self.update_endpoint(client.meter_readings, "meterReadings") or ok
        if ok:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "online", 1)

    async def update_endpoint(self, func, name):
        try:
            data = await func()
        except SmartmeterLoginError as err:
            self.logger.error(f"Login failed: {err}")
            await fhem.readingsSingleUpdate(self.hash, "state", "login failed", 1)
            return False
        except Exception as err:
            self.logger.error(f"Failed to update {name}: {err!r}")
            await fhem.readingsSingleUpdate(self.hash, "state", "update failed", 1)
            return False
        if data is not None:
            await self.update_readings(data)
        return True

    async def update_readings(self, data):
        flat_data = utils.flatten_json(data)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in flat_data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, name, flat_data[name])
        except Exception:
            self.logger.exception("Failed readings update")
        await fhem.readingsEndUpdate(self.hash, 1)
