import asyncio

from .. import fhem, generic


class huawei_modbus(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.bridge = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 30,
                "format": "int",
                "help": "Update interval in seconds",
            },
        }
        await self.set_attr_config(attr_config)

        set_config = {}
        await self.set_set_config(set_config)

        if len(args) < 4:
            return "Usage: define my_sun2000 fhempy fusionsolar_modbus IP PORT SLAVE_ID"

        self.ip = args[3]
        self.port = 502
        self.slave_id = 1

        if len(args) >= 5:
            self.port = int(args[4])

            if len(args) == 6:
                self.slave_id = int(args[5])
            else:
                return (
                    "Usage: define my_sun2000 fhempy fusionsolar_modbus IP PORT"
                    + " SLAVE_ID"
                )

        self.hash["IP"] = self.ip
        self.hash["PORT"] = self.port
        self.hash["SLAVE_ID"] = self.slave_id

        self.create_async_task(self.start())

    async def Undefine(self, hash):
        if self.bridge:
            await self.bridge.stop()
        return await super().Undefine(self.hash)

    async def start(self):
        # try to connect until successful
        while not self.bridge:
            try:
                await self.connect()
            except Exception as e:
                self.logger.error(e)
                await asyncio.sleep(10)

        while True:
            try:
                await self.update()
            except Exception as e:
                self.logger.error(e)
                # try to reconnect
                await self.bridge.stop()
                await self.connect()

            await asyncio.sleep(self._attr_interval)

    async def connect(self):
        from huawei_solar import HuaweiSolarBridge

        self.bridge = await HuaweiSolarBridge.create(
            host=self.ip, port=self.port, slave_id=self.slave_id
        )

    async def update(self):
        data = await self.bridge.update()

        await fhem.readingsBeginUpdate(self.hash)
        try:
            for key in data:
                await fhem.readingsBulkUpdateIfChanged(self.hash, key, data[key].value)
        except Exception as e:
            self.logger.error(e)
        await fhem.readingsEndUpdate(self.hash, 1)
