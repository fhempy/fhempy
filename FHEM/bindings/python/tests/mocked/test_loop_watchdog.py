import asyncio
import logging
import os
import time

import pytest

from fhempy.lib.core import loop_watchdog
from fhempy.lib.core.loop_watchdog import LoopWatchdog

# a blocking function which looks like it belongs to a fhempy module
FAKE_MODULE_FILE = os.path.join(os.sep, "x", "fhempy", "lib", "fakemod", "fakemod.py")
_namespace = {"time": time}
exec(
    compile("def block(seconds):\n    time.sleep(seconds)\n", FAKE_MODULE_FILE, "exec"),
    _namespace,
)
fake_block = _namespace["block"]


@pytest.mark.asyncio
@pytest.mark.allow_blocking
async def test_blocked_loop_is_logged_with_module(caplog, monkeypatch):
    monkeypatch.setattr(loop_watchdog, "LOG_INTERVAL", 0)
    caplog.set_level(logging.WARNING, logger="fhempy.lib.core.loop_watchdog")
    watchdog = LoopWatchdog(asyncio.get_running_loop(), threshold=0.2, interval=0.05)
    watchdog.start()
    try:
        await asyncio.sleep(0.2)
        fake_block(0.6)
        await asyncio.sleep(0.3)
    finally:
        watchdog.stop()

    messages = [r.getMessage() for r in caplog.records]
    blocked = [m for m in messages if m.startswith("Event loop blocked")]
    assert len(blocked) == 1
    assert "in fakemod" in blocked[0]
    assert "fakemod.py" in blocked[0]
    durations = [m for m in messages if m.startswith("Event loop was blocked for")]
    assert len(durations) == 1
    assert int(durations[0].split()[-1][:-2]) >= 400


@pytest.mark.asyncio
async def test_responsive_loop_logs_nothing(caplog):
    caplog.set_level(logging.WARNING, logger="fhempy.lib.core.loop_watchdog")
    watchdog = LoopWatchdog(asyncio.get_running_loop(), threshold=0.2, interval=0.05)
    watchdog.start()
    try:
        for _ in range(10):
            await asyncio.sleep(0.03)
    finally:
        watchdog.stop()
    assert caplog.records == []


def test_check_logs_once_per_blockade(caplog, monkeypatch):
    monkeypatch.setattr(loop_watchdog, "LOG_INTERVAL", 60)
    caplog.set_level(logging.WARNING, logger="fhempy.lib.core.loop_watchdog")
    watchdog = LoopWatchdog(None, threshold=0.5)
    watchdog._loop_thread_id = __import__("threading").get_ident()
    watchdog._last_beat = 100.0
    watchdog.check(101.0)
    watchdog.check(102.0)
    assert len(caplog.records) == 1
    # recovered
    watchdog._last_beat = 103.0
    watchdog.check(103.1)
    assert caplog.records[-1].getMessage() == "Event loop was blocked for 3000ms"
    # second blockade within LOG_INTERVAL is not logged again
    watchdog.check(104.0)
    watchdog._last_beat = 105.0
    watchdog.check(105.1)
    assert len(caplog.records) == 2


@pytest.mark.asyncio
@pytest.mark.allow_blocking
async def test_blocking_callback_is_detected_by_test_guard():
    from . import conftest

    conftest._blocked.clear()
    fake_block(conftest.BLOCK_THRESHOLD + 0.1)
    # the blocking step of this test ends with the next await
    await asyncio.sleep(0)
    assert len(conftest._blocked) == 1
    assert "test_blocking_callback_is_detected_by_test_guard" in conftest._blocked[0][1]
