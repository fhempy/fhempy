
# MQTT HomeAssistant Discovery
This module automatically detects new MQTT devices and creates a proper MQTT2_DEVICE out of it, including all readings and commands.

Functionality:
 - mqtt_ha_discovery connects to the MQTT broker
 - it subscribes for all HomeAssistant topics
 - if it receives a HomeAssistant configuration, it checks if a device with the name in readingList attribute exists
 - if the device wasn't found within FHEM, it will be created automatically
 - after that it updates the readingList and setList based on the HomeAssistant discovery topics if the topic wasn't configured yet

# Usage
```
define mqttha fhempy mqtt_ha_discovery [IP] [PORT]
```

 - IP: Default 127.0.0.1 of the MQTT broker.
 - PORT: Default 1883 of the MQTT broker.

Devices are automatically detected on reboot. You can also activate respectRetain in MQTT2_SERVER to enable detection of devices without reboot.

# Currently supported types
 - switch
 - light (brightness)
 - sensor

# Supported platforms
 - ESPhome
 - Zigbee2MQTT
 - a lot of others who support MQTT HomeAssistant discovery
