
# gree_climate
This module controls your gree climate HVAC which are controlled by EWPE Smart app.

# Usage
```
define gree_scanner fhempy gree_climate scan
```

After a few seconds all your gree climate devices should appeare as separate devices in FHEM.


You can define individual devices with

```
define my_hvac fhempy gree_climate NAME
```
 - NAME: Name of the device which is equivalent to the WiFi hotspot (e.g. c677d9dd)