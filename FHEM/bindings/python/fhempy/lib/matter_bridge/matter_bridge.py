"""Matter bridge: FHEM devices in Apple Home, Google Home, Alexa, SmartThings.

fhempy runs bridge.mjs (matter.js) as child process and exchanges one JSON
object per line with it, see bridge.mjs.
"""

import asyncio
import functools
import json
import signal

from .. import fhem, generic, utils
from ..core import child_process, fhemweb, pending_restore
from ..matter import server
from . import devices as bridge_devices
from . import runtime

RESTART_DELAY = 10
RELOAD_DELAY = 2
# new FHEM devices show up in 'set add' after this time
CANDIDATES_INTERVAL = 600
INFO_ATTRS = ("alias", "matterName", "matterType", "matterInvert", "genericDeviceType")
# attributes of FHEM devices which change their Matter device
RELOAD_ATTRS = (
    "alias",
    "matterName",
    "matterType",
    "matterInvert",
    "genericDeviceType",
)
DEVICE_ATTR_LIST = (
    "matterName matterType:auto," + ",".join(bridge_devices.TYPES) + " matterInvert:0,1"
)
DEFAULT_ROOM = "MatterBridge"
# icons of the room and the bridge in FHEMWEB
ROOM_ICON = "it_network"
BRIDGE_ICON = "mqtt_bridge_1"
# TYPEs which never make sense in a Matter app
EXCLUDED_TYPES = (
    "FHEMWEB",
    "telnet",
    "Global",
    "notify",
    "at",
    "DOIF",
    "watchdog",
    "FileLog",
    "DbLog",
    "DbRep",
    "SVG",
    "weblink",
    "eventTypes",
    "autocreate",
    "allowed",
    "statistics",
    "HMinfo",
    "holiday",
    "BindingsIo",
    "fhempyServer",
    "PythonBinding",
    "CUL",
    "HMLAN",
    "HMUARTLGW",
    "MQTT",
    "MQTT2_SERVER",
    "ZWDongle",
    "SIGNALduino",
    "JeeLink",
    "HUEBridge",
    "msgConfig",
    "readingsGroup",
    "logProxy",
    "RSS",
    "speedtest",
)
# rootVendorId of the pairing -> app name
VENDORS = {
    0x1349: "Apple Home",
    0x6006: "Google Home",
    0x1217: "Amazon Alexa",
    0x110A: "SmartThings",
    0x130A: "Home Assistant",
}

DEVICES_HELP = (
    "Additional FHEM devices which are shown in Matter apps, separated by "
    "comma, e.g. Lamp1,Plug2. A device specification like TYPE=HUEDevice "
    "works too.<br>Easier: put the devices into the room of attribute "
    "bridge_room or use 'set add'."
)
ROOM_HELP = (
    "All FHEM devices in this room are shown in your Matter apps (Apple "
    "Home, Google Home, Alexa...), default MatterBridge. Empty: only the "
    "devices of attribute devices."
)
ADD_HELP = (
    "Make a FHEM device available in your Matter apps (Apple Home, Google "
    "Home, Alexa...). It is put into the room of attribute bridge_room and "
    "shows up in the apps after a few seconds.<br>"
    "The type (light, plug, blind, thermostat, sensor...) is detected "
    "automatically. If it is wrong, set the attribute matterType of the "
    "device. The name in the app is the alias of the device, or attribute "
    "matterName."
)
PAIRING_MODE_HELP = (
    "Allow pairing with one more app (e.g. Apple Home and Google Home at "
    "the same time) for 15 minutes. Scan the QR code shown on this page "
    "with the new app within this time.<br>"
    "Alternatively share the bridge from the first app (Google Home: "
    "'Linked Matter apps & services', Apple Home: 'Turn On Pairing Mode')."
)
RESET_HELP = (
    "Removes all pairings, the bridge gets a new pairing code. Remove the "
    "bridge from your apps too and pair it again."
)


def format_manual_code(code):
    code = str(code or "")
    if len(code) == 11 and code.isdigit():
        return f"{code[:4]}-{code[4:7]}-{code[7:]}"
    return code


