
# Homekit
This module represents devices which support homekit. It does NOT publish FHEM devices to Siri. If you have a device which supports homekit but doesn't have a proper FHEM module, you can use this module to integrate the device into FHEM.


# Usage
```
define velux_gateway fhempy homekit HOMEKITID PIN
```

 - HOMEKITID: It's normally the MAC address of the device.
 - PIN: HomeKit PIN from the HomeKit device (XXX-XX-XXX)


# Thanks
Thanks to the aiohomekit project and Home Assistant which code I used to implement it for fhempy.