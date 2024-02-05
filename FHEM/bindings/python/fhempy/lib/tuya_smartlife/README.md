
# Tuya SmartLife
This module uses the official tuya library to communicate with all sort of tuya devices supported by SmartLife app.

## Installation
 1. Setup all your devices within the SmartLife app.
 2. Get the usercode from your SmartLife app account settings page.
 3. Define the tuya_smartlife_integration device in FHEM.
 4. Scan the QR code with the SmartLife app to link your account.
 5. set tuya_smartlife_integration scan_done within FHEM to finish the login process.


## Usage
```
define tuya_smartlife_integration fhempy tuya_smartlife setup USERCODE
```

 - USERCODE: From the SmartLife app account settings page
