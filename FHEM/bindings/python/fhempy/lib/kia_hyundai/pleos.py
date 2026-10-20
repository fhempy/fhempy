"""Pleos Vehicle Data API: official Hyundai/Kia/Genesis data API (EU Data Act).

The user creates a personal API key (client ID and client secret) in the
Pleos Playground under "My Vehicle Data API". The API is read-only and
returns the values the car last sent to the manufacturer, it never wakes
up the car.
"""

import time

import aiohttp

API_URL = "https://api.pleos.ai/v1"
BRANDS = ("kia", "hyundai", "genesis")
REQUEST_TIMEOUT = 30
# Pleos access tokens are valid for one hour
TOKEN_EXPIRY = 3600
# renew the token this many seconds before it expires
RENEW_BEFORE = 120
# endpoint -> reading prefix
ENDPOINTS = {
    "batteries": "battery",
    "powertrains": "powertrain",
    "driving": "driving",
    "locations": "location",
    "status": "status",
}


class ApiError(Exception):
    def __init__(self, status, code="", message=""):
        self.status = status
        self.code = str(code or "")
        super().__init__(f"HTTP {status} {self.code} {message}".strip())


class LoginFailed(Exception):
    pass


class RateLimited(ApiError):
    pass


class NoData(Exception):
    pass


class PleosApi:
    def __init__(self, client_id="", client_secret="", brand=""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.brand = brand
        self._token = ""
        self._token_expires = 0

    async def _request(self, method, path, brand, token="", body=None):
        headers = {"Accept": "application/json", "Brand": brand}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method, API_URL + path, headers=headers, json=body
            ) as resp:
                try:
                    data = await resp.json(content_type=None)
                except ValueError:
                    data = None
                if not isinstance(data, dict):
                    data = {}
                if resp.status >= 400:
                    error = data.get("error")
                    if not isinstance(error, dict):
                        error = data
                    code = error.get("code", "")
                    message = error.get("message", "")
                    if resp.status == 429:
                        raise RateLimited(resp.status, code, message)
                    raise ApiError(resp.status, code, message)
                return data.get("data", data)

    async def _get_token(self, brand):
        data = await self._request(
            "POST",
            "/auth/personal-token",
            brand,
            body={"clientId": self.client_id, "clientSecret": self.client_secret},
        )
        token = data.get("accessToken") if isinstance(data, dict) else None
        if not token:
            raise LoginFailed("Pleos sent no access token")
        self._token = token
        self._token_expires = time.time() + int(data.get("expiresIn") or TOKEN_EXPIRY)

    async def login(self):
        """Get an access token, find out the brand if it is unknown."""
        if not self.client_id or not self.client_secret:
            raise LoginFailed("client ID and client secret missing")
        errors = []
        for brand in [self.brand] if self.brand else BRANDS:
            try:
                await self._get_token(brand)
                self.brand = brand
                return
            except RateLimited:
                raise
            except ApiError as exc:
                if exc.status >= 500:
                    raise
                errors.append(f"{brand}: {exc}")
        raise LoginFailed(
            "client ID or client secret not accepted (" + ", ".join(errors) + ")"
        )

    def logout(self):
        self._token = ""
        self._token_expires = 0

    async def get(self, path):
        if not self._token or time.time() > self._token_expires - RENEW_BEFORE:
            await self.login()
        try:
            return await self._request("GET", path, self.brand, self._token)
        except ApiError as exc:
            if exc.status != 401:
                raise
        # token revoked or expired early
        await self.login()
        return await self._request("GET", path, self.brand, self._token)

    async def vehicles(self):
        data = await self.get("/vehicles/consent")
        vehicles = data.get("vehicles", []) if isinstance(data, dict) else data
        return [v for v in vehicles or [] if isinstance(v, dict) and v.get("vin")]

    async def vehicle_data(self, vin):
        """Values of all endpoints, endpoints without data are left out."""
        result = {}
        for endpoint in ENDPOINTS:
            try:
                result[endpoint] = await self.get(f"/vehicles/{vin}/{endpoint}")
            except RateLimited:
                raise
            except ApiError as exc:
                # no data (e.g. code 4045) or not available for this car
                if exc.status >= 500 or exc.status == 401:
                    raise
        if not result:
            raise NoData("the car sent no values to the server yet")
        return result
