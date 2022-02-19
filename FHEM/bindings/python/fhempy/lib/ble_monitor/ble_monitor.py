from fhempy.lib import fhem
from fhempy.lib.ble_monitor.blemonitor import BLEmonitor
from fhempy.lib.ble_monitor.bt_helpers import BT_INTERFACES
from .. import generic


class ble_monitor(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)

        self.blemonitor = None

        attr_config = {
            "hci_interface": {
                "default": "0",
                "options": ",".join(list(map(str, BT_INTERFACES))),
                "format": "int",
                "help": f"{BT_INTERFACES}",
                "function": "set_attr_generic",
            },
            "encryption_key": {
                "default": "",
                "help": (
                    "Get encryption key (BLE KEY) "
                    "via https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor"
                ),
                "function": "set_attr_generic",
            },
        }
        self.set_attr_config(attr_config)

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(args) != 4:
            return "Usage: define my_miscale fhempy ble_monitor 11:22:33:44:55:66"

        self.mac_addr = args[3]

        self.blemonitor = BLEmonitor.getInstance(self.logger)
        self.blemonitor.register_device(self)

    def mac(self):
        return self.mac_addr

    def hci(self):
        return self._attr_hci_interface

    def encryption_key(self):
        if self._attr_encryption_key == "":
            return None
        return self._attr_encryption_key

    async def received_data(self, data):
        try:
            await fhem.readingsBeginUpdate(self.hash)
            for reading in data:
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, reading, data[reading]
                )
            await fhem.readingsEndUpdate(self.hash, 1)
        except Exception:
            self.logger.exception("Failed to update readings")

    async def set_attr_generic(self, hash):
        self.blemonitor.unregister_device(self)
        self.blemonitor.register_device(self)

    async def Undefine(self, hash):
        if self.blemonitor:
            self.blemonitor.unregister_device(self)
        return await super().Undefine(hash)
