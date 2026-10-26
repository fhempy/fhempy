"""Home Assistant MQTT discovery: parses the config messages and creates
MQTT2_DEVICEs with readingList/setList. Used by mqtt_ha_discovery and
autodiscovery, it needs no MQTT library.

The device is set up the way Home Assistant's MQTT integration uses the
discovery config:
- JSON state messages (Zigbee2MQTT, JSON lights of ESPHome) become one reading
  per value (json2nameValue), other state topics one reading per entity
- lights (schema json and default) get on/off, brightness, color_temp, color
  and effect like the light card of Home Assistant
- switch, select, number and button entities get their set commands
- availability (availability_topic or the availability list, mode all/any/
  latest) is the reading availability: online/offline
"""

import json
import re

from .. import fhem, utils
from .mqtt_ha_abbreviations import ABBREVIATIONS, DEVICE_ABBREVIATIONS

# keys of a device discovery payload which are not inherited by its components
DEVICE_DISCOVERY_KEYS = ("device", "origin", "components")
# FHEM reading names may only contain these characters
INVALID_READING_CHARS = re.compile(r"[^A-Za-z0-9._\-]")
DISCOVERY_TOPIC = "homeassistant/#"

# Home Assistant defaults
DEFAULT_PAYLOAD_ON = "ON"
DEFAULT_PAYLOAD_OFF = "OFF"
DEFAULT_PAYLOAD_OPEN = "OPEN"
DEFAULT_PAYLOAD_CLOSE = "CLOSE"
DEFAULT_PAYLOAD_STOP = "STOP"
DEFAULT_PAYLOAD_LOCK = "LOCK"
DEFAULT_PAYLOAD_UNLOCK = "UNLOCK"
DEFAULT_PAYLOAD_AVAILABLE = "online"
DEFAULT_PAYLOAD_NOT_AVAILABLE = "offline"
DEFAULT_BRIGHTNESS_SCALE = 255
DEFAULT_MIN_KELVIN = 2000
DEFAULT_MAX_KELVIN = 6535
DEFAULT_MIN_MIREDS = 153
DEFAULT_MAX_MIREDS = 500
BRIGHTNESS_MODES = ("brightness", "color_temp", "hs", "xy", "rgb", "rgbw", "rgbww")
COLOR_MODES = ("hs", "xy", "rgb", "rgbw", "rgbww")

# {{ value_json.a.b }}, {{ value_json["a"] }}, {{ value_json.a | default(0) }}
VALUE_JSON_TEMPLATE = re.compile(
    r"^\{\{\s*value_json((?:\.\w+|\[\s*['\"][^'\"\]]+['\"]\s*\])+)\s*"
    r"(?:\|[^}]*)?\}\}$"
)
VALUE_JSON_PART = re.compile(r"\.(\w+)|\[\s*['\"]([^'\"\]]+)['\"]\s*\]")
VALUE_TEMPLATE = re.compile(r"^\{\{\s*value\s*\}\}$")
# payload is the whole JSON message (json2nameValue), no single value
JSON_MESSAGE = object()
# readingList lines of older versions, replaced by the new ones
LEGACY_READING = re.compile(r"^\{ \{ [\w.\-]+=>lc\(\\?\$EVENT\) \} \}$")
LEGACY_LIGHT_SET = re.compile(
    r"^\S+_(?:on (\S+) \{\"state\": \"ON\", \"transition\": 1\}"
    r"|off (\S+) \{\"state\": \"OFF\", \"transition\": 1\}"
    r"|brightness:colorpicker,BRI,0,5,255 (\S+) "
    r"\{\"state\":\"ON\",\"brightness\":\\?\$EVTPART1\})$"
)
REGEX_CHARS = re.compile(r"([\\^$.|?*+()\[\]{}])")


def _expand(payload, abbreviations):
    return {abbreviations.get(key, key): val for key, val in payload.items()}


def normalize_payload(payload_json):
    """Return the payload with full key names and expanded ~ base topic.

    HomeAssistant allows abbreviated and full key names in discovery
    payloads, ESPHome sends abbreviations, Zigbee2MQTT and Tasmota the full
    names."""
    payload = _expand(payload_json, ABBREVIATIONS)
    if isinstance(payload.get("device"), dict):
        payload["device"] = _expand(payload["device"], DEVICE_ABBREVIATIONS)
    if isinstance(payload.get("availability"), list):
        payload["availability"] = [
            _expand(entry, ABBREVIATIONS)
            for entry in payload["availability"]
            if isinstance(entry, dict)
        ]
    base_topic = payload.get("~")
    if isinstance(base_topic, str):
        _expand_base_topic(payload, base_topic)
        for entry in payload.get("availability") or []:
            _expand_base_topic(entry, base_topic)
    return payload


def _expand_base_topic(payload, base_topic):
    for key, val in payload.items():
        if not (key.endswith("_topic") or key == "topic"):
            continue
        if not isinstance(val, str):
            continue
        if val.startswith("~"):
            payload[key] = base_topic + val[1:]
        elif val.endswith("~"):
            payload[key] = val[:-1] + base_topic


