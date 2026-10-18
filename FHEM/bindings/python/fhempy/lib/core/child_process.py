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
import threading

PR_SET_PDEATHSIG = 1


def _terminate_with_parent():
    # runs in the child before exec
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)


def log_path(name):
    """Log file for the output of a child process, e.g. .fhempy/log/z2m.log"""
    return os.path.join(os.getcwd(), ".fhempy", "log", name + ".log")


class OutputLog:
    """Log file of a child process.

    With capture=True stdout and stderr of the process are written to a
    rotating log file instead of the fhempy log (which FHEM reads line by
    line). With capture=False the process writes path itself.
    If the process exits with an error (not stopped by stop()), the last
    lines of the file are written to the fhempy log."""

    def __init__(
        self,
        path,
        logger=None,
        capture=True,
        max_bytes=5 * 1024 * 1024,
        backup_count=2,
        tail_lines=20,
    ):
        self.path = path
        self.logger = logger
        self.capture = capture
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.tail_lines = tail_lines
        self.stopping = False

    def tail(self):
        """Last lines of the log file"""
        try:
            with open(self.path, "rb") as f:
                f.seek(max(0, os.fstat(f.fileno()).st_size - 16384))
                data = f.read()
        except OSError:
            return []
        lines = data.decode("utf-8", errors="replace").splitlines()
        return [line.rstrip() for line in lines[-self.tail_lines :]]

    def attach(self, proc):
        proc.output_log = self
        threading.Thread(
            target=self._run, args=(proc,), name="output-log", daemon=True
        ).start()

    def _open(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            return open(self.path, "ab")
        except OSError:
            return None

    def _rotate(self):
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.path}.{i}"
            if os.path.exists(src):
                os.replace(src, f"{self.path}.{i + 1}")
        os.replace(self.path, self.path + ".1")

    def _copy(self, proc):
        f = self._open()
        try:
            for line in iter(proc.stdout.readline, b""):
                if f is None:
                    continue
                try:
                    f.write(line)
                    f.flush()
                    if f.tell() > self.max_bytes:
                        f.close()
                        f = None
                        self._rotate()
                        f = self._open()
                except OSError:
                    # e.g. disk full, keep reading so the process doesn't block
                    pass
        finally:
            if f is not None:
                f.close()
            proc.stdout.close()

    def _run(self, proc):
        if self.capture:
            self._copy(proc)
        returncode = proc.wait()
        if returncode != 0 and not self.stopping and self.logger is not None:
            self.logger.error(
                f"Process exited with code {returncode}, last lines of "
                f"{self.path}:\n" + "\n".join(self.tail())
            )


def start(args, output_log=None, **kwargs):
    """subprocess.Popen which stops the process together with fhempy.

    With output_log (OutputLog) a crash is reported in the fhempy log and with
    output_log.capture stdout and stderr go to its log file."""
    if sys.platform == "linux":
        kwargs.setdefault("preexec_fn", _terminate_with_parent)
    if os.name == "posix":
        kwargs.setdefault("start_new_session", True)
    if output_log is not None and output_log.capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    proc = subprocess.Popen(args, **kwargs)
    if output_log is not None:
        output_log.attach(proc)
    return proc


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
    # don't report the exit as crash
    output_log = getattr(proc, "output_log", None)
    if output_log is not None:
        output_log.stopping = True

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
