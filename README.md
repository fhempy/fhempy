[![Download](https://img.shields.io/pypi/dm/fhempy)](https://pypistats.org/packages/fhempy)
[![python](https://img.shields.io/badge/python-3.7+-critical)](https://github.com/fhempy/fhempy)
[![Version](https://img.shields.io/pypi/v/fhempy)](https://pypi.org/project/fhempy/)
[![LastCommit](https://img.shields.io/github/last-commit/fhempy/fhempy)](https://github.com/fhempy/fhempy/commits/master)
[![BuyCoffee](https://img.shields.io/badge/buycoffee-thx-blue)](https://paypal.me/todominik)

# fhempy

fhempy allows the usage of Python 3 (NOT 2!) language to write FHEM modules. Python 3.8 or higher is required, therefore I recommend using bullseye.

This repository includes following working modules:

|Module | Description|
|-------|--------------|
|[ble_monitor](FHEM/bindings/python/fhempy/lib/ble_monitor/README.md)|Supports a lot of BLE devices|
|[ble_presence](FHEM/bindings/python/fhempy/lib/ble_presence/README.md)|Presence detection incl. RSSI for Bluetooth Low Energy|
|[ble_reset](FHEM/bindings/python/fhempy/lib/ble_reset/README.md)|Resets all Bluetooth interfaces every X hours|
|[bt_presence](FHEM/bindings/python/fhempy/lib/bt_presence/README.md)|Presence detection incl. RSSI for Bluetooth|
|[blue_connect](FHEM/bindings/python/fhempy/lib/blue_connect/README.md)|Blue Connect|
|[ddnssde](FHEM/bindings/python/fhempy/lib/ddnssde/)|Dynamic DNS updater for free ddnss.de service|
|discover_mdns|Discover mDNS (e.g. googlecast) devices|
|discover_ble|Discover Bluetooth LE devices|
|discover_upnp|Discover UPnP devices|
|dlna_dmr|Control DLNA MediaRenderer devices|
|[eq3bt](FHEM/bindings/python/fhempy/lib/eq3bt/README.md)|Control EQ3 Bluetooth thermostat|
|[erelax_vaillant](FHEM/bindings/python/fhempy/lib/erelax_vaillant/README.md)|Control eRelax Vaillant|
|[esphome](FHEM/bindings/python/fhempy/lib/esphome/README.md)|Installs and starts the ESP Home dashboard for easy ESP Home device management|
|[fusionsolar](FHEM/bindings/python/fhempy/lib/fusionsolar/README.md)|Retrieve values from FusionSolar Kiosk|
|[geizhals](FHEM/bindings/python/fhempy/lib/geizhals/README.md)|Retrieve prices from geizhals|
|gfprobt|Control GF Pro Bluetooth irrigation control|
|[github_backup](FHEM/bindings/python/fhempy/lib/github_backup/)|Backup FHEM config to github|
|[googlecast](FHEM/bindings/python/fhempy/lib/googlecast/README.md)|Control Cast devices and stream Spotify|
|[google_weather](FHEM/bindings/python/fhempy/lib/google_weather/README.md)|Retrieve weather from Google|
|[gree_climate](FHEM/bindings/python/fhempy/lib/gree_climate/README.md)|Control gree HVAC devices|
|helloworld|Hello World example for developers to start writing their own module|
|[kia_hyundai](FHEM/bindings/python/fhempy/lib/kia_hyundai/README.md)|Control your Kia/Hyundai car|
|[meross](FHEM/bindings/python/fhempy/lib/meross/README.md)|Control Meross devices|
|[miscale](FHEM/bindings/python/fhempy/lib/miscale/README.md)|Xiaomi Mi Scale V1/2 support|
|[miflora](FHEM/bindings/python/fhempy/lib/miflora/README.md)|Xiaomi BLE Plant Sensor|
|[miio](FHEM/bindings/python/fhempy/lib/miio/README.md)|Control Xiaomi WiFi devices|
|[mitemp](FHEM/bindings/python/fhempy/lib/mitemp/README.md)|Xiaomi BLE Temperature/Humidity Sensor|
|[nefit](FHEM/bindings/python/fhempy/lib/nefit/README.md)|Control nefit devices|
|[nespresso_ble](FHEM/bindings/python/fhempy/lib/nespresso_ble/README.md)|Nespresso Bluetooth coffee machine|
|[object_detection](FHEM/bindings/python/fhempy/lib/object_detection/README.md)|TensorFlow Lite object detection|
|[pyit600](FHEM/bindings/python/fhempy/lib/pyit600/README.md)|Control Salus iT600 devices|
|[rct_power](FHEM/bindings/python/fhempy/lib/rct_power/README.md)|RCT Power inverter|
|[ring](FHEM/bindings/python/fhempy/lib/ring/README.md)|Ring doorbell/chime/cam|
|[seatconnect](FHEM/bindings/python/fhempy/lib/seatconnect/README.md)|Control your Seat/Cupra car|
|[spotify](FHEM/bindings/python/fhempy/lib/spotify/README.md)|Control Spotify Connect and use FHEM as Spotify Connect player|
|[skodaconnect](FHEM/bindings/python/fhempy/lib/skodaconnect/README.md)|Control your skoda car|
|[tuya](FHEM/bindings/python/fhempy/lib/tuya/README.md)|Control tuya devices localy incl. real-time updates (only WiFi devices)|
|[tuya_cloud](FHEM/bindings/python/fhempy/lib/tuya_cloud/README.md)|Control tuya devices via cloud incl. real-time updates (WiFi & ZigBee)|
|[warema](FHEM/bindings/python/fhempy/lib/warema/)|Control Warema devices|
|[wienerlinien](FHEM/bindings/python/fhempy/lib/wienerlinien/README.md)|Wiener Linien departure times|
|[xiaomi_gateway3](FHEM/bindings/python/fhempy/lib/xiaomi_gateway3/README.md)|Xiaomi Gateway V3 (only V3\!)|
|[xiaomi_tokens](FHEM/bindings/python/fhempy/lib/xiaomi_tokens/README.md)|Retrieve all Xiaomi Tokens from Cloud|
|[volvo_software_update](FHEM/bindings/python/fhempy/lib/volvo_software_update/README.md)|Get notified about Volvo software updates|
|[zigbee2mqtt](FHEM/bindings/python/fhempy/lib/zigbee2mqtt/README.md)|Install, update and run Zigbee2MQTT server|

## Installation
Python >=3.8 is required, Python 2 won't work\!

### Console
#### Debian 11 (Bullseye)
Copy & paste this command if you are running Debian Bullseye.
```
sudo apt install python3 python3-pip python3-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git libprotocol-websocket-perl
```

#### Others
Use the following 2 commands if you run Debian 10 (Buster) or older (e.g. stretch, jessie, ...).
```
sudo apt install python3 python3-pip python3-dev libffi-dev libssl-dev libjpeg-dev zlib1g-dev autoconf build-essential libglib2.0-dev libdbus-1-dev bluez libbluetooth-dev git
```
```
sudo cpan Protocol::WebSocket
```

### FHEM
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

Wait a few minutes until fhempy is installed. **This might take up to 15 minutes!** fhempy_local will show up with a green circle when finished.
All further requirements are installed automatically via pip as soon as the specific module is used the first time.
 
## Usage in FHEM (examples)
This are just a few examples for some modules, please see the modules readme linked in the table above for more details
 - `define castdevice fhempy googlecast "Living Room"`
 - `define eq3bt fhempy eq3bt 00:11:22:33:44:66:77`
 - `define upnp fhempy discover_upnp`

## fhempy peers (e.g. extend Bluetooth range)
fhempy allows to run modules locally (same device as FHEM runs on) or on remote peers. Those remote peers only make sense if you want to extend the range of bluetooth or want to distribute the load of some modules to other more powerfull devices (e.g. video object detection).


### Peer setup (short version)
Only on remote peers, do not run this commands on the FHEM instance. Run this commands with user "pi".

```
### WARNING: DO THIS COMMAND ONLY ON REMOTE PEER, NOT ON YOUR FHEM INSTANCE ###
pip3 install --upgrade fhempy
# systemd service installation
curl -sL https://raw.githubusercontent.com/fhempy/fhempy/master/install_systemd_fhempy.sh | sudo -E bash -
```

### Peer setup (long version)
Only needed if you didn't run Peer setup (short version). The following steps are only needed if you want to install fhempy on a remote peer, you should not run them on your FHEM installation.

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

![Flow Chart](/flowchart.png)

## Write your own module
Check helloworld example for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use utils.run_blocking.
