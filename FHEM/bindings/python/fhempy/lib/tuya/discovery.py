"""Finds Tuya WiFi devices for autodiscovery.

Tuya devices broadcast their device id and IP every few seconds on UDP 6666
(protocol 3.1, plain JSON) and 6667 (3.3 and newer, AES encrypted with a key
known from the protocol). Only packages of fhempy itself are used here.
"""

import json
from hashlib import md5

from Cryptodome.Cipher import AES

PORTS = (6666, 6667)
UDP_KEY = md5(b"yGAdlopoPVldABfn").digest()  # NOSONAR, fixed by the protocol
PREFIX = bytes.fromhex("000055aa")


def _unpad(data):
    if not data or data[-1] > 16:
        return data
    return data[: -data[-1]]


def parse(data):
    """Device info of a broadcast package or None."""
    if not data.startswith(PREFIX) or len(data) < 28:
        return None
    payload = data[20:-8]
    try:
        info = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        try:
            decrypted = AES.new(UDP_KEY, AES.MODE_ECB).decrypt(  # NOSONAR
                payload[: len(payload) // 16 * 16]
            )
            info = json.loads(_unpad(decrypted).decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return None
    if not isinstance(info, dict) or "gwId" not in info:
        return None
    return info


async def search(ctx):
    found = {}
    for data, ip, _ in await ctx.udp_listen(PORTS, wait=8):
        info = parse(data)
        if info is None or info["gwId"] in found:
            continue
        found[info["gwId"]] = info
        ctx.found(
            id=info["gwId"],
            ip=info.get("ip", ip),
            title=f"Tuya device {info.get('ip', ip)}",
            version=info.get("version", ""),
        )
