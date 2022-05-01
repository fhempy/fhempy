
# Tuya Cloud
This module uses the official tuya library to communicate with all sort of tuya devices supported by the Tuya Cloud API.

## Installation
You need to setup a Tuya IoT project on the tuya development platform. It also requires you to create a Tuya Developer account which is used in the first step of the instructions. That's not the SmartLife or TuyaApp account!

Please follow the instructions here:

https://github.com/tuya/tuya-home-assistant/wiki/Tuya-IoT-Platform-Configuration-Guide


## Usage
Please read installation instructions before! You need the tuya developer account and a smart home project on the tuya platform to get client id and client secret.

```
define tuya_cloud_connector fhempy tuya_cloud setup <CLIENT_ID> <CLIENT_SECRET> <USERNAME> <PASSWORD> [<APPTYPE>] [<REGION>]
```

This command will create the tuya cloud connector device which automatically create all tuya devices in your FHEM installation.

 - CLIENT_ID: From tuya developer portal
 - CLIENT_SECRET: From tuya developer portal
 - USERNAME: From SmartLife/Tuya app (not developer account)
 - PASSWORD: From SmartLife/Tuya app (not developer account)
 - APPTYPE: smartlife (default) or tuyaSmart, depending on the app you use
 - REGION: Europe (default), China, America, India, EasternAmerica, WesternEurope