def parse_discovery(topic, payload):
    """Return a list of (component, node_id, object_id, payload) of a config msg.

    Supports the topics
    <prefix>/<component>/[<node_id>/]<object_id>/config and the device based
    discovery <prefix>/device/<object_id>/config with all components in cmps.
    Raises ValueError for invalid JSON.
    """
    parts = topic.split("/")
    if parts[-1] != "config" or len(parts) not in (4, 5):
        return []
    if not payload:
        # empty payload, entity got removed
        return []
    payload_json = json.loads(payload)
    if not isinstance(payload_json, dict):
        return []
    payload_json = normalize_payload(payload_json)

    component = parts[1]
    node_id = parts[2] if len(parts) == 5 else None
    object_id = parts[-2]

    if component != "device":
        return [(component, node_id, object_id, payload_json)]

    shared = {
        key: val
        for key, val in payload_json.items()
        if key not in DEVICE_DISCOVERY_KEYS
    }
    entities = []
    for cmp_id, cmp_json in (payload_json.get("components") or {}).items():
        if not isinstance(cmp_json, dict):
            continue
        entity = {**shared, **normalize_payload(cmp_json)}
        if "device" in payload_json:
            entity["device"] = payload_json["device"]
        entities.append((entity.get("platform"), object_id, cmp_id, entity))
    return entities


def device_info(node_id, object_id, payload_json):
    """Return (device_name, device_id) of the entity."""
    dev = payload_json.get("device")
    if not isinstance(dev, dict):
        dev = {}
    ids = dev.get("identifiers")
    if isinstance(ids, list):
        ids = ids[0] if ids else None
    if ids is None:
        cns = dev.get("connections")
        ids = cns[0][1] if cns else None
    device_name = dev.get("name") or node_id or ids or object_id
    device_id = ids or node_id or object_id
    return str(device_name), str(device_id)


def device_model(payload_json):
    """'manufacturer model' of the entity's device, e.g. 'Xiaomi WSDCGQ11LM'"""
    dev = payload_json.get("device")
    if not isinstance(dev, dict):
        return ""
    parts = [dev.get("manufacturer"), dev.get("model")]
    return " ".join(str(part) for part in parts if part)


def reading_name(object_id, payload_json):
    name = payload_json.get("name") or object_id
    return INVALID_READING_CHARS.sub("_", utils.gen_fhemdev_name(str(name)))


def fhem_device_name(device_name, device_id):
    name = utils.gen_fhemdev_name("MQTT2_" + device_name + "_" + device_id)
    return INVALID_READING_CHARS.sub("_", name)


def supported(component, payload_json):
    """A reading or set command is created for the entity"""
    if component in PLATFORMS:
        return any(
            value and key.endswith("_topic") and key not in OTHER_TOPICS
            for key, value in payload_json.items()
        )
    return bool(
        payload_json.get("state_topic")
        or (component in COMMANDS and payload_json.get("command_topic"))
    )


async def existing_device(hash, fhem_name, payload_json):
    """Name of the MQTT2_DEVICE of the entity in FHEM, or None."""
    if str(
        await fhem.checkIfDeviceExists(hash, "TYPE", "MQTT2_DEVICE", "NAME", fhem_name)
    ) in ("1", "True"):
        return fhem_name

    # devices created by older versions or renamed by the user
    stat_t = payload_json.get("state_topic")
    if stat_t and " " not in stat_t:
        dev_exists = await fhem.CommandList(
            hash, "readingList=(?s).*" + re.escape(stat_t) + ":.* NAME"
        )
        if dev_exists and not dev_exists.startswith("No device"):
            return dev_exists.split()[0]
    return None


# --- value templates ---


def template_key(template):
    """What a value template takes from the message: None for the whole
    message, the json2nameValue reading name for {{ value_json.a.b }} or
    JSON_MESSAGE for other templates on JSON messages."""
    if not isinstance(template, str) or VALUE_TEMPLATE.match(template.strip()):
        return None
    match = VALUE_JSON_TEMPLATE.match(template.strip())
    if match:
        parts = VALUE_JSON_PART.findall(match.group(1))
        return "_".join(attr or item for attr, item in parts)
    if "value_json" in template:
        return JSON_MESSAGE
    return None


def command_payload(template, value="$EVTPART1"):
    """Payload of a command template with {{ value }}, None if the template
    can't be converted."""
    if not template:
        return value
    if not isinstance(template, str):
        return None
    converted = re.sub(
        r"\{\{\s*(?:value|position|tilt_position)\s*\}\}", value, template
    )
    if "{{" in converted or "{%" in converted:
        return None
    return converted


def topic_regex(topic):
    """readingList regexp of a topic, spaces would split the attribute"""
    return REGEX_CHARS.sub(r"\\\1", topic).replace(" ", ".")


def perl_quote(value):
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def perl_key(name):
    """hash key in perl, quoted unless it is a plain word"""
    return name if re.fullmatch(r"[A-Za-z_]\w*", name) else perl_quote(name)


def _number(value, default):
    return value if isinstance(value, (int, float)) and value > 0 else default


# --- set commands with perl ---


