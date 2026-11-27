import asyncio

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

from fhempy.lib import fhem, utils
from fhempy.lib.generic import FhemModule

# wrong credentials don't get better with a retry, Meross might lock the account
LOGIN_ERRORS = (
    "BadLoginException",
    "BadDomainException",
    "WrongMFAException",
    "MissingMFA",
    "MFARequired",
)


class meross_setup:
    def __init__(self, logger, fhemdevice: FhemModule):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash
        self.ready = False
        self._devices = []
        self._errors = utils.ErrorLogger(logger)

    async def Define(self, hash, args, argsh):
        self._username = args[4]
        self._password = args[5]

        self.fhemdev.create_async_task(self.run_setup())

    async def run_setup(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)
        while True:
            try:
                self._devices = await self._connect()
                self._errors.success(key="connect")
                break
            except Exception as ex:
                if any(cls.__name__ in LOGIN_ERRORS for cls in type(ex).__mro__):
                    self.logger.error(f"Meross login failed: {ex}")
                    await fhem.readingsSingleUpdate(
                        self.hash, "state", "login failed, check username/password", 1
                    )
                    return
                # e.g. no internet yet after a reboot, the cloud comes back
                self._errors.failed(
                    "Failed to connect to Meross cloud, retrying", key="connect"
                )
                delay = self._errors.next_delay("connect", 10, 600)
                await fhem.readingsSingleUpdate(
                    self.hash,
                    "state",
                    f"connection failed, retry in {int(delay)}s: "
                    + utils.describe_exception(ex)[:150],
                    1,
                )
                await asyncio.sleep(delay)

        if len(self._devices) > 0:
            await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
            await self._init_devices()
            self.ready = True
        else:
            await fhem.readingsSingleUpdate(self.hash, "state", "no devices found", 1)

    async def _connect(self):
        """Log in and return the devices of the account."""
        # Setup the HTTP client API from user-password
        http_api_client = await MerossHttpClient.async_from_user_password(
            api_base_url="https://iotx-eu.meross.com",
            email=self._username,
            password=self._password,
        )
        manager = None
        try:
            # Setup and start the device manager
            manager = MerossManager(http_client=http_api_client)
            await manager.async_init()
            # Retrieve all the devices that are registered on this account
            await manager.async_device_discovery()
            return manager.find_devices()
        except Exception:
            # don't keep the MQTT connection and the token of a failed attempt
            if manager is not None:
                try:
                    manager.close()
                except Exception:
                    self.logger.debug("Failed to close Meross manager", exc_info=True)
            try:
                await http_api_client.async_logout()
            except Exception:
                self.logger.debug("Failed to log out from Meross", exc_info=True)
            raise

    async def _create_fhem_device(self, name, device_id):
        devalias = name
        devname = name + "_" + device_id
        devname = utils.gen_fhemdev_name(devname)
        device_exists = await fhem.checkIfDeviceExists(
            self.hash, "FHEMPYTYPE", "meross", "DEVICEID", device_id
        )
        if not device_exists:
            self.logger.info(
                (f"create: {devname} fhempy meross " f"{self.hash['NAME']} {device_id}")
            )
            # define each device (CommandDefine ... tuya_cloud_setup_dev deviceid
            await fhem.CommandDefine(
                self.hash,
                (f"{devname} fhempy meross " f"{self.hash['NAME']} {device_id}"),
            )
            await fhem.CommandAttr(self.hash, f"{devname} alias {devalias}")
            # wait for FHEM to handle CommandDefine
            await asyncio.sleep(1)

    async def _init_devices(self):
        # wait for init to complete, otherwise devices might not be available yet
        while await fhem.init_done(self.hash) == 0:
            await asyncio.sleep(3)

        # iterate through device list
        for device in self._devices:
            await self._create_fhem_device(device.name, device.uuid)

    def get_device_by_id(self, id):
        for dev in self._devices:
            if dev.uuid == id:
                return dev
        return None
