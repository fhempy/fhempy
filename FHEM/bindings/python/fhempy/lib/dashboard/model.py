"""What the tablets show: rooms, tiles, the header (weather, people at home,
warnings) and scenes, built from the FHEM devices without any configuration.
Pure functions, no FHEM access, so everything here is easy to test.

info of a FHEM device (see dashboard.fetch_infos):
NAME, TYPE, FHEMPYTYPE, alias, room, sets, readings (dict), times (dict),
attrs (dict)
"""

import re

from ..matter_bridge import devices as kinds

# FHEMWEB rooms which are no rooms of the home
HIDDEN_ROOMS = {
    "hidden",
    "unsorted",
    "everything",
    "fhempy",
    "timeline",
    "matterbridge",
    "ai",
    "system",
    "logs",
    "plots",
    "",
}

# order of the tiles in a room, things you switch first
KIND_ORDER = (
    "light",
    "dimmer",
    "blind",
    "thermostat",
    "switch",
    "outlet",
    "lock",
    "contact",
    "temperature",
    "humidity",
    "motion",
)
SWITCHABLE = ("light", "dimmer", "switch", "outlet")
LIGHTS = ("light", "dimmer")
DOOR_WORDS = ("tür", "tuer", "door", "tor", "gate", "garage", "eingang", "entrance")
TILTED_WORDS = ("tilt", "gekippt", "kipp")
PRESENT_STATES = ("home", "awoken", "asleep", "gotosleep", "present", "anwesend")
PRESENCE_TYPES = ("ROOMMATE", "GUEST")
PRESENCE_DEVICE_TYPES = ("PRESENCE",)
PRESENCE_FHEMPY_TYPES = ("arp_presence", "bt_presence", "ble_presence")
LOW_BATTERY = ("low", "empty", "leer", "critical", "warn", "warning")
BATTERY_READINGS = ("battery", "batteryState", "batteryLevel", "batteryPercent")
LOW_BATTERY_PERCENT = 15
# readings the tablets need, everything else isn't sent by FHEM
READINGS = (
    "state",
    "pct",
    "dim",
    "brightness",
    "level",
    "position",
    "desired-temp",
    "desiredTemperature",
    "desired",
    "setpoint",
    "measured-temp",
    "temperature",
    "measuredTemperature",
    "actualTemperature",
    "currentTemperature",
    "humidity",
    "contact",
    "motion",
    "occupancy",
    "lock",
    "lockState",
    "power",
    "condition",
    "cur_temperature",
    "cur_weather",
    "next_days_0_max_temp",
    "next_days_0_min_temp",
    "fc1_high_c",
    "fc1_low_c",
    "fc0_high_c",
    "fc0_low_c",
    "message",
    "ding",
    "doorbell",
    "ring",
    "action",
    "button",
) + BATTERY_READINGS
ENERGY_FHEMPY_TYPES = (
    "fusionsolar",
    "goodwe",
    "rct_power",
    "alphaesscloud",
    "huawei_modbus",
    "tibber",
    "zappi",
)
ENERGY_READINGS = {
    "solar": (
        "pv_power",
        "solar_power",
        "inverter_output_power",
        "power_generated",
        "powerProduction",
        "ppv",
        "pv_input_power",
        "input_power",
    ),
    "grid": ("grid_power", "power_grid", "from_grid_power", "rt_powerNet"),
    "load": (
        "electrical_load",
        "load_power",
        "house_consumption",
        "consumption_power",
        "power_total",
    ),
    "battery": ("battery_soc", "SOC", "soc"),
    "price": ("current_price_total",),
}
DOORBELL_WORDS = ("klingel", "doorbell", "türglocke", "tuerglocke", "läuten")
DOORBELL_FHEMPY_TYPES = ("ring",)
DOORBELL_READINGS = ("state", "ding", "doorbell", "ring", "action", "button", "press")
DOORBELL_VALUES = (
    "ding",
    "ring",
    "ringing",
    "pressed",
    "press",
    "on",
    "1",
    "true",
    "single",
    "short",
    "doorbell",
    "klingel",
)
READINGS = READINGS + tuple(r for names in ENERGY_READINGS.values() for r in names)
WEATHER_TYPES = ("Weather",)
WEATHER_FHEMPY_TYPES = ("openmeteo_weather",)
SCENE_TYPES = ("LightScene",)
# fhempy modules the dashboard uses even without room
TIMELINE_TYPE = "timeline"
PUSH_TYPE = "push"
SPECIAL_FHEMPY_TYPES = (
    PRESENCE_FHEMPY_TYPES
    + WEATHER_FHEMPY_TYPES
    + ENERGY_FHEMPY_TYPES
    + DOORBELL_FHEMPY_TYPES
    + (TIMELINE_TYPE, PUSH_TYPE)
)


