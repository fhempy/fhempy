import asyncio
import datetime
from aionefit import NefitCore

import re
import math

from .. import fhem, generic


class nefit(generic.FhemModule):

    URL_RRC_UISTATUS = "/ecus/rrc/uiStatus"
    URL_REC_GASUSAGEPOINTER = "/ecus/rrc/recordings/gasusagePointer"
    URL_REC_GASUSAGE = "/ecus/rrc/recordings/gasusage"
    URL_REC_YEARTOTAL = "/ecus/rrc/recordings/yearTotal"
    URL_OUTDOOR_TEMP = "/system/sensors/temperatures/outdoor_t1"
    URL_DAY_STARTSWITH = "/ecus/rrc/dayassunday/day"
    URL_DAY_ACTIVE = "/ecus/rrc/dayassunday/day%DAY%/active"
    URL_DAY_MODE = "/ecus/rrc/dayassunday/day%DAY%/mode"
    URL_DAY_DATE = "/ecus/rrc/dayassunday/day%DAY%/date"
    URL_SYSTEM_PRESSURE = "/system/appliance/systemPressure"

    def __init__(self, logger):
        super().__init__(logger)

        self.first_run = True
        self.module_shutdown = False

        attr_config = {
            "interval": {
                "default": 900,
                "format": "int",
                "help": "Change interval, default is 900.",
            },
            "password": {"default": ""},
            "access_key": {"default": ""},
        }
        self.set_attr_config(attr_config)

        set_config = {
            "mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "params": {"mode": {"default": "clock", "optional": False}},
                "options": "clock,manual",
            },
            "desiredTemp": {
                "args": ["temperature"],
                "params": {"temperature": {"format": "float"}},
                "options": "slider,10,0.5,30,1",
            },
            "dayAsSunday_00_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "0",
            },
            "dayAsSunday_01_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "1",
            },
            "dayAsSunday_02_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "2",
            },
            "dayAsSunday_03_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "3",
            },
            "dayAsSunday_04_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "4",
            },
            "dayAsSunday_05_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "5",
            },
            "dayAsSunday_06_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "6",
            },
            "dayAsSunday_12_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "12",
            },
            "dayAsSunday_07_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "7",
            },
            "dayAsSunday_08_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "8",
            },
            "dayAsSunday_09_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "9",
            },
            "dayAsSunday_10_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "10",
            },
            "dayAsSunday_11_active": {
                "args": ["onoff"],
                "options": "on,off",
                "function": "set_dayassunday_activate",
                "function_param": "11",
            },
            "dayAsSunday_07_date": {
                "args": ["dateval"],
                "function": "set_dayassunday_date",
                "function_param": "7",
            },
            "dayAsSunday_08_date": {
                "args": ["dateval"],
                "function": "set_dayassunday_date",
                "function_param": "8",
            },
            "dayAsSunday_09_date": {
                "args": ["dateval"],
                "function": "set_dayassunday_date",
                "function_param": "9",
            },
            "dayAsSunday_10_date": {
                "args": ["dateval"],
                "function": "set_dayassunday_date",
                "function_param": "10",
            },
            "dayAsSunday_11_date": {
                "args": ["dateval"],
                "function": "set_dayassunday_date",
                "function_param": "11",
            },
            "todayAsSunday": {"args": ["onoff"], "options": "on,off"},
            "tomorrowAsSunday": {"args": ["onoff"], "options": "on,off"},
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define netfit_thermostat fhempy nefit <SERIAL_NUMBER>"

        self._serial_number = args[3]
        hash["SERIAL_NUMBER"] = self._serial_number

        if self._attr_access_key == "" or self._attr_password == "":
            await fhem.readingsBeginUpdate(hash)
            await fhem.readingsBulkUpdateIfChanged(
                hash, "state", "set access_key and password attribute"
            )
            await fhem.readingsEndUpdate(hash, 1)
        else:
            await fhem.readingsSingleUpdateIfChanged(hash, "state", "connecting", 1)
            self.create_async_task(self.nefit_connect())

    async def set_attr_password(self, hash):
        if self._attr_password != "" and self._attr_access_key != "":
            self.create_async_task(self.nefit_connect())

    async def set_attr_access_key(self, hash):
        if self._attr_password != "" and self._attr_access_key != "":
            self.create_async_task(self.nefit_connect())

    async def set_dayassunday_activate(self, hash, params):
        day = params["function_param"]
        onoff = params["onoff"]
        self._nefit_client.put_value(nefit.URL_DAY_ACTIVE.replace("%DAY%", day), onoff)
        await self.update_dayassunday(day)

    async def set_dayassunday_date(self, hash, params):
        day = params["function_param"]
        dateval = params["dateval"]
        self._nefit_client.put_value(nefit.URL_DAY_DATE.replace("%DAY%", day), dateval)
        await self.update_dayassunday(day)

    async def set_desiredTemp(self, hash, params):
        self._nefit_client.set_temperature(params["temperature"])
        self._nefit_client.get(nefit.URL_RRC_UISTATUS)

    async def set_mode(self, hash, params):
        self._nefit_client.set_usermode(params["mode"])
        self._nefit_client.get(nefit.URL_RRC_UISTATUS)

    async def set_todayAsSunday(self, hash, params):
        # call set_dayassunday_activate
        await self.set_dayassunday_activate(
            hash, {"onoff": params["onoff"], "function_param": "11"}
        )
        if params["onoff"] == "on":
            # call set_dayssunday_date
            today = datetime.date.today()
            await self.set_dayassunday_date(
                hash,
                {
                    "dateval": f"{today.month:02d}-{today.day:02d}",
                    "function_param": "11",
                },
            )

    async def set_tomorrowAsSunday(self, hash, params):
        # call set_dayassunday_activate
        await self.set_dayassunday_activate(
            hash, {"onoff": params["onoff"], "function_param": "10"}
        )
        if params["onoff"] == "on":
            # call set_dayssunday_date
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            await self.set_dayassunday_date(
                hash,
                {
                    "dateval": f"{tomorrow.month:02d}-{tomorrow.day:02d}",
                    "function_param": "10",
                },
            )

    async def received_message(self, msg):
        try:
            if msg["id"] == nefit.URL_RRC_UISTATUS:
                await self.handle_uistatus(msg)
            elif msg["id"] == nefit.URL_REC_GASUSAGEPOINTER:
                await self.handle_gasusagepointer(msg)
            elif msg["id"] == nefit.URL_REC_GASUSAGE:
                await self.handle_gasusage(msg)
            elif msg["id"] == nefit.URL_REC_YEARTOTAL:
                await self.handle_yeartotal(msg)
            elif msg["id"] == nefit.URL_OUTDOOR_TEMP:
                await self.handle_outdoortemp(msg)
            elif msg["id"] == nefit.URL_SYSTEM_PRESSURE:
                await self.handle_systempressure(msg)
            elif msg["id"].startswith(nefit.URL_DAY_STARTSWITH):
                await self.handle_dayassunday(msg)
        except Exception:
            self.logger.exception(f"Failed to handle msg: {msg}")

    async def handle_systempressure(self, msg):
        if msg["value"] <= msg["maxValue"] and msg["value"] >= msg["minValue"]:
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "system_pressure", float(msg["value"]) / 10, 1
            )

    async def handle_dayassunday(self, msg):
        day = int(re.findall(r"\d+", msg["id"])[0])
        val_type = re.findall(r"/(\w+)$", msg["id"])[0]
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, f"dayassunday_{day:02d}_{val_type}", msg["value"], 1
        )

    async def handle_outdoortemp(self, msg):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "outdoor_temperature", msg["value"], 1
        )

    async def handle_yeartotal(self, msg):
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "year_total_kwh", msg["value"], 1
        )

    async def handle_gasusage(self, msg):
        entry = msg["value"][self._gasusage_page_entry]
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        if entry["d"] == f"{yesterday.day:02d}-{yesterday.month:02d}-{yesterday.year}":
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "yesterday_consumption_ch", entry["ch"], 1
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "yesterday_consumption_hw", entry["hw"], 1
            )
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "yesterday_temperature", entry["T"] / 10, 1
            )

    async def handle_gasusagepointer(self, msg):
        if msg["value"] < 2:
            # no entry in history yet
            return

        self._gasusage_page = math.ceil((msg["value"] - 2) / 32)
        self._gasusage_page_entry = (msg["value"] - 2) % 32
        self._nefit_client.get(
            nefit.URL_REC_GASUSAGE + "?page=" + str(self._gasusage_page)
        )

    async def handle_uistatus(self, msg):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "ars", msg["value"]["ARS"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "boiler_heating", msg["value"]["BAI"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "boiler_block", msg["value"]["BBE"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "boiler_lock", msg["value"]["BLE"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "boiler_maintainance", msg["value"]["BMR"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "clock_program", msg["value"]["CPM"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "current_switchpoint", msg["value"]["CSP"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "current_time_date", msg["value"]["CTD"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "control", msg["value"]["CTR"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "todayAsSunday", msg["value"]["DAS"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "hot_water", msg["value"]["DHW"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "dot", msg["value"]["DOT"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "esi", msg["value"]["ESI"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temp_in_fahrenheit", msg["value"]["FAH"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "fireplace_mode", msg["value"]["FPA"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "presence_detection_status_device", msg["value"]["HED_DB"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "presence_detection_device", msg["value"]["HED_DEV"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "presence_detection", msg["value"]["HED_EN"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "holiday_mode", msg["value"]["HMD"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "inhouse_status", msg["value"]["IHS"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temperature", msg["value"]["IHT"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "manual_mode_temperature", msg["value"]["MMT"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "pmr", msg["value"]["PMR"]
            )
            await fhem.readingsBulkUpdateIfChanged(self.hash, "rs", msg["value"]["RS"])
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "tomorrowAsSunday", msg["value"]["TAS"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temperature_override_duration", msg["value"]["TOD"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temperature_override", msg["value"]["TOR"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "temperature_override", msg["value"]["TOT"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "desiredTemp", msg["value"]["TSP"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "mode", msg["value"]["UMD"]
            )
        except Exception:
            self.logger.exception("Failed to handle uiStatus")

        await fhem.readingsEndUpdate(self.hash, 1)

    async def nefit_connect(self):
        if self.first_run:
            self._nefit_client = NefitCore(
                self._serial_number,
                self._attr_access_key,
                self._attr_password,
                message_callback=self.received_message,
            )

            self._nefit_client.failed_auth_handler = self.failed_auth_handler
            self._nefit_client.no_content_callback = self.no_content_callback
            self._nefit_client.session_end_callback = self.session_end_callback

        await self._nefit_client.connect()
        await self._nefit_client.xmppclient.connected_event.wait()

        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected", 1)

        if self.first_run:
            self.create_async_task(self.update_loop())
            self.first_run = False

    async def failed_auth_handler(self, event):
        pass

    async def no_content_callback(self, data):
        pass

    async def session_end_callback(self):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "disconnected", 1)
        if not self.module_shutdown:
            await asyncio.sleep(10)
            await self.nefit_connect()

    async def update_loop(self):
        while True:
            try:
                self._nefit_client.get(nefit.URL_RRC_UISTATUS)
                self._nefit_client.get(nefit.URL_REC_YEARTOTAL)
                self._nefit_client.get(nefit.URL_OUTDOOR_TEMP)
                self._nefit_client.get(nefit.URL_SYSTEM_PRESSURE)
                await self.update_dayassunday()

                await self.update_gasusage()
            except Exception:
                self.logger.exception("Failed to update readings")
            try:
                await asyncio.sleep(self._attr_interval)
            except asyncio.CancelledError:
                pass

    async def update_dayassunday(self, day=None):
        if day is None:
            for day in range(13):
                self._nefit_client.get(nefit.URL_DAY_ACTIVE.replace("%DAY%", str(day)))
                self._nefit_client.get(nefit.URL_DAY_DATE.replace("%DAY%", str(day)))
                self._nefit_client.get(nefit.URL_DAY_MODE.replace("%DAY%", str(day)))
        else:
            self._nefit_client.get(nefit.URL_DAY_ACTIVE.replace("%DAY%", str(day)))
            self._nefit_client.get(nefit.URL_DAY_DATE.replace("%DAY%", str(day)))
            self._nefit_client.get(nefit.URL_DAY_MODE.replace("%DAY%", str(day)))

    async def update_gasusage(self):
        self._nefit_client.get(nefit.URL_REC_GASUSAGEPOINTER)

    async def Undefine(self, hash):
        await super().Undefine(hash)
        self.module_shutdown = True
