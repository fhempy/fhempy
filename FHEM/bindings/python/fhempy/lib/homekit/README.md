
# Homekit
This module represents devices which support homekit. It does NOT publish FHEM devices to Siri. If you have a device which supports homekit but doesn't have a proper FHEM module, you can use this module to integrate the device into FHEM.


# Usage
```
define velux_gateway fhempy homekit HOMEKITID PIN
```

 - HOMEKITID: It's normally the MAC address of the device.
 - PIN: HomeKit PIN from the HomeKit device (XXX-XX-XXX)

Autodiscovery finds unpaired HomeKit devices in the network and via Bluetooth.

## Bluetooth devices
HomeKit devices with Bluetooth LE (e.g. Eve Window Guard, Eve Door & Window) work without a hub. They use the Bluetooth scan all fhempy modules share. The device must not be paired with Apple Home, a HomeKit device has only one owner. Remove it there or reset it first. Bluetooth devices aren't polled, they report changes on their own (attribute interval isn't used).


# Thanks
Thanks to the aiohomekit project and Home Assistant which code I used to implement it for fhempy.