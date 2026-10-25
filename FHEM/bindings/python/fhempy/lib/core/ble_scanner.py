"""
One shared Bluetooth LE scan for all modules of this fhempy instance.

An adapter can only run one discovery at a time and every scan disturbs WiFi
and connected Bluetooth devices, especially on the combined chip of a
Raspberry Pi. Modules don't scan on their own, they register a callback and
get every advertisement:

    scanner = BleScanner.get_instance(logger)
    scanner.add_callback(callback)          # callback(device, advertisement)
    scanner.remove_callback(callback)

The scan runs continuously, passive (only listening) where BlueZ supports
advertisement monitors, active otherwise. A passive scan doesn't get the names
some devices only send on request, therefore a short active scan runs every
15 minutes. While a module connects to a device the scan pauses
(async with scanner.paused()). After the Bluetooth recovery had to reset an
adapter, or with mode "interval", it only scans 10s every 5 minutes.
"""

import asyncio
import contextlib
import time

from bleak import BleakScanner
from bleak.exc import BleakError

from .. import utils

MODE_CONTINUOUS = "continuous"
MODE_INTERVAL = "interval"

INTERVAL_SCAN_TIME = 10
DEFAULT_INTERVAL = 300
ACTIVE_REFRESH = 900
# back to continuous scanning after a recovery
RECOVERY_FALLBACK = 3600
NO_ADAPTER_RETRY = 600
# devices seen within this time are found without scanning again
RECENT_MAX_AGE = 60


def _passive_args():
    """BlueZ advertisement monitor patterns matching (nearly) all devices."""
    from bleak.assigned_numbers import AdvertisementDataType
    from bleak.args.bluez import OrPattern

    return {
        "or_patterns": [
            OrPattern(0, AdvertisementDataType.FLAGS, bytes([flags]))
            for flags in (0x02, 0x06, 0x1A)
        ]
    }


