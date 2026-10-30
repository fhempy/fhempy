"""Turns the stored events into a readable story per day: on and off become
one entry with a duration, repeats are bundled, devices switched together are
grouped and everything unusual while nobody is at home is marked.

Pure functions, no FHEM access."""

import collections
import datetime
import functools
import re
import time

from . import classify
from .store import day_of, day_start

# a second "on" within this time continues the previous entry
MERGE_GAP = 15 * 60
# entries of at least GROUP_MIN devices within this time were switched together
GROUP_WINDOW = 2
GROUP_MIN = 3
# a door opened shortly before somebody was detected at home is no alert
ALERT_GRACE = 10 * 60

ACTIVE_VALUES = {
    "on",
    "open",
    "opened",
    "tilted",
    "motion",
    "detected",
    "occupied",
    "unlocked",
    "present",
    "true",
    "alarm",
    "ring",
    "ringing",
    "wet",
    "leak",
    "smoke",
}
INACTIVE_VALUES = {
    "off",
    "closed",
    "nomotion",
    "no_motion",
    "clear",
    "unoccupied",
    "locked",
    "false",
    "dry",
    "noalarm",
    "no_alarm",
}
# end of something, not worth an own entry
SILENT_VALUES = {"nomotion", "no_motion", "clear", "unoccupied", "noalarm", "no_alarm"}
# readings whose name is not part of the text ("Front door open")
NAMELESS_READINGS = {
    "state",
    "contact",
    "motion",
    "presence",
    "occupancy",
    "lock",
    "lockstate",
    "door",
    "window",
}
VALUE_TEXTS = {
    "nomotion": "no motion",
    "no_motion": "no motion",
    "motion": "motion",
    "noalarm": "no alarm",
}
RESIDENTS_TEXTS = {
    "home": "Somebody is at home",
    "absent": "Everybody left",
    "gone": "Everybody is away for a longer time",
    "none": "Nobody lives here",
    "gotosleep": "Going to sleep",
    "asleep": "Everybody is asleep",
    "awoken": "Good morning",
}
ROOMMATE_TEXTS = {
    "home": "is at home",
    "absent": "left",
    "gone": "is away for a longer time",
    "gotosleep": "goes to sleep",
    "asleep": "is asleep",
    "awoken": "woke up",
}
ALWAYS_ALERT_READINGS = ("smoke", "leak", "water", "alarm", "gas", "tamper", "sabotage")


def label(infos, device):
    info = infos.get(device, {})
    return info.get("alias") or device


@functools.lru_cache(maxsize=4096)
def reading_label(reading):
    """readable name of a reading: "target temperature" for desired-temp,
    "boost heating countdown" for boost_heating_countdown"""
    if classify.is_setpoint(reading):
        return "target temperature"
    if classify.is_temperature(reading):
        return "temperature"
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", reading)
    return re.sub(r"[_\-]+", " ", text).strip().lower() or reading


@functools.lru_cache(maxsize=4096)
def unit(reading):
    """unit of a numeric reading if it's obvious from its name"""
    name = reading.lower()
    if classify.is_setpoint(reading) or "temp" in name or "dewpoint" in name:
        return "°C"
    if any(word in name for word in ("humid", "battery", "position", "valve")):
        return "%"
    return ""


def value_text(reading, value):
    """value with unit, CLOSED as closed"""
    text = VALUE_TEXTS.get(value.lower(), value)
    if text.isupper():
        text = text.lower()
    number = classify.number(text)
    if number is not None and unit(reading) and re.fullmatch(r"-?[\d.,]+", text):
        return f"{text} {unit(reading)}"
    return text


def describe(info, reading, value):
    """what happened without the name of the device, e.g. "set to 20 °C"
    or "window closed"; nameless: the name is directly followed by it"""
    text = value_text(reading, value)
    if classify.is_setpoint(reading) and classify.number(value) is not None:
        return "set to " + text, True
    if classify.is_window(reading) and classify.device_category(info) == (
        classify.CLIMATE
    ):
        return "window " + text, False
    if reading in NAMELESS_READINGS:
        return text, True
    return f"{reading_label(reading)} {text}", False


