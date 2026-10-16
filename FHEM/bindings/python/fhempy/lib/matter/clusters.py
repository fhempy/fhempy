"""Mapping of Matter clusters to FHEM readings and set commands.

Attributes are addressed like the Matter server does it:
"<endpoint>/<cluster id>/<attribute id>".
"""

import math

# cluster ids
IDENTIFY = 3
ON_OFF = 6
LEVEL_CONTROL = 8
DESCRIPTOR = 29
BASIC_INFORMATION = 40
POWER_SOURCE = 47
BRIDGED_DEVICE_BASIC_INFORMATION = 57
BOOLEAN_STATE = 69
AIR_QUALITY = 91
SMOKE_CO_ALARM = 92
ELECTRICAL_POWER_MEASUREMENT = 144
ELECTRICAL_ENERGY_MEASUREMENT = 145
DOOR_LOCK = 257
WINDOW_COVERING = 258
THERMOSTAT = 513
FAN_CONTROL = 514
COLOR_CONTROL = 768
ILLUMINANCE_MEASUREMENT = 1024
TEMPERATURE_MEASUREMENT = 1026
PRESSURE_MEASUREMENT = 1027
RELATIVE_HUMIDITY_MEASUREMENT = 1029
OCCUPANCY_SENSING = 1030
CO2_MEASUREMENT = 1037
PM25_MEASUREMENT = 1066
TVOC_MEASUREMENT = 1070
# Eve devices report power and energy in their own cluster
EVE = 0x130AFC01

FEATURE_MAP = 65532

# device types
DEVICE_TYPE_AGGREGATOR = 14
DEVICE_TYPE_BRIDGED_NODE = 19
DEVICE_TYPE_CONTACT_SENSOR = 21
DEVICE_TYPE_LIGHTS = (256, 257, 268, 269)
DEVICE_TYPE_PLUGS = (266, 267)
DEVICE_TYPE_WATER_LEAK_DETECTOR = 67
DEVICE_TYPE_RAIN_SENSOR = 68

THERMOSTAT_MODES = {0: "off", 1: "auto", 3: "cool", 4: "heat", 5: "emergency_heat"}
FAN_MODES = {0: "off", 1: "low", 2: "medium", 3: "high", 4: "on", 5: "auto"}
LOCK_STATES = {0: "not_fully_locked", 1: "locked", 2: "unlocked", 3: "unlatched"}
AIR_QUALITY_STATES = {
    0: "unknown",
    1: "good",
    2: "fair",
    3: "moderate",
    4: "poor",
    5: "very_poor",
    6: "extremely_poor",
}
ALARM_STATES = {0: "ok", 1: "warning", 2: "critical"}

# readings which are used for the state, first one wins
STATE_READINGS = [
    "lock",
    "onoff",
    "position",
    "contact",
    "water_leak",
    "rain",
    "motion",
    "smoke",
    "measured-temp",
]


def _round(value, digits=1):
    return round(value, digits)


def _scaled(factor, digits=1):
    def convert(value, ctx):
        return _round(value / factor, digits)

    return convert


def _enum(mapping):
    def convert(value, ctx):
        return mapping.get(value, str(value))

    return convert


def _on_off(value, ctx):
    return "on" if value else "off"


def _level_to_pct(value, ctx):
    return int(round(value * 100 / 254))


def _hue(value, ctx):
    return int(round(value * 360 / 254))


def _sat(value, ctx):
    return int(round(value * 100 / 254))


def _mireds_to_kelvin(value, ctx):
    if not value:
        return None
    return int(round(1000000 / value))


def _position(value, ctx):
    # Matter: 0 = fully open, 10000 = fully closed
    # FHEM: 100 = open, 0 = closed (like most FHEM shutter modules)
    return int(round(100 - value / 100))


def _illuminance(value, ctx):
    if value <= 0:
        return 0
    return _round(math.pow(10, (value - 1) / 10000), 1)


def _boolean_state(value, ctx):
    if DEVICE_TYPE_WATER_LEAK_DETECTOR in ctx["device_types"]:
        return "leak" if value else "dry"
    if DEVICE_TYPE_RAIN_SENSOR in ctx["device_types"]:
        return "rain" if value else "dry"
    # contact sensor: true = contact (closed)
    return "closed" if value else "open"