def _color_command(topic, mode):
    """Perl for the RGB colorpicker: converts the hex color to the color of
    the light's color mode like Home Assistant's light card."""
    rgb = "map { hex($_) / 255 } ($EVTPART1 =~ /^#?(..)(..)(..)/)"
    fmt = topic.replace("%", "%%") + ' {"state":"ON","color":'
    if mode == "xy":
        # sRGB to CIE xy, Wide RGB D65 like homeassistant.util.color
        return (
            "{ my @c = map { $_ > 0.04045 ? (($_ + 0.055) / 1.055) ** 2.4 : "
            f"$_ / 12.92 }} {rgb}; "
            "my $X = $c[0] * 0.664511 + $c[1] * 0.154324 + $c[2] * 0.162028; "
            "my $Y = $c[0] * 0.283881 + $c[1] * 0.668433 + $c[2] * 0.047685; "
            "my $s = $X + $Y + $c[0] * 0.000088 + $c[1] * 0.07231 + "
            "$c[2] * 0.986039 || 1; "
            f"sprintf({perl_quote(fmt + '{"x":%.4f,"y":%.4f}}')}, "
            "$X / $s, $Y / $s) }"
        )
    if mode == "hs":
        return (
            f"{{ my @c = {rgb}; "
            "my ($mx, $mn) = (sort { $a <=> $b } @c)[2, 0]; my $d = $mx - $mn; "
            "my $h = !$d ? 0 : $mx == $c[0] ? 60 * ($c[1] - $c[2]) / $d : "
            "$mx == $c[1] ? 60 * (($c[2] - $c[0]) / $d + 2) : "
            "60 * (($c[0] - $c[1]) / $d + 4); $h += 360 if ($h < 0); "
            f"sprintf({perl_quote(fmt + '{"h":%.1f,"s":%.1f}}')}, "
            "$h, $mx ? $d / $mx * 100 : 0) }"
        )
    return (
        f"{{ sprintf({perl_quote(fmt + '{"r":%d,"g":%d,"b":%d}}')}, "
        f"map {{ $_ * 255 }} {rgb}) }}"
    )


def _rgb_command(topic):
    """default schema rgb_command_topic: 'r,g,b'"""
    return (
        f"{{ {perl_quote(topic + ' ')} . join(',', "
        "map { hex($_) } ($EVTPART1 =~ /^#?(..)(..)(..)/)) }"
    )


def _json_code(spec):
    """perl of a JSON topic: json2nameValue with aliases and on/off in lower
    case like the state of other FHEM devices"""
    prefix = f", {perl_quote(spec['prefix'])}" if spec["prefix"] else ""
    code = f"json2nameValue($EVENT{prefix})"
    lc = sorted(
        key if key in spec["alias"] else spec["prefix"] + key for key in spec["lc"]
    )
    lc += sorted(name for name, onoff in spec["raw"].items() if onoff)
    raw = sorted(spec["raw"])
    alias = sorted(spec["alias"].items())
    if not (lc or raw or alias):
        return code
    parts = [f"my $r = {code};"]
    parts += [f"$r->{{{perl_key(name)}}} = $EVENT;" for name in raw]
    parts += [
        f"$r->{{{perl_key(name)}}} = $r->{{{perl_key(spec['prefix'] + key)}}};"
        for name, key in alias
    ]
    parts += [
        f"$r->{{{perl_key(key)}}} = lc($r->{{{perl_key(key)}}}) if "
        f"(($r->{{{perl_key(key)}}} // '') =~ /^(ON|OFF)$/);"
        for key in lc
    ]
    return " ".join(parts + ["$r"])


# --- the device ---


class DeviceAttributes:
    """readingList, setList... of all entities of one device"""

    def __init__(self):
        # topic -> {"json": bool, "prefix": str, "lc": set, "raw": {reading: lc}}
        self.topics = {}
        self.sets = {}
        self.availability = []
        self.availability_mode = "latest"
        self.web_cmd = []
        self.state_format = []
        # stateFormat of the device itself, e.g. temperatures of a thermostat
        self.main_state_format = []
        # the reading state is set, no stateFormat needed
        self.has_state = False
        self.primary = None

    # readings

    def _topic(self, topic):
        return self.topics.setdefault(
            topic,
            {"json": False, "prefix": "", "lc": set(), "raw": {}, "alias": {}},
        )

    def add_reading(self, topic, template, name, onoff=False, alias=None):
        """The reading of an entity's state topic, returns its name.
        alias: reading name for a JSON value, e.g. state for POWER"""
        if not isinstance(topic, str) or not topic:
            return None
        key = template_key(template)
        spec = self._topic(topic)
        if key is None:
            spec["raw"][name] = onoff
            return name
        spec["json"] = True
        if key is JSON_MESSAGE:
            return None
        if alias and alias != key:
            spec["alias"][alias] = key
            key = alias
        if onoff:
            spec["lc"].add(key)
        return key

    def add_json(self, topic, prefix=""):
        if not isinstance(topic, str) or not topic:
            return
        spec = self._topic(topic)
        spec["json"] = True
        spec["prefix"] = spec["prefix"] or prefix

    def add_set(self, name, args, topic, payload, perl=False):
        """perl: payload is a perl expression returning topic and message"""
        if not topic or " " in topic or payload is None or name in self.sets:
            return
        cmd = name + (":" + args if args else "")
        if perl:
            self.sets[name] = f"{cmd} {payload}"
        else:
            self.sets[name] = f"{cmd} {topic} {payload}".rstrip()

    def add_availability(self, payload_json):
        if self.availability:
            return
        entries = payload_json.get("availability")
        if not isinstance(entries, list):
            entries = []
        if payload_json.get("availability_topic"):
            entries = [
                {
                    "topic": payload_json["availability_topic"],
                    "value_template": payload_json.get("availability_template"),
                    "payload_available": payload_json.get("payload_available"),
                    "payload_not_available": payload_json.get("payload_not_available"),
                }
            ] + entries
        self.availability = [
            e for e in entries if isinstance(e.get("topic"), str) and e["topic"]
        ]
        self.availability_mode = payload_json.get("availability_mode", "latest")

    # attributes

    def reading_lines(self):
        lines = []
        for topic, spec in self.topics.items():
            regex = topic_regex(topic) + ":.*"
            if spec["json"]:
                lines.append(f"{regex} {{ {_json_code(spec)} }}")
            else:
                values = ", ".join(
                    f"{perl_key(name)}=>{'lc($EVENT)' if onoff else '$EVENT'}"
                    for name, onoff in spec["raw"].items()
                )
                lines.append(f"{regex} {{ {{ {values} }} }}")
        lines += self.availability_lines()
        return lines

    def availability_lines(self):
        """Every topic sets its hidden reading .availability<i> to 1/0, the
        reading availability is calculated like Home Assistant does."""
        count = len(self.availability)
        if self.availability_mode == "all":
            combine = "(grep { !$_ } @a) ? 'offline' : 'online'"
        elif self.availability_mode == "any":
            combine = "(grep { $_ } @a) ? 'online' : 'offline'"
        else:
            combine = "$v ? 'online' : 'offline'"
        lines = []
        for i, entry in enumerate(self.availability):
            key = template_key(entry.get("value_template"))
            if isinstance(key, str):
                # Zigbee2MQTT < 1.20 sent online/offline without JSON
                value = (
                    f"$EVENT =~ /^\\s*\\{{/ ? "
                    f"(json2nameValue($EVENT)->{{{perl_key(key)}}} // '') : $EVENT"
                )
            else:
                value = "$EVENT"
            available = entry.get("payload_available") or DEFAULT_PAYLOAD_AVAILABLE
            not_available = (
                entry.get("payload_not_available") or DEFAULT_PAYLOAD_NOT_AVAILABLE
            )
            others = (
                f"my @a = map {{ $_ == {i} ? $v : "
                'ReadingsVal($NAME, ".availability$_", 1) } '
                f"(0..{count - 1}); "
                if count > 1 and self.availability_mode != "latest"
                else ""
            )
            if not others and self.availability_mode != "latest":
                others = "my @a = ($v); "
            lines.append(
                f"{topic_regex(entry['topic'])}:.* {{ my $p = {value}; "
                f"return undef if ($p ne {perl_quote(available)} && "
                f"$p ne {perl_quote(not_available)}); "
                f"my $v = $p eq {perl_quote(available)} ? 1 : 0; {others}"
                f"return {{ '.availability{i}' => $v, availability => {combine} }} }}"
            )
        return lines

    def set_lines(self):
        return list(self.sets.values())

    def attributes(self):
        attrs = {
            "readingList": self.reading_lines(),
            "setList": self.set_lines(),
        }
        if self.web_cmd:
            attrs["webCmd"] = ":".join(self.web_cmd)
        state_format = self.main_state_format or self.state_format[:3]
        if state_format and not self.has_state:
            attrs["stateFormat"] = " ".join(state_format)
        return attrs


