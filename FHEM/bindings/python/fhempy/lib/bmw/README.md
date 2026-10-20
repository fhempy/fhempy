# BMW and MINI (BMW CarData)

Shows battery level, range, mileage, charging, doors, windows, tire pressure, position and
much more of your BMW or MINI in FHEM, e.g. of a BMW iX3. It uses **BMW CarData**, the official
interface BMW offers its customers in Europe since 2025 (the old My BMW app interface used by
other tools was blocked by BMW in September 2025).

You only need your My BMW login and one ID that you create yourself in the BMW portal. You
don't need the VIN of your car, FHEM finds it.

## 1. Create the device

```
define my_bmw fhempy bmw
```

## 2. Create your client ID at BMW (once, about 3 minutes)

The detail page of the device in FHEMWEB shows these steps with links:

1. Open [My BMW](https://www.bmw.de/de-de/mybmw/vehicle-overview) (MINI:
   [My MINI](https://www.mini.de/de-de/mymini/vehicle-overview)), log in and select your car.
2. Click the tile **BMW CarData** and then **CarData Client erstellen** (Create CarData Client).
3. Switch on both **Zugriff auf CarData API anfragen** (CarData API) and **CarData Stream**.
   If the page shows an error, reload it and switch them on one after the other.
4. Copy the client ID, paste it on the detail page of the device in FHEMWEB and click
   **Save** (or use `set my_bmw client_id <client ID>`).

You can also give the client ID directly when you create the device:
`define my_bmw fhempy bmw 1a2b3c4d-...`

## 3. Log in

FHEM now shows a link and a code on the detail page (and in the state). Open the link, log
in with your My BMW account and confirm. A few seconds later FHEM shows your car, e.g.
`state 78% 312 km`. The login is kept, also after a restart of FHEM.

## 4. Live values (optional)

FHEM requests the values from the BMW server every 40 minutes. BMW allows only 50 requests
per day, so this is as often as it gets.

For **live values** (e.g. the battery level while charging, doors and position right after you
park) switch on the CarData stream for your car: open the BMW CarData page of your car again,
click **Datenauswahl ändern** (change data selection) under **CarData Stream**, tick the values
you want (e.g. everything under *Elektrofahrzeug* and *Fahrzeugstatus*) and save. Lock or unlock
the car in the My BMW app to make it send its values. While live values arrive, FHEM doesn't
need to request them and saves the requests.

BMW allows only one stream per BMW account. If another program (e.g. Home Assistant) already
uses the stream of your account, one of them doesn't get live values.

## Readings

| Reading | Description |
|---|---|
| `soc` | Battery level in % |
| `soc_target` | Charging target in % |
| `range` | Electric range in km as shown in the car |
| `mileage` | Mileage in km |
| `charging_status` | Charging state as sent by BMW |
| `charging_power` | Charging power in kW |
| `charging_time_remaining` | Minutes until the charging target is reached |
| `plugged` | `yes` when the charging cable is plugged in |
| `lock`, `doors` | Lock state of the car |
| `door_front_driver`, `door_front_passenger`, ... | `open` or `closed` |
| `window_front_driver`, ... | Window state |
| `trunk`, `hood` | `open` or `closed` |
| `latitude`, `longitude`, `heading` | Position of the car |
| `tire_front_left`, ... | Tire pressure |
| `battery_12v`, `battery_health` | 12 V battery level, high voltage battery health |
| `climate` | Air conditioning / preconditioning state |
| `service_distance`, `inspection_date` | Next service and inspection |
| `check_control_messages` | Warnings of the car |
| `model`, `brand`, `color`, `construction_date`, `vin` | Data of your car |
| `last_update` | Time of the newest value sent by the car |
| `stream` | `connected` when FHEM receives live values |
| `api_requests_24h` | BMW requests in the last 24 hours (max. 50) |

Values that are not in this list (e.g. from your stream data selection) get a reading named
after the BMW value, e.g. `cabin_sunroof_relativePosition`. Which values your car sends depends
on the car, e.g. a car with combustion engine sends no battery level.

## Commands

| Command | Description |
|---|---|
| `set my_bmw client_id <client ID>` | Save the client ID and start the login |
| `set my_bmw login` | Log in again |
| `set my_bmw update` | Request all values now (counts towards the 50 requests per day) |

## Attributes

| Attribute | Description |
|---|---|
| `interval` | Seconds between two requests to the BMW server, default 2400 (40 minutes), minimum 900. No request is made while live values arrive. |
| `vin` | Only for several cars in one BMW account: the VIN of the car to show (reading `vehicles` lists all cars). Default: the first car. |

## Good to know

- BMW CarData only reads values, it can't lock the car or start the air conditioning.
- If the login expires (e.g. after FHEM was switched off for a long time), FHEM shows a new
  login link automatically.
- BMW CarData is available for BMW and MINI customers in Europe. BMW motorcycles are listed
  but send no data.
