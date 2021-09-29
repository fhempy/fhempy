import asyncio
from fhempy.lib.generic import FhemModule
from fhempy.lib import fhem, fhem_pythonbinding
from meross_iot.model.enums import OnlineStatus, Namespace


class meross_device:
    def __init__(self, logger, fhemdevice: FhemModule):
        self.logger = logger
        self.fhemdev = fhemdevice
        self.hash = fhemdevice.hash

    async def Define(self, hash, args, argsh):
        self._setupdev_name = args[3]
        self._deviceid = args[4]
        self._device = None
        self.hash["DEVICEID"] = self._deviceid

        self._setupdev = None
        await fhem.readingsSingleUpdate(self.hash, "state", "ready", 1)
        self.fhemdev.create_async_task(self._init_device())

    async def _get_set_commands(self):
        set_conf = {}
        set_conf["on"] = {}
        set_conf["off"] = {}
        self.fhemdev.set_set_config(set_conf)

    async def set_on(self, hash, params):
        await self._device.async_turn_on()

    async def set_off(self, hash, params):
        await self._device.async_turn_off()

    async def _init_device(self):
        try:
            await self._connect_to_setup_device()
            await self._setup_device()
            await self._get_set_commands()
            await self.update_readings()
        except Exception as ex:
            self.logger.exception(ex)

    async def _connect_to_setup_device(self):
        while self._setupdev is None or self._setupdev.ready is False:
            await asyncio.sleep(1)
            self._setupdev = fhem_pythonbinding.getFhemPyDeviceByName(
                self._setupdev_name
            )
            if self._setupdev:
                self._setupdev = self._setupdev.meross_device

    async def _async_push_notification_received(
        self, namespace: Namespace, data: dict, device_internal_id: str
    ):
        update_state = False
        full_update = False

        if namespace == Namespace.CONTROL_UNBIND:
            self.logger.warning(
                f"Received unbind event. Removing device {self._device.name} from FHEM"
            )
            await self.platform.async_remove_entity(self.entity_id)
        elif namespace == Namespace.SYSTEM_ONLINE:
            self.logger.warning(f"Device {self._device.name} reported online event.")
            online = OnlineStatus(int(data.get("online").get("status")))
            update_state = True
            full_update = online == OnlineStatus.ONLINE

        elif namespace == Namespace.HUB_ONLINE:
            self.logger.warning(
                f"Device {self._device.name} reported (HUB) online event."
            )
            online = OnlineStatus(int(data.get("status")))
            update_state = True
            full_update = online == OnlineStatus.ONLINE
        else:
            update_state = True
            full_update = False

        if full_update:
            await self._device.async_update()

        if update_state:
            await self.update_readings()

    async def _setup_device(self):
        self._device = self._setupdev.get_device_by_id(self._deviceid)

        if self._device is not None:
            await self._device.async_update()
            self._device.register_push_notification_handler_coroutine(
                self._async_push_notification_received
            )

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "uuid", self._device.uuid)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "name", self._device.name)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "firmware_version", self._device.firmware_version
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "hardware_version", self._device.hardware_version
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "internal_id", self._device.internal_id
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "mqtt_host", self._device.mqtt_host
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "mqtt_port", self._device.mqtt_port
        )
        await fhem.readingsBulkUpdateIfChanged(self.hash, "type", self._device.type)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "online_status", self._device.online_status.name
        )
        onoff = "off"
        if self._device.is_on():
            onoff = "on"
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", onoff)
        await fhem.readingsEndUpdate(self.hash, 1)
