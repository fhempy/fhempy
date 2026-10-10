
# google_weather
This module retrieves the current weather and the forecast for the next hours and days.

Google only shows weather data to browsers with JavaScript, therefore the data comes from
[Open-Meteo](https://open-meteo.com) (free, no API key needed). The module name and the
readings stay the same as before.

# Usage
```
define my_weather fhempy google_weather LOCATION
```

LOCATION=Name of the location (e.g. Berlin), an address (e.g. "Unter den Linden 1, Berlin") or coordinates as `LATITUDE,LONGITUDE`
(e.g. `52.52,13.41`). Locations with spaces in the name must be quoted. Use coordinates if
the name matches the wrong place.

Names and addresses are looked up once via [Nominatim](https://nominatim.openstreetmap.org)
(OpenStreetMap), with the Open-Meteo geocoding API as fallback.

Examples
```
define my_weather fhempy google_weather Berlin
define my_weather fhempy google_weather "New York"
define my_weather fhempy google_weather "Stephansplatz 1, Wien"
define my_weather fhempy google_weather 48.21,16.37
```

# Attributes
- `interval`: update interval in minutes, default 61
- `language`: `en` (default) or `de` for weather conditions, day names and location name