def entry_text(infos, device, reading, value):
    info = infos.get(device, {})
    name = label(infos, device)
    if reading == "state":
        if info.get("TYPE") == classify.RESIDENTS_TYPE and value in RESIDENTS_TEXTS:
            return RESIDENTS_TEXTS[value]
        if info.get("TYPE") in ("ROOMMATE", "GUEST") and value in ROOMMATE_TEXTS:
            return f"{name} {ROOMMATE_TEXTS[value]}"
    text, nameless = describe(info, reading, value)
    return f"{name} {text}" if nameless else f"{name}: {text}"


def short_text(infos, device, reading, value):
    """entry_text without the name of the device, for its own history"""
    text = entry_text(infos, device, reading, value)
    name = label(infos, device)
    if text.startswith(name + ": "):
        text = text[len(name) + 2 :]
    elif text.startswith(name + " "):
        text = text[len(name) + 1 :]
    return text[:1].upper() + text[1:]


def _is_absent(absences, ts, now):
    """nobody at home at ts and for at least ALERT_GRACE afterwards"""
    for start, end in absences:
        if ts < start:
            continue
        if (end if end is not None else now) - ts >= ALERT_GRACE:
            return True
    return False


def _is_alert(entry, infos, absences, now):
    value = entry["value"].lower()
    if value not in ACTIVE_VALUES:
        return False
    reading = entry["reading"].lower()
    if entry["category"] == classify.SECURITY and any(
        word in reading for word in ALWAYS_ALERT_READINGS
    ):
        return True
    if entry["category"] not in (classify.SECURITY, classify.PRESENCE):
        return False
    if infos.get(entry["device"], {}).get("TYPE") in classify.PRESENCE_TYPES:
        return False
    return _is_absent(absences, entry["ts"], now)


def _repeats_state(previous, ts, value):
    """True if the event only repeats what the previous entry already says:
    the same number, on while still on, off while already off"""
    lower = value.lower()
    if lower == previous["value"].lower() and classify.number(value) is not None:
        # the same target temperature again is no decision
        return True
    if previous["value"].lower() not in ACTIVE_VALUES:
        return False
    if previous["end"] is None and lower in ACTIVE_VALUES:
        # still on: devices which repeat their state don't start a new entry
        if previous["value"] != value:
            previous["count"] += 1
        previous["last"] = ts
        return True
    # still off
    return previous["end"] is not None and lower in INACTIVE_VALUES


def _close(previous, ts, value):
    previous["end"] = ts
    previous["end_value"] = value
    previous["last"] = ts


def _continue_entry(previous, ts, value):
    """True if the event only continues the previous entry of its reading:
    on again shortly after off, the matching off or the same value again"""
    if previous is None:
        return False
    if _repeats_state(previous, ts, value):
        return True
    lower = value.lower()
    was_active = previous["value"].lower() in ACTIVE_VALUES
    if ts - previous["last"] > MERGE_GAP:
        # off long after on closes the running entry
        closes = was_active and previous["end"] is None and lower in INACTIVE_VALUES
        if closes:
            _close(previous, ts, value)
        return closes
    if was_active and lower in ACTIVE_VALUES:
        # on again shortly after off
        previous["count"] += 1
        previous["end"] = None
    elif was_active and lower in INACTIVE_VALUES:
        _close(previous, ts, value)
        return True
    elif lower == previous["value"].lower():
        previous["count"] += 1
    else:
        return False
    previous["last"] = ts
    return True


def _finish_entry(entry, infos, absences, now):
    entry["alert"] = _is_alert(entry, infos, absences, now)
    if not entry["duration"]:
        entry["end"] = entry["last"] if entry["count"] > 1 else None
    elif entry["end"] is None and now - entry["last"] > 86400:
        # the "off" got lost
        entry["end"] = entry["last"]
    entry["running"] = entry["duration"] and entry["end"] is None
    del entry["last"]
    del entry["duration"]


