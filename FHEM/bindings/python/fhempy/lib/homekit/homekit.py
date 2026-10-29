import asyncio
import json
import logging

import aiohomekit
from aiohomekit.controller.ip.connection import SecureHomeKitConnection
from aiohomekit.exceptions import AccessoryDisconnectedError, AccessoryNotFoundError
from aiohomekit.model.characteristics.characteristic import NUMBER_TYPES
from aiohomekit.model.characteristics.characteristic_formats import (
    CharacteristicFormats,
)
from zeroconf import ServiceStateChange
from zeroconf.asyncio import AsyncServiceBrowser

from .. import fhem
from .. import fhem_pythonbinding as fhempy
from .. import generic, utils
from ..core import zeroconf

# aiohomekit doesn't browse by itself, it attaches to an existing
# AsyncServiceBrowser for these types (find_brower_for_hap_type)
HOMEKIT_SERVICES = ["_hap._tcp.local.", "_hap._udp.local."]

# Bluetooth devices which are out of range or asleep
BLE_RETRY_INTERVAL = 60


_aiohomekit_connect_once = SecureHomeKitConnection._connect_once


async def _connect_once_closing(self):
    # aiohomekit keeps the TCP connection open if pair-verify fails (e.g. a
    # hanging Homebridge answers with garbage) and opens a new one on each
    # reconnect attempt, until fhempy runs out of file descriptors (#686)
    try:
        await _aiohomekit_connect_once(self)
    except BaseException:
        self._drop_transport()
        raise


SecureHomeKitConnection._connect_once = _connect_once_closing


