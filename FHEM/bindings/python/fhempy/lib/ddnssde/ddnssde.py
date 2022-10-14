import asyncio

import aiohttp
from bs4 import BeautifulSoup
from fhempy.lib import utils

from .. import fhem, generic


class ddnssde(generic.FhemModule):

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
        + "image/avif,image/webp,image/apng,*/*;"
        + "q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-AT,en;q=0.9,de-AT;q=0.8,de;"
        + "q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Length": "58",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "ddnss.de",
        "Origin": "https://ddnss.de",
        "Referer": "https://ddnss.de/login.php",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14989.36.0) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Chrome OS",
    }

    def __init__(self, logger):
        super().__init__(logger)

        self.ip_infos = {}
        self.update_key_ready = asyncio.Event()
        self.hostname_ready = asyncio.Event()

        attr_config = {
            "ip_check_interval": {
                "default": 15,
                "format": "int",
                "help": "Change interval in minutes, default is 15.",
            },
            "hostname": {
                "default": "-",
                "options": "all",
                "help": "Select the hostname you would like to update",
            },
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 5:
            return "Usage: define ddnss.updater fhempy ddnssde USERNAME PASSWORD"

        self.username = args[3]
        self.password = args[4]

        self.current_ip = await fhem.ReadingsVal(self.hash["NAME"], "current_ip", "")

        self.create_async_task(self.update_ddnss_data_loop())
        self.create_async_task(self.update_ip_loop())

    async def update_readings(self, readings):
        await fhem.readingsBeginUpdate(self.hash)
        for name in readings:
            await fhem.readingsBulkUpdateIfChanged(self.hash, name, readings[name])
        await fhem.readingsEndUpdate(self.hash, 1)

    async def get_json_data(self, url):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=ddnssde.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        return None

    async def get_current_ip(self):
        return await self.get_json_data("https://wtfismyip.com/json")

    async def check_myip(self):
        # sorry for the wording, it comes from WTFismyip service
        ip_infos = await self.get_current_ip()
        self.ip_infos = {
            "current_ip": ip_infos["YourFuckingIPAddress"],
            "isp_location": ip_infos["YourFuckingLocation"],
            "isp_hostname": ip_infos["YourFuckingHostname"],
            "isp": ip_infos["YourFuckingISP"],
            "isp_country": ip_infos["YourFuckingCountryCode"],
        }
        await self.update_readings(self.ip_infos)
        return self.ip_infos

    async def is_ip_updated(self):
        ip_infos = await self.check_myip()
        new_ip = ip_infos["current_ip"]
        if new_ip != self.current_ip:
            self.current_ip = new_ip
            return True
        return False

    async def update_ddnss_data(self):
        await self.login()
        ret = await self.retrieve_ddnss_data()
        if ret is False:
            self.logger.error("Failed to retrieve ddnss data")
            return
        await self.update_ddnss_readings()

    async def update_ddnss_data_loop(self):
        while True:
            try:
                await self.update_ddnss_data()
                await asyncio.sleep(7500)
            except Exception:
                self.logger.exception("Failed to update ddnss, retry")
                await asyncio.sleep(30)

    async def update_ddnss_readings(self):
        readings = {
            "update_key": self.update_key,
            "mail": self.ddnss_mail,
            "last_login": self.ddnss_login,
        }

        hostattr = ["all"]
        for host in self.hostnames:
            host_underscore = host.replace(".", "_")
            hostattr.append(host_underscore)
            if host_underscore == self._attr_hostname:
                readings["state"] = host + ": " + self.hostnames[host]["ip"]
            readings[f"host_{host_underscore}"] = host
            readings[f"host_{host_underscore}_ip"] = self.hostnames[host]["ip"]
            readings[f"host_{host_underscore}_last_upd"] = self.hostnames[host][
                "last_update"
            ]
        await self.update_readings(readings)

        # update attribute hostname
        self._conf_attr["hostname"]["options"] = ",".join(hostattr)
        self.set_attr_config(self._conf_attr)
        await utils.handle_define_attr(self._conf_attr, self, self.hash)

    async def login(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get("https://ddnss.de/") as resp:
                if resp.status != 200:
                    raise Exception(f"Open ddnss.de failed with status {resp.status}")
            async with session.get("https://ddnss.de/login.php") as resp:
                if resp.status != 200:
                    raise Exception(f"Open ddnss.de failed with status {resp.status}")

            async with session.post(
                "https://ddnss.de/do.php",
                data={
                    "action": "login",
                    "username": self.username,
                    "passwd": self.password,
                },
                headers=ddnssde.headers,
            ) as resp:
                if resp.status != 200:
                    raise Exception(
                        f"Failed to login to ddnss.de, HTTP status {resp.status}"
                    )

            self.cookie_jar = session.cookie_jar

    async def retrieve_ddnss_data(self):
        async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
            async with session.get(
                "https://ddnss.de/ua/index.php", headers=ddnssde.headers
            ) as resp:
                data = await resp.text()
                soup = BeautifulSoup(data, "html.parser")
                well_class = soup.find("div", {"class": "well"})
                if well_class is None:
                    return False
                self.update_key = well_class.find("b").text
                self.ddnss_mail = well_class.findAll("p")[1].text
                self.ddnss_login = well_class.findAll("p")[2].text
                self.update_key_ready.set()

            async with session.get(
                "https://ddnss.de/ua/vhosts_list.php", headers=ddnssde.headers
            ) as resp:
                data = await resp.text()
                soup = BeautifulSoup(data, "html.parser")
                self.hostnames = {}
                hostarr = soup.find("tbody").findAll("tr")
                for host in hostarr:
                    hostdetailsarr = host.findAll("td")
                    hostname = hostdetailsarr[1].find("u").text.split()[0]
                    ip = hostdetailsarr[2].text.split()[-1]
                    last_upd = hostdetailsarr[3].text
                    self.hostnames[hostname] = {"ip": ip, "last_update": last_upd}

            return True

    async def update_ip_loop(self):
        while True:
            if self._attr_hostname == "-":
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "Please set hostname attribute", 1
                )
                await self.hostname_ready.wait()

            await self.update_key_ready.wait()
            try:
                if await self.is_ip_updated():
                    await self.set_ddnss_ip()
                await asyncio.sleep(self._attr_ip_check_interval * 60)
            except Exception:
                self.logger.exception("Failed to check ip")
                await asyncio.sleep(30)

    async def set_attr_hostname(self, hash):
        if self._attr_hostname != "-":
            self.hostname_ready.set()
            self.hostname_ready.clear()
        else:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "Please set hostname attribute", 1
            )

    async def set_ddnss_ip(self):
        async with aiohttp.ClientSession(cookie_jar=self.cookie_jar) as session:
            async with session.get(
                f"http://ddnss.de/upd.php?key={self.update_key}"
                + f"&host={self._attr_hostname.replace('_','.')}",
                headers=ddnssde.headers,
            ) as resp:
                if resp.status == 200:
                    await self.update_ddnss_data()
                else:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "failed to update", 1
                    )