def build_entries(rows, infos, absences, now):
    """rows: (ts, device, reading, value, category) sorted by ts"""
    entries = []
    last = {}
    for ts, device, reading, value, category in rows:
        key = (device, reading)
        if _continue_entry(last.get(key), ts, value) or value.lower() in SILENT_VALUES:
            continue
        entry = {
            "ts": ts,
            "end": None,
            "last": ts,
            "count": 1,
            "device": device,
            "reading": reading,
            "value": value,
            "category": category,
            "text": entry_text(infos, device, reading, value),
            "short": short_text(infos, device, reading, value),
            "room": infos.get(device, {}).get("room", ""),
            "duration": value.lower() in ACTIVE_VALUES,
            "on_change": classify.on_change(infos.get(device, {}), reading),
        }
        entries.append(entry)
        last[key] = entry

    for entry in entries:
        _finish_entry(entry, infos, absences, now)
    return group_entries(entries)


GROUP_NOUNS = {
    classify.LIGHT: "lights",
    classify.CLIMATE: "heating devices",
    classify.SECURITY: "doors and locks",
    classify.ENERGY: "outlets",
}


def group_text(group):
    """e.g. "4 lights on" or "6 devices changed at once"."""
    categories = {e["category"] for e in group}
    noun = "devices"
    if len(categories) == 1:
        noun = GROUP_NOUNS.get(categories.pop(), noun)
    values = {e["value"].lower() for e in group}
    if len(values) == 1:
        return f"{len(group)} {noun} {VALUE_TEXTS.get(values.pop(), group[0]['value'])}"
    return f"{len(group)} {noun} changed at once"


def group_entries(entries):
    """entries of several devices within GROUP_WINDOW seconds, e.g. a scene,
    become one entry with children"""
    result = []
    i = 0
    while i < len(entries):
        j = i + 1
        while j < len(entries) and entries[j]["ts"] - entries[i]["ts"] <= GROUP_WINDOW:
            j += 1
        group = entries[i:j]
        if len({e["device"] for e in group}) >= GROUP_MIN:
            categories = collections.Counter(e["category"] for e in group)
            result.append(
                {
                    "ts": group[0]["ts"],
                    # all switched off again: how long the scene lasted
                    "end": (
                        max(e["end"] for e in group)
                        if all(e["end"] for e in group)
                        else None
                    ),
                    "count": 1,
                    "device": "",
                    "reading": "",
                    "value": "",
                    "category": categories.most_common(1)[0][0],
                    "text": group_text(group),
                    "room": "",
                    "alert": any(e["alert"] for e in group),
                    "running": any(e["running"] for e in group),
                    "children": group,
                }
            )
            i = j
        else:
            result.append(entries[i])
            i += 1
    return result


TEMPERATURE_ORDER = (
    "measured-temp",
    "measured-temperature",
    "temperature",
    "local_temperature",
    "current_temperature",
)


def _temperature_reading(readings):
    """the measured temperature among the readings of a thermostat"""
    found = [r for r in readings if classify.is_temperature(r)]
    for name in TEMPERATURE_ORDER:
        if name in found:
            return name
    return sorted(found)[0] if found else None


def _setpoint_reading(readings):
    found = sorted(r for r in readings if classify.is_setpoint(r))
    return found[0] if found else None


def _new_trend(infos, device, reading, category):
    name = label(infos, device)
    return {
        "device": device,
        "reading": reading,
        "text": name if reading == "state" else f"{name}: {reading}",
        "label": name,
        "name": reading_label(reading),
        "unit": unit(reading),
        "category": category,
        "room": infos.get(device, {}).get("room", ""),
        "min": None,
        "max": None,
        "on_change": classify.on_change(infos.get(device, {}), reading),
    }


