"""Fail tests whose code blocks the asyncio event loop.

While the loop hangs in synchronous code, fhempy can't answer FHEM and FHEM
is frozen. Every callback the loop runs during a test is timed; a test fails
if one of them took longer than BLOCK_THRESHOLD. Tests which block on purpose
use @pytest.mark.allow_blocking.
"""

import asyncio
import time

import pytest

# generous, GitHub runners are slow and noisy; production watchdog uses 0.5s
BLOCK_THRESHOLD = 0.5

_blocked = []
_original_run = asyncio.events.Handle._run


def _describe(handle):
    callback = getattr(handle, "_callback", None)
    task = getattr(callback, "__self__", None)
    if isinstance(task, asyncio.Task):
        coro = task.get_coro()
        code = getattr(coro, "cr_code", None)
        if code is not None:
            return f"{code.co_qualname} ({code.co_filename}:{code.co_firstlineno})"
    return repr(handle)


def _timed_run(self):
    start = time.monotonic()
    try:
        return _original_run(self)
    finally:
        duration = time.monotonic() - start
        if duration > BLOCK_THRESHOLD:
            _blocked.append((duration, _describe(self)))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "allow_blocking: test may block the event loop on purpose"
    )
    asyncio.events.Handle._run = _timed_run


def pytest_unconfigure(config):
    asyncio.events.Handle._run = _original_run


@pytest.fixture(autouse=True)
def fail_on_blocked_loop(request):
    _blocked.clear()
    yield
    blocked = list(_blocked)
    _blocked.clear()
    if blocked and request.node.get_closest_marker("allow_blocking") is None:
        details = "\n".join(f"  {d * 1000:.0f}ms in {what}" for d, what in blocked)
        pytest.fail(
            f"Event loop was blocked longer than {BLOCK_THRESHOLD * 1000:.0f}ms "
            f"(FHEM would be frozen meanwhile):\n{details}",
            pytrace=False,
        )
