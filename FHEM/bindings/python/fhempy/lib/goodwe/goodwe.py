import asyncio

import goodwe as gw

from .. import fhem, generic, utils


class goodwe(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 300,
                "format": "int",
                "help": "Change interval in seconds, default is 300s.",
            }
        }
        await self.set_attr_config(attr_config)

        if len(args) != 4:
            return "Usage: define inverter fhempy goodwe IP"

        self.ip = args[3]

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        self.inverter = None
        while self.inverter is None:
            self.inverter = await gw.connect(self.ip)
            await asyncio.sleep(30)

        while True:
            try:
                runtime_data = await self.inverter.read_runtime_data()
                await self.handle_data(runtime_data)
            except Exception:
                await fhem.readingsSingleUpdate(self.hash, "state", "error", 1)
            await asyncio.sleep(self._attr_interval)

    async def handle_data(self, runtime_data):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for sensor in self.inverter.sensors():
                if sensor.id_ in runtime_data:
                    reading = utils.gen_reading_name(sensor.name)
                    if sensor.unit:
                        reading += "_" + sensor.unit
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        reading,
                        runtime_data[sensor.id_],
                    )
            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")
        except Exception:
            self.logger.exception("Failed to update readings")
        await fhem.readingsEndUpdate(self.hash, 1)
