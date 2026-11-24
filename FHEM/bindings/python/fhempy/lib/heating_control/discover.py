"""Finds the devices for the heating control in the FHEM devices.

Thermostats are found by what they can do (a temperature reading and a
set command for the target temperature), they are used automatically.
Everything else (mixer, pump, flow/return/supply sensors, room
thermometers) is only suggested, the user confirms it on the detail page.
Names are just a hint for the order of the suggestions.
"""

import re

TEMP_READINGS = (
    "measured-temp",
    "measuredTemperature",
    "measured_temperature",
    "local_temperature",
    "localTemperature",
    "actualTemperature",
    "currentTemperature",
    "current_temperature",
    "temperature",
    "temp",
)
TARGET_READINGS = (
    "desired-temp",
    "desiredTemperature",
    "desired_temperature",
    "occupied_heating_setpoint",
    "current_heating_setpoint",
    "setpoint",
    "targetTemperature",
    "target_temperature",
)
VALVE_READINGS = (
    "valveposition",
    "ValvePosition",
    "valve_position",
    "valve",
    "actuator",
    "pi_heating_demand",
    "heating_demand",
)
# health of battery devices, by the readings the FHEM modules use
BATTERY_LOW_FLAGS = (
    "battery_low",
    "batteryLow",
    "lowBattery",
    "low_battery",
    "LowBattery",
)
BATTERY_TEXT = ("battery", "batteryState", "battery_state", "Battery")
BATTERY_PERCENT = (
    "batteryPercent",
    "battery_percent",
    "batteryPercentage",
    "battery_percentage",
    "battery",
    "Battery",
)
BATTERY_LOW_PERCENT = 20
LOW_WORDS = ("low", "empty", "critical", "replace", "warning", "true", "on", "yes", "1")
UNREACHABLE_STATES = (
    "unreachable",
    "offline",
    "dead",
    "disconnected",
    "unavailable",
    "not connected",
    "timeout",
)
WINDOW_READINGS = ("window", "windowOpen", "window_open", "windowopen")
POWER_READINGS = (
    "power",
    "apower",
    "power_0",
    "switch0_apower",
    "switch_0_apower",
    "relay_0_power",
    "relay0_power",
    "energy_power",
    "currentPower",
    "Power",
)
# set commands for a 0-100 % position, in this order
POSITION_SETS = ("pct", "position", "level", "brightness", "dim", "value")
WEATHER_TYPES = ("Weather", "PROPLANTA", "DWD_OpenData", "OPENWEATHER")
WEATHER_FHEMPYTYPES = ("openmeteo_weather", "google_weather")
OWN_TYPES = ("heating_control", "heating_advisor", "dashboard", "matter_bridge")
IGNORED_ROOMS = ("fhempy", "hidden", "unsorted", "everything", "")
FORECAST_READING = re.compile(
    r"^(?:next_hours_(\d+)_temperature|hfc(\d+)_temperature)$"
)
TEMP_NAME = re.compile(r"temp", re.IGNORECASE)
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")

HINTS = {
    "mixer": ("mischer", "mixer", "mischventil", "ventil", "valve", "3wege", "mix"),
    "pump": ("pumpe", "pump", "umwälz", "umwaelz", "circ", "heizkreis"),
    "flow": ("vorlauf", "flow", "vl", "feed"),
    "return": ("rücklauf", "ruecklauf", "return", "rl", "back"),
    "supply": ("zulauf", "kessel", "puffer", "speicher", "boiler", "supply", "heizung"),
    "outdoor": ("aussen", "außen", "outdoor", "outside", "garten", "balkon", "wetter"),
}


def number(value):
    if value is None:
        return None
    match = NUMBER.search(str(value))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "."))
    except ValueError:
        return None


def set_names(info):
    names = set()
    for part in str(info.get("sets") or "").split():
        names.add(part.split(":", 1)[0])
    return names


def first(names, available):
    for name in names:
        if name in available:
            return name
    return None


def room_of(info):
    for room in str(info.get("room") or "").split(","):
        room = room.strip()
        if room.lower() not in IGNORED_ROOMS:
            return room
    return ""


def label(name, info):
    return info.get("alias") or name


def is_weather(info):
    return (
        info.get("TYPE") in WEATHER_TYPES
        or info.get("FHEMPYTYPE") in WEATHER_FHEMPYTYPES
    )


def _words(name, info):
    return f"{name} {info.get('alias', '')}".lower()


def _hint_score(role, name, info):
    words = _words(name, info)
    return sum(2 if len(w) > 3 else 1 for w in HINTS[role] if w in words)


def thermostat_of(name, info):
    """{"temp", "target", "setter", "valve", "window"} or None"""
    readings = info.get("readings") or {}
    sets = set_names(info)
    target = first(TARGET_READINGS, sets)
    if target is None:
        return None
    temp = first(TEMP_READINGS, readings)
    if temp is None or number(readings.get(temp)) is None:
        return None
    return {
        "temp": temp,
        "target": first(TARGET_READINGS, readings) or target,
        "setter": target,
        "valve": first(VALVE_READINGS, readings),
        "window": first(WINDOW_READINGS, readings),
    }