def _hour_value(reading, total, count, last):
    # a target temperature is a step, its last value counts
    return last if classify.is_setpoint(reading) else round(total / count, 2)


def changed(low, high):
    """a curve changed when the difference can be read: the values are shown
    with one decimal (whole numbers from 100), up to 1% of the value. GPS
    coordinates or a counter only moving in the 4th decimal stay unchanged."""
    if low is None or high is None:
        return False
    middle = abs(low + high) / 2
    return high > low and high - low >= min(1 if middle >= 100 else 0.1, middle / 100)


def _range(trend, values):
    values = [v for v in values if v is not None]
    if values:
        trend["min"] = min(values)
        trend["max"] = max(values)
    trend["changed"] = changed(trend["min"], trend["max"])


def _carry(carry):
    """rows before the period -> (device, reading) -> last value"""
    return {(row[1], row[2]): row[8] for row in carry}


def _fill_day(trend, held, start, now):
    """FHEM only sends changes of many readings: hours without a value keep
    the last one. Returns the value at the end of the day."""
    points, lasts = trend["points"], trend.pop("lasts")
    for hour in range(24):
        if start + hour * 3600 > now:
            break
        if points[hour] is None:
            points[hour] = held
        else:
            held = lasts[hour]
    return held


def _attach_target(trend, setpoint, points, values):
    """the target temperature as second curve of the measured temperature"""
    values = [v for v in values if v is not None]
    if not values:
        return
    trend["target"] = {
        "reading": setpoint["reading"],
        "name": reading_label(setpoint["reading"]),
        "points": points,
        "min": min(values),
        "max": max(values),
        "on_change": setpoint.get("on_change", False),
    }
    trend["changed"] = trend["changed"] or changed(min(values), max(values))


def _pair_day(trends, held, start, now):
    """thermostats: one curve with measured and target temperature"""
    by_device = collections.defaultdict(dict)
    for trend in trends:
        by_device[trend["device"]][trend["reading"]] = trend
    result = []
    for device, readings in by_device.items():
        measured = _temperature_reading(readings)
        setpoint = _setpoint_reading(readings) or _setpoint_reading(
            [r for d, r in held if d == device]
        )
        if measured and setpoint:
            target = readings.pop(setpoint, None)
            if target is not None:
                points = target["points"]
            else:
                # no new target today: the one set before
                value = held[(device, setpoint)]
                target = {"reading": setpoint}
                points = [
                    value if start + hour * 3600 <= now else None for hour in range(24)
                ]
            _attach_target(readings[measured], target, points, points)
        result.extend(readings.values())
    return result


def _activity_current(reading, last, now):
    """state of a reading now: "Closed" since the end of its last entry"""
    active = last["value"].lower() in ACTIVE_VALUES
    if active and last["end"] is not None and last["end"] < now:
        value = last.get("end_value") or (
            "closed" if "open" in last["value"] else "off"
        )
        return {"text": value_text(reading, value), "since": last["end"]}
    since = last["ts"] if active else (last["end"] or last["ts"])
    return {"text": value_text(reading, last["value"]), "since": since}


def build_activity(entries, infos, now):
    """entries of one device (oldest first) -> per reading of the story:
    when it was on/open (segments) or what happened (moments), how often,
    how long in total, its state now. Numbers are in the curves."""
    by_reading = collections.defaultdict(list)
    for entry in entries:
        if entry.get("children") or classify.number(entry["value"]) is not None:
            continue
        by_reading[entry["reading"]].append(entry)
    result = []
    for reading, items in by_reading.items():
        info = infos.get(items[0]["device"], {})
        segments, total, longest, count = [], 0, 0, 0
        active_value = None
        for entry in items:
            count += entry["count"]
            active = entry["value"].lower() in ACTIVE_VALUES
            end = entry["end"] or (now if entry["running"] else None)
            what = describe(info, reading, entry["value"])[0]
            what = what[:1].upper() + what[1:]
            if active and end is not None:
                segments.append([entry["ts"], end, what])
                total += end - entry["ts"]
                longest = max(longest, end - entry["ts"])
            else:
                # a moment: button press or a value without end
                segments.append([entry["ts"], None, what])
            if active:
                active_value = entry["value"]
        text, nameless = describe(info, reading, active_value or items[-1]["value"])
        result.append(
            {
                "reading": reading,
                "name": "" if nameless else reading_label(reading),
                "what": text[:1].upper() + text[1:],
                "category": items[-1]["category"],
                "count": count,
                "total": round(total),
                "longest": round(longest),
                "segments": segments,
                "current": _activity_current(reading, items[-1], now),
            }
        )
    return result


