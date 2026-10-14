# Wiener Netze Smartmeter
This module displays data from the smartmeter network of Wiener Netze (Vienna).


## Usage
```
define my_consumption fhempy wienernetze_smartmeter USERNAME PASSWORD
```

USERNAME: Log.wien username
PASSWORD: Log.wien password

The login (log.wien with PKCE) and the API follow the Home Assistant
integration https://github.com/DarwinsBuddy/WienerNetzeSmartmeter.
Readings are updated every hour (`consumptions`, `meterReadings`),
`baseInformation` once after login.

`state` shows `online`, `login failed` (check username/password),
`connection error` or `update failed`.
