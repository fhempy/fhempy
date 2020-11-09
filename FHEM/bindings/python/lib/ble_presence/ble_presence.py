
import asyncio
import logging
import time

import aioblescan as aiobs

from .. import fhem

class ble_presence:

    btctrl = None
    conn = None
    mac_listener = {}
    found_devices = {}

    def __init__(self, logger):
        self.logger = logger
        self.hash = None
        self.blescanTask = None

        self._name = ""
        self._rssi = 0
        self._address = ""
        self._presence = ""
        return

    @staticmethod
    def add_mac_listener(mac, listener):
        ble_presence.mac_listener[mac.lower()] = listener
        if len(ble_presence.mac_listener) == 1:
            ble_presence.start_ble_scan()

    @staticmethod
    def remove_mac_listener(mac):
        del ble_presence.mac_listener[mac.lower()]
        if len(ble_presence.mac_listener) == 0:
            ble_presence.stop_ble_scan()

    @staticmethod
    def process_ble_data(data):
        if len(ble_presence.mac_listener) == 0:
            return
        
        # check for removed devices
        for mac in list(ble_presence.found_devices):
            if time.time() - ble_presence.found_devices[mac] > 5:
                if mac in ble_presence.mac_listener:
                    ble_presence.mac_listener[mac](mac, "", 0)
                del ble_presence.found_devices[mac]

        ev = aiobs.HCI_Event()
        ev.decode(data)
        mac = ev.retrieve("peer")
        name = ev.retrieve("Short Name")
        name_val = None
        for n in name:
            name_val = str(n.val.decode("ascii"))
        name = ev.retrieve("Complete Name")
        for n in name:
            name_val = str(n.val.decode("ascii"))
        rssi = ev.retrieve("rssi")
        rssi_val = None
        for n in rssi:
            rssi_val = str(n.val)
        for mac_entry in mac:
            ble_presence.found_devices[mac_entry.val.lower()] = time.time()
            if mac_entry.val.lower() in ble_presence.mac_listener:
                ble_presence.mac_listener[mac_entry.val.lower()](mac_entry.val.lower(), name_val, rssi_val)

    @staticmethod
    def start_ble_scan():
        iface = 0
        event_loop = asyncio.get_event_loop()
        mysocket = aiobs.create_bt_socket(iface)
        fac = event_loop._create_connection_transport(mysocket,aiobs.BLEScanRequester,None,None)
        asyncio.create_task(ble_presence._start_ble_scan(fac))
    
    @staticmethod
    async def _start_ble_scan(fac):
        ble_presence.conn,ble_presence.btctrl = await fac
        ble_presence.btctrl.process = ble_presence.process_ble_data
        # activate active scan
        cmd = aiobs.HCI_Cmd_LE_Set_Scan_Params(scan_type=1)
        ble_presence.btctrl.transport.write(cmd.encode())
        # start scan
        ble_presence.btctrl.send_scan_request()

    @staticmethod
    def stop_ble_scan():
        ble_presence.btctrl.stop_scan_request()
        ble_presence.conn.close()

    def update_reading(self, address, name, rssi):
        asyncio.create_task(self.update_reading_task(address, name, rssi))

    async def update_reading_task(self, address, name, rssi):
        if rssi == 0 and name == "":
            presence = "offline"
        else:
            presence = "online"
        
        if self._address != address:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "address", address, 1)
            self._address = address

        if self._rssi != rssi:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "rssi", str(rssi), 1)
            self._rssi = rssi

        if self._name != name and name is not None:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "name", name, 1)
            self._name = name

        if self._presence != presence:
            await fhem.readingsSingleUpdateIfChanged(self.hash, "presence", presence, 1)
            await fhem.readingsSingleUpdateIfChanged(self.hash, "state", presence, 1)
            self._presence = presence

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        if len(args) < 4:
            return "Usage: define p_mysmartphone PythonModule ble_presence <MAC>"

        self._address = args[3]
        self.hash["MAC"] = args[3]

        ble_presence.add_mac_listener(self._address, self.update_reading)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        ble_presence.remove_mac_listener(self._address)