import asyncio
import traceback

from fhempy.lib.generic import FhemModule
from zeroconf.asyncio import AsyncServiceBrowser

from .. import fhem
from ..core.zeroconf import zeroconf


class discover_mdns(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.loop = asyncio.get_event_loop()
        self.zeroconf = None
        self.hash = None
        self.browser = None

    # zeroconf callback
    def update_service(self, zeroconf, type, name):
        self.logger.debug("Service %s updated" % (name))
        res = asyncio.run_coroutine_threadsafe(self.foundDevice(type, name), self.loop)
        res.result()

    # zeroconf callback
    def remove_service(self, zeroconf, type, name):
        self.logger.debug("Service %s removed" % (name))

    # zeroconf callback
    def add_service(self, zeroconf, type, name):
        self.logger.debug("Service %s added" % (name))
        res = asyncio.run_coroutine_threadsafe(self.foundDevice(type, name), self.loop)
        res.result()

    async def foundDevice(self, type, name):
        try:
            info = await self.zeroconf.async_get_service_info(type, name)

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
            elif info.type == "_spotify-connect":
                if not (
                    await fhem.checkIfDeviceExists(
                        self.hash, "PYTHONTYPE", "spotify", "PYTHONTYPE", "spotify"
                    )
                ):
                    self.logger.debug("create spotify")
                    await fhem.CommandDefine(
                        self.hash, "spotify_connect PythonModule spotify"
                    )
                else:
                    self.logger.debug("device spotify exists already, do not create")
            else:
                return

            # wait for the devices to initialize
            await asyncio.sleep(10)
        except Exception:
            self.logger.error(traceback.print_exc())

    async def runZeroconfScan(self):
        # await here to finish define before zeroconf object is created
        await asyncio.sleep(1)
        self.zeroconf = zeroconf.get_instance(self.logger).get_async_zeroconf()
        listener = self
        services = [
            "_googlecast._tcp.local.",
            "_soundtouch._tcp.local.",
            "_http._tcp.local.",
            "_spotify-connect",
        ]
        self.browser = AsyncServiceBrowser(self.zeroconf.zeroconf, services, listener)

    # FHEM
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        await fhem.readingsSingleUpdate(self.hash, "state", "active", 1)
        self.create_async_task(self.runZeroconfScan())

        if await fhem.AttrVal(self.hash["NAME"], "icon", "") == "":
            await fhem.CommandAttr(self.hash, self.hash["NAME"] + " icon rc_SEARCH")

    # FHEM
    async def Undefine(self, hash):
        if self.browser:
            self.browser.cancel()
        await super().Undefine(hash)
