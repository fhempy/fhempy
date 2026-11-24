"""What the tablets show: rooms, tiles, the header (weather, people at home,
warnings) and scenes, built from the FHEM devices without any configuration.
Pure functions, no FHEM access, so everything here is easy to test.

info of a FHEM device (see dashboard.fetch_infos):
NAME, TYPE, FHEMPYTYPE, alias, room, sets, readings (dict), times (dict),
attrs (dict)
"""

import datetime
import math
import re

from ..matter_bridge import devices as kinds
from . import inputs, media, views

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
    "fan",
    "media",
    "inputs",
    "lock",
    "contact",
    "smoke",
    "water",
    "temperature",
    "humidity",
    "motion",
)
SWITCHABLE = ("light", "dimmer", "switch", "outlet")
# tiles with "switch off in 15 min / 30 min / 1 h / 2 h"
TIMER_KINDS = SWITCHABLE + ("fan", "irrigation")
TIMER_PREFIX = "dashboard_timer_"
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
    "lastArrival",
    "lastDeparture",
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
READINGS = READINGS + tuple(r for r in media.READINGS if r not in READINGS)
READINGS = READINGS + tuple(r for r in views.READINGS if r not in READINGS)
READINGS = READINGS + ("fan", "fan_pct", "fan_mode")
# CO2 of the air in ppm
CO2_READINGS = ("co2", "CO2", "carbonDioxide", "carbon_dioxide")
# reachability: HomeMatic Activity, zigbee2mqtt/MQTT availability
REACH_READINGS = ("Activity", "availability")
UNREACHABLE_WORDS = ("dead", "unreachable", "offline", "disconnected", "not connected")
READINGS = READINGS + CO2_READINGS + REACH_READINGS


# waste collection devices (e.g. ABFALL): text and days of the next pickup
BIN_READINGS = ("next_text", "next_days")
READINGS = READINGS + BIN_READINGS
# colour lights: HUEDevice, zigbee2mqtt, Tasmota, Shelly, WLED, ...
RGB_SETS = ("rgb", "hex", "RGB", "Color", "color")
CT_SETS = ("ct", "color_temp", "colortemp", "colorTemperature", "CT", "ColorTemp")
COLOR_READINGS = ("rgb", "hex", "RGB", "Color", "color")
CT_READINGS = ("ct", "color_temp", "colortemp", "colorTemperature", "CT", "ColorTemp")
READINGS = READINGS + COLOR_READINGS + CT_READINGS
# how far the valve of a thermostat is open, in percent
VALVE_READINGS = (
    "actuator",
    "ValvePosition",
    "valveposition",
    "valve_position",
    "valve",
    "pi_heating_demand",
    "heating_demand",
    "level_valve",
)
# what a thermostat does right now: heating, idle
ACTION_READINGS = ("hvac_action", "hvacAction", "running_state", "heating_state")
READINGS = READINGS + VALVE_READINGS + ACTION_READINGS


# smoke and water detectors: readings which say there is smoke or water
HAZARD_READINGS = {
    "smoke": (
        "smoke",
        "smoke_detected",
        "smokeDetected",
        "smoke_detect",
        "smokeAlarm",
        "fire",
    ),
    "water": (
        "water_leak",
        "waterLeak",
        "leak",
        "flood",
        "water_detected",
        "waterDetected",
        "moistureDetected",
        "waterlevelDetected",
    ),
}
READINGS = READINGS + tuple(r for names in HAZARD_READINGS.values() for r in names)
# the next hours of openmeteo_weather: warnings before the night or leaving
# (WARN_HOURS) and the weather details (FORECAST_HOURS)
WARN_HOURS = 12
FORECAST_HOURS = 24
FORECAST_DAYS = 7
HOUR_KEYS = ("time", "condition", "precipitation", "temperature", "windspeed")
FORECAST_READINGS = tuple(
    f"next_hours_{i:02d}_{key}" for i in range(FORECAST_HOURS) for key in HOUR_KEYS
)
# days: openmeteo_weather next_days_N_*, FHEM Weather fcN_*
DAY_READINGS = {
    "openmeteo": ("next_days_{}_", ("name", "weather", "max_temp", "min_temp", "precipitation")),
    "weather": ("fc{}_", ("day_of_week", "condition", "high_c", "low_c", "chOfRainDay")),
}
FORECAST_READINGS += tuple(
    prefix.format(i) + key
    for prefix, keys in DAY_READINGS.values()
    for i in range(FORECAST_DAYS + 1)
    for key in keys
)
# readings with the current power in W, the first one present is used
POWER_READINGS = ("power", "cur_power", "current_power", "currentPower", "actPower")
READINGS = READINGS + POWER_READINGS
READINGS = READINGS + tuple(r for r in FORECAST_READINGS if r not in READINGS)
READING_SET = frozenset(READINGS)
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


def power_reading(info):
    """name of the reading with the current power in W, None if there is none"""
    readings = info.get("readings") or {}
    for name in POWER_READINGS:
        if name in readings:
            return name
    return None


def _reading_time(info, *names):
    times = info.get("times") or {}
    for name in names:
        if name in times:
            return times[name]
    return None


WINDOW_WORDS = ("fenster", "window", "tür", "tuer", "door", "kontakt", "contact")
CONTACT_STATES = ("open", "opened", "closed", "tilted", "offen", "geschlossen", "gekippt")


def kind_of(info, view=None):
    """view: chosen on a tablet (attr device_views), 'none': no own view"""
    if inputs.has_inputs(info):
        return "inputs"
    if media.is_media(info):
        return "media"
    if view in views.VIEWS:
        return view
    if view != "none":
        found = views.detect(info)
        if found is not None:
            return found
    hazard = hazard_kind(info)
    if hazard is not None:
        return hazard
    kind = kinds.detect_type(info)
    if kind is not None:
        return kind
    # window handles and contacts which only have state open/closed/tilted
    state = str(_reading(info, "state") or "").strip().lower()
    text = _text(info)
    if state in CONTACT_STATES and any(word in text for word in WINDOW_WORDS):
        return "contact"
    return None


CALM_VALUES = (
    "0",
    "false",
    "off",
    "no",
    "none",
    "ok",
    "clear",
    "dry",
    "idle",
    "idle_off",
    "noalarm",
    "no_alarm",
    "normal",
    "nosmoke",
    "no_smoke",
    "quiet",
    "ruhe",
)
ALARM_VALUES = (
    "1",
    "true",
    "on",
    "yes",
    "detected",
    "alarm",
    "wet",
    "leak",
    "smoke",
    "fire",
)


def hazard_kind(info):
    """smoke or water detector: one of its readings says smoke or water.
    Devices with set commands (e.g. a valve with a leak reading) are no
    detectors."""
    readings = info.get("readings") or {}
    for kind, names in HAZARD_READINGS.items():
        if any(name in readings for name in names):
            sets = kinds.set_names(info.get("sets")) - {"alarmTest", "test"}
            if sets & {"on", "off", "pct", "open", "close"}:
                return None
            return kind
    return None


def hazard_alarm(kind, info):
    """True: smoke or water, False: calm, None: the detector doesn't say"""
    result = None
    for name in HAZARD_READINGS[kind]:
        value = _reading(info, name)
        if value is None:
            continue
        word = str(value).strip().lower()
        if word in CALM_VALUES or word.startswith(("no ", "no_", "kein")):
            result = False if result is None else result
        elif word in ALARM_VALUES or "alarm" in word or name == "smoke_detect":
            # HomeMatic: smoke_detect is the name of the detector which
            # raised the alarm, none when all are calm
            return True
    return result


def is_door(info):
    text = _text(info)
    return any(word in text for word in DOOR_WORDS)


def tile_state(kind, info):
    """state of a tile, keys depend on kind"""
    if kind == "inputs":
        return inputs.state(info)
    if kind == "media":
        state = {k: v for k, v in media.state(info).items() if v is not None}
        state["presets"] = media.presets(info)
        return state
    state = {k: v for k, v in kinds.state(kind, info).items() if v is not None}
    if kind == "contact":
        raw = str(_reading(info, "contact", "state") or "").lower()
        if state.get("closed") is False and any(w in raw for w in TILTED_WORDS):
            state["tilted"] = True
        state["since"] = _reading_time(info, "contact", "state")
    if kind == "thermostat":
        state.update(heating_state(info))
    if kind == "motion":
        # last change: since when somebody is there or the room is quiet
        state["since"] = _reading_time(info, "motion", "occupancy", "presence", "state")

    if kind in HAZARD_READINGS:
        state["alarm"] = bool(hazard_alarm(kind, info))
        state["since"] = _reading_time(info, *HAZARD_READINGS[kind])
    if kind in ("temperature", "thermostat"):
        humidity = kinds.number(_reading(info, "humidity"))
        if humidity is not None:
            state["humidity"] = humidity
    if kind == "fan":
        state["on"] = bool(state.get("percent"))
    elif kinds.has_fan_endpoint(kind, info):
        state["fan"] = kinds.state("fan", info)
    if kind in LIGHTS and color_caps(info):
        state.update(color_state(info))
    if kind in views.VIEWS:
        return views.state(kind, info)
    if kind in ("switch", "outlet"):
        power = kinds.number(_reading(info, *POWER_READINGS))
        if power is not None:
            state["power"] = power
    if battery_low(info):
        state["battery_low"] = True
    co2 = kinds.number(_reading(info, *CO2_READINGS))
    if co2 is not None:
        state["co2"] = co2
    if unreachable(info):
        state["unreachable"] = True
    if kind in CLIMATE_KINDS:
        # sensors report every few minutes: the hour of the newest value
        # shows one that went silent (battery, radio, gone)
        seen = max((str(t) for t in (info.get("times") or {}).values()), default="")
        if seen:
            state["seen"] = seen[:13]
    return state


