import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

HUB_SERIAL = "11111111"
ZAPPI_SERIAL = "22222222"

ZAPPI_DATA = {
    "sno": int(ZAPPI_SERIAL),
    "fwv": "3560S3.142",
    "zmo": 3,
    "sta": 1,
    "pst": "A",
    "ectt1": "Grid",
    "ectp1": 100,
    "ectt2": "Generation",
    "ectp2": 200,
    "ectt3": "None",
    "ectp3": 0,
}


def mock_api(requests):
    async def get(self, url, data=None, oauth=False):
        requests.append(url)
        if url == "/cgi-jstatus-*":
            return [
                {"eddi": []},
                {"zappi": [ZAPPI_DATA]},
                {"harvi": []},
                {"asn": "s18.myenergi.net", "fwv": "3401S3.077"},
            ]
        if url == f"/cgi-jstatus-Z{ZAPPI_SERIAL}":
            return {"zappi": [ZAPPI_DATA]}
        # myenergi answers requests for unknown zappi serials without zappi key
        return {"status": "-14"}

    return get


async def define_device(mocker, serial, api_get):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("zappi")
    mocker.patch("pymyenergi.connection.Connection.get", api_get)
    from fhempy.lib.zappi.zappi import zappi

    mock_fhem.readings.pop("testzappi", None)
    testhash = {"NAME": "testzappi", "FHEMPYTYPE": "zappi"}
    device = zappi(logging.getLogger(__name__))
    # avoid starting the endless update loop
    mocker.patch.object(device, "update_zappi_data", mocker.AsyncMock())
    # run setup_connection in the test instead of a background task
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        testhash, ["testzappi", "fhempy", "zappi", serial, "apikey"], {}
    )
    await device.setup_connection()
    return device


@pytest.mark.asyncio
async def test_zappi_v1_with_external_hub(mocker):
    requests = []
    device = await define_device(mocker, HUB_SERIAL, mock_api(requests))

    assert device.zappi_box.serial_number == int(ZAPPI_SERIAL)
    assert f"/cgi-jstatus-Z{ZAPPI_SERIAL}" in requests
    assert f"/cgi-jstatus-Z{HUB_SERIAL}" not in requests
    assert mock_fhem.readings["testzappi"]["zappi_serial"] == int(ZAPPI_SERIAL)
    assert mock_fhem.readings["testzappi"]["state"] == "connected"


@pytest.mark.asyncio
async def test_zappi_v2_serial(mocker):
    requests = []
    device = await define_device(mocker, ZAPPI_SERIAL, mock_api(requests))

    assert device.zappi_box.serial_number == int(ZAPPI_SERIAL)
    assert mock_fhem.readings["testzappi"]["state"] == "connected"


@pytest.mark.asyncio
async def test_no_zappi_found(mocker):
    async def get(self, url, data=None, oauth=False):
        return [{"eddi": []}, {"asn": "s18.myenergi.net"}]

    device = await define_device(mocker, HUB_SERIAL, get)

    assert device.zappi_box is None
    assert mock_fhem.readings["testzappi"]["state"] == "no zappi found"
