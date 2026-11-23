import json

from fhempy.lib import fhem
from fhempy.lib.ble_monitor.blemonitor import BLEmonitor
from fhempy.lib.ble_monitor.bt_helpers import BT_INTERFACES

from .. import generic
from . import describe


class ble_monitor(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.blemonitor = None
        # current values of the device (reading names), for state
        self._values = {}
        self._alias_checked = False

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        attr_config = {
            "hci_interface": {
                "default": "0",
                "options": ",".join(list(map(str, BT_INTERFACES))),
                "format": "int",
                "help": f"{BT_INTERFACES}",
                "function": "set_attr_generic",
            },
            "scan": {
                "default": "shared",
                "options": "shared,hci",
                "help": (
                    "shared: advertisements of fhempy's shared Bluetooth scan "
                    "(BlueZ), which all Bluetooth modules use.<br>"
                    "hci: own raw HCI scan, only for systems without BlueZ, "
                    "conflicts with the scan of other modules."
                ),
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
        await self.set_attr_config(attr_config)

        if len(args) != 4:
            return "Usage: define my_miscale fhempy ble_monitor 11:22:33:44:55:66"

        self.mac_addr = args[3]

        self.blemonitor = BLEmonitor.getInstance(self.logger)
        self.blemonitor.register_device(self)
        # also after a reconnect to FHEM (state was "fhempy server offline")
        self.create_async_task(self._restore_state())

    def mac(self):
        return self.mac_addr

    def hci(self):
        return self._attr_hci_interface

    def scan(self):
        return self._attr_scan

    def encryption_key(self):
        if self._attr_encryption_key == "":
            return None
        return self._attr_encryption_key

    async def _readings(self):
        """All readings of the device in FHEM."""
        name = fhem.perlString(self.hash["NAME"])
        ret = await fhem.sendCommandHash(
            self.hash,
            f"my $r = $main::defs{{{name}}}{{READINGS}} // {{}};; "
            "toJSON({ map { $_ => $r->{$_}{VAL} } keys %$r })",
        )
        try:
            readings = json.loads(ret or "{}")
        except (TypeError, ValueError):
            return {}
        return readings if isinstance(readings, dict) else {}

    async def _restore_state(self):
        """state from the readings of the last run: nothing is received until
        the device sends again (a toothbrush only while it's used)."""
        try:
            readings = await self._readings()
            readings.pop("state", None)
            # values received in the meantime are newer
            self._values = {**readings, **self._values}
            await fhem.readingsSingleUpdateIfChanged(
                self.hash, "state", describe.state(self._values), 1
            )
            await self._set_alias()
        except Exception:
            self.logger.exception("Failed to restore state")

    async def _set_alias(self):
        """alias like 'Oral-B IO Series 7' once the model is known, only if
        the user didn't set one."""
        if self._alias_checked:
            return
        alias = describe.label(self._values)
        if not alias:
            return
        self._alias_checked = True
        name = self.hash["NAME"]
        if await fhem.AttrVal(name, "alias", "") == "":
            await fhem.CommandAttr(self.hash, f"{name} alias {alias}")

    async def received_data(self, data):
        try:
            # FHEM readings must not contain spaces ("battery low")
            values = {describe.reading_name(key): value for key, value in data.items()}
            self._values.update(values)
            await fhem.readingsBeginUpdate(self.hash)
            for reading, value in values.items():
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "state", describe.state(self._values)
            )
            await fhem.readingsEndUpdate(self.hash, 1)
            await self._set_alias()
        except Exception:
            self.logger.exception("Failed to update readings")

    async def set_attr_generic(self, hash):
        self.blemonitor.unregister_device(self)
        self.blemonitor.register_device(self)

    async def Undefine(self, hash):
        if self.blemonitor:
            self.blemonitor.unregister_device(self)
        return await super().Undefine(hash)
