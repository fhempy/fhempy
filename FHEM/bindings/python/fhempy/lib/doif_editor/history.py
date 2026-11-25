"""Read access to the database of the timeline module: past events for the
simulation, "Why?" and values over a period (sum, minimum, ... of the last
hours). All functions are blocking, call them with utils.run_blocking."""

import os
import sqlite3
import threading
import time

FUNCTIONS = ("sum", "min", "max", "avg", "count", "since")


class History:
    def __init__(self, path):
        self.path = path
        self._db = None
        self._lock = threading.Lock()

    def available(self):
        return bool(self.path) and os.path.exists(self.path)

    def _conn(self):
        if self._db is None:
            self._db = sqlite3.connect(
                f"file:{self.path}?mode=ro", uri=True, check_same_thread=False
            )
        return self._db

    def close(self):
        with self._lock:
            if self._db is not None:
                self._db.close()
                self._db = None

    def events(self, pairs, start, end, limit=200000):
        """events of the (device, reading) pairs, oldest first. A pair with
        reading None means all readings of the device"""
        devices = sorted({device for device, _ in pairs})
        if not devices:
            return []
        wanted = set(pairs)
        rows = []
        with self._lock:
            db = self._conn()
            for device in devices:
                rows.extend(
                    db.execute(
                        "SELECT ts, device, reading, value FROM events"
                        " WHERE device = ? AND ts >= ? AND ts < ?"
                        " ORDER BY ts LIMIT ?",
                        (device, start, end, limit),
                    ).fetchall()
                )
        rows = [
            row
            for row in rows
            if (row[1], row[2]) in wanted or (row[1], None) in wanted
        ]
        rows.sort(key=lambda row: row[0])
        return rows

    def values_before(self, pairs, start, days=31):
        """last value of each pair before start: {(device, reading): (ts, value)}"""
        result = {}
        with self._lock:
            db = self._conn()
            for device, reading in sorted(set(pairs), key=str):
                if reading is None:
                    continue
                row = db.execute(
                    "SELECT ts, value FROM events WHERE device = ? AND reading = ?"
                    " AND ts < ? AND ts >= ? ORDER BY ts DESC LIMIT 1",
                    (device, reading, start, start - days * 86400),
                ).fetchone()
                if row is None:
                    row = db.execute(
                        "SELECT hour, COALESCE(last, sum / n) FROM hourly"
                        " WHERE device = ? AND reading = ? AND hour < ?"
                        " AND hour >= ? ORDER BY hour DESC LIMIT 1",
                        (device, reading, int(start), int(start) - days * 86400),
                    ).fetchone()
                if row is not None:
                    result[(device, reading)] = (row[0], str(row[1]))
        return result

    def aggregate(self, device, reading, function, hours, now=None):
        """value of device:reading over the last hours: sum, min, max, avg of
        the numbers, count of the events or since (seconds since the last
        change). None if there are no data"""
        now = now or time.time()
        start = now - hours * 3600
        with self._lock:
            db = self._conn()
            if function == "count":
                row = db.execute(
                    "SELECT COUNT(*) FROM events WHERE device = ? AND reading = ?"
                    " AND ts >= ? AND ts < ?",
                    (device, reading, start, now),
                ).fetchone()
                return float(row[0])
            if function == "since":
                row = db.execute(
                    "SELECT MAX(ts) FROM events WHERE device = ? AND reading = ?"
                    " AND ts < ?",
                    (device, reading, now),
                ).fetchone()
                return None if row[0] is None else now - row[0]
            column = {
                "sum": "SUM(sum)",
                "min": "MIN(min)",
                "max": "MAX(max)",
                "avg": "SUM(sum) / SUM(n)",
            }[function]
            row = db.execute(
                f"SELECT {column}, COUNT(*) FROM hourly WHERE device = ?"
                " AND reading = ? AND hour >= ? AND hour < ?",
                (device, reading, int(start // 3600 * 3600), now),
            ).fetchone()
            if not row[1]:
                return None
            return float(row[0]) if row[0] is not None else None

    def recent_values(self, device, reading, days=30, limit=12):
        """distinct values of the last days, most frequent first"""
        with self._lock:
            db = self._conn()
            rows = db.execute(
                "SELECT value, COUNT(*) AS n FROM events WHERE device = ?"
                " AND reading = ? AND ts >= ? GROUP BY value ORDER BY n DESC"
                " LIMIT ?",
                (device, reading, time.time() - days * 86400, limit),
            ).fetchall()
        return [row[0] for row in rows]

    def range_of(self, device, reading, days=7):
        """minimum and maximum of the last days"""
        with self._lock:
            db = self._conn()
            row = db.execute(
                "SELECT MIN(min), MAX(max) FROM hourly WHERE device = ?"
                " AND reading = ? AND hour >= ?",
                (device, reading, int(time.time() - days * 86400)),
            ).fetchone()
        if row is None or row[0] is None:
            return None
        return row[0], row[1]
