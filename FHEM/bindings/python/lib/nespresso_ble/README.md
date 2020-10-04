
# Nespresso BLE
This module is used to connect to a Bluetooth enabled Nespresso coffee machine.

## Usage
```
define nespresso_device PythonModule nespresso_ble <MAC> <AUTHKEY>
```

## Obtain Auth Key (Android only)

1. Activate developer mode on Android
2. Activate Bluetooth HCI snoop log
3. Deactivate Bluetooth and activate it again after about 30s
4. Open Nespresso app and connect to machine
5. Go to developer settings and create bug report
6. Wait for bug report to be generated (takse some minutes)
7. Send bug report via mail to your mail address
8. Open bluetooth_hci.log (FS/data/misc/bluetooth/logs/ in the zip file) in Wireshark
9. Filter on Bluetooth mac: bluetooth.addr == xx:xx:xx:xx:xx:xx:xx:xx
10. Search for	"Sent Write Request, Handle: 0x0014 (Unknown)"
11. Go to frame details below and get the auth key
```
Frame 289: 20 bytes on wire (160 bits), 20 bytes captured (160 bits)
Bluetooth
Bluetooth HCI H4
Bluetooth HCI ACL Packet
Bluetooth L2CAP Protocol
Bluetooth Attribute Protocol
    Opcode: Write Request (0x12)
    Handle: 0x0014 (Unknown)
    Value: 8123456789012345   <=== THIS IS THE AUTH KEY
    [Response in Frame: 307]
```