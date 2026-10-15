"""JSON helpers for the FHEM websocket connection.

Non-ASCII characters are sent as UTF-8 (no \\u escapes), so FHEM gets the same
UTF-8 bytes it uses internally.
"""

import json


def json_dumps(obj):
    return json.dumps(obj, ensure_ascii=False)


json_loads = json.loads
