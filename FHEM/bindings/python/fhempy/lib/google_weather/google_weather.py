import asyncio
import functools
import json
from random import randrange

import aiohttp
from bs4 import BeautifulSoup
from fhempy.lib import utils

from .. import fhem, generic


class google_weather(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 61,
                "format": "int",
                "help": "Change interval in minutes, default is 61.",
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

    def set_user_agent(self, headers):
        user_agent = [
            (
                "Mozilla/5.0 (X11; CrOS x86_64 14909.100.0) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (X11; CrOS x86_64 15054.63.0) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
            ),
            (
                "Mozilla/5.0 (X11; CrOS x86_64 15117.28.0) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
            ),
        ]
        sec_ch_ua = [
            '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        ]
        sec_ch_full_version = ['"104.0.5112.83"', '"106.0.5249.49"', '"107.0.5304.22"']
        sec_ch_full_version_list = [
            (
                '"Chromium";v="104.0.5112.83", " Not A;Brand";v="99.0.0.0", '
                '"Google Chrome";v="104.0.5112.83"'
            ),
            (
                '"Chromium";v="106.0.5249.49", "Google Chrome";v="106.0.5249.49",'
                ' "Not;A=Brand";v="99.0.0.0"'
            ),
            (
                '"Google Chrome";v="107.0.5304.22", "Chromium";v="107.0.5304.22",'
                ' "Not=A?Brand";v="24.0.0.0"'
            ),
        ]
        sec_ch_ua_platform_version = ['"14909.100.0"', '"15054.63.0"', '"15117.28.0"']
        ua_id = randrange(len(user_agent))
        headers["user-agent"] = user_agent[ua_id]
        headers["sec-ch-ua"] = sec_ch_ua[ua_id]
        headers["sec-ch-ua-full-version"] = sec_ch_full_version[ua_id]
        headers["sec-ch-ua-full-version-list"] = sec_ch_full_version_list[ua_id]
        headers["sec-ch-ua-platform-version"] = sec_ch_ua_platform_version[ua_id]
        headers["sec-ch-ua-arch"] = '"x86"'
        headers["sec-ch-ua-bitness"] = '"64"'
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-model"] = '""'
        headers["sec-ch-ua-platform"] = '"Chrome OS"'
        headers["sec-ch-ua-wow64"] = "?0"

    async def update_loop(self):
        headers = {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,image/apng,*/*;"
                "q=0.8,application/signed-exchange;v=b3;q=0.9"
            ),
            "accept-language": (
                "en-DE,en;q=0.9,de-DE;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5"
            ),
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "x-chrome-connected": (
                "source=Chrome,mode=0,enable_account_consistency=true,"
                "supervised=false,consistency_enabled_by_default=false"
            ),
        }
        self.set_user_agent(headers)

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
            await asyncio.sleep(self._attr_interval * 60)

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

        wdata = None
        for script in soup.find_all("script"):
            if script.text.find("\\x22wobnm\\x22") > -1:
                wdata = script.text
                break
        if wdata is not None:
            start_json = wdata.find("\\x22wobnm\\x22")
            end_json = wdata.find("';google.pmc=")
            weather_json = json.loads(
                "{" + wdata[start_json:end_json].replace("\\x22", '"')
            )

        self.next_hours = []
        for x in weather_json["wobnm"]["wobhl"]:
            self.next_hours.append(x)
            if len(self.next_hours) > 24:
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
                self.hash, f"next_days_{i}_name", day["name"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_days_{i}_weather", day["weather"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_days_{i}_weather_img", f"<html>{day['image']}</html>"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_days_{i}_max_temp", day["max_temp"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_days_{i}_min_temp", day["min_temp"]
            )
            i += 1

        i = 0
        for nh in self.next_hours:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_hours_{i:02d}_condition", nh["c"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_hours_{i:02d}_time", nh["dts"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_hours_{i:02d}_humidity", nh["h"].replace("%", "")
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                f"next_hours_{i:02d}_img",
                '<html><img src="' + nh["iu"] + '"/></html>',
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_hours_{i:02d}_precipitation", nh["p"].replace("%", "")
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"next_hours_{i:02d}_temperature", nh["tm"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                f"next_hours_{i:02d}_windspeed",
                nh["ws"].replace(" km/h", ""),
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
