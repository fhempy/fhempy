"""Room schedules: switch points with a temperature per weekday.

Text form (reading and set command), every point is "from time on":

    Mo-Fr 00:00 17, 06:00 21, 08:00 18.5, 16:30 21, 22:00 17; Sa-Su 15

A value without a time is the whole day. Instead of a number "comfort" or
"eco" uses the comfort or eco temperature of the room. A day without a
point at 00:00 keeps the last temperature of the day before.

The old form with comfort periods still works, the rest of such a day is
eco:

    Mo-Fr 06:00-08:00,16:30-22:00; Sa-Su 07:30-23:00

German day names work as well (Mo Di Mi Do Fr Sa So), "-" alone means the
whole day eco.

The schedule is stored in the JSON format of the FHEM module weekprofile
(every temperature applies until its time, the last one until 24:00):

    {"Mon":{"time":["06:00","08:00","24:00"],"temp":["17","21","17"]},...}

and the set command takes this format as well.
"""

import datetime
import json
import re

DAYS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
DAY_ALIASES = {
    "mo": 0,
    "tu": 1,
    "di": 1,
    "we": 2,
    "mi": 2,
    "th": 3,
    "do": 3,
    "fr": 4,
    "sa": 5,
    "su": 6,
    "so": 6,
}
LEVELS = {"comfort": "comfort", "komfort": "comfort", "eco": "eco", "spar": "eco"}
WEEKPROFILE_DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
DEFAULT = "Mo-Fr 06:00-08:00,16:00-22:00; Sa-Su 07:00-22:30"
PERIOD = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$")
POINT = re.compile(r"^(?:(\d{1,2}):(\d{2})\s+)?(\S+)$")
MIN_TEMP = 5.0
MAX_TEMP = 30.0


def _day(token):
    key = token.strip().lower()[:2]
    if key not in DAY_ALIASES:
        raise ValueError(f"unknown day {token}")
    return DAY_ALIASES[key]


def _days(spec):
    days = []
    for part in spec.split(","):
        if "-" in part:
            first, last = (_day(p) for p in part.split("-", 1))
            day = first
            while True:
                days.append(day)
                if day == last:
                    break
                day = (day + 1) % 7
        else:
            days.append(_day(part))
    return days


def _minutes(hours, minutes):
    value = int(hours) * 60 + int(minutes)
    if value > 24 * 60 or int(minutes) > 59:
        raise ValueError(f"invalid time {hours}:{minutes}")
    return value


def value_of(text):
    """a temperature (float) or the level "comfort"/"eco"; ValueError"""
    word = str(text).strip().lower().removesuffix("c").removesuffix("°").rstrip()
    if word in LEVELS:
        return LEVELS[word]
    try:
        temp = float(word.replace(",", "."))
    except ValueError:
        raise ValueError(f"invalid temperature {text}") from None
    if not MIN_TEMP <= temp <= MAX_TEMP:
        raise ValueError(f"temperature {text} is not between 5 and 30 °C")
    return temp


def merge(periods):
    result = []
    for start, end in sorted(periods):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(end, result[-1][1]))
        else:
            result.append((start, end))
    return result


def _from_periods(periods):
    """comfort periods -> points, the rest of the day eco"""
    points = {0: "eco"}
    for start, end in merge(periods):
        points[start] = "comfort"
        if end < 24 * 60:
            points[end] = "eco"
    return sorted(points.items())


def _tokens(spec):
    """split at "," but keep a decimal comma (21,5) with its number"""
    tokens = []
    for part in (p.strip() for p in spec.split(",")):
        if tokens and re.fullmatch(r"\d+", part) and re.search(r"\d$", tokens[-1]):
            tokens[-1] += "." + part
        elif part:
            tokens.append(part)
    return tokens


def _period(token):
    """(start, end) of a comfort period like 06:00-08:00, None otherwise"""
    match = PERIOD.match(token)
    if not match:
        return None
    start = _minutes(match.group(1), match.group(2))
    end = _minutes(match.group(3), match.group(4))
    if end <= start:
        raise ValueError(f"period {token} ends before it starts")
    return start, end


def _point(token):
    """(minute, value) of a switch point like 06:00 21; ValueError"""
    match = POINT.match(token)
    if not match:
        raise ValueError(f"invalid point {token}, use 06:00 21")
    minute = 0
    if match.group(1) is not None:
        minute = _minutes(match.group(1), match.group(2))
        if minute >= 24 * 60:
            raise ValueError(f"invalid time {token}")
    return minute, value_of(match.group(3))


def _points(spec):
    spec = spec.strip()
    if spec in ("-", ""):
        return [(0, "eco")]
    periods, points = [], {}
    for token in _tokens(spec):
        period = _period(token)
        if period:
            periods.append(period)
        else:
            minute, value = _point(token)
            points[minute] = value
    if periods and points:
        raise ValueError("use either periods (06:00-08:00) or points (06:00 21)")
    if periods:
        return _from_periods(periods)
    return sorted(points.items())


