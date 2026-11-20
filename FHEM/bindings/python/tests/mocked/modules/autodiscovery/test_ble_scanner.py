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


@pytest.mark.asyncio
async def test_active_scan_if_passive_scan_fails(ble_scanner, mocker):
    # BlueZ without --experimental
    from bleak.exc import BleakError

    scanners = []

    class FakeBleakScanner:
        def __init__(self, callback, scanning_mode="active", bluez=None):
            self.mode = scanning_mode
            scanners.append(self)

        async def start(self):
            if self.mode == "passive":
                raise BleakError(
                    "passive scanning on Linux requires BlueZ >= 5.56 with "
                    "--experimental enabled and Linux kernel >= 5.10"
                )

        async def stop(self):
            return

    mocker.patch.object(ble_scanner, "BleakScanner", FakeBleakScanner)
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    await scanner._scan(active=False, duration=0)
    assert scanner._passive_supported is False
    await scanner._scan(active=True, duration=0)
    assert [s.mode for s in scanners] == ["passive", "active"]
    assert scanner.scanning == "active"


@pytest.mark.asyncio
async def test_passive_problem(ble_scanner, mocker):
    mocker.patch.object(ble_scanner.platform, "release", return_value="6.12.47")
    experimental = (
        "passive scanning on Linux requires BlueZ >= 5.56 with --experimental "
        "enabled and Linux kernel >= 5.10"
    )
    assert ble_scanner.passive_problem(experimental) == "experimental"
    assert ble_scanner.passive_problem("something else") == ""
    mocker.patch.object(ble_scanner.platform, "release", return_value="5.4.83-v7l+")
    assert ble_scanner.passive_problem(experimental) == "kernel"


@pytest.mark.asyncio
async def test_warning_and_passive_retry_after_bluez_fix(ble_scanner, mocker):
    from bleak.exc import BleakError

    mocker.patch.object(ble_scanner.platform, "release", return_value="6.12.47")
    experimental = {"on": False}

    class FakeBleakScanner:
        def __init__(self, callback, scanning_mode="active", bluez=None):
            self.mode = scanning_mode

        async def start(self):
            if self.mode == "passive" and not experimental["on"]:
                raise BleakError("requires BlueZ >= 5.56 with --experimental")

        async def stop(self):
            return

    mocker.patch.object(ble_scanner, "BleakScanner", FakeBleakScanner)
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    changes = []
    scanner.add_state_callback(lambda: changes.append(scanner.passive_problem))
    await scanner._scan(active=False, duration=0)
    assert scanner.passive_problem == "experimental"
    # the user ran the command, the next passive try works
    experimental["on"] = True
    scanner._passive_supported = True
    await scanner._scan(active=False, duration=0)
    assert scanner.passive_problem == ""
    assert changes == ["experimental", ""]


@pytest.mark.asyncio
async def test_busy_adapter_logs_error_without_traceback(ble_scanner, mocker, caplog):
    import asyncio

    from bleak.exc import BleakDBusError

    class BusyScanner:
        def __init__(self, callback, scanning_mode="active", bluez=None):
            pass

        async def start(self):
            raise BleakDBusError(
                "org.bluez.Error.InProgress", ["Operation already in progress"]
            )

        async def stop(self):
            return

    mocker.patch.object(ble_scanner, "BleakScanner", BusyScanner)
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    scanner.set_mode(ble_scanner.MODE_INTERVAL)
    waits = []

    async def wait_changed(timeout):
        waits.append(timeout)
        if len(waits) == 2:
            raise asyncio.CancelledError

    mocker.patch.object(scanner, "_wait_changed", wait_changed)
    with caplog.at_level(logging.DEBUG), pytest.raises(asyncio.CancelledError):
        await scanner._run()
    assert waits == [ble_scanner.BUSY_RETRY, ble_scanner.BUSY_RETRY]
    errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(errors) == 1
    assert errors[0].exc_info is None
    assert "busy" in errors[0].getMessage()
    assert scanner.scanning == "busy"


@pytest.mark.asyncio
async def test_additional_adapters_are_scanned_once(ble_scanner, mocker):
    """One scan per adapter, all callbacks share it. A failing additional
    adapter doesn't stop the scan of the default adapter."""
    started = []

    class FakeBleakScanner:
        def __init__(self, callback, scanning_mode="active", bluez=None, adapter=None):
            self.adapter = adapter
            self.mode = scanning_mode

        async def start(self):
            if self.adapter == "hci2":
                raise OSError("no such adapter")
            started.append((self.adapter, self.mode))

        async def stop(self):
            return

    mocker.patch.object(ble_scanner, "BleakScanner", FakeBleakScanner)
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    mocker.patch.object(scanner, "_run", mocker.AsyncMock())
    scanner.add_callback(lambda d, a: None)
    first, second, third = (lambda d, a: None), (lambda d, a: None), (lambda d, a: None)
    scanner.add_callback(first, adapter=1)
    scanner.add_callback(second, adapter="hci1")
    scanner.add_callback(third, adapter="hci2")
    # hci0 is the default adapter
    scanner.add_callback(lambda d, a: None, adapter="0")
    assert scanner.adapters == ["hci1", "hci2"]
    await scanner._scan(active=True, duration=0)
    assert started == [(None, "active"), ("hci1", "active")]
    scanner.remove_callback(first)
    assert scanner.adapters == ["hci1", "hci2"]
    scanner.remove_callback(second)
    scanner.remove_callback(third)
    assert scanner.adapters == []


