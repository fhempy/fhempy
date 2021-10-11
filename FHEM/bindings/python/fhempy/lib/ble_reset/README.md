
# BLE Reset
BLE reset module is used if you have troubles with BLE issues on your Raspberry Pi. It restarts the bluetooth service and resets all hci devices. After the restart/reset bluetooth should work again as expected.

## Installation
```
sudo visudo
```
add the following entries in the "User privilege specification" section
```
fhem    ALL=NOPASSWD: /bin/systemctl restart bluetooth
fhem    ALL=NOPASSWD: /bin/hciconfig hci? reset
fhem    ALL=NOPASSWD: /bin/hciconfig hci? up
```

## Usage
```
define ble_reset fhempy ble_reset
```

## Attributes
 - reset_time: Time in HH:MM format at which Bluetooth should be reset