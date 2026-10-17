"""Fail tests whose code blocks the asyncio event loop.

While the loop hangs in synchronous code, fhempy can't answer FHEM and FHEM
is frozen. Every callback the loop runs during a test is timed; a test fails
if one of them took longer than BLOCK_THRESHOLD. Tests which block on purpose
use @pytest.mark.allow_blocking.

Time spent importing is not counted: tests import module code inside
coroutines after installing its dependencies, fhempy itself imports modules
in an executor.
"""

import asyncio
import builtins
import threading
import time

import pytest

# generous, GitHub runners are slow and noisy; production watchdog uses 0.5s
BLOCK_THRESHOLD = 0.5

_blocked = []
_original_run = asyncio.events.Handle._run
_original_import = builtins.__import__
_import_state = threading.local()


def _timed_import(*args, **kwargs):
    depth = getattr(_import_state, "depth", 0)
    if depth:
        return _original_import(*args, **kwargs)
    _import_state.depth = 1
    start = time.monotonic()
    try:
        return _original_import(*args, **kwargs)
    finally:
        _import_state.depth = 0
        _import_state.spent = (
            getattr(_import_state, "spent", 0.0) + time.monotonic() - start
        )


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
    spent_before = getattr(_import_state, "spent", 0.0)
    start = time.monotonic()
    try:
        return _original_run(self)
    finally:
        duration = time.monotonic() - start
        duration -= getattr(_import_state, "spent", 0.0) - spent_before
        if duration > BLOCK_THRESHOLD:
            _blocked.append((duration, _describe(self)))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "allow_blocking: test may block the event loop on purpose"
    )
    asyncio.events.Handle._run = _timed_run
    builtins.__import__ = _timed_import


def pytest_unconfigure(config):
    asyncio.events.Handle._run = _original_run
    builtins.__import__ = _original_import


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
