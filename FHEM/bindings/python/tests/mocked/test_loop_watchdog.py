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
    watchdog._running_since = 100.0
    watchdog.check(100.3)
    assert caplog.records == []
    watchdog.check(101.0)
    watchdog.check(102.0)
    assert len(caplog.records) == 1
    assert "Blocking code" in caplog.records[0].getMessage()
    # recovered
    watchdog._running_since = None
    watchdog.finished(100.0, 3.0)
    assert caplog.records[-1].getMessage() == "Event loop was blocked for 3000ms"
    # second blockade within LOG_INTERVAL: logged, without stack
    watchdog._running_since = 104.0
    watchdog.check(104.6)
    assert len(caplog.records) == 3
    assert "Blocking code" not in caplog.records[-1].getMessage()


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


@pytest.mark.asyncio
async def test_test_guard_does_not_count_imports(monkeypatch):
    from . import conftest

    real_import = conftest._original_import

    def slow_import(*args, **kwargs):
        time.sleep(conftest.BLOCK_THRESHOLD + 0.1)
        return real_import(*args, **kwargs)

    monkeypatch.setattr(conftest, "_original_import", slow_import)
    conftest._blocked.clear()
    import json  # noqa: F401

    monkeypatch.setattr(conftest, "_original_import", real_import)
    await asyncio.sleep(0)
    assert conftest._blocked == []


@pytest.mark.asyncio
async def test_idle_loop_is_not_woken(monkeypatch):
    # the former heartbeat woke the loop 10 times per second, this was
    # fhempy's whole idle CPU usage
    loop = asyncio.get_running_loop()
    watchdog = LoopWatchdog(loop, threshold=0.2, interval=0.05)
    watchdog.start()
    try:
        await asyncio.sleep(0)
        before = len(loop._scheduled) + len(loop._ready)
        await asyncio.sleep(0.3)
        # only the sleep of this test is scheduled
        assert len(loop._scheduled) + len(loop._ready) <= before + 1
    finally:
        watchdog.stop()


@pytest.mark.asyncio
@pytest.mark.allow_blocking
@pytest.mark.parametrize("seconds", [0.21, 0.3, 0.45])
async def test_every_blockade_above_threshold_is_logged_with_module(
    caplog, monkeypatch, seconds
):
    # threshold 0.2 corresponds to 0.5 s in production
    monkeypatch.setattr(loop_watchdog, "LOG_INTERVAL", 0)
    caplog.set_level(logging.WARNING, logger="fhempy.lib.core.loop_watchdog")
    watchdog = LoopWatchdog(asyncio.get_running_loop(), threshold=0.2, interval=0.1)
    watchdog.start()
    try:
        await asyncio.sleep(0.03)
        fake_block(seconds)
        await asyncio.sleep(0.15)
    finally:
        watchdog.stop()
    messages = [r.getMessage() for r in caplog.records]
    assert len(messages) >= 1
    assert all("in fakemod" in m or m.startswith("Event loop was blocked for") for m in messages)
    assert any("in fakemod" in m for m in messages)


def test_short_callbacks_are_not_logged(caplog):
    caplog.set_level(logging.WARNING, logger="fhempy.lib.core.loop_watchdog")
    watchdog = LoopWatchdog(None, threshold=0.5)
    watchdog._running_since = 100.0
    watchdog.check(100.1)
    assert caplog.records == []
