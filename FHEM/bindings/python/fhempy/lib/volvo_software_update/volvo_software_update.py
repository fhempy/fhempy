import asyncio

import aiohttp
from bs4 import BeautifulSoup

from .. import fhem, generic


class volvo_software_update(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 1800,
                "format": "int",
                "help": "Change interval, default is 1800s.",
            }
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define my_volvo_update fhempy volvo_software_update URL"

        self.update_url = args[3]

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp get
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.update_url) as resp:
                        if resp.status == 200:
                            await self.handle_response(await resp.text())
                        else:
                            await fhem.readingsSingleUpdate(
                                self.hash,
                                "state",
                                f"failed: HTTP error {resp.status}",
                                1,
                            )
                            self.logger.error(
                                f"Failed to fetch {self.update_url}, "
                                f"failed with status {resp.status}"
                            )
            except Exception:
                self.logger.exception("Failed to update")
            await asyncio.sleep(self._attr_interval)

    async def handle_response(self, response):
        # bs4
        soup = BeautifulSoup(response, "html.parser")
        entries = soup.findAll("div", {"class": "segment"})
        for entry in entries:
            if entry.find("h2"):
                await fhem.readingsBeginUpdate(self.hash)
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "latest_release_notes", f"<html>{entry}</html>"
                )
                release_text = entry.find("h2").text

                if release_text.find(" V") > 0:
                    release_number = release_text[release_text.find(" V") + 2 :]
                    state_text = "Version "
                else:
                    release_number = release_text
                    state_text = ""

                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "latest_release", release_number
                )
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "state", f"{state_text}{release_number}"
                )
                latest_update = soup.findAll("em")[-1].text
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "latest_update", latest_update
                )
                await fhem.readingsEndUpdate(self.hash, 1)
                break
