"""Finds Xiaomi WiFi devices (miIO protocol) for autodiscovery.

Every miIO device answers the "hello" broadcast on UDP 54321 with its device
id. The model isn't part of the answer, the host name the device sends to the
router usually is (e.g. roborock-vacuum-s5_miio123456).
"""

import struct

PORT = 54321
HELLO = bytes.fromhex("21310020" + "ff" * 28)


def parse(data):
    """device id of a hello answer or None"""
    if len(data) < 32 or data[:2] != b"\x21\x31" or data == HELLO:
        return None
    return struct.unpack(">I", data[8:12])[0]


def title_from_hostname(hostname):
    """'roborock-vacuum-s5_miio123' -> 'roborock vacuum s5'"""
    model = hostname.split("_miio")[0]
    return model.replace("-", " ").strip()


async def search(ctx):
    found = set()
    for data, ip in await ctx.udp_broadcast(PORT, HELLO, wait=3):
        device_id = parse(data)
        if device_id is None or device_id in found:
            continue
        found.add(device_id)
        hostname = await ctx.hostname(ip)
        model = title_from_hostname(hostname) if "_miio" in hostname else ""
        ctx.found(
            id=str(device_id),
            ip=ip,
            title=f"Xiaomi {model or 'device'} ({ip})",
            model=model,
        )
