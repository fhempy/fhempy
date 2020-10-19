
import asyncio
import concurrent
import dbus
import functools
import re
import subprocess

from .. import fhem, utils


class ble_reset:

    def __init__(self, logger):
        self.logger = logger
        self._hours = 24
        self._resettask = None
        return

    def get_hci_ifaces(self):
        iface_list = []
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()
        for path, interfaces in objects.items():
            adapter = interfaces.get("org.bluez.Adapter1")
            if adapter is None:
                continue
            iface_list.append(re.search(r'\d+$', path)[0])
        return iface_list

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        hours = await fhem.ReadingsVal(hash['NAME'], "interval", "24h")
        if hours == "manual":
            self._hours = 0
        else:
            self._hours = int(hours[:-1])
            self._resettask = asyncio.create_task(self.ble_reset())

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "interval", hours)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "active")
        await fhem.readingsEndUpdate(hash, 1)
        return ""

    async def ble_reset(self):
        while True:
            if self._hours > 0:
                await asyncio.sleep(3600 * self._hours)
            with concurrent.futures.ThreadPoolExecutor() as pool:
                await asyncio.get_event_loop().run_in_executor(
                    pool, functools.partial(self.do_ble_reset))
            if self._hours == 0:
                return

    def do_ble_reset(self):
        try:
            ifaces = self.get_hci_ifaces()
            subprocess.Popen(["sudo", "systemctl", "restart", "bluetooth"]).wait()
            for iface in ifaces:
                subprocess.Popen([
                    "sudo", "hciconfig", "hci" + iface, "reset"]).wait()
        except:
            self.logger.exception("Failed to reset bluetooth")

    async def Undefine(self, hash):
        if self._resettask:
            self._resettask.cancel()

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        set_list_conf = {
           "interval": { "args": ["hours"], "format": "1h,2h,4h,8h,12h,24h,manual" },
           "resetnow": {}
        }
        return await utils.handle_set(set_list_conf, self, hash, args, argsh)

    async def set_interval(self, hash, params):
        if self._resettask:
            self._resettask.cancel()

        hours = params['hours']
        if hours == "manual":
            self._hours = 0
        else:
            self._hours = int(hours[:-1])
        await fhem.readingsSingleUpdate(hash, "interval", hours, 1)

        self._resettask = asyncio.create_task(self.ble_reset())

    async def set_resetnow(self, hash):
        asyncio.create_task(self.ble_reset())
