import asyncio
import time

from fhempy.lib.fusionsolar.fusionsolar_api import FusionSolarRestApi

from .. import fhem, generic, utils

# FusionSolar refreshes its portal data every 5 minutes
DEFAULT_INTERVAL = 300
MIN_INTERVAL = 60
# wait between reconnects, doubled after every failure: FusionSolar can be
# down for hours (maintenance) and too many logins trigger a captcha
RETRY_DELAY_MIN = 30
RETRY_DELAY_MAX = 900
# FusionSolar blocks logins with a captcha for a longer time
CAPTCHA_DELAY_MIN = 3600
CAPTCHA_DELAY_MAX = 7200


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
        if len(argsh) > 0 and argsh[next(iter(argsh))][:4] == "http":
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
        # never give up, the server or the session comes back eventually
        failures = 0
        captchas = 0
        while True:
            self.restapi = FusionSolarRestApi(
                self.logger,
                self._username,
                self._password,
                self._region,
            )
            if await self.restapi.login():
                # returns as soon as an update fails, e.g. expired session
                captchas = 0
                if await self.update_readings():
                    failures = 0
                failures += 1
                state, delay = "failed", self.retry_delay(failures)
            elif self.restapi.captcha_required:
                captchas += 1
                state, delay = "captcha required", self.captcha_delay(captchas)
            else:
                failures += 1
                state, delay = "login failed", self.retry_delay(failures)
            await fhem.readingsSingleUpdate(
                self.hash, "state", f"{state}, reconnect in {delay}s", 1
            )
            await asyncio.sleep(delay)

    @staticmethod
    def retry_delay(failures):
        return min(RETRY_DELAY_MIN * 2 ** min(failures - 1, 10), RETRY_DELAY_MAX)

    @staticmethod
    def captcha_delay(captchas):
        return min(CAPTCHA_DELAY_MIN * 2 ** min(captchas - 1, 10), CAPTCHA_DELAY_MAX)

    async def update_readings(self):
        """Update until a request fails, returns True if any update worked."""
        updated = False
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
                updated = True
            except Exception:
                self._errors.failed("Failed to update readings")
                self.logger.debug(f"Received data:\n{self.restapi.data_string}")
                return updated
            finally:
                await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self.next_update_delay(cycle_start))

    def next_update_delay(self, cycle_start):
        # fixed interval measured from the start of the cycle, so slow
        # requests don't shift the update times
        interval = max(int(self._attr_interval), MIN_INTERVAL)
        return max(interval - (time.monotonic() - cycle_start), 0)
