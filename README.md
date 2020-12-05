![Download](https://img.shields.io/pypi/dw/fhempy)
![Version](https://img.shields.io/pypi/v/fhempy)
![LastCommit](https://img.shields.io/github/last-commit/dominikkarall/fhempy)

# fhempy (BETA)

fhempy allows the usage of Python 3 (NOT 2!) language to write FHEM modules

This repository includes following working modules:
Module | Description
-------|--------------
[ble_presence](FHEM/bindings/python/lib/ble_presence/README.md)|Presence detection incl. RSSI for Bluetooth Low Energy
[ble_reset](FHEM/bindings/python/lib/ble_reset/README.md)|Resets all Bluetooth interfaces every X hours
[bt_presence](FHEM/bindings/python/lib/bt_presence/README.md)|Presence detection incl. RSSI for Bluetooth
discover_mdns|Discover mDNS (e.g. googlecast) devices
discover_ble|Discover Bluetooth LE devices
discover_upnp|Discover UPnP devices
dlna_dmr|Control DLNA MediaRenderer devices)
[eq3bt](FHEM/bindings/python/lib/eq3bt/README.md)|Control EQ3 Bluetooth thermostat
[esphome](FHEM/bindings/python/lib/esphome/README.md)|Installs and starts the ESP Home dashboard for easy ESP Home device management
[googlecast](FHEM/bindings/python/lib/googlecast/README.md)|Control Cast devices
helloworld|Hello World example
[miflora](FHEM/bindings/python/lib/miflora/README.md)|Xiaomi BLE Plant Sensor
[miio](FHEM/bindings/python/lib/miio/README.md)|Control Xiaomi WiFi devices
[mitemp](FHEM/bindings/python/lib/mitemp/README.md)|Xiaomi BLE Temperature/Humidity Sensor
[nespresso_ble](FHEM/bindings/python/lib/nespresso_ble/README.md)|Nespresso Bluetooth coffee machine
[object_detection](FHEM/bindings/python/lib/object_detection/README.md)|TensorFlow Lite object detection
[ring](FHEM/bindings/python/lib/ring/README.md)|Ring doorbell/chime/cam
[wienerlinien](FHEM/bindings/python/lib/wienerlinien/README.md)|Wiener Linien departure times
xiaomi_gateway3|Xiaomi Gateway V3 (only V3!)
[xiaomi_tokens](FHEM/bindings/python/lib/xiaomi_tokens/README.md)|Retrieve all Xiaomi Tokens from Cloud

## Installation
Python >=3.7 is required, Python 2 won't work!

### Console
```
sudo apt install python3 python3-pip libssl-dev libffi-dev

sudo cpan Protocol::WebSocket
```
### FHEM
```
update add https://raw.githubusercontent.com/dominikkarall/fhempy/master/controls_pythonbinding.txt

update

define local_pybinding BindingsIo Python
```

All further requirements are installed automatically via pip as soon as the specific module is used the first time.
 
## Usage in FHEM (examples)
This are just a few examples for some modules, please see the modules readme linked in the table above for more details
 - `define castdevice PythonModule googlecast "Living Room"`
 - `define eq3bt PythonModule eq3bt 00:11:22:33:44:66:77`
 - `define upnp PythonModule discover_upnp`

## Run Python modules on remote Python peers (e.g. extend Bluetooth range)
FHEM Pythonbinding allows to run modules locally (same device as FHEM runs on) or on remote peers. Those remote peers only make sense if you want to extend the range of bluetooth or want to distribute the load of some modules to other more powerfull devices (e.g. video object detection).

### Installation
The following steps are only needed if you want to install FHEM Pythonbinding on a remote peer, you should not run them on your FHEM installation.

- `sudo pip3 install fhempy`
- Systemd configuration for autostart
  - `curl -sL https://raw.githubusercontent.com/dominikkarall/fhempy/master/install_systemd_fhempy.sh | sudo -E bash -`
  - fhempy is run with user pi, you can change that in the fhempy.service file in /etc/systemd/system/
- FHEM configuration
  - `define remote_pybinding BindingsIo IP:15733 Python`
  - `define eq3device PythonModule eq3bt MAC`
  - `attr eq3device IODev remote_pybinding`

### Log file
`journalctl -u fhempy.service -f`

### Update
Just do `set remote_pybinding update` and the remote peer will install the new package via pip and restart afterwads.

## Functionality

### 10_BindingsIo
This module is a DevIo device which builds a language neutral communicaton bridge in JSON via websockets.
### 10_PythonBinding
This module just starts the fhempy server instance
### 10_PythonModule
This module is used as the bridge to BindingsIo. It calls BindingsIo with IOWrite.
### fhempy
This is the Python server instance which handles JSON websocket messages from BindingsIo. Based on the message it executes the proper function and replies to BindingsIo via websocket.

### Call flow
This example shows how Define function is called from the Python module.
 1. define castdevice PythonModule googlecast "Living Room"
 2. PythonModule sends IOWrite to BindingsIo
 3. BindingsIo sends a JSON websocket message to fhempy
 4. fhempy loads the corresponding module (e.g. googlecast), creates an instance of the object (e.g. googlecast) and calls the Define function on that instance
 5. Define function is executed within the Python context, as long as the function is executed, FHEM waits for the answer the same way as it does for Perl modules
 6. Python Define returns the result via JSON via websocket to BindingsIo

At any time within the functions FHEM functons like readingsSingleUpdate(...) can be called by using the fhem.py module (fhem.readingsSingleUpdate(...)). There are just a few functions supported at the moment.

![Flow Chart](/flowchart.png)

## Write your own module
Check helloworld example for writing an own module. Be aware that no function which is called from FHEM is allowed to run longer than 1s. In general no blocking code should be used with asyncio. If you want to call blocking code, use run_in_executor (see googlecast code).
