import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_listener_and_search_use_library_arguments(mocker):
    # wrong keyword arguments broke the advertisements listener and search
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("discover_upnp")
    from fhempy.lib.core import ssdp as ssdp_module

    listener = mocker.patch.object(
        ssdp_module, "SsdpAdvertisementListener", autospec=True
    )
    search = mocker.patch.object(ssdp_module, "async_ssdp_search", autospec=True)
    mocker.patch.object(ssdp_module, "ClientSession")
    mocker.patch.object(ssdp_module.ssdp, "_ssdp__instance", None)
    instance = ssdp_module.ssdp.getInstance(logging.getLogger(__name__))

    await instance.advertisements()
    await instance.search_once()

    listener.assert_called_once()
    listener.return_value.async_start.assert_awaited_once()
    search.assert_awaited_once()
