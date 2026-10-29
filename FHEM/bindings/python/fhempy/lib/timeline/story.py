"""Turns the stored events into a readable story per day: on and off become
one entry with a duration, repeats are bundled, devices switched together are
grouped and everything unusual while nobody is at home is marked.

Pure functions, no FHEM access."""

import collections
import datetime

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


def entry_text(infos, device, reading, value):
    info = infos.get(device, {})
    name = label(infos, device)
    if reading == "state":
        if info.get("TYPE") == classify.RESIDENTS_TYPE and value in RESIDENTS_TEXTS:
            return RESIDENTS_TEXTS[value]
        if info.get("TYPE") in ("ROOMMATE", "GUEST") and value in ROOMMATE_TEXTS:
            return f"{name} {ROOMMATE_TEXTS[value]}"
    value_text = VALUE_TEXTS.get(value.lower(), value)
    if reading in NAMELESS_READINGS:
        return f"{name} {value_text}"
    return f"{name}: {reading} {value_text}"


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


def _continue_entry(previous, ts, value):
    """True if the event only continues the previous entry of its reading:
    on again shortly after off, the matching off or the same value again"""
    if previous is None:
        return False
    lower = value.lower()
    was_active = previous["value"].lower() in ACTIVE_VALUES
    if was_active and previous["end"] is None and lower in ACTIVE_VALUES:
        # still on: devices which repeat their state don't start a new entry
        if previous["value"] != value:
            previous["count"] += 1
        previous["last"] = ts
        return True
    if was_active and previous["end"] is not None and lower in INACTIVE_VALUES:
        # still off
        return True
    if ts - previous["last"] > MERGE_GAP:
        # off long after on closes the running entry
        closes = was_active and previous["end"] is None and lower in INACTIVE_VALUES
        if closes:
            previous["end"] = ts
            previous["last"] = ts
        return closes
    if was_active and lower in ACTIVE_VALUES:
        # on again shortly after off
        previous["count"] += 1
        previous["end"] = None
    elif was_active and lower in INACTIVE_VALUES:
        previous["end"] = ts
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


def build_trends(rows, infos):
    """rows: (hour, device, reading, category, min, max, sum, n)
    -> day -> list of trends with 24 hourly averages"""
    days = {}
    for hour, device, reading, category, low, high, total, count in rows:
        if category not in (classify.CLIMATE, classify.ENERGY) or not count:
            continue
        moment = datetime.datetime.fromtimestamp(hour)
        trends = days.setdefault(moment.strftime("%Y-%m-%d"), {})
        trend = trends.get((device, reading))
        if trend is None:
            name = label(infos, device)
            trend = {
                "device": device,
                "reading": reading,
                "text": name if reading == "state" else f"{name}: {reading}",
                "label": name,
                "category": category,
                "room": infos.get(device, {}).get("room", ""),
                "min": low,
                "max": high,
                "points": [None] * 24,
                "on_change": classify.on_change(infos.get(device, {}), reading),
            }
            trends[(device, reading)] = trend
        trend["min"] = min(trend["min"], low)
        trend["max"] = max(trend["max"], high)
        trend["points"][moment.hour] = round(total / count, 2)
    for trends in days.values():
        for trend in trends.values():
            trend["changed"] = trend["max"] != trend["min"]
    return {
        day: sorted(trends.values(), key=lambda t: (t["category"], t["text"]))
        for day, trends in days.items()
    }


def build_device_trends(rows, infos):
    """rows: (hour, device, reading, category, min, max, sum, n) of one device
    -> one trend per reading with the hourly averages of the whole period"""
    trends = {}
    for hour, device, reading, category, low, high, total, count in rows:
        if not count:
            continue
        trend = trends.get(reading)
        if trend is None:
            name = label(infos, device)
            trend = {
                "device": device,
                "reading": reading,
                "text": name if reading == "state" else f"{name}: {reading}",
                "category": category,
                "min": low,
                "max": high,
                "points": [],
                "on_change": classify.on_change(infos.get(device, {}), reading),
            }
            trends[reading] = trend
        trend["min"] = min(trend["min"], low)
        trend["max"] = max(trend["max"], high)
        trend["points"].append([hour, round(total / count, 2)])
    for trend in trends.values():
        trend["changed"] = trend["max"] != trend["min"]
    return sorted(trends.values(), key=lambda t: (not t["changed"], t["reading"]))


def build(first_day, last_day, rows, hourly_rows, hidden, absences, infos, now):
    """the response of get entries, newest day first"""
    entries = build_entries(rows, infos, absences, now)
    by_day = collections.defaultdict(list)
    for entry in entries:
        by_day[day_of(entry["ts"])].append(entry)
    trends = build_trends(hourly_rows, infos)

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