def parse(text):
    """text -> {day 0-6: [(minute, temperature or level), ...]}, days which
    are not mentioned are eco all day. Raises ValueError."""
    week = {day: [(0, "eco")] for day in range(7)}
    text = (text or "").strip()
    if not text:
        return week
    if text.startswith("{"):
        return from_weekprofile(text)
    for group in text.split(";"):
        group = group.strip()
        if not group:
            continue
        days, _, spec = group.partition(" ")
        parsed = _points(spec)
        for day in _days(days):
            week[day] = list(parsed)
    return week


def _hm(minute):
    return f"{minute // 60:02d}:{minute % 60:02d}"


def _value_text(value):
    return value if isinstance(value, str) else f"{value:g}"


def _day_range(days):
    if len(days) == 1:
        return DAYS[days[0]]
    return f"{DAYS[days[0]]}-{DAYS[days[-1]]}"


def day_text(points):
    if not points:
        return "-"
    if len(points) == 1 and points[0][0] == 0:
        return _value_text(points[0][1])
    return ", ".join(f"{_hm(m)} {_value_text(v)}" for m, v in points)


def to_text(week):
    """canonical text, equal days next to each other are grouped"""
    groups = []
    for day in range(7):
        points = list(week.get(day, []))
        if groups and groups[-1][1] == points and groups[-1][0][-1] == day - 1:
            groups[-1][0].append(day)
        else:
            groups.append(([day], points))
    return "; ".join(f"{_day_range(days)} {day_text(p)}" for days, p in groups)


def value_at(week, when):
    """temperature or level at a moment; a day without a point at 00:00
    keeps the last value of the day before"""
    minute = when.hour * 60 + when.minute
    day = when.weekday()
    current = [v for m, v in week.get(day, []) if m <= minute]
    if current:
        return current[-1]
    for back in range(1, 8):
        points = week.get((day - back) % 7, [])
        if points:
            return points[-1][1]
    return "eco"


def next_switch(week, when):
    """datetime of the next change of the value after when, None if the
    schedule never changes"""
    current = value_at(week, when)
    day_start = when.replace(hour=0, minute=0, second=0, microsecond=0)
    for offset in range(8):
        day = day_start + datetime.timedelta(days=offset)
        for minute in sorted({m for m, _ in week.get(day.weekday(), [])} | {0}):
            moment = day + datetime.timedelta(minutes=minute)
            if moment <= when:
                continue
            if value_at(week, moment) != current:
                return moment
    return None


def day_points(week, day):
    """points of a day from 00:00 on (the start from the day before)"""
    points = list(week.get(day, []))
    if not points or points[0][0] > 0:
        # 2026-11-23 is a Monday
        start = value_at(week, datetime.datetime(2026, 11, 23 + day))
        points.insert(0, (0, start))
    return points


def to_weekprofile(week, temp_of):
    """weekprofile JSON, temp_of turns comfort/eco into a temperature"""
    profile = {}
    for day in range(7):
        points = []
        for minute, value in day_points(week, day):
            temp = f"{temp_of(value):g}"
            if not points or points[-1][1] != temp:
                points.append((minute, temp))
        times = [_hm(m) for m, _ in points[1:]] + ["24:00"]
        temps = [t for _, t in points]
        profile[WEEKPROFILE_DAYS[day]] = {"time": times, "temp": temps}
    return json.dumps(profile, separators=(",", ":"))


def _weekprofile_temp(text):
    word = str(text).strip().lower()
    if word == "off":
        return MIN_TEMP
    if word == "on":
        return MAX_TEMP
    return value_of(word)


def from_weekprofile(text):
    """weekprofile JSON -> week; ValueError"""
    try:
        profile = json.loads(text) if isinstance(text, str) else text
    except ValueError:
        raise ValueError("invalid weekprofile JSON") from None
    if not isinstance(profile, dict):
        raise ValueError("invalid weekprofile JSON")
    week = {day: [(0, "eco")] for day in range(7)}
    for day, name in enumerate(WEEKPROFILE_DAYS):
        entry = profile.get(name)
        if entry is not None:
            week[day] = _weekprofile_day(name, entry)
    return week


def _weekprofile_minute(name, until):
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", str(until).strip())
    if not match:
        raise ValueError(f"{name}: invalid time {until}")
    return _minutes(match.group(1), match.group(2))


def _weekprofile_day(name, entry):
    """one weekprofile day {"time": [...], "temp": [...]} -> points"""
    times, temps = entry.get("time") or [], entry.get("temp") or []
    if not times or len(times) != len(temps):
        raise ValueError(f"{name}: time and temp need the same length")
    points, start = [], 0
    for until, temp in zip(times, temps):
        end = _weekprofile_minute(name, until)
        if end <= start:
            raise ValueError(f"{name}: times have to rise")
        value = _weekprofile_temp(temp)
        if not points or points[-1][1] != value:
            points.append((start, value))
        start = end
    return points
