
# ble_monitor
Monitor BLE devices (trackers, toothbrushes, body scales, ...) passively.

List of supported devices: https://custom-components.github.io/ble_monitor/devices

# Usage

Only needed with `attr <device> scan hci`:

```
sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
```

```
define my_body_scale fhempy ble_monitor MAC
```

Autodiscovery suggests a name after the model, which the BLE parser recognizes from the data of the advertisement (e.g. `Oral_B_IO_Series_7` instead of a generic name). Once the model is known, the device gets an `alias` like `Oral-B IO Series 7`, only if no alias is set.

`state` shows the main values: the toothbrush state, `T: 21.5 H: 45` for climate sensors, `open`/`closed`, ... After a restart of fhempy or FHEM it's restored from the readings, until the device sends again (`waiting for data` if it never sent).

ble_monitor uses fhempy's shared Bluetooth scan (BlueZ), the same scan as autodiscovery, ble_presence and the other Bluetooth modules. There is only one scan per adapter, so the modules don't change each other's scan settings. With `hci_interface` other than 0 that adapter is scanned as well. Advertisements of ESPHome and SMLIGHT Bluetooth proxies are received too.

Attribute `scan`:
- `shared` (default): shared scan via BlueZ.
- `hci`: own raw HCI scan of the adapter (needs CAP_NET_RAW, see above). Only for systems without BlueZ (bluetoothd), it conflicts with the scan of the other modules. If another program resets the adapter or changes its scan, ble_monitor notices it from the adapter's events and sets up its scan again.
