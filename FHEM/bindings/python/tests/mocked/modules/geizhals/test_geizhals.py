import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

PRICE_HISTORY = {
    "meta": {"last_formatted": "today", "current_best": 80, "max": 90, "min": 70}
}


class FakeResponse:
    def __init__(self, status, text="", json=None):
        self.status = status
        self._text = text
        self._json = json

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def text(self):
        return self._text

    async def json(self):
        return self._json


def fake_session(page_status, page_html=""):
    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def get(self, url, headers=None):
            return FakeResponse(page_status, text=page_html)

        def post(self, url, headers=None, json=None):
            return FakeResponse(200, json=PRICE_HISTORY)

    return FakeSession


async def run_update_loop(mocker, page_status, page_html=""):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("geizhals")
    from fhempy.lib.geizhals import geizhals as gh_module

    mock_fhem.readings.pop("testgh", None)
    device = gh_module.geizhals(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        {"NAME": "testgh", "FHEMPYTYPE": "geizhals"},
        ["testgh", "fhempy", "geizhals", "https://geizhals.at/pi-5-a3065178.html"],
        {},
    )
    mocker.patch.object(
        gh_module.aiohttp, "ClientSession", fake_session(page_status, page_html)
    )

    async def stop(sec):
        raise StopAsyncIteration

    mocker.patch.object(gh_module.asyncio, "sleep", stop)
    with pytest.raises(StopAsyncIteration):
        await device.update_loop()
    return mock_fhem.readings["testgh"]


@pytest.mark.asyncio
async def test_blocked_product_page_still_updates_price(mocker, caplog):
    readings = await run_update_loop(mocker, 403)

    assert readings["current_price_euro"] == 80
    assert "store" not in readings
    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]


@pytest.mark.asyncio
async def test_product_page_readings(mocker):
    html = (
        '<h1 class="variant__header__headline">Raspberry Pi 5</h1>'
        '<div id="offer__0"><div class="merchant__logo-caption"> Shop </div>'
        '<div class="offer__delivery-time">lagernd</div></div>'
    )
    readings = await run_update_loop(mocker, 200, html)

    assert readings["store"] == "Shop"
    assert readings["store_availability"] == "lagernd"
    assert "image" not in readings
