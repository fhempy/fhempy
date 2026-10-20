"""BMW CarData: official BMW/MINI customer API (EU, since 2025).

Login is the OAuth device code flow with the personal client ID of the
user, data comes from the REST API (max. 50 requests per day) and from the
CarData MQTT stream (live, no limit).
"""

import base64
import datetime
import hashlib
import json
import secrets
import time

import aiohttp

AUTH_URL = "https://customer.bmwgroup.com/gcdm/oauth"
API_URL = "https://api-cardata.bmwgroup.com"
STREAM_HOST = "customer.streaming-cardata.bmwgroup.com"
STREAM_PORT = 9000
SCOPE = "authenticate_user openid cardata:api:read cardata:streaming:read"
REQUEST_TIMEOUT = 30
CONTAINER_NAME = "fhempy"
CONTAINER_PURPOSE = "FHEM"

# descriptor -> reading name, the most important values get short names
READINGS = {
    "vehicle.drivetrain.batteryManagement.header": "soc",
    "vehicle.powertrain.electric.battery.stateOfCharge.target": "soc_target",
    "vehicle.drivetrain.electricEngine.kombiRemainingElectricRange": "range",
    "vehicle.drivetrain.electricEngine.remainingElectricRange": "range_estimate",
    "vehicle.vehicle.travelledDistance": "mileage",
    "vehicle.drivetrain.electricEngine.charging.status": "charging_status",
    "vehicle.drivetrain.electricEngine.charging.hvStatus": "charging_hv_status",
    "vehicle.drivetrain.electricEngine.charging.timeRemaining": (
        "charging_time_remaining"
    ),
    "vehicle.drivetrain.electricEngine.charging.level": "charging_level",
    "vehicle.drivetrain.electricEngine.charging.method": "charging_method",
    "vehicle.powertrain.electric.battery.charging.power": "charging_power",
    "vehicle.powertrain.electric.battery.charging.acLimit.selected": (
        "charging_ac_limit"
    ),
    "vehicle.powertrain.tractionBattery.charging.port.anyPosition.isPlugged": (
        "plugged"
    ),
    "vehicle.body.chargingPort.status": "charging_port",
    "vehicle.body.chargingPort.lockedStatus": "charging_cable_lock",
    "vehicle.powertrain.electric.battery.stateOfHealth.displayed": ("battery_health"),
    "vehicle.drivetrain.batteryManagement.maxEnergy": "battery_max_energy",
    "vehicle.electricalSystem.battery.stateOfCharge": "battery_12v",
    # lock is only sent on request, doors also by the stream
    "vehicle.cabin.door.lock.status": "lock",
    "vehicle.cabin.door.status": "doors",
    "vehicle.cabin.door.row1.driver.isOpen": "door_front_driver",
    "vehicle.cabin.door.row1.passenger.isOpen": "door_front_passenger",
    "vehicle.cabin.door.row2.driver.isOpen": "door_rear_driver",
    "vehicle.cabin.door.row2.passenger.isOpen": "door_rear_passenger",
    "vehicle.cabin.window.row1.driver.status": "window_front_driver",
    "vehicle.cabin.window.row1.passenger.status": "window_front_passenger",
    "vehicle.cabin.window.row2.driver.status": "window_rear_driver",
    "vehicle.cabin.window.row2.passenger.status": "window_rear_passenger",
    "vehicle.cabin.sunroof.status": "sunroof",
    "vehicle.body.trunk.isOpen": "trunk",
    "vehicle.body.trunk.isLocked": "trunk_lock",
    "vehicle.body.hood.isOpen": "hood",
    "vehicle.cabin.infotainment.navigation.currentLocation.latitude": "latitude",
    "vehicle.cabin.infotainment.navigation.currentLocation.longitude": "longitude",
    "vehicle.cabin.infotainment.navigation.currentLocation.heading": "heading",
    "vehicle.isMoving": "moving",
    "vehicle.vehicle.preConditioning.activity": "climate",
    "vehicle.vehicle.preConditioning.remainingTime": "climate_time_remaining",
    "vehicle.chassis.axle.row1.wheel.left.tire.pressure": "tire_front_left",
    "vehicle.chassis.axle.row1.wheel.right.tire.pressure": "tire_front_right",
    "vehicle.chassis.axle.row2.wheel.left.tire.pressure": "tire_rear_left",
    "vehicle.chassis.axle.row2.wheel.right.tire.pressure": "tire_rear_right",
    "vehicle.status.serviceDistance.next": "service_distance",
    "vehicle.status.serviceTime.inspectionDateLegal": "inspection_date",
    "vehicle.status.checkControlMessages": "check_control_messages",
}

