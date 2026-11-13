"""Evaluates DOIF conditions of the editor model without FHEM: "What would
happen now?" with the current values and the simulation of the past days
with the events of the timeline. Code parts (Perl) can't be evaluated, they
are "unknown" (None)."""

import datetime
import math
import re

from . import parser

WEEKDAY_NAMES = {
    # DOIF: 0 Sunday ... 6 Saturday, 7 weekend/holiday, 8 working day
    "so": 0,
    "su": 0,
    "sun": 0,
    "sonntag": 0,
    "sunday": 0,
    "mo": 1,
    "mon": 1,
    "montag": 1,
    "monday": 1,
    "di": 2,
    "tu": 2,
    "tue": 2,
    "dienstag": 2,
    "tuesday": 2,
    "mi": 3,
    "we": 3,
    "wed": 3,
    "mittwoch": 3,
    "wednesday": 3,
    "do": 4,
    "th": 4,
    "thu": 4,
    "donnerstag": 4,
    "thursday": 4,
    "fr": 5,
    "fri": 5,
    "freitag": 5,
    "friday": 5,
    "sa": 6,
    "sat": 6,
    "samstag": 6,
    "saturday": 6,
    "wochenende": 7,
    "weekend": 7,
    "at": 8,
    "ar": 8,
    "arbeitstag": 8,
    "workday": 8,
}
NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


# --- sun ------------------------------------------------------------------------


