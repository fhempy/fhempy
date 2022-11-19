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
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Chrome OS"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            }
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
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
