import asyncio
import functools
import json
from io import BytesIO

from tuya_sharing import (
    CustomerDevice,
    LoginControl,
    Manager,
    SharingDeviceListener,
    SharingTokenListener,
)

import fhempy.lib.fhem as fhem
import fhempy.lib.utils as utils

from .const import APP_QR_CODE_HEADER, CONF_CLIENT_ID, CONF_SCHEMA


class tuya_smartlife_setup:
    def __init__(self, logger, fhemdevice):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.usercode = self.fhemdev.usercode
        self.hash = fhemdevice.hash
        self._t_devicelist = []
        self._ready = False

        # init login control
        self.login_control = LoginControl()

    async def login(self):
        # use LoginControl.qr_code to login

        # get token_info from reading
        self.token_info = json.loads(
            await fhem.ReadingsVal(self.hash["NAME"], "token_info", "{}")
        )
        # get terminal_id from reading
        self.terminal_id = await fhem.ReadingsVal(self.hash["NAME"], "terminal_id", "")
        # get endpoint from reading
        self.endpoint = await fhem.ReadingsVal(self.hash["NAME"], "endpoint", "")

        # check if token_info is not {}
        if self.token_info == {}:
            response = await utils.run_blocking(
                functools.partial(
                    self.login_control.qr_code,
                    CONF_CLIENT_ID,
                    CONF_SCHEMA,
                    self.usercode,
                )
            )

            # check if response has success True
            if response.get("success", False):
                qr_code = response["result"]["qrcode"]
                self._qr_code = qr_code
                self.logger.debug("qr_code=%s", qr_code)
                img = self._generate_qr_code(APP_QR_CODE_HEADER + qr_code)

                # set reading qr_code to img
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "login_qr_code", "<html>" + img + "</html>", 1
                )

                # set attr webCmd to scan_done
                await fhem.CommandAttr(
                    self.hash, f"{self.hash['NAME']} webCmd scan_done"
                )

                # inform user via state to scan qr_code and press scan_done
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash,
                    "state",
                    "Please scan QR Code and press scan_done",
                    1,
                )
        else:
            # connect to smartlife
            self.fhemdev.create_async_task(self.connect_to_smartlife())

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

            # remove login_qr_code reading and webCmd attr
            await fhem.readingsSingleUpdateIfChanged(self.hash, "login_qr_code", "-", 1)
            await fhem.CommandDeleteAttr(self.hash, f"{self.hash['NAME']} webCmd")

            await self.save_token_info()

            self.fhemdev.create_async_task(self.connect_to_smartlife())
        else:
            self.logger.error(f"login_result failed: {info}")
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "state", f"login failed: {info}", 1
            )

    async def save_token_info(self):
        # save token_info to reading
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "token_info",
            json.dumps(self.token_info),
            1,
        )

        # save terminal_id and endpoint to reading
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "terminal_id",
            self.terminal_id,
            1,
        )
        await fhem.readingsSingleUpdateIfChanged(
            self.hash,
            "endpoint",
            self.endpoint,
            1,
        )

    async def connect_to_smartlife(self):
        token_listener = TokenListener(self.logger, self)
        self.device_manager = Manager(
            CONF_CLIENT_ID,
            self.usercode,
            self.terminal_id,
            self.endpoint,
            self.token_info,
            token_listener,
        )

        t_cloud_setup = self

        class DeviceListener(SharingDeviceListener):
            """Device Update Listener."""

            def __init__(self, logger, manager) -> None:
                super().__init__()
                self.logger = logger
                self.manager = manager

            def update_device(self, device: CustomerDevice):
                self.logger.debug(f"update_device received for {device.id}")
                for dev in t_cloud_setup.tuya_devices:
                    if dev.id == device.id:
                        try:
                            asyncio.run_coroutine_threadsafe(
                                dev.update(device), t_cloud_setup.fhemdev.loop
                            )
                        except Exception:
                            self.logger.exception("Failed to update device")

            def add_device(self, device: CustomerDevice):
                self.logger.info(f"add_device received for {device.id}")
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.add_fhem_device(device), t_cloud_setup.fhemdev.loop
                    )
                except Exception:
                    self.logger.exception("Failed to add device")

            async def add_fhem_device(self, device: CustomerDevice):
                await t_cloud_setup._create_fhem_device(device.name, device.id)

            def remove_device(self, device_id: str):
                self.logger.info(f"remove_device received for {device_id}")

        await utils.run_blocking(
            functools.partial(self.device_manager.update_device_cache)
        )

        listener = DeviceListener(self.logger, self.device_manager)
        self.device_manager.add_device_listener(listener)

        self._ready = True

        await self._init_devices()

        await utils.run_blocking(functools.partial(self.device_manager.refresh_mq))
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected", 1)

    def _generate_qr_code(self, data: str) -> str:
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
                    "<svg style='width:228px;height:228px;'",
                )
            )

    async def Undefine(self, hash):
        return

    @property
    def ready(self):
        return self._ready

    def register_tuya_device(self, device):
        self._t_devicelist.append(device)

    def unregister_tuya_device(self, device):
        self._t_devicelist.remove(device)

    @property
    def tuya_devices(self):
        return self._t_devicelist

    async def _create_fhem_device(self, name, device_id):
        devalias = name
        devname = "tuya_smartlife_" + device_id
        devname = utils.gen_fhemdev_name(devname)
        device_exists = await fhem.checkIfDeviceExists(
            self.hash, "FHEMPYTYPE", "tuya_smartlife", "DEVICEID", device_id
        )

        if not device_exists:
            self.logger.info(
                (
                    f"create: {devname} fhempy tuya_smartlife "
                    f"{self.hash['NAME']} {device_id}"
                )
            )
            # define each device (CommandDefine ... tuya_cloud_setup_dev deviceid
            await fhem.CommandDefine(
                self.hash,
                (
                    f"{devname} fhempy tuya_smartlife "
                    f"{self.hash['NAME']} {device_id}"
                ),
            )
            await fhem.CommandAttr(self.hash, f"{devname} alias {devalias}")
            # wait for FHEM to handle CommandDefine
            await asyncio.sleep(1)

    async def _init_devices(self):
        # wait for init to complete, otherwise devices might not be available yet
        while await fhem.init_done(self.hash) == 0:
            await asyncio.sleep(3)

        # retrieve devices from device_manager and create them
        for device_id in self.device_manager.device_map:
            await self._create_fhem_device(
                self.device_manager.device_map[device_id].name, device_id
            )
            await asyncio.sleep(1)

    async def send_commands(self, deviceid, commands):
        await utils.run_blocking(
            functools.partial(self.device_manager.send_commands, deviceid, commands)
        )


class TokenListener(SharingTokenListener):
    def __init__(self, logger, tuya_smartlife_setup: tuya_smartlife_setup) -> None:
        """Init TokenListener."""
        self.logger = logger
        self.tuya_smartlife_setup = tuya_smartlife_setup

    def update_token(self, token_info):
        self.logger.debug("update token info : %s", token_info)
        self.tuya_smartlife_setup.token_info = token_info
        self.tuya_smartlife_setup.fhemdev.create_async_task(
            self.tuya_smartlife_setup.save_token_info()
        )