def _boolean_state_name(ctx):
    if DEVICE_TYPE_WATER_LEAK_DETECTOR in ctx["device_types"]:
        return "water_leak"
    if DEVICE_TYPE_RAIN_SENSOR in ctx["device_types"]:
        return "rain"
    return "contact"


def _occupancy(value, ctx):
    return "motion" if value & 1 else "nomotion"


def _battery_percent(value, ctx):
    return int(round(value / 2))


def _battery(value, ctx):
    return "ok" if value == 0 else "low"


def _energy(value, ctx):
    if isinstance(value, dict):
        value = value.get("0", value.get("energy"))
    if value is None:
        return None
    # mWh -> kWh
    return _round(value / 1000000, 3)


def _text(value, ctx):
    return str(value)


def _reachable(value, ctx):
    return "online" if value else "offline"


# (cluster, attribute): (reading name or function(ctx), converter)
ATTRIBUTES = {
    (ON_OFF, 0): ("onoff", _on_off),
    (LEVEL_CONTROL, 0): ("pct", _level_to_pct),
    (COLOR_CONTROL, 0): ("hue", _hue),
    (COLOR_CONTROL, 1): ("sat", _sat),
    (COLOR_CONTROL, 7): ("ct", _mireds_to_kelvin),
    (WINDOW_COVERING, 14): ("position", _position),
    (THERMOSTAT, 0): ("measured-temp", _scaled(100)),
    (THERMOSTAT, 17): ("desired-temp-cool", _scaled(100)),
    (THERMOSTAT, 18): ("desired-temp", _scaled(100)),
    (THERMOSTAT, 28): ("mode", _enum(THERMOSTAT_MODES)),
    (DOOR_LOCK, 0): ("lock", _enum(LOCK_STATES)),
    (FAN_CONTROL, 0): ("fan_mode", _enum(FAN_MODES)),
    (FAN_CONTROL, 3): ("fan_pct", _scaled(1, 0)),
    (TEMPERATURE_MEASUREMENT, 0): ("temperature", _scaled(100)),
    (RELATIVE_HUMIDITY_MEASUREMENT, 0): ("humidity", _scaled(100)),
    (ILLUMINANCE_MEASUREMENT, 0): ("illuminance", _illuminance),
    (PRESSURE_MEASUREMENT, 0): ("pressure", _scaled(1)),
    (OCCUPANCY_SENSING, 0): ("motion", _occupancy),
    (BOOLEAN_STATE, 0): (_boolean_state_name, _boolean_state),
    (POWER_SOURCE, 12): ("batteryPercent", _battery_percent),
    (POWER_SOURCE, 14): ("battery", _battery),
    (ELECTRICAL_POWER_MEASUREMENT, 4): ("voltage", _scaled(1000)),
    (ELECTRICAL_POWER_MEASUREMENT, 5): ("current", _scaled(1000, 3)),
    (ELECTRICAL_POWER_MEASUREMENT, 8): ("power", _scaled(1000)),
    (ELECTRICAL_ENERGY_MEASUREMENT, 1): ("energy", _energy),
    (AIR_QUALITY, 0): ("air_quality", _enum(AIR_QUALITY_STATES)),
    (SMOKE_CO_ALARM, 1): ("smoke", _enum(ALARM_STATES)),
    (SMOKE_CO_ALARM, 2): ("co", _enum(ALARM_STATES)),
    (CO2_MEASUREMENT, 0): ("co2", _scaled(1, 0)),
    (PM25_MEASUREMENT, 0): ("pm25", _scaled(1)),
    (TVOC_MEASUREMENT, 0): ("tvoc", _scaled(1)),
    (BASIC_INFORMATION, 1): ("vendor", _text),
    (BASIC_INFORMATION, 3): ("model", _text),
    (BASIC_INFORMATION, 5): ("label", _text),
    (BASIC_INFORMATION, 10): ("firmware", _text),
    (BRIDGED_DEVICE_BASIC_INFORMATION, 1): ("vendor", _text),
    (BRIDGED_DEVICE_BASIC_INFORMATION, 3): ("model", _text),
    (BRIDGED_DEVICE_BASIC_INFORMATION, 5): ("label", _text),
    (BRIDGED_DEVICE_BASIC_INFORMATION, 10): ("firmware", _text),
    (BRIDGED_DEVICE_BASIC_INFORMATION, 17): ("reachable", _reachable),
    (EVE, 0x130A0008): ("voltage", _scaled(1)),
    (EVE, 0x130A0009): ("current", _scaled(1, 3)),
    (EVE, 0x130A000A): ("power", _scaled(1)),
    (EVE, 0x130A000B): ("energy", _scaled(1, 3)),
}

