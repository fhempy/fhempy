import logging

import pytest
from tests.utils import mock_fhem

from fhempy.lib.pkg_installer import check_and_install_dependencies

FORECAST = {
    "current": {
        "time": "2026-10-10T08:15",
        "temperature_2m": 12.4,
        "relative_humidity_2m": 81,
        "weather_code": 3,
        "wind_speed_10m": 9.6,
    },
    "hourly": {
        "time": [f"2026-10-10T{h:02d}:00" for h in range(24)]
        + [f"2026-10-11T{h:02d}:00" for h in range(24)],
        "temperature_2m": [10.0 + h / 10 for h in range(48)],
        "relative_humidity_2m": [80] * 48,
        "precipitation_probability": [h for h in range(48)],
        "weather_code": [61] * 48,
        "wind_speed_10m": [5.2] * 48,
    },
    "daily": {
        "time": ["2026-10-10", "2026-10-11"],
        "weather_code": [3, 95],
        "temperature_2m_max": [15.6, 18.2],
        "temperature_2m_min": [7.4, 9.0],
    },
}

GEOCODING = {
    "results": [
        {
            "name": "Berlin",
            "country": "Deutschland",
            "latitude": 52.52,
            "longitude": 13.41,
        }
    ]
}


async def define_device(mocker, city="Berlin"):
    mock_fhem.mock_module(mocker)
    await check_and_install_dependencies("openmeteo_weather")
    from fhempy.lib.openmeteo_weather.openmeteo_weather import openmeteo_weather

    mock_fhem.readings.pop("testweather", None)
    testhash = {"NAME": "testweather", "FHEMPYTYPE": "openmeteo_weather"}
    device = openmeteo_weather(logging.getLogger(__name__))
    mocker.patch.object(device, "create_async_task", lambda coro: coro.close())
    await device.Define(
        testhash, ["testweather", "fhempy", "openmeteo_weather", city], {}
    )
    return device


NOMINATIM = [
    {
        "lat": "48.2085",
        "lon": "16.3721",
        "display_name": "1, Stephansplatz, Innere Stadt, Wien, 1010, Österreich",
        "address": {"road": "Stephansplatz", "city": "Wien", "country": "Österreich"},
    }
]


def mock_api(mocker, device, geocoding=GEOCODING, nominatim=None):
    from fhempy.lib.openmeteo_weather import openmeteo_weather as gw

    calls = []

    async def get_json(session, url, params, headers=None):
        calls.append((url, params))
        if url == gw.NOMINATIM_URL:
            if isinstance(nominatim, Exception):
                raise nominatim
            return nominatim if nominatim is not None else []
        if url == gw.GEOCODING_URL:
            return geocoding
        return FORECAST

    mocker.patch.object(device, "_get_json", get_json)
    return calls


@pytest.mark.asyncio
async def test_update_sets_readings(mocker):
    device = await define_device(mocker)
    calls = mock_api(mocker, device)

    await device.update(None)

    readings = mock_fhem.readings["testweather"]
    assert readings["cur_temperature"] == "12"
    assert readings["cur_humidity"] == "81"
    assert readings["cur_precipitation"] == "8"
    assert readings["cur_weather"] == "Overcast"
    assert "cloudy.png" in readings["cur_weather_img"]
    assert readings["cur_windspeed"] == "10"
    assert readings["cur_windspeed_with_unit"] == "10 km/h"
    assert readings["next_days_0_name"] == "Saturday"
    assert readings["next_days_1_weather"] == "Thunderstorm"
    assert readings["next_days_1_max_temp"] == "18"
    assert readings["next_days_1_min_temp"] == "9"
    assert readings["next_hours_00_time"] == "Saturday 08:00"
    assert readings["next_hours_00_precipitation"] == "8"
    assert readings["next_hours_24_time"] == "Sunday 08:00"
    assert "next_hours_25_time" not in readings
    assert readings["location"] == "Berlin, Deutschland"
    assert readings["state"].startswith("<html><img")
    assert calls[2][1]["latitude"] == 52.52

    # location is resolved only once
    await device.update(None)
    assert len(calls) == 4


@pytest.mark.asyncio
async def test_address_via_nominatim(mocker):
    device = await define_device(mocker, "Stephansplatz 1, Wien")
    calls = mock_api(mocker, device, nominatim=NOMINATIM)

    await device.update(None)

    from fhempy.lib.openmeteo_weather import openmeteo_weather as gw

    assert [c[0] for c in calls] == [gw.NOMINATIM_URL, gw.FORECAST_URL]
    assert calls[0][1]["q"] == "Stephansplatz 1, Wien"
    assert calls[1][1]["latitude"] == 48.2085
    assert mock_fhem.readings["testweather"]["location"] == "Wien, Österreich"


@pytest.mark.asyncio
async def test_nominatim_error_falls_back_to_open_meteo(mocker):
    device = await define_device(mocker)
    mock_api(mocker, device, nominatim=RuntimeError("HTTP error 429"))

    await device.update(None)

    assert mock_fhem.readings["testweather"]["location"] == "Berlin, Deutschland"


@pytest.mark.asyncio
async def test_coordinates_and_german(mocker):
    device = await define_device(mocker, "48.21,16.37")
    device._attr_language = "de"
    calls = mock_api(mocker, device)

    await device.update(None)

    readings = mock_fhem.readings["testweather"]
    assert len(calls) == 1
    assert calls[0][1]["latitude"] == 48.21
    assert readings["cur_weather"] == "Bedeckt"
    assert readings["next_days_0_name"] == "Samstag"


@pytest.mark.asyncio
async def test_unknown_location(mocker):
    device = await define_device(mocker, "Nowhereville")
    mock_api(mocker, device, geocoding={})

    await device.update(None)

    assert "not found" in mock_fhem.readings["testweather"]["state"]


@pytest.mark.asyncio
async def test_google_weather_alias(mocker):
    mock_fhem.mock_module(mocker)
    from fhempy.lib.google_weather.google_weather import google_weather
    from fhempy.lib.openmeteo_weather.openmeteo_weather import openmeteo_weather

    assert issubclass(google_weather, openmeteo_weather)