def _on_service_state_change(
    zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    # zeroconf calls handlers with keyword arguments (zeroconf=, service_type=,
    # name=, state_change=), so the parameter names must match exactly.
    # aiohomekit registers its own handler on the browser
    pass


class homekit(generic.FhemModule):

    controller: aiohomekit.Controller = None
    aiobrowser: AsyncServiceBrowser = None
    # controller which got the Bluetooth transport
    ble_controller: aiohomekit.Controller = None
    _controller_lock = asyncio.Lock()

    @staticmethod
    async def get_controller():
        async with homekit._controller_lock:
            if homekit.controller is None:
                await homekit._start_controller()
        return homekit.controller

    @staticmethod
    async def _start_controller():
        aio_zc = zeroconf.zeroconf.get_instance(
            logging.Logger("homekit")
        ).get_async_zeroconf()
        if homekit.aiobrowser is None:
            homekit.aiobrowser = AsyncServiceBrowser(
                aio_zc.zeroconf,
                HOMEKIT_SERVICES,
                handlers=[_on_service_state_change],
            )
        controller = aiohomekit.Controller(aio_zc)
        await controller.async_start()
        homekit.controller = controller

    @staticmethod
    async def start_ble(controller, logger):
        # aiohomekit only starts HAP-BLE if bleak was imported before it. Add it
        # on demand, setups with network devices only (e.g. Velux) don't need
        # a Bluetooth scan.
        async with homekit._controller_lock:
            if homekit.ble_controller is controller:
                return
            homekit.ble_controller = controller
            try:
                from .ble import SharedScanBleController

                await controller._async_register_backend(
                    SharedScanBleController(char_cache=controller._char_cache)
                )
            except Exception:
                logger.exception("HomeKit over Bluetooth not available")

    def __init__(self, logger):
        self._ready = asyncio.Event()
        self._setup_running = False
        self._owns_pairing = False
        self.pairing = None
        self._stop_listening = None
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)

    @property
    def ready(self):
        return self._ready

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": (
                    "Change interval, default is 60 seconds. Bluetooth devices "
                    "report changes on their own."
                ),
            },
            "pairing_data": {
                "default": "{}",
                "format": "json",
                "help": "Pairing data from HomeKit device",
            },
        }
        await self.set_attr_config(attr_config)

        self.set_config = {}
        await self.set_set_config(self.set_config)

        if len(args) != 5:
            return (
                "Usage: define velux_gateway fhempy homekit HOMEKITID|GW_NAME PIN|AID"
            )
        if args[4].find("-") > -1:
            # homekit pin found
            hash["HOMEKIT_ID"] = args[3]
            hash["HOMEKIT_PIN"] = args[4]
            # Attr calls (startup) must not start a second setup meanwhile
            self._setup_running = True
            self.create_async_task(
                self.setup_gateway_device(hash["HOMEKIT_ID"], args[4])
            )
        else:
            hash["HOMEKIT_GW"] = args[3]
            hash["HOMEKIT_AID"] = args[4]
            self.aid = int(args[4])
            self.create_async_task(self.setup_device(args[3], int(args[4])))

    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self._stop_listening is not None:
            self._stop_listening()
            self._stop_listening = None
        pairing = getattr(self, "pairing", None)
        self.pairing = None
        # accessory devices share the connection of their gateway
        if pairing is not None and self._owns_pairing:
            try:
                await pairing.close()
            except Exception:
                self.logger.exception("Failed to close HomeKit connection")

    async def set_attr_pairing_data(self, hash):
        # hash is the Attr message from FHEM, it doesn't carry the internals.
        # FHEM calls Attr on startup and when setup_gateway_device stores new
        # pairing data, only a changed pairing on a gateway needs a new setup.
        if "HOMEKIT_ID" not in self.hash or self._setup_running:
            return
        pairing = getattr(self, "pairing", None)
        if pairing is not None and pairing.pairing_data == self._attr_pairing_data:
            return
        self.create_async_task(
            self.setup_gateway_device(self.hash["HOMEKIT_ID"], self.hash["HOMEKIT_PIN"])
        )

    async def setup_gateway_device(self, homekitid, pin):
        self._setup_running = True
        try:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "state", "connecting", 1
            )
            await self._setup_gateway_device(homekitid, pin)
        except Exception as ex:
            self.logger.exception("Failed to set up HomeKit device")
            await fhem.readingsSingleUpdate(self.hash, "state", f"error: {ex}", 1)
        finally:
            self._setup_running = False

    async def _setup_gateway_device(self, homekitid, pin):
        controller = await homekit.get_controller()

        self.pairing = None
        if self._attr_pairing_data == {}:
            # not paired yet
            discovery = await self._wait_for_discovery(controller, homekitid)
            finish_pairing = await discovery.async_start_pairing(homekitid)
            self.pairing = await finish_pairing(pin)
            self._owns_pairing = True
            pairing_data = json.dumps(self.pairing.pairing_data)
            await fhem.CommandAttr(
                self.hash, f"{self.hash['NAME']} pairing_data {pairing_data}"
            )
        else:
            if self._attr_pairing_data.get("Connection") == "BLE":
                # aiohomekit needs the advertisement to connect
                await homekit.start_ble(controller, self.logger)
                await self._wait_for_discovery(controller, homekitid)
            self.pairing = controller.load_pairing(
                self._attr_pairing_data["AccessoryPairingID"],
                dict(self._attr_pairing_data),
            )
            self._owns_pairing = True

        name, accessories = await self._read_gateway()
        await fhem.readingsSingleUpdate(self.hash, "name", name, 1)

        for accessory in accessories:
            devname = utils.gen_fhemdev_name(
                f"hkdev_{self.hash['HOMEKIT_ID']}_{accessory['aid']}"
            )
            dev_ex = await fhem.checkIfDeviceExists(
                self.hash,
                "HOMEKIT_GW",
                self.hash["NAME"],
                "HOMEKIT_AID",
                str(accessory["aid"]),
            )
            if dev_ex:
                continue

            await fhem.CommandDefine(
                self.hash,
                f"{devname} fhempy homekit {self.hash['NAME']} {accessory['aid']}",
            )

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "ready", 1)
        self._ready.set()

    async def _wait_for_discovery(self, controller, homekitid):
        # The accessory (e.g. Homebridge) might start after FHEM. async_find
        # returns as soon as zeroconf announces it, so keep waiting for it.
        # aiohomekit keys Bluetooth devices by the lowercase id
        homekitid = homekitid.lower()
        while True:
            try:
                return await controller.async_find(homekitid)
            except AccessoryNotFoundError:
                # not announced via mDNS, it might be a Bluetooth device
                await homekit.start_ble(controller, self.logger)
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "waiting for device", 1
                )

    async def _read_gateway(self):
        # aiohomekit keeps reconnecting in the background and reconnects at
        # once when zeroconf announces the accessory. Wait for that connection
        # instead of failing when the accessory isn't up yet (FHEM start).
        connection = getattr(self.pairing, "connection", None)
        # only IP connections (_hap._tcp) have the reconnect loop
        ensure_connection = getattr(connection, "ensure_connection", None)
        while True:
            if ensure_connection is not None:
                await ensure_connection()
            try:
                name = await self.pairing.get_primary_name()
                accessories = await self.pairing.list_accessories_and_characteristics()
                return name, accessories
            except Exception as ex:
                if self._is_ble():
                    # out of range or asleep, try again later
                    self.logger.info(f"Waiting for HomeKit Bluetooth device: {ex}")
                    await fhem.readingsSingleUpdateIfChanged(
                        self.hash, "state", "waiting for device", 1
                    )
                    await asyncio.sleep(BLE_RETRY_INTERVAL)
                    continue
                if (
                    not isinstance(ex, AccessoryDisconnectedError)
                    or ensure_connection is None
                    or connection.is_connected
                ):
                    raise
                self.logger.info(f"Waiting for HomeKit device: {ex}")
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash, "state", "waiting for device", 1
                )

    async def setup_device(self, gw_device_name, aid):
        # load pairing data from homekit gateway
        gw_device = fhempy.getFhemPyDeviceByName(gw_device_name)
        await gw_device.ready.wait()
        # use the gateway connection, aiohomekit keeps one pairing per
        # accessory id for zeroconf updates (reconnect) anyway
        self.pairing = gw_device.pairing
        gw_name = await self.pairing.get_primary_name()
        await fhem.readingsSingleUpdateIfChanged(self.hash, "gw_name", gw_name, 1)

        for accessory in self.pairing.accessories:
            if accessory.aid == aid:
                for service in accessory.services:
                    for char in service.characteristics:
                        if "pw" in char.perms:
                            # char.type convert to string (position_target)
                            await self.char_to_set(char)
        await self.set_set_config(self.set_config)

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "ready", 1)

        if self._is_ble():
            await self.update_readings()
            await self.subscribe_events()
        else:
            self.create_async_task(self.update_readings_from_homekit())

    def _is_ble(self):
        return (
            self.pairing is not None
            and self.pairing.pairing_data.get("Connection") == "BLE"
        )

    async def subscribe_events(self):
        # Polling would drain the battery of a Bluetooth device. aiohomekit
        # reads the changed values when the state number in the advertisement
        # goes up and reports them as events.
        chars = []
        for accessory in self.pairing.accessories:
            if accessory.aid == self.aid:
                for service in accessory.services:
                    for char in service.characteristics:
                        if "ev" in char.perms:
                            chars.append((self.aid, char.iid))
        self._stop_listening = self.pairing.dispatcher_connect(self._on_events)
        await self.pairing.subscribe(chars)

    def _on_events(self, events):
        # events: {(aid, iid): {"value": value}}
        self.pairing.accessories.process_changes(events)
        if any(aid == self.aid for aid, _ in events):
            self.create_async_task(self.update_readings())

    async def update_readings_from_homekit(self):
        while True:
            try:
                await self.pairing.list_accessories_and_characteristics()
                await self.update_readings()
                self._errors.success()
            except Exception:
                self._errors.failed("Failed to update readings from HomeKit device")
            await asyncio.sleep(self._attr_interval)

    @staticmethod
    def _reading_name(char):
        return utils.gen_reading_name(char.description or char.type)

    async def update_readings(self):
        for accessory in self.pairing.accessories:
            if accessory.aid == self.aid:
                for service in accessory.services:
                    for char in service.characteristics:
                        if "pr" in char.perms:
                            await fhem.readingsSingleUpdateIfChanged(
                                self.hash,
                                self._reading_name(char),
                                char.value,
                                1,
                            )

    async def put_characteristic(self, char, value):
        aid = int(self.hash["HOMEKIT_AID"])
        result = await self.pairing.put_characteristics([(aid, char.iid, value)])
        # the response only lists characteristics on errors (status != 0)
        errors = {k: v for k, v in (result or {}).items() if v.get("status")}
        if errors:
            self.logger.error(
                f"HomeKit device rejected {self._reading_name(char)}: {errors}"
            )
            return
        if "pr" in char.perms:
            # don't wait for the next poll (interval) to show the new value
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, self._reading_name(char), value, 1
            )

    def set_value(self, hash, params):
        # new_value is already converted by its format (int, float, bool, str),
        # put in background so FHEM gets the reply at once
        self.create_async_task(
            self.put_characteristic(params["function_param"], params["new_value"])
        )

    async def char_to_set(self, char):
        if char.format in NUMBER_TYPES:
            self.set_config[self._reading_name(char)] = {
                "args": ["new_value"],
                "params": {
                    "new_value": {
                        "format": (
                            "float"
                            if char.format == CharacteristicFormats.float
                            else "int"
                        )
                    }
                },
                "function": "set_value",
                "function_param": char,
                "options": f"slider,{char.minValue},{char.minStep},{char.maxValue},1",
            }
        elif char.format == CharacteristicFormats.bool:
            self.set_config[self._reading_name(char)] = {
                "args": ["new_value"],
                "params": {"new_value": {"format": "bool"}},
                "function": "set_value",
                "function_param": char,
                "options": "on,off",
            }
        elif char.format == CharacteristicFormats.string:
            self.set_config[self._reading_name(char)] = {
                "args": ["new_value"],
                "params": {"new_value": {"format": "string"}},
                "function": "set_value",
                "function_param": char,
            }
