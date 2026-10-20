import asyncio
import json
import time
from datetime import datetime

import aiohttp
from volvocarsapi.api import VolvoCarsApi
from volvocarsapi.auth import AccessTokenManager
from volvocarsapi.models import VolvoApiException, VolvoAuthException
from yarl import URL

from .. import fhem, generic, utils

AUTH_URL = "https://volvoid.eu.volvocars.com/as/authorization.oauth2"
TOKEN_URL = "https://volvoid.eu.volvocars.com/as/token.oauth2"
# client of the Volvo Cars app, the only way to log in with username/password
CLIENT_ID = "h4Yf0b"
AUTH_BASIC = (
    "Basic "
    "aDRZZjBiOlU4WWtTYlZsNnh3c2c1WVFxWmZyZ1ZtSWFEcG"
    "hPc3kxUENhVXNpY1F0bzNUUjVrd2FKc2U0QVpkZ2ZJZmNMeXc="
)
SCOPES = [
    "openid",
    "conve:brake_status",
    "conve:climatization_start_stop",
    "conve:command_accessibility",
    "conve:commands",
    "conve:diagnostics_engine_status",
    "conve:diagnostics_workshop",
    "conve:doors_status",
    "conve:engine_status",
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
]
TOKEN_READING = ".volvo_token"
# refresh token doesn't rotate and expires ~180 days after the OTP login
REFRESH_TOKEN_MAX_AGE = 180 * 24 * 3600
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30)


class VolvoLoginRequired(Exception):
    """A new login with one-time password is required."""


