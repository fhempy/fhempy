# kia_hyundai
Connect to your Kia, Hyundai or Genesis car.

In Europe Kia and Hyundai block the old app interface. Use the official **Pleos Vehicle
Data API** instead (EU Data Act, Europe only), it only needs a client ID and a client secret
which you create yourself in a few minutes.

# Pleos Vehicle Data API (Europe, recommended)
```
define my_car fhempy kia_hyundai
```

The detail page of the device in FHEMWEB shows these steps with links:

1. Open the [Pleos Playground](https://pleos.ai/playground) and create a free account.
2. Click on your account icon and open **My Vehicle Data API**.
3. Choose the tab of your brand (Kia, Hyundai or Genesis), accept the terms, click
   **Get API Key** and log in with your Kia Connect / Bluelink / Genesis Connected account
   (the account of the main user of the car).
4. Copy the client ID and the client secret, paste them on the detail page of the device and
   click **Save** (or use `set my_car credentials <client ID> <client secret>`).

FHEM finds the brand and the car on its own, the client secret is stored encrypted. See also
the [Pleos instructions](https://document.pleos.ai/en/api-reference/vehicle-data-api/getting-started/for-private-users/request-my-vehicle-api-key).

The API is read-only: it shows the values the car last sent to the Kia/Hyundai server (e.g.
after driving or while charging), it never wakes up the car and can't lock the car or start
the climate control. The key contains only the cars which were in your app account when you
created it, for a new car delete the key and create a new one.

## Readings
- `soc`, `range`, `odometer` (km), `charging` (on/off), `charging_status`, `plugged`,
  `charging_time_remaining` (minutes), `charge_limit_ac`, `charge_limit_dc`, `climate`,
  `latitude`, `longitude`, `last_update`
- All values Pleos sends, e.g. `battery_charge_stateOfCharge`, `powertrain_...`,
  `driving_...`, `location_...`, `status_...`

## Attributes
- `update_interval`: minutes between two requests, default 15
- `vin`: only needed if there are several cars in your key

## Set commands
- `credentials <client ID> <client secret>`: your personal Pleos API key
- `update_data`: get the latest values from the Pleos server now

# Kia Connect / Bluelink app interface (old)
```
define my_car fhempy kia_hyundai USERNAME PASSWORD PIN CAR_TYPE REGION
```

USERNAME: E-Mail address of your Kia/Hyundai account
PASSWORD: Password of your Kia/Hyundai account
PIN: Car PIN
CAR_TYPE: Kia or Hyundai
REGION: Europe, USA or Canada

## Set commands
- `update_data`: Get the latest vehicle state from the Kia/Hyundai cloud (cached data, used for the periodic update).
- `force_update`: Request the current state directly from the car and update the readings afterwards. This wakes up the car and Kia/Hyundai may apply rate limits, therefore it is not used for the periodic update.
- `lock`, `unlock`, `start_climate`, `stop_climate`, `start_charge`, `stop_charge`, `charge_limits`
