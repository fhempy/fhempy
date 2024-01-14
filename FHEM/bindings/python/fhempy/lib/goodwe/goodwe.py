import asyncio

import goodwe as gw
from goodwe.inverter import OperationMode

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

        set_config = {
            "operation_mode": {
                "args": ["mode"],
                "options": "general,off_grid,backup,eco,peak_shaving,eco_charge,eco_discharge",
                "help": "Change operations mode of the inverter.",
            }
        }
        await self.set_set_config(set_config)

        if len(args) != 4:
            return "Usage: define inverter fhempy goodwe IP"

        self.ip = args[3]

        self.create_async_task(self.update_loop())

    async def set_operation_mode(self, hash, params):
        if params["mode"] == "general":
            set_mode = OperationMode.GENERAL
        elif params["mode"] == "off_grid":
            set_mode = OperationMode.OFF_GRID
        elif params["mode"] == "backup":
            set_mode = OperationMode.BACKUP
        elif params["mode"] == "eco":
            set_mode = OperationMode.ECO
        elif params["mode"] == "peak_shaving":
            set_mode = OperationMode.PEAK_SHAVING
        elif params["mode"] == "eco_charge":
            set_mode = OperationMode.ECO_CHARGE
        elif params["mode"] == "eco_discharge":
            set_mode = OperationMode.ECO_DISCHARGE
        else:
            set_mode = OperationMode.GENERAL
        self.create_async_task(
            self.inverter.set_operation_mode(
                set_mode
            )
        )

    def get_enum_name(self, enum_value):
        for name, value in OperationMode.__members__.items():
            if value == enum_value:
                return name

    async def update_loop(self):
        self.inverter = None
        while self.inverter is None:
            self.inverter = await gw.connect(self.ip)
            await asyncio.sleep(30)

        while True:
            try:
                runtime_data = await self.inverter.read_runtime_data()
                await self.handle_data(runtime_data)

                operation_mode = await self.inverter.get_operation_mode()
                await fhem.readingsSingleUpdate(self.hash, "operation_mode", self.get_enum_name(operation_mode))
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
