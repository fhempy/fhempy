"""Heating control: mixer and circulation pump of a heating circuit, the
room thermostats with very simple schedules, vacation mode and a flow
temperature which learns what the house needs.

- the heat source (boiler, buffer, heat pump) is not touched, the module
  mixes its supply down to the flow temperature the house needs
- event based: every new value of a sensor or thermostat triggers a
  control step, a timer only wakes up at the next schedule change
- discover.py finds thermostats, suggests the other devices
- controller.py holds the control logic, curve.py the learned curve,
  pumps.py the Grundfos ALPHA pumps, render.py the detail page
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
from . import controller, curve, discover, pumps, render, schedule

EVENT_DELAY = 1.0
RELOAD_DELAY = 5.0
# safety check while the pump runs, in case a sensor only reports changes
HEARTBEAT = 300
HISTORY_SECONDS = 24 * 3600
HISTORY_STEP = 60
LIVE_STEP = 10
ROOM_ICON = "sani_heating"
LEARN_MIN_MINUTES = 15
SETTLE_SECONDS = 90 * 60
PUMP_MIN_SECONDS = 10 * 60
THERMOSTAT_REPEAT = 15 * 60
OWN_SET_GRACE = 120
# a FHEM reading value which starts with a number (Perl regexp)
NUMBER_RE = r"/^\s*-?\d+(?:[.,]\d+)?(?![\d:.\-])/"
GETS = {
    "readings": {
        "args": ["device"],
        "help": "Number readings of a device as JSON (used by the detail page).",
    },
    "page": {"help": "The page of the heating control (used by its own room)."},
    "live": {"help": "Current values as JSON (used by the page)."},
}
ROOM_KEY = re.compile(r"[^A-Za-z0-9_]")
# setup: nothing is controlled until the user starts the control
MODES = ("setup", "auto", "off")
HEAT_SOURCES = (
    "buffer",
    "heatpump",
    "wood",
    "pellet",
    "gas",
    "oil",
    "district",
    "solar",
)

ATTRS = {
    "mixer": {
        "default": "",
        "help": "Mixer 0-100 %: device[:set command], e.g. mixer:pct. "
        "Choose it on the detail page.",
    },
    "mixer_invert": {
        "default": "0",
        "format": "int",
        "options": "0,1",
        "help": "1 if 0 % of the mixer means full supply (hot).",
    },
    "mixer_step": {
        "default": "2",
        "format": "float",
        "help": "Smallest change of the mixer in % (default 2).",
    },
    "mixer_interval": {
        "default": "30",
        "format": "int",
        "help": "Seconds between two mixer commands at most (default 30).",
    },
    "pump": {
        "default": "",
        "help": "Circulation pump on/off: device[:power reading].",
    },
    "pump_model": {
        "default": "",
        "options": ",".join(m.replace(" ", "_") for m in pumps.model_names()),
        "help": "Grundfos ALPHA type of the pump, used to estimate the flow.",
    },
    "pump_setting": {
        "default": "",
        "options": ",".join(pumps.SETTINGS),
        "help": "Setting of the pump: AUTOADAPT, PP1-3 (proportional pressure), "
        "CP1-3 (constant pressure) or I/II/III (constant speed).",
    },
    "pump_power": {
        "default": "",
        "help": "Power of the pump in W shown on its display, only needed "
        "if the switch of the pump doesn't measure it.",
    },
    "flow_factor": {
        "default": "1.0",
        "format": "float",
        "help": "Correction of the estimated flow, e.g. 0.9 if a heat meter "
        "shows 10 % less.",
    },
    "fixed_flow": {
        "default": "",
        "help": "Known flow in l/h, replaces the estimate from the pump.",
    },
    "flow_sensor": {
        "default": "",
        "help": "Flow temperature (Vorlauf): device:reading.",
    },
    "return_sensor": {
        "default": "",
        "help": "Return temperature (Rücklauf): device:reading.",
    },
    "supply_sensor": {
        "default": "",
        "help": "Temperature of the heat source before the mixer: device:reading.",
    },
    "heat_source": {
        "default": "buffer",
        "options": ",".join(HEAT_SOURCES),
        "help": "What delivers the heat, only for the picture and the name on "
        "the detail page: buffer tank, heat pump, wood stove, pellets, gas, oil, "
        "district heating, solar.",
    },
    "outdoor_sensor": {
        "default": "",
        "help": "Outdoor temperature: device:reading, default the weather device.",
    },
    "weather": {
        "default": "",
        "help": "Weather device with forecast (openmeteo_weather, Weather, ...), "
        "found automatically.",
    },
    "thermometers": {
        "default": "",
        "help": "Room thermometers which replace the temperature of the "
        "thermostats: room=device:reading,room2=device",
    },
    "thermostat_rooms": {
        "default": "",
        "help": "Own rooms instead of the FHEM rooms: "
        "thermostat=room,thermostat2=room (set in the setup assistant).",
    },
    "exclude_thermostats": {
        "default": "",
        "help": "Thermostats which are not controlled, comma separated.",
    },
    "design_flow": {
        "default": "55",
        "format": "float",
        "help": "Flow temperature at the design outdoor temperature (start "
        "value, the module learns the correction), 55 radiators, 35 floor.",
    },
    "design_outdoor": {
        "default": "-12",
        "format": "float",
        "help": "Coldest outdoor temperature of the region (default -12).",
    },
    "min_flow": {
        "default": "20",
        "format": "float",
        "help": "Lowest flow temperature.",
    },
    "max_flow": {
        "default": "60",
        "format": "float",
        "help": "Highest flow temperature (45 for floor heating!).",
    },
    "heating_limit": {
        "default": "16",
        "format": "float",
        "help": "No heating from this outdoor temperature on (with forecast).",
    },
    "forecast_hours": {
        "default": "6",
        "format": "int",
        "help": "Hours of the weather forecast used for the flow temperature.",
    },
    "comfort_default": {
        "default": "21",
        "format": "float",
        "help": "Comfort of new rooms.",
    },
    "eco_default": {"default": "18", "format": "float", "help": "Eco of new rooms."},
    "vacation_default": {
        "default": "16",
        "format": "float",
        "help": "Temperature during the vacation (default 16).",
    },
}

SETS = {
    "mode": {
        "args": ["mode"],
        "options": ",".join(MODES),
        "help": "setup: controls nothing (after define, until the setup is "
        "finished), auto: the module controls mixer, pump and thermostats "
        "(starts the control, only with a finished setup), off: it only measures.",
    },
    "room_temp": {
        "args": ["room", "temperature"],
        "help": "Temperature of a room until the next change of its schedule, "
        "<code>auto</code> goes back to the schedule.",
    },
    "comfort_temp": {
        "args": ["room", "temperature"],
        "help": "Comfort temperature of a room (or <code>all</code>).",
    },
    "eco_temp": {
        "args": ["room", "temperature"],
        "help": "Eco temperature of a room (or <code>all</code>).",
    },
    "schedule": {
        "args": ["room", "schedule"],
        "help": "Schedule of a room: from which time which temperature, as many "
        "points per day as you like, e.g. <code>Mo-Fr 00:00 17, 06:00 21, "
        "08:00 18, 16:00 21.5, 22:00 17; Sa-So 15</code>. <code>comfort</code> "
        "and <code>eco</code> instead of a number use the temperatures of the "
        "room, the old form <code>Mo-Fr 06:00-08:00,16:00-22:00</code> "
        "(comfort periods, the rest eco) works as well. The JSON of the module "
        'weekprofile (<code>{"Mon":{"time":["06:00","24:00"],'
        '"temp":["17","21"]},...}</code>) is taken too, the schedule '
        "is saved in this format.",
    },
    "copy_schedule": {
        "args": ["from", "to"],
        "help": "Copy schedule and temperatures of a room to another room "
        "or to <code>all</code>.",
    },
    "vacation": {
        "args": ["until", "temperature"],
        "params": {"temperature": {"optional": True}},
        "help": "Vacation until the day you are back (2026-12-27 or 7d), "
        "optional temperature. The house is warm again on that day.",
    },
    "vacation_off": {"help": "End the vacation now."},
    "reset_learning": {"help": "Forget the learned flow temperatures."},
    "rescan": {"help": "Search the devices again now."},
    "create_room": {
        "args": ["room"],
        "params": {"room": {"optional": True}},
        "help": "Creates a room of its own in FHEMWEB (default Heizungssteuerung "
        "or Heating) which shows only the page of the heating control.",
    },
}


UMLAUTS = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
)


def room_key(name):
    key = ROOM_KEY.sub("_", str(name).translate(UMLAUTS))
    return key.strip("_") or "room"


def split_ref(text):
    """'device:reading' -> (device, reading or None)"""
    text = (text or "").strip()
    if not text:
        return None, None
    device, _, reading = text.partition(":")
    return device, reading or None


def parse_assignments(text):
    """'room=dev:reading,room2=dev' -> {room: (dev, reading)}"""
    result = {}
    for part in (text or "").split(","):
        room, sep, ref = part.partition("=")
        if sep and room.strip():
            result[room.strip()] = split_ref(ref)
    return result


def parse_until(text, now):
    """'2026-12-27', '27.12.2026', '7d' or '7' (days) -> datetime 00:00 of
    the day back home"""
    text = str(text).strip().lower()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if text.endswith("d") and text[:-1].isdigit():
        return today + datetime.timedelta(days=int(text[:-1]))
    if text.isdigit() and len(text) <= 3:
        return today + datetime.timedelta(days=int(text))
    if re.fullmatch(r"\d{1,2}\.\d{1,2}\.", text):
        day = datetime.datetime.strptime(f"{text}{now.year}", "%d.%m.%Y")
        return day if day >= today else day.replace(year=now.year + 1)
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError(f"unknown date {text}, use 2026-12-27 or 7d")


class Room:
    def __init__(self, name, comfort, eco):
        self.name = name
        self.key = room_key(name)
        self.thermostats = []
        self.thermometer = (None, None)
        self.comfort = comfort
        self.eco = eco
        self.week = schedule.parse(schedule.DEFAULT)
        self.override = None  # (temperature, until timestamp)
        self.bias = None
        self.actual = None
        self.target = None
        self.state = "eco"
        self.valve = None
        self.window = False
        # [{"device", "label", "kind": "unreachable"|"battery", "battery"}]
        self.alerts = []

    def temp_of(self, value):
        """temperature of a schedule value (number or comfort/eco)"""
        if value == "comfort":
            return self.comfort
        if value == "eco":
            return self.eco
        return value

    def view(self):
        return {
            "key": self.key,
            "name": self.name,
            "actual": self.actual,
            "source": "thermometer" if self.thermometer[0] else "thermostat",
            "target": self.target,
            "state": self.state,
            "comfort": self.comfort,
            "eco": self.eco,
            "schedule": schedule.to_text(self.week),
            # switch points with temperatures, comfort/eco resolved
            "week": {
                str(d): [[m, self.temp_of(v)] for m, v in self.week.get(d, [])]
                for d in range(7)
            },
            "override_until": self.override[1] if self.override else None,
            "valve": self.valve,
            "window": self.window,
            "alerts": list(self.alerts),
            "thermostats": list(self.thermostats),
            "thermometer": ":".join(r for r in self.thermometer if r) or "",
        }


class heating_control(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.infos = {}
        self.numeric_devices = []
        # read before: while FHEM waits for FW_detailFn it answers no
        # command of another device (e.g. global), the page would time out
        self.language = "EN"
        self.own_rooms = []
        self.control_room = ""
        self.found = discover.discover({})
        self.values = {}
        self.rooms = {}
        self.thermostats = {}
        self.mode = "setup"
        self.setup_done = ""
        self.vacation = None  # (until timestamp, temperature)
        self.learned = curve.Learned()
        self.mixer_ctl = controller.Mixer()
        self.house = {}
        self.history = collections.deque(maxlen=HISTORY_SECONDS // HISTORY_STEP + 10)
        self.heat_total = 0.0
        self.heat_today = 0.0
        self.heat_day = None
        self.pump_on = None
        self.pump_changed = 0.0
        self.mixer_sent = None
        self.mixer_sent_at = 0.0
        self.sent_setpoints = {}
        self.last_eval = None
        self.last_learn = None
        self.last_target_change = 0.0
        self.last_history = 0.0
        self.last_live = 0.0
        self.reason = "idle"
        self._listening = []
        self._eval_handle = None
        self._eval_task = None
        self._reload_handle = None
        self._timer_changed = asyncio.Event()
        self._stopping = False
        self._ready = False

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        self._stopping = False
        await super().Define(hash, args, argsh)
        await self.set_set_config(SETS)
        await self.set_get_config(GETS)
        await self.set_attr_config(ATTRS)
        await self.set_icon("sani_heating")
        await fhem.readingsSingleUpdate(self.hash, "state", "starting", 1)
        self.create_async_task(self.start())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._stopping = True
        for handle in (self._eval_handle, self._reload_handle):
            if handle is not None:
                handle.cancel()
        await self.unregister_events()
        await self.save_history()
        await super().Undefine(hash)

    # FHEM FUNCTION
    async def Set(self, hash, args, argsh):
        # the schedule contains spaces, take all words
        if len(args) > 3 and args[1] == "schedule":
            return await self.set_schedule(
                hash, {"room": args[2], "schedule": " ".join(args[3:])}
            )
        return await super().Set(hash, args, argsh)

    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        # no command to FHEM here, it waits for this answer (deadlock)
        return render.page(self.view(), self.language) + str(detail)

    # --- attributes: any device change reloads ---

    def schedule_reload(self, hash=None):
        if self._stopping or not self._ready:
            return
        if self._reload_handle is not None:
            self._reload_handle.cancel()
        loop = asyncio.get_running_loop()
        self._reload_handle = loop.call_later(
            RELOAD_DELAY, lambda: self.create_async_task(self.reload())
        )

    def __getattr__(self, name):
        # set_attr_<attribute> of every attribute reloads the devices
        if name.startswith("set_attr_") and name[9:] in ATTRS:
            return self.schedule_reload
        raise AttributeError(name)

    # --- start, discovery, events ---

    async def start(self):
        await self.load_history()
        await self.load_state()
        self._ready = True
        await self.reload()
        self.create_async_task(self.timer_loop())

    def history_path(self):
        return os.path.join(
            os.getcwd(), ".fhempy", "heating_control", f"{self.hash['NAME']}.json"
        )

    async def load_history(self):
        path = self.history_path()

        def load():
            try:
                with open(path, encoding="utf-8") as file:
                    return json.load(file)
            except (OSError, ValueError):
                return {}

        data = await utils.run_blocking(functools.partial(load))
        cutoff = time.time() - HISTORY_SECONDS
        for point in data.get("history", []):
            if isinstance(point, list) and point and point[0] >= cutoff:
                self.history.append(point)

    async def save_history(self):
        if not hasattr(self, "hash"):
            return
        path = self.history_path()
        data = {"history": list(self.history)}

        def save():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as file:
                json.dump(data, file)
            os.replace(tmp, path)

        try:
            await utils.run_blocking(functools.partial(save))
        except OSError as exc:
            self.logger.error(f"Failed to save the history: {exc}")

    async def read_language(self):
        result = await fhem.sendCommandHash(
            self.hash, "AttrVal('global', 'language', 'EN')"
        )
        return str(result or "EN")

    async def read_own_rooms(self):
        name = fhem.perlString(self.hash["NAME"])
        result = await fhem.sendCommandHash(self.hash, f"AttrVal({name}, 'room', '')")
        return [room.strip() for room in str(result or "").split(",") if room.strip()]

    async def own_readings(self):
        name = fhem.perlString(self.hash["NAME"])
        cmd = (
            f"my $h = $defs{{{name}}}; my %r; if ($h) {{ foreach my $k "
            "(keys %{$h->{READINGS} // {}}) { $r{$k} = $h->{READINGS}{$k}{VAL} } }"
            " to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            data = json.loads(result)
            return data if isinstance(data, dict) else {}
        except (TypeError, ValueError):
            return {}

    async def load_state(self):
        readings = await self.own_readings()
        self.saved = readings
        # only a control the user started once runs on, a new device (or one
        # from before setup_done existed) waits for the end of the setup
        self.setup_done = readings.get("setup_done", "")
        self.control_room = readings.get(".control_room", "")
        self.mode = readings.get("mode", "setup") if self.setup_done else "setup"
        if self.mode not in MODES:
            self.mode = "setup"
        self.learned.from_text(readings.get("learned_curve", ""))
        self.heat_total = discover.number(readings.get("heat_energy")) or 0.0
        self.heat_today = discover.number(readings.get("heat_today")) or 0.0
        self.heat_day = readings.get("heat_day") or datetime.date.today().isoformat()
        vacation = readings.get("vacation", "off").split()
        if len(vacation) == 2:
            try:
                until = datetime.datetime.strptime(vacation[0], "%Y-%m-%d")
                self.vacation = (until.timestamp(), float(vacation[1]))
            except ValueError:
                self.vacation = None

    def restore_room(self, room):
        prefix = f"room_{room.key}_"
        saved = getattr(self, "saved", {})
        comfort = discover.number(saved.get(prefix + "comfort"))
        eco = discover.number(saved.get(prefix + "eco"))
        room.comfort = comfort if comfort is not None else room.comfort
        room.eco = eco if eco is not None else room.eco
        text = saved.get(prefix + "schedule")
        if text:
            try:
                room.week = schedule.parse(text)
            except ValueError:
                self.logger.error(f"Invalid saved schedule of {room.name}: {text}")
        override = str(saved.get(prefix + "override", "-")).split()
        if len(override) == 2:
            try:
                temp, until = float(override[0]), float(override[1])
                if until > time.time():
                    room.override = (temp, until)
            except ValueError:
                pass

    async def read_infos(self):
        pattern = (
            "temp|Temp|desired|setpoint|Setpoint|valve|Valve|actuator|demand|"
            "window|power|Power|^state$|^pct$|^position$|^level$|^brightness$|"
            "battery|Battery|^Activity$|^availab|^reachable$|^connected$"
        )
        cmd = (
            "my %r; my $re = " + fhem.perlString(pattern) + ";"
            " foreach my $d (keys %defs) { my $h = $defs{$d};"
            " next if ($h->{TEMPORARY} || defined($h->{SNIPPET}));"
            " my %rd; foreach my $n (keys %{$h->{READINGS} // {}}) {"
            " next if ($n !~ /$re/);"
            " $rd{$n} = $h->{READINGS}{$n}{VAL} }"
            " next if (!%rd);"
            " $r{$d} = { TYPE => $h->{TYPE}, FHEMPYTYPE => ($h->{FHEMPYTYPE} // ''),"
            " room => AttrVal($d, 'room', ''), alias => AttrVal($d, 'alias', ''),"
            " sets => ($h->{TYPE} =~ /^(Weather|PROPLANTA|DWD_OpenData)$/ ? ''"
            " : (getAllSets($d) // '')), readings => \\%rd } } to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            infos = json.loads(result)
            return infos if isinstance(infos, dict) else {}
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read the FHEM devices: {result}")
            return {}

    async def read_numeric_devices(self):
        """all devices with at least one number reading, for the sensor
        selection: [(name, alias)]"""
        cmd = (
            "my @r; foreach my $d (sort keys %defs) { my $h = $defs{$d};"
            " next if ($h->{TEMPORARY} || defined($h->{SNIPPET}));"
            " my $rd = $h->{READINGS} // {};"
            " next if (!grep { ($rd->{$_}{VAL} // '') =~ "
            + NUMBER_RE
            + " } keys %{$rd});"
            " push(@r, [$d, AttrVal($d, 'alias', '')]) } to_json(\\@r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            devices = json.loads(result)
            return [d for d in devices if isinstance(d, list) and len(d) == 2]
        except (TypeError, ValueError):
            return []

    async def get_readings(self, hash, params):
        """number readings of a device as JSON, for the detail page"""
        name = fhem.perlString(params["device"])
        cmd = (
            f"my $h = $defs{{{name}}}; my %r; if ($h) {{ my $rd = $h->{{READINGS}} // {{}};"
            " foreach my $k (keys %{$rd}) { my $v = $rd->{$k}{VAL} // '';"
            " $r{$k} = $v if ($v =~ " + NUMBER_RE + ") } } to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            readings = json.loads(result)
        except (TypeError, ValueError):
            readings = {}
        if not isinstance(readings, dict):
            readings = {}
        ordered = sorted(
            readings.items(),
            key=lambda item: (not discover.TEMP_NAME.search(item[0]), item[0].lower()),
        )
        return json.dumps(ordered)

    async def reload(self):
        if self._stopping:
            return
        self._reload_handle = None
        self.language = await self.read_language()
        self.own_rooms = await self.read_own_rooms()
        self.numeric_devices = await self.read_numeric_devices()
        self.infos = await self.read_infos()
        self.found = discover.discover(self.infos, self.hash["NAME"])
        self.values = {
            name: dict(info.get("readings") or {}) for name, info in self.infos.items()
        }
        self.build_rooms()
        await self.register_events()
        await self.evaluate()
        self.schedule_timer()

    def build_rooms(self):
        excluded = {
            d.strip()
            for d in str(self._attr_exclude_thermostats).split(",")
            if d.strip()
        }
        thermometers = parse_assignments(self._attr_thermometers)
        thermometers = {room_key(k): v for k, v in thermometers.items()}
        rooms = {}
        self.thermostats = {}
        for name, thermostat in self.found["thermostats"].items():
            if name in excluded:
                continue
            self.thermostats[name] = thermostat
            room_name = self.room_of(name)
            key = room_key(room_name)
            room = rooms.get(key)
            if room is None:
                room = self.rooms.get(key)
                if room is None:
                    room = Room(
                        room_name, self._attr_comfort_default, self._attr_eco_default
                    )
                    self.restore_room(room)
                room.thermostats = []
                rooms[key] = room
            room.thermostats.append(name)
        for key, room in rooms.items():
            device, reading = thermometers.get(key, (None, None))
            if device and not reading:
                temps = discover.temperature_readings(self.infos.get(device, {}))
                reading = temps[0] if temps else "temperature"
            room.thermometer = (device, reading)
        self.rooms = dict(sorted(rooms.items(), key=lambda item: item[1].name.lower()))

    def used_devices(self):
        devices = set(self.thermostats)
        for room in self.rooms.values():
            if room.thermometer[0]:
                devices.add(room.thermometer[0])
        for attr in ("mixer", "pump", "flow_sensor", "return_sensor", "supply_sensor"):
            device, _ = split_ref(getattr(self, "_attr_" + attr))
            if device:
                devices.add(device)
        outdoor, _ = split_ref(self._attr_outdoor_sensor)
        if outdoor:
            devices.add(outdoor)
        weather = self.weather_device()
        if weather:
            devices.add(weather)
        return sorted(devices)

    def weather_device(self):
        if self._attr_weather:
            return self._attr_weather
        return self.found["weather"][0] if self.found["weather"] else None

    async def register_events(self):
        await self.unregister_events()
        names = self.used_devices()
        for name in names:
            fhem.register_event_listener(name, self.handle_event)
        fhem.register_event_listener("global", self.handle_global_event)
        self._listening = names + ["global"]
        await fhem.setEventDevices(self.hash, self._listening)

    async def unregister_events(self):
        for name in self._listening:
            fhem.unregister_event_listener(name, self.handle_event)
            fhem.unregister_event_listener(name, self.handle_global_event)
        if self._listening and self._stopping:
            await fhem.setEventDevices(self.hash, [])
        self._listening = []

    def handle_event(self, device, reading, value):
        self.values.setdefault(device, {})[reading] = value
        thermostat = self.thermostats.get(device)
        if thermostat and reading == thermostat["target"]:
            self.thermostat_changed(device, value)
        self.request_evaluation()

    def handle_global_event(self, device, reading, value):
        words = str(value).split(" ")
        if words[0] in ("DEFINED", "DELETED", "RENAMED"):
            self.schedule_reload()
        elif words[0] in ("ATTR", "DELETEATTR") and len(words) > 2:
            if words[2] == "room" and words[1] in self.infos:
                self.schedule_reload()
            elif words[1] == "global" and words[2] == "language":
                self.schedule_reload()
            elif words[1] == self.hash["NAME"] and words[2] == "room":
                self.schedule_reload()

    def thermostat_changed(self, device, value):
        """someone turned the thermostat: the room keeps this temperature
        until its next schedule change"""
        sent = self.sent_setpoints.get(device)
        temp = discover.number(value)
        if temp is None or self.mode != "auto":
            return
        if sent and abs(sent[0] - temp) < 0.25:
            return
        if sent and time.time() - sent[1] < OWN_SET_GRACE and sent[2] is not None:
            # slow thermostats report the old value once more
            if abs(sent[2] - temp) < 0.25:
                return
        for room in self.rooms.values():
            if device in room.thermostats:
                wanted = controller.round_half(temp - (room.bias or 0.0))
                if room.target is not None and abs(wanted - room.target) < 0.25:
                    return
                self.logger.info(f"{room.name}: {wanted} °C set at {device}")
                room.override = (wanted, self.room_switch_time(room))
                self.sent_setpoints[device] = (temp, time.time(), None)
                self.create_async_task(self.save_room(room))

    def request_evaluation(self, delay=EVENT_DELAY):
        if self._stopping or not self._ready or self._eval_handle is not None:
            return
        loop = asyncio.get_running_loop()
        self._eval_handle = loop.call_later(delay, self._start_evaluation)

    def _start_evaluation(self):
        self._eval_handle = None
        if self._eval_task is not None and not self._eval_task.done():
            # still running: evaluate again afterwards
            self.request_evaluation()
            return
        self._eval_task = self.create_async_task(self.evaluate())

    # --- timer: schedule changes, end of vacation, heartbeat ---

    def next_wakeup(self, now):
        moments = []
        local = datetime.datetime.fromtimestamp(now)
        for room in self.rooms.values():
            switch = schedule.next_switch(room.week, local)
            if switch is not None:
                moments.append(switch.timestamp())
            if room.override:
                moments.append(room.override[1])
        if self.vacation:
            moments.append(self.vacation[0])
        tomorrow = (local + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        moments.append(tomorrow.timestamp())
        if self.pump_on:
            moments.append(now + HEARTBEAT)
        future = [m for m in moments if m > now]
        return min(future) if future else now + 3600

    def schedule_timer(self):
        """the schedule changed: compute the next wakeup again"""
        self._timer_changed.set()

    async def timer_loop(self):
        while not self._stopping:
            wake = self.next_wakeup(time.time())
            self._timer_changed.clear()
            try:
                await asyncio.wait_for(
                    self._timer_changed.wait(), max(wake - time.time(), 1) + 0.5
                )
                # woken by a change, not by the time
                continue
            except asyncio.TimeoutError:
                pass
            self.request_evaluation(0)

    # --- the control step ---

    def value(self, device, reading):
        if not device:
            return None
        return discover.number(self.values.get(device, {}).get(reading))

    def sensor(self, attr):
        device, reading = split_ref(getattr(self, "_attr_" + attr))
        if device and not reading:
            temps = discover.temperature_readings(
                {"readings": self.values.get(device, {})}
            )
            reading = temps[0] if temps else "temperature"
        return self.value(device, reading)

    def outdoor(self):
        current = self.sensor("outdoor_sensor") if self._attr_outdoor_sensor else None
        weather = self.weather_device()
        forecast = []
        if weather:
            info = {"readings": self.values.get(weather, {})}
            forecast = discover.forecast(info)
            if current is None:
                current = discover.current_outdoor(info)
        effective = controller.effective_outdoor(
            current, forecast, max(self._attr_forecast_hours, 1)
        )
        return current, effective

    def room_switch_time(self, room):
        switch = schedule.next_switch(room.week, datetime.datetime.now())
        if switch is None:
            return time.time() + 24 * 3600
        return switch.timestamp()

    def update_room(self, room, now):
        if room.override and room.override[1] <= now:
            room.override = None
            self.create_async_task(self.save_room(room))
        old_target = room.target
        self.update_target(room, now)
        if old_target is not None and abs(old_target - room.target) > 0.01:
            self.last_target_change = now
        room.alerts = self.alerts_of(room)
        self.update_measurements(room)

    @staticmethod
    def schedule_state(room, value):
        """comfort/eco state of a schedule value"""
        if isinstance(value, str):
            return value
        # own temperatures: warm or saving by the eco temperature
        return "comfort" if value > room.eco + 0.01 else "eco"

    def update_target(self, room, now):
        """target temperature and state from vacation, override or schedule"""
        if self.vacation and self.vacation[0] > now:
            room.target, room.state = self.vacation[1], "vacation"
        elif room.override:
            room.target, room.state = room.override[0], "manual"
        else:
            value = schedule.value_at(room.week, datetime.datetime.fromtimestamp(now))
            room.target = room.temp_of(value)
            room.state = self.schedule_state(room, value)

    def update_measurements(self, room):
        """actual temperature, thermostat bias, valve and window of a room"""
        temps, valves, window = self.thermostat_values(room)
        temps = [t for t in temps if t is not None]
        valves = [v for v in valves if v is not None]
        thermostat_temp = sum(temps) / len(temps) if temps else None
        device, reading = room.thermometer
        room_temp = self.value(device, reading) if device else None
        if room_temp is not None:
            room.bias = controller.thermostat_bias(
                room.bias, thermostat_temp, room_temp
            )
            room.actual = room_temp
        else:
            room.bias = None
            room.actual = thermostat_temp
        room.valve = max(valves) if valves else None
        room.window = window
        if window:
            room.state = "window"

    def thermostat_values(self, room):
        """temperatures, valve positions and window state of the thermostats"""
        temps, valves, window = [], [], False
        dead = {a["device"] for a in room.alerts if a["kind"] == "unreachable"}
        for name in room.thermostats:
            thermostat = self.thermostats[name]
            if name not in dead:
                # an unreachable thermostat only has an old temperature
                temps.append(self.value(name, thermostat["temp"]))
            if thermostat["valve"]:
                valves.append(self.value(name, thermostat["valve"]))
            if thermostat["window"]:
                state = str(self.values.get(name, {}).get(thermostat["window"], ""))
                window = window or state.lower() in ("open", "on", "1", "true", "offen")
        return temps, valves, window

    def alerts_of(self, room):
        """thermostats and the room thermometer which can't be reached or
        whose battery is low"""
        alerts = []
        devices = list(room.thermostats)
        if room.thermometer[0] and room.thermometer[0] not in devices:
            devices.append(room.thermometer[0])
        for name in devices:
            readings = self.values.get(name, {})
            label = discover.label(name, self.infos.get(name, {}))
            if discover.unreachable(readings):
                alerts.append({"device": name, "label": label, "kind": "unreachable"})
            low, percent = discover.battery(readings)
            if low:
                alerts.append(
                    {
                        "device": name,
                        "label": label,
                        "kind": "battery",
                        "battery": percent,
                    }
                )
        return alerts

    def alerts_text(self, rooms):
        parts = [
            f"{a['device']}: {'battery low' if a['kind'] == 'battery' else 'unreachable'}"
            for room in rooms
            for a in room.alerts
        ]
        return ", ".join(parts) or "none"

    async def send_set(self, definition):
        result = await fhem.sendCommandHash(
            self.hash, f"CommandSet(undef, {fhem.perlString(definition)})"
        )
        if result:
            self.logger.error(f"set {definition} failed: {result}")
            await fhem.readingsSingleUpdate(
                self.hash, "last_error", f"set {definition}: {result}", 1
            )
            return False
        return True

    async def control_thermostats(self, room, now):
        if room.target is None:
            return
        setpoint = controller.thermostat_setpoint(room.target, room.bias)
        for name in room.thermostats:
            thermostat = self.thermostats[name]
            current = self.value(name, thermostat["target"])
            sent = self.sent_setpoints.get(name)
            if current is not None and abs(current - setpoint) < 0.25:
                continue
            if (
                sent
                and abs(sent[0] - setpoint) < 0.01
                and now - sent[1] < THERMOSTAT_REPEAT
            ):
                continue
            self.sent_setpoints[name] = (setpoint, now, current)
            await self.send_set(f"{name} {thermostat['setter']} {setpoint:g}")

    def settings(self):
        return {
            "design_flow": self._attr_design_flow,
            "design_outdoor": self._attr_design_outdoor,
            "min_flow": self._attr_min_flow,
            "max_flow": self._attr_max_flow,
            "heating_limit": self._attr_heating_limit,
        }

    def flow_target(self, outdoor_eff, rooms):
        targets = [r.target for r in rooms if r.target is not None]
        reference = max(targets) if targets else self._attr_comfort_default
        target = curve.flow_target(
            outdoor_eff, reference, self.settings(), self.learned
        )
        if target is None:
            return None
        boost = controller.room_boost([r.__dict__ for r in rooms])
        return round(
            controller.clamp(target + boost, self._attr_min_flow, self._attr_max_flow),
            1,
        )

    async def control_pump(self, wanted, now):
        device, _ = split_ref(self._attr_pump)
        if self.pump_on is None:
            state = str(self.values.get(device, {}).get("state", "")).lower()
            self.pump_on = state == "on" if device else None
        if wanted is None or not device or wanted == self.pump_on:
            return
        if self.reason != "frost" and now - self.pump_changed < PUMP_MIN_SECONDS:
            return
        if await self.send_set(f"{device} {'on' if wanted else 'off'}"):
            self.pump_on = wanted
            self.pump_changed = now
            if not wanted:
                self.mixer_ctl.reset()

    async def control_mixer(self, position, now):
        device, setter = split_ref(self._attr_mixer)
        if not device or position is None:
            return
        if not setter:
            setter = discover.position_setter(self.infos.get(device, {})) or "pct"
        value = 100 - position if self._attr_mixer_invert else position
        value = int(round(value))
        if (
            self.mixer_sent is not None
            and abs(value - self.mixer_sent) < self._attr_mixer_step
        ):
            return
        wait = self.mixer_sent_at + self._attr_mixer_interval - now
        if wait > 0:
            self.request_evaluation(wait + 0.1)
            return
        if await self.send_set(f"{device} {setter} {value}"):
            self.mixer_sent = value
            self.mixer_sent_at = now

    def pump_power(self):
        device, reading = split_ref(self._attr_pump)
        if device:
            reading = reading or discover.power_reading(
                {"readings": self.values.get(device, {})}
            )
            power = self.value(device, reading) if reading else None
            if power is not None:
                return power
        return discover.number(self._attr_pump_power)

    def flow_rate(self, power):
        if not self.pump_on:
            return 0.0 if self.pump_on is False else None
        fixed = discover.number(self._attr_fixed_flow)
        if fixed:
            return fixed
        model = str(self._attr_pump_model).replace("_", " ")
        flow = pumps.estimate_flow(model, self._attr_pump_setting, power)
        if flow is None:
            return None
        return round(flow * (self._attr_flow_factor or 1.0), 0)

    def count_heat(self, heat_w, now):
        today = datetime.date.today().isoformat()
        if self.heat_day != today:
            self.heat_day = today
            self.heat_today = 0.0
        if heat_w and self.last_eval is not None:
            hours = min(now - self.last_eval, 600) / 3600
            self.heat_today += heat_w * hours / 1000
            self.heat_total += heat_w * hours / 1000

    def learn(self, rooms, outdoor_eff, flow, flow_target, now):
        if self.last_learn is None:
            self.last_learn = now
            return
        if now - self.last_learn < LEARN_MIN_MINUTES * 60:
            return
        hours = min(now - self.last_learn, 3600) / 3600
        self.last_learn = now
        steady = (
            self.mode == "auto"
            and self.pump_on
            and now - self.pump_changed > SETTLE_SECONDS
            and now - self.last_target_change > SETTLE_SECONDS
            and flow is not None
            and flow_target is not None
            and abs(flow - flow_target) < 3
            and not (self.vacation and self.vacation[0] > now)
        )
        if not steady:
            return
        error = controller.learn_error([r.__dict__ for r in rooms])
        if error is not None:
            self.learned.learn(outdoor_eff, error, hours)

    async def evaluate(self):
        if self._stopping:
            return
        now = time.time()
        if self.vacation and self.vacation[0] <= now:
            self.vacation = None
        rooms = list(self.rooms.values())
        for room in rooms:
            self.update_room(room, now)
        current, outdoor_eff = self.outdoor()
        flow = self.sensor("flow_sensor")
        ret = self.sensor("return_sensor")
        supply = self.sensor("supply_sensor")
        target = self.flow_target(outdoor_eff, rooms)
        room_dicts = [r.__dict__ for r in rooms]
        wanted, self.reason = controller.pump_decision(
            bool(self.pump_on), room_dicts, outdoor_eff, self.settings(), (flow, ret)
        )
        if self.mode == "auto":
            for room in rooms:
                await self.control_thermostats(room, now)
            await self.control_pump(wanted, now)
            if self.pump_on or self.reason == "frost":
                seconds = now - self.last_eval if self.last_eval else 0
                position = self.mixer_ctl.position(target, flow, supply, ret, seconds)
                if self.reason == "frost":
                    position = max(position or 0, 30.0)
            else:
                position = 0.0
            await self.control_mixer(position, now)
        power = self.pump_power() if self.pump_on else 0.0
        flow_lh = self.flow_rate(power)
        heat_w = pumps.heat_watts(flow_lh, flow, ret) if self.pump_on else 0.0
        self.count_heat(heat_w, now)
        self.learn(rooms, outdoor_eff, flow, target, now)
        self.last_eval = now
        self.house = {
            "outdoor": current,
            "outdoor_eff": outdoor_eff,
            "flow": flow,
            "flow_target": target,
            "return": ret,
            "supply": supply,
            "mixer": self.mixer_position(),
            "pump": self.pump_on,
            "pump_power": power,
            "flow_lh": flow_lh,
            "heat_w": round(heat_w) if heat_w is not None else None,
            "heat_today": round(self.heat_today, 2),
            "heat_total": round(self.heat_total, 1),
            "reason": self.reason,
        }
        await self.update_readings(rooms)
        self.add_history(now)
        await self.push_live(now)

    def mixer_position(self):
        if self.mixer_sent is not None:
            sent = self.mixer_sent
            return 100 - sent if self._attr_mixer_invert else sent
        device, setter = split_ref(self._attr_mixer)
        value = self.value(device, setter or "pct")
        if value is None:
            return None
        return 100 - value if self._attr_mixer_invert else value

    def state_text(self):
        if self.mode == "setup":
            missing = self.missing()
            return "setup: " + (",".join(missing) if missing else "ready to start")
        if self.mode == "off":
            return "off"
        if self.vacation and self.vacation[0] > time.time():
            return "vacation"
        missing = self.missing()
        if missing:
            return "setup: " + ",".join(missing)
        return self.reason

    def missing(self):
        missing = []
        if not self.rooms:
            missing.append("thermostats")
        for attr in ("mixer", "pump", "flow_sensor"):
            if not getattr(self, "_attr_" + attr):
                missing.append(attr)
        return missing

    async def update_readings(self, rooms):
        house = self.house
        values = {
            "mode": self.mode,
            "outdoor_temp": house["outdoor"],
            "outdoor_effective": house["outdoor_eff"],
            "flow_temp": house["flow"],
            "flow_target": house["flow_target"],
            "return_temp": house["return"],
            "supply_temp": house["supply"],
            "mixer": house["mixer"],
            "pump": "on" if self.pump_on else "off",
            "pump_power": house["pump_power"],
            "flow_rate": house["flow_lh"],
            "heat_power": house["heat_w"],
            "heat_today": f"{self.heat_today:.2f}",
            "heat_energy": f"{self.heat_total:.1f}",
            "heat_day": self.heat_day,
            "learned_curve": self.learned.to_text(),
            "vacation": self.vacation_text(),
            "setup_done": self.setup_done or None,
            "state": self.state_text(),
            "alerts": self.alerts_text(rooms),
        }
        for room in rooms:
            prefix = f"room_{room.key}_"
            values[prefix + "temperature"] = room.actual
            values[prefix + "target"] = room.target
            values[prefix + "state"] = room.state
            values[prefix + "valve"] = room.valve
        await fhem.readingsBeginUpdate(self.hash)
        try:
            for reading, value in values.items():
                if value is None:
                    continue
                if isinstance(value, float):
                    value = f"{value:.1f}"
                await fhem.readingsBulkUpdateIfChanged(self.hash, reading, value)
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    def vacation_text(self):
        if not self.vacation:
            return "off"
        day = datetime.datetime.fromtimestamp(self.vacation[0]).strftime("%Y-%m-%d")
        return f"{day} {self.vacation[1]:g}"

    async def save_room(self, room):
        prefix = f"room_{room.key}_"
        override = (
            f"{room.override[0]:g} {int(room.override[1])}" if room.override else "-"
        )
        # weekprofile has numbers only: comfort/eco become their temperature
        profile = schedule.to_weekprofile(room.week, room.temp_of)
        room.week = schedule.from_weekprofile(profile)
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, prefix + "schedule", profile
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, prefix + "comfort", f"{room.comfort:g}"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, prefix + "eco", f"{room.eco:g}"
            )
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, prefix + "override", override
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    def add_history(self, now):
        if now - self.last_history < HISTORY_STEP:
            return
        self.last_history = now
        h = self.house
        self.history.append(
            [
                int(now),
                h["flow"],
                h["flow_target"],
                h["return"],
                h["supply"],
                h["outdoor"],
                h["mixer"],
                1 if self.pump_on else 0,
                h["heat_w"],
            ]
        )
        cutoff = now - HISTORY_SECONDS
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()

    async def push_live(self, now):
        if now - self.last_live < LIVE_STEP:
            return
        self.last_live = now
        data = self.live_view()
        script = "if(window.fhcLive)fhcLive(" + render.js_json(data) + ")"
        await fhem.FW_runJavascript(self.hash, script, self.hash["NAME"])
        # the page in the room of its own
        for room in self.own_rooms:
            if room == self.control_room:
                await fhem.FW_runJavascript(self.hash, script, "room=" + room)

    def live_view(self):
        data = self.view(history=False)
        if self.history:
            data["point"] = self.history[-1]
        return data

    # --- detail page data ---

    def options(self, candidates, role):
        ranked = discover.ranked(role, candidates, self.infos)
        result = []
        for candidate in ranked:
            device = candidate[0]
            extra = candidate[1] if len(candidate) > 1 and candidate[1] else ""
            value = f"{device}:{extra}" if extra else device
            label = discover.label(device, self.infos.get(device, {}))
            if extra:
                label += f" ({extra})"
            reading_value = (
                self.values.get(device, {}).get(extra) if role != "mixer" else None
            )
            if reading_value is not None and role != "pump":
                label += f" = {reading_value}"
            result.append([value, label])
        return result

    def setup_view(self):
        temps = self.found["temperatures"]
        roles = {}
        for attr, role, candidates in (
            ("mixer", "mixer", self.found["mixers"]),
            ("pump", "pump", self.found["pumps"]),
        ):
            suggestion = discover.suggest(role, candidates, self.infos)
            roles[attr] = {
                "value": getattr(self, "_attr_" + attr),
                "options": self.options(candidates, role),
                "suggestion": (
                    ":".join(s for s in suggestion if s) if suggestion else ""
                ),
            }
        sensors = {}
        for attr, role in (
            ("flow_sensor", "flow"),
            ("return_sensor", "return"),
            ("supply_sensor", "supply"),
            ("outdoor_sensor", "outdoor"),
        ):
            suggestion = discover.suggest(role, temps, self.infos)
            sensors[attr] = {
                "value": getattr(self, "_attr_" + attr),
                "suggestion": ":".join(suggestion) if suggestion else "",
            }
        thermometers = {}
        for room in self.rooms.values():
            candidates = discover.room_thermometers(room.name, self.found, self.infos)
            thermometers[room.key] = {
                "value": ":".join(r for r in room.thermometer if r) or "",
                "suggestion": ":".join(candidates[0]) if candidates else "",
            }
        # thermometer suggestion by FHEM room, for rooms named in the setup
        room_thermometers = {}
        for thermostat in self.found["thermostats"].values():
            room = thermostat["room"]
            candidates = discover.room_thermometers(room, self.found, self.infos)
            if candidates and room not in room_thermometers:
                room_thermometers[room] = ":".join(candidates[0])
        model = str(self._attr_pump_model).replace("_", " ")
        return {
            "roles": roles,
            "weather": {
                "value": self._attr_weather,
                "found": self.found["weather"],
                "used": self.weather_device() or "",
            },
            "pump_model": model,
            "pump_models": pumps.model_names(),
            "pump_setting": self._attr_pump_setting,
            "pump_settings": pumps.settings_of(model),
            "pump_settings_all": pumps.settings_of(None),
            "no_autoadapt": [
                m
                for m in pumps.model_names()
                if "AUTOADAPT" not in pumps.settings_of(m)
            ],
            "mixer_invert": bool(self._attr_mixer_invert),
            "pump_power": self._attr_pump_power,
            "sensors": sensors,
            "thermometers": thermometers,
            "room_thermometers": room_thermometers,
            "devices": self.sensor_devices(),
            "missing": self.missing(),
            "thermostats": self.thermostats_view(),
            # what the control will switch, shown before the user starts it
            "controlled": {
                "mixer": split_ref(self._attr_mixer)[0] or "",
                "pump": split_ref(self._attr_pump)[0] or "",
                "thermostats": sorted(self.thermostats),
            },
        }

    def assigned_rooms(self):
        """own rooms of the thermostats (attribute thermostat_rooms)"""
        result = {}
        for part in str(self._attr_thermostat_rooms or "").split(","):
            name, sep, room = part.partition("=")
            if sep and name.strip() and room.strip():
                result[name.strip()] = room.strip()
        return result

    def room_of(self, thermostat):
        found = self.found["thermostats"].get(thermostat, {})
        return self.assigned_rooms().get(thermostat) or found.get("room") or thermostat

    def thermostats_view(self):
        """all found thermostats, also the excluded ones, for the setup"""
        result = []
        for name, thermostat in self.found["thermostats"].items():
            info = self.infos.get(name, {})
            result.append(
                {
                    "name": name,
                    "label": discover.label(name, info),
                    "room": self.room_of(name),
                    "fhem_room": thermostat["room"],
                    "temp": self.value(name, thermostat["temp"]),
                    "used": name in self.thermostats,
                }
            )
        return sorted(result, key=lambda t: (t["room"].lower(), t["label"].lower()))

    def sensor_devices(self):
        """[name, label] of all devices with number readings, devices with
        a temperature reading first"""
        with_temp = {device for device, _ in self.found["temperatures"]}
        devices = sorted(
            self.numeric_devices,
            key=lambda d: (d[0] not in with_temp, (d[1] or d[0]).lower()),
        )
        return [
            [name, f"{alias} ({name})" if alias else name] for name, alias in devices
        ]

    def curve_view(self, outdoor_eff):
        targets = [r.target for r in self.rooms.values() if r.target is not None]
        room = max(targets) if targets else self._attr_comfort_default
        points = []
        empty = curve.Learned()
        for outdoor in range(-15, 21):
            points.append(
                [
                    outdoor,
                    round(curve.flow_target(outdoor, room, self.settings(), empty), 1),
                    round(
                        curve.flow_target(outdoor, room, self.settings(), self.learned),
                        1,
                    ),
                ]
            )
        return {
            "points": points,
            "current": [outdoor_eff, self.house.get("flow_target")],
            "hours": round(self.learned.total_hours(), 1),
            "limit": self._attr_heating_limit,
        }

    def view(self, history=True):
        data = {
            "name": self.hash["NAME"] if hasattr(self, "hash") else "",
            "mode": self.mode,
            "heat_source": self._attr_heat_source,
            "state": self.state_text(),
            "house": self.house,
            "rooms": [room.view() for room in self.rooms.values()],
            "vacation": {
                "active": bool(self.vacation and self.vacation[0] > time.time()),
                "until": self.vacation_text().split()[0] if self.vacation else "",
                "temp": (
                    self.vacation[1] if self.vacation else self._attr_vacation_default
                ),
            },
            "now": int(time.time()),
            "control_room": (
                self.control_room if self.control_room in self.own_rooms else ""
            ),
        }
        if history:
            data["history"] = list(self.history)
            data["curve"] = self.curve_view(self.house.get("outdoor_eff"))
            data["setup"] = self.setup_view()
        return data

    # --- set commands ---

    def find_rooms(self, name):
        name = str(name).strip()
        if name.lower() in ("all", "alle"):
            return list(self.rooms.values())
        key = room_key(name)
        if key in self.rooms:
            return [self.rooms[key]]
        for room in self.rooms.values():
            if room.name.lower() == name.lower() or room.key.lower() == key.lower():
                return [room]
        raise ValueError(f"Unknown room {name}, rooms: {', '.join(self.rooms)}")

    @staticmethod
    def temperature(value):
        temp = discover.number(value)
        if temp is None or not 5 <= temp <= 30:
            raise ValueError(f"temperature {value} must be 5-30")
        return controller.round_half(temp)

    async def changed(self, rooms):
        for room in rooms:
            await self.save_room(room)
        self.last_target_change = time.time()
        self.schedule_timer()
        await self.evaluate()
        return ""

    async def set_mode(self, hash, params):
        mode = params["mode"]
        if mode not in MODES:
            return f"mode must be one of {', '.join(MODES)}"
        if mode == "auto":
            missing = self.missing()
            if missing:
                return "Finish the setup first, missing: " + ", ".join(missing)
            if not self.setup_done:
                self.setup_done = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.mode = mode
        self.logger.info(f"mode {mode}")
        await self.evaluate()
        return ""

    async def set_room_temp(self, hash, params):
        try:
            rooms = self.find_rooms(params["room"])
            if str(params["temperature"]).lower() == "auto":
                for room in rooms:
                    room.override = None
            else:
                temp = self.temperature(params["temperature"])
                for room in rooms:
                    room.override = (temp, self.room_switch_time(room))
        except ValueError as exc:
            return str(exc)
        return await self.changed(rooms)

    async def _set_level(self, params, attr):
        try:
            rooms = self.find_rooms(params["room"])
            temp = self.temperature(params["temperature"])
        except ValueError as exc:
            return str(exc)
        for room in rooms:
            setattr(room, attr, temp)
        return await self.changed(rooms)

    async def set_comfort_temp(self, hash, params):
        return await self._set_level(params, "comfort")

    async def set_eco_temp(self, hash, params):
        return await self._set_level(params, "eco")

    async def set_schedule(self, hash, params):
        try:
            rooms = self.find_rooms(params["room"])
            week = schedule.parse(params["schedule"])
        except ValueError as exc:
            return str(exc)
        for room in rooms:
            room.week = {day: list(points) for day, points in week.items()}
        return await self.changed(rooms)

    async def set_copy_schedule(self, hash, params):
        try:
            source = self.find_rooms(params["from"])[0]
            rooms = [r for r in self.find_rooms(params["to"]) if r is not source]
        except ValueError as exc:
            return str(exc)
        for room in rooms:
            room.week = {day: list(points) for day, points in source.week.items()}
            room.comfort, room.eco = source.comfort, source.eco
        return await self.changed(rooms)

    async def set_vacation(self, hash, params):
        try:
            until = parse_until(params["until"], datetime.datetime.now())
            temp = params.get("temperature")
            temp = self.temperature(temp) if temp else self._attr_vacation_default
        except ValueError as exc:
            return str(exc)
        if until.timestamp() <= time.time():
            return "The day back home has to be in the future."
        self.vacation = (until.timestamp(), temp)
        for room in self.rooms.values():
            room.override = None
        return await self.changed(list(self.rooms.values()))

    async def set_vacation_off(self, hash, params):
        self.vacation = None
        return await self.changed([])

    async def set_reset_learning(self, hash, params):
        self.learned.reset()
        await self.evaluate()
        return ""

    async def set_rescan(self, hash, params):
        await self.reload()
        return ""

    async def set_create_room(self, hash, params):
        default = (
            "Heizungssteuerung" if self.language.upper().startswith("DE") else "Heating"
        )
        room = re.sub(r"[,\s]+", "_", str(params.get("room") or default)).strip("_")
        if not room:
            return "room name missing"
        # FHEM waits for this set, the attribute commands run after it
        self.control_room = room
        self.create_async_task(self.create_room(room))
        return ""

    async def create_room(self, room):
        # alone in the room the page replaces the device row (fhempy_summaryFn)
        result = await fhemweb.add_room(self.hash, room, ROOM_ICON)
        if result:
            self.logger.error(f"create_room {room}: {result}")
            return
        await fhem.readingsSingleUpdate(self.hash, ".control_room", room, 0)
        self.own_rooms = await self.read_own_rooms()

    async def get_page(self, hash, params):
        return render.page(self.view(), self.language, room=True)

    async def get_live(self, hash, params):
        return json.dumps(self.live_view(), default=str)
