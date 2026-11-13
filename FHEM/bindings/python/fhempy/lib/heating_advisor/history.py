"""Import of past measurements from the fhempy timeline (hourly values and
events), so the advisor has something to learn from right away.
Blocking, call with utils.run_blocking."""

import os
import sqlite3

from . import discover

SLOT = 900
ABSENT = "absent"


def timeline_db(name, cwd=None):
    return os.path.join(cwd or os.getcwd(), ".fhempy", "timeline", f"{name}.db")


def _hourly(db, device, reading, start):
    rows = db.execute(
        "SELECT hour, sum / n, last FROM hourly WHERE device = ? AND reading = ?"
        " AND hour >= ? AND n > 0 ORDER BY hour",
        (device, reading, int(start)),
    ).fetchall()
    return {int(hour): (avg, last) for hour, avg, last in rows}


def _events(db, device, reading, start):
    return db.execute(
        "SELECT ts, value FROM events WHERE device = ? AND reading = ?"
        " AND ts >= ? ORDER BY ts",
        (device, reading, start - 31 * 86400),
    ).fetchall()


def _absences(db, start):
    try:
        return db.execute(
            "SELECT start, end FROM absences WHERE end IS NULL OR end >= ?",
            (start,),
        ).fetchall()
    except sqlite3.Error:
        return []


def _mean_series(series_list):
    """{hour: avg} of several sensors -> mean per hour"""
    result = {}
    for series in series_list:
        for hour, (avg, _) in series.items():
            if avg is not None:
                result.setdefault(hour, []).append(avg)
    return {hour: sum(v) / len(v) for hour, v in result.items()}


def _state_at(changes, ts):
    """last value of sorted (ts, value) changes at ts"""
    value = None
    for when, state in changes:
        if when > ts:
            break
        value = state
    return value


def import_rooms(path, found, start, end):
    """grid rows per room {room: [rows]} from a timeline database"""
    if not os.path.exists(path):
        return {}
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return _import(db, found, start, end)
    finally:
        db.close()


def _import(db, found, start, end):
    outdoor = {}
    if found.get("outdoor"):
        outdoor = {
            h: avg for h, (avg, _) in _hourly(db, *found["outdoor"], start).items()
        }
    absences = _absences(db, start)
    result = {}
    for room, entry in found["rooms"].items():
        sensors = [_hourly(db, d, r, start) for d, r in entry["sensors"]]
        temps = _mean_series(sensors)
        if not temps:
            temps = _mean_series(
                [
                    _hourly(db, t["device"], t["temp"], start)
                    for t in entry["thermostats"]
                    if t["temp"]
                ]
            )
        if not temps:
            continue
        targets = [
            _hourly(db, t["device"], t["target"], start) for t in entry["thermostats"]
        ]
        valves = _mean_series(
            [
                _hourly(db, t["device"], t["valve"], start)
                for t in entry["thermostats"]
                if t["valve"]
            ]
        )
        surface = _mean_series([_hourly(db, d, r, start) for d, r in entry["surface"]])
        contacts = [
            [
                (ts, discover.contact_open({"readings": {r: v}}, r))
                for ts, v in _events(db, d, r, start)
            ]
            for d, r in entry["contacts"]
        ]
        target_changes = [
            [
                (ts, discover.number(v))
                for ts, v in _events(db, t["device"], t["target"], start)
            ]
            for t in entry["thermostats"]
        ]
        hours = sorted(temps)
        rows = []
        for i, hour in enumerate(hours):
            nxt = temps.get(hour + 3600)
            for q in range(4):
                ts = hour + q * SLOT
                if ts < start or ts >= end:
                    continue
                f = (q * SLOT + SLOT / 2 - 1800) / 3600
                y = temps[hour]
                if nxt is not None and f > 0:
                    y += (nxt - y) * f
                prev = temps.get(hour - 3600)
                if prev is not None and f < 0:
                    y += (y - prev) * f
                setp = [_state_at(changes, ts + SLOT / 2) for changes in target_changes]
                setp = [s for s in setp if s is not None]
                if not setp:
                    setp = [t[hour][1] for t in targets if hour in t]
                opens = [_state_at(c, ts + SLOT / 2) for c in contacts]
                opens = [o for o in opens if o is not None]
                absent = any(a <= ts and (b is None or b > ts) for a, b in absences)
                rows.append(
                    {
                        "ts": ts,
                        "y": round(y, 2),
                        "setp": max(setp) if setp else None,
                        "valve": min(max(valves[hour] / 100, 0.0), 1.0)
                        if hour in valves
                        else None,
                        "window": (1.0 if any(opens) else 0.0) if opens else None,
                        "detected": 0,
                        "surface": surface.get(hour),
                        "present": (0.0 if absent else 1.0) if absences else None,
                        "ta": outdoor.get(hour),
                    }
                )
        result[room] = rows
    return result
