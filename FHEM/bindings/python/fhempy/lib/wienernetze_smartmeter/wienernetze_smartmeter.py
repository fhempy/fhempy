import asyncio

from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from .api.client import AsyncSmartmeter


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
        client = AsyncSmartmeter(self.username, self.password)
        await client.refresh_token()
        data = await client.base_information()
        await self.update_readings(data)
        while True:
            try:
                data = await client.consumptions()
                await self.update_readings(data)
                data = await client.meter_readings()
                await self.update_readings(data)
            except Exception:
                self.logger.exception("Failed to update values")
            await asyncio.sleep(3600)

    async def update_readings(self, data):
        flat_data = utils.flatten_json(data)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in flat_data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, name, flat_data[name])
        except Exception:
            self.logger.exception("Failed readings update")
        await fhem.readingsEndUpdate(self.hash, 1)
