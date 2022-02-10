import asyncio

from fhempy.lib.rct_power.api import RctPowerApiClient, ValidApiResponse
from rctclient.registry import REGISTRY
from rctclient.frame import SendFrame
from rctclient.utils import encode_value
from rctclient.types import Command

from .. import fhem, utils
from .. import generic


class rct_power(generic.FhemModule):

    DEFAULT_OBJECTS = [
        "inverter_sn",
        "db.temp1",
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
    ]

    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 10,
                "format": "int",
                "help": "Poll interval in seconds, default is 10s.",
            },
            "device_readings": {
                "default": "",
                "format": "array",
                "help": (
                    "Add further objects/readings which should be retrieved<br>"
                    + "Find details about possible objects here:<br>"
                    + '<a href="https://github.com/svalouch/python-rctclient/'
                    + "blob/67b0f7bc5a8fb6d8b8e15d68d4a24b1d9fb93e48/src/"
                    + 'rctclient/registry.py#L202">Object Infos</a><br><br>'
                    + "Example: battery.bms_sn,battery.bms_power_version"
                ),
            },
            "device_readings_json": {
                "default": "{}",
                "format": "json",
                "options": "textField-long",
                "help": "Advanced JSON configuration<br>"
                + "Example:<br>"
                + "{<br>"
                + '&nbsp;&nbsp;&nbsp;&nbsp;"battery.soc_target": {<br>'
                + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"reading": "battery_soc_target",<br>'
                + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"factor":100<br>'
                + "&nbsp;&nbsp;&nbsp;&nbsp;}<br>"
                + "}",
            },
        }
        self.set_attr_config(attr_config)

        set_config = {"battery_soc_target_high": {"args": ["id", "value"]}}
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

    async def set_battery_soc_target_high(self, hash, params):
        oinfo = REGISTRY.get_by_id(params["id"])
        payload = encode_value(oinfo.request_data_type, params["value"])
        sframe = SendFrame(command=Command.WRITE, id=params["id"], payload=payload)

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
            retrieve_objects = [
                *rct_power.DEFAULT_OBJECTS,
                *self._attr_device_readings,
                *list(self._attr_device_readings_json),
            ]
            for val in retrieve_objects:
                for object_info in REGISTRY.all():
                    if object_info.name == val:
                        object_ids.append(object_info.object_id)

            response = await self.rctclient.async_get_data(object_ids)
            for object_id in response:
                # set reading name from attribute config
                reading = response[object_id].object_name
                if reading in self._attr_device_readings_json:
                    reading = self._attr_device_readings_json[reading].get(
                        "reading", response[object_id].object_name
                    )

                if isinstance(response[object_id], ValidApiResponse):
                    # do factor calculation for float values
                    value = response[object_id].value
                    if isinstance(value, float):
                        factor = self._attr_device_readings_json.get(
                            response[object_id].object_name, {}
                        ).get("factor", 1)
                        value = value * factor
                        value = f"{value:.2f}"

                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        reading,
                        value,
                    )
                else:
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        reading,
                        response[object_id].cause,
                    )

            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")

        except Exception:
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "connection error")
            self.logger.exception("Failed to update_readings")
        await fhem.readingsEndUpdate(self.hash, 1)
