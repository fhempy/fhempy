<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/logo-dark.svg">
    <img alt="fhempy" src="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/logo-light.svg" width="440">
  </picture>
</p>

<p align="center">
  <a href="#-matter"><img src="https://img.shields.io/badge/Matter-supported-brightgreen?style=for-the-badge" alt="Matter supported" height="36"></a>
</p>

<p align="center">
  <b>69 ready-to-use integrations for <a href="https://fhem.de">FHEM</a>, written in Python. Now with Matter support.</b>
</p>

<p align="center">
  <a href="https://pypistats.org/packages/fhempy"><img src="https://img.shields.io/pypi/dm/fhempy" alt="Downloads"></a>
  <a href="https://github.com/fhempy/fhempy"><img src="https://img.shields.io/badge/python-3.12+-blue" alt="Python 3.12+"></a>
  <a href="https://pypi.org/project/fhempy/"><img src="https://img.shields.io/pypi/v/fhempy" alt="Version"></a>
  <a href="https://github.com/fhempy/fhempy/commits/master"><img src="https://img.shields.io/github/last-commit/fhempy/fhempy" alt="Last commit"></a>
  <a href="https://paypal.me/todominik"><img src="https://img.shields.io/badge/buy%20me%20a%20coffee-thx-yellow" alt="Buy me a coffee"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick start</a> ·
  <a href="#-matter">Matter</a> ·
  <a href="#-ai">AI</a> ·
  <a href="#-remote-access">Remote access</a> ·
  <a href="#-timeline">Timeline</a> ·
  <a href="#-tablet-dashboard">Tablets</a> ·
  <a href="#-modules">Modules</a> ·
  <a href="#-troubleshooting">Troubleshooting</a> ·
  <a href="#fhempy-peers-eg-extend-bluetooth-range">Remote peers</a> ·
  <a href="#write-your-own-module">Write your own module</a>
</p>