# set commands per cluster: name -> definition
#   command: Matter command (device_command) or write: attribute id
#   options: FHEMWEB widget
SET_COMMANDS = {
    IDENTIFY: {
        "identify": {
            "command": "Identify",
            "payload": {"identifyTime": 15},
            "help": "Lets the device blink or beep for 15 seconds, "
            "so you know which device this is.",
        },
    },
    ON_OFF: {
        "on": {"command": "On", "help": "Switch on."},
        "off": {"command": "Off", "help": "Switch off."},
        "toggle": {"command": "Toggle", "help": "Switch on if off, off if on."},
    },
    LEVEL_CONTROL: {
        "pct": {
            "command": "MoveToLevelWithOnOff",
            "options": "slider,0,1,100",
            "help": "Brightness/level in percent (0-100). 0 switches off.",
        },
    },
    COLOR_CONTROL: {
        "ct": {
            "command": "MoveToColorTemperature",
            "feature": 16,
            "options": "colorpicker,CT,2000,10,6500",
            "help": "Color temperature in Kelvin, "
            "e.g. 2700 = warm white, 6500 = cold white.",
        },
        "hue": {
            "command": "MoveToHue",
            "feature": 1,
            "options": "colorpicker,HUE,0,1,360",
            "help": "Color as hue in degrees (0-360), 0 = red, 120 = green, "
            "240 = blue.",
        },
        "sat": {
            "command": "MoveToSaturation",
            "feature": 1,
            "options": "slider,0,1,100",
            "help": "Color saturation in percent (0 = white, 100 = full color).",
        },
    },
    WINDOW_COVERING: {
        "open": {"command": "UpOrOpen", "help": "Open the cover/shutter."},
        "close": {"command": "DownOrClose", "help": "Close the cover/shutter."},
        "stop": {"command": "StopMotion", "help": "Stop moving."},
        "position": {
            "command": "GoToLiftPercentage",
            "options": "slider,0,1,100",
            "help": "Move to position in percent, 100 = open, 0 = closed.",
        },
    },
    THERMOSTAT: {
        "desired-temp": {
            "write": 18,
            "options": "slider,5,0.5,30,1",
            "help": "Target temperature for heating in °C.",
        },
        "mode": {
            "write": 28,
            "options": "off,heat,cool,auto",
            "help": "Thermostat mode: off, heat, cool or auto. "
            "Not every device supports every mode.",
        },
    },
    DOOR_LOCK: {
        "lock": {"command": "LockDoor", "timed": True, "help": "Lock the door."},
        "unlock": {
            "command": "UnlockDoor",
            "timed": True,
            "help": "Unlock the door.",
        },
    },
    FAN_CONTROL: {
        "fan_mode": {
            "write": 0,
            "options": "off,low,medium,high,auto",
            "help": "Fan speed: off, low, medium, high or auto.",
        },
    },
}


def parse_path(path):
    endpoint, cluster, attribute = path.split("/")
    return int(endpoint), int(cluster), int(attribute)


def endpoints_of(attributes):
    return sorted({parse_path(path)[0] for path in attributes})


def clusters_of(attributes, endpoint):
    return sorted(
        {parse_path(path)[1] for path in attributes if parse_path(path)[0] == endpoint}
    )


def device_types(attributes, endpoint):
    types = set()
    for entry in attributes.get(f"{endpoint}/{DESCRIPTOR}/0") or []:
        if isinstance(entry, dict):
            value = entry.get("0", entry.get("deviceType"))
            if value is not None:
                types.add(value)
    return types


