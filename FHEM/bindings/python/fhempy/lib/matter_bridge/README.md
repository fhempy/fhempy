# Matter bridge

Use your FHEM devices in **Apple Home, Google Home, Amazon Alexa and SmartThings**, including
voice control with Siri, Google Assistant/Gemini and Alexa. Everything runs locally in your
network, no cloud account or port forwarding is needed.

The bridge works the other way round than the `matter` module: `matter` controls Matter devices
from FHEM, `matter_bridge` makes FHEM devices available as Matter devices.

## 1. Create the bridge

```
define matterbridge fhempy matter_bridge
```

On the first start fhempy installs matter.js, this takes a few minutes. Watch the readings
`state` and `next_step`, they always tell you what to do next.

**Requirements**
- Node.js 22.13 or newer. On 64-bit Linux fhempy installs it automatically if it is missing.
  On a 32-bit Raspberry Pi OS install it yourself:
  `curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - && sudo apt install nodejs`
- IPv6 must be enabled in your home network (it is by default on most routers).
- A hub of your app in the same network: Apple TV or HomePod for Apple Home; Nest Hub, Nest Mini,
  Nest Audio, Chromecast with Google TV or Google TV Streamer for Google Home; an Echo device
  for Alexa.
- FHEM must be up to date (`update all` and restart FHEM), so that fhempy gets the changes of
  your devices.

## 2. Choose your devices

```
set matterbridge add Livingroom_Light
set matterbridge add Plug_TV
```

`set add` offers a list of your FHEM devices. The device shows up in your apps after a few
seconds. The kind of device is detected automatically:

| FHEM device | In the app | Readings used | Commands sent to FHEM |
|-------------|------------|---------------|-----------------------|
| `on`/`off` | switch, or light if the name contains light/Licht/Lampe | `state` | `on`, `off` |
| `on`/`off` and `pct`, `dim` or `brightness` | dimmable light | `state`, `pct` | `on`, `off`, `pct 50` |
| `pct`/`position` and `up`/`down`/`open`/`close` | blind/shutter | `pct`, `position` | `pct 30`, `stop` |
| `desired-temp` (or `desiredTemperature`) | thermostat | `measured-temp`, `temperature`, `desired-temp` | `desired-temp 21.5` |
| `lock`/`unlock` | door lock | `lock`, `state` | `lock`, `unlock` |
| reading `contact` | door/window contact | `contact` (open/closed) | |
| reading `motion` | motion sensor | `motion` | |
| reading `temperature` | temperature sensor (+ humidity sensor if there is a reading `humidity`) | `temperature`, `humidity` | |
| reading `humidity` | humidity sensor | `humidity` | |

If you already use homebridge, alexa-fhem or gassistant-fhem, the attribute `genericDeviceType`
of your devices is used as well.

**Attributes of your FHEM devices** (added automatically when the device is used by the bridge)

| Attribute | Description |
|-----------|-------------|
| `matterType` | Kind of device if it isn't detected correctly: `switch`, `outlet`, `light`, `dimmer`, `blind`, `thermostat`, `lock`, `contact`, `motion`, `temperature`, `humidity` |
| `matterName` | Name in the app (default: alias, otherwise the device name). Most apps let you rename devices as well. |
| `matterInvert` | `1` if the position of your blind is reversed (FHEM 0 = open). Set automatically for ROLLO devices. |

## 3. Pair the bridge with your app

Open the bridge in FHEMWEB, a QR code is shown at the top.

- **Apple Home**: *+* → *Add Accessory* → scan the QR code. Confirm *Add Anyway* when the app
  says the accessory isn't certified.
- **Google Home**: Google only accepts uncertified Matter devices after you created a free
  developer project once, with the same Google account as in the Google Home app:
  1. Open https://console.home.google.com and create a project (any name).
  2. *Add Matter integration* → *Next: Develop* → *Next: Setup*.
  3. Enter any product name, Vendor ID **0xFFF1** (*Test VID*) and Product ID **0x8000**, save.
  4. In the Google Home app: *+* → *Device* → *Matter-enabled device* → scan the QR code.
- **Amazon Alexa**: *+* → *Add Device* → *Other* → *Matter* → scan the QR code.
- **SmartThings**: *+* → *Add device* → *Partner devices* → *Matter*.

Pairing takes up to a minute. Afterwards the reading `paired_with` shows the app.

**Use more than one app**: `set matterbridge pairing_mode`, then scan the same QR code with the
next app within 15 minutes. Or share the bridge from the first app (Google Home: *Linked Matter
apps & services*, Apple Home: *Turn On Pairing Mode*).

**Voice control**: once a device is in Google Home, Apple Home or Alexa, you can use it with the
voice assistant, e.g. *"Hey Google, turn on the living room light"*.

## Commands

| Command | Description |
|---------|-------------|
| `add <device>` | Make a FHEM device available in your apps |
| `remove <device>` | Remove a FHEM device from your apps |
| `pairing_mode` | Allow pairing with one more app for 15 minutes |
| `refresh` | Read all devices from FHEM again (normally automatic) |
| `restart` | Restart the bridge |
| `reset_pairing` | Remove all pairings, the bridge gets a new QR code. Remove the bridge from your apps too. |

## Attributes

| Attribute | Description |
|-----------|-------------|
| `devices` | FHEM devices used by the bridge, separated by comma. `set add`/`set remove` change it. A device specification like `room=Matter` works too. |
| `port` | Network port of the bridge, default 5550. All apps have to be paired again after a change. |
| `bridge_name` | Name of the bridge which is shown when you pair it, default FHEM |

## Troubleshooting

- **state "FHEM update needed"**: run `update all` in FHEM and restart FHEM. Without it the
  apps don't see changes of your devices.
- **The app can't find the bridge**: phone, hub and FHEM must be in the same network, IPv6 must
  be enabled in the router. Check that nothing else uses port 5550.
- **A device has the wrong type or doesn't show up**: see reading `unsupported_devices` and set the
  attribute `matterType` of the device.
- **A command from the app has no effect**: see reading `lastError` and the fhempy log.
- **Logs**: fhempy log and `.fhempy/matter_bridge/<bridge name>/bridge.log` in your FHEM directory.
- **Backup**: `.fhempy/matter_bridge/<bridge name>` contains the pairings, github_backup saves it
  by default. If it is lost, the bridge has to be removed from all apps and paired again.
