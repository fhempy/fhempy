"""Xiaomi cloud login and device list.

Based on the Xiaomi Cloud Tokens Extractor by Piotr Machowski (MIT License):
https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import string
import time
from urllib.parse import parse_qs, urlparse

import requests
from Cryptodome.Cipher import ARC4

logger = logging.getLogger(__name__)

SERVERS = ["cn", "de", "us", "ru", "tw", "sg", "in", "i2"]

ACCOUNT_URL = "https://account.xiaomi.com"
STS_URL = "https://sts.api.io.mi.com/sts"
REQUEST_TIMEOUT = 30


class XiaomiCloudError(Exception):
    pass


class CaptchaRequired(Exception):
    """The login needs the text of the captcha image."""

    def __init__(self, image):
        super().__init__("Captcha required")
        self.image = image


class VerificationRequired(Exception):
    """The login needs the code Xiaomi sent by email (2FA)."""

    def __init__(self):
        super().__init__("Verification code required")


class XiaomiCloud:
    def __init__(self):
        self._agent = self._generate_agent()
        self._device_id = "".join(
            secrets.choice(string.ascii_lowercase) for _ in range(6)
        )
        self._session = requests.Session()
        self._ssecurity = None
        self.user_id = None
        self._service_token = None
        self._username = None
        self._password = None
        self._sign = None
        self._location = None
        self._captcha_fields = None
        self._2fa_context = None
        self._qr = None

    @property
    def logged_in(self):
        return self._ssecurity is not None and self._service_token is not None

    @staticmethod
    def _generate_agent():
        agent_id = "".join(secrets.choice("ABCDE") for _ in range(13))
        random_text = "".join(secrets.choice(string.ascii_lowercase) for _ in range(18))
        return f"{random_text}-{agent_id} APP/com.xiaomi.mihome APPV/10.5.201"

    @staticmethod
    def _to_json(text):
        return json.loads(text.replace("&&&START&&&", ""))

    def _headers(self):
        return {
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _get(self, url, **kwargs):
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        return self._session.get(url, **kwargs)

    def _post(self, url, **kwargs):
        kwargs.setdefault("headers", self._headers())
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        return self._session.post(url, **kwargs)

    # password login
    def login(self, username, password):
        """Login with username and password.

        Raises CaptchaRequired or VerificationRequired if the user has to
        solve a captcha or enter the code from the email, continue with
        submit_captcha/submit_verification_code then.
        """
        self._username = username
        self._password = password
        for domain in ["mi.com", "xiaomi.com"]:
            self._session.cookies.set("sdkVersion", "accountsdk-18.8.15", domain=domain)
            self._session.cookies.set("deviceId", self._device_id, domain=domain)

        if self._login_step1():
            # still logged in from an earlier session
            self._login_step3()
            return
        fields = {
            "sid": "xiaomiio",
            # the Xiaomi login expects the MD5 hash of the password
            "hash": hashlib.md5(password.encode()).hexdigest().upper(),  # NOSONAR
            "callback": STS_URL,
            "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
            "user": username,
            "_sign": self._sign,
            "_json": "true",
        }
        self._login_step2(fields)

    def _login_step1(self):
        """Returns True if the login is already done (no password needed)."""
        resp = self._get(
            f"{ACCOUNT_URL}/pass/serviceLogin?sid=xiaomiio&_json=true",
            cookies={"userId": self._username},
        )
        if resp.status_code != 200:
            raise XiaomiCloudError(f"Login step 1 failed: HTTP {resp.status_code}")
        data = self._to_json(resp.text)
        if "_sign" in data:
            self._sign = data["_sign"]
            return False
        if "ssecurity" in data:
            self._set_login_data(data)
            return True
        raise XiaomiCloudError("Invalid username")

    def _set_login_data(self, data):
        self._ssecurity = data["ssecurity"]
        self.user_id = data.get("userId")
        self._location = data.get("location")

    def _login_step2(self, fields):
        resp = self._post(
            f"{ACCOUNT_URL}/pass/serviceLoginAuth2",
            params=fields,
            allow_redirects=False,
        )
        if resp.status_code != 200:
            raise XiaomiCloudError(f"Login failed: HTTP {resp.status_code}")
        data = self._to_json(resp.text)

        if data.get("captchaUrl"):
            if "captCode" in fields and data.get("code") == 87001:
                logger.info("Wrong captcha, please try again")
            self._captcha_fields = fields
            raise CaptchaRequired(self._load_captcha(data["captchaUrl"]))

        if len(str(data.get("ssecurity", ""))) > 4:
            self._set_login_data(data)
            self._login_step3()
            return

        if "notificationUrl" in data:
            self._start_verification(data["notificationUrl"])
            raise VerificationRequired()

        desc = data.get("desc") or data.get("description") or "unknown error"
        raise XiaomiCloudError(
            f"Login failed: {desc} (code {data.get('code')}), "
            "please check username/password"
        )

    def _load_captcha(self, url):
        if url.startswith("/"):
            url = ACCOUNT_URL + url
        resp = self._get(url)
        if resp.status_code != 200:
            raise XiaomiCloudError("Unable to load captcha image")
        return resp.content

    def submit_captcha(self, code):
        if self._captcha_fields is None:
            raise XiaomiCloudError("No captcha requested, please start the login first")
        fields = dict(self._captcha_fields)
        fields["captCode"] = code
        self._captcha_fields = None
        self._login_step2(fields)

    def _login_step3(self):
        if self._service_token:
            return
        if not self._location:
            raise XiaomiCloudError("Login failed: no service token location")
        resp = self._get(self._location)
        if resp.status_code != 200:
            raise XiaomiCloudError(
                f"Unable to get service token: HTTP {resp.status_code}"
            )
        self._service_token = resp.cookies.get("serviceToken")
        if not self._service_token:
            raise XiaomiCloudError("Unable to get service token")

    # 2FA via email
    def _start_verification(self, notification_url):
        self._get(notification_url)
        context = parse_qs(urlparse(notification_url).query)["context"][0]
        self._2fa_context = context
        self._get(
            f"{ACCOUNT_URL}/identity/list",
            params={"sid": "xiaomiio", "context": context, "_locale": "en_US"},
        )
        self._post(
            f"{ACCOUNT_URL}/identity/auth/sendEmailTicket",
            params={
                "_dc": str(int(time.time() * 1000)),
                "sid": "xiaomiio",
                "context": context,
                "mask": "0",
                "_locale": "en_US",
            },
            data={
                "retry": "0",
                "icode": "",
                "_json": "true",
                "ick": self._session.cookies.get("ick", ""),
            },
        )

    def submit_verification_code(self, code):
        context = self._2fa_context
        if context is None:
            raise XiaomiCloudError(
                "No verification code requested, please start the login first"
            )
        resp = self._post(
            f"{ACCOUNT_URL}/identity/auth/verifyEmail",
            params={
                "_flag": "8",
                "_json": "true",
                "sid": "xiaomiio",
                "context": context,
                "mask": "0",
                "_locale": "en_US",
            },
            data={
                "_flag": "8",
                "ticket": code,
                "trust": "false",
                "_json": "true",
                "ick": self._session.cookies.get("ick", ""),
            },
        )
        if resp.status_code != 200:
            raise XiaomiCloudError(f"Verification failed: HTTP {resp.status_code}")
        finish_loc = self._verification_finish_location(resp, context)
        self._2fa_context = None
        self._finish_verification(finish_loc)

    def _verification_finish_location(self, resp, context):
        finish_loc = None
        try:
            data = self._to_json(resp.text)
            if data.get("code") not in (None, 0):
                error = data.get("tips") or data.get("desc") or data
                raise XiaomiCloudError(f"Verification failed: {error}")
            finish_loc = data.get("location")
        except ValueError:
            finish_loc = resp.headers.get("Location")
        if not finish_loc:
            resp = self._get(
                f"{ACCOUNT_URL}/identity/result/check",
                params={"sid": "xiaomiio", "context": context, "_locale": "en_US"},
                allow_redirects=False,
            )
            finish_loc = resp.headers.get("Location")
        if not finish_loc:
            raise XiaomiCloudError("Verification failed: no finish location")
        return finish_loc

    def _finish_verification(self, finish_loc):
        if "identity/result/check" in finish_loc:
            resp = self._get(finish_loc, allow_redirects=False)
            end_url = resp.headers.get("Location")
        else:
            end_url = finish_loc
        if not end_url:
            raise XiaomiCloudError("Verification failed: no end location")

        resp = self._get(end_url, allow_redirects=False)
        if resp.status_code == 200 and "Xiaomi Account - Tips" in resp.text:
            resp = self._get(end_url, allow_redirects=False)
        try:
            pragma = json.loads(resp.headers.get("extension-pragma", "{}"))
        except ValueError:
            pragma = {}
        if not pragma.get("ssecurity"):
            raise XiaomiCloudError("Verification failed: no ssecurity received")
        self._ssecurity = pragma["ssecurity"]
        self._finish_sts(resp)

    def _finish_sts(self, resp):
        sts_url = resp.headers.get("Location")
        if not sts_url:
            idx = resp.text.find(STS_URL)
            if idx != -1:
                end = resp.text.find('"', idx)
                sts_url = resp.text[idx:end] if end != -1 else resp.text[idx:]
        if not sts_url:
            raise XiaomiCloudError("Verification failed: no STS location")
        resp = self._get(sts_url)
        if resp.status_code != 200:
            raise XiaomiCloudError(f"Verification failed: STS HTTP {resp.status_code}")
        self._service_token = resp.cookies.get(
            "serviceToken"
        ) or self._session.cookies.get("serviceToken", domain=".sts.api.io.mi.com")
        if not self._service_token:
            raise XiaomiCloudError("Verification failed: no service token")
        self.user_id = (
            self.user_id
            or self._session.cookies.get("userId", domain=".xiaomi.com")
            or self._session.cookies.get("userId", domain=".sts.api.io.mi.com")
        )

    # QR code login
    def qr_login_start(self):
        """Returns (qr image bytes, login url), wait with qr_login_wait."""
        resp = self._get(
            f"{ACCOUNT_URL}/longPolling/loginUrl",
            params={
                "_qrsize": "240",
                "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
                "callback": STS_URL,
                "_hasLogo": "false",
                "sid": "xiaomiio",
                "serviceParam": "",
                "_locale": "en_GB",
                "_dc": str(int(time.time() * 1000)),
            },
        )
        if resp.status_code != 200:
            raise XiaomiCloudError(f"Unable to get QR code: HTTP {resp.status_code}")
        data = self._to_json(resp.text)
        if "qr" not in data:
            raise XiaomiCloudError("Unable to get QR code")
        self._qr = data
        image = self._get(data["qr"])
        if image.status_code != 200:
            raise XiaomiCloudError("Unable to load QR code image")
        return image.content, data["loginUrl"]

    def qr_login_wait(self):
        """Blocks until the QR code was scanned or the timeout passed."""
        if self._qr is None:
            raise XiaomiCloudError("Please start the QR code login first")
        timeout = self._qr.get("timeout", 300)
        start = time.time()
        while True:
            try:
                resp = self._session.get(self._qr["lp"], timeout=10)
            except requests.exceptions.Timeout:
                if time.time() - start > timeout:
                    raise XiaomiCloudError("QR code login timed out")
                continue
            if resp.status_code == 200:
                break
            if time.time() - start > timeout:
                raise XiaomiCloudError(f"QR code login failed: HTTP {resp.status_code}")
            time.sleep(2)
        self._qr = None
        self._set_login_data(self._to_json(resp.text))
        self._login_step3()

    # devices
    def get_devices(self, server):
        """Returns all devices of own and shared homes of the server."""
        devices = []
        for home_id, owner in self._get_homes(server):
            resp = self._api_call(
                server,
                "/v2/home/home_device_list",
                '{"home_owner": '
                + str(owner)
                + ',"home_id": '
                + str(home_id)
                + ',  "limit": 200,  "get_split_device": true, '
                '"support_smart_home": true}',
            )
            if resp and resp.get("result"):
                devices.extend(resp["result"].get("device_info") or [])
        return devices

    def _get_homes(self, server):
        """Returns (home id, owner) of own and shared homes."""
        homes = []
        resp = self._api_call(
            server,
            "/v2/homeroom/gethome",
            '{"fg": true, "fetch_share": true, "fetch_share_dev": true, '
            '"limit": 300, "app_ver": 7}',
        )
        if resp and resp.get("result"):
            for home in resp["result"].get("homelist") or []:
                homes.append((home["id"], self.user_id))
        resp = self._api_call(
            server,
            "/v2/user/get_device_cnt",
            '{ "fetch_own": true, "fetch_share": true}',
        )
        if resp and resp.get("result"):
            share = resp["result"].get("share") or {}
            for home in share.get("share_family") or []:
                homes.append((home["home_id"], home["home_owner"]))
        return homes

    @staticmethod
    def _api_url(server):
        return (
            "https://" + ("" if server == "cn" else server + ".") + "api.io.mi.com/app"
        )

    def _api_call(self, server, path, data):
        url = self._api_url(server) + path
        headers = {
            "Accept-Encoding": "identity",
            "User-Agent": self._agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2",
            "MIOT-ENCRYPT-ALGORITHM": "ENCRYPT-RC4",
        }
        cookies = {
            "userId": str(self.user_id),
            "yetAnotherServiceToken": str(self._service_token),
            "serviceToken": str(self._service_token),
            "locale": "en_GB",
            "timezone": "GMT+02:00",
            "is_daylight": "1",
            "dst_offset": "3600000",
            "channel": "MI_APP_STORE",
        }
        nonce = self._generate_nonce(round(time.time() * 1000))
        signed_nonce = self._signed_nonce(nonce)
        fields = self._enc_params(url, "POST", signed_nonce, nonce, {"data": data})
        resp = self._session.post(
            url,
            headers=headers,
            cookies=cookies,
            params=fields,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            logger.debug(f"{path} on {server} failed: HTTP {resp.status_code}")
            return None
        return json.loads(self._decrypt_rc4(signed_nonce, resp.text))

    @staticmethod
    def _generate_nonce(millis):
        nonce_bytes = os.urandom(8) + int(millis / 60000).to_bytes(4, byteorder="big")
        return base64.b64encode(nonce_bytes).decode()

    def _signed_nonce(self, nonce):
        digest = hashlib.sha256(
            base64.b64decode(self._ssecurity) + base64.b64decode(nonce)
        ).digest()
        return base64.b64encode(digest).decode()

    @staticmethod
    def _enc_signature(url, method, signed_nonce, params):
        parts = [method.upper(), url.split("com")[1].replace("/app/", "/")]
        parts += [f"{k}={v}" for k, v in params.items()]
        parts.append(signed_nonce)
        return base64.b64encode(
            # signature algorithm of the Xiaomi cloud API
            hashlib.sha1("&".join(parts).encode("utf-8")).digest()  # NOSONAR
        ).decode()

    def _enc_params(self, url, method, signed_nonce, nonce, params):
        params["rc4_hash__"] = self._enc_signature(url, method, signed_nonce, params)
        for key, value in params.items():
            params[key] = self._encrypt_rc4(signed_nonce, value)
        params.update(
            {
                "signature": self._enc_signature(url, method, signed_nonce, params),
                "ssecurity": self._ssecurity,
                "_nonce": nonce,
            }
        )
        return params

    @staticmethod
    def _rc4(password):
        # the Xiaomi cloud API requires RC4, there is no other option
        cipher = ARC4.new(base64.b64decode(password))  # NOSONAR
        cipher.encrypt(bytes(1024))
        return cipher

    @classmethod
    def _encrypt_rc4(cls, password, payload):
        return base64.b64encode(cls._rc4(password).encrypt(payload.encode())).decode()

    @classmethod
    def _decrypt_rc4(cls, password, payload):
        return cls._rc4(password).encrypt(base64.b64decode(payload))
