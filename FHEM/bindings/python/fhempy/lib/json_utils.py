"""JSON helpers for the FHEM websocket connection.

orjson is several times faster than json. Values orjson rejects (e.g. ints
larger than 64 bit) fall back to json, so the result is always valid JSON.
Non-ASCII characters are sent as UTF-8 (no \\u escapes), so FHEM gets the
same UTF-8 bytes it uses internally.
"""

import json

try:
    import orjson
except ImportError:  # pragma: no cover - orjson is a fhempy dependency
    orjson = None


def _json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False)


if orjson is not None:

    def json_dumps(obj):
        try:
            return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode("utf-8")
        except TypeError:
            return _json_dumps(obj)

    def json_loads(data):
        try:
            return orjson.loads(data)
        except orjson.JSONDecodeError:
            # orjson is stricter than json (e.g. NaN), keep json's behaviour
            return json.loads(data)

else:  # pragma: no cover
    json_dumps = _json_dumps
    json_loads = json.loads
