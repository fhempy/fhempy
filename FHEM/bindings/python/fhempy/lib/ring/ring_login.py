"""Ring login via the OAuth v2 web flow (authorization code + PKCE).

Ring blocks the old password grant on https://oauth.ring.com/oauth/token
with "406 Not Acceptable". The Ring app signs in through /oauth/v2 instead:
open the authorize page, post the credentials (and the 2FA code), follow the
redirect that carries the authorization code and exchange it for tokens.

All functions here are blocking (requests) and run in a worker thread.
"""

import base64
import hashlib
import json
import platform
import re
import secrets
import time
from urllib.parse import urljoin, urlsplit, parse_qs

import requests

OAUTH_BASE_URL = "https://oauth.ring.com"
TOKEN_URL = OAUTH_BASE_URL + "/oauth/token"
CLIENT_ID = "ring_official_android"
REDIRECT_URI = "https://ring.com/signin/callback"
USER_AGENT = "android:com.ringapp"
APP_VERSION = "3.102.0"
TIMEOUT = 20
MAX_REDIRECTS = 5

_CSRF_NAMES = ("csrf-token", "csrfToken", "csrf_token", "_csrf", "XSRF-TOKEN")


class RingLoginError(Exception):
    """Login failed for an unexpected reason."""


class RingAccessDenied(RingLoginError):
    """Wrong username or password."""


class RingRequires2FA(RingLoginError):
    """Ring sent a 2FA code, set it with 2fa_code."""


class RingInvalid2FA(RingLoginError):
    """The 2FA code was wrong or expired."""


def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _json_or_none(response):
    try:
        return response.json()
    except ValueError:
        return None


def _find_csrf_in_object(obj, depth=0):
    if depth > 5:
        return None
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in ("csrftoken", "csrf", "csrf-token", "csrf_token"):
                if isinstance(value, str):
                    return value
            found = _find_csrf_in_object(value, depth + 1)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _find_csrf_in_object(value, depth + 1)
            if found:
                return found
    return None


def _csrf_from_next_data(html):
    next_data = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not next_data:
        return None
    try:
        return _find_csrf_in_object(json.loads(next_data.group(1)))
    except ValueError:
        return None


def _csrf_from_html(html):
    for name in ("csrf-token", "csrfToken", "_csrf"):
        for pattern in (
            r'name="' + name + r'"[^>]*value="([^"]+)"',
            r'value="([^"]+)"[^>]*name="' + name + r'"',
            r'meta[^>]*name="' + name + r'"[^>]*content="([^"]+)"',
        ):
            match = re.search(pattern, html)
            if match:
                return match.group(1)
    match = re.search(r"[\"']csrf[-_]?[Tt]oken[\"']\s*[=:]\s*[\"']([^\"']+)[\"']", html)
    return match.group(1) if match else None


def extract_csrf_token(html, cookies):
    """Find the CSRF token of the Ring sign-in page."""
    for name in _CSRF_NAMES:
        if cookies.get(name):
            return cookies[name]
    token = _csrf_from_next_data(html) or _csrf_from_html(html)
    if token:
        return token
    raise RingLoginError("Unable to find CSRF token on the Ring sign-in page")


