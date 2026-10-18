"""Exercise update selection and dispatch without installing any packages."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fhempy.lib import fhem, fhem_pythonbinding, pkg_installer, updates


def distribution(version, **fields):
    return {"filename": f"fhempy-{version}-py3-none-any.whl", "yanked": False, **fields}


def test_version_choices_are_sorted_filtered_and_include_installed(monkeypatch):
    monkeypatch.setattr(updates.platform, "python_version", lambda: "3.13.2")
    files = [
        distribution("2.1.3"), distribution("2.1.4"), distribution("2.1.9"),
        distribution("2.1.10"), {"filename": "fhempy-2.1.10.tar.gz"},
        distribution("3.0.0rc1"), distribution("3.0.0.dev1"),
        distribution("3.0.0", yanked=True), distribution("3.0.1", yanked=""),
        distribution("4.0.0", **{"requires-python": ">=3.14"}),
        distribution("5.0.0", **{"requires-python": "invalid"}),
        {"filename": "other-6.0.0.tar.gz"}, {"filename": "invalid.zip"},
    ]
    assert updates.available_versions(files, "2.1.4") == ["2.1.10", "2.1.9", "2.1.4"]
    assert updates.available_versions(files, "6.0.0") == ["6.0.0"]
    assert updates.available_versions([], "2.1.4") == ["2.1.4"]


@pytest.mark.parametrize("args,expected", [
    ([], "fhempy"), (["latest"], "fhempy"),
    (["2.1.4"], "fhempy==2.1.4"), (["v2.1.5"], "fhempy==2.1.5"),
    (["2.1.10"], "fhempy==2.1.10"),
    (["2.1.3"], "fhempy==2.1.3"),
])
def test_exact_requirements(args, expected):
    assert updates.package_requirement(args) == expected


@pytest.mark.parametrize("args", [["garbage"], [""], [">=2.1.4"],
                                  ["https://example.org/code.zip"], ["2.1.5", "extra"]])
def test_invalid_update_requirements(args):
    with pytest.raises(ValueError):
        updates.package_requirement(args)


@pytest.fixture
def binding(monkeypatch):
    monkeypatch.setattr(fhem_pythonbinding, "stop_event", asyncio.Event())
    monkeypatch.setattr(fhem_pythonbinding, "id_received_timestamp", {})
    monkeypatch.setattr(fhem_pythonbinding.version, "__version__", "2.1.4")
    monkeypatch.setattr(fhem, "__version__", "2.1.4")
    monkeypatch.setattr(fhem, "release_check_lock", asyncio.Lock())
    websocket = AsyncMock()
    pb = fhem_pythonbinding.fhempy(websocket)
    monkeypatch.setattr(fhem, "wsconnection", pb)
    monkeypatch.setattr(fhem, "readingsSingleUpdate", AsyncMock())
    monkeypatch.setattr(pkg_installer, "force_update_package", AsyncMock(return_value=True))
    monkeypatch.setattr(updates, "get_versions", AsyncMock(return_value=["2.1.5", "2.1.4"]))
    monkeypatch.setattr(pb, "restart", AsyncMock())
    return pb, websocket


async def command(pb, kind, args=None):
    await pb.onMessage(json.dumps({"id": 123, "NAME": "binding", "msgtype": kind,
                                   "args": args or [], "argsh": {}}))


@pytest.mark.asyncio
@pytest.mark.parametrize("args,package", [([], "fhempy"), (["latest"], "fhempy"),
                                          (["2.1.4"], "fhempy==2.1.4"),
                                          (["2.1.5"], "fhempy==2.1.5")])
async def test_update_dispatch_never_uses_cached_latest(binding, args, package):
    pb, _ = binding
    await command(pb, "update", args)
    pkg_installer.force_update_package.assert_awaited_once_with(package)
    updates.get_versions.assert_not_awaited()
    pb.restart.assert_awaited_once()
    assert not fhem_pythonbinding.id_received_timestamp
    assert not pb._updating
    assert all(call.args[1] == "update_status" for call in fhem.readingsSingleUpdate.call_args_list)


@pytest.mark.asyncio
@pytest.mark.parametrize("args", [["bad"], ["2.1.5", "extra"]])
async def test_rejected_versions_never_install_or_restart(binding, args):
    pb, _ = binding
    await command(pb, "update", args)
    pkg_installer.force_update_package.assert_not_awaited()
    pb.restart.assert_not_awaited()
    assert fhem.readingsSingleUpdate.call_args.args[1] == "update_status"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [False, OSError("installer missing")])
async def test_failed_exact_install_never_falls_back_or_restarts(binding, failure):
    pb, _ = binding
    installer = pkg_installer.force_update_package
    if isinstance(failure, Exception):
        installer.side_effect = failure
    else:
        installer.return_value = failure
    await command(pb, "update", ["2.1.5"])
    installer.assert_awaited_once_with("fhempy==2.1.5")
    pb.restart.assert_not_awaited()
    assert fhem.readingsSingleUpdate.call_args.args[2].startswith("failed:")
    assert not pb._updating


@pytest.mark.asyncio
async def test_concurrent_update_is_not_queued(binding):
    pb, _ = binding
    entered, finish = asyncio.Event(), asyncio.Event()

    async def install(package):
        entered.set()
        await finish.wait()
        return True

    pkg_installer.force_update_package.side_effect = install
    first = asyncio.create_task(command(pb, "update", ["2.1.5"]))
    await entered.wait()
    await command(pb, "update")
    finish.set()
    await first
    pkg_installer.force_update_package.assert_awaited_once_with("fhempy==2.1.5")
    pb.restart.assert_awaited_once()


@pytest.mark.asyncio
async def test_manual_check_updates_readings_without_installing(binding):
    pb, ws = binding
    await command(pb, "checkUpdate")
    messages = [json.loads(call.args[0]) for call in ws.send.call_args_list]
    assert messages[0]["update_check"] == "checking"
    assert messages[-1]["update_check"] == "ok"
    assert messages[-1]["version_available"] == "2.1.5"
    assert messages[-1]["version_options"] == "2.1.5,2.1.4"
    assert all(msg["msgtype"] == "version" for msg in messages)
    pkg_installer.force_update_package.assert_not_awaited()
    pb.restart.assert_not_awaited()
    assert not fhem_pythonbinding.id_received_timestamp


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [TimeoutError(), ValueError("invalid response")])
async def test_failed_check_preserves_last_good_version_information(binding, error):
    pb, ws = binding
    updates.get_versions.side_effect = error
    await command(pb, "checkUpdate")
    messages = [json.loads(call.args[0]) for call in ws.send.call_args_list]
    assert messages[-1]["update_check"].startswith("failed: ")
    assert all("version_options" not in msg and "version_available" not in msg for msg in messages)
    assert not fhem.release_check_lock.locked()


@pytest.mark.asyncio
async def test_overlapping_checks_share_in_flight_request(binding):
    pb, _ = binding
    entered, finish = asyncio.Event(), asyncio.Event()

    async def fetch(installed):
        entered.set()
        await finish.wait()
        return ["2.1.4"]

    updates.get_versions.side_effect = fetch
    first = asyncio.create_task(command(pb, "checkUpdate"))
    await entered.wait()
    await command(pb, "checkUpdate")
    finish.set()
    await first
    updates.get_versions.assert_awaited_once_with("2.1.4")


@pytest.mark.asyncio
async def test_periodic_check_runs_immediately_then_every_twelve_hours(monkeypatch):
    check = AsyncMock()
    intervals = []

    async def sleep(seconds):
        intervals.append(seconds)
        if len(intervals) == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(fhem, "check_update", check)
    monkeypatch.setattr(fhem.asyncio, "sleep", sleep)
    with pytest.raises(asyncio.CancelledError):
        await fhem.send_latest_release()
    assert intervals == [43200, 43200]
    assert check.await_count == 2


@pytest.mark.asyncio
async def test_version_reply_advertises_capability_without_overwriting_choices(binding):
    _, ws = binding
    await fhem.send_version()
    message = json.loads(ws.send.call_args.args[0])
    assert message["version"] == "2.1.4"
    assert message["update_version_supported"] == 1
    assert "version_options" not in message


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [None, RuntimeError("HTTP 503")])
async def test_index_fetch_uses_json_and_bounded_timeout(monkeypatch, failure):
    import aiohttp

    response = MagicMock()
    response.raise_for_status.side_effect = failure
    response.json = AsyncMock(return_value={"files": [distribution("2.1.5")]})
    request = MagicMock()
    request.__aenter__ = AsyncMock(return_value=response)
    request.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock()
    session.get.return_value = request
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=session)
    context.__aexit__ = AsyncMock(return_value=False)
    factory = MagicMock(return_value=context)
    monkeypatch.setattr(aiohttp, "ClientSession", factory)
    if failure:
        with pytest.raises(RuntimeError, match="503"):
            await updates.get_versions("2.1.4")
        response.json.assert_not_awaited()
    else:
        assert await updates.get_versions("2.1.4") == ["2.1.5", "2.1.4"]
    assert factory.call_args.kwargs["timeout"].total == 15
    assert session.get.call_args.args == (updates.INDEX_URL,)
    assert session.get.call_args.kwargs["headers"]["Accept"] == "application/vnd.pypi.simple.v1+json"


def test_uv_to_pip_fallback_preserves_exact_version(monkeypatch):
    calls = []
    monkeypatch.setattr(pkg_installer, "find_uv", lambda: "/test/uv")
    monkeypatch.setattr(pkg_installer, "uv_index_args", lambda: [])
    monkeypatch.setattr(pkg_installer, "is_virtual_env", lambda: False)

    class Process:
        def __init__(self, args, **kwargs):
            calls.append(args)
            self.returncode = 1 if args[0] == "/test/uv" else 0

        def communicate(self):
            return b"", b"test installer result"

    monkeypatch.setattr(pkg_installer, "Popen", Process)
    assert pkg_installer.install_package("fhempy==2.1.5")
    assert len(calls) == 2
    assert all("fhempy==2.1.5" in args for args in calls)
    assert calls[0][calls[0].index("--upgrade-package") + 1] == "fhempy"
    assert "--upgrade" in calls[1]
