"""Start and stop external programs (e.g. esphome dashboard) used by modules.

Child processes are started in their own process group and, on Linux, are
terminated by the kernel as soon as fhempy exits. This makes sure that no
program keeps running (and keeps ports or FHEM's output pipe open) after a
fhempy update, restart or crash.
"""

import asyncio
import ctypes
import os
import signal
import subprocess
import sys

PR_SET_PDEATHSIG = 1


def _terminate_with_parent():
    # runs in the child before exec
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)


def start(args, **kwargs):
    """subprocess.Popen which stops the process together with fhempy"""
    if sys.platform == "linux":
        kwargs.setdefault("preexec_fn", _terminate_with_parent)
    if os.name == "posix":
        kwargs.setdefault("start_new_session", True)
    return subprocess.Popen(args, **kwargs)


def _signal_process_group(proc, sig):
    try:
        if os.name == "posix":
            # also stop all processes started by the child
            os.killpg(proc.pid, sig)
        else:
            proc.send_signal(sig)
    except ProcessLookupError:
        pass


async def stop(proc, sig=signal.SIGTERM, timeout=10):
    """Stop the process started with start(), returns True if it stopped"""
    if proc.poll() is not None:
        return True

    _signal_process_group(proc, sig)
    if await _wait(proc, timeout):
        return True

    _signal_process_group(proc, signal.SIGKILL if os.name == "posix" else sig)
    return await _wait(proc, 5)


async def _wait(proc, timeout):
    for _ in range(int(timeout * 10)):
        if proc.poll() is not None:
            return True
        await asyncio.sleep(0.1)
    return proc.poll() is not None
