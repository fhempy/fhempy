import asyncio

import aiohttp
import pyprusalink

from fhempy.lib.utils import flatten_json

from .. import fhem, generic


class prusalink(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 6:
            return "Usage: define prusa_mk4 fhempy prusalink URL USERNAME PASSWORD"

        await self.set_icon("3d_printer")

        self.url = args[3]
        self.username = args[4]
        self.password = args[5]

        self.create_async_task(self.update_loop())

    async def retrieve_data(self):
        data = {}
        try:
            data["status"] = await self.pl.get_status()
        except Exception as ex:
            self.logger.exception("Failed to update")
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                f"failed: {ex}",
                1,
            )
        return data

    async def update_loop(self):
        async with aiohttp.ClientSession() as session:
            self.pl = pyprusalink.PrusaLink(
                session, self.url, self.username, self.password
            )
            while True:
                data = await self.retrieve_data()
                flat_json = flatten_json(data)
                await fhem.readingsBeginUpdate(self.hash)
                try:
                    for name in flat_json:
                        await fhem.readingsBulkUpdateIfChanged(
                            self.hash, name, flat_json[name]
                        )
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, "state", flat_json["status_printer_state"]
                    )
                except Exception:
                    self.logger.exception("Failed to update readings")
                await fhem.readingsEndUpdate(self.hash, 1)

                await asyncio.sleep(30)
