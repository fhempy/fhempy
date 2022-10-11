
# arp_presence
This module checks the presence of devices via the ARP table. iOS devices are also supported, which ususally don't work properly with LAN ping.

# Usage
```
define my_iphone fhempy arp_presence IP
```

Thanks to:
 - https://github.com/mudape/iphonedetect/