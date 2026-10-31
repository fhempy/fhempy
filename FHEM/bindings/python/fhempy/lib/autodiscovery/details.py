"""What a found MQTT device can do, shown on its tile in the autodiscovery
dialog before it is created.

Everything comes from the Home Assistant discovery messages of the device
(components, device classes, units, ranges, entity categories, device info),
the current values from its state topics and, for Zigbee2MQTT, the
description and power source from <base>/bridge/devices.

summary() returns plain JSON for discovery.js:
- chips: up to 4 main functions with value, more: count of the others
- groups: "Can do" (controls), "Measures" (sensors), "Settings" (config
  entities), "Status" (diagnostic entities: battery, signal...)
- battery, signal, power: shown next to the title
- device: manufacturer, model, description, firmware, via
- fhem: commands of the MQTT2_DEVICE which is created
"""

import json
import time

from ..core import mqtt_ha

MAX_CHIPS = 4
MAX_OPTIONS = 3
MAX_COMMANDS = 8
# topics whose messages are kept per device
MAX_TOPICS = 20

CONTROL_COMPONENTS = (
    "light",
    "switch",
    "climate",
    "cover",
    "fan",
    "lock",
    "siren",
    "select",
    "number",
    "button",
    "text",
    "valve",
    "humidifier",
    "water_heater",
)
# main measurements first on the tile
CLASS_ORDER = (
    "motion",
    "occupancy",
    "presence",
    "door",
    "window",
    "opening",
    "garage_door",
    "smoke",
    "moisture",
    "temperature",
    "humidity",
    "atmospheric_pressure",
    "pressure",
    "carbon_dioxide",
    "illuminance",
    "power",
    "energy",
)

# icon names of the SVG symbols in discovery.js
ICON_BY_CLASS = {
    "temperature": "therm",
    "humidity": "drop",
    "moisture": "drop",
    "pressure": "gauge",
    "atmospheric_pressure": "gauge",
    "battery": "batt",
    "signal_strength": "sig",
    "illuminance": "sun",
    "light": "sun",
    "power": "bolt",
    "energy": "bolt",
    "current": "bolt",
    "voltage": "bolt",
    "motion": "walk",
    "occupancy": "walk",
    "presence": "walk",
    "door": "door",
    "window": "door",
    "opening": "door",
    "garage_door": "door",
    "smoke": "alarm",
    "gas": "alarm",
    "carbon_monoxide": "alarm",
    "safety": "alarm",
    "vibration": "alarm",
    "tamper": "alarm",
    "carbon_dioxide": "air",
    "pm25": "air",
    "pm10": "air",
    "volatile_organic_compounds": "air",
    "timestamp": "clock",
    "duration": "clock",
}
ICON_BY_COMPONENT = {
    "switch": "power",
    "light": "power",
    "climate": "therm",
    "cover": "cover",
    "fan": "fan",
    "lock": "lock",
    "siren": "alarm",
    "button": "push",
    "select": "list",
    "number": "slider",
    "text": "list",
}
ICON_BY_UNIT = {"lqi": "sig", "dBm": "sig", "%": "drop", "W": "bolt", "kWh": "bolt"}
# binary sensor texts like in Home Assistant: (on, off)
BINARY_TEXT = {
    "motion": ("motion", "clear"),
    "occupancy": ("occupied", "clear"),
    "presence": ("present", "away"),
    "door": ("open", "closed"),
    "window": ("open", "closed"),
    "opening": ("open", "closed"),
    "garage_door": ("open", "closed"),
    "moisture": ("wet", "dry"),
    "smoke": ("smoke", "clear"),
    "gas": ("gas", "clear"),
    "carbon_monoxide": ("detected", "clear"),
    "battery": ("low", "ok"),
    "tamper": ("tampered", "ok"),
    "vibration": ("vibration", "clear"),
    "connectivity": ("connected", "disconnected"),
    "problem": ("problem", "ok"),
    "light": ("light", "dark"),
}
VIA_NAMES = (
    ("zigbee2mqtt", "Zigbee2MQTT"),
    ("esphome", "ESPHome"),
    ("tasmota", "Tasmota"),
)


def _label(object_id, payload_json, fallback):
    name = payload_json.get("name")
    if isinstance(name, str) and name:
        return name
    if name is None and "name" in payload_json:
        # the device itself, e.g. the light of a bulb
        return fallback
    text = str(object_id or fallback).replace("_", " ")
    return text[:1].upper() + text[1:]


def _json_path(template):
    """['a', 'b'] for {{ value_json.a.b }}, [] for {{ value }}, None if the
    template can't be read without Jinja"""
    if not isinstance(template, str) or mqtt_ha.VALUE_TEMPLATE.match(template.strip()):
        return []
    match = mqtt_ha.VALUE_JSON_TEMPLATE.match(template.strip())
    if not match:
        return None
    return [a or b for a, b in mqtt_ha.VALUE_JSON_PART.findall(match.group(1))]


