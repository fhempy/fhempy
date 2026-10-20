# E-scooter (Xiaomi, Ninebot, Scooter Hacking Utility)

Shows battery, range, mileage and temperatures of your Xiaomi or Ninebot (Segway) e-scooter
in FHEM. FHEM connects via Bluetooth whenever the scooter is switched on and nearby, e.g. when
you come home or while it is charging.

Works with the current Bluetooth firmware of Xiaomi (M365, Pro, 1S, Pro 2, Mi 3...) and Ninebot
(G30 Max, F, ES, Xiaomi 4...) scooters, also with custom firmware flashed with the
[Scooter Hacking Utility](https://scooterhacking.org) (SHU).

## 1. Create the device

Switch on the scooter, put it close to your FHEM and run:

```
define my_scooter fhempy scooter
```

That's all, you don't need the Bluetooth address. FHEM searches for the scooter and takes the
one with the best signal. Scooters already used by another FHEM device are skipped, so for a
second scooter just define a second device.

## 2. Pair

As soon as the scooter is found, the state shows **pairing, press the power button when it
beeps**. Press the power button of the scooter briefly when it beeps. The state shows the
battery level afterwards, e.g. `78%`.

Pairing is only needed once. If the scooter isn't paired within a minute, use `set my_scooter
pair` and try again.

**Pairing with an app:** Xiaomi and Ninebot scooters remember only one paired app. After you
paired FHEM, the Scooter Hacking Utility or the Mi Home/Segway app might ask you to pair again
(power button). After that, FHEM shows `pairing lost, use set pair`. Use `set my_scooter pair`
to pair FHEM again once you are done with the app.

The scooter accepts only one Bluetooth connection at a time. FHEM connects only for a few
seconds per update, so apps can still connect in between.

## Commands

| Command | Description |
|---|---|
| `set my_scooter update` | Read the values now |
| `set my_scooter pair` | Pair again, press the power button when the scooter beeps |
| `set my_scooter search` | Forget the scooter and search for a new one |

## Attributes

| Attribute | Description |
|---|---|
| `interval` | Seconds between two updates while the scooter is nearby, and between two searches while it is away. Default 60. |
| `protocol` | `auto` (default) detects the scooter type. `xiaomi`: Xiaomi with new Bluetooth firmware, `xiaomi_plain`: Xiaomi with old Bluetooth firmware, `ninebot`: Ninebot/Segway and Xiaomi 4. |

## Readings

| Reading | Description |
|---|---|
| `state` | Battery level, `absent` while the scooter is away or switched off |
| `presence` | `present` or `absent` |
| `battery` | Battery level in % |
| `battery_voltage`, `battery_current` | Battery voltage (V) and current (A) |
| `battery_remaining_capacity`, `battery_capacity` | Remaining and factory capacity (mAh) |
| `battery_temperature1`, `battery_temperature2` | Battery temperatures (°C) |
| `battery_health` | Battery health in % |
| `range` | Estimated remaining range (km) |
| `mileage` | Total mileage (km) |
| `temperature` | Scooter temperature (°C) |
| `error_code` | Error code of the scooter, 0 means no error |
| `serial_number`, `firmware_esc`, `firmware_ble`, `firmware_bms` | Serial number and firmware versions |
| `name`, `protocol`, `rssi` | Bluetooth name, detected protocol and signal strength |

The values keep their last value while the scooter is away. The scooter switches off its
Bluetooth when it is switched off, so FHEM only gets new values while it is switched on.

## Bluetooth permissions

If the state stays at `searching` although the scooter is switched on next to FHEM, add the
following settings to `/etc/dbus-1/system.d/bluetooth.conf`:
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
Set the user to the one which runs fhempy. On FHEM installations it's fhem, on remote peers it's
normally pi. Restart dbus afterwards: `sudo systemctl restart dbus`

The encryption is done by [miauth](https://github.com/dnandha/miauth), thanks to the Scooter
Hacking community for reverse engineering the protocols.
