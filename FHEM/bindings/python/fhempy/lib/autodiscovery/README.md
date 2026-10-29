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
- Devices which already exist in FHEM aren't offered. The list *Found devices* shows
  them collapsed below the new devices (*Already in FHEM*, with a link to the device),
  ignored devices as well (*Ignored*, button *Offer again*). A search field filters
  the list by name, type, model or IP.
- A device deleted in FHEM is offered again in *Found devices* within a minute
  (without popup), *Create* sets it up again.

Found are:

| How | Devices |
|-----|---------|
| mDNS | Google Cast, HomeKit (not paired yet), Spotify Connect, Matter (commissioning mode) |
| UPnP | DLNA media renderers |
| Bluetooth | eQ-3 thermostats, Nespresso, Xiaomi/Ninebot scooters, Mi Flora, Mi thermometers, Mi scales, Oral-B toothbrushes, Govee, Matter devices to pair |
| Search | Tuya, Gree air conditioners, Xiaomi WiFi devices (miio), GoodWe inverters |
| MQTT | Every ESPHome/Zigbee2MQTT/Tasmota/... device which sends Home Assistant MQTT discovery |

## MQTT devices

autodiscovery listens for Home Assistant MQTT discovery messages (`homeassistant/#`) on

- the broker on this computer (port 1883, e.g. Mosquitto or the MQTT2_SERVER of FHEM),
- brokers announced via mDNS (`_mqtt._tcp`),
- the broker of a `mqtt_ha_discovery` device, if you have one.

Each new device is offered on its own, *Create* defines a MQTT2_DEVICE with
`readingList` and `setList` (switch, light, sensor). *Create all* doesn't create MQTT
devices. If FHEM itself isn't connected to the broker yet (no MQTT2_SERVER on that port,
no MQTT2_CLIENT), a MQTT2_CLIENT `mqtt_broker` is created first, with `autocreate no`.
After connecting, autodiscovery sends `online` to `homeassistant/status`, like Home
Assistant does, so the devices send their discovery messages again.

Zigbee2MQTT needs `homeassistant: true` in its configuration.yaml to send them.

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

The passive scan needs BlueZ with `--experimental` (and Linux 5.10 or newer). Without
it the scan runs actively, the reading `bluetooth_warning` and the detail page of
`fhempy_discovery` show a warning with a command to copy. Run it once on the Raspberry
Pi, it starts BlueZ with `--experimental`, also after a reboot.

## Attributes

| Attribute | Default | |
|-----------|---------|--|
| `popup` | 1 | 0: no popups, the devices are only listed |
| `ble` | continuous | `interval`: scan every `ble_interval` seconds, `off`: no Bluetooth |
| `ble_interval` | 300 | Seconds between two scans with `ble interval` |
| `notify` | | Name of a push device, found devices are also sent to your phone |
| `mqtt` | auto | MQTT broker for MQTT devices: `auto`, `off` or `host[:port]` |
| `mqtt_username`, `mqtt_password` | | Login of the MQTT broker, if needed |
| `disable` | 0 | 1: stops all searches |

## Set / Get

- `set fhempy_discovery scan`: searches again now
- `set fhempy_discovery createAll`: creates all found devices without required input
- `set fhempy_discovery recreate <id>` / `recreateAll`: sets up MQTT devices which
  are in FHEM already again like new ones (readingList, setList, webCmd, stateFormat,
  devStateIcon are replaced, attrTemplate leftovers removed). The FHEM name and the
  other attributes (room, alias, icon...) stay, so DOIFs and notifies keep working.
  In the dialog: *Set up again* in *Already in FHEM*.
- `set fhempy_discovery ignore <id>` / `unignore <id>`
- `get fhempy_discovery candidates`: all found devices as JSON (new, in FHEM, ignored)

## For developers

See [DEVELOPMENT.md](../../../../../../DEVELOPMENT.md#autodiscovery), every module
describes in its `manifest.json` how it's found.
