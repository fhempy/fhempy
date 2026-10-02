
# Zappi
This module privides the data from a Zappi charger wallbox. Optional it shows the measurements from connected harvi boxes. It can also be used to start/stop the charging, select charging mnode and set greenlevel for ECO+ mode,

Special thanks to CJNE for proving the myenergi API

## Setup

 - Register/Login into https://myaccount.myenergi.com

 - Go to Location => myenergi Products

 - Create an api key for your zappi device via the "advanced..." button 

 - Copy the SN (serial number) of the hub the API key was created for. For a Zappi v2 this is the serial of the Zappi wallbox itself, for a Zappi v1 with external hub it is the serial of the hub. The Zappi connected to the hub is detected automatically.

 - optional copy the SNs for the installed harvis

## Usage
```
define myZappiBox fhempy zappi serialnumber API_Key [harvi1] [harvi2] ... [harviN] 
```

SERIALNO: serial number of the hub (Zappi v2: serial of the zappi wallbox, Zappi v1: serial of the external hub)
APIKEY: apikey for this hub from the myEnergi portal
[hari1] ... [harviN] are optional harvi serials