class VolvoIdAuth(AccessTokenManager):
    """Volvo ID login with username, password and one-time password (e-mail).

    Volvo disabled the password-only login, the app now always asks for a
    one-time password. Afterwards the refresh token keeps the login alive.
    """

    def __init__(self, websession, logger, on_token_update):
        super().__init__(websession)
        self.logger = logger
        self.token = None
        self._on_token_update = on_token_update
        self._lock = asyncio.Lock()
        self._flow_session = None
        self._otp_url = None

    @property
    def otp_pending(self):
        return self._otp_url is not None

    async def async_get_access_token(self):
        async with self._lock:
            if self.token is None:
                raise VolvoLoginRequired("No login available")
            if self.token.get("expires_at", 0) < time.time() + 60:
                await self._async_refresh()
            return self.token["access_token"]

    def invalidate_access_token(self):
        if self.token:
            self.token["expires_at"] = 0

    async def _async_refresh(self):
        try:
            data = await self._token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self.token["refresh_token"],
                }
            )
        except aiohttp.ClientResponseError as ex:
            if ex.status in (400, 401, 403):
                self.token = None
                raise VolvoLoginRequired("Refresh token expired") from ex
            raise VolvoApiException(str(ex), "token refresh") from ex
        except (aiohttp.ClientError, TimeoutError) as ex:
            raise VolvoApiException(ex.__class__.__name__, "token refresh") from ex
        # refresh token is usually not returned again
        data.setdefault("refresh_token", self.token["refresh_token"])
        await self._set_token(data, self.token.get("login_at", time.time()))

    async def _token_request(self, data):
        headers = {
            "authorization": AUTH_BASIC,
            "x-xsrf-header": "PingFederate",
        }
        async with self.websession.post(
            TOKEN_URL, headers=headers, data=data, timeout=REQUEST_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

    async def _set_token(self, data, login_at):
        self.token = {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": time.time() + int(data.get("expires_in", 1800)),
            "login_at": login_at,
        }
        await self._on_token_update(self.token)

    async def _flow_request(self, url, *, json_data=None, form_data=None):
        # Volvo ID returns http links which redirect and lose the POST data
        url = URL(url)
        if url.host and url.host.endswith(".volvocars.com"):
            url = url.with_scheme("https")
        headers = {"x-xsrf-header": "PingFederate"}
        async with self._flow_session.post(
            url,
            headers=headers,
            json=json_data,
            data=form_data,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
        ) as resp:
            try:
                data = await resp.json(content_type=None)
            except ValueError:
                data = None
            if resp.status >= 400 or not isinstance(data, dict):
                message = data.get("message", "") if isinstance(data, dict) else ""
                raise VolvoAuthException(f"{resp.status} {message}".strip(), "login")
            return data

    async def async_start_login(self, username, password):
        """Send username/password. Returns True if logged in, False if the
        one-time password, sent by e-mail, is required."""
        await self.close()
        # own session to keep the cookies of the login flow
        self._flow_session = aiohttp.ClientSession()
        data = await self._flow_request(
            AUTH_URL,
            form_data={
                "client_id": CLIENT_ID,
                "response_type": "code",
                "response_mode": "pi.flow",
                "acr_values": "urn:volvoid:aal:bronze:2sv",
                "scope": " ".join(SCOPES),
            },
        )
        if data.get("status") == "USERNAME_PASSWORD_REQUIRED":
            url = data["_links"]["checkUsernamePassword"]["href"]
            data = await self._flow_request(
                url + "?action=checkUsernamePassword",
                json_data={"username": username, "password": password},
            )
        status = data.get("status")
        if status == "OTP_REQUIRED":
            self._otp_url = data["_links"]["checkOtp"]["href"] + "?action=checkOtp"
            return False
        if status == "COMPLETED":
            await self._complete(data)
            return True
        await self.close()
        raise VolvoAuthException(
            f"Unexpected login status {status}: {data.get('message', '')}", "login"
        )

    async def async_submit_otp(self, otp):
        if self._otp_url is None:
            raise VolvoAuthException("No login in progress", "otp")
        data = await self._flow_request(self._otp_url, json_data={"otp": otp})
        if data.get("status") != "OTP_VERIFIED":
            raise VolvoAuthException(
                f"One-time password not accepted: {data.get('status')}", "otp"
            )
        url = data["_links"]["continueAuthentication"]["href"]
        data = await self._flow_request(url + "?action=continueAuthentication")
        if data.get("status") != "COMPLETED":
            raise VolvoAuthException(
                f"Login not completed: {data.get('status')}", "otp"
            )
        await self._complete(data)

    async def _complete(self, data):
        code = data["authorizeResponse"]["code"]
        await self.close()
        token = await self._token_request(
            {"code": code, "grant_type": "authorization_code"}
        )
        await self._set_token(token, time.time())

    async def close(self):
        self._otp_url = None
        if self._flow_session:
            await self._flow_session.close()
            self._flow_session = None


class volvo(generic.FhemModule):

    # reading prefix: library function
    STATUS_ENDPOINTS = {
        "brakes": "async_get_brakes_status",
        "diagnostics": "async_get_diagnostics",
        "doors": "async_get_doors_status",
        "engine": "async_get_engine_warnings",
        "engine_status": "async_get_engine_status",
        "fuel": "async_get_fuel_status",
        "odometer": "async_get_odometer",
        "statistics": "async_get_statistics",
        "tyres": "async_get_tyre_states",
        "warnings": "async_get_warnings",
        "windows": "async_get_window_states",
    }

    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)

        self.session = None
        self.auth = None
        self.api = None
        self.vin = None
        self.vehicle = None
        self.isECar = False
        self._encryption_key = None
        self._update_task = None
        self._location_available = True

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self.attr_config = {
            "car": {
                "default": "",
                "help": "VIN of the car you would like to control "
                "(only needed for more than one car).",
            },
            "interval": {
                "default": 300,
                "format": "int",
                "help": "Readings update intervall in seconds (default 5min).",
            },
        }
        await self.set_attr_config(self.attr_config)
        await self.set_icon("car")

        if len(args) != 6:
            return "Usage: define my_volvo fhempy volvo VCC_API_KEY username password"
        self.appkey = args[3]
        self.username = args[4]
        self.password = args[5]

        self.set_config = {
            "otp": {
                "args": ["code"],
                "help": "One-time password from the Volvo e-mail.",
            },
            "login": {
                "help": "Start a new login, Volvo sends a new one-time password.",
            },
            "update": {"help": "Update all readings now."},
        }
        await self.set_set_config(self.set_config)

        self._encryption_key = await fhem.getUniqueId(hash)
        self.session = aiohttp.ClientSession()
        self.auth = VolvoIdAuth(self.session, self.logger, self._store_token)
        self.api = VolvoCarsApi(self.session, self.auth, self.appkey)
        self.create_async_task(self.connect())

    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self.auth:
            await self.auth.close()
        if self.session:
            await self.session.close()
            self.session = None

    async def _store_token(self, token):
        encrypted = utils.encrypt_string(json.dumps(token), self._encryption_key)
        await fhem.readingsSingleUpdate(self.hash, TOKEN_READING, encrypted, 1)
        valid_until = datetime.fromtimestamp(
            token["login_at"] + REFRESH_TOKEN_MAX_AGE
        ).strftime("%Y-%m-%d")
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "login_valid_until", valid_until, 1
        )

    async def _load_token(self):
        encrypted = await fhem.ReadingsVal(self.hash["NAME"], TOKEN_READING, "")
        if encrypted == "":
            return None
        try:
            return json.loads(utils.decrypt_string(encrypted, self._encryption_key))
        except Exception:
            self.logger.warning("Stored Volvo login can't be read, login again")
            return None

    async def connect(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        if self.auth.token is None:
            self.auth.token = await self._load_token()
        if self.auth.token is None:
            await self.start_login()
            return
        await self.start_updates()

    async def start_login(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "login", 1)
        try:
            done = await self.auth.async_start_login(self.username, self.password)
        except Exception as ex:
            self.logger.error(f"Volvo login failed: {ex}")
            await fhem.readingsSingleUpdate(
                self.hash, "state", "login failed, check username/password", 1
            )
            return
        if done:
            await self.start_updates()
            return
        self.logger.info(
            "Volvo sent a one-time password by e-mail, "
            f"please use: set {self.hash['NAME']} otp <code>"
        )
        await fhem.readingsSingleUpdate(
            self.hash, "state", "one-time password sent by e-mail, use set otp", 1
        )

    def set_otp(self, hash, params):
        self.create_async_task(self._handle_otp(str(params["code"]).strip()))

    async def _handle_otp(self, otp):
        try:
            if not self.auth.otp_pending:
                # login flow expired (e.g. restart), start new one
                await self.start_login()
                return
            await self.auth.async_submit_otp(otp)
        except Exception as ex:
            self.logger.error(f"Volvo one-time password failed: {ex}")
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "one-time password wrong, try again or use set login",
                1,
            )
            return
        await self.start_updates()

    def set_login(self, hash, params):
        self.create_async_task(self.start_login())

    def set_update(self, hash, params):
        self.create_async_task(self.refresh_readings())

    async def refresh_readings(self):
        try:
            await self.update_readings()
        except VolvoLoginRequired:
            await self.start_login()

    async def set_attr_car(self, hash):
        if self.auth and self.auth.token:
            await self.start_updates()

    async def start_updates(self):
        if self._update_task and self._update_task is not asyncio.current_task():
            self._update_task.cancel()
            # wait until the old update loop has stopped
            await asyncio.gather(self._update_task, return_exceptions=True)
        self._update_task = self.create_async_task(self.update_loop())

    async def update_loop(self):
        try:
            if not await self.get_car():
                return
            await self.get_commands()
            while True:
                await self.update_readings()
                await asyncio.sleep(self._attr_interval)
        except VolvoLoginRequired:
            self.logger.warning("Volvo login expired, new login required")
            self.create_async_task(self.start_login())

    async def get_car(self):
        vins = await self._get_vins()
        self.vin = await self._select_vin(vins)
        if self.vin is None:
            return False
        self.api.vin = self.vin
        await self._update_car_details()
        await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
        return True

    async def _get_vins(self):
        while True:
            try:
                return await self.api.async_get_vehicles()
            except VolvoLoginRequired:
                raise
            except VolvoAuthException as ex:
                self.logger.error(f"Failed to get cars, check VCC API key: {ex}")
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "access denied, check VCC API key", 1
                )
                self.auth.invalidate_access_token()
            except Exception as ex:
                self.logger.error(f"Failed to get cars: {ex}")
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "failed to get cars", 1
                )
            await asyncio.sleep(self._attr_interval)

    async def _select_vin(self, vins):
        found = ",".join(vins)
        if len(vins) == 0:
            state = "no cars found"
        elif self._attr_car in vins:
            return self._attr_car
        elif self._attr_car != "":
            state = "car not found, found cars: " + found
        elif len(vins) == 1:
            return vins[0]
        else:
            self.logger.info(f"Car IDs: {found}")
            state = "found cars: " + found + " Please set the attribute car"
        await fhem.readingsSingleUpdate(self.hash, "state", state, 1)
        return None

    async def _update_car_details(self):
        try:
            self.vehicle = await self.api.async_get_vehicle_details()
        except VolvoLoginRequired:
            raise
        except Exception as ex:
            self.logger.error(f"Failed to get car details: {ex}")
            self.vehicle = None
        if self.vehicle is None:
            return
        self.isECar = self.vehicle.has_battery_engine()
        details = {
            "car_vin": self.vehicle.vin,
            "car_modelYear": self.vehicle.model_year,
            "car_gearbox": self.vehicle.gearbox,
            "car_fuelType": self.vehicle.fuel_type,
            "car_externalColour": self.vehicle.external_colour,
            "car_batteryCapacityKWH": self.vehicle.battery_capacity_kwh,
        }
        if self.vehicle.description:
            details["car_model"] = self.vehicle.description.model
        await self._bulk_update(details)

    async def _bulk_update(self, values):
        await fhem.readingsBeginUpdate(self.hash)
        for reading, value in values.items():
            if value is not None:
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def get_commands(self):
        try:
            cmds = await self.api.async_get_commands()
        except VolvoLoginRequired:
            raise
        except Exception as ex:
            self.logger.error(f"Failed to get commands: {ex}")
            return
        set_conf = dict(self.set_config)
        for cmd in cmds:
            if cmd is None:
                continue
            set_conf[cmd.command.lower()] = {
                "function": "set_command",
                "function_param": cmd.href.rstrip("/").rsplit("/", 1)[-1],
            }
        await self.set_set_config(set_conf)

    def set_command(self, hash, params):
        self.create_async_task(
            self.execute_command(params["cmd"], params["function_param"])
        )

    async def execute_command(self, name, command):
        await fhem.readingsSingleUpdate(self.hash, "lastcommand_name", name, 1)
        try:
            result = await self.api.async_execute_command(command)
        except VolvoLoginRequired:
            await self.start_login()
            return
        except Exception as ex:
            self.logger.error(f"Command {name} failed: {ex}")
            await fhem.readingsSingleUpdate(self.hash, "lastcommand", "failed", 1)
            return
        status = result.invoke_status if result else "UNKNOWN"
        message = result.message if result else ""
        await fhem.readingsSingleUpdate(self.hash, "lastcommand", status, 1)
        await fhem.readingsSingleUpdate(
            self.hash, "lastcommand_message", message or "", 1
        )
        # get new states after command
        await asyncio.sleep(10)
        await self.refresh_readings()

    async def update_readings(self):
        if self.vin is None:
            return
        failed = 0
        for domain, function in volvo.STATUS_ENDPOINTS.items():
            data = await self._get(function)
            if data is None:
                failed += 1
            else:
                await self.update_values(domain, data)
        if self.isECar:
            data = await self._get("async_get_energy_state")
            if data is None:
                failed += 1
            else:
                await self.update_values("energy", data)
        if self._location_available:
            await self.update_location()

        state = "connected" if failed == 0 else "failed to read some data"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    async def _get(self, function):
        try:
            data = await getattr(self.api, function)()
            self._errors.success(key=function)
            return data
        except VolvoLoginRequired:
            raise
        except Exception as ex:
            if isinstance(ex, VolvoAuthException):
                # get a new access token with the next request
                self.auth.invalidate_access_token()
            self._errors.failed(f"Failed to get data ({function}): {ex}", key=function)
            return None

    async def update_location(self):
        try:
            data = await self.api.async_get_location()
        except VolvoLoginRequired:
            raise
        except VolvoAuthException:
            # location isn't granted for every account
            self.logger.debug("Location not available")
            self._location_available = False
            return
        except Exception as ex:
            self.logger.debug(f"Failed to get location: {ex}")
            return
        location = data.get("location")
        if location is None or location.geometry is None:
            return
        values = {}
        coords = location.geometry.coordinates
        if len(coords) >= 2:
            values["location_longitude"] = coords[0]
            values["location_latitude"] = coords[1]
        if location.properties:
            values["location_heading"] = location.properties.heading
            values["location_timestamp"] = self._format_ts(
                location.properties.timestamp
            )
        await self._bulk_update(values)

    @staticmethod
    def _format_ts(timestamp):
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        return timestamp

    async def update_values(self, domain, data):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for key, field in data.items():
                if field is None:
                    continue
                # energy state: status ERROR means no value available
                if getattr(field, "status", None) == "ERROR":
                    continue
                if field.value is None:
                    continue
                name = f"{domain}_{key}"
                await fhem.readingsBulkUpdateIfChanged(self.hash, name, field.value)
                if field.timestamp is not None:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, name + "_timestamp", self._format_ts(field.timestamp)
                    )
                if field.unit:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, name + "_unit", field.unit
                    )
        except Exception:
            self.logger.exception(f"Failed to update readings for {domain}")
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)
