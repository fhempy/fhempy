"""Tablet dashboard: a modern web app for wall, couch and door tablets.

The tablets connect to an own small web server of fhempy (not FHEMWEB), get
rooms and tiles built from the FHEM devices (model.py) and live values over a
WebSocket. A tablet is added by scanning a QR code with a one-time code, it
gets its own token then (no login, no expiry). Every tablet keeps its own
place (wall, couch, door), room, layout and restrictions."""

import asyncio
import datetime
import functools
import hashlib
import hmac
import html
import json
import os
import platform
import re
import secrets
import ssl
import tempfile
import time

from .. import fhem, generic, utils
from ..version import __version__
from . import go2rtc, media, model, views

DEFAULT_PORT = 8095
DEFAULT_HTTPS_PORT = 8096
PAIR_CODE_LIFETIME = 600
PAIR_CODES_MAX = 5
PAIR_FAILS_MAX = 10
PAIR_FAILS_WINDOW = 60
RELOAD_DELAY = 2
RING_REPEAT = 20
MAX_MESSAGE_SIZE = 64 * 1024
MAX_SDP_SIZE = 32 * 1024
MAX_IMAGE_SIZE = 3 * 1024 * 1024
IMAGE_CACHE = 40
# the header (warnings, running devices, energy) is built at most this often
HEADER_DELAY = 0.5
# "All off": devices per group, seconds between groups and until the check
# which devices are still on
ALL_OFF_GROUP = 4
ALL_OFF_PAUSE = 0.4
ALL_OFF_CHECK = 6


# settings stay open this long after the PIN, wrong PINs: PIN_TRIES within
# PIN_WAIT seconds, then no more tries until PIN_WAIT passed
PIN_OPEN = 10 * 60
PIN_TRIES = 5
PIN_WAIT = 5 * 60


# seconds between reading the calendars
CALENDAR_INTERVAL = 300
# seconds between the checks if a washing machine is done
APPLIANCE_INTERVAL = 60
# "Laundry done" stays this long on Home unless somebody ticks it off
APPLIANCE_DONE_HOURS = 12
ATTRS_TEXT = (
    "devices",
    "hidden_devices",
    "doorbell",
    "cameras",
    "go2rtc",
    "door_camera",
    "door_opener",
    "keep_on",
    "measure_only",
    "notices",
    "floors",
    "may_open",
    "appliances",
    "alarm_system",
    "alarm_pin",
    "device_views",
    "energy_price",
)
PLACES = ("wall", "couch", "door")
PLACE_NAMES = {"wall": "Wall", "couch": "Couch", "door": "Door"}
WWW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
STATIC_FILES = {
    "index.html": "text/html; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
    "app.css": "text/css; charset=utf-8",
    "sw.js": "application/javascript; charset=utf-8",
    "manifest.webmanifest": "application/manifest+json",
    "icon.svg": "image/svg+xml",
    "icon-192.png": "image/png",
    "icon-512.png": "image/png",
    # texts of the language of the tablet, see lang_script
    "lang.js": "application/javascript; charset=utf-8",
}
# more languages than German and English: www/lang/<code>.json
LANGUAGES = ("de", "en", "fr", "it", "nl")
# never on a tablet
EXCLUDED_TYPES = (
    "FHEMWEB",
    "telnet",
    "Global",
    "FileLog",
    "DbLog",
    "notify",
    "at",
    "DOIF",
    "watchdog",
    "SVG",
    "weblink",
    "eventTypes",
    "autocreate",
    "allowed",
    "readingsGroup",
    "readingsProxy",
    "HMinfo",
    "MQTT2_SERVER",
    "MQTT2_CLIENT",
)
ARRANGE_MESSAGES = (
    "rooms_setup",
    "move_device",
    "rename_room",
    "keep_on",
    "delete_device",
    "device_view",
    "measure_only",
    "floors",
)
# changes of settings, layout and rooms: only with the PIN when one is set
LOCKED_MESSAGES = ARRANGE_MESSAGES + (
    "setup",
    "layout",
    "notice",
    "appliance",
    "energy_price",
    "may_open",
)
RELOAD_ATTRS = (
    "room",
    "alias",
    "genericDeviceType",
    "matterType",
    "disable",
    "setList",
)
LAYOUT_KEYS = (
    "room_order",
    "hidden_rooms",
    "hidden_tiles",
    "tile_order",
    "theme",
    "start",
    "tile_size",
    "accent",
    "lite",
    "saver",
)
# small, wide, tall, big
TILE_SIZES = ("s", "w", "t", "b")
ACCENTS = ("amber", "teal", "blue", "violet", "pink", "green", "lamps")
# minutes until the screensaver, 0: never
SAVER_MINUTES = (0, 2, 5, 10, 15, 30)
SETTINGS_ATTRS = (
    "devices",
    "hidden_devices",
    "doorbell",
    "door_camera",
    "door_opener",
)


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def clean_layout(layout):
    """layout of a tablet as sent by the tablet: only lists of strings"""
    result = {}
    if not isinstance(layout, dict):
        return result
    for key in LAYOUT_KEYS:
        value = layout.get(key)
        if key == "tile_order" and isinstance(value, dict):
            result[key] = {
                str(room)[:100]: [str(v)[:200] for v in ids[:500]]
                for room, ids in list(value.items())[:200]
                if isinstance(ids, list)
            }
        elif key == "tile_size" and isinstance(value, dict):
            result[key] = {
                str(tile)[:200]: size
                for tile, size in list(value.items())[:1000]
                if size in TILE_SIZES
            }
        elif key == "theme" and value in ("auto", "dark", "light"):
            result[key] = value
        elif key == "start" and value == "cameras":
            result[key] = value
        elif key == "accent" and value in ACCENTS:
            result[key] = value
        elif key == "lite" and value in ("auto", "on", "off"):
            result[key] = value
        elif key == "saver" and not isinstance(value, bool) and value in SAVER_MINUTES:
            result[key] = value
        elif isinstance(value, list):
            result[key] = [str(v)[:200] for v in value[:500]]
    return result


def parse_opener(text):
    """'Door_opener on' -> ('Door_opener', 'on')"""
    device, _, args = str(text or "").strip().partition(" ")
    if not device or not args.strip():
        return None
    return device, args.strip()


async def read_limited(stream, limit):
    """whole body of a response, at most limit bytes: StreamReader.read(n)
    returns only what has arrived so far, which cut covers off after the
    first network chunk"""
    chunks = []
    size = 0
    while True:
        chunk = await stream.read(64 * 1024)
        if not chunk:
            return b"".join(chunks)
        size += len(chunk)
        if size > limit:
            raise ValueError("image too big")
        chunks.append(chunk)


def qr_image(text):
    import segno

    uri = segno.make(text, micro=False, error="m").png_data_uri(
        scale=5, border=4, dark="#000", light="#fff"
    )
    return (
        f'<img src="{uri}" alt="QR code" '
        'style="width:200px;height:200px;max-width:none;image-rendering:pixelated">'
    )


def parse_message(msg, text_type):
    """JSON object of a WebSocket text message, None for anything else"""
    if msg.type != text_type:
        return None
    try:
        message = json.loads(msg.data)
    except ValueError:
        return None
    return message if isinstance(message, dict) else None


def read_static(path):
    with open(path, "rb") as file:
        return file.read()


BUILD_MARK = b"__DASHBOARD_BUILD__"


def www_build():
    """short hash of the app files: changes with every fhempy update that
    changes the dashboard. app.js gets it built in, so a tablet running old
    code from its cache notices the new version."""
    digest = hashlib.sha256()
    names = ["app.js", "app.css"]
    names += [os.path.join("lang", f"{code}.json") for code in LANGUAGES[2:]]
    for name in names:
        try:
            digest.update(read_static(os.path.join(WWW_DIR, name)))
        except OSError:
            pass
    return digest.hexdigest()[:12]


def choose_language(cookie, accept):
    """language of a tablet: chosen in its settings (cookie), otherwise the
    first language of the browser the dashboard knows, otherwise English"""
    if cookie in LANGUAGES:
        return cookie
    for part in str(accept or "").split(","):
        code = part.split(";")[0].strip()[:2].lower()
        if code in LANGUAGES:
            return code
    return "en"


def lang_script(code):
    """lang.js: window.DASH_LANG with the texts of www/lang/<code>.json"""
    data = {"code": code}
    if code in LANGUAGES[2:]:
        try:
            found = json.loads(
                read_static(os.path.join(WWW_DIR, "lang", f"{code}.json"))
            )
            data.update(found)
        except (OSError, ValueError):
            data = {"code": "en"}
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"window.DASH_LANG = {text};\n".encode()


def server_ssl_context(ca_key, ca_cert, ip):
    """certificate for all local names of this host, signed by the own CA"""
    from ..push import certs

    names = [ip] + [n for n in certs.local_names() if n != ip]
    key, cert = certs.create_server_cert(ca_key, ca_cert, names)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    with tempfile.TemporaryDirectory() as tmp:
        cert_file = os.path.join(tmp, "cert.pem")
        key_file = os.path.join(tmp, "key.pem")
        with open(cert_file, "w", encoding="utf-8") as file:
            file.write(certs.cert_pem(cert) + certs.cert_pem(ca_cert))
        with open(key_file, "w", encoding="utf-8") as file:
            file.write(certs.key_pem(key))
        context.load_cert_chain(cert_file, key_file)
    return context


