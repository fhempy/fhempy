import asyncio
from datetime import datetime

from .. import fhem, generic


USAGE = "Usage: define hello_fhempy fhempy helloworld"
MODES = ("eco", "comfort")
MIN_TEMPERATURE = 10
MAX_TEMPERATURE = 30


# A callable format converts and validates input before any handler runs.
# Return the value or raise ValueError with an explanation for the user.
def _integer(value, minimum=0, maximum=None):
    try:
        number = int(value)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("expected a whole number") from None
    if maximum is not None and not minimum <= number <= maximum:
        raise ValueError(f"expected {minimum} to {maximum}")
    if number < minimum:
        raise ValueError(f"expected at least {minimum}")
    return number


def _mode(value):
    if value not in MODES:
        raise ValueError("choose " + " or ".join(MODES))
    return value


def _positive_integer(value):
    return _integer(value, minimum=1)


def _temperature(value):
    return _integer(value, minimum=MIN_TEMPERATURE, maximum=MAX_TEMPERATURE)


def _endday(value):
    try:
        datetime.strptime(value, "%d.%m.%Y")
    except (ValueError, TypeError):
        raise ValueError("expected a valid date (DD.MM.YYYY)") from None
    return value


def _endtime(value):
    try:
        datetime.strptime(value, "%H:%M")
    except (ValueError, TypeError):
        raise ValueError("expected a valid time (HH:MM, 00:00 to 23:59)") from None
    return value


class helloworld(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

    @staticmethod
    def validate_define(args, argsh):
        """Check arguments without I/O, before a running device is undefined."""
        if len(args) != 3 or argsh:
            return USAGE
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        # Reuse the binding's validation hook for direct Define calls, too.
        error = self.validate_define(args, argsh)
        if error:
            return error
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 100,
                "format": _positive_integer,
                "help": "<b>interval</b><br>Positive whole seconds, default: 100.",
            }
        }
        await self.set_attr_config(attr_config)

        temperature_help = (
            f"Whole degrees from {MIN_TEMPERATURE} to {MAX_TEMPERATURE}."
        )
        set_config = {
            "mode": {
                "args": ["mode"],
                "argsh": ["mode"],
                "params": {"mode": {"default": MODES[0], "format": _mode}},
                "options": ",".join(MODES),
                "help": "<b>mode</b><br>Select " + " or ".join(MODES) + ".",
            },
            "desiredTemp": {
                "args": ["temperature"],
                "params": {"temperature": {"format": _temperature}},
                "options": f"slider,{MIN_TEMPERATURE},1,{MAX_TEMPERATURE}",
                "help": "<b>desiredTemp</b><br>" + temperature_help,
            },
            "holidayMode": {
                "args": ["endday", "endtime", "temperature"],
                "params": {
                    "endday": {"default": "31.12.2030", "format": _endday},
                    "endtime": {"default": "23:59", "format": _endtime},
                    "temperature": {"default": 21, "format": _temperature},
                },
                "help": (
                    "<b>holidayMode [endday [endtime [temperature]]]</b><br>"
                    "Enter space-separated values in the input field: "
                    "end date (DD.MM.YYYY), end time (HH:MM), temperature.<br>"
                    f"{temperature_help}<br>"
                    "Example: <code>24.12.2030 18:30 19</code>.<br>"
                    "Omitted trailing values use their configured defaults. "
                    "This example only updates readings; it does not schedule heating."
                ),
            },
            "on": {
                "args": ["seconds"],
                "params": {
                    "seconds": {"default": 0, "format": _integer}
                },
                "help": (
                    "<b>on [seconds]</b><br>"
                    "Show the optional duration in state (whole seconds, at least 0). "
                    "This example does not switch off automatically."
                ),
            },
            "off": {
                "help": (
                    "<b>off</b><br>Set state to off and start a background task "
                    "which updates state again later."
                ),
            },
        }
        await self.set_set_config(set_config)

        get_config = {
            "info": {
                "help": "<b>info</b><br>Show the device state and configured interval.",
            },
            "help": {
                "help": "<b>help</b><br>List the Define usage, commands and attributes.",
            },
        }
        await self.set_get_config(get_config)

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
        # Omitted seconds use the configured default, converted to an integer.
        seconds = params["seconds"]
        if seconds != 0:
            await fhem.readingsSingleUpdate(hash, "state", "on " + str(seconds), 1)
        else:
            await fhem.readingsSingleUpdate(hash, "state", "on", 1)

    async def set_off(self, hash, params):
        # params is an empty dict because off has no configured arguments.
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
        await fhem.readingsSingleUpdate(hash, "desiredTemp", temp, 1)

    async def set_holidayMode(self, hash, params):
        await fhem.readingsBeginUpdate(hash)
        try:
            for reading in ("endday", "endtime", "temperature"):
                await fhem.readingsBulkUpdate(hash, reading, params[reading])
        finally:
            await fhem.readingsEndUpdate(hash, 1)

    # Get handlers use the same (hash, params) signature as Set handlers.
    async def get_info(self, hash, params):
        state = await fhem.ReadingsVal(hash["NAME"], "state", "unknown")
        return (
            f"Device: {hash['NAME']}\n"
            f"State: {state}\n"
            f"Interval: {self._attr_interval} seconds"
        )

    # A handler without asynchronous work can be a regular function.
    def get_help(self, hash, params):
        return "\n".join([
            USAGE,
            "Set commands: " + ", ".join(self._conf_set),
            "Get commands: " + ", ".join(self._conf_get),
            "Attributes: " + ", ".join(self._conf_attr),
        ])