def heating_state(info):
    """valve: percent open, heating: the thermostat really heats. Without
    valve and action the tablets guess from target and current temperature."""
    result = {}
    valve = kinds.number(_reading(info, *VALVE_READINGS))
    if valve is not None and 0 <= valve <= 100:
        result["valve"] = valve
        result["heating"] = valve > 0
    action = str(_reading(info, *ACTION_READINGS) or "").strip().lower()
    if action:
        if "heat" in action:
            result["heating"] = True
        elif "valve" not in result:
            result["heating"] = False
    return result


def target_range(info):
    """(min, max, step) of the target temperature from the set command,
    e.g. desired-temp:slider,4.5,0.5,30.5"""
    args = _set_args(info.get("sets"))
    for name in kinds.TARGET_SETS:
        if name not in args:
            continue
        parts = args[name].split(",")
        if parts[0] == "slider" and len(parts) >= 4:
            low, step, high = (kinds.number(p) for p in parts[1:4])
            if None not in (low, step, high) and low < high and step > 0:
                return low, high, step
        numbers = [kinds.number(p) for p in parts]
        numbers = [n for n in numbers if n is not None]
        if len(numbers) >= 2:
            return min(numbers), max(numbers), 0.5
    return 4.5, 30.0, 0.5


def unreachable(info):
    """the device says it is not reachable: Activity dead, availability
    offline or such a state"""
    for name in REACH_READINGS + ("state",):
        value = str(_reading(info, name) or "").strip().lower()
        if value in UNREACHABLE_WORDS:
            return True
    return False


def _low_battery_reading(info):
    """name of the reading which says the battery is low, None if it is fine"""
    for name in BATTERY_READINGS:
        value = _reading(info, name)
        if value is None:
            continue
        word = str(value).strip().lower()
        if word in LOW_BATTERY:
            return name
        number = kinds.number(word)
        if (
            number is not None
            and name in ("batteryLevel", "batteryPercent", "battery")
            and "v" not in word
            and number <= LOW_BATTERY_PERCENT
            and word not in ("1", "0")
        ):
            return name
    return None


def battery_low(info):
    return _low_battery_reading(info) is not None


def low_batteries(infos):
    """all devices which need a new battery, also those without a tile.
    level: percent if the device reports one, since: last change"""
    result = []
    for name, info in infos.items():
        reading = _low_battery_reading(info)
        if reading is None:
            continue
        rooms = rooms_of(info)
        result.append(
            {
                "id": name,
                "name": display_name(info),
                "room": rooms[0] if rooms else "",
                "level": kinds.number(_reading(info, reading)),
                "since": _reading_time(info, reading),
            }
        )
    result.sort(key=lambda b: (b["room"].lower(), b["name"].lower()))
    return result


def tile(info, room=None, view=None):
    kind = kind_of(info, view)
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
        low, high, step = target_range(info)
        result["min"] = low
        result["max"] = high
        result["step"] = step
    if kind == "media":
        result["media"] = media.features(info)
    if kind == "inputs":
        result["inputs"] = inputs.parse(info)
    if kind in views.VIEWS:
        result["view"] = views.features(kind, info)
        result["detected"] = view not in views.VIEWS
    if kind == "fan" or kinds.has_fan_endpoint(kind, info):
        result["fan"] = True
    if kind in LIGHTS:
        caps = color_caps(info)
        if caps:
            result["color"] = {k: v for k, v in caps.items() if k != "sets"}
    return result


# --- colour and white of lights ---

HEX6 = re.compile(r"^#?([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?$")


def _set_args(sets):
    """'on rgb:colorpicker,RGB ct:colorpicker,CT,154,1,500' -> {name: args}"""
    result = {}
    for entry in (sets or "").split():
        name, _, args = entry.partition(":")
        result[name] = args
    return result


def _ct_range(args):
    """(min, max) of a colour temperature set, mired or kelvin"""
    numbers = [kinds.number(n) for n in re.split(r"[,]", args or "")]
    numbers = [n for n in numbers if n is not None]
    if len(numbers) >= 3 and ("colorpicker" in args or "slider" in args):
        low, high = numbers[0], numbers[-1]
    elif len(numbers) >= 2:
        low, high = min(numbers), max(numbers)
    else:
        return None
    if low >= high:
        return None
    return low, high


def color_caps(info):
    """what a light can do besides dimming: {'rgb': True, 'ct': [2000, 6500]}
    (colour temperature always in kelvin for the tablets), with the FHEM set
    names in 'sets'. Found by the set commands, never by names."""
    args = _set_args(info.get("sets"))
    caps, sets = {}, {}
    for name in RGB_SETS:
        if name in args and (
            "colorpicker,RGB" in args[name] or name in ("rgb", "hex", "RGB")
        ):
            sets["rgb"] = name
            caps["rgb"] = True
            break
    for name in CT_SETS:
        if name not in args:
            continue
        rng = _ct_range(args[name])
        if rng is None:
            # e.g. HUEDevice without a range: mired 153..500
            rng = (153, 500)
        low, high = rng
        kelvin = high > 1000
        if kelvin:
            caps["ct"] = [int(low), int(high)]
        else:
            caps["ct"] = [int(round(1e6 / high)), int(round(1e6 / low))]
        sets["ct"] = {"name": name, "low": low, "high": high, "kelvin": kelvin}
        break
    if not caps:
        return None
    caps["sets"] = sets
    return caps


def color_state(info):
    """current colour as #rrggbb and white as kelvin, if the device tells"""
    readings = info.get("readings") or {}
    state = {}
    for name in COLOR_READINGS:
        match = HEX6.match(str(readings.get(name, "")).strip())
        if match:
            state["rgb"] = "#" + match.group(1).lower()
            break
    for name in CT_READINGS:
        value = kinds.number(readings.get(name))
        if value:
            state["ct"] = int(value if value > 1000 else round(1e6 / value))
            break
    return state


def color_command(info, action, value):
    caps = color_caps(info)
    if caps is None:
        return []
    sets = caps["sets"]
    if action == "rgb" and "rgb" in sets:
        match = HEX6.match(str(value or "").strip())
        if match is None:
            raise ValueError(f"no colour: {value}")
        return [f"{sets['rgb']} {match.group(1).upper()}"]
    if action == "ct" and "ct" in sets:
        kelvin = kinds.number(value)
        if kelvin is None or kelvin <= 0:
            raise ValueError(f"no colour temperature: {value}")
        ct = sets["ct"]
        target = kelvin if ct["kelvin"] else 1e6 / kelvin
        target = max(ct["low"], min(ct["high"], target))
        return [f"{ct['name']} {int(round(target))}"]
    return []


def device_readings(info):
    """readings of a device the tablets need: the common ones and the
    inputs of a DOIF"""
    if info.get("TYPE") in inputs.INPUT_TYPES:
        return READING_SET | set(inputs.reading_names(info))
    return READING_SET


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


# switches 'All off' leaves on unless set otherwise: heating, cooling, network
KEEP_ON_PARTS = (
    "heiz",
    "heatpump",
    "wärmepumpe",
    "waermepumpe",
    "umwälz",
    "umwaelz",
    "boiler",
    "kühl",
    "kuehl",
    "gefrier",
    "fridge",
    "freezer",
    "router",
    "fritz",
    "aquarium",
    "lüftung",
    "lueftung",
    "ventilation",
)
KEEP_ON_WORDS = ("nas", "server", "wlan", "wifi", "dect", "heater", "heating")


def keeps_on(info):
    """found by name or alias: a heating plug stays on with 'All off'"""
    text = f"{info.get('NAME', '')} {info.get('alias') or ''}"
    if any(part in text.lower() for part in KEEP_ON_PARTS):
        return True
    return any(w.lower() in KEEP_ON_WORDS for w in _split_words(text))


