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
import secrets
import ssl
import tempfile
import time

from .. import fhem, generic, utils
from . import go2rtc, model

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
ATTRS_TEXT = (
    "devices",
    "hidden_devices",
    "doorbell",
    "cameras",
    "go2rtc",
    "door_camera",
    "door_opener",
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
}
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
RELOAD_ATTRS = ("room", "alias", "genericDeviceType", "matterType", "disable")
LAYOUT_KEYS = ("room_order", "hidden_rooms", "hidden_tiles", "tile_order", "theme")
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
        elif key == "theme" and value in ("auto", "dark", "light"):
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
        self.data = {"rooms": [], "tiles": {}, "scenes": []}
        self.head = {}
        self.tablets = {}
        self.codes = {}
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
        self.ca_pem = ""
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
        }
        await self.set_attr_config(attr_config)
        await self.set_icon("it_television")
        self._unique_id = await fhem.getUniqueId(hash)
        await self.load_tablets()
        await self.update_set_config()
        self.ip = await utils.run_blocking(functools.partial(utils.get_local_ip))
        await self.reload()
        await self.start_server()
        self.ready = True
        self.create_async_task(self.start_cameras())

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
                "<table class=\"block wide\"><tr><td>The dashboard is starting, "
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
        return result

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

    def set_attr_hidden_devices(self, hash):
        self.schedule_reload()

    def set_attr_doorbell(self, hash):
        self.schedule_reload()

    def set_attr_door_camera(self, hash):
        self.schedule_reload()

    def set_attr_door_opener(self, hash):
        self.schedule_reload()

    # --- FHEM devices ---

    async def resolve_devices(self):
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
            f" && $d->{{TYPE}} !~ /^(?:{excluded})$/"
            " && AttrVal($_, 'disable', '0') ne '1'"
            " && ($b{$_} || AttrVal($_, 'room', '') ne ''"
            f" || $d->{{TYPE}} =~ /^(?:{special_types})$/"
            " || (defined($d->{FHEMPYTYPE})"
            f" && $d->{{FHEMPYTYPE}} =~ /^(?:{special_fhempy})$/))"
            " } @n)"
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
        wanted = ",".join(fhem.perlString(r) for r in model.READINGS)
        cmd = (
            "my %w = map { $_ => 1 } (" + wanted + "); my %r;"
            " foreach my $d (" + names_perl + ") {"
            " next if (!defined($defs{$d})); my $h = $defs{$d}; my (%rd, %tm);"
            " foreach my $k (keys %{$h->{READINGS}}) { next if (!$w{$k});"
            " $rd{$k} = $h->{READINGS}{$k}{VAL}; $tm{$k} = $h->{READINGS}{$k}{TIME} }"
            " $r{$d} = {NAME => $d, TYPE => $h->{TYPE},"
            " FHEMPYTYPE => ($h->{FHEMPYTYPE} // ''),"
            " alias => AttrVal($d, 'alias', ''), room => AttrVal($d, 'room', ''),"
            " sets => (getAllSets($d) // ''), readings => \\%rd, times => \\%tm,"
            " attrs => { map { $_ => AttrVal($d, $_, '') }"
            " ('genericDeviceType', 'matterType', 'matterInvert') } } }"
            " to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            return json.loads(result)
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read FHEM devices: {result}")
            return {}

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

    async def reload(self):
        names = await self.resolve_devices()
        self.infos = await self.fetch_infos(names)
        before = (self.data, self.head)
        self.data = model.build(self.infos)
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
        head = model.header(self.infos, self.data["tiles"])
        head["sun"] = self.sun
        head["door"] = self.door()
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

    async def handle_event(self, device, reading, value):
        info = self.infos.get(device)
        if info is None:
            return
        await self.check_special_event(info, device, reading, value)
        if reading not in model.READINGS:
            return
        info.setdefault("readings", {})[reading] = value
        info.setdefault("times", {})[reading] = now_text()
        item = self.data["tiles"].get(device)
        if item is not None:
            state = model.tile_state(item["kind"], info)
            if state != item["state"]:
                item["state"] = state
                await self.send_tile(item)
                rooms = model.motion_rooms(item)
                if rooms:
                    await self.broadcast({"type": "motion", "rooms": rooms})
        head = self.make_header()
        if head != self.head:
            self.head = head
            await self.broadcast({"type": "header", "header": head})

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

    def handle_global_event(self, device, reading, value):
        words = str(value).split(" ")
        if len(words) < 2:
            return
        if words[0] in ("ATTR", "DELETEATTR") and len(words) > 2:
            if words[2] in RELOAD_ATTRS:
                self.schedule_reload()
        elif words[0] in ("DELETED", "RENAMED", "DEFINED", "MODIFIED"):
            self.schedule_reload()

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

    # --- actions of the tablets ---

    async def run_action(self, tablet, message):
        if tablet.get("readonly"):
            return
        action = str(message.get("action", ""))
        special = {
            "all_off": self.action_all_off,
            "open_door": self.action_open_door,
            "scene": self.action_scene,
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
        for name in model.all_off(self.data["tiles"], room):
            await self.fhem_set(tablet, name, "off")

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
            await self.fhem_set(tablet, scene["device"], f"scene {scene['scene']}")

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
            if not await self.fhem_set(tablet, item["id"], arg):
                # show the real state again
                await self.send_tile(item)
                return

    async def fhem_set(self, tablet, device, arg):
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
            return False
        return True

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
        app.router.add_get("/api/history", self.handle_history)
        app.router.add_get("/api/sparks", self.handle_sparks)
        app.router.add_post("/api/webrtc", self.handle_webrtc)
        app.router.add_get("/api/snapshot", self.handle_snapshot)
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

        name = self.hash["NAME"]
        key_text = await fhem.ReadingsVal(name, ".ca_key", "")
        cert_text = await fhem.ReadingsVal(name, ".ca_cert", "")
        if key_text and cert_text:
            try:
                key = certs.load_key(utils.decrypt_string(key_text, self._unique_id))
                return key, certs.load_cert(cert_text.replace("\\n", "\n"))
            except Exception:
                self.logger.exception("CA of the https address broken, new one")
        key, cert = certs.create_ca(f"{name} dashboard (FHEM)")
        await fhem.readingsSingleUpdate(
            self.hash,
            ".ca_key",
            utils.encrypt_string(certs.key_pem(key), self._unique_id),
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
        body = await utils.run_blocking(
            functools.partial(read_static, os.path.join(WWW_DIR, name))
        )
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

        self._checked(request)
        day = request.query.get("day") or datetime.date.today().isoformat()
        try:
            day = datetime.date.fromisoformat(day).isoformat()
        except ValueError:
            raise web.HTTPBadRequest()
        return web.json_response(await self.timeline_day(day))

    async def handle_history(self, request):
        from aiohttp import web

        tablet = self._checked(request)
        item = self.data["tiles"].get(request.query.get("id", ""))
        if item is None or not self.allowed_tile(tablet, item):
            raise web.HTTPNotFound()
        return web.json_response(await self.timeline_device_history(item["id"]))

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
                await self.handle_message(tablet, message)
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
                "tablet": self.public_tablet(tablet),
                **self.model_message(tablet),
            }
        )
        return tablet

    async def handle_message(self, tablet, message):
        kind = message.get("type")
        if kind == "action":
            await self.run_action(tablet, message)
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

    async def send_tablet(self, tablet, with_model=False):
        for ws, tablet_id in self.connected():
            if tablet_id != tablet["id"]:
                continue
            await self.send(ws, {"type": "tablet", "tablet": self.public_tablet(tablet)})
            if with_model:
                await self.send(ws, {"type": "model", **self.model_message(tablet)})

    async def send(self, ws, message):
        try:
            await ws.send_json(message)
        except (ConnectionError, RuntimeError):
            self.clients.pop(ws, None)

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
            f"{' (read only)' if t.get('readonly') else ''}</td>"
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
