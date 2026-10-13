# arp_presence
This module checks the presence of devices via the ARP table. iOS devices are also supported, which usually won't work properly with LAN ping.

## Usage
```
define presence_my_device fhempy arp_presence IP_OR_MAC
```

- IPv4 addresses and MAC addresses are supported.
- MAC addresses can be specified in the format `00:1a:2b:3c:4d:5e` (Linux), `00-1a-2b-3c-4d-5e` (Windows), `001a.2b3c.4d5e` (Cisco) and `001a2b3c4d5e` (plain hex); all case-insensitive.

## Set commands
 - update: starts a presence scan right away

## Attributes
 - interval: Change scan interval in seconds, default: 60 (seconds)

## Thanks
 - https://github.com/mudape/iphonedetect/