# plugs and switches which may only measure
MEASURE_KINDS = ("switch", "outlet")


def build(infos, order=None, keep_on=None, measure=None, device_views=None):
    """rooms and tiles of all devices.
    order: names of rooms in the wanted order (others follow sorted)
    keep_on: devices 'All off' leaves on, None: found by their names
    measure: plugs which only measure, the tablets never switch them
    device_views: device -> own view or 'none', see views.parse_views"""
    device_views = device_views or {}
    tiles = {}
    rooms = {}
    scenes = []
    for name in sorted(infos):
        info = infos[name]
        if info.get("TYPE") in SCENE_TYPES:
            scenes.extend(_scene_items(name, info))
            continue
        device_rooms = rooms_of(info)
        item = (
            tile(info, device_rooms[0], device_views.get(name))
            if device_rooms
            else None
        )
        if item is None:
            continue
        if item["kind"] in SWITCHABLE:
            item["keep_on"] = (
                keeps_on(info) if keep_on is None else name in keep_on
            )
            if measure and name in measure and item["kind"] in MEASURE_KINDS:
                item["measure"] = True
                item["keep_on"] = True
        elif item["kind"] == "media" and keep_on and name in keep_on:
            item["keep_on"] = True
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
    home, people = [], []
    for info in sorted(residents, key=lambda i: i["NAME"].lower()):
        state = str(_reading(info, "state") or "").strip().lower()
        person = _person(info)
        present = state in PRESENT_STATES
        if present:
            home.append(person)
        people.append({**person, "home": present, "since": _presence_since(info, present)})
    people.sort(key=lambda p: (not p["home"], p["name"].lower()))
    return {"home": home, "total": len(residents), "people": people}


def _presence_since(info, present):
    """arrival or departure time: ROOMMATE/GUEST lastArrival/lastDeparture,
    otherwise the time of the state"""
    value = str(_reading(info, "lastArrival" if present else "lastDeparture") or "")
    if re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d", value):
        return value[:19]
    return _reading_time(info, "state")


def weather(infos):
    for info in sorted(infos.values(), key=lambda i: i["NAME"].lower()):
        if info.get("FHEMPYTYPE") in WEATHER_FHEMPY_TYPES:
            return {
                "temperature": kinds.number(_reading(info, "cur_temperature")),
                "condition": str(_reading(info, "cur_weather") or ""),
                "high": kinds.number(_reading(info, "next_days_0_max_temp")),
                "low": kinds.number(_reading(info, "next_days_0_min_temp")),
                "warn": weather_warning(info),
                "hours": forecast_hours(info),
                "days": forecast_days(info, "openmeteo"),
            }
        if info.get("TYPE") in WEATHER_TYPES:
            return {
                "temperature": kinds.number(_reading(info, "temperature")),
                "condition": str(_reading(info, "condition") or ""),
                "high": kinds.number(_reading(info, "fc0_high_c", "fc1_high_c")),
                "low": kinds.number(_reading(info, "fc0_low_c", "fc1_low_c")),
                "warn": None,
                "hours": [],
                "days": forecast_days(info, "weather"),
            }
    return None


# rain from this probability on, storm from this wind speed in km/h
RAIN_PERCENT = 60
STORM_KMH = 60
_THUNDER_RE = re.compile(r"gewitter|thunder", re.I)


def weather_warning(info):
    """the first rain, storm or frost of the next hours: {"kind": "rain",
    "at": "15:00"} or None. Only from the hourly forecast of
    openmeteo_weather, found by its readings."""
    for i in range(WARN_HOURS):
        prefix = f"next_hours_{i:02d}_"
        when = str(_reading(info, prefix + "time") or "")
        if not when:
            break
        at = when[-5:]
        wind = kinds.number(_reading(info, prefix + "windspeed"))
        if _THUNDER_RE.search(str(_reading(info, prefix + "condition") or "")) or (
            wind is not None and wind >= STORM_KMH
        ):
            return {"kind": "storm", "at": at}
        rain = kinds.number(_reading(info, prefix + "precipitation"))
        if rain is not None and rain >= RAIN_PERCENT:
            return {"kind": "rain", "at": at}
        temperature = kinds.number(_reading(info, prefix + "temperature"))
        if temperature is not None and temperature <= 0:
            return {"kind": "frost", "at": at}
    return None


def forecast_hours(info):
    """the next 24 hours of openmeteo_weather: [{"at": "17:00", "temp": 7,
    "rain": 10, "condition": "Bewölkt"}]"""
    result = []
    for i in range(FORECAST_HOURS):
        prefix = f"next_hours_{i:02d}_"
        when = str(_reading(info, prefix + "time") or "")
        if not when:
            break
        result.append(
            {
                "at": when[-5:],
                "temp": kinds.number(_reading(info, prefix + "temperature")),
                "rain": kinds.number(_reading(info, prefix + "precipitation")),
                "condition": str(_reading(info, prefix + "condition") or ""),
            }
        )
    return result


def forecast_days(info, source):
    """the next days: [{"name": "Di", "condition": "Regen", "high": 12,
    "low": 4, "rain": 80}], today first. The FHEM Weather module counts
    from fc0 or fc1 depending on its API."""
    prefix, keys = DAY_READINGS[source]
    first = 0 if _reading(info, prefix.format(0) + keys[2]) is not None else 1
    result = []
    for i in range(first, first + FORECAST_DAYS):
        values = [_reading(info, prefix.format(i) + key) for key in keys]
        if values[2] is None and values[3] is None:
            break
        result.append(
            {
                "name": str(values[0] or ""),
                "condition": str(values[1] or ""),
                "high": kinds.number(values[2]),
                "low": kinds.number(values[3]),
                "rain": kinds.number(values[4]),
            }
        )
    return result


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
                "may_open": item.get("may_open"),
            }
        )
    result.sort(key=lambda c: (c["since"] or "9999", c["name"].lower()))
    return result


# --- doors and gates which may be open at some times, e.g. a yard gate by day ---

_WINDOW_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")


def clean_window(value):
    """'7:00-20:00' -> '07:00-20:00', None when it is no time window"""
    match = _WINDOW_RE.match(str(value or ""))
    if not match:
        return None
    h1, m1, h2, m2 = (int(x) for x in match.groups())
    if h1 > 23 or h2 > 24 or m1 > 59 or m2 > 59 or (h2 == 24 and m2):
        return None
    if (h1, m1) == (h2, m2):
        return None
    return f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}"


def parse_may_open(value):
    """attribute may_open: 'Yard_gate=07:00-20:00,Garage=08:00-18:00'
    -> {device: '07:00-20:00'}"""
    result = {}
    for entry in re.split(r"[,;\s]+(?=[^,;\s]+=)", str(value or "").strip()):
        name, _, window = entry.partition("=")
        window = clean_window(window)
        if name.strip() and window:
            result[name.strip().rstrip(",;")] = window
    return result


def format_may_open(windows):
    return ",".join(f"{n}={w}" for n, w in sorted(windows.items()))


def may_open_now(window, minutes):
    """window '07:00-20:00', minutes since midnight. Over midnight works too:
    '22:00-06:00'"""
    window = clean_window(window)
    if window is None:
        return False
    start, end = (
        int(part[:2]) * 60 + int(part[3:]) for part in window.split("-")
    )
    if start < end:
        return start <= minutes < end
    return minutes >= start or minutes < end


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
                    "keep_on": bool(item.get("keep_on")),
                    "measure": bool(item.get("measure")),
                }
            )
    result.sort(key=lambda r: (r["kind"] not in LIGHTS, r["room"], r["name"].lower()))
    return result


def playing(tiles):
    """music players and TVs which are playing right now"""
    result = []
    for item in tiles.values():
        state = item["state"]
        if item["kind"] != "media" or not state.get("playing"):
            continue
        result.append(
            {
                "id": item["id"],
                "name": item["name"],
                "room": (item["rooms"] or [""])[0],
                "title": state.get("title"),
                "artist": state.get("artist") or state.get("station"),
            }
        )
    result.sort(key=lambda r: (r["room"], r["name"].lower()))
    return result


def in_header(info):
    """devices the header needs: weather, energy, people and batteries.
    The header is built from these only, not from all devices."""
    if is_weather(info) or is_energy(info):
        return True
    if info.get("TYPE") in PRESENCE_TYPES + PRESENCE_DEVICE_TYPES:
        return True
    if info.get("FHEMPYTYPE") in PRESENCE_FHEMPY_TYPES:
        return True
    readings = info.get("readings") or {}
    if all(r in readings for r in BIN_READINGS):
        return True
    return any(r in readings for r in BATTERY_READINGS)


