import asyncio
import site
import socket
import subprocess
import os

from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class esphome(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None
        self._set_list = {"start": {}, "stop": {}, "restart": {}}
        self.set_set_config(self._set_list)
        self._attr_list = {
            "disable": {"default": "0", "options": "0,1"},
            "port_dashboard": {"default": "6052", "format": "int"},
        }
        self.set_attr_config(self._attr_list)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        if self._attr_disable == "1":
            return

        await self.start_process()

        if await fhem.init_done(hash) == 1:
            # create weblinks on first define
            self.create_async_task(self.create_weblink())

    async def start_process(self):
        my_env = os.environ
        my_env["PATH"] = site.getuserbase() + "/bin:" + my_env["PATH"]
        self._esphomeargs = [
            site.getuserbase() + "/bin/esphome",
            "dashboard",
            "esphome_config/",
            "--port",
            self._attr_port_dashboard,
        ]

        try:
            self.proc = subprocess.Popen(self._esphomeargs, env=my_env)
        except Exception:
            try:
                self._esphomeargs = [
                    "esphome",
                    "dashboard",
                    "esphome_config/",
                    "--port",
                    self._attr_port_dashboard,
                ]
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
            "esphome_dashboard htmlattr width='900' height='700' frameborder='0' marginheight='0' marginwidth='0'",
        )
        await fhem.CommandAttr(self.hash, "esphome_dashboard room ESPHome")
        await fhem.CommandAttr(self.hash, "esphome_dashboard sortby 2")

        await fhem.CommandDefine(
            self.hash,
            """
esphome_installer weblink htmlCode <style>a[target='_blank']::after {
content: '';
width: 1em;
height: 1em;
margin: 0 0.05em 0 0.1em;
background: url(data:image/svg+xml;base64,
PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb
3g9IjAgMCAxNiAxNiIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij48cGF0aCBkPS
JNOSAyTDkgMyAxMi4zIDMgNiA5LjMgNi43IDEwIDEzIDMuNyAxMyA3IDE0IDc
gMTQgMlpNNCA0QzIuOSA0IDIgNC45IDIgNkwyIDEyQzIgMTMuMSAyLjkgMTQg
NCAxNEwxMCAxNEMxMS4xIDE0IDEyIDEzLjEgMTIgMTJMMTIgNyAxMSA4IDExI
DEyQzExIDEyLjYgMTAuNiAxMyAxMCAxM0w0IDEzQzMuNCAxMyAzIDEyLjYgMy
AxMkwzIDZDMyA1LjQgMy40IDUgNCA1TDggNSA5IDRaIi8+PC9zdmc+) no-repeat;
background-size: contain;
display: inline-block;
vertical-align: text-bottom;
}</style>
<a href='https://esphome.github.io/esp-web-tools/'
 style='font-size: 20px;' target='_blank'>
Click here to easily install ESPHome on a new devices
</a><br><br>""".replace(
                "\n", ""
            ),
        )
        await fhem.CommandAttr(self.hash, "esphome_installer room ESPHome")
        await fhem.CommandAttr(self.hash, "esphome_installer sortby 1")

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
