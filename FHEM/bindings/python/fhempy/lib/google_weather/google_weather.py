# comment to allow FHEM update
# Google search only returns weather data to browsers running JavaScript,
# therefore the data is retrieved from Open-Meteo (https://open-meteo.com).
import asyncio
import re
from datetime import datetime

import aiohttp

from .. import fhem, generic

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
# Nominatim (OpenStreetMap) also finds addresses, Open-Meteo only place names.
# Nominatim usage policy: identifying user agent, max 1 request per second.
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {"User-Agent": "fhempy-google_weather (github.com/fhempy/fhempy)"}
PLACE_KEYS = ["city", "town", "village", "municipality", "suburb", "county", "state"]
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ICON_URL = "https://ssl.gstatic.com/onebox/weather/64/{}.png"
COORDINATES = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")
NEXT_HOURS = 25
FORECAST_DAYS = 8

# WMO weather code: (english, german, icon)
WEATHER_CODES = {
    0: ("Clear sky", "Klar", "sunny"),
    1: ("Mainly clear", "Überwiegend klar", "sunny_s_cloudy"),
    2: ("Partly cloudy", "Teilweise bewölkt", "partly_cloudy"),
    3: ("Overcast", "Bedeckt", "cloudy"),
    45: ("Fog", "Nebel", "fog"),
    48: ("Rime fog", "Reifnebel", "fog"),
    51: ("Light drizzle", "Leichter Nieselregen", "rain_light"),
    53: ("Drizzle", "Nieselregen", "rain_light"),
    55: ("Dense drizzle", "Starker Nieselregen", "rain_light"),
    56: ("Freezing drizzle", "Gefrierender Nieselregen", "sleet"),
    57: ("Freezing drizzle", "Gefrierender Nieselregen", "sleet"),
    61: ("Light rain", "Leichter Regen", "rain_light"),
    63: ("Rain", "Regen", "rain"),
    65: ("Heavy rain", "Starker Regen", "rain_heavy"),
    66: ("Freezing rain", "Gefrierender Regen", "sleet"),
    67: ("Freezing rain", "Gefrierender Regen", "sleet"),
    71: ("Light snow", "Leichter Schneefall", "snow_light"),
    73: ("Snow", "Schneefall", "snow"),
    75: ("Heavy snow", "Starker Schneefall", "snow_heavy"),
    77: ("Snow grains", "Schneegriesel", "snow_light"),
    80: ("Light showers", "Leichte Regenschauer", "rain_s_cloudy"),
    81: ("Showers", "Regenschauer", "rain_s_cloudy"),
    82: ("Heavy showers", "Starke Regenschauer", "rain_heavy"),
    85: ("Snow showers", "Schneeschauer", "snow_s_cloudy"),
    86: ("Heavy snow showers", "Starke Schneeschauer", "snow_heavy"),
    95: ("Thunderstorm", "Gewitter", "thunderstorms"),
    96: ("Thunderstorm with hail", "Gewitter mit Hagel", "thunderstorms"),
    99: ("Thunderstorm with hail", "Gewitter mit Hagel", "thunderstorms"),
}

DAY_NAMES = {
    "en": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    "de": [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    ],
}


