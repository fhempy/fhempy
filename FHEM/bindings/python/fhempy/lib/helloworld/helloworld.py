import asyncio

from .. import fhem, utils
from ..generic import FhemModule


class helloworld(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        attr_config = {
            "interval": {
                "default": 100,
                "format": "int",
                "help": "Change interval, default is 100.",
            }
        }
        self.set_attr_config(attr_config)

        set_config = {
            "mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "params": {"mode": {"default": "eco", "optional": False}},
                "options": "eco,comfort",
            },
            "desiredTemp": {"args": ["temperature"], "options": "slider,10,1,30"},
            "holidayMode": {
                "args": ["endday", "endtime", "temperature"],
                "params": {
                    "endday": {"default": "31.12.2030"},
                    "endtime": {"default": "23:59"},
                    "temperature": {"default": 21, "format": "int"},
                },
            },
            "on": {
                "args": ["seconds"],
                "params": {
                    "seconds": {"default": 0, "optional": True, "format": "int"}
                },
                "help": "Specify seconds as parameter to change to off after X seconds.",
            },
            "off": {},
        }
        self.set_set_config(set_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) > 3:
            return "Usage: define hello_fhempy PythonModule helloworld"
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "on")
        await fhem.readingsEndUpdate(hash, 1)

    # Attribute function format: set_attr_NAMEOFATTRIBUTE(self, hash)
    # self._attr_NAMEOFATTRIBUTE contains the new state
    async def set_attr_interval(self, hash):
        # attribute was set to self._attr_interval
        # you can use self._attr_interval already with the new variable
        pass

    # Set functions in format: set_NAMEOFSETFUNCTION(self, hash, params)
    async def set_on(self, hash, params):
        # params contains the keyword which was defined in set_list_conf for "on"
        # if not provided by the user it will be "" as defined in set_list_conf (default = "" and optional = True)
        seconds = params["seconds"]
        if seconds != 0:
            await fhem.readingsSingleUpdate(hash, "state", "on " + str(seconds), 1)
        else:
            await fhem.readingsSingleUpdate(hash, "state", "on", 1)

    async def set_off(self, hash, params):
        # no params argument here, as set_off doesn't have arguments defined in set_list_conf
        await fhem.readingsSingleUpdate(hash, "state", "off", 1)
        self.create_async_task(self.long_running_task())
        return ""

    async def long_running_task(self):
        await asyncio.sleep(30)
        await fhem.readingsSingleUpdate(self.hash, "state", "long running off", 1)

    async def set_mode(self, hash, params):
        # user can specify mode as mode=eco or just eco as argument
        # params['mode'] contains the mode provided by user
        mode = params["mode"]
        await fhem.readingsSingleUpdate(hash, "mode", mode, 1)

    async def set_desiredTemp(self, hash, params):
        temp = params["temperature"]
        await fhem.readingsSingleUpdate(hash, "mode", temp, 1)

    async def set_holidayMode(self, hash, params):
        start = params["start"]
        end = params["end"]
        temp = params["temperature"]
        await fhem.readingsSingleUpdate(hash, "start", start, 1)
        await fhem.readingsSingleUpdate(hash, "end", end, 1)
        await fhem.readingsSingleUpdate(hash, "temp", temp, 1)
