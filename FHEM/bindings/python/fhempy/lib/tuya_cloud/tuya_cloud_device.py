import asyncio
import functools
import json
import colorsys

import fhempy.lib.fhem as fhem
import fhempy.lib.utils as utils
import fhempy.lib.fhem_pythonbinding as fpb


class tuya_cloud_device:
    def __init__(self, logger, fhemdevice):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash

    async def Define(self, hash, args, argsh):
        self._t_setupdev = args[3]
        self._t_deviceid = args[4]
        self._t_devicelist = []
        self.hash["DEVICEID"] = self._t_deviceid

        self.tuyaiot = None
        self.default_code = None
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
            self.tuyaiot = fpb.getFhemPyDeviceByName(self._t_setupdev)
            if self.tuyaiot is not None:
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
                set_conf[fct["code"]] = {
                    "args": ["new_val"],
                    "function_param": fct,
                    "function": "set_json",
                }
                if fct["code"] == "colour_data":
                    set_conf[fct["code"]]["function"] = "set_colour_data"
                    set_conf[fct["code"]]["options"] = "colorpicker,RGB"
                elif fct["code"] == "colour_data_v2":
                    set_conf[fct["code"]]["function"] = "set_colour_data_v2"
                    set_conf[fct["code"]]["options"] = "colorpicker,RGB"

        set_conf = self.prepare_onoff_usage(set_conf)
        self.fhemdev.set_set_config(set_conf)

    def prepare_onoff_usage(self, set_conf):
        self.default_code = None
        if "switch" in set_conf:
            self.default_code = "switch"
        elif "switch_1" in set_conf:
            self.default_code = "switch_1"
        elif "switch_led" in set_conf:
            self.default_code = "switch_led"

        if self.default_code is not None:
            set_conf["on"] = {
                "function_param": {"code": self.default_code},
                "function": "set_boolean",
            }
            set_conf["off"] = {
                "function_param": {"code": self.default_code},
                "function": "set_boolean",
            }
            del set_conf[self.default_code]
        return set_conf

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

    async def set_json(self, hash, params):
        code = params["function_param"]["code"]
        await self.send_commands(
            [{"code": code, "value": json.loads(params["new_val"])}]
        )

    async def set_integer(self, hash, params):
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": params["selected_val"]}])

    async def set_colour_data(self, hash, params):
        # convert e.g. ff0000 to hsv (360, 255, 255) and set hsv values with json
        hsv = self.fhemrgb2hsv(params["new_val"])
        if self._t_info["category"] == "dj":
            hsv["s"] = int(hsv["s"] / 1000 * 255)
            hsv["v"] = int(hsv["v"] / 1000 * 255)
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": hsv}])

    async def set_colour_data_v2(self, hash, params):
        # convert e.g. ff0000 to hsv (360, 1000, 1000) and set hsv values with json
        hsv = self.fhemrgb2hsv(params["new_val"])
        code = params["function_param"]["code"]
        await self.send_commands([{"code": code, "value": hsv}])

    def fhemrgb2hsv(self, rgb):
        red = int(rgb[0:2], base=16)
        green = int(rgb[2:4], base=16)
        blue = int(rgb[4:6], base=16)
        hsv = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        return {
            "h": int(hsv[0] * 360),
            "s": int(hsv[1] * 1000),
            "v": int(hsv[2] * 1000),
        }

    async def send_commands(self, commands):
        await self.tuyaiot.send_commands(self._t_deviceid, commands)

    @property
    def id(self):
        return self._t_deviceid

    def _convert_code2fhem(self, code):
        if code == self.default_code:
            return "state"

        # pir device
        if code == "pir" and self._t_info["category"] == "pir":
            return "state"

        # smoke detector
        if code == "smoke_sensor_status":
            return "state"

        # water detector
        if code == "watersensor_state":
            return "state"

        # door window sensor
        if code == "doorcontact_state":
            return "state"

        return code

    def _convert_value2fhem(self, code, value):
        for code_def in self._t_specification["status"]:
            if code_def["code"] == code and code_def["type"] == "Integer":
                values = json.loads(code_def["values"])
                return value / (10 ** int(values["scale"]))

        if code == "icon":
            return (
                self.tuyaiot.device_manager.api.endpoint.replace("openapi", "images")
                + "/"
                + value
            )
        # pir device
        elif code == "pir" and self._t_info["category"] == "pir":
            if value == "pir":
                self.fhemdev.create_async_task(
                    self.reset_reading("state", "nomotion", 180)
                )
                return "motion"
        # door window sensor
        elif code == "doorcontact_state":
            if value is True:
                return "open"
            return "closed"

        if isinstance(value, bool):
            if value:
                return "on"
            return "off"
        return value

    async def reset_reading(self, reading, resetvalue, timeout):
        await asyncio.sleep(timeout)
        await fhem.readingsSingleUpdate(self.fhemdev.hash, reading, resetvalue, 1)

    async def update(self, device):
        await self.update_readings_dict(device.status)

    async def update_readings_arr(self, status_arr):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for status in status_arr:
                if status["code"] in ["colour_data", "colour_data_v2"]:
                    await self.update_readings_hsv(
                        status["code"], json.loads(status["value"])
                    )
                else:
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
                if st_name in ["colour_data", "colour_data_v2"]:
                    await self.update_readings_hsv(
                        st_name, json.loads(status_dic[st_name])
                    )
                else:
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        self._convert_code2fhem(st_name),
                        self._convert_value2fhem(st_name, status_dic[st_name]),
                    )
        except Exception as ex:
            self.logger.exception(ex)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_readings_hsv(self, hsv_code, hsv_json):
        if hsv_code == "colour_data" and self._t_info["category"] == "dj":
            # only category dj (light) has old colour_data
            rgb = colorsys.hsv_to_rgb(
                int(hsv_json["h"]) / 360,
                int(hsv_json["s"]) / 255,
                int(hsv_json["v"]) / 255,
            )
        else:
            rgb = colorsys.hsv_to_rgb(
                int(hsv_json["h"]) / 360,
                int(hsv_json["s"]) / 1000,
                int(hsv_json["v"]) / 1000,
            )

        red = int(rgb[0] * 255)
        green = int(rgb[1] * 255)
        blue = int(rgb[2] * 255)
        rgb_hex = f"{red:02x}{green:02x}{blue:02x}"
        await fhem.readingsBulkUpdate(
            self.hash,
            hsv_code,
            rgb_hex,
        )
