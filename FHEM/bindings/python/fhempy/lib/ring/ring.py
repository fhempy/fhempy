import asyncio
import functools
import json
import time

from oauthlib.oauth2 import AccessDeniedError, MissingTokenError
from ring_doorbell import Auth, Ring

try:
    # Python 3.7
    from asyncio.futures import CancelledError
except ImportError:
    # Python 3.8+
    from asyncio import CancelledError

from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class ring(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.loop = asyncio.get_event_loop()
        self._username = None
        self._password = ""
        self._token = ""
        self._2facode = None
        self._attr_dingPollInterval = 5
        self._attr_deviceUpdateInterval = 300
        self._history = []
        self._rdevice = None
        self._lastrecording_url = ""
        self._livestreamjson = ""
        self._login_lock = asyncio.Lock()
        self._snapshot = None
        self._attr_list = {
            "deviceUpdateInterval": {"default": 300, "format": "int"},
            "dingPollInterval": {"default": 2, "format": "int"},
        }
        self.set_attr_config(self._attr_list)
        self.set_list_conf = {
            "password": {"args": ["password"]},
            "2fa_code": {"args": ["2facode"]},
        }
        self.set_set_config(self.set_list_conf)
        return

    async def token_updated(self, token):
        self._token = token
        encrypted_token = utils.encrypt_string(
            json.dumps(token), self._reading_encryption_key
        )
        await fhem.readingsSingleUpdate(self.hash, "token", encrypted_token, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 5:
            return (
                "Usage: define rrring PythonModule ring <USERNAME> <RING_DEVICE_NAME>"
            )
        self._username = args[3]
        self._rdevname = args[4]
        self._reading_encryption_key = await fhem.getUniqueId(hash)
        # ring service
        self._ring = None
        # ring doorbell/chime/... device
        self._rdevice = None
        self.hash["USERNAME"] = args[3]
        self.hash["RINGDEVICE"] = args[4]
        self.create_async_task(self.ring_login())

    async def ring_login(self):
        async with self._login_lock:
            if self._token == "":
                token_reading = await fhem.ReadingsVal(self.hash["NAME"], "token", "")
                if token_reading != "":
                    token_reading = utils.decrypt_string(
                        token_reading, self._reading_encryption_key
                    )
                    self._token = json.loads(token_reading)
            if self._password == "":
                self._password = await fhem.ReadingsVal(
                    self.hash["NAME"], "password", ""
                )
                if self._password != "":
                    self._password = utils.decrypt_string(
                        self._password, self._reading_encryption_key
                    )
            try:
                ret = await utils.run_blocking(functools.partial(self.blocking_login))
                if ret:
                    await fhem.readingsSingleUpdate(self.hash, "state", ret, 1)
                    return
                await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
                # start update loop, we are already in a task, therefore no need to create
                await self.update_loop()
            except Exception:
                await fhem.readingsSingleUpdate(self.hash, "state", "Login failed", 1)
                self.logger.error("Login failed")

    async def update_loop(self):
        try:
            await utils.run_blocking(functools.partial(self._ring.update_data))
            devices = await utils.run_blocking(functools.partial(self._ring.devices))
            for dev_type in devices:
                for dev in devices[dev_type]:
                    if dev.name == self._rdevname:
                        self._rdevice = dev

            if self._rdevice is None:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "device not found", 1
                )
                return

            if self._rdevice is not None and self._rdevice.has_capability("volume"):
                self.set_list_conf["volume"] = {
                    "args": ["volume"],
                    "params": {"volume": {"format": "int"}},
                    "options": "slider,0,1,10",
                }
            self.set_set_config(self.set_list_conf)

            await self.update_readings()

            self.create_async_task(self.update_dings_loop())

            while True:
                try:
                    await utils.run_blocking(functools.partial(self.poll_device))
                    await self.update_readings()
                    # handle history
                    if len(self._history) > 0:
                        i = 1
                        for event in self._history:
                            await self.update_history_readings(event, i)
                            i += 1
                except Exception:
                    self.logger.exception("Failed to poll devices")
                await asyncio.sleep(self._attr_deviceUpdateInterval)
        except CancelledError:
            pass
        except Exception:
            self.logger.exception("Failed to update devices")

    async def update_dings_loop(self):
        alert_active = 0
        while True:
            try:
                await utils.run_blocking(functools.partial(self.poll_dings))
                # handle alerts
                alerts = self._ring.active_alerts()
                self.logger.debug("Received dings: " + str(alerts))
                if len(alerts) > 0:
                    for alert in alerts:
                        if alert["doorbot_id"] == self._rdevice.id:
                            alert_active = 1
                            await self.update_alert_readings(alert)
                elif alert_active == 1:
                    alert_active = 0
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "connected", 1
                    )
                    await utils.run_blocking(functools.partial(self.poll_device))
                    await self.update_readings()
            except Exception:
                self.logger.exception("Failed to poll dings...")
                await utils.run_blocking(functools.partial(self.blocking_login))
            await asyncio.sleep(self._attr_dingPollInterval)

    async def update_alert_readings(self, alert):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "alert_id", alert["id"])
        await fhem.readingsBulkUpdate(self.hash, "alert_kind", alert["kind"])
        await fhem.readingsBulkUpdate(self.hash, "alert_sip_to", alert["sip_to"])
        await fhem.readingsBulkUpdate(self.hash, "alert_sip_token", alert["sip_token"])
        await fhem.readingsBulkUpdate(
            self.hash, "alert_doorbot_id", alert["doorbot_id"]
        )
        await fhem.readingsBulkUpdate(self.hash, "state", alert["kind"])
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_history_readings(self, event, idx):
        await fhem.readingsBeginUpdate(self.hash)
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
        await fhem.readingsEndUpdate(self.hash, 1)

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
                await self.update_if_available("last_recording_id")
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, "last_recording_url", self._lastrecording_url
                )
                if self._livestreamjson != "":
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, "livestream_json", json.dumps(self._livestreamjson)
                    )
                # if self._snapshot:
                #     snapshot = '<html><img src="data:image/png,' + self._snapshot + '"/></html>'
                #     await fhem.readingsBulkUpdateIfChanged(self.hash, "snapshot", snapshot)
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

    def poll_dings(self):
        self._ring.update_dings()

    def poll_device(self):
        self._rdevice.update_health_data()
        self._ring.update_data()
        self._history = []
        if (
            self._rdevice.family == "doorbots"
            or self._rdevice.family == "authorized_doorbots"
        ):
            # disable it, as it creates a lot of history entries
            # self._livestreamjson = self._rdevice.live_streaming_json
            for event in self._rdevice.history(limit=5):
                self._history.append(event)
            self._lastrecording_url = self._rdevice.recording_url(
                self._rdevice.last_recording_id
            )
            if self._lastrecording_url is False:
                self.blocking_login()
            # self._snapshot = self._rdevice.get_snapshot()

    def blocking_login(self):
        def token_updater(token):
            asyncio.run_coroutine_threadsafe(
                self.token_updated(token), self.loop
            ).result()

        if self._token != "":
            self._auth = Auth("MyProject/1.0", self._token, token_updater)
        else:
            if self._password != "":
                self._auth = Auth("MyProject/1.0", None, token_updater)
                if self._2facode:
                    self._auth.fetch_token(
                        self._username, self._password, self._2facode
                    )
                else:
                    try:
                        self._auth.fetch_token(self._username, self._password)
                    except AccessDeniedError:
                        return "AccessDenied: wrong username or password"
                    except MissingTokenError:
                        return "please set 2fa_code"
            else:
                return "please set password"
        self._ring = Ring(self._auth)

    async def set_volume(self, hash, params):
        new_vol = params["volume"]
        self.create_async_task(self.set_volume_task(new_vol))

    async def set_volume_task(self, new_volume):
        await utils.run_blocking(
            functools.partial(self.set_volume_blocking, new_volume)
        )
        await self.update_readings()

    def set_volume_blocking(self, new_volume):
        self._rdevice.volume = new_volume

    async def set_password(self, hash, params):
        self._password = params["password"]
        encrypted_password = utils.encrypt_string(
            self._password, self._reading_encryption_key
        )
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "password", encrypted_password, 1
        )
        self.create_async_task(self.ring_login())

    async def set_2fa_code(self, hash, params):
        self._2facode = params["2facode"]
        self.create_async_task(self.ring_login())
