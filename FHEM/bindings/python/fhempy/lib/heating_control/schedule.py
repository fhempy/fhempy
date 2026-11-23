"""Very simple room schedules: comfort periods per weekday, the rest of the
day is eco. Text form (reading and set command):

    Mo-Fr 06:00-08:00,16:30-22:00; Sa-Su 07:30-23:00

German day names work as well (Mo Di Mi Do Fr Sa So), "-" alone means the
whole day eco, "00:00-24:00" the whole day comfort.
"""

import datetime
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
DEFAULT = "Mo-Fr 06:00-08:00,16:00-22:00; Sa-Su 07:00-22:30"
PERIOD = re.compile(r"^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$")


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


def _periods(spec):
    if spec.strip() in ("-", ""):
        return []
    periods = []
    for part in spec.split(","):
        match = PERIOD.match(part.strip())
        if not match:
            raise ValueError(f"invalid period {part.strip()}, use 06:00-08:00")
        start = _minutes(match.group(1), match.group(2))
        end = _minutes(match.group(3), match.group(4))
        if end <= start:
            raise ValueError(f"period {part.strip()} ends before it starts")
        periods.append((start, end))
    return merge(periods)


def merge(periods):
    result = []
    for start, end in sorted(periods):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(end, result[-1][1]))
        else:
            result.append((start, end))
    return result


def parse(text):
    """text -> {day 0-6: [(start minute, end minute), ...]}, days which are
    not mentioned are eco all day. Raises ValueError."""
    week = {day: [] for day in range(7)}
    text = (text or "").strip()
    if not text:
        return week
    for group in text.split(";"):
        group = group.strip()
        if not group:
            continue
        days, _, periods = group.partition(" ")
        parsed = _periods(periods)
        for day in _days(days):
            week[day] = parsed
    return week


def _hm(minute):
    return f"{minute // 60:02d}:{minute % 60:02d}"


def _day_range(days):
    if len(days) == 1:
        return DAYS[days[0]]
    return f"{DAYS[days[0]]}-{DAYS[days[-1]]}"


def to_text(week):
    """canonical text, equal days next to each other are grouped"""
    groups = []
    for day in range(7):
        periods = week.get(day, [])
        if groups and groups[-1][1] == periods and groups[-1][0][-1] == day - 1:
            groups[-1][0].append(day)
        else:
            groups.append(([day], periods))
    parts = []
    for days, periods in groups:
        text = ",".join(f"{_hm(s)}-{_hm(e)}" for s, e in periods) or "-"
        parts.append(f"{_day_range(days)} {text}")
    return "; ".join(parts)


def is_comfort(week, when):
    minute = when.hour * 60 + when.minute
    return any(s <= minute < e for s, e in week.get(when.weekday(), []))


def next_switch(week, when):
    """datetime of the next change comfort <-> eco after when, None if the
    schedule never changes"""
    current = is_comfort(week, when)
    day_start = when.replace(hour=0, minute=0, second=0, microsecond=0)
    for offset in range(8):
        day = day_start + datetime.timedelta(days=offset)
        points = sorted(
            {m for s, e in week.get(day.weekday(), []) for m in (s, e)} | {0}
        )
        for minute in points:
            moment = day + datetime.timedelta(minutes=minute)
            if moment <= when:
                continue
            if is_comfort(week, moment) != current:
                return moment
    return None


def day_bar(week, day):
    """48 half hours of a weekday, True = comfort"""
    periods = week.get(day, [])
    return [any(s <= slot * 30 < e for s, e in periods) for slot in range(48)]
