"""set fhempy_local installPeer: fhempy installs itself on a peer via SSH.

The peer is an asyncssh server in the test, which runs the commands with bash
and a fake sudo, the installer script is replaced by one printing the steps.
"""

import asyncio
import os
import stat
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fhempy.lib import fhem, pkg_installer
from fhempy.lib.core.peer_installer import peer_installer

PASSWORD = "geheim 123"

FAKE_SUDO = """#!/bin/bash
# sudo -S -p '' <command>: checks the password from stdin
read -r password
if [ "$password" != "$FHEMPY_TEST_PASSWORD" ]; then
  echo "sudo: 1 incorrect password attempt"
  exit 1
fi
shift 3
SUDO_USER=$USER exec "$@"
"""

FAKE_INSTALLER = """#!/bin/bash
echo "fhempy-install: 1/5 installing system packages"
echo "fhempy-install: 3/5 installing fhempy"
echo "running as $SUDO_USER"
echo "fhempy-install: done 10.0.0.2"
"""


def test_parse_args():
    assert peer_installer.parse_args(["pi.local", "pi", "pw"]) == (
        "pi.local",
        "pi",
        "pw",
    )
    assert peer_installer.parse_args(["pi@10.0.0.2", "pw"]) == ("10.0.0.2", "pi", "pw")
    with pytest.raises(ValueError):
        peer_installer.parse_args(["10.0.0.2", "pw"])
    with pytest.raises(ValueError):
        peer_installer.parse_args(["10.0.0.2", "pi", ""])


def test_peer_device_name_matches_discovery():
    assert peer_installer.peer_device_name("10.0.0.2") == "fhempy_peer_10_0_0_2"


def test_start_rejects_invalid_arguments():
    assert peer_installer.start({"NAME": "local"}, ["host"]) is not None
    assert peer_installer.start({"NAME": "local"}, ["-oProxy", "pi", "pw"]) is not None


