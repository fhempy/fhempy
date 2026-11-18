# Bluetooth fitness devices

Heart rate straps, power meters, speed/cadence sensors and smart trainers with the standard
Bluetooth profiles, e.g. Polar H9/H10/Verity Sense, Garmin HRM, Wahoo TICKR, Wahoo KICKR
and KICKR CORE, Tacx, Elite, treadmills and rowers with the Fitness Machine Service.

```
define polar_h10 fhempy ble_fitness A0:9E:1A:12:34:56
define kickr fhempy ble_fitness E8:FE:12:34:56:78
```

Autodiscovery finds them, also via an [ESPHome Bluetooth proxy](../esphome_ble_proxy/README.md)
(needs `active: true` in its YAML for the connection). A chest strap only advertises while it
is worn (moist electrodes), a trainer while it is awake, so put the strap on or pedal once.

fhempy doesn't scan on its own: as soon as the shared Bluetooth scan (local adapter or proxy)
receives the device, it connects. When the device switches off, the readings go to 0 and
fhempy waits for the next advertisement. Most straps and trainers accept two connections,
an app like Zwift or the watch can be used at the same time.

## Readings

| Reading | Meaning |
|---------|---------|
| `state` | `off`, `connecting`, `connected`, or the live values like `210 W, 142 bpm` |
| `heart_rate` | bpm |
| `heart_rate_zone` | 0 to 5 (50/60/70/80/90 % of the maximum heart rate), needs `age` or `max_heart_rate` |
| `rr_interval`, `hrv` | last beat-to-beat interval (ms), heart rate variability (RMSSD of the last 60 s, ms), only straps which send RR intervals (Polar H9/H10, ...) |
| `sensor_contact` | `yes`/`no`, whether the strap touches the skin |
| `power`, `cadence`, `speed` | W, rpm, km/h |
| `distance`, `resistance`, `incline`, `stroke_rate`, `strokes` | from trainers, treadmills and rowers (km, level, %, strokes/min) |
| `batteryPercent`, `battery` | `low` at 15 % or less |
| `trainer_control` | `available` or `none`, after a command the trainer's answer (`ok`, `control not permitted`, ...) |

### Workout summary

A workout starts with the first heart rate, power or cadence and ends 2 minutes after the device
disconnected or after 5 minutes without any of them. `workout` is `active` meanwhile and
`finished` at the end, together with:

| Reading | Meaning |
|---------|---------|
| `workout_duration` | minutes |
| `workout_heart_rate_avg`, `workout_heart_rate_max` | bpm |
| `workout_power_avg`, `workout_power_max`, `workout_energy` | W, kJ |
| `workout_cadence_avg`, `workout_speed_avg`, `workout_distance` | rpm, km/h, km |
| `workout_calories` | kcal: from the power, otherwise from the device, otherwise from the heart rate (needs `age` and `weight`) |
| `workout_zone1` .. `workout_zone5` | minutes in each heart rate zone |

Example, a fan which runs faster the harder you train:

```
define fan_by_heart_rate notify polar_h10:heart_rate_zone:.* { fhem("set fan_basement " . ($EVTPART1 >= 3 ? "high" : $EVTPART1 >= 1 ? "low" : "off")) }
```

## Trainer control

Trainers with a Fitness Machine control point (KICKR, KICKR CORE, ...) get these set commands:

- `set <name> target_power <watts>`: ERG mode, the trainer holds the power whatever the cadence
- `set <name> grade <percent>`: simulation mode, ride a slope of -20 to 20 %
- `set <name> release_control`: ends ERG/simulation, other apps can control the trainer again

Only one app can control the trainer at a time. While Zwift or a similar app controls it,
the commands are refused (`trainer_control` shows `control not permitted`).

## Attributes

- `age`: years, for the maximum heart rate (208 - 0.7 * age) and the calories
- `max_heart_rate`: measured maximum heart rate, overrides the one from the age
- `weight`: kg, for the calories from the heart rate
- `sex`: `male` (default) or `female`, for the calories from the heart rate
- `wheel_circumference`: mm, for the speed of speed sensors and power meters, default 2105
  (700x25C)
