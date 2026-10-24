"""Finds GoodWe inverters for autodiscovery.

The WiFi module of the inverters answers a broadcast on UDP 48899 with
"<ip>,<mac>,<name>".
"""

PORT = 48899
REQUEST = b"WIFIKIT-214028-READ"


def parse(data, ip):
    """(ip, mac, name) of an answer or None"""
    try:
        parts = data.decode("ascii").strip().split(",")
    except UnicodeDecodeError:
        return None
    if len(parts) < 3 or not parts[1]:
        return None
    return parts[0] or ip, parts[1], parts[2]


async def search(ctx):
    for data, ip in await ctx.udp_broadcast(PORT, REQUEST, wait=3):
        result = parse(data, ip)
        if result is None:
            continue
        ip, mac, name = result
        ctx.found(ip=ip, mac=mac, title=f"GoodWe inverter {name}".strip())
