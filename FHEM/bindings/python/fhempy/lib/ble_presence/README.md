
# BLE Presence
This module is used to check the presence of Bluetooth Low Energy devices.

## Installation
### Bluetooth permissions
Add the following settings to `/etc/dbus-1/system.d/bluetooth.conf`
```
  <policy user="fhem">
    <allow own="org.bluez"/>
    <allow send_destination="org.bluez"/>
    <allow send_interface="org.bluez.GattCharacteristic1"/>
    <allow send_interface="org.bluez.GattDescriptor1"/>
    <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
    <allow send_interface="org.freedesktop.DBus.Properties"/>
  </policy>
```
Set the user to the one which runs fhempy. On FHEM installations it's fhem, on remote peers it's normally pi.
Restart dbus afterwards: `sudo systemctl restart dbus`

### BLE permissions
You need to set special permissions to bluepy-helper to allow BLE commands to be sent. bluepy-helper installation path depends on your system.

#### FHEM installations
```
sudo find /opt/fhem -name bluepy-helper
sudo setcap 'cap_net_raw,cap_net_admin+eip' PATH_FROM_FIND
```

#### Remote peers
Run the following commands after the define in FHEM.

```
find $HOME/.local -name bluepy-helper
sudo setcap 'cap_net_raw,cap_net_admin+eip' PATH_FROM_FIND
```

## Usage
```
define ble_tag fhempy ble_presence <MAC>
```
The easiest way: open the autodiscovery device (`fhempy_discovery`), click
"Add Bluetooth tag" and hold the tag next to the Raspberry Pi. The tag with the
strongest signal is created, no MAC needed.

The tag is found by the Bluetooth scan shared with autodiscovery and the other
Bluetooth modules (see the attribute `ble` of autodiscovery). bluepy and its
permissions above are only needed to read the battery level.

### Attributes
- `absent_timeout`: seconds without advertisement until the tag is absent
  (default 60)
- `read_characteristics`: battery (default), all or off
- `hci_device`: adapter used to read the battery level (default hci0)

AirTags, Samsung SmartTags and other Find My tags change their address every
few minutes and can't be tracked.
