# Volvo
This module connects to your Volvo account and retrieves data from your car. It can also be used to activate climate control, lock/unlock, etc..

It uses the official Volvo Cars API (Connected Vehicle API v2, Energy API v2, Location API) via the [volvocarsapi](https://github.com/thomasddn/volvo-cars-api) library.

Thanks to iobroker colleagues! Their code helped me to understand the volvo logic:
https://github.com/TA2k/ioBroker.volvo

## Setup

 - Register/Login into https://developer.volvocars.com/account/
 - You need a Google or Github Account, this is not related to your Volvo app credentials
 - Create an Application
 - Copy VCC API Key Primary

## Usage
```
define my_volvo fhempy volvo VCC_API_KEY VOLVO_USERNAME VOLVO_PASSWORD
```

VCC_API_KEY: From developer portal\
VOLVO_USERNAME: Your Volvo app username (=email address)\
VOLVO_PASSWORD: Your Volvo app password

### Login with one-time password
Volvo requires a one-time password for every new login. After the define, Volvo sends
the one-time password to your email address. Enter it with:
```
set my_volvo otp 123456
```
The login is stored (encrypted) and renewed automatically. Volvo asks for a new
one-time password after about 180 days, see reading `login_valid_until`. The module
then sends a new one-time password automatically, just enter it again with `set otp`.
Use `set login` to request a new one-time password manually.

If you have more than one car, set the attribute `car` to the VIN of the car.

## Set
 - `otp <code>`: one-time password from the Volvo email
 - `login`: start a new login, Volvo sends a new one-time password
 - `update`: update all readings now
 - commands of your car, e.g. `lock`, `unlock`, `climatization_start`, `honk`, `flash`
   (depends on your car). Result in readings `lastcommand` and `lastcommand_message`.

## Attributes
 - `car`: VIN of the car (only needed for more than one car)
 - `interval`: update interval in seconds (default 300)
