import asyncio
import functools
import json
import random
import string
import uuid

import aiohttp
from oauthlib.common import urldecode
from oauthlib.oauth2 import OAuth2Error
from ring_doorbell import Auth, Ring, RingEventListener
from ring_doorbell.const import NAMESPACE_UUID, OAuth
from ring_doorbell.exceptions import AuthenticationError

from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from .ring_login import (
    USER_AGENT,
    RingAccessDenied,
    RingInvalid2FA,
    RingLoginError,
    RingPkceLogin,
    RingRequires2FA,
)

# state goes back to "connected" this many seconds after a ding/motion
ALERT_RESET_SECONDS = 60
MAX_BACKOFF_SECONDS = 300


class RingDeviceNotFound(Exception):
    """No Ring device with the defined name."""


class RingAuth(Auth):
    """Auth that refreshes tokens with the headers the Ring app sends.

    API queries already send User-Agent and hardware_id, the aiohttp session
    adds "Accept: application/json".
    """

    async def async_refresh_tokens(self):
        try:
            headers = {
                "User-Agent": self.user_agent,
                "hardware_id": self.hardware_id,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            }
            body = self._oauth_client.prepare_refresh_body(
                refresh_token=self._token["refresh_token"]
            )
            resp = await self._session.request(
                "POST",
                OAuth.ENDPOINT,
                data=dict(urldecode(body)),
                headers=headers,
                auth=self._auth,
            )
            async with resp:
                text = await resp.text()
            self._token = self._oauth_client.parse_request_body_response(
                text, scope=OAuth.SCOPE
            )
        except OAuth2Error as ex:
            raise AuthenticationError(ex) from ex

        if self.token_updater is not None:
            self.token_updater(self._token)

        return self._token


