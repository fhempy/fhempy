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
import platform
import re
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
# try passive again, e.g. after BlueZ was restarted with --experimental
PASSIVE_RETRY = 3600

PASSIVE_NEEDS_EXPERIMENTAL = "experimental"
PASSIVE_NEEDS_KERNEL = "kernel"
# starts bluetoothd with --experimental, also after a reboot
EXPERIMENTAL_COMMAND = (
    'B="$(ls /usr/libexec/bluetooth/bluetoothd /usr/lib/bluetooth/bluetoothd '
    '2>/dev/null | head -n1)" && [ -n "$B" ] && '
    "sudo mkdir -p /etc/systemd/system/bluetooth.service.d && "
    "printf '[Service]\\nExecStart=\\nExecStart=%s --experimental\\n' \"$B\" | "
    "sudo tee /etc/systemd/system/bluetooth.service.d/fhempy-experimental.conf "
    ">/dev/null && sudo systemctl daemon-reload && sudo systemctl restart bluetooth"
)


def kernel_supports_passive(release=None):
    """Passive scans need Linux 5.10 or newer."""
    match = re.match(r"(\d+)\.(\d+)", release or platform.release())
    if not match:
        return True
    return (int(match.group(1)), int(match.group(2))) >= (5, 10)


def passive_problem(error):
    """Why a passive scan failed: PASSIVE_NEEDS_EXPERIMENTAL,
    PASSIVE_NEEDS_KERNEL or '' (unknown)."""
    if not kernel_supports_passive():
        return PASSIVE_NEEDS_KERNEL
    text = str(error)
    if "experimental" in text or "AdvertisementMonitor" in text:
        return PASSIVE_NEEDS_EXPERIMENTAL
    return ""


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
        self._passive_failed = 0
        self._last_active = 0
        # why the passive scan doesn't work, see passive_problem()
        self.passive_problem = ""
        self._passive_logged = False
        self._state_callbacks = []
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

    def add_state_callback(self, callback):
        """callback() is called when passive_problem changes"""
        if callback not in self._state_callbacks:
            self._state_callbacks.append(callback)

    def remove_state_callback(self, callback):
        if callback in self._state_callbacks:
            self._state_callbacks.remove(callback)

    def _set_passive_problem(self, problem):
        if problem == self.passive_problem:
            return
        self.passive_problem = problem
        for callback in list(self._state_callbacks):
            try:
                callback()
            except Exception:
                self.logger.exception("Failed to handle Bluetooth scan state")

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
                if (
                    not self._passive_supported
                    and time.monotonic() - self._passive_failed > PASSIVE_RETRY
                ):
                    self._passive_supported = True
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

    def _passive_failed_with(self, exc):
        self._passive_supported = False
        self._passive_failed = time.monotonic()
        problem = passive_problem(exc)
        if problem != self.passive_problem or not self._passive_logged:
            self._passive_logged = True
            if problem == PASSIVE_NEEDS_EXPERIMENTAL:
                self.logger.warning(
                    "BlueZ runs without --experimental, Bluetooth is scanned "
                    "actively. Run once to scan passively: " + EXPERIMENTAL_COMMAND
                )
            else:
                self.logger.info(
                    f"Passive Bluetooth scan not possible ({exc}), scan active"
                )
        self._set_passive_problem(problem)

    async def _scan(self, active, duration):
        """Scans until duration is over, the mode changes or a pause starts."""
        if active:
            scanner = BleakScanner(self._detection, scanning_mode="active")
        else:
            try:
                scanner = BleakScanner(
                    self._detection, scanning_mode="passive", bluez=_passive_args()
                )
            except (BleakError, ImportError, ValueError) as exc:
                self._passive_failed_with(exc)
                return
        mode = self.effective_mode
        try:
            await scanner.start()
        except BleakError as exc:
            if not active:
                # e.g. BlueZ without --experimental or an old kernel
                self._passive_failed_with(exc)
                return
            raise
        if not active:
            self._set_passive_problem("")
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
