import asyncio
import functools

from tuya_iot import (
    AuthType,
    TuyaDevice,
    TuyaDeviceListener,
    TuyaDeviceManager,
    TuyaHomeManager,
    TuyaOpenAPI,
    TuyaOpenMQ,
)
from fhempy.lib import fhem, utils

from fhempy.lib.generic import FhemModule

from .const import (
    TUYA_ENDPOINT,
)


class tuya_cloud_setup:
    def __init__(self, logger, fhemdevice: FhemModule):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash
        self._t_devicelist = []
        self._ready = False

    async def Define(self, hash, args, argsh):
        self._t_apikey = args[4]
        self._t_apisecret = args[5]
        self._t_username = args[6]
        self._t_password = args[7]
        if len(args) > 8:
            self._t_apptype = args[8]
        else:
            self._t_apptype = "smartlife"

        if len(args) > 9:
            self._t_region = args[9]
        else:
            self._t_region = "Europe"

        self.fhemdev.create_async_task(self.run_setup())

    def _get_region_url(self, region) -> str:
        for url in TUYA_ENDPOINT:
            if TUYA_ENDPOINT[url] == region:
                return url

    def _get_countrycode(self, region) -> str:
        if region == "Europe":
            return "eu"
        else:
            return "cn"

    async def run_setup(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        if await self._init_tuya_sdk() is True:
            self._ready = True
            await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
            await self._init_devices()

    async def restart_mqtt_loop(self):
        while True:
            await asyncio.sleep(7100)  # nearly 2 hours
            try:
                await self.restart_mqtt()
            except Exception as ex:
                self.logger.exception(ex)

    async def restart_mqtt(self):
        try:
            self.device_manager.mq.stop()
            self.tuya_mq.stop()
        except Exception:
            pass

        self.tuya_mq = TuyaOpenMQ(self.device_manager.api)
        self.tuya_mq.start()

        self.device_manager.mq = self.tuya_mq
        self.tuya_mq.add_message_listener(self.device_manager.on_message)

    async def _init_tuya_sdk(self) -> bool:
        auth_type = AuthType(0)
        api = TuyaOpenAPI(
            self._get_region_url(self._t_region),
            self._t_apikey,
            self._t_apisecret,
            auth_type,
        )

        api.set_dev_channel("fhempy")

        response = (
            await utils.run_blocking(
                functools.partial(api.connect, self._t_username, self._t_password)
            )
            if auth_type == AuthType.CUSTOM
            else await utils.run_blocking(
                functools.partial(
                    api.connect,
                    self._t_username,
                    self._t_password,
                    self._get_countrycode(self._t_region),
                    self._t_apptype,
                )
            )
        )
        if response.get("success", False) is False:
            if response.get("code", 0) == 2406:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", "Tuya project too old, create new one", 1
                )
            else:
                await fhem.readingsSingleUpdate(
                    self.hash, "state", f"failed to login: {response}", 1
                )
                self.logger.error(f"Tuya login error response: {response}")
            return False

        self.tuya_mq = TuyaOpenMQ(api)
        self.tuya_mq.start()
        # self.fhemdev.create_async_task(self.restart_mqtt_loop())

        self.device_manager = TuyaDeviceManager(api, self.tuya_mq)

        # Get device list
        self.home_manager = TuyaHomeManager(api, self.tuya_mq, self.device_manager)
        await utils.run_blocking(
            functools.partial(self.home_manager.update_device_cache)
        )
        t_cloud_setup = self

        class DeviceListener(TuyaDeviceListener):
            """Device Update Listener."""

            def __init__(self, logger) -> None:
                super().__init__()
                self.logger = logger

            def update_device(self, device: TuyaDevice):
                self.logger.debug(f"update_device received for {device.id}")
                for dev in t_cloud_setup.tuya_devices:
                    if dev.id == device.id:
                        try:
                            asyncio.run_coroutine_threadsafe(
                                dev.update(device), t_cloud_setup.fhemdev.loop
                            )
                        except Exception:
                            self.logger.exception("Failed to update device")

            def add_device(self, device: TuyaDevice):
                self.logger.info(f"add_device received for {device.id}")
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.add_fhem_device(device), t_cloud_setup.fhemdev.loop
                    )
                except Exception:
                    self.logger.exception("Failed to add device")

            async def add_fhem_device(self, device: TuyaDevice):
                await t_cloud_setup._create_fhem_device(device.name, device.id)
                try:
                    self.tuya_mq.stop()
                except Exception:
                    pass
                self.tuya_mq = TuyaOpenMQ(
                    t_cloud_setup.device_manager.device_manager.api
                )
                self.tuya_mq.start()

                t_cloud_setup.device_manager.mq = self.tuya_mq
                self.tuya_mq.add_message_listener(
                    t_cloud_setup.device_manager.on_message
                )

            def remove_device(self, device_id: str):
                self.logger.info(f"remove_device received for {device_id}")

        __listener = DeviceListener(self.logger)
        self.device_manager.add_device_listener(__listener)
        self.tuya_mq.add_message_listener(self.device_manager.on_message)

        return True

    @property
    def ready(self):
        return self._ready

    def register_tuya_device(self, device):
        self._t_devicelist.append(device)

    @property
    def tuya_devices(self):
        return self._t_devicelist

    async def _create_fhem_device(self, name, device_id):
        devalias = name
        devname = name + "_" + device_id
        devname = utils.remove_umlaut(devname.replace(" ", "_").replace("-", "_"))
        device_exists = await fhem.checkIfDeviceExists(
            self.hash, "PYTHONTYPE", "tuya_cloud", "DEVICEID", device_id
        )
        if not device_exists:
            self.logger.info(
                (
                    f"create: {devname} PythonModule tuya_cloud "
                    f"{self.hash['NAME']} {device_id}"
                )
            )
            # define each device (CommandDefine ... tuya_cloud_setup_dev deviceid
            await fhem.CommandDefine(
                self.hash,
                (
                    f"{devname} PythonModule tuya_cloud "
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

    async def send_commands(self, deviceid, commands):
        await utils.run_blocking(
            functools.partial(self.device_manager.send_commands, deviceid, commands)
        )
