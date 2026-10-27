"""Puts every reading of a FHEM device into one of three layers:

story  - changes a person would notice: door, light, motion, someone comes home
trend  - measurements like temperature or power, shown as daily curves
tech   - signal strength, last seen, versions... stored but hidden

Pure functions, no FHEM access."""

import re

from ..matter_bridge.devices import GENERIC_DEVICE_TYPES, LIGHT_WORDS

STORY = "story"
TREND = "trend"
TECH = "tech"
LAYERS = (STORY, TREND, TECH)

SECURITY = "security"
PRESENCE = "presence"
LIGHT = "light"
CLIMATE = "climate"
ENERGY = "energy"
DEVICES = "devices"
CATEGORIES = (SECURITY, PRESENCE, LIGHT, CLIMATE, ENERGY, DEVICES)

# FHEM modules which are infrastructure or automations, their changes are
# never part of the story
TECH_TYPES = {
    "FHEMWEB",
    "telnet",
    "Global",
    "notify",
    "at",
    "DOIF",
    "watchdog",
    "FileLog",
    "DbLog",
    "DbRep",
    "SVG",
    "weblink",
    "eventTypes",
    "autocreate",
    "allowed",
    "statistics",
    "HMinfo",
    "holiday",
    "BindingsIo",
    "fhempyServer",
    "PythonBinding",
    "MQTT2_SERVER",
    "MQTT",
    "CUL",
    "HMUARTLGW",
    "ZWDongle",
    "SIGNALduino",
    "JeeLink",
    "Twilight",
    "Astro",
    "readingsGroup",
    "readingsProxy",
    "SYSMON",
    "dewpoint",
    "sequence",
    "Calendar",
    "Weather",
    "PROPLANTA",
}
PRESENCE_TYPES = {"RESIDENTS", "ROOMMATE", "GUEST", "PET", "PRESENCE"}
RESIDENTS_TYPE = "RESIDENTS"
# states of RESIDENTS when nobody is at home
ABSENT_STATES = ("absent", "gone", "none")

# readings which change often and are only interesting when something breaks.
# Also a regexp in FHEM for "device:reading: value", so only use syntax Perl
# understands as well and never match ":" or " " ([^: ]* instead of .*).
_ANY = "[^: ]*"
TECH_READINGS = "|".join(
    (
        f"rssi{_ANY}",
        f"{_ANY}_rssi",
        f"{_ANY}RSSI{_ANY}",
        "linkquality",
        "lqi",
        "last_?seen",
        "lastSeen",
        "lastRcv",
        "protLastRcv",
        f"{_ANY}[Tt]imestamp{_ANY}",
        f"{_ANY}_ts",
        f"R-{_ANY}",
        f"uptime{_ANY}",
        f"{_ANY}[Vv]oltage",
        "vbat",
        f"{_ANY}firmware{_ANY}",
        f"{_ANY}[Vv]ersion{_ANY}",
        f"update{_ANY}",
        f"{_ANY}signal{_ANY}",
        f"wifi{_ANY}",
        "ip",
        "ipAddress",
        "mac",
        f"{_ANY}_address",
        "Activity",
        "alive",
        f"{_ANY}heartbeat{_ANY}",
        "lastcmd",
        "lastCmd",
        "cmds",
        "model",
        "manufacturer",
        f"{_ANY}[Ii]nterval",
        f"next{_ANY}",
        "IODev",
        f"{_ANY}_count",
        f"{_ANY}[Cc]ounter",
        "connection",
        f"{_ANY}_connected",
        "battery_?percent",
        "batteryPercent",
        "battery_?level",
        "batteryLevel",
    )
)
_TECH_RE = re.compile(f"^(?:{TECH_READINGS})$", re.IGNORECASE)

