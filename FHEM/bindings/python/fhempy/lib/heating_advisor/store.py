"""SQLite storage: measurements per room on a 15 minute grid, the hourly
weather and learned values. Blocking, call with utils.run_blocking."""

import json
import os
import sqlite3
import threading

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS grid ("
    " room TEXT NOT NULL, ts INTEGER NOT NULL, y REAL, setp REAL, valve REAL,"
    " window REAL, detected INTEGER, surface REAL, present REAL, ta REAL,"
    " PRIMARY KEY (room, ts))",
    "CREATE TABLE IF NOT EXISTS weather ("
    " ts INTEGER PRIMARY KEY, temp REAL, direct REAL, diffuse REAL)",
    "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)",
)
GRID_COLUMNS = (
    "ts",
    "y",
    "setp",
    "valve",
    "window",
    "detected",
    "surface",
    "present",
    "ta",
)


class Store:
    def __init__(self, path):
        self.path = path
        self._db = None
        self._lock = threading.Lock()

    def open(self):
        if self.path != ":memory:":
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        with self._lock:
            for statement in SCHEMA:
                self._db.execute(statement)
            self._db.commit()

    def close(self):
        with self._lock:
            if self._db is not None:
                self._db.close()
                self._db = None

    def add_grid(self, room, rows):
        """rows: dicts with the GRID_COLUMNS, existing slots are replaced"""
        with self._lock:
            self._db.executemany(
                "INSERT OR REPLACE INTO grid (room, ts, y, setp, valve, window,"
                " detected, surface, present, ta) VALUES (?,?,?,?,?,?,?,?,?,?)",
                [(room,) + tuple(row.get(c) for c in GRID_COLUMNS) for row in rows],
            )
            self._db.commit()

    def grid(self, room, start, end=None):
        with self._lock:
            cur = self._db.execute(
                "SELECT ts, y, setp, valve, window, detected, surface, present, ta"
                " FROM grid WHERE room = ? AND ts >= ? AND ts < ? ORDER BY ts",
                (room, int(start), int(end if end is not None else 2**62)),
            )
            return [dict(zip(GRID_COLUMNS, row)) for row in cur.fetchall()]

    def first_ts(self, room):
        with self._lock:
            row = self._db.execute(
                "SELECT MIN(ts) FROM grid WHERE room = ?", (room,)
            ).fetchone()
            return row[0] if row else None

    def add_weather(self, rows):
        with self._lock:
            self._db.executemany(
                "INSERT OR REPLACE INTO weather (ts, temp, direct, diffuse)"
                " VALUES (?,?,?,?)",
                rows,
            )
            self._db.commit()

    def weather(self, start):
        with self._lock:
            return self._db.execute(
                "SELECT ts, temp, direct, diffuse FROM weather WHERE ts >= ?"
                " ORDER BY ts",
                (int(start),),
            ).fetchall()

    def get(self, key, default=None):
        with self._lock:
            row = self._db.execute(
                "SELECT value FROM kv WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except ValueError:
            return default

    def put(self, key, value):
        with self._lock:
            self._db.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
            self._db.commit()

    def cleanup(self, before):
        with self._lock:
            self._db.execute("DELETE FROM grid WHERE ts < ?", (int(before),))
            self._db.execute("DELETE FROM weather WHERE ts < ?", (int(before),))
            self._db.commit()