@pytest_asyncio.fixture
async def ssh_peer(tmp_path, monkeypatch):
    await pkg_installer.check_and_install_dependencies("core/peer_installer")
    import asyncssh

    bindir = tmp_path / "bin"
    bindir.mkdir()
    sudo = bindir / "sudo"
    sudo.write_text(FAKE_SUDO)
    sudo.chmod(sudo.stat().st_mode | stat.S_IEXEC)
    script = tmp_path / "install_peer.sh"
    script.write_text(FAKE_INSTALLER)
    monkeypatch.setattr(peer_installer, "SCRIPT", str(script))
    monkeypatch.setattr(peer_installer, "KNOWN_HOSTS", str(tmp_path / "known_hosts"))

    env = dict(
        os.environ,
        PATH=f"{bindir}:{os.environ['PATH']}",
        FHEMPY_TEST_PASSWORD=PASSWORD,
        USER="pi",
        TMPDIR=str(tmp_path / "remote_tmp"),
    )
    (tmp_path / "remote_tmp").mkdir()

    async def handle_process(process):
        proc = await asyncio.create_subprocess_exec(
            "bash",
            "-c",
            process.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        await process.redirect(stdin=proc.stdin, stdout=proc.stdout)
        process.exit(await proc.wait())

    class Server(asyncssh.SSHServer):
        def begin_auth(self, username):
            return True

        def password_auth_supported(self):
            return True

        def validate_password(self, username, password):
            return username == "pi" and password == PASSWORD

    host_key = asyncssh.generate_private_key("ssh-ed25519")
    server = await asyncssh.create_server(
        Server,
        "127.0.0.1",
        0,
        server_host_keys=[host_key],
        process_factory=handle_process,
        encoding=None,
    )
    port = server.sockets[0].getsockname()[1]
    real_connect = asyncssh.connect

    def connect(host, **kwargs):
        return real_connect(host, port=port, **kwargs)

    real_get_key = asyncssh.get_server_host_key

    def get_server_host_key(host, **kwargs):
        return real_get_key(host, port=port, **kwargs)

    monkeypatch.setattr(asyncssh, "connect", connect)
    monkeypatch.setattr(asyncssh, "get_server_host_key", get_server_host_key)
    yield tmp_path
    server.close()
    await server.wait_closed()


@pytest.fixture
def fhem_mock(monkeypatch):
    readings = []

    async def reading(hash, name, value, trigger):
        readings.append(value)

    monkeypatch.setattr(fhem, "readingsSingleUpdate", reading)
    monkeypatch.setattr(fhem, "checkIfDeviceExists", AsyncMock(return_value=0))
    define = AsyncMock(return_value=None)
    monkeypatch.setattr(fhem, "CommandDefine", define)
    return readings, define


@pytest.mark.asyncio
async def test_install_peer(ssh_peer, fhem_mock):
    readings, define = fhem_mock
    installer = peer_installer.PeerInstaller(
        {"NAME": "fhempy_local"}, "127.0.0.1", "pi", PASSWORD
    )
    await installer.run()

    assert "127.0.0.1: 1/5 installing system packages" in readings
    assert "127.0.0.1: 3/5 installing fhempy" in readings
    assert readings[-1] == "127.0.0.1: done, fhempy_peer_127_0_0_1 is ready"
    define.assert_awaited_once_with(
        {"NAME": "fhempy_local"},
        "fhempy_peer_127_0_0_1 BindingsIo 127.0.0.1:15733 fhempy",
    )
    # the uploaded installer is removed again, the password is forgotten
    assert list((ssh_peer / "remote_tmp").iterdir()) == []
    assert installer.password is None
    assert not any(PASSWORD in r for r in readings)


@pytest.mark.asyncio
async def test_wrong_password(ssh_peer, fhem_mock):
    readings, define = fhem_mock
    await peer_installer.PeerInstaller(
        {"NAME": "fhempy_local"}, "127.0.0.1", "pi", "wrong"
    ).run()
    assert readings[-1] == "127.0.0.1: failed: wrong user or password"
    define.assert_not_awaited()


@pytest.mark.asyncio
async def test_failed_step_is_shown(ssh_peer, fhem_mock):
    readings, define = fhem_mock
    (ssh_peer / "install_peer.sh").write_text(
        'echo "fhempy-install: 2/5 installing Python environment"\n'
        'echo "fhempy-install: failed: creating the Python environment failed"\n'
        "exit 1\n"
    )
    await peer_installer.PeerInstaller(
        {"NAME": "fhempy_local"}, "127.0.0.1", "pi", PASSWORD
    ).run()
    assert readings[-1] == ("127.0.0.1: failed: creating the Python environment failed")
    define.assert_not_awaited()


@pytest.mark.asyncio
async def test_existing_peer_device_is_kept(ssh_peer, fhem_mock, monkeypatch):
    readings, define = fhem_mock
    monkeypatch.setattr(fhem, "checkIfDeviceExists", AsyncMock(return_value=1))
    await peer_installer.PeerInstaller(
        {"NAME": "fhempy_local"}, "127.0.0.1", "pi", PASSWORD
    ).run()
    assert readings[-1].endswith("is ready")
    define.assert_not_awaited()


@pytest.mark.asyncio
async def test_changed_host_key_is_rejected(ssh_peer, fhem_mock):
    readings, define = fhem_mock
    (ssh_peer / "known_hosts").write_text(
        "127.0.0.1 ssh-ed25519 "
        "AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl\n"
    )
    await peer_installer.PeerInstaller(
        {"NAME": "fhempy_local"}, "127.0.0.1", "pi", PASSWORD
    ).run()
    assert "host key of 127.0.0.1 changed" in readings[-1]
    define.assert_not_awaited()


@pytest.mark.asyncio
async def test_host_key_is_remembered(ssh_peer, fhem_mock):
    for _ in range(2):
        await peer_installer.PeerInstaller(
            {"NAME": "fhempy_local"}, "127.0.0.1", "pi", PASSWORD
        ).run()
    readings, _ = fhem_mock
    assert readings[-1].endswith("is ready")
    lines = (ssh_peer / "known_hosts").read_text().splitlines()
    assert len(lines) == 1 and lines[0].startswith("127.0.0.1 ssh-ed25519 ")