def _is_primary(component, payload_json, entities):
    """The entity which is the device itself: Home Assistant names it like the
    device (name null), or the only light of the device."""
    if component not in PRIMARY_COMPONENTS:
        return False
    if payload_json.get("name") is None:
        return True
    lights = [e for e in entities if e[0] == "light"]
    return component == "light" and len(lights) == 1


def _name(object_id, payload_json, primary):
    return "" if primary else reading_name(object_id, payload_json)


def _cmd_name(prefix, name):
    return f"{prefix}_{name}" if prefix else name


def add_light(dev, object_id, payload_json, primary, shared_topic):
    prefix = _name(object_id, payload_json, primary)
    schema = payload_json.get("schema", "default")
    if schema == "json":
        modes = _add_json_light(dev, prefix, payload_json, primary or shared_topic)
    elif schema == "default":
        modes = _add_default_light(dev, prefix, payload_json)
    else:
        modes = _add_template_light(dev, prefix, payload_json)

    if primary and dev.primary is None:
        dev.primary = object_id
        dev.has_state = True
        dev.web_cmd = ["on", "off"]
        if any(mode in BRIGHTNESS_MODES for mode in modes):
            dev.web_cmd.append("brightness")


def _add_json_light(dev, prefix, payload_json, unprefixed):
    """schema json: one JSON message for state and command, returns the
    supported color modes"""
    cmd_t = payload_json.get("command_topic")
    modes = payload_json.get("supported_color_modes")
    if not isinstance(modes, list):
        modes = ["brightness"] if payload_json.get("brightness") else []
    state_t = payload_json.get("state_topic")
    dev.add_json(state_t, "" if unprefixed else prefix + "_")
    if state_t:
        dev.topics[state_t]["lc"].add("state")
    dev.add_set(_cmd_name(prefix, "on"), "noArg", cmd_t, '{"state":"ON"}')
    dev.add_set(_cmd_name(prefix, "off"), "noArg", cmd_t, '{"state":"OFF"}')
    if any(mode in BRIGHTNESS_MODES for mode in modes):
        scale = _number(payload_json.get("brightness_scale"), DEFAULT_BRIGHTNESS_SCALE)
        dev.add_set(
            _cmd_name(prefix, "brightness"),
            f"colorpicker,BRI,0,1,{scale}",
            cmd_t,
            '{"state":"ON","brightness":$EVTPART1}',
        )
    if "color_temp" in modes:
        dev.add_set(
            _cmd_name(prefix, "color_temp"),
            _color_temp_args(payload_json),
            cmd_t,
            '{"state":"ON","color_temp":$EVTPART1}',
        )
    color_mode = next((mode for mode in modes if mode in COLOR_MODES), None)
    if color_mode and cmd_t and " " not in cmd_t:
        dev.add_set(
            _cmd_name(prefix, "color"),
            "colorpicker,RGB",
            cmd_t,
            _color_command(cmd_t, color_mode),
            perl=True,
        )
    effects = payload_json.get("effect_list")
    if payload_json.get("effect") and isinstance(effects, list):
        _add_effect(dev, prefix, cmd_t, effects, '{"effect":"$EVTPART1"}')
    return modes