def header(infos, tiles):
    return {
        "weather": weather(infos),
        "energy": energy(infos),
        "presence": presence(infos),
        "open": open_contacts(tiles),
        "running": running(tiles),
        "playing": playing(tiles),
        "battery": low_batteries(infos),
        "bins": bin_devices(infos),
    }


# --- alarm system ---

ALARM_MODES = {
    "away": ("armAway", "arm_away", "armed", "arm", "away", "scharf", "on"),
    "home": ("armHome", "arm_home", "armStay", "arm_stay", "armNight", "home", "night"),
    "off": ("disarm", "disarmed", "unscharf", "off"),
}
_TRIGGERED_RE = re.compile(r"trigger|alarm|alert|intrusion|einbruch|ausgel", re.I)


def alarm_mode(info):
    """mode of an alarm system from its state: off, home, away, triggered"""
    state = str(_reading(info, "state") or "").strip().lower()
    if not state:
        return None
    if "disarm" in state or "unscharf" in state or state in ("off", "aus"):
        return "off"
    if _TRIGGERED_RE.search(state):
        return "triggered"
    if any(w in state for w in ("home", "stay", "night", "intern")):
        return "home"
    if "arm" in state or "scharf" in state or state in ("on", "away", "extern"):
        return "away"
    return None


def alarm_commands(info):
    """mode -> set command of an alarm system, by its set commands"""
    sets = kinds.set_names(info.get("sets"))
    result = {}
    for mode, names in ALARM_MODES.items():
        for name in names:
            if name in sets:
                result[mode] = name
                break
    return result


def alarm_system(info, pin=False):
    """the alarm system chosen with attribute alarm_system, None: none"""
    if not info:
        return None
    return {
        "id": info["NAME"],
        "name": display_name(info),
        "mode": alarm_mode(info),
        "modes": [m for m in ALARM_MODES if m in alarm_commands(info)],
        "since": _reading_time(info, "state"),
        "pin": pin,
    }


def alarms(tiles, system=None):
    """smoke, water and a triggered alarm system: shown on every tablet"""
    result = []
    for item in tiles.values():
        if item["kind"] in HAZARD_READINGS and item["state"].get("alarm"):
            result.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "kind": item["kind"],
                    "room": (item["rooms"] or [""])[0],
                    "since": item["state"].get("since"),
                }
            )
    if system and system["mode"] == "triggered":
        result.append(
            {
                "id": system["id"],
                "name": system["name"],
                "kind": "intrusion",
                "room": "",
                "since": system["since"],
            }
        )
    result.sort(key=lambda a: (a["since"] or "", a["name"].lower()))
    return result


def clean_pin(value):
    """the PIN of the settings: 4 to 8 digits, None: no PIN"""
    pin = str(value or "").strip()
    if re.fullmatch(r"\d{4,8}", pin):
        return pin
    return None


# --- calendars and waste collection ---

CALENDAR_DAYS = 14
# a pickup of waste, from the summary of a calendar entry
_BIN_RE = re.compile(
    r"(rest|bio|papier|wertstoff|plastik|verpackungs?)?(m(ü|ue)ll|tonne|abfall)"
    r"|gelbe[rns]?\s*(sack|säcke|tonne)|altpapier|sperrm(ü|ue)ll|altglas"
    r"|\b(garbage|trash|recycling|waste|compost|bin|bins)\b",
    re.I,
)


def is_bin(summary):
    return bool(_BIN_RE.search(str(summary or "")))


def parse_calendar(text):
    """lines 'calendar|start|end|summary' (seconds since the epoch) of
    'get <calendar> events' -> [{"cal", "start", "end", "summary"}]"""
    result = []
    for line in str(text or "").splitlines():
        parts = line.split("|", 3)
        if len(parts) != 4:
            continue
        try:
            start, end = int(float(parts[1])), int(float(parts[2]))
        except ValueError:
            continue
        summary = parts[3].strip().replace("\\,", ",")
        if summary:
            result.append({"cal": parts[0], "start": start, "end": end, "summary": summary})
    result.sort(key=lambda e: (e["start"], e["summary"].lower()))
    return result


def bin_calendars(events):
    """calendars mostly holding pickups of waste: there every entry is a
    pickup, also "Gelb" or "Papier" alone. Found by the entries, not by the
    name of the calendar."""
    counts = {}
    for event in events:
        total, bins = counts.get(event["cal"], (0, 0))
        counts[event["cal"]] = (total + 1, bins + is_bin(event["summary"]))
    return {cal for cal, (total, bins) in counts.items() if bins * 2 > total}


def _day(epoch, now):
    """0: today, 1: tomorrow, ... of a time, local time"""
    then = datetime.datetime.fromtimestamp(epoch).date()
    return (then - datetime.datetime.fromtimestamp(now).date()).days


def calendar(events, now):
    """what the tablets show of the calendars: the entries of today and
    tomorrow and the pickups of waste of today and tomorrow"""
    bin_cals = bin_calendars(events)
    entries, bins = [], []
    for event in events:
        if event["end"] <= now:
            continue
        day = max(0, _day(event["start"], now))
        if day > 1:
            continue
        allday = event["end"] - event["start"] >= 86400 and (
            datetime.datetime.fromtimestamp(event["start"]).strftime("%H:%M")
            == "00:00"
        )
        if event["cal"] in bin_cals or is_bin(event["summary"]):
            if allday or day == 1 or event["start"] > now - 3600:
                bins.append({"what": event["summary"], "day": day})
            continue
        entries.append(
            {
                "summary": event["summary"],
                "day": day,
                "allday": allday,
                "at": ""
                if allday
                else datetime.datetime.fromtimestamp(event["start"]).strftime("%H:%M"),
                "now": event["start"] <= now,
            }
        )
    return {"entries": entries[:12], "bins": bins}


def bin_devices(infos):
    """pickups of waste of today and tomorrow from devices with the readings
    next_text and next_days (e.g. ABFALL)"""
    result = []
    for info in infos.values():
        readings = info.get("readings") or {}
        if not all(r in readings for r in BIN_READINGS):
            continue
        days = kinds.number(readings.get("next_days"))
        text = str(readings.get("next_text") or "").strip()
        if days is not None and 0 <= days <= 1 and text:
            result.append({"what": text, "day": int(days)})
    return result


# --- commands of the tablets ---


def short_error(text):
    """the answer of FHEM to a failed set, short enough for a tablet"""
    text = " ".join(str(text or "").split())
    text = re.split(r",? choose one of", text, maxsplit=1)[0]
    return text if len(text) <= 120 else text[:119] + "…"


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


def _fan_mode(value):
    mode = str(value or "").strip().lower()
    if mode not in kinds.FAN_MODES:
        raise ValueError(f"no fan mode: {value}")
    return {"mode": mode}


FAN_ACTIONS = {
    "fan_mode": _fan_mode,
    "fan_percent": lambda value: {"percent": _clamp(value, 0, 100)},
}


def _fan_toggle(item, info, action):
    if action == "toggle":
        action = "off" if item["state"].get("on") else "on"
    if action not in ("on", "off"):
        return []
    mode = "medium" if action == "on" else "off"
    return kinds.fhem_commands("fan", info, {"mode": mode})


def command(item, info, action, value=None):
    """FHEM set arguments for an action of a tablet, e.g. ['pct 50'].
    Only what the kind of the tile allows, never free commands."""
    if item.get("measure") and action in ("on", "off", "toggle", "timer"):
        # e.g. the plug of a fridge: shows its power, never switched
        return []
    if item["kind"] == "media":
        return media.command(info, action, value)
    if item["kind"] in views.VIEWS:
        return views.command(item["kind"], info, action, value)
    if item["kind"] == "inputs":
        if action != "input" or not isinstance(value, dict):
            return []
        return inputs.command(info, str(value.get("name", "")), value.get("value"))
    if item.get("fan") and action in FAN_ACTIONS:
        return kinds.fhem_commands("fan", info, FAN_ACTIONS[action](value))
    if item["kind"] == "fan":
        return _fan_toggle(item, info, action)
    if item["kind"] in LIGHTS and action in ("rgb", "ct"):
        return color_command(info, action, value)
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


def timer_name(device):
    """name of the temporary at device which switches a device off"""
    return TIMER_PREFIX + re.sub(r"[^A-Za-z0-9._]", "_", device)


def timer_minutes(value):
    """minutes of a timer from a tablet, 0: cancel, at most a day"""
    number = kinds.number(value)
    if number is None:
        return 0
    return max(0, min(24 * 60, int(number)))


def timer_definition(device, minutes, off_args):
    """definition of the at device: at +01:30:00 set lamp off"""
    hours, mins = divmod(int(minutes), 60)
    sets = "; ".join(f"set {device} {arg}" for arg in off_args)
    return f"{timer_name(device)} at +{hours:02d}:{mins:02d}:00 {sets}"


