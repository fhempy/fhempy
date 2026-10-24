"""Finds Gree air conditioners for autodiscovery.

The devices answer a scan broadcast on UDP 7000. The answer is AES encrypted
with a key known from the protocol, ECB on older and GCM on newer firmware.
Only packages of fhempy itself are used here.
"""

import base64
import json

from Cryptodome.Cipher import AES

PORT = 7000
SCAN = json.dumps({"t": "scan"}).encode()
# fixed by the protocol
ECB_KEY = b"a3K8Bx%2r8Y7#xDh"  # NOSONAR
GCM_KEY = b"{yxAHAY_Lm6pbC/<"  # NOSONAR
GCM_NONCE = bytes(
    [0x54, 0x40, 0x78, 0x44, 0x49, 0x67, 0x5A, 0x51, 0x6C, 0x5E, 0x63, 0x13]
)
GCM_AAD = b"qualcomm-test"


def _unpad(data):
    # PKCS7 or zero padding
    data = data.rstrip(b"\x00")
    if data and data[-1] <= 16 and data.endswith(bytes([data[-1]]) * data[-1]):
        data = data[: -data[-1]]
    return data


def decrypt_pack(response):
    pack = base64.b64decode(response["pack"])
    if "tag" in response:
        cipher = AES.new(GCM_KEY, AES.MODE_GCM, nonce=GCM_NONCE)
        cipher.update(GCM_AAD)
        data = cipher.decrypt_and_verify(pack, base64.b64decode(response["tag"]))
    else:
        data = AES.new(ECB_KEY, AES.MODE_ECB).decrypt(pack)  # NOSONAR
    return json.loads(_unpad(data).decode("utf-8"))


def parse(data):
    """(mac, name) of a scan answer or None"""
    try:
        response = json.loads(data.decode("utf-8"))
        if response.get("t") != "pack":
            return None
        info = decrypt_pack(response)
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return None
    mac = info.get("mac") or response.get("cid")
    if not mac:
        return None
    return mac, info.get("name") or ""


async def search(ctx):
    for data, ip in await ctx.udp_broadcast(PORT, SCAN, wait=4):
        result = parse(data)
        if result is None:
            continue
        mac, name = result
        ctx.found(mac=mac, name=name or mac, ip=ip)
