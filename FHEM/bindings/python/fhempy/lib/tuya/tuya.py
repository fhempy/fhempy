import ast
import asyncio
import functools
import importlib
import json
import re

from .. import fhem, generic, utils
from . import mappings


class tuya(generic.FhemModule):
    def __init__(self, logger):
        # import needs to be here, otherwise we are in a thread without
        # event loop which is required in tinytuya
        self.tt = importlib.import_module("tinytuya")
        self.tt.loop = asyncio.get_event_loop()
        super().__init__(logger)
        self._connected_device = None
        self.tuya_cloud = None
        self.tt_key = ""
        self.tt_secret = ""
        self.last_status = None
        self.create_device_list = []
        self.update_lock = asyncio.Lock()
        self.master_switch = ""
        self.update_dps_loop_task = None
        self.status_quick_loop_task = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 7:
            return (
                "Usage: define wifi_plug fhempy tuya"
                " setup <API_KEY> <API_SECRET> <DEVICE_ID> [<REGION>=eu]<br>"
                "OR if you want to define only one device with existing local key<br>"
                " <PRODUCTID> <DEVICE_ID> <IP> <LOCAL_KEY> "
                "[<VERSION>=3.3] [<API_KEY>] [<API_SECRET>]"
            )

        self.tt_type = args[3]
        if self.tt_type == "setup":
            self.tt_key = args[4]
            self.tt_secret = args[5]
            self.tt_did = args[6]
            if len(args) == 8:
                self.tt_region = args[7]
            else:
                self.tt_region = "eu"
            self.set_set_config({"scan_devices": {}})
            await fhem.readingsSingleUpdate(self.hash, "state", "ready", 1)
            # set internal
            hash["DEVICEID"] = 0
            hash["API_KEY"] = self.tt_key
            hash["API_SECRET"] = self.tt_secret
            hash["REGION"] = self.tt_region
            self.create_async_task(self.setup_cloud())
            return

        await fhem.readingsSingleUpdateIfChanged(self.hash, "online", "0", 1)
        self.tt_productid = self.tt_type
        self.tt_region = "eu"
        self.tt_did = args[4]
        self.tt_ip = args[5]
        self.tt_localkey = args[6]
        if len(args) >= 8:
            self.tt_version = float(args[7])
        else:
            self.tt_version = 3.3
        if len(args) == 10:
            self.tt_key = args[8]
            self.tt_secret = args[9]

        if self.tt_ip == "offline":
            await fhem.readingsSingleUpdate(
                self.hash, "state", "Change DEF and use IP instead of 'offline'", 1
            )
            return

        # set internal
        hash["DEVICEID"] = self.tt_did
        # set attributes
        self.attr_config = {
            "tuya_spec_functions": {"default": ""},
            "tuya_spec_status": {"default": ""},
        }
        self.set_attr_config(self.attr_config)
        # this is needed to set default values
        await utils.handle_define_attr(self.attr_config, self, hash)

        await self.setup_cloud()

        # create device
        self.create_async_task(self.create_device())

    async def setup_cloud(self):
        # create cloud device for cloud calls
        if self.tt_key and self.tt_secret:
            self.tuya_cloud = await utils.run_blocking(
                functools.partial(
                    self.tt.Cloud,
                    self.tt_region,
                    self.tt_key,
                    self.tt_secret,
                    self.tt_did,
                )
            )

    async def _create_mapping_dev(self):
        self.tuya_spec_functions = []
        self.tuya_spec_status = []
        schema = mappings.knownSchemas[self.tt_type]["schema"]
        for schema_part in schema:
            # rename to values
            schema_part["values"] = schema_part["property"]
            schema_part["type"] = schema_part["values"]["type"]
            schema_part["dp_id"] = schema_part["id"]
            schema_part["desc"] = ""
            if schema_part["type"] == "bool":
                schema_part["type"] = "Boolean"
            elif schema_part["type"] == "value":
                schema_part["type"] = "Integer"
            elif schema_part["type"] == "enum":
                schema_part["type"] = "Enum"
            elif schema_part["type"] == "string":
                schema_part["type"] = "String"
            else:
                continue
            self.tuya_spec_status.append(schema_part)
            if schema_part["mode"] == "rw":
                self.tuya_spec_functions.append(schema_part)

        await self._generate_set()

        await self.setup_connection()
        status = await self._connected_device.detect_available_dps()
        await self.update_readings(status, set_ready=True)

    async def set_attr_dp(self, hash):
        # check defined dp_Xs and their value
        # set set_conf based on the set dp_Xs
        dp_conf = {}
        for attr_name in self.__dict__:
            if attr_name.find("_attr_dp_") != -1:
                dp_id = re.search(r"\d+$", attr_name)[0]
                dp_conf[dp_id] = self.__dict__[attr_name]
                for fct in self.tuya_spec_functions:
                    if fct["code"] == dp_conf[dp_id]:
                        fct["id"] = int(dp_id)
                for status in self.tuya_spec_status:
                    if status["code"] == dp_conf[dp_id]:
                        status["id"] = int(dp_id)

        await self._generate_set()

    async def _generate_set(self):
        set_conf = {}

        # identify master switch
        for fct in self.tuya_spec_functions:
            if fct["code"] == "switch_1":
                self.master_switch = fct["code"]
            elif fct["code"] == "switch_led" and self.master_switch == "":
                self.master_switch = fct["code"]
            elif fct["code"][0:6] == "switch" and self.master_switch == "":
                self.master_switch = fct["code"]

        for fct in self.tuya_spec_functions:
            if "id" not in fct:
                # no id configured for this function
                continue
            if fct["type"] == "Boolean":
                if fct["code"] == self.master_switch:
                    set_conf["on"] = {
                        "help": fct["desc"],
                        "function_param": fct,
                        "function": "set_boolean",
                    }
                    set_conf["off"] = {
                        "help": fct["desc"],
                        "function_param": fct,
                        "function": "set_boolean",
                    }
                else:
                    set_conf[fct["code"]] = {
                        "options": "on,off",
                        "args": ["onoff"],
                        "help": fct["desc"],
                        "function_param": fct,
                        "function": "set_boolean",
                    }
            elif fct["type"] == "Enum":
                values = fct["values"]
                if "translation" in values:
                    options = list(values["translation"].values())
                else:
                    options = values["range"]
                set_conf[fct["code"]] = {
                    "options": ",".join(options),
                    "args": ["new_val"],
                    "help": fct["desc"],
                    "function_param": fct,
                    "function": "set_other_types",
                }
            elif fct["type"] == "Integer":
                spec = fct["values"]
                step = spec["step"] / (10 ** spec["scale"])
                if self.tt_productid == "IAYz2WK1th0cMLmL":
                    min = spec["min"] / 2
                    max = spec["max"] / 2
                else:
                    min = spec["min"] / (10 ** spec["scale"])
                    max = spec["max"] / (10 ** spec["scale"])
                slider = f"slider,{min},{step},{max}"
                set_conf[fct["code"]] = {
                    "options": slider,
                    "args": ["new_val"],
                    "params": {"new_val": {"format": "int"}},
                    "help": fct["desc"],
                    "function_param": fct,
                    "function": "set_integer",
                }
            elif fct["type"] == "String":
                set_conf[fct["code"]] = {
                    "args": ["new_val"],
                    "help": fct["desc"],
                    "function_param": fct,
                    "function": "set_other_types",
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

        self.set_set_config(set_conf)

    async def set_create_device(self, hash, params):
        nameid = params["name"]
        for dev in self.create_device_list:
            if nameid == dev["name_esc"] + "_" + dev["device_id"]:
                await fhem.CommandDefine(
                    self.hash,
                    (
                        f"tuya_local_{dev['device_id']} fhempy tuya "
                        f"{dev['productid']} {dev['device_id']} {dev['ip']} "
                        f"{dev['local_key']} {dev['version']} "
                        f"{self.tt_key} {self.tt_secret}"
                    ),
                )
                await fhem.CommandAttr(
                    self.hash, f"tuya_local_{dev['device_id']} alias {dev['name']}"
                )

    async def set_boolean(self, hash, params):
        switch_id = params["function_param"]["id"]
        onoff = False
        if "onoff" in params:
            if params["onoff"] == "on":
                onoff = True
        else:
            if params["cmd"] == "on":
                onoff = True
        if self._connected_device:
            await self._connected_device.set_dp(onoff, switch_id)

    async def set_integer(self, hash, params):
        index = params["function_param"]["id"]
        if "translation" in params["function_param"]["values"]:
            for val in params["function_param"]["values"]["translation"].keys():
                if (
                    params["function_param"]["values"]["translation"][val]
                    == params["new_val"]
                ):
                    new_val = val
        else:
            if self.tt_productid == "IAYz2WK1th0cMLmL":
                if params["function_param"]["code"] == "temp_set":
                    params["new_val"] *= 0.2
            new_val = int(
                params["new_val"] * (10 ** params["function_param"]["values"]["scale"])
            )
        if self._connected_device:
            await self._connected_device.set_dp(new_val, index)

    async def set_other_types(self, hash, params):
        index = params["function_param"]["id"]
        if "translation" in params["function_param"]["values"]:
            for val in params["function_param"]["values"]["translation"].keys():
                if (
                    params["function_param"]["values"]["translation"][val]
                    == params["new_val"]
                ):
                    params["new_val"] = val
        new_val = params["new_val"]
        if self._connected_device:
            await self._connected_device.set_dp(new_val, index)

    async def set_colour_data(self, hash, params):
        index = params["function_param"]["id"]
        rgb = self.fhemrgb2rgb(params["new_val"])
        if "category" in self.info_dict and self.info_dict["category"] == "dj":
            hexvalue = self.tt.BulbDevice._rgb_to_hexvalue(
                rgb["r"], rgb["g"], rgb["b"], "A"
            )
        else:
            hexvalue = self.tt.BulbDevice._rgb_to_hexvalue(
                rgb["r"], rgb["g"], rgb["b"], "B"
            )
        await self.change_to_colour_mode()
        await self._connected_device.set_dp(hexvalue, index)

    async def set_colour_data_v2(self, hash, params):
        index = params["function_param"]["id"]
        rgb = self.fhemrgb2rgb(params["new_val"])
        hexvalue = self.tt.BulbDevice._rgb_to_hexvalue(
            rgb["r"], rgb["g"], rgb["b"], "B"
        )
        await self.change_to_colour_mode()
        await self._connected_device.set_dp(hexvalue, index)

    async def change_to_colour_mode(self):
        if "work_mode" in self._conf_set:
            await self._connected_device.set_dp(
                "colour", self._conf_set["work_mode"]["function_param"]["id"]
            )

    def fhemrgb2rgb(self, rgb):
        red = int(rgb[0:2], base=16)
        green = int(rgb[2:4], base=16)
        blue = int(rgb[4:6], base=16)
        return {
            "r": red,
            "g": green,
            "b": blue,
        }

    # check if tuya_spec_functions and tuya_spec_status attr is set?
    async def check_tuya_attributes(self):
        self.tuya_spec_functions = await fhem.AttrVal(
            self.hash["NAME"], "tuya_spec_functions", "[]"
        )
        self.tuya_spec_status = await fhem.AttrVal(
            self.hash["NAME"], "tuya_spec_status", "[]"
        )
        self.tuya_spec_functions = ast.literal_eval(self.tuya_spec_functions)
        self.tuya_spec_status = ast.literal_eval(self.tuya_spec_status)

        self._convert_values_to_json()

    def _convert_values_to_json(self):
        for spec in self.tuya_spec_functions + self.tuya_spec_status:
            if spec["values"] == "":
                spec["values"] = "{}"
            if isinstance(spec["values"], str):
                spec["values"] = json.loads(spec["values"])

    # get functions/status from tuya
    async def get_tuya_dev_specification(self):
        # Get specification
        resp = await utils.run_blocking(
            functools.partial(self.tuya_cloud.getdps, self.tt_did)
        )
        self.logger.debug(f"getdps: {resp}")
        return resp["result"]

    async def get_tuya_dev_info(self):
        resp = await utils.run_blocking(
            functools.partial(self.tuya_cloud.getdevices, True)
        )
        if "Error" in resp:
            self.logger.error(f"getdevices: {resp}")
            return {}

        self.logger.debug(f"getdevices: {resp}")
        for dev in resp["result"]:
            if dev["id"] == self.tt_did:
                return dev
        return {}

    async def get_tuya_dev_description(self):
        # Get function description
        response_dict = await utils.run_blocking(
            functools.partial(self.tuya_cloud.getfunctions, self.tt_did)
        )
        self.logger.debug("getfunctions: f{response_dict}")
        fct_desc = response_dict["result"]["functions"]
        fct_code_desc = {}
        for fct in fct_desc:
            fct_code_desc[fct["code"]] = fct["desc"]
        return fct_code_desc

    async def async_status_updated(self, status):
        async with self.update_lock:
            await self.update_readings(status)

    def status_updated(self, status):
        self.create_async_task(self.async_status_updated(status))

    def disconnected(self):
        self.create_async_task(self.async_disconnected())

    async def _add_desc_to_spec(self, spec_fcts, desc):
        for spec in spec_fcts:
            if spec["code"] in desc:
                spec["desc"] = desc[spec["code"]]
        return spec_fcts

    async def retrieve_tuya_specs(self):
        # retrieve cloud codes
        spec = await self.get_tuya_dev_specification()
        self.tuya_spec_functions = spec["functions"]
        self.tuya_spec_status = spec["status"]
        self._convert_values_to_json()
        desc = await self.get_tuya_dev_description()
        self.tuya_spec_functions = await self._add_desc_to_spec(
            self.tuya_spec_functions, desc
        )
        await fhem.CommandAttr(
            self.hash,
            (
                f"{self.hash['NAME']} tuya_spec_functions "
                f"{str(self.tuya_spec_functions)}"
            ),
        )
        await fhem.CommandAttr(
            self.hash,
            f"{self.hash['NAME']} tuya_spec_status {str(self.tuya_spec_status)}",
        )

    async def _create_cloudmapping_dev(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "Initializing...", 1)
        # check if attributes are set
        await self.check_tuya_attributes()
        if len(self.tuya_spec_functions) == 0 and len(self.tuya_spec_status) == 0:
            await self.retrieve_tuya_specs()
            info = await self.get_tuya_dev_info()
            await self.update_info_readings(info)
        else:
            self.info_dict = {
                "category": await fhem.ReadingsVal(self.hash["NAME"], "category", "")
            }

        await self.setup_connection()

        status = await self._connected_device.detect_available_dps()

        await self.prepare_attributes(status)
        await self.update_readings(status, set_ready=True)

    async def prepare_attributes(self, status):
        options = []
        dps = {}
        for opt in self.tuya_spec_status:
            options.append(opt["code"])
            dps[f"dp_{int(opt['dp_id']):02d}"] = ""

        for dp in list(status):
            dps[f"dp_{int(dp):02d}"] = ""

        attr_conf = {}
        for dp in list(dps):
            attr_conf[dp] = {
                "function": "set_attr_dp",
                "default": "",
                "options": ",".join(options),
            }
        self.attr_config.update(attr_conf)
        self.set_attr_config(self.attr_config)
        await utils.handle_define_attr(self.attr_config, self, self.hash)

        # if spec contains dp_id
        for spec in self.tuya_spec_status + self.tuya_spec_functions:
            if "dp_id" in spec:
                dp = spec["dp_id"]
                code = spec["code"]
                val = await fhem.AttrVal(self.hash["NAME"], f"dp_{int(dp):02d}", "")
                if val == "":
                    if f"dp_{int(dp):02d}" in self.attr_config:
                        await fhem.CommandAttr(
                            self.hash,
                            f"{self.hash['NAME']} dp_{int(dp):02d} {code}",
                        )
                    else:
                        self.logger.warning(
                            f"dp_{int(dp):02d} in spec but not found locally."
                            " This should be reported to TuYa"
                        )
        await self.set_attr_dp(self.hash)

    async def update_dps_loop(self):
        while True:
            await asyncio.sleep(5)
            # this is required to force update measurements (power, current, voltage)
            if self._connected_device:
                await self._connected_device.device.device.updatedps()

    async def status_quick_loop(self):
        while True:
            await asyncio.sleep(60)
            # this loop just ensures that all dps are updated every 60s
            if self._connected_device:
                await self._connected_device.device.device.status_quick()

    async def setup_connection(self):
        state_set = False
        connected = False
        while not connected:
            try:
                self._connected_device = await self.tt.connect(
                    self.tt_ip,
                    self.tt_did,
                    self.tt_localkey,
                    self.tt_version,
                    self,
                    timeout=15,
                )
                if self.update_dps_loop_task is not None:
                    self.update_dps_loop_task = self.create_async_task(
                        self.update_dps_loop()
                    )
                if self.status_quick_loop_task is not None:
                    self.status_quick_loop_task = self.create_async_task(
                        self.status_quick_loop()
                    )
                connected = True
            except Exception:
                if not state_set:
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "online", "0", 1
                    )
                    state_set = True
                    self.logger.exception("Failed to connect to device")
                # short sleep is required for passive devices
                await asyncio.sleep(1)

    async def create_device(self):
        try:
            if self.tt_key != "" and self.tt_secret != "":
                await self._create_cloudmapping_dev()
            elif self.tt_type in mappings.knownSchemas:
                await self._create_mapping_dev()
            else:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "Please use API_KEY and API_SECRET", 1
                )
        except Exception:
            self.logger.exception("Failed create_device")

    async def async_disconnected(self):
        await fhem.readingsSingleUpdate(self.hash, "online", "0", 1)
        self._connected_device = None
        await asyncio.sleep(5)
        await self.setup_connection()

    def convert(self, value, schema):
        if schema["type"] == "Integer":
            values = schema["values"]
            if self.tt_productid == "IAYz2WK1th0cMLmL":
                if schema["code"] == "cur_voltage":
                    value /= 0.2
                elif schema["code"] == "upper_temp":
                    value /= 10
                elif schema["code"] == "temp_set":
                    value /= 0.2
            elif self.tt_productid == "wifvoilfrqeo6hvu":
                if schema["code"] == "cur_voltage":
                    value /= 10
            return value / (10 ** values["scale"])
        elif schema["type"] == "Boolean":
            if value is True:
                return "on"
            return "off"
        elif schema["type"] == "Enum":
            if "translation" in schema["values"]:
                if str(value) in schema["values"]["translation"]:
                    return schema["values"]["translation"][value]
        return value

    def alpha_to_dec(self, s):
        o = ord(s)
        if o >= ord("A") and o <= ord("Z"):
            return o - ord("A")
        if o >= ord("a") and o <= ord("z"):
            return o - ord("a") + 26
        if o >= ord("0") and o <= ord("9"):
            return o - ord("0") + 26 + 26
        if o == ord("/"):
            return 63
        return o

    def string_to_hexarr(self, s):
        resarr = []
        alphaarr = []
        for x in s:
            alphaarr.append(self.alpha_to_dec(x))
        x = 0
        while x < len(alphaarr):
            resarr.append(alphaarr[x] >> 2)
            resarr.append((alphaarr[x] & 0x03) << 2 | ((alphaarr[x + 1] & 0x30) >> 4))
            resarr.append(alphaarr[x + 1] & 0x0F)
            x += 2
        return resarr

    def convert_json(self, value, schema):
        flat_json = {}
        if "category" in self.info_dict and self.info_dict["category"] == "zndb":
            if schema["dp_id"] == 6:
                hexarr = self.string_to_hexarr(value)
                if len(hexarr) > 15:
                    flat_json["voltage"] = (
                        hexarr[1] << 8 | hexarr[2] << 4 | hexarr[3]
                    ) / 10
                    flat_json["current"] = (
                        hexarr[7] << 8 | hexarr[8] << 4 | hexarr[9]
                    ) / 1000
                    flat_json["power"] = hexarr[13] << 8 | hexarr[14] << 4 | hexarr[15]
        return flat_json

    async def update_info_readings(self, info_dict):
        self.info_dict = info_dict
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for reading in info_dict:
                if reading == "status":
                    continue
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading, info_dict[reading]
                )
        except Exception:
            self.logger.exception("Failed to update info readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_readings(self, status, set_ready=False):
        if "dps" in status:
            status = status["dps"]
        state_set = not set_ready
        await fhem.readingsBeginUpdate(self.hash)
        try:
            stateused = False
            for dp in status:
                found = False
                for st in self.tuya_spec_status:
                    if "dp_id" in st and st["dp_id"] == int(dp):
                        found = True
                        reading = st["code"]
                        if st["code"] == self.master_switch:
                            reading = "state"
                            stateused = True
                        self.logger.debug(
                            f"handle type {st['type']} for dp_id "
                            f"{st['dp_id']} with value {status[dp]}"
                        )
                        if st["type"] == "Json":
                            if st["code"] in ["colour_data", "colour_data_v2"]:
                                await self.update_readings_colour(
                                    st["code"], status[dp]
                                )
                            else:
                                flat_json = self.convert_json(status[dp], st)
                                for name in flat_json:
                                    await fhem.readingsBulkUpdateIfChanged(
                                        self.hash,
                                        reading + "_" + name,
                                        flat_json[name],
                                    )
                        else:
                            if reading == "state":
                                state_set = True
                            await fhem.readingsBulkUpdateIfChanged(
                                self.hash,
                                reading,
                                self.convert(status[dp], st),
                            )
                        break

                if not found:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        f"dp_{int(dp):02d}",
                        status[dp],
                    )
            if not stateused:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "online", "1")
            if not state_set:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "ready")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def Undefine(self, hash):
        if self._connected_device:
            await self._connected_device.close()
            self._connected_device = None
        await super().Undefine(hash)

    # The following code is only for setup/scan process via tuya cloud
    async def set_scan_devices(self, hash, params):
        self.create_async_task(self._scan_devices())

    async def _scan_devices(self):
        json_data = await utils.run_blocking(
            functools.partial(self.tuya_cloud.getdevices, verbose=True)
        )
        if "Error" in json_data:
            self.logger.error(f"getdevices: {json_data}")
            await fhem.readingsSingleUpdate(self.hash, "state", f"{json_data}", 1)
            return

        # Filter to only Name, ID and Key, product_id, icon
        tuyadevices = []
        for i in json_data["result"]:
            item = {}
            item["name"] = i["name"].strip()
            item["id"] = i["id"]
            item["ip"] = i["ip"]
            item["sub"] = i["sub"]
            item["key"] = i["local_key"]
            item["product_id"] = i["product_id"]
            item["icon"] = i["icon"]
            await fhem.readingsBeginUpdate(self.hash)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, item["id"] + "_name", item["name"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, item["id"] + "_id", item["id"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, item["id"] + "_localkey", item["key"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, item["id"] + "_productid", item["product_id"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                item["id"] + "_icon",
                "https://images.tuyaeu.com/" + item["icon"],
            )
            await fhem.readingsEndUpdate(self.hash, 1)
            tuyadevices.append(item)

        # Display device list
        self.logger.debug("Device Listing")
        output = json.dumps(tuyadevices, indent=4)  # sort_keys=True)
        self.logger.debug(output)
        await fhem.readingsSingleUpdate(
            self.hash,
            "state",
            f"found {len(tuyadevices)} devices, start local scan...",
            1,
        )

        # scan local devices to get IP
        self.logger.debug("Scan local devices...")
        devices = await utils.run_blocking(
            functools.partial(self.tt.deviceScan, False, 20, False, False)
        )

        def getIP(d, gwid):
            for ip in d:
                if gwid == d[ip]["gwId"]:
                    return (ip, d[ip]["version"])
            return (0, 0)

        self.logger.debug("Polling local devices...")
        count_found = 0
        self.create_device_list = []
        for i in tuyadevices:
            name = i["name"]
            id = i["id"]
            (ip, ver) = getIP(devices, i["id"])
            local_key = i["key"]
            productid = i["product_id"]

            # do not create device if no IP was discovered
            if ver == 0 and i["sub"] is True:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, f"{id}_ip", "offline", 1
                )
                continue

            if ver == 0:
                # device not discovered
                ip = "offline"
                ver = "3.3"
            else:
                count_found += 1

            await fhem.readingsSingleUpdateIfChanged(self.hash, f"{id}_ip", ip, 1)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, f"{id}_version", str(ver), 1
            )

            # create FHEM device
            self.create_device_list.append(
                {
                    "name": name,
                    "name_esc": name.replace(" ", "_"),
                    "device_id": id,
                    "productid": productid,
                    "ip": ip,
                    "local_key": local_key,
                    "version": ver,
                }
            )

        # devices which can be created from setup
        set_conf = {"scan_devices": {}}
        set_conf["create_device"] = {"args": ["name"], "options": ""}
        options = []
        for dev in self.create_device_list:
            options.append(dev["name_esc"] + "_" + dev["device_id"])
        set_conf["create_device"]["options"] = ",".join(options)
        self.set_set_config(set_conf)

        await fhem.readingsSingleUpdate(
            self.hash,
            "state",
            f"{count_found} devices found localy",
            1,
        )

    async def update_readings_colour(self, code, hexcolour):
        if code == "colour_data" and self.info_dict["category"] == "dj":
            # only category dj (light) has old colour_data
            (red, green, blue) = self.tt.BulbDevice._hexvalue_to_rgb(hexcolour, "A")
        else:
            (red, green, blue) = self.tt.BulbDevice._hexvalue_to_rgb(hexcolour, "B")

        rgb_hex = f"{red:02x}{green:02x}{blue:02x}"
        await fhem.readingsBulkUpdate(
            self.hash,
            code,
            rgb_hex,
        )
