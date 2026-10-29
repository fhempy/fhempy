import asyncio
from unittest.mock import MagicMock

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_controller_starts_with_zeroconf_browser(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")

    from zeroconf.asyncio import AsyncZeroconf

    from fhempy.lib.core import zeroconf
    from fhempy.lib.homekit.homekit import homekit

    azc = AsyncZeroconf(interfaces=["127.0.0.1"])
    instance = MagicMock()
    instance.get_async_zeroconf.return_value = azc
    mocker.patch.object(zeroconf.zeroconf, "get_instance", return_value=instance)
    mocker.patch.object(homekit, "controller", None)
    mocker.patch.object(homekit, "aiobrowser", None, create=True)
    try:
        # aiohomekit needs an AsyncServiceBrowser for the HAP service types
        controllers = await asyncio.gather(
            *[homekit.get_controller() for _ in range(3)]
        )
        assert controllers[0] is not None
        assert all(c is controllers[0] for c in controllers)
        await controllers[0].async_stop()
    finally:
        if homekit.aiobrowser is not None:
            await homekit.aiobrowser.async_cancel()
        await azc.async_close()


def test_service_state_handler_accepts_zeroconf_kwargs():
    from zeroconf import ServiceStateChange
    from zeroconf._services import Signal

    from fhempy.lib.homekit.homekit import _on_service_state_change

    # zeroconf fires handlers with keyword arguments only
    signal = Signal()
    signal.registration_interface.register_handler(_on_service_state_change)
    signal.fire(
        zeroconf=None,
        service_type="_hap._tcp.local.",
        name="test._hap._tcp.local.",
        state_change=ServiceStateChange.Added,
    )


@pytest.mark.asyncio
async def test_gateway_ready_and_attr_from_fhem(mocker):
    import json
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from fhempy.lib.homekit.homekit import homekit

    pairing_data = {"AccessoryPairingID": "0E:45:82:43:53:8E", "AccessoryIP": "x"}
    mock_fhem.readings.pop("testhkgw", None)
    mock_fhem.attributes["testhkgw"] = {"pairing_data": json.dumps(pairing_data)}
    pairing = MagicMock()
    pairing.pairing_data = pairing_data
    pairing.connection.ensure_connection = AsyncMock()
    pairing.get_primary_name = AsyncMock(return_value="Bridge")
    pairing.list_accessories_and_characteristics = AsyncMock(return_value=[])
    controller = MagicMock()
    controller.load_pairing.return_value = pairing
    mocker.patch.object(homekit, "get_controller", AsyncMock(return_value=controller))

    gw = homekit(logging.getLogger(__name__))
    testhash = {"NAME": "testhkgw", "FHEMPYTYPE": "homekit"}
    args = ["testhkgw", "fhempy", "homekit", "0E:45:82:43:53:8E", "123-45-678"]
    await gw.Define(testhash, args, {})
    # FHEM sends the attribute on startup while the setup runs, its hash is
    # the message without the internals (HOMEKIT_ID)
    attr_msg = {"NAME": "testhkgw", "function": "Attr"}
    attr_args = ["set", "testhkgw", "pairing_data", json.dumps(pairing_data)]
    await gw.Attr(attr_msg, attr_args, {})
    await asyncio.wait_for(gw.ready.wait(), 5)
    await gw.Attr(attr_msg, attr_args, {})
    await asyncio.sleep(0)

    assert mock_fhem.readings["testhkgw"]["state"] == "ready"
    assert mock_fhem.readings["testhkgw"]["name"] == "Bridge"
    assert controller.load_pairing.call_count == 1
    mock_fhem.attributes.pop("testhkgw", None)


def _gateway_pairing(pairing_data):
    from unittest.mock import AsyncMock

    pairing = MagicMock()
    pairing.pairing_data = pairing_data
    pairing.connection.is_connected = False
    pairing.connection.ensure_connection = AsyncMock()
    pairing.get_primary_name = AsyncMock(return_value="Bridge")
    pairing.list_accessories_and_characteristics = AsyncMock(return_value=[])
    return pairing


@pytest.mark.asyncio
async def test_gateway_waits_for_device_started_later(mocker):
    # issue 625: Homebridge starts after FHEM, the gateway must not stay in
    # error state but connect as soon as the accessory is reachable
    import json
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.exceptions import AccessoryDisconnectedError

    from fhempy.lib.homekit.homekit import homekit

    pairing_data = {"AccessoryPairingID": "0E:45:82:43:53:8F", "AccessoryIP": "x"}
    mock_fhem.readings.pop("testhkgw2", None)
    mock_fhem.attributes["testhkgw2"] = {"pairing_data": json.dumps(pairing_data)}
    pairing = _gateway_pairing(pairing_data)
    pairing.get_primary_name = AsyncMock(
        side_effect=[
            AccessoryDisconnectedError("Error while connecting to device"),
            "Bridge",
        ]
    )
    controller = MagicMock()
    controller.load_pairing.return_value = pairing
    mocker.patch.object(homekit, "get_controller", AsyncMock(return_value=controller))

    gw = homekit(logging.getLogger(__name__))
    testhash = {"NAME": "testhkgw2", "FHEMPYTYPE": "homekit"}
    args = ["testhkgw2", "fhempy", "homekit", "0E:45:82:43:53:8F", "123-45-678"]
    await gw.Define(testhash, args, {})
    await asyncio.wait_for(gw.ready.wait(), 5)

    assert mock_fhem.readings["testhkgw2"]["state"] == "ready"
    assert pairing.connection.ensure_connection.await_count == 2
    mock_fhem.attributes.pop("testhkgw2", None)


@pytest.mark.asyncio
async def test_gateway_error_when_connected_but_request_fails(mocker):
    import json
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.exceptions import AccessoryDisconnectedError

    from fhempy.lib.homekit.homekit import homekit

    pairing_data = {"AccessoryPairingID": "0E:45:82:43:53:90", "AccessoryIP": "x"}
    mock_fhem.readings.pop("testhkgw3", None)
    mock_fhem.attributes["testhkgw3"] = {"pairing_data": json.dumps(pairing_data)}
    pairing = _gateway_pairing(pairing_data)
    pairing.connection.is_connected = True
    pairing.get_primary_name = AsyncMock(side_effect=AccessoryDisconnectedError("x"))
    controller = MagicMock()
    controller.load_pairing.return_value = pairing
    mocker.patch.object(homekit, "get_controller", AsyncMock(return_value=controller))

    gw = homekit(logging.getLogger(__name__))
    testhash = {"NAME": "testhkgw3", "FHEMPYTYPE": "homekit"}
    args = ["testhkgw3", "fhempy", "homekit", "0E:45:82:43:53:90", "123-45-678"]
    await gw.Define(testhash, args, {})
    for _ in range(10):
        await asyncio.sleep(0)

    # no endless retry loop while connected
    assert mock_fhem.readings["testhkgw3"]["state"].startswith("error")
    assert pairing.get_primary_name.await_count == 1
    mock_fhem.attributes.pop("testhkgw3", None)


@pytest.mark.asyncio
async def test_unpaired_gateway_waits_for_discovery(mocker):
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.exceptions import AccessoryNotFoundError

    from fhempy.lib.homekit.homekit import homekit

    pairing_data = {"AccessoryPairingID": "0E:45:82:43:53:91", "AccessoryIP": "x"}
    mock_fhem.readings.pop("testhkgw4", None)
    mock_fhem.attributes.pop("testhkgw4", None)
    pairing = _gateway_pairing(pairing_data)
    discovery = MagicMock()
    discovery.async_start_pairing = AsyncMock(
        return_value=AsyncMock(return_value=pairing)
    )
    controller = MagicMock()
    controller.async_find = AsyncMock(
        side_effect=[AccessoryNotFoundError("not found"), discovery]
    )
    mocker.patch.object(homekit, "get_controller", AsyncMock(return_value=controller))

    gw = homekit(logging.getLogger(__name__))
    testhash = {"NAME": "testhkgw4", "FHEMPYTYPE": "homekit"}
    args = ["testhkgw4", "fhempy", "homekit", "0E:45:82:43:53:91", "123-45-678"]
    await gw.Define(testhash, args, {})
    await asyncio.wait_for(gw.ready.wait(), 5)

    assert controller.async_find.await_count == 2
    assert mock_fhem.readings["testhkgw4"]["state"] == "ready"


@pytest.mark.asyncio
async def test_accessory_uses_gateway_connection(mocker):
    import logging

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from fhempy.lib import fhem_pythonbinding
    from fhempy.lib.homekit.homekit import homekit

    gw = homekit(logging.getLogger(__name__))
    gw.pairing = _gateway_pairing({})
    gw.pairing.accessories = []
    gw.ready.set()
    mocker.patch.object(fhem_pythonbinding, "getFhemPyDeviceByName", return_value=gw)

    dev = homekit(logging.getLogger(__name__))
    dev.hash = {"NAME": "testhkdev", "FHEMPYTYPE": "homekit"}
    dev.set_config = {}
    mocker.patch.object(dev, "set_set_config")
    mocker.patch.object(dev, "create_async_task", side_effect=lambda coro: coro.close())
    await dev.setup_device("testhkgw", 1)
    assert dev.pairing is gw.pairing

    # deleting an accessory device must not close the gateway connection
    mocker.patch("fhempy.lib.generic.FhemModule.Undefine")
    await dev.Undefine(dev.hash)
    gw.pairing.close.assert_not_called()


@pytest.mark.asyncio
async def test_set_sends_value_and_updates_reading(mocker):
    # issue 684: "set ... on" sent False to the device
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.model.characteristics.characteristic_formats import (
        CharacteristicFormats,
    )

    from fhempy.lib.homekit.homekit import homekit

    def char(iid, description, fmt, value):
        c = MagicMock()
        c.iid = iid
        c.description = description
        c.type = description
        c.format = fmt
        c.perms = ["pr", "pw", "ev"]
        c.value = value
        c.minValue, c.minStep, c.maxValue = 0, 1, 100
        return c

    dev = homekit(logging.getLogger(__name__))
    dev.hash = {"NAME": "testhkset", "FHEMPYTYPE": "homekit", "HOMEKIT_AID": "2"}
    mock_fhem.readings.pop("testhkset", None)
    dev.pairing = MagicMock()
    dev.pairing.put_characteristics = AsyncMock(return_value={})
    dev.set_config = {}
    on = char(9, "On", CharacteristicFormats.bool, False)
    temp = char(11, "Target Temperature", CharacteristicFormats.float, 20.0)
    await dev.char_to_set(on)
    await dev.char_to_set(temp)
    # some devices send characteristics without description: use the type
    unnamed = char(12, None, CharacteristicFormats.int, 5)
    unnamed.type = "Custom-Level"
    await dev.char_to_set(unnamed)
    assert "custom_level" in dev.set_config
    await dev.set_set_config(dev.set_config)

    for args, expected in (
        (["testhkset", "on", "on"], (2, 9, True)),
        (["testhkset", "on", "off"], (2, 9, False)),
        (["testhkset", "target_temperature", "21.5"], (2, 11, 21.5)),
    ):
        await dev.Set(dev.hash, args, {})
        for _ in range(5):
            await asyncio.sleep(0)
        dev.pairing.put_characteristics.assert_awaited_with([expected])

    assert mock_fhem.readings["testhkset"]["on"] is False
    assert mock_fhem.readings["testhkset"]["target_temperature"] == 21.5

    # rejected by the device: reading stays
    dev.pairing.put_characteristics = AsyncMock(
        return_value={(2, 9): {"status": -70402, "description": "busy"}}
    )
    await dev.Set(dev.hash, ["testhkset", "on", "on"], {})
    for _ in range(5):
        await asyncio.sleep(0)
    assert mock_fhem.readings["testhkset"]["on"] is False


@pytest.mark.asyncio
async def test_failed_pair_verify_closes_connection(mocker):
    # a broken Homebridge accepts the connection but answers pair-verify with
    # garbage, every reconnect attempt must close its connection (#686)
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")

    from aiohomekit.controller.ip.connection import SecureHomeKitConnection

    import fhempy.lib.homekit.homekit  # noqa: F401 patches aiohomekit

    open_connections = set()

    async def handle(reader, writer):
        open_connections.add(writer)
        while await reader.read(4096):
            writer.write(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/pairing+tlv8\r\n"
                b"Content-Length: 0\r\n\r\n"
            )
            await writer.drain()
        open_connections.discard(writer)
        writer.close()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    pairing_data = {
        "AccessoryIP": "127.0.0.1",
        "AccessoryPort": port,
        "AccessoryPairingID": "AA:BB:CC:DD:EE:FF",
        "AccessoryLTPK": "00" * 32,
        "iOSPairingId": "fhempy",
        "iOSDeviceLTSK": "11" * 32,
        "iOSDeviceLTPK": "22" * 32,
    }
    connection = SecureHomeKitConnection(None, pairing_data)
    try:
        for _ in range(3):
            with pytest.raises(Exception):
                await connection._connect_once()
            await asyncio.sleep(0.1)
            assert connection.transport is None
            assert len(open_connections) == 0
    finally:
        await connection.close()
        server.close()
        await server.wait_closed()


HOMEKIT_ID = "0E:45:82:43:53:92"
# Apple data of an unpaired HomeKit device: type 0x06, length, status flags,
# device id, category (contact sensor), state number, config, version
HOMEKIT_ADV = bytes.fromhex("063101" "0e4582435392" "0a00" "0100" "0202")


@pytest.mark.asyncio
async def test_ble_controller_uses_shared_scan(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.characteristic_cache import CharacteristicCacheMemory
    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData

    from fhempy.lib.core.ble_scanner import BleScanner
    from fhempy.lib.homekit.ble import SharedScanBleController

    scanner = MagicMock()
    mocker.patch.object(BleScanner, "get_instance", return_value=scanner)
    controller = SharedScanBleController(char_cache=CharacteristicCacheMemory())
    await controller.async_start()
    callback = scanner.add_callback.call_args[0][0]

    device = BLEDevice("AA:BB:CC:DD:EE:FF", "Eve Window Guard", None)
    advertisement = AdvertisementData(
        local_name="Eve Window Guard",
        manufacturer_data={76: HOMEKIT_ADV},
        service_data={},
        service_uuids=[],
        tx_power=None,
        rssi=-60,
        platform_data=(),
    )
    callback(device, advertisement)
    discovery = await controller.async_find(HOMEKIT_ID.lower(), timeout=1)
    assert discovery.device.address == "AA:BB:CC:DD:EE:FF"

    await controller.async_stop()
    scanner.remove_callback.assert_called_once_with(callback)


@pytest.mark.asyncio
async def test_start_ble_only_once_per_controller(mocker):
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from fhempy.lib.homekit.ble import SharedScanBleController
    from fhempy.lib.homekit.homekit import homekit

    mocker.patch.object(homekit, "ble_controller", None)
    controller = MagicMock()
    controller._async_register_backend = AsyncMock()
    logger = logging.getLogger(__name__)
    await homekit.start_ble(controller, logger)
    await homekit.start_ble(controller, logger)
    controller._async_register_backend.assert_awaited_once()
    backend = controller._async_register_backend.call_args[0][0]
    assert isinstance(backend, SharedScanBleController)


@pytest.mark.asyncio
async def test_ble_gateway_waits_for_advertisement(mocker):
    import json
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.exceptions import AccessoryDisconnectedError

    from fhempy.lib.homekit import homekit as homekit_module
    from fhempy.lib.homekit.homekit import homekit

    pairing_data = {"AccessoryPairingID": HOMEKIT_ID, "Connection": "BLE"}
    mock_fhem.readings.pop("testhkble", None)
    mock_fhem.attributes["testhkble"] = {"pairing_data": json.dumps(pairing_data)}
    pairing = MagicMock(spec=["pairing_data", "get_primary_name", "close"])
    pairing.pairing_data = pairing_data
    pairing.list_accessories_and_characteristics = AsyncMock(return_value=[])
    # out of range at the first try
    pairing.get_primary_name = AsyncMock(
        side_effect=[AccessoryDisconnectedError("not reachable"), "Window"]
    )
    controller = MagicMock()
    controller.load_pairing.return_value = pairing
    controller.async_find = AsyncMock(return_value=MagicMock())
    mocker.patch.object(homekit, "get_controller", AsyncMock(return_value=controller))
    start_ble = mocker.patch.object(homekit, "start_ble", AsyncMock())
    mocker.patch.object(homekit_module, "BLE_RETRY_INTERVAL", 0)

    gw = homekit(logging.getLogger(__name__))
    testhash = {"NAME": "testhkble", "FHEMPYTYPE": "homekit"}
    args = ["testhkble", "fhempy", "homekit", HOMEKIT_ID, "123-45-678"]
    await gw.Define(testhash, args, {})
    await asyncio.wait_for(gw.ready.wait(), 5)

    start_ble.assert_awaited()
    # the advertisement is needed before the pairing can connect
    controller.async_find.assert_awaited_with(HOMEKIT_ID.lower())
    assert mock_fhem.readings["testhkble"]["state"] == "ready"
    assert mock_fhem.readings["testhkble"]["name"] == "Window"
    mock_fhem.attributes.pop("testhkble", None)


@pytest.mark.asyncio
async def test_ble_accessory_updates_readings_on_events(mocker):
    import logging
    from unittest.mock import AsyncMock

    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("homekit")
    from aiohomekit.model import Accessories

    from fhempy.lib import fhem_pythonbinding
    from fhempy.lib.homekit.homekit import homekit

    # contact sensor (window closed), iid 9 reports events
    accessories = Accessories.from_list(
        [
            {
                "aid": 1,
                "services": [
                    {
                        "iid": 8,
                        "type": "00000080-0000-1000-8000-0026BB765291",
                        "characteristics": [
                            {
                                "iid": 9,
                                "type": "0000006A-0000-1000-8000-0026BB765291",
                                "format": "uint8",
                                "perms": ["pr", "ev"],
                                "value": 0,
                            }
                        ],
                    }
                ],
            }
        ]
    )
    listeners = []
    gw = homekit(logging.getLogger(__name__))
    gw.pairing = MagicMock()
    gw.pairing.pairing_data = {"Connection": "BLE"}
    gw.pairing.accessories = accessories
    gw.pairing.get_primary_name = AsyncMock(return_value="Window")
    gw.pairing.subscribe = AsyncMock()
    gw.pairing.dispatcher_connect = MagicMock(
        side_effect=lambda cb: listeners.append(cb) or MagicMock()
    )
    gw.ready.set()
    mocker.patch.object(fhem_pythonbinding, "getFhemPyDeviceByName", return_value=gw)

    dev = homekit(logging.getLogger(__name__))
    dev.hash = {"NAME": "testhkbledev", "FHEMPYTYPE": "homekit"}
    dev.aid = 1
    dev.set_config = {}
    mock_fhem.readings.pop("testhkbledev", None)
    mocker.patch.object(dev, "set_set_config")
    polling = mocker.patch.object(dev, "update_readings_from_homekit")
    await dev.setup_device("testhkgw", 1)

    # no polling, it would drain the battery
    polling.assert_not_called()
    gw.pairing.subscribe.assert_awaited_once_with([(1, 9)])
    assert mock_fhem.readings["testhkbledev"]["contact_sensor_state"] == 0

    # window opened
    listeners[0]({(1, 9): {"value": 1}})
    for _ in range(5):
        await asyncio.sleep(0)
    assert mock_fhem.readings["testhkbledev"]["contact_sensor_state"] == 1

    mocker.patch("fhempy.lib.generic.FhemModule.Undefine")
    stop_listening = dev._stop_listening
    await dev.Undefine(dev.hash)
    stop_listening.assert_called_once()
