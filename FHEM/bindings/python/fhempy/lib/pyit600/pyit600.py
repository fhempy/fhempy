import asyncio
import logging
import re

from .. import fhem
from .. import generic

from pyit600.exceptions import IT600AuthenticationError, IT600ConnectionError
from pyit600.gateway_singleton import IT600GatewaySingleton

_LOGGER = logging.getLogger(__name__)

class pyit600(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.attr_config = {
            "update_interval": {
                "default": 60,
                "format": "int",
                "help": "Readings update intervall in seconds (default 60s).",
            },
            "update_readings": {
                "default": "always",
                "options": "always,onchange",
                "help": "Update readings only on value change or always (default always).",
            },
            "update_min_interval": {
                "default": 0,
                "format": "int",
                "help": "Update by interval in combination with onchange. Add multiplier (default 0 -> off, e.g. 5 -> 5x update_interval).",
            },
            "readings_device_id": {
                "default": "off",
                "options": "off,on",
                "help": "Create readings with device ID, also if device name is available (default off).",
            },
            "readings_cmpl_dev_str": {
                "default": "on",
                "options": "on,off",
                "help": "Create readings with all values of device (default on).",
            },
        }
        self.set_attr_config(self.attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 5:
            return (
                "Usage: define my_salus_device fhempy pyit600 host euid"
            )
        self.host = args[3]
        self.euid = args[4]
        self.debug = 1
        self.min_interval_timer = 1 
        _LOGGER.debug(f'host: %s, euid: %s',self.host, self.euid)
        self.create_async_task(self.start_login())
        await fhem.readingsSingleUpdate(self.hash, "state", "connecting", 1)

    async def start_login(self):
        async with IT600GatewaySingleton.get_instance(host=self.host, euid=self.euid, debug=self.debug) as self.gateway:
            try:
                _LOGGER.debug(f'start login')
                await self.gateway.connect()
                await self.gateway.poll_status(send_callback=False)
                self.prepare_set_commands()
                await self.update_readings()
            except IT600ConnectionError:
                await fhem.readingsSingleUpdate(self.hash, "state", "Connection error", 1)
                _LOGGER.info(f'Connection error: check if you have specified gateway')
            except IT600AuthenticationError:
                await fhem.readingsSingleUpdate(self.hash, "state", "Authentication error", 1)
                _LOGGER.info(f'Authentication error: check if you have specified gateway EUID is correctly.')

    def prepare_set_commands(self):
        self.set_config = {
            "target_temperature" : {
                "args": ["climate_device_id", "temperature"],
                "params": {
                    "climate_device_id": {"format": "str"},
                    "temperature": {"default": 23, "format": "float"}},
                "help": (
                    "Parameters: deviceID Temperature <br>"
                    "e.g. set my_salus_device target_temperature 001e5e09020770e3 23<br>"
                )
            }
        }
        self.set_set_config(self.set_config)

    async def set_target_temperature(self, hash, params):
        self.create_async_task(
            self.gateway.set_climate_device_temperature(params["climate_device_id"], params["temperature"])
        )

    async def update_readings(self):
        while True:
            _LOGGER.debug(f'update reading')
            await self.update_readings_once()
            await asyncio.sleep(self._attr_update_interval)

    async def update_readings_once(self):
        for remaining_attempts in reversed(range(60)): 
            try:
                await self.gateway.poll_status(send_callback=False)
                break
            except Exception as e:
                if remaining_attempts == 0:
                    await fhem.readingsSingleUpdate(self.hash, "state", "Connection timeout: retrying stopped",1) 
                    raise e
                else:
                    _LOGGER.info(f'Connection timeout - remaining attempts: %d',remaining_attempts)
                    await fhem.readingsSingleUpdate(self.hash, "state", "Connection timeout: retrying ...",1)
                    await asyncio.sleep(self._attr_update_interval)

        try:
            climate_devices = self.gateway.get_climate_devices()

            if not climate_devices:
                await fhem.readingsSingleUpdate(self.hash, "state", "No device found", 1)
            else:
                await fhem.readingsSingleUpdateIfChanged(self.hash, "state", "online", 1)

                if (self._attr_update_readings == "always") or \
                   ((self._attr_update_min_interval > 0) and (self.min_interval_timer >= self._attr_update_min_interval)):
                   
                    self.min_interval_timer = 1
                    
                    for climate_device_id in climate_devices:
                        
                        if self._attr_readings_cmpl_dev_str == "on":
                            await fhem.readingsSingleUpdate(
                                self.hash, climate_device_id, climate_devices.get(climate_device_id), 1)
                                
                        try:
                            name = re.search('name=''(.+?)'',', str(climate_devices.get(climate_device_id))).group(1)
                            name = name.replace(" ", "")
                            name = name.replace("'", "")
                            curtemp = re.search('current_temperature=(.+?),', str(climate_devices.get(climate_device_id))).group(1)
                            
                            if name == 'unknown' or self._attr_readings_device_id == "on":
                                await fhem.readingsSingleUpdate(self.hash, climate_device_id + "_curtemp", curtemp, 1)
                            else:
                                await fhem.readingsSingleUpdate(self.hash, name + "_curtemp", curtemp, 1)
                        except AttributeError:
                            _LOGGER.info(f'Error on reading device name or current temperature!')

                        try:
                            name = re.search('name=''(.+?)'',', str(climate_devices.get(climate_device_id))).group(1)
                            name = name.replace(" ", "")
                            name = name.replace("'", "")
                            targtemp = re.search('target_temperature=(.+?),', str(climate_devices.get(climate_device_id))).group(1)
                            
                            if name == 'unknown' or self._attr_readings_device_id == "on":
                                await fhem.readingsSingleUpdate(self.hash, climate_device_id + "_targtemp", targtemp, 1)
                            else:
                                await fhem.readingsSingleUpdate(self.hash, name + "_targtemp", targtemp, 1)
                        except AttributeError:
                            _LOGGER.info(f'Error on reading device name or target temperature!')

                else:
                    self.min_interval_timer += 1

                    for climate_device_id in climate_devices:
                        if self._attr_readings_cmpl_dev_str == "on":
                            await fhem.readingsSingleUpdateIfChanged(
                                self.hash, climate_device_id, climate_devices.get(climate_device_id), 1)
                                
                        try:
                            name = re.search('name=''(.+?)'',', str(climate_devices.get(climate_device_id))).group(1)
                            name = name.replace(" ", "")
                            name = name.replace("'", "")
                            curtemp = re.search('current_temperature=(.+?),', str(climate_devices.get(climate_device_id))).group(1)
                            
                            if name == 'unknown' or self._attr_readings_device_id == "on":
                                await fhem.readingsSingleUpdateIfChanged(self.hash, climate_device_id + "_curtemp", curtemp, 1)
                            else:
                                await fhem.readingsSingleUpdateIfChanged(self.hash, name + "_curtemp", curtemp, 1)
                        except AttributeError:
                            _LOGGER.info(f'Error on reading device name or current temperature!')

                        try:
                            name = re.search('name=''(.+?)'',', str(climate_devices.get(climate_device_id))).group(1)
                            name = name.replace(" ", "")
                            name = name.replace("'", "")
                            targtemp = re.search('target_temperature=(.+?),', str(climate_devices.get(climate_device_id))).group(1)
                            
                            if name == 'unknown' or self._attr_readings_device_id == "on":
                                await fhem.readingsSingleUpdateIfChanged(self.hash, climate_device_id + "_targtemp", targtemp, 1)
                            else:
                                await fhem.readingsSingleUpdateIfChanged(self.hash, name + "_targtemp", targtemp, 1)
                        except AttributeError:
                            _LOGGER.info(f'Error on reading device name or target temperature!')

        except Exception:
            self.logger.exception("Failed to update readings")
