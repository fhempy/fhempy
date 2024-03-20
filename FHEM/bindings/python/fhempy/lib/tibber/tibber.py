import asyncio
import datetime

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
        
        # additional total consumption / production reading
        await fhem.readingsBulkUpdate(self.hash, "rt_powerNet" , data["power"]-data["powerProduction"])
        await fhem.readingsEndUpdate(self.hash, 1)

    async def update_home_data(self):
        home = self.tibber_connection.get_homes()[0]
        await home.update_info()

        if home.has_real_time_consumption:
            await home.rt_subscribe(self._rt_callback)

        self.create_async_task(self.update_current_price_data())
        self.create_async_task(self.update_prices_forPeriods())

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

                
            except Exception:
                self.logger.error("Failed to update readings")
            await fhem.readingsEndUpdate(self.hash, 1)
            
            await asyncio.sleep(self._attr_interval)

    async def update_current_price_data(self):
            """
            Updates the current price data from Tibber API and updates the readings in FHEM.

            This method retrieves the current price information from the Tibber API and updates the corresponding readings
            in FHEM. It continuously fetches the latest price data and updates the readings every new hour.

            Raises:
                Exception: If there is an error updating the data from Tibber API or updating the readings in FHEM.

            """
            home = self.tibber_connection.get_homes()[0]
            
            while True:
                try:
                    await home.update_info()
                    await home.update_price_info()
                except Exception:
                    self.logger.error("Failed to update data from tibber, retry in 60s")
                    await asyncio.sleep(60)
                    continue

                await fhem.readingsBeginUpdate(self.hash)
                try:
                    #  price information incl price rank
                    price, level, time, rank = home.current_price_data()
                   
                    
                    
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
                    await fhem.readingsBulkUpdate(
                        self.hash, "current_price_rank", rank
                    )

                
                except Exception:
                    self.logger.error("Failed to update readings")
                await fhem.readingsEndUpdate(self.hash, 1)
                
                #  update readings every new hour to fetch new current_* data
                now = datetime.datetime.now()
                remaining_seconds = 3600 - (now.minute * 60 + now.second)
                await asyncio.sleep(remaining_seconds+5)

    async def Undefine(self, hash):
        if self.tibber_connection:
            await self.tibber_connection.close_connection()
        return await super().Undefine(hash)
    
    async def update_prices_forPeriods(self):
            """
            Updates the price information for different periods and stores the results in FHEM readings.

            This method retrieves the price information for different periods from the Tibber API and calculates
            the periods with the lowest and highest prices. It then updates the corresponding readings in FHEM.

            Raises:
                Exception: If there is an error updating the data from Tibber or updating the readings in FHEM.

            """
            home = self.tibber_connection.get_homes()[0]
            
            while True:
                try:
                    await home.update_info()
                    await home.update_price_info()
                except Exception:
                    self.logger.error("Failed to update data from tibber, retry in 60s")
                    await asyncio.sleep(60)
                    continue

                await fhem.readingsBeginUpdate(self.hash)
                try:

                    time_list = list(home._price_info.keys())
                    price_list = list(home._price_info.values())
                    now = datetime.datetime.now()

                    # find the index of the element with lowest price today
                    cheapest_price_idx_today = price_list.index(min(price_list[now.hour:24]))    

                    # find the index of the element with lowest price 
                    cheapest_price_idx_total = price_list.index(min(price_list[now.hour:]))

                    # find 3h window with lowest price
                    cheapest_price_3h_idx = min(range(now.hour, len(price_list) - 3), key=lambda i: sum(price_list[i:i+3]))
                    

                    #find 2h window with lowest price
                    cheapest_price_2h_idx = min(range(now.hour, len(price_list) - 2), key=lambda i: sum(price_list[i:i+2]))
                
                    # find the index of the element with highest price today
                    highest_price_idx_today = price_list.index(max(price_list[now.hour:24])) 

                    # find the index of the element with highest price 
                    highest_price_idx_total = price_list.index(max(price_list[now.hour:]))    

                    # find 3h window with highest price
                    highest_price_3h_idx = max(range(now.hour, len(price_list) - 3), key=lambda i: sum(price_list[i:i+3]))

                    #find 2h window with highest price
                    highest_price_2h = max(range(now.hour, len(price_list) - 2), key=lambda i: sum(price_list[i:i+2]))

                    # update readings

                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_today", price_list[cheapest_price_idx_today])
                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_total", price_list[cheapest_price_idx_total])
                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_today_startsAt", datetime.datetime.fromisoformat(time_list[cheapest_price_idx_today]))  
                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_total_startsAt", datetime.datetime.fromisoformat(time_list[cheapest_price_idx_total]))
                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_3h_window_startsAt", datetime.datetime.fromisoformat(time_list[cheapest_price_3h_idx]))
                    await fhem.readingsBulkUpdate(self.hash, "cheapest_price_2h_window_startsAt", datetime.datetime.fromisoformat(time_list[cheapest_price_2h_idx]))
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_today", price_list[highest_price_idx_today])
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_total", price_list[highest_price_idx_total])    
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_today_startsAt", datetime.datetime.fromisoformat(time_list[highest_price_idx_today]))
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_total_startsAt", datetime.datetime.fromisoformat(time_list[highest_price_idx_total]))
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_3h_window_startsAt", datetime.datetime.fromisoformat(time_list[highest_price_3h_idx]))
                    await fhem.readingsBulkUpdate(self.hash, "highest_price_2h_window_startsAt", datetime.datetime.fromisoformat(time_list[highest_price_2h]))


                
                except Exception:
                    self.logger.error("Failed to update readings")
                
                await fhem.readingsEndUpdate(self.hash, 1)
                # get remaining seconds until next full hour 
                remaining_seconds = 3600 - (now.minute * 60 + now.second)
                await asyncio.sleep(remaining_seconds+5)

