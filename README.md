<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/logo-dark.svg">
    <img alt="fhempy" src="https://raw.githubusercontent.com/fhempy/fhempy/master/docs/images/logo-light.svg" width="440">
  </picture>
</p>

<p align="center">
  <b>62 ready-to-use integrations for <a href="https://fhem.de">FHEM</a>, written in Python.</b>
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
  <a href="#-modules">Modules</a> ·
  <a href="#-troubleshooting">Troubleshooting</a> ·
  <a href="#fhempy-peers-eg-extend-bluetooth-range">Remote peers</a> ·
  <a href="#write-your-own-module">Write your own module</a>
</p>

## ✨ Why fhempy?
- **Lots of devices out of the box**: Tuya, Xiaomi, Google Cast, Spotify, Zigbee2MQTT, ESPHome, solar inverters, cars, Bluetooth sensors and many more.
- **No Python fiddling**: fhempy sets up its own Python environment (even a newer Python if your system's is too old) and every module installs its libraries automatically the first time you use it.
- **Feels like any other FHEM device**: `define`, `set`, `get`, `attr` and readings work as usual.
- **Extend your range**: run modules on a remote Raspberry Pi, e.g. close to your Bluetooth devices.

## 🚀 Quick start

### 1. Install the system packages
Copy & paste this command on the machine running FHEM:
```
sudo apt install python3 python3-pip python3-dev python3-venv libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git libprotocol-websocket-perl libjson-xs-perl
```

> [!NOTE]
> fhempy runs with Python 3.12 or newer. You don't need to upgrade your system for that: if your Python is older than 3.13 (e.g. Debian 12 Bookworm or Raspberry Pi OS Bookworm), fhempy installs Python 3.13 for itself with [uv](https://docs.astral.sh/uv/). uv also installs all Python packages, which is much faster than pip.

On other distributions install the same packages with your package manager. If there is no package for the Perl module Protocol::WebSocket, install it with `sudo cpan Protocol::WebSocket`.

### 2. Add fhempy to FHEM
Enter these commands one after another in the FHEM command field:
```
update add https://raw.githubusercontent.com/fhempy/fhempy/master/controls_pythonbinding.txt
```
```
update
```
```
shutdown restart
```
```
define fhempy_local BindingsIo fhempy
```

Now lean back: the first start sets up fhempy and **can take up to 15 minutes** on a Raspberry Pi. `fhempy_local` shows a green circle as soon as it's ready.

### 3. Define your first device
Pick a module from the [list below](#-modules) and define it like any other FHEM device, for example:
```
define castdevice fhempy googlecast "Living Room"
define eq3bt fhempy eq3bt 00:11:22:33:44:66:77
define upnp fhempy discover_upnp
```
The module's README (linked in the list) explains its options. Its Python libraries are installed automatically on first use.

### 🐳 Docker
Running FHEM in Docker? [fhempy-docker](https://github.com/fhem/fhempy-docker) provides a ready-made image per module, e.g. `ghcr.io/fhem/fhempy-docker-<modulename>:latest`. Start the container in the same network as FHEM and connect it with `define fhempy_peer_<modulename> BindingsIo fhempy-<modulename>:15733 fhempy`.

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
|[kia_hyundai](FHEM/bindings/python/fhempy/lib/kia_hyundai/README.md)|Control your Kia/Hyundai car|
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
|[ble_reset](FHEM/bindings/python/fhempy/lib/ble_reset/README.md)|Resets all Bluetooth interfaces every X hours|
|[blue_connect](FHEM/bindings/python/fhempy/lib/blue_connect/README.md)|Blue Connect pool sensor|
|[bt_presence](FHEM/bindings/python/fhempy/lib/bt_presence/README.md)|Presence detection incl. RSSI for Bluetooth|
|[eq3bt](FHEM/bindings/python/fhempy/lib/eq3bt/README.md)|Control EQ3 Bluetooth thermostats|
|gfprobt|Control GF Pro Bluetooth irrigation control|
|[miflora](FHEM/bindings/python/fhempy/lib/miflora/README.md)|Xiaomi BLE plant sensor|
|[miscale](FHEM/bindings/python/fhempy/lib/miscale/README.md)|Xiaomi Mi Scale V1/2 support|
|[mitemp](FHEM/bindings/python/fhempy/lib/mitemp/README.md)|Xiaomi BLE temperature/humidity sensor|
|[nespresso_ble](FHEM/bindings/python/fhempy/lib/nespresso_ble/README.md)|Nespresso Bluetooth coffee machine|

### 🎵 Media
|Module | Description|
|-------|------------|
|dlna_dmr|Control DLNA MediaRenderer devices|
|[googlecast](FHEM/bindings/python/fhempy/lib/googlecast/README.md)|Control Cast devices and stream Spotify|
|[spotify](FHEM/bindings/python/fhempy/lib/spotify/README.md)|Control Spotify Connect and use FHEM as Spotify Connect player|

### 🔍 Presence & discovery
|Module | Description|
|-------|------------|
|[arp_presence](FHEM/bindings/python/fhempy/lib/arp_presence/)|ARP based presence detection, works also for iOS|
|discover_ble|Discover Bluetooth LE devices|
|discover_mdns|Discover mDNS (e.g. Google Cast) devices|
|discover_upnp|Discover UPnP devices|

### 🧰 Information & tools
|Module | Description|
|-------|------------|
|[aktionsfinder](FHEM/bindings/python/fhempy/lib/aktionsfinder/)|Keep informed about product promotions|
|[ddnssde](FHEM/bindings/python/fhempy/lib/ddnssde/)|Dynamic DNS updater for the free ddnss.de service|
|[geizhals](FHEM/bindings/python/fhempy/lib/geizhals/README.md)|Retrieve prices from geizhals|
|[github_backup](FHEM/bindings/python/fhempy/lib/github_backup/)|Backup FHEM config to GitHub|
|[github_restore](FHEM/bindings/python/fhempy/lib/github_restore/)|Restore FHEM config from GitHub|
|[google_weather](FHEM/bindings/python/fhempy/lib/google_weather/README.md)|Retrieve weather from Google|
|[ikos](FHEM/bindings/python/fhempy/lib/ikos/README.md)|Check prices for Ikos resorts|
|[object_detection](FHEM/bindings/python/fhempy/lib/object_detection/README.md)|TensorFlow Lite object detection|
|[piclock](FHEM/bindings/python/fhempy/lib/piclock/README.md)|Create a LED clock with MAX7219|
|[prusalink](FHEM/bindings/python/fhempy/lib/prusalink/README.md)|Prusa 3D printer|
|[websitetests](FHEM/bindings/python/fhempy/lib/websitetests/)|Do some basic website checks|
|[wienerlinien](FHEM/bindings/python/fhempy/lib/wienerlinien/README.md)|Wiener Linien departure times|
|helloworld|Hello World example for developers to start writing their own module|

## 🩺 Troubleshooting
- **`fhempy_local` stays red**: open the device `fhempyserver_15733` in FHEM. Its reading `python` shows the Python version fhempy found, or why it can't start.
- **Where is the log?** fhempy writes its own log file next to the FHEM log: `log/fhempy-YYYY-MM-DD.log`. Set `attr fhempyserver_15733 verbose 5` for debug output.
- **`Please make sure that python3-venv package is installed`**: run `sudo apt install python3-venv` and restart fhempy with `set fhempyserver_15733 restart`.
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
fhempy allows to run modules locally (same device as FHEM runs on) or on remote peers. Those remote peers only make sense if you want to extend the range of bluetooth or want to distribute the load of some modules to other more powerfull devices (e.g. video object detection).


### Peer setup (short version)
Only on remote peers, do not run this commands on the FHEM instance. Run this commands with user "pi".

```
### WARNING: DO THIS COMMAND ONLY ON REMOTE PEER, NOT ON YOUR FHEM INSTANCE ###
# systemd service installation
curl -sL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo -E bash -
```

### Peer setup (long version)
Only needed if you didn't run Peer setup (short version). The following steps are only needed if you want to install fhempy on a remote peer, you should not run them on your FHEM installation.

- Setup virtual environment for fhempy: `python3 -m venv .fhempy/fhempy_venv`
- Activate venv: `source .fhempy/fhempy_venv/bin/activate`
- Install fhempy with user pi: `pip3 install --upgrade fhempy`
- Make sure your main fhempy instance (within FHEM) is running
- Test fhempy by just running it with user pi, type `fhempy` and enter. Wait a few seconds until it gets discovered and you see the incoming FHEM connection.
- Systemd configuration for autostart
  - `curl -sL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo -E bash -`
  - fhempy is run with user pi, you can change that in the fhempy.service file in /etc/systemd/system/
- FHEM configuration
  - The remote peer is autodiscovered and will show up in FHEM as device e.g. fhempy_peer_192_168_1_50
  - You can move any device to the remote peer by changing the IODev of the device.
  - If autodiscovery doesn't work (it's based on zeroconf), you can define it with `define fhempy_peer_IP BindingsIo IP:15733 fhempy`

### Log file
`journalctl -u fhempy.service -f`

### Update
Just do `set remote_pybinding update` and the remote peer will install the new package via pip and restart afterwads.

## Functionality

### 10_BindingsIo
This module is a DevIo device which builds a language neutral communicaton bridge in JSON via websockets.
### 10_fhempyServer
This module just starts the fhempy server instance
### 10_fhempy
This module is used as the bridge to BindingsIo. It calls BindingsIo with IOWrite.
### fhempy
This is the Python server instance which handles JSON websocket messages from BindingsIo. Based on the message it executes the proper function and replies to BindingsIo via websocket.

### Call flow
This example shows how Define function is called from the Python module.
 1. define castdevice fhempy googlecast "Living Room"
 2. fhempy sends IOWrite to BindingsIo
 3. BindingsIo sends a JSON websocket message to fhempy
 4. fhempy loads the corresponding module (e.g. googlecast), creates an instance of the object (e.g. googlecast) and calls the Define function on that instance
 5. Define function is executed within the Python context, as long as the function is executed, FHEM waits for the answer the same way as it does for Perl modules
 6. Python Define returns the result via JSON via websocket to BindingsIo

At any time within the functions FHEM functons like readingsSingleUpdate(...) can be called by using the fhem.py module (fhem.readingsSingleUpdate(...)). There are just a few functions supported at the moment.

![Flow Chart](https://raw.githubusercontent.com/fhempy/fhempy/master/flowchart.png)

## Write your own module
Check helloworld example for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use utils.run_blocking.

## 🤝 Contributing
Due to limited time I'm unable to fully support fhempy on my own and I'm looking for developers to help maintain and enhance the project. Bug fixes, new modules and documentation improvements are all welcome, just open an issue or a pull request. See [DEVELOPMENT.md](DEVELOPMENT.md) to get started.

Your support would mean a lot!
