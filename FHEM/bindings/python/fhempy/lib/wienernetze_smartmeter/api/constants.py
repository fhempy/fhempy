"""Constants of the Wiener Netze Smartmeter API.

Kept in sync with https://github.com/DarwinsBuddy/WienerNetzeSmartmeter
"""

PAGE_URL = "https://smartmeter-web.wienernetze.at/"
API_CONFIG_URL = "https://smartmeter-web.wienernetze.at/assets/app-config.json"
API_URL_ALT = "https://service.wienernetze.at/sm/api/"
# defaults, app-config.json delivers the current values as b2cApiUrl/b2bApiUrl
API_URL = "https://api.wstw.at/gateway/WN_SMART_METER_PORTAL_API_B2C/1.0"
API_URL_B2B = "https://api.wstw.at/gateway/WN_SMART_METER_PORTAL_API_B2B/1.0"
REDIRECT_URI = "https://smartmeter-web.wienernetze.at/"
API_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
AUTH_URL = "https://log.wien/auth/realms/logwien/protocol/openid-connect/"  # noqa
CLIENT_ID = "wn-smartmeter"

LOGIN_ARGS = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_mode": "fragment",
    "response_type": "code",
    "scope": "openid",
    "nonce": "",
    "code_challenge_method": "S256",
}


def build_access_token_args(**kwargs):
    args = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    args.update(**kwargs)
    return args


def build_verbrauchs_args(**kwargs):
    args = {
        "period": "DAY",
        "accumulate": False,
        "offset": 0,
        "dayViewResolution": "HOUR",
    }
    args.update(**kwargs)
    return args


# log.wien is used from a browser, send browser like headers for the login
LOGIN_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-AT,de;q=0.9,en;q=0.8",
}