## ✨ Why fhempy?
- **Matter support**: control Matter lights, plugs, sensors, thermostats, locks and blinds directly from FHEM, also devices behind Hue, IKEA or Aqara bridges. And the other way round: use your FHEM devices in Apple Home, Google Home and Alexa, with voice control. See [Matter](#-matter).
- **Talk to FHEM with AI**: ask Claude or a local AI model *"switch off all lights when I leave the house"* and it creates the DOIF for you, which you approve with one click. See [AI](#-ai).
- **What happened at home?** The timeline shows all events as a readable story per day, e.g. of your holidays, without technical noise. See [Timeline](#-timeline).
- **A modern dashboard for your tablets**: on the wall, next to the couch or at the front door, set up in a minute on the tablet itself, with doorbell camera and door opener. See [Tablet dashboard](#-tablet-dashboard).
- **FHEM on your phone, from anywhere**: one `define` gives you a fixed https address with password, no VPN app and no port forwarding. See [Remote access](#-remote-access).
- **Lots of devices out of the box**: Tuya, Xiaomi, Google Cast, Spotify, Zigbee2MQTT, ESPHome, solar inverters, cars, Bluetooth sensors and many more.
- **No Python fiddling**: fhempy sets up its own Python environment (even a newer Python if your system's is too old) and every module installs its libraries automatically the first time you use it.
- **Feels like any other FHEM device**: `define`, `set`, `get`, `attr` and readings work as usual.
- **Extend your range**: run modules on a remote Raspberry Pi, e.g. close to your Bluetooth devices.

## 🔗 Matter
fhempy brings [Matter](https://csa-iot.org/all-solutions/matter/) to FHEM. It installs and runs the same Matter server Home Assistant uses, no extra hardware or Docker needed:
```
define matter fhempy matter
set matter pair <code>
```
Use the pairing code printed on the device, or create one in Apple Home, Google Home or Alexa ("Connect to other apps"); the device keeps working there too. Every Matter device gets its own FHEM device with the matching commands (`on`, `off`, `pct`, `ct`, `position`, `desired-temp`, `lock`...) and readings. The [Matter README](FHEM/bindings/python/fhempy/lib/matter/README.md) explains every step, and the reading `next_step` always tells you what to do next.

**Your FHEM devices in Apple Home, Google Home and Alexa**: the Matter bridge makes FHEM devices available as Matter devices, so you can switch them in these apps and with Siri, Google Assistant/Gemini or Alexa. Everything stays local, no cloud account or gassistant-fhem/alexa-fhem setup needed:
```
define matterbridge fhempy matter_bridge
set matterbridge add Livingroom_Light
```
Then scan the QR code shown in FHEMWEB with your app. The [Matter bridge README](FHEM/bindings/python/fhempy/lib/matter_bridge/README.md) explains every step.

## 🤖 AI
Control FHEM in plain language with AI apps like Claude Desktop, Claude Code, LM Studio or Cursor:
```
define AI fhempy mcp_server
```
Copy the secret address shown in FHEMWEB into your AI app, then ask *"Which lights are on?"* or *"Switch off all lights when I leave the house."* Automations created by the AI wait for your approval, your passwords are never sent to the AI. The [MCP server README](FHEM/bindings/python/fhempy/lib/mcp_server/README.md) explains every step.

## 📱 Remote access
Open FHEM on your phone while you're away, in the normal browser:
```
define remote fhempy remote_access
```
Open the device in FHEMWEB, log in to Tailscale (free, with your Google, Microsoft, Apple or GitHub account) and allow access once. Then scan the QR code with your phone: FHEM is at `https://fhem.<your-name>.ts.net`, protected by a password. No VPN app, no port forwarding in the router, and FHEMWEB in your home network stays as it is. The [remote access README](FHEM/bindings/python/fhempy/lib/remote_access/README.md) explains every step.

## 🔔 Push notifications
Notifications on your phone and tablet, without app and without account (replaces Pushbullet):
```
define push fhempy push
```
Open the device on the phone and tap *Enable notifications*. Then send from notify or DOIF with `set push message Washing machine is done`, on Android also with picture and buttons which run FHEM commands. The [push README](FHEM/bindings/python/fhempy/lib/push/README.md) explains every step.

## 🕒 Timeline
See what happened at home, e.g. during your holidays:
```
define timeline fhempy timeline
```
fhempy records the events of all FHEM devices and shows them on the device page as a story per day: doors, lights, motion, who came home. Signal strength, last seen and similar technical events are hidden automatically, temperatures and power become small daily curves, and everything unusual while nobody was at home is highlighted. The [timeline README](FHEM/bindings/python/fhempy/lib/timeline/README.md) explains every step.

## 📱 Tablet dashboard
A modern dashboard for the tablets at home, in its own look and without configuration in FHEM:
```
define tablets fhempy dashboard
```
Open the device, scan the QR code with the tablet and choose where it is: on the wall, at the couch or at the door. Rooms and tiles come from your FHEM rooms, open windows are shown by name, and when somebody rings the door tablet shows the camera live, lets you talk and opens the door. Every tablet keeps its own layout. The [dashboard README](FHEM/bindings/python/fhempy/lib/dashboard/README.md) explains every step.

## 🚀 Quick start

### 1. Install fhempy
Copy & paste this line into the FHEM command field and press enter:
```
{eval GetFileFromURL("https://raw.githubusercontent.com/fhempy/fhempy/master/install_fhempy.pl")}
```

That's it. FHEM downloads the fhempy files and creates `fhempy_local`, which sets up everything else on its own. No restart, no `sudo` and no system packages needed. A window shows the progress until fhempy is ready, the state of `fhempy_local` in the room *fhempy* shows it too:

1. `Installing fhempy: 1/4 installing uv`
2. `Installing fhempy: 2/4 installing Python 3.13` (only if your system Python is older)
3. `Installing fhempy: 3/4 installing fhempy`
4. `Installing fhempy: 4/4 starting fhempy`

`fhempy_local` turns green with the fhempy version as soon as it's ready. If something goes wrong, the state shows the reason in red.

<p align="center"><img src="docs/images/install-dialog.png" alt="fhempy installation window: progress and setup tiles for Matter, Matter Bridge, Zigbee2MQTT and AI (MCP server)" width="800"></p>

When fhempy is ready, the window offers Matter, Matter Bridge, Zigbee2MQTT and the AI MCP server: one click creates the device.

> [!NOTE]
> fhempy runs with Python 3.12 or newer. You don't need to upgrade your system for that: if your Python is older than 3.13 (e.g. Debian 12 Bookworm or Raspberry Pi OS Bookworm), fhempy installs Python 3.13 for itself with [uv](https://docs.astral.sh/uv/). uv also installs all Python packages, which is much faster than pip.

The line runs [install_fhempy.pl](install_fhempy.pl): it adds the fhempy update source, downloads the fhempy FHEM modules (`update all pythonbinding`), loads them and defines `fhempy_local`. Running it again is harmless, e.g. after a failed try. If nothing happens at all, FHEM couldn't download the script from GitHub.

Optional: `sudo apt install libcpanel-json-xs-perl` makes FHEM decode fhempy messages much faster. Check it with `{InternalVal("fhempy_local", "JSON_BACKEND", "")}` in FHEM.

### 2. Bluetooth modules and piclock only: system packages
Most modules need nothing else. The Bluetooth modules ble_presence, bt_presence, eq3bt, miflora, mitemp and the piclock module still build some of their libraries, which needs these packages:
```
sudo apt install python3-dev python3-venv libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git
```

### 3. Define your first device
fhempy searches your network and Bluetooth on its own ([autodiscovery](FHEM/bindings/python/fhempy/lib/autodiscovery/README.md)). Found devices are shown right after the installation, new ones later as a popup, one click creates them.

The easiest way: click **+ Install modules** next to `fhempy_local` in the room *fhempy*. Search or browse all modules, click one and press *Set up*. If a module needs more information (e.g. a login or an IP address), the window asks for it and creates the device for you.

<p align="center"><img src="docs/images/module-installer.png" alt="fhempy module installer: search, categories and a tile with logo for every module" width="700"></p>

Of course you can also define devices like any other FHEM device, pick a module from the [list below](#-modules), for example:
```
define matter fhempy matter
define castdevice fhempy googlecast "Living Room"
define eq3bt fhempy eq3bt 00:11:22:33:44:66:77
```
The module's README (linked in the list) explains its options. Its Python libraries are installed automatically on first use.

### 🔄 Updates
Click the update icon of `fhempy_local` or run `set fhempy_local update`. fhempy installs the new version, restarts and also updates its FHEM modules (`10_BindingsIo.pm`, `10_fhempy.pm`, ...) and reloads them in FHEM. FHEM `update` and `shutdown restart` aren't needed for fhempy anymore. With `attr fhempy_local autoUpdate 1` fhempy installs new releases automatically at night (`autoUpdateTime`, default 03:00).

### 🐳 Docker
Running FHEM in Docker? fhempy also runs directly in the FHEM container (e.g. [fhem-docker](https://github.com/fhem/fhem-docker)): it creates its own Python environment in `.fhempy` of the FHEM directory, so keep that directory on a volume. For Bluetooth or Matter use `network_mode: host`.

Alternatively [fhempy-docker](https://github.com/fhem/fhempy-docker) provides a ready-made image per module, e.g. `ghcr.io/fhem/fhempy-docker-<modulename>:latest`. Start the container in the same network as FHEM and connect it with `define fhempy_peer_<modulename> BindingsIo fhempy-<modulename>:15733 fhempy`.

## 🧩 Modules

### ☀️ Energy & solar
|Module | Description|
|-------|------------|
|[alphaesscloud](FHEM/bindings/python/fhempy/lib/alphaesscloud/)|Alpha ESS inverter cloud integration|
|[energie_gv_at](FHEM/bindings/python/fhempy/lib/energie_gv_at/)|Retrieve current Austrian energy status|
|[fusionsolar](FHEM/bindings/python/fhempy/lib/fusionsolar/README.md)|Retrieve data from FusionSolar|
|[goodwe](FHEM/bindings/python/fhempy/lib/goodwe/)|Get data from GoodWe inverters|
|[huawei_modbus](FHEM/bindings/python/fhempy/lib/huawei_modbus/)|Retrieve data from Huawei inverters|
|[rct_power](FHEM/bindings/python/fhempy/lib/rct_power/README.md)|RCT Power inverter|
|[tibber](FHEM/bindings/python/fhempy/lib/tibber/README.md)|Get consumption data from tibber|
|[wienernetze_smartmeter](FHEM/bindings/python/fhempy/lib/wienernetze_smartmeter/)|Retrieve data from Wiener Netze smartmeter|
|[zappi](FHEM/bindings/python/fhempy/lib/zappi/README.md)|Zappi charger|

### 🚗 Cars
|Module | Description|
|-------|------------|
|[bmw](FHEM/bindings/python/fhempy/lib/bmw/README.md)|BMW and MINI (e.g. iX3) via official BMW CarData: battery, range, charging, doors, position, live values|
|[kia_hyundai](FHEM/bindings/python/fhempy/lib/kia_hyundai/README.md)|Kia/Hyundai/Genesis car, official Pleos API (EU) or app interface|
|[seatconnect](FHEM/bindings/python/fhempy/lib/seatconnect/README.md)|Control your Seat/Cupra car|
|[skodaconnect](FHEM/bindings/python/fhempy/lib/skodaconnect/README.md)|Control your Skoda car|
|[volvo](FHEM/bindings/python/fhempy/lib/volvo/)|Retrieve infos from your Volvo car (only new API)|
|[volvo_software_update](FHEM/bindings/python/fhempy/lib/volvo_software_update/README.md)|Get notified about Volvo software updates|

### 🏠 Smart home devices
|Module | Description|
|-------|------------|
|[erelax_vaillant](FHEM/bindings/python/fhempy/lib/erelax_vaillant/README.md)|Control eRelax Vaillant|
|[esphome](FHEM/bindings/python/fhempy/lib/esphome/README.md)|Installs and starts the ESPHome dashboard for easy ESPHome device management|
|[gree_climate](FHEM/bindings/python/fhempy/lib/gree_climate/README.md)|Control Gree HVAC devices|
|[homekit](FHEM/bindings/python/fhempy/lib/homekit/README.md)|Control HomeKit devices|
|[matter](FHEM/bindings/python/fhempy/lib/matter/README.md)|Control Matter devices (lights, plugs, sensors, thermostats, locks, blinds), also devices behind Hue/IKEA/Aqara bridges|
|[matter_bridge](FHEM/bindings/python/fhempy/lib/matter_bridge/README.md)|Use FHEM devices in Apple Home, Google Home, Alexa and SmartThings, including voice control|
|[meross](FHEM/bindings/python/fhempy/lib/meross/README.md)|Control Meross devices|
|[miio](FHEM/bindings/python/fhempy/lib/miio/README.md)|Control Xiaomi WiFi devices|
|[mqtt_ha_discovery](FHEM/bindings/python/fhempy/lib/mqtt_ha_discovery/)|Support Home Assistant MQTT discovery|
|[nefit](FHEM/bindings/python/fhempy/lib/nefit/README.md)|Control Nefit devices|
|[ring](FHEM/bindings/python/fhempy/lib/ring/README.md)|Ring doorbell/chime/cam|
|[pyit600](FHEM/bindings/python/fhempy/lib/pyit600/README.md)|Control Salus iT600 devices|
|[tuya](FHEM/bindings/python/fhempy/lib/tuya/README.md)|Recommended: control Tuya devices locally incl. real-time updates (only WiFi devices)|
|[tuya_cloud](FHEM/bindings/python/fhempy/lib/tuya_cloud/README.md)|Control Tuya devices via cloud incl. real-time updates (WiFi & ZigBee)|
|[tuya_smartlife](FHEM/bindings/python/fhempy/lib/tuya_smartlife/README.md)|Recommended: control Tuya devices via cloud incl. real-time updates (WiFi & ZigBee)|
|[warema](FHEM/bindings/python/fhempy/lib/warema/)|Control Warema devices|
|[xiaomi_gateway3](FHEM/bindings/python/fhempy/lib/xiaomi_gateway3/README.md)|Xiaomi Gateway V3 (only V3!)|
|[xiaomi_tokens](FHEM/bindings/python/fhempy/lib/xiaomi_tokens/README.md)|Retrieve all Xiaomi tokens from the cloud|
|[zigbee2mqtt](FHEM/bindings/python/fhempy/lib/zigbee2mqtt/README.md)|Install, update and run a Zigbee2MQTT server|

### 📶 Bluetooth
|Module | Description|
|-------|------------|
|[ble_monitor](FHEM/bindings/python/fhempy/lib/ble_monitor/README.md)|Supports a lot of BLE devices|
|[ble_presence](FHEM/bindings/python/fhempy/lib/ble_presence/README.md)|Presence detection incl. RSSI for Bluetooth Low Energy|
|[blue_connect](FHEM/bindings/python/fhempy/lib/blue_connect/README.md)|Blue Connect pool sensor|
|[bt_presence](FHEM/bindings/python/fhempy/lib/bt_presence/README.md)|Presence detection incl. RSSI for Bluetooth|
|[eq3bt](FHEM/bindings/python/fhempy/lib/eq3bt/README.md)|Control EQ3 Bluetooth thermostats|
|[gfprobt](FHEM/bindings/python/fhempy/lib/gfprobt/)|Control GF Pro Bluetooth irrigation control|
|[mantra_ble](FHEM/bindings/python/fhempy/lib/mantra_ble/README.md)|mAntra ceiling fan lamps|
|[miflora](FHEM/bindings/python/fhempy/lib/miflora/README.md)|Xiaomi BLE plant sensor|
|[miscale](FHEM/bindings/python/fhempy/lib/miscale/README.md)|Xiaomi Mi Scale V1/2 support|
|[mitemp](FHEM/bindings/python/fhempy/lib/mitemp/README.md)|Xiaomi BLE temperature/humidity sensor|
|[nespresso_ble](FHEM/bindings/python/fhempy/lib/nespresso_ble/README.md)|Nespresso Bluetooth coffee machine|
|[scooter](FHEM/bindings/python/fhempy/lib/scooter/README.md)|Xiaomi and Ninebot e-scooters (also with Scooter Hacking Utility firmware): battery, range, mileage, connects automatically when nearby|

### 🎵 Media
|Module | Description|
|-------|------------|
|[dlna_dmr](FHEM/bindings/python/fhempy/lib/dlna_dmr/)|Control DLNA MediaRenderer devices|
|[googlecast](FHEM/bindings/python/fhempy/lib/googlecast/README.md)|Control Cast devices and stream Spotify|
|[spotify](FHEM/bindings/python/fhempy/lib/spotify/README.md)|Control Spotify Connect and use FHEM as Spotify Connect player|

### 🔍 Presence & discovery
|Module | Description|
|-------|------------|
|[arp_presence](FHEM/bindings/python/fhempy/lib/arp_presence/)|ARP based presence detection, works also for iOS|
|[autodiscovery](FHEM/bindings/python/fhempy/lib/autodiscovery/README.md)|Finds devices in your network and via Bluetooth, adds residents and Bluetooth tags|
|[discover_ble](FHEM/bindings/python/fhempy/lib/discover_ble/README.md)|Replaced by autodiscovery|
|[discover_mdns](FHEM/bindings/python/fhempy/lib/discover_mdns/README.md)|Replaced by autodiscovery|
|[discover_upnp](FHEM/bindings/python/fhempy/lib/discover_upnp/README.md)|Replaced by autodiscovery|

### 🧰 Information & tools
|Module | Description|
|-------|------------|
|[dashboard](FHEM/bindings/python/fhempy/lib/dashboard/README.md)|Modern dashboard for wall, couch and door tablets: set up on the tablet in a minute, doorbell with live video, talking and door opener|
|[ddnssde](FHEM/bindings/python/fhempy/lib/ddnssde/)|Dynamic DNS updater for the free ddnss.de service|
|[geizhals](FHEM/bindings/python/fhempy/lib/geizhals/README.md)|Retrieve prices from geizhals|
|[github_backup](FHEM/bindings/python/fhempy/lib/github_backup/)|Backup FHEM config to GitHub|
|[github_restore](FHEM/bindings/python/fhempy/lib/github_restore/)|Restore FHEM config from GitHub|
|[ikos](FHEM/bindings/python/fhempy/lib/ikos/README.md)|Check prices for Ikos resorts|
|[mcp_server](FHEM/bindings/python/fhempy/lib/mcp_server/README.md)|Control FHEM with AI apps (Claude, LM Studio...), the AI can also create automations for you|
|[object_detection](FHEM/bindings/python/fhempy/lib/object_detection/README.md)|TensorFlow Lite object detection|
|[openmeteo_weather](FHEM/bindings/python/fhempy/lib/openmeteo_weather/README.md)|Weather and forecast from Open-Meteo (replaces google_weather)|
|[piclock](FHEM/bindings/python/fhempy/lib/piclock/README.md)|Create a LED clock with MAX7219|
|[prusalink](FHEM/bindings/python/fhempy/lib/prusalink/README.md)|Prusa 3D printer|
|[push](FHEM/bindings/python/fhempy/lib/push/README.md)|Push notifications to phones and tablets (Android, iPhone), no app and no account, replaces Pushbullet|
|[remote_access](FHEM/bindings/python/fhempy/lib/remote_access/README.md)|FHEM on your phone from anywhere: https address with password via Tailscale Funnel, no VPN app or port forwarding|
|[system_update](FHEM/bindings/python/fhempy/lib/system_update/README.md)|Keeps the Raspberry Pi up to date: security updates every night, backup before and health check after each update, critical packages only on your click|
|[timeline](FHEM/bindings/python/fhempy/lib/timeline/README.md)|What happened at home, e.g. during the holidays: all events as readable story per day, without technical noise|
|[websitetests](FHEM/bindings/python/fhempy/lib/websitetests/)|Do some basic website checks|
|[wienerlinien](FHEM/bindings/python/fhempy/lib/wienerlinien/README.md)|Wiener Linien departure times|
|[helloworld](FHEM/bindings/python/fhempy/lib/helloworld/)|Hello World example for developers to start writing their own module|

## 🩺 Troubleshooting
- **`fhempy_local` stays red**: open the device `fhempyserver_15733` in FHEM. Its reading `python` shows the Python version fhempy found, or why it can't start.
- **Where is the log?** fhempy writes its own log file next to the FHEM log: `log/fhempy-YYYY-MM-DD.log`. Set `attr fhempyserver_15733 verbose 5` for debug output.
- **`Installing fhempy failed: ...`**: the state of `fhempy_local` names the reason, the fhempy log has the details. If uv can't be downloaded from github.com and the system Python has no venv support, run `sudo apt install python3-venv` and restart fhempy with `set fhempyserver_15733 restart`.
- **A module doesn't work**: check its README first. Questions are welcome in the [FHEM forum](https://forum.fhem.de/), bugs in the [GitHub issues](https://github.com/fhempy/fhempy/issues).

## Bluetooth auto recovery
Modules using Bluetooth LE via bleak (blue_connect, eq3bt, gfprobt, mitemp2) detect a stuck Bluetooth adapter and try to recover it automatically. After 3 failed connection attempts in a row (connect errors, or scans which don't see any device at all) the adapter gets recovered, each time escalating one stage further:
1. Power cycle the adapter via BlueZ D-Bus. No extra permissions needed besides the `bluetooth.conf` policy from the module README.
2. Reset the adapter via [bluetooth-auto-recovery](https://github.com/Bluetooth-Devices/bluetooth-auto-recovery) (MGMT power cycle, USB reset). Requires `CAP_NET_ADMIN` for the fhempy process.
3. Restart bluetoothd via `sudo -n systemctl restart bluetooth`. Requires a sudoers entry.

If bluetoothd doesn't answer on D-Bus at all, it gets restarted right away. Stages without the required permissions are skipped. Two recoveries of the same adapter are at least 5 minutes apart (doubling up to 1 hour while the adapter doesn't recover). The reading `connection_recovery` shows the last recovery of a device.

Allow stage 2 by adding `CAP_NET_ADMIN` to the service which starts fhempy (`fhem` on FHEM installations, `fhempy` on remote peers):
```
sudo systemctl edit fhem
```
```
[Service]
AmbientCapabilities=CAP_NET_ADMIN
```

Allow stage 3 via `sudo visudo` (replace `fhem` with the user running fhempy, e.g. `pi` on remote peers):
```
fhem    ALL=NOPASSWD: /usr/bin/systemctl restart bluetooth
```

## fhempy peers (e.g. extend Bluetooth range)
fhempy can run modules on other computers (peers), e.g. a Raspberry Pi close to your Bluetooth devices or a more powerful machine for video object detection. FHEM finds peers on its own and creates a `fhempy_peer_<IP>` device; set a device's `IODev` to it to run that device there.

### Install a peer from FHEM (no terminal needed)
1. Prepare the Raspberry Pi with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/): in the settings set a host name (e.g. `fhempy-bt`), user and password and **enable SSH**.
2. Start the Pi and enter in FHEM:
```
set fhempy_local installPeer fhempy-bt.local pi <password>
```
Use the host name from step 1 with `.local` or the IP address of the Pi, and the user and password you set. The reading `peer_install` of `fhempy_local` shows the progress (system packages, Python, fhempy, service). When it's done, `fhempy_peer_<IP>` is ready. The password is only used for this installation, fhempy doesn't store it.

The peer gets everything at once: the system packages for the Bluetooth modules, Bluetooth permissions for the [auto recovery](#bluetooth-auto-recovery) and a systemd service which starts fhempy on boot. Running `installPeer` again repairs an installation.

### Install a peer from its terminal
Log in to the peer (not your FHEM machine) and run:
```
curl -fsSL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo bash
```
fhempy runs as the user who called `sudo`. If autodiscovery doesn't work (it's based on zeroconf), define the peer yourself: `define fhempy_peer_IP BindingsIo IP:15733 fhempy`.

### Log file and update
The peer's log: `journalctl -u fhempy -f`. Update a peer like the local fhempy with `set fhempy_peer_<IP> update`.

## 🏗️ How it works

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/architecture-dark.svg">
    <img alt="fhempy architecture: FHEM devices talk via BindingsIo to the fhempy Python process, which talks to your devices and cloud services. Optional fhempy peers run on other computers." src="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/architecture-light.svg" width="860">
  </picture>
</p>

In short:

1. **FHEM** – you define a device as usual, e.g. `define livingroom fhempy googlecast`.
2. **BindingsIo** – forwards everything for that device (define, set, attr, ...) to fhempy. `fhempy_local` is created during installation and connects to the fhempy on the same computer.
3. **fhempy** – a Python process that FHEM starts automatically. It loads the matching Python module (here `googlecast`), which talks to your device or cloud service.
4. **Back to FHEM** – readings and state changes travel the same way back and show up in FHEM like for any other device.

Optionally fhempy can also run on **another computer** (a [fhempy peer](#fhempy-peers-eg-extend-bluetooth-range)), e.g. a Raspberry Pi next to a Bluetooth thermostat. FHEM finds it automatically and creates a `fhempy_peer_...` BindingsIo; set a device's `IODev` to it to run that device there.

<details>
<summary>Details for developers</summary>

| Part | What it does |
| --- | --- |
| [10_fhempy.pm](FHEM/10_fhempy.pm) | The FHEM module behind every `define ... fhempy ...` device. Hands all calls to its BindingsIo with `IOWrite`. |
| [10_BindingsIo.pm](FHEM/10_BindingsIo.pm) | DevIo device that connects to fhempy via websocket and exchanges JSON messages. |
| [10_fhempyServer.pm](FHEM/10_fhempyServer.pm) | Starts the local fhempy process. |
| [fhempy](FHEM/bindings/python/fhempy/) | The Python (asyncio) server: receives the messages, runs the module function and replies. |

Example: `define castdevice fhempy googlecast "Living Room"`

1. The fhempy device sends `IOWrite` to BindingsIo.
2. BindingsIo sends a JSON websocket message to fhempy.
3. fhempy loads the module (`googlecast`), creates an instance and calls its `Define` function.
4. FHEM waits for the answer, the same way as for Perl modules, and fhempy returns the result as JSON via websocket.

At any time a module can call FHEM functions like `readingsSingleUpdate(...)` via the fhem.py module (`fhem.readingsSingleUpdate(...)`).

</details>

## Write your own module
Check the [helloworld example](FHEM/bindings/python/fhempy/lib/helloworld/) for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use utils.run_blocking.

## 🤝 Contributing
Due to limited time I'm unable to fully support fhempy on my own and I'm looking for developers to help maintain and enhance the project. Bug fixes, new modules and documentation improvements are all welcome, just open an issue or a pull request. See [DEVELOPMENT.md](DEVELOPMENT.md) to get started.

Your support would mean a lot!
