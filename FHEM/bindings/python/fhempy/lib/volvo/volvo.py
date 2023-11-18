import asyncio

import aiohttp

from .. import fhem, generic


class volvo(generic.FhemModule):

    VEHICLELIST = "https://api.volvocars.com/extended-vehicle/v1/vehicles"
    VEHICLE_COMMANDS = (
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/commands"
    )
    VEHICLE_COMMANDS_ACCEPT = (
        "application/vnd.volvocars.api.connected-vehicle.commandlist.v1+json"
    )

    REGULAR_UPDATE_URLS = {
        "https://api.volvocars.com/energy/v1/vehicles/{vin}/recharge-status": "application/vnd.volvocars.api.energy.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/doors": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/environment": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/engine": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/engine-status": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/odometer": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/statistics": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/tyres": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
        "https://api.volvocars.com/connected-vehicle/v1/vehicles/{vin}/warnings": "application/vnd.volvocars.api.connected-vehicle.vehicledata.v1+json",
    }

    def __init__(self, logger):
        super().__init__(logger)

        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.vin = "NO_VIN"

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self.session = aiohttp.ClientSession()

        self.attr_config = {
            "car": {
                "default": "",
                "help": "Select the car you would like to control.",
            },
            "update_interval": {
                "default": 5,
                "format": "int",
                "help": "Readings update intervall in minutes (default 5min).",
            },
        }
        await self.set_attr_config(self.attr_config)
        await self.set_icon("car")

        if len(args) != 6:
            return "Usage: define my_volvo fhempy volvo appkey username password"
        self.appkey = args[3]
        self.username = args[4]
        self.password = args[5]
        self.create_async_task(self.update_loop())

    async def Undefine(self, hash):
        if self.session:
            await self.session.close()

    async def login(self):
        url = "https://volvoid.eu.volvocars.com/as/token.oauth2"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "authorization": (
                "Basic "
                "aDRZZjBiOlU4WWtTYlZsNnh3c2c1WVFxWmZyZ1ZtSWFEcG"
                "hPc3kxUENhVXNpY1F0bzNUUjVrd2FKc2U0QVpkZ2ZJZmNMeXc="
            ),
            "access_token_manager_id": "JWTh4Yf0b",
            "user-agent": "okhttp/4.10.0",
        }
        params = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "scope": " ".join(
                [
                    "openid",
                    "email",
                    "profile",
                    "care_by_volvo:financial_information:invoice:read",
                    "care_by_volvo:financial_information:payment_method",
                    "care_by_volvo:subscription:read",
                    "customer:attributes",
                    "customer:attributes:write",
                    "order:attributes",
                    "vehicle:attributes",
                    "tsp_customer_api:all",
                    "conve:brake_status",
                    "conve:climatization_start_stop",
                    "conve:command_accessibility",
                    "conve:commands",
                    "conve:diagnostics_engine_status",
                    "conve:diagnostics_workshop",
                    "conve:doors_status",
                    "conve:engine_status",
                    "conve:environment",
                    "conve:fuel_status",
                    "conve:honk_flash",
                    "conve:lock",
                    "conve:lock_status",
                    "conve:navigation",
                    "conve:odometer_status",
                    "conve:trip_statistics",
                    "conve:tyre_status",
                    "conve:unlock",
                    "conve:vehicle_relation",
                    "conve:warnings",
                    "conve:windows_status",
                    "energy:battery_charge_level",
                    "energy:charging_connection_status",
                    "energy:charging_system_status",
                    "energy:electric_range",
                    "energy:estimated_charging_time",
                    "energy:recharge_status",
                    "vehicle:attributes",
                ]
            ),
        }
        try:
            response = {}
            async with self.session.post(url, headers=headers, data=params) as resp:
                if resp.content_type != "application/json":
                    await fhem.readingsSingleUpdate(self.hash, "state", "Login failed")
                    return

                response = await resp.json()

                if resp.status == 200:
                    self.access_token = response["access_token"]
                    self.refresh_token = response["refresh_token"]
                    self.expires_in = response["expires_in"]
                else:
                    self.logger.error(f"Failed to get data from {url}: {response}")
        except Exception:
            self.logger.exception(f"Failed to get data from {url}")

    async def update_with_refresh_token(self):
        url = "https://volvoid.eu.volvocars.com/as/token.oauth2"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "authorization": (
                "Basic "
                "aDRZZjBiOlU4WWtTYlZsNnh3c2c1WVFxWmZyZ1ZtSWFEcG"
                "hPc3kxUENhVXNpY1F0bzNUUjVrd2FKc2U0QVpkZ2ZJZmNMeXc="
            ),
            "user-agent": "okhttp/4.10.0",
        }
        params = {
            "access_token_manager_id": "JWTh4Yf0b",
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        try:
            response = {}
            async with self.session.post(url, headers=headers, data=params) as resp:
                if resp.content_type != "application/json":
                    await fhem.readingsSingleUpdate(self.hash, "state", "Login failed")
                    return

                response = await resp.json()

                if resp.status == 200:
                    self.access_token = response["access_token"]
                    self.refresh_token = response["refresh_token"]
                    self.expires_in = response["expires_in"]
                else:
                    self.logger.error(f"Failed to get data from {url}: {response}")
        except Exception:
            self.logger.exception(f"Failed to get data from {url}")

    async def update_loop(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        await self.login()
        if self.access_token is None:
            await fhem.readingsSingleUpdate(self.hash, "state", "connection failed", 1)
            return

        self.create_async_task(self.update_token())
        await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)

        await self.get_cars()
        await self.get_commands()

        while True:
            await self.get_regular_update_urls()
            await asyncio.sleep(1800)

    async def get_commands(self):
        cmds = await self.volvo_get(
            volvo.VEHICLE_COMMANDS, volvo.VEHICLE_COMMANDS_ACCEPT
        )
        set_conf = {}
        for cmd in cmds["data"]:
            set_conf[cmd["command"].lower()] = {
                "function": "set_command",
                "function_param": {"command": cmd["command"], "href": cmd["href"]},
            }
        await self.set_set_config(set_conf)

    async def set_command(self, hash, params):
        cmd = params["function_param"]["command"]
        url = params["function_param"]["href"]
        self.create_async_task(self.execute_command(cmd, url))

    async def execute_command(self, command, url):
        cmd_type = command.replace("_", "").lower()
        headers = {
            "content-type": f"application/vnd.volvocars.api.connected-vehicle.{cmd_type}.v1+json",
            "vcc-api-key": self.appkey,
            "authorization": f"Bearer {self.access_token}",
        }
        try:
            response = {}
            data = None
            if cmd_type == "unlock":
                data = {"unlockDuration": 120}
            async with self.session.post(url, headers=headers, data=data) as resp:
                response = await resp.json()

                if response["status"] == 202:
                    await asyncio.sleep(10)
                    async_href = response["async"]["href"]
                    resp = await self.volvo_get(
                        async_href,
                        "application/vnd.volvocars.api.connected-vehicle.requestdetailresponse.v1+json",
                    )
                    if resp["status"] == 200:
                        await fhem.readingsSingleUpdate(
                            self.hash, "lastcommand", "ok", 1
                        )
                    else:
                        await fhem.readingsSingleUpdate(
                            self.hash, "lastcommand", "failed", 1
                        )
        except Exception:
            self.logger.exception(f"Failed to get data from {url}")
            return {}

    async def update_token(self):
        while True:
            await asyncio.sleep(self.expires_in - 30)
            await self.update_with_refresh_token()

    async def get_regular_update_urls(self):
        for url in volvo.REGULAR_UPDATE_URLS:
            start = url.rfind("/") + 1
            domain = url[start:].replace("-", "_")
            data = await self.volvo_get(url, volvo.REGULAR_UPDATE_URLS[url])
            await self.update_readings(data["data"], domain)

    async def get_cars(self):
        cars = await self.volvo_get(volvo.VEHICLELIST)
        if len(cars["vehicles"]) == 0:
            self.logger.error("No cars found")
            return

        self.vin = cars["vehicles"][0]["id"]

    async def update_readings(self, data, domain=""):
        try:
            for reading in data:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, domain + "_" + reading, data[reading]["value"], 1
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash,
                    domain + "_" + reading + "_timestamp",
                    data[reading]["timestamp"],
                    1,
                )
        except Exception:
            self.logger.exception("Failed to update readings")

    async def volvo_get(self, url, accept_header="application/json"):
        url = url.replace("{vin}", self.vin)
        headers = {
            "accept": accept_header,
            "vcc-api-key": self.appkey,
            "authorization": f"Bearer {self.access_token}",
        }
        try:
            response = {}
            async with self.session.get(url, headers=headers) as resp:
                response = await resp.json()

                if resp.status == 200:
                    return response
                else:
                    self.logger.error(f"Failed to get data from {url}: {response}")
        except Exception:
            self.logger.exception(f"Failed to get data from {url}")
            return {}
