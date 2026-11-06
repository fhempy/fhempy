"""Detect a blocked asyncio event loop.

While the event loop hangs in synchronous code, fhempy can't answer FHEM.
FHEM waits for function replies (Set, Get, Attr, ...) and is frozen in the
meantime. Every callback of the loop is timed, so each blockade of at least
THRESHOLD is logged with its exact duration. A thread looks at the running
callback every POLL seconds without waking the loop: it records the stack of
a callback running longer than POLL and logs it right away after THRESHOLD,
so the blocking module is found even if the loop never recovers. A blockade
>= THRESHOLD still runs >= POLL at one of the thread's checks, so its stack
is always known. The former heartbeat woke the loop 10 times per second, on a
Raspberry Pi this was the whole idle CPU usage of fhempy.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import traceback

logger = logging.getLogger(__name__)

THRESHOLD = 0.5
# the thread checks the running callback this often, POLL <= THRESHOLD / 2
POLL = 0.25
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
    def __init__(self, loop, threshold=THRESHOLD, interval=POLL):
        self._loop = loop
        self._threshold = threshold
        self._interval = min(interval, threshold / 2)
        self._loop_thread_id = None
        self._stop = threading.Event()
        self._thread = None
        self._original_run = None
        # start time of the callback which runs right now, None between callbacks
        self._running_since = None
        # (start of the callback, stack) seen by the thread
        self._seen = None
        # start of the callback whose blockade was already logged by the thread
        self._logged_since = None
        self._last_log = None
        # called in the loop after a blockade: on_blocked(module, duration)
        self.on_blocked = None

    def start(self):
        self._loop_thread_id = threading.get_ident()
        self._install()
        self._thread = threading.Thread(
            target=self._watch, name="fhempy_loop_watchdog", daemon=True
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._original_run is not None:
            asyncio.events.Handle._run = self._original_run
            self._original_run = None

    def _install(self):
        original = asyncio.events.Handle._run
        self._original_run = original
        watchdog = self
        loop_thread = self._loop_thread_id
        monotonic = time.monotonic

        def _run(handle):
            if threading.get_ident() != loop_thread:
                # e.g. a module with its own loop in a thread
                return original(handle)
            start = monotonic()
            watchdog._running_since = start
            try:
                return original(handle)
            finally:
                watchdog._running_since = None
                duration = monotonic() - start
                if duration >= watchdog._threshold:
                    watchdog.finished(start, duration)

        asyncio.events.Handle._run = _run

    def _watch(self):
        while not self._stop.wait(self._interval):
            self.check(time.monotonic())

    def check(self, now):
        """Called by the thread, the loop keeps running meanwhile."""
        since = self._running_since
        if since is None:
            return
        lag = now - since
        if lag < self._interval:
            return
        if self._seen is None or self._seen[0] != since:
            frame = sys._current_frames().get(self._loop_thread_id)
            if frame is None:
                return
            self._seen = (since, traceback.extract_stack(frame))
        if lag >= self._threshold and self._logged_since != since:
            self._logged_since = since
            self._report(lag, self._seen[1], still_blocked=True)

    def finished(self, since, duration):
        """Called in the loop after a callback which ran >= threshold."""
        seen = self._seen
        stack = seen[1] if seen is not None and seen[0] == since else None
        if self._logged_since == since:
            logger.warning(f"Event loop was blocked for {duration * 1000:.0f}ms")
        else:
            self._report(duration, stack, still_blocked=False)
        if self.on_blocked is not None:
            try:
                self.on_blocked(_module_of(stack) if stack else None, duration)
            except Exception:
                logger.exception("Failed to handle the blocked event loop")

    def _report(self, duration, stack, still_blocked):
        module = _module_of(stack) if stack else None
        where = f" in {module}" if module else ""
        if still_blocked:
            text = f"Event loop blocked for >{duration * 1000:.0f}ms{where}"
        else:
            text = f"Event loop was blocked for {duration * 1000:.0f}ms{where}"
        now = time.monotonic()
        if stack and (self._last_log is None or now - self._last_log >= LOG_INTERVAL):
            # the stack at most once per LOG_INTERVAL, the duration always
            self._last_log = now
            logger.warning(
                f"{text}, FHEM waits for fhempy meanwhile. Blocking code:\n"
                + "".join(traceback.format_list(stack[-STACK_LIMIT:]))
            )
        else:
            logger.warning(f"{text}, FHEM waits for fhempy meanwhile")
