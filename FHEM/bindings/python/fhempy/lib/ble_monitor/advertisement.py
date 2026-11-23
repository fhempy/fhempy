"""Raw advertising data of an advertisement, as the adapter received it.

The shared scan (bleak) and the Bluetooth proxies deliver parsed
advertisements, the BLE parser of ble_monitor needs HCI LE advertising
reports. Only stdlib, autodiscovery uses it too."""

UUID16_SUFFIX = "-0000-1000-8000-00805f9b34fb"
AD_NAME = 0x09
AD_UUID16 = 0x03
AD_UUID128 = 0x07
AD_SERVICE_DATA16 = 0x16
AD_SERVICE_DATA128 = 0x21
AD_MANUFACTURER = 0xFF
# the HCI event has one length byte: 255 minus the report header (subevent,
# number of reports, event type, address type, address, data length, rssi)
HCI_REPORT_OVERHEAD = 12
MAX_AD_LEN = 255 - HCI_REPORT_OVERHEAD


def hci_packet(address, address_type, rssi, data):
    """HCI LE advertising report like the local adapter sends it, for an
    advertisement received by an ESPHome Bluetooth proxy."""
    mac = bytes.fromhex(address.replace(":", ""))[::-1]
    data = bytes(data)[:MAX_AD_LEN]
    report = bytes([0x02, 0x01, 0x00, address_type & 0xFF]) + mac
    report += bytes([len(data)]) + bytes(data) + bytes([rssi & 0xFF])
    return bytes([0x04, 0x3E, len(report)]) + report


def _ad(ad_type, payload):
    payload = bytes(payload)[:254]
    return bytes([len(payload) + 1, ad_type]) + payload


def _uuid16(uuid):
    """0xFE95 for 0000fe95-0000-1000-8000-00805f9b34fb, None for others."""
    uuid = uuid.lower()
    if uuid.endswith(UUID16_SUFFIX) and uuid.startswith("0000"):
        return int(uuid[4:8], 16)
    return None


def _uuid128_bytes(uuid):
    return bytes.fromhex(uuid.replace("-", ""))[::-1]


def _changed_entries(service_data, manufacturer_data, previous):
    """Only the entries which changed since previous. If none changed, the
    entries which changed last time (BlueZ keeps old entries, e.g. ThermoPro
    sends a new manufacturer id for every value), else all of them."""
    if previous is None:
        return service_data, manufacturer_data
    old_service, old_manufacturer = previous[:2]
    changed_service = {k: v for k, v in service_data.items() if old_service.get(k) != v}
    changed_manufacturer = {
        k: v for k, v in manufacturer_data.items() if old_manufacturer.get(k) != v
    }
    if changed_service or changed_manufacturer:
        return changed_service, changed_manufacturer
    if len(previous) == 4:
        last_service, last_manufacturer = previous[2:]
        last_service = {k: v for k, v in last_service.items() if k in service_data}
        last_manufacturer = {
            k: v for k, v in last_manufacturer.items() if k in manufacturer_data
        }
        if last_service or last_manufacturer:
            return last_service, last_manufacturer
    return service_data, manufacturer_data


def _uuid_list_ads(service_uuids):
    uuid16 = b""
    uuid128 = b""
    for uuid in service_uuids:
        short = _uuid16(uuid)
        if short is not None:
            uuid16 += short.to_bytes(2, "little")
        else:
            uuid128 += _uuid128_bytes(uuid)
    parts = []
    if uuid16:
        parts.append(_ad(AD_UUID16, uuid16))
    if uuid128:
        parts.append(_ad(AD_UUID128, uuid128))
    return parts


def _service_data_ad(uuid, data):
    short = _uuid16(uuid)
    if short is not None:
        return _ad(AD_SERVICE_DATA16, short.to_bytes(2, "little") + data)
    return _ad(AD_SERVICE_DATA128, _uuid128_bytes(uuid) + data)


def advertisement_data(advertisement, previous=None):
    raw, _, _ = _advertisement_data(advertisement, previous)
    return raw


def _advertisement_data(advertisement, previous=None):
    """Raw advertising data (AD structures) rebuilt from bleak's
    AdvertisementData, as the adapter received it. BlueZ merges all
    advertisements of a device: with the (service_data, manufacturer_data) of
    the previous call only the entries which changed since then are included,
    so a value isn't parsed again. If nothing changed, all of them are."""
    service_data, manufacturer_data = _changed_entries(
        dict(advertisement.service_data or {}),
        dict(advertisement.manufacturer_data or {}),
        previous,
    )
    parts = []
    if advertisement.local_name:
        parts.append(_ad(AD_NAME, advertisement.local_name.encode("utf-8")))
    parts += _uuid_list_ads(advertisement.service_uuids or [])
    parts += [_service_data_ad(uuid, data) for uuid, data in service_data.items()]
    parts += [
        _ad(AD_MANUFACTURER, company.to_bytes(2, "little") + data)
        for company, data in manufacturer_data.items()
    ]
    raw = b""
    for part in parts:
        if len(raw) + len(part) > MAX_AD_LEN:
            break
        raw += part
    return raw, service_data, manufacturer_data
