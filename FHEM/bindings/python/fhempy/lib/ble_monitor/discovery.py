"""Autodiscovery of ble_monitor devices.

describe_ble() runs the BLE parser of ble_monitor on an advertisement found
by autodiscovery, so the suggested device name says what the device is
(e.g. Oral-B IO Series 7) instead of a generic ble_sensor. The model is
recognized from the content of the advertisement, the name the device
sends is only the fallback.
"""

import functools
import logging

from . import describe
from .advertisement import advertisement_data, hci_packet

_LOGGER = logging.getLogger(__name__)
# generic beacons (phones, tags, ...) aren't a model which can be named
GENERIC_TYPES = ("iBeacon", "AltBeacon", "Eddystone-TLM")


@functools.lru_cache(maxsize=1)
def _get_parser():
    from .parser import FhempyBleParser

    # discovery: every device is parsed, no whitelist
    return FhempyBleParser(discovery=True)


def describe_ble(address, advertisement):
    """Values for the templates of the discovery rule:
    label (e.g. 'Oral-B IO Series 7', else the name the device sends),
    manufacturer, model, kind (e.g. Toothbrush) and described (True if the
    parser recognized the model)."""
    local_name = advertisement.local_name or ""
    values = {
        "label": local_name,
        "manufacturer": "",
        "model": "",
        "kind": "",
        "described": False,
    }
    try:
        rssi = advertisement.rssi if advertisement.rssi is not None else -127
        sensor, _ = _get_parser().parse_raw_data(
            hci_packet(address, 0, rssi, advertisement_data(advertisement))
        )
    except Exception:
        _LOGGER.debug("Parsing the advertisement of %s failed", address, exc_info=True)
        return values
    if not sensor or not sensor.get("type") or sensor["type"] in GENERIC_TYPES:
        return values
    values.update(
        {
            "label": describe.label(sensor),
            "manufacturer": describe.manufacturer(sensor),
            "model": str(sensor["type"]),
            "kind": describe.kind(sensor),
            "described": True,
        }
    )
    return values