class dashboard(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.runners = []
        self._server_lock = asyncio.Lock()
        self.ip = "127.0.0.1"
        self.infos = {}
        self._arrange_infos = {}
        self.data = {"rooms": [], "tiles": {}, "scenes": []}
        self.head = {}
        # devices the header is built from, see model.in_header
        self._head_infos = {}
        self._header_task = None
        self.tablets = {}
        # device -> end of its "switch off in" timer (epoch seconds)
        self.timers = {}
        # tablet id -> {"until": epoch, "steps": [...]} of good night / leaving
        self.undo = {}
        self.codes = {}
        self.build = www_build()

        # tablet id -> end of the time the settings are open after the PIN
        self.unlocked = {}
        # tablet id -> times of wrong PINs
        self.pin_fails = {}
        self.pair_fails = []
        self.clients = {}
        self._listening = []
        self._reload_task = None
        self._unique_id = None
        self.cameras = go2rtc.Go2rtc(logger)
        self.streams = []
        self.last_ring = 0
        self.https_ready = False
        self.doorbells = []
        self.sun = None
        # entries of the FHEM Calendar devices, see model.parse_calendar
        self.calendar_events = []
        # device -> reading time of a notice ticked off on a tablet
        self.dismissed = {}

        # device -> model.ApplianceWatch of plugs which report their power
        self.watches = {}
        # learned: durations of programs, done time, plugs to ask about
        self.appliance_data = {"cycles": {}, "done": {}, "ask": []}
        self.ca_pem = ""
        # covers of the presets of music players, learned while they play
        self.preset_art = {}
        self._preset_learners = {}
        self._images = {}
        # until Define has read the attributes, e.g. when FHEMWEB shows the
        # device page right after define
        self.ready = False
        self._attr_port = DEFAULT_PORT
        self._attr_https_port = DEFAULT_HTTPS_PORT
        for name in ATTRS_TEXT:
            setattr(self, "_attr_" + name, "")

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        attr_config = {
            "port": {
                "default": str(DEFAULT_PORT),
                "format": "int",
                "help": f"Network port of the dashboard, default {DEFAULT_PORT}.",
            },
            "https_port": {
                "default": str(DEFAULT_HTTPS_PORT),
                "format": "int",
                "help": "Port of the https address, needed to talk at the door "
                f"(microphone), default {DEFAULT_HTTPS_PORT}. 0: no https.",
            },
            "devices": {
                "default": "",
                "help": "Only these devices are shown, e.g. room=Livingroom,"
                "Kitchen. Empty: all devices with a room.",
            },
            "hidden_devices": {
                "default": "",
                "help": "These devices are never shown on the tablets, "
                "e.g. Alarm_system,TYPE=CUL_HM.",
            },
            "doorbell": {
                "default": "",
                "help": "Doorbell devices, e.g. Doorbell or Bell:action. Empty: "
                "devices with klingel/doorbell in the name and ring devices.",
            },
            "cameras": {
                "default": "",
                "help": "Cameras for the tablets as name=address, separated by "
                "spaces, e.g. Door=rtsp://user:pass@192.168.1.20/stream1. fhempy "
                "downloads go2rtc for them. Not needed with attribute go2rtc.",
            },
            "go2rtc": {
                "default": "",
                "help": "Address of an existing go2rtc (e.g. of Frigate or Home "
                "Assistant), e.g. http://192.168.1.5:1984. Its cameras are used.",
            },
            "door_camera": {
                "default": "",
                "help": "Camera shown when somebody rings (name of the go2rtc "
                "stream). Empty: the first camera.",
            },
            "door_opener": {
                "default": "",
                "help": "Command of the door opener without set, e.g. "
                "Door_opener on. The tablet at the door shows 'Slide to open'.",
            },
            "settings_pin": {
                "default": "",
                "help": "PIN of 4 to 8 digits for the settings, arranging rooms "
                "and editing tiles on the tablets. After the PIN they stay open "
                "for 10 minutes. Empty: no PIN.",
            },
            "floors": {
                "default": "",
                "help": "Rooms grouped by floor on Home, e.g. "
                "Ground floor=Kitchen,Living room;Upstairs=Bath,Bedroom. "
                "Also set on the tablets in the settings.",
            },
            "may_open": {
                "default": "",
                "help": "Doors and gates which may be open at some times without "
                "a warning, e.g. Yard_gate=07:00-20:00,Garage=08:00-18:00. "
                "Also set on the tablets in the details of a door.",
            },
            "notices": {
                "default": "",
                "help": "Own notices on Home while a device has a value, "
                "separated by ';': device[:reading][=value] text, e.g. "
                "Mailbox Mail is here; Basement:water=wet Water in the basement. "
                "Without =value: while it is on/open/1. Also set on the tablets "
                "in the details of a device.",
            },
            "device_views": {
                "default": "",
                "help": "Own views of devices, e.g. Robby:vacuum,Valve_garden:"
                "irrigation,Plug:none. Views: vacuum, car, wallbox, heatpump, "
                "irrigation, none: a normal tile. Empty: found by their set "
                "commands and readings. Also set on the tablet.",
            },
            "energy_price": {
                "default": "",
                "help": "Price of electricity in €/kWh for the energy page, "
                "optional with the feed-in tariff, e.g. 0.32 or 0.32,0.08. A "
                "price reading of a device (e.g. tibber) wins. Also set on the "
                "tablet.",
            },
            "appliances": {
                "default": "",
                "help": "Plugs of a washing machine, dryer or dishwasher, e.g. "
                "Plug_basement:washer,Plug_kitchen:dishwasher (none: no "
                "appliance). The tablets ask after the first program found by "
                "the power, this is set by their answer.",
            },
            "alarm_system": {
                "default": "",
                "help": "Alarm system the tablets arm and disarm, e.g. "
                "Alarm_system. Its set commands are used: armAway/armed/arm/on, "
                "armHome/home/night and disarm/disarmed/off. A state with "
                "alarm or triggered shows the alarm on all tablets.",
            },
            "alarm_pin": {
                "default": "",
                "help": "PIN of 4 to 8 digits to disarm the alarm system on the "
                "tablets. FHEM checks it, the tablets never get it. Empty: "
                "disarming needs a second tap.",
            },
            "measure_only": {
                "default": "",
                "help": "Plugs which only measure, e.g. of a fridge or freezer: "
                "the tablets show their power but never switch them, also not "
                "with All off. Separated by commas. Also set on the tablets in "
                "the details of a plug.",
            },
            "keep_on": {
                "default": "",
                "help": "Devices which 'All off' leaves on, e.g. heating, heat "
                "pump or fridge plugs, separated by commas. none: all are "
                "switched off. Empty: found by their name. Also set on the "
                "tablets in the details of a device.",
            },
        }
        await self.set_attr_config(attr_config)
        await self.set_icon("it_television")
        self._unique_id = await fhem.getUniqueId(hash)
        await self.load_tablets()
        await self.load_timers()
        await self.load_preset_art()
        await self.load_appliances()
        await self.update_set_config()
        self.ip = await utils.run_blocking(functools.partial(utils.get_local_ip))
        await self.reload()
        await self.start_server()
        self.ready = True
        self.create_async_task(self.start_cameras())
        self.create_async_task(self.calendar_loop())
        self.create_async_task(self.appliance_loop())

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await self.stop_server()
        await self.cameras.stop()
        for name in self._listening:
            fhem.unregister_event_listener(name, self.handle_event)
            fhem.unregister_event_listener(name, self.handle_global_event)
        self._listening = []
        await super().Undefine(hash)

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        if not self.ready:
            return (
                '<div class="makeTable wide"><span class="mkTitle">Tablets</span>'
                '<table class="block wide"><tr><td>The dashboard is starting, '
                "reload this page in a moment.</td></tr></table></div>" + str(detail)
            )
        return self.setup_html() + str(detail)

    # --- tablets ---

    async def load_tablets(self):
        raw = await fhem.ReadingsVal(self.hash["NAME"], ".tablets", "")
        try:
            tablets = json.loads(raw) if raw else {}
        except ValueError:
            self.logger.error("Failed to read the tablets, they have to be added again")
            tablets = {}
        self.tablets = tablets if isinstance(tablets, dict) else {}

    async def save_tablets(self):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(
            self.hash, ".tablets", json.dumps(self.tablets, ensure_ascii=False)
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "tablets",
            ",".join(t["name"] for t in self.tablets.values()) or "none",
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        await self.update_set_config()
        await self.update_state()

    async def load_preset_art(self):
        raw = await fhem.ReadingsVal(self.hash["NAME"], ".preset_art", "")
        try:
            known = json.loads(raw) if raw else {}
        except ValueError:
            known = {}
        self.preset_art = known if isinstance(known, dict) else {}

    async def save_preset_art(self):
        await fhem.readingsSingleUpdate(
            self.hash,
            ".preset_art",
            json.dumps(self.preset_art, ensure_ascii=False),
            0,
        )

    def new_pair_code(self):
        now = time.time()
        self.codes = {c: t for c, t in self.codes.items() if t > now}
        while len(self.codes) >= PAIR_CODES_MAX:
            self.codes.pop(min(self.codes, key=self.codes.get))
        code = f"{secrets.randbelow(1000000):06d}"
        self.codes[code] = now + PAIR_CODE_LIFETIME
        return code

    def check_pair_code(self, code):
        now = time.time()
        self.pair_fails = [t for t in self.pair_fails if t > now - PAIR_FAILS_WINDOW]
        if len(self.pair_fails) >= PAIR_FAILS_MAX:
            return False
        expires = self.codes.pop(str(code), None)
        if expires is None or expires < now:
            self.pair_fails.append(now)
            return False
        return True

    async def add_tablet(self, device=""):
        token = secrets.token_urlsafe(24)
        tablet_id = secrets.token_hex(4)
        number = len(self.tablets) + 1
        names = {t["name"] for t in self.tablets.values()}
        while f"Tablet{number}" in names:
            number += 1
        self.tablets[tablet_id] = {
            "id": tablet_id,
            "name": f"Tablet{number}",
            "device": str(device)[:40],
            "token": token_hash(token),
            "place": "",
            "room": "",
            "layout": {},
            "rooms": [],
            "readonly": False,
            "created": now_text(),
        }
        await self.save_tablets()
        self.logger.info(f"New tablet {self.tablets[tablet_id]['name']}")
        return token, self.tablets[tablet_id]

    def tablet_by_token(self, token):
        if not token:
            return None
        wanted = token_hash(str(token))
        for tablet in self.tablets.values():
            if hmac.compare_digest(tablet.get("token", ""), wanted):
                return tablet
        return None

    def tablet_of_request(self, request):
        header = request.headers.get("Authorization", "")
        token = header[7:].strip() if header[:7].lower() == "bearer " else ""
        return self.tablet_by_token(token)

    def public_tablet(self, tablet):
        result = {
            k: tablet.get(k)
            for k in ("id", "name", "place", "room", "layout", "rooms", "readonly")
        }
        result["https"] = self.https_url() if self.https_ready else ""
        result["arrange"] = self.can_arrange(tablet)
        result["timeline"] = self.sees_timeline(tablet)
        result["pin"] = self.settings_pin() is not None
        return result

    @staticmethod
    def sees_timeline(tablet):
        """set tablet_timeline <tablet> 0 hides what happened at home"""
        return tablet.get("timeline", True) is not False

    # --- set commands ---

    def set_config(self):
        config = {
            "refresh": {"help": "Read rooms and devices again."},
            "test_ring": {
                "help": "Show on all tablets what happens when somebody rings."
            },
        }
        if self.tablets:
            options = ",".join(t["name"] for t in self.tablets.values())
            config["remove_tablet"] = {
                "args": ["tablet"],
                "options": options,
                "help": "The tablet can't connect anymore, it has to scan the "
                "QR code again.",
            }
            config["rename_tablet"] = {
                "args": ["tablet", "new_name"],
                "help": "Give a tablet a name, e.g. Kitchen.",
            }
            config["tablet_rooms"] = {
                "args": ["tablet", "rooms"],
                "help": "Rooms a tablet may show, comma separated, e.g. "
                "Kids_room. all: every room.",
            }
            config["tablet_readonly"] = {
                "args": ["tablet", "readonly"],
                "options": "0,1",
                "help": "1: the tablet only shows, it can't switch anything.",
            }
            config["tablet_timeline"] = {
                "args": ["tablet", "timeline"],
                "options": "0,1",
                "help": "0: the tablet doesn't show the timeline (what happened "
                "at home, history of devices), 1: it does (default).",
            }
        return config

    async def update_set_config(self):
        await self.set_set_config(self.set_config())

    async def Set(self, hash, args, argsh):
        try:
            return await super().Set(hash, args, argsh)
        except ValueError as err:
            return str(err)

    def _tablet_by_name(self, name):
        for tablet in self.tablets.values():
            if tablet["name"] == name:
                return tablet
        raise ValueError(f"Unknown tablet {name}")

    async def set_refresh(self, hash, params):
        await self.reload()

    async def set_test_ring(self, hash, params):
        await self.ring({"id": "", "name": "Test"}, force=True)

    async def set_remove_tablet(self, hash, params):
        tablet = self._tablet_by_name(params["tablet"])
        self.tablets.pop(tablet["id"], None)
        await self.save_tablets()
        for ws, tablet_id in self.connected():
            if tablet_id == tablet["id"]:
                await ws.close()

    async def set_rename_tablet(self, hash, params):
        tablet = self._tablet_by_name(params["tablet"])
        new_name = str(params["new_name"]).strip()[:40]
        if not new_name:
            raise ValueError("Name missing")
        tablet["name"] = new_name
        await self.save_tablets()
        await self.send_tablet(tablet)

    async def set_tablet_rooms(self, hash, params):
        tablet = self._tablet_by_name(params["tablet"])
        rooms = str(params["rooms"]).strip()
        tablet["rooms"] = (
            [] if rooms in ("", "all") else [r for r in rooms.split(",") if r]
        )
        await self.save_tablets()
        await self.send_tablet(tablet, with_model=True)

    async def set_tablet_readonly(self, hash, params):
        tablet = self._tablet_by_name(params["tablet"])
        tablet["readonly"] = str(params["readonly"]) == "1"
        await self.save_tablets()
        await self.send_tablet(tablet)

    async def set_tablet_timeline(self, hash, params):
        tablet = self._tablet_by_name(params["tablet"])
        tablet["timeline"] = str(params["timeline"]) != "0"
        await self.save_tablets()
        await self.send_tablet(tablet)

    async def set_attr_port(self, hash):
        await self.start_server()

    async def set_attr_https_port(self, hash):
        await self.start_server()

    def set_attr_cameras(self, hash):
        self.create_async_task(self.start_cameras())

    def set_attr_go2rtc(self, hash):
        self.create_async_task(self.start_cameras())

    def set_attr_devices(self, hash):
        self.schedule_reload()

    def set_attr_notices(self, hash):
        self.schedule_reload()

    def set_attr_floors(self, hash):
        if self.ready:
            self.schedule_header()

    def set_attr_may_open(self, hash):
        self.schedule_reload()

    def set_attr_appliances(self, hash):
        if self.ready:
            self.schedule_header()

    def set_attr_keep_on(self, hash):
        self.schedule_reload()

    def set_attr_measure_only(self, hash):
        self.schedule_reload()

    def set_attr_hidden_devices(self, hash):
        self.schedule_reload()

    def set_attr_doorbell(self, hash):
        self.schedule_reload()

    def set_attr_door_camera(self, hash):
        self.schedule_reload()

    def set_attr_door_opener(self, hash):
        self.schedule_reload()

    def set_attr_alarm_system(self, hash):
        self.schedule_reload()

    def set_attr_alarm_pin(self, hash):
        self.schedule_reload()

    def set_attr_settings_pin(self, hash):
        # a new PIN closes the settings everywhere
        self.unlocked = {}
        self.pin_fails = {}
        if self.ready:
            self.create_async_task(self.send_all_tablets())

    async def send_all_tablets(self):
        for tablet in list(self.tablets.values()):
            await self.send_tablet(tablet)

    # --- FHEM devices ---

    async def resolve_devices(self, any_room=False):
        spec = (self._attr_devices or "").strip()
        hidden = (self._attr_hidden_devices or "").strip()
        bell = self.doorbell_spec()[0]
        excluded = "|".join(EXCLUDED_TYPES)
        special_types = "|".join(
            model.PRESENCE_TYPES
            + model.PRESENCE_DEVICE_TYPES
            + model.WEATHER_TYPES
            + model.SCENE_TYPES
        )
        special_fhempy = "|".join(model.SPECIAL_FHEMPY_TYPES)
        cmd = (
            f"my $spec = {fhem.perlString(spec)};"
            f" my $hidden = {fhem.perlString(hidden)};"
            f" my $bell = {fhem.perlString(bell)}; my (%h, %b);"
            " if ($hidden ne '') { $h{$_} = 1 foreach (devspec2array($hidden)) }"
            " if ($bell ne '') { $b{$_} = 1 foreach (devspec2array($bell)) }"
            " my @n = ($spec ne '') ? devspec2array($spec) : keys %defs;"
            " push(@n, keys %b);"
            " my %seen; join(',', sort grep { my $d = $defs{$_};"
            " !$seen{$_}++ && defined($d) && !$h{$_} && !$d->{TEMPORARY}"
            " && !defined($d->{SNIPPET})"
            f" && ($d->{{TYPE}} !~ /^(?:{excluded})$/"
            # DOIFs with inputs (setList) are shown
            " || ($d->{TYPE} eq 'DOIF' && AttrVal($_, 'setList', '') ne ''))"
            " && AttrVal($_, 'disable', '0') ne '1'"
            + (
                # arranging rooms: also the devices without a room, but not
                # the ones hidden on purpose
                " && AttrVal($_, 'room', '') !~ /(?:^|,)hidden(?:,|$)/i"
                if any_room
                else " && ($b{$_} || AttrVal($_, 'room', '') ne ''"
                f" || $d->{{TYPE}} =~ /^(?:{special_types})$/"
                " || (defined($d->{FHEMPYTYPE})"
                f" && $d->{{FHEMPYTYPE}} =~ /^(?:{special_fhempy})$/))"
            )
            + " } @n)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        if not isinstance(result, str) or result.startswith("Exception"):
            self.logger.error(f"Failed to read FHEM devices: {result}")
            return []
        return [n for n in result.split(",") if n and n != self.hash["NAME"]]

    async def fetch_infos(self, names):
        if not names:
            return {}
        names_perl = ",".join(fhem.perlString(n) for n in names)
        readings = set(model.READINGS) | {n["reading"] for n in self.notices()}
        wanted = ",".join(fhem.perlString(r) for r in sorted(readings))
        cmd = (
            "my %w = map { $_ => 1 } (" + wanted + "); my %r;"
            " foreach my $d (" + names_perl + ") {"
            " next if (!defined($defs{$d})); my $h = $defs{$d}; my (%rd, %tm, %x);"
            # the inputs of a DOIF are readings with the names of its setList
            " if ($h->{TYPE} eq 'DOIF') { foreach (split(/\\s+/,"
            " AttrVal($d, 'setList', ''))) { my ($n) = split(/:/, $_); $x{$n} = 1"
            " if (defined($n) && $n ne '') } }"
            " my $last = '';"
            " foreach my $k (keys %{$h->{READINGS}}) {"
            " my $t = $h->{READINGS}{$k}{TIME} // ''; $last = $t if ($t gt $last);"
            " next if (!$w{$k} && !$x{$k});"
            " $rd{$k} = $h->{READINGS}{$k}{VAL}; $tm{$k} = $h->{READINGS}{$k}{TIME} }"
            " $r{$d} = {NAME => $d, TYPE => $h->{TYPE},"
            " FHEMPYTYPE => ($h->{FHEMPYTYPE} // ''),"
            " alias => AttrVal($d, 'alias', ''), room => AttrVal($d, 'room', ''),"
            " sets => (getAllSets($d) // ''), readings => \\%rd, times => \\%tm,"
            " last => $last,"
            " attrs => { map { $_ => AttrVal($d, $_, '') }"
            " ('genericDeviceType', 'matterType', 'matterInvert', 'setList') } } }"
            " to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            return json.loads(result)
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read FHEM devices: {result}")
            return {}

    async def fetch_calendars(self):
        """entries of the next days of all Calendar devices"""
        code = (
            "my @r; foreach my $c (devspec2array('TYPE=Calendar')) {"
            " next if (!defined($defs{$c}) || $defs{$c}{TYPE} ne 'Calendar');"
            " my $t = CommandGet(undef, \"$c events format:custom=\\\"\\$t1|\\$t2|\\$S\\\""
            f" limit:from=0,to=+{model.CALENDAR_DAYS}d\") // '';"
            " foreach my $l (split(/\\n/, $t)) { push(@r, \"$c|$l\") } }"
            " join(\"\\n\", @r)"
        )
        try:
            result = await fhem.sendCommandHash(self.hash, code)
        except Exception as err:
            self.logger.error(f"Failed to read the calendars: {err}")
            return self.calendar_events
        return model.parse_calendar(result)

    async def calendar_loop(self):
        """calendars change rarely and give no events for new entries: read
        them every few minutes, the header follows the day by itself"""
        while True:
            self.calendar_events = await self.fetch_calendars()
            head = self.make_header()
            if head != self.head:
                self.head = head
                await self.broadcast({"type": "header", "header": head})
            await asyncio.sleep(CALENDAR_INTERVAL)

    async def fetch_sun(self):
        """sunrise and sunset of today for the light/dark design"""
        result = await fhem.sendCommandHash(
            self.hash,
            "defined(&sunrise_abs) ? sunrise_abs() . ',' . sunset_abs() : ''",
        )
        parts = str(result or "").split(",")
        if len(parts) == 2 and all(len(p) >= 5 for p in parts):
            return {"rise": parts[0][:5], "set": parts[1][:5]}
        return None

    def doorbell_spec(self):
        """attribute doorbell 'Bell:action' -> ('Bell', 'action')"""
        spec = (self._attr_doorbell or "").strip()
        names, readings = [], {}
        for part in spec.split(","):
            name, _, reading = part.partition(":")
            if name:
                names.append(name)
                if reading:
                    readings[name] = reading
        return ",".join(names), readings

    def find_doorbells(self):
        spec, readings = self.doorbell_spec()
        if spec:
            wanted = spec.split(",")
            bells = [
                {"id": n, "name": model.display_name(self.infos[n])}
                for n in wanted
                if n in self.infos
            ]
        else:
            bells = model.doorbells(self.infos)
        for bell in bells:
            bell["reading"] = readings.get(bell["id"], "")
        return bells

    def door(self):
        streams = self.streams
        camera = (self._attr_door_camera or "").strip()
        if camera not in streams:
            camera = streams[0] if streams else ""
        return {
            "camera": camera,
            "cameras": streams,
            "opener": parse_opener(self._attr_door_opener) is not None,
            "bells": [{"id": b["id"], "name": b["name"]} for b in self.doorbells],
        }

    def schedule_reload(self):
        if self._reload_task is not None and not self._reload_task.done():
            return

        async def reload_later():
            await asyncio.sleep(RELOAD_DELAY)
            await self.reload()

        self._reload_task = self.create_async_task(reload_later())

    def notices(self):
        return model.parse_notices(getattr(self, "_attr_notices", ""))

    def alarm_system_name(self):
        return (getattr(self, "_attr_alarm_system", "") or "").strip()

    async def reload(self):
        names = await self.resolve_devices()
        # devices of notices may have no room
        names += [n["device"] for n in self.notices() if n["device"] not in names]
        alarm = self.alarm_system_name()
        if alarm and alarm not in names:
            names.append(alarm)
        self.infos = await self.fetch_infos(names)
        for name, info in self.infos.items():
            if media.is_media(info):
                info["preset_art"] = self.preset_art.setdefault(name, {})
        self._head_infos = {n: i for n, i in self.infos.items() if model.in_header(i)}
        before = (self.data, self.head)
        # the alarm system gets no tile: "All off" must not disarm it
        self.data = model.build(
            {n: i for n, i in self.infos.items() if n != alarm},
            keep_on=self.keep_on_names(),
            device_views=views.parse_views(self._attr_device_views),
            measure=self.measure_names(),
        )
        self.apply_timers()
        self.apply_may_open()
        self.doorbells = self.find_doorbells()
        self.sun = await self.fetch_sun()
        self.head = self.make_header()
        # FHEM defines and deletes helper devices (at, notify) all the time,
        # the tablets only draw everything again when something they show
        # changed
        changed = (self.data, self.head) != before
        await self.register_events(list(self.infos))
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "rooms", len(self.data["rooms"])
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "tiles", len(self.data["tiles"])
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "doorbells",
            ",".join(b["id"] for b in self.doorbells) or "none",
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        if not changed:
            return
        for ws, tablet_id in self.connected():
            tablet = self.tablets.get(tablet_id)
            if tablet is not None:
                await self.send(ws, {"type": "model", **self.model_message(tablet)})

    def make_header(self):
        head = model.header(self._head_infos, self.data["tiles"])
        head["sun"] = self.sun
        head["calendar"] = model.calendar(self.calendar_events, time.time())
        head["calendar"]["bins"] += head.pop("bins", [])
        head["door"] = self.door()
        head["floors"] = model.parse_floors(getattr(self, "_attr_floors", ""))
        head["notices"] = model.active_notices(
            self.notices(), self.infos, self.dismissed
        )
        # which devices have a notice, for the switch in their details
        head["notice_setup"] = {n["device"]: n["text"] for n in self.notices()}

        head["appliances"] = self.appliance_header()

        system = model.alarm_system(
            self.infos.get(self.alarm_system_name()),
            pin=model.clean_pin(getattr(self, "_attr_alarm_pin", "")) is not None,
        )
        head["alarm"] = {
            "system": system,
            "alarms": model.alarms(self.data["tiles"], system),
        }
        head["timeline"] = self.timeline_device() is not None
        return head

    async def register_events(self, names):
        for name in self._listening:
            fhem.unregister_event_listener(name, self.handle_event)
            fhem.unregister_event_listener(name, self.handle_global_event)
        for name in names:
            fhem.register_event_listener(name, self.handle_event)
        fhem.register_event_listener("global", self.handle_global_event)
        self._listening = names + ["global"]
        if not await fhem.setEventDevices(self.hash, self._listening):
            await self.update_state(
                "FHEM update needed: run 'update all' and restart FHEM, "
                "otherwise the tablets don't show changes"
            )
            return
        # only the readings the tablets use, collected by FHEM
        await fhem.setEventFilter(self.hash, self.event_filter())

    def event_filter(self):
        """regexp for "device:reading: value" of the events the dashboard
        needs: every event of global, doorbells and push devices, of the
        others only the readings the tiles and the header use and state"""
        everything = ["global"] + [b["id"] for b in self.doorbells]
        # notices may use any reading
        everything += [n["device"] for n in self.notices() if n["device"] in self.infos]
        everything += [
            name
            for name, info in self.infos.items()
            if info.get("FHEMPYTYPE") == model.PUSH_TYPE
            # inputs of DOIFs have their own reading names
            or model.inputs.has_inputs(info)
        ]
        devices = "|".join(re.escape(n) for n in sorted(set(everything)))
        readings = "|".join(re.escape(r) for r in sorted(set(model.READINGS)))
        # events without "reading: " are state events, FHEM leaves out
        # "state: " when the event isn't the current value of state (e.g.
        # state changed twice in one update)
        return f"^(?:(?:{devices}):|[^:]+:(?:{readings}): |[^:]+:(?!.*: ))"

    async def handle_event(self, device, reading, value):
        info = self.infos.get(device)
        if info is None:
            return
        await self.check_special_event(info, device, reading, value)
        if reading not in model.device_readings(info):
            if any(n["device"] == device and n["reading"] == reading for n in self.notices()):
                info.setdefault("readings", {})[reading] = value
                info.setdefault("times", {})[reading] = now_text()
                self.schedule_header()
            return
        info.setdefault("readings", {})[reading] = value
        info.setdefault("times", {})[reading] = now_text()
        if reading in model.BATTERY_READINGS:
            self._head_infos[device] = info
        item = self.data["tiles"].get(device)
        if item is not None and reading == model.power_reading(info):
            await self.watch_power(item, value)
        if item is not None and item["kind"] == "media":
            await self.learn_preset_art(device, info)
        if item is not None:
            state = model.tile_state(item["kind"], info)
            if "on" in item["state"] and "on" not in state:
                # e.g. set_off until the device confirms: as before
                state["on"] = item["state"]["on"]
            if state != item["state"]:
                item["state"] = state
                if state.get("on") is False and device in self.timers:
                    # switched off by hand or by the timer: the timer is done
                    await self.cancel_timer(item, send=False)
                await self.send_tile(item)
                rooms = model.motion_rooms(item)
                if rooms:
                    await self.broadcast({"type": "motion", "rooms": rooms})
        self.schedule_header()

    # --- washing machine, dryer and dishwasher ---

    def appliances(self):
        return model.parse_appliances(getattr(self, "_attr_appliances", ""))

    async def load_appliances(self):
        raw = await fhem.ReadingsVal(self.hash["NAME"], ".appliances", "")
        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            data = {}
        if isinstance(data, dict):
            for key, empty in (("cycles", {}), ("done", {}), ("ask", [])):
                if isinstance(data.get(key), type(empty)):
                    self.appliance_data[key] = data[key]

    async def save_appliances(self):
        await fhem.readingsSingleUpdate(
            self.hash, ".appliances", json.dumps(self.appliance_data), 0
        )

    async def watch_power(self, item, value):
        if item["kind"] not in ("switch", "outlet"):
            return
        if self.appliances().get(item["id"]) == "none":
            return
        watch = self.watches.setdefault(item["id"], model.ApplianceWatch())
        result = watch.feed(model.kinds.number(value), time.time())
        await self.appliance_result(item["id"], watch, result)

    async def appliance_result(self, name, watch, result):
        if result is None:
            return
        data = self.appliance_data
        what = self.appliances().get(name)
        if result == "start":
            if data["done"].pop(name, None) is not None:
                await self.save_appliances()
            self.schedule_header()
            return
        if result == "short":
            self.schedule_header()
            return
        if what in model.APPLIANCES:
            cycles = data["cycles"].setdefault(name, [])
            cycles.append(int(watch.seconds))
            del cycles[: -model.APPLIANCE_KEEP]
            data["done"][name] = time.time()
            item = self.data["tiles"].get(name)
            await self.broadcast(
                {
                    "type": "appliance_done",
                    "id": name,
                    "what": what,
                    "name": item["name"] if item else name,
                }
            )
        elif what is None and name not in data["ask"]:
            # the first program of an unknown plug: the tablets ask once
            data["ask"].append(name)
            data["cycles"].setdefault(name, []).append(int(watch.seconds))
        await self.save_appliances()
        self.schedule_header()

    async def appliance_loop(self):
        """done is "no power for a while", which sends no event"""
        while True:
            await asyncio.sleep(APPLIANCE_INTERVAL)
            now = time.time()
            for name, watch in list(self.watches.items()):
                await self.appliance_result(name, watch, watch.tick(now))
            done = self.appliance_data["done"]
            old = [n for n, t in done.items() if now - t > APPLIANCE_DONE_HOURS * 3600]
            for name in old:
                done.pop(name)
            if old:
                await self.save_appliances()
                self.schedule_header()

    def appliance_header(self):
        """running and done appliances, plugs to ask about"""
        known = self.appliances()
        tiles = self.data["tiles"]
        data = self.appliance_data
        result = {"running": [], "done": [], "ask": []}
        for name, what in sorted(known.items()):
            item = tiles.get(name)
            if item is None or what not in model.APPLIANCES:
                continue
            base = {
                "id": name,
                "name": item["name"],
                "what": what,
                "room": (item["rooms"] or [""])[0],
            }
            watch = self.watches.get(name)
            if watch is not None and watch.running:
                result["running"].append(
                    {
                        **base,
                        "since": int(watch.start),
                        "typical": model.typical_seconds(data["cycles"].get(name)),
                    }
                )
            elif name in data["done"]:
                result["done"].append({**base, "at": int(data["done"][name])})
        for name in data["ask"]:
            item = tiles.get(name)
            if item is None or name in known:
                continue
            result["ask"].append(
                {
                    "id": name,
                    "name": item["name"],
                    "room": (item["rooms"] or [""])[0],
                    "guess": model.appliance_guess(item["name"] + " " + name),
                }
            )
        return result

    async def answer_appliance(self, tablet, message):
        """the tablet says what a plug is: washer, dryer, dishwasher, none"""
        name = str(message.get("id", ""))
        what = str(message.get("what", ""))
        if name not in self.data["tiles"] or what not in model.APPLIANCES + ("none",):
            return
        known = self.appliances()
        known[name] = what
        value = model.format_appliances(known)
        self.logger.info(f"{tablet['name']}: {name} is {what}")
        await fhem.sendCommandHash(
            self.hash,
            "CommandAttr(undef, "
            + fhem.perlString(f"{self.hash['NAME']} appliances {value}")
            + ")",
        )
        self._attr_appliances = value
        if name in self.appliance_data["ask"]:
            self.appliance_data["ask"].remove(name)
        if what == "none":
            self.watches.pop(name, None)
            self.appliance_data["cycles"].pop(name, None)
        await self.save_appliances()
        await self.update_header()

    async def appliance_seen(self, message):
        if self.appliance_data["done"].pop(str(message.get("id", "")), None):
            await self.save_appliances()
            await self.update_header()

    def schedule_header(self):
        """build the header again soon: busy homes send hundreds of events per
        second, building it for every event costs a lot of CPU"""
        if self._header_task is not None and not self._header_task.done():
            return

        async def later():
            await asyncio.sleep(HEADER_DELAY)
            await self.update_header()

        self._header_task = self.create_async_task(later())

    async def update_header(self):
        head = self.make_header()
        if head != self.head:
            self.head = head
            await self.broadcast({"type": "header", "header": head})

    async def learn_preset_art(self, device, info):
        learner = self._preset_learners.get(device)
        if learner is None:
            learner = self._preset_learners[device] = media.PresetArtLearner()
        known = self.preset_art.setdefault(device, {})
        info["preset_art"] = known
        changed = learner.update(known, info, time.monotonic())
        info["station_logo"] = learner.logo
        if changed:
            await self.save_preset_art()

    async def check_special_event(self, info, device, reading, value):
        if info.get("FHEMPYTYPE") == model.PUSH_TYPE and reading == "message":
            await self.broadcast({"type": "push", "text": str(value)[:500]})
            return
        for bell in self.doorbells:
            if bell["id"] != device:
                continue
            wanted = bell.get("reading")
            if (wanted and reading == wanted) or (
                not wanted and model.rings(reading, value)
            ):
                await self.ring(bell)

    async def ring(self, bell, force=False):
        now = time.time()
        if not force and now - self.last_ring < RING_REPEAT:
            return
        self.last_ring = now
        self.logger.info(f"Doorbell {bell['name']}")
        door = self.door()
        await self.broadcast(
            {
                "type": "ring",
                "bell": bell.get("id", ""),
                "name": bell["name"],
                "camera": door["camera"],
                "opener": door["opener"],
                "time": now_text(),
            }
        )

    async def handle_global_event(self, device, reading, value):
        # global events have no reading, the whole text is the value
        words = (str(value) if reading == "state" else f"{reading}: {value}").split(" ")
        if len(words) < 2:
            return
        name = words[1]
        if words[0] in ("ATTR", "DELETEATTR") and len(words) > 2:
            if words[2] in RELOAD_ATTRS:
                self.schedule_reload()
        elif words[0] in ("DELETED", "MODIFIED"):
            # FHEM defines, modifies and deletes helper devices (at, DOIF
            # timers) all the time, reading all devices again is expensive
            if name in self.infos:
                self.schedule_reload()
        elif words[0] in ("RENAMED", "DEFINED"):
            if words[0] == "RENAMED" and name in self.infos:
                self.schedule_reload()
            elif await self.may_show(words[-1]):
                self.schedule_reload()

    async def may_show(self, name):
        """a new device: could it be shown at all (not temporary, no helper)"""
        if self._reload_task is not None and not self._reload_task.done():
            return False
        excluded = "|".join(EXCLUDED_TYPES)
        result = await fhem.sendCommandHash(
            self.hash,
            f"my $d = $defs{{{fhem.perlString(name)}}};"
            " (defined($d) && !$d->{TEMPORARY} && !defined($d->{SNIPPET})"
            f" && $d->{{TYPE}} !~ /^(?:{excluded})$/) ? 1 : 0",
        )
        return str(result).strip() == "1"

    def model_message(self, tablet):
        data = model.filter_rooms(self.data, tablet.get("rooms") or [])
        return {
            "rooms": data["rooms"],
            "tiles": data["tiles"],
            "scenes": data["scenes"],
            "header": self.head,
        }

    def allowed_tile(self, tablet, item):
        allowed = tablet.get("rooms") or []
        return not allowed or any(r in allowed for r in item["rooms"])

    async def send_tile(self, item):
        for ws, tablet_id in self.connected():
            tablet = self.tablets.get(tablet_id)
            if tablet is not None and self.allowed_tile(tablet, item):
                await self.send(ws, {"type": "tile", "tile": item})

    # --- doors and gates which may be open at some times ---

    def may_open(self):
        return model.parse_may_open(getattr(self, "_attr_may_open", ""))

    def apply_may_open(self):
        for name, window in self.may_open().items():
            item = self.data["tiles"].get(name)
            if item is not None and item["kind"] == "contact":
                item["may_open"] = window

    async def set_may_open(self, tablet, message):
        """the tablet sets or removes the time a door may be open"""
        item = self.data["tiles"].get(str(message.get("id", "")))
        if item is None or item["kind"] != "contact":
            return
        windows = self.may_open()
        window = model.clean_window(message.get("window"))
        if window:
            windows[item["id"]] = window
        else:
            windows.pop(item["id"], None)
        value = model.format_may_open(windows)
        self.logger.info(f"{tablet['name']}: may_open {value}")
        if value:
            command = "CommandAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} may_open {value}"
            )
        else:
            command = "CommandDeleteAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} may_open"
            )
        await fhem.sendCommandHash(self.hash, command + ")")
        self._attr_may_open = value
        await self.reload()

    # --- devices which 'All off' leaves on ---

    def keep_on_names(self):
        """None: found by their names"""
        value = (self._attr_keep_on or "").strip()
        if not value:
            return None
        return {n.strip() for n in value.split(",") if n.strip() and n != "none"}

    async def set_keep_on(self, tablet, message):
        item = self.data["tiles"].get(str(message.get("id", "")))
        if item is None or item["kind"] not in model.SWITCHABLE:
            return
        keep = {i for i, t in self.data["tiles"].items() if t.get("keep_on")}
        if message.get("keep"):
            keep.add(item["id"])
        else:
            keep.discard(item["id"])
        value = ",".join(sorted(keep)) or "none"
        self.logger.info(f"{tablet['name']}: attr keep_on {value}")
        await fhem.sendCommandHash(
            self.hash,
            "CommandAttr(undef, "
            f"{fhem.perlString(self.hash['NAME'] + ' keep_on ' + value)})",
        )
        self._attr_keep_on = value
        await self.reload()

    # --- own views of vacuums, cars, wallboxes, heat pumps, irrigation ---

    async def set_device_view(self, tablet, message):
        device = str(message.get("id", ""))
        view = str(message.get("view", ""))
        if device not in self.data["tiles"] or view not in views.VIEWS + ("none", ""):
            return
        chosen = views.parse_views(self._attr_device_views)
        if view:
            chosen[device] = view
        else:
            # found automatically again
            chosen.pop(device, None)
        value = views.format_views(chosen)
        name = self.hash["NAME"]
        if value:
            self.logger.info(f"{tablet['name']}: attr device_views {value}")
            code = f"CommandAttr(undef, {fhem.perlString(name + ' device_views ' + value)})"
        else:
            self.logger.info(f"{tablet['name']}: deleteattr device_views")
            code = f"CommandDeleteAttr(undef, {fhem.perlString(name + ' device_views')})"
        await fhem.sendCommandHash(self.hash, code)
        self._attr_device_views = value
        await self.reload()

    # --- plugs which only measure ---

    def measure_names(self):
        value = getattr(self, "_attr_measure_only", "") or ""
        return {n.strip() for n in value.split(",") if n.strip()}

    async def set_measure_only(self, tablet, message):
        item = self.data["tiles"].get(str(message.get("id", "")))
        if item is None or item["kind"] not in model.MEASURE_KINDS:
            return
        names = self.measure_names()
        if message.get("measure"):
            names.add(item["id"])
        else:
            names.discard(item["id"])
        value = ",".join(sorted(names))
        self.logger.info(f"{tablet['name']}: measure_only {value}")
        if value:
            command = "CommandAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} measure_only {value}"
            )
        else:
            command = "CommandDeleteAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} measure_only"
            )
        await fhem.sendCommandHash(self.hash, command + ")")
        self._attr_measure_only = value
        await self.reload()

    # --- floors ---

    async def set_floors(self, tablet, message):
        floors = message.get("floors")
        if not isinstance(floors, list):
            return
        value = model.format_floors([f for f in floors[:20] if isinstance(f, dict)])
        self.logger.info(f"{tablet['name']}: floors {value}")
        if value:
            command = "CommandAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} floors {value}"
            )
        else:
            command = "CommandDeleteAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} floors"
            )
        await fhem.sendCommandHash(self.hash, command + ")")
        self._attr_floors = value
        await self.update_header()

    # --- arranging rooms ---

    def can_arrange(self, tablet):
        """only tablets which may see and switch everything change rooms"""
        return not tablet.get("readonly") and not tablet.get("rooms")

    async def arrange(self, tablet, message, ws):
        if not self.can_arrange(tablet):
            return
        kind = message.get("type")
        if kind == "keep_on":
            await self.set_keep_on(tablet, message)
            return
        if kind == "device_view":
            await self.set_device_view(tablet, message)
            return
        if kind == "measure_only":
            await self.set_measure_only(tablet, message)
            return
        if kind == "floors":
            await self.set_floors(tablet, message)
            return
        if kind == "move_device":
            await self.arrange_move(tablet, message)
        elif kind == "rename_room":
            await self.arrange_rename(tablet, message)
        elif kind == "delete_device":
            await self.arrange_delete(tablet, message)
        if kind != "rooms_setup":
            # FHEM sends ATTR events as well, this is for safety
            self.schedule_reload()
        if ws is not None:
            infos = await self.fetch_infos(await self.resolve_devices(any_room=True))
            self._arrange_infos = infos
            await self.send(ws, {"type": "rooms_setup", **model.arrangement(infos)})

    async def arrange_move(self, tablet, message):
        name = str(message.get("id", ""))
        info = self._arrange_infos.get(name) or self.infos.get(name)
        source = model.clean_room(message.get("from"), allow_empty=True)
        target = model.clean_room(message.get("to"), allow_empty=True)
        if info is None or source is None or target is None:
            return
        value = model.moved_rooms(info.get("room", ""), source, target)
        self.logger.info(f"{tablet['name']}: attr {name} room {value}")
        if value:
            command = f"CommandAttr(undef, {fhem.perlString(f'{name} room {value}')})"
        else:
            command = f"CommandDeleteAttr(undef, {fhem.perlString(f'{name} room')})"
        result = await fhem.sendCommandHash(self.hash, command)
        if result:
            self.logger.error(f"attr {name} room failed: {result}")
            return
        info["room"] = value

    async def arrange_delete(self, tablet, message):
        """delete a device which isn't used anymore, only devices offered
        when arranging rooms"""
        name = str(message.get("id", ""))
        if name not in self._arrange_infos or name == self.hash["NAME"]:
            return
        self.logger.info(f"{tablet['name']}: delete {name}")
        result = await fhem.sendCommandHash(
            self.hash, f"CommandDelete(undef, {fhem.perlString(name)})"
        )
        if result:
            self.logger.error(f"delete {name} failed: {result}")
            return
        self._arrange_infos.pop(name, None)

    async def arrange_rename(self, tablet, message):
        source = model.clean_room(message.get("from"))
        target = model.clean_room(message.get("to"))
        if not source or not target or source == target:
            return
        self.logger.info(f"{tablet['name']}: rename room {source} to {target}")
        await fhem.sendCommandHash(
            self.hash,
            f"my ($f, $t) = ({fhem.perlString(source)}, {fhem.perlString(target)});"
            " foreach my $d (sort keys %defs) {"
            " my @r = map { s/^\\s+|\\s+$//gr } split(',', AttrVal($d, 'room', ''));"
            " next if (!grep { $_ eq $f } @r); my %s;"
            " @r = grep { !$s{$_}++ } map { $_ eq $f ? $t : $_ } @r;"
            " CommandAttr(undef, \"$d room \" . join(',', @r)) } ''",
        )
        # the tablets keep their order, hidden rooms and their own room
        for other in self.tablets.values():
            other["layout"] = model.renamed_layout(other.get("layout"), source, target)
            if other.get("room") == source:
                other["room"] = target
            if source in (other.get("rooms") or []):
                other["rooms"] = [target if r == source else r for r in other["rooms"]]
        await self.save_tablets()
        for other in self.tablets.values():
            await self.send_tablet(other)

    # --- actions of the tablets ---

    async def run_action(self, tablet, message):
        if tablet.get("readonly"):
            return
        action = str(message.get("action", ""))
        special = {
            "all_off": self.action_all_off,
            "open_door": self.action_open_door,
            "scene": self.action_scene,
            "timer": self.action_timer,
            "routine": self.action_routine,
            "undo": self.action_undo,
            "notice_done": self.action_notice_done,
            "alarm_mode": self.action_alarm_mode,
        }.get(action)
        if special is not None:
            await special(tablet, message)
        else:
            await self.action_tile(tablet, action, message)

    async def action_all_off(self, tablet, message):
        allowed = tablet.get("rooms") or []
        room = message.get("room") or None
        if allowed and room not in allowed:
            return
        # the tablet sends the devices it shows (rooms hidden on it stay on)
        ids = message.get("ids")
        wanted = set(str(i) for i in ids) if isinstance(ids, list) else None
        names = [
            name
            for name in model.all_off(self.data["tiles"], room)
            if wanted is None or name in wanted
        ]
        failed = []
        # a few at a time: many radio commands at once get lost (433 MHz,
        # HomeMatic duty cycle, Zigbee groups)
        for start in range(0, len(names), ALL_OFF_GROUP):
            if start:
                await asyncio.sleep(ALL_OFF_PAUSE)
            for name in names[start : start + ALL_OFF_GROUP]:
                if not await self.fhem_set(tablet, name, "off"):
                    failed.append(name)
        if names:
            self.create_async_task(self.check_all_off(tablet, names, failed))

    async def check_all_off(self, tablet, names, failed):
        """tell the tablet which devices are still on after a moment"""
        await asyncio.sleep(ALL_OFF_CHECK)
        tiles = self.data["tiles"]
        left = [
            {"id": name, "name": tiles[name]["name"]}
            for name in names
            if name in tiles and (name in failed or tiles[name]["state"].get("on"))
        ]
        await self.send_to_tablet(
            tablet, {"type": "all_off", "done": len(names) - len(left), "left": left}
        )

    async def action_routine(self, tablet, message):
        """good night or leaving home: lights and switches off, at night the
        blinds down, and remember how it was for undo"""
        mode = message.get("mode")
        if mode not in model.ROUTINES:
            return
        tiles = {
            i: t
            for i, t in self.data["tiles"].items()
            if self.allowed_tile(tablet, t)
        }
        off = message.get("off") if isinstance(message.get("off"), list) else []
        close = message.get("close") if isinstance(message.get("close"), list) else []
        steps, undo = model.routine_steps(tiles, mode, off, close)
        failed = await self.run_steps(tablet, steps)
        self.undo[tablet["id"]] = {
            "until": time.time() + model.UNDO_SECONDS,
            "steps": undo,
        }
        await self.send_to_tablet(
            tablet,
            {
                "type": "routine",
                "mode": mode,
                "done": len(steps) - len(failed),
                "failed": failed,
                "undo": bool(undo),
                "until": self.undo[tablet["id"]]["until"],
            },
        )

    async def action_undo(self, tablet, message):
        entry = self.undo.pop(tablet["id"], None)
        if entry is None or entry["until"] < time.time():
            return
        failed = await self.run_steps(tablet, entry["steps"])
        await self.send_to_tablet(tablet, {"type": "undone", "failed": failed})

    async def run_steps(self, tablet, steps):
        """(device, action, value) one after the other, names that failed"""
        failed = []
        for device, action, value in steps:
            item = self.data["tiles"].get(device)
            if item is None:
                continue
            try:
                args = model.command(item, self.infos.get(device, {}), action, value)
            except ValueError:
                continue
            for arg in args:
                if await self.fhem_set_error(tablet, device, arg):
                    failed.append(item["name"])
                    await self.send_tile(item)
                    break
        return failed

    async def send_to_tablet(self, tablet, message):
        for ws, tablet_id in self.connected():
            if tablet_id == tablet["id"]:
                await self.send(ws, message)

    async def action_notice_done(self, tablet, message):
        """tick off a notice: reset the device (e.g. a dummy to off) or hide
        it until the device reports again"""
        name = str(message.get("id", ""))
        notice = next((n for n in self.notices() if n["device"] == name), None)
        info = self.infos.get(name)
        if notice is None or info is None:
            return
        command = model.notice_reset(notice, info)
        if command is not None:
            error = await self.fhem_set_error(tablet, name, command)
            if not error:
                return
            await self.send_failed(tablet, name, model.display_name(info), error)
        self.dismissed[name] = (info.get("times") or {}).get(notice["reading"])
        await self.update_header()

    async def set_notice(self, tablet, message):
        """the tablet adds, changes or removes the notice of a device"""
        name = str(message.get("id", ""))
        if name not in self.infos:
            return
        notices = [n for n in self.notices() if n["device"] != name]
        if message.get("on"):
            old = next((n for n in self.notices() if n["device"] == name), None)
            notices.append(
                {
                    "device": name,
                    "reading": old["reading"] if old else "state",
                    "value": old["value"] if old else None,
                    "text": str(message.get("text") or "").strip()[:80],
                }
            )
        value = model.format_notices(notices)
        self.logger.info(f"{tablet['name']}: notices {value}")
        if value:
            command = "CommandAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} notices {value}"
            )
        else:
            command = "CommandDeleteAttr(undef, " + fhem.perlString(
                f"{self.hash['NAME']} notices"
            )
        await fhem.sendCommandHash(self.hash, command + ")")
        self._attr_notices = value
        await self.update_header()

    async def action_alarm_mode(self, tablet, message):
        """arm or disarm the alarm system, disarming needs the alarm PIN"""
        info = self.infos.get(self.alarm_system_name())
        mode = str(message.get("mode", ""))
        command = model.alarm_commands(info).get(mode) if info else None
        answer = {"type": "alarm_mode", "mode": mode, "ok": False, "wait": False}
        if command is None:
            await self.send_to_tablet(tablet, answer)
            return
        pin = model.clean_pin(getattr(self, "_attr_alarm_pin", ""))
        if mode == "off" and pin is not None:
            ok, wait = self.check_pin(tablet, pin, message.get("pin"), "alarm")
            if not ok:
                answer["wait"] = wait
                answer["wrong"] = True
                await self.send_to_tablet(tablet, answer)
                return
        error = await self.fhem_set_error(tablet, info["NAME"], command)
        if error:
            await self.send_failed(tablet, info["NAME"], model.display_name(info), error)
        answer["ok"] = not error
        await self.send_to_tablet(tablet, answer)

    async def action_open_door(self, tablet, message):
        opener = parse_opener(self._attr_door_opener)
        if opener is None:
            return
        if tablet.get("place") == "door" or message.get("ringing"):
            await self.fhem_set(tablet, opener[0], opener[1])

    async def action_scene(self, tablet, message):
        allowed = tablet.get("rooms") or []
        scene = next(
            (s for s in self.data["scenes"] if s["id"] == message.get("id")), None
        )
        if scene is not None and (not allowed or scene["room"] in allowed):
            error = await self.fhem_set_error(
                tablet, scene["device"], f"scene {scene['scene']}"
            )
            if error:
                await self.send_failed(tablet, None, scene["name"], error)

    # --- timers: switch off in 15 min ... ---

    async def load_timers(self):
        raw = await fhem.ReadingsVal(self.hash["NAME"], ".timers", "")
        try:
            timers = json.loads(raw) if raw else {}
        except ValueError:
            timers = {}
        self.timers = model.running_timers(
            timers if isinstance(timers, dict) else {}, time.time()
        )

    async def save_timers(self):
        await fhem.readingsSingleUpdate(
            self.hash, ".timers", json.dumps(self.timers, ensure_ascii=False), 0
        )

    def apply_timers(self):
        self.timers = model.running_timers(self.timers, time.time())
        for name, item in self.data["tiles"].items():
            if name in self.timers:
                item["timer"] = self.timers[name]

    async def action_timer(self, tablet, message):
        item = self.data["tiles"].get(str(message.get("id", "")))
        if (
            item is None
            or item["kind"] not in model.TIMER_KINDS
            or not self.allowed_tile(tablet, item)
        ):
            return
        minutes = model.timer_minutes(message.get("value"))
        if minutes <= 0:
            await self.cancel_timer(item)
            return
        info = self.infos.get(item["id"], {})
        off = model.command(item, info, "off")
        if not off:
            return
        if not item["state"].get("on"):
            # "on for 30 min"
            for arg in model.command(item, info, "on"):
                error = await self.fhem_set_error(tablet, item["id"], arg)
                if error:
                    await self.send_failed(tablet, item["id"], item["name"], error)
                    await self.send_tile(item)
                    return
        definition = model.timer_definition(item["id"], minutes, off)
        result = await fhem.sendCommandHash(
            self.hash,
            "{ my ($n, $d) = ("
            + fhem.perlString(model.timer_name(item["id"]))
            + ", "
            + fhem.perlString(definition)
            + "); CommandDelete(undef, $n) if ($defs{$n});"
            " my $r = CommandDefine(undef, $d);"
            " if (!$r && $defs{$n}) { $defs{$n}{TEMPORARY} = 1;"
            " CommandAttr(undef, \"$n room hidden\") }"
            " $r // '' }",
        )
        if result:
            self.logger.error(f"timer {definition} failed: {result}")
            await fhem.readingsSingleUpdate(
                self.hash, "lastError", f"timer {definition}: {result}", 1
            )
            await self.send_failed(tablet, item["id"], item["name"], str(result))
            return
        self.logger.info(f"{tablet['name']}: {definition}")
        self.timers[item["id"]] = round(time.time() + minutes * 60)
        item["timer"] = self.timers[item["id"]]
        await self.save_timers()
        await self.send_tile(item)

    async def cancel_timer(self, item, send=True):
        had = self.timers.pop(item["id"], None) is not None
        item.pop("timer", None)
        await fhem.sendCommandHash(
            self.hash,
            "{ my $n = "
            + fhem.perlString(model.timer_name(item["id"]))
            + "; CommandDelete(undef, $n) if ($defs{$n}); '' }",
        )
        if had:
            await self.save_timers()
        if send:
            await self.send_tile(item)

    async def action_tile(self, tablet, action, message):
        item = self.data["tiles"].get(str(message.get("id", "")))
        if item is None or not self.allowed_tile(tablet, item):
            return
        info = self.infos.get(item["id"], {})
        try:
            args = model.command(item, info, action, message.get("value"))
        except ValueError:
            return
        for arg in args:
            error = await self.fhem_set_error(tablet, item["id"], arg)
            if error:
                # tell the tablet why and show the real state again
                await self.send_failed(tablet, item["id"], item["name"], error)
                await self.send_tile(item)
                return

    async def fhem_set(self, tablet, device, arg):
        return not await self.fhem_set_error(tablet, device, arg)

    async def fhem_set_error(self, tablet, device, arg):
        """empty when set worked, otherwise the answer of FHEM"""
        definition = f"{device} {arg}"
        self.logger.info(f"{tablet['name']}: set {definition}")
        result = await fhem.sendCommandHash(
            self.hash, f"CommandSet(undef, {fhem.perlString(definition)})"
        )
        if result:
            self.logger.error(f"set {definition} failed: {result}")
            await fhem.readingsSingleUpdate(
                self.hash, "lastError", f"set {definition}: {result}", 1
            )
            return str(result)
        return ""

    async def send_failed(self, tablet, tile_id, name, error):
        message = {
            "type": "failed",
            "id": tile_id,
            "name": name,
            "reason": model.short_error(error),
        }
        await self.send_to_tablet(tablet, message)

    # --- timeline ---

    def timeline_device(self):
        from ..fhem_pythonbinding import getFhemPyDeviceByName

        for name, info in self.infos.items():
            if info.get("FHEMPYTYPE") == model.TIMELINE_TYPE:
                instance = getFhemPyDeviceByName(name)
                if instance is not None and hasattr(instance, "get_entries"):
                    return instance
        return None

    async def timeline_day(self, day):
        instance = self.timeline_device()
        if instance is None:
            return {"error": "no timeline"}
        entries = json.loads(
            await instance.get_entries(instance.hash, {"from": day, "to": day})
        )
        trends = json.loads(await instance.get_trends(instance.hash, {"day": day}))
        if "error" in entries:
            return entries
        found = entries.get("days") or [{}]
        return {
            "day": day,
            "today": entries.get("today"),
            "first": entries.get("first"),
            "periods": entries.get("periods", []),
            "entries": found[0].get("entries", []),
            "trends": trends.get("trends", []),
        }

    async def timeline_sparks(self, devices):
        """temperature and humidity of today per device for the tiles"""
        instance = self.timeline_device()
        if instance is None or not devices:
            return {}
        day = datetime.date.today().isoformat()
        trends = json.loads(await instance.get_trends(instance.hash, {"day": day}))
        return model.sparks(trends.get("trends", []), devices)

    async def timeline_device_history(self, device):
        instance = self.timeline_device()
        if instance is None:
            return {"error": "no timeline"}
        return json.loads(
            await instance.get_device(instance.hash, {"device": device, "days": "1"})
        )

    # --- energy over days ---

    def energy_buckets(self, span, now):
        """(start, end) of the bars: hours of today, or days"""
        today = datetime.date.fromtimestamp(now)

        def midnight(day):
            return datetime.datetime.combine(day, datetime.time()).timestamp()

        if span == "day":
            start = midnight(today)
            end = midnight(today + datetime.timedelta(days=1))
            hours = []
            hour = start
            while hour < end:
                hours.append((hour, hour + 3600))
                hour += 3600
            return hours
        days = model.ENERGY_RANGES[span]
        return [
            (
                midnight(today - datetime.timedelta(days=i)),
                midnight(today - datetime.timedelta(days=i - 1)),
            )
            for i in range(days - 1, -1, -1)
        ]

    def energy_consumers(self, tablet):
        """(id, name, device, reading) of devices which report their power"""
        result = []
        for item in self.data["tiles"].values():
            if item["state"].get("power") is None:
                continue
            reading = model.power_reading(self.infos.get(item["id"]) or {})
            if reading is not None and self.allowed_tile(tablet, item):
                result.append((item["id"], item["name"], item["id"], reading))
        return result

    async def energy_history(self, tablet, span):
        instance = self.timeline_device()
        if instance is None or not hasattr(instance, "hourly_values"):
            return {"error": "no timeline"}
        now = time.time()
        buckets = self.energy_buckets(span, now)
        sources = model.energy_sources(self.infos)
        consumers = self.energy_consumers(tablet)
        wanted = [s[:2] for s in sources.values()] + [c[2:] for c in consumers]
        series = await instance.hourly_values(wanted, buckets[0][0], buckets[-1][1])
        if series is None:
            return {"error": "no timeline"}
        report = model.energy_report(
            series,
            sources,
            consumers,
            buckets,
            now,
            model.parse_energy_price(self._attr_energy_price),
        )
        report["range"] = span
        price = model.parse_energy_price(self._attr_energy_price)
        report["price_attr"] = model.format_energy_price(*price) if price else ""
        report["sources"] = sorted(k for k in sources if k != "price")
        return report

    async def set_energy_price(self, tablet, message):
        # 0,32 on a German tablet
        values = [
            str(message.get(k) or "").strip().replace(",", ".")
            for k in ("price", "feed_in")
        ]
        price = model.parse_energy_price(",".join(v for v in values if v))
        if price is None and values[0]:
            return
        if price is None:
            self.logger.info(f"{tablet['name']}: deleteattr energy_price")
            await fhem.sendCommandHash(
                self.hash,
                "CommandDeleteAttr(undef, "
                f"{fhem.perlString(self.hash['NAME'] + ' energy_price')})",
            )
            self._attr_energy_price = ""
            return
        value = model.format_energy_price(*price)
        self.logger.info(f"{tablet['name']}: attr energy_price {value}")
        await fhem.sendCommandHash(
            self.hash,
            "CommandAttr(undef, "
            f"{fhem.perlString(self.hash['NAME'] + ' energy_price ' + value)})",
        )
        self._attr_energy_price = value

    # --- HTTP server ---

    def url(self):
        # plain http: the tablets are in the home network
        return f"http://{self.ip}:{self._attr_port}/"  # NOSONAR

    def https_url(self):
        return f"https://{self.ip}:{self._attr_https_port}/"

    async def start_server(self):
        async with self._server_lock:
            await self.stop_server()
            await self._start_server()

    def make_app(self):
        from aiohttp import web

        app = web.Application(client_max_size=MAX_MESSAGE_SIZE)
        app.router.add_get("/", self.handle_static)
        app.router.add_get("/api/ws", self.handle_ws)
        app.router.add_post("/api/pair", self.handle_pair)
        app.router.add_get("/api/timeline", self.handle_timeline)
        app.router.add_get("/api/energy", self.handle_energy)
        app.router.add_get("/api/history", self.handle_history)
        app.router.add_get("/api/sparks", self.handle_sparks)
        app.router.add_post("/api/webrtc", self.handle_webrtc)
        app.router.add_get("/api/snapshot", self.handle_snapshot)
        app.router.add_get("/api/image", self.handle_image)
        app.router.add_get("/fhempy-ca.crt", self.handle_ca)
        app.router.add_get("/{file}", self.handle_static)
        return app

    async def _start_server(self):
        from aiohttp import web

        runner = web.AppRunner(self.make_app(), access_log=None)
        await runner.setup()
        try:
            await web.TCPSite(runner, port=self._attr_port).start()
        except OSError as err:
            await runner.cleanup()
            self.logger.error(f"Dashboard can't use port {self._attr_port}: {err}")
            await self.update_state(
                f"port {self._attr_port} is used by another program, "
                "change attribute port"
            )
            return
        self.runners.append(runner)
        self.logger.info(f"Dashboard on {self.url()}")
        await fhem.readingsSingleUpdateIfChanged(self.hash, "url", self.url(), 1)
        await self.start_https(runner)
        await self.update_state()

    async def start_https(self, runner):
        from aiohttp import web

        self.https_ready = False
        if not self._attr_https_port:
            return
        try:
            context = await self.ssl_context()
            await web.TCPSite(
                runner, port=self._attr_https_port, ssl_context=context
            ).start()
        except Exception as err:
            self.logger.warning(f"No https address for the tablets: {err}")
            return
        self.https_ready = True
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "https_url", self.https_url(), 1
        )

    async def load_ca(self):
        from ..push import certs

        await certs.load()

        name = self.hash["NAME"]
        key_text = await fhem.ReadingsVal(name, ".ca_key", "")
        cert_text = await fhem.ReadingsVal(name, ".ca_cert", "")
        if key_text and cert_text:
            try:
                key = certs.load_key(
                    await utils.async_decrypt_string(key_text, self._unique_id)
                )
                return key, certs.load_cert(cert_text.replace("\\n", "\n"))
            except Exception:
                self.logger.exception("CA of the https address broken, new one")
        key, cert = certs.create_ca(f"{name} dashboard (FHEM)")
        await fhem.readingsSingleUpdate(
            self.hash,
            ".ca_key",
            await utils.async_encrypt_string(certs.key_pem(key), self._unique_id),
            0,
        )
        await fhem.readingsSingleUpdate(
            self.hash, ".ca_cert", certs.cert_pem(cert).replace("\n", "\\n"), 0
        )
        return key, cert

    async def ssl_context(self):
        from ..push import certs

        ca_key, ca_cert = await self.load_ca()
        self.ca_pem = certs.cert_pem(ca_cert)
        return await utils.run_blocking(
            functools.partial(server_ssl_context, ca_key, ca_cert, self.ip)
        )

    async def stop_server(self):
        for ws, _ in self.connected():
            await ws.close()
        self.clients = {}
        runners, self.runners = self.runners, []
        for runner in runners:
            await runner.cleanup()

    async def start_cameras(self):
        cameras = go2rtc.parse_cameras(self._attr_cameras)
        try:
            await self.cameras.start((self._attr_go2rtc or "").strip(), cameras)
        except Exception as err:
            self.logger.error(f"Cameras not available: {err}")
            await fhem.readingsSingleUpdate(self.hash, "lastError", str(err), 1)
            return
        # go2rtc needs a moment to start
        for _ in range(10):
            self.streams = await self.cameras.streams()
            if self.streams or not self.cameras.url:
                break
            await asyncio.sleep(1)
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "cameras", ",".join(self.streams) or "none", 1
        )
        head = self.make_header()
        if head != self.head:
            self.head = head
            await self.broadcast({"type": "header", "header": head})

    async def update_state(self, error=None):
        if error:
            state = error
        elif not self.runners:
            state = "stopped"
        else:
            state = f"ready, {len(self.tablets)} tablets"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    @staticmethod
    def origin_allowed(request):
        """A web page of another host must not use the dashboard"""
        from yarl import URL

        origin = request.headers.get("Origin")
        if not origin:
            return True
        try:
            return URL(origin).host == request.url.host
        except ValueError:
            return False

    async def handle_static(self, request):
        from aiohttp import web

        name = request.match_info.get("file", "index.html")
        if name not in STATIC_FILES:
            raise web.HTTPNotFound()
        if name == "lang.js":
            code = choose_language(
                request.cookies.get("dashLang", ""),
                request.headers.get("Accept-Language", ""),
            )
            body = await utils.run_blocking(functools.partial(lang_script, code))
            return web.Response(
                body=body,
                headers={
                    "Content-Type": STATIC_FILES[name],
                    "Cache-Control": "no-cache",
                    "Vary": "Cookie, Accept-Language",
                },
            )
        body = await utils.run_blocking(
            functools.partial(read_static, os.path.join(WWW_DIR, name))
        )
        if name == "app.js":
            body = body.replace(BUILD_MARK, self.build.encode())
        return web.Response(
            body=body,
            headers={
                "Content-Type": STATIC_FILES[name],
                "Cache-Control": "no-cache",
                "Permissions-Policy": "microphone=(self), camera=()",
            },
        )

    async def handle_ca(self, request):
        from aiohttp import web

        # the CA of the https address, as stored in FHEM
        pem = await fhem.ReadingsVal(self.hash["NAME"], ".ca_cert", "")
        if not self.ca_pem or not pem:
            raise web.HTTPNotFound()
        return web.Response(
            body=pem.replace("\\n", "\n").encode(),
            headers={
                "Content-Type": "application/x-x509-ca-cert",
                "Content-Disposition": 'attachment; filename="fhempy-ca.crt"',
            },
        )

    async def handle_pair(self, request):
        from aiohttp import web

        if not self.origin_allowed(request):
            return web.json_response({"error": "origin"}, status=403)
        try:
            body = await request.json()
        except ValueError:
            return web.json_response({"error": "invalid"}, status=400)
        if not isinstance(body, dict) or not self.check_pair_code(body.get("code")):
            return web.json_response({"error": "code"}, status=403)
        token, tablet = await self.add_tablet(body.get("device", ""))
        return web.json_response({"token": token, "tablet": self.public_tablet(tablet)})

    def _checked(self, request):
        from aiohttp import web

        if not self.origin_allowed(request):
            raise web.HTTPForbidden()
        tablet = self.tablet_of_request(request)
        if tablet is None:
            raise web.HTTPUnauthorized()
        return tablet

    async def handle_timeline(self, request):
        from aiohttp import web

        tablet = self._checked(request)
        if not self.sees_timeline(tablet):
            raise web.HTTPForbidden()
        day = request.query.get("day") or datetime.date.today().isoformat()
        try:
            day = datetime.date.fromisoformat(day).isoformat()
        except ValueError:
            raise web.HTTPBadRequest()
        data = await self.timeline_day(day)
        allowed = tablet.get("rooms") or []
        if allowed and "entries" in data:
            # tablets for some rooms only see what happened there
            data["entries"] = [
                e
                for e in data["entries"]
                if any(r in allowed for r in str(e.get("room") or "").split(","))
            ]
            devices = {
                item["id"]
                for item in self.data["tiles"].values()
                if self.allowed_tile(tablet, item)
            }
            data["trends"] = [
                tr for tr in data.get("trends", []) if tr.get("device") in devices
            ]
            data["periods"] = []
        return web.json_response(data)

    async def handle_history(self, request):
        from aiohttp import web

        tablet = self._checked(request)
        item = self.data["tiles"].get(request.query.get("id", ""))
        if item is None or not self.allowed_tile(tablet, item):
            raise web.HTTPNotFound()
        data = await self.timeline_device_history(item["id"])
        if not self.sees_timeline(tablet) and isinstance(data, dict):
            # the curves stay, what happened when not
            data = {k: v for k, v in data.items() if k in ("trends", "from", "to")}
        return web.json_response(data)

    async def handle_energy(self, request):
        from aiohttp import web

        tablet = self._checked(request)
        span = request.query.get("range", "day")
        if span not in model.ENERGY_RANGES:
            raise web.HTTPBadRequest()
        return web.json_response(await self.energy_history(tablet, span))

    async def handle_sparks(self, request):
        from aiohttp import web

        tablet = self._checked(request)
        devices = {
            item["id"]
            for item in self.data["tiles"].values()
            if item["kind"] in model.CLIMATE_KINDS and self.allowed_tile(tablet, item)
        }
        return web.json_response(await self.timeline_sparks(devices))

    def _stream(self, request):
        from aiohttp import web

        stream = request.query.get("stream", "")
        if stream not in self.streams:
            raise web.HTTPNotFound()
        return stream

    async def handle_webrtc(self, request):
        from aiohttp import web

        self._checked(request)
        stream = self._stream(request)
        offer = await request.text()
        if not offer or len(offer) > MAX_SDP_SIZE:
            raise web.HTTPBadRequest()
        try:
            answer = await self.cameras.webrtc(stream, offer)
        except Exception as err:
            self.logger.error(f"Live picture of {stream} failed: {err}")
            raise web.HTTPBadGateway()
        return web.Response(text=answer, content_type="application/sdp")

    async def handle_snapshot(self, request):
        from aiohttp import web

        self._checked(request)
        stream = self._stream(request)
        try:
            content_type, body = await self.cameras.snapshot(stream)
        except Exception:
            raise web.HTTPBadGateway()
        return web.Response(
            body=body,
            headers={"Content-Type": content_type, "Cache-Control": "no-store"},
        )

    def image_url(self, tablet, request):
        """URL of a cover the tablet may see: only URLs from the readings of
        music players it shows, never URLs sent by the tablet"""
        item = self.data["tiles"].get(request.query.get("id", ""))
        if item is None or item["kind"] != "media":
            return None
        if not self.allowed_tile(tablet, item):
            return None
        info = self.infos.get(item["id"], {})
        preset = request.query.get("preset")
        if preset == "logo":
            return media.logo_url(info)
        if preset:
            return (info.get("preset_art") or {}).get(str(preset)[:2])
        return media.art_url(info)

    async def fetch_image(self, url):
        aiohttp = await utils.import_module("aiohttp")

        cached = self._images.get(url)
        if cached is not None:
            return cached
        timeout = aiohttp.ClientTimeout(total=8)
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.get(url) as resp,
        ):
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").split(";")[0]
            if not content_type.startswith("image/"):
                raise ValueError(f"no image: {content_type}")
            body = await read_limited(resp.content, MAX_IMAGE_SIZE)
        while len(self._images) >= IMAGE_CACHE:
            self._images.pop(next(iter(self._images)))
        self._images[url] = (content_type, body)
        return content_type, body

    async def handle_image(self, request):
        """covers of music players through fhempy: the tablets may use https
        while the players only offer http, and need no access to them"""
        from aiohttp import web

        tablet = self._checked(request)
        url = self.image_url(tablet, request)
        if not url:
            raise web.HTTPNotFound()
        try:
            content_type, body = await self.fetch_image(url)
        except Exception as err:
            self.logger.debug(f"Failed to load cover {url}: {err}")
            raise web.HTTPNotFound()
        return web.Response(
            body=body,
            headers={
                "Content-Type": content_type,
                "Cache-Control": "private, max-age=86400",
            },
        )

    async def handle_ws(self, request):
        from aiohttp import WSMsgType, web

        if not self.origin_allowed(request):
            raise web.HTTPForbidden()
        ws = web.WebSocketResponse(heartbeat=30, max_msg_size=MAX_MESSAGE_SIZE)
        await ws.prepare(request)
        tablet = None
        try:
            async for msg in ws:
                message = parse_message(msg, WSMsgType.TEXT)
                if message is None:
                    continue
                if tablet is None:
                    tablet = await self.greet(ws, message)
                    if tablet is None:
                        break
                    continue
                if tablet["id"] not in self.tablets:
                    break
                await self.handle_message(tablet, message, ws)
        finally:
            self.clients.pop(ws, None)
        return ws

    async def greet(self, ws, message):
        """first message of a tablet: hello with its token"""
        tablet = self.tablet_by_token(message.get("token"))
        if message.get("type") != "hello" or tablet is None:
            await ws.send_json({"type": "unknown"})
            return None
        self.clients[ws] = tablet["id"]
        tablet["seen"] = now_text()
        await ws.send_json(
            {
                "type": "welcome",
                "build": self.build,
                "tablet": self.public_tablet(tablet),
                **self.model_message(tablet),
            }
        )
        return tablet

    async def handle_message(self, tablet, message, ws=None):
        kind = message.get("type")
        if kind == "unlock":
            await self.unlock(tablet, message, ws)
            return
        if kind in LOCKED_MESSAGES and not self.is_unlocked(tablet):
            if ws is not None:
                await self.send(ws, {"type": "locked"})
            return
        if kind == "setup" and not tablet.get("place"):
            # the first setup of a new tablet needs no PIN, also the layout
            # right after it
            self.unlocked[tablet["id"]] = time.time() + 60
        if kind in ARRANGE_MESSAGES:
            await self.arrange(tablet, message, ws)
        elif kind == "action":
            await self.run_action(tablet, message)
        elif kind == "bug_info" and ws is not None:
            await self.send(ws, {"type": "bug_info", "info": self.bug_info()})
        elif kind == "notice" and not tablet.get("readonly"):
            await self.set_notice(tablet, message)
        elif kind == "may_open" and not tablet.get("readonly"):
            await self.set_may_open(tablet, message)

        elif kind == "energy_price" and not tablet.get("readonly"):
            await self.set_energy_price(tablet, message)
        elif kind == "appliance" and not tablet.get("readonly"):
            await self.answer_appliance(tablet, message)
        elif kind == "appliance_seen" and not tablet.get("readonly"):
            await self.appliance_seen(message)
        elif kind == "setup":
            place = message.get("place")
            if place in PLACES:
                tablet["place"] = place
            if "room" in message:
                tablet["room"] = str(message.get("room") or "")[:100]
            if "name" in message and str(message["name"]).strip():
                tablet["name"] = str(message["name"]).strip()[:40]
            await self.save_tablets()
            await self.send_tablet(tablet)
        elif kind == "layout":
            tablet["layout"] = clean_layout(message.get("layout"))
            await self.save_tablets()
            await self.send_tablet(tablet)

    # --- PIN for the settings ---

    def settings_pin(self):
        return model.clean_pin(getattr(self, "_attr_settings_pin", ""))

    def is_unlocked(self, tablet):
        if self.settings_pin() is None:
            return True
        return self.unlocked.get(tablet["id"], 0) > time.time()

    def check_pin(self, tablet, pin, given, what="settings"):
        """(ok, wait): wait when there were too many wrong PINs. Wrong PINs
        of the settings and of the alarm system count together."""
        now = time.time()
        fails = [t for t in self.pin_fails.get(tablet["id"], []) if t > now - PIN_WAIT]
        ok = False
        if pin is None:
            ok = True
        elif len(fails) < PIN_TRIES:
            ok = hmac.compare_digest(str(given or ""), pin)
        if ok:
            self.pin_fails.pop(tablet["id"], None)
            return True, False
        fails.append(now)
        self.pin_fails[tablet["id"]] = fails
        self.logger.warning(f"{tablet['name']}: wrong PIN for the {what}")
        return False, len(fails) >= PIN_TRIES

    async def unlock(self, tablet, message, ws):
        ok, wait = self.check_pin(tablet, self.settings_pin(), message.get("pin"))
        if ok:
            self.unlocked[tablet["id"]] = time.time() + PIN_OPEN
        answer = {
            "type": "unlocked",
            "ok": ok,
            "until": self.unlocked.get(tablet["id"], 0),
            "wait": wait,
        }
        if ws is not None:
            await self.send(ws, answer)

    async def send_tablet(self, tablet, with_model=False):
        for ws, tablet_id in self.connected():
            if tablet_id != tablet["id"]:
                continue
            await self.send(
                ws, {"type": "tablet", "tablet": self.public_tablet(tablet)}
            )
            if with_model:
                await self.send(ws, {"type": "model", **self.model_message(tablet)})

    async def send(self, ws, message):
        try:
            await ws.send_json(message)
        except (ConnectionError, RuntimeError):
            self.clients.pop(ws, None)

    def bug_info(self):
        """versions and counts for a bug report, nothing personal: no names,
        no addresses, only which attributes are set"""
        kinds = {}
        for item in self.data["tiles"].values():
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
        return {
            "fhempy": __version__,
            "build": self.build,
            "python": platform.python_version(),
            "system": f"{platform.system()} {platform.machine()}",
            "devices": len(self.infos),
            "tiles": len(self.data["tiles"]),
            "rooms": len(self.data["rooms"]),
            "kinds": dict(sorted(kinds.items())),
            "tablets": len(self.tablets),
            "connected": len(self.clients),
            "https": bool(self._attr_https_port),
            "attrs": sorted(
                a for a in ATTRS_TEXT if (getattr(self, "_attr_" + a, "") or "")
            ),
        }

    def connected(self):
        """(websocket, tablet id) of the connected tablets, as a copy: sending
        can end connections, which removes them from self.clients"""
        return list(self.clients.items())

    async def broadcast(self, message):
        for ws, _ in self.connected():
            await self.send(ws, message)

    # --- FHEMWEB page ---

    def setup_html(self):
        if not hasattr(self, "hash"):
            return ""
        code = self.new_pair_code()
        link = f"{self.url()}#pair={code}"
        status = (
            ""
            if self.runners
            else "<b style='color:#c00'>The dashboard is not running, see "
            "reading state.</b><br><br>"
        )
        rows = "".join(
            f"<tr><td>{html.escape(t['name'])}</td>"
            f"<td>{html.escape(PLACE_NAMES.get(t.get('place'), '-'))}</td>"
            f"<td>{html.escape(t.get('room') or '-')}</td>"
            f"<td>{html.escape(', '.join(t.get('rooms') or []) or 'all')}"
            f"{' (read only)' if t.get('readonly') else ''}"
            f"{' (no timeline)' if not self.sees_timeline(t) else ''}</td>"
            f"<td>{html.escape(t.get('seen') or t.get('created') or '')}</td></tr>"
            for t in self.tablets.values()
        )
        tablets = (
            "<br><b>Tablets</b><table><tr><th align=left>Name</th>"
            "<th align=left>Place</th><th align=left>Room</th>"
            "<th align=left>May show</th><th align=left>Last seen</th></tr>"
            f"{rows}</table>"
            if rows
            else ""
        )
        https = ""
        if self.https_ready:
            ca = html.escape(self.url() + "fhempy-ca.crt")
            https = (
                "<br><details><summary><b>Talk at the door (microphone)</b></summary>"
                "Browsers allow the microphone only on https pages. Install the "
                f'certificate <a href="{ca}">fhempy-ca.crt</a> once on the door '
                "tablet:<ul>"
                "<li><b>iPad</b>: open the link in Safari, Allow, Settings &rarr; "
                "Profile Downloaded &rarr; Install, then Settings &rarr; General "
                "&rarr; About &rarr; Certificate Trust Settings &rarr; switch on "
                "the fhempy certificate.</li>"
                "<li><b>Android</b>: open the link, Settings &rarr; Security "
                "&rarr; Install a certificate &rarr; CA certificate.</li></ul>"
                "Then tap <i>Switch to https</i> in the settings of the dashboard "
                "on the tablet.</details>"
            )
        return (
            '<div class="makeTable wide"><span class="mkTitle">Add a tablet</span>'
            '<table class="block wide"><tr class="odd"><td>'
            f"{status}"
            '<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center">'
            f"<div>{qr_image(link)}</div><div>"
            "<b>1.</b> Scan the QR code with the camera of the tablet.<br>"
            "<b>2.</b> Choose where the tablet is (wall, couch, door). Done.<br><br>"
            f'Or open <a href="{html.escape(self.url())}" target="_blank">'
            f"{html.escape(self.url())}</a> on the tablet and enter the code "
            f"<b style='font-size:1.4em;letter-spacing:2px'>{code}</b><br>"
            "<small>The code works once and for 10 minutes. Reload this page for "
            "a new one.</small></div></div>"
            f"{tablets}{https}</td></tr></table></div>"
        )
