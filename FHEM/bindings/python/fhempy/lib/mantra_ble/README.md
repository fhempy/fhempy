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
Control light and fan via standard commands:
```
set BedroomFan on
set BedroomFan off
set BedroomFan fan off
set BedroomFan fan_speed 15
set BedroomFan fan_preset summer
```

## Notes
Communication is unidirectional (BLE broadcast), so FHEM acts as the state master.


## Acknowledgements

Raw packet structure, whitening algorithms, and codec logic are based on the reverse-engineering work done by [NicoIIT](https://github.com/NicoIIT/ha-ble-adv) in the `ha-ble-adv` project (MIT License).