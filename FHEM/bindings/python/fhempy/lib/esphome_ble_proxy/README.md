# ESPHome Bluetooth proxy

Uses an ESP32 with [ESPHome](https://esphome.io/components/bluetooth_proxy/) as an
additional Bluetooth adapter for all Bluetooth modules of fhempy. Put proxies where
the Raspberry Pi doesn't reach the devices, or use fhempy without local Bluetooth.

```
define bt_proxy_kitchen fhempy esphome_ble_proxy bluetooth-proxy-1a2b3c.local
define bt_proxy_garage fhempy esphome_ble_proxy 192.168.1.50 <encryption key>
```

Ready-made proxies (firmware from [esphome.github.io/bluetooth-proxies](https://esphome.github.io/bluetooth-proxies/))
are found by autodiscovery. The encryption key is only needed if the YAML has
`api: encryption: key:`.

## ESPHome YAML

```yaml
esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true

api:
  encryption:
    key: "..."
```

`active: true` in `bluetooth_proxy` is needed for modules which connect to their
devices (eq3bt, blue_connect, gfprobt, mitemp2, scooter). Without it the proxy only
receives advertisements.

## What works

| Module | Via proxy |
|--------|-----------|
| Advertisements: autodiscovery (Bluetooth), ble_presence, ble_monitor | yes, unlimited devices |
| Connections: eq3bt, blue_connect, gfprobt, mitemp2, scooter | yes, with `active: true` |
| homekit (Bluetooth), miflora, mitemp, nespresso_ble, bt_presence | no, only local adapters (own Bluetooth libraries or classic Bluetooth) |

fhempy picks for every device the adapter with the best signal. A local adapter is
used unless the proxy receives the device more than 10 dB better. If a connection
via proxy fails, the local adapters are tried.

## Limits

- An ESP32 holds 3 connections at the same time (ESPHome default, up to 9 with
  `connection_slots`, but then RAM gets short). Devices which stay connected (eq3bt
  keeps the connection open) use one slot each.
- Only one program can receive the advertisements of a proxy: a proxy which is used
  by Home Assistant can't be used by fhempy at the same time.
- The proxy can't pair with a PIN. eQ-3 thermostats with firmware 1.20+ which need a
  PIN have to be paired by a local adapter once (see eq3bt).
- Connections via WiFi take a bit longer and drop more often, fhempy reconnects.
- Modules running in their own worker process (fhempy does this on dependency
  conflicts) don't see the proxies.

## Readings

- `state`: connected, disconnected, encryption key required, wrong encryption key,
  no bluetooth_proxy configured
- `active_connections`: yes if the proxy can connect to devices
- `connections_free`, `connections_limit`
- `advertisements_per_minute`
- `name`, `model`, `esphome_version`, `bluetooth_mac`
