import asyncio
import colorsys
import functools
import json
import time
from random import randrange

import fhempy.lib.fhem as fhem
import fhempy.lib.fhem_pythonbinding as fpb
import fhempy.lib.utils as utils


class tuya_smartlife_device:
    def __init__(self, logger, fhemdevice):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash
        self.readings_update_lock = asyncio.Lock()
        self.last_status = None

    async def Define(self, hash, args, argsh):
        self._t_setupdev = args[3]
        self._t_deviceid = args[4]
        self._t_devicelist = []
        self.hash["DEVICEID"] = self._t_deviceid

        self.tuyaiot = None
        self.default_code = None

        # read current energy just on define
        self.energy = float(await fhem.ReadingsVal(self.hash["NAME"], "energy", "0"))
        self.last_energy_ts = None
        self.last_energy_value = 0

        await fhem.readingsSingleUpdate(self.hash, "state", "ready", 1)
        self.fhemdev.create_async_task(self._init_device())

    async def Undefine(self, hash):
        if self.tuyaiot:
            self.tuyaiot.unregister_tuya_device(self)

    async def _init_device(self):
        try:
            await self._connect_to_setup_device()
            await self._setup_device()
        except Exception as ex:
            self.logger.exception(ex)

    async def _connect_to_setup_device(self):
        while self.tuyaiot is None or self.tuyaiot.ready is False:
            self.tuyaiot = fpb.getFhemPyDeviceByName(self._t_setupdev)
            if self.tuyaiot is not None:
                self.tuyaiot = self.tuyaiot.setup_device

            await asyncio.sleep(randrange(20))

        self.tuyaiot.register_tuya_device(self)
        self.device = self.tuyaiot.device_manager.device_map[self._t_deviceid]
        self.device.set_up = True

    async def _setup_device(self):
        # retrieve functions/status/types
        self._t_specification = self.device.function

        # retrieve general infos
        self._t_info = self.device
        # update static device readings
        # TODO await self.update_readings_dict(self._t_info)

        # retrieve current status
        self._t_status = self.device.status

        # setup set commands
        await self._generate_set()

        # update status
        await self.update_readings_arr(self._t_status)

    async def _generate_set(self):
        set_conf = {}
        for fct in self._t_specification:
            if self._t_specification[fct].type == "Boolean":
                set_conf[self._t_specification[fct].code] = {
                    "options": "on,off",
                    "args": ["onoff"],
                    "function_param": self._t_specification[fct],
                    "function": "set_boolean",
                }
            elif self._t_specification[fct].type == "Enum":
                options = json.loads(self._t_specification[fct].values)["range"]
                set_conf[self._t_specification[fct].code] = {
                    "options": ",".join(options),
                    "args": ["selected_val"],
                    "function_param": self._t_specification[fct],
                    "function": "set_enum",
                }
            elif self._t_specification[fct].type == "Integer":
                spec = json.loads(self._t_specification[fct].values)
                slider = f"slider,{spec['min']},{spec['step']},{spec['max']}"
                set_conf[self._t_specification[fct].code] = {
                    "options": slider,
                    "args": ["selected_val"],
                    "params": {"selected_val": {"format": "int"}},
                    "function_param": self._t_specification[fct],
                    "function": "set_integer",
                }
            elif self._t_specification[fct].type == "String":
                set_conf[self._t_specification[fct].code] = {
                    "args": ["new_val"],
                    "function_param": self._t_specification[fct],
                    "function": "set_string",
                }
            elif self._t_specification[fct].type == "Json":
                set_conf[self._t_specification[fct].code] = {
                    "args": ["new_val"],
                    "function_param": self._t_specification[fct],
                    "function": "set_json",
                }
                if self._t_specification[fct].code == "colour_data":
                    set_conf[self._t_specification[fct].code][
                        "function"
                    ] = "set_colour_data"
                    set_conf[self._t_specification[fct].code][
                        "options"
                    ] = "colorpicker,RGB"
                elif self._t_specification[fct].code == "colour_data_v2":
                    set_conf[self._t_specification[fct].code][
                        "function"
                    ] = "set_colour_data_v2"
                    set_conf[self._t_specification[fct].code][
                        "options"
                    ] = "colorpicker,RGB"

        set_conf = self.prepare_onoff_usage(set_conf)

        for st in self.device.status:
            if st == "cur_power":
                set_conf["reset_energy"] = {}
                break

        await self.fhemdev.set_set_config(set_conf)

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

    async def set_reset_energy(self, hash, params):
        self.last_energy_ts = time.time()
        self.last_energy_value = 0
        await fhem.readingsSingleUpdateIfChanged(self.hash, "energy", 0, 1)

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
        code = params["function_param"].code
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
        # pir device
        if code == "pir" and self.device.category == "pir":
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
        async with self.readings_update_lock:
            await fhem.readingsBeginUpdate(self.hash)
            try:
                # iterature through key, value pairs
                for status, val in status_arr.items():
                    if status in ["colour_data", "colour_data_v2"]:
                        await self.update_readings_hsv(status, json.loads(val))
                    else:
                        await fhem.readingsBulkUpdate(
                            self.hash,
                            self._convert_code2fhem(status),
                            self._convert_value2fhem(status, val),
                        )
            except Exception:
                self.logger.exception(
                    f"Exception in handling status values from tuya: {status_arr}"
                )
            await fhem.readingsEndUpdate(self.hash, 1)

    async def update_readings_dict(self, status_dic):
        async with self.readings_update_lock:
            # check if last_status dictionary equals status_dic dictionary
            if self.last_status != status_dic:
                self.last_status = status_dic.copy()
            else:
                return

            await fhem.readingsBeginUpdate(self.hash)
            try:
                for st_name in status_dic:
                    if st_name in ["colour_data", "colour_data_v2"]:
                        await self.update_readings_hsv(
                            st_name, json.loads(status_dic[st_name])
                        )
                    else:
                        if st_name == "cur_power" and status_dic[st_name] > 0:
                            cur_power = self._convert_value2fhem(
                                st_name, status_dic[st_name]
                            )

                            if self.last_energy_ts is not None:
                                # last value available
                                cur_energy = (
                                    (time.time() - self.last_energy_ts)
                                    * (self.last_energy_value + cur_power)
                                    / 2
                                ) / (3600 * 1000)
                                self.energy += cur_energy

                            self.last_energy_ts = time.time()
                            self.last_energy_value = cur_power
                            await fhem.readingsBulkUpdateIfChanged(
                                self.hash,
                                "energy",
                                round(self.energy, 3),
                            )
                        await fhem.readingsBulkUpdate(
                            self.hash,
                            self._convert_code2fhem(st_name),
                            self._convert_value2fhem(st_name, status_dic[st_name]),
                        )
            except Exception as ex:
                self.logger.exception(ex)
            await fhem.readingsEndUpdate(self.hash, 1)

    async def update_readings_hsv(self, hsv_code, hsv_json):
        if hsv_code == "colour_data" and self.device.category == "dj":
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
