"""DOIFs with inputs (attributes readingList and setList) on the tablets.
The setList says which values a person may change and how (slider, list,
time, text), the readings of the same name hold the current values.

Pure functions, no FHEM access.
"""

import re

from ..matter_bridge import devices as kinds

INPUT_TYPES = ("DOIF",)
# DOIF commands which are no inputs
DOIF_COMMANDS = (
    "disable",
    "enable",
    "initialize",
    "checkall",
    "cmd",
    "on",
    "off",
)
MAX_INPUTS = 12
MAX_TEXT = 100
_TIME = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?$")
_NAME = re.compile(r"^[\w\-.]+$")


def has_inputs(info):
    return info.get("TYPE") in INPUT_TYPES and bool(parse(info))


def _widget(name, spec):
    parts = spec.split(",")
    kind = parts[0].lower() if parts else ""
    if kind in ("slider", "knob"):
        numbers = [kinds.number(p) for p in parts[1:4]]
        low, step, high = (numbers + [None, None, None])[:3]
        low = 0 if low is None else low
        step = 1 if not step else step
        high = 100 if high is None else high
        return {"name": name, "type": "slider", "min": low, "max": high, "step": step}
    if kind == "time":
        return {"name": name, "type": "time"}
    if kind in ("noarg", ""):
        return {"name": name, "type": "button"}
    if kind.startswith("textfield") or kind == "colorpicker":
        return {"name": name, "type": "text"}
    if kind in ("select", "multiple", "multiple-strict"):
        parts = parts[1:]
    options = [p for p in parts if p]
    if not options:
        return {"name": name, "type": "text"}
    if {o.lower() for o in options} <= {"on", "off"}:
        return {"name": name, "type": "switch", "options": options}
    return {"name": name, "type": "select", "options": options}


def parse(info):
    """the inputs of a DOIF from its setList attribute"""
    attrs = info.get("attrs") or {}
    text = str(attrs.get("setList") or "")
    result = []
    for entry in text.split():
        name, _, spec = entry.partition(":")
        if not _NAME.match(name) or name in DOIF_COMMANDS:
            continue
        if any(i["name"] == name for i in result):
            continue
        result.append(_widget(name, spec))
        if len(result) >= MAX_INPUTS:
            break
    return result


def reading_names(info):
    return tuple(i["name"] for i in parse(info))


def state(info):
    readings = info.get("readings") or {}
    values = {}
    for item in parse(info):
        if item["type"] != "button" and item["name"] in readings:
            values[item["name"]] = readings[item["name"]]
    return {"values": values, "state": readings.get("state")}


def _slider_value(item, text):
    number = kinds.number(text)
    if number is None:
        raise ValueError(f"not a number: {text}")
    number = max(item["min"], min(item["max"], number))
    number = round(round(number / item["step"]) * item["step"], 6)
    return str(int(number)) if float(number).is_integer() else str(number)


def _option_value(item, text):
    if text not in item["options"]:
        raise ValueError(f"not an option: {text}")
    return text


def _time_value(item, text):
    if not _TIME.match(text):
        raise ValueError(f"no time: {text}")
    return text


def _text_value(item, text):
    if "\n" in text or "\r" in text or len(text) > MAX_TEXT:
        raise ValueError("text too long")
    return text


CHECKS = {
    "slider": _slider_value,
    "select": _option_value,
    "switch": _option_value,
    "time": _time_value,
    "text": _text_value,
}


def _check(item, value):
    """the value as FHEM gets it, ValueError if it doesn't fit the input"""
    if item["type"] == "button":
        return None
    text = str("" if value is None else value).strip()
    return CHECKS.get(item["type"], _text_value)(item, text)


def command(info, name, value):
    """FHEM set arguments for a new value of an input"""
    item = next((i for i in parse(info) if i["name"] == name), None)
    if item is None:
        return []
    checked = _check(item, value)
    if checked is None:
        return [name]
    if checked == "":
        return []
    return [f"{name} {checked}"]
