import asyncio
import functools

import aiohttp
from bs4 import BeautifulSoup

from .. import fhem, generic, utils


class geizhals(generic.FhemModule):

    headers = {
        "accept": "application/json",
        "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "content-type": "application/json",
        "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Chrome OS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://geizhals.at/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 3,
                "format": "int",
                "help": "Change interval in hours, default is 3 hours.",
            }
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define gh.pixel fhempy geizhals URL"

        self.url = args[3]
        self.product_id = self.url[self.url.rfind("-a") + 2 : self.url.rfind(".html")]
        self.location = self.url[
            self.url.find("geizhals") + 9 : self.url.find("geizhals") + 11
        ]
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "link",
            '<html><a href="'
            + self.url
            + '" target="_blank">Open geizhals '
            + "(new window/tab)</a><br></html>",
            1,
        )

        self.create_async_task(self.update_loop())

    async def update_product_page_infos(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url,
                headers=geizhals.headers,
            ) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    await utils.run_blocking(
                        functools.partial(self.handle_product_page, html)
                    )

    def handle_product_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        self.product_name = soup.find(
            "h1", {"class": "variant__header__headline"}
        ).text[1:-1]
        self.store = soup.find("span", {"class": "notrans"}).text[1:-1]
        self.store_availability = (
            soup.find("div", {"id": "offer__0"})
            .find("div", {"class": "offer__delivery-time"})
            .text
        )

    async def update_loop(self):
        # get product page infos
        await self.update_product_page_infos()
        if await fhem.AttrVal(self.hash["NAME"], "alias", "") == "":
            await fhem.CommandAttr(
                self.hash, f"{self.hash['NAME']} alias {self.product_name}"
            )

        while True:
            # aiohttp post
            data = {"id": self.product_id, "params": {"days": 31, "loc": self.location}}
            try:
                await fhem.readingsBeginUpdate(self.hash)
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://geizhals.at/api/gh0/price_history",
                        headers=geizhals.headers,
                        json=data,
                    ) as resp:
                        if resp.status == 200:
                            await self.handle_response(await resp.json())
                        else:
                            await fhem.readingsSingleUpdate(
                                self.hash,
                                "state",
                                f"failed: HTTP error {resp.status}",
                                1,
                            )
                            self.logger.error(
                                f"Failed to fetch from geizhals, "
                                f"failed with status {resp.status}"
                            )

                await self.update_product_page_infos()
                await fhem.readingsBulkUpdateIfChanged(self.hash, "store", self.store)
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "store_availability", self.store_availability
                )

            except Exception:
                self.logger.exception("Failed to update")

            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self._attr_interval * 60 * 60)

    async def handle_response(self, response):
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "last_update", response["meta"]["last_formatted"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "current_price_euro", response["meta"]["current_best"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "max", response["meta"]["max"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "min", response["meta"]["min"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "state",
            str(response["meta"]["current_best"])
            + " € ("
            + str(response["meta"]["min"])
            + " € - "
            + str(response["meta"]["max"])
            + " €)",
        )