class google_weather(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._location = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)

        attr_config = {
            "interval": {
                "default": 61,
                "format": "int",
                "help": "Change interval in minutes, default is 61.",
            },
            "language": {
                "default": "en",
                "options": "en,de",
                "help": "Language of weather conditions and day names, default en.",
            },
        }
        await self.set_attr_config(attr_config)

        if len(args) != 4:
            return "Usage: define my_weather fhempy google_weather CITY"

        self.city = args[3]
        self._location = None

        self.create_async_task(self.update_loop())

    async def update_loop(self):
        while True:
            try:
                async with aiohttp.ClientSession(
                    trust_env=True, timeout=aiohttp.ClientTimeout(total=30)
                ) as session:
                    await self.update(session)
            except asyncio.CancelledError:
                raise
            except Exception as ex:
                self.logger.exception("Failed to update")
                await fhem.readingsSingleUpdate(
                    self.hash, "state", f"failed: {type(ex).__name__}", 1
                )
            await asyncio.sleep(self._attr_interval * 60)

    def _lang(self):
        return "de" if self._attr_language == "de" else "en"

    async def _get_json(self, session, url, params, headers=None):
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise WeatherError(f"HTTP error {resp.status}: {await resp.text()}")
            return await resp.json()

    async def resolve_location(self, session):
        lang = self._lang()
        if self._location is not None and self._location["language"] == lang:
            return self._location

        match = COORDINATES.match(self.city)
        if match:
            self._location = {
                "latitude": float(match.group(1)),
                "longitude": float(match.group(2)),
                "name": self.city,
                "language": lang,
            }
            return self._location

        try:
            location = await self._search_nominatim(session, lang)
        except Exception:
            self.logger.exception("Nominatim search failed, using Open-Meteo")
            location = None
        if location is None:
            location = await self._search_open_meteo(session, lang)
        if location is None:
            raise WeatherError(f"location {self.city} not found")
        location["language"] = lang
        self._location = location
        return self._location

    async def _search_nominatim(self, session, lang):
        data = await self._get_json(
            session,
            NOMINATIM_URL,
            {
                "q": self.city,
                "format": "jsonv2",
                "limit": 1,
                "addressdetails": 1,
                "accept-language": lang,
            },
            headers=NOMINATIM_HEADERS,
        )
        if not data:
            return None
        res = data[0]
        address = res.get("address", {})
        place = next((address[key] for key in PLACE_KEYS if key in address), None)
        name = ", ".join(part for part in [place, address.get("country")] if part)
        return {
            "latitude": float(res["lat"]),
            "longitude": float(res["lon"]),
            "name": name or res.get("display_name", self.city),
        }

    async def _search_open_meteo(self, session, lang):
        data = await self._get_json(
            session,
            GEOCODING_URL,
            {"name": self.city, "count": 1, "language": lang, "format": "json"},
        )
        results = data.get("results") or []
        if len(results) == 0:
            return None
        res = results[0]
        name = ", ".join(part for part in [res.get("name"), res.get("country")] if part)
        return {
            "latitude": res["latitude"],
            "longitude": res["longitude"],
            "name": name,
        }

    async def update(self, session):
        try:
            location = await self.resolve_location(session)
        except WeatherError as ex:
            self.logger.error(f"Failed to resolve location: {ex}")
            await fhem.readingsSingleUpdate(self.hash, "state", f"failed: {ex}", 1)
            return

        data = await self._get_json(
            session,
            FORECAST_URL,
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
                ),
                "hourly": (
                    "temperature_2m,relative_humidity_2m,precipitation_probability,"
                    "weather_code,wind_speed_10m"
                ),
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "wind_speed_unit": "kmh",
                "timezone": "auto",
                "forecast_days": FORECAST_DAYS,
            },
        )
        await self.update_readings(location, data)

    def _condition(self, code):
        lang_idx = 1 if self._lang() == "de" else 0
        entry = WEATHER_CODES.get(code)
        if entry is None:
            return "-", "-"
        return entry[lang_idx], f'<img src="{ICON_URL.format(entry[2])}"/>'

    def _day_name(self, timestamp):
        return DAY_NAMES[self._lang()][datetime.fromisoformat(timestamp).weekday()]

    @staticmethod
    def _num(value):
        if value is None:
            return "-"
        return str(round(value))

    async def update_readings(self, location, data):
        current = data["current"]
        hourly = data["hourly"]
        daily = data["daily"]

        # first hourly entry of the current hour
        current_hour = current["time"][:13]
        start = 0
        for idx, hour_time in enumerate(hourly["time"]):
            if hour_time[:13] >= current_hour:
                start = idx
                break

        cur_condition, cur_condition_img = self._condition(current["weather_code"])
        cur_temp = self._num(current["temperature_2m"])
        cur_windspeed = self._num(current["wind_speed_10m"])
        cur_precipitation = self._num(hourly["precipitation_probability"][start])

        await fhem.readingsBeginUpdate(self.hash)
        try:
            await self._bulk("cur_temperature", cur_temp)
            await self._bulk("cur_humidity", self._num(current["relative_humidity_2m"]))
            await self._bulk("cur_precipitation", cur_precipitation)
            await self._bulk("cur_weather", cur_condition)
            await self._bulk("cur_weather_img", f"<html>{cur_condition_img}</html>")
            await self._bulk("cur_windspeed_with_unit", f"{cur_windspeed} km/h")
            await self._bulk("cur_windspeed", cur_windspeed)

            for i, day in enumerate(daily["time"]):
                condition, img = self._condition(daily["weather_code"][i])
                await self._bulk(f"next_days_{i}_name", self._day_name(day))
                await self._bulk(f"next_days_{i}_weather", condition)
                await self._bulk(f"next_days_{i}_weather_img", f"<html>{img}</html>")
                await self._bulk(
                    f"next_days_{i}_max_temp", self._num(daily["temperature_2m_max"][i])
                )
                await self._bulk(
                    f"next_days_{i}_min_temp", self._num(daily["temperature_2m_min"][i])
                )

            for i, idx in enumerate(
                range(start, min(start + NEXT_HOURS, len(hourly["time"])))
            ):
                hour_time = hourly["time"][idx]
                condition, img = self._condition(hourly["weather_code"][idx])
                prefix = f"next_hours_{i:02d}"
                await self._bulk(f"{prefix}_condition", condition)
                await self._bulk(
                    f"{prefix}_time", f"{self._day_name(hour_time)} {hour_time[11:16]}"
                )
                await self._bulk(
                    f"{prefix}_humidity",
                    self._num(hourly["relative_humidity_2m"][idx]),
                )
                await self._bulk(f"{prefix}_img", f"<html>{img}</html>")
                await self._bulk(
                    f"{prefix}_precipitation",
                    self._num(hourly["precipitation_probability"][idx]),
                )
                await self._bulk(
                    f"{prefix}_temperature", self._num(hourly["temperature_2m"][idx])
                )
                await self._bulk(
                    f"{prefix}_windspeed", self._num(hourly["wind_speed_10m"][idx])
                )

            await self._bulk("location", location["name"])
            await self._bulk(
                "last_update",
                f"{self._day_name(current['time'])} {current['time'][11:16]}",
            )
            await self._bulk(
                "state",
                (
                    f"<html>{cur_condition_img}<br>{cur_temp}°C / "
                    f"{cur_precipitation}% / {cur_windspeed} km/h</html>"
                ),
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    async def _bulk(self, reading, value):
        await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)


class WeatherError(Exception):
    pass
