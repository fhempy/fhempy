import asyncio
import concurrent
import datetime
import functools
import re
import subprocess

import dbus
from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class ble_reset(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._hours = 24
        self._resettask = None
        self._attr_list = {"reset_time": {"default": "04:00", "format": "str"}}
        self.set_attr_config(self._attr_list)
        set_list_conf = {
            "interval": {"args": ["hours"], "options": "1h,2h,4h,8h,12h,24h,manual"},
            "resetnow": {},
        }
        self.set_set_config(set_list_conf)
        return

    def get_hci_ifaces(self):
        iface_list = []
        bus = dbus.SystemBus()
        manager = dbus.Interface(
            bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager"
        )
        objects = manager.GetManagedObjects()
        for path, interfaces in objects.items():
            adapter = interfaces.get("org.bluez.Adapter1")
            if adapter is None:
                continue
            iface_list.append(re.search(r"\d+$", path)[0])
        return iface_list

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        self._reset_time = datetime.datetime.strptime(self._attr_reset_time, "%H:%M")

        hours = await fhem.ReadingsVal(hash["NAME"], "interval", "24h")
        if hours == "manual":
            self._hours = 0
        else:
            self._hours = int(hours[:-1])
            self._resettask = self.create_async_task(self.ble_reset())

        await fhem.readingsBeginUpdate(hash)
        await fhem.readingsBulkUpdateIfChanged(hash, "interval", hours)
        await fhem.readingsBulkUpdateIfChanged(hash, "state", "active")
        await fhem.readingsEndUpdate(hash, 1)

    async def ble_reset(self):
        while True:
            if self._hours > 0:
                now = datetime.datetime.now()
                first_reset = datetime.datetime(
                    now.year,
                    now.month,
                    now.day,
                    self._reset_time.hour,
                    self._reset_time.minute,
                )
                # calculate next reset time
                if (now - first_reset).total_seconds() > 0:
                    next_reset = now + datetime.timedelta(
                        seconds=(self._hours * 3600)
                        - ((now - first_reset).seconds % (self._hours * 3600))
                    )
                else:
                    next_reset = now + datetime.timedelta(
                        seconds=1 + ((first_reset - now).seconds % (self._hours * 3600))
                    )
                await fhem.readingsSingleUpdateIfChanged(
                    self.hash,
                    "nextreset",
                    f"{next_reset.hour:02}:{next_reset.minute:02}",
                    1,
                )
                await asyncio.sleep((next_reset - now).seconds)
            # do reset now
            await self.ble_reset_once()

            now = datetime.datetime.now()
            await fhem.readingsSingleUpdate(
                self.hash, "lastreset", f"{now.hour:02}:{now.minute:02}", 1
            )
            if self._hours == 0:
                return

    async def ble_reset_once(self):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await asyncio.get_event_loop().run_in_executor(
                pool, functools.partial(self.do_ble_reset)
            )
        now = datetime.datetime.now()
        await fhem.readingsSingleUpdate(
            self.hash, "lastreset", f"{now.hour:02}:{now.minute:02}", 1
        )

    def do_ble_reset(self):
        try:
            ifaces = self.get_hci_ifaces()
            subprocess.Popen(["sudo", "systemctl", "restart", "bluetooth"]).wait()
            for iface in ifaces:
                subprocess.Popen(["sudo", "hciconfig", "hci" + iface, "reset"]).wait()
                subprocess.Popen(["sudo", "hciconfig", "hci" + iface, "up"]).wait()
        except Exception:
            self.logger.exception("Failed to reset bluetooth")

    async def set_interval(self, hash, params):
        if self._resettask:
            self._resettask.cancel()

        hours = params["hours"]
        if hours == "manual":
            self._hours = 0
            await fhem.readingsSingleUpdate(hash, "nextreset", "-", 1)
        else:
            self._hours = int(hours[:-1])
        await fhem.readingsSingleUpdate(hash, "interval", hours, 1)

        self._resettask = self.create_async_task(self.ble_reset())

    async def set_resetnow(self, hash, params):
        self.create_async_task(self.ble_reset_once())

    async def set_attr_reset_time(self, hash):
        if self._resettask:
            self._resettask.cancel()
        self._reset_time = datetime.datetime.strptime(self._attr_reset_time, "%H:%M")
        self._resettask = self.create_async_task(self.ble_reset())
