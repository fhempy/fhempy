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
Cyclic garbage of frozen objects isn't collected anymore, so once a day the
collector checks everything again.
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
# frozen objects are checked by the garbage collector again this often (s)
UNFREEZE_INTERVAL = 86400

_malloc_trim = None
_loaded = False


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


_last_unfreeze = None


def freeze_objects():
    """Collects the garbage and freezes the surviving objects, they aren't
    checked by later collections. Runs in the event loop (the collector
    needs the GIL anyway), only the not yet frozen objects are checked,
    except once per UNFREEZE_INTERVAL."""
    global _last_unfreeze
    now = time.monotonic()
    if _last_unfreeze is None:
        _last_unfreeze = now
    elif now - _last_unfreeze >= UNFREEZE_INTERVAL:
        _last_unfreeze = now
        gc.unfreeze()
    start = time.perf_counter()
    gc.collect()
    gc.freeze()
    logger.debug(
        f"{gc.get_freeze_count()} objects frozen for the garbage collector "
        f"({(time.perf_counter() - start) * 1000:.0f}ms)"
    )


async def trim_periodically():
    await asyncio.sleep(FIRST_TRIM_DELAY)
    malloc_trim = _get_malloc_trim()
    if malloc_trim is None:
        logger.debug("malloc_trim not available, memory isn't trimmed")
    while True:
        try:
            freeze_objects()
        except Exception:
            logger.debug("gc.freeze failed", exc_info=True)
        if malloc_trim is not None:
            try:
                await asyncio.to_thread(trim)
            except Exception:
                logger.debug("malloc_trim failed", exc_info=True)
        await asyncio.sleep(TRIM_INTERVAL)
