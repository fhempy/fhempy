"""Detect a blocked asyncio event loop.

While the event loop hangs in synchronous code, fhempy can't answer FHEM.
FHEM waits for function replies (Set, Get, Attr, ...) and is frozen in the
meantime. A thread checks a heartbeat of the loop and logs where the loop
hangs, so the blocking module can be found.
"""

import logging
import os
import sys
import threading
import time
import traceback

logger = logging.getLogger(__name__)

THRESHOLD = 0.5
INTERVAL = 0.1
# log the stack of a blocked loop at most this often
LOG_INTERVAL = 60
STACK_LIMIT = 8


def _module_of(stack):
    """Name of the innermost fhempy module in the stack, e.g. tuya_cloud."""
    marker = os.sep + os.path.join("fhempy", "lib") + os.sep
    for frame in reversed(stack):
        idx = frame.filename.rfind(marker)
        if idx == -1:
            continue
        parts = frame.filename[idx + len(marker) :].split(os.sep)
        if len(parts) > 1 and parts[0] != "core":
            return parts[0]
    return None


class LoopWatchdog:
    def __init__(self, loop, threshold=THRESHOLD, interval=INTERVAL):
        self._loop = loop
        self._threshold = threshold
        self._interval = interval
        self._last_beat = time.monotonic()
        self._loop_thread_id = None
        self._stop = threading.Event()
        self._thread = None
        self._blocked_since = None
        self._last_log = None
        # the current blockade was logged, log its duration when it ends
        self._logged = False

    def start(self):
        self._loop_thread_id = threading.get_ident()
        self._last_beat = time.monotonic()
        self._loop.call_soon(self._beat)
        self._thread = threading.Thread(
            target=self._watch, name="fhempy_loop_watchdog", daemon=True
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _beat(self):
        self._last_beat = time.monotonic()
        if not self._stop.is_set():
            self._loop.call_later(self._interval, self._beat)

    def _watch(self):
        while not self._stop.wait(self._interval):
            self.check(time.monotonic())

    def check(self, now):
        lag = now - self._last_beat
        if lag > self._threshold:
            if self._blocked_since is None:
                self._blocked_since = self._last_beat
                self._report_blocked(lag)
        elif self._blocked_since is not None:
            duration = (self._last_beat - self._blocked_since) * 1000
            self._blocked_since = None
            if self._logged:
                self._logged = False
                logger.warning(f"Event loop was blocked for {duration:.0f}ms")

    def _report_blocked(self, lag):
        now = time.monotonic()
        if self._last_log is not None and now - self._last_log < LOG_INTERVAL:
            return
        frame = sys._current_frames().get(self._loop_thread_id)
        if frame is None:
            return
        stack = traceback.extract_stack(frame)
        module = _module_of(stack)
        self._last_log = now
        self._logged = True
        where = f" in {module}" if module else ""
        logger.warning(
            f"Event loop blocked for >{lag * 1000:.0f}ms{where}, FHEM waits for "
            "fhempy meanwhile. Blocking code:\n"
            + "".join(traceback.format_list(stack[-STACK_LIMIT:]))
        )
