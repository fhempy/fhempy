"""Finds a MQTT broker on this computer for autodiscovery, e.g. Mosquitto or
the MQTT2_SERVER of FHEM. Brokers in the network are found via mDNS."""

import asyncio

HOST = "127.0.0.1"
PORT = 1883


async def search(ctx):
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(HOST, PORT), 2)
    except (OSError, asyncio.TimeoutError):
        return
    writer.close()
    ctx.found(ip=HOST, port=PORT)
