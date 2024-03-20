
# Zappi
This module connects to your Volvo account and retrieves data from your car. It can also be used to activate climate control, lock/unlock, etc..

Thanks to ...

## Setup

 - Register/Login into https://myaccount.myenergi.com

 - Go to Location => myenergi Products

 - Create an api key for your zappi device via the "advanced..." button 

 - Copy the SN (serial number) for your Zappi wallbox

 - optional copy the SNs for the installed harvis

## Usage
```
define myZappiBox fhempy zappi serialnumber API_Key [harvi1] [harvi2] ... [harviN] 
```

SERIALNO: serial number of the zappi wallbox
APIKEY: apikey for the zappi wallbox from the myEnergi portal
[hari1] ... [harviN] are optional harvi serials

