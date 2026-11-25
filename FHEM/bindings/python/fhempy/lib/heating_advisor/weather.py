"""Sun position, sun on the facades and the weather from Open-Meteo
(history and forecast, no account needed)."""

import datetime
import json
import math
import urllib.parse

from .. import utils

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY = "temperature_2m,shortwave_radiation,direct_radiation,diffuse_radiation"
# Open-Meteo keeps up to 92 past days in the forecast API
MAX_PAST_DAYS = 92
FACADES = (90.0, 180.0, 270.0)  # east, south, west


def sun_position(ts, lat, lon):
    """(elevation, azimuth) in degrees, azimuth 0 = north, 90 = east"""
    dt = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    day = dt.timetuple().tm_yday
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    gamma = 2 * math.pi / 365 * (day - 1 + (hour - 12) / 24)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )
    minutes = hour * 60 + eqtime + 4 * lon
    ha = math.radians(minutes / 4 - 180)
    phi = math.radians(lat)
    cos_zen = math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(
        decl
    ) * math.cos(ha)
    cos_zen = min(max(cos_zen, -1.0), 1.0)
    zen = math.acos(cos_zen)
    elevation = 90 - math.degrees(zen)
    sin_zen = math.sin(zen)
    if sin_zen < 1e-6:
        return elevation, 180.0
    cos_az = (math.sin(decl) - math.sin(phi) * cos_zen) / (math.cos(phi) * sin_zen)
    az = math.degrees(math.acos(min(max(cos_az, -1.0), 1.0)))
    if ha > 0:
        az = 360 - az
    return elevation, az


def facade_sun(direct, diffuse, elevation, azimuth):
    """sun (W/m²) on vertical east, south and west facades from the direct
    and diffuse radiation on a horizontal surface"""
    diffuse = max(diffuse or 0.0, 0.0)
    if elevation <= 1.0:
        return (diffuse / 2,) * 3
    sin_el = math.sin(math.radians(elevation))
    beam = min(max(direct or 0.0, 0.0) / max(sin_el, 0.1), 1100.0)
    cos_el = math.cos(math.radians(elevation))
    return tuple(
        beam * cos_el * max(0.0, math.cos(math.radians(azimuth - facade))) + diffuse / 2
        for facade in FACADES
    )


def sun_at(ts, lat, lon, direct, diffuse):
    elevation, azimuth = sun_position(ts, lat, lon)
    return facade_sun(direct, diffuse, elevation, azimuth)


def clear_sky(ts, lat, lon):
    """rough (direct, diffuse) on a horizontal surface without clouds"""
    elevation, _ = sun_position(ts, lat, lon)
    if elevation <= 0:
        return 0.0, 0.0
    sin_el = math.sin(math.radians(elevation))
    dni = 1000 * 0.7 ** (1 / max(sin_el, 0.05)) ** 0.678
    return dni * sin_el, 0.1 * 1000 * sin_el


async def fetch(lat, lon, past_days=2, forecast_days=7):
    """hourly weather: list of (ts start of the hour, temperature, direct,
    diffuse). Radiation values are the mean of the hour before ts, they
    are shifted by half an hour to the middle of that hour."""
    query = urllib.parse.urlencode(
        {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "hourly": HOURLY,
            "past_days": min(max(int(past_days), 0), MAX_PAST_DAYS),
            "forecast_days": forecast_days,
            "timeformat": "unixtime",
            "timezone": "UTC",
        }
    )
    body = await utils.http_get(f"{FORECAST_URL}?{query}", timeout=30)
    return parse(json.loads(body))


def parse(data):
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    temps = hourly.get("temperature_2m") or []
    direct = hourly.get("direct_radiation") or []
    diffuse = hourly.get("diffuse_radiation") or []
    rows = []
    for i, ts in enumerate(times):
        temp = temps[i] if i < len(temps) else None
        if temp is None:
            continue
        rows.append(
            (
                int(ts),
                float(temp),
                float(direct[i] or 0.0) if i < len(direct) else 0.0,
                float(diffuse[i] or 0.0) if i < len(diffuse) else 0.0,
            )
        )
    return rows


class Weather:
    """hourly weather, interpolated to any time"""

    def __init__(self):
        self.hours = {}

    def add(self, rows):
        for ts, temp, direct, diffuse in rows:
            self.hours[ts] = (temp, direct, diffuse)
        # keep at most a year
        if len(self.hours) > 24 * 400:
            for ts in sorted(self.hours)[: len(self.hours) - 24 * 400]:
                del self.hours[ts]

    def last_ts(self):
        return max(self.hours) if self.hours else None

    def at(self, ts):
        """(temperature, direct, diffuse) at ts, None if unknown"""
        base = int(ts // 3600 * 3600)
        a = self.hours.get(base)
        b = self.hours.get(base + 3600)
        if a is None and b is None:
            return None
        if a is None or b is None:
            return a or b
        f = (ts - base) / 3600
        # radiation: mean of the hour before, so b covers base..base+1h
        return (a[0] + (b[0] - a[0]) * f, b[1], b[2])

    def to_json(self):
        return {str(ts): list(v) for ts, v in self.hours.items()}

    def from_json(self, data):
        for ts, values in (data or {}).items():
            try:
                self.hours[int(ts)] = tuple(float(v) for v in values)
            except (TypeError, ValueError):
                continue
