"""
Starts a service to scan in intervals for new devices.
"""

from fhempy.lib.core.ssdp import ssdp
from fhempy.lib.generic import FhemModule

from .. import fhem


class discover_upnp(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.hash = None
        self.create_devs = {}

    async def found_device(self, upnp_device):
        if upnp_device and upnp_device.udn:
            await fhem.readingsSingleUpdate(
                self.hash,
                upnp_device.udn.replace(":", ".")
                + "_"
                + upnp_device.device_type.replace(":", "."),
                upnp_device.friendly_name,
                0,
            )
            if upnp_device.device_type == "urn:schemas-upnp-org:device:MediaRenderer:1":
                self.create_devs[upnp_device.udn] = {
                    "name": "".join(filter(str.isalnum, upnp_device.friendly_name))
                    + "_"
                    + upnp_device.device_type.split(":")[-2],
                    "devname": "".join(filter(str.isalnum, upnp_device.friendly_name))
                    + "_"
                    + upnp_device.device_type.split(":")[-2],
                }
                set_config = {"create": {"args": ["device"], "options": ""}}
                set_devs = []
                for dev in self.create_devs:
                    set_devs.append(self.create_devs[dev]["name"])
                set_config["create"]["options"] = ",".join(set_devs)
                await self.set_set_config(set_config)

    async def removed_device(self, upnp_device):
        return

    # FHEM Define
    async def Define(self, hash, args, argsh):
        """Start a discovery service."""
        await super().Define(hash, args, argsh)
        await self.set_set_config({})
        ssdp.getInstance(self.logger).register_listener(self)
        await ssdp.getInstance(self.logger).start_search()
        await fhem.readingsSingleUpdate(hash, "state", "active", 0)

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon rc_SEARCH")

    async def set_create(self, hash, params):
        for udn in self.create_devs:
            if self.create_devs[udn]["name"] == params["device"]:
                await fhem.CommandDefine(
                    self.hash,
                    self.create_devs[udn]["devname"] + " fhempy dlna_dmr " + udn,
                )

    # FHEM Undefine
    async def Undefine(self, hash):
        await ssdp.getInstance(self.logger).stop_search()
        await super().Undefine(hash)
