"""Stands in for bridge.mjs in tests: answers like the real bridge and
writes every message it receives to the file given as first argument."""

import json
import sys

log = open(sys.argv[1], "a", encoding="utf-8")


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


commanded = False
for line in sys.stdin:
    message = json.loads(line)
    log.write(line)
    log.flush()
    if message["cmd"] == "devices":
        send(
            {
                "event": "status",
                "commissioned": False,
                "qr": "MT:Y.K90AFN00KA0648G00",
                "manual": "34970112332",
                "fabrics": [],
            }
        )
        if not commanded and message["devices"]:
            # a Matter app switches the first device on
            commanded = True
            send(
                {
                    "event": "command",
                    "id": message["devices"][0]["id"],
                    "command": {"on": True},
                }
            )
    elif message["cmd"] == "pairing_mode":
        send({"event": "pairing_mode", "minutes": 15})
