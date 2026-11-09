"""Heating advisor: learns how the house stores and loses heat and tells
from how many hours or days of absence a heating setback pays off.

- discover.py finds the room temperatures, thermostats, window contacts,
  the outdoor temperature and the residents
- the module samples them every minute into a 15 minute grid (store.py)
- advisor.py/model.py fit a grey-box model (air + walls) per room every
  night, a Kalman filter follows the current state live
- planner.py compares "keep heating" with "set back and heat up again"
  until the felt temperature (air AND walls) is comfortable again
- the module can also do the setback: set absence ... apply
"""

import asyncio
import datetime
import functools
import json
import os
import re
import statistics
import time

from .. import fhem, generic, utils
from . import advisor, discover, history, model, planner, render, weather
from .store import Store

SAMPLE_INTERVAL = 60
DISCOVER_INTERVAL = 600
WEATHER_INTERVAL = 3600
PLAN_INTERVAL = 3600
FIT_HOUR = 3
KEEP_DAYS = 400
SLOT = advisor.SLOT
STEPS_PER_HOUR = planner.STEPS_PER_HOUR
FORECAST_HOURS = (1, 2, 3, 6, 12, 24, 48)
FROST = 5.0
READING_PATTERN = (
    "^("
    + "|".join(
        re.escape(r)
        for r in discover.TEMP_READINGS
        + discover.TARGET_READINGS
        + discover.VALVE_READINGS
        + discover.THERMOSTAT_WINDOW_READINGS
        + ("contact", "state", "humidity")
    )
    + ")$"
)
ROOM_READING = re.compile(r"[^A-Za-z0-9_\-.]")

ATTRS = {
    "rooms": {
        "default": "",
        "help": "Rooms to use, comma separated (default: all rooms with a "
        "temperature).",
    },
    "exclude_devices": {
        "default": "",
        "help": "Devices which are not used, comma separated.",
    },
    "extra_devices": {
        "default": "",
        "help": "Devices which are used although they don't look like a "
        "room thermometer, thermostat or window contact (e.g. no room set "
        "in FHEM is fine if the device has a room attribute).",
    },
    "outdoor_sensor": {
        "default": "",
        "help": "device or device:reading of the outdoor temperature "
        "(default: found by name, otherwise Open-Meteo).",
    },
    "heating_type": {
        "default": "auto",
        "options": "auto,heatpump,gas,oil,electric,district",
        "help": "Heating, for the efficiency (heat pumps need much more "
        "energy when heating up fast).",
    },
    "floor_heating": {
        "default": "auto",
        "help": "auto (by device names), all, none or a comma separated "
        "list of rooms with floor heating.",
    },
    "heating_power_kW": {
        "default": "",
        "help": "Maximum heating power of the house in kW. Without it the "
        "energies (kWh, €) are rough estimates, the percentages and hours "
        "don't need it.",
    },
    "comfort_temp": {
        "default": "",
        "help": "Comfort setpoint (default: the usual setpoint of each thermostat).",
    },
    "setback_temp": {
        "default": "auto",
        "help": "Temperature during a setback, auto tries several and "
        "takes the one which saves most.",
    },
    "min_temp": {
        "default": 12,
        "format": "float",
        "help": "The air never gets colder than this during a setback (mould, frost).",
    },
    "comfort_basis": {
        "default": "operative",
        "options": "operative,air",
        "help": "operative: warm means air AND walls are warm (felt "
        "temperature), air: only the air temperature counts.",
    },
    "max_radiant_asymmetry": {
        "default": 3,
        "format": "float",
        "help": "Maximum difference air minus walls in K when the room "
        "counts as warm again (cold walls feel unpleasant).",
    },
    "price_kWh": {
        "default": "",
        "help": "Price per kWh (final energy) as number or device:reading "
        "(e.g. of a tibber device).",
    },
    "worth_threshold_pct": {
        "default": 5,
        "format": "float",
        "help": "A setback is worth it from this saving in percent.",
    },
    "worth_threshold_kWh": {
        "default": 0.5,
        "format": "float",
        "help": "... and at least this many kWh.",
    },
    "history_days": {
        "default": 60,
        "format": "int",
        "help": "Days of measurements the model learns from.",
    },
}


def room_key(room):
    return ROOM_READING.sub("_", room)


