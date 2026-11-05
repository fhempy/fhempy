import asyncio
import logging
import threading

import pytest

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest.mark.asyncio
async def test_http_client_is_created_in_thread(mocker):
    await check_and_install_dependencies("prusalink")
    from fhempy.lib.prusalink import prusalink as module

    created_in = []

    class FakeClient:
        def __init__(self):
            created_in.append(threading.current_thread())

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    mocker.patch.object(module.httpx, "AsyncClient", FakeClient)
    mocker.patch.object(module.pyprusalink, "PrusaLink", mocker.MagicMock())
    device = module.prusalink(logging.getLogger("test"))
    device.url = "http://printer"
    device.username = "user"
    device.password = "pw"

    async def no_data():
        raise asyncio.CancelledError

    mocker.patch.object(device, "retrieve_data", no_data)
    with pytest.raises(asyncio.CancelledError):
        await device.update_loop()
    assert created_in and created_in[0] is not threading.main_thread()
