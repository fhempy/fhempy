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

## 2. Confirm with the power button

As soon as a scooter is found, the state shows **pairing NBScooter1234, press its power button
when it beeps**. Press the power button of your scooter briefly when it beeps. The state shows
the battery level afterwards, e.g. `78%`.

## Only your scooter is used

- A scooter found by the search is only used after you pressed **its** power button. If nobody
  presses it within a minute or two (e.g. it's the scooter of your neighbour), FHEM drops it,
  ignores it until the next `set search` and searches again. Exception: Xiaomi scooters with
  old Bluetooth firmware (`protocol xiaomi_plain`) have no pairing, switch off other scooters
  nearby while searching.
- After the confirmation the device is bound to this one scooter. The readings `address`
  (Bluetooth address) and `name` show which one. FHEM never searches again on its own, other
  scooters nearby are ignored, even if yours is away.
- To use a different scooter, run `set my_scooter search` and confirm the new one with its
  power button.

If the pairing gets lost later, use `set my_scooter pair` and press the power button again.

**Pairing with an app:** Xiaomi and Ninebot scooters remember only one paired app. After you
paired FHEM, the Scooter Hacking Utility or the Mi Home/Segway app might ask you to pair again
(power button). After that, FHEM shows `pairing lost, use set pair`. Use `set my_scooter pair`
to pair FHEM again once you are done with the app.

The scooter accepts only one Bluetooth connection at a time. By default FHEM connects only for
a few seconds per update, so apps can still connect in between. With `attr my_scooter
keep_connected 1` FHEM stays connected while the scooter is nearby, apps can't connect then.

## Commands

| Command | Description |
|---|---|
| `set my_scooter update` | Read the values now |
| `set my_scooter pair` | Pair again, press the power button when the scooter beeps |
| `set my_scooter search` | Forget the scooter and search for a new one, confirm it with its power button |

## Attributes

| Attribute | Description |
|---|---|
| `interval` | Seconds between two updates while the scooter is nearby, and between two searches while it is away. Default 60. |
| `keep_connected` | `1`: stay connected while the scooter is nearby and update every `interval` seconds, apps like the Scooter Hacking Utility can't connect meanwhile. `0` (default): connect only for a few seconds per update. |
| `protocol` | `auto` (default) detects the scooter type. `xiaomi`: Xiaomi with new Bluetooth firmware, `xiaomi_plain`: Xiaomi with old Bluetooth firmware, `ninebot`: Ninebot/Segway and Xiaomi 4. |

## Readings

| Reading | Description |
|---|---|
| `state` | Battery level, `absent` while the scooter is away or switched off |
| `presence` | `present` or `absent` |
| `address`, `name` | Bluetooth address and name of the scooter this device is bound to |
| `connection` | `connected` while FHEM stays connected (`keep_connected 1`), `disconnected` otherwise |
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
| `protocol`, `rssi` | Detected protocol and signal strength |

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
