import logging
from types import SimpleNamespace

import pytest
import pytest_asyncio

from fhempy.lib.autodiscovery import residents
from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest_asyncio.fixture
async def ble_scanner():
    # bleak is installed with the module, not with fhempy
    await check_and_install_dependencies("autodiscovery")
    from fhempy.lib.core import ble_scanner

    return ble_scanner


def device(address, path=""):
    return SimpleNamespace(address=address, name="", details={"path": path})


def advertisement(rssi, name=""):
    return SimpleNamespace(rssi=rssi, local_name=name)


@pytest.mark.asyncio
async def test_recent_device(ble_scanner):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    dev = device("aa:bb:cc:dd:ee:ff")
    scanner._detection(dev, advertisement(-50))
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF") == (dev, -50)
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF", max_age=-1) is None
    assert scanner.recent_device("11:22:33:44:55:66") is None


@pytest.mark.asyncio
async def test_paused(ble_scanner):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    async with scanner.paused():
        async with scanner.paused():
            assert scanner._pause_count == 2
        assert scanner._pause_count == 1
    assert scanner._pause_count == 0
    # nobody uses the scanner: pausing does nothing
    async with ble_scanner.paused():
        pass


@pytest.mark.asyncio
async def test_seen_by(ble_scanner):
    dev = device("AA", "/org/bluez/hci1/dev_AA")
    assert ble_scanner.seen_by(dev, None)
    assert ble_scanner.seen_by(dev, "hci1")
    assert not ble_scanner.seen_by(dev, "hci0")


@pytest.mark.asyncio
async def test_interval_mode_after_adapter_recovery(ble_scanner):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    assert scanner.effective_mode == ble_scanner.MODE_CONTINUOUS
    scanner.adapter_recovered()
    assert scanner.effective_mode == ble_scanner.MODE_INTERVAL


def test_private_mac():
    assert residents.is_private_mac("da:a1:19:00:00:01")
    assert not residents.is_private_mac("00:1a:11:00:00:01")
    assert not residents.is_private_mac("")


class FakeScanner:
    def __init__(self, adverts):
        self.adverts = adverts

    def add_callback(self, callback):
        for address, rssi in self.adverts:
            callback(device(address), advertisement(rssi, "Tag"))

    def remove_callback(self, callback):
        return


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adverts,expected",
    [
        ([("AA", -40), ("BB", -70), ("AA", -45)], "AA"),
        # two tags next to the Pi: unclear which one
        ([("AA", -40), ("BB", -45)], None),
        # too far away
        ([("AA", -75)], None),
    ],
)
async def test_find_tag(mocker, adverts, expected):
    async def used(hash):
        return set()

    mocker.patch.object(residents, "used_addresses", side_effect=used)
    tag = await residents.find_tag({}, FakeScanner(adverts), seconds=0)
    assert (tag and tag["address"]) == expected
