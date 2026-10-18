import os
import subprocess
import sys
import time

import pytest
from fhempy.lib.core import child_process

pytestmark = pytest.mark.skipif(os.name != "posix", reason="process groups")


def process_exists(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # zombies of already stopped processes don't count
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().split()[2] != "Z"
    except (FileNotFoundError, ProcessLookupError):
        # process was reaped between kill and open/read
        return False


@pytest.mark.asyncio
async def test_stop_also_stops_processes_started_by_the_child(tmp_path):
    pidfile = tmp_path / "grandchild.pid"
    proc = child_process.start(["sh", "-c", f"sleep 60 & echo $! > {pidfile}; wait"])
    while not pidfile.exists() or pidfile.read_text() == "":
        time.sleep(0.01)
    grandchild = int(pidfile.read_text())

    assert await child_process.stop(proc, timeout=5)
    time.sleep(0.1)
    assert not process_exists(grandchild)


@pytest.mark.skipif(sys.platform != "linux", reason="PR_SET_PDEATHSIG")
def test_child_is_stopped_when_fhempy_exits(tmp_path):
    pidfile = tmp_path / "child.pid"
    # simulates fhempy, which exits with os._exit without stopping modules
    parent = (
        "import os, sys\n"
        "from fhempy.lib.core import child_process\n"
        "proc = child_process.start(['sleep', '60'])\n"
        f"open({str(pidfile)!r}, 'w').write(str(proc.pid))\n"
        "os._exit(0)\n"
    )
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
    subprocess.run([sys.executable, "-c", parent], check=True, env=env)
    child = int(pidfile.read_text())

    for _ in range(50):
        if not process_exists(child):
            break
        time.sleep(0.1)
    assert not process_exists(child)


def wait_for(condition, timeout=5):
    for _ in range(int(timeout * 100)):
        if condition():
            return True
        time.sleep(0.01)
    return condition()


def test_output_goes_to_own_log_file_and_crash_is_reported(tmp_path, mocker):
    logger = mocker.Mock()
    log = child_process.OutputLog(str(tmp_path / "log" / "dev.log"), logger)
    proc = child_process.start(
        ["sh", "-c", "for i in 1 2 3; do echo line$i; done; echo err >&2; exit 3"],
        output_log=log,
    )
    assert wait_for(lambda: logger.error.called)
    assert proc.returncode == 3
    assert (tmp_path / "log" / "dev.log").read_text() == "line1\nline2\nline3\nerr\n"
    message = logger.error.call_args[0][0]
    assert "code 3" in message
    assert message.endswith("line3\nerr")


def test_log_file_is_rotated(tmp_path, mocker):
    path = tmp_path / "dev.log"
    log = child_process.OutputLog(str(path), mocker.Mock(), max_bytes=100)
    proc = child_process.start(
        ["sh", "-c", "for i in $(seq 1 100); do echo line$i; done"], output_log=log
    )
    assert wait_for(lambda: proc.returncode is not None)
    time.sleep(0.1)
    assert (tmp_path / "dev.log.1").exists()
    assert (tmp_path / "dev.log.2").exists()
    assert not (tmp_path / "dev.log.3").exists()
    assert "line100" in path.read_text()


@pytest.mark.asyncio
async def test_stop_is_not_reported_as_crash(tmp_path, mocker):
    logger = mocker.Mock()
    log = child_process.OutputLog(str(tmp_path / "dev.log"), logger)
    proc = child_process.start(["sleep", "60"], output_log=log)
    assert await child_process.stop(proc, timeout=5)
    time.sleep(0.2)
    logger.error.assert_not_called()


def test_crash_of_process_writing_its_own_log_is_reported(tmp_path, mocker):
    logger = mocker.Mock()
    path = tmp_path / "server.log"
    path.write_text("".join(f"old{i}\n" for i in range(30)) + "FATAL boom\n")
    log = child_process.OutputLog(str(path), logger, capture=False)
    child_process.start(["sh", "-c", "exit 1"], output_log=log)
    assert wait_for(lambda: logger.error.called)
    message = logger.error.call_args[0][0]
    assert message.endswith("FATAL boom")
    assert "old10\n" not in message and "old11" in message
