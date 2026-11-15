"""fhempy changes on top of the BLE parser copied from ble_monitor.

The files in ble_parser/ are copied by tools/sync_ble_parser.py and must
not be edited, fhempy specific fixes go here.
"""

from .ble_parser import BleParser

THERMOPRO_TYPES = ("TP357", "TP359")


class FhempyBleParser(BleParser):
    """BleParser with fixes that are not in ble_monitor (yet).

    ThermoPro TP357S: the byte after the humidity is a 2 bit battery level
    (0..2 -> 0/50/100 %) in the upper bits 0x20. ble_monitor compares it
    with 2 and always reports "battery low" for it.
    """

    def parse_advertisement(
        self,
        mac,
        rssi,
        service_class_uuid16=None,
        service_class_uuid128=None,
        local_name="",
        service_data_list=None,
        man_spec_data_list=None,
    ):
        sensor_data, tracker_data = super().parse_advertisement(
            mac,
            rssi,
            service_class_uuid16,
            service_class_uuid128,
            local_name,
            service_data_list,
            man_spec_data_list,
        )
        if sensor_data and sensor_data.get("type") in THERMOPRO_TYPES:
            for man_spec_data in man_spec_data_list or []:
                if man_spec_data[0] >= 0x08:
                    sensor_data.pop("battery low", None)
                    sensor_data["battery"] = (man_spec_data[6] & 0x03) * 50
                    break
        return sensor_data, tracker_data