def running_timers(timers, now):
    """timers which haven't run yet, {device: end as epoch seconds}"""
    result = {}
    for device, end in (timers or {}).items():
        if isinstance(end, (int, float)) and end > now:
            result[str(device)] = end
    return result


def all_off(tiles, room=None):
    """lights and switches to switch off, optionally only in one room"""
    return [
        t["id"]
        for t in tiles.values()
        if t["kind"] in SWITCHABLE
        and t["state"].get("on")
        and not t.get("keep_on")
        and (room is None or room in t["rooms"])
    ]


# --- good night and leaving home ---

ROUTINES = ("night", "away")
UNDO_SECONDS = 10 * 60


def door_open(tiles):
    """a door contact is open: then good night / leaving home lock nothing"""
    return any(
        t["kind"] == "contact" and t.get("door") and t["state"].get("closed") is False
        for t in tiles.values()
    )


def routine_steps(tiles, mode, off_ids, close_ids, lock_ids=(), heat=False):
    """what good night / leaving home does, and how to undo it:
    (steps, undo) with (device, action, value). Switches off the lights and
    switches the tablet sends (not those left on with 'All off'); at night
    also closes the blinds it sends, when leaving only against the heat
    (heat=True, chosen on the tablet). Locks it sends are locked when all
    doors are closed, never unlocked again by undo.
    Undo restores what was before."""
    steps, undo = [], []
    for device in off_ids:
        item = tiles.get(str(device))
        if item is not None:
            _switch_off(item, steps, undo)
    if mode == "night" or heat:
        _close_blinds(tiles, close_ids, steps, undo)
    if not door_open(tiles):
        _lock(tiles, lock_ids, steps)
    return steps, undo


def _switch_off(item, steps, undo):
    if item["kind"] == "media":
        _media_off(item, steps, undo)
        return
    _fan_off(item, steps, undo)
    if (
        item["kind"] in SWITCHABLE
        and item["state"].get("on")
        and not item.get("keep_on")
    ):
        steps.append((item["id"], "off", None))
        undo.append((item["id"], "on", None))


def _close_blinds(tiles, close_ids, steps, undo):
    for device in close_ids:
        item = tiles.get(str(device))
        if item is None or item["kind"] != "blind":
            continue
        position = item["state"].get("position")
        if position is None or position > 0:
            steps.append((item["id"], "position", 0))
            if position is not None:
                undo.append((item["id"], "position", position))


def _lock(tiles, lock_ids, steps):
    """locks are never unlocked by undo"""
    for device in lock_ids:
        item = tiles.get(str(device))
        if item is not None and item["kind"] == "lock" and item["state"].get("locked") is False:
            steps.append((item["id"], "lock", None))


# the alarm system mode of good night and leaving home
ROUTINE_ALARM = {"night": "home", "away": "away"}


def routine_alarm(system, mode):
    """mode the alarm system is armed to with good night / leaving home,
    None: no alarm system, it can't, it already is or it is triggered"""
    if not system:
        return None
    wanted = ROUTINE_ALARM.get(mode)
    if wanted not in system.get("modes", ()):
        return None
    if system.get("mode") in (wanted, "triggered"):
        return None
    return wanted


def media_goes_off(item):
    """music players, speakers and TVs good night / leaving home switches
    off: those with on/off when they are on, the others when they play"""
    if item["kind"] != "media" or item.get("keep_on"):
        return False
    state = item["state"]
    if (item.get("media") or {}).get("power"):
        return bool(state.get("on"))
    return bool(state.get("playing"))


def fan_percent(item):
    """speed of a fan tile or of the fan of a ceiling light, 0: off"""
    if not item.get("fan"):
        return 0
    state = item["state"] if item["kind"] == "fan" else item["state"].get("fan") or {}
    return state.get("percent") or 0


def _fan_off(item, steps, undo):
    """fans and the fans of ceiling lights off, undo sets the speed again"""
    percent = fan_percent(item)
    if not percent or item.get("keep_on"):
        return
    if item["kind"] == "fan":
        steps.append((item["id"], "off", None))
    else:
        steps.append((item["id"], "fan_percent", 0))
    undo.append((item["id"], "fan_percent", percent))


def _media_off(item, steps, undo):
    """off where the device can be switched off, else pause what plays"""
    if not media_goes_off(item):
        return
    if (item.get("media") or {}).get("power"):
        steps.append((item["id"], "off", None))
        undo.append((item["id"], "on", None))
    else:
        steps.append((item["id"], "pause", None))
        undo.append((item["id"], "play", None))


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



# --- energy over days: from the hourly values of the timeline ---

ENERGY_RANGES = {"day": 1, "week": 7, "month": 30}
ENERGY_FLOWS = ("solar", "grid", "load", "price")
TOP_CONSUMERS = 8


def energy_sources(infos):
    """flow -> (device, reading, factor to W or None) like energy(); price
    in €/kWh has factor 1"""
    result = {}
    for info in sorted(infos.values(), key=lambda i: i["NAME"].lower()):
        if not is_energy(info):
            continue
        readings = info.get("readings") or {}
        for key in ENERGY_FLOWS:
            if key in result:
                continue
            for name in ENERGY_READINGS[key]:
                if name in readings and _energy_value(key, readings[name]) is not None:
                    result[key] = (info["NAME"], name, _factor(key, readings[name]))
                    break
    return result


def _factor(key, value):
    """the timeline keeps the number of '1.2 kW', the dashboard wants W.
    None: like watts(), decided by the values of the days"""
    if key == "price":
        return 1
    return 1000 if "kw" in str(value).lower() else None


def _series_factor(series):
    """1000 if all values are small numbers with decimals: kW, see watts()"""
    values = [v for row in series.get("rows", []) for v in (row[3], row[4])]
    if series.get("carry") is not None:
        values.append(series["carry"])
    values = [v for v in values if v is not None]
    if values and all(abs(v) < 50 for v in values):
        if any(v != int(v) for v in values):
            return 1000
    return 1


def parse_energy_price(text):
    """attr energy_price '0.32' or '0.32,0.08' (price, feed-in) in €/kWh.
    Returns (price, feed_in) or None"""
    parts = [p.strip().replace(" ", "") for p in str(text or "").split(",")]
    values = []
    for part in parts[:2]:
        try:
            value = float(part.replace("€", ""))
        except ValueError:
            return None
        if not 0 <= value < 10:
            return None
        values.append(value)
    if not values or len(parts) > 2:
        return None
    return values[0], values[1] if len(values) > 1 else None


def format_energy_price(price, feed_in=None):
    text = f"{price:g}"
    if feed_in:
        text += f",{feed_in:g}"
    return text


def hourly_watts(series, start, end, now, factor=1):
    """hour -> (mean value, share of the hour which is over) from the hourly
    rows of the timeline. FHEM sends only changes: an hour without a row
    keeps the last value, the value at the start of an hour counts as one
    more sample."""
    rows = {row[0]: row for row in series.get("rows", [])}
    value = series.get("carry")
    result = {}
    hour = int(start)
    while hour < end and hour < now:
        row = rows.get(hour)
        if row is not None and row[2]:
            total, count = row[1], row[2]
            if value is not None:
                total, count = total + value, count + 1
            mean = total / count
            value = row[3]
        else:
            mean = value
        if mean is not None:
            result[hour] = (mean * factor, min(1, (now - hour) / 3600))
        hour += 3600
    return result


def _kwh(watts_by_hour, sign=0):
    """kWh per hour; sign 1 only positive values, -1 only negative ones"""
    result = {}
    for hour, (watt, share) in watts_by_hour.items():
        if sign > 0:
            watt = max(watt, 0)
        elif sign < 0:
            watt = max(-watt, 0)
        result[hour] = watt / 1000 * share
    return result