def _add_default_light(dev, prefix, payload_json):
    """schema default: a topic for each value"""
    cmd_t = payload_json.get("command_topic")
    dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("state_value_template"),
        prefix or "state",
        True,
        None if prefix else "state",
    )
    dev.add_set(
        _cmd_name(prefix, "on"),
        "noArg",
        cmd_t,
        str(payload_json.get("payload_on", DEFAULT_PAYLOAD_ON)),
    )
    dev.add_set(
        _cmd_name(prefix, "off"),
        "noArg",
        cmd_t,
        str(payload_json.get("payload_off", DEFAULT_PAYLOAD_OFF)),
    )
    _add_default_light_values(dev, prefix, payload_json)
    return ["brightness"] if payload_json.get("brightness_command_topic") else []


def _add_template_light(dev, prefix, payload_json):
    """schema template: on/off if the templates are plain payloads"""
    cmd_t = payload_json.get("command_topic")
    dev.add_reading(payload_json.get("state_topic"), None, prefix or "state", True)
    dev.add_set(
        _cmd_name(prefix, "on"),
        "noArg",
        cmd_t,
        command_payload(payload_json.get("command_on_template"), ""),
    )
    dev.add_set(
        _cmd_name(prefix, "off"),
        "noArg",
        cmd_t,
        command_payload(payload_json.get("command_off_template"), ""),
    )
    return []


def _color_temp_args(payload_json):
    if payload_json.get("color_temp_kelvin"):
        low = _number(payload_json.get("min_kelvin"), DEFAULT_MIN_KELVIN)
        high = _number(payload_json.get("max_kelvin"), DEFAULT_MAX_KELVIN)
        return f"colorpicker,CT,{low},10,{high}"
    low = _number(payload_json.get("min_mireds"), DEFAULT_MIN_MIREDS)
    high = _number(payload_json.get("max_mireds"), DEFAULT_MAX_MIREDS)
    return f"colorpicker,CT,{low},1,{high}"


def _add_effect(dev, prefix, topic, effects, payload):
    effects = [str(effect) for effect in effects]
    if not effects or any(" " in e or "," in e for e in effects):
        return
    dev.add_set(_cmd_name(prefix, "effect"), ",".join(effects), topic, payload)


def _add_default_light_values(dev, prefix, payload_json):
    """default schema: one topic per value"""
    for value in ("brightness", "color_temp", "effect", "rgb", "hs", "xy", "white"):
        dev.add_reading(
            payload_json.get(f"{value}_state_topic"),
            payload_json.get(f"{value}_value_template"),
            _cmd_name(prefix, value),
        )
        topic = payload_json.get(f"{value}_command_topic")
        template = payload_json.get(f"{value}_command_template")
        if value == "brightness":
            scale = _number(
                payload_json.get("brightness_scale"), DEFAULT_BRIGHTNESS_SCALE
            )
            dev.add_set(
                _cmd_name(prefix, value),
                f"colorpicker,BRI,0,1,{scale}",
                topic,
                command_payload(template),
            )
        elif value == "color_temp":
            dev.add_set(
                _cmd_name(prefix, value),
                _color_temp_args(payload_json),
                topic,
                command_payload(template),
            )
        elif value == "effect":
            effects = payload_json.get("effect_list")
            if isinstance(effects, list) and command_payload(template) is not None:
                _add_effect(dev, prefix, topic, effects, command_payload(template))
        elif value == "rgb" and topic and not template:
            dev.add_set(
                _cmd_name(prefix, "color"),
                "colorpicker,RGB",
                topic,
                _rgb_command(topic),
                perl=True,
            )


def add_switch(dev, object_id, payload_json, primary):
    name = _name(object_id, payload_json, primary)
    reading = dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("value_template"),
        name or "state",
        True,
        None if name else "state",
    )
    if isinstance(reading, str) and not primary:
        name = reading
    cmd_t = payload_json.get("command_topic")
    for cmd, key, default in (
        ("on", "payload_on", DEFAULT_PAYLOAD_ON),
        ("off", "payload_off", DEFAULT_PAYLOAD_OFF),
    ):
        dev.add_set(
            _cmd_name(name, cmd),
            "noArg",
            cmd_t,
            str(payload_json.get(key, default)),
        )
    if primary and dev.primary is None:
        dev.primary = object_id
        dev.has_state = True
        dev.web_cmd = ["on", "off"]


def add_value_entity(dev, component, object_id, payload_json):
    """sensor, binary_sensor, select, number, button and the state of all
    other components"""
    name = reading_name(object_id, payload_json)
    reading = dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("value_template"),
        name,
        component == "binary_sensor",
    )
    if isinstance(reading, str):
        name = reading
    unit = payload_json.get("unit_of_measurement")
    if component == "sensor" and isinstance(reading, str) and unit:
        dev.state_format.append(f"{reading} {unit}")
    cmd_t = payload_json.get("command_topic")
    payload = command_payload(payload_json.get("command_template"))
    if component == "select":
        options = [str(o) for o in payload_json.get("options") or []]
        if options and not any(" " in o or "," in o for o in options):
            dev.add_set(name, ",".join(options), cmd_t, payload)
    elif component == "number":
        low = payload_json.get("min", 1)
        high = payload_json.get("max", 100)
        step = payload_json.get("step", 1)
        dev.add_set(name, f"slider,{low},{step},{high}", cmd_t, payload)
    elif component == "button":
        dev.add_set(
            name, "noArg", cmd_t, str(payload_json.get("payload_press", "PRESS"))
        )
    elif component == "text":
        dev.add_set(name, "textField", cmd_t, payload)


