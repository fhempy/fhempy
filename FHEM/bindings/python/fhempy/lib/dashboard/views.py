"""Own views of devices which are more than a switch: robot vacuum, car,
wallbox, heat pump and irrigation. Found by the set commands and readings
of the device (never by its name), or chosen on the tablet
(attr device_views).

Pure functions, no FHEM access.
"""

from ..matter_bridge import devices as kinds

VIEWS = ("vacuum", "car", "wallbox", "heatpump", "irrigation")

CAR_FHEMPY_TYPES = (
    "bmw",
    "volvo",
    "kia_hyundai",
    "skoda_api",
    "skodaconnect",
    "seatconnect",
)
WALLBOX_FHEMPY_TYPES = ("zappi",)

# readings of each view: key -> reading names, the first found wins
FACTS = {
    "vacuum": {
        "status": ("activity", "status", "state"),
        "battery": ("batteryPercent", "battery_level", "batteryLevel", "battery"),
        "area": (
            "cleaned_area",
            "cleanedArea",
            "clean_area",
            "cleaningArea",
            "last_clean_area",
        ),
        "duration": ("cleaning_time", "clean_time", "cleanTime", "cleaningTime"),
        "fan": ("fan_speed", "fanSpeed", "suction", "fan_power"),
        "error": ("error", "error_code", "lastError"),
    },
    "car": {
        "soc": (
            "soc",
            "battery_level",
            "batteryLevel",
            "charging_level",
            "stateOfCharge",
        ),
        "fuel": ("fuel_level", "fuelLevel", "fuel"),
        "range": (
            "range",
            "range_estimate",
            "range_km",
            "remaining_range",
            "rangeElectric",
        ),
        "charging": (
            "charging_status",
            "chargingState",
            "charging_hv_status",
            "charging",
        ),
        "power": ("charging_power", "chargingPower", "charge_power"),
        "plugged": ("plugged", "plugin", "charging_cable", "cable_connected"),
        "locked": ("locked", "doors_locked", "door_lock_state", "lockState"),
        "mileage": ("mileage", "odometer"),
        "remaining": ("charging_time_remaining", "chargingTimeRemaining"),
    },
    "wallbox": {
        "status": (
            "operating_status",
            "charging_state",
            "chargingState",
            "car_state",
            "state",
        ),
        "plugged": ("plug_status", "car_connected", "carConnected", "plugged", "car"),
        "power": ("charging_power", "charge_power", "power_ct", "power"),
        "energy": (
            "session_energy",
            "energy_session",
            "charged_energy",
            "energy_today",
        ),
        "mode": ("charge_mode", "chargeMode", "mode"),
    },
    "heatpump": {
        "status": ("operating_mode", "operatingMode", "heatpump_state", "state"),
        "flow": (
            "flow_temperature",
            "flowTemperature",
            "flow_temp",
            "temperature_flow",
            "vorlauf",
            "Vorlauftemperatur",
        ),
        "return": (
            "return_temperature",
            "returnTemperature",
            "return_temp",
            "temperature_return",
            "ruecklauf",
            "Ruecklauftemperatur",
        ),
        "outside": (
            "outside_temperature",
            "outsideTemperature",
            "outdoor_temperature",
            "outside_temp",
            "aussentemperatur",
        ),
        "dhw": (
            "hot_water_temperature",
            "hotWaterTemperature",
            "dhw_temperature",
            "dhw_temp",
            "warmwasser",
        ),
        "compressor": (
            "compressor",
            "compressor_state",
            "compressorState",
            "compressor_speed",
            "verdichter",
        ),
        "cop": ("cop", "COP"),
        "power": ("power", "electrical_power", "power_consumption"),
    },
    "irrigation": {
        "moisture": ("soil_moisture", "soilMoisture", "moisture", "bodenfeuchte"),
        "next": ("next_start", "nextStart", "scheduling-next_start"),
        "remaining": ("remaining", "remaining_time", "duration_left"),
    },
}
READINGS = tuple(
    sorted(
        {name for facts in FACTS.values() for names in facts.values() for name in names}
    )
)

