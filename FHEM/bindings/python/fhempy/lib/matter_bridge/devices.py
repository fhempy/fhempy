"""Which Matter device a FHEM device becomes and how its readings and the
commands from Matter apps are converted. Pure functions, no FHEM access."""

import re

TYPES = (
    "switch",
    "outlet",
    "light",
    "dimmer",
    "blind",
    "thermostat",
    "lock",
    "contact",
    "motion",
    "temperature",
    "humidity",
)

TYPE_HELP = {
    "switch": "switch (on/off)",
    "outlet": "plug (on/off)",
    "light": "light (on/off)",
    "dimmer": "dimmable light (on/off, brightness)",
    "blind": "blind/shutter (position, stop)",
    "thermostat": "thermostat (temperature, desired temperature)",
    "lock": "door lock (lock/unlock)",
    "contact": "door/window contact",
    "motion": "motion sensor",
    "temperature": "temperature sensor",
    "humidity": "humidity sensor",
}

# genericDeviceType (used by homebridge, alexa-fhem, gassistant-fhem)
GENERIC_DEVICE_TYPES = {
    "switch": "switch",
    "outlet": "outlet",
    "light": "light",
    "blind": "blind",
    "shutter": "blind",
    "window": "blind",
    "thermostat": "thermostat",
    "lock": "lock",
    "contact": "contact",
    "door": "contact",
    "garage": "contact",
    "motion": "motion",
    "occupancy": "motion",
    "temperature": "temperature",
    "humidity": "humidity",
}

LEVEL_SETS = ("pct", "dim", "brightness", "level")
POSITION_SETS = ("pct", "position")
TARGET_SETS = ("desired-temp", "desiredTemperature", "desired", "setpoint")
CURRENT_READINGS = (
    "measured-temp",
    "temperature",
    "measuredTemperature",
    "actualTemperature",
    "currentTemperature",
)
LIGHT_WORDS = ("licht", "lampe", "leuchte", "light", "lamp", "hue", "bulb", "led")
# modules where position 0 means open (100 = closed)
INVERTED_POSITION_TYPES = ("ROLLO",)

ON_VALUES = ("on", "an", "ein", "1", "true", "yes", "open")
OFF_VALUES = ("off", "aus", "0", "false", "no", "closed")
MOTION_VALUES = ("motion", "on", "1", "true", "yes", "detected", "occupied")
NO_MOTION_VALUES = (
    "nomotion",
    "no_motion",
    "off",
    "0",
    "false",
    "no",
    "clear",
    "unoccupied",
)
OPEN_VALUES = ("open", "opened", "offen", "tilted", "gekippt", "on", "1", "true")
CLOSED_VALUES = ("closed", "close", "geschlossen", "off", "0", "false")
LOCKED_VALUES = ("locked", "lock", "verriegelt", "zu")
UNLOCKED_VALUES = ("unlocked", "unlock", "entriegelt", "open", "auf")

NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")


def set_names(sets):
    """'on off pct:slider,0,1,100' -> {'on', 'off', 'pct'}"""
    return {entry.split(":")[0] for entry in (sets or "").split() if entry}


def number(value):
    if value is None:
        return None
    m = NUMBER.search(str(value))
    if m is None:
        return None
    return float(m.group(0).replace(",", "."))


def _first(names, available):
    for name in names:
        if name in available:
            return name
    return None


def _word(value):
    return str(value or "").strip().split(" ")[0].lower()


def _detect_actuator(info, sets, dimmable):
    if _first(TARGET_SETS, sets):
        return "thermostat"
    if "lock" in sets and "unlock" in sets:
        return "lock"
    moves = sets & {"up", "down", "open", "close", "closes", "opens", "stop"}
    if _first(POSITION_SETS, sets) and moves:
        return "blind"
    if "on" in sets and "off" in sets:
        if dimmable:
            return "dimmer"
        text = " ".join(
            (info.get("TYPE", ""), info.get("NAME", ""), info.get("alias", ""))
        ).lower()
        if any(word in text for word in LIGHT_WORDS):
            return "light"
        return "switch"
    return None


def _detect_sensor(readings):
    if "contact" in readings:
        return "contact"
    if "motion" in readings:
        return "motion"
    if _first(CURRENT_READINGS, readings):
        return "temperature"
    if "humidity" in readings:
        return "humidity"
    return None


def detect_type(info):
    """Matter type of a FHEM device or None if it can't be bridged.
    info: TYPE, NAME, alias, sets, readings (dict), attrs (dict)"""
    attrs = info.get("attrs", {})
    wanted = attrs.get("matterType", "")
    if wanted in TYPES:
        return wanted

    sets = set_names(info.get("sets"))
    dimmable = _first(LEVEL_SETS, sets) is not None
    generic = GENERIC_DEVICE_TYPES.get(attrs.get("genericDeviceType", "").lower())
    if generic == "light" and dimmable:
        return "dimmer"
    if generic is not None:
        return generic
    return _detect_actuator(info, sets, dimmable) or _detect_sensor(
        info.get("readings", {})
    )


def endpoint_id(name):
    # matter.js doesn't allow dots in endpoint ids
    return name.replace(".", "_")


def endpoints(info):
    """Matter endpoints of a FHEM device: [{id, type, name}]"""
    device_type = detect_type(info)
    if device_type is None:
        return []
    attrs = info.get("attrs", {})
    label = attrs.get("matterName") or info.get("alias") or info["NAME"]
    return [
        {
            "id": endpoint_id(info["NAME"]),
            "type": device_type,
            "name": label,
            "parts": extra_sensors(device_type, info),
        }
    ]


