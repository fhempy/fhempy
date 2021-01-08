import asyncio
import json
import tinytuya
import functools

from .. import fhem, utils
from ..generic import FhemModule
from . import const


class tuya(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.tt_device = None
        self.last_status = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 7:
            return (
                "Usage: define wifi_plug PythonModule tuya"
                " setup <API_KEY> <API_SECRET> <DEVICE_ID> [<REGION>=eu]<br>"
                "OR if you want to define only one device with existing local key<br>"
                " <TYPE> <DEVICE_ID> <IP> <LOCAL_KEY> [<VERSION>=3.3]"
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
        else:
            self.tt_id = args[4]
            self.tt_ip = args[5]
            self.tt_key = args[6]
            if len(args) == 8:
                self.tt_version = float(args[7])
            else:
                self.tt_version = 3.3
            # set internal
            hash["DEVICEID"] = self.tt_id
            # set attributes
            attr_config = {
                "interval": {
                    "default": 15,
                    "format": "int",
                    "help": "Change status update interval, default is 15.",
                },
                "device_type": {
                    "default": "Device",
                    "options": "OutletDevice,CoverDevice,BulbDevice,Device",
                },
            }
            self.set_attr_config(attr_config)
            # this is needed to set default values
            await utils.handle_define_attr(attr_config, self, hash)
            # create device
            self.tt_device = getattr(tinytuya, self.tt_type)(
                self.tt_id, self.tt_ip, self.tt_key
            )
            self.tt_device.set_version(self.tt_version)
            self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            await self.update_once()
            await asyncio.sleep(self._attr_interval)

    async def update_once(self):
        try:
            status = await utils.run_blocking(functools.partial(self.tt_device.status))
            if self.last_status != status:
                await self.update_readings(status)
        except (ValueError, TypeError):
            pass
        except Exception:
            self.logger.error("Failed to get current status from device")

    async def update_readings(self, status):
        set_config = {}
        status = status["dps"]
        tt_type = type(self.tt_device).__name__
        if tt_type in const.dp_ids:
            dp_ids = const.dp_ids[tt_type]
        else:
            dp_ids = const.dp_ids["OutletDevice"]

        await fhem.readingsBeginUpdate(self.hash)
        try:
            for dp in status:
                if dp in dp_ids:
                    if "convert" in dp_ids[dp]:
                        val = dp_ids[dp]["convert"](status[dp])
                    else:
                        val = status[dp]
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash, dp_ids[dp]["name"], val
                    )
                    if "set" in dp_ids[dp]:
                        set_config.update(dp_ids[dp]["set"])
        except:
            self.logger.exception("Failed to update readings")
        self.set_set_config(set_config)
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_attr_device_type(self, hash):
        if self.tt_device:
            del self.tt_device
            self.tt_device = None
        self.tt_type = self._attr_device_type
        self.tt_device = getattr(tinytuya, self.tt_type)(
            self.tt_id, self.tt_ip, self.tt_key
        )
        self.tt_device.set_version(self.tt_version)

    async def set_onoff(self, hash, params):
        if params["cmd"][0:2] == "on":
            func = self.tt_device.turn_on
            new_state = "on"
        else:
            func = self.tt_device.turn_off
            new_state = "off"
        self.create_async_task(
            self._call_fct_upd_reading(
                functools.partial(func, switch=params["function_param"]),
                "state",
                new_state,
            )
        )

    async def _call_fct_upd_reading(self, function, reading, new_state):
        await utils.run_blocking(function)
        await fhem.readingsSingleUpdate(self.hash, reading, new_state, 1)

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
                tinytuya.tuyaPlatform,
                self.tt_region,
                self.tt_key,
                self.tt_secret,
                uri,
                token,
            )
        )

    async def _scan_devices(self):
        # Get Oauth Token from tuyaPlatform
        uri = "token?grant_type=1"
        response_dict = await self._request_tuyacloud(uri)
        token = response_dict["result"]["access_token"]

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

            # do not create device if no IP was discovered
            if ver == 0:
                continue

            await fhem.readingsSingleUpdateIfChanged(self.hash, f"{id}_ip", ip, 1)
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, f"{id}_version", str(ver), 1
            )

            if (
                await fhem.checkIfDeviceExists(
                    self.hash, "PYTHONTYPE", "tuya", "DEVICEID", id
                )
                is False
            ):
                # create FHEM device
                await fhem.CommandDefine(
                    self.hash,
                    f"{name}_{id} PythonModule tuya Device {id} {ip} {local_key} {ver}",
                )
                count_created += 1

        await fhem.readingsSingleUpdate(
            self.hash,
            "state",
            f"done, created {count_created} devices",
            1,
        )
