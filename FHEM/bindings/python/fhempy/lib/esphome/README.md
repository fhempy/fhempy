
# ESPHome
This module installs and starts the ESPHome Device Builder (the ESPHome dashboard) to configure and update ESPHome devices via dashboard.

## Usage
```
define esp_home fhempy esphome
```
## MQTT
If ESPHome devices use `mqtt:`, the Device Builder connects to their broker for device discovery. fhempy starts it with the fixed MQTT client id `esphome-dashboard-fhempy-<NAME>`, so FHEM's MQTT2_SERVER autocreates only one MQTT2_DEVICE for it instead of a new one on every start.

## Logging
The output of the Device Builder (compile and upload logs too) goes to `FHEM-ROOT-DIRECTORY/.fhempy/log/<NAME>.log` (rotated at 5 MB), not to the fhempy log. If it crashes, the last lines are written to the fhempy log.
