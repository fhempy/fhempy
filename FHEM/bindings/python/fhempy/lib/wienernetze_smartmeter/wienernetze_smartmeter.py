import asyncio

from fhempy.lib.generic import FhemModule
from vienna_smartmeter import AsyncSmartmeter

from .. import fhem, utils


class wienernetze_smartmeter(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        set_list_conf = {"update": {}}
        await self.set_set_config(set_list_conf)
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
        while True:
            data = await client.welcome()
            flat_data = utils.flatten_json(data)
            await fhem.readingsBeginUpdate(self.hash)
            for name in flat_data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, name, flat_data[name])
            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(3600)
