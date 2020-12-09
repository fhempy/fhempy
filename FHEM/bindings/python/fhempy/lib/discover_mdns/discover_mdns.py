import asyncio
import logging
import traceback
import concurrent.futures
from zeroconf import ServiceBrowser, Zeroconf
import threading

from .. import fhem
from ..core.zeroconf import zeroconf


class discover_mdns:
    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self.zeroconf = None
        self.hash = None
        self.browser = None

    # zeroconf callback
    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        self.logger.debug("Service %s updated, service info: %s" % (name, info))
        res = asyncio.run_coroutine_threadsafe(self.foundDevice(name, info), self.loop)
        res.result()

    # zeroconf callback
    def remove_service(self, zeroconf, type, name):
        self.logger.debug("Service %s removed" % (name))

    # zeroconf callback
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        self.logger.debug("Service %s added, service info: %s" % (name, info))
        res = asyncio.run_coroutine_threadsafe(self.foundDevice(name, info), self.loop)
        res.result()

    async def foundDevice(self, name, info):
        if info is None:
            return
        try:

            def get_value(key):
                """Retrieve value and decode to UTF-8."""
                value = info.properties.get(key.encode("utf-8"))

                if value is None or isinstance(value, str):
                    return value
                return value.decode("utf-8")

            if info.type == "_googlecast._tcp.local.":
                # check if device exists already, if not commanddefine
                if not (
                    await fhem.checkIfDeviceExists(
                        self.hash,
                        "PYTHONTYPE",
                        "googlecast",
                        "CASTNAME",
                        get_value("fn"),
                    )
                ):
                    self.logger.debug("create device: " + get_value("fn"))
                    await fhem.CommandDefine(
                        self.hash,
                        get_value("md").replace(" ", "_")
                        + "_"
                        + get_value("fn").replace(" ", "_")
                        + " PythonModule googlecast '"
                        + get_value("fn")
                        + "'",
                    )
                else:
                    self.logger.debug(
                        "device " + get_value("fn") + " exists already, do not create"
                    )
            elif info.type == "_soundtouch._tcp.local.":
                if not (
                    await fhem.checkIfDeviceExists(
                        self.hash, "TYPE", "BOSEST", "DEVICEID", "0"
                    )
                ):
                    self.logger.debug("create bosest")
                    await fhem.CommandDefine(self.hash, "bosesystem BOSEST")
                else:
                    self.logger.debug("device BOSEST exists already, do not create")
            elif (
                info.type == "_http._tcp.local."
                and info.name == "fhempy._http._tcp.local."
            ):
                if not (
                    await fhem.checkIfDeviceExists(
                        self.hash, "TYPE", "BindingsIo", "IP", get_value("ip")
                    )
                ):
                    ip = get_value("ip")
                    port = get_value("port")
                    ipstr = ip.replace(".", "_")
                    await fhem.CommandDefine(
                        self.hash, f"fhempy_peer_{ipstr} BindingsIo {ip}:{port} Python"
                    )
            else:
                return

            # wait for the devices to initialize
            await asyncio.sleep(10)
        except Exception as err:
            self.logger.error(traceback.print_exc())

    async def runZeroconfScan(self):
        # await here to finish define before zeroconf object is created
        await asyncio.sleep(1)
        self.zeroconf = zeroconf.get_instance(self.logger).get_zeroconf()
        listener = self
        services = [
            "_googlecast._tcp.local.",
            "_soundtouch._tcp.local.",
            "_http._tcp.local.",
        ]
        self.browser = ServiceBrowser(self.zeroconf, services, listener)

    # FHEM
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await fhem.readingsSingleUpdate(self.hash, "state", "active", 1)
        self.loop.create_task(self.runZeroconfScan())

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon rc_SEARCH")

        return ""

    # FHEM
    async def Set(self, hash, args, argsh):
        return ""

    # FHEM
    async def Undefine(self, hash):
        if self.browser:
            self.browser.cancel()
