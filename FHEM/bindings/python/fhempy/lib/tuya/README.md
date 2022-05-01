
# Tuya
This module supports local Tuya device control via their local key. The devices need to be added to the Tuya cloud via SmartLife to be able to extract the local key.

## Installation
First of all it is required to get the local key of your devices. Please follow the steps below:
 1. Connect a device with your SmartLife app and copy the Virtual ID of one device (doesn't matter which) to a text editor
 2. Create a developer account here: https://auth.tuya.com/register
 3. Login with your account here: https://auth.tuya.com/
 4. Create a new project here (name, etc. doesn't matter): https://iot.tuya.com/cloud/ (upper right corner)
 5. Copy API key and API secret to a text editor, we are going to need in within FHEM
 6. Go to "Devices"
 7. Select "Link Tuya App Account"
 8. "Add App Account"
 9. Open SmartLife app, select profile and scan QR code (upper right corner) with the app
 10. Click on "Service API" within your project
 11. Click "Go To Authorize" and add the following APIs
  - IoT Core
  - Authorization
  - Device Status Notification


## Usage
Note: If you know your local keys already, just move over to individual device setup.
### Automatic Setup
```
define tuya_system fhempy tuya setup API_KEY API_SECRET DEVICE_ID
set tuya_system start_scan
```
The scan might take some minutes to finish, please wait and take a coffee.
 - API_KEY: From tuya developer portal
 - API_SECRET: From tuya developer portal
 - DEVICE_ID: From SmartLife app, doesn't matter which device, we just need one to retrieve the proper uid from it

### Individual Device
If a device couldn't be setup properly or you know your local keys and don't need setup, you can define it on your own
```
define wifi_plug fhempy tuya PRODUCT_ID DEVICE_ID IP LOCAL_KEY [VERSION] [API_KEY] [API_SECRET]
```
 - PRODUCT_ID: Set to "api" if API_KEY and API_SECRET are provided, otherwise use the proper product id
 - DEVICE_ID: Take that one from the tuya_system device you created
 - IP: Check for the IP in your tuya_system device or on your router
 - LOCAL_KEY: Take that one from the tuya_system device you created
 - VERSION: Take that one from the tuya_system device you created (default 3.3)
 - API_KEY: If the product ID couldn't be found in the standard mappings, the possible functions will be retrieved from tuya cloud
 - API_SECRET: If the product ID couldn't be found in the standard mappings, the possible functions will be retrieved from tuya cloud