class ring(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self._username = None
        self._password = ""
        self._token = ""
        self._2facode = None
        self._pkce_login = None
        self._attr_dingPollInterval = 5
        self._attr_deviceUpdateInterval = 300
        self._history = []
        self._ring = None
        self._rdevice = None
        self._http_session = None
        self._listener = None
        self._last_recording_id = None
        self._lastrecording_url = ""
        self._login_lock = asyncio.Lock()
        self._loop_tasks = []
        self._alert_reset_task = None

    async def token_updated(self, token):
        self._token = token
        encrypted_token = await utils.async_encrypt_string(
            json.dumps(token), self._reading_encryption_key
        )
        await fhem.readingsSingleUpdate(self.hash, "token", encrypted_token, 1)

    def _token_updater(self, token):
        # called by ring_doorbell inside the event loop
        self._token = token
        self.create_async_task(self.token_updated(token))

    async def _fcm_credentials(self):
        reading = await fhem.ReadingsVal(self.hash["NAME"], "fcm_credentials", "")
        if reading == "":
            return None
        try:
            return json.loads(
                await utils.async_decrypt_string(reading, self._reading_encryption_key)
            )
        except Exception:
            self.logger.debug("Ignoring invalid fcm credentials", exc_info=True)
            return None

    async def _store_fcm_credentials(self, credentials):
        encrypted = await utils.async_encrypt_string(
            json.dumps(credentials), self._reading_encryption_key
        )
        await fhem.readingsSingleUpdate(self.hash, "fcm_credentials", encrypted, 1)

    def _fcm_credentials_updated(self, credentials):
        self.create_async_task(self._store_fcm_credentials(credentials))

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self._attr_list = {
            "deviceUpdateInterval": {"default": 300, "format": "int"},
            "dingPollInterval": {"default": 5, "format": "int"},
        }
        await self.set_attr_config(self._attr_list)
        self.set_list_conf = {
            "password": {"args": ["password"]},
            "2fa_code": {"args": ["2facode"]},
        }
        await self.set_set_config(self.set_list_conf)

        if len(args) < 5:
            return (
                "Usage: define rrring fhempy ring <USERNAME>"
                " <RING_DEVICE_NAME> [<IDENTIFIER>]"
            )
        self._username = args[3]
        self._rdevname = args[4]
        if len(args) > 5:
            self._ridentifier = args[5]
            self.hash["IDENTIFIER"] = args[5]
        else:
            # keep the identifier across restarts, otherwise Ring sees a new
            # client device (hardware id) on every start
            self._ridentifier = await fhem.ReadingsVal(
                self.hash["NAME"], "identifier", ""
            )
            if self._ridentifier == "":
                characters = string.ascii_letters + string.digits
                self._ridentifier = "".join(
                    random.choice(characters) for _ in range(20)  # NOSONAR
                )
                await fhem.readingsSingleUpdate(
                    self.hash, "identifier", self._ridentifier, 1
                )
        self._reading_encryption_key = await fhem.getUniqueId(hash)
        self._ring = None
        self._rdevice = None
        self.hash["USERNAME"] = args[3]
        self.hash["RINGDEVICE"] = args[4]
        self.create_async_task(self.ring_login())

    async def _load_credentials(self):
        if self._token == "":
            token_reading = await fhem.ReadingsVal(self.hash["NAME"], "token", "")
            if token_reading != "":
                token_reading = await utils.async_decrypt_string(
                    token_reading, self._reading_encryption_key
                )
                self._token = json.loads(token_reading)
        if self._password == "":
            self._password = await fhem.ReadingsVal(self.hash["NAME"], "password", "")
            if self._password != "":
                self._password = await utils.async_decrypt_string(
                    self._password, self._reading_encryption_key
                )

    async def ring_login(self):
        async with self._login_lock:
            await self._stop_ring()
            await self._load_credentials()
            try:
                token = self._token
                if token == "":
                    if self._password == "":
                        await fhem.readingsSingleUpdate(
                            self.hash, "state", "please set password", 1
                        )
                        return
                    token = await utils.run_blocking(
                        functools.partial(self._fetch_token)
                    )
                    if isinstance(token, str):
                        await fhem.readingsSingleUpdate(self.hash, "state", token, 1)
                        return
                    await self.token_updated(token)
                await self._start_ring(token)
            except AuthenticationError:
                await self._stop_ring()
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "Login expired, please set password", 1
                )
                self._errors.failed("Login failed", key="login")
                return
            except RingDeviceNotFound:
                await self._stop_ring()
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "device not found", 1
                )
                return
            except Exception:
                await self._stop_ring()
                await fhem.readingsSingleUpdate(self.hash, "state", "Login failed", 1)
                self._errors.failed("Login failed, retry later", key="login")
                # e.g. network down, try again later
                self._loop_tasks.append(self.create_async_task(self._retry_login()))
                return
            self._errors.success(key="login")
            await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
            self._loop_tasks.append(self.create_async_task(self.update_loop()))
            await self._start_events()

    async def _retry_login(self):
        await asyncio.sleep(MAX_BACKOFF_SECONDS)
        self.create_async_task(self.ring_login())

    async def _start_ring(self, token):
        # send "Accept: application/json" like the Ring app
        self._http_session = aiohttp.ClientSession(
            headers={"Accept": "application/json"}
        )
        auth = RingAuth(
            USER_AGENT,
            token,
            self._token_updater,
            self._hardware_id(),
            http_client_session=self._http_session,
        )
        # keep the device model of older versions, it is shown in the Ring app
        auth.device_model = "ring-doorbell:" + self._ridentifier + "/1.0"
        self._ring = Ring(auth)
        await self._ring.async_update_data()
        self._rdevice = self._ring.get_device_by_name(self._rdevname)
        if self._rdevice is None:
            raise RingDeviceNotFound(self._rdevname)

        if self._rdevice.has_capability("volume"):
            self.set_list_conf["volume"] = {
                "args": ["volume"],
                "params": {"volume": {"format": "int"}},
                "options": "slider,0,1,10",
            }
            await self.set_set_config(self.set_list_conf)
        await self.poll_device()
        await self.update_readings()

    async def _stop_ring(self):
        for task in self._loop_tasks:
            self.cancel_async_task(task)
        self._loop_tasks = []
        if self._alert_reset_task:
            self.cancel_async_task(self._alert_reset_task)
            self._alert_reset_task = None
        listener = self._listener
        self._listener = None
        if listener:
            try:
                await listener.stop()
            except Exception:
                self.logger.debug("Failed to stop event listener", exc_info=True)
        session = self._http_session
        self._http_session = None
        if session:
            await session.close()
        self._ring = None
        self._rdevice = None

    async def _start_events(self):
        """Receive dings/motion via push (Firebase), poll only as fallback."""
        try:
            self._listener = RingEventListener(
                self._ring,
                await self._fcm_credentials(),
                self._fcm_credentials_updated,
            )
            if await self._listener.start():
                self._listener.add_notification_callback(self._on_ring_event)
                await fhem.readingsSingleUpdate(self.hash, "events", "push", 1)
                return
            self.logger.warning("Ring push events not available, polling dings")
        except Exception:
            self.logger.warning(
                "Ring push events not available, polling dings", exc_info=True
            )
        self._listener = None
        await fhem.readingsSingleUpdate(self.hash, "events", "polling", 1)
        self._loop_tasks.append(self.create_async_task(self.poll_dings_loop()))

    def _on_ring_event(self, event):
        # called by the event listener inside the event loop
        if self._rdevice is None or event.doorbot_id != self._rdevice.id:
            return
        if event.is_update:
            return
        self.create_async_task(self.update_alert_readings(event))
        if self._alert_reset_task:
            self.cancel_async_task(self._alert_reset_task)
        self._alert_reset_task = self.create_async_task(self._reset_alert())

    async def _reset_alert(self):
        await asyncio.sleep(ALERT_RESET_SECONDS)
        self._alert_reset_task = None
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected", 1)
        try:
            await self.poll_device()
            await self.update_readings()
        except Exception:
            self._errors.failed("Failed to poll device", key="poll")

    async def poll_dings_loop(self):
        alert_ids = set()
        failures = 0
        while True:
            try:
                await self._ring.async_update_dings()
                alerts = [
                    alert
                    for alert in self._ring.active_alerts()
                    if alert["doorbot_id"] == self._rdevice.id
                ]
                for alert in alerts:
                    if alert["id"] not in alert_ids:
                        self._on_ring_event(alert)
                alert_ids = {alert["id"] for alert in alerts}
                self._errors.success(key="dings")
                failures = 0
            except AuthenticationError:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "Login expired, please set password", 1
                )
                return
            except Exception:
                failures += 1
                self._errors.failed("Failed to poll dings", key="dings")
            await asyncio.sleep(self._wait_time(self._attr_dingPollInterval, failures))

    @staticmethod
    def _wait_time(interval, failures):
        # back off after errors to avoid hammering the Ring API
        if failures == 0:
            return interval
        return min(interval * 2**failures, MAX_BACKOFF_SECONDS)

    async def update_loop(self):
        failures = 0
        while True:
            await asyncio.sleep(
                self._wait_time(self._attr_deviceUpdateInterval, failures)
            )
            try:
                await self._ring.async_update_devices()
                await self.poll_device()
                await self.update_readings()
                self._errors.success(key="poll")
                failures = 0
            except AuthenticationError:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "Login expired, please set password", 1
                )
                return
            except Exception:
                failures += 1
                self._errors.failed("Failed to poll devices", key="poll")

    async def poll_device(self):
        await self._rdevice.async_update_health_data()
        if self._rdevice.family not in ("doorbots", "authorized_doorbots"):
            return
        self._history = await self._rdevice.async_history(limit=5)
        self._last_recording_id = await self._rdevice.async_get_last_recording_id()
        if self._last_recording_id:
            url = await self._rdevice.async_recording_url(self._last_recording_id)
            self._lastrecording_url = url or ""

    async def update_alert_readings(self, alert):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdate(self.hash, "alert_id", alert["id"])
            await fhem.readingsBulkUpdate(self.hash, "alert_kind", alert["kind"])
            await fhem.readingsBulkUpdate(self.hash, "alert_state", alert["state"])
            await fhem.readingsBulkUpdate(
                self.hash, "alert_doorbot_id", alert["doorbot_id"]
            )
            await fhem.readingsBulkUpdate(self.hash, "state", alert["kind"])
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def update_history_readings(self, event, idx):
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "history_" + str(idx) + "_id", event["id"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "history_" + str(idx) + "_kind", event["kind"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "history_" + str(idx) + "_answered", event["answered"]
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "history_" + str(idx) + "_created_at", event["created_at"]
        )

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "address", self._rdevice.address
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "family", self._rdevice.family
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "device_id", self._rdevice.device_id
            )
            await fhem.readingsBulkUpdateIfChanged(self.hash, "id", self._rdevice.id)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model", self._rdevice.model
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "firmware", self._rdevice.firmware
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "latitude", self._rdevice.latitude
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "longitude", self._rdevice.longitude
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "kind", self._rdevice.kind
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "name", self._rdevice.name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "timezone", self._rdevice.timezone
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "wifi_name", self._rdevice.wifi_name
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "wifi_signal_strength", self._rdevice.wifi_signal_strength
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "wifi_signal_category", self._rdevice.wifi_signal_category
            )
            await self.update_if_available("battery_life")
            await self.update_if_available("existing_doorbell_type")
            await self.update_if_available("existing_doorbell_type_enabled")
            await self.update_if_available("existing_doorbell_type_duration")
            await self.update_if_available("subscribed")
            await self.update_if_available("subscribed_motion")
            await self.update_if_available("has_subscription")
            await self.update_if_available("volume")
            await self.update_if_available("connection_status")
            if (
                self._rdevice.family == "doorbots"
                or self._rdevice.family == "authorized_doorbots"
            ):
                if self._last_recording_id:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, "last_recording_id", self._last_recording_id
                    )
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "last_recording_url", self._lastrecording_url
                )
                for idx, event in enumerate(self._history, start=1):
                    await self.update_history_readings(event, idx)
        except Exception:
            self.logger.exception(
                "Failed to update readings, please report here: https://forum.fhem.de/index.php/topic,117381"
            )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_if_available(self, reading):
        if hasattr(self._rdevice, reading):
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, reading, getattr(self._rdevice, reading)
            )

    def _hardware_id(self):
        # same id as older versions used, existing tokens stay valid
        return str(
            uuid.uuid5(
                uuid.UUID(NAMESPACE_UUID),
                str(uuid.getnode()) + self._ridentifier + "/1.0",
            )
        )

    def _fetch_token(self):
        """Sign in with password (and 2FA code), returns error text or token."""
        try:
            pending = self._pkce_login
            if self._2facode and pending and pending.waiting_for_2fa:
                code = self._2facode
                self._2facode = None
                token = pending.verify_2fa(code)
            else:
                # a code without a waiting sign-in (e.g. after restart) is stale
                self._2facode = None
                self._pkce_login = RingPkceLogin(self._hardware_id())
                token = self._pkce_login.login(self._username, self._password)
        except RingRequires2FA:
            return "please set 2fa_code"
        except RingInvalid2FA:
            return "invalid 2fa_code, please set 2fa_code again"
        except RingAccessDenied:
            self._pkce_login = None
            return "AccessDenied: wrong username or password"
        except RingLoginError as ex:
            self._pkce_login = None
            self.logger.error(f"Ring login failed: {ex}")
            return "Login failed"
        self._pkce_login = None
        return token

    async def set_volume(self, hash, params):
        self.create_async_task(self.set_volume_task(params["volume"]))

    async def set_volume_task(self, new_volume):
        try:
            await self._rdevice.async_set_volume(new_volume)
        except Exception:
            self._errors.failed("Failed to set volume", key="volume")
            return
        await self.update_readings()

    async def set_password(self, hash, params):
        self._password = params["password"]
        encrypted_password = await utils.async_encrypt_string(
            self._password, self._reading_encryption_key
        )
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "password", encrypted_password, 1
        )
        self._token = ""
        self._2facode = None
        await fhem.CommandDeleteReading(self.hash, self.hash["NAME"] + " token")
        self.create_async_task(self.ring_login())

    async def set_2fa_code(self, hash, params):
        self._2facode = params["2facode"]
        self.create_async_task(self.ring_login())

    async def Undefine(self, hash):
        await self._stop_ring()
        await super().Undefine(hash)
