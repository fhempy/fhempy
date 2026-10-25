"""Home Assistant MQTT discovery: parses the config messages and creates
MQTT2_DEVICEs with readingList/setList. Used by mqtt_ha_discovery and
autodiscovery, it needs no MQTT library."""

import json
import re

from .. import fhem, utils

# HomeAssistant allows abbreviated and full key names in discovery payloads.
# ESPHome sends abbreviations, Zigbee2MQTT and Tasmota the full names.
# Normalize to the abbreviations used in this module.
ABBREVIATIONS = {
    "availability_topic": "avty_t",
    "command_topic": "cmd_t",
    "components": "cmps",
    "device": "dev",
    "device_class": "dev_cla",
    "origin": "o",
    "payload_off": "pl_off",
    "payload_on": "pl_on",
    "platform": "p",
    "state_class": "stat_cla",
    "state_topic": "stat_t",
    "supported_color_modes": "sup_clrm",
    "unique_id": "uniq_id",
    "unit_of_measurement": "unit_of_meas",
}
DEVICE_ABBREVIATIONS = {
    "identifiers": "ids",
    "manufacturer": "mf",
    "model": "mdl",
    "sw_version": "sw",
}
# keys of a device discovery payload which are not inherited by its components
DEVICE_DISCOVERY_KEYS = ("dev", "o", "cmps")
# FHEM reading names may only contain these characters
INVALID_READING_CHARS = re.compile(r"[^A-Za-z0-9._\-]")
DISCOVERY_TOPIC = "homeassistant/#"


def normalize_payload(payload_json):
    """Return the payload with abbreviated keys and expanded ~ base topic."""
    payload = {ABBREVIATIONS.get(key, key): val for key, val in payload_json.items()}
    if isinstance(payload.get("dev"), dict):
        payload["dev"] = {
            DEVICE_ABBREVIATIONS.get(key, key): val
            for key, val in payload["dev"].items()
        }
    base_topic = payload.get("~")
    if isinstance(base_topic, str):
        for key, val in payload.items():
            if not (key.endswith("_t") or key.endswith("_topic")):
                continue
            if not isinstance(val, str):
                continue
            if val.startswith("~"):
                payload[key] = base_topic + val[1:]
            elif val.endswith("~"):
                payload[key] = val[:-1] + base_topic
    return payload


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
    for cmp_id, cmp_json in (payload_json.get("cmps") or {}).items():
        if not isinstance(cmp_json, dict):
            continue
        entity = {**shared, **normalize_payload(cmp_json)}
        if "dev" in payload_json:
            entity["dev"] = payload_json["dev"]
        entities.append((entity.get("p"), object_id, cmp_id, entity))
    return entities


def device_info(node_id, object_id, payload_json):
    """Return (device_name, device_id) of the entity."""
    dev = payload_json.get("dev")
    if not isinstance(dev, dict):
        dev = {}
    ids = dev.get("ids")
    if isinstance(ids, list):
        ids = ids[0] if ids else None
    if ids is None:
        ids = dev.get("cns", [[None, None]])[0][1] if dev.get("cns") else None
    device_name = dev.get("name") or node_id or ids or object_id
    device_id = ids or node_id or object_id
    return str(device_name), str(device_id)


def device_model(payload_json):
    """'manufacturer model' of the entity's device, e.g. 'Xiaomi WSDCGQ11LM'"""
    dev = payload_json.get("dev")
    if not isinstance(dev, dict):
        return ""
    parts = [dev.get("mf"), dev.get("mdl")]
    return " ".join(str(part) for part in parts if part)


def reading_name(object_id, payload_json):
    name = payload_json.get("name") or object_id
    return INVALID_READING_CHARS.sub("_", utils.gen_fhemdev_name(str(name)))


def fhem_device_name(device_name, device_id):
    name = utils.gen_fhemdev_name("MQTT2_" + device_name + "_" + device_id)
    return INVALID_READING_CHARS.sub("_", name)


async def existing_device(hash, fhem_name, payload_json):
    """Name of the MQTT2_DEVICE of the entity in FHEM, or None."""
    if str(
        await fhem.checkIfDeviceExists(hash, "TYPE", "MQTT2_DEVICE", "NAME", fhem_name)
    ) in ("1", "True"):
        return fhem_name

    # devices created by older versions or renamed by the user
    stat_t = payload_json.get("stat_t")
    if stat_t and " " not in stat_t:
        dev_exists = await fhem.CommandList(
            hash, "readingList=(?s).*" + re.escape(stat_t) + ":.* NAME"
        )
        if dev_exists and not dev_exists.startswith("No device"):
            return dev_exists.split()[0]
    return None


def generate_reading_list(object_id, payload_json):
    if not payload_json.get("stat_t"):
        return None
    return (
        payload_json["stat_t"]
        + ":.* { { "
        + reading_name(object_id, payload_json)
        + "=>lc($EVENT) } }"
    )


