
# Volvo
This module connects to your Volvo account and retrieves data from your car. It can also be used to activate climate control, lock/unlock, etc..

Thanks to iobroker colleagues! Their code helped me to understand the volvo logic:
https://github.com/TA2k/ioBroker.volvo

## Setup

 - Register/Login into https://developer.volvocars.com/account/

 - You need a Google or Github Account this is not related to you APP Credentials

 - Create an Application

 - Copy VCC API Key Primary

## Usage
```
define my_volvo fhempy volvo VCCAPIKEY VOLVO_USERNAME VOLVO_PASSWORD
```

VCCAPIKEY: From developer portal
VOLVO_USERNAME: Your app username (=email address)
VOLVO_PASSWORD: Your app password