# --- climate, cover, fan, lock, siren ---

# topics which aren't state or command topics of an entity
OTHER_TOPICS = ("availability_topic", "json_attributes_topic")
DEFAULT_MIN_TEMP = 7
DEFAULT_MAX_TEMP = 35
DEFAULT_MIN_HUMIDITY = 30
DEFAULT_MAX_HUMIDITY = 99
DEFAULT_HVAC_MODES = ["auto", "off", "cool", "heat", "dry", "fan_only"]
DEFAULT_FAN_MODES = ["auto", "low", "medium", "high"]
DEFAULT_SWING_MODES = ["on", "off"]


def _options(values):
    """FHEM dropdown of the values, None if a value can't be used in it"""
    if not isinstance(values, list):
        return None
    values = [str(value) for value in values]
    if not values or any(" " in v or "," in v or not v for v in values):
        return None
    return ",".join(values)


def _slider(low, step, high):
    floats = any(isinstance(v, float) and not v.is_integer() for v in (low, step, high))
    values = [
        int(v) if isinstance(v, float) and v.is_integer() else v
        for v in (low, step, high)
    ]
    return "slider," + ",".join(str(v) for v in values) + (",1" if floats else "")


def _state(dev, payload_json, prefix, name, topic_key, template_key, onoff=False):
    """reading of a state topic of the entity"""
    return dev.add_reading(
        payload_json.get(topic_key),
        payload_json.get(template_key),
        _cmd_name(prefix, name),
        onoff,
    )


def _command(dev, payload_json, prefix, name, args, topic_key, template_key):
    """set command which publishes the argument (with the command template)"""
    template = payload_json.get(template_key) if template_key else None
    dev.add_set(
        _cmd_name(prefix, name),
        args,
        payload_json.get(topic_key),
        command_payload(template),
    )


def _payload_command(dev, payload_json, prefix, name, payload_key, default):
    """set command without argument, e.g. open of a cover. A payload set to
    null in the discovery config disables the command."""
    payload = payload_json.get(payload_key, default)
    template = payload_json.get("command_template")
    if payload is not None and template:
        payload = command_payload(template, str(payload))
    dev.add_set(
        _cmd_name(prefix, name),
        "noArg",
        payload_json.get("command_topic"),
        None if payload is None else str(payload),
    )


def _set_primary(dev, object_id, primary, web_cmd, has_state=True):
    if primary and dev.primary is None:
        dev.primary = object_id
        dev.web_cmd = web_cmd
        dev.has_state = has_state


def add_climate(dev, object_id, payload_json, primary):
    """Thermostats and air conditioners like Home Assistant's climate card"""
    prefix = _name(object_id, payload_json, primary)
    current = _state(
        dev,
        payload_json,
        prefix,
        "current_temperature",
        "current_temperature_topic",
        "current_temperature_template",
    )
    target = _state(
        dev,
        payload_json,
        prefix,
        "desired_temp",
        "temperature_state_topic",
        "temperature_state_template",
    )
    for name in ("mode", "fan_mode", "swing_mode", "swing_horizontal_mode"):
        _state(
            dev,
            payload_json,
            prefix,
            name,
            f"{name}_state_topic",
            f"{name}_state_template",
        )
    _state(dev, payload_json, prefix, "action", "action_topic", "action_template")
    _state(
        dev,
        payload_json,
        prefix,
        "preset_mode",
        "preset_mode_state_topic",
        "preset_mode_value_template",
    )
    _state(
        dev,
        payload_json,
        prefix,
        "current_humidity",
        "current_humidity_topic",
        "current_humidity_template",
    )
    _state(
        dev,
        payload_json,
        prefix,
        "humidity",
        "target_humidity_state_topic",
        "target_humidity_state_template",
    )
    for name, key in (
        ("desired_temp_low", "temperature_low"),
        ("desired_temp_high", "temperature_high"),
    ):
        _state(
            dev,
            payload_json,
            prefix,
            name,
            f"{key}_state_topic",
            f"{key}_state_template",
        )

    step = payload_json.get("temp_step", 1)
    temp = _slider(
        payload_json.get("min_temp", DEFAULT_MIN_TEMP),
        step if isinstance(step, (int, float)) and step > 0 else 1,
        payload_json.get("max_temp", DEFAULT_MAX_TEMP),
    )
    for name, key in (
        ("desired_temp", "temperature"),
        ("desired_temp_low", "temperature_low"),
        ("desired_temp_high", "temperature_high"),
    ):
        _command(
            dev,
            payload_json,
            prefix,
            name,
            temp,
            f"{key}_command_topic",
            f"{key}_command_template",
        )
    for name, modes, default in (
        ("mode", "modes", DEFAULT_HVAC_MODES),
        ("fan_mode", "fan_modes", DEFAULT_FAN_MODES),
        ("swing_mode", "swing_modes", DEFAULT_SWING_MODES),
        ("swing_horizontal_mode", "swing_horizontal_modes", DEFAULT_SWING_MODES),
        ("preset_mode", "preset_modes", []),
    ):
        options = _options(payload_json.get(modes, default))
        if options:
            _command(
                dev,
                payload_json,
                prefix,
                name,
                options,
                f"{name}_command_topic",
                f"{name}_command_template",
            )
    _command(
        dev,
        payload_json,
        prefix,
        "humidity",
        _slider(
            payload_json.get("min_humidity", DEFAULT_MIN_HUMIDITY),
            1,
            payload_json.get("max_humidity", DEFAULT_MAX_HUMIDITY),
        ),
        "target_humidity_command_topic",
        "target_humidity_command_template",
    )
    for cmd, key, default in (
        ("on", "payload_on", "ON"),
        ("off", "payload_off", "OFF"),
    ):
        payload = command_payload(
            payload_json.get("power_command_template"),
            str(payload_json.get(key, default)),
        )
        dev.add_set(
            _cmd_name(prefix, cmd),
            "noArg",
            payload_json.get("power_command_topic"),
            payload,
        )

    if isinstance(current, str):
        unit = "°" + str(payload_json.get("temperature_unit", "C"))
        dev.main_state_format = [f"{current} {unit}"] + (
            [f"({target} {unit})"] if isinstance(target, str) else []
        )
    if payload_json.get("temperature_command_topic"):
        _set_primary(
            dev, object_id, primary, [_cmd_name(prefix, "desired_temp")], False
        )
    else:
        _set_primary(dev, object_id, primary, [], False)


