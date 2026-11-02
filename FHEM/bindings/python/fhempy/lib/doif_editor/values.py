"""Computed values: a calculation read from top to bottom like a receipt.

value = {"name": "Kochzeit", "title": "Kochzeit Eier", "unit": "min",
         "rows": [row, ...], "min": "", "max": "", "round": ""}
row = {"op": "start" | "mul" | "add" | "sub" | "set",
       "amount": amount, "only_if": condition tree (parser model) or None}
amount = {"k": "fixed", "v": 2}
       | {"k": "source", "source": source, "map": mapping}
source = {"k": "reading", "dev", "reading"} | {"k": "time", "part": "hour" |
         "weekday" | "month"} | {"k": "history", "dev", "reading", "func",
         "hours"} | {"k": "input", "name"} | {"k": "value", "name"}
mapping = {"mode": "direct"} | {"mode": "per", "v": 0.2}
        | {"mode": "steps", "steps": [{"from", "to", "v"}], "else": v}
        | {"mode": "values", "values": [{"value", "v"}], "else": v}
        | {"mode": "linear", "points": [[x, y], ...]}

Factors ("mul") are written in percent. fhempy computes the values and
writes them as readings of the editor device, rules use them like any
reading, e.g. [automations:Kochzeit_s] in wait.
"""

import math
import re

from . import evaluate

UNIT_SECONDS = {"s": 1, "min": 60, "h": 3600}
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class Unknown(Exception):
    """a source has no value"""


def reading_name(title):
    """reading name of a value from its title: Kochzeit Eier -> Kochzeit_Eier"""
    text = (
        str(title or "")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ß", "ss")
    )
    text = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")
    if not text or not text[0].isalpha():
        text = "Wert_" + text
    return text[:40]


def to_number(value):
    number = evaluate.to_number(value)
    if number is None:
        raise Unknown(value)
    return number


def source_value(source, ctx):
    """raw value of a source (number or text)"""
    kind = source.get("k")
    if kind == "reading":
        value = ctx["reading"](source.get("dev", ""), source.get("reading") or "state")
        if value is None:
            raise Unknown(f"{source.get('dev')}:{source.get('reading')}")
        return value
    if kind == "time":
        now = ctx["now"]
        part = source.get("part", "hour")
        if part == "hour":
            return now.hour + now.minute / 60
        if part == "weekday":
            # 0 Sunday like DOIF, 7 weekend handled in steps
            return (now.weekday() + 1) % 7
        if part == "month":
            return now.month
        raise Unknown(part)
    if kind == "history":
        value = ctx["history"](
            source.get("dev", ""),
            source.get("reading") or "state",
            source.get("func", "sum"),
            float(source.get("hours") or 24),
        )
        if value is None:
            raise Unknown("history")
        return value
    if kind == "input":
        value = ctx["input"](source.get("name", ""))
        if value is None:
            raise Unknown(source.get("name"))
        return value
    if kind == "value":
        value = ctx["value"](source.get("name", ""))
        if value is None:
            raise Unknown(source.get("name"))
        return value
    raise Unknown(kind)


def _in_step(x, step):
    low = step.get("from")
    high = step.get("to")
    low = None if low in (None, "") else float(low)
    high = None if high in (None, "") else float(high)
    if low is not None and high is not None and low > high:
        # over midnight, e.g. 22 to 6 o'clock
        return x >= low or x < high
    return (low is None or x >= low) and (high is None or x < high)


def map_value(mapping, raw):
    mode = mapping.get("mode", "direct")
    if mode == "direct":
        return to_number(raw)
    if mode == "per":
        return to_number(raw) * float(mapping.get("v") or 0)
    if mode == "values":
        text = str(raw).strip().lower()
        for entry in mapping.get("values", []):
            if str(entry.get("value", "")).strip().lower() == text:
                return float(entry.get("v") or 0)
        if mapping.get("else") not in (None, ""):
            return float(mapping["else"])
        raise Unknown(raw)
    if mode == "steps":
        x = to_number(raw)
        for step in mapping.get("steps", []):
            if _in_step(x, step):
                return float(step.get("v") or 0)
        if mapping.get("else") not in (None, ""):
            return float(mapping["else"])
        raise Unknown(raw)
    if mode == "linear":
        x = to_number(raw)
        points = sorted(
            (float(p[0]), float(p[1])) for p in mapping.get("points", []) if len(p) == 2
        )
        if not points:
            raise Unknown("no points")
        if x <= points[0][0]:
            return points[0][1]
        if x >= points[-1][0]:
            return points[-1][1]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            if x1 <= x <= x2:
                if x2 == x1:
                    return y2
                return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    raise Unknown(mode)


def amount_value(amount, ctx):
    if amount.get("k") == "fixed":
        return float(amount.get("v") or 0), None
    raw = source_value(amount.get("source", {}), ctx)
    return map_value(amount.get("map", {"mode": "direct"}), raw), raw


def compute(value, ctx):
    """result and receipt steps [{op, amount, raw, result, skipped}]"""
    result = None
    steps = []
    for row in value.get("rows", []):
        op = row.get("op", "start")
        step = {"op": op}
        if row.get("only_if") and ctx.get("condition"):
            active = ctx["condition"](row["only_if"])
            if not active:
                step["skipped"] = True
                step["result"] = result
                steps.append(step)
                continue
        try:
            amount, raw = amount_value(row.get("amount", {}), ctx)
        except (Unknown, ValueError, TypeError) as exc:
            step["error"] = str(exc) or "unknown"
            steps.append(step)
            return None, steps
        step["amount"] = amount
        step["raw"] = raw
        if op == "start" or op == "set" or result is None:
            result = amount if op != "mul" else 0.0
        elif op == "mul":
            result = result * amount / 100
        elif op == "add":
            result = result + amount
        elif op == "sub":
            result = result - amount
        step["result"] = result
        steps.append(step)
    if result is None:
        return None, steps
    if value.get("min") not in (None, ""):
        result = max(result, float(value["min"]))
    if value.get("max") not in (None, ""):
        result = min(result, float(value["max"]))
    if value.get("round") not in (None, "", 0, "0"):
        step = float(value["round"])
        if step > 0:
            result = math.floor(result / step + 0.5) * step
    return result, steps


def format_number(number):
    if number is None:
        return ""
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.2f}".rstrip("0").rstrip(".")


def readings_of(value, result):
    """readings to write: {reading: text}"""
    name = value.get("name") or reading_name(value.get("title"))
    if result is None:
        return {name: "unknown"}
    readings = {name: format_number(result)}
    factor = UNIT_SECONDS.get(value.get("unit", ""))
    if factor and factor != 1:
        readings[name + "_s"] = str(int(round(result * factor)))
    return readings


def sources_of(value):
    """(device, reading) pairs a value depends on"""
    pairs = set()
    for row in value.get("rows", []):
        source = row.get("amount", {}).get("source", {})
        if source.get("k") in ("reading", "history"):
            pairs.add((source.get("dev", ""), source.get("reading") or "state"))
    return pairs


def depends_on_time(value):
    return any(
        row.get("amount", {}).get("source", {}).get("k") in ("time", "history")
        for row in value.get("rows", [])
    )
