import asyncio
import functools

import aiohttp
from bs4 import BeautifulSoup
from fhempy.lib import utils

from .. import fhem, generic


class google_weather(generic.FhemModule):
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
            return "Usage: define my_weather fhempy google_weather CITY"

        self.city = args[3]
        self.update_url = f"https://www.google.com/search?q={self.city}+weather"

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/75.0.3770.100 Safari/537.36"
            ),
        }
        while True:
            # aiohttp get
            try:
                async with aiohttp.ClientSession(trust_env=True) as session:
                    async with session.get(self.update_url, headers=headers) as resp:
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

    def soup_extract(self, soup, element, search_obj):
        element = soup.find(element, search_obj)
        if element is None:
            self.logger.error(f"Element {element} with {search_obj} not found!")
        return element

    def soup_extract_text(self, soup, element, search_obj):
        element = self.soup_extract(soup, element, search_obj)
        if element is None:
            return "-"
        return element.text

    def get_current_temperature(self, soup):
        return self.soup_extract_text(soup, "span", {"id": "wob_tm"})

    def get_current_condition(self, soup):
        return self.soup_extract(soup, "img", {"wob_tci"})

    def get_current_windspeed(self, soup):
        return self.soup_extract_text(soup, "span", {"id": "wob_ws"})

    def get_last_update(self, soup):
        return self.soup_extract_text(soup, "div", {"id": "wob_dts"})

    def get_location_name(self, soup):
        return self.soup_extract_text(soup, "div", {"id": "wob_loc"})

    def get_current_precipitation(self, soup):
        return self.soup_extract_text(soup, "span", {"id": "wob_pp"})

    def get_current_humidity(self, soup):
        return self.soup_extract_text(soup, "span", {"id": "wob_hm"}).replace("%", "")

    def get_next_days(self, soup):
        next_days = []
        days = soup.find("div", attrs={"id": "wob_dp"})
        for day in days.findAll("div", attrs={"class": "wob_df"}):
            # extract the name of the day
            day_name = day.findAll("div")[0].attrs["aria-label"]
            # get weather status for that day
            image = day.find("img")
            weather = image.attrs["alt"]
            temp = day.findAll("span", {"class": "wob_t"})
            # maximum temparature in Celsius, use temp[1].text if you want fahrenheit
            max_temp = temp[0].text
            # minimum temparature in Celsius, use temp[3].text if you want fahrenheit
            min_temp = temp[2].text
            next_days.append(
                {
                    "name": day_name,
                    "weather": weather,
                    "max_temp": max_temp,
                    "min_temp": min_temp,
                    "image": image,
                }
            )
        return next_days

    def extract_weather(self, response):
        soup = BeautifulSoup(response, "html.parser")
        self.cur_temp = self.get_current_temperature(soup)
        cur_condition_element = self.get_current_condition(soup)
        if cur_condition_element is None:
            self.cur_condition = "-"
            self.cur_condition_img = "-"
        else:
            self.cur_condition = cur_condition_element["alt"]
            self.cur_condition_img = f"{cur_condition_element}"
        self.cur_windspeed = self.get_current_windspeed(soup)
        self.cur_windspeed_number = self.cur_windspeed.split(" ")[0]
        self.cur_precipitation = self.get_current_precipitation(soup).replace("%", "")
        self.cur_humidity = self.get_current_humidity(soup)
        self.next_days = self.get_next_days(soup)
        self.last_update = self.get_last_update(soup)
        self.location = self.get_location_name(soup)
        # wind alle 3h
        self.next_windspeed = []
        for x in soup.find("div", {"id": "wob_wg"}):
            self.next_windspeed.append((x.find("span", {"class": "wob_t"})))
            if len(self.next_windspeed) > 4:
                break

        # regen stuendlich
        self.next_precipitation = []
        for x in soup.find("div", {"id": "wob_pg"}):
            self.next_precipitation.append(x.find("div"))
            if len(self.next_precipitation) > 9:
                break

    async def handle_response(self, response):
        # bs4
        await utils.run_blocking(functools.partial(self.extract_weather, response))

        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_temperature", self.cur_temp
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_humidity", self.cur_humidity
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_precipitation", self.cur_precipitation
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_weather", self.cur_condition
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_weather_img", f"<html>{self.cur_condition_img}</html>"
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_windspeed_with_unit", self.cur_windspeed
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "cur_windspeed", self.cur_windspeed_number
        )

        i = 0
        for day in self.next_days:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_day_{i}_name", day["name"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_day_{i}_weather", day["weather"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_day_{i}_weather_img", f"<html>{day['image']}</html>"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_day_{i}_max_temp", day["max_temp"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_day_{i}_min_temp", day["min_temp"]
            )
            i += 1

        i = 0
        for wind in self.next_windspeed:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_windspeed_{i}_long", wind["aria-label"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_windspeed_{i}", wind.text
            )
            i += 1

        i = 0
        for precipitation in self.next_precipitation:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_precipitation_{i}_long", precipitation["aria-label"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                f"next_precipitation_{i}",
                precipitation["aria-label"].split(" ")[0],
            )
            i += 1

        await fhem.readingsBulkUpdateIfChanged(self.hash, "location", self.location)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "last_update", self.last_update
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "state",
            (
                f"<html>{self.cur_condition_img}<br>{self.cur_temp}°C / "
                f"{self.cur_precipitation}% / {self.cur_windspeed}</html>"
            ),
        )
        await fhem.readingsEndUpdate(self.hash, 1)
