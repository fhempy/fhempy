"""API client for FusionSolar Kiosk."""
import time

import aiohttp


class FusionSolarRestApi:

    ENERGY_FLOW_PATH = (
        "/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_"
    )
    STATION_DETAIL_PATH = (
        "/rest/pvms/web/station/v1/overview/station-detail?stationDn=STATION&_="
    )

    def __init__(self, logger, username, password, region="region01eu5"):
        self.logger = logger
        self._region = region
        self._username = username
        self._password = password
        self._stationdetail = None
        self._inverter_output_power = 0
        self._from_grid = 0
        self._to_grid = 0
        self._electrical_load = 0
        self._battery_soc = None
        self._battery_battery_power = None
        self._battery_charge_capacity = None
        self._battery_discharge_capacity = None
        self._string_output_power = 0

    async def login(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://" + self._region + ".fusionsolar.huawei.com/"
                async with session.get(url) as resp:
                    self.logger.debug(f"response from {url}: {resp}")
                    self._regionhost = resp.host

                    if self._regionhost is None:
                        self.logger.error(f"Failed to get region host: {resp}")
                        return False

            url = (
                "https://"
                + self._regionhost
                + "/unisso/v2/"
                + "validateUser.action?service="
                + "%2Funisess%2Fv1%2Fauth%3Fservice%3D%252F"
                + "netecowebext%252Fhome%252Findex.html"
            )

            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "en-AT,en;q=0.9",
                "content-type": "application/json",
                "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Chrome OS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest",
                "Referer": "https://"
                + self._regionhost
                + "/unisso/login.action?service=%2Funisess%2Fv1%2Fauth%3Fservice%3D%252Fnetecowebext%252Fhome%252Findex.html",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }
            body = {
                "organizationName": "",
                "username": self._username,
                "password": self._password,
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, json=body) as resp:
                    self.logger.debug(f"response from {url}: {resp}")
                    response = resp.cookies

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-language": "en-AT,en;q=0.9",
                "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Chrome OS"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-site",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "Referer": "https://" + self._regionhost + "/",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }

            async with aiohttp.ClientSession(
                headers=headers, cookies=response
            ) as session:
                url = "https://" + self._region + ".fusionsolar.huawei.com/"
                async with session.get(
                    url,
                    max_redirects=20,
                ) as resp2:
                    self.logger.debug(f"response from {url}: {resp2}")
                    if resp2.status == 200:
                        self._cookies = session.cookie_jar
                    else:
                        self.logger.error(f"Failed to retrieve cookies: {resp2}")
                        return False

                url = (
                    "https://"
                    + self._region
                    + ".fusionsolar.huawei.com/unisess/v1/auth/session"
                )
                async with session.get(url) as resp3:
                    self.logger.debug(f"response from {url}: {resp3}")
                    response = await resp3.json()
                    csrfToken = response["csrfToken"]

                headers = {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "en-AT,en;q=0.9",
                    "content-type": "application/json",
                    "roarand": csrfToken,
                    "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Chrome OS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-non-renewal-session": "true",
                    "x-requested-with": "XMLHttpRequest",
                    "x-timezone-offset": "120",
                    "Referer": "https://"
                    + self._region
                    + ".fusionsolar.huawei.com/pvmswebsite/assets/build/index.html",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }
                body = {
                    "curPage": 1,
                    "pageSize": 10,
                    "gridConnectionTime": "",
                    "queryTime": round(time.time() * 1000),
                    "timeZone": 2,
                    "sortId": "createTime",
                    "sortDir": "DESC",
                    "locale": "en_US",
                }
                url = (
                    "https://"
                    + self._region
                    + ".fusionsolar.huawei.com/rest/pvms/web/station/v1/station/station-list"
                )
                async with session.post(
                    url,
                    json=body,
                    headers=headers,
                ) as resp3:
                    self.logger.debug(f"response from {url}: {resp3}")
                    response = await resp3.json()
                    self._stationname = response["data"]["list"][0]["dn"]

            return True

        except Exception as ex:
            self.logger.exception(f"Failed to get data from {url}: {ex}")
            return False

    async def _get_rest_data(self, path):
        url = (
            "https://"
            + self._region
            + ".fusionsolar.huawei.com"
            + path.replace("STATION", self._stationname)
        )

        headers = {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;"
                "q=0.8,application/signed-exchange;v=b3;q=0.9,"
                "application/json, text/javascript, */*; q=0.01"
            ),
            "accept-language": (
                "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5"
            ),
            "cache-control": "max-age=0",
            "content-type": "application/json",
            "sec-ch-ua": (
                '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"'
            ),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Chrome OS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        resp = await self._get(url, headers)
        return resp

    async def send_idle(self):
        url = (
            "https://"
            + self._region
            + ".fusionsolar.huawei.com/rest/plat/smapp/v1/idle"
        )

        headers = {
            "accept": "application/json",
            "accept-language": (
                "en-AT,en;q=0.9,de-AT;q=0.8," "de;q=0.7,en-GB;q=0.6,en-US;q=0.5"
            ),
            "content-type": "application/json",
            "sec-ch-ua": (
                '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"'
            ),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"ChromeOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-non-renewal-active": "true",
            "x-non-renewal-session": "false",
            "x-requested-with": "XMLHttpRequest",
            "Referer": (
                f"https://{self._region}.fusionsolar.huawei.com"
                "/pvmswebsite/assets/build/index.html"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        await self._get(url, headers)

    async def _get(self, url, headers):
        try:
            response = {}
            async with aiohttp.ClientSession(
                headers=headers, cookie_jar=self._cookies
            ) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await self.login()
                        return {}

                    response = await resp.json()

            if "success" in response and response["success"] is True:
                if "data" in response:
                    return response["data"]
                return response

            return response
        except Exception as ex:
            self.logger.exception(f"Failed to get data from {url}: {ex}")
            return {}

    async def update(self):
        await self.update_station_detail()
        await self.update_energy_balance()
        await self.update_energy_flow()
        await self.send_idle()

    async def update_energy_flow(self):
        self._inverter_output_power = "-"
        self._from_grid = "-"
        self._to_grid = "-"
        self._electrical_load = "-"
        self._string_output_power = "-"
        self._battery_soc = None
        self._battery_battery_power = None
        self._battery_charge_capacity = None
        self._battery_discharge_capacity = None

        # https://region01eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_
        result = await self._get_rest_data(FusionSolarRestApi.ENERGY_FLOW_PATH)
        if "flow" in result:
            for node in result["flow"]["nodes"]:
                if node["name"] == "neteco.pvms.devTypeLangKey.inverter":
                    if node["deviceTips"]["ACTIVE_POWER"] == "--":
                        self._inverter_output_power = 0
                    else:
                        self._inverter_output_power = float(
                            node["deviceTips"]["ACTIVE_POWER"]
                        )
                elif node["name"] == "neteco.pvms.KPI.kpiView.electricalLoad":
                    self._electrical_load = float(
                        node["description"]["value"].replace(" kW", "")
                    )
                elif node["name"] == "neteco.pvms.devTypeLangKey.energy_store":
                    self._battery_soc = float(node["deviceTips"]["SOC"])
                    self._battery_charge_capacity = float(
                        node["deviceTips"]["CHARGE_CAPACITY"]
                    )
                    self._battery_battery_power = float(
                        node["deviceTips"]["BATTERY_POWER"]
                    )
                    self._battery_discharge_capacity = float(
                        node["deviceTips"]["DISCHARGE_CAPACITY"]
                    )
                elif node["name"] == "neteco.pvms.devTypeLangKey.string":
                    self._string_output_power = float(
                        node["description"]["value"].replace(" kW", "")
                    )
            for node in result["flow"]["links"]:
                if "description" in node and "label" in node["description"]:
                    if (
                        node["description"]["label"]
                        == "neteco.pvms.energy.flow.buy.power"
                    ):
                        if node["fromNode"] == "3":
                            # from grid is fromNode 3
                            self._from_grid = float(
                                node["description"]["value"].replace(" kW", "")
                            )
                            self._to_grid = 0
                        else:
                            # to grid is fromNode 2
                            self._to_grid = float(
                                node["description"]["value"].replace(" kW", "")
                            )
                            self._from_grid = 0

    async def update_energy_balance(self):
        pass

    async def update_station_detail(self):
        # https://region01eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/overview/station-detail?stationDn=STATION&_=
        self._stationdetail = await self._get_rest_data(
            FusionSolarRestApi.STATION_DETAIL_PATH
        )

    @property
    def station(self):
        return self._stationdetail["dn"]

    @property
    def co2_saved(self):
        return self._stationdetail["co2"]

    @property
    def battery_soc(self):
        return self._battery_soc

    @property
    def battery_charge_capacity(self):
        return self._battery_charge_capacity

    @property
    def battery_power(self):
        return self._battery_battery_power

    @property
    def battery_discharge_capacity(self):
        return self._battery_discharge_capacity

    @property
    def total_lifetime_energy(self):
        return float(self._stationdetail["cumulativeEnergy"])

    @property
    def total_current_day_energy(self):
        return float(self._stationdetail["dailyEnergy"])

    @property
    def total_current_month_energy(self):
        return float(self._stationdetail["monthEnergy"])

    @property
    def total_current_year_energy(self):
        return float(self._stationdetail["yearEnergy"])

    @property
    def grid_connected_time(self):
        return self._stationdetail["gridConnectedTime"]

    @property
    def installed_capacity(self):
        return self._stationdetail["installedCapacity"]

    @property
    def daily_self_use_energy(self):
        return round(self._stationdetail["realNrgKpi"]["dailyNrg"]["selfUseNrg"], 2)

    @property
    def daily_use_energy(self):
        return round(self._stationdetail["realNrgKpi"]["dailyNrg"]["useNrg"], 2)

    @property
    def daily_self_use_ratio(self):
        if self.daily_self_use_energy == 0:
            return 0

        return round(self.daily_self_use_energy / self.daily_use_energy * 100, 2)

    @property
    def daily_self_use_solar_ratio(self):
        if self.total_current_day_energy == 0:
            return 0

        return round(
            self.daily_self_use_energy / self.total_current_day_energy * 100,
            2,
        )

    @property
    def inverter_output_power(self):
        return self._inverter_output_power

    @property
    def string_output_power(self):
        return self._string_output_power

    @property
    def electrical_load(self):
        return self._electrical_load

    @property
    def grid_power(self):
        if self._to_grid == 0 and self._from_grid == 0:
            return 0

        if self._to_grid > 0:
            return -(self._to_grid)

        return self._from_grid

    @property
    def to_grid_power(self):
        return self._to_grid

    @property
    def from_grid_power(self):
        return self._from_grid
