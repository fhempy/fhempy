import functools

from fhempy.lib.generic import FhemModule
from micloud import MiCloud

from .. import fhem, utils


class xiaomi_tokens(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._username = None
        self._password = None
        self._country = ["de", "cn", "sg"]
        self._all_devices = {}

        self._set_list_conf = {
            "username": {"args": ["username"]},
            "password": {"args": ["password"]},
            "get_tokens": {},
        }
        self.set_set_config(self._set_list_conf)
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        await fhem.readingsSingleUpdateIfChanged(hash, "state", "active", 1)

        self._uniqueid = await fhem.getUniqueId(self.hash)
        self._enc_username = await fhem.ReadingsVal(
            self.hash["NAME"], "xiaomi_username", ""
        )
        if self._enc_username != "":
            self._username = utils.decrypt_string(self._enc_username, self._uniqueid)

        self._enc_password = await fhem.ReadingsVal(
            self.hash["NAME"], "xiaomi_password", ""
        )
        if self._enc_password != "":
            self._password = utils.decrypt_string(self._enc_password, self._uniqueid)

        # retrieve tokens
        if self._username and self._password:
            self.create_async_task(self.obtain_tokens())
        return

    async def set_username(self, hash, params):
        self._username = params["username"]
        self._enc_username = utils.encrypt_string(self._username, self._uniqueid)
        await fhem.readingsSingleUpdateIfChanged(
            hash, "xiaomi_username", self._enc_username, 1
        )
        return ""

    async def set_password(self, hash, params):
        self._password = params["password"]
        self._enc_password = utils.encrypt_string(self._password, self._uniqueid)
        await fhem.readingsSingleUpdateIfChanged(
            hash, "xiaomi_password", self._enc_password, 1
        )
        return ""

    async def set_get_tokens(self, hash, params):
        if self._username and self._password:
            self.create_async_task(self.obtain_tokens())
        else:
            return "Please set username & password first!"

    async def set_create_miio_device(self, hash, params):
        arr = params["dev"].split("_")
        did = arr[0]
        country = arr[1]
        model = self._all_devices[did + country]["model"]
        ip = self._all_devices[did + country]["localip"]
        token = self._all_devices[did + country]["token"]
        if "vacuum" in model:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_vacuum_{did} PythonModule miio vacuum {ip} {token}",
                )
            )
        elif "viomi" in model:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_vacuum_{did} PythonModule miio viomivacuum {ip} {token}",
                )
            )
        elif "chuangmi" in model or "camera" in model:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_camera_{did} PythonModule miio chuangmicamera {ip} {token}",
                )
            )
        else:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_device_{did} PythonModule miio device {ip} {token}",
                )
            )

    async def set_create_gateway3_device(self, hash, params):
        arr = params["dev"].split("_")
        did = arr[0]
        country = arr[1]
        ip = self._all_devices[did + country]["localip"]
        token = self._all_devices[did + country]["token"]
        if ip != "" and token != "":
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"xiaomigw3_{did} PythonModule xiaomi_gateway3 {ip} {token}",
                )
            )

    async def obtain_tokens(self):
        try:
            await utils.run_blocking(functools.partial(self.thread_get_tokens))
        except Exception as ex:
            await fhem.readingsSingleUpdateIfChanged(f"Failed to get tokens: {ex}")
            return

        self._miio_devices = []
        self._xiaomigw3_devices = []
        await fhem.readingsBeginUpdate(self.hash)
        for dev in self._device_list:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_" + dev["country"] + "_name", dev["name"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_" + dev["country"] + "_token", dev["token"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_" + dev["country"] + "_model", dev["model"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_" + dev["country"] + "_ip", dev["localip"]
            )
            self._all_devices[dev["did"] + dev["country"]] = dev
            if dev["did"][0:3] != "blt" and dev["localip"] != "":
                self._miio_devices.append(
                    dev["did"]
                    + "_"
                    + dev["country"]
                    + "_("
                    + dev["name"].replace(" ", "_")
                    + ")"
                )
                if dev["model"] == "lumi.gateway.mgl03":
                    self._xiaomigw3_devices.append(
                        dev["did"]
                        + "_"
                        + dev["country"]
                        + "_("
                        + dev["name"].replace(" ", "_")
                        + ")"
                    )
        await fhem.readingsEndUpdate(self.hash, 1)

        self._set_list_conf["create_miio_device"] = {
            "args": ["dev"],
            "help": "Creates a fhempy miio device to control your Xiaomi device.",
            "options": ",".join(self._miio_devices),
        }
        self._set_list_conf["create_gateway3_device"] = {
            "args": ["dev"],
            "help": "Creates a fhempy xiaomi_gateway3 device and devices for all connected devices.",
            "options": ",".join(self._xiaomigw3_devices),
        }
        self.set_set_config(self._set_list_conf)

    def thread_get_tokens(self):
        self._device_list = []
        mc = MiCloud(self._username, self._password)
        if mc.login():
            for country in self._country:
                dev_list = mc.get_devices(country=country)
                for dev in dev_list:
                    dev["country"] = country
                    self._device_list.append(dev)
        else:
            raise Exception("Login failed, please check username/password!")
