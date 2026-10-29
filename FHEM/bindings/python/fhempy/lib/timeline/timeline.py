"""Timeline: records the events of all FHEM devices and shows on the detail
page what happened, as readable story per day (e.g. during the holidays).

FHEM sends the events once per second (fhempy_setEventRecorder in
10_fhempy.pm), they are classified (classify.py), stored in SQLite (store.py)
and summarized when the page asks for them (story.py, www/fhempy/timeline.js).
"""

import asyncio
import collections
import datetime
import functools
import json
import os
import re
import time

from .. import fhem, generic, utils
from ..core import fhemweb
from . import classify, story
from .store import Store, day_of, day_start

FLUSH_INTERVAL = 5
READINGS_INTERVAL = 60
CLEANUP_INTERVAL = 6 * 3600
INFO_RELOAD_DELAY = 5
# story readings changing more often become tech (not security/presence,
# their repeats are bundled)
FREQUENT_PER_HOUR = 60
DEFAULT_DAYS = 7
MAX_DAYS = 31
# absences of at least this long are offered as periods, e.g. holidays
PERIOD_MIN_SECONDS = 20 * 3600
ROOM = "Timeline"
ROOM_ICON = "time_calendar"
DEVICE_ICON = "time_calendar"
# attributes of other devices which change their text or classification
INFO_ATTRS = ("alias", "room", "genericDeviceType", classify.ON_CHANGE_ATTR)
# FHEM only counts these events, they are never shown and would only cost
# traffic and space ("device:reading: value")
SKIP_EVENTS = f"^[^:]+:(?i:{classify.TECH_READINGS}): "

HIDDEN_HELP = (
    "Readings which are never shown in the timeline, e.g. "
    "<code>Hallway_motion:motion Sensor1:*</code>. With a value only these "
    "values, e.g. <code>Router:status:booting|reconnecting</code>. Each part "
    "is a regexp. Set by the <i>Hide from story</i> button."
)
ALWAYS_SHOW_HELP = (
    "Readings which are always shown in the timeline, even if fhempy "
    "thinks they are technical, e.g. <code>Washer:program</code>. "
    "Set by the <i>Always show</i> button."
)


def _rule_part(text, flags=0):
    """regexp of one part of device:reading:value, None for any"""
    if text in ("", "*", ".*"):
        return None
    try:
        return re.compile(text, flags)
    except re.error:
        return re.compile(re.escape(text), flags)


def parse_rules(text):
    """device:reading or device:reading:value, each part a regexp"""
    rules = []
    for word in str(text or "").split():
        device, _, rest = word.partition(":")
        reading, _, value = rest.partition(":")
        if device:
            rules.append(
                (
                    _rule_part(device),
                    _rule_part(reading),
                    _rule_part(value, re.IGNORECASE),
                )
            )
    return rules


def _part_matches(regexp, text):
    return regexp is None or regexp.fullmatch(text) is not None


def matches(rules, device, reading, value=""):
    return any(
        _part_matches(d, device)
        and _part_matches(r, reading)
        and _part_matches(v, str(value).strip())
        for d, r, v in rules
    )


