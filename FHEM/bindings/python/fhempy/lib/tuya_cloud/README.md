
# Tuya Cloud
This module uses the official tuya library to communicate with all sort of tuya devices supported by the Tuya Cloud API.

## Installation
You need to setup a Tuya IoT project on the tuya development platform.

Please follow the instructions here:

https://github.com/tuya/tuya-home-assistant/wiki/Tuya-IoT-Platform-Configuration-Guide-Using-Smart-Home-PaaS


## Usage
Please read installation instructions before! You need the tuya account and a smart home project on the tuya platform to get api key and api secret.

```
define tuya_cloud_connector PythonModule tuya_cloud setup <API_KEY> <API_SECRET> <USERNAME> <PASSWORD> [<APPTYPE>] [<REGION>]
```
This command will create the tuya cloud connector device which automatically create all tuya devices in your FHEM installation.
 - API_KEY: From tuya developer portal
 - API_SECRET: From tuya developer portal
 - USERNAME: From SmartLife app
 - PASSWORD: From SmartLife app
 - APPTYPE: smartlife (default) or tuyaSmart, depending on the app you use
 - REGION: Europe (default), China, America, India, EasternAmerica, WesternEurope
