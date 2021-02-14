# THANKS to https://github.com/AlexxIT/XiaomiGateway3 for the HASS implementation
# which I used as a base for the FHEM implementation

import asyncio
import functools
import logging

from .. import fhem, utils
from ..generic import FhemModule
from .core.gateway3 import Gateway3

DOMAINS = [
    "binary_sensor",
    "climate",
    "cover",
    "light",
    "remote",
    "sensor",
    "switch",
    "alarm_control_panel",
]


class xiaomi_gateway3(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.gw = None
        self.devices = {}
        self.fhempy_devices = {}

    @property
    def gateway3(self):
        return self.gw.gateway3

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self.hash = hash

        if len(args) < 5:
            return "Usage: define devname PythonModule xiaomi_gateway3 <IP> <TOKEN>"

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

    async def register_device(self, fhempy_device, handler):
        did = fhempy_device.did
        self.fhempy_devices[did] = fhempy_device
        # wait till gateway is ready
        while self.gw is None:
            await asyncio.sleep(3)
        self.gw.add_update(did, handler)
        if did == "lumi.0":
            self.gw.add_stats(did, handler)
        if did in self.devices and "init" in self.devices[did]:
            await fhempy_device.initialize(self.devices[did])

    async def connect_gw(self):
        config = {"devices": {}}
        self.gw = FhempyGateway(self.logger, self.hash, self.host, self.token, config)
        # prepare domains
        for domain in DOMAINS:
            self.gw.add_setup(domain, self.create_device)
        # start check task
        self.create_async_task(self.is_connected())
        # run gateway
        self.gw.start()

    async def is_connected(self):
        while True:
            if await self.gw.is_connected():
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "connected", 1
                )
            else:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "disconnected", 1
                )
            await asyncio.sleep(60)

    async def create_device(self, gw, device, type):
        self.logger.debug(f"Check if device {device['did']} exists")
        did = device["did"]
        self.devices[did] = device
        if did == "lumi.0":
            did = "lumi." + device["mac"]
        if not await fhem.checkIfDeviceExists(
            self.hash, "PYTHONTYPE", "xiaomi_gateway3_device", "DID", did
        ):
            devname = (
                "".join(filter(str.isalnum, device["model"])) + "_" + device["mac"]
            )
            await fhem.CommandDefine(
                self.hash,
                devname
                + " PythonModule xiaomi_gateway3_device "
                + self.hash["NAME"]
                + " "
                + did,
            )
        else:
            if "init" in device and did in self.fhempy_devices:
                if did == "lumi." + device["mac"]:
                    device["version"] = self.gw.version()
                await self.fhempy_devices[did].initialize(device)


class FhempyGateway:
    def __init__(self, logger, hash, host, token, config):
        self.gw = Gateway3(host, token, config)
        self.loop = asyncio.get_event_loop()

    @property
    def gateway3(self):
        return self.gw

    def add_setup(self, domain, handler):
        def setup(gw, device, attr):
            asyncio.run_coroutine_threadsafe(
                handler(gw, device, attr), self.loop
            ).result()

        self.gw.add_setup(domain, setup)

    def add_update(self, did, handler):
        def update(data):
            asyncio.run_coroutine_threadsafe(handler(data), self.loop).result()

        self.gw.add_update(did, update)

    def add_stats(self, ieee, handler):
        def stats(data):
            asyncio.run_coroutine_threadsafe(handler(data), self.loop).result()

        self.gw.add_stats(ieee, stats)

    def version(self):
        return self.gw.ver

    def start(self):
        self.gw.start()

    async def is_connected(self):
        return await utils.run_blocking(functools.partial(self.gw._check_port, 23))