class _Source:
    """Where the current value of an item is: topic and JSON path"""

    def __init__(self, topic, path):
        self.topic = topic
        self.path = path

    def read(self, messages):
        if not self.topic or self.path is None or self.topic not in messages:
            return None
        value = messages[self.topic]
        for key in self.path:
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        return value


def _source(payload_json, topic_key="state_topic", template_key="value_template"):
    return _Source(
        payload_json.get(topic_key), _json_path(payload_json.get(template_key))
    )


def _number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def _fmt(value, unit=""):
    """21.4 °C, 54 %, True -> on"""
    if value is None or isinstance(value, (dict, list)):
        return ""
    if isinstance(value, bool):
        return "on" if value else "off"
    number = _number(value)
    if number is not None and not isinstance(value, str):
        text = (
            f"{number:.2f}".rstrip("0").rstrip(".") if number % 1 else str(int(number))
        )
    else:
        text = str(value)
    if len(text) > 24:
        text = text[:23] + "…"
    return f"{text} {unit}".strip() if unit else text


def _range(low, high, unit=""):
    if low is None or high is None:
        return ""
    return f"{_fmt(low)}–{_fmt(high)} {unit}".strip()


def _on_off(value, on, off):
    if value is None:
        return ""
    if value == on or str(value).lower() == str(on).lower():
        return "on"
    if value == off or str(value).lower() == str(off).lower():
        return "off"
    return _fmt(value)


class _Item:
    def __init__(self, icon, label, source=None, rng="", main=True, fmt=None):
        self.icon = icon
        self.label = label
        self.source = source
        self.range = rng
        self.main = main
        self.fmt = fmt or _fmt

    def public(self, messages):
        raw = self.source.read(messages) if self.source else None
        item = {"icon": self.icon, "label": self.label}
        value = self.fmt(raw) if raw is not None else ""
        if value:
            item["value"] = value
        if self.range:
            item["range"] = self.range
        return item


# --- items of the components ---


def _light_items(label, p):
    schema = p.get("schema", "default")
    modes = p.get("supported_color_modes")
    if not isinstance(modes, list):
        modes = (
            ["brightness"]
            if p.get("brightness") or p.get("brightness_command_topic")
            else []
        )
    if p.get("color_temp_command_topic") and "color_temp" not in modes:
        modes.append("color_temp")
    if schema == "json":
        state = _Source(p.get("state_topic"), ["state"])
        bri = _Source(p.get("state_topic"), ["brightness"])
        ct = _Source(p.get("state_topic"), ["color_temp"])
    else:
        state = _source(p, "state_topic", "state_value_template")
        bri = _source(p, "brightness_state_topic", "brightness_value_template")
        ct = _source(p, "color_temp_state_topic", "color_temp_value_template")
    on = p.get("payload_on", mqtt_ha.DEFAULT_PAYLOAD_ON)
    off = p.get("payload_off", mqtt_ha.DEFAULT_PAYLOAD_OFF)
    items = [_Item("power", label, state, fmt=lambda v: _on_off(v, on, off))]
    if any(mode in mqtt_ha.BRIGHTNESS_MODES for mode in modes):
        scale = _number(p.get("brightness_scale")) or mqtt_ha.DEFAULT_BRIGHTNESS_SCALE
        items.append(
            _Item("sun", "Brightness", bri, "0–100 %", fmt=lambda v: _percent(v, scale))
        )
    if "color_temp" in modes:
        items.append(
            _Item("ctemp", "Color temperature", ct, _kelvin_range(p), fmt=_kelvin)
        )
    if any(mode in mqtt_ha.COLOR_MODES for mode in modes):
        items.append(_Item("palette", "Color"))
    effects = p.get("effect_list")
    if isinstance(effects, list) and effects:
        items.append(_Item("spark", "Effects", rng=_options(effects), main=False))
    return items


def _percent(value, scale):
    number = _number(value)
    if number is None:
        return ""
    return f"{round(number * 100 / scale)} %"


def _kelvin(mireds):
    number = _number(mireds)
    if not number:
        return ""
    return f"{round(1000000 / number / 50) * 50} K"


def _kelvin_range(p):
    if p.get("color_temp_kelvin"):
        low = p.get("min_kelvin", mqtt_ha.DEFAULT_MIN_KELVIN)
        high = p.get("max_kelvin", mqtt_ha.DEFAULT_MAX_KELVIN)
    else:
        low = 1000000 / (_number(p.get("max_mireds")) or mqtt_ha.DEFAULT_MAX_MIREDS)
        high = 1000000 / (_number(p.get("min_mireds")) or mqtt_ha.DEFAULT_MIN_MIREDS)
    low, high = round(low / 100) * 100, round(high / 100) * 100
    return f"{low}–{high} K"


