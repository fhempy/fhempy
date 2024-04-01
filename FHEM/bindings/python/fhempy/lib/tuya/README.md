
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
define wifi_plug fhempy tuya PRODUCT_ID DEVICE_ID IP [VERSION] [API_KEY] [API_SECRET]
attr wifi_plug localkey LOCALKEY_FROM_TUYA_SYSTEM_READINGS
```
 - PRODUCT_ID: Set to "api" if API_KEY and API_SECRET are provided, otherwise use the proper product id
 - DEVICE_ID: Take that one from the tuya_system device you created
 - IP: Check for the IP in your tuya_system device or on your router
 - VERSION: Take that one from the tuya_system device you created (default 3.3)
 - API_KEY: If the product ID couldn't be found in the standard mappings, the possible functions will be retrieved from tuya cloud
 - API_SECRET: If the product ID couldn't be found in the standard mappings, the possible functions will be retrieved from tuya cloud


## Adding Readings and Functions

The module will automatically create known readings and functions for the device. Unknown data points from the device readings will appear as `dp_xxx` numbers in the readings list. If you want to add these as proper readings, you can do so by extending the `tuya_spec_status` and `tuya_spec_functions` attributes.

`tuya_spec_status` is used to define the readings that should be created for the device. `tuya_spec_functions` is used to define the `set xxx` functions that should be created for the reading.

Additionally, you have to add a reading to the device with the name of the data point and the name of the new reading you created, e.g. `attr DEVICE dp_117 readingName`.

### Values for `tuya_spec_functions` and `tuya_spec_status`

These attributes have to be set as a JSON array. Each entry in the array is a JSON object with the following attributes (`tuya_spec_status` doesn't use the `desc` attribute):

- `dp_id`: The ID of the data point (only the number, e.g. `117`)
- `code`: The name for the reading to be created (e.g. `temperature`)
- `type`: The data type of the reading (Integer, Float, String etc.)
- `desc`: Description of the reading shown in the FHEMWEB interface
- `values`: Description of the possible values for the reading (JSON Object)
  - `values.min`: Minimum value for the reading (on the tuya side)
  - `values.max`: Maximum value for the reading (on the tuya side)
  - `values.unit`: Unit to display for the reading (e.g. °C)
  - `values.scale`: Scaling factor for the reading (1 divides by 10, 2 divides by 100 etc.)
  - `values.step`: Step size for the reading (in the unit of the tuya side!)


### Example

Example for Tuya Water Quality Meter with EC and PH warning / relay function:

#### tuya_spec_functions

This has to be set as an attribute to the device in one line! (no line breaks) For better readability the JSON is formatted and split into multiple lines here.

```
[
  {
    "code": "ec_high",
    "dp_id": 117,
    "type": "Integer",
    "values": {
      "unit": "mS/cm",
      "min": 0,
      "max": 199999,
      "scale": 3,
      "step": 100
    },
    "desc": "set EC high mark"
  },
  {
    "code": "ec_low",
    "dp_id": 118,
    "type": "Integer",
    "values": {
      "unit": "mS/cm",
      "min": 0,
      "max": 199999,
      "scale": 3,
      "step": 100
    },
    "desc": "set EC low mark"
  },
  {
    "code": "ph_high",
    "dp_id": 107,
    "type": "Integer",
    "values": {
      "unit": "PH",
      "min": 0,
      "max": 1500,
      "scale": 2,
      "step": 10
    },
    "desc": "set PH high mark"
  },
  {
    "code": "ph_low",
    "dp_id": 108,
    "type": "Integer",
    "values": {
      "unit": "PH",
      "min": 0,
      "max": 1500,
      "scale": 2,
      "step": 10
    },
    "desc": "set PH low mark"
  },
  {
    "code": "temp_high",
    "dp_id": 102,
    "type": "Integer",
    "values": {
      "unit": "°C",
      "min": -100,
      "max": 1100,
      "scale": 1,
      "step": 1
    },
    "desc": "set temperature high mark"
  },
  {
    "code": "temp_low",
    "dp_id": 103,
    "type": "Integer",
    "values": {
      "unit": "°C",
      "min": -100,
      "max": 1100,
      "scale": 1,
      "step": 1
    },
    "desc": "set temperature low mark"
  }
]
```

the same as above in one line:

```
attr DEVICE tuya_spec_functions [{"code":"ec_high","dp_id":117,"type":"Integer","values":{"unit":"mS/cm","min":0,"max":199999,"scale":3,"step":100},"desc":"set EC high mark"},{"code":"ec_low","dp_id":118,"type":"Integer","values":{"unit":"mS/cm","min":0,"max":199999,"scale":3,"step":100},"desc":"set EC low mark"},{"code":"ph_high","dp_id":107,"type":"Integer","values":{"unit":"PH","min":0,"max":1500,"scale":2,"step":10},"desc":"set PH high mark"},{"code":"ph_low","dp_id":108,"type":"Integer","values":{"unit":"PH","min":0,"max":1500,"scale":2,"step":10},"desc":"set PH low mark"},{"code":"temp_high","dp_id":102,"type":"Integer","values":{"unit":"°C","min":-100,"max":1100,"scale":1,"step":1},"desc":"set temperature high mark"},{"code":"temp_low","dp_id":103,"type":"Integer","values":{"unit":"°C","min":-100,"max":1100,"scale":1,"step":1},"desc":"set temperature low mark"}]
```

#### tuya_spec_status

This has to be set as an attribute to the device in one line! (no line breaks) For better readability the JSON is formatted and split into multiple lines here.

```
[
  {
    "code": "ec_high",
    "dp_id": 117,
    "type": "Integer",
    "values": {
      "unit": "mS/cm",
      "min": 0,
      "max": 199999,
      "scale": 3,
      "step": 100
    }
  },
  {
    "code": "ec_low",
    "dp_id": 118,
    "type": "Integer",
    "values": {
      "unit": "mS/cm",
      "min": 0,
      "max": 199999,
      "scale": 3,
      "step": 100
    }
  },
  {
    "code": "ph_high",
    "dp_id": 107,
    "type": "Integer",
    "values": {
      "unit": "PH",
      "min": 0,
      "max": 1500,
      "scale": 2,
      "step": 10
    }
  },
  {
    "code": "ph_low",
    "dp_id": 108,
    "type": "Integer",
    "values": {
      "unit": "PH",
      "min": 0,
      "max": 1500,
      "scale": 2,
      "step": 10
    }
  },
  {
    "code": "temperature",
    "dp_id": 8,
    "type": "Integer",
    "values": {
      "unit": "℃",
      "min": -100,
      "max": 1100,
      "scale": 1,
      "step": 1
    }
  },
  {
    "code": "ec",
    "dp_id": 116,
    "type": "Integer",
    "values": {
      "unit": "mS/cm",
      "min": 0,
      "max": 199999,
      "scale": 3,
      "step": 100
    }
  },
  {
    "code": "ph",
    "dp_id": 106,
    "type": "Integer",
    "values": {
      "unit": "",
      "min": 0,
      "max": 1500,
      "scale": 2,
      "step": 10
    }
  },
  {
    "code": "temp_high",
    "dp_id": 102,
    "type": "Integer",
    "values": {
      "unit": "℃",
      "min": -100,
      "max": 1100,
      "scale": 1,
      "step": 1
    }
  },
  {
    "code": "temp_low",
    "dp_id": 103,
    "type": "Integer",
    "values": {
      "unit": "℃",
      "min": -100,
      "max": 1100,
      "scale": 1,
      "step": 1
    }
  }
]
```

the same as above in one line:

```
attr DEVICE tuya_spec_status [{"code":"ec_high","dp_id":117,"type":"Integer","values":{"unit":"mS/cm","min":0,"max":199999,"scale":3,"step":100}},{"code":"ec_low","dp_id":118,"type":"Integer","values":{"unit":"mS/cm","min":0,"max":199999,"scale":3,"step":100}},{"code":"ph_high","dp_id":107,"type":"Integer","values":{"unit":"PH","min":0,"max":1500,"scale":2,"step":10}},{"code":"ph_low","dp_id":108,"type":"Integer","values":{"unit":"PH","min":0,"max":1500,"scale":2,"step":10}},{"code":"temperature","dp_id":8,"type":"Integer","values":{"unit":"℃","min":-100,"max":1100,"scale":1,"step":1}},{"code":"ec","dp_id":116,"type":"Integer","values":{"unit":"mS/cm","min":0,"max":199999,"scale":3,"step":100}},{"code":"ph","dp_id":106,"type":"Integer","values":{"unit":"","min":0,"max":1500,"scale":2,"step":10}},{"code":"temp_high","dp_id":102,"type":"Integer","values":{"unit":"℃","min":-100,"max":1100,"scale":1,"step":1}},{"code":"temp_low","dp_id":103,"type":"Integer","values":{"unit":"℃","min":-100,"max":1100,"scale":1,"step":1}}]
```

#### Attributes to add to the device

These attributes tell the module to create the readings and functions for the device. The `dp_xxx` readings will not be updated anymore, but the new readings will be updated with the data from the device.

```
attr DEVICE dp_08 temperature
attr DEVICE dp_102 temp_high
attr DEVICE dp_103 temp_low
attr DEVICE dp_106 ph
attr DEVICE dp_107 ph_high
attr DEVICE dp_108 ph_low
attr DEVICE dp_116 ec
attr DEVICE dp_117 ec_high
attr DEVICE dp_118 ec_low
```
