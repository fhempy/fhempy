import asyncio
import site
import socket
import subprocess

from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class esphome(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None
        self._set_list = {"start": {}, "stop": {}, "restart": {}}
        self.set_set_config(self._set_list)
        self._attr_list = {"disable": {"default": "0", "options": "0,1"}}
        self.set_attr_config(self._attr_list)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        if self._attr_disable == "1":
            return

        await self.start_process()

        if await fhem.AttrVal(self.hash["NAME"], "room", "") == "":
            await fhem.CommandAttr(self.hash, hash["NAME"] + " room ESPHome")
            self.create_async_task(self.create_weblink())

    async def start_process(self):
        self._esphomeargs = [
            site.getuserbase() + "/bin/esphome",
            "esphome_config/",
            "dashboard",
        ]

        try:
            self.proc = subprocess.Popen(self._esphomeargs)
        except Exception:
            try:
                self._esphomeargs = ["esphome", "esphome_config/", "dashboard"]
                self.proc = subprocess.Popen(self._esphomeargs)
            except Exception:
                return "Failed to execute esphome"

        await fhem.readingsSingleUpdate(self.hash, "state", "running", 1)

    async def stop_process(self):
        if self.proc:
            self.proc.terminate()
            self.proc = None
        await fhem.readingsSingleUpdate(self.hash, "state", "stopped", 1)

    async def create_weblink(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        await fhem.CommandDefine(
            self.hash, "esphome_dashboard weblink iframe http://" + local_ip + ":6052/"
        )
        await fhem.CommandAttr(
            self.hash,
            "esphome_dashboard htmlattr width='900' height='700' frameborder='0' marginheight='0' marginwidth='0'",
        )
        await fhem.CommandAttr(self.hash, "esphome_dashboard room ESPHome")

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self.proc:
            self.proc.terminate()
        return await super().Undefine(hash)

    async def set_attr_disable(self, hash):
        if self._attr_disable == "0":
            await self.start_process()
        else:
            await self.stop_process()

    async def set_start(self, hash, params):
        await self.stop_process()
        await self.start_process()
        return ""

    async def set_stop(self, hash, params):
        await self.stop_process()
        return ""

    async def set_restart(self, hash, params):
        return await self.set_start(hash, None)
