
# google_weather
Renamed to [openmeteo_weather](../openmeteo_weather/README.md). Google only shows weather data
to browsers with JavaScript, therefore the data now comes from Open-Meteo.

Existing `google_weather` devices keep working with the same readings. For new devices use:
```
define my_weather fhempy openmeteo_weather LOCATION
```
