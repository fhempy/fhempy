import asyncio
import json
import re

import aiomqtt

from .. import fhem, generic, utils

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


def reading_name(object_id, payload_json):
    name = payload_json.get("name") or object_id
    return INVALID_READING_CHARS.sub("_", utils.gen_fhemdev_name(str(name)))


class mqtt_ha_discovery(generic.FhemModule):

    existing_devices = {}

    def __init__(self, logger):
        super().__init__(logger)

        self.reset_existing_devices_task = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "force_autocreate": {
                "default": False,
                "format": "bool",
                "help": "Always create a new device on discovery.",
            }
        }
        await self.set_attr_config(attr_config)

        set_config = {}
        await self.set_set_config(set_config)

        if len(args) > 7:
            return "Usage: define mqttdiscovery fhempy mqtt_ha_discovery"

        if len(args) > 3:
            self.mqtt_host = args[3]
        else:
            self.mqtt_host = "127.0.0.1"

        if len(args) > 4:
            self.mqtt_port = int(args[4])
        else:
            self.mqtt_port = 1883

        if len(args) > 5:
            self.mqtt_user = args[5]
        else:
            self.mqtt_user = None

        if len(args) > 6:
            self.mqtt_pw = args[6]
        else:
            self.mqtt_pw = None

        self.create_async_task(self.setup())

    async def setup(self):
        await self.connect_to_broker()

    async def connect_to_broker(self):
        while True:
            try:
                async with aiomqtt.Client(
                    self.mqtt_host,
                    self.mqtt_port,
                    username=self.mqtt_user,
                    password=self.mqtt_pw,
                    logger=self.logger,
                ) as client:
                    async with client.messages() as messages:
                        await client.subscribe("homeassistant/#")
                        async for message in messages:
                            try:
                                await self.handle_ha_msg(message)
                            except Exception:
                                self.logger.exception(
                                    f"Failed to handle message on {message.topic}: "
                                    f"{message.payload!r}"
                                )
            except aiomqtt.MqttError:
                self.logger.error("Connection lost; Reconnecting in 5 seconds ...")
                await asyncio.sleep(5)

    async def handle_ha_msg(self, msg):
        topic = msg.topic.value
        try:
            entities = parse_discovery(topic, msg.payload)
        except ValueError:
            self.logger.debug(f"Ignore invalid discovery payload on {topic}")
            return

        for component, node_id, object_id, payload_json in entities:
            device_name, device_id = device_info(node_id, object_id, payload_json)
            fhem_device_name = await self.create_device(
                device_name, device_id, payload_json
            )
            if fhem_device_name is None:
                continue
            await self.set_attributes(
                fhem_device_name, component, object_id, payload_json
            )

    async def set_attributes(
        self, fhem_device_name, component, object_id, payload_json
    ):
        if not payload_json.get("stat_t") and not payload_json.get("cmd_t"):
            return

        cur_readingList = await fhem.AttrVal(fhem_device_name, "readingList", "")
        cur_setList = await fhem.AttrVal(fhem_device_name, "setList", "")
        cur_readingList = await self.repair_escaped_events(
            fhem_device_name, "readingList", cur_readingList
        )
        cur_setList = await self.repair_escaped_events(
            fhem_device_name, "setList", cur_setList
        )

        # get attribute based on topic
        readingList = None
        setList = None
        if component == "switch":
            readingList, setList = await self.generate_switch_attributes(
                object_id, payload_json
            )
        elif component == "light":
            readingList, setList = await self.generate_light_attributes(
                object_id, payload_json
            )
        elif component == "sensor":
            readingList, setList = await self.generate_sensor_attributes(
                object_id, payload_json
            )

        # check if topic is already in the attribute
        if readingList and cur_readingList.find(payload_json["stat_t"]) == -1:
            if cur_readingList != "":
                cur_readingList += "\n"
            new_readingList = cur_readingList + readingList
            await fhem.CommandAttr(
                self.hash, f"{fhem_device_name} readingList {new_readingList}"
            )

        if setList and cur_setList.find(payload_json["cmd_t"]) == -1:
            if cur_setList != "":
                cur_setList += "\n"
            new_setList = cur_setList + setList
            await fhem.CommandAttr(
                self.hash, f"{fhem_device_name} setList {new_setList}"
            )

    async def repair_escaped_events(self, fhem_device_name, attr, value):
        # 0.1.769 - 0.1.775 wrote a backslash before $EVENT, see perlString
        if "\\$EV" not in value:
            return value
        value = value.replace("\\$EV", "$EV")
        await fhem.CommandAttr(self.hash, f"{fhem_device_name} {attr} {value}")
        return value

    def generate_reading_list(self, object_id, payload_json):
        if not payload_json.get("stat_t"):
            return None
        return (
            payload_json["stat_t"]
            + ":.* { { "
            + reading_name(object_id, payload_json)
            + "=>lc($EVENT) } }"
        )

    async def generate_switch_attributes(self, object_id, payload_json):
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
        return (self.generate_reading_list(object_id, payload_json), set_list)

    async def generate_light_attributes(self, object_id, payload_json):
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
        return (self.generate_reading_list(object_id, payload_json), set_list)

    async def generate_sensor_attributes(self, object_id, payload_json):
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
        return (self.generate_reading_list(object_id, payload_json), None)

    async def reset_existing_devices(self):
        await asyncio.sleep(60)
        mqtt_ha_discovery.existing_devices.clear()
        self.reset_existing_devices_task = None

    def remember_device(self, device_id, fhem_name):
        mqtt_ha_discovery.existing_devices[device_id] = fhem_name
        if self.reset_existing_devices_task is None:
            self.reset_existing_devices_task = self.create_async_task(
                self.reset_existing_devices()
            )

    async def create_device(self, device_name, device_id, payload_json):
        if device_id in mqtt_ha_discovery.existing_devices:
            return mqtt_ha_discovery.existing_devices[device_id]

        fhem_name = utils.gen_fhemdev_name("MQTT2_" + device_name + "_" + device_id)
        fhem_name = INVALID_READING_CHARS.sub("_", fhem_name)

        if str(
            await fhem.checkIfDeviceExists(
                self.hash, "TYPE", "MQTT2_DEVICE", "NAME", fhem_name
            )
        ) in ("1", "True"):
            self.remember_device(device_id, fhem_name)
            return fhem_name

        # devices created by older versions or renamed by the user
        stat_t = payload_json.get("stat_t")
        if stat_t and " " not in stat_t:
            dev_exists = await fhem.CommandList(
                self.hash, "readingList=(?s).*" + re.escape(stat_t) + ":.* NAME"
            )
            if dev_exists and not dev_exists.startswith("No device"):
                fhem_name = dev_exists.split()[0]
                self.remember_device(device_id, fhem_name)
                return fhem_name

        await fhem.CommandDefine(self.hash, f"{fhem_name} MQTT2_DEVICE")
        self.remember_device(device_id, fhem_name)
        return fhem_name
