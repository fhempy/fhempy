# mAntra BLE
Control your mAntra ceiling fan lamp (Coin, Coin mini, Alisio, etc.) locally via Bluetooth Low Energy (BLE) advertisements. No cloud or smartphone app needed after setup.

## Requirements
The `fhem` user needs passwordless sudo rights for `hcitool`. Add this to `/etc/sudoers.d/011_fhem-nopasswd`:
```
fhem ALL=(ALL) NOPASSWD: /usr/bin/hcitool
```

## Setup
Get your 4-digit hex ID by sharing the lamp via QR code in the official "mAntra lighting" app. Scan the code with another phone's camera - the ID is the 4-digit hex value right after the bracket (e.g. `720E[1F42&...` $\rightarrow$ `1F42`).

```
define BedroomFan fhempy mantra_ble 1F42
```

## Usage
Control light and fan via standard commands (examples for light on/off, brightness, color temperature, and fan settings):
```
set BedroomFan on|off
set BedroomFan light on|off
set BedroomFan brightness 0..100
set BedroomFan ct 2700..6500
set BedroomFan fan on|off
set BedroomFan fan_speed 0..31
set BedroomFan fan_preset summer|winter|sleep|breeze
```
Fan preset "sleep" sets the silent night mode of the fan, preset "winter" reverses the fan rotation, and preset "breeze" ramps speed up and down repeatedly, as the original presets on the remote control.

## Notes
Communication is unidirectional (BLE broadcast), so FHEM acts as the state master.

## Integration with Google Home
If you use `gassistant-fhem` to integrate into your Google Home, you'll have to manually set the homebridgeMapping attribute of your fhempy mantra_ble device, as fan speeds currently cannot be auto-discovered by `gassistant-fhem`.
To do so, and also support the lamp brightness and color temperature settings, add the following attribute by using the following command (replace `BedroomFan` with your actual device name):
```
attr BedroomFan homebridgeMapping {"Brightness":{"reading":"brightness","cmd":"brightness","minValue":0,"maxValue":100},"ColorTemperature":{"reading":"ct","cmd":"ct","temperatureMinK":2700,"temperatureMaxK":6500},"FanSpeed":{"reading":"fan_speed","ordered":true,"reversible":false,"speeds":{"speed_off":{"cmd":"fan off","value":"off","synonyms":{"en":["off","stop","turn off","zero"],"de":["aus","stopp","ausschalten","null"]}},"speed_night":{"cmd":"fan_preset sleep","value":"sleep","synonyms":{"en":["night","night mode","sleep","sleep mode","whisper"],"de":["nacht","nachtmodus","schlaf","schlafmodus","flüstermodus","flüstern","leise"]}},"speed_1":{"cmd":"fan_speed 1","value":"1","synonyms":{"en":["one","speed 1","level 1","low","slow"],"de":["eins","stufe 1","langsam","niedrig"]}},"speed_2":{"cmd":"fan_speed 4","value":"4","synonyms":{"en":["two","speed 2","level 2"],"de":["zwei","stufe 2"]}},"speed_3":{"cmd":"fan_speed 8","value":"8","synonyms":{"en":["three","speed 3","level 3"],"de":["drei","stufe 3"]}},"speed_4":{"cmd":"fan_speed 12","value":"12","synonyms":{"en":["four","speed 4","level 4","medium","mid"],"de":["vier","stufe 4","mittel","mittlere stufe"]}},"speed_5":{"cmd":"fan_speed 17","value":"17","synonyms":{"en":["five","speed 5","level 5"],"de":["fünf","stufe 5"]}},"speed_6":{"cmd":"fan_speed 21","value":"21","synonyms":{"en":["six","speed 6","level 6"],"de":["sechs","stufe 6"]}},"speed_7":{"cmd":"fan_speed 26","value":"26","synonyms":{"en":["seven","speed 7","level 7","fast"],"de":["sieben","stufe 7","schnell"]}},"speed_8":{"cmd":"fan_speed 31","value":"31","synonyms":{"en":["eight","speed 8","level 8","max","maximum","full"],"de":["acht","stufe 8","maximum","maximal","voll","stärkste stufe"]}}}}}
```
This rather long mapping with a couple of synonyms will enable controlling the fan via English and German voice commands in eight steps (roughly corresponding to the steps on the physical mAntra remote control). Note that in order to turn off the fan, you have to say _"Set the fan of <ceiling lamp name> to off"_, instead of _"Turn ceiling fan off"_, as this will turn off the light. This is because I preferred to represent the ceiling fan lamp as _one_ device instead of two (a lamp and a fan) and currently can't be overcome.

## Acknowledgements

Raw packet structure, whitening algorithms, and codec logic are based on the reverse-engineering work done by [NicoIIT](https://github.com/NicoIIT/ha-ble-adv) in the `ha-ble-adv` project (MIT License). The mantra_ble fhempy module has been written by [Fabian Schneider](https://github.com/fabianswebworld). Please don't hesitate to contact me in case of problems or feedback.