def energy_report(series, sources, consumers, buckets, now, price=None):
    """energy of the energy page.
    series: (device, reading) -> hourly rows, see timeline hourly_values
    sources: energy_sources(); consumers: [(id, name, device, reading)]
    buckets: [(start, end)] of the bars (hours of a day or days)
    price: (price, feed_in) of the attribute, the price reading wins"""
    start, end = buckets[0][0], buckets[-1][1]

    def flow(key, sign=0):
        source = sources.get(key)
        if source is None:
            return None
        found = series.get(source[:2], {})
        factor = source[2] or _series_factor(found)
        watt = hourly_watts(found, start, end, now, factor)
        return _kwh(watt, sign) if watt else None

    flows = {
        "solar": flow("solar", 1),
        "import": flow("grid", 1),
        "export": flow("grid", -1),
        "load": flow("load"),
    }
    if flows["load"] is None and flows["solar"] is not None and flows["import"]:
        flows["load"] = {
            hour: flows["solar"].get(hour, 0)
            + flows["import"].get(hour, 0)
            - flows["export"].get(hour, 0)
            for hour in set(flows["solar"]) | set(flows["import"])
        }
    hourly_price = None
    if "price" in sources:
        found = hourly_watts(series.get(sources["price"][:2], {}), start, end, now)
        hourly_price = {hour: value for hour, (value, _) in found.items()}
    fixed, feed_in = price if price else (None, None)

    def price_at(hour):
        if hourly_price and hour in hourly_price:
            return hourly_price[hour]
        return fixed

    def total(values, first, last):
        return sum(v for h, v in values.items() if first <= h < last)

    bars = []
    for first, last in buckets:
        bar = {"at": first}
        for key, values in flows.items():
            if values is not None:
                bar[key] = round(total(values, first, last), 3)
        bars.append(bar)
    totals = {}
    for key, values in flows.items():
        if values is not None:
            totals[key] = round(total(values, start, end), 3)
    cost = None
    if flows["import"] is not None:
        prices = [(v, price_at(h)) for h, v in flows["import"].items()]
        if prices and all(p is not None for _, p in prices):
            cost = sum(v * p for v, p in prices)
    elif flows["load"] is not None and flows["solar"] is None:
        # no meter at the grid and no solar: all the house used is bought
        prices = [(v, price_at(h)) for h, v in flows["load"].items()]
        if all(p is not None for _, p in prices):
            cost = sum(v * p for v, p in prices)
    if cost is not None:
        totals["cost"] = round(cost, 2)
    if feed_in and flows["export"]:
        totals["revenue"] = round(totals["export"] * feed_in, 2)
    if totals.get("load") and "import" in totals:
        share = 1 - totals["import"] / totals["load"]
        totals["autarky"] = round(min(max(share, 0), 1) * 100)

    used = []
    for item_id, name, device, reading in consumers:
        watt = hourly_watts(series.get((device, reading), {}), start, end, now)
        kwh = sum(_kwh(watt, 1).values())
        if kwh >= 0.01:
            entry = {"id": item_id, "name": name, "kwh": round(kwh, 2)}
            if fixed is not None or hourly_price:
                cost = sum(
                    v * (price_at(h) or 0) for h, v in _kwh(watt, 1).items()
                )
                entry["cost"] = round(cost, 2)
            used.append(entry)
    used.sort(key=lambda e: (-e["kwh"], e["name"].lower()))
    return {
        "bars": bars,
        "totals": totals,
        "consumers": used[:TOP_CONSUMERS],
        "price": "reading" if hourly_price else ("attr" if fixed is not None else None),
        "feed_in": feed_in,
    }


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


CLIMATE_KINDS = ("thermostat", "temperature", "humidity")
_SETPOINT_RE = re.compile(r"(desired|target|set|soll|comfort|eco)", re.IGNORECASE)


def _spark_key(reading):
    name = reading.lower()
    if "humid" in name:
        return "h"
    if "temp" in name and not _SETPOINT_RE.search(name):
        return "t"
    return None


def sparks(trends, devices):
    """timeline trends of a day -> device -> {"t": temperatures, "h": humidity}
    with 24 hourly values (None where nothing is known yet), the first
    matching reading of a device wins"""
    result = {}
    for trend in trends:
        device = trend.get("device")
        key = _spark_key(str(trend.get("reading", "")))
        if device not in devices or key is None:
            continue
        points = [
            p[1] if isinstance(p, list) else p for p in trend.get("points") or []
        ]
        if sum(p is not None for p in points) < 2:
            continue
        result.setdefault(device, {}).setdefault(key, points)
    return result


# --- arranging rooms on a tablet ---

ROOM_ABBREVIATIONS = {
    "wz": "Wohnzimmer",
    "sz": "Schlafzimmer",
    "kz": "Kinderzimmer",
    "az": "Arbeitszimmer",
    "ez": "Esszimmer",
    "gz": "Gästezimmer",
    "bz": "Badezimmer",
    "ku": "Küche",
    "kue": "Küche",
    "fl": "Flur",
    "wc": "WC",
}
_INVALID_ROOM_RE = re.compile(r'[,;|"\\\n\r\t]')


def clean_room(value, allow_empty=False):
    """a room name sent by a tablet -> the name, "" or None when not usable"""
    room = str(value or "").strip()
    if not room:
        return "" if allow_empty else None
    if len(room) > 40 or _INVALID_ROOM_RE.search(room):
        return None
    if room.lower() in HIDDEN_ROOMS:
        return None
    return room


def _plain(text):
    text = str(text).lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    return re.sub(r"[^a-z0-9]", "", text)


def _initials(room):
    words = [w for w in re.split(r"[\s_\-]+", room) if w]
    if len(words) > 1:
        return "".join(_plain(w)[:1] for w in words)
    plain = _plain(room)
    if plain.endswith("zimmer") and len(plain) > 6:
        return plain[0] + "z"
    return None


def _matches(word, room):
    plain = _plain(room)
    if not word or not plain:
        return False
    if word == plain or word == _initials(room):
        return True
    return len(word) >= 3 and len(plain) >= 3 and (
        plain.startswith(word) or word.startswith(plain)
    )


def suggest_room(info, rooms):
    """room for a device from its name or alias: wz_Lampe -> Wohnzimmer,
    existing rooms first"""
    words = _split_words(str(info.get("NAME", ""))) + _split_words(
        str(info.get("alias") or "")
    )
    words = [_plain(w) for w in words]
    for room in rooms:
        if any(_matches(word, room) for word in words):
            return room
    for word in words:
        if word in ROOM_ABBREVIATIONS:
            return ROOM_ABBREVIATIONS[word]
    return ""


IDLE_DAYS = 30