def _options(values):
    values = [str(v) for v in values]
    text = ", ".join(values[:MAX_OPTIONS])
    if len(values) > MAX_OPTIONS:
        text += f", +{len(values) - MAX_OPTIONS}"
    return text


def _switch_items(label, p):
    on = p.get("state_on", p.get("payload_on", mqtt_ha.DEFAULT_PAYLOAD_ON))
    off = p.get("state_off", p.get("payload_off", mqtt_ha.DEFAULT_PAYLOAD_OFF))
    return [_Item("power", label, _source(p), fmt=lambda v: _on_off(v, on, off))]


def _climate_items(label, p):
    unit = "°C" if p.get("temperature_unit", "C") == "C" else "°F"
    items = [
        _Item(
            "therm",
            "Target temperature",
            _source(p, "temperature_state_topic", "temperature_state_template"),
            _range(
                p.get("min_temp", mqtt_ha.DEFAULT_MIN_TEMP),
                p.get("max_temp", mqtt_ha.DEFAULT_MAX_TEMP),
                unit,
            ),
            fmt=lambda v: _fmt(v, unit),
        )
    ]
    if p.get("current_temperature_topic"):
        items.insert(
            0,
            _Item(
                "therm",
                "Temperature",
                _source(p, "current_temperature_topic", "current_temperature_template"),
                fmt=lambda v: _fmt(v, unit),
            ),
        )
    if p.get("mode_command_topic"):
        modes = p.get("modes") or mqtt_ha.DEFAULT_HVAC_MODES
        items.append(
            _Item(
                "list",
                "Mode",
                _source(p, "mode_state_topic", "mode_state_template"),
                _options(modes),
            )
        )
    return items


def _cover_items(label, p):
    items = [_Item("cover", label, _source(p), "open, close, stop")]
    if p.get("position_topic") or p.get("set_position_topic"):
        items.append(
            _Item(
                "slider",
                "Position",
                _source(p, "position_topic", "position_template"),
                "0–100 %",
                fmt=lambda v: _fmt(v, "%"),
            )
        )
    return items


def _value_items(component, label, p):
    unit = p.get("unit_of_measurement") or ""
    icon = _icon(component, p)
    source = _source(p)
    if component == "binary_sensor":
        texts = BINARY_TEXT.get(p.get("device_class"), ("on", "off"))
        on = p.get("payload_on", mqtt_ha.DEFAULT_PAYLOAD_ON)
        off = p.get("payload_off", mqtt_ha.DEFAULT_PAYLOAD_OFF)

        def fmt(v):
            text = _on_off(v, on, off)
            return {"on": texts[0], "off": texts[1]}.get(text, text)

        return [_Item(icon, label, source, fmt=fmt)]
    rng = ""
    if component == "number":
        rng = _range(p.get("min", 1), p.get("max", 100), unit)
    elif component == "select":
        rng = _options(p.get("options") or [])
    elif component == "button":
        source = None
    return [_Item(icon, label, source, rng, fmt=lambda v: _fmt(v, unit))]


def _icon(component, p):
    device_class = p.get("device_class")
    if device_class in ICON_BY_CLASS:
        return ICON_BY_CLASS[device_class]
    if component in ICON_BY_COMPONENT:
        return ICON_BY_COMPONENT[component]
    return ICON_BY_UNIT.get(p.get("unit_of_measurement"), "dot")


def _group(component, p):
    category = p.get("entity_category")
    if category == "config":
        return "settings"
    if (
        category == "diagnostic"
        or p.get("device_class") in mqtt_ha.DIAGNOSTIC_CLASSES
        or p.get("unit_of_measurement") in mqtt_ha.DIAGNOSTIC_UNITS
    ):
        return "status"
    if component in CONTROL_COMPONENTS:
        return "control"
    return "measure"


def _items(component, object_id, p):
    if component == "light":
        return _light_items(_label(object_id, p, "On / off"), p)
    if component in ("switch", "fan", "siren"):
        return _switch_items(_label(object_id, p, "On / off"), p)
    if component == "lock":
        return _value_items(component, _label(object_id, p, "Lock"), p)
    if component == "climate":
        return _climate_items(_label(object_id, p, "Thermostat"), p)
    if component == "cover":
        return _cover_items(_label(object_id, p, "Cover"), p)
    return _value_items(component, _label(object_id, p, component.capitalize()), p)


# --- the device ---


def ieee_of(device_id):
    """0x00158d0001a2b3c4 of zigbee2mqtt_0x00158d0001a2b3c4"""
    _, _, ieee = str(device_id).rpartition("_")
    return ieee if ieee.startswith("0x") else ""


