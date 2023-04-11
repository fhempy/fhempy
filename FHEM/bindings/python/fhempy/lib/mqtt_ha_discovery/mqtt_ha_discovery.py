import asyncio
import json

import asyncio_mqtt as aiomqtt

from .. import fhem, generic, utils


class mqtt_ha_discovery(generic.FhemModule):

    existing_devices = []

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
                        await self.handle_ha_msg(message)
        except aiomqtt.MqttError:
            self.logger.error("Connection lost; Reconnecting in 5 seconds ...")
            await asyncio.sleep(5)

    async def handle_ha_msg(self, msg):
        topic = msg.topic.value
        payload = msg.payload
        payload_json = json.loads(payload)

        device_name = payload_json["dev"]["name"]
        fhem_device_name = await self.create_device(topic, device_name, payload_json)
        await self.set_attributes(fhem_device_name, topic, payload_json)

    async def set_attributes(self, fhem_device_name, topic, payload_json):
        cur_readingList = await fhem.AttrVal(fhem_device_name, "readingList", "")
        cur_setList = await fhem.AttrVal(fhem_device_name, "setList", "")

        # split topic
        _, component, dev_name, object_id, topic_type = topic.split("/")

        if topic_type != "config":
            return

        # get attribute based on topic
        readingList = None
        setList = None
        if component == "switch":
            readingList, setList = await self.generate_switch_attributes(
                object_id, topic, payload_json
            )
        elif component == "light":
            readingList, setList = await self.generate_light_attributes(
                object_id, topic, payload_json
            )
        elif component == "sensor":
            readingList, setList = await self.generate_sensor_attributes(
                object_id, topic, payload_json
            )

        # check if topic is already in the attribute
        if readingList and cur_readingList.find(payload_json.get("stat_t")) == -1:
            if cur_readingList != "":
                cur_readingList += "\n"
            new_readingList = cur_readingList + readingList
            await fhem.CommandAttr(
                self.hash, f"{fhem_device_name} readingList {new_readingList}"
            )

        if setList and cur_setList.find(payload_json.get("cmd_t")) == -1:
            if cur_setList != "":
                cur_setList += "\n"
            new_setList = cur_setList + setList
            await fhem.CommandAttr(
                self.hash, f"{fhem_device_name} setList {new_setList}"
            )

    async def generate_switch_attributes(self, object_id, topic, payload_json):
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

        # create readingList entry
        reading_list = [
            payload_json["stat_t"]
            + ":.* { { "
            + payload_json["name"]
            + "=>lc(\$EVENT) } }"
        ]
        # create setList entry
        set_list = [
            payload_json["name"] + "_on " + payload_json["cmd_t"] + " on",
            payload_json["name"] + "_off " + payload_json["cmd_t"] + " off",
        ]
        return ("\n".join(reading_list), "\n".join(set_list))

    async def generate_light_attributes(self, object_id, topic, payload_json):
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

        # create readingList entry
        reading_list = [
            payload_json["stat_t"]
            + ":.* { { "
            + payload_json["name"]
            + "=>lc(\$EVENT) } }"
        ]
        # create setList entry
        set_list = [
            payload_json["name"]
            + "_on "
            + payload_json["cmd_t"]
            + '{"state": "on", "transition": 1}',
            payload_json["name"]
            + "_off "
            + payload_json["cmd_t"]
            + '{"state": "on", "transition": 1}',
        ]
        if "brightness" in payload_json["supported_color_modes"]:
            set_list.append(
                payload_json["name"]
                + "_brightness:colorpicker,BRI,0,5,255 "
                + payload_json["cmd_t"]
                + '{"state":"on","\$EVTPART0":"\$EVTPART1"}'
            )
        return ("\n".join(reading_list), "\n".join(set_list))

    async def generate_sensor_attributes(self, object_id, topic, payload_json):
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

        # create readingList entry
        reading_list = [
            payload_json["stat_t"]
            + ":.* { { "
            + payload_json["name"]
            + "=>lc(\$EVENT) } }"
        ]
        return ("\n".join(reading_list), None)

    async def reset_existing_devices(self):
        await asyncio.sleep(60)
        mqtt_ha_discovery.existing_devices.clear()

    async def create_device(self, topic, device_name, payload_json):
        if device_name in mqtt_ha_discovery.existing_devices:
            return

        dev_exists = await fhem.CommandList(
            self.hash, "readingList=.*" + device_name + "/.* NAME"
        )
        if dev_exists:
            mqtt_ha_discovery.existing_devices.append(device_name)
            if self.reset_existing_devices_task is None:
                self.reset_existing_devices_task = self.create_async_task(
                    self.reset_existing_devices()
                )
            return dev_exists.split()[0]

        fhem_name = utils.gen_fhemdev_name(
            "MQTT2_" + device_name + "_" + payload_json["dev"]["ids"]
        )

        await fhem.CommandDefine(self.hash, f"{fhem_name} MQTT2_DEVICE")
        return fhem_name
