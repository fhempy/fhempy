import asyncio

from tibber import Tibber

from .. import fhem, generic


class tibber(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.tibber_connection = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 3600,
                "format": "int",
                "help": "Change interval, default is 3600s.",
            }
        }
        await self.set_attr_config(attr_config)

        if len(args) != 4:
            return "Usage: define mytibber fhempy tibber TOKEN"

        self.token = args[3]

        self.create_async_task(self.setup_connection())

    async def setup_connection(self):
        self.tibber_connection = Tibber(self.token, user_agent="fhempy")
        await self.tibber_connection.update_info()
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "tibber_name", self.tibber_connection.name, 1
        )
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "tibber_userid", self.tibber_connection.user_id, 1
        )
        await self.update_home_data()

    def _rt_callback(self, pkg):
        data = pkg.get("data")
        if data is None:
            return
        self.create_async_task(self.update_rt_data(data.get("liveMeasurement")))

    async def update_rt_data(self, data):
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for name in data:
                await fhem.readingsBulkUpdate(self.hash, "rt_" + name, data[name])
        except Exception:
            self.logger.error("Failed to update realtime readings")
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_home_data(self):
        home = self.tibber_connection.get_homes()[0]
        await home.update_info()

        if home.has_real_time_consumption:
            await home.rt_subscribe(self._rt_callback)

        while True:
            try:
                await home.fetch_consumption_data()
                await home.update_info()
                await home.update_price_info()
            except Exception:
                self.logger.error("Failed to update data from tibber, retry in 60s")
                await asyncio.sleep(60)
                continue

            await fhem.readingsBeginUpdate(self.hash)
            try:
                for i, (timestamp, value) in enumerate(home._price_info.items()):
                    # Extracting date and time
                    date, time = timestamp.split('T')
                    time = time.split('+')[0]  # Removing timezone offset
                    hour = time.split(':')[0].lstrip('0')  # Removing leading zero from hour

                    # Determining whether it's today or tomorrow
                    day_key = 'today' if i < 24 else 'tomorrow'

                    # Creating the new key in the desired format
                    new_key = f'{day_key}_{hour.zfill(2)}00'

                    # Assigning the value to the new key in the new dictionary
                    await fhem.readingsBulkUpdate(self.hash, new_key, value)

                await fhem.readingsBulkUpdate(self.hash, "address", home.address1)
                await fhem.readingsBulkUpdate(
                    self.hash, "has_active_subscription", home.has_active_subscription
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "has_production", home.has_production
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "has_real_time_consumption",
                    home.has_real_time_consumption,
                )
                await fhem.readingsBulkUpdate(self.hash, "home_id", home.home_id)
                await fhem.readingsBulkUpdate(self.hash, "month_cons", home.month_cons)
                await fhem.readingsBulkUpdate(self.hash, "month_cost", home.month_cost)
                await fhem.readingsBulkUpdate(self.hash, "home_name", home.name)
                await fhem.readingsBulkUpdate(self.hash, "peak_hour", home.peak_hour)

                # price info
                await fhem.readingsBulkUpdate(
                    self.hash, "current_price_energy", home.current_price_info["energy"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "current_price_tax", home.current_price_info["tax"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "current_price_total", home.current_price_info["total"]
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "current_price_startsat",
                    home.current_price_info["startsAt"],
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "current_price_level", home.current_price_info["level"]
                )
            except Exception:
                self.logger.error("Failed to update readings")
            await fhem.readingsEndUpdate(self.hash, 1)
            await asyncio.sleep(self._attr_interval)

    async def Undefine(self, hash):
        if self.tibber_connection:
            await self.tibber_connection.close_connection()
        return await super().Undefine(hash)
