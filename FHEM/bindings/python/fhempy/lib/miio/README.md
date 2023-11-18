
# MIIO Devices (Xiaomi WiFi Devices)
This module is based on the python-miio:
https://github.com/rytilahti/python-miio

## Usage
```
define cam fhempy miio <TYPE> <IP> <TOKEN>
```
 - TYPE: Choose one of the following types
    - airconditioningcompanion
    - airconditioningcompanionv3
    - airdehumidifier
    - airfresh
    - airfresht2017
    - airhumidifier
    - airhumidifierca1
    - airhumidifiercb1
    - airhumidifierjsq
    - airhumidifiermiot
    - airhumidifiermjjsq
    - airpurifier
    - airpurifiermiot
    - airqualitymonitor
    - alarmclock
    - aqaracamera
    - ceil
    - chuangmicamera
    - chuangmiir
    - chuangmiplug
    - cooker
    - device
    - fan
    - fanp5
    - fansa1
    - fanv2
    - fanza1
    - fanza3
    - fanza4
    - gateway
    - gatewayalarm
    - gatewaydevice
    - gatewaylight
    - gatewayradio
    - gatewayzigbee
    - heater
    - miotdevice
    - philipsbulb
    - philipseyecare
    - philipsmoonlight
    - philipsrwread
    - philipswhitebulb
    - plug
    - plugv1
    - plugv3
    - powerstrip
    - pwznrelay
    - toiletlid
    - vacuum
    - viomivacuum
    - waterpurifier
    - wifirepeater
    - wifispeaker
    - yeelight

 - IP: IP address of the device. It's recommended to set the device to a static IP address to prevent IP changes via DHCP.

 - TOKEN: Token can be easily extracted via xiaomi_tokens module:
https://github.com/fhempy/fhempy/blob/master/FHEM/bindings/python/fhempy/lib/xiaomi_tokens/README.md

## Set commands
Set commands are automtically generated based on the type, therefore it's recommended to first of all define a device to see the possible commands.