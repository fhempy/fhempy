# Skoda (MyŠkoda Public API)

Connects FHEM to the official MyŠkoda Public API of Škoda. The module doesn't
assume a specific model or equipment: it shows what the API reports for your
car and offers only the commands your car supports.

Module by forum user **Wolle02**, integrated into fhempy.

## Usage

You need an API key for the MyŠkoda Public API and the VIN of the car the key
is enabled for.

```
define my_skoda fhempy skoda_api API_KEY VIN [S-PIN]
```

The S-PIN is optional and only needed for the auxiliary heating. Instead of the
define you can also set the attributes `api_key`, `vin` and `spin`.

The first update runs right after the define, afterwards every 30 minutes
(attribute `update_interval`, minimum 300 seconds). When the API answers with
HTTP 429 the module waits as long as the server asks for (`Retry-After`).

## Readings

- Every JSON value of the API gets a reading with the prefix `api_`, nested
  fields are joined with `_`, e.g. `vehicle.odometer.mileageInKm` becomes
  `api_vehicle_odometer_mileageInKm`. Lists are stored as JSON and every entry
  as its own reading. New API fields show up without a module update.
- `api_rawJson`: the complete answer of the API.
- Short readings for frequently used values: `mileage`, `fuelLevel` (fuel or
  battery in %), `range`, `totalRange`, `parkingAddress`, `latitude`,
  `longitude`, `doorsLocked`, `locked`, `doors`, `windows`, `lights`, `trunk`,
  `bonnet`, `sunroof` and the `...CapturedAt` timestamps.
- `apiErrors`: partial errors of the API, e.g. functions the car doesn't
  support or that are temporarily unavailable.
- `rateLimitRemaining`, `rateLimitLimit`, `rateLimitReset`, `apiKeyExpiresAt`:
  quota and API key expiry reported by the server.
- `lastApiAttempt`, `lastApiUpdate`, `lastApiError`: last poll, last successful
  poll and last error (empty after a successful poll).
- `lastCommand`, `lastCommandStatus`, `lastCommandAt`, `lastCommandError`:
  result of the last remote command.

## Set commands

Before the first answer of the API only `update` is available. Afterwards
commands whose area the API reports as `*_UNSUPPORTED` are hidden.

| Command | Function |
|---|---|
| `update` | Update all readings now. |
| `start_air_conditioning` / `stop_air_conditioning` | Air conditioning, uses `target_temperature` and `ac_without_external_power`. |
| `start_auxiliary_heating` / `stop_auxiliary_heating` | Auxiliary heating, needs the S-PIN. |
| `start_active_ventilation` / `stop_active_ventilation` | Active ventilation. |
| `start_charging` / `stop_charging` | Charging. |
| `charge_limit <percent>` | Target state of charge, the car may accept only some values. |
| `charge_mode <mode>` | `MANUAL`, `TIMER`, `TIMER_CHARGING_WITH_CLIMATISATION`, `PREFERRED_CHARGING_TIMES`, `ONLY_OWN_CURRENT`, `IMMEDIATE_DISCHARGING` or `HOME_STORAGE_CHARGING`. |
| `update_charging_profile <id>` | Replace a charging profile with the JSON of attribute `charging_profile_json` (its `id` must match). |

Remote commands change the state of the car and use additional API requests.

## Attributes

| Attribute | Meaning |
|---|---|
| `api_key`, `vin`, `spin` | Only needed if they are not part of the define. |
| `update_interval` | Update interval in seconds, default 1800, minimum 300. |
| `target_temperature` | Target temperature in °C for air conditioning and auxiliary heating (default 21). |
| `ac_without_external_power` | Allow air conditioning without external power: `1` (default) or `0`. |
| `auxiliary_heating_duration` | Duration of the auxiliary heating in seconds (default 120). |
| `auxiliary_heating_mode` | `HEATING` (default) or `VENTILATION`. |
| `charging_profile_json` | Complete JSON of a charging profile for `update_charging_profile`. |

## Notes

- API key, VIN, S-PIN, GPS position and `api_rawJson` are personal data, don't
  share them publicly.
- Which functions work depends on the car, its equipment and the permissions of
  the API key. A command can end with an API error, see `lastCommandError`.
- The older module [skodaconnect](../skodaconnect/README.md) uses the
  unofficial Skoda Connect login with username and password.