def idle_days(info, now=None):
    """days since the newest reading of the device changed, None: unknown"""
    last = str(info.get("last") or "")
    try:
        then = datetime.datetime.strptime(last[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    now = now or datetime.datetime.now()
    return max(0, (now - then).days)


def arrangement(infos, now=None):
    """rooms with their devices and the devices without a room, for
    arranging the rooms on a tablet. idle: days without any new reading when
    more than IDLE_DAYS"""
    rooms, unassigned = {}, []
    for name in sorted(infos):
        info = infos[name]
        if info.get("TYPE") in SCENE_TYPES:
            continue
        kind = kind_of(info)
        if kind is None:
            continue
        visible = rooms_of(info)
        item = {"id": name, "name": display_name(info), "kind": kind, "rooms": visible}
        days = idle_days(info, now)
        if days is not None and days > IDLE_DAYS:
            item["idle"] = days
        if not visible:
            unassigned.append(item)
        for room in visible:
            rooms.setdefault(room, []).append(item)
    names = sorted(rooms, key=str.lower)
    for item in unassigned:
        item["suggestion"] = suggest_room(infos[item["id"]], names)
    return {
        "rooms": [
            {
                "name": room,
                "devices": sorted(rooms[room], key=lambda i: i["name"].lower()),
            }
            for room in names
        ],
        "unassigned": sorted(unassigned, key=lambda i: i["name"].lower()),
    }


def moved_rooms(value, source, target):
    """attribute room of a device moved from room source ("" when it had none)
    to room target ("" removes it from source), the other rooms stay"""
    rooms = []
    for room in str(value or "").split(","):
        room = room.strip()
        if room and room not in rooms:
            rooms.append(room)
    index = 0
    if source in rooms:
        index = rooms.index(source)
        rooms.remove(source)
    if target and target not in rooms:
        rooms.insert(index, target)
    return ",".join(rooms)


def renamed_layout(layout, source, target):
    """layout of a tablet after renaming a room"""
    result = dict(layout or {})
    for key in ("room_order", "hidden_rooms"):
        if isinstance(result.get(key), list):
            result[key] = [target if r == source else r for r in result[key]]
    order = result.get("tile_order")
    if isinstance(order, dict) and source in order:
        order = dict(order)
        order[target] = order.pop(source)
        result["tile_order"] = order
    return result


# --- floors: rooms grouped by floor, FHEM itself knows no floors ---


def parse_floors(value):
    """attribute floors: 'Ground floor=Kitchen,Living room;Upstairs=Bath'
    -> [{name, rooms}]. A room belongs to the first floor naming it."""
    result, seen = [], set()
    for entry in re.split(r"[;\n]", str(value or "")):
        name, _, rooms = entry.partition("=")
        name = name.strip()[:40]
        if not name or any(f["name"] == name for f in result):
            continue
        members = []
        for room in rooms.split(","):
            room = room.strip()
            if room and room not in seen:
                seen.add(room)
                members.append(room)
        result.append({"name": name, "rooms": members})
    return result


def format_floors(floors):
    parts = []
    for floor in floors:
        name = re.sub(r"[;=,\n]", " ", str(floor.get("name") or "")).strip()[:40]
        rooms = [
            re.sub(r"[;,\n]", " ", str(r)).strip()
            for r in floor.get("rooms") or []
            if str(r).strip()
        ]
        if name:
            parts.append(name + "=" + ",".join(rooms))
    return ";".join(parts)


# --- own notices: "Mail is here" while a device has a value ---

# a notice without =value shows while the reading is one of these
ACTIVE_VALUES = (
    "on",
    "open",
    "opened",
    "1",
    "true",
    "yes",
    "motion",
    "detected",
    "present",
    "alarm",
    "an",
    "ein",
    "offen",
    "ja",
)
_NOTICE_RE = re.compile(r"^([^\s:=;]+)(?::([^\s=;]+))?(?:=(\S+))?(?:\s+(.*))?$")


def parse_notices(value):
    """attribute notices, one per line or separated by ';':
    'Mailbox Mail is here; Basement:water=wet Water in the basement'
    -> [{device, reading, value, text}]"""
    result = []
    seen = set()
    for entry in re.split(r"[;\n]", str(value or "")):
        match = _NOTICE_RE.match(entry.strip())
        if not match:
            continue
        device, reading, wanted, text = match.groups()
        if device in seen:
            continue
        seen.add(device)
        result.append(
            {
                "device": device,
                "reading": reading or "state",
                "value": wanted,
                "text": (text or "").strip()[:80],
            }
        )
    return result


def format_notices(notices):
    parts = []
    for n in notices:
        spec = n["device"]
        if n.get("reading") and n["reading"] != "state":
            spec += ":" + n["reading"]
        if n.get("value"):
            spec += "=" + n["value"]
        text = re.sub(r"[;\n]", " ", n.get("text") or "").strip()
        parts.append(f"{spec} {text}".strip())
    return "; ".join(parts)


def notice_active(notice, info):
    value = (info.get("readings") or {}).get(notice["reading"])
    if value is None:
        return False
    word = str(value).strip().lower()
    if notice.get("value"):
        return word == notice["value"].lower()
    return word in ACTIVE_VALUES


def active_notices(notices, infos, dismissed=None):
    """notices whose device has the value now. dismissed: device -> time of
    the reading when it was ticked off without a command to reset it"""
    dismissed = dismissed or {}
    result = []
    for n in notices:
        info = infos.get(n["device"])
        if info is None or not notice_active(n, info):
            continue
        since = (info.get("times") or {}).get(n["reading"])
        if n["device"] in dismissed and dismissed[n["device"]] == since:
            continue
        rooms = rooms_of(info)
        result.append(
            {
                "id": n["device"],
                "text": n["text"] or display_name(info),
                "room": rooms[0] if rooms else "",
                "since": since,
                "reset": notice_reset(n, info) is not None,
            }
        )
    result.sort(key=lambda x: x["since"] or "", reverse=True)
    return result


def notice_reset(notice, info):
    """set command which takes the notice back, e.g. off of a dummy"""
    sets = kinds.set_names(info.get("sets"))
    if notice["reading"] != "state" or notice.get("value") not in (None, "on"):
        return None
    return "off" if "off" in sets else None


# --- washing machine, dryer and dishwasher, found by their power ---

APPLIANCES = ("washer", "dryer", "dishwasher")
# above this the appliance runs
APPLIANCE_RUN_W = 15
# a program heats or spins: more than a TV, a lamp or a router ever draws
APPLIANCE_PEAK_W = 300
APPLIANCE_MIN_MINUTES = 20
# below APPLIANCE_RUN_W this long: the program is done, used only while
# nothing is learned about a plug yet
APPLIANCE_DONE_MINUTES = 10
# the end is reported this long after the power dropped, when the learned
# programs say that the program ends here
APPLIANCE_QUICK_SECONDS = 30
# a pause the learned programs know may take this long at most
APPLIANCE_MAX_PAUSE = 90 * 60
# shorter dips below APPLIANCE_RUN_W are no pause
APPLIANCE_GAP_SECONDS = 30
# a program shows as running after this, a dryer turning its drum against
# creases or a kettle do not
APPLIANCE_CONFIRM_SECONDS = 180
APPLIANCE_BURST_SECONDS = 90
# power profiles: average power per APPLIANCE_BIN seconds, the last
# APPLIANCE_RUNS programs of each plug are kept
APPLIANCE_BIN = 60
APPLIANCE_RUNS = 12
# mean difference per minute (in square roots of W) up to which a learned
# program is the same program: 1800 against 2000 W is 2.3
APPLIANCE_MATCH = 3.0
# cost of a minute faster or slower than the learned program: while the
# power stays the same, the time since the start tells the position
APPLIANCE_WARP = 0.5
# durations of the last programs used for "about 20 min left"
APPLIANCE_KEEP = 5
# only a hint for the suggestion, the user confirms
APPLIANCE_HINTS = {
    "washer": ("wasch", "washer", "washing", "laundry"),
    "dryer": ("trockn", "dryer", "tumble"),
    "dishwasher": ("spülm", "spuelm", "geschirr", "dishwasher", "dish"),
}


def appliance_guess(name):
    """washer/dryer/dishwasher from the name, None: no idea"""
    text = str(name or "").lower()
    for what, words in APPLIANCE_HINTS.items():
        if any(w in text for w in words):
            return what
    return None


def parse_appliances(value):
    """attribute appliances 'Plug_A:washer,Plug_B:none' -> {device: what}"""
    result = {}
    for entry in re.split(r"[,\s]+", str(value or "")):
        name, _, what = entry.partition(":")
        if name and what in APPLIANCES + ("none",):
            result[name] = what
    return result


def format_appliances(appliances):
    return ",".join(f"{n}:{w}" for n, w in sorted(appliances.items()))


def parse_done_by(value):
    """attribute appliance_done_by 'Plug_A:Door_contact,Plug_B:Motion' ->
    {plug: device which sets the done appliance to seen}"""
    result = {}
    for entry in re.split(r"[,\s]+", str(value or "")):
        name, _, device = entry.partition(":")
        if name and device:
            result[name] = device
    return result


def format_done_by(done_by):
    return ",".join(f"{n}:{d}" for n, d in sorted(done_by.items()) if d)


# kinds offered first on the tablet as "done by": somebody at the appliance
DONE_BY_KINDS = ("contact", "motion")


def done_by_triggers(kind, before, after):
    """a change of the "done by" device which means somebody is at the
    appliance: motion detected, the door opened or closed, a button pressed
    or any other change of the device"""
    if kind == "motion":
        return bool(after.get("occupied")) and not before.get("occupied")
    if kind == "contact":
        return "closed" in after and after.get("closed") != before.get("closed")
    keys = set(before) | set(after)
    keys.discard("since")
    keys.discard("battery_low")
    return any(before.get(k) != after.get(k) for k in keys)


def typical_seconds(durations):
    """median of the last programs, None: none yet"""
    values = sorted(d for d in durations or [] if isinstance(d, (int, float)) and d > 0)
    if not values:
        return None
    return int(values[len(values) // 2])


class ApplianceWatch:
    """follows the power of a plug: a program starts above APPLIANCE_RUN_W
    and ends when the power stays below it. Only programs of at least
    APPLIANCE_MIN_MINUTES with a peak of APPLIANCE_PEAK_W count, so a coffee
    machine, a kettle or a TV are no washing machine.

    Every program is learned as a power profile (average power per minute
    and its pauses). A running program is compared with the learned ones
    (dynamic time warping, a few additions per minute), which gives the
    remaining time of this program and tells a pause of the program from
    its end: when the learned programs end where the power drops, the end
    is reported APPLIANCE_QUICK_SECONDS later."""

    def __init__(self, what=None, runs=None):
        # washer, dryer, dishwasher or None: not known yet
        self.what = what
        # learned programs of this plug, oldest first, see profile()
        self.runs = runs if runs is not None else []
        # last power and length of the last program
        self.power = 0
        self.seconds = 0
        self.ended = None
        # the last finished program
        self.profile = None
        self._reset()

    def _reset(self):
        self.start = None
        self.last_active = None
        self.peak = 0
        # time when the program is done if the power stays low
        self.deadline = None
        self.confirmed = False
        # average power per APPLIANCE_BIN seconds
        self.bins = []
        self._acc = 0.0
        self._time = None
        # pauses: [seconds after start, length, lowest power]
        self.gaps = []
        self._gap_start = None
        self._gap_min = None
        # dynamic time warping against the learned programs
        self._refs = []
        self._rows = []
        self._fed = 0

    @property
    def running(self):
        """a program runs, shown on the tablets"""
        return self.start is not None and self.confirmed

    def feed(self, power, now):
        """'start', 'done', 'short' (no program) or None"""
        if power is None:
            return None
        if self.start is not None:
            self._advance(now)
        before, self.power = self.power, power
        if power >= APPLIANCE_RUN_W:
            if self.start is None:
                self._begin(now)
            elif self._gap_start is not None:
                if now - self._gap_start >= APPLIANCE_GAP_SECONDS:
                    self.gaps.append(
                        [
                            int(self._gap_start - self.start),
                            int(now - self._gap_start),
                            round(self._gap_min, 1),
                        ]
                    )
            self._gap_start = None
            self.deadline = None
            self.last_active = now
            self.peak = max(self.peak, power)
        elif self.start is not None:
            if before >= APPLIANCE_RUN_W or self._gap_start is None:
                # plugs report changes only: it ran until now
                self.last_active = now
                self._gap_start = now
                self._gap_min = power
            else:
                self._gap_min = min(self._gap_min, power)
            self._learn()
            # every new low value may tell more: decide again
            self.deadline = self.last_active + self.done_wait(power)
        return self.tick(now)

    def tick(self, now):
        """the same results as feed, without a new power value"""
        if self.start is None:
            return None
        if not self.confirmed and (
            self.last_active - self.start >= APPLIANCE_CONFIRM_SECONDS
            or (
                self.power >= APPLIANCE_RUN_W
                and now - self.start >= APPLIANCE_CONFIRM_SECONDS
            )
        ):
            self.confirmed = True
            return "start"
        if self.power >= APPLIANCE_RUN_W or self.deadline is None:
            return None
        if now < self.deadline:
            return None
        return self._finish()

    def next_check(self):
        """time when tick has something to tell without a new power value"""
        if self.start is None:
            return None
        times = []
        if not self.confirmed and self.power >= APPLIANCE_RUN_W:
            times.append(self.start + APPLIANCE_CONFIRM_SECONDS)
        if self.deadline is not None and self.power < APPLIANCE_RUN_W:
            times.append(self.deadline)
        return min(times) if times else None

    # --- the profile of the running program ---

    def _begin(self, now):
        self._reset()
        self.start = now
        self._time = now
        # programs of this plug which look like a program: at least 3 minutes
        self._refs = [
            r
            for r in self.runs
            if isinstance(r, dict) and len(r.get("bins") or []) >= 3
        ]
        self._refs = [(r, [_level(b) for b in r["bins"]]) for r in self._refs]
        self._rows = [None] * len(self._refs)
        self._fed = 0

    def _advance(self, now):
        """the power stays the same until the next value"""
        t = self._time
        if t is None or now <= t:
            return
        while t < now:
            bin_end = self.start + (len(self.bins) + 1) * APPLIANCE_BIN
            step = min(now, bin_end) - t
            self._acc += self.power * step
            t += step
            if t >= bin_end:
                self.bins.append(int(round(self._acc / APPLIANCE_BIN)))
                self._acc = 0.0
        self._time = now
        self._learn()

    def _learn(self):
        """compare every new full minute with the learned programs: one row
        of the dynamic time warping per minute and learned program"""
        while self._fed < len(self.bins):
            i = self._fed
            q = _level(self.bins[i])
            for k, (_, ref) in enumerate(self._refs):
                self._rows[k] = _dtw_row(self._rows[k], i, q, ref)
            self._fed += 1

    def matches(self):
        """learned programs like the running one, best first:
        (program, position in seconds, weight from 0 to 1)"""
        if self.start is None or not self._refs:
            return []
        partial = (self._time or self.start) - self.start - self._fed * APPLIANCE_BIN
        partial = max(0, partial)
        if self._fed == 0:
            return [(r, partial, 1.0) for r, _ in self._refs]
        found = []
        for (run, _), row in zip(self._refs, self._rows):
            if not row or not row[1]:
                continue
            lo, costs = row
            j = min(range(len(costs)), key=costs.__getitem__)
            found.append(
                (costs[j] / self._fed, run, (lo + j + 1) * APPLIANCE_BIN + partial)
            )
        found = [f for f in found if f[0] <= APPLIANCE_MATCH]
        if not found:
            return []
        found.sort(key=lambda f: f[0])
        best = found[0][0]
        scale = max(1.0, best)
        result = []
        for distance, run, position in found[:5]:
            weight = math.exp(-(distance - best) / scale)
            if weight >= 0.2:
                result.append((run, position, weight))
        return result

    def predict(self, now=None):
        """{'end': time, 'like': learned program} of the running program,
        None: nothing learned yet"""
        found = self.matches()
        if not found:
            return None
        now = self._time if now is None else now
        ran = (self._time or now) - self.start
        total = sum(w for _, _, w in found)
        left = sum(max(0, r["seconds"] - p) * w for r, p, w in found) / total
        # time since the last value: the program went on meanwhile
        left = max(0, left - max(0, now - (self._time or now)))
        best = found[0][0]
        return {
            "end": int(now + left),
            "ran": int(ran),
            "like": {"at": int(best.get("start", 0)), "seconds": int(best["seconds"])},
        }

    def done_wait(self, power):
        """seconds after the power dropped until the program is done"""
        if not self._refs:
            if self.what == "dryer":
                # a dryer turns its drum all the time, there are no pauses
                return APPLIANCE_QUICK_SECONDS
            return APPLIANCE_DONE_MINUTES * 60
        levels = [g[2] for r, _ in self._refs for g in r.get("gaps", []) if len(g) > 2]
        if levels and min(levels) >= 1.0 and power < 0.6 * min(levels):
            # less than in any pause of the learned programs: off or standby
            return APPLIANCE_QUICK_SECONDS
        found = self.matches()
        if not found:
            # a program not learned yet
            return APPLIANCE_DONE_MINUTES * 60
        total = sum(w for _, _, w in found)
        ending = 0.0
        pauses = []
        for run, position, weight in found:
            near = max(300, 0.1 * run["seconds"])
            here = [g[1] for g in run.get("gaps", []) if abs(g[0] - position) <= near]
            if here:
                pauses.extend(here)
            elif run["seconds"] - position <= max(180, 0.05 * run["seconds"]):
                ending += weight
        if ending > total / 2:
            return APPLIANCE_QUICK_SECONDS
        if pauses:
            # the learned program pauses here
            return min(APPLIANCE_MAX_PAUSE, max(pauses) * 1.3 + 60)
        # an unknown pause: as long as the longest learned one
        longest = [g[1] for r, _ in self._refs for g in r.get("gaps", [])]
        return min(
            APPLIANCE_DONE_MINUTES * 60,
            max(60, 1.5 * max(longest) if longest else 60),
        )

    def _finish(self):
        self._advance(self.last_active)
        seconds = _trim_tail(self.last_active - self.start, self.gaps)
        peak = self.peak
        bins = self.bins[: max(1, -(-int(seconds) // APPLIANCE_BIN))]
        profile = {
            "start": int(self.start),
            "seconds": int(seconds),
            "bins": bins,
            "gaps": [g for g in self.gaps if g[0] + g[1] <= seconds],
        }
        ended = self.last_active
        self._reset()
        self.seconds = seconds
        # the last time with power: somebody at the appliance after this has
        # seen it is done
        self.ended = ended
        if seconds >= APPLIANCE_MIN_MINUTES * 60 and peak >= APPLIANCE_PEAK_W:
            self.profile = profile
            self.runs.append(profile)
            del self.runs[:-APPLIANCE_RUNS]
            return "done"
        return "short"


def _level(power):
    """the difference of 2000 and 2100 W matters less than of 0 and 100 W"""
    return math.sqrt(max(0.0, float(power)))


def _dtw_row(prev, i, q, ref):
    """row i of the open end dynamic time warping of the running program
    against a learned one, within a band: (first column, costs). Each step
    which is not diagonal costs APPLIANCE_WARP."""
    last = len(ref) - 1
    band = max(5, (i + 1) // 4)
    hi = min(last, i + band)
    lo = min(max(0, i - band), hi)
    costs = []
    for j in range(lo, hi + 1):
        if prev is None:
            best = 0.0 if j == 0 else math.inf
        else:
            plo, pcosts = prev
            best = math.inf
            if plo <= j < plo + len(pcosts):
                best = pcosts[j - plo] + APPLIANCE_WARP
            if plo <= j - 1 < plo + len(pcosts):
                best = min(best, pcosts[j - 1 - plo])
        if costs:
            best = min(best, costs[-1] + APPLIANCE_WARP)
        costs.append(abs(q - ref[j]) + best)
    return lo, costs


def _trim_tail(seconds, gaps):
    """a dryer turns the drum for a few seconds every few minutes after the
    program against creases: two or more short bursts at the end are no part
    of the program"""
    bursts = []
    end = seconds
    for offset, length, *_ in reversed(gaps):
        gap_end = offset + length
        if gap_end > end:
            continue
        if end - gap_end > APPLIANCE_BURST_SECONDS:
            break
        bursts.append(offset)
        end = offset
    if len(bursts) >= 2:
        return end
    return seconds
