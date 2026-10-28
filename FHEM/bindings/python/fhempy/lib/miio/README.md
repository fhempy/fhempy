
# MIIO Devices (Xiaomi WiFi Devices)
This module is based on the python-miio:
https://github.com/rytilahti/python-miio

## Usage
```
define cam fhempy miio <TYPE> <IP> <TOKEN>
```
 - TYPE: Choose one of the following types
    - airconditionermiot
    - airconditioningcompanion
    - airconditioningcompanionmcn02
    - airconditioningcompanionv3
    - airdehumidifier
    - airdogx3
    - airfresh
    - airfresha1
    - airfresht2017
    - airhumidifier
    - airhumidifierjsq
    - airhumidifierjsqs
    - airhumidifiermiot
    - airhumidifiermjjsq
    - airpurifier
    - airpurifiermiot
    - airqualitymonitor
    - airqualitymonitorcgdn1
    - alarmclock
    - aqaracamera
    - ceil
    - chuangmicamera
    - chuangmiir
    - chuangmiplug
    - cooker
    - curtainmiot
    - device
    - dreamevacuum
    - fan
    - fan1c
    - fanleshow
    - fanmiot
    - fanp5
    - fanza5
    - g1vacuum
    - gateway
    - heater
    - heatermiot
    - huizuo
    - huizuolampfan
    - huizuolampheater
    - huizuolampscene
    - miotdevice
    - petwaterdispenser
    - philipsbulb
    - philipseyecare
    - philipsmoonlight
    - philipsrwread
    - philipswhitebulb
    - powerstrip
    - pwznrelay
    - roborockvacuum
    - roidmivacuummiot
    - scisharecoffee
    - toiletlid
    - viomivacuum
    - walkingpad
    - waterpurifier
    - waterpurifieryunmi
    - wifirepeater
    - wifispeaker
    - yeelight
    - yeelightdualcontrolmodule

   Older names like vacuum, fanv2, plugv1 or airhumidifierca1 still work.

 - IP: IP address of the device. It's recommended to set the device to a static IP address to prevent IP changes via DHCP.

 - TOKEN: Token can be easily extracted via xiaomi_tokens module:
https://github.com/fhempy/fhempy/blob/master/FHEM/bindings/python/fhempy/lib/xiaomi_tokens/README.md

## Set commands
Set commands are automtically generated based on the type, therefore it's recommended to first of all define a device to see the possible commands.