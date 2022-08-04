import asyncio

import aiohttp

from .. import fhem, generic


class geizhals(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 3600,
                "format": "int",
                "help": "Change interval, default is 3600s.",
            }
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define gh.pixel fhempy geizhals URL"

        url = args[3]
        self.product_id = url[url.rfind("-a") + 2 : url.rfind(".html")]
        self.location = url[url.find("geizhals") + 9 : url.find("geizhals") + 11]

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp post
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
            data = {"id": self.product_id, "params": {"days": 31, "loc": self.location}}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://geizhals.at/api/gh0/price_history",
                        headers=headers,
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
            except Exception:
                self.logger.exception("Failed to update")
            await asyncio.sleep(self._attr_interval)

    async def handle_response(self, response):
        await fhem.readingsBeginUpdate(self.hash)
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
        await fhem.readingsEndUpdate(self.hash, 1)
