import asyncio
import concurrent.futures
import logging
import threading
import traceback

from fhempy.lib import fhem
from fhempy.lib.core.zeroconf import zeroconf
from zeroconf import ServiceBrowser, Zeroconf


class discover_fhempy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.zeroconf = None
        self.browser = None
        self.hash = {"NAME": "discover_fhempy"}

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

            if info.type == "_http._tcp.local." and info.name[0:6] == "fhempy":
                if get_value("ip") is not None:
                    if not (
                        await fhem.checkIfDeviceExists(
                            self.hash, "TYPE", "BindingsIo", "IP", get_value("ip")
                        )
                    ):
                        ip = get_value("ip")
                        port = get_value("port")
                        ipstr = ip.replace(".", "_")
                        await fhem.CommandDefine(
                            self.hash,
                            f"fhempy_peer_{ipstr} BindingsIo {ip}:{port} Python",
                        )
            else:
                return

            # wait for the devices to initialize
            await asyncio.sleep(10)
        except Exception as err:
            self.logger.error(traceback.print_exc())

    async def runZeroconfScan(self):
        self.zeroconf = zeroconf.get_instance(self.logger).get_zeroconf()
        listener = self
        services = [
            "_http._tcp.local.",
        ]
        self.browser = ServiceBrowser(self.zeroconf, services, listener)

    async def activate(self):
        await self.runZeroconfScan()
        return ""

    async def deactivate(self):
        if self.browser:
            self.browser.cancel()