def rooms_of(info):
    """visible rooms of a device, in the order of attribute room"""
    result = []
    for room in str(info.get("room") or "").split(","):
        room = room.strip()
        if room.lower() not in HIDDEN_ROOMS and room not in result:
            result.append(room)
    return result


def _split_words(name):
    name = re.sub(r"([a-zäöü])([A-ZÄÖÜ])", r"\1 \2", name)
    return [w for w in re.split(r"[\s_.\-]+", name) if w]


def display_name(info, room=None):
    """alias, otherwise a readable device name: wz_LampeDecke -> Lampe Decke.
    The name of the room is left out, the tile is in the room anyway."""
    alias = str(info.get("alias") or "").strip()
    if alias:
        return alias
    name = str(info.get("NAME") or "")
    prefix, sep, rest = name.partition("_")
    # wz_Lamp, EG_Kitchen_Light: short prefixes for floor or room
    if sep and rest and len(prefix) <= 3:
        name = rest
    words = _split_words(name)
    if room and len(words) > 1:
        rest = [w for w in words if w.lower() != room.lower()]
        if rest:
            words = rest
    if not words:
        return str(info.get("NAME") or "")
    return " ".join(w[:1].upper() + w[1:] for w in words)


def _text(info):
    return " ".join(
        str(info.get(key) or "") for key in ("NAME", "alias", "TYPE")
    ).lower()


def _reading(info, *names):
    readings = info.get("readings") or {}
    for name in names:
        if name in readings:
            return readings[name]
    return None


def _reading_time(info, *names):
    times = info.get("times") or {}
    for name in names:
        if name in times:
            return times[name]
    return None


WINDOW_WORDS = ("fenster", "window", "tür", "tuer", "door", "kontakt", "contact")
CONTACT_STATES = ("open", "opened", "closed", "tilted", "offen", "geschlossen", "gekippt")


def kind_of(info):
    kind = kinds.detect_type(info)
    if kind is not None:
        return kind
    # window handles and contacts which only have state open/closed/tilted
    state = str(_reading(info, "state") or "").strip().lower()
    text = _text(info)
    if state in CONTACT_STATES and any(word in text for word in WINDOW_WORDS):
        return "contact"
    return None


def is_door(info):
    text = _text(info)
    return any(word in text for word in DOOR_WORDS)


def tile_state(kind, info):
    """state of a tile, keys depend on kind"""
    state = {k: v for k, v in kinds.state(kind, info).items() if v is not None}
    if kind == "contact":
        raw = str(_reading(info, "contact", "state") or "").lower()
        if state.get("closed") is False and any(w in raw for w in TILTED_WORDS):
            state["tilted"] = True
        state["since"] = _reading_time(info, "contact", "state")
    if kind in ("temperature", "thermostat"):
        humidity = kinds.number(_reading(info, "humidity"))
        if humidity is not None:
            state["humidity"] = humidity
    if kind in ("switch", "outlet"):
        power = kinds.number(_reading(info, "power"))
        if power is not None:
            state["power"] = power
    if battery_low(info):
        state["battery_low"] = True
    return state


def battery_low(info):
    for name in BATTERY_READINGS:
        value = _reading(info, name)
        if value is None:
            continue
        word = str(value).strip().lower()
        if word in LOW_BATTERY:
            return True
        number = kinds.number(word)
        if (
            number is not None
            and name in ("batteryLevel", "batteryPercent", "battery")
            and "v" not in word
            and number <= LOW_BATTERY_PERCENT
            and word not in ("1", "0")
        ):
            return True
    return False


def tile(info, room=None):
    kind = kind_of(info)
    if kind is None:
        return None
    result = {
        "id": info["NAME"],
        "name": display_name(info, room),
        "kind": kind,
        "rooms": rooms_of(info),
        "state": tile_state(kind, info),
    }
    if kind == "contact":
        result["door"] = is_door(info)
    if kind == "blind":
        sets = kinds.set_names(info.get("sets"))
        result["stop"] = "stop" in sets
    if kind == "thermostat":
        result["step"] = 0.5
    return result


def _tile_sort_key(item):
    kind = item["kind"]
    order = KIND_ORDER.index(kind) if kind in KIND_ORDER else len(KIND_ORDER)
    return (order, item["name"].lower())


def scenes_of(info):
    """LightScene: the scenes of 'set <name> scene <scene>'"""
    for entry in str(info.get("sets") or "").split():
        name, _, options = entry.partition(":")
        if name == "scene" and options:
            return [s for s in options.split(",") if s]
    return []


def _scene_items(name, info):
    return [
        {"id": f"{name}:{scene}", "device": name, "scene": scene, "name": scene,
         "room": room}
        for room in rooms_of(info)
        for scene in scenes_of(info)
    ]