def parse_time(text, now):
    """hours (12, 1.5, 3d), HH:MM (next), YYYY-MM-DD[_HH:MM] -> timestamp"""
    text = str(text).strip()
    match = re.fullmatch(r"(\d+(?:[.,]\d+)?)\s*([hd]?)", text)
    if match:
        value = float(match.group(1).replace(",", "."))
        return now + value * (86400 if match.group(2) == "d" else 3600)
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", text)
    if match:
        base = datetime.datetime.fromtimestamp(now)
        when = base.replace(
            hour=int(match.group(1)),
            minute=int(match.group(2)),
            second=0,
            microsecond=0,
        )
        if when.timestamp() <= now:
            when += datetime.timedelta(days=1)
        return when.timestamp()
    for fmt in ("%Y-%m-%d_%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(text, fmt).timestamp()
        except ValueError:
            continue
    raise ValueError(
        f"unknown time {text}, use e.g. 36h, 3d, 07:30 or 2026-12-27_18:00"
    )


def time_text(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


class heating_advisor(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.store = None
        self.found = {
            "rooms": {},
            "outdoor": None,
            "residents": [],
            "heating_type": None,
            "floor_rooms": set(),
        }
        self.wx = weather.Weather()
        self.lat = 50.11
        self.lon = 8.68
        self.fits = {}
        self.filters = {}
        self.live = {}
        self.view = None
        self._slot = None
        self._samples = {}
        self._stopping = False
        self._ta_bias = 0.0
        self._fitting = False
        self._planning = False
        self._last_plan = 0
        self._last_fit_day = None
        self._fixed_results = {}
        self._plan = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_set_config(
            {
                "absence": {
                    "args": ["until", "apply"],
                    "params": {"apply": {"optional": True}},
                    "help": "Compute an absence from now, until e.g. 36h, 3d, "
                    "07:30 or 2026-12-27_18:00. With <code>apply</code> the "
                    "thermostats are set back and heat up again in time "
                    "(readings plan_*).",
                },
                "heat_up_at": {
                    "args": ["time"],
                    "help": "The house is set back now: start heating up as "
                    "late as possible so it is warm (air and walls) at time, "
                    "e.g. 06:30.",
                },
                "cancel": {
                    "help": "Cancel the running setback, the thermostats go "
                    "back to their comfort setpoints now.",
                },
                "learn_night": {
                    "help": "Learning experiment: set the heating back by 4 K "
                    "tonight (22:00) and heat up again in time for 06:00. "
                    "Helps if the heating never was off so far.",
                },
                "relearn": {
                    "help": "Learn the model of all rooms again now.",
                },
                "rediscover": {
                    "help": "Search the devices again now.",
                },
                "import_history": {
                    "help": "Import the measurements of the last 90 days from "
                    "the fhempy timeline again.",
                },
            }
        )
        await self.set_get_config(
            {
                "forecast": {
                    "args": ["hours", "setpoint"],
                    "params": {"setpoint": {"optional": True}},
                    "help": "Forecast of all rooms as JSON for the next hours, "
                    "heating off or at setpoint (air).",
                },
                "model": {
                    "help": "Learned values of all rooms as JSON.",
                },
            }
        )
        await self.set_attr_config(ATTRS)
        await self.set_icon("temp_temperature")
        await fhem.readingsSingleUpdate(self.hash, "state", "starting", 1)
        self.create_async_task(self.run())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._stopping = True
        await super().Undefine(hash)
        if self.store is not None:
            await utils.run_blocking(functools.partial(self.store.close))

    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return render.page(self.view) + str(detail)

    # --- helpers ---

    def db_path(self):
        return os.path.join(
            os.getcwd(), ".fhempy", "heating_advisor", f"{self.hash['NAME']}.db"
        )

    async def blocking(self, function, *args, **kwargs):
        return await utils.run_blocking(functools.partial(function, *args, **kwargs))

    def heating_type(self):
        if self._attr_heating_type in planner.HEATING_TYPES:
            return self._attr_heating_type
        return self.found.get("heating_type") or "gas"

    def emitter(self, room):
        attr = str(self._attr_floor_heating).strip()
        if attr == "all":
            return "floor"
        if attr in ("none", ""):
            return "radiator"
        if attr == "auto":
            return "floor" if room in self.found.get("floor_rooms", ()) else "radiator"
        rooms = [r.strip() for r in attr.split(",")]
        return "floor" if room in rooms else "radiator"

    def heat_to_mass(self, room):
        return model.HEAT_TO_MASS[self.emitter(room)]

    def setback_attr(self):
        value = discover.number(self._attr_setback_temp)
        return (
            value if str(self._attr_setback_temp).strip() not in ("auto", "") else None
        )

    def has_contacts(self, room):
        entry = self.found["rooms"].get(room, {})
        return bool(entry.get("contacts")) or any(
            t.get("window") for t in entry.get("thermostats", [])
        )

    def scale(self):
        """kWh scale of the nominal model units"""
        kw = discover.number(self._attr_heating_power_kW)
        total = sum(f["params"]["p_heat"] for f in self.fits.values() if f)
        if kw and total > 0:
            return kw * 1000 / total
        return 1.0

    async def price(self):
        text = str(self._attr_price_kWh).strip()
        if not text:
            return None
        value = discover.number(text) if ":" not in text else None
        if value is not None:
            return value
        device, _, reading = text.partition(":")
        return discover.number(await fhem.ReadingsVal(device, reading or "state", ""))

    def normal(self, room):
        comfort = discover.number(self._attr_comfort_temp)
        if comfort:
            return comfort
        return self.live.get(room, {}).get("normal", 21.0)

    # --- start ---

    async def run(self):
        self.store = Store(self.db_path())
        try:
            await self.blocking(self.store.open)
        except Exception as exc:
            self.logger.exception("Failed to open the database")
            await fhem.readingsSingleUpdate(
                self.hash, "state", f"error: {utils.describe_exception(exc)}", 1
            )
            return
        self.fits = await self.blocking(self.store.get, "fits", {}) or {}
        self._plan = await self.blocking(self.store.get, "plan", None)
        self._fixed_results = await self.blocking(self.store.get, "fixed", {}) or {}
        self.lat = (
            discover.number(await fhem.AttrVal("global", "latitude", "")) or 50.11
        )
        self.lon = (
            discover.number(await fhem.AttrVal("global", "longitude", "")) or 8.68
        )
        rows = await self.blocking(self.store.weather, time.time() - KEEP_DAYS * 86400)
        self.wx.add(rows)
        await self.discover()
        await self.update_weather()
        if not await self.blocking(self.store.get, "imported", False):
            await self.import_history()
        await self.init_rooms()
        await fhem.readingsSingleUpdate(self.hash, "state", "learning", 1)
        if self.needs_fit():
            self.create_async_task(self.fit_all())
        else:
            self.create_async_task(self.plan_all())
        self.create_async_task(self.sample_loop())
        self.create_async_task(self.slow_loop())

    def needs_fit(self):
        if not self.fits:
            return True
        updated = min((f or {}).get("updated", 0) for f in self.fits.values())
        return time.time() - updated > 86400 or set(self.fits) != set(
            self.found["rooms"]
        )

    async def discover(self):
        cmd = (
            "my %r; my $re = " + fhem.perlString(READING_PATTERN) + ";"
            " foreach my $d (keys %defs) { my $h = $defs{$d};"
            " next if ($h->{TEMPORARY} || defined($h->{SNIPPET}));"
            " my %rd; foreach my $n (keys %{$h->{READINGS} // {}}) {"
            " next if ($n !~ /$re/);"
            " $rd{$n} = $h->{READINGS}{$n}{VAL} } "
            " $r{$d} = { TYPE => $h->{TYPE}, FHEMPYTYPE => ($h->{FHEMPYTYPE} // ''),"
            " room => AttrVal($d, 'room', ''), alias => AttrVal($d, 'alias', ''),"
            " genericDeviceType => AttrVal($d, 'genericDeviceType', ''),"
            " readings => \\%rd } } to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            infos = json.loads(result)
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read the FHEM devices: {result}")
            return
        self.infos = infos
        exclude = {d.strip() for d in str(self._attr_exclude_devices).split(",")}
        exclude.add(self.hash["NAME"])
        extra = [
            d.strip() for d in str(self._attr_extra_devices).split(",") if d.strip()
        ]
        for device in extra:
            if device in infos and not infos[device].get("room"):
                infos[device]["room"] = "House"
        rooms = [r.strip() for r in str(self._attr_rooms).split(",") if r.strip()]
        found = discover.discover(infos, exclude=exclude, rooms=rooms or None)
        outdoor = str(self._attr_outdoor_sensor).strip()
        if outdoor:
            device, _, reading = outdoor.partition(":")
            found["outdoor"] = (device, reading or "temperature")
        self.found = found
        await self.update_device_readings()

    async def update_device_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "rooms", ",".join(sorted(self.found["rooms"])) or "none"
        )
        outdoor = self.found.get("outdoor")
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "outdoor_source",
            f"{outdoor[0]}:{outdoor[1]}" if outdoor else "Open-Meteo",
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "heating_type", self.heating_type()
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    def devices_view(self):
        result = []
        for room, entry in sorted(self.found["rooms"].items()):
            names = [d for d, _ in entry["sensors"]]
            names += [t["device"] for t in entry["thermostats"]]
            names += [d for d, _ in entry["contacts"] + entry["surface"]]
            result.append((room, list(dict.fromkeys(names))))
        outdoor = self.found.get("outdoor")
        result.append(("Outdoor", [outdoor[0] if outdoor else "Open-Meteo"]))
        return result

    async def update_weather(self, past_days=None):
        last = self.wx.last_ts()
        if past_days is None:
            if last is None or last < time.time() - 80 * 86400:
                past_days = weather.MAX_PAST_DAYS
            else:
                past_days = min(int((time.time() - last) / 86400) + 2, 92)
        try:
            rows = await weather.fetch(self.lat, self.lon, past_days=past_days)
        except Exception as exc:
            self.logger.warning(
                f"Failed to get the weather from Open-Meteo: "
                f"{utils.describe_exception(exc)}"
            )
            return False
        self.wx.add(rows)
        await self.blocking(self.store.add_weather, rows)
        return True

    async def import_history(self):
        timeline = [
            name
            for name, info in getattr(self, "infos", {}).items()
            if info.get("FHEMPYTYPE") == "timeline"
        ]
        imported = 0
        end = advisor.slot_of(time.time())
        start = end - 90 * 86400
        for name in sorted(timeline)[:1]:
            path = history.timeline_db(name)
            try:
                rooms = await self.blocking(
                    history.import_rooms, path, self.found, start, end
                )
            except Exception:
                self.logger.exception("Failed to import the timeline history")
                continue
            for room, rows in rooms.items():
                await self.blocking(self.store.add_grid, room, rows)
                imported += len(rows)
        await self.blocking(self.store.put, "imported", True)
        if imported:
            self.logger.info(
                f"Imported {imported * SLOT / 86400:.0f} room days from the timeline"
            )
        return imported

    async def init_rooms(self):
        """live filters from the stored measurements of the last days"""
        for room in self.found["rooms"]:
            grid = await self.blocking(self.store.grid, room, time.time() - 14 * 86400)
            state = self.live.setdefault(room, {})
            state["normal"] = advisor.normal_setpoint(grid)
            self.restart_filter(room, grid)

    def restart_filter(self, room, grid):
        fit = self.fits.get(room)
        params = fit["params"] if fit else model.default_params()
        filt = model.Filter(model.Discrete(params, self.heat_to_mass(room)))
        rows = advisor.model_rows(
            grid[-96 * 3 :],
            self.wx,
            self.lat,
            self.lon,
            self.has_contacts(room),
            self._ta_bias,
        )
        for row in rows:
            self.filter_step(filt, row)
        self.filters[room] = filt

    def filter_step(self, filt, row):
        if filt.x is None:
            if row.get("y") is not None:
                filt.start(row)
            return None
        known = row.get("h") is not None and row.get("window") is not None
        filt.predict(
            {
                "ta": row["ta"],
                "sun": row["sun"],
                "present": row.get("present"),
                "heat": row["h"] * filt.model.params["p_heat"] if known else None,
                "window": row.get("window") or 0.0,
            }
        )
        if row.get("y") is None:
            return None
        return filt.update(row["y"])

    # --- sampling ---

    async def sample_loop(self):
        while not self._stopping:
            try:
                await self.sample()
                await self.run_plan()
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger.exception("Failed to sample the devices")
            await asyncio.sleep(SAMPLE_INTERVAL)

    async def read_values(self):
        wanted = discover.devices_of(self.found)
        if not wanted:
            return {}
        spec = ",".join(
            f"{fhem.perlString(d)} => [{','.join(fhem.perlString(r) for r in sorted(rs))}]"
            for d, rs in sorted(wanted.items())
        )
        cmd = (
            f"my %w = ({spec}); my %r; foreach my $d (keys %w) {{"
            " next if (!defined($defs{$d})); my %v;"
            " foreach my $n (@{$w{$d}}) { my $x = ReadingsVal($d, $n, undef);"
            " $v{$n} = $x if (defined($x)) } $r{$d} = \\%v } to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            return json.loads(result)
        except (TypeError, ValueError):
            return None

    async def sample(self, now=None):
        now = now or time.time()
        values = await self.read_values()
        if values is None:
            return
        slot = advisor.slot_of(now)
        if self._slot is not None and slot != self._slot:
            await self.finish_slot(self._slot)
        self._slot = slot
        outdoor = self.found.get("outdoor")
        ta = None
        if outdoor:
            ta = discover.number(values.get(outdoor[0], {}).get(outdoor[1]))
        presence = discover.present(values, self.found.get("residents", []))
        for room, entry in self.found["rooms"].items():
            sample = discover.sample_room(entry, values)
            sample["ta"] = ta
            sample["present"] = presence
            self._samples.setdefault(room, []).append(sample)
            if sample["y"] is not None:
                live = self.live.setdefault(room, {})
                live["air"] = sample["y"]
                if sample["setp"] is not None:
                    live["setp"] = sample["setp"]

    @staticmethod
    def aggregate(samples, slot):
        def mean(key):
            values = [s[key] for s in samples if s.get(key) is not None]
            return sum(values) / len(values) if values else None

        def last(key):
            values = [s[key] for s in samples if s.get(key) is not None]
            return values[-1] if values else None

        return {
            "ts": slot,
            "y": mean("y"),
            "setp": last("setp"),
            "valve": mean("valve"),
            "window": mean("window"),
            "detected": 0,
            "surface": mean("surface"),
            "present": mean("present"),
            "ta": mean("ta"),
        }

    async def finish_slot(self, slot):
        samples, self._samples = self._samples, {}
        for room, room_samples in samples.items():
            row = self.aggregate(room_samples, slot)
            filt = self.filters.get(room)
            if filt is not None:
                rows = advisor.model_rows(
                    [row],
                    self.wx,
                    self.lat,
                    self.lon,
                    self.has_contacts(room),
                    self._ta_bias,
                )
                result = self.filter_step(filt, rows[0]) if rows else None
                if result is not None and not self.has_contacts(room):
                    e, s = result
                    if e < -max(0.3, 3 * s**0.5):
                        row["detected"] = 1
                self.live.setdefault(room, {})["detected"] = row["detected"]
            await self.blocking(self.store.add_grid, room, [row])
        await self.update_live_readings()

    async def update_live_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        felts = []
        for room in self.found["rooms"]:
            filt = self.filters.get(room)
            if filt is None or filt.x is None:
                continue
            k = (self.fits.get(room) or {}).get("surface_k") or model.SURFACE_K
            ti, tm = filt.x
            ts = model.surface_temp(ti, tm, k)
            felt = model.operative_temp(ti, tm, k)
            felts.append(felt)
            live = self.live.setdefault(room, {})
            live.update(wall=ts, felt=felt, air_model=ti)
            key = room_key(room)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{key}_wall_temp", round(ts, 1)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{key}_operative_temp", round(felt, 1)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, f"{key}_radiant_asymmetry_K", round(ti - ts, 1)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                f"{key}_window_open_detected",
                "yes" if live.get("detected") else "no",
            )
        if felts:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "operative_temp", round(sum(felts) / len(felts), 1)
            )
        await fhem.readingsEndUpdate(self.hash, 1)

    # --- learning and planning ---

    async def slow_loop(self):
        last_discover = last_weather = time.time()
        while not self._stopping:
            await asyncio.sleep(SAMPLE_INTERVAL)
            now = time.time()
            try:
                if now - last_discover >= DISCOVER_INTERVAL:
                    last_discover = now
                    await self.discover()
                if now - last_weather >= WEATHER_INTERVAL:
                    last_weather = now
                    await self.update_weather()
                today = datetime.date.today().isoformat()
                if (
                    datetime.datetime.now().hour == FIT_HOUR
                    and self._last_fit_day != today
                ):
                    self._last_fit_day = today
                    await self.blocking(self.store.cleanup, now - KEEP_DAYS * 86400)
                    await self.fit_all()
                elif now - self._last_plan >= PLAN_INTERVAL:
                    await self.plan_all()
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger.exception("Failed to update the heating advisor")

    async def room_rows(self, room, days=None):
        days = days or self._attr_history_days
        grid = await self.blocking(self.store.grid, room, time.time() - days * 86400)
        return grid, advisor.model_rows(
            grid,
            self.wx,
            self.lat,
            self.lon,
            self.has_contacts(room),
            self._ta_bias,
        )

    async def fit_all(self):
        if self._fitting:
            return
        self._fitting = True
        try:
            outdoor_grid = []
            for room in self.found["rooms"]:
                grid, rows = await self.room_rows(room)
                if self.found.get("outdoor"):
                    outdoor_grid = grid
                self.live.setdefault(room, {})["normal"] = advisor.normal_setpoint(
                    grid[-96 * 14 :]
                )
                if len([r for r in rows if r.get("y") is not None]) < 96:
                    continue
                old = self.fits.get(room)
                result = await self.blocking(
                    advisor.fit_room, rows, self.heat_to_mass(room), old
                )
                result["updated"] = time.time()
                self.fits[room] = result
                self.restart_filter(room, grid)
                await asyncio.sleep(0)
            if outdoor_grid:
                self._ta_bias = advisor.ta_bias(outdoor_grid, self.wx)
            for room in list(self.fits):
                if room not in self.found["rooms"]:
                    del self.fits[room]
            await self.blocking(self.store.put, "fits", self.fits)
            await self.update_model_readings()
            await self.compute_fixed()
        finally:
            self._fitting = False
        await self.plan_all()

    async def update_model_readings(self):
        await fhem.readingsBeginUpdate(self.hash)
        scale = self.scale()
        states = []
        loss = storage = 0.0
        errors = []
        for room, fit in self.fits.items():
            if not fit:
                continue
            params = fit["params"]
            key = room_key(room)
            state = advisor.state_of(fit)
            states.append(state)
            air_h, mass_h = advisor.time_constants_h(params)
            room_loss = advisor.heat_loss_w_per_k(params) * scale
            loss += room_loss
            storage += advisor.storage_j_per_k(params) * scale
            if fit.get("rmse") is not None:
                errors.append(fit["rmse"])
            for name, value in (
                ("model_state", state),
                (
                    "model_quality",
                    f"±{fit['rmse']:.2f} K" if fit.get("rmse") is not None else "-",
                ),
                ("heat_loss_W_per_K", round(room_loss)),
                ("time_constant_air_h", round(air_h, 1)),
                ("time_constant_mass_h", round(mass_h)),
                (
                    "solar_gain_factor_m2",
                    round((params["g_e"] + params["g_s"] + params["g_w"]) * scale, 1),
                ),
                ("window_cost_W_per_K", round(params["h_win"] * scale)),
            ):
                await fhem.readingsBulkUpdateIfChanged(
                    self.hash, f"{key}_{name}", value
                )
        if states:
            order = ("learning", "ready", "good")
            house_state = min(states, key=order.index)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "model_state", house_state
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "model_quality",
                f"±{statistics.mean(errors):.2f} K" if errors else "-",
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "heat_loss_W_per_K", round(loss)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "storage_kWh_per_K", round(storage / 3.6e6, 1)
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "energy_basis",
                "heating_power_kW"
                if discover.number(self._attr_heating_power_kW)
                else "estimate",
            )
            await fhem.readingsBulkUpdate(
                self.hash, "model_updated", time_text(time.time())
            )
        await fhem.readingsEndUpdate(self.hash, 1)

    def rooms_for_planning(self, steady_ta=None):
        rooms = []
        for room in self.found["rooms"]:
            fit = self.fits.get(room)
            if not fit:
                continue
            params = fit["params"]
            k = fit.get("surface_k") or model.SURFACE_K
            r = planner.Room(
                room,
                params,
                self.heat_to_mass(room),
                k,
                None,
                self.normal(room),
                self.emitter(room),
            )
            if steady_ta is not None:
                r.x0 = planner.steady_state(r, steady_ta)
            else:
                filt = self.filters.get(room)
                if filt is None or filt.x is None:
                    continue
                r.x0 = filt.x
            rooms.append(r)
        return rooms

    def forecast_inputs(self, steps, start=None):
        start = start or advisor.slot_of(time.time())
        inputs = []
        last = None
        for i in range(steps):
            ts = start + i * SLOT + SLOT / 2
            w = self.wx.at(ts) or last
            if w is None:
                w = (5.0, 0.0, 0.0)
            last = w
            inputs.append(
                {
                    "ta": w[0] + self._ta_bias,
                    "sun": weather.sun_at(ts, self.lat, self.lon, w[1], w[2]),
                    "present": 0.0,
                    "window": 0.0,
                }
            )
        return inputs

    def forecast_for(self, steps):
        """weather of the next steps, repeating the last days of the
        forecast for longer absences"""
        known = self.forecast_inputs(min(steps, 7 * 96))
        while len(known) < steps:
            known += known[-96:]
        return known[:steps]

    async def compute_fixed(self):
        """break-even at constant outdoor temperatures, only changes with
        the model"""
        results = {}
        for ta in (0.0, -10.0, 10.0):
            rooms = self.rooms_for_planning(steady_ta=ta)
            if not rooms:
                continue
            res = await self.blocking(
                planner.savings_by_duration,
                rooms,
                lambda n, ta=ta: planner.constant_inputs(ta, n),
                self.setback_attr(),
                self._attr_min_temp,
                self.heating_type(),
                self.scale(),
                self._attr_comfort_basis,
                self._attr_max_radiant_asymmetry,
            )
            results[str(ta)] = planner.worth_from(
                res, self._attr_worth_threshold_pct, self._attr_worth_threshold_kWh
            )
            # reheat after a long setback at this temperature
            if ta == 0.0:
                reheat = {}
                for r in rooms:
                    setback = self.setback_attr() or max(
                        self._attr_min_temp, r.normal - 4
                    )
                    reheat[r.name] = await self.blocking(
                        planner.reheat_hours,
                        r,
                        ta,
                        setback,
                        self.heating_type(),
                        self._attr_comfort_basis,
                        self._attr_max_radiant_asymmetry,
                    )
                results["reheat"] = reheat
        self._fixed_results = results
        await self.blocking(self.store.put, "fixed", results)

    async def plan_all(self):
        if self._planning:
            return
        self._planning = True
        self._last_plan = time.time()
        try:
            await self._plan_all()
        finally:
            self._planning = False

    async def _plan_all(self):
        rooms = self.rooms_for_planning()
        if not rooms:
            self.view = self.empty_view()
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "learning: no measurements yet"
                if self.found["rooms"]
                else "no room temperatures found",
                1,
            )
            return
        heating_type = self.heating_type()
        scale = self.scale()
        results = await self.blocking(
            planner.savings_by_duration,
            rooms,
            self.forecast_for,
            self.setback_attr(),
            self._attr_min_temp,
            heating_type,
            scale,
            self._attr_comfort_basis,
            self._attr_max_radiant_asymmetry,
        )
        thr_pct, thr_kwh = (
            self._attr_worth_threshold_pct,
            self._attr_worth_threshold_kWh,
        )
        worth = planner.worth_from(results, thr_pct, thr_kwh)
        steps = 7 * 24 * STEPS_PER_HOUR
        inputs = self.forecast_inputs(steps)
        forecasts = {}
        for room in rooms:
            forecasts[room.name] = await self.blocking(
                planner.forecast_off, room, inputs
            )
        self.results = results
        self.forecasts = forecasts
        price = await self.price()
        by_hours = {r["hours"]: r for r in results}
        await fhem.readingsBeginUpdate(self.hash)
        up = fhem.readingsBulkUpdateIfChanged
        state_text = (
            f"setback worth it from {planner.hours_text(worth)}"
            if worth is not None
            else "setback not worth it"
        )
        states = [advisor.state_of(self.fits.get(r.name)) for r in rooms]
        if "learning" in states:
            state_text += " (still learning)"
        await up(self.hash, "state", state_text)
        await up(
            self.hash, "setback_worth_from_h", worth if worth is not None else "never"
        )
        await up(self.hash, "setback_worth_from_text", planner.hours_text(worth))
        for ta, name in (("0.0", "at_0C"), ("-10.0", "at_m10C"), ("10.0", "at_10C")):
            if ta in self._fixed_results:
                value = self._fixed_results[ta]
                await up(
                    self.hash,
                    f"setback_worth_from_h_{name}",
                    value if value is not None else "never",
                )
        for hours, name in ((24, "24h"), (168, "7d")):
            r = by_hours.get(hours)
            if r is None:
                continue
            await up(self.hash, f"savings_{name}_kWh", round(r["saving_kwh"], 1))
            await up(self.hash, f"savings_{name}_pct", round(r["saving_pct"], 1))
            if price is not None:
                await up(
                    self.hash, f"savings_{name}_eur", round(r["saving_kwh"] * price, 2)
                )
        best24 = by_hours.get(24)
        setbacks = []
        for room in rooms:
            key = room_key(room.name)
            room_worth = planner.worth_from(results, thr_pct, thr_kwh, room.name)
            await up(
                self.hash,
                f"{key}_setback_worth_from_h",
                room_worth if room_worth is not None else "never",
            )
            if best24:
                rr = best24["rooms"].get(room.name)
                if rr and rr["best"] is not None:
                    setbacks.append(rr["setback"])
                    await up(self.hash, f"{key}_best_setback_temp", rr["setback"])
            states_off = forecasts[room.name]
            for hours in (12, 24):
                ti, tm = states_off[hours * STEPS_PER_HOUR - 1]
                k = room.k
                await up(
                    self.hash,
                    f"{key}_forecast_off_{hours}h",
                    round(model.operative_temp(ti, tm, k), 1),
                )
            reheat = (self._fixed_results.get("reheat") or {}).get(room.name)
            if reheat:
                await up(
                    self.hash,
                    f"{key}_reheat_hours",
                    round(reheat[1], 1) if reheat[1] is not None else "never",
                )
                await up(
                    self.hash,
                    f"{key}_reheat_hours_air",
                    round(reheat[0], 1) if reheat[0] is not None else "never",
                )
        if setbacks:
            await up(self.hash, "best_setback_temp", statistics.median(setbacks))
        reheats = [v for v in (self._fixed_results.get("reheat") or {}).values() if v]
        if reheats:
            walls = [v[1] for v in reheats]
            airs = [v[0] for v in reheats if v[0] is not None]
            await up(
                self.hash,
                "reheat_hours",
                "never" if None in walls else round(max(walls), 1),
            )
            if airs:
                await up(self.hash, "reheat_hours_air", round(max(airs), 1))
        # house forecast: mean felt temperature of the rooms
        house = []
        for i in range(steps):
            values = [model.operative_temp(*forecasts[r.name][i], r.k) for r in rooms]
            house.append(sum(values) / len(values))
        for hours in FORECAST_HOURS:
            await up(
                self.hash,
                f"forecast_off_{hours}h",
                round(house[hours * STEPS_PER_HOUR - 1], 1),
            )
        await up(self.hash, "forecast_off_7d", round(house[-1], 1))
        horizon = house[: 48 * STEPS_PER_HOUR]
        low = min(range(len(horizon)), key=horizon.__getitem__)
        start = advisor.slot_of(time.time())
        await up(self.hash, "forecast_off_min", round(horizon[low], 1))
        await up(
            self.hash, "forecast_off_min_time", time_text(start + (low + 1) * SLOT)
        )
        frost = [planner.first_below(forecasts[r.name], FROST) for r in rooms]
        frost = [f for f in frost if f is not None]
        await up(
            self.hash,
            "forecast_off_below_frost",
            time_text(start + (min(frost) + 1) * SLOT) if frost else "never",
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        self.view = self.detail_view(rooms, results, worth, house)

    def empty_view(self):
        return {
            "headline": "Learning how your house keeps the heat",
            "subline": "Not enough measurements yet. The first estimate comes "
            "after a few hours, a good one after some nights.",
            "devices": self.devices_view(),
        }

    def detail_view(self, rooms, results, worth, house):
        felt, air, wall = [], [], []
        step = 2  # every 30 minutes, 48 h
        for i in range(0, 48 * STEPS_PER_HOUR, step):
            felt.append(house[i])
            airs = [self.forecasts[r.name][i][0] for r in rooms]
            walls = [model.surface_temp(*self.forecasts[r.name][i], r.k) for r in rooms]
            air.append(sum(airs) / len(airs))
            wall.append(sum(walls) / len(walls))
        explain = []
        fixed = self._fixed_results
        if fixed.get("0.0") is not None:
            explain.append(
                f"At 0 °C outside a setback is worth it from "
                f"{planner.hours_text(fixed['0.0'])}, at -10 °C from "
                f"{planner.hours_text(fixed.get('-10.0'))}."
            )
        day_drop = house[0] - house[24 * STEPS_PER_HOUR - 1]
        explain.append(
            f"Without heating the felt temperature drops by {day_drop:.1f} K "
            "in the next 24 hours (weather forecast included)."
        )
        reheat = {
            name: v for name, v in (fixed.get("reheat") or {}).items() if v and v[1]
        }
        if reheat:
            # the room which needs longest, air and walls of the same room
            slowest = max(reheat, key=lambda name: reheat[name][1])
            air_h, wall_h = reheat[slowest]
            explain.append(
                f"After a long setback ({slowest}, the slowest room) the air "
                f"is warm again after {air_h or 0:.1f} h, but it takes "
                f"{wall_h:.1f} h until the walls are warm too and it feels "
                "comfortable."
            )
        room_rows = []
        thr = (self._attr_worth_threshold_pct, self._attr_worth_threshold_kWh)
        for r in rooms:
            fit = self.fits.get(r.name) or {}
            live = self.live.get(r.name, {})
            rh = (fixed.get("reheat") or {}).get(r.name) or (None, None)
            room_rows.append(
                {
                    "name": r.name,
                    "air": live.get("air"),
                    "wall": live.get("wall"),
                    "felt": live.get("felt"),
                    "off24": model.operative_temp(
                        *self.forecasts[r.name][24 * STEPS_PER_HOUR - 1], r.k
                    ),
                    "worth": planner.hours_text(
                        planner.worth_from(results, *thr, r.name)
                    ),
                    "reheat": rh[1],
                    "model": f"{advisor.state_of(fit)}\u00a0·\u00a0"
                    f"{fit.get('days', 0):g}\u00a0d"
                    + (
                        f"\u00a0·\u00a0±{fit['rmse']:.2f}\u00a0K"
                        if fit.get("rmse")
                        else ""
                    ),
                }
            )
        return {
            "headline": (
                f"Setback worth it from {planner.hours_text(worth)} of absence"
                if worth is not None
                else "A setback is not worth it in the next two weeks"
            ),
            "subline": f"Heating: {self.heating_type()}, comfort = "
            + (
                "air and walls (felt temperature)"
                if self._attr_comfort_basis == "operative"
                else "air temperature"
            ),
            "explain": explain,
            "curve": {"hours": 48, "felt": felt, "air": air, "wall": wall},
            "savings": [
                {k: r[k] for k in ("hours", "saving_pct", "saving_kwh")}
                for r in results
            ],
            "threshold_pct": thr[0],
            "threshold_kwh": thr[1],
            "rooms": room_rows,
            "devices": self.devices_view(),
        }

    # --- doing the setback ---

    async def make_plan(self, kind, return_ts, apply, setback_now=True):
        now = time.time()
        if kind == "learn_night":
            base = datetime.datetime.fromtimestamp(now)
            start = base.replace(hour=22, minute=0, second=0, microsecond=0)
            if base.hour < 5:
                start = base
            elif base.hour >= 22:
                start = base
            start_ts = start.timestamp()
        else:
            start_ts = now
        absence = max(int((return_ts - start_ts) / SLOT), 1)
        rooms = self.rooms_for_planning()
        if not rooms:
            return None, "Nothing learned yet, try again in a few hours."
        offset = max(int((start_ts - now) / SLOT), 0)
        inputs = self.forecast_for(offset + absence + planner.TAIL_HOURS * 4)
        plan = {
            "kind": kind,
            "start": start_ts,
            "return": return_ts,
            "apply": apply,
            "rooms": {},
            "created": now,
        }
        keep = saving = 0.0
        for room in rooms:
            entry = self.found["rooms"].get(room.name, {})
            thermostats = {
                t["device"]: {
                    "target": t["target"],
                    "normal": self.live.get(room.name, {}).get("setp"),
                }
                for t in entry.get("thermostats", [])
            }
            if kind == "learn_night":
                setback = max(self._attr_min_temp, room.normal - 4)
            elif kind == "heat_up":
                setback = (
                    self.live.get(room.name, {}).get("setp") or self._attr_min_temp
                )
            else:
                setback = self.setback_attr()
            if offset:
                states, _, _ = await self.blocking(
                    planner.simulate,
                    room,
                    inputs[:offset],
                    [room.normal] * offset,
                    self.heating_type(),
                )
                room.x0 = states[-1]
            result = await self.blocking(
                planner.best_plan,
                room,
                inputs[offset:],
                absence,
                setback,
                self._attr_min_temp,
                self.heating_type(),
                self._attr_comfort_basis,
                self._attr_max_radiant_asymmetry,
            )
            best = result["best"]
            keep += result["keep_final"]
            if best is None:
                reheat_ts = start_ts
                boost = 0.0
            else:
                reheat_ts = start_ts + best["reheat"] * SLOT
                boost = best["boost"]
                saving += max(result["saving"], 0.0)
            plan["rooms"][room.name] = {
                "setback": result["setback"],
                "normal": room.normal,
                "reheat": reheat_ts,
                "boost": boost,
                "worth": best is not None and result["saving"] > 0,
                "thermostats": thermostats,
                "phase": "pending" if setback_now else "setback",
            }
        scale = self.scale()
        plan["saving_kwh"] = planner.kwh(saving, scale)
        plan["saving_pct"] = 100 * saving / keep if keep else 0.0
        plan["worth"] = (
            plan["saving_pct"] >= self._attr_worth_threshold_pct
            and plan["saving_kwh"] >= self._attr_worth_threshold_kWh
        )
        return plan, None

    async def update_plan_readings(self):
        plan = self._plan
        up = fhem.readingsBulkUpdateIfChanged
        await fhem.readingsBeginUpdate(self.hash)
        if not plan:
            await up(self.hash, "plan_state", "none")
        else:
            phases = {r["phase"] for r in plan["rooms"].values()}
            if not plan.get("apply"):
                state = "computed"
            elif phases == {"done"}:
                state = "done"
            elif "reheat" in phases:
                state = "heating up"
            elif "setback" in phases:
                state = "set back"
            else:
                state = "planned"
            reheat = [r["reheat"] for r in plan["rooms"].values() if r["worth"]]
            setbacks = [r["setback"] for r in plan["rooms"].values() if r["worth"]]
            await up(self.hash, "plan_state", state)
            await up(self.hash, "plan_kind", plan["kind"])
            await up(self.hash, "plan_start", time_text(plan["start"]))
            await up(self.hash, "plan_return", time_text(plan["return"]))
            await up(self.hash, "plan_worth", "yes" if plan["worth"] else "no")
            await up(self.hash, "plan_saving_kWh", round(plan["saving_kwh"], 1))
            await up(self.hash, "plan_saving_pct", round(plan["saving_pct"], 1))
            await up(
                self.hash,
                "plan_reheat_start",
                time_text(min(reheat)) if reheat else "-",
            )
            await up(
                self.hash,
                "plan_setback_temp",
                statistics.median(setbacks) if setbacks else "-",
            )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def set_thermostats(self, room_plan, value):
        for device, info in room_plan["thermostats"].items():
            cmd = f"{device} {info['target']} {value:g}"
            result = await fhem.sendCommandHash(
                self.hash, f"CommandSet(undef, {fhem.perlString(cmd)})"
            )
            if result:
                self.logger.warning(f"set {cmd}: {result}")

    def comfort_value(self, room_plan, device_info):
        return device_info.get("normal") or room_plan["normal"]

    async def run_plan(self, now=None):
        plan = self._plan
        if not plan or not plan.get("apply"):
            return
        now = now or time.time()
        changed = False
        for room_plan in plan["rooms"].values():
            phase = room_plan["phase"]
            if phase == "pending" and now >= plan["start"]:
                if room_plan["worth"] and now < room_plan["reheat"]:
                    await self.set_thermostats(room_plan, room_plan["setback"])
                    room_plan["phase"] = "setback"
                else:
                    room_plan["phase"] = "done"
                changed = True
            elif phase == "setback" and now >= room_plan["reheat"]:
                target = room_plan["normal"] + room_plan["boost"]
                await self.set_thermostats(room_plan, target)
                room_plan["phase"] = "reheat"
                changed = True
            elif phase == "reheat" and now >= plan["return"]:
                if room_plan["boost"]:
                    for device, info in room_plan["thermostats"].items():
                        await self.set_thermostats(
                            {"thermostats": {device: info}},
                            self.comfort_value(room_plan, info),
                        )
                room_plan["phase"] = "done"
                changed = True
        if changed:
            await self.blocking(self.store.put, "plan", plan)
            await self.update_plan_readings()

    # --- attribute changes ---

    async def _rediscover(self):
        await self.discover()
        await self.init_rooms()
        await self.plan_all()

    async def _replan(self):
        await self.update_model_readings()
        await self.compute_fixed()
        self._last_plan = 0
        await self.plan_all()

    def _on_attr(self, coro_function):
        # attributes are also set while FHEM starts, before run() finished
        if self.store is None or self._stopping:
            return
        self.create_async_task(coro_function())

    def set_attr_rooms(self, hash):
        self._on_attr(self._rediscover)

    set_attr_exclude_devices = set_attr_rooms
    set_attr_extra_devices = set_attr_rooms
    set_attr_outdoor_sensor = set_attr_rooms

    def set_attr_heating_type(self, hash):
        self._on_attr(self._replan)

    set_attr_floor_heating = set_attr_heating_type
    set_attr_heating_power_kW = set_attr_heating_type
    set_attr_comfort_temp = set_attr_heating_type
    set_attr_setback_temp = set_attr_heating_type
    set_attr_min_temp = set_attr_heating_type
    set_attr_comfort_basis = set_attr_heating_type
    set_attr_max_radiant_asymmetry = set_attr_heating_type
    set_attr_worth_threshold_pct = set_attr_heating_type
    set_attr_worth_threshold_kWh = set_attr_heating_type

    # --- sets ---

    async def set_absence(self, hash, params):
        try:
            return_ts = parse_time(params["until"], time.time())
        except ValueError as exc:
            return str(exc)
        apply = str(params.get("apply", "")).lower() in ("apply", "1", "yes", "on")
        plan, error = await self.make_plan("absence", return_ts, apply)
        if error:
            return error
        await self.cancel_running()
        self._plan = plan
        await self.blocking(self.store.put, "plan", plan)
        await self.update_plan_readings()
        if apply:
            await self.run_plan()
        return ""

    async def set_heat_up_at(self, hash, params):
        try:
            return_ts = parse_time(params["time"], time.time())
        except ValueError as exc:
            return str(exc)
        plan, error = await self.make_plan(
            "heat_up", return_ts, True, setback_now=False
        )
        if error:
            return error
        for room_plan in plan["rooms"].values():
            room_plan["worth"] = True
        await self.cancel_running(restore=False)
        self._plan = plan
        await self.blocking(self.store.put, "plan", plan)
        await self.update_plan_readings()
        await self.run_plan()
        return ""

    async def set_learn_night(self, hash, params):
        now = datetime.datetime.fromtimestamp(time.time())
        morning = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now.hour >= 5:
            morning += datetime.timedelta(days=1)
        plan, error = await self.make_plan("learn_night", morning.timestamp(), True)
        if error:
            return error
        for room_plan in plan["rooms"].values():
            # an experiment: set back even if it doesn't pay off
            room_plan["worth"] = True
            if room_plan["reheat"] <= plan["start"]:
                room_plan["reheat"] = plan["return"] - 2 * 3600
        await self.cancel_running()
        self._plan = plan
        await self.blocking(self.store.put, "plan", plan)
        await self.update_plan_readings()
        await self.run_plan()
        return ""

    async def cancel_running(self, restore=True):
        plan = self._plan
        if not plan or not plan.get("apply"):
            return
        for room_plan in plan["rooms"].values():
            if room_plan["phase"] in ("setback", "reheat") and restore:
                for device, info in room_plan["thermostats"].items():
                    await self.set_thermostats(
                        {"thermostats": {device: info}},
                        self.comfort_value(room_plan, info),
                    )
            room_plan["phase"] = "done"

    async def set_cancel(self, hash, params):
        await self.cancel_running()
        self._plan = None
        await self.blocking(self.store.put, "plan", None)
        await self.update_plan_readings()
        return ""

    async def set_relearn(self, hash, params):
        self.create_async_task(self.fit_all())
        return ""

    async def set_rediscover(self, hash, params):
        await self.discover()
        await self.init_rooms()
        return ""

    async def set_import_history(self, hash, params):
        count = await self.import_history()
        if not count:
            return "Nothing imported (no fhempy timeline with these devices)."
        await self.init_rooms()
        self.create_async_task(self.fit_all())
        return ""

    # --- gets ---

    async def get_forecast(self, hash, params):
        hours = discover.number(params["hours"]) or 24
        steps = int(min(max(hours, 1), 14 * 24) * STEPS_PER_HOUR)
        setpoint = discover.number(params.get("setpoint"))
        inputs = self.forecast_for(steps)
        result = {}
        start = advisor.slot_of(time.time())
        for room in self.rooms_for_planning():
            states, _, _ = await self.blocking(
                planner.simulate, room, inputs, [setpoint] * steps, "electric"
            )
            result[room.name] = [
                {
                    "time": time_text(start + (i + 1) * SLOT),
                    "air": round(ti, 2),
                    "wall": round(model.surface_temp(ti, tm, room.k), 2),
                    "felt": round(model.operative_temp(ti, tm, room.k), 2),
                }
                for i, (ti, tm) in enumerate(states)
                if (i + 1) % STEPS_PER_HOUR == 0
            ]
        return json.dumps(result)

    async def get_model(self, hash, params):
        return json.dumps(self.fits, indent=1, default=str)
