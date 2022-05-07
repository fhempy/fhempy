"""API client for FusionSolar Kiosk."""
import logging
import html
import json

from .const import (
    ATTR_DATA,
    ATTR_FAIL_CODE,
    ATTR_SUCCESS,
    ATTR_DATA_REALKPI,
)

from requests import get
import aiohttp

_LOGGER = logging.getLogger(__name__)


class FusionSolarRestApi:

    ENERGY_FLOW_PATH = (
        "/rest/pvms/web/station/v1/overview/energy-flow?stationDn=STATION&_"
    )

    def __init__(self, logger, station, sessionid, region="region01eu5"):
        self.logger = logger
        self._region = region
        self._station = station
        self._sessionid = sessionid
        self._inverter_output_power = 0
        self._from_grid = 0
        self._to_grid = 0
        self._electrical_load = 0

    async def _get_rest_data(self, path):
        url = (
            "https://"
            + self._region
            + ".fusionsolar.huawei.com"
            + path.replace("STATION", self._station)
        )
        headers = {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;"
                "q=0.8,application/signed-exchange;v=b3;q=0.9"
            ),
            "accept-language": (
                "en-AT,en;q=0.9,de-AT;q=0.8,de;q=0.7,en-GB;q=0.6,en-US;q=0.5"
            ),
            "cache-control": "max-age=0",
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
        try:
            response = {}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    response = await resp.json()

            if response["success"] is True:
                return response["data"]
            else:
                self.logger.error(f"Failed to get data from {path}: {response}")
        except Exception:
            self.logger.exception(f"Failed to get data from {path}")
            return {}

    async def update(self):
        await self.update_energy_balance()
        await self.update_energy_flow()

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
            for node in result["flow"]["links"]:
                if node["description"]["label"] == "neteco.pvms.energy.flow.buy.power":
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

    async def update_energy_balance(self):
        pass

    @property
    def inverter_output_power(self):
        return self._inverter_output_power

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


class FusionSolarKioksApi:
    def __init__(self, host):
        self._host = host

    def getRealTimeKpi(self, id: str):
        url = self._host + "/rest/pvms/web/kiosk/v1/station-kiosk-file?kk=" + id
        headers = {
            "accept": "application/json",
        }

        try:
            response = get(url, headers=headers)
            # _LOGGER.debug(response.text)
            jsonData = response.json()

            if not jsonData[ATTR_SUCCESS]:
                raise FusionSolarKioskApiError(
                    f"Retrieving the data failed with failCode: {jsonData[ATTR_FAIL_CODE]}, data: {jsonData[ATTR_DATA]}"
                )

            # convert encoded html string to JSON
            jsonData[ATTR_DATA] = json.loads(html.unescape(jsonData[ATTR_DATA]))
            _LOGGER.debug("Received data for " + id + ": ")
            _LOGGER.debug(jsonData[ATTR_DATA][ATTR_DATA_REALKPI])
            return jsonData[ATTR_DATA][ATTR_DATA_REALKPI]

        except FusionSolarKioskApiError as error:
            _LOGGER.error(error)
            _LOGGER.debug(response.text)

        return {ATTR_SUCCESS: False}


class FusionSolarKioskApiError(Exception):
    pass
