import base64
import functools
import html

from fhempy.lib.generic import FhemModule

from .. import fhem, utils
from .xiaomi_cloud import (
    SERVERS,
    CaptchaRequired,
    VerificationRequired,
    XiaomiCloud,
    XiaomiCloudError,
)


class xiaomi_tokens(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._username = None
        self._password = None
        self._cloud = None
        self._device_list = []
        self._all_devices = {}

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        self._attr_list = {
            "servers": {
                "default": ",".join(SERVERS),
                "help": "Comma separated list of Xiaomi cloud servers to check.",
            }
        }
        await self.set_attr_config(self._attr_list)

        self._set_list_conf = {
            "username": {"args": ["username"]},
            "password": {"args": ["password"]},
            "get_tokens": {"help": "Login with username/password and get tokens."},
            "qr_login": {"help": "Login by scanning a QR code with the Mi Home app."},
            "captcha": {
                "args": ["code"],
                "help": "Text of the captcha image if the login requires it.",
            },
            "verify_code": {
                "args": ["code"],
                "help": "Code from the email Xiaomi sends if the login requires it.",
            },
        }
        await self.set_set_config(self._set_list_conf)

        await fhem.readingsSingleUpdateIfChanged(hash, "state", "active", 1)

        self._uniqueid = await fhem.getUniqueId(self.hash)
        self._enc_username = await fhem.ReadingsVal(
            self.hash["NAME"], "xiaomi_username", ""
        )
        self._enc_username = self._enc_username.replace("\\n", "")
        if self._enc_username != "":
            self._username = utils.decrypt_string(self._enc_username, self._uniqueid)

        self._enc_password = await fhem.ReadingsVal(
            self.hash["NAME"], "xiaomi_password", ""
        )
        self._enc_password = self._enc_password.replace("\\n", "")
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

    async def set_qr_login(self, hash, params):
        self.create_async_task(self.qr_login())

    async def set_captcha(self, hash, params):
        if self._cloud is None:
            return "Please start the login with get_tokens first!"
        self.create_async_task(
            self._login(
                functools.partial(self._cloud.submit_captcha, params["code"].strip())
            )
        )

    async def set_verify_code(self, hash, params):
        if self._cloud is None:
            return "Please start the login with get_tokens first!"
        self.create_async_task(
            self._login(
                functools.partial(
                    self._cloud.submit_verification_code, params["code"].strip()
                )
            )
        )

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
                    f"miio_vacuum_{did} fhempy miio vacuum {ip} {token}",
                )
            )
        elif "viomi" in model:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_vacuum_{did} fhempy miio viomivacuum {ip} {token}",
                )
            )
        elif "chuangmi" in model or "camera" in model:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_camera_{did} fhempy miio chuangmicamera {ip} {token}",
                )
            )
        else:
            self.create_async_task(
                fhem.CommandDefine(
                    self.hash,
                    f"miio_device_{did} fhempy miio device {ip} {token}",
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
                    f"xiaomigw3_{did} fhempy xiaomi_gateway3 {ip} {token}",
                )
            )

    async def obtain_tokens(self):
        self._cloud = XiaomiCloud()
        await fhem.readingsSingleUpdate(self.hash, "state", "logging in...", 1)
        await self._login(
            functools.partial(self._cloud.login, self._username, self._password)
        )

    async def qr_login(self):
        self._cloud = XiaomiCloud()
        cloud = self._cloud
        try:
            image, login_url = await utils.run_blocking(cloud.qr_login_start)
        except Exception as ex:
            await self._login_failed(ex)
            return
        img = base64.b64encode(image).decode()
        await fhem.readingsSingleUpdate(
            self.hash,
            "login_qr_code",
            f"<html><img src='data:image/png;base64,{img}'/><br>"
            f"<a href='{html.escape(login_url, quote=True)}' target='_blank'>"
            "Login URL</a></html>",
            1,
        )
        await fhem.readingsSingleUpdate(
            self.hash, "state", "Please scan the QR code with the Mi Home app", 1
        )
        await self._login(cloud.qr_login_wait)

    async def _login(self, login_step):
        cloud = self._cloud
        try:
            await utils.run_blocking(login_step)
        except CaptchaRequired as captcha:
            img = base64.b64encode(captcha.image).decode()
            await fhem.readingsSingleUpdate(
                self.hash,
                "captcha",
                f"<html><img src='data:image/jpeg;base64,{img}'/></html>",
                1,
            )
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "Please enter the captcha: set " + self.hash["NAME"] + " captcha TEXT",
                1,
            )
            return
        except VerificationRequired:
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "Please enter the code Xiaomi sent you by email: set "
                + self.hash["NAME"]
                + " verify_code CODE",
                1,
            )
            return
        except Exception as ex:
            await self._login_failed(ex)
            return
        if cloud is not self._cloud:
            # another login was started meanwhile
            return
        await fhem.readingsSingleUpdateIfChanged(self.hash, "captcha", "-", 1)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "login_qr_code", "-", 1)
        await fhem.readingsSingleUpdate(
            self.hash, "state", "logged in, retrieving tokens...", 1
        )
        try:
            await utils.run_blocking(functools.partial(self.thread_get_tokens, cloud))
        except Exception as ex:
            self.logger.exception("Failed to get tokens")
            await fhem.readingsSingleUpdate(self.hash, "state", f"{ex}", 1)
            return
        await self.update_device_readings()
        await fhem.readingsSingleUpdate(
            self.hash, "state", f"{len(self._device_list)} devices found", 1
        )

    async def _login_failed(self, ex):
        if isinstance(ex, XiaomiCloudError):
            self.logger.error(f"Failed to login: {ex}")
        else:
            self.logger.exception("Failed to login")
        await fhem.readingsSingleUpdate(self.hash, "state", f"{ex}", 1)

    async def update_device_readings(self):

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
        await self.set_set_config(self._set_list_conf)

    def thread_get_tokens(self, cloud):
        device_list = []
        for server in self._attr_servers.split(","):
            server = server.strip()
            if server == "":
                continue
            try:
                dev_list = cloud.get_devices(server)
            except Exception:
                self.logger.exception(f"Failed to get devices from server {server}")
                continue
            for dev in dev_list:
                dev["country"] = server
                for key in ["name", "token", "model", "localip"]:
                    dev[key] = dev.get(key) or ""
                device_list.append(dev)
        self._device_list = device_list