# fallback if BMW rejects the full list, all of these are known to work
BASIC_DESCRIPTORS = [
    "vehicle.drivetrain.batteryManagement.header",
    "vehicle.powertrain.electric.battery.stateOfCharge.target",
    "vehicle.drivetrain.electricEngine.remainingElectricRange",
    "vehicle.drivetrain.electricEngine.charging.status",
    "vehicle.drivetrain.electricEngine.charging.hvStatus",
    "vehicle.drivetrain.electricEngine.charging.timeRemaining",
    "vehicle.drivetrain.electricEngine.charging.level",
    "vehicle.drivetrain.electricEngine.charging.method",
    "vehicle.powertrain.electric.battery.charging.power",
    "vehicle.powertrain.electric.battery.charging.acLimit.selected",
    "vehicle.powertrain.tractionBattery.charging.port.anyPosition.isPlugged",
    "vehicle.body.chargingPort.lockedStatus",
    "vehicle.powertrain.electric.battery.stateOfHealth.displayed",
    "vehicle.drivetrain.batteryManagement.maxEnergy",
]

OPEN_CLOSED = ("door_", "trunk", "hood")
YES_NO = ("plugged", "moving")
LOCKED = ("trunk_lock",)


class CarDataError(Exception):
    def __init__(self, message, status=None, error=None):
        super().__init__(message)
        self.status = status
        self.error = error


class LoginRequired(CarDataError):
    """The refresh token is invalid, the user has to log in again."""


def new_pkce():
    verifier = secrets.token_urlsafe(64)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    return verifier, challenge


def reading_name(descriptor):
    if descriptor in READINGS:
        return READINGS[descriptor]
    name = descriptor.removeprefix("vehicle.")
    return "".join(c if c.isalnum() else "_" for c in name)


def reading_value(name, value):
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    text = str(value)
    lower = text.lower()
    if lower in ("true", "false"):
        is_true = lower == "true"
        if name.startswith(OPEN_CLOSED):
            return "open" if is_true else "closed"
        if name in YES_NO:
            return "yes" if is_true else "no"
        if name in LOCKED:
            return "locked" if is_true else "unlocked"
        return "1" if is_true else "0"
    return text


def readings_from_data(data):
    """Convert {descriptor: {value, unit, timestamp}} to readings.

    Returns (readings, newest timestamp), values without value are skipped.
    """
    readings = {}
    newest = None
    for descriptor, entry in (data or {}).items():
        if not isinstance(entry, dict):
            continue
        name = reading_name(descriptor)
        value = reading_value(name, entry.get("value"))
        if value is None or value == "":
            continue
        readings[name] = value
        timestamp = parse_time(entry.get("timestamp"))
        if timestamp and (newest is None or timestamp > newest):
            newest = timestamp
    return readings, newest


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


