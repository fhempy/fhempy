import asyncio

import aiomqtt

from .. import fhem, generic, utils
from ..autodiscovery.engine import Engine
from ..core import mqtt_ha
from ..core.mqtt_ha import device_info, parse_discovery


class mqtt_ha_discovery(generic.FhemModule):

    existing_devices = {}

    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)

        self.reset_existing_devices_task = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "force_autocreate": {
                "default": False,
                "format": "bool",
                "help": "Always create new devices, also while autodiscovery "
                "runs. Otherwise autodiscovery offers each new device and only "
                "existing devices are updated here.",
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
                        self._errors.success()
                        async for message in messages:
                            try:
                                await self.handle_ha_msg(message)
                            except Exception:
                                self.logger.exception(
                                    f"Failed to handle message on {message.topic}: "
                                    f"{message.payload!r}"
                                )
            except aiomqtt.MqttError as exc:
                # MqttError isn't an OSError, log it without traceback
                self._errors.failed(
                    f"MQTT connection to {self.mqtt_host}:{self.mqtt_port} lost, "
                    "reconnecting every 5s",
                    exc=ConnectionError(str(exc)),
                )
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
            await mqtt_ha.set_attributes(
                self.hash, fhem_device_name, component, object_id, payload_json
            )

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

        fhem_name = mqtt_ha.fhem_device_name(device_name, device_id)
        existing = await mqtt_ha.existing_device(self.hash, fhem_name, payload_json)
        if existing:
            self.remember_device(device_id, existing)
            return existing

        engine = Engine.running_instance()
        if engine is not None and not self._attr_force_autocreate:
            # autodiscovery offers new devices itself, also of this broker
            engine.mqtt.add_broker(
                self.mqtt_host, self.mqtt_port, self.mqtt_user, self.mqtt_pw
            )
            return None

        await fhem.CommandDefine(self.hash, f"{fhem_name} MQTT2_DEVICE")
        self.remember_device(device_id, fhem_name)
        return fhem_name