def sun_time(date, event, latitude, longitude, zenith=90.833):
    """local sunrise/sunset of date (datetime.date) as datetime, NOAA
    algorithm like SUNRISE_EL with horizon REAL"""
    day = date.timetuple().tm_yday
    lng_hour = longitude / 15
    approx = day + ((6 if event == "sunrise" else 18) - lng_hour) / 24
    anomaly = 0.9856 * approx - 3.289
    true_long = (
        anomaly
        + 1.916 * math.sin(math.radians(anomaly))
        + 0.020 * math.sin(math.radians(2 * anomaly))
        + 282.634
    ) % 360
    right_asc = (
        math.degrees(math.atan(0.91764 * math.tan(math.radians(true_long)))) % 360
    )
    right_asc += (true_long // 90) * 90 - (right_asc // 90) * 90
    right_asc /= 15
    sin_dec = 0.39782 * math.sin(math.radians(true_long))
    cos_dec = math.cos(math.asin(sin_dec))
    cos_h = (
        math.cos(math.radians(zenith)) - sin_dec * math.sin(math.radians(latitude))
    ) / (cos_dec * math.cos(math.radians(latitude)))
    if cos_h > 1 or cos_h < -1:
        # polar day or night
        return datetime.datetime.combine(
            date, datetime.time(6 if event == "sunrise" else 18)
        )
    hour = (
        360 - math.degrees(math.acos(cos_h))
        if event == "sunrise"
        else math.degrees(math.acos(cos_h))
    ) / 15
    local_mean = hour + right_asc - 0.06571 * approx - 6.622
    utc = (local_mean - lng_hour) % 24
    midnight = datetime.datetime(
        date.year, date.month, date.day, tzinfo=datetime.timezone.utc
    )
    moment = midnight + datetime.timedelta(hours=utc)
    local = moment.astimezone().replace(tzinfo=None)
    if local.date() != date:
        local = local.replace(year=date.year, month=date.month, day=date.day)
    return local


class Context:
    """values and time for an evaluation"""

    def __init__(self, values, now, latitude=50.112, longitude=8.686, holidays=()):
        self.values = values  # {(device, reading): (ts, value)}
        self.now = now  # datetime
        self.latitude = latitude
        self.longitude = longitude
        self.holidays = set(holidays)
        self.event = None  # (device, reading, value) which triggered
        self.timer = None  # leaf text of the timer which triggered
        self.self_name = ""

    def value(self, device, reading):
        if device == "$SELF":
            device = self.self_name
        item = self.values.get((device, reading or "state"))
        return None if item is None else item[1]

    def age(self, device, reading):
        item = self.values.get((device, reading or "state"))
        if item is None or item[0] is None:
            return None
        return self.now.timestamp() - item[0]

    def time_of(self, time, date=None):
        """datetime of a timer time on date (default today), None if unknown"""
        date = date or self.now.date()
        kind = time.get("k")
        if kind == "clock":
            parts = [int(x) for x in time["v"].split(":")]
            while len(parts) < 3:
                parts.append(0)
            hour = parts[0] % 24
            return datetime.datetime.combine(
                date, datetime.time(hour, parts[1], parts[2])
            ) + (datetime.timedelta(days=1) if parts[0] >= 24 else datetime.timedelta())
        if kind == "sun":
            moment = sun_time(date, time["event"], self.latitude, self.longitude)
            return moment + datetime.timedelta(seconds=int(time.get("offset") or 0))
        if kind == "reading":
            value = self.value(time["dev"], time["reading"])
            if value is None:
                return None
            match = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", value)
            if not match:
                return None
            return datetime.datetime.combine(
                date,
                datetime.time(
                    int(match.group(1)) % 24,
                    int(match.group(2)),
                    int(match.group(3) or 0),
                ),
            )
        return None

    def day_matches(self, days, date=None):
        if not days:
            return True
        date = date or self.now.date()
        weekday = (date.weekday() + 1) % 7  # Sunday 0
        weekend = weekday in (0, 6) or date in self.holidays
        for word in re.split(r"[\s,]+", days.strip()):
            if not word:
                continue
            key = word.lower()
            numbers = (
                [int(c) for c in key] if key.isdigit() else [WEEKDAY_NAMES.get(key)]
            )
            for number in numbers:
                if number is None:
                    return None
                if number == weekday and number < 7:
                    return True
                if number == 7 and weekend:
                    return True
                if number == 8 and not weekend:
                    return True
        return False


def perl_true(value):
    return value is not None and value != "" and value != "0"


def to_number(value):
    if value is None:
        return None
    match = NUMBER_RE.search(str(value))
    return float(match.group(0).replace(",", ".")) if match else None


def compare(left, op, right):
    if left is None or right is None:
        return None
    if op in ("==", "!=", "<", ">", "<=", ">="):
        a, b = to_number(left), to_number(right)
        if a is None or b is None:
            # Perl compares non numbers as 0
            a = 0.0 if a is None else a
            b = 0.0 if b is None else b
        return {
            "==": a == b,
            "!=": a != b,
            "<": a < b,
            ">": a > b,
            "<=": a <= b,
            ">=": a >= b,
        }[op]
    a, b = str(left), str(right)
    if op in ("=~", "!~"):
        try:
            found = re.search(b, a) is not None
        except re.error:
            return None
        return found if op == "=~" else not found
    return {
        "eq": a == b,
        "ne": a != b,
        "lt": a < b,
        "gt": a > b,
        "le": a <= b,
        "ge": a >= b,
    }[op]


def _reading_value(ctx, device, reading, fmt):
    if fmt == "sec":
        age = ctx.age(device, reading)
        return None if age is None else str(int(age))
    value = ctx.value(device, reading)
    if fmt and fmt.startswith("d") and value is not None:
        number = to_number(value)
        return None if number is None else str(number)
    return value


def _value_of(ctx, value):
    kind = value.get("k")
    if kind in ("text", "number"):
        return value.get("v")
    if kind == "reading":
        return _reading_value(
            ctx, value["dev"], value.get("reading") or "state", value.get("fmt")
        )
    return None


def _in_range(ctx, leaf):
    start = ctx.time_of(leaf["from"])
    end = ctx.time_of(leaf["to"])
    if start is None or end is None:
        return None
    now = ctx.now
    if end <= start:
        # over midnight: until the end of the next day's range
        inside = now >= start or now < end
        date = now.date() if now >= start else now.date() - datetime.timedelta(days=1)
    else:
        inside = start <= now < end
        date = now.date()
    if not inside:
        return False
    return ctx.day_matches(leaf.get("days"), date)


def eval_leaf(ctx, leaf):
    kind = leaf.get("t")
    result = None
    if kind == "cmp":
        left = _reading_value(
            ctx, leaf["dev"], leaf.get("reading") or "state", leaf.get("fmt")
        )
        result = compare(left, leaf["op"], _value_of(ctx, leaf["value"]))
    elif kind == "change":
        result = perl_true(
            _reading_value(
                ctx, leaf["dev"], leaf.get("reading") or "state", leaf.get("fmt")
            )
        )
    elif kind == "event":
        event = ctx.event
        if event is None or leaf.get("check"):
            result = False
        else:
            device = ctx.self_name if leaf["dev"] == "$SELF" else leaf["dev"]
            text = event[2] if event[1] == "state" else f"{event[1]}: {event[2]}"
            try:
                result = (
                    event[0] == device and re.search(leaf["regex"], text) is not None
                )
            except re.error:
                result = None
    elif kind == "anyevent":
        event = ctx.event
        if event is None:
            result = False
        else:
            text = f"{event[0]}:{event[1]}: {event[2]}"
            try:
                result = re.search(leaf["regex"], text) is not None
            except re.error:
                result = None
    elif kind in ("time", "every"):
        if leaf.get("check"):
            result = False
        else:
            result = ctx.timer == parser.leaf_text(dict(leaf, **{"not": False}))
            if result:
                result = ctx.day_matches(leaf.get("days"))
    elif kind == "range":
        result = _in_range(ctx, leaf)
    elif kind in ("and", "or"):
        result = eval_tree(ctx, leaf)
    if leaf.get("not") and result is not None:
        result = not result
    return result


def eval_tree(ctx, tree):
    if tree is None:
        return True
    kind = tree.get("t")
    if kind in ("and", "or"):
        results = [eval_tree(ctx, item) for item in tree.get("items", [])]
        if kind == "and":
            if False in results:
                result = False
            elif None in results:
                result = None
            else:
                result = True
        else:
            if True in results:
                result = True
            elif None in results:
                result = None
            else:
                result = False
        if tree.get("not") and result is not None:
            result = not result
        return result
    return eval_leaf(ctx, tree)


def explain(ctx, tree):
    """leaves with their result and current value for the UI"""
    result = []

    def walk(node):
        if node is None:
            return
        if node.get("t") in ("and", "or"):
            for item in node.get("items", []):
                walk(item)
            return
        current = None
        if node.get("t") in ("cmp", "change"):
            current = _reading_value(
                ctx, node["dev"], node.get("reading") or "state", node.get("fmt")
            )
        elif node.get("t") == "range":
            start, end = ctx.time_of(node["from"]), ctx.time_of(node["to"])
            if start and end:
                current = f"{start:%H:%M}-{end:%H:%M}"
        elif node.get("t") == "time":
            moment = ctx.time_of(node["at"])
            current = moment.strftime("%H:%M") if moment else None
        result.append(
            {
                "text": parser.leaf_text(node),
                # a point in time is only true at that moment
                "result": (
                    None if node.get("t") in ("time", "every") else eval_leaf(ctx, node)
                ),
                "current": current,
            }
        )

    walk(tree)
    return result


def which_case(ctx, rule, last_case=None, do_always=False):
    """index of the case DOIF would execute or None"""
    cases = rule.get("cases", [])
    for index, case in enumerate(cases):
        if case.get("kind") == "else" or case.get("cond") is None:
            result = True
        else:
            result = eval_tree(ctx, case.get("cond"))
        if result is None:
            return "unknown"
        if result:
            if index == last_case and not do_always:
                return None
            return index
    return None


# --- simulation -------------------------------------------------------------------


def timer_leaves(rule):
    leaves = []

    def walk(node):
        if node is None:
            return
        if node.get("t") in ("and", "or"):
            for item in node.get("items", []):
                walk(item)
        elif node.get("t") in ("time", "range", "every") and not node.get("check"):
            leaves.append(node)

    for case in rule.get("cases", []):
        walk(case.get("cond"))
    return leaves


def timer_moments(ctx, leaf, start, end):
    """(datetime, timer text) of a timer leaf between start and end"""
    moments = []
    text = parser.leaf_text(dict(leaf, **{"not": False}))
    day = start.date() - datetime.timedelta(days=1)
    while day <= end.date():
        kind = leaf.get("t")
        times = []
        if kind == "time":
            times.append(ctx.time_of(leaf["at"], day))
        elif kind == "range":
            times.append(ctx.time_of(leaf["from"], day))
            times.append(ctx.time_of(leaf["to"], day))
            if leaf.get("every"):
                step = ctx.time_of(leaf["every"], datetime.date(2000, 1, 1))
                if step is not None and times[0] is not None and times[1] is not None:
                    seconds = step.hour * 3600 + step.minute * 60 + step.second
                    moment = times[0]
                    stop = (
                        times[1]
                        if times[1] > times[0]
                        else times[1] + datetime.timedelta(days=1)
                    )
                    while seconds > 0 and moment < stop and len(times) < 2000:
                        moment += datetime.timedelta(seconds=seconds)
                        times.append(moment)
        elif kind == "every":
            step = ctx.time_of(leaf["every"], datetime.date(2000, 1, 1))
            if step is not None:
                seconds = step.hour * 3600 + step.minute * 60 + step.second
                moment = datetime.datetime.combine(day, datetime.time())
                while seconds > 0 and moment.date() == day:
                    times.append(moment)
                    moment += datetime.timedelta(seconds=seconds)
        for moment in times:
            if moment is not None and start <= moment < end:
                moments.append((moment, text))
        day += datetime.timedelta(days=1)
    return moments


def simulate(rule, events, initial, start, end, ctx_args, do_always=False):
    """replays events [(ts, device, reading, value)] through the rule.
    Returns executions [{ts, case, trigger}] and unknown (code parts)"""
    triggers, _, _, _ = parser.reads_and_writes(rule)
    values = dict(initial)
    ctx = Context(values, datetime.datetime.fromtimestamp(start), **ctx_args)
    ctx.self_name = rule.get("name", "")
    items = [(row[0], "event", row) for row in events]
    for leaf in timer_leaves(rule):
        for moment, text in timer_moments(
            ctx,
            leaf,
            datetime.datetime.fromtimestamp(start),
            datetime.datetime.fromtimestamp(end),
        ):
            items.append((moment.timestamp(), "timer", text))
    items.sort(key=lambda item: (item[0], item[1] != "event"))
    executions = []
    unknown = 0
    last_case = None
    single = len(rule.get("cases", [])) == 1
    for ts, kind, payload in items:
        ctx.now = datetime.datetime.fromtimestamp(ts)
        ctx.event = None
        ctx.timer = None
        if kind == "event":
            _, device, reading, value = payload
            values[(device, reading)] = (ts, value)
            if (device, reading) not in triggers and not any(
                trigger[0].startswith("@") for trigger in triggers
            ):
                continue
            ctx.event = (device, reading, value)
            label = (
                f"{device}: {value}"
                if reading == "state"
                else f"{device} {reading}: {value}"
            )
        else:
            ctx.timer = payload
            label = payload.strip("[]")
        case = which_case(ctx, rule, last_case, do_always)
        if case == "unknown":
            unknown += 1
            continue
        if case is None:
            if single and not do_always and last_case == 0:
                # implicit DOELSE of a single case: cmd_2
                cond = eval_tree(ctx, rule["cases"][0].get("cond"))
                if cond is False:
                    last_case = 1
            continue
        last_case = case
        executions.append({"ts": ts, "case": case, "trigger": label})
    return executions, unknown
