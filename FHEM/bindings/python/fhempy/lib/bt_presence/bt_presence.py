import asyncio
import logging
import bluetooth
import functools
from bt_proximity import BluetoothRSSI

from .. import fhem
from .. import utils


class bt_presence:
    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.btscan_task = None
        self._interval = {"absent": 10, "present": 60}
        self._threshold = {"absent": 0, "present": 0}
        self._curr_state = ""
        self._count_diff_state = 0

    def lookup_name(self, mac):
        return bluetooth.lookup_name(mac, timeout=5)

    async def run_bt_scan(self):
        curr_name = ""
        curr_rssi = 0
        while True:
            new_state = "absent"
            try:
                # check max 3 times for device_name
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
            except:
                self.logger.exception("BleakScanner failed")

            if self._curr_state != new_state:
                self._count_diff_state += 1
                if self._count_diff_state >= self._threshold[new_state]:
                    self._curr_state = new_state
                    self._count_diff_state = 0
                    await self.update_state(self._curr_state)

            await asyncio.sleep(self._interval[self._curr_state])

    async def update_state(self, new_state):
        await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", new_state, 1)
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", new_state, 1)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define p_mysmartphone PythonModule bt_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        await fhem.addToDevAttrList(
            hash["NAME"],
            "absentInterval presentInterval absentThreshold presentThreshold",
        )

        self._interval = {
            "absent": int(await fhem.AttrVal(hash["NAME"], "absentInterval", "60")),
            "present": int(await fhem.AttrVal(hash["NAME"], "presentInterval", "60")),
        }
        self._threshold = {
            "absent": int(await fhem.AttrVal(hash["NAME"], "absentThreshold", "0")),
            "present": int(await fhem.AttrVal(hash["NAME"], "presentThreshold", "0")),
        }

        if self.btscan_task:
            self.btscan_task.cancel()
        self.btscan_task = asyncio.create_task(self.run_bt_scan())
        return ""

    # FHEM FUNCTION
    async def Undefine(self, hash):
        if self.btscan_task:
            self.btscan_task.cancel()

    async def Attr(self, hash, args, argsh):
        cmd = args[0]
        name = args[1]
        attr_name = args[2]
        attr_val = args[3]

        if cmd == "set":
            if attr_name == "absentInterval":
                self._interval["absent"] = int(attr_val)
            elif attr_name == "presentInterval":
                self._interval["present"] = int(attr_val)
            elif attr_name == "absentThreshold":
                self._threshold["absent"] = int(attr_val)
            elif attr_name == "presentThreshold":
                self._threshold["present"] = int(attr_val)
        else:
            if attr_name == "absentInterval":
                self._interval["absent"] = 10
            elif attr_name == "presentInterval":
                self._interval["present"] = 60
            elif attr_name == "absentThreshold":
                self._threshold["absent"] = 0
            elif attr_name == "presentThreshold":
                self._threshold["present"] = 0
