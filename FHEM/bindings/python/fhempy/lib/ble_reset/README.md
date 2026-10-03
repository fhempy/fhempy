# BLE Reset
BLE reset module is used if you have troubles with BLE issues on your Raspberry Pi. It resets all Bluetooth adapters (power cycle, USB reset if needed) every X hours. After the reset bluetooth should work again as expected.

Modules using Bluetooth LE via bleak also recover stuck adapters automatically, see [Bluetooth auto recovery](../../../../../../README.md#bluetooth-auto-recovery).

## Installation
The reset requires `CAP_NET_ADMIN` for the fhempy process. Add it to the service which starts fhempy (`fhem` on FHEM installations, `fhempy` on remote peers):
```
sudo systemctl edit fhem
```
```
[Service]
AmbientCapabilities=CAP_NET_ADMIN
```

## Usage
```
define ble_reset fhempy ble_reset
```

## Attributes
 - reset_time: Time in HH:MM format at which Bluetooth should be reset
