"""Contains the Async Smartmeter API Client.

Login flow and endpoints follow
https://github.com/DarwinsBuddy/WienerNetzeSmartmeter (api/client.py).
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from urllib import parse

import aiohttp
from lxml import html

from . import constants as const
from .errors import (
    SmartmeterConnectionError,
    SmartmeterLoginError,
    SmartmeterQueryError,
)

logger = logging.getLogger(__name__)

TIMEOUT = 20
# renew the access token a bit before it really expires
TOKEN_EXPIRY_MARGIN = timedelta(seconds=30)


def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")


def generate_code_challenge(code_verifier):
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def _form_action(text):
    try:
        forms = html.fromstring(text).xpath("(//form/@action)")
    except Exception:
        forms = []
    return forms[0] if forms else None


def _code_from_location(location):
    parsed = parse.urlparse(location)
    # response_mode=fragment returns the code in the fragment
    for part in (parsed.fragment, parsed.query):
        params = parse.parse_qs(part)
        if "code" in params:
            return params["code"][0]
    return None


class AsyncSmartmeter:
    """Async Smartmeter Client."""

    def __init__(self, username, password, session=None, timeout=TIMEOUT):
        """Access the Smart Meter API asynchronously.

        Args:
            username (str): Username used for API Login
            password (str): Password used for API Login
            session (aiohttp.ClientSession): An optional session object
            timeout (int): Timeout for all session calls. Defaults to TIMEOUT.
        """
        self._username = username
        self._password = password
        self._session = session or aiohttp.ClientSession()
        self._timeout = timeout
        self._access_token = None
        self._refresh_token = None
        self._access_token_expiration = None
        self._api_gateway_token = None
        self._api_gateway_b2b_token = None
        self.api_url = const.API_URL
        self.api_url_b2b = const.API_URL_B2B
        self._login_lock = asyncio.Lock()

    def is_logged_in(self):
        return (
            self._access_token is not None
            and self._access_token_expiration is not None
            and datetime.now() < self._access_token_expiration
        )

    async def _get(self, url, **kwargs):
        async with asyncio.timeout(self._timeout):
            async with self._session.get(url, **kwargs) as response:
                return response.status, dict(response.headers), await response.text()

    async def _post(self, url, **kwargs):
        async with asyncio.timeout(self._timeout):
            async with self._session.post(url, **kwargs) as response:
                return response.status, dict(response.headers), await response.text()

    async def _load_login_page(self, code_challenge):
        login_args = dict(const.LOGIN_ARGS, code_challenge=code_challenge)
        login_url = const.AUTH_URL + "auth?" + parse.urlencode(login_args)
        try:
            status, _, text = await self._get(login_url)
        except Exception as exception:
            raise SmartmeterConnectionError("Could not load login page") from exception
        if status != 200:
            raise SmartmeterConnectionError(
                f"Could not load login page (HTTP {status})"
            )
        action = _form_action(text)
        if action is None:
            raise SmartmeterConnectionError("No form found on the login page")
        return action

    async def _credentials_login(self, action):
        """log.wien asks for the username first and for the password on a
        second page."""
        try:
            status, headers, text = await self._post(
                action,
                data={"username": self._username, "login": " "},
                allow_redirects=False,
            )
            password_action = _form_action(text)
            if password_action is None:
                raise SmartmeterLoginError(
                    "Login failed, no password form after username "
                    f"(HTTP {status}). Check username."
                )
            status, headers, text = await self._post(
                password_action,
                data={"username": self._username, "password": self._password},
                allow_redirects=False,
            )
        except SmartmeterLoginError:
            raise
        except Exception as exception:
            raise SmartmeterConnectionError(
                "Could not login with credentials"
            ) from exception

        location = headers.get("Location")
        if location is None:
            raise SmartmeterLoginError("Login failed. Check username/password.")
        code = _code_from_location(location)
        if code is None:
            raise SmartmeterLoginError(
                "Login failed. Could not extract 'code' from 'Location'"
            )
        return code

    async def _load_tokens(self, code, code_verifier):
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.post(
                    const.AUTH_URL + "token",
                    data=const.build_access_token_args(
                        code=code, code_verifier=code_verifier
                    ),
                ) as response:
                    status = response.status
                    if status == 200:
                        tokens = await response.json(content_type=None)
        except Exception as exception:
            raise SmartmeterConnectionError(
                "Could not obtain access token"
            ) from exception
        if status != 200:
            raise SmartmeterLoginError(f"Could not obtain access token (HTTP {status})")
        if tokens.get("token_type", "Bearer").lower() != "bearer":
            raise SmartmeterLoginError(
                f"Bearer token required, but got {tokens['token_type']!r}"
            )
        return tokens

    async def _load_api_keys(self):
        """API keys and URLs are published in the app-config.json of the
        smartmeter web portal."""
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.get(
                    const.API_CONFIG_URL,
                    headers={"Authorization": f"Bearer {self._access_token}"},
                ) as response:
                    config = await response.json(content_type=None)
        except Exception as exception:
            raise SmartmeterConnectionError("Could not obtain API key") from exception
        if not isinstance(config, dict):
            raise SmartmeterConnectionError("Unexpected app-config.json format")
        for key in ("b2cApiKey", "b2bApiKey"):
            if key not in config:
                raise SmartmeterConnectionError(f"{key} not found in app-config.json")
        self._api_gateway_token = config["b2cApiKey"]
        self._api_gateway_b2b_token = config["b2bApiKey"]
        self.api_url = config.get("b2cApiUrl") or const.API_URL
        self.api_url_b2b = config.get("b2bApiUrl") or const.API_URL_B2B

    async def login(self, force=False):
        """Login with username/password if there is no valid access token."""
        async with self._login_lock:
            if self.is_logged_in() and not force:
                return
            self._access_token = None
            self._session.cookie_jar.clear()
            code_verifier = generate_code_verifier()
            action = await self._load_login_page(generate_code_challenge(code_verifier))
            code = await self._credentials_login(action)
            tokens = await self._load_tokens(code, code_verifier)
            self._access_token = tokens["access_token"]
            self._refresh_token = tokens.get("refresh_token")
            expires_in = timedelta(seconds=int(tokens.get("expires_in", 300)))
            self._access_token_expiration = (
                datetime.now() + expires_in - TOKEN_EXPIRY_MARGIN
            )
            await self._load_api_keys()
            logger.debug("Successfully authenticated Smart Meter API")

    async def refresh_token(self):
        """Create a valid access token (kept for compatibility)."""
        await self.login(force=True)

    def _dt_string(self, dt):
        return dt.strftime(const.API_DATE_FORMAT)[:-3] + "Z"

    async def zaehlpunkte(self):
        """Returns zaehlpunkte (contracts) for currently logged in user."""
        return await self._request("zaehlpunkte")

    async def get_zaehlpunkt(self, zaehlpunkt=None):
        """Returns (customer_id, zaehlpunktnummer) of the given or first
        zaehlpunkt."""
        contracts = await self.zaehlpunkte()
        for contract in contracts or []:
            for zp in contract.get("zaehlpunkte", []):
                if zaehlpunkt is None or zp.get("zaehlpunktnummer") == zaehlpunkt:
                    return contract.get("geschaeftspartner"), zp["zaehlpunktnummer"]
        raise SmartmeterQueryError(f"Zaehlpunkt {zaehlpunkt} not found")

    async def verbrauch(self, date_from: datetime, zaehlpunkt=None):
        """Returns hourly consumption of 24h starting at date_from."""
        customer_id, zaehlpunkt = await self.get_zaehlpunkt(zaehlpunkt)
        endpoint = f"messdaten/{customer_id}/{zaehlpunkt}/verbrauch"
        query = const.build_verbrauchs_args(dateFrom=self._dt_string(date_from))
        return await self._request(endpoint, query=query)

    async def profil(self):
        """Get profil of logged in user."""
        return await self._request("user/profile", const.API_URL_ALT)

    async def consumptions(self):
        """Returns response from 'consumptions' endpoint."""
        return await self._request("zaehlpunkt/consumptions")

    async def base_information(self):
        """Returns response from 'baseInformation' endpoint."""
        return await self._request("zaehlpunkt/baseInformation")

    async def meter_readings(self):
        """Returns response from 'meterReadings' endpoint."""
        return await self._request("zaehlpunkt/meterReadings")

    async def _request(
        self,
        endpoint,
        base_url=None,
        method="GET",
        data=None,
        query=None,
        _retry=True,
    ):
        """Send requests to the Smartmeter API."""
        await self.login()

        orig_base_url = base_url
        if base_url is None:
            base_url = self.api_url
        url = base_url.rstrip("/") + "/" + endpoint
        if query:
            separator = "?" if "?" not in endpoint else "&"
            url += separator + parse.urlencode(query)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        if base_url == self.api_url:
            headers["X-Gateway-APIKey"] = self._api_gateway_token
        elif base_url == self.api_url_b2b:
            headers["X-Gateway-APIKey"] = self._api_gateway_b2b_token

        logger.debug(f"REQUEST: {url}")
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    status = response.status
                    text = await response.text()
        except (asyncio.TimeoutError, aiohttp.ClientError, OSError) as exception:
            raise SmartmeterConnectionError(
                f"Error fetching {endpoint}: {exception!r}"
            ) from exception

        if status == 401 and _retry:
            # token got invalid, login again and retry once
            await self.login(force=True)
            return await self._request(
                endpoint, orig_base_url, method, data, query, _retry=False
            )
        return self._parse_response(endpoint, status, text)

    @staticmethod
    def _parse_response(endpoint, status, text):
        if status >= 400:
            raise SmartmeterQueryError(
                f"Request {endpoint} failed (HTTP {status})",
                code=status,
                error_response=text[:500],
            )
        try:
            result = json.loads(text) if text else None
        except ValueError as exception:
            raise SmartmeterQueryError(
                f"Invalid JSON from {endpoint}", error_response=text[:500]
            ) from exception
        if isinstance(result, dict) and "Exception" in result:
            raise SmartmeterQueryError(
                f"Cannot access {endpoint}: {result['Exception']}",
                error_response=text[:500],
            )
        return result