def _via(entities, device_id):
    text = str(device_id).lower()
    for _, _, p in entities:
        dev = p.get("device") or {}
        via = str(dev.get("via_device") or "").lower()
        origin = p.get("origin") or {}
        text += " " + via + " " + str(origin.get("name", "")).lower()
    for key, name in VIA_NAMES:
        if key in text:
            return name
    return ""


def _device_info(entities, device_id, bridge):
    dev = {}
    for _, _, p in entities:
        if isinstance(p.get("device"), dict):
            dev = p["device"]
            break
    info = {
        "manufacturer": str(dev.get("manufacturer") or ""),
        "model": str(dev.get("model") or ""),
        "firmware": str(dev.get("sw_version") or ""),
        "via": _via(entities, device_id),
        "description": str(bridge.get("description") or ""),
    }
    return {k: v for k, v in info.items() if v}


def _commands(entities):
    try:
        attrs = mqtt_ha.generate_attributes(list(entities))
    except Exception:
        return []
    names = []
    lines = attrs.get("setList") or []
    if isinstance(lines, str):
        lines = lines.splitlines()
    for line in lines:
        name = line.split(" ", 1)[0].split(":", 1)[0]
        if name and name not in names:
            names.append(name)
    return names


class DeviceDetails:
    """Collects the messages of an offered device, summary() for the
    tile"""

    def __init__(self):
        # topic -> last message (JSON decoded if possible)
        self.messages = {}
        self.last_message = 0

    @staticmethod
    def state_topics(entities):
        topics = set()
        for _, _, p in entities:
            for key, value in p.items():
                if (
                    isinstance(value, str)
                    and key.endswith("_topic")
                    and key not in mqtt_ha.OTHER_TOPICS
                    and "command" not in key
                    and not key.startswith("set_")
                    and " " not in value
                    and "+" not in value
                    and "#" not in value
                ):
                    topics.add(value)
        return topics

    def message(self, topic, payload):
        """True if it is a new value"""
        if topic not in self.messages and len(self.messages) >= MAX_TOPICS:
            return False
        try:
            value = json.loads(payload)
        except (ValueError, TypeError):
            value = (
                payload.decode(errors="replace")
                if isinstance(payload, bytes)
                else payload
            )
        self.last_message = time.time()
        if self.messages.get(topic) == value:
            return False
        self.messages[topic] = value
        return True

    def summary(self, entities, device_id, bridge=None):
        """bridge: Zigbee2MQTT bridge/devices entry (description,
        power_source)"""
        bridge = bridge or {}
        groups = {"control": [], "measure": [], "settings": [], "status": []}
        battery = signal = None
        for component, object_id, p in sorted(entities, key=_entity_order):
            group = _group(component, p)
            for item in _items(component, object_id, p):
                public = item.public(self.messages)
                groups[group].append((item, public))
                if p.get("device_class") == "battery" and component == "sensor":
                    battery = public.get("value", battery)
                elif _icon(component, p) == "sig":
                    signal = public.get("value", signal)
        main = [entry for g in ("control", "measure") for entry in groups[g]]
        chips = [public for item, public in main if item.main][:MAX_CHIPS]
        result = {
            "chips": chips,
            "more": len(main) - len(chips),
            "groups": [
                {"title": title, "items": [public for _, public in groups[key]]}
                for key, title in (
                    ("control", "Can do"),
                    ("measure", "Measures"),
                    ("settings", "Settings"),
                    ("status", "Status"),
                )
                if groups[key]
            ],
            "device": _device_info(entities, device_id, bridge),
            "commands": _commands(entities)[:MAX_COMMANDS],
        }
        power = bridge.get("power_source", "")
        if battery is not None:
            result["battery"] = battery
        elif power and "battery" not in power.lower():
            result["power"] = "mains"
        if signal is not None:
            # Zigbee link quality 0-255 without unit next to the title
            result["signal"] = signal.removesuffix(" lqi")
        if self.last_message:
            result["last_message"] = int(self.last_message)
        return result


def _entity_order(entity):
    """the device itself (name null) first, then the main measurements"""
    component, object_id, p = entity
    primary = p.get("name", "") is None
    device_class = p.get("device_class")
    rank = CLASS_ORDER.index(device_class) if device_class in CLASS_ORDER else 99
    return (
        not primary,
        component not in ("light", "switch", "climate", "cover"),
        rank,
        str(object_id),
    )


def bridge_devices(payload):
    """ieee -> {description, power_source} of a Zigbee2MQTT
    bridge/devices message"""
    try:
        devices = json.loads(payload)
    except (ValueError, TypeError):
        return {}
    result = {}
    if not isinstance(devices, list):
        return result
    for dev in devices:
        if not isinstance(dev, dict) or not dev.get("ieee_address"):
            continue
        definition = dev.get("definition") or {}
        result[str(dev["ieee_address"]).lower()] = {
            "description": definition.get("description") or "",
            "power_source": dev.get("power_source") or "",
        }
    return result