def add_cover(dev, object_id, payload_json, primary):
    """Blinds, shutters, garage doors"""
    prefix = _name(object_id, payload_json, primary)
    dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("value_template"),
        prefix or "state",
        False,
        None if prefix else "state",
    )
    _state(dev, payload_json, prefix, "position", "position_topic", "position_template")
    _state(
        dev, payload_json, prefix, "tilt", "tilt_status_topic", "tilt_status_template"
    )
    for name, key, default in (
        ("open", "payload_open", DEFAULT_PAYLOAD_OPEN),
        ("close", "payload_close", DEFAULT_PAYLOAD_CLOSE),
        ("stop", "payload_stop", DEFAULT_PAYLOAD_STOP),
    ):
        _payload_command(dev, payload_json, prefix, name, key, default)
    position = _slider(
        payload_json.get("position_closed", 0),
        1,
        payload_json.get("position_open", 100),
    )
    _command(
        dev,
        payload_json,
        prefix,
        "position",
        position,
        "set_position_topic",
        "set_position_template",
    )
    tilt = _slider(
        payload_json.get("tilt_min", 0), 1, payload_json.get("tilt_max", 100)
    )
    _command(
        dev,
        payload_json,
        prefix,
        "tilt",
        tilt,
        "tilt_command_topic",
        "tilt_command_template",
    )
    web_cmd = ["open", "stop", "close"] if payload_json.get("command_topic") else []
    if payload_json.get("set_position_topic"):
        web_cmd.append("position")
    _set_primary(
        dev, object_id, primary, web_cmd, bool(payload_json.get("state_topic"))
    )


def add_fan(dev, object_id, payload_json, primary):
    prefix = _name(object_id, payload_json, primary)
    dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("state_value_template"),
        prefix or "state",
        True,
        None if prefix else "state",
    )
    for name in ("percentage", "preset_mode", "oscillation", "direction"):
        template = f"{name}_value_template"
        _state(dev, payload_json, prefix, name, f"{name}_state_topic", template)
    for cmd, key, default in (
        ("on", "payload_on", "ON"),
        ("off", "payload_off", "OFF"),
    ):
        _payload_command(dev, payload_json, prefix, cmd, key, default)
    speed = _slider(
        payload_json.get("speed_range_min", 1),
        1,
        payload_json.get("speed_range_max", 100),
    )
    _command(
        dev,
        payload_json,
        prefix,
        "percentage",
        speed,
        "percentage_command_topic",
        "percentage_command_template",
    )
    presets = _options(payload_json.get("preset_modes"))
    if presets:
        _command(
            dev,
            payload_json,
            prefix,
            "preset_mode",
            presets,
            "preset_mode_command_topic",
            "preset_mode_command_template",
        )
    _command(
        dev,
        payload_json,
        prefix,
        "direction",
        "forward,reverse",
        "direction_command_topic",
        "direction_command_template",
    )
    for cmd, key, default in (
        ("oscillation_on", "payload_oscillation_on", "oscillate_on"),
        ("oscillation_off", "payload_oscillation_off", "oscillate_off"),
    ):
        payload = command_payload(
            payload_json.get("oscillation_command_template"),
            str(payload_json.get(key, default)),
        )
        dev.add_set(
            _cmd_name(prefix, cmd),
            "noArg",
            payload_json.get("oscillation_command_topic"),
            payload,
        )
    _set_primary(
        dev, object_id, primary, ["on", "off"], bool(payload_json.get("state_topic"))
    )


def add_lock(dev, object_id, payload_json, primary):
    prefix = _name(object_id, payload_json, primary)
    dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("value_template"),
        prefix or "state",
        False,
        None if prefix else "state",
    )
    for name, key, default in (
        ("lock", "payload_lock", DEFAULT_PAYLOAD_LOCK),
        ("unlock", "payload_unlock", DEFAULT_PAYLOAD_UNLOCK),
        # only if the lock can open the door
        ("open", "payload_open", None),
    ):
        _payload_command(dev, payload_json, prefix, name, key, default)
    _set_primary(
        dev,
        object_id,
        primary,
        ["lock", "unlock"],
        bool(payload_json.get("state_topic")),
    )


