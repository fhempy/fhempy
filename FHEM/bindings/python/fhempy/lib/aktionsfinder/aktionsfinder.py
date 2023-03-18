import asyncio

import aiohttp

from .. import fhem, generic


class aktionsfinder(generic.FhemModule):

    SEARCH_API = "https://api.post.at/aktionsfinder/afcore/api/public/v2/search"

    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 24,
                "format": "int",
                "help": "Change interval, default is 24h.",
            }
        }
        await self.set_attr_config(attr_config)

        if len(args) < 4:
            return "Usage: define water fhempy aktionsfinder voeslauer"

        self.search_item = " ".join(args[3:])

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp post
            headers = {
                "authority": "api.post.at",
                "accept": "*/*",
                "accept-currency": "EUR",
                "accept-language": "de",
                "content-type": "application/json",
                "ocp-apim-subscription-key": "3b9e1fb43aa746e583919d322d2f239f",
                "origin": "https://www.aktionsfinder.at",
                "sec-ch-ua": 'Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Chrome OS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                "x-client-token": "YWZ3ZWJwd2E6OTNtMXBpZTY0bnN6NnVsZnRkeWQ0MjhuNjl6N296OHRwbXQwM3VkZQ==",
            }
            query_json = {
                "radius": "50000",
                "query": self.search_item,
                "lat": 48.21,
                "lng": 16.37,
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        aktionsfinder.SEARCH_API,
                        json=query_json,
                        headers=headers,
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
                            self.logger.error(f"Failed with status {resp.status}")
            except Exception:
                self.logger.exception("Failed to update")
            await asyncio.sleep(self._attr_interval * 3600)

    async def handle_response(self, response):
        await fhem.readingsBeginUpdate(self.hash)
        lowest_price = None
        for result in response["searchResult"]["content"]:
            if result["newPrice"] is None:
                continue

            if lowest_price is None or result["newPrice"] < lowest_price:
                lowest_price = result["newPrice"]
            else:
                # do not update if the price is not lowest
                continue

            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "vendor", result["vendorTitle"]
            )
            img_html = f"<html><img src=\"{result['image']['large']}\"/></html>"
            await fhem.readingsBulkUpdateIfChanged(self.hash, "image", img_html)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "valid_from", result["validFrom"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "valid_to", result["validTo"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "price_old", result["oldPrice"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "price_new", result["newPrice"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "state",
                str(result["newPrice"])
                + "€ ("
                + result["validFrom"]
                + " - "
                + result["validTo"]
                + ")",
            )

        await fhem.readingsEndUpdate(self.hash, 1)