@pytest.mark.asyncio
async def test_address_type(ble_scanner):
    random = SimpleNamespace(details={"props": {"AddressType": "random"}})
    public = SimpleNamespace(details={"props": {"AddressType": "public"}})
    proxy = SimpleNamespace(details=None)
    assert ble_scanner.address_type(random) == 1
    assert ble_scanner.address_type(public) == 0
    assert ble_scanner.address_type(proxy) == 0


@pytest.mark.asyncio
async def test_recent_device_per_adapter(ble_scanner):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    near = device("AA:BB:CC:DD:EE:FF", "/org/bluez/hci1/dev_AA_BB_CC_DD_EE_FF")
    far = device("AA:BB:CC:DD:EE:FF", "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF")
    scanner._detection(near, advertisement(-50))
    # the last advertisement doesn't hide the one of the other adapter
    scanner._detection(far, advertisement(-80))
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF", adapter="hci1") == (near, -50)
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF", adapter="hci0") == (far, -80)
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF", adapter="hci2") is None
    # without adapter: the best signal
    assert scanner.recent_device("AA:BB:CC:DD:EE:FF") == (near, -50)


@pytest.mark.asyncio
async def test_cleanup_recent_per_adapter(ble_scanner):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    scanner._detection(device("AA", "/org/bluez/hci0/dev_AA"), advertisement(-50))
    scanner._detection(device("AA", "/org/bluez/hci1/dev_AA"), advertisement(-60))
    scanner._detection(device("BB", "/org/bluez/hci0/dev_BB"), advertisement(-60))
    old = ble_scanner.time.monotonic() - 11 * ble_scanner.RECENT_MAX_AGE
    scanner._recent["AA"]["hci0"] = scanner._recent["AA"]["hci0"][:2] + (old,)
    scanner._recent["BB"]["hci0"] = scanner._recent["BB"]["hci0"][:2] + (old,)
    scanner._cleanup_recent()
    assert list(scanner._recent["AA"]) == ["hci1"]
    assert "BB" not in scanner._recent


@pytest.mark.asyncio
async def test_listens_on(ble_scanner, mocker):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    assert not scanner.listens_on("hci0")
    scanner._task = mocker.MagicMock(done=mocker.MagicMock(return_value=False))
    scanner._listening = {None, "hci1"}
    assert scanner.listens_on(None)
    assert scanner.listens_on("hci0")
    assert scanner.listens_on("hci1")
    assert not scanner.listens_on("hci2")
    scanner._pause_count = 1
    assert not scanner.listens_on("hci0")


@pytest.mark.asyncio
async def test_scans_adapter(ble_scanner, mocker):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    assert not scanner.scans_adapter("hci0")
    scanner._task = mocker.MagicMock(done=mocker.MagicMock(return_value=False))
    scanner._adapters = {print: "hci1"}
    assert scanner.scans_adapter("hci0")
    assert scanner.scans_adapter("hci1")
    assert not scanner.scans_adapter("hci2")


@pytest.mark.asyncio
async def test_wait_for_device(ble_scanner, mocker):
    import asyncio

    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    scanner._task = mocker.MagicMock(done=mocker.MagicMock(return_value=False))
    scanner._listening = {None, "hci1"}
    dev = device("AA:BB", "/org/bluez/hci1/dev_AA_BB")

    async def advertise():
        await asyncio.sleep(0.01)
        # another adapter: not what we wait for
        scanner._detection(
            device("AA:BB", "/org/bluez/hci0/dev_AA_BB"), advertisement(-90)
        )
        scanner._detection(dev, advertisement(-40))

    task = asyncio.create_task(advertise())
    found, quiet = await scanner.wait_for_device("aa:bb", adapter="hci1", timeout=1)
    await task
    assert found == (dev, -40)
    assert not quiet
    assert scanner._waiters == []


@pytest.mark.asyncio
async def test_wait_for_device_quiet_adapter(ble_scanner, mocker):
    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    scanner._task = mocker.MagicMock(done=mocker.MagicMock(return_value=False))
    scanner._listening = {None}
    found, quiet = await scanner.wait_for_device("AA:BB", timeout=0.01)
    assert found is None
    # the adapter received nothing at all
    assert quiet


@pytest.mark.asyncio
async def test_wait_for_device_other_devices_or_pause_not_quiet(ble_scanner, mocker):
    import asyncio

    scanner = ble_scanner.BleScanner(logging.getLogger(__name__))
    scanner._task = mocker.MagicMock(done=mocker.MagicMock(return_value=False))
    scanner._listening = {None}

    async def other_device():
        await asyncio.sleep(0.005)
        scanner._detection(
            device("CC:DD", "/org/bluez/hci0/dev_CC_DD"), advertisement(-60)
        )

    task = asyncio.create_task(other_device())
    found, quiet = await scanner.wait_for_device("AA:BB", timeout=0.05)
    await task
    assert found is None and not quiet

    async def pause():
        async with scanner.paused():
            await asyncio.sleep(0.005)

    task = asyncio.create_task(pause())
    found, quiet = await scanner.wait_for_device("AA:BB", timeout=0.05)
    await task
    # the scan paused meanwhile, that's no hint for a broken adapter
    assert found is None and not quiet


@pytest.mark.asyncio
async def test_adapter_of(ble_scanner):
    assert ble_scanner.adapter_of(device("AA", "/org/bluez/hci2/dev_AA")) == "hci2"
    assert ble_scanner.adapter_of(device("AA")) == "hci0"
    assert ble_scanner.adapter_name(None) == "hci0"
    assert ble_scanner.adapter_name("1") == "hci1"
