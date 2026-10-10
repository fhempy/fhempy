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
