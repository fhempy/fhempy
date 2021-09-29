import asyncio

from meross_iot.manager import MerossManager
from meross_iot.http_api import MerossHttpClient

from fhempy.lib import fhem, utils
from fhempy.lib.generic import FhemModule


class meross_setup:
    def __init__(self, logger, fhemdevice: FhemModule):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash
        self.ready = False
        self._devices = []

    async def Define(self, hash, args, argsh):
        self._username = args[4]
        self._password = args[5]

        self.fhemdev.create_async_task(self.run_setup())

    async def run_setup(self):
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)

        # Setup the HTTP client API from user-password
        http_api_client = await MerossHttpClient.async_from_user_password(
            email=self._username, password=self._password
        )

        # Setup and start the device manager
        manager = MerossManager(http_client=http_api_client)
        await manager.async_init()

        # Retrieve all the MSS310 devices that are registered on this account
        await manager.async_device_discovery()
        self._devices = manager.find_devices()
        if len(self._devices) > 0:
            await fhem.readingsSingleUpdate(self.hash, "state", "connected", 1)
            await self._init_devices()
            self.ready = True
        else:
            await fhem.readingsSingleUpdate(self.hash, "state", "failed to connect", 1)

    async def _create_fhem_device(self, name, device_id):
        devalias = name
        devname = name + "_" + device_id
        devname = utils.gen_fhemdev_name(devname)
        device_exists = await fhem.checkIfDeviceExists(
            self.hash, "PYTHONTYPE", "meross", "DEVICEID", device_id
        )
        if not device_exists:
            self.logger.info(
                (
                    f"create: {devname} PythonModule meross "
                    f"{self.hash['NAME']} {device_id}"
                )
            )
            # define each device (CommandDefine ... tuya_cloud_setup_dev deviceid
            await fhem.CommandDefine(
                self.hash,
                (f"{devname} PythonModule meross " f"{self.hash['NAME']} {device_id}"),
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
