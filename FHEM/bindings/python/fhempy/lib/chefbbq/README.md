# CHEFBBQ

Bluetooth LE BBQ thermometer sold as CHEFBBQ (advertises as `CHEFBBQ`), base station with 4 probes.

## Define

`define bbq fhempy chefbbq <MAC>`

Devices are also found by autodiscovery. By default the connection goes through the local
adapter or Bluetooth proxy with the best signal, see attribute `adapter`.

## Readings

| Reading | Description |
|---|---|
| `temperature_1` … `temperature_4` | Probe temperature in °C (whole degrees) or `unplugged` |
| `ambient_1` … `ambient_4` | Second temperature value reported per probe |
| `target_1` … `target_4` | Target temperature in °C as confirmed by the device |
| `battery_1` … `battery_4` | Probe battery in % (`battery_x_raw`: raw value) |
| `battery` | Base station battery in % (`battery_raw`: raw value) |
| `alarm` | Buzzer alarm `on` / `off` |

## Set

- `target_1` … `target_4 <temperature>`: target temperature of a probe in °C
- `alarm on|off`: buzzer alarm
- `reconnect`: connect again

## Attributes

- `adapter auto|local|proxy|proxy:<name>|hci0|hci1|…`: `auto` (default) connects through
  the local adapter or Bluetooth proxy with the best signal, `local` only through local
  adapters, `proxy` only through Bluetooth proxies, `proxy:<name>` only through this proxy
  and `hciX` only through this local adapter. Useful to pin the connection to the receiver
  closest to the grill. The list shows the local adapters and the connected proxies
  (`set <name> reconnect` updates it). With a fixed local adapter the shared Bluetooth scan
  of fhempy listens on that adapter as well, the module never scans on its own.
- `widget slider|knob`: control for the target temperatures in FHEMWEB
- `tempMin`, `tempMax`: range of the target temperature control (default 30 / 250)
- `batteryRawEmpty`, `batteryRawFull`: raw battery values for 0 % and 100 %
  (default 100 / 158, a freshly charged probe reports 158)

## Example: one row per probe

```
define bbqRG readingsGroup <Probe>,<Temp&nbsp;&deg;C>,<Ambient&nbsp;&deg;C>,<Target&nbsp;&deg;C> bbq:<1>,temperature_1,ambient_1,target_1 bbq:<2>,temperature_2,ambient_2,target_2 bbq:<3>,temperature_3,ambient_3,target_3 bbq:<4>,temperature_4,ambient_4,target_4
attr bbqRG commands { 'target_1' => 'target_1:slider,30,1,250', 'target_2' => 'target_2:slider,30,1,250', 'target_3' => 'target_3:slider,30,1,250', 'target_4' => 'target_4:slider,30,1,250' }
```

Use `&deg;` and `&nbsp;` in labels, a plain `°` breaks the FHEMWEB update.

## Protocol

Service UUID `000084cf-f7e3-55b4-6c4c-9fd140100a1x`, write `…0a16`, notify `…0a17`.
Frames are `CC AA <len> <payload> <xor>` to the device and `CC DD <len> <payload> <xor>`
from the device, `len` is the total frame length and `xor` the XOR of all preceding bytes.

| Frame | Description |
|---|---|
| `FE 01` | start notifications |
| `0F 01 2C 00 <02/00> 00` | alarm on / off |
| `Cx 18 00 40 .. .. <target LE> .. .. 68 42` | target of probe x in 1/100 °C |
| `CC DD 0A 0F 01 2C <bat> <alarm> 01` | status of the base station |
| `CC DD 10 Cx <bat> <flags> <flags> <temp> <target> <temp2> <limit2>` | probe x, uint16 LE in 1/100 °C |