def add_siren(dev, object_id, payload_json, primary):
    prefix = _name(object_id, payload_json, primary)
    dev.add_reading(
        payload_json.get("state_topic"),
        payload_json.get("state_value_template"),
        prefix or "state",
        True,
        None if prefix else "state",
    )
    on = payload_json.get("payload_on", "ON")
    off = payload_json.get("payload_off", "OFF")
    template = payload_json.get("command_template")
    off_template = payload_json.get("command_off_template") or template
    if template:
        # templates with tone, duration and volume can't be converted
        on_payload = command_payload(template, str(on))
        off_payload = command_payload(off_template, str(off))
    else:
        # Home Assistant sends the state as JSON without command template
        on_payload = json.dumps({"state": on}, separators=(",", ":"))
        off_payload = json.dumps({"state": off}, separators=(",", ":"))
    cmd_t = payload_json.get("command_topic")
    dev.add_set(_cmd_name(prefix, "on"), "noArg", cmd_t, on_payload)
    dev.add_set(_cmd_name(prefix, "off"), "noArg", cmd_t, off_payload)
    _set_primary(
        dev, object_id, primary, ["on", "off"], bool(payload_json.get("state_topic"))
    )


PLATFORMS = {
    "climate": add_climate,
    "cover": add_cover,
    "fan": add_fan,
    "lock": add_lock,
    "siren": add_siren,
}


# components with set commands
COMMANDS = ("light", "switch", "select", "number", "button", "text")
# components which can be the device itself
PRIMARY_COMPONENTS = ("light", "switch", "climate", "cover", "fan", "lock", "siren")


def generate_attributes(entities):
    """Attributes of the MQTT2_DEVICE of all entities of a device.

    entities: list of (component, object_id, payload_json)
    """
    dev = DeviceAttributes()
    entities = [e for e in entities if supported(e[0], e[2])]
    state_topics = {}
    for _, _, payload_json in entities:
        topic = payload_json.get("state_topic")
        if topic:
            state_topics[topic] = state_topics.get(topic, 0) + 1
    # the device itself first: its readings and commands get the short names
    entities.sort(key=lambda e: not _is_primary(e[0], e[2], entities))
    for component, object_id, payload_json in entities:
        dev.add_availability(payload_json)
        primary = _is_primary(component, payload_json, entities)
        if dev.primary is not None:
            primary = False
        if component == "light":
            shared = state_topics.get(payload_json.get("state_topic"), 0) > 1
            add_light(dev, object_id, payload_json, primary, shared)
        elif component == "switch":
            add_switch(dev, object_id, payload_json, primary)
        elif component in PLATFORMS:
            PLATFORMS[component](dev, object_id, payload_json, primary)
        else:
            add_value_entity(dev, component, object_id, payload_json)
        dev.add_json(payload_json.get("json_attributes_topic"))
    return dev.attributes()


# --- write to FHEM ---


def _generated_reading(line):
    """readingList line written by fhempy (this or an older version)"""
    code = line.split(" ", 1)[1] if " " in line else ""
    return bool(
        LEGACY_READING.match(code) or "json2nameValue" in code or "availability" in code
    )


def merge_reading_list(current, generated):
    """New readingList: generated lines replace older fhempy lines of the same
    topic, lines of the user are kept."""
    lines = [line for line in current.split("\n") if line.strip()]
    for line in generated:
        if line in lines:
            continue
        regex = line.split(" ", 1)[0]
        kind = "availability" in line
        same = [
            i
            for i, old in enumerate(lines)
            if old.split(" ", 1)[0] == regex and ("availability" in old) == kind
        ]
        ours = [i for i in same if _generated_reading(lines[i])]
        if ours:
            lines[ours[0]] = line
        elif not same:
            lines.append(line)
    return "\n".join(lines)


def merge_set_list(current, generated):
    """New setList: commands of the user are kept, the light commands of
    older versions are removed."""
    topics = {line.split(" ")[1] for line in generated if " " in line}
    lines = []
    for line in current.split("\n"):
        if not line.strip():
            continue
        legacy = LEGACY_LIGHT_SET.match(line)
        if legacy and any(t in topics for t in legacy.groups() if t):
            continue
        lines.append(line)
    names = {line.split(" ")[0].split(":")[0] for line in lines}
    for line in generated:
        if line.split(" ")[0].split(":")[0] not in names:
            lines.append(line)
    return "\n".join(lines)


async def repair_escaped_events(hash, fhem_device_name, attr, value):
    # 0.1.769 - 0.1.775 wrote a backslash before $EVENT, see perlString
    if "\\$EV" not in value:
        return value
    value = value.replace("\\$EV", "$EV")
    await fhem.CommandAttr(hash, f"{fhem_device_name} {attr} {value}")
    return value


async def set_device_attributes(hash, fhem_device_name, entities):
    """Sets readingList/setList... of the device for all its entities.

    entities: list of (component, object_id, payload_json)
    """
    attrs = generate_attributes(entities)
    for attr, merge in (
        ("readingList", merge_reading_list),
        ("setList", merge_set_list),
    ):
        current = await fhem.AttrVal(fhem_device_name, attr, "")
        current = await repair_escaped_events(hash, fhem_device_name, attr, current)
        if not attrs[attr]:
            continue
        new = merge(current, attrs[attr])
        if new != current:
            await fhem.CommandAttr(hash, f"{fhem_device_name} {attr} {new}")
    for attr in ("webCmd", "stateFormat"):
        if attr in attrs and not await fhem.AttrVal(fhem_device_name, attr, ""):
            await fhem.CommandAttr(hash, f"{fhem_device_name} {attr} {attrs[attr]}")


# fhem device name -> {(component, object_id): payload_json}
_entities = {}


async def set_attributes(hash, fhem_device_name, component, object_id, payload_json):
    """Adds the entity to the device, the attributes are set for all entities
    of the device received so far."""
    entities = _entities.setdefault(fhem_device_name, {})
    entities[(component, object_id)] = payload_json
    await set_device_attributes(
        hash,
        fhem_device_name,
        [(c, o, p) for (c, o), p in entities.items()],
    )
