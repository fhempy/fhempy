
import asyncio

from .. import fhem

class miio:

    def __init__(self, logger):
        self.logger = logger
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        return "Module not ready yet"

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        return ""
