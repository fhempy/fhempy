import asyncio
import logging
import threading
import time

import pytest
import pytest_asyncio

from fhempy.lib.pkg_installer import check_and_install_dependencies


@pytest_asyncio.fixture
async def blemonitor(mocker):
    # janus, aioblescan and bleparser are installed with the module
    await check_and_install_dependencies("ble_monitor")
    from fhempy.lib.ble_monitor import blemonitor

    started = []

    class FakeThread:
        def __init__(self, logger, config, dataqueue):
            started.append(threading.get_ident())
            self.alive = False

        def start(self):
            self.alive = True

        def is_alive(self):
            return self.alive

        def join(self):
            self.alive = False

    mocker.patch.object(blemonitor, "HCIdump", FakeThread)
    mocker.patch.object(blemonitor, "RESTART_DELAY", 0.05)
    monitor = blemonitor.BLEmonitor(logging.getLogger("test"))
    yield monitor, started
    monitor.task_measuring.cancel()
    monitor.task_tracker.cancel()


@pytest.mark.asyncio
async def test_many_restarts_start_the_scan_once(blemonitor):
    monitor, started = blemonitor
    for _ in range(10):
        monitor.restart()
        await asyncio.sleep(0.01)
    assert started == []
    await asyncio.wait_for(monitor._restart_task, 2)
    assert len(started) == 1
    # stop/start (joins the old thread) doesn't run on the event loop
    assert started[0] != threading.get_ident()


@pytest.mark.asyncio
async def test_restart_requested_while_restarting_runs_again(blemonitor, mocker):
    monitor, started = blemonitor
    original = monitor._restart_now

    def restart_now():
        original()
        if len(started) == 1:
            # a device registered while the old thread was joined
            monitor._restart_requested = time.monotonic()

    mocker.patch.object(monitor, "_restart_now", restart_now)
    monitor.restart()
    await asyncio.wait_for(monitor._restart_task, 5)
    assert len(started) == 2
