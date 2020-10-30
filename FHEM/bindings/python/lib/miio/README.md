
# MIIO Devices (Xiaomi WiFi Devices)
This module is based on the python-miio:
https://github.com/rytilahti/python-miio

## Usage
```
define cam PythonModule miio <TYPE> <IP> <TOKEN>
```
 - Type can be one of the following
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

 - Token can be easily extracted via xiaomi_tokens module:
https://github.com/dominikkarall/fhem_pythonbinding/blob/master/FHEM/bindings/python/lib/xiaomi_tokens/README.md

## Set commands
All set commands without additional arguments are supported.