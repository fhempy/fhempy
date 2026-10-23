import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "manifest2modules", REPO / "manifest2modules.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modules_json_is_up_to_date(monkeypatch):
    monkeypatch.chdir(REPO)
    builder = load_builder()
    current = (REPO / builder.OUTPUT).read_text(encoding="utf-8")
    assert builder.build() == current, "run: python3 manifest2modules.py"


def write_manifest(lib, module, installer):
    (lib / module).mkdir(parents=True)
    (lib / module / "manifest.json").write_text(
        json.dumps({"requirements": [], "installer": installer})
    )


def test_presets_order_and_logo(tmp_path):
    builder = load_builder()
    lib = tmp_path / "lib"
    www = tmp_path / "www"
    www.mkdir()
    (www / "b.png").write_bytes(b"")
    base = {"description": "d", "category": "bt", "name": "n"}
    write_manifest(
        lib,
        "b_mod",
        {
            **base,
            "title": "B",
            "logo": "b.png",
            "params": [{"type": "mac", "optional": True}],
        },
    )
    write_manifest(lib, "a_mod", {**base, "title": "A", "order": 5000})
    write_manifest(lib, "c_mod", {**base, "title": "C", "order": 10})
    (lib / "no_installer").mkdir()
    (lib / "no_installer" / "manifest.json").write_text('{"requirements": []}')

    catalog = json.loads(builder.build(str(lib), str(www)))

    assert [m["id"] for m in catalog] == ["c_mod", "b_mod", "a_mod"]
    assert catalog[1]["params"] == [{**builder.PRESETS["mac"], "optional": True}]
    assert "order" not in catalog[0]


def test_missing_logo_fails(tmp_path):
    builder = load_builder()
    write_manifest(
        tmp_path / "lib",
        "x",
        {
            "title": "X",
            "description": "d",
            "category": "bt",
            "name": "x",
            "logo": "missing.png",
        },
    )
    with pytest.raises(ValueError, match="missing.png"):
        builder.build(str(tmp_path / "lib"), str(tmp_path))
