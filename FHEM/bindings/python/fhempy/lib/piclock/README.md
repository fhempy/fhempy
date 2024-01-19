
# piclock
PiClock for MAX7219 displays including current temperature and weather condition.
It also supports buttons to execute commands if GPIO pin gets high.

# Usage
```
define piclock fhempy piclock DEVICE:TEMP_READING DEVICE:WEATHER_READING BUTTONS
```

Example
```
define piclock fhempy piclock gweather:tempearture gweather:condition 4,17,27,22,18
```


Buttons are not yet supported!


Buttons can be used to execute commands. The number is the GPIO number of the Raspberry Pi.
If one of the buttons change state to high, a command in FHEM can be executed.

