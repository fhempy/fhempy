import base64
import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.github_restore.github_restore import github_restore

BACKUP_DIR = "master_fhem_rpi"
FILES = {
    "fhem.cfg": b"define z2m fhempy zigbee2mqtt\n",
    ".fhempy/zigbee2mqtt/data/configuration.yaml": b"restored: true\n",
    ".fhempy/zigbee2mqtt/data/database.db": b"restored database\n",
    ".fhempy/matter_server/data/fabric/node.1": b"restored node\n",
    ".fhempy/matter_bridge/bridge/pairing.json": b"{}\n",
    "FHEM/FhemUtils/uniqueID": b"uniqueID:0123\n",
}


def mock_github(url):
    if "/commits?" in url:
        return [{"sha": "c1", "commit": {"author": {"date": "2026-10-01T03:38:00Z"}}}]
    if "/git/trees/" in url:
        return {
            "tree": [{"path": BACKUP_DIR, "type": "tree", "sha": "t"}]
            + [
                {"path": f"{BACKUP_DIR}/{name}", "type": "blob", "sha": name}
                for name in FILES
            ]
        }
    if "/git/blobs/" in url:
        name = url.split("/git/blobs/")[1]
        return {"content": base64.b64encode(FILES[name]).decode("ascii")}
    return None


@pytest.mark.asyncio
async def test_zigbee2mqtt_data_is_restored_as_pending(mocker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mock_fhem.mock_module(mocker)
    mock_fhem.readings.pop("testrestore", None)

    device = github_restore(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    mocker.patch.object(device, "github_get", mocker.AsyncMock(side_effect=mock_github))
    testhash = {"NAME": "testrestore", "FHEMPYTYPE": "github_restore"}
    await device.Define(
        testhash,
        [
            "testrestore",
            "fhempy",
            "github_restore",
            "https://github.com/user/fhem_backup",
            BACKUP_DIR,
        ],
        {},
    )
    device.gh_token_ready.set()
    stale = tmp_path / ".fhempy/zigbee2mqtt_restore/data/stale.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("from an earlier restore")

    await device.restore_backup()

    assert (tmp_path / "fhem.cfg").read_bytes() == FILES["fhem.cfg"]
    # zigbee2mqtt isn't installed yet, its data must not be written there
    assert not (tmp_path / ".fhempy/zigbee2mqtt").exists()
    pending = tmp_path / ".fhempy/zigbee2mqtt_restore/data"
    assert (pending / "configuration.yaml").read_bytes() == b"restored: true\n"
    assert (pending / "database.db").read_bytes() == b"restored database\n"
    assert not stale.exists()
    state = mock_fhem.readings["testrestore"]["state"]
    assert state.startswith("Backup restored")
    assert "zigbee2mqtt data will be applied" in state
    # a running Matter server would overwrite its storage, it's staged too
    assert not (tmp_path / ".fhempy/matter_server").exists()
    assert (
        tmp_path / ".fhempy/matter_server_restore/fabric/node.1"
    ).read_bytes() == b"restored node\n"
    assert "Matter data will be applied" in state
    assert not (tmp_path / ".fhempy/matter_bridge").exists()
    assert (
        tmp_path / ".fhempy/matter_bridge_restore/bridge/pairing.json"
    ).read_bytes() == b"{}\n"
    assert "Matter bridge pairings will be applied" in state
    assert (tmp_path / "FHEM/FhemUtils/uniqueID").read_bytes() == b"uniqueID:0123\n"


def test_matter_restore_replaces_storage(tmp_path):
    from fhempy.lib.core import pending_restore

    storage = tmp_path / ".fhempy/matter_server/data"
    (storage / "fabric").mkdir(parents=True)
    (storage / "fabric/node.9").write_text("current fabric")
    pending = tmp_path / ".fhempy/matter_server_restore"
    (pending / "fabric").mkdir(parents=True)
    (pending / "fabric/node.1").write_text("restored")

    assert pending_restore.apply_matter_restore(storage) == ["fabric/node.1"]

    # keys of two fabrics must not be mixed
    assert sorted(p.name for p in storage.rglob("*") if p.is_file()) == ["node.1"]
    assert (storage / "fabric/node.1").read_text() == "restored"
    previous = tmp_path / ".fhempy/matter_server/data.before_restore"
    assert (previous / "fabric/node.9").read_text() == "current fabric"
    assert not pending.exists()
    # consumed, nothing to apply on the next start
    assert pending_restore.apply_matter_restore(storage) == []


def test_bridge_restore_replaces_pairings(tmp_path):
    from fhempy.lib.core import pending_restore

    bridge = tmp_path / ".fhempy/matter_bridge/bridge"
    other = tmp_path / ".fhempy/matter_bridge_restore/other"
    other.mkdir(parents=True)
    (other / "pairing.json").write_text("other bridge")
    assert pending_restore.apply_bridge_restore(bridge) == []

    pending = tmp_path / ".fhempy/matter_bridge_restore/bridge"
    (pending / "data").mkdir(parents=True)
    (pending / "data/keys").write_text("restored")
    (bridge / "data").mkdir(parents=True)
    (bridge / "data/old").write_text("current")

    assert pending_restore.apply_bridge_restore(bridge) == ["data/keys"]
    assert sorted(p.name for p in bridge.rglob("*") if p.is_file()) == ["keys"]
    assert (bridge.with_name("bridge.before_restore") / "data/old").exists()
    assert not pending.exists()
    # the other bridge still gets its pairings
    assert (other / "pairing.json").exists()
    assert pending_restore.apply_bridge_restore(
        other.parent.parent / "matter_bridge/other"
    ) == ["pairing.json"]
    assert not other.parent.exists()
