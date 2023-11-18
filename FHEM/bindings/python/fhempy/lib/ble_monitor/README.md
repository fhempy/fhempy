
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
