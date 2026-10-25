import importlib.util
import json
from pathlib import Path

import pytest

from fhempy.lib.autodiscovery import catalog

REPO = Path(__file__).resolve().parents[7]


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "manifest2modules", REPO / "manifest2modules.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discovery_json_is_up_to_date(monkeypatch):
    monkeypatch.chdir(REPO)
    builder = load_builder()
    current = (REPO / builder.DISCOVERY_OUTPUT).read_text(encoding="utf-8")
    assert builder.build_discovery() == current, "run: python3 manifest2modules.py"


def write_manifest(lib, module, discovery, installer=None):
    (lib / module).mkdir(parents=True)
    manifest = {"requirements": [], "discovery": discovery}
    if installer:
        manifest["installer"] = installer
    (lib / module / "manifest.json").write_text(json.dumps(manifest))


def test_build_normalizes_rules(tmp_path):
    builder = load_builder()
    write_manifest(
        tmp_path,
        "cast",
        {"mdns": ["_googlecast._tcp.local."], "unique": "{txt.id}"},
        {"title": "Google Cast", "name": "cast", "logo": "googlecast.png"},
    )
    entries = json.loads(builder.build_discovery(str(tmp_path)))
    assert entries == [
        {
            "module": "cast",
            "title": "Google Cast",
            "name": "cast",
            "logo": "googlecast.png",
            "rules": [
                {"mdns": [{"type": "_googlecast._tcp.local."}], "unique": "{txt.id}"}
            ],
        }
    ]


@pytest.mark.parametrize(
    "discovery,error",
    [
        ({"unique": "x"}, "needs one of"),
        ({"mdns": ["_x._tcp"], "unique": "x"}, ".local."),
        ({"ble": [{"name": "x"}]}, "unique or single"),
        ({"search": True}, "discovery.py"),
        ({"ble": [{"name": "x"}], "unique": "x", "action": "foo"}, "unknown"),
    ],
)
def test_build_rejects_invalid_rules(tmp_path, discovery, error):
    builder = load_builder()
    write_manifest(tmp_path, "mod", discovery)
    with pytest.raises(ValueError, match=error):
        builder.build_discovery(str(tmp_path))


def test_render():
    values = {"txt": {"fn": "Living Room"}, "ip": "1.2.3.4"}
    assert catalog.render("{txt.fn} ({ip})", values) == "Living Room (1.2.3.4)"
    assert catalog.render("{txt.missing}{nothing}", values) == ""


def test_device_name():
    assert catalog.device_name("Wohnzimmer Lautsprecher", "x") == (
        "Wohnzimmer_Lautsprecher"
    )
    assert catalog.device_name("Küche (oben)", "x") == "Kueche_oben"
    assert catalog.device_name("???", "fallback") == "fallback"


def test_real_catalog_matches_googlecast():
    entries = catalog.load()
    values = {
        "name": "Chromecast-abc",
        "ip": "192.168.1.20",
        "txt": {"fn": "Living Room", "md": "Chromecast", "id": "abc123"},
    }
    matches = list(catalog.match_mdns(entries, "_googlecast._tcp.local.", values))
    assert [entry["module"] for entry, _ in matches] == ["googlecast"]
    found = catalog.candidate(*matches[0], values, "mdns")
    assert found["id"] == "googlecast:abc123"
    assert found["title"] == "Living Room"
    assert found["name"] == "Living_Room"
    assert found["define"] == ["Living Room"]
    assert found["exists"] == "Living Room"
    assert found["logo"] == "googlecast.png"


def test_homekit_only_unpaired_devices():
    entries = catalog.load()
    paired = {"txt": {"sf": "0", "id": "AA:BB"}}
    unpaired = {"txt": {"sf": "1", "id": "AA:BB"}}
    assert not list(catalog.match_mdns(entries, "_hap._tcp.local.", paired))
    matches = list(catalog.match_mdns(entries, "_hap._tcp.local.", unpaired))
    found = catalog.candidate(*matches[0], {**unpaired, "name": "Velux"}, "mdns")
    assert found["define"] == ["AA:BB"]
    assert found["params"][0]["label"] == "Setup code"


def test_ssdp_media_renderer():
    entries = catalog.load()
    values = {
        "device_type": "urn:schemas-upnp-org:device:MediaRenderer:1",
        "udn": "uuid:1234",
        "friendly_name": "TV",
    }
    matches = list(catalog.match_ssdp(entries, values))
    assert [entry["module"] for entry, _ in matches] == ["dlna_dmr"]
    assert catalog.candidate(*matches[0], values, "ssdp")["define"] == ["uuid:1234"]


def test_ble_rssi_and_names():
    entries = catalog.load()
    assert [
        e["module"]
        for e, _ in catalog.match_ble(entries, "CC-RT-BLE", set(), set(), -60)
    ] == ["eq3bt"]
    # the neighbour's thermostat
    assert not list(catalog.match_ble(entries, "CC-RT-BLE", set(), set(), -95))
    # scooter by manufacturer id, Matter by service data
    assert [
        e["module"] for e, _ in catalog.match_ble(entries, "", {16974}, set(), -50)
    ] == ["scooter"]
    matter_uuid = {"0000fff6-0000-1000-8000-00805f9b34fb"}
    matches = list(catalog.match_ble(entries, "", set(), matter_uuid, -50))
    found = catalog.candidate(*matches[0], {"address": "AA"}, "ble")
    assert found["action"] == "set"
    assert found["set"]["command"] == "pair_new_device"


def test_single_rule_uses_module_as_unique():
    entries = catalog.load()
    matches = list(catalog.match_mdns(entries, "_spotify-connect._tcp.local.", {}))
    found = catalog.candidate(*matches[0], {"name": "x"}, "mdns")
    assert found["id"] == "spotify:spotify"
