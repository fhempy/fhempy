
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from .. import fhem

class helloworld:

    def __init__(self):
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "on")
        await fhem.readingsBulkUpdateIfChanged(hash, "hello", "world")
        await fhem.readingsEndUpdate(hash, 1)
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash, args, argsh):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        if (len(args) < 2 or args[1] == "?"):
            return ("Unknown argument ?, choose one of "
                    "on:noArg off:noArg")
        else:
            action = args[1]
            if (action == "on"):
                await fhem.readingsSingleUpdate(hash, "state", "on", 1)
            else:
                await fhem.readingsSingleUpdate(hash, "state", "off", 1)
