import logging

import pytest
import pytest_asyncio
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

NAME = "testbbq"


@pytest_asyncio.fixture
async def chefbbq(mocker):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("chefbbq")
    from fhempy.lib.chefbbq import chefbbq

    mock_fhem.readings.pop(NAME, None)
    module = chefbbq.chefbbq(logging.getLogger(__name__))
    module.hash = {"NAME": NAME}
    return module


def frame(payload):
    from fhempy.lib.chefbbq import chefbbq

    pkt = bytearray([0xCC, 0xDD, len(payload) + 4]) + bytearray(payload)
    pkt.append(chefbbq._xor(pkt))
    return bytes(pkt)


def test_command_frame():
    from fhempy.lib.chefbbq import chefbbq

    assert chefbbq._ccaa_pkt([0xFE, 0x01]) == bytes(
        [0xCC, 0xAA, 0x06, 0xFE, 0x01, 0x9F]
    )


@pytest.mark.asyncio
async def test_probe_notification(chefbbq):
    # probe 2: battery 158, 65.43 C, target 80 C, ambient 24.5 C
    payload = [0xC2, 158, 0, 0] + list((6543).to_bytes(2, "little"))
    payload += list((8000).to_bytes(2, "little")) + list((2450).to_bytes(2, "little"))
    payload += [0, 0]
    await chefbbq._on_notification(frame(payload))
    readings = mock_fhem.readings[NAME]
    assert readings["temperature_2"] == 65
    assert readings["target_2"] == 80
    assert readings["ambient_2"] == 24
    assert readings["battery_2"] == 100


@pytest.mark.asyncio
async def test_unplugged_probe_and_status(chefbbq):
    payload = [0xC1, 129, 0, 0, 0xFF, 0xFF, 0, 0, 0, 0, 0, 0]
    await chefbbq._on_notification(frame(payload))
    await chefbbq._on_notification(frame([0x0F, 0x01, 0x2C, 129, 0x02, 0x01]))
    readings = mock_fhem.readings[NAME]
    assert readings["temperature_1"] == "unplugged"
    assert readings["alarm"] == "on"
    assert readings["battery"] == 50


@pytest.mark.asyncio
async def test_invalid_checksum_ignored(chefbbq):
    data = bytearray(frame([0x0F, 0x01, 0x2C, 129, 0x02, 0x01]))
    data[-1] ^= 0xFF
    await chefbbq._on_notification(bytes(data))
    assert "alarm" not in mock_fhem.readings.get(NAME, {})


@pytest.mark.asyncio
async def test_adapter_options_list_adapters_and_proxies(chefbbq, mocker):
    import bluetooth_adapters

    from fhempy.lib.core import ble_proxy

    mocker.patch.object(
        bluetooth_adapters,
        "get_bluetooth_adapters",
        mocker.AsyncMock(return_value=["hci1", "hci0"]),
    )
    proxy = mocker.MagicMock(connectable=True, source="11:22")
    proxy.name = "Garden proxy"
    scan_only = mocker.MagicMock(connectable=False, source="33:44")
    scan_only.name = "SLZB"
    mocker.patch.object(ble_proxy, "proxies", return_value=[proxy, scan_only])
    assert (
        await chefbbq._adapter_options()
        == "auto,local,proxy,hci0,hci1,proxy:Garden_proxy"
    )
