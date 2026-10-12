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