SENSOR_TYPES = ("contact", "motion", "temperature", "humidity")
# a thermostat shows the measured temperature itself
COVERED_SENSORS = {"thermostat": ("temperature",)}


def _has_sensor(sensor, readings):
    if sensor == "temperature":
        return _first(CURRENT_READINGS, readings) is not None
    return sensor in readings


def extra_sensors(device_type, info):
    """Sensors of a FHEM device in addition to its main function, e.g. the
    humidity of a temperature sensor. They become parts of the same Matter
    device, one FHEM device is one device in the apps."""
    readings = info.get("readings", {})
    covered = (device_type,) + COVERED_SENSORS.get(device_type, ())
    return [
        sensor
        for sensor in SENSOR_TYPES
        if sensor not in covered and _has_sensor(sensor, readings)
    ]


def _position_inverted(info):
    inverted = info.get("attrs", {}).get("matterInvert", "")
    if inverted in ("0", "1"):
        return inverted == "1"
    return info.get("TYPE") in INVERTED_POSITION_TYPES


def _is_on(value, level=None):
    word = _word(value)
    if word in ON_VALUES or word.startswith("on") or word.startswith("dim"):
        return True
    if word in OFF_VALUES or word.startswith("off"):
        return False
    if level is not None:
        return level > 0
    return None


def _choice(value, true_values, false_values):
    word = _word(value)
    if word in true_values:
        return True
    if word in false_values:
        return False
    return None


def _reading(info, *names):
    readings = info.get("readings", {})
    for name in names:
        if name in readings:
            return readings[name]
    return None


def _percent(value):
    value = number(value)
    return None if value is None else max(0, min(100, round(value)))


def _onoff_state(info):
    return {"on": _is_on(_reading(info, "state"))}


def _dimmer_state(info):
    level = _percent(_reading(info, "pct", "dim", "brightness", "level"))
    return {"on": _is_on(_reading(info, "state"), level), "level": level}


def _blind_state(info):
    position = _percent(_reading(info, "pct", "position"))
    if position is not None and _position_inverted(info):
        position = 100 - position
    return {"position": position}


def _thermostat_state(info):
    return {
        "current": number(_reading(info, *CURRENT_READINGS)),
        "target": number(_reading(info, *TARGET_SETS)),
    }


def _lock_state(info):
    value = _reading(info, "lock", "lockState", "state")
    return {"locked": _choice(value, LOCKED_VALUES, UNLOCKED_VALUES)}


def _contact_state(info):
    value = _reading(info, "contact", "state")
    is_open = _choice(value, OPEN_VALUES, CLOSED_VALUES)
    return {"closed": None if is_open is None else not is_open}


def _motion_state(info):
    value = _reading(info, "motion", "occupancy", "state")
    return {"occupied": _choice(value, MOTION_VALUES, NO_MOTION_VALUES)}


def _temperature_state(info):
    return {"temperature": number(_reading(info, *CURRENT_READINGS))}


def _humidity_state(info):
    return {"humidity": number(_reading(info, "humidity"))}


STATES = {
    "switch": _onoff_state,
    "outlet": _onoff_state,
    "light": _onoff_state,
    "dimmer": _dimmer_state,
    "blind": _blind_state,
    "thermostat": _thermostat_state,
    "lock": _lock_state,
    "contact": _contact_state,
    "motion": _motion_state,
    "temperature": _temperature_state,
    "humidity": _humidity_state,
}


def state(device_type, info):
    """Matter state (see bridge.mjs) from the readings of the FHEM device"""
    convert = STATES.get(device_type)
    return convert(info) if convert else {}


def endpoint_state(endpoint, info):
    """state of the main function and all parts (their keys don't overlap)"""
    result = {}
    for device_type in [endpoint["type"]] + endpoint.get("parts", []):
        result.update(state(device_type, info))
    return result


def _format(value):
    value = round(value, 1)
    return str(int(value)) if value == int(value) else str(value)


def _onoff_commands(info, sets, command):
    if "on" in command:
        return ["on" if command["on"] else "off"]
    return []


def _dimmer_commands(info, sets, command):
    if command.get("on") is False:
        return ["off"]
    level_set = _first(LEVEL_SETS, sets)
    if "level" in command and level_set is not None:
        return [f"{level_set} {command['level']}"]
    if command.get("on"):
        return ["on"]
    return []


def _blind_commands(info, sets, command):
    if command.get("stop"):
        return ["stop"] if "stop" in sets else []
    position_set = _first(POSITION_SETS, sets)
    if "position" not in command or position_set is None:
        return []
    position = command["position"]
    if _position_inverted(info):
        position = 100 - position
    return [f"{position_set} {position}"]


def _thermostat_commands(info, sets, command):
    target_set = _first(TARGET_SETS, sets)
    if "target" in command and target_set is not None:
        return [f"{target_set} {_format(command['target'])}"]
    return []


def _lock_commands(info, sets, command):
    if "locked" in command:
        return ["lock" if command["locked"] else "unlock"]
    return []


COMMANDS = {
    "switch": _onoff_commands,
    "outlet": _onoff_commands,
    "light": _onoff_commands,
    "dimmer": _dimmer_commands,
    "blind": _blind_commands,
    "thermostat": _thermostat_commands,
    "lock": _lock_commands,
}


def fhem_commands(device_type, info, command):
    """FHEM set arguments for a command of a Matter app, e.g. ['pct 50']"""
    convert = COMMANDS.get(device_type)
    if convert is None:
        return []
    return convert(info, set_names(info.get("sets")), command)
