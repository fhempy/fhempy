
import asyncio
import logging
import concurrent.futures
from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes

from .. import fhem

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class mdnsscanner:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.zeroconf = None
        self.hash = None
        self.foundDeviceActive = 0

    def remove_service(self, zeroconf, type, name):
        logger.debug("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.debug("Service %s added, service info: %s" % (name, info))
        self.loop.create_task(self.foundDevice(name, info))

    async def foundDevice(self, name, info):
        # due to non async callback, we need to make sure that only one process runs
        while True:
            if self.foundDeviceActive == 1:
                await asyncio.sleep(1)
            else:
                break

        self.foundDeviceActive = 1
        def get_value(key):
            """Retrieve value and decode to UTF-8."""
            value = info.properties.get(key.encode("utf-8"))

            if value is None or isinstance(value, str):
                return value
            return value.decode("utf-8")

        if (info.type == "_googlecast._tcp.local."):
            # TODO check if device exists already, if not commanddefine
            await fhem.CommandDefine(self.hash, get_value('md').replace(" ", "_") + "_" + get_value('fn').replace(" ", "_") +  " PythonModule googlecast '" + get_value('fn') + "'")
        self.foundDeviceActive = 0

    async def runZeroconfFind(self):
        return ",".join(ZeroconfServiceTypes.find())
    
    async def runZeroconfScan(self):
        self.zeroconf = Zeroconf()
        listener = self
        services = ["_googlecast._tcp.local.", "_soundtouch._tcp.local."]
        browser = ServiceBrowser(self.zeroconf, services, listener)

    # FHEM
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self.loop.create_task(self.runZeroconfScan())
        return ""

    # FHEM
    async def Set(self, hash, args, argsh):
        return ""

    # FHEM
    async def Undefine(self, hash, args, argsh):
        self.zeroconf.close()
