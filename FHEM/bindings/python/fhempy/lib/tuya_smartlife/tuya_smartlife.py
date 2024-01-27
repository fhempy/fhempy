#!/usr/bin/env python3
"""Support for Tuya Smart devices."""

import functools
from io import BytesIO

from tuya_sharing import LoginControl, Manager, SharingTokenListener

import fhempy.lib.tuya_cloud.tuya_cloud_device as tcd
import fhempy.lib.tuya_cloud.tuya_cloud_setup as tcs
from fhempy.lib import fhem, utils
from fhempy.lib.generic import FhemModule

CONF_CLIENT_ID = "HA_3y9q4ak7g4ephrvke"
CONF_SCHEMA = "haauthorize"
APP_QR_CODE_HEADER = "tuyaSmart--qrLogin?token="


class tuya_smartlife(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.device = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        # initialize set commands
        set_conf = {
            "scan_done": {},
        }
        self.set_set_config(set_conf)

        # define my_tuya_smartlife fhempy tuya_smartlife USERCODE
        # check if usercode is available
        if len(args) < 4:
            return "Usage: define my_tuya_smartlife fhempy tuya_smartlife USERCODE"

        self.usercode = args[3]

        # init login control
        self.login_control = LoginControl()

        # start login procedure asynchron
        self.create_async_task(self.login)

    async def login(self):
        # use LoginControl.qr_code to login
        response = await utils.run_blocking(
            functools.partial(
                self.login_control.qr_code, CONF_CLIENT_ID, CONF_SCHEMA, self.usercode
            )
        )

        # check if response has success True
        if response.get("success", False):
            qr_code = response["result"]["qrcode"]
            self._qr_code = qr_code
            self.logger.debug("qr_code=%s", qr_code)
            img = self._generate_qr_code(APP_QR_CODE_HEADER + qr_code)

            # set reading qr_code to img
            await fhem.readingsSingleUpdateIfChanged(self.hash, "login_qr_code", img, 1)

    async def set_scan_done(self, hash, params):
        """Check login_result from LoginControl to get token and secret"""
        ret, info = await utils.run_blocking(
            functools.partial(
                self.login_control.login_result,
                self._qr_code,
                CONF_CLIENT_ID,
                self.usercode,
            )
        )
        if ret:
            self.token_info = {
                "t": info.get("t"),
                "uid": info.get("uid"),
                "expire_time": info.get("expire_time"),
                "access_token": info.get("access_token"),
                "refresh_token": info.get("refresh_token"),
            }
            self.terminal_id = info.get("terminal_id")
            self.endpoint = info.get("endpoint")

    async def connect_to_smartlife(self):
        token_listener = TokenListener(self)
        smart_life_manager = Manager(
            CONF_CLIENT_ID,
            self.usercode,
            self.terminal_id,
            self.endpoint,
            self.token_info,
            token_listener,
        )

    def _generate_qr_code(data: str) -> str:
        """Generate a base64 PNG string represent QR Code image of data."""
        import pyqrcode  # pylint: disable=import-outside-toplevel

        qr_code = pyqrcode.create(data)

        with BytesIO() as buffer:
            qr_code.svg(file=buffer, scale=4)
            return str(
                buffer.getvalue()
                .decode("ascii")
                .replace("\n", "")
                .replace(
                    (
                        '<?xml version="1.0" encoding="UTF-8"?>'
                        '<svg xmlns="http://www.w3.org/2000/svg"'
                    ),
                    "<svg",
                )
            )

    async def Undefine(self, hash):
        if self.device:
            await self.device.Undefine(hash)
        return await super().Undefine(hash)

    async def set_reset_energy(self, hash, params):
        await self.device.set_reset_energy(hash, params)

    async def set_boolean(self, hash, params):
        await self.device.set_boolean(hash, params)

    async def set_enum(self, hash, params):
        await self.device.set_enum(hash, params)

    async def set_json(self, hash, params):
        await self.device.set_json(hash, params)

    async def set_string(self, hash, params):
        await self.device.set_string(hash, params)

    async def set_integer(self, hash, params):
        await self.device.set_integer(hash, params)

    async def set_colour_data(self, hash, params):
        await self.device.set_colour_data(hash, params)

    async def set_colour_data_v2(self, hash, params):
        await self.device.set_colour_data_v2(hash, params)

    @property
    def tuya_cloud_device(self):
        return self.device


class TokenListener(SharingTokenListener):
    def __init__(self, logger, tuya_smartlife: tuya_smartlife) -> None:
        """Init TokenListener."""
        self.logger = logger
        self.tuya_smartlife = tuya_smartlife

    def update_token(self, token_info):
        self.logger.debug("update token info : %s", token_info)
        self.tuya_smartlife.token_info = token_info
