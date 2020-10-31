
import asyncio
import functools
from miio.click_common import DeviceGroupMeta

from .. import fhem,utils
import inspect
import enum
import typing
import json

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
            fct = getattr(self._miio_device_class, dev_cmd)
            sig = inspect.signature(fct)
            if len(list(sig.parameters)) > 1:
                self._set_list[dev_cmd]["args"] = []
                for par in sig.parameters:
                    if sig.parameters[par].name == "self":
                        continue
                    self._set_list[dev_cmd]["args"].append(sig.parameters[par].name)
                    if len(list(sig.parameters)) == 2:
                        # set options if there is only one parameter
                        annot = sig.parameters[par].annotation
                        if not inspect.isclass(annot):
                            self.logger.error("Annotation is not class: " + str(annot))
                        if inspect.isclass(annot) and issubclass(annot, enum.Enum):
                            self._set_list[dev_cmd]["options"] = ",".join(list(map(lambda x:x.name, annot)))
                        elif inspect.isclass(annot) and issubclass(annot, bool):
                            self._set_list[dev_cmd]["options"] = "on,off"

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
            asyncio.create_task(self.send_command(fct_cmd, params))
    
    def is_number(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    async def send_command(self, fct, params):
        sig = inspect.signature(fct)
        args = []
        for par_name in sig.parameters:
            ann = sig.parameters[par_name].annotation
            if inspect.isclass(ann) and issubclass(ann, enum.Enum):
                args.append(ann[params[par_name]])
            elif inspect.isclass(ann) and issubclass(ann, bool):
                args.append(params[par_name] == "on")
            elif ann == typing.List:
                args.append(json.loads(params[par_name]))
            elif ann == inspect.Signature.empty:
                if self.is_number(params[par_name]):
                    args.append(float(params[par_name]))
                else:
                    args.append(params[par_name])
            else:
                args.append(ann(params[par_name]))
        # call function with arguments
        reply = await utils.run_blocking(functools.partial(fct, *args))
        # handle reply
        if hasattr(reply, "__dict__"):
            await fhem.readingsBeginUpdate(self.hash)
            try:
                st = dict((x, getattr(reply, x)) for x in reply.__class__.__dict__ if isinstance(reply.__class__.__dict__[x], property))
                for prop in st:
                    await fhem.readingsBulkUpdateIfChanged(self.hash, prop, st[prop])
            except:
                await fhem.readingsBulkUpdateIfChanged(self.hash, fct.__name__, reply)
            await fhem.readingsEndUpdate(self.hash, 1)
        else:
            if reply != "['ok']":
                await fhem.readingsSingleUpdateIfChanged(self.hash, fct.__name__, reply, 1)
        await self.set_command(self.hash, { "cmd": "status" })

    async def status_request(self, fct):
        reply = await utils.run_blocking(functools.partial(fct))
        await fhem.readingsBeginUpdate(self.hash)
        try:
            st = dict((x, getattr(reply, x)) for x in reply.__class__.__dict__ if isinstance(reply.__class__.__dict__[x], property))
            for prop in st:
                await fhem.readingsBulkUpdateIfChanged(self.hash, prop, st[prop])
        except:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "cmd_reply_val", reply)
        await fhem.readingsEndUpdate(self.hash, 1)