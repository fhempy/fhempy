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
    with open(f"/proc/{pid}/stat") as f:
        return f.read().split()[2] != "Z"


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