# reading name -> category of readings which tell a story
_STORY_READINGS = (
    (
        re.compile(
            r"^(contact|window|door|.*door.*|lock|lockstate|.*_lock|alarm.*|"
            r"smoke.*|.*leak.*|tamper|sabotage|siren|doorbell|ring|ding|"
            r"vibration|gas|co_alarm|water_alarm)$",
            re.IGNORECASE,
        ),
        SECURITY,
    ),
    (
        re.compile(
            r"^(motion|occupancy|presence|.*_presence|person|residents.*|location)$",
            re.IGNORECASE,
        ),
        PRESENCE,
    ),
    (
        re.compile(
            r"^(desired-temp|desiredTemperature|target_?temperature|mode|"
            r"hvac_?mode|boost|window_?open|windowOpen|heating)$",
            re.IGNORECASE,
        ),
        CLIMATE,
    ),
    (
        re.compile(r"^(battery|battery_low|batteryState|status|error|program)$", re.I),
        DEVICES,
    ),
)

# numeric reading name -> category
_TREND_READINGS = (
    (
        re.compile(
            r".*(temp|humid|co2|voc|pressure|pm\d|dewpoint|illuminance|lux|"
            r"wind|rain).*",
            re.IGNORECASE,
        ),
        CLIMATE,
    ),
    (
        re.compile(r".*(power|energy|current|consumption|kwh|watt|total).*", re.I),
        ENERGY,
    ),
)

_NUMBER_RE = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*(\S{0,6})\s*$")
_SECURITY_WORDS = (
    "tür",
    "door",
    "fenster",
    "window",
    "tor",
    "gate",
    "garage",
    "schloss",
    "lock",
)
_CLIMATE_WORDS = ("heiz", "thermostat", "klima", "heat", "climate", "hvac")
_ENERGY_WORDS = ("plug", "steckdose", "outlet", "socket", "zappi", "wallbox")


def number(value):
    """value as float, also with unit ("21.5 °C"), None if not numeric"""
    match = _NUMBER_RE.match(str(value))
    if not match:
        return None
    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


def is_tech_reading(reading):
    return bool(_TECH_RE.match(reading))


def device_category(info):
    """category of the state of a device"""
    device_type = info.get("TYPE", "")
    if device_type in PRESENCE_TYPES:
        return PRESENCE
    generic = GENERIC_DEVICE_TYPES.get(str(info.get("genericDeviceType", "")).lower())
    if generic in ("light", "dimmer"):
        return LIGHT
    if generic in ("lock", "contact"):
        return SECURITY
    if generic == "motion":
        return PRESENCE
    if generic == "thermostat":
        return CLIMATE
    if generic == "outlet":
        return ENERGY
    text = " ".join((device_type, info.get("NAME", ""), info.get("alias", ""))).lower()
    for words, category in (
        (LIGHT_WORDS, LIGHT),
        (_SECURITY_WORDS, SECURITY),
        (_CLIMATE_WORDS, CLIMATE),
        (_ENERGY_WORDS, ENERGY),
    ):
        if any(word in text for word in words):
            return category
    return DEVICES


def _is_tech_device(info):
    device_type = info.get("TYPE", "")
    if device_type in TECH_TYPES or info.get("FHEMPYTYPE") == "timeline":
        return True
    rooms = [r for r in str(info.get("room", "")).split(",") if r]
    # helper dummies the user didn't put into a room
    return "hidden" in rooms or (device_type == "dummy" and not rooms)


def _classify_number(info, reading):
    for regexp, category in _TREND_READINGS:
        if regexp.match(reading):
            return TREND, category
    if reading == "state":
        return TREND, device_category(info)
    return TREND, DEVICES


def classify(info, reading, value):
    """(layer, category) of one event. info: NAME, TYPE, alias, room,
    genericDeviceType of the device, may be incomplete."""
    if _is_tech_device(info) or is_tech_reading(reading):
        return TECH, DEVICES

    value = str(value)
    numeric = number(value)
    for regexp, category in _STORY_READINGS:
        if not regexp.match(reading):
            continue
        if numeric is None or category == SECURITY or category == PRESENCE:
            return STORY, category
        # desired-temp 21 is a decision, battery 87 is not
        return (STORY, CLIMATE) if category == CLIMATE else (TECH, DEVICES)

    if numeric is not None:
        return _classify_number(info, reading)
    if reading != "state":
        # other text readings are details of the device
        return TECH, DEVICES
    if value.startswith("set_") or ":" in value or len(value) > 40:
        # pending commands and stateFormat summaries of other readings
        return TECH, DEVICES
    return STORY, device_category(info)
