"""Finds the devices the heating advisor uses, by room and reading names.
Pure functions, no FHEM access.

infos: device name -> {TYPE, FHEMPYTYPE, room, alias, genericDeviceType,
readings: {reading: value}}"""

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
    "pi_heating_demand",
    "heating_demand",
)
# thermostats which detect open windows themselves
THERMOSTAT_WINDOW_READINGS = ("window", "windowOpen", "window_open", "windowopen")
CONTACT_READINGS = ("contact", "window", "state")
OPEN_VALUES = ("open", "opened", "offen", "tilted", "gekippt", "on", "1", "true")
CLOSED_VALUES = ("closed", "close", "geschlossen", "zu", "off", "0", "false")
# zigbee2mqtt: contact true = magnet touches = closed
CONTACT_CLOSED = {"true": True, "false": False}

OUTDOOR_WORDS = (
    "aussen",
    "außen",
    "outdoor",
    "outside",
    "garten",
    "garden",
    "balkon",
    "balcony",
    "terrasse",
    "terrace",
    "wetter",
    "weather",
    "aussentemp",
)
# not a room temperature
IGNORE_WORDS = (
    "kühl",
    "kuehl",
    "gefrier",
    "fridge",
    "freezer",
    "pool",
    "wasser",
    "water",
    "boiler",
    "speicher",
    "vorlauf",
    "rücklauf",
    "ruecklauf",
    "flow",
    "cpu",
    "server",
    "aquarium",
    "sauna",
    "kamin",
    "ofen",
    "oven",
    "grill",
    "heizstab",
    "sonde",
    "probe",
    "keller_hzg",
    "puffer",
)
SURFACE_WORDS = ("wand", "wall", "oberfl", "surface", "boden", "floor", "ir_temp")
WINDOW_WORDS = (
    "fenster",
    "window",
    "tür",
    "tuer",
    "door",
    "terrasse",
    "balkon",
    "dach",
    "velux",
    "kontakt",
    "contact",
)
FLOOR_WORDS = ("fbh", "fußboden", "fussboden", "floor", "underfloor", "estrich")
HEATPUMP_WORDS = ("wärmepumpe", "waermepumpe", "heatpump", "heat_pump", "luftwp")
GAS_WORDS = ("gastherme", "therme", "brenner", "burner", "gas")
WEATHER_TYPES = ("Weather", "PROPLANTA", "DWD_OpenData", "OPENWEATHER")
WEATHER_FHEMPYTYPES = ("openmeteo_weather", "google_weather")
HEATING_FHEMPYTYPES = {"nefit": "gas", "erelax_vaillant": "gas"}
IGNORED_ROOMS = ("fhempy", "hidden", "unsorted", "everything", "")
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")


def number(value):
    if value is None:
        return None
    match = NUMBER.search(str(value))
    if match is None:
        return None
    return float(match.group(0).replace(",", "."))


def words_of(name, info):
    return " ".join(
        (name, str(info.get("alias", "")), str(info.get("room", "")))
    ).lower()


def has_word(text, words):
    return any(word in text for word in words)


def room_of(info):
    for room in str(info.get("room", "")).split(","):
        room = room.strip()
        if room.lower() not in IGNORED_ROOMS:
            return room
    return None


def first(names, readings):
    for name in names:
        if name in readings:
            return name
    return None


def contact_open(info, reading):
    """True/False for a contact reading, None if unknown"""
    value = str(info.get("readings", {}).get(reading, "")).strip().lower()
    word = value.split(" ")[0] if value else ""
    if reading == "contact" and word in CONTACT_CLOSED:
        return not CONTACT_CLOSED[word]
    if word in OPEN_VALUES:
        return True
    if word in CLOSED_VALUES:
        return False
    return None


def contact_reading(name, info):
    readings = info.get("readings", {})
    generic = str(info.get("genericDeviceType", "")).lower()
    for reading in CONTACT_READINGS:
        if reading not in readings:
            continue
        if reading == "state" and generic not in ("contact", "window", "door"):
            if not has_word(words_of(name, info), WINDOW_WORDS):
                continue
            if first(TEMP_READINGS + TARGET_READINGS, readings):
                continue
        if contact_open(info, reading) is not None:
            return reading
    return None


def is_weather(info):
    return (
        info.get("TYPE") in WEATHER_TYPES
        or info.get("FHEMPYTYPE") in WEATHER_FHEMPYTYPES
    )


