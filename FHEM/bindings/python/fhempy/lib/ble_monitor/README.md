
# ble_monitor
Monitor BLE devices (trackers, toothbrushes, body scales, ...) passively.

List of supported devices: https://custom-components.github.io/ble_monitor/devices

# Usage

```
sudo setcap 'cap_net_raw,cap_net_admin+eip' `readlink -f \`which python3\``
```

```
define my_body_scale fhempy ble_monitor MAC
```

ble_monitor scans the adapter (attribute `hci_interface`, default hci0) directly. If another program resets the adapter or changes its scan (e.g. the Matter server while `pair_new_device` runs, BlueZ scans), ble_monitor notices it from the adapter's events and sets up its scan again.
