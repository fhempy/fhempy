# comment to allow FHEM update
# google_weather was renamed to openmeteo_weather, Google search only returns
# weather data to browsers running JavaScript. Kept for existing devices.
from ..openmeteo_weather.openmeteo_weather import openmeteo_weather


class google_weather(openmeteo_weather):
    pass
