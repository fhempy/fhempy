import asyncio

from .. import fhem, generic
from alphaess.alphaess import alphaess
from datetime import date, timedelta

class alphaesscloud(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.appID = None
        self.appSecret = None
        self.serial = None
        self.ESSunit = None
        self.client = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        
        attr_config = {
            "interval": {
                "default": 60,
                "format": "int",
                "help": "Change interval, default is 60.",
            }
        }
        await self.set_attr_config(attr_config)

        if len(args) !=6:
            return "Usage: define myAlphaESSCloud fhempy alphaesscloud appID appSecret serial"
        
        self.appID = args[3]
        self.appSecret = args[4]
        self.serial = args[5]
        
        self.create_async_task(self.setup_connection())

    async def setup_connection(self):
            """
            Sets up the connection to the AlphaESS cloud and retrieves necessary information.

            This method connects to the AlphaESS cloud using the provided app ID and app secret.
            It retrieves the list of ESS units associated with the account and checks if the
            specified serial number matches any of the units. If a match is found, it updates
            the state to "connected" and updates the readings from the unit's item list.

            If the serial number does not match any of the units, it updates the state to
            "ESS unit not found please check serial number".

            Additionally, it retrieves the discharging and charging configuration information
            for the ESS unit and updates the readings accordingly.

            Finally, it kicks off the routine to update the data from the cloud continuously.

            Returns:
                None
            """
               
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connecting",1)

            self.client: alphaess = alphaess(self.appID,self.appSecret)
            ESSList = await self.client.getESSList()
            if ESSList != None:
                self.logger.error(f"Retrieved: {len(ESSList)} ESS units")
            else:
                await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "no ESS units found ",1)

            for unit in ESSList:
                if "sysSn" in unit:
                    if unit["sysSn"] == self.serial:
                        self.ESSunit = unit
                        
                        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected",1)
                        await self.update_readings_from_itemlist(unit)
                        break

            if self.ESSunit == None:
                await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "ESS unit not found please check serial number",1)
                return
            
            dischargingInfo = await self.client.getDisChargeConfigInfo(self.serial)
            if dischargingInfo != None:
                await self.update_readings_from_itemlist(dischargingInfo)
            else:
                self.logger.error("No discharging info found")

            chargingInfo = await self.client.getChargeConfigInfo(self.serial)
            if chargingInfo != None:
                await self.update_readings_from_itemlist(chargingInfo)
            else:
                self.logger.error("No charging info found")

            await self.update_data_from_cloud()



      

    

    async def update_data_from_cloud(self):
            """
            Updates the data from the cloud for the AlphaESS device.

            This method continuously retrieves data from the cloud for the specified AlphaESS device.
            It retrieves the sum data and last power data from the cloud and updates the readings in FHEM.
            If an exception occurs during the update process, the state reading is updated to indicate the failure.

            
            Returns:
            None
            """
            while True:
                try:
                    sumData = await self.client.getSumDataForCustomer(self.serial)
                    if sumData != None:
                        await self.update_readings_from_itemlist(sumData)

                    lastPower = await self.client.getLastPowerData(self.serial)
                    if lastPower != None:
                        await self.update_readings_from_itemlist(lastPower)

                except Exception:
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "data update failed", 1)

                if self._attr_interval > 10:
                    await asyncio.sleep(self._attr_interval)
                else:
                    await asyncio.sleep(10)

    async def update_readings_from_itemlist(self, itemlist):
            """
            Updates the readings from the given itemlist via a bluk update.

            Args:
                itemlist (dict): A dictionary containing the readings to be updated.

            Returns:
                None
            """
            await fhem.readingsBeginUpdate(self.hash)
            for key, value in itemlist.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        await fhem.readingsBulkUpdate(self.hash, sub_key, sub_value)
                else:
                        await fhem.readingsBulkUpdate(self.hash, key, value)
            await fhem.readingsEndUpdate(self.hash, 1)


    
