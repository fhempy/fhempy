import asyncio
import functools
import html
import json

import hyundai_kia_connect_api as api

from .. import fhem, generic, utils
from . import pleos

PLEOS_INTERVAL = 15
PLEOS_RETRY = (60, 1800)
PLEOS_RATE_LIMIT_WAIT = 3600
PLAYGROUND_URL = "https://pleos.ai/playground"
GUIDE_URL = (
    "https://document.pleos.ai/en/api-reference/vehicle-data-api/getting-started/"
    "for-private-users/request-my-vehicle-api-key"
)
USAGE = (
    "Usage: define my_car fhempy kia_hyundai (official Pleos API, Europe) or "
    "define my_car fhempy kia_hyundai USERNAME PASSWORD PIN CAR_BRAND REGION_CODE"
)
# set commands which need the car data of the first successful update
CAR_COMMANDS = (
    "lock",
    "unlock",
    "start_climate",
    "stop_climate",
    "start_charge",
    "stop_charge",
    "charge_limits",
)


class kia_hyundai(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self.pleos = None
        self._pleos_task = None
        self._pleos_status = ""
        self._wakeup = asyncio.Event()
        self._unique_id = None
        self.vm = None
        self.vehicle = None

    @staticmethod
    def validate_define(args, argsh):
        if len(args) not in (3, 8):
            return USAGE
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        error = self.validate_define(args, argsh)
        if error:
            return error
        self.hash = hash
        await self.set_icon("car")
        if len(args) == 3:
            return await self.define_pleos()

        attr_config = {
            "update_interval": {
                "default": 30,
                "format": "int",
                "help": "Change interval in minutes, default is 30.",
            }
        }
        await self.set_attr_config(attr_config)

        set_config = {
            "lock": {},
            "unlock": {},
            "start_climate": {
                "args": ["set_temp", "duration", "defrost", "climate", "heating"],
                "help": "Params: Temperature Duration Defrost(on/off) Climate(on/off) Heating(on/off)",
                "params": {
                    "set_temp": {"default": 21, "format": "int"},
                    "duration": {"default": 5, "format": "int"},
                    "defrost": {"default": False, "format": "bool"},
                    "climate": {"default": True, "format": "bool"},
                    "heating": {"default": False, "format": "bool"},
                },
            },
            "stop_climate": {},
            "start_charge": {},
            "stop_charge": {},
            "charge_limits": {
                "args": ["ac_limit", "dc_limit"],
                "help": "Params AC Limit DC Limit",
                "params": {
                    "ac_limit": {"default": 90, "format": "int"},
                    "dc_limit": {"default": 90, "format": "int"},
                },
            },
            "update_data": {},
            "force_update": {
                "help": "Request current data from the car (wakes up the car, "
                + "use rarely due to rate limits)",
            },
        }
        await self.set_set_config(set_config)

        self.username = args[3]
        self.password = args[4]
        self.pin = args[5]
        brands = [
            k for k, v in api.const.BRANDS.items() if v.lower() == args[6].lower()
        ]
        if len(brands) == 0:
            return "Unknown CAR_BRAND, use one of: " + ", ".join(
                api.const.BRANDS.values()
            )
        self.car_brand = brands[0]
        if args[7].lower() == "eu":
            args[7] = "Europe"
        regions = [
            k for k, v in api.const.REGIONS.items() if v.lower() == args[7].lower()
        ]
        if len(regions) == 0:
            return "Unknown REGION_CODE, use one of: " + ", ".join(
                api.const.REGIONS.values()
            )
        self.region_code = regions[0]
        self.create_async_task(self.connect_to_car())

    async def connect_to_car(self):
        self.vm = api.VehicleManager(
            self.region_code,
            self.car_brand,
            self.username,
            self.password,
            self.pin,
            geocode_api_enable=False,
            geocode_api_use_email=False,
        )
        while True:
            try:
                await utils.run_blocking(
                    functools.partial(self.vm.check_and_refresh_token)
                )
                self.create_async_task(self.update_loop())
                self._errors.success(key="login")
                break
            except Exception:
                self._errors.failed(
                    "Failed to login to server, retry in 120s. In Europe use the "
                    "official Pleos API instead: define my_car fhempy kia_hyundai "
                    "(without parameters)",
                    key="login",
                )
                await asyncio.sleep(120)

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_update_interval * 60)

    async def update_once(self, force=False):
        try:
            await utils.run_blocking(functools.partial(self.vm.check_and_refresh_token))
            if force:
                # request current state from the car instead of the cloud cache
                await utils.run_blocking(
                    functools.partial(
                        self.vm.force_refresh_vehicle_state, self.first_vehicle_id()
                    )
                )
            await utils.run_blocking(
                functools.partial(self.vm.update_all_vehicles_with_cached_state)
            )
            await self.update_readings()
            self._errors.success()
        except Exception:
            self._errors.failed("Failed to update car data")
            await fhem.readingsSingleUpdate(self.hash, "state", "error", 1)

    def first_vehicle_id(self):
        # use only first vehicle
        return next(iter(self.vm.vehicles))

    async def update_readings(self):
        self.vehicle = self.vm.vehicles[self.first_vehicle_id()]
        flat_json = utils.flatten_json(self.vehicle.data)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in flat_json:
                await fhem.readingsBulkUpdate(self.hash, name, flat_json[name])
            await fhem.readingsBulkUpdate(
                self.hash, "geolocation", self.vehicle.geocode[0]
            )
            await fhem.readingsBulkUpdate(self.hash, "state", "online")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        if len(args) > 1 and args[1] in CAR_COMMANDS and self.vehicle is None:
            return (
                "Not connected to the car yet, please wait until the car data "
                "was loaded (reading state is online)"
            )
        return await super().Set(hash, args, argsh)

    # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)
    async def set_update_data(self, hash, params):
        if self.pleos:
            self._wakeup.set()
            return
        self.create_async_task(self.update_once())

    async def set_force_update(self, hash, params):
        self.create_async_task(self.update_once(force=True))

    async def set_lock(self, hash, params):
        self.create_async_task(self.execute_command(self.vm.lock, self.vehicle.id))

    async def set_unlock(self, hash, params):
        self.create_async_task(self.execute_command(self.vm.unlock, self.vehicle.id))

    async def set_start_climate(self, hash, params):
        self.create_async_task(
            self.execute_command(
                self.vm.start_climate,
                self.vehicle.id,
                api.ClimateRequestOptions(
                    set_temp=params["set_temp"],
                    duration=params["duration"],
                    defrost=params["defrost"],
                    climate=params["climate"],
                    heating=int(params["heating"]),
                ),
            )
        )

    async def set_stop_climate(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.stop_climate, self.vehicle.id)
        )

    async def set_start_charge(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.start_charge, self.vehicle.id)
        )

    async def set_stop_charge(self, hash, params):
        self.create_async_task(
            self.execute_command(self.vm.stop_charge, self.vehicle.id)
        )

    async def set_charge_limits(self, hash, params):
        self.create_async_task(
            self.execute_command(
                self.vm.set_charge_limits,
                self.vehicle.id,
                params["ac_limit"],
                params["dc_limit"],
            )
        )

    async def execute_command(self, command, *kwargs):
        try:
            # check token
            await utils.run_blocking(functools.partial(self.vm.check_and_refresh_token))

            # execute function
            await utils.run_blocking(functools.partial(command, *kwargs))
        except Exception as exc:
            # runs in background, FHEM already got the reply of the set
            self.logger.error(
                f"Command {getattr(command, '__name__', command)} failed: "
                + utils.describe_exception(exc)
            )
            await fhem.readingsSingleUpdate(
                self.hash, "last_command_error", utils.describe_exception(exc), 1
            )

    # --- Pleos Vehicle Data API (EU Data Act) ---

    async def define_pleos(self):
        attr_config = {
            "update_interval": {
                "default": PLEOS_INTERVAL,
                "format": "int",
                "help": "Minutes between two requests to the Pleos server, "
                f"default {PLEOS_INTERVAL}. The car sends its values to the "
                "server on its own (e.g. after driving or while charging), "
                "the request never wakes up the car.",
            },
            "vin": {
                "default": "",
                "help": "Only needed if there are several cars in your account: "
                "the vehicle identification number of the car to show. Empty: "
                "the first car.",
            },
        }
        await self.set_attr_config(attr_config)
        await self.set_set_config(
            {
                "credentials": {
                    "args": ["client_id", "client_secret"],
                    "help": "Client ID and client secret of your personal Pleos "
                    "API key, see the instructions on the detail page.",
                },
                "update_data": {
                    "help": "Get the latest values from the Pleos server now."
                },
            }
        )
        name = self.hash["NAME"]
        self._unique_id = await fhem.getUniqueId(self.hash)
        self.pleos = pleos.PleosApi(
            await fhem.ReadingsVal(name, ".client_id", ""),
            await self._read_secret(".client_secret"),
            await fhem.ReadingsVal(name, "brand", ""),
        )
        if self._pleos_task:
            self.cancel_async_task(self._pleos_task)
        self._pleos_task = self.create_async_task(self._pleos_run())
        return None

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.setup_html() + str(detail)

    async def _read_secret(self, reading):
        value = await fhem.ReadingsVal(self.hash["NAME"], reading, "")
        if not value:
            return ""
        try:
            return utils.decrypt_string(value, self._unique_id)
        except Exception:
            self.logger.warning(f"Failed to decrypt {reading}, please set it again")
            return ""

    async def set_credentials(self, hash, params):
        client_id = params["client_id"].strip()
        client_secret = params["client_secret"].strip()
        if not client_id or not client_secret:
            return "Please enter client ID and client secret"
        self.pleos.client_id = client_id
        self.pleos.client_secret = client_secret
        self.pleos.brand = ""
        self.pleos.logout()
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, ".client_id", client_id)
        await fhem.readingsBulkUpdate(
            self.hash,
            ".client_secret",
            utils.encrypt_string(client_secret, self._unique_id),
        )
        await fhem.readingsEndUpdate(self.hash, 0)
        await self._pleos_state("connecting")
        self._wakeup.set()
        return None

    async def set_attr_vin(self, hash):
        if self.pleos:
            self._wakeup.set()

    async def set_attr_update_interval(self, hash):
        if self.pleos:
            self._wakeup.set()

    async def _pleos_state(self, state):
        self._pleos_status = state
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    async def _sleep(self, seconds):
        try:
            await asyncio.wait_for(self._wakeup.wait(), max(seconds, 0))
        except TimeoutError:
            pass

    async def _pleos_run(self):
        retry = PLEOS_RETRY[0]
        while True:
            self._wakeup.clear()
            wait = max(self._attr_update_interval, 1) * 60
            if not self.pleos.client_id or not self.pleos.client_secret:
                await self._pleos_state("credentials missing")
                wait = None
            else:
                try:
                    await self._pleos_update()
                    self._errors.success()
                    retry = PLEOS_RETRY[0]
                except pleos.LoginFailed as exc:
                    self.logger.warning(f"Pleos login failed: {exc}")
                    await self._pleos_state(f"login failed: {exc}"[:200])
                    wait = None
                except pleos.RateLimited:
                    self.logger.warning("Pleos rate limit reached, waiting 1 hour")
                    await self._pleos_state("rate limit reached")
                    wait = PLEOS_RATE_LIMIT_WAIT
                except Exception as exc:
                    self._errors.failed("Pleos request failed")
                    await self._pleos_state(f"error: {exc}"[:200])
                    wait = retry
                    retry = min(retry * 2, PLEOS_RETRY[1])
            # without valid credentials wait until they are set
            await self._sleep(365 * 24 * 3600 if wait is None else wait)

    async def _pleos_update(self):
        vehicles = await self.pleos.vehicles()
        if not vehicles:
            raise pleos.NoData(
                "no car in the API key, create a new key after adding the car "
                "to your app account"
            )
        wanted = self._attr_vin.strip().upper()
        vehicle = vehicles[0]
        if wanted:
            matching = [v for v in vehicles if v["vin"].upper() == wanted]
            if not matching:
                raise pleos.NoData(
                    f"VIN {wanted} not found, known: "
                    + ", ".join(v["vin"] for v in vehicles)
                )
            vehicle = matching[0]
        vin = vehicle["vin"]
        self.hash["VIN"] = vin
        data = await self.pleos.vehicle_data(vin)
        await self._pleos_readings(vehicle, vehicles, data)

    async def _pleos_readings(self, vehicle, vehicles, data):
        readings = {
            "brand": self.pleos.brand,
            "vin": vehicle["vin"],
            "model": vehicle.get("sellname") or vehicle.get("name") or "",
            "nickname": vehicle.get("nickname") or "",
            "vehicles": ",".join(v["vin"] for v in vehicles),
        }
        for endpoint, values in data.items():
            prefix = pleos.ENDPOINTS[endpoint]
            for key, value in utils.flatten_json(values or {}).items():
                readings[f"{prefix}_{key}"] = value
        readings.update(pleos_summary(data))
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name, value in readings.items():
                if value is None:
                    value = ""
                elif isinstance(value, bool):
                    value = "on" if value else "off"
                await fhem.readingsBulkUpdateIfChanged(self.hash, name, value)
            state = " ".join(
                f"{readings[key]}{unit}"
                for key, unit in (("soc", "%"), ("range", " km"))
                if key in readings
            )
            self._pleos_status = state or "online"
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", self._pleos_status
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    def setup_html(self):
        if not self.pleos or not hasattr(self, "hash"):
            return ""
        if self.pleos.client_id and not self._pleos_status.startswith("login failed"):
            return ""
        name = self.hash["NAME"]
        cmd = json.dumps(f"set {name} credentials ")
        error = ""
        if self.pleos.client_id:
            error = (
                f"<b style='color:#c00'>{html.escape(self._pleos_status)}</b>"
                "<br><br>"
            )
        body = (
            error + "<b>Connect your Kia, Hyundai or Genesis (Europe)</b><br><br>"
            f'1. Open the <a href="{PLAYGROUND_URL}" target="_blank">Pleos '
            "Playground</a> and create a free account (sign up).<br>"
            "2. Click on your account icon and open <b>My Vehicle Data API</b>"
            ".<br>"
            "3. Choose the tab of your brand (Kia, Hyundai or Genesis), accept "
            "the terms, click <b>Get API Key</b> and log in with your Kia "
            "Connect / Bluelink / Genesis Connected account (the account of the "
            "main user of the car).<br>"
            "4. Copy the client ID and the client secret and paste them here:"
            "<br><br>"
            '<input type="text" id="pleosClientId" size="40" '
            'placeholder="Client ID"><br>'
            '<input type="password" id="pleosClientSecret" size="40" '
            'placeholder="Client Secret"> '
            "<button onclick=\"var i=document.getElementById('pleosClientId')"
            ".value.trim(),s=document.getElementById('pleosClientSecret')"
            ".value.trim();if(i&&s)FW_cmd(FW_root+'?cmd='+encodeURIComponent("
            f"{html.escape(cmd)}+i+' '+s)+'&amp;XHR=1',function(){{"
            'setTimeout(function(){location.reload()},3000)})">Save</button>'
            "<br><br>The key contains only the cars which are in your account "
            "when you create it. For a new car delete the key and create a new "
            f'one. <a href="{GUIDE_URL}" target="_blank">Pleos instructions</a>'
        )
        return (
            '<div class="makeTable wide"><span class="mkTitle">Pleos Vehicle '
            'Data API</span><table class="block wide"><tr class="odd"><td>'
            f"{body}</td></tr></table></div>"
        )


