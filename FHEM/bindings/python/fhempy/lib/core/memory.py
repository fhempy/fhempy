"""Give memory freed by Python back to the operating system.

glibc keeps freed heap memory in the process for later allocations. After the
startup (module imports, Define of all devices, TLS requests) and after load
peaks several MB stay allocated although Python doesn't use them anymore.
malloc_trim releases them. Other C libraries (e.g. musl) don't have it,
nothing is done there.
"""

import asyncio
import ctypes
import ctypes.util
import logging

logger = logging.getLogger(__name__)

# after the connection to FHEM, FHEM defines all devices meanwhile (s)
FIRST_TRIM_DELAY = 120
TRIM_INTERVAL = 3600

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


async def trim_periodically():
    await asyncio.sleep(FIRST_TRIM_DELAY)
    if _get_malloc_trim() is None:
        logger.debug("malloc_trim not available, memory isn't trimmed")
        return
    while True:
        try:
            await asyncio.to_thread(trim)
        except Exception:
            logger.debug("malloc_trim failed", exc_info=True)
        await asyncio.sleep(TRIM_INTERVAL)
