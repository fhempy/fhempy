import asyncio
import functools
import json
from tuya_iot.device import TuyaDevice
from fhempy.lib.generic import FhemModule
from fhempy.lib import fhem, fhem_pythonbinding, utils


class tuya_cloud_device:
    def __init__(self, logger, fhemdevice: FhemModule):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash

    async def Define(self, hash, args, argsh):
        self._t_setupdev = args[3]
        self._t_deviceid = args[4]
        self._t_devicelist = []
        self.hash["DEVICEID"] = self._t_deviceid

        self.tuyaiot = None
        await fhem.readingsSingleUpdate(self.hash, "state", "ready", 1)
        self.fhemdev.create_async_task(self._init_device())

    async def _init_device(self):
        try:
            await self._connect_to_setup_device()
            await self._setup_device()
        except Exception as ex:
            self.logger.exception(ex)

    async def _connect_to_setup_device(self):
        while self.tuyaiot is None or self.tuyaiot.ready is False:
            await asyncio.sleep(1)
            self.tuyaiot = fhem_pythonbinding.getFhemPyDeviceByName(self._t_setupdev)
            self.tuyaiot = self.tuyaiot.tuya_cloud_device

        self.tuyaiot.register_tuya_device(self)

    async def _setup_device(self):
        # retrieve functions/status/types
        self._t_specification = await utils.run_blocking(
            functools.partial(
                self.tuyaiot.device_manager.get_device_specification, self._t_deviceid
            )
        )
        if self._t_specification["success"]:
            self._t_specification = self._t_specification["result"]
        else:
            await fhem.readingsSingleUpdate(
                self.hash, "state", self._t_specification["msg"], 1
            )
            self._t_specification = {"functions": [], "status": []}
        # retrieve general infos
        self._t_info = await utils.run_blocking(
            functools.partial(
                self.tuyaiot.device_manager.get_device_info, self._t_deviceid
            )
        )
        self._t_info = self._t_info["result"]
        await self.update_readings_dict(self._t_info)
        # retrieve current status
        self._t_status = await utils.run_blocking(
            functools.partial(
                self.tuyaiot.device_manager.get_device_status, self._t_deviceid
            )
        )
        self._t_status = self._t_status["result"]

        # setup set commands
        await self._generate_set()

        # update status
        await self.update_readings_arr(self._t_status)

    async def _generate_set(self):
        set_conf = {}
        for fct in self._t_specification["functions"]:
            if fct["type"] == "Boolean":
                if fct["code"] == "switch_1" or fct["code"] == "switch":
                    set_conf["on"] = {
                        "function_param": fct,
                        "function": "set_boolean",
                    }
                    set_conf["off"] = {
                        "function_param": fct,
                        "function": "set_boolean",
                    }
                else:
                    set_conf[fct["code"]] = {
                        "options": "on,off",
                        "args": ["onoff"],
                        "function_param": fct,
                        "function": "set_boolean",
                    }
            elif fct["type"] == "Enum":
                options = json.loads(fct["values"])["range"]
                set_conf[fct["code"]] = {
                    "options": ",".join(options),
                    "args": ["selected_val"],
                    "function_param": fct,
                    "function": "set_enum",
                }
            elif fct["type"] == "Integer":
                spec = json.loads(fct["values"])
                slider = f"slider,{spec['min']},{spec['step']},{spec['max']}"
                set_conf[fct["code"]] = {
                    "options": slider,
                    "args": ["selected_val"],
                    "params": {"selected_val": {"format": "int"}},
                    "function_param": fct,
                    "function": "set_integer",
                }
            elif fct["type"] == "String":
                set_conf[fct["code"]] = {
                    "args": ["new_val"],
                    "function_param": fct,
                    "function": "set_string",
                }
            elif fct["type"] == "Json":
                pass
        self.fhemdev.set_set_config(set_conf)

    async def set_boolean(self, hash, params):
        code = params["function_param"]["code"]
        onoff = False
        if "onoff" in params:
            if params["onoff"] == "on":
                onoff = True
        else:
            if params["cmd"] == "on":
                onoff = True
        await self.send_commands([{"code": code, "value": onoff}])

    async def set_enum(self, hash, params):
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": params["selected_val"]}])

    async def set_string(self, hash, params):
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": params["new_val"]}])

    async def set_integer(self, hash, params):
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": params["selected_val"]}])

    async def send_commands(self, commands):
        await self.tuyaiot.send_commands(self._t_deviceid, commands)

    @property
    def id(self):
        return self._t_deviceid

    def _convert_code2fhem(self, code):
        if code == "switch_1" or code == "switch":
            return "state"
        return code

    def _convert_value2fhem(self, code, value):
        for code_def in self._t_specification["status"]:
            if code_def["code"] == code and code_def["type"] == "Integer":
                values = json.loads(code_def["values"])
                return value / (10 ** values["scale"])

        if code == "icon":
            return (
                self.tuyaiot.device_manager.api.endpoint.replace("openapi", "images")
                + "/"
                + value
            )
        if isinstance(value, bool):
            if value:
                return "on"
            return "off"
        return value

    async def update(self, device: TuyaDevice):
        await self.update_readings_dict(device.status)

    async def update_readings_arr(self, status_arr):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for status in status_arr:
                await fhem.readingsBulkUpdate(
                    self.hash,
                    self._convert_code2fhem(status["code"]),
                    self._convert_value2fhem(status["code"], status["value"]),
                )
        except Exception as ex:
            self.logger.exception(ex)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_readings_dict(self, status_dic):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for st_name in status_dic:
                await fhem.readingsBulkUpdate(
                    self.hash,
                    self._convert_code2fhem(st_name),
                    self._convert_value2fhem(st_name, status_dic[st_name]),
                )
        except Exception as ex:
            self.logger.exception(ex)
        await fhem.readingsEndUpdate(self.hash, 1)
