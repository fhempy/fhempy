"""API client for FusionSolar Kiosk."""
import aiohttp


class FusionSolarRestApi:

    ENERGY_FLOW_PATH = (
        "/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_"
    )
    STATION_DETAIL_PATH = (
        "/rest/pvms/web/station/v1/overview/station-detail?stationDn=STATION&_="
    )

    def __init__(self, logger, sessionid, stationname, region="region01eu5"):
        self.logger = logger
        self._region = region
        self._stationname = stationname
        self._sessionid = sessionid
        self._stationdetail = None
        self._inverter_output_power = 0
        self._from_grid = 0
        self._to_grid = 0
        self._electrical_load = 0
        self._battery_soc = None
        self._battery_battery_power = None
        self._battery_charge_capacity = None
        self._battery_discharge_capacity = None

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
            "cookie": f"bspsession={self._sessionid}",
        }
        await self._send(url, headers)

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
            "cookie": (
                "locale=en-us; user_time_a_lang=; "
                "user_digital_format=%2C%23%230.00; "
                "timezone=Europe%2FAmsterdam; delimiter=-; "
                "format=yyyy-MM-dd%20HH%3Amm%3Ass; "
                "timemode=client; timezoneoffset=60; user_time_show_dst=1; "
                "supportlang=en; lang=en; esc_first_visit_time=1654870587; "
                "__hau=HuaweiConnect.1654870589.1486370478; "
                f"bspsession={self._sessionid}"
            ),
            "Referer": (
                f"https://{self._region}.fusionsolar.huawei.com"
                "/pvmswebsite/assets/build/index.html"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        await self._send(url, headers)

    async def _send(self, url, headers):
        try:
            response = {}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    response = await resp.json()

            if "success" in response and response["success"] is True:
                if "data" in response:
                    return response["data"]
                return response

            return response
        except Exception:
            self.logger.exception(f"Failed to get data from {url}: {response}")
            return {}

    async def update(self):
        await self.update_station_detail()
        await self.update_energy_balance()
        await self.update_energy_flow()
        await self.send_idle()

    async def update_energy_flow(self):
        # https://region01eu5.fusionsolar.huawei.com/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_
        result = await self._get_rest_data(FusionSolarRestApi.ENERGY_FLOW_PATH)
        if "flow" in result:
            for node in result["flow"]["nodes"]:
                if node["name"] == "neteco.pvms.devTypeLangKey.inverter":
                    pass  # inverter values
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
            for node in result["flow"]["links"]:
                if "description" in node and "label" in node["description"]:
                    if (
                        node["description"]["label"]
                        == "neteco.pvms.energy.flow.buy.power"
                    ):
                        self._from_grid = float(
                            node["description"]["value"].replace(" kW", "")
                        )
                        self._to_grid = 0
                    elif (
                        node["description"]["label"]
                        == "neteco.pvms.KPI.kpiView.onGridPower"
                    ):
                        self._to_grid = float(
                            node["description"]["value"].replace(" kW", "")
                        )
                        self._from_grid = 0
                    elif (
                        node["description"]["label"]
                        == "neteco.pvms.basicUnifSignal.optimizer.outputPower"
                    ):
                        self._inverter_output_power = float(
                            node["description"]["value"].replace(" kW", "")
                        )
                    elif (
                        node["description"]["label"]
                        == "neteco.pvms.devTypeLangKey.string"
                    ):
                        self._string_output_power = float(
                            node["description"]["value"].replace(" kW", "")
                        )

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
        return round(self._stationdetail["dailySelfUseEnergy"], 2)

    @property
    def daily_use_energy(self):
        return round(self._stationdetail["dailyUseEnergy"], 2)

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
