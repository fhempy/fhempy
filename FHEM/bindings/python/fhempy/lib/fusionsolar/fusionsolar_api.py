"""API client for FusionSolar Kiosk."""
import asyncio
import codecs
import os
import time
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA384
from Cryptodome.PublicKey import RSA


@dataclass
class SignalSet:
    signals: list

    def __repr__(self):
        return repr(self.signals)

    def get_ids(self):
        return [signal.id for signal in self.signals]

    def get_name_by_id(self, id):
        for signal in self.signals:
            if signal.id == int(id):
                return signal.name.lower().replace(" ", "_")


@dataclass
class Signal:
    id: int
    name: str
    unit: str

    def __repr__(self):
        return f"{self.name} ({self.unit})"


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
    DEVICE_STATISTICS_SIGNALS = (
        "/rest/pvms/web/device/v1/device-statistics-signal?"
        + "deviceDn=%INVERTER_STATION%"
    )
    DEVICE_SIGNALS = "/rest/pvms/web/device/v1/device-history-data"

    def __init__(self, logger, username, password, region="eu5"):
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
        self._battery_soc = 0
        self._battery_battery_power = 0
        self._battery_charge_capacity = 0
        self._battery_discharge_capacity = 0
        self._string_output_power = 0
        self._available_signals = None

    async def get_pubkey(self, session):
        # pubkey to get pubkey
        url = "https://" + self._region + ".fusionsolar.huawei.com/unisso/pubkey"
        async with session.get(url) as resp:
            self.logger.debug(f"response from {url}: {resp}")
            j = await resp.json()
            return j

    async def validate_user(self, session):
        url = (
            "https://"
            + self._region
            + ".fusionsolar.huawei.com"
            + "/unisso/"
            + self._validate_user_ver
            + "/validateUser.action"
        )

        body = {
            "multiRegionName": "",
            "organizationName": "",
            "username": self._username,
            "password": self._password_encrypted
            if self._validate_user_ver == "v3"
            else self._password,
        }

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            "content-type": "application/json",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Chrome OS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

        async with session.post(
            url,
            json=body,
            headers=headers,
            max_redirects=20,
            params={
                "service": "/unisess/v1/auth?service=%2Fnetecowebext%2Fhome%2Findex.html",
                "decision": 1,
                "actionErrors": 465,
                "timeStamp": self._timestamp,
                "nonce": codecs.encode(os.urandom(16), "hex").decode(),
            },
        ) as resp:
            self.logger.debug(f"response from {url}: {resp}")
            j = await resp.json()
            return j

    async def login_redirect(self, session, redurl):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Chrome OS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        if redurl[0:4] == "http":
            self.api_base = redurl
            url = redurl
        else:
            url = "https://" + self._region + ".fusionsolar.huawei.com" + redurl
        async with session.get(url, max_redirects=20, headers=headers) as resp:
            return resp

    async def get_jsessionid(self, session):
        url = "https://" + self._region + ".fusionsolar.huawei.com/"
        async with session.get(url, max_redirects=20) as resp:
            return resp

    async def login(self):
        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                resp = await self.get_jsessionid(session)

                fusion_pubkey_json = await self.get_pubkey(session)
                self._validate_user_ver = "v2"
                if fusion_pubkey_json["enableEncrypt"]:
                    self._validate_user_ver = "v3"
                    self.public_key = RSA.import_key(
                        fusion_pubkey_json["pubKey"].encode("UTF-8")
                    )
                    cipher = PKCS1_OAEP.new(self.public_key, SHA384)
                    hex_pwd = cipher.encrypt(self._password.encode("UTF-8"))
                    self._password_encrypted = (
                        codecs.encode(hex_pwd, "base64").decode().replace("\n", "")
                        + fusion_pubkey_json["version"]
                    )
                    self._timestamp = fusion_pubkey_json["timeStamp"]

                # validateUser.action to get bspsessionid
                json_resp = await self.validate_user(session)
                redurl = json_resp["redirectURL"]

                if redurl:
                    resp = await self.login_redirect(session, redurl)
                    self._cookies = session.cookie_jar

                headers = {
                    "accept": "application/json",
                    "accept-language": "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5",
                    "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Chrome OS"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-requested-with": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                }

                url = self.api_base + "/unisess/v1/auth/session"
                async with session.get(url, headers=headers) as resp3:
                    self.logger.debug(f"response from {url}: {resp3}")
                    response = await resp3.json()
                    self._csrftoken = response["csrfToken"]

                headers = {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "en-AT,en;q=0.9",
                    "content-type": "application/json",
                    "roarand": self._csrftoken,
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
                    "timeZone": 1,
                    "sortId": "createTime",
                    "sortDir": "DESC",
                    "locale": "en_US",
                }
                url = self.api_base + "/rest/pvms/web/station/v1/station/station-list"
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
            self.logger.exception(f"Failed to get data: {ex}")
            return False

    async def _get_rest_data(self, path, params={}):
        current_utc_time = int(datetime.utcnow().timestamp() * 1000)
        path = path.replace("%STATION%", self._stationname).replace(
            "%CURRENT_UTC_TIME%", str(current_utc_time)
        )
        if self._inverter_station:
            path = path.replace("%INVERTER_STATION%", self._inverter_station)

        url = self.api_base + path
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
            "roarand": self._csrftoken,
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
            "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        resp = await self._get(url, headers, params=params)
        return resp

    async def send_idle(self):
        url = self.api_base + "/rest/plat/smapp/v1/idle"

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
        }
        await self._get(url, headers)

    async def _get(self, url, headers, max_retries=5, params={}):
        try:
            response = {}
            async with aiohttp.ClientSession(
                trust_env=True, headers=headers, cookie_jar=self._cookies
            ) as session:
                retry = 1
                while retry < max_retries:
                    retry += 1
                    async with session.get(url, params=params) as resp:
                        if resp.status != 200:
                            # wait a few seconds before login
                            self.logger.error(
                                f"Response from {url} was {resp.status}, try to relogin"
                            )
                            await asyncio.sleep(30)
                            await self.login()
                            continue
                        else:
                            if resp.headers["Content-Type"].startswith("text/html"):
                                await self.login()
                                continue
                            else:
                                response = await resp.json()
                                break

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
        self._battery_soc = 0
        self._battery_battery_power = 0
        self._battery_charge_capacity = 0
        self._battery_discharge_capacity = 0
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
                    if node["deviceTips"]["SOC"] != "--":
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

    async def update_available_device_signals(self):
        available_signals = await self._get_rest_data(
            FusionSolarRestApi.DEVICE_STATISTICS_SIGNALS
        )
        data = available_signals["signalList"]
        self._available_signals = SignalSet(
            signals=[
                Signal(row["id"], row["name"], row["unit"].get("unit", ""))
                for row in data
            ]
        )

    async def update_device_signals(self):
        if self._available_signals is None:
            await self.update_available_device_signals()

        self._device_signals = await self._get_rest_data(
            FusionSolarRestApi.DEVICE_SIGNALS,
            params={
                "deviceDn": self._inverter_station,
                "signalIds": self._available_signals.get_ids(),
                "date": int(datetime.now().timestamp() * 1000),
            },
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
    def device_signals(self):
        device_signals = {}
        for sigid in self._device_signals:
            sig_name = self._available_signals.get_name_by_id(sigid)
            sig_value_history = self._device_signals[sigid]["pmDataList"]
            last_val = "-"
            for row in sig_value_history:
                if "dnId" not in row:
                    continue
                last_val = row["counterValue"]
            device_signals[sig_name] = last_val
        return device_signals

    @property
    def data_string(self):
        return (
            f"Stationdetail Data:\n{self._stationdetail}\n\n"
            f"Energyflow Data:\n{self._energyflowdata}\n\n"
            f"Energybalance Data:\n{self._energy_balance}\n\n"
        )