def temperature_readings(info):
    readings = info.get("readings") or {}
    found = []
    for reading, value in readings.items():
        if reading in TARGET_READINGS or FORECAST_READING.match(reading):
            continue
        if not TEMP_NAME.search(reading) or "target" in reading.lower():
            continue
        if "set" in reading.lower() or "desired" in reading.lower():
            continue
        if number(value) is not None:
            found.append(reading)
    return sorted(found, key=lambda r: (r not in TEMP_READINGS, r))


def position_setter(info):
    sets = str(info.get("sets") or "").split()
    for wanted in POSITION_SETS:
        for part in sets:
            name, _, options = part.partition(":")
            if name == wanted and (
                not options or "slider" in options or "," in options
            ):
                return name
    return None


def switchable(info):
    sets = set_names(info)
    return "on" in sets and "off" in sets


def power_reading(info):
    readings = info.get("readings") or {}
    reading = first(POWER_READINGS, readings)
    if reading and number(readings.get(reading)) is not None:
        return reading
    return None


def discover(infos, own_name=""):
    """{"thermostats": {name: {...}}, "rooms": {room: [thermostat names]},
    "temperatures": [(device, reading)], "mixers": [(device, setter)],
    "pumps": [(device, power reading)], "weather": [device]}"""
    found = {
        "thermostats": {},
        "rooms": {},
        "temperatures": [],
        "mixers": [],
        "pumps": [],
        "weather": [],
    }
    for name in sorted(infos):
        info = infos[name]
        if name == own_name or info.get("FHEMPYTYPE") in OWN_TYPES:
            continue
        if is_weather(info):
            found["weather"].append(name)
            continue
        thermostat = thermostat_of(name, info)
        if thermostat:
            thermostat["room"] = room_of(info) or label(name, info)
            found["thermostats"][name] = thermostat
            found["rooms"].setdefault(thermostat["room"], []).append(name)
            continue
        for reading in temperature_readings(info):
            found["temperatures"].append((name, reading))
        setter = position_setter(info)
        if setter:
            found["mixers"].append((name, setter))
        elif switchable(info):
            found["pumps"].append((name, power_reading(info) or ""))
    return found


def ranked(role, candidates, infos):
    """candidates sorted, the best suggestion first"""

    def score(candidate):
        name = candidate[0]
        info = infos.get(name, {})
        value = _hint_score(role, name, info)
        if len(candidate) > 1 and candidate[1]:
            value += 2 if role == "pump" else 0
            value += _hint_score(role, candidate[1], {})
        return -value, name

    return sorted(candidates, key=score)


def suggest(role, candidates, infos):
    """the best candidate if its name hints at the role, else None"""
    best = ranked(role, candidates, infos)
    if not best:
        return None
    name = best[0][0]
    words = (
        _words(name, infos.get(name, {}))
        + " "
        + (best[0][1] if len(best[0]) > 1 else "").lower()
    )
    if any(w in words for w in HINTS[role]):
        return best[0]
    return None


def room_thermometers(room, found, infos):
    """temperature sensors in this FHEM room which are no thermostat"""
    result = []
    for name, reading in found["temperatures"]:
        info = infos.get(name, {})
        if room_of(info) == room and _hint_score("outdoor", name, info) == 0:
            if not any(
                _hint_score(r, name, info) for r in ("flow", "return", "supply")
            ):
                result.append((name, reading))
    return result


def forecast(info):
    """hourly forecast of a weather device: [(hours ahead, temperature)]"""
    result = []
    for reading, value in (info.get("readings") or {}).items():
        match = FORECAST_READING.match(reading)
        temp = number(value)
        if not match or temp is None:
            continue
        if match.group(1) is not None:
            hours = int(match.group(1))
        else:
            hours = int(match.group(2)) - 1
        result.append((hours, temp))
    return sorted(result)


def current_outdoor(info):
    readings = info.get("readings") or {}
    for reading in ("cur_temperature", "temperature", "temp_c", "fc0_temp"):
        value = number(readings.get(reading))
        if value is not None:
            return value
    return None


def _low_flag(value):
    return str(value).strip().lower() in LOW_WORDS


def battery(readings):
    """(low, percent or None) from the battery readings of a device"""
    readings = readings or {}
    for reading in BATTERY_LOW_FLAGS:
        if reading in readings and _low_flag(readings[reading]):
            return True, None
    percent = None
    for reading in BATTERY_PERCENT:
        value = readings.get(reading)
        if value is None or number(value) is None:
            continue
        text = str(value).strip()
        # voltages (e.g. "2.9" or "3.0 V") are no percent
        if "v" in text.lower() or (number(value) < 5 and "." in text):
            continue
        percent = number(value)
        break
    if percent is not None:
        return percent <= BATTERY_LOW_PERCENT, percent
    for reading in BATTERY_TEXT:
        value = readings.get(reading)
        if value is not None and number(value) is None:
            word = str(value).strip().lower().split(" ")[0]
            if word in ("low", "empty", "critical", "replace", "warning"):
                return True, None
    return False, None


def unreachable(readings):
    """True if the readings of a device say it can't be reached"""
    readings = readings or {}
    if str(readings.get("Activity", "")).strip().lower() == "dead":
        return True
    for reading in ("availability", "available", "reachable", "connected"):
        if reading in readings and str(readings[reading]).strip().lower() in (
            "offline",
            "false",
            "0",
            "no",
            "unavailable",
            "unreachable",
            "disconnected",
        ):
            return True
    state = str(readings.get("state", "")).strip().lower()
    return state in UNREACHABLE_STATES or "unreachable" in state