# FHEMWEB icon of a new FHEM device: first match of device type or cluster
ICONS_BY_DEVICE_TYPE = (
    (DEVICE_TYPE_LIGHTS, "light_light"),
    # Matter bridges like Hue, IKEA, Aqara
    ((DEVICE_TYPE_AGGREGATOR,), "mqtt_bridge_1"),
    (DEVICE_TYPE_PLUGS, "message_socket"),
    ((DEVICE_TYPE_CONTACT_SENSOR,), "fts_window_1w"),
    ((DEVICE_TYPE_WATER_LEAK_DETECTOR, DEVICE_TYPE_RAIN_SENSOR), "secur_alarm"),
)
ICONS_BY_CLUSTER = (
    (DOOR_LOCK, "secur_locked"),
    (WINDOW_COVERING, "fts_shutter"),
    (THERMOSTAT, "sani_heating"),
    (FAN_CONTROL, "vent_ventilation"),
    (SMOKE_CO_ALARM, "secur_smoke_detector"),
    (COLOR_CONTROL, "light_light"),
    (ON_OFF, "message_socket"),
    (OCCUPANCY_SENSING, "motion_detector"),
    (BOOLEAN_STATE, "fts_window_1w"),
    (TEMPERATURE_MEASUREMENT, "temp_temperature"),
    (RELATIVE_HUMIDITY_MEASUREMENT, "humidity"),
    (AIR_QUALITY, "vent_ambient_air"),
    (CO2_MEASUREMENT, "vent_ambient_air"),
    (PM25_MEASUREMENT, "vent_ambient_air"),
    (TVOC_MEASUREMENT, "vent_ambient_air"),
    (ILLUMINANCE_MEASUREMENT, "message_light_intensity"),
    (ELECTRICAL_POWER_MEASUREMENT, "measure_power"),
    (PRESSURE_MEASUREMENT, "weather_barometric_pressure"),
)


def default_icon(attributes, endpoints):
    """FHEMWEB icon for the FHEM device of these endpoints, None if unknown"""
    types = set()
    found = set()
    for endpoint in endpoints:
        types |= device_types(attributes, endpoint)
        found.update(clusters_of(attributes, endpoint))
    for device_types_, icon in ICONS_BY_DEVICE_TYPE:
        if types & set(device_types_):
            return icon
    for cluster, icon in ICONS_BY_CLUSTER:
        if cluster in found:
            return icon
    return None


def parts_of(attributes, endpoint):
    return list(attributes.get(f"{endpoint}/{DESCRIPTOR}/3") or [])


def bridged_endpoints(attributes):
    """Endpoints of devices behind a Matter bridge (e.g. Hue, IKEA, Aqara)"""
    result = []
    for endpoint in endpoints_of(attributes):
        if (
            DEVICE_TYPE_BRIDGED_NODE in device_types(attributes, endpoint)
            or f"{endpoint}/{BRIDGED_DEVICE_BASIC_INFORMATION}/17" in attributes
            or f"{endpoint}/{BRIDGED_DEVICE_BASIC_INFORMATION}/5" in attributes
        ):
            result.append(endpoint)
    return result


def device_endpoints(attributes, endpoint=None):
    """Endpoints which belong to one FHEM device.

    endpoint None: the node itself without bridged devices
    endpoint X: the bridged device on endpoint X incl. its parts
    """
    bridged = bridged_endpoints(attributes)
    if endpoint is None:
        excluded = set()
        for ep in bridged:
            excluded.add(ep)
            excluded.update(parts_of(attributes, ep))
        return [ep for ep in endpoints_of(attributes) if ep not in excluded]
    return sorted({endpoint, *parts_of(attributes, endpoint)})


def _reading_candidates(attributes, endpoint):
    ctx = {"device_types": device_types(attributes, endpoint)}
    for path in attributes:
        ep, cluster, attribute = parse_path(path)
        if ep != endpoint or (cluster, attribute) not in ATTRIBUTES:
            continue
        name, converter = ATTRIBUTES[(cluster, attribute)]
        if callable(name):
            name = name(ctx)
        yield (path, name, converter, ctx, endpoint)


def _set_candidates(attributes, endpoint):
    for cluster in clusters_of(attributes, endpoint):
        features = attributes.get(f"{endpoint}/{cluster}/{FEATURE_MAP}")
        for set_name, definition in SET_COMMANDS.get(cluster, {}).items():
            if (
                "feature" in definition
                and isinstance(features, int)
                and not features & definition["feature"]
            ):
                continue
            yield set_name, cluster, definition


