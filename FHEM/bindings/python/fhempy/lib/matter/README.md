# Matter

Control Matter devices (lights, plugs, sensors, thermostats, locks, blinds...) directly from FHEM.
fhempy installs and runs the [Matter server](https://github.com/matter-js/matterjs-server) of the
Open Home Foundation (the same one Home Assistant uses) for you. Every Matter device gets its own
FHEM device automatically.

## 1. Create the Matter controller

```
define matter fhempy matter
```

That's all. On the first start fhempy installs the Matter server, this takes a few minutes.
Watch the readings `state` and `next_step` of the device `matter`, they always tell you what to do next.

**Requirements**
- Node.js 22.13 or newer. On 64-bit Linux (PC, Raspberry Pi with 64-bit OS) fhempy installs it
  automatically if it is missing. On a 32-bit Raspberry Pi OS install it yourself:
  `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - && sudo apt install nodejs`
- IPv6 must be enabled in your home network (it is by default on most routers).
- For **Thread** devices (e.g. Eve, Nanoleaf, IKEA, Aqara) you need a Thread border router, e.g. Apple TV 4K,
  HomePod mini, Google Nest Hub (2nd gen), Amazon Echo 4th gen or an OpenThread border router.
  WiFi and Ethernet devices don't need anything else.

## 2. Pair a device

Click on `set matter pair`, enter the pairing code and press `set`.
The code is either the 11 digit number (e.g. `3497-011-2332`) or the text of the QR code (starts with `MT:`).
Pairing takes up to a few minutes, the result is shown in the reading `pairing`.

**Where do I get the code?**

| Your situation | What to do |
|----------------|------------|
| The device already works with Apple Home, Google Home, Alexa, SmartThings or the app of the manufacturer | Open the device in that app and choose *Turn on pairing mode*, *Share*, *Linked Matter apps* or *Connect to other apps*. You get a new code, it is valid for a few minutes. The device keeps working in the other app. **This is the easiest way.** |
| New WiFi/Thread device which isn't in your network yet | Easiest: add it with the app of your phone first (see above). Alternative: Bluetooth pairing directly from FHEM, see below. |
| Device behind a Matter bridge (Philips Hue, IKEA Dirigera, Aqara hub, SwitchBot...) | Enable Matter in the app of the bridge and use the code shown there. Every device of the bridge gets its own FHEM device. |

**Pair a brand-new device via Bluetooth (for advanced users)**
1. Set the attribute `bluetooth_adapter` to the number of your Bluetooth adapter (`0` for hci0).
2. WiFi devices: `set matter wifi_credentials <WiFi name> <WiFi password>`.<br>
   Thread devices: `set matter thread_dataset <dataset>` (active dataset as hex string from your Thread border router).
3. `set matter pair_new_device <code from the device>`

## 3. Use your devices

New devices are created automatically with the name `matter_<node id>` (devices behind a bridge:
`matter_<node id>_<endpoint>`) and the name of the device as alias. They are put into the room
**Matter** together with the controller, so you see at a glance which devices came via Matter,
and get an icon matching their type (light, plug, blind, thermostat, sensor...). Change the room
and icon like for any FHEM device. Which commands and readings a device has depends on what the
device can do:

| Device | Commands | Readings |
|--------|----------|----------|
| Plug, switch, light | `on`, `off`, `toggle` | `onoff` |
| Dimmable light | `pct` (0-100) | `pct` |
| Color light | `ct` (Kelvin), `hue` (0-360), `sat` (0-100) | `ct`, `hue`, `sat` |
| Blinds/shutters | `open`, `close`, `stop`, `position` (100 = open, 0 = closed) | `position` |
| Thermostat | `desired-temp`, `mode` (off, heat, cool, auto) | `measured-temp`, `desired-temp`, `mode` |
| Door lock | `lock`, `unlock` | `lock` |
| Fan, air purifier | `fan_mode` | `fan_mode`, `fan_pct` |
| Sensors | | `temperature`, `humidity`, `pressure`, `illuminance`, `motion`, `contact`, `water_leak`, `smoke`, `co`, `co2`, `pm25`, `tvoc`, `air_quality` |
| Energy meter | | `power` (W), `energy` (kWh), `voltage`, `current` |
| Buttons | | `button` (`pressed`, `short`, `double`, `long`...) |
| Battery devices | | `battery` (ok/low), `batteryPercent` |

Every device also has:
- `identify`: the device blinks or beeps, so you know which one it is.
- `share`: creates a code (reading `share_code`) to add the device to another app as well.
- `refresh`: reads all information of the device again.
- readings `vendor`, `model`, `firmware`; `state` shows `offline` if the device isn't reachable.

If a device has several outlets/lights, the second one gets commands and readings with the
endpoint number, e.g. `on_2`, `onoff_2`.

**Device not fully supported?** Set the attribute `rawReadings` to `1`, then all Matter attributes
are shown as readings `raw_<endpoint>_<cluster>_<attribute>`. With `set <device> command` and
`set <device> write_attribute` you can send any Matter command. Please open an issue on GitHub with
the readings so the device can be supported.

## Commands of the controller

| Command | Description |
|---------|-------------|
| `pair <code>` | Pair a device which is in your network (see above) |
| `pair_new_device <code>` | Pair a brand-new device via Bluetooth |
| `wifi_credentials <ssid> <password>` | WiFi for new devices (only for `pair_new_device`) |
| `thread_dataset <dataset>` | Thread network for new devices (only for `pair_new_device`) |
| `discover` | Find devices in pairing mode, result in reading `discovered` |
| `create_devices` | Create missing FHEM devices (normally automatic) |
| `remove_node <node id>` | Remove a device from FHEM's Matter network (see internal `MATTER_NODE`), delete the FHEM device afterwards |
| `restart` | Restart the Matter server |
| `update` | Install the newest Matter server (only if a device doesn't work with the tested version) |

## Attributes of the controller

| Attribute | Description |
|-----------|-------------|
| `port` | Port of the Matter server, default 5580. Only reachable from this computer. |
| `bluetooth_adapter` | Bluetooth adapter number for `pair_new_device`, e.g. `0` |
| `primary_interface` | Network interface for IPv6 (e.g. `eth0`), only if pairing fails on computers with several interfaces |
| `test_dcl` | `1`: also pair devices with a test/development certificate (beta firmware). Only if you trust the vendor. Default `0` |
| `autocreate` | `1` (default): create FHEM devices automatically |

## Use an existing Matter server

If you already run a Matter server (e.g. the Home Assistant add-on or the Docker container),
fhempy can use it instead of installing its own one:
```
define matter fhempy matter ws://192.168.1.10:5580/ws
```
The devices are shared with Home Assistant then.

## Troubleshooting

- **Pairing fails / timeout**: codes from other apps are only valid for a few minutes, create a new one.
  Make sure the device and FHEM are in the same network and IPv6 is enabled in your router.
  Thread devices need a Thread border router.
- **state "Node.js 22.13 or newer needed"**: install Node.js (see requirements) and restart fhempy.
- **Logs**: fhempy log and `.fhempy/matter_server/matter_server.log` in your FHEM directory.
- **Backup**: `.fhempy/matter_server/data` contains the keys of your Matter network. If it is lost,
  all devices have to be reset and paired again. Include it in your backup! github_backup backs it up
  by default, github_restore applies it before the Matter server starts.