def build_trends(rows, infos, carry=(), now=None):
    """rows: (hour, device, reading, category, min, max, sum, n, last)
    carry: the same rows of the time before (Store.values_before)
    -> day -> list of trends with 24 hourly values"""
    now = now or time.time()
    days = {}
    # day and hour of each start of an hour, the same for all readings
    moments = {}
    for hour, device, reading, category, _, _, total, count, last in rows:
        if category not in (classify.CLIMATE, classify.ENERGY) or not count:
            continue
        moment = moments.get(hour)
        if moment is None:
            local = datetime.datetime.fromtimestamp(hour)
            moment = moments[hour] = (local.strftime("%Y-%m-%d"), local.hour)
        trends = days.setdefault(moment[0], {})
        trend = trends.get((device, reading))
        if trend is None:
            trend = _new_trend(infos, device, reading, category)
            trend["points"] = [None] * 24
            trend["lasts"] = [None] * 24
            trends[(device, reading)] = trend
        trend["points"][moment[1]] = _hour_value(reading, total, count, last)
        trend["lasts"][moment[1]] = last
    held = _carry(row for row in carry if row[3] in (classify.CLIMATE, classify.ENERGY))
    result = {}
    for day in sorted(days):
        start = day_start(day)
        for key, trend in days[day].items():
            held[key] = _fill_day(trend, held.get(key), start, now)
            _range(trend, trend["points"])
        trends = _pair_day(list(days[day].values()), held, start, now)
        result[day] = sorted(trends, key=lambda t: (t["category"], t["text"]))
    return result


