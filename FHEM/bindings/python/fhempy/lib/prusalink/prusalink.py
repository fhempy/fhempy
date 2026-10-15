import asyncio

import httpx
import pyprusalink

from fhempy.lib.utils import flatten_json

from .. import fhem, generic, utils


class prusalink(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)

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
            self._errors.success()
        except Exception as ex:
            self._errors.failed("Failed to get printer status")
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                f"failed: {utils.describe_exception(ex)}",
                1,
            )
        return data

    async def update_loop(self):
        async with httpx.AsyncClient() as session:
            self.pl = pyprusalink.PrusaLink(
                session, self.url, self.username, self.password
            )
            while True:
                data = await self.retrieve_data()
                if not data:
                    await asyncio.sleep(30)
                    continue
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
                    self._errors.failed("Failed to update readings", key="readings")
                else:
                    self._errors.success(key="readings")
                finally:
                    await fhem.readingsEndUpdate(self.hash, 1)

                await asyncio.sleep(30)
