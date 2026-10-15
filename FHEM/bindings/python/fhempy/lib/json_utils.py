"""High-performance JSON serialization helpers with automatic fallback."""

try:
    import orjson

    def json_dumps(obj):
        return orjson.dumps(obj).decode("utf-8")

    json_loads = orjson.loads
    HAS_ORJSON = True
except ImportError:
    import json

    def json_dumps(obj):
        return json.dumps(obj, ensure_ascii=False)

    json_loads = json.loads
    HAS_ORJSON = False