class DeviceModel:
    """Readings and set commands of one FHEM device"""

    def __init__(self, attributes, endpoints):
        self.endpoints = endpoints
        self.readings = {}  # path -> (reading, converter, ctx)
        self.sets = {}  # set name -> definition incl. endpoint/cluster
        self._build(attributes)

    def _build(self, attributes):
        reading_endpoints = {}
        set_endpoints = {}
        candidates = []
        for endpoint in self.endpoints:
            for entry in _reading_candidates(attributes, endpoint):
                candidates.append(entry)
                reading_endpoints.setdefault(entry[1], []).append(endpoint)
            for set_name, cluster, definition in _set_candidates(attributes, endpoint):
                if set_name == "identify" and "identify" in set_endpoints:
                    # one identify is enough
                    continue
                set_endpoints.setdefault(set_name, []).append(
                    (endpoint, cluster, definition)
                )

        # the first endpoint gets the plain name, others name_<endpoint>
        for path, name, converter, ctx, endpoint in candidates:
            if reading_endpoints[name][0] != endpoint:
                name = f"{name}_{endpoint}"
            self.readings[path] = (name, converter, ctx)
        for set_name, entries in set_endpoints.items():
            for i, (endpoint, cluster, definition) in enumerate(entries):
                name = set_name if i == 0 else f"{set_name}_{endpoint}"
                self.sets[name] = dict(
                    definition, endpoint=endpoint, cluster=cluster, base=set_name
                )

    def convert(self, path, value):
        """Returns (reading, value) or None if the attribute isn't mapped"""
        if path not in self.readings or value is None:
            return None
        name, converter, ctx = self.readings[path]
        try:
            converted = converter(value, ctx)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
        if converted is None:
            return None
        return name, converted

    def state(self, readings):
        for name in STATE_READINGS:
            if name in readings:
                value = readings[name]
                if name == "position":
                    return {100: "open", 0: "closed"}.get(value, value)
                return value
        # sensors: "T: 21.5 H: 45.0" like other FHEM modules
        parts = [
            f"{short}: {readings[name]}"
            for name, short in (
                ("temperature", "T"),
                ("humidity", "H"),
                ("power", "P"),
                ("illuminance", "L"),
            )
            if name in readings
        ]
        if parts:
            return " ".join(parts)
        return "online"

    def command_args(self, set_name, value):
        """Matter command or attribute write for a set command"""
        definition = self.sets[set_name]
        endpoint = definition["endpoint"]
        cluster = definition["cluster"]
        base = definition["base"]
        if "write" in definition:
            return {
                "kind": "write",
                "attribute_path": f"{endpoint}/{cluster}/{definition['write']}",
                "value": write_value(base, value),
            }
        return {
            "kind": "command",
            "endpoint_id": endpoint,
            "cluster_id": cluster,
            "command_name": definition["command"],
            "payload": command_payload(base, definition, value),
            "timed": definition.get("timed", False),
        }


def _options():
    return {"optionsMask": 0, "optionsOverride": 0}


def command_payload(set_name, definition, value):
    if set_name == "pct":
        level = max(0, min(254, int(round(float(value) * 254 / 100))))
        return {"level": level, "transitionTime": 0, **_options()}
    if set_name == "ct":
        kelvin = max(1000, float(value))
        return {
            "colorTemperatureMireds": int(round(1000000 / kelvin)),
            "transitionTime": 0,
            **_options(),
        }
    if set_name == "hue":
        hue = max(0, min(254, int(round(float(value) * 254 / 360))))
        return {"hue": hue, "direction": 0, "transitionTime": 0, **_options()}
    if set_name == "sat":
        sat = max(0, min(254, int(round(float(value) * 254 / 100))))
        return {"saturation": sat, "transitionTime": 0, **_options()}
    if set_name == "position":
        position = max(0, min(100, float(value)))
        return {"liftPercent100thsValue": int(round((100 - position) * 100))}
    return dict(definition.get("payload", {}))


def write_value(set_name, value):
    if set_name == "desired-temp":
        return int(round(float(value) * 100))
    if set_name == "mode":
        return _reverse(THERMOSTAT_MODES, value)
    if set_name == "fan_mode":
        return _reverse(FAN_MODES, value)
    return value


def _reverse(mapping, value):
    for key, name in mapping.items():
        if name == value:
            return key
    raise ValueError(f"Unknown value {value}, use one of " + ",".join(mapping.values()))
