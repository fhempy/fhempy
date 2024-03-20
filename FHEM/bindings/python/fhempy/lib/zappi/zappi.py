import asyncio

from .. import fhem, generic
from pymyenergi.connection import Connection
from pymyenergi.zappi import Zappi
from pymyenergi.harvi import Harvi

class zappi(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.zappi_box = None
        self.harvis = []
        self.harvi_serials = []

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

        set_config = {
            "charge_mode": {
                "args": ["charge_mode"],
                "argsh": ["charge_mode"],
                "params": {"charge_mode": {"default": "Stopped", "optional": False}},
                "options": "Fast,Eco,Eco+,Stopped",
            },
            "green_energy_ratio": {"args": ["green_energy"], "options": "slider,0,10,100"},
            
           
        }
        await self.set_set_config(set_config)

        if len(args) < 5:
            return "Usage: define myZappiBox fhempy zappi serialnumber API_Key [harvi1] [harvi2] ... [harviN] \n [hari1] ... [harviN] are optional harvi serials"
        
        self.serialNo = args[3]
        self.Apikey = args[4]
        
        #get harvi serials from args
        if len(args) > 5:
            self.harvi_serials = args[5:]

        self.create_async_task(self.setup_connection())

    async def setup_connection(self):
            """
            Sets up the connection to the Zappi device and initializes the Zappi and Harvi objects.
            """
                
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connecting",1)

            conn = Connection(self.serialNo, self.Apikey)
            self.zappi_box = Zappi(conn, self.serialNo)
           
            #iterate through harvi serials and create harvi objects
            for serial in self.harvi_serials:
                self.harvis.append(Harvi(conn, serial)) 

            if self.zappi_box != None:
                await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "connected",1)
                await self.zappi_box.refresh()
                            
                await fhem.readingsSingleUpdateIfChanged(self.hash, "zappi_serial", self.zappi_box.serial_number, 1)
                await fhem.readingsSingleUpdateIfChanged(self.hash, "zappi_firmware_version", self.zappi_box.firmware_version, 1)

                # add harvi serial numbers for every single harvi 
                for harvi in self.harvis:
                    await harvi.refresh()
                    harviname = ''.join(e for e in harvi.ct1.name if e.isalnum())
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "harvi_serial_" + harviname, harvi.serial_number, 1)
                    await fhem.readingsSingleUpdateIfChanged(self.hash, "harvi_firmware_" + harviname, harvi.firmware_version, 1)
                
                await self.update_zappi_data()
            else:
                await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "disconnected")

      

    async def set_green_energy_ratio(self, hash, params):
        # update green energy ratio
        green_eng = params["green_energy"]
        await fhem.readingsSingleUpdate(hash, "green_energy_min", green_eng, 1)
        await self.zappi_box.set_minimum_green_level(green_eng)
        
    async def long_running_task(self):
        await asyncio.sleep(30)
        await fhem.readingsSingleUpdate(self.hash, "state", "long running off", 1)

    async def set_charge_mode(self, hash, params):
        # set charge mode
        mode = params["charge_mode"]
        #self.zappi_box.refresh
        await self.zappi_box.set_charge_mode(mode)
        await fhem.readingsSingleUpdate(self.hash, "charge_mode", mode, 1)

   
        

    async def update_zappi_data(self):
            """
            Updates the readings of the Zappi device and its associated Harvi devices.
            """
            while True:
                
                try:
                    await self.zappi_box.refresh()
                    
                    # Update Zappi readings
                    await fhem.readingsBeginUpdate(self.hash)
                    await fhem.readingsBulkUpdate(self.hash, "operating_status", self.zappi_box.status)
                    await fhem.readingsBulkUpdate(self.hash, "plug_status", self.zappi_box.plug_status)
                    await fhem.readingsBulkUpdate(self.hash, "green_energy_min", self.zappi_box.minimum_green_level)
                    await fhem.readingsBulkUpdate(self.hash, "green_energy_total", self.zappi_box.energy_green)
                    await fhem.readingsBulkUpdate(self.hash, "energy_total", self.zappi_box.energy_total)
                    await fhem.readingsBulkUpdate(self.hash, "energy_today", self.zappi_box.energy_total)
                    await fhem.readingsBulkUpdate(self.hash, "firmware_update_available", self.zappi_box.update_available)
                    await fhem.readingsBulkUpdate(self.hash, "charge_mode", self.zappi_box.charge_mode)
                    await fhem.readingsBulkUpdate(self.hash, "locked", self.zappi_box.locked)
                    await fhem.readingsBulkUpdate(self.hash, "lock_when_plugged", self.zappi_box.lock_when_pluggedin)
                    await fhem.readingsBulkUpdate(self.hash, "lock_when_unplugged", self.zappi_box.lock_when_unplugged)
                    await fhem.readingsBulkUpdate(self.hash, "charge_when_locked", self.zappi_box.charge_when_locked)
                    await fhem.readingsBulkUpdate(self.hash, "charge_session_allowed", self.zappi_box.charge_session_allowed)
                    await fhem.readingsBulkUpdate(self.hash, "power_grid", self.zappi_box.power_grid)
                    await fhem.readingsBulkUpdate(self.hash, "power_generated", self.zappi_box.power_generated)
                    await fhem.readingsBulkUpdate(self.hash, "smart_boosted_energy", self.zappi_box.boost_amount)
                    await fhem.readingsBulkUpdate(self.hash, "power_ct1", self.zappi_box.ct1.power)
                    await fhem.readingsBulkUpdate(self.hash, "power_ct2", self.zappi_box.ct2.power)
                    await fhem.readingsBulkUpdate(self.hash, "power_ct3", self.zappi_box.ct3.power)
                    await fhem.readingsBulkUpdate(self.hash, "power_total", self.zappi_box.ct1.power + self.zappi_box.ct2.power + self.zappi_box.ct3.power)

                    # Iterate over the Harvi devices and update readings
                    for harvi in self.harvis:
                        await harvi.refresh()
                        harviname = ''.join(e for e in harvi.ct1.name if e.isalnum())
                        await fhem.readingsBulkUpdate(self.hash, harviname + "_CT1", harvi.ct1.power)
                        await fhem.readingsBulkUpdate(self.hash, harviname + "_CT2", harvi.ct2.power)
                        await fhem.readingsBulkUpdate(self.hash, harviname + "_CT3", harvi.ct3.power)
                        
                       
                    """
                    if self.zappi_box.smart_boost_start_hour > -1:
                        smartBoostStart = self.zappi_box.smart_boost_start_hour + ":" + self.zappi_box.smart_boost_start_minute
                        await fhem.readingsBulkUpdate(self.hash, "smart_boost_start",  smartBoostStart)
                    else:
                        await fhem.readingsBulkUpdate(self.hash, "smart_boost_start",  "not set")
                    """
                    await fhem.readingsBulkUpdate(self.hash, "smart_boost_amount", self.zappi_box.smart_boost_amount)
                    await fhem.readingsEndUpdate(self.hash, 1)
                except Exception:
                    self.logger.error("Failed to update zappi readings")
                    
                
                
                await asyncio.sleep(self._attr_interval)

    