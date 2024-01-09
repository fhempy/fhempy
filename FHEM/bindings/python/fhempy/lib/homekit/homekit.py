import asyncio
import json
import logging
from typing import cast

import aiohomekit
from aiohomekit.model.characteristics.characteristic import NUMBER_TYPES
from aiohomekit.model.characteristics.characteristic_types import CharacteristicsTypes
from zeroconf import IPVersion, ServiceStateChange
from zeroconf.asyncio import (
    AsyncServiceBrowser,
    AsyncServiceInfo,
    AsyncZeroconfServiceTypes,
)

from .. import fhem
from .. import fhem_pythonbinding as fhempy
from .. import generic, utils
from ..core import zeroconf

HOMEKIT_SERVICES = ["_hap._udp.local.", "_hap._tcp.local."]


class homekit(generic.FhemModule):

    controller: aiohomekit.Controller = None
    aiobrowser: AsyncServiceBrowser = None

    def async_on_service_state_change(
        zeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        if service_type in HOMEKIT_SERVICES:
            # print(
            #    f"Service {name} of type {service_type} state changed: {state_change}"
            # )
            if state_change is not ServiceStateChange.Added:
                return
            asyncio.ensure_future(
                homekit.async_display_service_info(zeroconf, service_type, name)
            )

    async def async_display_service_info(
        zeroconf, service_type: str, name: str
    ) -> None:
        info = AsyncServiceInfo(service_type, name)
        await info.async_request(zeroconf, 3000)
        # print("Info from zeroconf.get_service_info: %r" % (info))
        if info:
            addresses = [
                "%s:%d" % (addr, cast(int, info.port))
                for addr in info.parsed_scoped_addresses()
            ]
            # print("  Name: %s" % name)
            # print("  Addresses: %s" % ", ".join(addresses))
            # print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            # print(f"  Server: {info.server}")
        # else:
        #    print("  No info")
        # print("\n")
        discovery_info = info
        properties = {
            key.lower().decode(): value
            for (key, value) in discovery_info.properties.items()
        }
        # print(f"props: {properties}")
        status_flags = int(properties["sf"])
        paired = not status_flags & 0x01
        # print(f"paired: {paired}")
        hkid = properties["id"].lower()
        model = properties["md"]

    async def get_controller():
        if homekit.controller is None:
            aio_zc = zeroconf.zeroconf.get_instance(
                logging.Logger("homekit")
            ).get_async_zeroconf()
            services = HOMEKIT_SERVICES
            homekit.aiobrowser = AsyncServiceBrowser(
                aio_zc.zeroconf,
                services,
                handlers=[homekit.async_on_service_state_change],
            )
            homekit.controller = aiohomekit.Controller(aio_zc)
            await homekit.controller.async_start()
        return homekit.controller

    def __init__(self, logger):
        self._ready = asyncio.Event()
        super().__init__(logger)

    @property
    def ready(self):
        return self._ready

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60 seconds.",
            },
            "pairing_data": {
                "default": "{}",
                "format": "json",
                "help": "Pairing data from HomeKit device",
            },
        }
        await self.set_attr_config(attr_config)

        self.set_config = {}
        await self.set_set_config(self.set_config)

        if len(args) != 5:
            return (
                "Usage: define velux_gateway fhempy homekit HOMEKITID|GW_NAME PIN|AID"
            )
        if args[4].find("-") > -1:
            # homekit pin found
            hash["HOMEKIT_ID"] = args[3]
            hash["HOMEKIT_PIN"] = args[4]
            self.create_async_task(
                self.setup_gateway_device(hash["HOMEKIT_ID"], args[4])
            )
        else:
            hash["HOMEKIT_GW"] = args[3]
            hash["HOMEKIT_AID"] = args[4]
            self.create_async_task(self.setup_device(args[3], int(args[4])))

    async def set_attr_pairing_data(self, hash):
        await self.setup_gateway_device(hash["HOMEKIT_ID"], hash["HOMEKIT_PIN"])

    async def setup_gateway_device(self, homekitid, pin):
        controller = await homekit.get_controller()

        self.pairing = None
        if self._attr_pairing_data == {}:
            # not paired yet
            discovery = await controller.async_find(homekitid)
            finish_pairing = await discovery.async_start_pairing(homekitid)
            self.pairing = await finish_pairing(pin)
            pairing_data = json.dumps(self.pairing.pairing_data)
            await fhem.CommandAttr(
                self.hash, f"{self.hash['NAME']} pairing_data {pairing_data}"
            )
        else:
            self.pairing = controller.load_pairing(
                self._attr_pairing_data["AccessoryPairingID"],
                dict(self._attr_pairing_data),
            )

        name = await self.pairing.get_primary_name()
        await fhem.readingsSingleUpdate(self.hash, "name", name, 1)

        accessories = await self.pairing.list_accessories_and_characteristics()
        for accessory in accessories:
            devname = utils.gen_fhemdev_name(
                f"hkdev_{self.hash['HOMEKIT_ID']}_{accessory['aid']}"
            )
            dev_ex = await fhem.checkIfDeviceExists(
                self.hash,
                "HOMEKIT_GW",
                self.hash["NAME"],
                "HOMEKIT_AID",
                str(accessory["aid"]),
            )
            if dev_ex:
                continue

            await fhem.CommandDefine(
                self.hash,
                f"{devname} fhempy homekit {self.hash['NAME']} {accessory['aid']}",
            )

        self._ready.set()

    async def setup_device(self, gw_device_name, aid):
        controller = await homekit.get_controller()
        # load pairing data from homekit gateway
        gw_device = fhempy.getFhemPyDeviceByName(gw_device_name)
        await gw_device.ready.wait()
        self.pairing = controller.load_pairing(
            gw_device._attr_pairing_data["AccessoryPairingID"],
            dict(gw_device._attr_pairing_data),
        )
        gw_name = await self.pairing.get_primary_name()
        await fhem.readingsSingleUpdateIfChanged(self.hash, "gw_name", gw_name, 1)

        for accessory in self.pairing.accessories:
            if accessory.aid == aid:
                for service in accessory.services:
                    for char in service.characteristics:
                        if "pw" in char.perms:
                            # char.type convert to string (position_target)
                            await self.char_to_set(char)
                        if "pr" in char.perms:
                            if char.description:
                                reading = char.description
                            else:
                                reading = char.type
                            await fhem.readingsSingleUpdateIfChanged(
                                self.hash,
                                utils.gen_reading_name(reading),
                                char.value,
                                1,
                            )

        await self.set_set_config(self.set_config)

    async def set_int(self, hash, params):
        char = params["function_param"]
        self.create_async_task(
            self.pairing.put_characteristics(
                [(int(self.hash["HOMEKIT_AID"]), char.iid, params["new_value"])]
            )
        )

    async def char_to_set(self, char):
        if char.format in NUMBER_TYPES:
            self.set_config[utils.gen_reading_name(char.description)] = {
                "args": ["new_value"],
                "params": {"new_value": {"format": "int"}},
                "function": "set_int",
                "function_param": char,
                "options": f"slider,{char.minValue},{char.minStep},{char.maxValue},1",
            }
