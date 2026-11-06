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
- The ESPHome API can't pass a PIN. Devices which need pairing with a PIN (eQ-3
  firmware 1.20+) work via proxy only if the proxy's YAML answers the PIN request
  (see below). Otherwise the device rejects the connection (insufficient
  authentication) and fhempy uses only the local adapters for it, reading
  `connection_proxy`.
- Connections via WiFi take a bit longer and drop more often, fhempy reconnects.
- Modules running in their own worker process (fhempy does this on dependency
  conflicts) don't see the proxies.

## Devices with PIN (eQ-3)

The pairing key is stored by the adapter which paired, a PIN entered on the Raspberry
Pi doesn't help the ESP32. Add to the YAML of the proxy (one `ble_client` per device,
it never connects by itself, it only answers the PIN request when fhempy pairs via
the proxy):

```yaml
esp32_ble:
  io_capability: keyboard_only
  max_connections: 4   # 3 for bluetooth_proxy + 1 per ble_client

ble_client:
  - mac_address: "00:1A:22:XX:XX:XX"
    id: eq3_pairing
    auto_connect: false
    on_passkey_request:
      then:
        - ble_client.passkey_reply:
            id: eq3_pairing
            passkey: 123456   # PIN shown on the thermostat
```

Restart fhempy (or the eq3bt device) after flashing.

## Readings

- `state`: connected, disconnected, encryption key required, wrong encryption key,
  no bluetooth_proxy configured
- `active_connections`: yes if the proxy can connect to devices
- `connections_free`, `connections_limit`
- `advertisements_per_minute`
- `name`, `model`, `esphome_version`, `bluetooth_mac`