def generate_switch_attributes(object_id, payload_json):
    # Example
    # {
    #     "name": "yellow",
    #     "stat_t": "baerli/switch/yellow/state",
    #     "cmd_t": "baerli/switch/yellow/command",
    #     "avty_t": "baerli/status",
    #     "uniq_id": "ESPswitchyellow",
    #     "dev": {
    #         "ids": "b4e62d451d0d",
    #         "name": "baerli",
    #         "sw": "esphome v2022.8.3 Oct  8 2022, 08:35:20",
    #         "mdl": "d1_mini",
    #         "mf": "espressif",
    #     },
    # }
    name = reading_name(object_id, payload_json)
    set_list = None
    if payload_json.get("cmd_t"):
        set_list = "\n".join(
            [
                f"{name}_on {payload_json['cmd_t']} "
                f"{payload_json.get('pl_on', 'ON')}",
                f"{name}_off {payload_json['cmd_t']} "
                f"{payload_json.get('pl_off', 'OFF')}",
            ]
        )
    return (generate_reading_list(object_id, payload_json), set_list)


def generate_light_attributes(object_id, payload_json):
    # Example
    # {
    #     "schema": "json",
    #     "clrm": True,
    #     "supported_color_modes": ["brightness"],
    #     "brightness": True,
    #     "name": "Light",
    #     "stat_t": "baerli/light/light/state",
    #     "cmd_t": "baerli/light/light/command",
    #     "avty_t": "baerli/status",
    #     "uniq_id": "ESPlightlight",
    #     "dev": {
    #         "ids": "b4e62d451d0d",
    #         "name": "baerli",
    #         "sw": "esphome v2022.8.3 Oct  8 2022, 08:35:20",
    #         "mdl": "d1_mini",
    #         "mf": "espressif",
    #     },
    # }
    name = reading_name(object_id, payload_json)
    cmd_t = payload_json.get("cmd_t")
    set_list = None
    if cmd_t and payload_json.get("schema") == "json":
        set_list = [
            f'{name}_on {cmd_t} {{"state": "ON", "transition": 1}}',
            f'{name}_off {cmd_t} {{"state": "OFF", "transition": 1}}',
        ]
        color_modes = payload_json.get("sup_clrm") or []
        if "brightness" in color_modes or payload_json.get("brightness") is True:
            set_list.append(
                f"{name}_brightness:colorpicker,BRI,0,5,255 {cmd_t} "
                '{"state":"ON","brightness":$EVTPART1}'
            )
    elif cmd_t:
        set_list = [
            f"{name}_on {cmd_t} {payload_json.get('pl_on', 'ON')}",
            f"{name}_off {cmd_t} {payload_json.get('pl_off', 'OFF')}",
        ]
    if set_list:
        set_list = "\n".join(set_list)
    return (generate_reading_list(object_id, payload_json), set_list)


def generate_sensor_attributes(object_id, payload_json):
    # Example
    # {
    #     "dev_cla": "voltage",
    #     "unit_of_meas": "V",
    #     "stat_cla": "measurement",
    #     "name": "luminance",
    #     "stat_t": "airpurifier/sensor/luminance/state",
    #     "avty_t": "airpurifier/status",
    #     "uniq_id": "807d3a78f153-adc",
    #     "dev": {
    #         "ids": "807d3a78f153",
    #         "name": "airpurifier",
    #         "sw": "esphome v2022.9.4 Nov 19 2022, 09:04:05",
    #         "mdl": "d1_mini",
    #         "mf": "espressif",
    #     },
    # }
    return (generate_reading_list(object_id, payload_json), None)


GENERATORS = {
    "switch": generate_switch_attributes,
    "light": generate_light_attributes,
    "sensor": generate_sensor_attributes,
}


async def repair_escaped_events(hash, fhem_device_name, attr, value):
    # 0.1.769 - 0.1.775 wrote a backslash before $EVENT, see perlString
    if "\\$EV" not in value:
        return value
    value = value.replace("\\$EV", "$EV")
    await fhem.CommandAttr(hash, f"{fhem_device_name} {attr} {value}")
    return value


async def set_attributes(hash, fhem_device_name, component, object_id, payload_json):
    """Adds the topics of the entity to readingList/setList of the device."""
    if not payload_json.get("stat_t") and not payload_json.get("cmd_t"):
        return

    cur_readingList = await fhem.AttrVal(fhem_device_name, "readingList", "")
    cur_setList = await fhem.AttrVal(fhem_device_name, "setList", "")
    cur_readingList = await repair_escaped_events(
        hash, fhem_device_name, "readingList", cur_readingList
    )
    cur_setList = await repair_escaped_events(
        hash, fhem_device_name, "setList", cur_setList
    )

    generator = GENERATORS.get(component)
    if generator is None:
        return
    readingList, setList = generator(object_id, payload_json)

    # check if topic is already in the attribute
    if readingList and cur_readingList.find(payload_json["stat_t"]) == -1:
        if cur_readingList != "":
            cur_readingList += "\n"
        new_readingList = cur_readingList + readingList
        await fhem.CommandAttr(
            hash, f"{fhem_device_name} readingList {new_readingList}"
        )

    if setList and cur_setList.find(payload_json["cmd_t"]) == -1:
        if cur_setList != "":
            cur_setList += "\n"
        new_setList = cur_setList + setList
        await fhem.CommandAttr(hash, f"{fhem_device_name} setList {new_setList}")