class RingPkceLogin:
    """One sign-in attempt. Keep the object between password and 2FA code."""

    def __init__(self, hardware_id, user_agent=USER_AGENT):
        self.hardware_id = hardware_id
        self.user_agent = user_agent
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent
        self._code_verifier = _b64url(secrets.token_bytes(32))
        self._state = secrets.token_hex(16)
        self._csrf_token = None
        self.waiting_for_2fa = False

    def login(self, username, password):
        """Sign in with username and password.

        Returns the token or raises RingRequires2FA if Ring sent a 2FA code.
        """
        self._open_authorize_page()
        self._submit_credentials(username, password)
        return self._finish()

    def verify_2fa(self, code):
        """Continue a sign-in that is waiting for the 2FA code."""
        if not self.waiting_for_2fa:
            raise RingLoginError("No sign-in is waiting for a 2FA code")
        response = self._session.post(
            OAUTH_BASE_URL + "/oauth/v2/2fa/verify",
            data={
                "2fa_code": code,
                "csrf-token": self._csrf_token,
                "remember_me": "false",
            },
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        if response.status_code in (400, 401):
            raise RingInvalid2FA("2FA code is invalid or expired")
        if response.status_code not in (200, 201):
            raise RingLoginError(
                f"2FA verification failed with status {response.status_code}"
            )
        self.waiting_for_2fa = False
        return self._finish()

    def _open_authorize_page(self):
        code_challenge = _b64url(
            hashlib.sha256(self._code_verifier.encode("ascii")).digest()
        )
        params = {
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "response_type": "code",
            "prompt": "login",
            "state": self._state,
            "scope": "client",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "device_model": "fhempy",
            "app_version": APP_VERSION,
            "dark_mode": "false",
            "device_brand": "python",
            "device_os_version": platform.python_version(),
            "app_brand": "ring",
            "hardware_id": self.hardware_id,
        }
        url = OAUTH_BASE_URL + "/oauth/v2/authorize"
        response = None
        for _ in range(MAX_REDIRECTS):
            response = self._session.get(
                url,
                params=params,
                allow_redirects=False,
                timeout=TIMEOUT,
            )
            params = None
            if response.is_redirect and response.headers.get("location"):
                url = urljoin(response.url, response.headers["location"])
                continue
            break
        if response is None or response.status_code >= 400:
            status = response.status_code if response is not None else "-"
            raise RingLoginError(f"Ring sign-in page failed with status {status}")
        self._csrf_token = extract_csrf_token(
            response.text, self._session.cookies.get_dict()
        )

    def _submit_credentials(self, username, password):
        response = self._session.post(
            OAUTH_BASE_URL + "/oauth/v2/signin",
            data={
                "username": username,
                "password": password,
                "csrf-token": self._csrf_token,
            },
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        data = _json_or_none(response)
        location = response.headers.get("location", "")
        if (
            response.status_code == 412
            or (
                isinstance(data, dict)
                and ("tsv_state" in data or "next_time_in_secs" in data)
            )
            or "/2fa" in location
        ):
            self.waiting_for_2fa = True
            raise RingRequires2FA("Ring sent a 2FA code")
        if response.status_code in (400, 401, 403):
            raise RingAccessDenied("wrong username or password")
        if response.status_code >= 400:
            raise RingLoginError(f"Sign-in failed with status {response.status_code}")

    def _authorization_code(self):
        url = OAUTH_BASE_URL + "/oauth/v2/authorize"
        for _ in range(MAX_REDIRECTS):
            response = self._session.get(url, allow_redirects=False, timeout=TIMEOUT)
            if not response.is_redirect:
                raise RingLoginError(
                    "Expected redirect from authorize but got "
                    f"{response.status_code}"
                )
            location = response.headers.get("location")
            if not location:
                raise RingLoginError("No location header in authorize redirect")
            url = urljoin(response.url, location)
            query = parse_qs(urlsplit(url).query)
            if "code" in query:
                if query.get("state", [None])[0] != self._state:
                    raise RingLoginError("State mismatch in Ring OAuth response")
                return query["code"][0]
        raise RingLoginError("No authorization code after following redirects")

    def _finish(self):
        code = self._authorization_code()
        response = requests.post(
            TOKEN_URL,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code_verifier": self._code_verifier,
                "client_id": CLIENT_ID,
            },
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
                "hardware_id": self.hardware_id,
            },
            timeout=TIMEOUT,
        )
        if response.status_code != 200:
            raise RingLoginError(
                f"Token request failed with status {response.status_code}"
            )
        token = response.json()
        if "access_token" not in token:
            raise RingLoginError("Ring did not return an access token")
        if "expires_in" in token and "expires_at" not in token:
            # requests_oauthlib needs expires_at to refresh the token in time
            token["expires_at"] = time.time() + int(token["expires_in"])
        self._session.close()
        return token
