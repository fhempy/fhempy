import asyncio
from zeroconf import Zeroconf, ServiceInfo


class zeroconf:

    instance = None

    def get_instance(logger):
        if zeroconf.instance is None:
            zeroconf.instance = zeroconf(logger)
        return zeroconf.instance

    def __init__(self, logger):
        self.logger = logger
        self.loop = asyncio.get_event_loop()
        self.zeroconf = Zeroconf()

    async def create_service(self, type, name, port, properties):
        info = ServiceInfo(
            type + "._tcp.local.",
            name + "." + type + "._tcp.local.",
            port,
            properties=properties,
        )
        self.zeroconf.register_service(info)

    def get_zeroconf(self):
        return self.zeroconf

    def stop(self):
        self.zeroconf.close()