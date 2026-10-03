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
