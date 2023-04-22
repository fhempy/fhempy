import asyncio
import re

import aiohttp
from bs4 import BeautifulSoup

from .. import fhem, generic


class ikos(generic.FhemModule):

    headers1 = {
        "authority": "ikosresorts.swapsystems.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Chrome OS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }
    headers2 = {
        "accept": "*/*",
        "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Chrome OS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "Referer": "https://ikosresorts.swapsystems.com/",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    }

    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        attr_config = {
            "interval": {
                "default": 24,
                "format": "int",
                "help": "Change interval in hours, default is 24 hours.",
            },
            "adults": {
                "default": 2,
                "format": "int",
                "help": "Number of adults in one room.",
            },
            "children": {
                "default": 0,
                "format": "int",
                "help": "Number of children in one room.",
            },
            "age_child1": {
                "default": 3,
                "format": "int",
                "help": "Age of first child.",
            },
            "age_child2": {
                "default": 3,
                "format": "int",
                "help": "Age of second child.",
            },
            "age_child3": {
                "default": 3,
                "format": "int",
                "help": "Age of third child.",
            },
            "age_child4": {
                "default": 3,
                "format": "int",
                "help": "Age of fourth child.",
            },
        }
        await self.set_attr_config(attr_config)

        if len(args) != 5:
            return "Usage: define june.holidays fhempy ikos [FROMDATE] [TODATE]"

        self.date_from = args[3]
        self.date_to = args[4]

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon weather_sun")

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            # aiohttp post
            data = {
                "sid": "",
                "fls": "",
                "starRating": "",
                "boardType": "",
                "fCurID": "",
                "SortBy": "",
                "CityID": 0,
                "HotelID": 0,
                "Checkin": self.date_from,
                "Checkout": self.date_to,
                "Rooms": 1,
                "Adults1": self._attr_adults,
                "Children1": self._attr_children,
                "r1C1": self._attr_age_child1,
                "r1C2": self._attr_age_child2,
                "r1C3": self._attr_age_child3,
                "r1C4": self._attr_age_child4,
                "Adults2": 0,
                "Children2": 0,
                "r2C1": 0,
                "r2C2": 0,
                "r2C3": 0,
                "r2C4": 0,
                "Adults3": 0,
                "Children3": 0,
                "r3C1": 0,
                "r3C2": 0,
                "r3C3": 0,
                "r3C4": 0,
                "SortID": 1,
            }

            try:
                await fhem.readingsBeginUpdate(self.hash)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://ikosresorts.swapsystems.com",
                        headers=ikos.headers1,
                        json=data,
                    ) as resp:
                        pass
                    async with session.get(
                        "https://ikosresorts.swapsystems.com/hotel_results",
                        data=data,
                        headers=ikos.headers2,
                    ) as resp:
                        await self.handle_response(await resp.text())
            except Exception:
                self.logger.exception("Failed to update")

            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self._attr_interval * 60 * 60)

    async def handle_response(self, response):
        soup = BeautifulSoup(response, "html.parser")
        hotels = soup.findAll("div", {"class": "Search-header-rounded"})
        flights = soup.findAll("div", {"class": "flights"})
        best_price = None
        for i in range(0, len(hotels)):
            lowest_price_text = hotels[i].find("strong").text
            lowest_price = re.findall("\d+\.\d+", lowest_price_text)[0]
            hotel_name = hotels[i].find("a", {"class": "cardtitle htd"})["data-id2"]
            room_type = flights[i].find("a", {"data-toggle": "modal"})["data-id2"]
            if best_price is None or lowest_price < best_price:
                best_price = lowest_price
                best_hotel = hotel_name
                best_room = room_type
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{i}_lowest_price", lowest_price
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{i}_hotel_name", hotel_name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{i}_room_type", room_type
            )
        if best_price is None:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", f"No rooms available"
            )
        else:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "best_price", best_price)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "best_price_hotel", best_hotel
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "best_price_room", best_room
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", f"{best_hotel}: {best_price}€"
            )
