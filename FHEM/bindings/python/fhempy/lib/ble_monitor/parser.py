"""bleparser with fixes for devices the pinned bleparser release rejects."""

from bleparser import BleParser
from bleparser.thermopro import parse_thermopro

THERMOPRO_TYPES = ("TP357", "TP359")


class FhempyBleParser(BleParser):
    """BleParser that also understands newer ThermoPro advertisements.

    bleparser 3.7.3 only accepts ThermoPro manufacturer data with exactly
    7 bytes. Newer variants like the TP357S send one byte more, which
    carries the battery level (2 bit: 0..2 -> 0/50/100 %).
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
        if service_data_list or not local_name:
            return sensor_data, tracker_data
        device_type = local_name[0:5]
        if device_type not in THERMOPRO_TYPES:
            return sensor_data, tracker_data
        for man_spec_data in man_spec_data_list or []:
            data_len = man_spec_data[0]
            if data_len < 0x07:
                continue
            if sensor_data is None:
                sensor_data = parse_thermopro(
                    self, man_spec_data, device_type, mac, rssi
                )
            if sensor_data is not None and data_len >= 0x08:
                sensor_data["battery"] = (man_spec_data[6] & 0x03) * 50
            break
        return sensor_data, tracker_data