# set commands of the actions: action -> set names, the first found wins
ACTIONS = {
    "vacuum": {
        "start": ("start", "clean", "startCleaning", "start_cleaning"),
        "pause": ("pause",),
        "stop": ("stop",),
        "dock": ("dock", "charge", "return_to_base", "returnToBase", "go_home", "home"),
        "locate": ("locate", "find", "findMe", "find_me"),
    },
    "car": {
        "lock": ("lock", "door_lock", "lock_doors"),
        "unlock": ("unlock", "door_unlock", "unlock_doors"),
        "charge_start": ("start_charging", "charge_start", "startCharging"),
        "charge_stop": ("stop_charging", "charge_stop", "stopCharging"),
        "climate_start": (
            "start_climatisation",
            "climate_start",
            "start_climate",
            "climatisation_start",
        ),
        "climate_stop": (
            "stop_climatisation",
            "climate_stop",
            "stop_climate",
            "climatisation_stop",
        ),
        "update": ("update", "refresh", "update_data"),
    },
    "wallbox": {
        "charge_start": ("start_charging", "charge_start", "start"),
        "charge_stop": ("stop_charging", "charge_stop", "stop"),
    },
    "heatpump": {
        "dhw_boost": ("dhw_boost", "hot_water_boost", "boost", "warmwasser_einmalig"),
    },
    "irrigation": {},
}
# sets with options the tablet shows as choice: view -> set names
MODE_SETS = {
    "vacuum": ("fan_speed", "fanSpeed", "suction"),
    "wallbox": ("charge_mode", "chargeMode", "mode"),
    "heatpump": ("operating_mode", "operatingMode", "mode", "opmode"),
}

_VACUUM_START = ACTIONS["vacuum"]["start"]
_VACUUM_DOCK = ("dock", "charge", "return_to_base", "returnToBase", "go_home")
_HEATPUMP_GROUPS = ("flow", "return", "compressor", "cop")
TRUE_WORDS = (
    "1",
    "true",
    "on",
    "yes",
    "ja",
    "locked",
    "connected",
    "plugged",
    "charging",
    "active",
    "running",
)
FALSE_WORDS = (
    "0",
    "false",
    "off",
    "no",
    "nein",
    "unlocked",
    "disconnected",
    "unplugged",
    "not_charging",
    "notcharging",
    "not charging",
    "idle",
    "complete",
    "completed",
    "finished",
    "inactive",
    "stopped",
)


def _reading(info, names):
    readings = info.get("readings") or {}
    for name in names:
        if name in readings and str(readings[name]).strip() not in ("", "-", "None"):
            return readings[name]
    return None


def _has(info, names):
    return _reading(info, names) is not None


def _set_options(info, name):
    """options of a set command 'charge_mode:Fast,Eco,Stop', [] without"""
    for entry in str(info.get("sets") or "").split():
        set_name, _, options = entry.partition(":")
        if set_name != name or not options:
            continue
        if options.startswith(("slider", "colorpicker", "textField", "time")):
            return []
        values = options.split(",")
        if values and values[0] in ("noArg", "select", "uzsuSelectRadio", "multiple"):
            values = values[1:]
        return [v for v in values if v and v != "noArg"]
    return []


