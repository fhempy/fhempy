import asyncio
import logging

from fhempy.lib import fhem
from fhempy.lib.core.zeroconf import zeroconf as fzeroconf
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf


class discover_fhempy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.zeroconf: AsyncZeroconf = None
        self.browser = None
        self.hash = {"NAME": "discover_fhempy"}

    # zeroconf callback
    def update_service(self, zc, type, name):
        asyncio.create_task(self.foundDevice(zc, type, name))

    # zeroconf callback
    def remove_service(self, zc, type, name):
        self.logger.debug("Service %s removed" % (name))

    # zeroconf callback
    def add_service(self, zc, type, name):
        asyncio.create_task(self.foundDevice(zc, type, name))

    async def foundDevice(self, zc, type, name):
        self.logger.debug(f"Found service: {type} - {name}")
        try:
            info = await self.zeroconf.async_get_service_info(type, name)
        except Exception:
            self.logger.exception(f"async_get_service_info failed for {type} - {name}")
            return

        self.logger.debug("Service %s found, service info: %s" % (name, info))
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
                            f"fhempy_peer_{ipstr} BindingsIo {ip}:{port} fhempy",
                        )
            else:
                return

            # wait for the devices to initialize
            await asyncio.sleep(10)
        except Exception:
            self.logger.exception("Failed to handle foundDevice")

    async def runZeroconfScan(self):
        self.zeroconf = fzeroconf.get_instance(self.logger).get_async_zeroconf()
        listener = self
        services = [
            "_http._tcp.local.",
        ]
        self.browser = AsyncServiceBrowser(self.zeroconf.zeroconf, services, listener)

    async def activate(self):
        await self.runZeroconfScan()
        return ""

    async def deactivate(self):
        if self.browser:
            await self.browser.async_cancel()
            self.browser = None
