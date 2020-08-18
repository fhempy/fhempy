
import asyncio
import logging
import traceback
import concurrent.futures
from zeroconf import ServiceBrowser, Zeroconf
import threading

from .. import fhem

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class mdnsscanner:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.zeroconf = None
        self.hash = None
        self.browser = None

    # zeroconf callback
    def remove_service(self, zeroconf, type, name):
        logger.debug("Service %s removed" % (name,))

    # zeroconf callback
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.debug("Service %s added, service info: %s" % (name, info))
        res = asyncio.run_coroutine_threadsafe(self.foundDevice(name, info), self.loop)
        res.result()

    async def foundDevice(self, name, info):
        try:
            def get_value(key):
                """Retrieve value and decode to UTF-8."""
                value = info.properties.get(key.encode("utf-8"))

                if value is None or isinstance(value, str):
                    return value
                return value.decode("utf-8")

            if (info.type == "_googlecast._tcp.local."):
                # check if device exists already, if not commanddefine
                if not (await fhem.checkIfDeviceExists(self.hash, "PYTHONTYPE", "googlecast", "CASTNAME", get_value('fn'))):
                    logger.debug("create device: " + get_value('fn'))
                    await fhem.CommandDefine(self.hash, get_value('md').replace(" ", "_") + "_" + get_value('fn').replace(" ", "_") +  " PythonModule googlecast '" + get_value('fn') + "'")
                else:
                    logger.debug("device " + get_value('fn') + " exists already, do not create")
            elif (info.type == "_soundtouch._tcp.local."):
                if not (await fhem.checkIfDeviceExists(self.hash, "TYPE", "BOSEST", "DEVICEID", "0")):
                    logger.debug("create bosest")
                    await fhem.CommandDefine(self.hash, "bosesystem BOSEST")
                else:
                    logger.debug("device BOSEST exists already, do not create")
            else:
                return

            await fhem.readingsSingleUpdate(self.hash, "lastFoundService", name, 1)
            # wait for the devices to initialize
            await asyncio.sleep(10)
        except Exception as err:
            logger.error(traceback.print_exc())
    
    async def runZeroconfScan(self):
        # await here to finish define before zeroconf object is created
        await asyncio.sleep(1)
        self.zeroconf = Zeroconf()
        listener = self
        services = ["_googlecast._tcp.local.", "_soundtouch._tcp.local."]
        self.browser = ServiceBrowser(self.zeroconf, services, listener)

    # FHEM
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await fhem.readingsSingleUpdate(self.hash, "state", "active", 1)
        self.loop.create_task(self.runZeroconfScan())
        return ""

    # FHEM
    async def Set(self, hash, args, argsh):
        return ""

    # FHEM
    async def Undefine(self, hash, args, argsh):
        if self.browser:
            self.browser.cancel()
        self.zeroconf.close()
