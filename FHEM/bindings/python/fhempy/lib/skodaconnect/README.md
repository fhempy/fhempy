
# Skoda Connect
This module connects to your Skoda Connect accounts and retrieves data from your car. It can also be used to activate climate control, lock/unlock, etc..

## Usage
```
define my_skoda PythonModule skodaconnect my@account.com PaSSwOrD SPIN
```

If you have more than one car, set the attribute `vin` to the car you want to connect to.

## Attributes
 - vin: VIN of the car you want to connect to