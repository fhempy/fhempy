
# Tuya
This module supports local Tuya device control via their local key. The devices need to be added to the Tuya cloud via SmartLife to be able to extract the local key.

## Installation
First of all it is required to get the local key of your devices. Please follow the steps below:
 1. Connect a device with your SmartLife app and copy the Virtual ID of one device (doesn't matter which) to a text editor
 2. Create a developer account here: https://auth.tuya.com/register
 3. Login with your account here: https://auth.tuya.com/
 4. Create a new project here (name, etc. doesn't matter): https://iot.tuya.com/cloud/ (upper right corner)
 5. Copy Client ID and Client Secret to a text editor, we are going to need in within FHEM
 6. Click link device within your project
 7. Select "Link devices by App Account"
 8. "Add App Account"
 9. Open SmartLife app, select profile and scan QR code (upper right corner) with the app
 10. Open "API Groups" on the tuya portal
 11. Click "Apply" for
  - Authorization management
  - Device management
  - Device Control


## Usage
```
define wifi_plug PythonModule tuya setup CLIENT_ID CLIENT_SECRET DEVICE_ID
```
 - CLIENT_ID: From tuya developer portal
 - CLIENT_SECRET: From tuya developer portal
 - DEVICE_ID: From SmartLife app, doesn't matter which device, we just need one to retrieve the proper uid from it
