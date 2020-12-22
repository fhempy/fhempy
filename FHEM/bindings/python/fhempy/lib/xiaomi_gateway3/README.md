
# Xiaomi Gateway 3
This module is used for Xiaomi Mijia Gateway 3.

## Installation
Please check if your firmware is supported or downgrade is needed:

https://github.com/AlexxIT/XiaomiGateway3#supported-firmwares

## Usage
```
define xiaomi_gw3 PythonModule xiaomi_gateway3 IP TOKEN
```
 - TOKEN: Token can be easily extracted via xiaomi_tokens module:

https://github.com/dominikkarall/fhempy/blob/master/FHEM/bindings/python/fhempy/lib/xiaomi_tokens/README.md

The device automatically creates the sensors/devices connected to the gateway within FHEM. Just check for new devices after a few seconds.
