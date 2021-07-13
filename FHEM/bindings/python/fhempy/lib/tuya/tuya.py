import ast
import asyncio
import functools
import json
import re

import tinytuya
from tinytuya import wizard as tt_wizard

from .. import fhem, utils
from ..generic import FhemModule
from . import mappings


class tuya(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.tt_device = None
        self.tt_key = None
        self.tt_secret = None
        self.last_status = None
        self.update_lock = asyncio.Lock()

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 7:
            return (
                "Usage: define wifi_plug PythonModule tuya"
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
        else:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "offline", 1)
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
            # set internal
            hash["DEVICEID"] = self.tt_did
            # set attributes
            self.attr_config = {
                "interval": {
                    "default": 15,
                    "format": "int",
                    "help": "Change status update interval, default is 15.",
                },
                "tuya_spec_functions": {"default": ""},
                "tuya_spec_status": {"default": ""},
                "keep_connected": {
                    "options": "on,off",
                    "format": "bool",
                    "default": "off",
                },
            }
            self.set_attr_config(self.attr_config)
            # this is needed to set default values
            await utils.handle_define_attr(self.attr_config, self, hash)
            # create device
            await self.create_device()
            self.create_async_task(self.update_loop())

    async def _create_mapping_dev(self):
        self.tuya_spec_functions = []
        self.tuya_spec_status = []
        schema = mappings.knownSchemas[self.tt_type]["schema"]
        for schema_part in schema:
            # rename to values
            schema_part["values"] = schema_part["property"]
            schema_part["type"] = schema_part["values"]["type"]
            schema_part["desc"] = ""
            schema_part["values"] = json.dumps(schema_part["values"])
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

    async def set_attr_keep_connected(self, hash):
        self.tt_device.set_socketPersistent(self._attr_keep_connected)

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
        for fct in self.tuya_spec_functions:
            if "id" not in fct:
                # no id configured for this function
                continue
            if fct["type"] == "Boolean":
                if fct["code"] == "switch_1":
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
                options = json.loads(fct["values"])["range"]
                set_conf[fct["code"]] = {
                    "options": ",".join(options),
                    "args": ["selected_val"],
                    "help": fct["desc"],
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
                    "help": fct["desc"],
                    "function_param": fct,
                    "function": "set_integer",
                }
            elif fct["type"] == "String":
                set_conf[fct["code"]] = {
                    "args": ["new_val"],
                    "help": fct["desc"],
                    "function_param": fct,
                    "function": "set_string",
                }
            elif fct["type"] == "Json":
                pass
        self.set_set_config(set_conf)

    async def set_boolean(self, hash, params):
        switch_id = params["function_param"]["id"]
        onoff = False
        if "onoff" in params:
            if params["onoff"] == "on":
                onoff = True
        else:
            if params["cmd"] == "on":
                onoff = True
        func = self.tt_device.set_status
        self.create_async_task(
            self._call_fct_upd_reading(functools.partial(func, onoff, switch=switch_id))
        )

    async def set_integer(self, hash, params):
        index = params["function_param"]["id"]
        new_val = params["selected_val"]
        func = self.tt_device.set_value
        self.create_async_task(
            self._call_fct_upd_reading(functools.partial(func, index, new_val))
        )

    async def set_enum(self, hash, params):
        index = params["function_param"]["id"]
        new_val = params["selected_val"]
        func = self.tt_device.set_status
        self.create_async_task(
            self._call_fct_upd_reading(functools.partial(func, new_val, index))
        )

    async def set_string(self, hash, params):
        index = params["function_param"]["id"]
        new_val = params["new_val"]
        func = self.tt_device.set_status
        self.create_async_task(
            self._call_fct_upd_reading(functools.partial(func, new_val, index))
        )

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

    # get functions/status from tuya
    async def get_tuya_dev_specification(self, token):
        # Get specification
        uri = f"devices/{self.tt_did}/specifications"
        response_dict = await self._request_tuyacloud(uri, token)
        return response_dict["result"]

    async def get_tuya_dev_description(self, token):
        # Get function description
        uri = f"devices/{self.tt_did}/functions"
        response_dict = await self._request_tuyacloud(uri, token)
        fct_desc = response_dict["result"]["functions"]
        fct_code_desc = {}
        for fct in fct_desc:
            fct_code_desc[fct["code"]] = fct["desc"]
        return fct_code_desc

    async def _add_desc_to_spec(self, spec_fcts, desc):
        for spec in spec_fcts:
            if spec["code"] in desc:
                spec["desc"] = desc[spec["code"]]
        return spec_fcts

    async def _create_cloudmapping_dev(self):
        if self.tt_key == "" or self.tt_secret == "":
            await fhem.readingsSingleUpdateIfChanged(
                self.hash,
                "state",
                "Please use API_KEY and API_SECRET",
            )
            return

        await fhem.readingsSingleUpdate(self.hash, "state", "Initializing...", 1)
        # check if attributes are set
        await self.check_tuya_attributes()
        if len(self.tuya_spec_functions) == 0 and len(self.tuya_spec_status) == 0:
            # retrieve cloud codes
            token = await self._obtain_token()
            if token is None:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "Login failed", 1
                )
                return

            spec = await self.get_tuya_dev_specification(token)
            self.tuya_spec_functions = spec["functions"]
            self.tuya_spec_status = spec["status"]
            desc = await self.get_tuya_dev_description(token)
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

        await fhem.readingsSingleUpdate(
            self.hash, "state", "Localscan...please wait...", 1
        )
        # retrieve local dp_s
        self.local_dev = None
        devices = await utils.run_blocking(
            functools.partial(tinytuya.deviceScan, False, 20)
        )

        for ip in devices:
            if devices[ip]["gwId"] == self.tt_did:
                self.local_dev = devices[ip]

        # create attributes dp_1...X
        # add options to attributes to select cloud codes
        # e.g.
        # dp_1 = "switch_1"
        # dp_42 = "switch_overcharge"
        if self.local_dev is not None:
            dev = tinytuya.OutletDevice(self.tt_did, self.tt_ip, self.tt_localkey)
            dev.set_version(self.tt_version)
            self.local_dev["dps"] = await utils.run_blocking(
                functools.partial(dev.status)
            )
            dps = []
            for dp in self.local_dev["dps"]["dps"]:
                dps.append(f"dp_{int(dp):02d}")

            options = []
            for opt in self.tuya_spec_status:
                options.append(opt["code"])
            attr_conf = {}
            for dp in dps:
                attr_conf[dp] = {
                    "function": "set_attr_dp",
                    "default": "",
                    "options": ",".join(options),
                }
            self.attr_config.update(attr_conf)
            self.set_attr_config(self.attr_config)
            await utils.handle_define_attr(attr_conf, self, self.hash)

        await fhem.readingsSingleUpdate(
            self.hash, "state", "Ready to configure dp_ attributes", 1
        )

    async def create_device(self):
        self.tt_device = tinytuya.Device(self.tt_did, self.tt_ip, self.tt_localkey)
        self.tt_device.set_version(self.tt_version)
        if self.tt_type in mappings.knownSchemas:
            await self._create_mapping_dev()
        else:
            self.create_async_task(self._create_cloudmapping_dev())

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_interval)

    async def update_once(self):
        async with self.update_lock:
            try:
                status = await utils.run_blocking(
                    functools.partial(self.tt_device.status)
                )
                if self.last_status != status:
                    await self.update_readings(status)
            except (ValueError, TypeError):
                pass
            except Exception:
                await fhem.readingsSingleUpdate(self.hash, "state", "offline", 1)
                self.logger.error("Failed to get current status from device")

    def convert(self, value, schema):
        if schema["type"] == "Integer":
            values = json.loads(schema["values"])
            return value / (10 ** values["scale"])
        elif schema["type"] == "Boolean":
            if value is True:
                return "on"
            return "off"
        return value

    async def update_readings(self, status):
        status = status["dps"]
        await fhem.readingsBeginUpdate(self.hash)
        try:
            stateused = False
            for dp in status:
                found = False
                for st in self.tuya_spec_status:
                    if "id" in st and st["id"] == int(dp):
                        found = True
                        reading = st["code"]
                        if st["code"] == "switch_1":
                            reading = "state"
                            stateused = True
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
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "online")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def _call_fct_upd_reading(self, function):
        try:
            await utils.run_blocking(function)
        except Exception:
            self.logger.exception("Failed to execute function")
        await self.update_once()

    async def Undefine(self, hash):
        if self.tt_device:
            del self.tt_device
        await super().Undefine(hash)

    # The following code is only for setup/scan process via tuya cloud
    async def set_scan_devices(self, hash, params):
        self.create_async_task(self._scan_devices())

    async def _request_tuyacloud(self, uri, token=None):
        return await utils.run_blocking(
            functools.partial(
                tt_wizard.tuyaPlatform,
                self.tt_region,
                self.tt_key,
                self.tt_secret,
                uri,
                token,
            )
        )

    async def _obtain_token(self):
        # Get Oauth Token from tuyaPlatform
        uri = "token?grant_type=1"
        response_dict = await self._request_tuyacloud(uri)
        if "result" in response_dict:
            token = response_dict["result"]["access_token"]
            return token
        return None

    async def _scan_devices(self):
        token = await self._obtain_token()

        # Get UID from sample Device ID
        uri = "devices/%s" % self.tt_did
        response_dict = await self._request_tuyacloud(uri, token)
        uid = response_dict["result"]["uid"]

        # Use UID to get list of all Devices for User
        uri = "users/%s/devices" % uid
        json_data = await self._request_tuyacloud(uri, token)

        # Filter to only Name, ID and Key
        tuyadevices = []
        for i in json_data["result"]:
            item = {}
            item["name"] = i["name"].strip()
            item["id"] = i["id"]
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
            functools.partial(tinytuya.deviceScan, False, 20)
        )

        def getIP(d, gwid):
            for ip in d:
                if gwid == d[ip]["gwId"]:
                    return (ip, d[ip]["version"])
            return (0, 0)

        self.logger.debug("Polling local devices...")
        count_created = 0
        for i in tuyadevices:
            name = i["name"].replace(" ", "_")
            id = i["id"]
            (ip, ver) = getIP(devices, i["id"])
            local_key = i["key"]
            productid = i["product_id"]

            # do not create device if no IP was discovered
            if ver == 0:
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, f"{id}_ip", "offline", 1
                )
                continue

            await fhem.readingsSingleUpdateIfChanged(self.hash, f"{id}_ip", ip, 1)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, f"{id}_version", str(ver), 1
            )

            # do not create a device if unknown
            # if productid not in mappings.knownSchemas:
            #    continue

            if not await fhem.checkIfDeviceExists(
                self.hash, "PYTHONTYPE", "tuya", "DEVICEID", id
            ):
                # create FHEM device
                await fhem.CommandDefine(
                    self.hash,
                    (
                        f"{name}_{id} PythonModule tuya "
                        f"{productid} {id} {ip} {local_key} "
                        f"{ver} {self.tt_key} {self.tt_secret}"
                    ),
                )
                count_created += 1

        await fhem.readingsSingleUpdate(
            self.hash,
            "state",
            f"done, created {count_created} devices",
            1,
        )
