"""Give memory freed by Python back to the operating system.

glibc keeps freed heap memory in the process for later allocations. After the
startup (module imports, Define of all devices, TLS requests) and after load
peaks several MB stay allocated although Python doesn't use them anymore.
malloc_trim releases them. Other C libraries (e.g. musl) don't have it,
nothing is done there.

The objects which exist after the startup (imported modules, defined devices)
stay alive until fhempy stops. Python's garbage collector still checks all of
them in every full collection: on a Raspberry Pi 2 this blocks the event loop
for several 100ms every few minutes, while it handles whatever runs at that
moment (e.g. a Bluetooth advertisement). gc.freeze() moves them out of the
collector's generations, full collections only check the newer objects then.

Cyclic garbage of frozen objects isn't collected anymore. Frozen objects
become garbage mainly when a device is deleted or redefined, so only then the
collector checks everything again (unfreeze, collect, freeze), once no further
device was removed for REMOVAL_SETTLE seconds (e.g. rereadcfg, deleting
several devices). This full check blocks the loop like the collections without
freeze did, but only after a change of the configuration instead of on a
timer while devices are in use. Other frozen garbage (e.g. a connection object
of the startup a module replaces) is kept, at most once per object, because
the replacement isn't frozen until the next freeze.
"""

import asyncio
import ctypes
import ctypes.util
import gc
import logging
import time

logger = logging.getLogger(__name__)

# after the connection to FHEM, FHEM defines all devices meanwhile (s)
FIRST_TRIM_DELAY = 120
TRIM_INTERVAL = 3600
# full check after the last removed device, removals meanwhile postpone it (s)
REMOVAL_SETTLE = 60
# a full check is logged as INFO from this duration on (s)
SLOW_COLLECTION = 0.5

_malloc_trim = None
_loaded = False

# set while freeze_objects runs: the loop watchdog doesn't warn about it
collecting = False
# monotonic start of the last freeze_objects call
last_collection_start = None

_removed = None


def _get_malloc_trim():
    global _malloc_trim, _loaded
    if not _loaded:
        _loaded = True
        try:
            libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6")
            _malloc_trim = libc.malloc_trim
            _malloc_trim.argtypes = [ctypes.c_size_t]
            _malloc_trim.restype = ctypes.c_int
        except (OSError, AttributeError):
            _malloc_trim = None
    return _malloc_trim


def trim():
    """True if memory was given back, runs without the GIL."""
    malloc_trim = _get_malloc_trim()
    if malloc_trim is None:
        return False
    return malloc_trim(0) == 1


def device_removed():
    """A device instance was deleted (Undefine, redefine, moved to a worker),
    its frozen objects are checked by the collector soon."""
    if _removed is not None:
        _removed.set()


def collection_started_since(since):
    """True if freeze_objects ran within a callback started at since."""
    start = last_collection_start
    return start is not None and start >= since


def freeze_objects(check_all=False):
    """Collects the garbage and freezes the surviving objects, they aren't
    checked by later collections. Runs in the event loop (the collector
    needs the GIL anyway), only the not yet frozen objects are checked,
    with check_all the frozen ones too."""
    global collecting, last_collection_start
    collecting = True
    start = time.perf_counter()
    last_collection_start = time.monotonic()
    try:
        if check_all:
            gc.unfreeze()
        gc.collect()
        gc.freeze()
    finally:
        collecting = False
    duration = time.perf_counter() - start
    level = logging.INFO if duration >= SLOW_COLLECTION else logging.DEBUG
    reason = " after devices were removed" if check_all else ""
    logger.log(
        level,
        f"Garbage collector checked {'all' if check_all else 'new'} objects"
        f"{reason} in {duration * 1000:.0f}ms, "
        f"{gc.get_freeze_count()} objects frozen",
    )


async def _wait_removed(seconds):
    """True if a device was removed within the given seconds."""
    try:
        await asyncio.wait_for(_removed.wait(), max(seconds, 0))
        return True
    except asyncio.TimeoutError:
        return False


async def _settle():
    """Waits until no device was removed for REMOVAL_SETTLE."""
    while True:
        _removed.clear()
        if not await _wait_removed(REMOVAL_SETTLE):
            return


def _freeze(check_all=False):
    try:
        freeze_objects(check_all)
    except Exception:
        logger.debug("gc.freeze failed", exc_info=True)


async def _trim(malloc_trim):
    if malloc_trim is None:
        return
    try:
        await asyncio.to_thread(trim)
    except Exception:
        logger.debug("malloc_trim failed", exc_info=True)


async def trim_periodically():
    global _removed
    _removed = asyncio.Event()
    await asyncio.sleep(FIRST_TRIM_DELAY)
    malloc_trim = _get_malloc_trim()
    if malloc_trim is None:
        logger.debug("malloc_trim not available, memory isn't trimmed")
    # removals during the startup are covered by the first collection
    _removed.clear()
    _freeze()
    await _trim(malloc_trim)
    next_trim = time.monotonic() + TRIM_INTERVAL
    while True:
        if await _wait_removed(next_trim - time.monotonic()):
            await _settle()
            _freeze(check_all=gc.get_freeze_count() > 0)
            await _trim(malloc_trim)
            continue
        _freeze()
        await _trim(malloc_trim)
        next_trim = time.monotonic() + TRIM_INTERVAL
