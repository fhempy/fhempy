import asyncio
import time

from fhempy.lib.fusionsolar.fusionsolar_api import FusionSolarRestApi

from .. import fhem, generic, utils

# FusionSolar refreshes its portal data every 5 minutes
DEFAULT_INTERVAL = 300
MIN_INTERVAL = 60


class fusionsolar(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._errors = utils.ErrorLogger(logger)
        self._stationname = None
        self._sessionid = None
        self._attr_interval = DEFAULT_INTERVAL

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        await self.set_attr_config(
            {
                "interval": {
                    "default": DEFAULT_INTERVAL,
                    "format": "int",
                    "help": (
                        f"Update interval in seconds, default {DEFAULT_INTERVAL}, "
                        f"minimum {MIN_INTERVAL}."
                    ),
                }
            }
        )
        if len(argsh) > 0 and argsh[list(argsh)[0]][:4] == "http":
            await fhem.readingsSingleUpdate(
                hash, "state", "Please read HELP to change define", 1
            )
            return

        if not (len(args) == 5 or len(args) == 6):
            return (
                "Usage: define my_solar fhempy fusionsolar "
                "USERNAME PASSWORD [REGION]"
            )

        self._username = args[3]
        self._password = args[4]
        self._region = args[5] if len(args) == 6 else "eu5"

        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.create_async_task(self.update())

    async def update(self):
        max_retries = 10
        retry = 0
        while retry < max_retries:
            self.restapi = FusionSolarRestApi(
                self.logger,
                self._username,
                self._password,
                self._region,
            )
            if await self.restapi.login():
                # we never come back from update_readings
                await self.update_readings()
                retry = 0
            else:
                retry += 1
                await fhem.readingsSingleUpdate(self.hash, "state", "login failed", 1)
                await asyncio.sleep(10)
        await fhem.readingsSingleUpdate(
            self.hash, "state", "login failed, no more retry", 1
        )

    async def update_readings(self):
        while True:
            cycle_start = time.monotonic()
            await fhem.readingsBeginUpdate(self.hash)
            try:
                await self.restapi.update()

                await fhem.readingsBulkUpdate(
                    self.hash, "from_grid_power", self.restapi.from_grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "to_grid_power", self.restapi.to_grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "electrical_load", self.restapi.electrical_load
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "grid_power", self.restapi.grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "inverter_output_power",
                    self.restapi.inverter_output_power,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "string_output_power",
                    self.restapi.string_output_power,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_ratio",
                    self.restapi.daily_self_use_ratio,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "station",
                    self.restapi.station,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "co2_saved",
                    self.restapi.co2_saved,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_energy",
                    self.restapi.daily_self_use_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_solar_ratio",
                    self.restapi.daily_self_use_solar_ratio,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_use_energy",
                    self.restapi.daily_use_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "grid_connected_time",
                    self.restapi.grid_connected_time,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "installed_capacity",
                    self.restapi.installed_capacity,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_day_energy",
                    self.restapi.total_current_day_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_month_energy",
                    self.restapi.total_current_month_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_year_energy",
                    self.restapi.total_current_year_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_lifetime_energy",
                    self.restapi.total_lifetime_energy,
                )

                # battery values
                if self.restapi.battery_soc is not None:
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_soc",
                        self.restapi.battery_soc,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_power",
                        self.restapi.battery_power,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_charge_capacity",
                        self.restapi.battery_charge_capacity,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_discharge_capacity",
                        self.restapi.battery_discharge_capacity,
                    )

                # device signals
                for sig_name in self.restapi.device_signals:
                    await fhem.readingsBulkUpdate(
                        self.hash, sig_name, self.restapi.device_signals[sig_name]
                    )

                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")
                self._errors.success()
            except Exception:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "failed")
                self._errors.failed("Failed to update readings")
                self.logger.debug(f"Received data:\n{self.restapi.data_string}")
            finally:
                await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self.next_update_delay(cycle_start))

    def next_update_delay(self, cycle_start):
        # fixed interval measured from the start of the cycle, so slow
        # requests don't shift the update times
        interval = max(int(self._attr_interval), MIN_INTERVAL)
        return max(interval - (time.monotonic() - cycle_start), 0)