def _sorted_rooms(rooms, order):
    order = list(order or [])

    def room_key(room):
        if room["name"] in order:
            return (0, order.index(room["name"]), "")
        return (1, -len(room["tiles"]), room["name"].lower())

    room_list = []
    for room, items in rooms.items():
        items.sort(key=_tile_sort_key)
        room_list.append({"name": room, "tiles": [t["id"] for t in items]})
    room_list.sort(key=room_key)
    return room_list


def build(infos, order=None):
    """rooms and tiles of all devices.
    order: names of rooms in the wanted order (others follow sorted)"""
    tiles = {}
    rooms = {}
    scenes = []
    for name in sorted(infos):
        info = infos[name]
        if info.get("TYPE") in SCENE_TYPES:
            scenes.extend(_scene_items(name, info))
            continue
        device_rooms = rooms_of(info)
        item = tile(info, device_rooms[0]) if device_rooms else None
        if item is None:
            continue
        tiles[name] = item
        for room in device_rooms:
            rooms.setdefault(room, []).append(item)
    return {"rooms": _sorted_rooms(rooms, order), "tiles": tiles, "scenes": scenes}


# --- header ---


def _person(info):
    name = display_name(info)
    return {"id": info["NAME"], "name": name, "initial": name[:1].upper()}


def presence(infos):
    """people at home: ROOMMATE/GUEST, otherwise presence devices"""
    residents = [
        i for i in infos.values() if i.get("TYPE") in PRESENCE_TYPES
    ]
    if not residents:
        residents = [
            i
            for i in infos.values()
            if i.get("TYPE") in PRESENCE_DEVICE_TYPES
            or i.get("FHEMPYTYPE") in PRESENCE_FHEMPY_TYPES
        ]
    if not residents:
        return None
    home = []
    for info in sorted(residents, key=lambda i: i["NAME"].lower()):
        state = str(_reading(info, "state") or "").strip().lower()
        if state in PRESENT_STATES:
            home.append(_person(info))
    return {"home": home, "total": len(residents)}


def weather(infos):
    for info in sorted(infos.values(), key=lambda i: i["NAME"].lower()):
        if info.get("FHEMPYTYPE") in WEATHER_FHEMPY_TYPES:
            return {
                "temperature": kinds.number(_reading(info, "cur_temperature")),
                "condition": str(_reading(info, "cur_weather") or ""),
                "high": kinds.number(_reading(info, "next_days_0_max_temp")),
                "low": kinds.number(_reading(info, "next_days_0_min_temp")),
            }
        if info.get("TYPE") in WEATHER_TYPES:
            return {
                "temperature": kinds.number(_reading(info, "temperature")),
                "condition": str(_reading(info, "condition") or ""),
                "high": kinds.number(_reading(info, "fc0_high_c", "fc1_high_c")),
                "low": kinds.number(_reading(info, "fc0_low_c", "fc1_low_c")),
            }
    return None


def is_weather(info):
    return (
        info.get("FHEMPYTYPE") in WEATHER_FHEMPY_TYPES
        or info.get("TYPE") in WEATHER_TYPES
    )


def is_presence(info):
    return (
        info.get("TYPE") in PRESENCE_TYPES + PRESENCE_DEVICE_TYPES
        or info.get("FHEMPYTYPE") in PRESENCE_FHEMPY_TYPES
    )


def open_contacts(tiles):
    """open windows and doors, longest open first"""
    result = []
    for item in tiles.values():
        if item["kind"] != "contact" or item["state"].get("closed") is not False:
            continue
        result.append(
            {
                "id": item["id"],
                "name": item["name"],
                "room": (item["rooms"] or [""])[0],
                "door": item.get("door", False),
                "tilted": item["state"].get("tilted", False),
                "since": item["state"].get("since"),
            }
        )
    result.sort(key=lambda c: (c["since"] or "9999", c["name"].lower()))
    return result


def running(tiles):
    """lights and switches which are on"""
    result = []
    for item in tiles.values():
        if item["kind"] in SWITCHABLE and item["state"].get("on"):
            result.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "kind": item["kind"],
                    "room": (item["rooms"] or [""])[0],
                    "power": item["state"].get("power"),
                }
            )
    result.sort(key=lambda r: (r["kind"] not in LIGHTS, r["room"], r["name"].lower()))
    return result


def header(infos, tiles):
    low = sorted(
        (
            {"id": t["id"], "name": t["name"], "room": (t["rooms"] or [""])[0]}
            for t in tiles.values()
            if t["state"].get("battery_low")
        ),
        key=lambda b: b["name"].lower(),
    )
    return {
        "weather": weather(infos),
        "energy": energy(infos),
        "presence": presence(infos),
        "open": open_contacts(tiles),
        "running": running(tiles),
        "battery": low,
    }


