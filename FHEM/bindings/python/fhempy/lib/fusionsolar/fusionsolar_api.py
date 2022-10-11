"""API client for FusionSolar Kiosk."""
import asyncio
import time
from datetime import datetime

import aiohttp


class FusionSolarRestApi:

    ENERGY_FLOW_PATH = (
        "/rest/pvms/web/station/v1/overview/energy-flow?"
        + "stationDn=%STATION%&_=%CURRENT_UTC_TIME%"
    )
    STATION_DETAIL_PATH = (
        "/rest/pvms/web/station/v1/overview/station-detail?"
        + "stationDn=%STATION%&_=%CURRENT_UTC_TIME%"
    )
    ENERGY_BALANCE = (
        "/rest/pvms/web/station/"
        + "v1/overview/energy-balance?stationDn=%STATION%&"
        + "timeDim=2&queryTime=%CURRENT_UTC_TIME%&timeZone=2&"
        + "timeZoneStr=Europe%2FBerlin&_=%CURRENT_UTC_TIME%"
    )
    DEVICE_SIGNALS = (
        "/rest/pvms/web/device/v1/device-real-kpi?"
        + "signalIds=10025&signalIds=10032&signalIds=10029&signalIds=10019&"
        + "signalIds=10022&signalIds=10006&signalIds=10020&signalIds=10021&"
        + "signalIds=10027&signalIds=10028&signalIds=21029&signalIds=10018&"
        + "signalIds=10008&signalIds=10009&signalIds=10010&signalIds=10011&"
        + "signalIds=10012&signalIds=10013&signalIds=10014&signalIds=10015&"
        + "signalIds=10016&signalIds=11002&signalIds=11005&signalIds=11008&"
        + "signalIds=11011&signalIds=11014&signalIds=11017&signalIds=11020&"
        + "signalIds=11023&signalIds=11026&signalIds=11029&signalIds=11032&"
        + "signalIds=11035&signalIds=11038&signalIds=11041&signalIds=11044&"
        + "signalIds=11047&signalIds=11050&signalIds=11053&signalIds=11056&"
        + "signalIds=11059&signalIds=11062&signalIds=11065&signalIds=11068&"
        + "signalIds=11071&signalIds=11001&signalIds=11004&signalIds=11007&"
        + "signalIds=11010&signalIds=11013&signalIds=11016&signalIds=11019&"
        + "signalIds=11022&signalIds=11025&signalIds=11028&signalIds=11031&"
        + "signalIds=11034&signalIds=11037&signalIds=11040&signalIds=11043&"
        + "signalIds=11046&signalIds=11049&signalIds=11052&signalIds=11055&"
        + "signalIds=11058&signalIds=11061&signalIds=11064&signalIds=11067&"
        + "signalIds=11070&signalIds=14001&signalIds=14002&signalIds=14003&"
        + "signalIds=14004&signalIds=14005&signalIds=14006&signalIds=14007&"
        + "signalIds=14008&signalIds=14009&signalIds=14010&signalIds=14011&"
        + "signalIds=14012&signalIds=14013&signalIds=14014&signalIds=14015&"
        + "signalIds=14016&signalIds=14017&signalIds=14018&signalIds=14019&"
        + "signalIds=14020&signalIds=14021&signalIds=14022&signalIds=14023&"
        + "signalIds=14024&signalIds=10047&signalIds=10051&"
        + "deviceDn=%INVERTER_STATION%&_=%CURRENT_UTC_TIME%"
    )

    def __init__(self, logger, username, password, region="region01eu5"):
        self.logger = logger
        self._region = region
        self._username = username
        self._password = password
        self._stationdetail = None
        self._energy_balance = None
        self._device_signals = None
        self._inverter_station = None
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
            async with aiohttp.ClientSession(trust_env=True) as session:
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

            async with aiohttp.ClientSession(
                trust_env=True, headers=headers
            ) as session:
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
                trust_env=True, headers=headers, cookies=response
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
        current_utc_time = int(datetime.utcnow().timestamp() * 1000)
        path = path.replace("%STATION%", self._stationname).replace(
            "%CURRENT_UTC_TIME%", str(current_utc_time)
        )
        if self._inverter_station:
            path = path.replace("%INVERTER_STATION%", self._inverter_station)

        url = "https://" + self._region + ".fusionsolar.huawei.com" + path
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
        if len(resp) == 0:
            # try again
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
                trust_env=True, headers=headers, cookie_jar=self._cookies
            ) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        # wait a few seconds before login
                        await asyncio.sleep(5)
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
        await self.update_device_signals()
        await self.send_idle()

    async def update_energy_flow(self):
        self._inverter_output_power = "-"
        self._from_grid = 0
        self._to_grid = 0
        self._electrical_load = "-"
        self._string_output_power = "-"
        self._battery_soc = None
        self._battery_battery_power = None
        self._battery_charge_capacity = None
        self._battery_discharge_capacity = None
        self._energyflowdata = None

        # https://region01eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_
        result = await self._get_rest_data(FusionSolarRestApi.ENERGY_FLOW_PATH)
        self._energyflowdata = result
        if "flow" in result:
            for node in result["flow"]["nodes"]:
                if node["name"] == "neteco.pvms.devTypeLangKey.inverter":
                    if node["deviceTips"]["ACTIVE_POWER"] == "--":
                        self._inverter_output_power = 0
                    else:
                        self._inverter_output_power = float(
                            node["deviceTips"]["ACTIVE_POWER"]
                        )
                    self._inverter_station = node["devIds"][0]
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
                        if node["description"]["value"] == "--":
                            self._to_grid = 0
                            self._from_grid = 0
                        else:
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
        self._energy_balance = await self._get_rest_data(
            FusionSolarRestApi.ENERGY_BALANCE
        )

    async def update_device_signals(self):
        self._device_signals = await self._get_rest_data(
            FusionSolarRestApi.DEVICE_SIGNALS
        )
        if "signals" not in self._device_signals:
            await asyncio.sleep(10)
            self._device_signals = await self._get_rest_data(
                FusionSolarRestApi.DEVICE_SIGNALS
            )

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
        if "selfUseNrg" in self._stationdetail["realNrgKpi"]["dailyNrg"]:
            return round(self._stationdetail["realNrgKpi"]["dailyNrg"]["selfUseNrg"], 2)
        return 0

    @property
    def daily_use_energy(self):
        if "useNrg" in self._stationdetail["realNrgKpi"]["dailyNrg"]:
            return round(self._stationdetail["realNrgKpi"]["dailyNrg"]["useNrg"], 2)
        return 0

    @property
    def daily_self_use_ratio(self):
        return self._energy_balance["selfUsePowerRatioByUse"]

    @property
    def daily_self_use_solar_ratio(self):
        return self._energy_balance["selfUsePowerRatioByProduct"]

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

    @property
    def string_details(self):
        string_details = {}
        if "signals" in self._device_signals:
            for signal in (11001, 11004):
                string_details[f"string_pv{int((signal-11001)/3+1)}"] = {
                    "voltage": self._device_signals["signals"][str(signal)]["value"],
                    "current": self._device_signals["signals"][str(signal + 1)][
                        "value"
                    ],
                }
        return string_details

    @property
    def data_string(self):
        return (
            f"Stationdetail Data:\n{self._stationdetail}\n\n"
            f"Energyflow Data:\n{self._energyflowdata}\n\n"
            f"Energybalance Data:\n{self._energy_balance}\n\n"
            f"Device Signals Data:\n{self._device_signals}\n"
        )
