# autodiscovery

Finds devices in your network and via Bluetooth and offers to create them in FHEM.
fhempy defines `fhempy_discovery` on its own once after the installation, you don't
have to do anything.

```
define fhempy_discovery fhempy autodiscovery
```

## What happens

- Found devices are listed on the detail page of `fhempy_discovery` (button
  *Found devices*) and in the setup window after the installation.
- A device that shows up while FHEM is running opens a popup in every open FHEMWEB
  page: *Create*, *Ignore* or *Later*. Each device pops up only once, also with several
  fhempy instances (peers).
- Nothing is created automatically, you always decide.
- Devices which already exist in FHEM aren't offered.

Found are:

| How | Devices |
|-----|---------|
| mDNS | Google Cast, HomeKit (not paired yet), Spotify Connect, Matter (commissioning mode), MQTT broker |
| UPnP | DLNA media renderers |
| Bluetooth | eQ-3 thermostats, Nespresso, Xiaomi/Ninebot scooters, Mi Flora, Mi thermometers, Mi scales, Oral-B toothbrushes, Govee, Matter devices to pair |
| Search | Tuya, Gree air conditioners, Xiaomi WiFi devices (miio), GoodWe inverters, local MQTT broker |
| mqtt_ha_discovery | New Zigbee2MQTT/Tasmota/... devices, while `fhempy_discovery` runs |

## Residents

*Add resident* searches the phones in your network and via Bluetooth. Pick the phone
of the person (and its Bluetooth address, the phone has to show its Bluetooth settings
during the search). fhempy creates

- `presence_<Name>_phone` (arp_presence) and `presence_<Name>_bluetooth` (bt_presence),
- `rr_<Name>` (ROOMMATE) and, if there is none yet, `rgr_Residents` (RESIDENTS).

The person is at home if any of both sees the phone.

## Bluetooth tags

*Add Bluetooth tag*: hold the tag right next to the Raspberry Pi, the tag with by far
the strongest signal is created as ble_presence device. AirTags and other Find My
tags change their address and aren't supported.

## Bluetooth scan

All Bluetooth modules share one scan, it runs passively where possible and stops while
a module connects to a device. If the adapter has problems the scan falls back to 10
seconds every 5 minutes for one hour.

## Attributes

| Attribute | Default | |
|-----------|---------|--|
| `popup` | 1 | 0: no popups, the devices are only listed |
| `ble` | continuous | `interval`: scan every `ble_interval` seconds, `off`: no Bluetooth |
| `ble_interval` | 300 | Seconds between two scans with `ble interval` |
| `notify` | | Name of a push device, found devices are also sent to your phone |
| `disable` | 0 | 1: stops all searches |

## Set / Get

- `set fhempy_discovery scan`: searches again now
- `set fhempy_discovery createAll`: creates all found devices without required input
- `set fhempy_discovery ignore <id>` / `unignore <id>`
- `get fhempy_discovery candidates`: all found devices as JSON

## For developers

See [DEVELOPMENT.md](../../../../../../DEVELOPMENT.md#autodiscovery), every module
describes in its `manifest.json` how it's found.
