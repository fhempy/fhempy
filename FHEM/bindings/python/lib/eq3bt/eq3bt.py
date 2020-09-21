
import asyncio
import functools

from bluepy.btle import BTLEException
import eq3bt as eq3

from .. import utils
from .. import fhem

class eq3bt:

    def __init__(self, logger):
        self.logger = logger
        self.set_list_conf = {
            "on": {},
            "off": {},
            "desiredTemperature": {"args": ["target_temp"], "format": "slider,4.5,0.5,29.5,1"},
            "updateStatus": {},
            "boost": {"args": ["target_state"], "format": "on,off"},
            "mode": {"args": ["target_mode"], "format": "manual,automatic"},
            "eco": {},
            "comfort": {},
            "childlock": {"args": ["target_state"], "format": "on,off"}
        }
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self.hash["MAC"] = args[3]
        self.thermostat = FhemThermostat(args[3])
        asyncio.create_task(self.thermostat.update())
        await fhem.readingsSingleUpdate(hash, "state", "offline", 1)
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return await utils.handle_set(self.set_list_conf, self, hash, args, argsh)
    
    async def update_readings(self):
        # TODO update all readings from thermostat device (device, state, schedule)
        return

    # SET Functions BEGIN
    async def set_on(self):
        asyncio.create_task(self.thermostat.activate_comfort())
    
    async def set_off(self):
        asyncio.create_task(self.thermostat.target_temperature(4.5))
    
    async def set_desiredTemperature(self, params):
        asyncio.create_task(self.thermostat.target_temperature(params["target_temp"]))
    
    async def set_updateStatus(self):
        asyncio.create_task(self.thermostat.update())
        # TODO add query_id and query_schedule
    
    async def set_boost(self, params):
        asyncio.create_task(self.thermostat.boost(params["target_state"] == "on"))
    
    async def set_mode(self, params):
        target_mode = params["target_mode"]
        if target_mode == "automatic":
            target_mode = eq3.Mode.Auto
        else:
            target_mode = eq3.Mode.Manual
        asyncio.create_task(self.thermostat.mode(target_mode))
    
    async def set_eco(self):
        asyncio.create_task(self.thermostat.activate_eco())
    
    async def set_comfort(self):
        asyncio.create_task(self.thermostat.activate_comfort())
    
    async def set_childlock(self, params):
        asyncio.create_task(self.thermostat.locked(params["target_state"] == "on"))
    # SET Functions END

    async def start_connection(self, mac):
        await self.thermostat.update()

class FhemThermostat(eq3.Thermostat):

    def __init__(self, mac):
        super(mac)
    
    async def update(self):
        await utils.run_blocking(functools.partial(super().update))
    
    async def query_id(self):
        await utils.run_blocking(functools.partial(super().query_id))
    
    async def query_schedule(self, day):
        await utils.run_blocking(functools.partial(super().query_schedule, day))
    
    async def set_schedule(self, data):
        await utils.run_blocking(functools.partial(super().set_schedule, data))
    
    @target_temperature.setter
    async def target_temperature(self, temperature):
        await utils.run_blocking(functools.partial(super().target_temperature, temperature))

    @mode.setter
    async def mode(self, mode):
        await utils.run_blocking(functools.partial(super().mode, mode))

    @boost.setter
    async def boost(self, boost):
        await utils.run_blocking(functools.partial(super().boost, boost))
    
    @locked.setter
    async def locked(self, lock):
        await utils.run_blocking(functools.partial(super().locked, lock))
    
    @temperature_offset.setter
    async def temperature_offset(self, offset):
        await utils.run_blocking(functools.partial(super().temperature_offset, offset))
    
    async def window_open_config(self, temperature, duration):
        await utils.run_blocking(functools.partial(super().window_open_config, temperature, duration))
    
    async def temperature_presets(self, comfort, eco):
        await utils.run_blocking(functools.partial(super().temperature_presets, comfort, eco))
    
    async def activate_comfort(self):
        await utils.run_blocking(functools.partial(super().activate_comfort))

    async def activate_eco(self):
        await utils.run_blocking(functools.partial(super().activate_eco))