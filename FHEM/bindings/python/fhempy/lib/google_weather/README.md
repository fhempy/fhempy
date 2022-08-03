
# google_weather
This module retrieves weather data from Google.

# Usage
```
define my_weather fhempy google_weather LOCATION
```

LOCATION=Name of the location. E.g. Berlin. Locations with spaces in the name must be quoted.

Examples
```
define my_weather fhempy google_weather Berlin
define my_weather fhempy google_weather "New York"
```