def _period_points(rows, held, start, end, now):
    """rows of one reading -> [hour, value] for every hour of the period from
    the first known value on, hours without a value keep the last one"""
    by_hour = {row[0]: row for row in rows}
    points = []
    hour = int(start // 3600 * 3600)
    while hour < end and hour <= now:
        row = by_hour.get(hour)
        if row is not None and row[7]:
            points.append([hour, _hour_value(row[2], row[6], row[7], row[8])])
            held = row[8]
        elif held is not None:
            points.append([hour, held])
        hour += 3600
    return points


def build_device_trends(rows, infos, carry=(), start=None, end=None, now=None):
    """rows: (hour, device, reading, category, min, max, sum, n, last) of one
    device -> one trend per reading with the hourly values of the period"""
    now = now or time.time()
    by_reading = collections.defaultdict(list)
    for row in rows:
        by_reading[row[2]].append(row)
    held = {reading: value for (_, reading), value in _carry(carry).items()}
    category = {row[2]: row[3] for row in list(carry) + list(rows)}
    if start is None:
        start = min((row[0] for row in rows), default=now)
        end = now + 1
    trends = {}
    for reading in set(by_reading) | set(held):
        points = _period_points(by_reading[reading], held.get(reading), start, end, now)
        if not points:
            continue
        device = (rows or carry)[0][1]
        trend = _new_trend(infos, device, reading, category[reading])
        trend["points"] = points
        _range(trend, [p[1] for p in points])
        trends[reading] = trend
    measured = _temperature_reading(trends)
    setpoint = _setpoint_reading(trends)
    if measured and setpoint:
        target = trends.pop(setpoint)
        points = target["points"]
        _attach_target(trends[measured], target, points, [p[1] for p in points])
    return sorted(trends.values(), key=lambda t: (not t["changed"], t["reading"]))


def _curve_points(rows, held, start, end, now):
    """rows of one reading -> [hour, avg, min, max], hours without a value
    keep the last one"""
    by_hour = {row[0]: row for row in rows}
    points = []
    hour = int(start // 3600 * 3600)
    while hour < end and hour <= now:
        row = by_hour.get(hour)
        if row is not None and row[7]:
            value = _hour_value(row[2], row[6], row[7], row[8])
            points.append([hour, value, row[4], row[5]])
            held = row[8]
        elif held is not None:
            points.append([hour, held, held, held])
        hour += 3600
    return points


def build_curve(device, readings, data, infos, period):
    """readings: the reading and maybe its target temperature, data: rows
    (reading -> hourly rows) and carry (reading -> value before the period),
    period: start, end, last day, today
    -> the curve for the curve popup with [hour, avg, min, max] per hour"""
    now = time.time()
    rows, carry = data["rows"], data["carry"]
    start, end, last, today = period
    reading = readings[0]
    real = rows.get(reading, [])
    points = _curve_points(real, carry.get(reading), start, end, now)
    total = sum(row[6] for row in real)
    count = sum(row[7] for row in real)
    info = infos.get(device, {})
    result = {
        "device": device,
        "reading": reading,
        "label": label(infos, device),
        "name": reading_label(reading),
        "unit": unit(reading),
        "category": real[-1][3] if real else classify.CLIMATE,
        "room": info.get("room", ""),
        "from": start,
        "to": end,
        "day": last.isoformat(),
        "today": today.isoformat(),
        "points": points,
        "min": min((p[2] for p in points), default=None),
        "max": max((p[3] for p in points), default=None),
        "avg": round(total / count, 2) if count else None,
        "on_change": classify.on_change(info, reading),
    }
    if not count and points:
        result["avg"] = round(sum(p[1] for p in points) / len(points), 2)
    if len(readings) > 1:
        target = _curve_target(readings[1], rows, carry, (start, end, now))
        if target:
            result["target"] = target
    return result


def _curve_target(reading, rows, carry, period):
    points = _curve_points(rows.get(reading, []), carry.get(reading), *period)
    if not points:
        return None
    return {
        "reading": reading,
        "name": reading_label(reading),
        "points": [[p[0], p[1]] for p in points],
        "min": min(p[1] for p in points),
        "max": max(p[1] for p in points),
    }


def curve_readings(reading, readings):
    """the reading of a curve popup and the target temperature for the
    measured temperature of a thermostat (also when the target was clicked)"""
    measured = _temperature_reading(readings)
    setpoint = _setpoint_reading(readings)
    if measured and setpoint and reading in (measured, setpoint):
        return [measured, setpoint]
    return [reading]


def build(
    first_day, last_day, rows, hourly_rows, hidden, absences, infos, now, carry=()
):
    """the response of get entries, newest day first"""
    entries = build_entries(rows, infos, absences, now)
    by_day = collections.defaultdict(list)
    for entry in entries:
        by_day[day_of(entry["ts"])].append(entry)
    trends = build_trends(hourly_rows, infos, carry, now)

    days = []
    day = datetime.datetime.strptime(last_day, "%Y-%m-%d").date()
    first = datetime.datetime.strptime(first_day, "%Y-%m-%d").date()
    today = datetime.date.fromtimestamp(now)
    while day >= first:
        name = day.isoformat()
        if day <= today:
            start = day_start(name)
            end = start + 86400
            days.append(
                {
                    "day": name,
                    "entries": by_day.get(name, []),
                    "hidden": hidden.get(name, 0),
                    "trends": trends.get(name, []),
                    "absent": any(
                        s < end and (e is None or e > start) and (e or now) - s >= 3600
                        for s, e in absences
                    ),
                }
            )
        day -= datetime.timedelta(days=1)
    return days