def discover(infos, exclude=(), rooms=None):
    """{"rooms": {room: {"sensors": [(dev, reading)], "thermostats":
    [{"device", "temp", "target", "valve", "window"}], "contacts":
    [(dev, reading)], "surface": [(dev, reading)], "humidity": [...]}},
    "outdoor": (dev, reading) or None, "residents": [dev],
    "heating_type": str or None, "floor_rooms": set}"""
    found = {}
    outdoor = []
    weather = []
    residents = []
    heating_type = None
    floor_rooms = set()
    for name in sorted(infos):
        if name in exclude:
            continue
        info = infos[name]
        readings = info.get("readings", {})
        text = words_of(name, info)
        if info.get("TYPE") == "RESIDENTS":
            residents.append(name)
            continue
        if info.get("FHEMPYTYPE") in HEATING_FHEMPYTYPES:
            heating_type = heating_type or HEATING_FHEMPYTYPES[info["FHEMPYTYPE"]]
        if has_word(text, HEATPUMP_WORDS):
            heating_type = "heatpump"
        elif heating_type is None and has_word(text, GAS_WORDS):
            heating_type = "gas"
        temp = first(TEMP_READINGS, readings)
        if temp is not None and number(readings[temp]) is None:
            temp = None
        if is_weather(info):
            if temp is not None:
                weather.append((name, temp))
            continue
        if info.get("TYPE") == "fhempy":
            continue
        if temp is not None and has_word(text, IGNORE_WORDS):
            temp = None
        room = room_of(info)
        if temp is not None and (room is None or has_word(text, OUTDOOR_WORDS)):
            if has_word(text, OUTDOOR_WORDS):
                outdoor.append((name, temp))
            temp = None
        if room is None or (rooms and room not in rooms):
            continue
        entry = found.setdefault(
            room,
            {
                "sensors": [],
                "thermostats": [],
                "contacts": [],
                "surface": [],
                "humidity": [],
            },
        )
        target = first(TARGET_READINGS, readings)
        if target is not None and number(readings[target]) is not None:
            window = first(THERMOSTAT_WINDOW_READINGS, readings)
            if window is not None and contact_open(info, window) is None:
                window = None
            entry["thermostats"].append(
                {
                    "device": name,
                    "temp": temp,
                    "target": target,
                    "valve": first(VALVE_READINGS, readings),
                    "window": window,
                }
            )
            if has_word(text, FLOOR_WORDS):
                floor_rooms.add(room)
            continue
        if temp is not None:
            if has_word(text, SURFACE_WORDS):
                entry["surface"].append((name, temp))
            else:
                entry["sensors"].append((name, temp))
        if "humidity" in readings and number(readings["humidity"]) is not None:
            entry["humidity"].append((name, "humidity"))
        contact = contact_reading(name, info)
        if contact is not None:
            entry["contacts"].append((name, contact))
    rooms_found = {
        room: entry
        for room, entry in found.items()
        if entry["sensors"] or any(t["temp"] for t in entry["thermostats"])
    }
    return {
        "rooms": rooms_found,
        "outdoor": (outdoor or weather or [None])[0],
        "residents": residents,
        "heating_type": heating_type,
        "floor_rooms": floor_rooms,
    }


def devices_of(found):
    """all devices with the readings needed: {device: set(readings)}"""
    result = {}

    def add(device, reading):
        if device and reading:
            result.setdefault(device, set()).add(reading)

    for entry in found["rooms"].values():
        for device, reading in (
            entry["sensors"] + entry["contacts"] + entry["surface"] + entry["humidity"]
        ):
            add(device, reading)
        for thermostat in entry["thermostats"]:
            for key in ("temp", "target", "valve", "window"):
                add(thermostat["device"], thermostat[key])
    if found.get("outdoor"):
        add(*found["outdoor"])
    for device in found.get("residents", []):
        add(device, "state")
    return result


ABSENT_STATES = ("absent", "gone", "none", "abwesend", "verreist")


def sample_room(entry, values):
    """one sample of a room from current values {device: {reading: value}}
    -> dict y, setp, valve, window, surface, humidity"""

    def get(device, reading):
        return values.get(device, {}).get(reading)

    temps = [number(get(d, r)) for d, r in entry["sensors"]]
    temps = [t for t in temps if t is not None and -30 < t < 50]
    if not temps:
        temps = [
            number(get(t["device"], t["temp"]))
            for t in entry["thermostats"]
            if t["temp"]
        ]
        temps = [t for t in temps if t is not None and -30 < t < 50]
    targets = [number(get(t["device"], t["target"])) for t in entry["thermostats"]]
    targets = [t for t in targets if t is not None]
    valves = [
        number(get(t["device"], t["valve"])) for t in entry["thermostats"] if t["valve"]
    ]
    valves = [v for v in valves if v is not None]
    opens = []
    for device, reading in entry["contacts"]:
        state = contact_open({"readings": values.get(device, {})}, reading)
        if state is not None:
            opens.append(state)
    for t in entry["thermostats"]:
        if t["window"]:
            state = contact_open({"readings": values.get(t["device"], {})}, t["window"])
            if state is not None:
                opens.append(state)
    surface = [number(get(d, r)) for d, r in entry["surface"]]
    surface = [s for s in surface if s is not None]
    return {
        "y": sum(temps) / len(temps) if temps else None,
        "setp": max(targets) if targets else None,
        "valve": min(max(sum(valves) / len(valves) / 100, 0.0), 1.0)
        if valves
        else None,
        "window": (1.0 if any(opens) else 0.0) if opens else None,
        "surface": sum(surface) / len(surface) if surface else None,
    }


def present(values, residents):
    """1 if somebody is at home, 0 if not, None if unknown"""
    states = [str(values.get(d, {}).get("state", "")).lower() for d in residents]
    states = [s for s in states if s]
    if not states:
        return None
    return 0.0 if all(s in ABSENT_STATES for s in states) else 1.0
