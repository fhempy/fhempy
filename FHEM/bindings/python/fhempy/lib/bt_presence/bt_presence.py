import asyncio
import functools
import logging

import bluetooth
from bt_proximity import BluetoothRSSI
from fhempy.lib.generic import FhemModule

from .. import fhem, utils


class bt_presence(FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.btscan_task = None
        self._curr_state = ""
        self._count_diff_state = 0
        attr_config = {
            "absentInterval": {"default": 10, "format": "int"},
            "presentInterval": {"default": 60, "format": "int"},
            "absentThreshold": {"default": 0, "format": "int"},
            "presentThreshold": {"default": 0, "format": "int"},
        }
        self.set_attr_config(attr_config)

    def lookup_name(self, mac):
        return bluetooth.lookup_name(mac, timeout=5)

    async def run_bt_scan(self):
        curr_name = ""
        curr_rssi = 0
        while True:
            new_state = "absent"
            try:
                # check max 3 times for device_name
                device_name = None
                for i in range(0, 2):
                    device_name = await utils.run_blocking(
                        functools.partial(self.lookup_name, self._address)
                    )
                    if device_name:
                        break

                if device_name:
                    self._btrssi = BluetoothRSSI(self._address)
                    rssi = await utils.run_blocking(
                        functools.partial(self._btrssi.request_rssi)
                    )
                    self._btrssi.close()
                    rssi = rssi[0]
                    if curr_name != device_name:
                        curr_name = device_name
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "name", device_name, 1
                        )
                    if curr_rssi != rssi:
                        curr_rssi = rssi
                        await fhem.readingsSingleUpdateIfChanged(
                            self.hash, "rssi", rssi, 1
                        )
                    new_state = "present"
            except Exception:
                self.logger.exception("BleakScanner failed")

            if self._curr_state != new_state:
                self._count_diff_state += 1
                if new_state == "present":
                    threshold = self._attr_presentThreshold
                else:
                    threshold = self._attr_absentThreshold
                if self._count_diff_state >= threshold:
                    self._curr_state = new_state
                    self._count_diff_state = 0
                    await self.update_state(self._curr_state)

            if self._curr_state == "present":
                interval = self._attr_presentInterval
            else:
                interval = self._attr_absentInterval
            await asyncio.sleep(interval)

    async def update_state(self, new_state):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", new_state, 1)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", new_state, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) < 4:
            return "Usage: define p_mysmartphone fhempy bt_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        if self.btscan_task:
            self.btscan_task.cancel()
        self.btscan_task = self.create_async_task(self.run_bt_scan())