def qr_image(text):
    """QR code as <img>, FHEMWEB styles inline SVGs like icons (small and
    clipped), an image keeps its size"""
    import segno

    uri = segno.make(text, micro=False, error="m").png_data_uri(
        scale=5, border=4, dark="#000", light="#fff"
    )
    return (
        f'<img src="{uri}" alt="Matter QR code" '
        'style="width:200px;height:200px;max-width:none;image-rendering:pixelated">'
    )


class matter_bridge(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.proc = None
        self.node = None
        self.node_env = None
        self.transport = None
        # FHEM device name -> info (TYPE, sets, readings, attrs)
        self.infos = {}
        # Matter endpoint id -> {device, type, name, state}
        self.endpoints = {}
        self.status = {}
        self._listening = []
        self._stopping = False
        self._errors = utils.ErrorLogger(logger)
        self._maintenance = asyncio.Lock()
        self._reload_task = None
        self._events_supported = True

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await self.set_set_config(self.set_config())
        await super().Define(hash, args, argsh)
        attr_config = {
            "devices": {
                "default": "",
                "help": DEVICES_HELP,
            },
            "port": {
                "default": "5550",
                "format": "int",
                "help": "Network port of the Matter bridge. Change it only if "
                "5550 is already used, all apps have to be paired again then.",
            },
            "bridge_room": {
                "default": DEFAULT_ROOM,
                "help": ROOM_HELP,
            },
            "bridge_name": {
                "default": "FHEM",
                "help": "Name of the bridge which is shown when you pair it. "
                "Restart the bridge after a change.",
            },
        }
        await self.set_attr_config(attr_config)
        await fhem.readingsSingleUpdate(self.hash, "state", "starting", 1)
        await self.setup_room()
        self.create_async_task(self.run())
        self.create_async_task(self.update_candidates_loop())

    def set_config(self, candidates=None, exposed=None):
        config = {
            "add": {"args": ["device"], "help": ADD_HELP},
            "remove": {
                "args": ["device"],
                "help": "Remove a FHEM device from your Matter apps.",
            },
            "pairing_mode": {"help": PAIRING_MODE_HELP},
            "refresh": {
                "help": "Read all devices from FHEM again (normally automatic)."
            },
            "restart": {"help": "Restart the Matter bridge."},
            "reset_pairing": {"help": RESET_HELP},
        }
        if candidates:
            config["add"]["options"] = ",".join(candidates)
        if exposed:
            config["remove"]["options"] = ",".join(exposed)
        return config

    # FHEM FUNCTION
    async def Undefine(self, hash):
        self._stopping = True
        await self.unregister_events()
        await self.stop_bridge()
        await super().Undefine(hash)

    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        return self.pairing_html() + str(detail)

    def pairing_html(self):
        qr = self.status.get("qr")
        if not qr:
            return ""
        try:
            image = qr_image(qr)
        except Exception:
            self.logger.exception("Failed to create QR code")
            image = ""
        code = format_manual_code(self.status.get("manual"))
        if self.status.get("commissioned"):
            text = (
                f"Paired with: {self.paired_apps() or 'unknown app'}.<br>"
                "To use FHEM devices in one more app: <b>set pairing_mode</b>, "
                "then scan this code with the new app within 15 minutes."
            )
        else:
            text = (
                "Open the Google Home, Apple Home, Alexa or SmartThings app, "
                "choose <i>Add device</i> &rarr; <i>Matter</i> and scan this "
                "code.<br>The app warns that the bridge isn't certified, "
                "continue anyway (Google Home needs a free developer project "
                "first, see help)."
            )
        return (
            '<div class="makeTable"><table class="block wide"><tr>'
            f'<td style="width:210px;vertical-align:top">{image}</td>'
            '<td style="vertical-align:top">'
            f"{text}<br><br>Pairing code: <b>{code}</b></td>"
            "</tr></table></div>"
        )

    # --- bridge process ---

    async def run(self):
        if not await self.install():
            return
        while not self._stopping:
            async with self._maintenance:
                started = await self.start_bridge()
            if started:
                await self.communicate()
            if self._stopping:
                return
            await self.update_state("bridge stopped, restarting")
            await asyncio.sleep(RESTART_DELAY)

    async def install(self):
        await self.update_state("installing Node.js")
        try:
            self.node, version, self.node_env = await server.prepare_node(self.logger)
        except server.NodeNotFound:
            await self.update_state(
                "Node.js 22.13 or newer needed",
                "Install Node.js 22 or newer (https://nodejs.org or "
                "'curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash - "
                "&& sudo apt install nodejs') and restart fhempy.",
            )
            return False
        await fhem.readingsSingleUpdate(
            self.hash, "node_version", f"{version[0]}.{version[1]}", 1
        )
        installed = await utils.run_blocking(
            functools.partial(runtime.installed_version)
        )
        if runtime.needs_install(installed):
            await self.update_state(
                "installing matter.js, this takes a few minutes",
                "Please wait until the installation is finished.",
            )
            try:
                await utils.run_blocking(
                    functools.partial(runtime.install, self.node, self.node_env)
                )
            except Exception as exc:
                self.logger.error(f"matter.js installation failed: {exc}")
                await self.update_state(
                    "installation failed, check fhempy log",
                    "Check internet connection and free disk space, then "
                    "'set restart'.",
                )
                return False
        await fhem.readingsSingleUpdateIfChanged(
            self.hash, "matterjs_version", runtime.MATTER_JS_VERSION, 1
        )
        return True

    async def start_bridge(self):
        if self._stopping:
            return False
        await self.apply_restore()
        try:
            self.proc = await utils.run_blocking(
                functools.partial(
                    runtime.start,
                    self.node,
                    self.node_env,
                    self.hash["NAME"],
                    self._attr_port,
                    self._attr_bridge_name or "FHEM",
                    logger=self.logger,
                )
            )
        except Exception:
            self.logger.exception("Failed to start Matter bridge")
            await self.update_state("failed to start, check fhempy log")
            return False
        await self.update_state("starting")
        return True

    async def apply_restore(self):
        """Pairings restored by github_restore, applied before the start"""
        try:
            applied = await utils.run_blocking(
                functools.partial(
                    pending_restore.apply_bridge_restore,
                    runtime.bridge_directory(self.hash["NAME"]),
                )
            )
        except Exception:
            self.logger.exception("Failed to apply restored Matter bridge backup")
            return
        if applied:
            self.logger.info(f"Applied restored pairings ({len(applied)} files)")

    async def communicate(self):
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader(limit=2**22)
        await loop.connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(reader), self.proc.stdout
        )
        self.transport, _ = await loop.connect_write_pipe(
            asyncio.Protocol, self.proc.stdin
        )
        try:
            await self.reload_devices()
            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                    message = json.loads(line)
                except ValueError:
                    self.logger.debug(f"Unexpected output: {line!r}")
                    continue
                await self.handle_message(message)
        finally:
            self.transport.close()
            self.transport = None
            await self.stop_bridge()
            self.status = {}

    async def stop_bridge(self):
        proc = self.proc
        self.proc = None
        if proc is None:
            return True
        if self.transport is not None:
            # closing stdin stops the bridge cleanly
            self.transport.close()
        return await child_process.stop(proc, signal.SIGTERM, timeout=15)

    def send(self, message):
        if self.transport is None or self.transport.is_closing():
            return
        self.transport.write((json.dumps(message) + "\n").encode())

    async def handle_message(self, message):
        event = message.get("event")
        if event == "status":
            self.status = message
            await self.update_status()
        elif event == "command":
            self.create_async_task(
                self.execute_command(message.get("id"), message.get("command", {}))
            )
        elif event == "pairing_mode":
            if message.get("busy"):
                await self.update_state(
                    "pairing mode opened by an app",
                    "An app already opened pairing mode with its own code (e.g. "
                    "Android while adding the bridge to Home Assistant). Finish "
                    "it there or wait 15 minutes, then try 'set pairing_mode' "
                    "again. Home Assistant needs to reach fhempy directly: same "
                    "network, IPv6, in Docker network_mode host.",
                )
            elif message.get("minutes"):
                await self.update_state(
                    f"pairing mode for {message.get('minutes')} minutes",
                    "Scan the QR code on this page with the new app now.",
                )
            else:
                # paired with the new app or time is up
                await self.update_status()
        elif event == "error":
            device = self.endpoints.get(message.get("id"), {}).get("device", "")
            self.logger.error(
                f"Matter bridge error {device}: {message.get('message')}".replace(
                    "  ", " "
                )
            )
            await fhem.readingsSingleUpdate(
                self.hash, "lastError", f"{device} {message.get('message')}", 1
            )

    async def update_status(self):
        commissioned = self.status.get("commissioned")
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "pairing_code", format_manual_code(self.status.get("manual"))
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "qr_code", self.status.get("qr", "")
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "paired_with", self.paired_apps() or "-"
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        if not self._events_supported:
            await self.update_state(
                "FHEM update needed",
                "Run 'update all' in FHEM and restart FHEM, otherwise the "
                "Matter apps don't see changes of your devices.",
            )
        elif commissioned:
            await self.update_state(
                f"paired ({len(self.status.get('fabrics', []))} apps)",
                "Done. Add more devices with 'set add'. "
                "Use 'set pairing_mode' to pair one more app.",
            )
        else:
            await self.update_state(
                "ready for pairing",
                "Open this device in FHEMWEB and scan the QR code with "
                "Google Home, Apple Home, Alexa or SmartThings.",
            )

    def paired_apps(self):
        apps = []
        for fabric in self.status.get("fabrics", []):
            name = (
                VENDORS.get(fabric.get("vendor"))
                or fabric.get("label")
                or (f"vendor 0x{fabric.get('vendor', 0):04X}")
            )
            apps.append(name)
        return ", ".join(apps)

    async def update_state(self, state, next_step=None):
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(self.hash, "state", state)
        if next_step is not None:
            await fhem.readingsBulkUpdateIfChanged(self.hash, "next_step", next_step)
        await fhem.readingsEndUpdate(self.hash, 1)

    # --- FHEM devices ---

    async def setup_room(self):
        """Once for a new bridge: put it into its room and give the room and
        the bridge an icon in FHEMWEB"""
        room = self._attr_bridge_room
        if room:
            await fhemweb.setup_room(self.hash, room, ROOM_ICON, BRIDGE_ICON)

    async def resolve_devices(self):
        """devices of attribute devices and all devices in bridge_room"""
        spec = (self._attr_devices or "").strip()
        room = self._attr_bridge_room or ""
        if not spec and not room:
            return []
        excluded = "|".join(EXCLUDED_TYPES)
        cmd = (
            f"my $self = {fhem.perlString(self.hash['NAME'])};"
            f" my $spec = {fhem.perlString(spec)};"
            f" my $room = {fhem.perlString(room)}; my %n;"
            " if ($spec ne '') { $n{$_} = 1 foreach (devspec2array($spec)) }"
            " if ($room ne '') { foreach my $d (keys %defs) {"
            " my $h = $defs{$d};"
            " next if ($h->{TEMPORARY} || defined($h->{SNIPPET}));"
            f" next if ($h->{{TYPE}} =~ /^({excluded})$/);"
            " $n{$d} = 1 if ((','.AttrVal($d, 'room', '').',') =~ /,\\Q$room\\E,/) } }"
            " join(',', sort grep { defined($defs{$_}) && $_ ne $self"
            " && !(defined($defs{$_}{FHEMPYTYPE})"
            " && $defs{$_}{FHEMPYTYPE} eq 'matter_bridge') } keys %n)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        return [name for name in str(result or "").split(",") if name]

    async def fetch_infos(self, names):
        if not names:
            return {}
        names_perl = ",".join(fhem.perlString(name) for name in names)
        attrs_perl = ",".join(fhem.perlString(attr) for attr in INFO_ATTRS)
        cmd = (
            "my %r; foreach my $d (" + names_perl + ") {"
            " next if(!defined($defs{$d})); my $h = $defs{$d};"
            f" addToDevAttrList($d, {fhem.perlString(DEVICE_ATTR_LIST)});"
            " my %rd; foreach my $k (keys %{$h->{READINGS}}) {"
            " $rd{$k} = $h->{READINGS}{$k}{VAL} }"
            " $r{$d} = {NAME => $d, TYPE => $h->{TYPE},"
            " alias => AttrVal($d, 'alias', ''),"
            " sets => (getAllSets($d) // ''), readings => \\%rd,"
            " attrs => { map { $_ => AttrVal($d, $_, '') } (" + attrs_perl + ") } } }"
            " to_json(\\%r)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        try:
            return json.loads(result)
        except (TypeError, ValueError):
            self.logger.error(f"Failed to read FHEM devices: {result}")
            return {}

    def schedule_reload(self):
        if self._reload_task is not None and not self._reload_task.done():
            return

        async def reload_later():
            await asyncio.sleep(RELOAD_DELAY)
            await self.reload_devices()

        self._reload_task = self.create_async_task(reload_later())

    async def reload_devices(self):
        names = await self.resolve_devices()
        self.infos = await self.fetch_infos(names)
        endpoints = {}
        unsupported = []
        for name in names:
            info = self.infos.get(name)
            device_endpoints = bridge_devices.endpoints(info) if info else []
            if not device_endpoints:
                unsupported.append(name)
            for endpoint in device_endpoints:
                endpoint["device"] = name
                endpoint["state"] = bridge_devices.endpoint_state(endpoint, info)
                endpoints[endpoint["id"]] = endpoint
        self.endpoints = endpoints

        await self.register_events(names)
        self.send(
            {
                "cmd": "devices",
                "devices": [
                    {key: ep[key] for key in ("id", "type", "name", "state", "parts")}
                    for ep in endpoints.values()
                ],
            }
        )

        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdateIfChanged(
            self.hash,
            "devices",
            ",".join(
                f"{ep['device']}:{'+'.join([ep['type']] + ep['parts'])}"
                for ep in endpoints.values()
            )
            or "-",
        )
        await fhem.readingsBulkUpdateIfChanged(
            self.hash, "unsupported_devices", ",".join(unsupported) or "-"
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        await self.update_set_config()

    async def register_events(self, names):
        await self.unregister_events()
        for name in names:
            fhem.register_event_listener(name, self.handle_event)
        # attribute changes, renamed and deleted devices
        fhem.register_event_listener("global", self.handle_global_event)
        self._listening = names + ["global"]
        self._events_supported = await fhem.setEventDevices(self.hash, self._listening)
        if not self._events_supported:
            await self.update_state(
                "FHEM update needed",
                "Run 'update all' in FHEM and restart FHEM, otherwise the "
                "Matter apps don't see changes of your devices.",
            )

    async def unregister_events(self):
        for name in self._listening:
            fhem.unregister_event_listener(name, self.handle_event)
            fhem.unregister_event_listener(name, self.handle_global_event)
        if self._listening and self._stopping:
            await fhem.setEventDevices(self.hash, [])
        self._listening = []

    async def handle_event(self, device, reading, value):
        info = self.infos.get(device)
        if info is None:
            return
        info.setdefault("readings", {})[reading] = value
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint["device"] != device:
                continue
            state = bridge_devices.endpoint_state(endpoint, info)
            changed = {
                key: value
                for key, value in state.items()
                if value is not None and endpoint["state"].get(key) != value
            }
            if changed:
                endpoint["state"].update(changed)
                self.send({"cmd": "state", "id": endpoint_id, "state": changed})

    async def handle_global_event(self, device, reading, value):
        words = value.split(" ")
        if len(words) < 2:
            return
        if words[0] in ("ATTR", "DELETEATTR") and len(words) > 2:
            if words[1] in self.infos and words[2] in RELOAD_ATTRS:
                self.schedule_reload()
            elif words[2] == "room" and self._attr_bridge_room:
                # a device was put into or removed from bridge_room
                self.schedule_reload()
        elif words[0] in ("DELETED", "RENAMED", "DEFINED"):
            self.schedule_reload()

    async def execute_command(self, endpoint_id, command):
        endpoint = self.endpoints.get(endpoint_id)
        if endpoint is None:
            return
        info = self.infos.get(endpoint["device"], {})
        args = bridge_devices.fhem_commands(endpoint["type"], info, command)
        for arg in args:
            definition = f"{endpoint['device']} {arg}"
            self.logger.info(f"Matter app: set {definition}")
            result = await fhem.sendCommandHash(
                self.hash, f"CommandSet(undef, {fhem.perlString(definition)})"
            )
            if result:
                self.logger.error(f"set {definition} failed: {result}")
                await fhem.readingsSingleUpdate(
                    self.hash, "lastError", f"set {definition}: {result}", 1
                )
                # show the real state in the app again
                self.send(
                    {"cmd": "state", "id": endpoint_id, "state": endpoint["state"]}
                )
                return

    # --- set add/remove ---

    async def update_candidates_loop(self):
        while True:
            await self.update_set_config()
            await asyncio.sleep(CANDIDATES_INTERVAL)

    async def candidates(self):
        excluded = "|".join(EXCLUDED_TYPES)
        cmd = (
            "join(',', grep { my $h = $defs{$_};"
            f" $_ ne {fhem.perlString(self.hash['NAME'])}"
            " && !$h->{TEMPORARY} && !defined($h->{SNIPPET})"
            f" && $h->{{TYPE}} !~ /^({excluded})$/"
            " && !(defined($h->{FHEMPYTYPE}) && $h->{FHEMPYTYPE} eq 'matter_bridge')"
            " } sort keys %defs)"
        )
        result = await fhem.sendCommandHash(self.hash, cmd)
        exposed = set(self.infos)
        return [n for n in str(result or "").split(",") if n and n not in exposed]

    async def update_set_config(self):
        candidates = await self.candidates()
        await self.set_set_config(self.set_config(candidates, sorted(self.infos)))

    async def set_add(self, hash, params):
        name = params["device"]
        infos = await self.fetch_infos([name])
        if name not in infos:
            return f"Unknown FHEM device {name}"
        if not bridge_devices.endpoints(infos[name]):
            types = ", ".join(bridge_devices.TYPES)
            return (
                f"Can't detect which kind of device {name} is. Set its attribute "
                f"matterType ({types}) and try again."
            )
        room = self._attr_bridge_room
        if room:
            rooms = await self.device_rooms(name)
            if room not in rooms:
                await fhem.CommandAttr(
                    self.hash, f"{name} room {','.join(rooms + [room])}"
                )
            return None
        names = [n for n in self._device_list() if n != name] + [name]
        await fhem.CommandAttr(
            self.hash, f"{self.hash['NAME']} devices {','.join(names)}"
        )
        return None

    async def device_rooms(self, name):
        rooms = await fhem.AttrVal(name, "room", "")
        return [r for r in str(rooms or "").split(",") if r]

    async def set_remove(self, hash, params):
        name = params["device"]
        removed = False
        room = self._attr_bridge_room
        if room:
            rooms = await self.device_rooms(name)
            if room in rooms:
                rooms.remove(room)
                if rooms:
                    await fhem.CommandAttr(self.hash, f"{name} room {','.join(rooms)}")
                else:
                    await fhem.CommandDeleteAttr(self.hash, f"{name} room")
                removed = True
        names = self._device_list()
        if name in names:
            names.remove(name)
            if names:
                await fhem.CommandAttr(
                    self.hash, f"{self.hash['NAME']} devices {','.join(names)}"
                )
            else:
                await fhem.CommandDeleteAttr(self.hash, f"{self.hash['NAME']} devices")
            removed = True
        if removed:
            return None
        if name in self.infos:
            return (
                f"{name} is added by the device specification in attribute "
                "devices, change the attribute."
            )
        return f"{name} isn't used by the Matter bridge"

    def _device_list(self):
        return [n for n in (self._attr_devices or "").split(",") if n]

    async def set_attr_devices(self, hash):
        if self.transport is not None:
            self.schedule_reload()

    async def set_attr_bridge_room(self, hash):
        if self.transport is not None:
            self.schedule_reload()

    async def set_refresh(self, hash, params):
        await self.reload_devices()

    async def set_pairing_mode(self, hash, params):
        if self.transport is None:
            return "The Matter bridge isn't running, check reading state."
        self.send({"cmd": "pairing_mode"})
        return None

    async def set_restart(self, hash, params):
        self.create_async_task(self.restart())

    async def restart(self):
        async with self._maintenance:
            await self.stop_bridge()

    async def set_reset_pairing(self, hash, params):
        self.create_async_task(self.reset_pairing())

    async def reset_pairing(self):
        async with self._maintenance:
            await self.stop_bridge()
            await utils.run_blocking(
                functools.partial(runtime.erase, self.hash["NAME"])
            )
            await fhem.readingsSingleUpdate(self.hash, "paired_with", "-", 1)
