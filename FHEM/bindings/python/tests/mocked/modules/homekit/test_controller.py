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
