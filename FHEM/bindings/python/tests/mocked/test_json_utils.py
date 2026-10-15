import pytest
from fhempy.lib.json_utils import json_dumps, json_loads, HAS_ORJSON
import json


def test_json_dumps_loads_roundtrip():
    data = {
        "id": 12345,
        "NAME": "test_device",
        "command": "set reading München",
        "flag": True,
        "empty": None,
        "pi": 3.14159,
        "nested": {"key": "value", "special": "Grüße ☺"},
    }
    dumped = json_dumps(data)
    assert isinstance(dumped, str)
    # Ensure non-ascii characters are preserved without \u escaping
    assert "München" in dumped
    assert "Grüße" in dumped

    loaded = json_loads(dumped)
    assert loaded == data


def test_json_loads_bytes_and_str():
    raw_str = '{"status": "ok", "code": 200}'
    raw_bytes = b'{"status": "ok", "code": 200}'
    assert json_loads(raw_str) == {"status": "ok", "code": 200}
    assert json_loads(raw_bytes) == {"status": "ok", "code": 200}


def test_json_loads_invalid():
    with pytest.raises(Exception):
        json_loads("{invalid json:")


def test_fallback_equivalence():
    data = {"greeting": "Hallo Welt", "city": "Küche", "num": 42}
    std_json_str = json.dumps(data, ensure_ascii=False)
    our_json_str = json_dumps(data)
    assert json_loads(std_json_str) == json_loads(our_json_str) == data
