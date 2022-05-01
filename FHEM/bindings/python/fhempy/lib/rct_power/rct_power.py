import asyncio

from fhempy.lib.rct_power.api import RctPowerApiClient, ValidApiResponse
from rctclient.registry import REGISTRY

from .. import fhem
from .. import generic


class rct_power(generic.FhemModule):

    DEFAULT_OBJECTS = [
        "inverter_sn",
        "db.temp1",
        "battery.soc",
        "battery.soc_target",
        "battery.cycles",
        "battery.soh",
        "power_mng.soc_max",
        "power_mng.soc_min",
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

        self.update_loop_task = None

        attr_config = {
            "interval": {
                "default": 10,
                "format": "int",
                "help": "Poll interval in seconds, default is 10s.",
            },
            "disable": {
                "default": 0,
                "format": "int",
                "options": "0,1",
            },
            "update_readings": {
                "default": "on_change",
                "options": "always,on_change",
            },
            "default_device_readings": {
                "default": "on",
                "help": "When off only readings defined in device_readings and device_readings_json are updated.",
            },
            "error_reading": {
                "default": "on",
                "help": "Use separate error reading.",
            },
            "device_readings": {
                "default": "",
                "format": "array",
                "help": (
                    "Add further objects/readings which should be retrieved<br>"
                    + "Find details about possible objects here:<br>"
                    + '<a href="https://rctclient.readthedocs.io/en/latest/'
                    + "inverter_registry.html"
                    + '">Object Infos</a><br><br>'
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
                + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"format":".2f"<br>'
                + "&nbsp;&nbsp;&nbsp;&nbsp;}<br>"
                + "}",
            },
        }
        self.set_attr_config(attr_config)

        set_config = {
            "display_brightness": {
                "args": ["value"],
                "params": {"value": {"format": "int"}},
                "help": "Display brightness [-] display_struct.brightness",
                "options": "slider,0,1,255",
                "function": "set_rct_write",
                "function_param": 0x29BDA75F,
            },
            "display_contrast": {
                "args": ["value"],
                "params": {"value": {"format": "int"}},
                "help": "Display contrast [-] display_struct.contrast",
                "options": "slider,0,1,255",
                "function": "set_rct_write",
                "function_param": 0xF247BB16,
            },
            "max_compensation_power": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum compensation power from battery [W].<br>Registry: p_rec_lim[0]",
                "options": "slider,0,1,10000",
                "function": "set_rct_write",
                "function_param": 0x85886E2E,
            },
            "max_power_batt2grid": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Battery power to grid limitation [W] (normally 0).<br>Registry: p_rec_lim[1]",
                "options": "slider,0,1,10000",
                "function": "set_rct_write",
                "function_param": 0x54829753,
            },
            "max_power_ac": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum inverter AC power [W].<br>Registry: p_rec_lim[2]",
                "options": "slider,0,1,10000",
                "function": "set_rct_write",
                "function_param": 0x9A67600D,
            },
            "battmng_kreserve": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Reserve coefficent for battery power management [-] Higher values = lower battery SoC (higher reserve). Decimal values from 0.00 - 2.00 are allowed.<br>Registry: bat_mng_struct.k_reserve",
                "function": "set_rct_write",
                "function_param": 0xF644DCA7,
            },
            "battmng_ktrust": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Time constant for battery power management [Seconds] Lower values = faster reaction on weather prediction. Decimal values from 0.00 - 1000 are allowed.<br>Registry: bat_mng_struct.k_trust",
                "function": "set_rct_write",
                "function_param": 0xB2FB9A90,
            },
            "batt_soc_min": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Minimum battery SoC target [-]. Decimal values from 0.00 - 1.00 are allowed.<br>Registry: power_mng.soc_min",
                "function": "set_rct_write",
                "function_param": 0xCE266F0F,
            },
            "batt_soc_max": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": (
                    "Maximum battery SoC target [-]. Decimal values from 0.00 - 1.00 are allowed."
                    "<br>Registry: power_mng.soc_max"
                ),
                "function": "set_rct_write",
                "function_param": 0x97997C93,
            },
            "conv_max_current": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum battery converter current (charge/discharge) [A]. Decimal values from 0.00 - 25.00 are allowed.<br>Registry: acc_conv.i_max",
                "function": "set_rct_write",
                "function_param": 0xE3F4D1DF,
            },
            "conv_max_dischargecurrent": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum battery discharge current [A]. Decimal values from 0.00 - 25.00 are allowed.<br>Registry: acc_conv.i_discharge_max",
                "function": "set_rct_write",
                "function_param": 0xC642B9D6,
            },
            "conv_max_chargecurrent": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum battery charge current [A]. Decimal values from 0.00 - 25.00 are allowed.<br>Registry: acc_conv.i_charge_max",
                "function": "set_rct_write",
                "function_param": 0xB0FA4D23,
            },
            "max_power_ac": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Maximum inverter AC power [W]. Decimal values from 0 - 10000 are allowed.<br>Registry: p_rec_lim[2]",
                "function": "set_rct_write",
                "function_param": 0x9A67600D,
            },
            "min_soc_maint_charge": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Min SoC for start maintenance charging [-]. Decimal values from 0.00 - 1.00 are allowed.<br>Registry: power_mng.soc_charge",
                "function": "set_rct_write",
                "function_param": 0xBD3A23C3,
            },
            "plant_power_reduction": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Regulatory power limitation of plant. Germany=0.7 [-]. Decimal values from 0.00 - 1.00 are allowed.<br>Registry: buf_v_control.power_reduction",
                "function": "set_rct_write",
                "function_param": 0xFE1AA500,
            },
            "max_power_batt2grid": {
                "args": ["value"],
                "params": {"value": {"format": "float"}},
                "help": "Battery power to grid limitation [W] (normally 0).<br>Registry: p_rec_lim[1]",
                "options": "slider,0,1,10000",
                "function": "set_rct_write",
                "function_param": 0x54829753,
            },
        }
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

    async def set_rct_write(self, hash, params):
        self.create_async_task(
            self.rctclient.async_send_data(params["function_param"], params["value"])
        )

    async def set_attr_disable(self, hash):
        if self._attr_disable == 1:
            self.cancel_async_task(self.update_loop_task)
            self.update_loop_task = None
        else:
            if self.update_loop_task is not None:
                self.update_loop_task = self.create_async_task(self.update_loop())

    async def setup_rct(self):
        self.rctclient = RctPowerApiClient(
            self.logger, hostname=self._hostname, port=self._port
        )
        self.update_loop_task = self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            if self._attr_disable == 1:
                return

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
                *self._attr_device_readings,
                *list(self._attr_device_readings_json),
            ]
            if self._attr_default_device_readings == "on":
                retrieve_objects = [
                    *rct_power.DEFAULT_OBJECTS,
                    *retrieve_objects,
                ]
            for val in retrieve_objects:
                for object_info in REGISTRY.all():
                    if object_info.name == val:
                        object_ids.append(object_info.object_id)

            response = await self.rctclient.async_get_data(object_ids)
            for object_id in response:
                if self._attr_error_reading == "on":
                    await fhem.readingsBulkUpdateIfChanged(
                        self.hash,
                        "error",
                        "",
                    )
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
                        format = self._attr_device_readings_json.get(
                            response[object_id].object_name, {}
                        ).get("format", ".2f")
                        value = f"{value:{format}}"

                    await self.readingsBulkUpdate(
                        self.hash,
                        reading,
                        value,
                    )
                else:
                    if self._attr_error_reading == "on":
                        await self.readingsBulkUpdate(
                            self.hash,
                            "error",
                            f"{reading} failed with {response[object_id].cause}",
                        )
                    else:
                        await self.readingsBulkUpdate(
                            self.hash,
                            reading,
                            response[object_id].cause,
                        )

            await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")

        except Exception:
            await fhem.readingsBulkUpdateIfChanged(hash, "state", "connection error")
            self.logger.exception("Failed to update_readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def readingsBulkUpdate(self, hash, reading, value):
        if self._attr_update_readings == "always":
            await fhem.readingsBulkUpdate(hash, reading, value)
        else:
            await fhem.readingsBulkUpdateIfChanged(hash, reading, value)
