"""fhempy module for the official MyŠkoda Public API.

Reads every documented data area of the car and provides the returned JSON
fields as readings. Remote commands follow the API v1.1.

Based on the module by forum user Wolle02.
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from urllib.parse import quote

import aiohttp

from .. import fhem, generic

API_BASE = "https://public.api.connect.skoda-auto.cz"
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=35)
MIN_INTERVAL = 300
DEFAULT_INTERVAL = 1800
# wait after HTTP 429 without Retry-After header
RATE_LIMIT_BACKOFF = 900
VEHICLE_PARTS = (
    "info",
    "status",
    "fuelStatus",
    "odometer",
    "parkingPosition",
    "airConditioning",
    "auxiliaryHeating",
    "activeVentilation",
    "charging",
    "chargingProfiles",
)
CHARGE_MODES = (
    "MANUAL",
    "TIMER",
    "TIMER_CHARGING_WITH_CLIMATISATION",
    "PREFERRED_CHARGING_TIMES",
    "ONLY_OWN_CURRENT",
    "IMMEDIATE_DISCHARGING",
    "HOME_STORAGE_CHARGING",
)
HEADER_READINGS = {
    "apiKeyExpiresAt": "x-api-key-expires-at",
    "rateLimitRemaining": "ratelimit-remaining",
    "rateLimitLimit": "ratelimit-limit",
    "rateLimitReset": "ratelimit-reset",
}

# commands without parameters: set name -> (HTTP method, path)
SIMPLE_COMMANDS = {
    "stop_air_conditioning": ("POST", "/air-conditioning/stop"),
    "stop_auxiliary_heating": ("POST", "/auxiliary-heating/stop"),
    "start_active_ventilation": ("POST", "/active-ventilation/start"),
    "stop_active_ventilation": ("POST", "/active-ventilation/stop"),
    "start_charging": ("POST", "/charging/start"),
    "stop_charging": ("POST", "/charging/stop"),
}

UPDATE_COMMAND = {"update": {"help": "Update all readings now."}}

# set commands per feature, hidden when the API reports one of the errors
COMMAND_GROUPS = (
    (
        ("AIR_CONDITIONING_UNSUPPORTED",),
        {
            "start_air_conditioning": {
                "help": "Start air conditioning with the attributes "
                "target_temperature and ac_without_external_power."
            },
            "stop_air_conditioning": {"help": "Stop air conditioning."},
        },
    ),
    (
        ("AUXILIARY_HEATING_UNSUPPORTED",),
        {
            "start_auxiliary_heating": {
                "help": "Start auxiliary heating, needs the S-PIN."
            },
            "stop_auxiliary_heating": {"help": "Stop auxiliary heating."},
        },
    ),
    (
        ("ACTIVE_VENTILATION_UNSUPPORTED",),
        {
            "start_active_ventilation": {"help": "Start active ventilation."},
            "stop_active_ventilation": {"help": "Stop active ventilation."},
        },
    ),
    (
        ("CHARGING_UNSUPPORTED",),
        {
            "start_charging": {"help": "Start charging."},
            "stop_charging": {"help": "Stop charging."},
            "charge_limit": {
                "args": ["percent"],
                "params": {"percent": {"format": "int"}},
                "options": "slider,50,10,100",
                "help": "Set the target state of charge in percent.",
            },
            "charge_mode": {
                "args": ["mode"],
                "options": ",".join(CHARGE_MODES),
                "help": "Set the charge mode.",
            },
        },
    ),
    (
        ("CHARGING_UNSUPPORTED", "CHARGING_PROFILES_UNSUPPORTED"),
        {
            "update_charging_profile": {
                "args": ["profile_id"],
                "params": {"profile_id": {"format": "int"}},
                "help": "Replace a charging profile with the JSON of the "
                "attribute charging_profile_json.",
            },
        },
    ),
)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _reading_name(path):
    """Stable reading name for a JSON path."""
    name = re.sub(r"[^A-Za-z0-9_]+", "_", path).strip("_") or "api_value"
    if name[0].isdigit():
        name = "api_" + name
    return name[:240]


def _to_str(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _flatten_json(value, path="api"):
    """Flattens nested JSON, lists are kept as JSON as well."""
    result = {}
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(_flatten_json(child, f"{path}_{key}"))
    elif isinstance(value, list):
        result[path] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        for index, child in enumerate(value):
            result.update(_flatten_json(child, f"{path}_{index}"))
    elif value is not None:
        result[path] = _to_str(value)
    return result


def _error_types(errors):
    if not isinstance(errors, list):
        return set()
    return {str(item.get("type", "")) for item in errors if isinstance(item, dict)}


def _error_text(errors):
    if not isinstance(errors, list):
        return str(errors or "")
    return "; ".join(
        str(item.get("type", item.get("detail", item)))
        if isinstance(item, dict)
        else str(item)
        for item in errors
    )


def _error_detail(body, body_text, status):
    for key in ("detail", "title", "message", "responseText"):
        if body.get(key):
            return str(body[key])
    return body_text or f"HTTP {status}"


def _parse_retry_after(value):
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return 0


def _summary(data):
    """Short readings for frequently used values."""
    vehicle = data.get("vehicle") or {}
    fuel = vehicle.get("fuelStatus") or {}
    engine_range = fuel.get("primaryEngineRange") or {}
    odometer = vehicle.get("odometer") or {}
    parking = vehicle.get("parkingPosition") or {}
    coords = parking.get("gpsCoordinates") or {}
    status = vehicle.get("status") or {}
    overall = status.get("overall") or {}
    detail = status.get("detail") or {}
    return {
        "vehicleName": vehicle.get("name"),
        "mileage": odometer.get("mileageInKm"),
        "fuelLevel": engine_range.get(
            "currentFuelLevelInPercent", engine_range.get("currentSoCInPercent")
        ),
        "range": engine_range.get("remainingRangeInKm"),
        "totalRange": fuel.get("totalRangeInKm"),
        "fuelCapturedAt": fuel.get("carCapturedTimestamp"),
        "odometerCapturedAt": odometer.get("carCapturedTimestamp"),
        "parkingState": parking.get("state"),
        "parkingAddress": parking.get("formattedAddress"),
        "latitude": coords.get("latitude"),
        "longitude": coords.get("longitude"),
        "doorsLocked": overall.get("doorsLocked"),
        "locked": overall.get("locked"),
        "doors": overall.get("doors"),
        "windows": overall.get("windows"),
        "lights": overall.get("lights"),
        "reliableLockStatus": overall.get("reliableLockStatus"),
        "trunk": detail.get("trunk"),
        "bonnet": detail.get("bonnet"),
        "sunroof": detail.get("sunroof"),
        "vehicleStatusCapturedAt": status.get("carCapturedTimestamp"),
    }


class ApiRequestError(Exception):
    def __init__(self, status, detail, body=None):
        super().__init__(detail)
        self.status = status
        self.detail = detail
        self.body = body or {}


class skoda_api(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.session = None
        self._poll_task = None
        self._retry_after = 0
        self._setter_names = None
        self._api_key = ""
        self._vin = ""
        self._spin = ""

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) > 6:
            return "Usage: define my_skoda fhempy skoda_api API_KEY VIN [S-PIN]"

        await self.set_attr_config(
            {
                "api_key": {
                    "default": "",
                    "help": "MyŠkoda Public API key, only needed if it is not "
                    "part of the define.",
                },
                "vin": {
                    "default": "",
                    "help": "VIN of the car, only needed if it is not part of "
                    "the define.",
                },
                "spin": {
                    "default": "",
                    "help": "S-PIN for the auxiliary heating, only needed if "
                    "it is not part of the define.",
                },
                "update_interval": {
                    "default": DEFAULT_INTERVAL,
                    "format": "int",
                    "help": f"Update interval in seconds, minimum {MIN_INTERVAL}.",
                },
                "target_temperature": {
                    "default": 21,
                    "format": "float",
                    "help": "Target temperature in °C for air conditioning "
                    "and auxiliary heating.",
                },
                "ac_without_external_power": {
                    "default": 1,
                    "format": "int",
                    "options": "0,1",
                    "help": "Allow air conditioning without external power.",
                },
                "auxiliary_heating_duration": {
                    "default": 120,
                    "format": "int",
                    "help": "Duration of the auxiliary heating in seconds.",
                },
                "auxiliary_heating_mode": {
                    "default": "HEATING",
                    "options": "HEATING,VENTILATION",
                    "help": "Mode of the auxiliary heating.",
                },
                "charging_profile_json": {
                    "default": "",
                    "help": "Complete JSON of a charging profile, used by "
                    "update_charging_profile.",
                },
            }
        )
        await self.set_icon("car")

        extra = list(args[3:]) + ["", "", ""]
        self._api_key, self._vin, self._spin = extra[0], extra[1].upper(), extra[2]

        self._setter_names = None
        await self._configure_setters(None)
        self.session = aiohttp.ClientSession(timeout=REQUEST_TIMEOUT)
        self._restart_polling()

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await super().Undefine(hash)
        self._poll_task = None
        if self.session:
            await self.session.close()
            self.session = None

    @property
    def api_key(self):
        return self._api_key or self._attr_api_key

    @property
    def vin(self):
        return (self._vin or self._attr_vin).upper()

    @property
    def spin(self):
        return self._spin or self._attr_spin

    @property
    def interval(self):
        return max(MIN_INTERVAL, self._attr_update_interval)

    # attribute hooks, a new key, VIN or interval applies immediately
    def set_attr_api_key(self, hash):
        self._restart_polling()

    def set_attr_vin(self, hash):
        self._restart_polling()

    def set_attr_update_interval(self, hash):
        self._restart_polling()

    def _restart_polling(self):
        if self._poll_task:
            self.cancel_async_task(self._poll_task)
        self._poll_task = self.create_async_task(self._poll_loop())

    async def _poll_loop(self):
        if not self.api_key or not self.vin:
            await fhem.readingsSingleUpdate(
                self.hash, "state", "API key or VIN missing", 1
            )
            return
        # several attribute changes in a row (e.g. FHEM start) poll only once
        await asyncio.sleep(1)
        while True:
            try:
                await self.fetch_once()
            except Exception:
                self.logger.exception("Failed to update MyŠkoda data")
            delay = max(self.interval, self._retry_after)
            self._retry_after = 0
            await asyncio.sleep(delay)

    def set_update(self, hash, params):
        if not self.api_key or not self.vin:
            return "API key or VIN missing."
        self._restart_polling()
        return ""

    async def _request(self, method, path, payload=None, params=None):
        url = f"{API_BASE}/api/v1/vehicles/{quote(self.vin, safe='')}{path}"
        headers = {"X-API-Key": self.api_key, "Accept": "application/json"}
        async with self.session.request(
            method, url, headers=headers, json=payload, params=params
        ) as response:
            body_text = await response.text()
            status = response.status
            response_headers = {k.lower(): v for k, v in response.headers.items()}
        try:
            body = json.loads(body_text) if body_text else {}
        except json.JSONDecodeError:
            body = {"responseText": body_text[:2000]}
        if not isinstance(body, dict):
            body = {"data": body}
        await self._update_header_readings(response_headers)
        if status not in (200, 202, 204):
            retry_after = _parse_retry_after(response_headers.get("retry-after"))
            if status == 429:
                retry_after = retry_after or RATE_LIMIT_BACKOFF
            self._retry_after = max(self._retry_after, retry_after)
            raise ApiRequestError(status, _error_detail(body, body_text, status), body)
        return body, status

    async def _update_header_readings(self, headers):
        for reading, header in HEADER_READINGS.items():
            if headers.get(header) is not None:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, reading, str(headers[header]), 1
                )

    async def fetch_once(self):
        await fhem.readingsSingleUpdate(self.hash, "lastApiAttempt", _now(), 1)
        try:
            data, _ = await self._request(
                "GET", "", params={"include": ",".join(VEHICLE_PARTS)}
            )
        except ApiRequestError as exc:
            self.logger.warning("MyŠkoda API error HTTP %s: %s", exc.status, exc.detail)
            await self._set_error(f"HTTP {exc.status}: {exc.detail}", "API error")
            return
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            self.logger.warning("MyŠkoda API not reachable: %r", exc)
            await self._set_error(repr(exc)[:500], "connection error")
            return

        errors = data.get("errors", [])
        await self._configure_setters(errors)

        values = _flatten_json(data)
        values["api_rawJson"] = json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        )
        values["apiErrors"] = _error_text(errors)
        values["lastApiUpdate"] = _now()
        values["lastApiError"] = ""
        for name, value in _summary(data).items():
            if value is not None:
                values[name] = _to_str(value)
        values["state"] = "connected"

        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name, value in values.items():
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, _reading_name(name), value
                )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def _set_error(self, message, state):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdate(self.hash, "lastApiError", message)
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def _configure_setters(self, errors):
        """Offer only commands the API doesn't report as unsupported.

        Before the first answer of the API only update is available."""
        commands = dict(UPDATE_COMMAND)
        if errors is not None:
            unsupported = _error_types(errors)
            for error_names, group in COMMAND_GROUPS:
                if not unsupported.intersection(error_names):
                    commands.update(group)
        for name, config in commands.items():
            if name in SIMPLE_COMMANDS:
                config["function"] = "set_simple_command"
        names = set(commands)
        if names != self._setter_names:
            self._setter_names = names
            await self.set_set_config(commands)

    async def _command(self, method, path, payload=None):
        values = {"lastCommand": f"{method} {path}", "lastCommandAt": _now()}
        try:
            _, status = await self._request(method, path, payload=payload)
            values["lastCommandStatus"] = str(status)
            values["lastCommandError"] = ""
            ret = ""
        except ApiRequestError as exc:
            ret = f"HTTP {exc.status}: {exc.detail}"
            values["lastCommandStatus"] = str(exc.status)
            values["lastCommandError"] = ret
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            ret = f"MyŠkoda API not reachable: {exc!r}"
            values["lastCommandStatus"] = "error"
            values["lastCommandError"] = ret
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name, value in values.items():
                await fhem.readingsBulkUpdate(self.hash, name, value)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)
        return ret

    async def set_simple_command(self, hash, params):
        method, path = SIMPLE_COMMANDS[params["cmd"]]
        return await self._command(method, path, {})

    async def set_start_air_conditioning(self, hash, params):
        return await self._command(
            "POST",
            "/air-conditioning/start",
            {
                "targetTemperature": {
                    "value": self._attr_target_temperature,
                    "unit": "CELSIUS",
                },
                "airConditioningWithoutExternalPower": bool(
                    self._attr_ac_without_external_power
                ),
            },
        )

    async def set_start_auxiliary_heating(self, hash, params):
        if not self.spin:
            return "S-PIN missing, add it to the define or set attribute spin."
        mode = str(self._attr_auxiliary_heating_mode).upper()
        if mode not in ("HEATING", "VENTILATION"):
            return "auxiliary_heating_mode must be HEATING or VENTILATION."
        payload = {
            "spin": self.spin,
            "durationInSeconds": self._attr_auxiliary_heating_duration,
            "startMode": mode,
            "targetTemperature": {
                "value": self._attr_target_temperature,
                "unit": "CELSIUS",
            },
        }
        return await self._command("POST", "/auxiliary-heating/start", payload)

    async def set_charge_limit(self, hash, params):
        percent = params["percent"]
        if not 1 <= percent <= 100:
            return "percent must be between 1 and 100."
        return await self._command(
            "PUT", "/charging/limit", {"targetStateOfChargeInPercent": percent}
        )

    async def set_charge_mode(self, hash, params):
        mode = str(params["mode"]).upper()
        if mode not in CHARGE_MODES:
            return "Unsupported mode, choose one of " + ", ".join(CHARGE_MODES)
        return await self._command("PUT", "/charging/mode", {"chargeMode": mode})

    async def set_update_charging_profile(self, hash, params):
        profile_id = params["profile_id"]
        raw = str(self._attr_charging_profile_json or "").strip()
        if not raw:
            return "Set attribute charging_profile_json to the complete profile first."
        try:
            profile = json.loads(raw)
        except json.JSONDecodeError as exc:
            return f"charging_profile_json is no valid JSON: {exc}"
        if not isinstance(profile, dict):
            return "charging_profile_json must be a JSON object."
        if str(profile.get("id")) != str(profile_id):
            return "profile_id must match the field id of charging_profile_json."
        return await self._command("PUT", f"/charging-profiles/{profile_id}", profile)
