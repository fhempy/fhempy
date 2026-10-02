
# kia_hyundai
Connect to your Kia or Hyundai car.

# Usage
```
define my_car fhempy kia_hyundai USERNAME PASSWORD PIN CAR_TYPE REGION
```

USERNAME: E-Mail address of your Kia/Hyundai account
PASSWORD: Password of your Kia/Hyundai account
PIN: Car PIN
CAR_TYPE: Kia or Hyundai
REGION: Europe, USA or Canada

# Set commands
- `update_data`: Get the latest vehicle state from the Kia/Hyundai cloud (cached data, used for the periodic update).
- `force_update`: Request the current state directly from the car and update the readings afterwards. This wakes up the car and Kia/Hyundai may apply rate limits, therefore it is not used for the periodic update.
