"""SQLite storage of the timeline. All methods are blocking, call them with
utils.run_blocking. One connection, used by one thread at a time."""

import datetime
import os
import sqlite3
import threading
import time

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS events ("
    " ts REAL NOT NULL, device TEXT NOT NULL, reading TEXT NOT NULL,"
    " value TEXT NOT NULL, layer TEXT NOT NULL, category TEXT NOT NULL)",
    "CREATE INDEX IF NOT EXISTS events_layer_ts ON events (layer, ts)",
    "CREATE INDEX IF NOT EXISTS events_device_ts ON events (device, ts)",
    # min/max/average per hour of numeric readings
    "CREATE TABLE IF NOT EXISTS hourly ("
    " hour INTEGER NOT NULL, device TEXT NOT NULL, reading TEXT NOT NULL,"
    " category TEXT NOT NULL, min REAL, max REAL, sum REAL, n INTEGER,"
    " PRIMARY KEY (device, reading, hour))",
    "CREATE INDEX IF NOT EXISTS hourly_hour ON hourly (hour)",
    # number of hidden events per day, including the ones FHEM only counted
    "CREATE TABLE IF NOT EXISTS daily (day TEXT PRIMARY KEY, hidden INTEGER)",
    # nobody at home, end NULL while still absent
    "CREATE TABLE IF NOT EXISTS absences (start REAL PRIMARY KEY, end REAL)",
    # readings which became tech because they change too often
    "CREATE TABLE IF NOT EXISTS frequent ("
    " device TEXT NOT NULL, reading TEXT NOT NULL, PRIMARY KEY (device, reading))",
)


def day_of(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def day_start(day):
    return datetime.datetime.strptime(day, "%Y-%m-%d").timestamp()


class Store:
    def __init__(self, path):
        self.path = path
        self._db = None
        self._lock = threading.Lock()

    def open(self):
        if self.path != ":memory:":
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with self._lock:
            self._db = sqlite3.connect(self.path, check_same_thread=False)
            self._db.execute("PRAGMA journal_mode=WAL")
            # few writes on the SD card, a crash loses at most the last seconds
            self._db.execute("PRAGMA synchronous=NORMAL")
            for statement in SCHEMA:
                self._db.execute(statement)
            self._db.commit()

    def close(self):
        with self._lock:
            if self._db is not None:
                self._db.close()
                self._db = None

    def add(self, events, hourly, hidden):
        """events: (ts, device, reading, value, layer, category)
        hourly: (hour, device, reading) -> [category, min, max, sum, n]
        hidden: day -> number of hidden events"""
        with self._lock:
            db = self._db
            db.executemany("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)", events)
            db.executemany(
                "INSERT INTO hourly VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                " ON CONFLICT (device, reading, hour) DO UPDATE SET"
                " min = MIN(min, excluded.min), max = MAX(max, excluded.max),"
                " sum = sum + excluded.sum, n = n + excluded.n",
                [
                    (hour, device, reading, *values)
                    for (hour, device, reading), values in hourly.items()
                ],
            )
            db.executemany(
                "INSERT INTO daily VALUES (?, ?) ON CONFLICT (day)"
                " DO UPDATE SET hidden = hidden + excluded.hidden",
                list(hidden.items()),
            )
            db.commit()

    def story(self, start, end):
        with self._lock:
            return self._db.execute(
                "SELECT ts, device, reading, value, category FROM events"
                " WHERE layer = 'story' AND ts >= ? AND ts < ? ORDER BY ts",
                (start, end),
            ).fetchall()

    def device_story(self, device, start, end):
        with self._lock:
            return self._db.execute(
                "SELECT ts, device, reading, value, category FROM events"
                " WHERE layer = 'story' AND device = ? AND ts >= ? AND ts < ?"
                " ORDER BY ts",
                (device, start, end),
            ).fetchall()

    def device_hourly(self, device, start, end):
        with self._lock:
            return self._db.execute(
                "SELECT hour, device, reading, category, min, max, sum, n"
                " FROM hourly WHERE device = ? AND hour >= ? AND hour < ?"
                " ORDER BY hour",
                (device, int(start), int(end)),
            ).fetchall()

    def details(self, start, end, limit=500):
        with self._lock:
            return self._db.execute(
                "SELECT ts, device, reading, value, layer FROM events"
                " WHERE layer != 'story' AND ts >= ? AND ts < ?"
                " ORDER BY ts DESC LIMIT ?",
                (start, end, limit),
            ).fetchall()

    def hourly(self, start, end):
        with self._lock:
            return self._db.execute(
                "SELECT hour, device, reading, category, min, max, sum, n"
                " FROM hourly WHERE hour >= ? AND hour < ? ORDER BY hour",
                (int(start), int(end)),
            ).fetchall()

    def hidden(self, first_day, last_day):
        with self._lock:
            return dict(
                self._db.execute(
                    "SELECT day, hidden FROM daily WHERE day >= ? AND day <= ?",
                    (first_day, last_day),
                ).fetchall()
            )

    def absence_changed(self, ts, absent):
        with self._lock:
            open_absence = self._db.execute(
                "SELECT start FROM absences WHERE end IS NULL"
            ).fetchone()
            if absent and open_absence is None:
                self._db.execute("INSERT INTO absences VALUES (?, NULL)", (ts,))
            elif not absent and open_absence is not None:
                self._db.execute(
                    "UPDATE absences SET end = ? WHERE start = ?",
                    (ts, open_absence[0]),
                )
            self._db.commit()

    def absences(self, start, end):
        with self._lock:
            return self._db.execute(
                "SELECT start, end FROM absences WHERE start < ?"
                " AND (end IS NULL OR end > ?) ORDER BY start",
                (end, start),
            ).fetchall()

    def long_absences(self, min_seconds, limit=10):
        now = time.time()
        with self._lock:
            return self._db.execute(
                "SELECT start, end FROM absences"
                " WHERE COALESCE(end, ?) - start >= ? ORDER BY start DESC LIMIT ?",
                (now, min_seconds, limit),
            ).fetchall()

    def frequent(self):
        with self._lock:
            return set(self._db.execute("SELECT device, reading FROM frequent"))

    def add_frequent(self, device, reading):
        with self._lock:
            self._db.execute(
                "INSERT OR IGNORE INTO frequent VALUES (?, ?)", (device, reading)
            )
            self._db.commit()

    def forget_frequent(self, device, reading):
        with self._lock:
            self._db.execute(
                "DELETE FROM frequent WHERE device = ? AND reading = ?",
                (device, reading),
            )
            self._db.commit()

    def first_ts(self):
        with self._lock:
            row = self._db.execute("SELECT MIN(ts) FROM events").fetchone()
            return row[0] if row else None

    def cleanup(self, details_days, story_days):
        now = time.time()
        details_end = now - details_days * 86400
        story_end = now - story_days * 86400
        with self._lock:
            db = self._db
            db.execute(
                "DELETE FROM events WHERE layer != 'story' AND ts < ?", (details_end,)
            )
            db.execute("DELETE FROM events WHERE ts < ?", (story_end,))
            db.execute("DELETE FROM hourly WHERE hour < ?", (int(story_end),))
            db.execute("DELETE FROM daily WHERE day < ?", (day_of(story_end),))
            db.execute(
                "DELETE FROM absences WHERE end IS NOT NULL AND end < ?",
                (story_end,),
            )
            db.commit()

    def size(self):
        try:
            return sum(
                os.path.getsize(self.path + suffix)
                for suffix in ("", "-wal")
                if os.path.exists(self.path + suffix)
            )
        except OSError:
            return 0
