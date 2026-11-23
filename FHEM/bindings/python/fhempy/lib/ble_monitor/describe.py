"""What a device is and its state, from the values of the BLE parser.

The parser recognizes a device by the content of its advertisements (e.g.
manufacturer data of a known company id with a known layout), not by its
name. Its result carries the model ("type") and the parser ("firmware").
Only stdlib and upstream tables, autodiscovery uses it too.
"""

import re

from .upstream_const import MANUFACTURER_DICT, MEASUREMENT_DICT

# "Xiaomi (MiBeacon V3 encrypted)", "BTHome V2", "Ruuvitag V5" -> maker
_FIRMWARE_SUFFIX = re.compile(r"\s*(\(.*\)|V\d.*)$")

# kind of device from what it measures, first match wins
_KINDS = (
    ("toothbrush", "Toothbrush"),
    ("weight", "Scale"),
    ("impedance", "Scale"),
    ("conductivity", "Plant sensor"),
    ("moisture", "Plant sensor"),
    ("temperature", "Thermometer"),
    ("motion", "Motion sensor"),
    ("opening", "Door/window sensor"),
    ("button", "Button"),
    ("remote", "Remote"),
)

# numeric readings shown in state, in this order
_STATE_VALUES = (
    ("temperature", "T"),
    ("humidity", "H"),
    ("moisture", "M"),
    ("conductivity", "C"),
    ("illuminance", "L"),
    ("co2", "CO2"),
    ("pm2.5", "PM2.5"),
    ("weight", "W"),
)

# binary readings shown in state: reading, text for 1, text for 0
_STATE_BINARY = (
    ("motion", "motion", "no motion"),
    ("opening", "open", "closed"),
    ("moisture_detected", "wet", "dry"),
    ("smoke", "smoke", "no smoke"),
    ("light", "light", "dark"),
)

STATE_NO_DATA = "waiting for data"
STATE_ACTIVE = "active"


def reading_name(key):
    """FHEM readings must not contain spaces ("battery low")."""
    return str(key).replace(" ", "_")


def _text(value):
    return "" if value is None else str(value).strip()


def manufacturer(values):
    """Maker of the device, '' if unknown."""
    model = _text(values.get("type"))
    if model in MANUFACTURER_DICT:
        return MANUFACTURER_DICT[model]
    return _FIRMWARE_SUFFIX.sub("", _text(values.get("firmware")))


def label(values):
    """Readable name like 'Oral-B IO Series 7', '' if the model is unknown."""
    model = _text(values.get("type"))
    if not model:
        return ""
    maker = manufacturer(values)
    if not maker or model.lower().startswith(maker.lower()):
        return model
    return f"{maker} {model}"


def kind(values):
    """'Toothbrush', 'Thermometer', ... from what the model measures."""
    model = _text(values.get("type"))
    measured = set()
    for group in MEASUREMENT_DICT.get(model, []):
        measured.update(group)
    measured.update(reading_name(key) for key in values)
    for key, text in _KINDS:
        if key in measured:
            return text
    return ""


def _number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else number


def state(values):
    """Short state for FHEM: the toothbrush state, 'T: 21.5 H: 45' for
    sensors, 'open'/'closed', ... values: readings (spaces or underscores)."""
    values = {
        reading_name(key): value for key, value in values.items() if key != "state"
    }
    if not values:
        return STATE_NO_DATA
    toothbrush = _text(values.get("toothbrush_state"))
    if toothbrush:
        return toothbrush
    parts = []
    for key, short in _STATE_VALUES:
        number = _number(values.get(key))
        if number is not None:
            parts.append(f"{short}: {number}")
    if parts:
        return " ".join(parts)
    for key, on, off in _STATE_BINARY:
        number = _number(values.get(key))
        if number is not None:
            return on if number else off
    for key in ("button", "remote", "switch"):
        text = _text(values.get(key))
        if text:
            return text
    return STATE_ACTIVE