# --- commands of the tablets ---


def _toggle(kind, state):
    if kind in SWITCHABLE:
        return {"on": not state.get("on")}
    if kind == "lock":
        return {"locked": not state.get("locked")}
    if kind == "blind":
        return {"position": 0 if (state.get("position") or 0) > 0 else 100}
    return None


def _level(value):
    level = _clamp(value, 0, 100)
    return {"on": False} if level == 0 else {"level": level}


# action -> wanted state, value is the number sent by the tablet
ACTIONS = {
    "on": lambda value: {"on": True},
    "off": lambda value: {"on": False},
    "level": _level,
    "position": lambda value: {"position": _clamp(value, 0, 100)},
    "stop": lambda value: {"stop": True},
    "target": lambda value: {"target": _clamp(value, 4.5, 30, 1)},
    "lock": lambda value: {"locked": True},
    "unlock": lambda value: {"locked": False},
}


def command(item, info, action, value=None):
    """FHEM set arguments for an action of a tablet, e.g. ['pct 50'].
    Only what the kind of the tile allows, never free commands."""
    if action == "toggle":
        wanted = _toggle(item["kind"], item["state"])
    elif action in ACTIONS:
        wanted = ACTIONS[action](value)
    else:
        wanted = None
    if wanted is None:
        return []
    return kinds.fhem_commands(item["kind"], info, wanted)


def _clamp(value, low, high, digits=0):
    number = kinds.number(value)
    if number is None:
        raise ValueError(f"not a number: {value}")
    number = max(low, min(high, number))
    if digits == 0:
        return int(round(number))
    return round(number * 2) / 2


def all_off(tiles, room=None):
    """lights and switches to switch off, optionally only in one room"""
    return [
        t["id"]
        for t in tiles.values()
        if t["kind"] in SWITCHABLE
        and t["state"].get("on")
        and (room is None or room in t["rooms"])
    ]


# --- energy ---


def is_energy(info):
    if info.get("FHEMPYTYPE") in ENERGY_FHEMPY_TYPES:
        return True
    readings = info.get("readings") or {}
    return any(r in readings for r in ENERGY_READINGS["solar"] + ENERGY_READINGS["grid"])


def watts(value):
    """'1.2 kW', '1200 W', 1200 -> 1200; small values with decimals are kW"""
    number = kinds.number(value)
    if number is None:
        return None
    text = str(value).lower()
    if "kw" in text or (abs(number) < 50 and number != int(number)):
        number *= 1000
    return round(number)


def _energy_value(key, value):
    if key in ("battery", "price"):
        return kinds.number(value)
    return watts(value)


def energy(infos):
    """solar, grid, load in W, battery in %, price; None without such devices"""
    result = {}
    for info in sorted(infos.values(), key=lambda i: i["NAME"].lower()):
        if not is_energy(info):
            continue
        for key, names in ENERGY_READINGS.items():
            value = _reading(info, *names)
            if key not in result and value is not None:
                result[key] = _energy_value(key, value)
    result = {k: v for k, v in result.items() if v is not None}
    if not result:
        return None
    if "load" not in result and "solar" in result and "grid" in result:
        result["load"] = result["solar"] + result["grid"]
    return result


# --- doorbell ---


def is_doorbell(info):
    if info.get("FHEMPYTYPE") in DOORBELL_FHEMPY_TYPES:
        return True
    text = _text(info)
    return any(word in text for word in DOORBELL_WORDS)


def rings(reading, value):
    """True if this event of a doorbell means somebody rings"""
    if reading not in DOORBELL_READINGS:
        return False
    word = str(value or "").strip().lower().split(" ")[0]
    return word in DOORBELL_VALUES


def doorbells(infos):
    return sorted(
        (
            {"id": i["NAME"], "name": display_name(i), "room": (rooms_of(i) or [""])[0]}
            for i in infos.values()
            if is_doorbell(i)
        ),
        key=lambda d: d["name"].lower(),
    )


def motion_rooms(item):
    """rooms of a motion sensor which just detected motion"""
    if item["kind"] == "motion" and item["state"].get("occupied"):
        return list(item["rooms"])
    return []


def filter_rooms(data, allowed):
    """only the rooms a restricted tablet may see"""
    if not allowed:
        return data
    rooms = [r for r in data["rooms"] if r["name"] in allowed]
    ids = {t for r in rooms for t in r["tiles"]}
    return {
        "rooms": rooms,
        "tiles": {k: v for k, v in data["tiles"].items() if k in ids},
        "scenes": [s for s in data["scenes"] if s["room"] in allowed],
    }
