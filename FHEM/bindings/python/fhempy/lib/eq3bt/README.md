
# EQ3 Bluetooth Thermostat
This module is used to control EQ3 Bluetooth thermostats.

Attention: If you use a firmware newer than 120, you need to pair it with the PIN code displayed on the thermostat.

## Pairing

These instructions were copied from eq3bt python module.

If you have thermostat with firmware version 1.20+ you need to specify the pairing pin. If the pin doesn't work in FHEM, use the procedure below to pair.

```
Press and hold wheel on thermostat until Pair will be displayed. Remember or write it.

$ sudo bluetoothctl
[bluetooth]# power on
[bluetooth]# agent on
[bluetooth]# default-agent
[bluetooth]# scan on
[bluetooth]# scan off
[bluetooth]# pair 00:1A:22:06:A7:83
[agent] Enter passkey (number in 0-999999): <enter pin>
[bluetooth]# trust 00:1A:22:06:A7:83
[bluetooth]# disconnect 00:1A:22:06:A7:83
[bluetooth]# exit

Optional steps:
[bluetooth]# devices - to list all bluetooth devices
[bluetooth]# info 00:1A:22:06:A7:83
Device 00:1A:22:06:A7:83 (public)
	Name: CC-RT-BLE
	Alias: CC-RT-BLE
	Paired: yes
	Trusted: yes
	Blocked: no
	Connected: no
	LegacyPairing: no
	UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
	UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
	UUID: Device Information        (0000180a-0000-1000-8000-00805f9b34fb)
	UUID: Vendor specific           (3e135142-654f-9090-134a-a6ff5bb77046)
	UUID: Vendor specific           (9e5d1e47-5c13-43a0-8635-82ad38a1386f)
	ManufacturerData Key: 0x0000
	ManufacturerData Value:
  00 00 00 00 00 00 00 00 00                       .........
```

Be aware that sometimes if you pair your device then mobile application (calor BT) can't connect with thermostat and vice versa.

## Installation
Add the following settings to `/etc/dbus-1/system.d/bluetooth.conf`
```
  <policy user="fhem">
    <allow own="org.bluez"/>
    <allow send_destination="org.bluez"/>
    <allow send_interface="org.bluez.GattCharacteristic1"/>
    <allow send_interface="org.bluez.GattDescriptor1"/>
    <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
    <allow send_interface="org.freedesktop.DBus.Properties"/>
  </policy>
```
Set the user to the one which runs fhempy. On FHEM installations it's fhem, on remote peers it's normally pi.
Restart dbus afterwards: `sudo systemctl restart dbus`

## Usage
```
define thermostat1 fhempy eq3bt MAC PIN
```

PIN: Optional pairing PIN, required starting from firmware version 120.


## Commands
 - boost on|off
 - childlock on|off
 - comfort
 - desiredTemperature
 - eco
 - mode manual|auto
 - off
 - on
 - resetConsumption all|consumption|consumptionToday|consumptionYesterday
 - updateStatus

## Readings
 - consumption: 1 unit of consumption means 100% valve open for 1 minute. E.g. consumption 10 means 10 minutes valve 100% open or 20 minutes valve 50% open.

## Attributes
 - keep_connected
    - on (default): Connections stays active and commands are more reliable.
    - off: connection is dropped after every command. Command execution takes longer.

## Screenshot
![Screenshot](screenshot.png)