def _km(value, unit):
    factor = {
        "": 1,
        "km": 1,
        "mile": 1.609344,
        "miles": 1.609344,
        "mi": 1.609344,
        "meter": 0.001,
        "m": 0.001,
        "feet": 0.0003048,
    }.get(str(unit or "").lower())
    try:
        return round(float(value) * factor)
    except (TypeError, ValueError):
        return None


def pleos_summary(data):
    """Short readings for the most important values."""
    out = {}
    charge = (data.get("batteries") or {}).get("charge") or {}
    if charge:
        out["soc"] = charge.get("stateOfCharge")
        out["charging"] = charge.get("charging")
        out["charging_status"] = charge.get("status")
        out["plugged"] = charge.get("plugin")
        out["charging_time_remaining"] = charge.get("remainTime")
        target = charge.get("targetStateOfCharge") or {}
        out["charge_limit_ac"] = target.get("standard")
        out["charge_limit_dc"] = target.get("quick")
    if (data.get("batteries") or {}).get("timestamp"):
        out["last_update"] = data["batteries"]["timestamp"]
    for entry in (data.get("powertrains") or {}).get("distanceToEmpties") or []:
        km = _km(entry.get("value"), entry.get("unit"))
        if km is None:
            continue
        kind = str(entry.get("type", "")).lower()
        out["range" if kind == "ev" else f"range_{kind}"] = km
    odometer = (data.get("driving") or {}).get("odometer") or {}
    if odometer:
        out["odometer"] = _km(odometer.get("value"), odometer.get("unit"))
    location = (data.get("locations") or {}).get("location") or {}
    if location:
        out["latitude"] = location.get("latitude")
        out["longitude"] = location.get("longitude")
    climate = (data.get("status") or {}).get("climateControl") or {}
    if climate:
        out["climate"] = climate.get("status")
    return {k: v for k, v in out.items() if v is not None}