class timeline(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.store = None
        self.infos = {}
        self._pending = []
        self._hourly = {}
        self._hidden = collections.Counter()
        self._recent = {}
        self._frequent = set()
        self._hidden_rules = set()
        self._show_rules = set()
        self._flush_lock = asyncio.Lock()
        self._reload_task = None
        self._stopping = False
        self._today = ""
        self._story_today = 0
        self._hidden_today = 0
        self._last_story = ""

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        await self.set_set_config(
            {
                "hide": {
                    "args": ["reading"],
                    "help": "Never show device:reading (or device:* for all "
                    "readings) in the timeline.",
                },
                "show": {
                    "args": ["reading"],
                    "help": "Always show device:reading in the timeline.",
                },
                "ignore": {
                    "args": ["reading"],
                    "help": "Ignore device:reading (or device:* for all "
                    "readings, device:reading:value for some values) "
                    "completely: adds it to the attribute skip_events, FHEM "
                    "doesn't send these events anymore.",
                },
                "prune": {
                    "help": "Delete the stored events which match the "
                    "attribute skip_events, e.g. after Stop recording.",
                },
                "auto": {
                    "args": ["reading"],
                    "help": "Let fhempy decide again whether device:reading "
                    "is shown.",
                },
                "on_change": {
                    "args": ["reading"],
                    "help": "Add the reading of device:reading to the "
                    "attribute event-on-change-reading of the device, so "
                    "FHEM only creates events when its value changes.",
                },
            }
        )
        await self.set_get_config(
            {
                "entries": {
                    "args": ["from", "to"],
                    "params": {
                        "from": {"optional": True},
                        "to": {"optional": True},
                    },
                    "help": "Timeline as JSON, from/to as YYYY-MM-DD "
                    "(default: last 7 days). Used by the detail page.",
                },
                "device": {
                    "args": ["device", "days"],
                    "params": {"days": {"optional": True}},
                    "help": "History of one device of the last days (default "
                    "7) as JSON. Used by the popup of the detail page.",
                },
                "curve": {
                    "args": ["reading", "day", "days"],
                    "params": {
                        "day": {"optional": True},
                        "days": {"optional": True},
                    },
                    "help": "Hourly values of device:reading of the days "
                    "(default 1) up to day (YYYY-MM-DD, default today) as "
                    "JSON. Used by the curve popup of the detail page.",
                },
                "details": {
                    "args": ["day"],
                    "help": "Hidden events of a day (YYYY-MM-DD) as JSON.",
                },
            }
        )
        await self.set_attr_config(
            {
                "hidden": {"default": "", "help": HIDDEN_HELP},
                "always_show": {"default": "", "help": ALWAYS_SHOW_HELP},
                "skip_events": {
                    "default": "",
                    "help": "Regexp of events (device:reading: value) FHEM "
                    "doesn't send to the timeline at all, e.g. "
                    "<code>^Weatherstation:.*</code>.",
                },
                "keep_days": {
                    "default": 730,
                    "format": "int",
                    "help": "Days the story and the daily curves are kept.",
                },
                "keep_details_days": {
                    "default": 14,
                    "format": "int",
                    "help": "Days the hidden (technical) events are kept.",
                },
            }
        )
        self._hidden_rules = parse_rules(self._attr_hidden)
        self._show_rules = parse_rules(self._attr_always_show)
        await fhem.readingsSingleUpdate(self.hash, "state", "starting", 1)
        self.create_async_task(self.run())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._stopping = True
        fhem.unregister_recorder_listener(self.hash["NAME"], self.handle_events)
        try:
            await fhem.setEventRecorder(self.hash, False)
        except Exception:
            self.logger.debug("Failed to stop the event recorder", exc_info=True)
        await super().Undefine(hash)
        if self.store is not None:
            await self.flush()
            await utils.run_blocking(functools.partial(self.store.close))

    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        name = json.dumps(self.hash["NAME"]).replace("<", generic._JS_ESCAPED_LT)
        return (
            '<div id="fhempyTimeline"></div><script>'
            'jQuery.getScript(FW_root+"/fhempy/timeline.js",'
            f"function(){{fhempyTimeline({name})}})</script>" + str(detail)
        )

    # --- recording ---

    def db_path(self):
        return os.path.join(
            os.getcwd(), ".fhempy", "timeline", f"{self.hash['NAME']}.db"
        )

    async def run(self):
        self.store = Store(self.db_path())
        try:
            await utils.run_blocking(functools.partial(self.store.open))
            self._frequent = await utils.run_blocking(
                functools.partial(self.store.frequent)
            )
        except Exception as exc:
            self.logger.exception("Failed to open the timeline database")
            await fhem.readingsSingleUpdate(
                self.hash, "state", f"error: {utils.describe_exception(exc)}", 1
            )
            return
        # stays in room fhempy like all fhempy devices, there as usual row
        await fhemweb.setup_room(
            self.hash, ROOM, ROOM_ICON, DEVICE_ICON, keep_fhempy=True
        )
        await self.reload_infos()
        await self.update_absence(time.time())
        if not await self.start_recorder():
            return
        await fhem.readingsSingleUpdate(self.hash, "state", "recording", 1)
        self.create_async_task(self.flush_loop())
        self.create_async_task(self.cleanup_loop())

    async def start_recorder(self):
        fhem.register_recorder_listener(self.hash["NAME"], self.handle_events)
        skip = SKIP_EVENTS
        if self._attr_skip_events:
            skip = f"{SKIP_EVENTS}|{self._attr_skip_events}"
        result = await fhem.setEventRecorder(self.hash, True, skip)
        if result == "old":
            await fhem.readingsSingleUpdate(
                self.hash,
                "state",
                "FHEM update needed: run 'update all' and restart FHEM",
                1,
            )
            return False
        if result != "ok":
            await fhem.readingsSingleUpdate(self.hash, "state", f"error: {result}", 1)
            return False
        return True

    async def set_attr_skip_events(self, hash):
        if self.store is not None and not self._stopping:
            if await self.start_recorder():
                await fhem.readingsSingleUpdate(self.hash, "state", "recording", 1)

    async def set_attr_hidden(self, hash):
        self._hidden_rules = parse_rules(self._attr_hidden)

    async def set_attr_always_show(self, hash):
        self._show_rules = parse_rules(self._attr_always_show)

    async def reload_infos(self):
        attrs = ",".join(fhem.perlString(attr) for attr in INFO_ATTRS)
        cmd = (
            "my %r; foreach my $d (keys %defs) { my $h = $defs{$d};"
            " next if ($h->{TEMPORARY} || defined($h->{SNIPPET}));"
            " $r{$d} = { TYPE => $h->{TYPE}, FHEMPYTYPE => ($h->{FHEMPYTYPE} // ''),"
            " map { $_ => AttrVal($d, $_, '') } (" + attrs + ") } }"
            " to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            self.infos = json.loads(result)
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read the FHEM devices: {result}")

    def schedule_reload(self):
        if self._reload_task is not None and not self._reload_task.done():
            return

        async def reload_later():
            await asyncio.sleep(INFO_RELOAD_DELAY)
            await self.reload_infos()

        self._reload_task = self.create_async_task(reload_later())

    def handle_global(self, value):
        words = value.split(" ")
        if len(words) < 2:
            return
        if words[0] in ("DEFINED", "DELETED", "RENAMED"):
            self.schedule_reload()
        elif words[0] in ("ATTR", "DELETEATTR") and len(words) > 2:
            if words[2] in INFO_ATTRS:
                self.schedule_reload()

    def layer_of(self, device, reading, value, info):
        if matches(self._hidden_rules, device, reading, value):
            return classify.TECH, classify.DEVICES
        layer, category = classify.classify(info, reading, value)
        if matches(self._show_rules, device, reading, value):
            if layer != classify.STORY and category == classify.DEVICES:
                category = classify.device_category(info)
            return classify.STORY, category
        if layer == classify.STORY and (device, reading) in self._frequent:
            return classify.TECH, category
        return layer, category

    def check_frequent(self, ts, device, reading, category):
        if category in (classify.SECURITY, classify.PRESENCE):
            return False
        recent = self._recent.setdefault((device, reading), collections.deque())
        recent.append(ts)
        while recent and recent[0] < ts - 3600:
            recent.popleft()
        if len(recent) <= FREQUENT_PER_HOUR:
            return False
        del self._recent[(device, reading)]
        self._frequent.add((device, reading))
        self.logger.info(
            f"{device}:{reading} changes more than {FREQUENT_PER_HOUR} times "
            "per hour, it is hidden in the timeline from now on "
            f"(set {self.hash['NAME']} show {device}:{reading} to show it)"
        )
        self.create_async_task(
            utils.run_blocking(
                functools.partial(self.store.add_frequent, device, reading)
            )
        )
        return True

    async def handle_events(self, events, skipped):
        if self.store is None or self._stopping:
            return
        today = day_of(time.time())
        if today != self._today:
            self._today = today
            self._story_today = 0
            self._hidden_today = 0
        skipped_count = sum(int(n) for n in skipped.values())
        if skipped_count:
            self._hidden[today] += skipped_count
            self._hidden_today += skipped_count
        for ts, device, reading, value in events:
            if device == "global":
                self.handle_global(value)
            else:
                self.record(ts, device, reading, value)

    def record(self, ts, device, reading, value):
        info = self.infos.get(device)
        if info is None:
            self.schedule_reload()
            info = {"NAME": device}
        layer, category = self.layer_of(device, reading, value, info)
        if layer == classify.STORY and self.check_frequent(
            ts, device, reading, category
        ):
            layer = classify.TECH
        self._pending.append((ts, device, reading, value, layer, category))
        if layer != classify.TREND and classify.is_setpoint(reading):
            # also a curve, together with the measured temperature
            self.aggregate(ts, device, reading, value, classify.CLIMATE)
        if layer == classify.STORY:
            self._story_today += 1
            self._last_story = story.entry_text(self.infos, device, reading, value)
            if info.get("TYPE") == classify.RESIDENTS_TYPE and reading == "state":
                self.create_async_task(self.update_absence(ts, value))
            return
        self._hidden[day_of(ts)] += 1
        self._hidden_today += 1
        if layer == classify.TREND:
            self.aggregate(ts, device, reading, value, category)

    def aggregate(self, ts, device, reading, value, category):
        number = classify.number(value)
        if number is None:
            return
        key = (int(ts // 3600 * 3600), device, reading)
        values = self._hourly.get(key)
        if values is None:
            self._hourly[key] = [category, number, number, number, 1, number]
        else:
            values[1] = min(values[1], number)
            values[2] = max(values[2], number)
            values[3] += number
            values[4] += 1
            values[5] = number

    async def update_absence(self, ts, state=None):
        if state is None:
            residents = [
                name
                for name, info in self.infos.items()
                if info.get("TYPE") == classify.RESIDENTS_TYPE
            ]
            if not residents:
                return
            state = await fhem.ReadingsVal(sorted(residents)[0], "state", "")
            if not state:
                return
        absent = state in classify.ABSENT_STATES
        await utils.run_blocking(
            functools.partial(self.store.absence_changed, ts, absent)
        )

    async def flush(self):
        async with self._flush_lock:
            if not self._pending and not self._hourly and not self._hidden:
                return
            events, self._pending = self._pending, []
            hourly, self._hourly = self._hourly, {}
            hidden, self._hidden = self._hidden, collections.Counter()
            try:
                await utils.run_blocking(
                    functools.partial(self.store.add, events, hourly, dict(hidden))
                )
            except Exception:
                self.logger.exception("Failed to write the timeline database")

    async def flush_loop(self):
        last_readings = 0
        while not self._stopping:
            await asyncio.sleep(FLUSH_INTERVAL)
            await self.flush()
            if time.time() - last_readings >= READINGS_INTERVAL:
                last_readings = time.time()
                await self.update_readings()

    async def update_readings(self):
        size = await utils.run_blocking(functools.partial(self.store.size))
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "story_events_today", self._story_today
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "hidden_events_today", self._hidden_today
        )
        if self._last_story:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "last_story", self._last_story
            )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "database_size", f"{size / 1e6:.1f} MB"
        )
        await fhem.readingsEndUpdate(self.hash, 1)

    async def cleanup_loop(self):
        while not self._stopping:
            try:
                await utils.run_blocking(
                    functools.partial(
                        self.store.cleanup,
                        self._attr_keep_details_days,
                        self._attr_keep_days,
                    )
                )
            except Exception:
                self.logger.exception("Failed to clean up the timeline database")
            await asyncio.sleep(CLEANUP_INTERVAL)

    # --- sets ---

    async def change_rules(self, target, hide, show):
        device, _, rest = target.partition(":")
        reading, _, value = rest.partition(":")
        if not device:
            return "Use device:reading, device:reading:value or device:*"
        key = f"{device}:{reading or '*'}" + (f":{value}" if value else "")
        rules = {}
        for attr, add in (("hidden", hide), ("always_show", show)):
            words = [w for w in getattr(self, "_attr_" + attr).split() if w != key]
            if add:
                words.append(key)
            rules[attr] = " ".join(words)
        for attr, text in rules.items():
            if text:
                await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} {attr} {text}")
            elif getattr(self, "_attr_" + attr):
                await fhem.CommandDeleteAttr(self.hash, f"{self.hash['NAME']} {attr}")
            setattr(self, "_attr_" + attr, text)
        self._hidden_rules = parse_rules(self._attr_hidden)
        self._show_rules = parse_rules(self._attr_always_show)
        if (device, reading) in self._frequent:
            self._frequent.discard((device, reading))
            await utils.run_blocking(
                functools.partial(self.store.forget_frequent, device, reading)
            )
        return None

    async def set_hide(self, hash, params):
        return await self.change_rules(params["reading"], True, False)

    async def set_show(self, hash, params):
        return await self.change_rules(params["reading"], False, True)

    async def set_auto(self, hash, params):
        return await self.change_rules(params["reading"], False, False)

    async def set_ignore(self, hash, params):
        device, _, rest = params["reading"].partition(":")
        reading, _, value = rest.partition(":")
        if not device or not reading:
            return "Use device:reading, device:reading:value or device:*"
        # reading names never contain ":", so "^device:reading:" matches exactly
        rule = f"^{re.escape(device)}:"
        if reading != "*":
            rule += f"{re.escape(reading)}:"
        if value:
            # FHEM events are "device:reading: value"
            rule += f" (?:{value})$"
            try:
                re.compile(rule)
            except re.error:
                return f"Invalid regexp {value}"
        current = self._attr_skip_events
        if rule in current.split("|"):
            return None
        value = f"{current}|{rule}" if current else rule
        await fhem.CommandAttr(self.hash, f"{self.hash['NAME']} skip_events {value}")
        self._attr_skip_events = value
        return None

    async def set_prune(self, hash, params):
        if self.store is None:
            return "The timeline is starting"
        if not self._attr_skip_events:
            return "The attribute skip_events is empty, nothing to delete"
        try:
            skip = re.compile(self._attr_skip_events)
        except re.error as err:
            return f"skip_events is no Python regexp: {err}"
        await self.flush()
        events, hours = await utils.run_blocking(
            functools.partial(self.store.prune, skip)
        )
        message = f"Deleted {events} events and {hours} hourly values"
        await fhem.readingsSingleUpdate(self.hash, "last_prune", message, 1)
        return message

    async def set_on_change(self, hash, params):
        device, _, reading = params["reading"].partition(":")
        if device not in self.infos or not classify.READING_NAME_RE.match(reading):
            return "Use device:reading of an existing device"
        attr = classify.ON_CHANGE_ATTR
        current = await fhem.AttrVal(device, attr, "")
        info = self.infos[device]
        info[attr] = current
        if classify.on_change(info, reading):
            return None
        value = f"{current},{reading}" if current else reading
        await fhem.CommandAttr(self.hash, f"{device} {attr} {value}")
        info[attr] = value
        return None

    # --- gets ---

    @staticmethod
    def parse_day(text, default):
        if not text:
            return default
        return datetime.datetime.strptime(str(text), "%Y-%m-%d").date()

    async def get_entries(self, hash, params):
        if self.store is None:
            return json.dumps({"error": "The timeline is starting"})
        today = datetime.date.today()
        try:
            last = self.parse_day(params.get("to"), today)
            first = self.parse_day(
                params.get("from"), last - datetime.timedelta(days=DEFAULT_DAYS - 1)
            )
        except ValueError:
            return "Use YYYY-MM-DD for from and to"
        first = max(first, last - datetime.timedelta(days=MAX_DAYS - 1))
        await self.flush()
        start = day_start(first.isoformat())
        end = day_start(last.isoformat()) + 86400
        data = await utils.run_blocking(
            functools.partial(self.query, start, end, first, last)
        )
        rows = [
            row for row in data["story"] if not matches(self._hidden_rules, *row[1:4])
        ]
        now = time.time()
        days = story.build(
            first.isoformat(),
            last.isoformat(),
            rows,
            data["hourly"],
            data["hidden"],
            data["absences"],
            self.infos,
            now,
            data["carry"],
        )
        return json.dumps(
            {
                "from": first.isoformat(),
                "to": last.isoformat(),
                "first": day_of(data["first"]) if data["first"] else today.isoformat(),
                "today": today.isoformat(),
                "days": days,
                "periods": [
                    {"start": day_of(s), "end": day_of(e if e is not None else now)}
                    for s, e in data["periods"]
                ],
                "categories": list(classify.CATEGORIES),
            },
            ensure_ascii=False,
        )

    def query(self, start, end, first, last):
        return {
            "story": self.store.story(start, end),
            "hourly": self.store.hourly(start, end),
            "carry": self.store.values_before(start),
            "hidden": self.store.hidden(first.isoformat(), last.isoformat()),
            "absences": self.store.absences(start - 86400, end),
            "periods": self.store.long_absences(PERIOD_MIN_SECONDS),
            "first": self.store.first_ts(),
        }

    async def get_device(self, hash, params):
        if self.store is None:
            return json.dumps({"error": "The timeline is starting"})
        device = params["device"]
        if device not in self.infos:
            return json.dumps({"error": f"Unknown device {device}"})
        try:
            days = int(params.get("days") or DEFAULT_DAYS)
        except ValueError:
            return json.dumps({"error": "days must be a number"})
        days = min(max(days, 1), MAX_DAYS)
        await self.flush()
        now = time.time()
        end = day_start(datetime.date.today().isoformat()) + 86400
        start = end - days * 86400
        data = await utils.run_blocking(
            functools.partial(self.query_device, device, start, end)
        )
        rows = [
            row for row in data["story"] if not matches(self._hidden_rules, *row[1:4])
        ]
        entries = story.build_entries(rows, self.infos, data["absences"], now)
        activity = story.build_activity(entries, self.infos, now)
        entries.reverse()
        info = self.infos[device]
        return json.dumps(
            {
                "device": device,
                "text": story.label(self.infos, device),
                "type": info.get("TYPE", ""),
                "room": info.get("room", ""),
                "from": start,
                "to": end,
                "entries": entries,
                "activity": activity,
                "trends": story.build_device_trends(
                    data["hourly"], self.infos, data["carry"], start, end, now
                ),
            },
            ensure_ascii=False,
        )

    async def get_curve(self, hash, params):
        if self.store is None:
            return json.dumps({"error": "The timeline is starting"})
        device, _, reading = str(params.get("reading", "")).partition(":")
        if device not in self.infos or not classify.READING_NAME_RE.match(reading):
            return json.dumps({"error": "Use device:reading of an existing device"})
        today = datetime.date.today()
        try:
            last = min(self.parse_day(params.get("day"), today), today)
            days = min(max(int(params.get("days") or 1), 1), MAX_DAYS)
        except ValueError:
            return json.dumps({"error": "Use YYYY-MM-DD and a number of days"})
        await self.flush()
        start = day_start((last - datetime.timedelta(days=days - 1)).isoformat())
        end = day_start((last + datetime.timedelta(days=1)).isoformat())
        data = await utils.run_blocking(
            functools.partial(self.query_curve, device, start, end)
        )
        rows = collections.defaultdict(list)
        for row in data["hourly"]:
            rows[row[2]].append(row)
        carry = {row[2]: row[8] for row in data["carry"]}
        readings = story.curve_readings(reading, set(rows) | set(carry))
        return json.dumps(
            story.build_curve(
                device,
                readings,
                {"rows": rows, "carry": carry},
                self.infos,
                (start, end, last, today),
            ),
            ensure_ascii=False,
        )

    def query_curve(self, device, start, end):
        return {
            "hourly": self.store.device_hourly(device, start, end),
            "carry": self.store.values_before(start, device),
        }

    def query_device(self, device, start, end):
        return {
            "story": self.store.device_story(device, start, end),
            "hourly": self.store.device_hourly(device, start, end),
            "carry": self.store.values_before(start, device),
            "absences": self.store.absences(start - 86400, end),
        }

    async def get_details(self, hash, params):
        if self.store is None:
            return json.dumps({"error": "The timeline is starting"})
        try:
            day = self.parse_day(params.get("day"), None)
        except ValueError:
            return "Use YYYY-MM-DD"
        await self.flush()
        start = day_start(day.isoformat())
        rows = await utils.run_blocking(
            functools.partial(self.store.details, start, start + 86400)
        )
        return json.dumps(
            [
                {
                    "ts": ts,
                    "device": device,
                    "reading": reading,
                    "value": value,
                    "layer": layer,
                    "text": story.entry_text(self.infos, device, reading, value),
                    "on_change": classify.on_change(
                        self.infos.get(device, {}), reading
                    ),
                }
                for ts, device, reading, value, layer in rows
            ],
            ensure_ascii=False,
        )