class CarDataApi:
    def __init__(self, client_id, auth_url=None, api_url=None):
        self.client_id = client_id
        self.auth_url = auth_url or AUTH_URL
        self.api_url = api_url or API_URL
        self.access_token = ""
        self.id_token = ""
        self.refresh_token = ""
        self.gcid = ""
        self.expires_at = 0
        self.on_request = None

    async def _post_auth(self, path, data):
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{self.auth_url}/{path}", data=data) as resp:
                try:
                    body = await resp.json(content_type=None)
                except ValueError:
                    body = {}
                if not isinstance(body, dict):
                    body = {}
                if resp.status != 200:
                    error = body.get("error", "")
                    text = body.get("error_description") or error or resp.reason
                    raise CarDataError(
                        f"BMW login failed ({resp.status}): {text}",
                        resp.status,
                        error,
                    )
                return body

    async def request_device_code(self, challenge):
        return await self._post_auth(
            "device/code",
            {
                "client_id": self.client_id,
                "response_type": "device_code",
                "scope": SCOPE,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            },
        )

    async def poll_token(self, device_code, verifier):
        """Returns True when logged in, False while the user hasn't confirmed."""
        try:
            tokens = await self._post_auth(
                "token",
                {
                    "client_id": self.client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "code_verifier": verifier,
                },
            )
        except CarDataError as exc:
            if exc.error in ("authorization_pending", "slow_down"):
                return False
            raise
        self._store_tokens(tokens)
        return True

    async def refresh(self, now):
        if not self.refresh_token:
            raise LoginRequired("Not logged in")
        try:
            tokens = await self._post_auth(
                "token",
                {
                    "client_id": self.client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
            )
        except CarDataError as exc:
            if exc.error in ("invalid_grant", "invalid_client", "unauthorized_client"):
                raise LoginRequired(str(exc), exc.status, exc.error) from exc
            raise
        self._store_tokens(tokens, now)

    def _store_tokens(self, tokens, now=None):
        now = time.time() if now is None else now
        self.access_token = tokens.get("access_token", "")
        self.id_token = tokens.get("id_token", "")
        self.refresh_token = tokens.get("refresh_token") or self.refresh_token
        self.gcid = tokens.get("gcid") or self.gcid
        self.expires_at = now + int(tokens.get("expires_in") or 3600)

    async def request(self, method, path, params=None, json_body=None):
        if self.on_request:
            self.on_request()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-version": "v1",
            "Accept": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method,
                f"{self.api_url}{path}",
                headers=headers,
                params=params,
                json=json_body,
            ) as resp:
                text = await resp.text()
                if resp.status >= 300:
                    raise CarDataError(
                        f"BMW CarData {path} failed ({resp.status}): {text[:300]}",
                        resp.status,
                    )
                if not text:
                    return {}
                return json.loads(text)

    async def vehicles(self):
        mappings = await self.request("GET", "/customers/vehicles/mappings")
        if isinstance(mappings, dict):
            mappings = mappings.get("mappings") or [mappings]
        return [
            m["vin"]
            for m in mappings
            if isinstance(m, dict)
            and m.get("vin")
            and m.get("mappingType", "PRIMARY") == "PRIMARY"
        ] or [m["vin"] for m in mappings if isinstance(m, dict) and m.get("vin")]

    async def basic_data(self, vin):
        return await self.request("GET", f"/customers/vehicles/{vin}/basicData")

    async def find_container(self):
        result = await self.request("GET", "/customers/containers")
        if isinstance(result, dict):
            result = result.get("containers") or []
        for container in result:
            if (
                isinstance(container, dict)
                and container.get("name") == CONTAINER_NAME
                and container.get("state", "ACTIVE") == "ACTIVE"
            ):
                return container.get("containerId", "")
        return ""

    async def create_container(self, descriptors):
        result = await self.request(
            "POST",
            "/customers/containers",
            json_body={
                "name": CONTAINER_NAME,
                "purpose": CONTAINER_PURPOSE,
                "technicalDescriptors": list(descriptors),
            },
        )
        container_id = result.get("containerId") if isinstance(result, dict) else ""
        if not container_id:
            raise CarDataError(f"BMW didn't return a container: {result}")
        return container_id

    async def telematic_data(self, vin, container_id):
        result = await self.request(
            "GET",
            f"/customers/vehicles/{vin}/telematicData",
            params={"containerId": container_id},
        )
        return result.get("telematicData") or result.get("data") or {}
