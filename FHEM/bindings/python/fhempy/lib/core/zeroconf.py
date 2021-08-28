import asyncio
import socket

from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf


class zeroconf:

    instance = None

    @staticmethod
    def get_instance(logger):
        if zeroconf.instance is None:
            zeroconf.instance = zeroconf(logger)
        return zeroconf.instance

    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self.zeroconf = AsyncZeroconf()

    async def register_service(self, type, name, port, properties):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        info = AsyncServiceInfo(
            type + "._tcp.local.",
            name + "." + type + "._tcp.local.",
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties=properties,
            server=hostname + ".local.",
        )
        await self.zeroconf.async_register_service(info)
        return info

    async def unregister_service(self, info):
        await self.zeroconf.async_unregister_service(info)

    def get_zeroconf(self):
        return self.zeroconf

    async def stop(self):
        await self.zeroconf.async_close()
