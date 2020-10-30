
import asyncio
import functools
from miio.click_common import DeviceGroupMeta

from .. import fhem,utils

class miio:

    def __init__(self, logger):
        self.logger = logger
        self._set_list = {}
        self._device = None
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._miio_devtype = args[3]
        self._miio_ip = args[4]
        self._miio_token = args[5]

        for device_class in DeviceGroupMeta.device_classes:
            if device_class.get_device_group().name == self._miio_devtype:
                self._miio_device_class = device_class
                break
        for dev_cmd in self._miio_device_class.get_device_group().commands.keys():
            self._set_list[dev_cmd] = { "function": "set_command" }
            if len(getattr(self._miio_device_class, dev_cmd).__code__.co_varnames[1:]) > 0:
                self._set_list[dev_cmd]["args"] = ["param"]
        self._device = self._miio_device_class(ip=self._miio_ip, token=self._miio_token)
        await fhem.readingsSingleUpdateIfChanged(hash, "state", "active", 1)
        asyncio.create_task(self.status_request_loop())

    async def status_request_loop(self):
        while True:
            await self.set_command(self.hash, {"cmd": "status"})
            await asyncio.sleep(300)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return await utils.handle_set(self._set_list, self, hash, args, argsh)

    async def set_command(self, hash, params):
        cmd = params['cmd']
        fct_cmd = getattr(self._device, cmd)
        if cmd == "status":
            asyncio.create_task(self.status_request(fct_cmd))
        else:
            asyncio.create_task(self.send_command(fct_cmd))

    async def send_command(self, fct):
        reply = await utils.run_blocking(functools.partial(fct))
        await fhem.readingsSingleUpdateIfChanged(self.hash, "cmd_reply", reply, 1)
        await self.set_command(self.hash, { "cmd": "status" })

    async def status_request(self, fct):
        status = await utils.run_blocking(functools.partial(fct))
        await fhem.readingsBeginUpdate(self.hash)
        st = vars(status)['data']
        for prop in st:
            await fhem.readingsBulkUpdateIfChanged(self.hash, prop, st[prop])
        await fhem.readingsEndUpdate(self.hash, 1)