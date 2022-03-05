# THANKS to https://github.com/AlexxIT/XiaomiGateway3 for the HASS implementation
# which I used as a base for the FHEM implementation

# current version is based on https://github.com/AlexxIT/XiaomiGateway3/tree/360c6d8ecc41f70ecf4f536e51bf379383f56200

import asyncio
import functools
import logging

from .. import fhem, utils
from .. import generic
from .core.gateway3 import GatewayEntry
from .core.utils import update_zigbee_firmware

DOMAINS = [
    "binary_sensor",
    "climate",
    "cover",
    "light",
    "remote",
    "sensor",
    "switch",
    "alarm_control_panel",
    "device_tracker",
]


class xiaomi_gateway3(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.gw = None
        self.devices = {}
        self.fhempy_devices = {}

        attr_conf = {"disable": {"options": "0,1", "default": "0", "format": "int"}}
        self.set_attr_config(attr_conf)

        set_conf = {
            "activate_zigbee2mqtt": {
                "help": (
                    "You need to install zigbee2mqtt aftewards<br>"
                    "=> https://www.zigbee2mqtt.io/getting_started/running_zigbee2mqtt.html#2-installing<br>"
                    "Set following lines in configuration.yaml<br>"
                    " serial:<br>"
                    "   port: tcp://GATEWAY_IP_ADDRESS:8888<br>"
                    "   adapter: ezsp<br>"
                    " mqtt:<br>"
                    "   client_id: zigbee_pi<br>"
                    "PLEASE CHECK THE LOG FILE AFTER CLICKING HERE, "
                    "DO NOT DISCONNECT GATEWAY FROM POWER"
                )
            },
            "deactivate_zigbee2mqtt": {},
        }
        self.set_set_config(set_conf)

    @property
    def gateway3(self):
        return self.gw.gateway3

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self.hash = hash

        if self._attr_disable == 1:
            return

        if len(args) < 5:
            return "Usage: define devname fhempy xiaomi_gateway3 <IP> <TOKEN>"

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon mqtt")
        await fhem.readingsSingleUpdateIfChanged(hash, "state", "disconnected", 1)

        logging.getLogger("fhempy.lib.xiaomi_gateway3.core.gateway3").setLevel(
            logging.ERROR
        )

        hash["HOST"] = args[3]
        hash["TOKEN"] = args[4]

        self.host = args[3]
        self.token = args[4]

        self.create_async_task(self.connect_gw())

        return ""

    async def set_activate_zigbee2mqtt(self, hash, params):
        self.create_async_task(update_zigbee_firmware(self.host, True))
        await fhem.readingsSingleUpdateIfChanged(hash, "zigbee2mqtt", "on", 1)

    async def set_deactivate_zigbee2mqtt(self, hash, params):
        self.create_async_task(update_zigbee_firmware(self.host, False))
        await fhem.readingsSingleUpdateIfChanged(hash, "zigbee2mqtt", "off", 1)

    async def set_attr_disable(self, hash):
        if self._attr_disable and self.gw is not None:
            await self.gw.stop()
            self.cancel_async_task(self.is_connected_task)
        else:
            self.create_async_task(self.connect_gw())

    async def register_device(self, fhempy_device, handler):
        did = fhempy_device.did
        self.fhempy_devices[did] = fhempy_device
        # wait till gateway is ready
        while self.gw is None:
            await asyncio.sleep(3)
        # if did == "lumi.0":
        #    self.gw.add_stats(did, handler)
        await asyncio.sleep(3)
        if did in self.devices and "init" in self.devices[did]:
            await fhempy_device.initialize(self.devices[did])

    async def connect_gw(self):
        await asyncio.sleep(0)
        self.gw = FhempyGateway(self.logger)
        z2m = await fhem.ReadingsVal(self.hash["NAME"], "zigbee2mqtt", "off")
        if z2m == "on":
            await self.gw.create_gateway(self.hash, self.host, self.token, zha=True)
        else:
            await self.gw.create_gateway(self.hash, self.host, self.token, zha=False)
            # prepare domains
            for domain in DOMAINS:
                self.gw.add_setup(domain, self.create_device)
        # start check task
        self.is_connected_task = self.create_async_task(self.is_connected())
        # run gateway
        self.gw.start()

    async def is_connected(self):
        last_was_connected = False
        while True:
            if await self.gw.is_connected():
                if last_was_connected is False:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "connected", 1
                    )
                    last_was_connected = True
            else:
                if last_was_connected is True:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "disconnected", 1
                    )
                    last_was_connected = False
            await asyncio.sleep(60)

    async def create_device(self, gw, device, type):
        self.logger.debug(f"Check if device {device['did']} exists")
        did = device["did"]
        self.devices[did] = device
        if not await fhem.checkIfDeviceExists(
            self.hash, "PYTHONTYPE", "xiaomi_gateway3_device", "DID", did
        ):
            devname = (
                "".join(filter(str.isalnum, str(device["model"]))) + "_" + device["mac"]
            )
            await fhem.CommandDefine(
                self.hash,
                devname
                + " fhempy xiaomi_gateway3_device "
                + self.hash["NAME"]
                + " "
                + did,
            )
        else:
            if "init" in device and did in self.fhempy_devices:
                if did == "lumi." + device["mac"]:
                    device["version"] = self.gw.version()
                await self.fhempy_devices[did].initialize(device)
        # wait for fhem
        await asyncio.sleep(2)


class FhempyGateway:
    def __init__(self, logger):
        self.loop = asyncio.get_event_loop()

    async def create_gateway(self, hash, host, token, **options):
        self.gw = GatewayEntry(host=host, token=token, **options)

    @property
    def gateway3(self):
        return self.gw

    def add_setup(self, domain, handler):
        async def setup(gw, device, attr):
            await handler(gw, device, attr)

        self.gw.add_setup(domain, setup)

    def version(self):
        return self.gw.ver

    def start(self):
        self.gw.start()

    async def stop(self):
        await self.gw.stop()

    async def is_connected(self):
        return await self.gw.check_port(23)
