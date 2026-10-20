import asyncio
import functools
import html
import json
import ssl
import time

from .. import fhem, generic, utils
from . import cardata

DEFAULT_INTERVAL = 2400
MIN_INTERVAL = 900
# BMW allows 50 API requests per 24 hours, keep some for set update
QUOTA_POLL = 44
QUOTA_TOTAL = 50
DAY = 24 * 60 * 60
# refresh the tokens this many seconds before they expire
REFRESH_BEFORE = 15 * 60
ERROR_RETRY = (60, 900)
STREAM_RETRY = (5, 300)
LOGIN_TIMEOUT = 600
PORTAL_URL = "https://www.bmw.de/de-de/mybmw/vehicle-overview"
MINI_PORTAL_URL = "https://www.mini.de/de-de/mymini/vehicle-overview"


class bmw(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self._wakeup = asyncio.Event()
        self._loop_task = None
        self._stream_task = None
        self._unique_id = None
        self.api = cardata.CarDataApi("")
        self.api.on_request = self._count_request
        self._api_calls = []
        self._vehicles = []
        self._vin = ""
        self._container_id = ""
        self._basic_loaded = False
        self._last_poll = 0
        self._last_stream = 0
        self._last_refresh = 0
        self._poll_now = False
        self._login_now = False
        self._login_info = None
        self._values = {}
        self._status = ""

    @staticmethod
    def validate_define(args, argsh):
        if len(args) > 4:
            return "Usage: define my_bmw fhempy bmw [client_id]"
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        error = self.validate_define(args, argsh)
        if error:
            return error
        self.hash = hash

        attr_config = {
            "interval": {
                "default": DEFAULT_INTERVAL,
                "format": "int",
                "help": "Seconds between two requests of all values from the "
                f"BMW server, default {DEFAULT_INTERVAL}, minimum {MIN_INTERVAL}. "
                "BMW allows only 50 requests per day. Live values from the "
                "car (stream) arrive anyway, no request is made while they do.",
            },
            "vin": {
                "default": "",
                "help": "Only needed if there are several cars in your BMW "
                "account: the vehicle identification number of the car to "
                "show. Empty: the first car.",
            },
        }
        await self.set_attr_config(attr_config)
        await self._update_set_config()
        await self.set_icon("car")

        name = hash["NAME"]
        self._unique_id = await fhem.getUniqueId(hash)
        client_id = args[3] if len(args) > 3 else ""
        stored_client_id = await fhem.ReadingsVal(name, ".client_id", "")
        self.api.client_id = client_id or stored_client_id
        if client_id and client_id != stored_client_id:
            await self._save_client_id(client_id)
        else:
            self.api.refresh_token = await self._read_secret(".refresh_token")
            self.api.gcid = await fhem.ReadingsVal(name, ".gcid", "")
            self._container_id = await fhem.ReadingsVal(name, ".container_id", "")
            # known car and model cost no API request after a restart
            vin = await fhem.ReadingsVal(name, "vin", "")
            if vin and self._attr_vin.strip().upper() in ("", vin):
                self._vin = vin
                self.hash["VIN"] = vin
                model = await fhem.ReadingsVal(name, "model", "")
                self._basic_loaded = bool(model)
                if model:
                    self.hash["MODEL"] = model
        calls = await fhem.ReadingsVal(name, ".api_calls", "")
        self._api_calls = [float(c) for c in calls.split(",") if c]

        if self._loop_task:
            self.cancel_async_task(self._loop_task)
        self._loop_task = self.create_async_task(self._run())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._stop_stream()
        await super().Undefine(hash)

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.setup_html() + str(detail)

    async def _update_set_config(self):
        set_config = {
            "client_id": {
                "args": ["client_id"],
                "help": "Your BMW CarData client ID, see the instructions on the "
                "detail page. FHEM shows a link for the BMW login afterwards.",
            },
        }
        if self.api.client_id:
            set_config["login"] = {
                "help": "Log in at BMW again, e.g. after the login expired."
            }
        if self.api.refresh_token:
            set_config["update"] = {
                "help": "Request all values from the BMW server now. BMW allows "
                "50 requests per day."
            }
        await self.set_set_config(set_config)

    async def set_client_id(self, hash, params):
        client_id = params["client_id"].strip()
        if not client_id:
            return "Please enter the client ID"
        await self._save_client_id(client_id)
        self._login_now = True
        self._wakeup.set()
        return None

    async def set_login(self, hash, params):
        self._login_now = True
        self._wakeup.set()

    async def set_update(self, hash, params):
        self._poll_now = True
        self._wakeup.set()

    async def set_attr_interval(self, hash):
        self._wakeup.set()

    async def set_attr_vin(self, hash):
        if self._attr_vin != self._vin and self.api.refresh_token:
            self._vin = ""
            self._basic_loaded = False
            self._last_poll = 0
            self._values = {}
            self._stop_stream()
            self._wakeup.set()

    # --- stored values ---

    async def _read_secret(self, reading):
        value = await fhem.ReadingsVal(self.hash["NAME"], reading, "")
        if not value:
            return ""
        try:
            return utils.decrypt_string(value, self._unique_id)
        except Exception:
            self.logger.warning(f"Failed to decrypt {reading}, please log in again")
            return ""

    async def _save_client_id(self, client_id):
        self.api.client_id = client_id
        self.api.refresh_token = ""
        self.api.gcid = ""
        self._container_id = ""
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, ".client_id", client_id)
        await fhem.readingsBulkUpdate(self.hash, ".refresh_token", "")
        await fhem.readingsBulkUpdate(self.hash, ".container_id", "")
        await fhem.readingsEndUpdate(self.hash, 0)
        await self._update_set_config()

    async def _save_tokens(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(
            self.hash,
            ".refresh_token",
            utils.encrypt_string(self.api.refresh_token, self._unique_id),
        )
        await fhem.readingsBulkUpdate(self.hash, ".gcid", self.api.gcid)
        await fhem.readingsEndUpdate(self.hash, 0)

    def _count_request(self):
        now = time.time()
        self._api_calls = [t for t in self._api_calls if now - t < DAY] + [now]
        self.create_async_task(self._save_api_calls())

    def _requests_24h(self):
        now = time.time()
        return len([t for t in self._api_calls if now - t < DAY])

    async def _save_api_calls(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(
            self.hash, ".api_calls", ",".join(f"{t:.0f}" for t in self._api_calls)
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "api_requests_24h", self._requests_24h()
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def _state(self, state):
        self._status = state
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    # --- main loop ---

    async def _sleep(self, seconds):
        try:
            await asyncio.wait_for(self._wakeup.wait(), max(seconds, 0))
        except TimeoutError:
            pass
        self._wakeup.clear()

    async def _run(self):
        retry = ERROR_RETRY[0]
        while True:
            try:
                wait = await self._step()
                self._errors.success()
                retry = ERROR_RETRY[0]
            except cardata.LoginRequired as exc:
                # show the login link right away, the user only has to click it
                self.logger.warning(f"BMW login expired, please log in again: {exc}")
                await self._logout()
                wait = 0
            except Exception as exc:
                self._errors.failed("BMW CarData request failed")
                await self._state(f"error: {exc}"[:200])
                wait = retry
                retry = min(retry * 2, ERROR_RETRY[1])
            await self._sleep(DAY if wait is None else wait)

    async def _logout(self):
        self._stop_stream()
        self.api.refresh_token = ""
        await fhem.readingsSingleUpdate(self.hash, ".refresh_token", "", 0)
        await self._update_set_config()

    async def _step(self):
        """One round, returns the seconds to wait or None to wait for set."""
        if not self.api.client_id:
            await self._state("set client_id, see detail page")
            return None
        if self._login_now or not self.api.refresh_token:
            self._login_now = False
            if not await self._login():
                return None

        now = time.time()
        if now > self.api.expires_at - REFRESH_BEFORE:
            await self.api.refresh(now)
            self._last_refresh = now
            await self._save_tokens()
            if self._stream_task:
                # the stream password is the id token, reconnect with the new one
                self._stop_stream()

        if not self._vin:
            await self._select_vehicle()
        if not self._basic_loaded:
            await self._load_basic_data()
        if not self._container_id:
            await self._ensure_container()

        if self._stream_task is None or self._stream_task.done():
            self._stream_task = self.create_async_task(self._stream())

        interval = max(self._attr_interval, MIN_INTERVAL)
        now = time.time()
        due = self._last_poll + interval
        stream_quiet = now - self._last_stream >= interval
        if self._poll_now or (now >= due and stream_quiet):
            await self._poll(forced=self._poll_now)
            self._poll_now = False
            due = time.time() + interval
        elif not stream_quiet:
            due = max(due, self._last_stream + interval)
        refresh_at = self.api.expires_at - REFRESH_BEFORE
        return min(due, refresh_at) - time.time()

    async def _login(self):
        verifier, challenge = cardata.new_pkce()
        try:
            code = await self.api.request_device_code(challenge)
        except cardata.CarDataError as exc:
            await self._state(
                f"login failed, check the client ID and its scopes: {exc}"[:200]
            )
            return False
        url = code.get("verification_uri_complete") or code.get("verification_uri")
        user_code = code.get("user_code", "")
        self._login_info = (url, user_code)
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, "login_url", url)
        await fhem.readingsBulkUpdate(self.hash, "login_code", user_code)
        await fhem.readingsEndUpdate(self.hash, 1)
        await self._state(f"open {url} and log in, code {user_code}")

        interval = float(code.get("interval", 5))
        deadline = time.time() + int(code.get("expires_in") or LOGIN_TIMEOUT)
        logged_in = False
        try:
            while time.time() < deadline:
                await asyncio.sleep(interval)
                try:
                    logged_in = await self.api.poll_token(code["device_code"], verifier)
                except cardata.CarDataError as exc:
                    await self._state(f"login failed: {exc}"[:200])
                    return False
                if logged_in:
                    break
        finally:
            self._login_info = None
            for reading in ("login_url", "login_code"):
                await fhem.CommandDeleteReading(
                    self.hash, f"{self.hash['NAME']} {reading}"
                )
        if not logged_in:
            await self._state("login timed out, use set login")
            return False
        self.logger.info("Logged in at BMW CarData")
        await self._save_tokens()
        await self._update_set_config()
        self._vin = ""
        self._basic_loaded = False
        self._last_poll = 0
        await self._state("logged in")
        return True

    async def _call(self, function, *args):
        """API request, refreshes the token once if BMW rejects it."""
        if self._requests_24h() >= QUOTA_TOTAL:
            raise cardata.CarDataError(
                "BMW allows only 50 requests per day, waiting for the next one"
            )
        try:
            return await function(*args)
        except cardata.CarDataError as exc:
            if exc.status != 401:
                raise
        await self.api.refresh(time.time())
        await self._save_tokens()
        return await function(*args)

    async def _select_vehicle(self):
        self._vehicles = await self._call(self.api.vehicles)
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "vehicles", ",".join(self._vehicles) or "none", 1
        )
        wanted = self._attr_vin.strip().upper()
        if wanted and wanted not in self._vehicles:
            await self._state(f"vin {wanted} not found in your BMW account")
            raise cardata.CarDataError(f"VIN {wanted} not in {self._vehicles}")
        if not self._vehicles:
            raise cardata.CarDataError(
                "No car in your BMW account, add it in the My BMW app first"
            )
        self._vin = wanted or self._vehicles[0]
        self.hash["VIN"] = self._vin
        await fhem.readingsSingleUpdateIfChanged(self.hash, "vin", self._vin, 1)

    async def _load_basic_data(self):
        data = await self._call(self.api.basic_data, self._vin)
        self._basic_loaded = True
        fields = {
            "model": data.get("modelName"),
            "brand": data.get("brand"),
            "drivetrain": data.get("driveTrain"),
            "color": data.get("colourDescription"),
            "construction_date": str(data.get("constructionDate") or "")[:10],
            "series": data.get("seriesDevt"),
        }
        await fhem.readingsBeginUpdate(self.hash)
        for reading, value in fields.items():
            if value:
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
        await fhem.readingsEndUpdate(self.hash, 1)
        if data.get("modelName"):
            self.hash["MODEL"] = data["modelName"]

    async def _ensure_container(self):
        container_id = await self._call(self.api.find_container)
        if not container_id:
            try:
                container_id = await self._call(
                    self.api.create_container, list(cardata.READINGS)
                )
            except cardata.CarDataError as exc:
                if exc.status != 400:
                    raise
                self.logger.warning(
                    f"BMW rejected the data list, using the battery values only: {exc}"
                )
                container_id = await self._call(
                    self.api.create_container, cardata.BASIC_DESCRIPTORS
                )
        self._container_id = container_id
        await fhem.readingsSingleUpdate(self.hash, ".container_id", container_id, 0)

    async def _poll(self, forced=False):
        limit = QUOTA_TOTAL if forced else QUOTA_POLL
        if self._requests_24h() >= limit:
            self.logger.info(
                "BMW allows only 50 requests per day, waiting before the next one"
            )
            self._last_poll = time.time()
            return
        self._last_poll = time.time()
        try:
            data = await self._call(
                self.api.telematic_data, self._vin, self._container_id
            )
        except cardata.CarDataError as exc:
            if exc.status in (400, 404):
                # container deleted in the BMW portal, create it again next round
                self._container_id = ""
                self._last_poll = 0
            raise
        await self._update_values(data)

    # --- stream ---

    def _stop_stream(self):
        if self._stream_task:
            self.cancel_async_task(self._stream_task)
            self._stream_task = None

    async def _stream(self):
        import aiomqtt

        retry = STREAM_RETRY[0]
        tls_context = await utils.run_blocking(
            functools.partial(ssl.create_default_context)
        )
        while True:
            try:
                async with aiomqtt.Client(
                    cardata.STREAM_HOST,
                    cardata.STREAM_PORT,
                    username=self.api.gcid,
                    password=self.api.id_token,
                    client_id=self.api.gcid,
                    tls_context=tls_context,
                    keepalive=30,
                    logger=self.logger,
                ) as client:
                    async with client.messages() as messages:
                        await client.subscribe(f"{self.api.gcid}/{self._vin}")
                        self._errors.success("stream")
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "stream", "connected", 1
                        )
                        retry = STREAM_RETRY[0]
                        async for message in messages:
                            await self._on_stream_message(message.payload)
            except (aiomqtt.MqttError, OSError) as exc:
                self._errors.failed(
                    "BMW CarData stream disconnected, reconnecting",
                    key="stream",
                    exc=ConnectionError(str(exc)),
                )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "stream", "disconnected", 1
                )
                refused = any(t in str(exc).lower() for t in ("authori", "password"))
                if refused and time.time() - self._last_refresh > MIN_INTERVAL:
                    # token expired, refresh it before the next connect
                    self.api.expires_at = 0
                    self._wakeup.set()
                    return
            await asyncio.sleep(retry)
            retry = min(retry * 2, STREAM_RETRY[1])

    async def _on_stream_message(self, payload):
        try:
            message = json.loads(payload)
        except (TypeError, ValueError):
            self.logger.debug(f"Ignore invalid stream message {payload!r}")
            return
        if not isinstance(message, dict):
            return
        if message.get("vin") and message["vin"] != self._vin:
            return
        self._last_stream = time.time()
        await self._update_values(message.get("data") or {})

    async def _update_values(self, data):
        readings, newest = cardata.readings_from_data(data)
        if not readings:
            return
        self._values.update(readings)
        await fhem.readingsBeginUpdate(self.hash)
        for name, value in readings.items():
            await fhem.readingsBulkUpdateIfChanged(self.hash, name, value)
        if newest:
            local = newest.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            await fhem.readingsBulkUpdateIfChanged(self.hash, "last_update", local)
        await fhem.readingsEndUpdate(self.hash, 1)
        await self._state(self._state_text())

    def _state_text(self):
        parts = []
        soc = self._values.get("soc")
        range_km = self._values.get("range") or self._values.get("range_estimate")
        if soc is not None:
            parts.append(f"{soc}%")
        if range_km is not None:
            parts.append(f"{range_km} km")
        if not parts:
            mileage = self._values.get("mileage")
            parts.append(f"{mileage} km total" if mileage else "connected")
        return " ".join(parts)

    # --- FHEMWEB ---

    def setup_html(self):
        if not hasattr(self, "hash"):
            return ""
        name = self.hash["NAME"]
        if self._login_info:
            url, code = self._login_info
            body = (
                "<b>Log in at BMW</b><br><br>"
                f'1. Open <a href="{html.escape(url)}" target="_blank">'
                f"<b>{html.escape(url)}</b></a><br>"
                f"2. Log in with your My BMW account, the code is "
                f'<b style="font-size:150%">{html.escape(code)}</b><br>'
                "3. Confirm the access. FHEM shows the data of your car a few "
                "seconds later (refresh this page)."
            )
        elif not self.api.client_id or self._status.startswith("login failed"):
            cmd = json.dumps(f"set {name} client_id ")
            error = ""
            if self.api.client_id:
                error = f"<b style='color:#c00'>{html.escape(self._status)}</b><br><br>"
            body = (
                error + "<b>Connect your BMW (or MINI) in 3 minutes</b><br><br>"
                f'1. Open <a href="{PORTAL_URL}" target="_blank">My BMW</a> '
                f'(MINI: <a href="{MINI_PORTAL_URL}" target="_blank">My MINI</a>)'
                ", log in and select your car.<br>"
                "2. Click the tile <b>BMW CarData</b> and then <b>CarData Client "
                "erstellen</b> (Create CarData Client).<br>"
                "3. Switch on both <b>Zugriff auf CarData API anfragen</b> and "
                "<b>CarData Stream</b>. If the page shows an error, reload it "
                "and switch them on one after the other.<br>"
                "4. Copy the client ID and paste it here:<br><br>"
                '<input type="text" id="bmwClientId" size="40" '
                'placeholder="e.g. 1a2b3c4d-...">'
                "<button onclick=\"var v=document.getElementById('bmwClientId')"
                ".value.trim();if(v)FW_cmd(FW_root+'?cmd='+encodeURIComponent("
                f"{html.escape(cmd)}+v)+'&amp;XHR=1',function(){{"
                'setTimeout(function(){location.reload()},2000)})">Save</button>'
                "<br><br>FHEM shows a link for the BMW login afterwards."
            )
        elif self.api.refresh_token and not self._last_stream:
            body = (
                "<b>Live values</b> (optional): no live values from the car "
                "arrived since FHEM started. Without them FHEM requests the "
                f"values every {max(self._attr_interval, MIN_INTERVAL) // 60} "
                "minutes. For live values open the "
                f'<a href="{PORTAL_URL}" target="_blank">BMW CarData</a> page '
                "of your car, click <b>Datenauswahl ändern</b> (change data "
                "selection) under <b>CarData Stream</b>, tick the values you "
                "want (e.g. everything under Elektrofahrzeug and Fahrzeugstatus) "
                "and save. Lock or unlock the car in the My BMW app to make it "
                "send its values."
            )
        else:
            return ""
        return (
            '<div class="makeTable wide"><span class="mkTitle">BMW CarData'
            '</span><table class="block wide"><tr class="odd"><td>'
            f"{body}</td></tr></table></div>"
        )
