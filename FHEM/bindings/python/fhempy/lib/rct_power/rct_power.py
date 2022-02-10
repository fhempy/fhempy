import asyncio

from fhempy.lib.rct_power.api import RctPowerApiClient, ValidApiResponse
from rctclient.registry import REGISTRY

from .. import fhem, utils
from .. import generic


class rct_power(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 10,
                "format": "int",
                "help": "Poll interval in seconds, default is 10s.",
            }
        }
        self.set_attr_config(attr_config)

        set_config = {}
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4 or len(args) > 5:
            return "Usage: define my_rct fhempy rct_power IP [PORT]"

        self._hostname = args[3]
        self._port = 8899
        if len(args) == 5:
            self._port = args[4]

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "connecting")
        await fhem.readingsEndUpdate(hash, 1)

        self.create_async_task(self.setup_rct())

    async def setup_rct(self):
        self.rctclient = RctPowerApiClient(
            self.logger, hostname=self._hostname, port=self._port
        )
        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            try:
                await self.update_readings()
            except Exception:
                self.logger.exception("Failed update_readings in loop")
            await asyncio.sleep(self._attr_interval)

    async def update_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            object_ids = []
            for val in [
                "inverter_sn",
                "db.temp1",
                "temperature.sink_temp_power_reduction",
                "battery.soc",
                "battery.cycles",
                "battery.soh",
                "battery.soc_target",
                "battery.soc_target_low",
                "battery.temperature",
                "battery.efficiency",
                "g_sync.p_acc_lp",
                "g_sync.p_ac_grid_sum_lp",
                "g_sync.p_ac_sum_lp",
                "energy.e_ac_day",
                "energy.e_grid_feed_day",
                "energy.e_load_day",
                "energy.e_grid_load_day",
            ]:
                for object_info in REGISTRY.all():
                    if object_info.name == val:
                        object_ids.append(object_info.object_id)

            response = await self.rctclient.async_get_data(object_ids)
            for object_id in response:
                if isinstance(response[object_id], ValidApiResponse):
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        response[object_id].object_name,
                        response[object_id].value,
                    )
                else:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        response[object_id].object_name,
                        response[object_id].cause,
                    )

            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")

        except Exception:
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "connection error")
            self.logger.exception("Failed to update_readings")
        await fhem.readingsEndUpdate(self.hash, 1)
