import asyncio
import functools

from micloud import MiCloud

from .. import utils
from .. import fhem


class xiaomi_tokens:
    def __init__(self, logger):
        self.logger = logger
        self._username = None
        self._password = None
        self._country = "de"
        return

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await fhem.readingsSingleUpdateIfChanged(hash, "state", "active", 1)
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash):
        return

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        set_list_conf = {
            "username": {"args": ["username"]},
            "password": {"args": ["password"]},
            "country": {"args": ["country"], "options": "de,cn,sg"},
            "get_tokens": {},
        }
        return await utils.handle_set(set_list_conf, self, hash, args, argsh)

    async def set_username(self, hash, params):
        self._username = params["username"]
        return ""

    async def set_password(self, hash, params):
        self._password = params["password"]
        return ""

    async def set_country(self, hash, params):
        self._country = params["country"]
        return ""

    async def set_get_tokens(self, hash):
        if self._username and self._password:
            asyncio.create_task(self.obtain_tokens())
        else:
            return "Please set username & password first!"

    async def obtain_tokens(self):
        await utils.run_blocking(functools.partial(self.thread_get_tokens))
        await fhem.readingsBeginUpdate(self.hash)
        for dev in self._device_list:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_name", dev["name"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_token", dev["token"]
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, dev["did"] + "_model", dev["model"]
            )
        await fhem.readingsEndUpdate(self.hash, 1)

    def thread_get_tokens(self):
        mc = MiCloud(self._username, self._password)
        mc.login()
        self._device_list = mc.get_devices(country=self._country)