class BleScanner:
    instance: "BleScanner" = None

    @staticmethod
    def get_instance(logger) -> "BleScanner":
        if BleScanner.instance is None:
            BleScanner.instance = BleScanner(logger)
        return BleScanner.instance

    @staticmethod
    def running_instance() -> "BleScanner":
        """The scanner if a module uses it, None otherwise."""
        scanner = BleScanner.instance
        if scanner is not None and scanner._callbacks:
            return scanner
        return None

    def __init__(self, logger):
        self.logger = logger
        self._callbacks = []
        self._recent = {}
        self._task = None
        self._pause_count = 0
        self._changed = asyncio.Event()
        self._mode = MODE_CONTINUOUS
        self._interval = DEFAULT_INTERVAL
        self._fallback_until = 0
        self._passive_supported = True
        self._last_active = 0
        self._errors = utils.ErrorLogger(logger)
        self.scanning = ""

    # --- API for modules ---

    def add_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="ble_scanner")

    def remove_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
        if not self._callbacks and self._task is not None:
            self._task.cancel()
            self._task = None

    def set_mode(self, mode, interval=DEFAULT_INTERVAL):
        self._mode = mode
        self._interval = max(INTERVAL_SCAN_TIME, interval)
        self._changed.set()

    def recent_device(self, address, max_age=RECENT_MAX_AGE):
        """(BLEDevice, rssi) seen within max_age seconds, otherwise None."""
        found = self._recent.get(address.upper())
        if found is None or time.monotonic() - found[2] > max_age:
            return None
        return found[0], found[1]

    @contextlib.asynccontextmanager
    async def paused(self):
        """Stops the scan while connecting, some adapters can't do both."""
        self._pause_count += 1
        self._changed.set()
        try:
            yield
        finally:
            self._pause_count -= 1
            self._changed.set()

    def adapter_recovered(self):
        """The Bluetooth recovery had to reset an adapter, scan less."""
        self._fallback_until = time.monotonic() + RECOVERY_FALLBACK
        self._changed.set()

    @property
    def interval(self):
        return self._interval

    @property
    def effective_mode(self):
        if self._mode == MODE_INTERVAL or time.monotonic() < self._fallback_until:
            return MODE_INTERVAL
        return MODE_CONTINUOUS

    # --- scanning ---

    def _detection(self, device, advertisement):
        self._recent[device.address.upper()] = (
            device,
            advertisement.rssi,
            time.monotonic(),
        )
        for callback in list(self._callbacks):
            try:
                callback(device, advertisement)
            except Exception:
                self.logger.exception("Failed to handle Bluetooth advertisement")

    def _cleanup_recent(self):
        limit = time.monotonic() - 10 * RECENT_MAX_AGE
        for address in [a for a, v in self._recent.items() if v[2] < limit]:
            del self._recent[address]

    async def _wait_changed(self, timeout):
        """Waits for a change (pause, mode) or the timeout, the caller checks
        the state afterwards. A change set before waiting isn't lost."""
        try:
            await asyncio.wait_for(self._changed.wait(), max(0, timeout))
        except asyncio.TimeoutError:
            pass
        self._changed.clear()

    async def _run(self):
        while True:
            try:
                self._cleanup_recent()
                if self._pause_count:
                    self.scanning = "paused"
                    await self._wait_changed(30)
                    continue
                if self.effective_mode == MODE_INTERVAL:
                    await self._scan(active=True, duration=INTERVAL_SCAN_TIME)
                    self.scanning = f"every {self._interval}s"
                    await self._wait_changed(self._interval)
                    continue
                if not self._passive_supported:
                    await self._scan(active=True, duration=ACTIVE_REFRESH)
                elif time.monotonic() - self._last_active > ACTIVE_REFRESH:
                    # names of some devices only come with an active scan
                    await self._scan(active=True, duration=INTERVAL_SCAN_TIME)
                else:
                    await self._scan(active=False, duration=ACTIVE_REFRESH)
            except asyncio.CancelledError:
                self.scanning = ""
                raise
            except Exception as exc:
                if "No Bluetooth adapters" in str(exc) or "not found" in str(exc):
                    self.scanning = "no adapter"
                else:
                    self.scanning = "failed"
                self._errors.failed(
                    f"Bluetooth scan failed, retry in {NO_ADAPTER_RETRY}s"
                )
                await self._wait_changed(NO_ADAPTER_RETRY)

    async def _scan(self, active, duration):
        """Scans until duration is over, the mode changes or a pause starts."""
        if active:
            scanner = BleakScanner(self._detection, scanning_mode="active")
        else:
            try:
                scanner = BleakScanner(
                    self._detection, scanning_mode="passive", bluez=_passive_args()
                )
            except (BleakError, ImportError, ValueError):
                self._passive_supported = False
                return
        mode = self.effective_mode
        try:
            await scanner.start()
        except BleakError as exc:
            if not active:
                # e.g. BlueZ without --experimental or an old kernel
                self.logger.info(f"Passive Bluetooth scan not possible ({exc}), scan active")
                self._passive_supported = False
                return
            raise
        self.scanning = "active" if active else "passive"
        self._errors.success()
        if active:
            self._last_active = time.monotonic()
        try:
            end = time.monotonic() + duration
            while (
                time.monotonic() < end
                and not self._pause_count
                and self.effective_mode == mode
            ):
                await self._wait_changed(end - time.monotonic())
        finally:
            try:
                await scanner.stop()
            except Exception:
                self.logger.debug("Failed to stop Bluetooth scan", exc_info=True)


def paused():
    """Pauses the shared scan if it runs, for connecting to a device."""
    scanner = BleScanner.running_instance()
    if scanner is None:
        return contextlib.nullcontext()
    return scanner.paused()


def seen_by(device, adapter):
    """The device was received by this adapter (e.g. hci0), None: any."""
    if not adapter:
        return True
    details = device.details if isinstance(device.details, dict) else {}
    return f"/{adapter}/" in str(details.get("path", ""))