def detect(info):
    """the view of a device or None. Car and wallbox first: they also know
    'start' or 'charge'."""
    attrs = info.get("attrs") or {}
    generic = str(attrs.get("genericDeviceType") or "").lower()
    if generic in VIEWS:
        return generic
    if generic in ("vacuum", "robot", "vacuumcleaner"):
        return "vacuum"
    facts = FACTS["car"]
    if info.get("FHEMPYTYPE") in CAR_FHEMPY_TYPES or (
        _has(info, facts["mileage"])
        and (
            _has(info, facts["range"])
            or _has(info, facts["soc"])
            or _has(info, facts["fuel"])
        )
    ):
        return "car"
    facts = FACTS["wallbox"]
    if info.get("FHEMPYTYPE") in WALLBOX_FHEMPY_TYPES or (
        _has(info, ("plug_status", "car_connected", "carConnected"))
        and (_has(info, ("charge_mode", "chargeMode")) or _has(info, facts["energy"]))
    ):
        return "wallbox"
    sets = kinds.set_names(info.get("sets"))
    if sets & set(_VACUUM_START) and sets & set(_VACUUM_DOCK):
        return "vacuum"
    found = [g for g in _HEATPUMP_GROUPS if _has(info, FACTS["heatpump"][g])]
    if len(found) >= 2:
        return "heatpump"
    if _has(info, FACTS["irrigation"]["moisture"]) and {"on", "off"} <= sets:
        return "irrigation"
    return None


def _bool(value):
    """True, False or None for readings like charging_status"""
    if value is None:
        return None
    text = str(value).strip().lower().replace("-", "_")
    if text in FALSE_WORDS or text.startswith(("not_", "no_", "un")):
        return False
    if text in TRUE_WORDS or text.startswith("charging"):
        return True
    return None


def _number(value):
    return kinds.number(value) if value is not None else None


def state(view, info):
    """values of the view for the tablet, keys see FACTS"""
    result = {}
    for key, names in FACTS[view].items():
        value = _reading(info, names)
        if value is None:
            continue
        if key == "compressor" and _bool(value) is None and _number(value) is not None:
            # speed in %
            result["compressor_pct"] = _number(value)
            result[key] = result["compressor_pct"] > 0
            continue
        if (
            key in ("charging", "plugged", "locked", "compressor")
            and _bool(value) is not None
        ):
            result[key] = _bool(value)
            continue
        if key in ("status", "mode", "next", "error", "fan", "charging", "plugged"):
            text = str(value).strip()
            if key == "error" and text.lower() in ("0", "none", "no error", "ok", "-"):
                continue
            result[key] = text[:60]
            continue
        number = _number(value)
        if number is not None:
            result[key] = number
    if view == "car" and result.get("charging") is None and result.get("power"):
        result["charging"] = result["power"] > 0
    power = result.get("power")
    if power and abs(power) < 30 and power != int(power):
        # kW without unit, like watts() of the energy
        result["power"] = power * 1000
    if view == "irrigation":
        result["on"] = bool(kinds.state("switch", info).get("on"))
    return result


def features(view, info):
    """actions and choices a tablet offers for the device"""
    sets = kinds.set_names(info.get("sets"))
    actions = [
        action
        for action, names in ACTIONS[view].items()
        if any(name in sets for name in names)
    ]
    result = {"view": view, "actions": actions}
    for name in MODE_SETS.get(view, ()):
        options = _set_options(info, name)
        if options:
            result["modes"] = options
            break
    return result


def command(view, info, action, value=None):
    """FHEM set arguments of an action, only set commands the device has"""
    sets = kinds.set_names(info.get("sets"))
    if view == "irrigation" and action in ("on", "off", "toggle"):
        if action == "toggle":
            action = "off" if state(view, info).get("on") else "on"
        return kinds.fhem_commands("switch", info, {"on": action == "on"})
    if action == "mode":
        for name in MODE_SETS.get(view, ()):
            options = _set_options(info, name)
            if options:
                if str(value) in options:
                    return [f"{name} {value}"]
                return []
        return []
    for name in ACTIONS.get(view, {}).get(action, ()):
        if name in sets:
            return [name]
    return []


def parse_views(text):
    """attr device_views 'Robby:vacuum,Garden:irrigation,Plug:none'
    -> {device: view or 'none'}"""
    result = {}
    for part in str(text or "").split(","):
        name, _, view = part.strip().partition(":")
        if name and (view in VIEWS or view == "none"):
            result[name] = view
    return result


def format_views(views):
    return ",".join(f"{name}:{view}" for name, view in sorted(views.items()))
