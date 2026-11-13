# SMLIGHT Bluetooth proxy

Uses the Bluetooth of a SMLIGHT SLZB gateway (e.g. SLZB-06MU, SLZB-MR) with SLZB-OS as an
additional Bluetooth receiver for fhempy. The gateway keeps its firmware, Zigbee and the
Thread border router (OTBR) keep working.

```
define slzb_bt_proxy fhempy smlight_ble_proxy 192.168.1.60
define slzb_bt_proxy fhempy smlight_ble_proxy slzb-06mu.local
```

SLZB gateways are found by autodiscovery.

## Setup on the gateway

In the SLZB-OS web interface (Bluetooth settings) enable both options, "Enable BLE" and
"Proxy BLE advertisements to a Home Assistant". One of them alone is not enough. The gateway
reboots when BLE is switched on or off, fhempy reconnects on its own. Only one
program can receive the advertisements of a gateway, so a gateway used by Home Assistant's
SMLIGHT integration as Bluetooth proxy can't be used by fhempy at the same time.

## What works

| Module | Via SMLIGHT proxy |
|--------|-------------------|
| Advertisements: autodiscovery (Bluetooth), ble_presence, ble_monitor | yes |
| Connections: eq3bt, blue_connect, gfprobt, mitemp2, scooter | no, the SLZB-OS proxy only scans |
| Matter pairing via Bluetooth | no |

For connections use a local adapter or an [ESPHome Bluetooth proxy](../esphome_ble_proxy/README.md).

## Attributes

- `scan_mode`: `passive` (default) only listens. `active` also asks the devices for their scan
  response (e.g. their name), uses a bit more battery of the devices.

## Readings

- `state`: `connected`, `connecting`, `BLE proxy disabled in SLZB-OS`, or
  `no advertisements, BLE proxy enabled in SLZB-OS?` if nothing arrived for 3 minutes
- `advertisements_per_minute`
- `model`, `firmware`, `hostname`, `mac`: from the web interface of the gateway (not shown if the
  web interface is password protected, the proxy works anyway)

Uses [bleak-smlight](https://github.com/Bluetooth-Devices/bleak-smlight) and
[pysmlight](https://github.com/smlight-tech/pysmlight) (UDP port 5050).
