import os
import site
import socket

from fhempy.lib.generic import FhemModule

from .. import fhem
from ..core import child_process


class esphome(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self._set_list = {"start": {}, "stop": {}, "restart": {}}
        await self.set_set_config(self._set_list)
        self._attr_list = {
            "disable": {"default": "0", "options": "0,1"},
            "port_dashboard": {"default": "6052", "help": "Default port ist 6052"},
        }
        await self.set_attr_config(self._attr_list)

        if self._attr_disable == "1":
            return

        await self.start_process()

        if await fhem.init_done(hash) == 1:
            # create weblinks on first define
            self.create_async_task(self.create_weblink())

    async def start_process(self):
        self._esphomeargs = [
            "esphome",
            "dashboard",
            "esphome_config/",
            "--port",
            self._attr_port_dashboard,
        ]

        try:
            self.proc = child_process.start(self._esphomeargs)
        except Exception:
            self.logger.exception("Failed to execute esphome, trying with env")

            try:
                my_env = os.environ.copy()
                my_env["PATH"] = site.getuserbase() + "/bin:" + my_env["PATH"]
                self._esphomeargs = [
                    site.getuserbase() + "/bin/esphome",
                    "dashboard",
                    "esphome_config/",
                    "--port",
                    self._attr_port_dashboard,
                ]

                self.proc = child_process.start(self._esphomeargs, env=my_env)
            except Exception:
                self.logger.exception("Failed to execute esphome, trying with site")

                return "Failed to execute esphome"

        await fhem.readingsSingleUpdate(self.hash, "state", "running", 1)

    async def stop_process(self):
        if self.proc is None:
            return
        # stop the process before talking to FHEM, FHEM might not answer
        # anymore during fhempy update or shutdown
        if await child_process.stop(self.proc):
            self.proc = None
            await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)
        else:
            self.logger.error("Failed to stop esphome process")
            await fhem.readingsSingleUpdate(self.hash, "state", "failed to stop", 1)

    async def create_weblink(self):
        if await fhem.checkIfDeviceExists(
            self.hash, "TYPE", "weblink", "NAME", "esphome_dashboard"
        ):
            return

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        await fhem.CommandDefine(
            self.hash, "esphome_dashboard weblink iframe http://" + local_ip + ":6052/"
        )
        await fhem.CommandAttr(
            self.hash,
            (
                "esphome_dashboard htmlattr width='900' height='700' "
                "frameborder='0' marginheight='0' marginwidth='0'"
            ),
        )
        await fhem.CommandAttr(self.hash, "esphome_dashboard room ESPHome")

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await self.stop_process()
        return await super().Undefine(hash)

    async def set_attr_disable(self, hash):
        if self._attr_disable == "0":
            await self.start_process()
        else:
            await self.stop_process()

    async def set_start(self, hash, params):
        self.create_async_task(self._restart())

    async def set_stop(self, hash, params):
        self.create_async_task(self.stop_process())

    async def _restart(self):
        await self.stop_process()
        await self.start_process()

    async def set_restart(self, hash, params):
        self.create_async_task(self._restart())
