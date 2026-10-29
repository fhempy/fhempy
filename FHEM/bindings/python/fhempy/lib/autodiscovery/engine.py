"""The scans of autodiscovery, shared by all autodiscovery devices of this
fhempy instance.

- mDNS: one zeroconf browser for all service types of the catalog, new devices
  are reported right away
- SSDP: advertisements are received right away, a search runs every 10min
- Bluetooth LE: the shared scan of core/ble_scanner, only if bleak works
- search(): discovery.py of the modules, every 10 minutes one after another
- MQTT: Home Assistant discovery messages on the brokers found, see mqtt.py

A found device which doesn't exist in FHEM yet is shown in a popup on every
open FHEMWEB page, never created on its own. Ignored and already shown
devices are stored in FHEM (getKeyValue), fhempy peers share this list.
Found devices which exist in FHEM are checked again every minute: a deleted
device is offered again in the list of found devices (no popup).
"""

import asyncio
import functools
import importlib
import ipaddress
import json
import time
from urllib.parse import urlsplit

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo

from .. import fhem, utils
from ..core.ssdp import ssdp
from ..core.zeroconf import zeroconf
from . import catalog
from .context import SearchContext
from .mqtt import MDNS_TYPE as MQTT_MDNS_TYPE
from .mqtt import MqttDiscovery

KEY = "fhempy_autodiscovery"
SEARCH_INTERVAL = 600
SEARCH_TIMEOUT = 30
SSDP_INTERVAL = 600
# check if existing devices were deleted in FHEM
RECHECK_INTERVAL = 60
# collect devices before showing the popup, e.g. after a power failure
POPUP_DELAY = 10
MDNS_INFO_TIMEOUT = 3000
# how long the candidates of the BLE scan are kept without advertisement
BLE_FORGET = 3600

STATUS_CHECKING = "checking"
STATUS_NEW = "new"
STATUS_EXISTS = "exists"
STATUS_CREATED = "created"
STATUS_IGNORED = "ignored"


def perl_json(value):
    return fhem.perlString(json.dumps(value, ensure_ascii=False))


class _SsdpListener:
    """Listener of core/ssdp for one device type"""

    def __init__(self, engine):
        self.engine = engine

    async def found_device(self, upnp_device):
        await self.engine.found_ssdp(upnp_device)

    async def removed_device(self, upnp_device):
        return


class Engine:
    instance: "Engine" = None

    @staticmethod
    def get_instance(logger) -> "Engine":
        if Engine.instance is None:
            Engine.instance = Engine(logger)
        return Engine.instance

    @staticmethod
    def running_instance() -> "Engine":
        """The engine if an autodiscovery device is defined, otherwise None."""
        engine = Engine.instance
        if engine is not None and engine.running:
            return engine
        return None

    def __init__(self, logger):
        self.logger = logger
        self.catalog = []
        self.frontends = []
        self.candidates = {}
        self.ignored = set()
        self.shown = set()
        self._tasks = []
        self._browser = None
        self._zeroconf = None
        self._ssdp_listeners = []
        self._ble = None
        self._popup_queue = []
        self._popup_task = None
        self._mdns_pending = set()
        self._background = set()
        self.ble_state = "off"
        self.running = False
        self.mqtt = MqttDiscovery(self)

    # --- frontends: the autodiscovery devices in FHEM ---

    @property
    def hash(self):
        return self.frontends[0].hash if self.frontends else None

    async def add_frontend(self, frontend):
        if frontend not in self.frontends:
            self.frontends.append(frontend)
        if not self.running:
            await self.start()
        else:
            await frontend.candidates_changed()

    async def remove_frontend(self, frontend):
        if frontend in self.frontends:
            self.frontends.remove(frontend)
        if not self.frontends and self.running:
            await self.stop()

    async def _notify_frontends(self):
        for frontend in list(self.frontends):
            try:
                await frontend.candidates_changed()
            except Exception:
                self.logger.exception("Failed to update autodiscovery device")

    # --- start/stop ---

    async def start(self):
        self.running = True
        self.catalog = await utils.run_blocking(functools.partial(catalog.load))
        await self.load_store()
        self._tasks.append(asyncio.create_task(self._start_mdns()))
        self._tasks.append(asyncio.create_task(self._ssdp_loop()))
        self._tasks.append(asyncio.create_task(self._search_loop()))
        self._tasks.append(asyncio.create_task(self._recheck_loop()))
        await self.update_ble()
        self.update_mqtt()

    def update_mqtt(self):
        """Starts or restarts MQTT discovery (attributes mqtt...)"""
        if self.frontends and hasattr(self.frontends[0], "mqtt_settings"):
            self.mqtt.configure(*self.frontends[0].mqtt_settings())
        else:
            self.mqtt.configure()

    async def stop(self):
        self.running = False
        self.mqtt.stop()
        for task in self._tasks:
            task.cancel()
        self._tasks = []
        if self._popup_task:
            self._popup_task.cancel()
            self._popup_task = None
        if self._browser:
            browser = self._browser
            self._browser = None
            try:
                await browser.async_cancel()
            except Exception:
                self.logger.exception("Failed to stop mDNS browser")
        for listener in self._ssdp_listeners:
            await ssdp.getInstance(self.logger).stop_search(listener)
        self._ssdp_listeners = []
        self._stop_ble()

    # --- store in FHEM ---

    async def load_store(self):
        cmd = f'my ($e, $v) = getKeyValue("{KEY}"); $v // ""'
        value = await fhem.sendCommandHash(self.hash, cmd)
        try:
            store = json.loads(value) if value else {}
        except (TypeError, ValueError):
            store = {}
        self.ignored = set(store.get("ignored", []))
        self.shown = set(store.get("shown", []))

    async def save_store(self):
        store = {"ignored": sorted(self.ignored), "shown": sorted(self.shown)}
        await fhem.sendCommandHash(
            self.hash, f'setKeyValue("{KEY}", {perl_json(store)}); ""'
        )

    # --- mDNS ---

    async def _start_mdns(self):
        types = sorted(set(catalog.mdns_types(self.catalog)) | {MQTT_MDNS_TYPE})
        try:
            self._zeroconf = zeroconf.get_instance(self.logger).get_async_zeroconf()
            self._browser = AsyncServiceBrowser(self._zeroconf.zeroconf, types, self)
        except Exception:
            self.logger.exception("Failed to start mDNS discovery")

    # zeroconf callbacks, they run in the event loop and mustn't wait
    def add_service(self, zc, service_type, name):
        self._mdns_task(service_type, name)

    def update_service(self, zc, service_type, name):
        self._mdns_task(service_type, name)

    def remove_service(self, zc, service_type, name):
        return

    def _mdns_task(self, service_type, name):
        key = (service_type, name)
        if key in self._mdns_pending or not self.running:
            return
        self._mdns_pending.add(key)
        task = asyncio.create_task(self.found_mdns(service_type, name))
        task.add_done_callback(lambda _: self._mdns_pending.discard(key))

    async def found_mdns(self, service_type, name):
        try:
            info = AsyncServiceInfo(service_type, name)
            if not await info.async_request(self._zeroconf.zeroconf, MDNS_INFO_TIMEOUT):
                return
            values = mdns_values(info)
        except Exception:
            self.logger.debug(f"No service info for {name}", exc_info=True)
            return
        if service_type == MQTT_MDNS_TYPE:
            self.mqtt.found_broker(values["ip"], values["port"])
        for entry, rule in catalog.match_mdns(self.catalog, service_type, values):
            await self.found(catalog.candidate(entry, rule, values, "mdns"), rule)

    # --- SSDP ---

    async def _ssdp_loop(self):
        types = catalog.ssdp_types(self.catalog)
        if not types:
            return
        searcher = ssdp.getInstance(self.logger)
        try:
            for device_type in types:
                listener = _SsdpListener(self)
                searcher.register_listener(listener, {"service_type": device_type})
                self._ssdp_listeners.append(listener)
                await searcher.start_search()
            while True:
                await asyncio.sleep(SSDP_INTERVAL)
                await searcher.search_once()
        except asyncio.CancelledError:
            raise
        except Exception:
            self.logger.exception("SSDP discovery failed")

    async def found_ssdp(self, upnp_device):
        values = {
            "udn": upnp_device.udn,
            "friendly_name": upnp_device.friendly_name,
            "manufacturer": upnp_device.manufacturer,
            "model_name": upnp_device.model_name,
            "device_type": upnp_device.device_type,
            "ip": urlsplit(upnp_device.device_url).hostname or "",
        }
        for entry, rule in catalog.match_ssdp(self.catalog, values):
            await self.found(catalog.candidate(entry, rule, values, "ssdp"), rule)

    # --- Bluetooth LE ---

    async def update_ble(self):
        """Starts or stops the shared Bluetooth scan (attribute ble)."""
        modes = [frontend.ble_mode() for frontend in self.frontends]
        mode = "off" if not modes or "off" in modes else modes[0]
        if mode == "off" or not any(catalog.rules(self.catalog, "ble")):
            self._stop_ble()
            self.ble_state = "off"
            return
        if self._ble is None:
            try:
                scanner_module = importlib.import_module("fhempy.lib.core.ble_scanner")
            except ImportError:
                self.ble_state = "not available (bleak missing)"
                return
            self._ble = scanner_module.BleScanner.get_instance(self.logger)
            self._ble.add_callback(self._ble_advertisement)
            self._ble.add_state_callback(self._ble_state_changed)
        interval = self.frontends[0].ble_interval()
        if mode == "interval":
            self._ble.set_mode("interval", interval)
        else:
            self._ble.set_mode("continuous", interval)
        self.ble_state = mode

    def _stop_ble(self):
        if self._ble is not None:
            self._ble.remove_callback(self._ble_advertisement)
            self._ble.remove_state_callback(self._ble_state_changed)
            self._ble = None

    def _ble_state_changed(self):
        self._run_later(self._notify_frontends())

    @property
    def ble_scanner(self):
        return self._ble

    def _ble_advertisement(self, device, advertisement):
        name = advertisement.local_name or device.name or ""
        uuids = {uuid.lower() for uuid in advertisement.service_uuids or []}
        uuids.update(uuid.lower() for uuid in (advertisement.service_data or {}))
        manufacturer_data = advertisement.manufacturer_data or {}
        matches = list(
            catalog.match_ble(
                self.catalog, name, manufacturer_data, uuids, advertisement.rssi
            )
        )
        if not matches:
            return
        values = {
            "address": device.address.upper(),
            "name": name,
            "rssi": advertisement.rssi,
            "homekit_id": catalog.homekit_id(manufacturer_data),
        }
        for entry, rule in matches:
            found = catalog.candidate(entry, rule, values, "ble")
            if found is None:
                continue
            known = self.candidates.get(found["id"])
            if known is not None:
                known["last_seen"] = time.time()
                known["rssi"] = advertisement.rssi
                continue
            # the callback mustn't wait
            self._run_later(self.found(found, rule))

    # --- search() of the modules ---

    async def _search_loop(self):
        await asyncio.sleep(5)
        while True:
            await self.search_all()
            await asyncio.sleep(SEARCH_INTERVAL)

    async def search_all(self):
        for entry, rule in list(catalog.rules(self.catalog, "search")):
            await self.search_module(entry, rule)

    async def search_module(self, entry, rule):
        module = entry["module"]
        found = []
        ctx = SearchContext(self.logger, found.append)
        try:
            discovery = await utils.run_blocking(
                functools.partial(
                    importlib.import_module, f"fhempy.lib.{module}.discovery"
                )
            )
            await asyncio.wait_for(discovery.search(ctx), SEARCH_TIMEOUT)
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError:
            self.logger.warning(f"search() of {module} took longer than 30s")
        except Exception:
            self.logger.exception(f"search() of {module} failed")
        for values in found:
            await self.found(catalog.candidate(entry, rule, values, "search"), rule)

    # --- devices found by other modules ---

    async def report(
        self,
        module,
        unique,
        title,
        kind,
        create,
        model="",
        hint="",
        logo="",
        check=None,
        recreate=None,
    ):
        """Devices found by other parts, e.g. MQTT discovery (mqtt.py).
        create: coroutine function called on a click on Create, returns an
        error text or ''. check: coroutine function, returns the name of the
        device in FHEM or ''. recreate: coroutine function called with the
        name of the existing device on a click on Set up again, returns an
        error text or ''."""
        entry = next((e for e in self.catalog if e["module"] == module), {})
        candidate = {
            "id": f"{module}:{unique}",
            "module": module,
            "unique": unique,
            "title": title,
            "model": model,
            "kind": kind,
            "name": catalog.device_name(title, module),
            "ip": "",
            "source": module,
            "action": "callback",
            "define": [],
            "params": [],
            "hint": hint,
            "exists": unique,
            "create": create,
        }
        if check is not None:
            candidate["check"] = check
        if recreate is not None:
            candidate["recreate"] = recreate
            candidate["can_recreate"] = True
        for key in ("logo", "icon"):
            if entry.get(key):
                candidate[key] = entry[key]
        if logo:
            candidate["logo"] = logo
        await self.found(candidate, {"exists": False})

    # --- found devices ---

    async def found(self, candidate, rule):
        if candidate is None or not self.running:
            return
        now = time.time()
        known = self.candidates.get(candidate["id"])
        if known is not None:
            known["last_seen"] = now
            if candidate.get("ip"):
                known["ip"] = candidate["ip"]
            return
        candidate["first_seen"] = now
        candidate["last_seen"] = now
        candidate["rule"] = rule
        # other updates run while FHEM is asked if the device exists
        candidate["status"] = STATUS_CHECKING
        self.candidates[candidate["id"]] = candidate
        try:
            exists = await self.exists(candidate, rule)
        except Exception:
            # try again when the device is seen next time
            del self.candidates[candidate["id"]]
            raise
        if exists:
            candidate["status"] = STATUS_EXISTS
            candidate["device"] = exists
            return
        self._set_open(candidate)
        await self._notify_frontends()

    def _set_open(self, candidate):
        """Status new or ignored, the popup for new devices not shown yet"""
        if candidate["id"] in self.ignored:
            candidate["status"] = STATUS_IGNORED
        else:
            candidate["status"] = STATUS_NEW
            self.logger.info(
                f"Found {candidate['kind']}: {candidate['title']} "
                f"({candidate['source']})"
            )
            if candidate["id"] not in self.shown:
                self._queue_popup(candidate["id"])

    async def exists(self, candidate, rule):
        """Name of the device in FHEM (any device of the module with the
        unique value in its definition or reading address), '' if none."""
        if candidate.get("check"):
            return await candidate["check"]() or ""
        if rule.get("exists") is False:
            return ""
        value = "" if rule.get("single") else candidate["exists"]
        cmd = (
            f"my $m = {fhem.perlString(candidate['module'])};; "
            f"my $u = lc({fhem.perlString(value)});; "
            "foreach my $d (keys %main::defs) { "
            "next if (($main::defs{$d}{FHEMPYTYPE} // '') ne $m);; "
            "return $d if ($u eq '');; "
            "return $d if (index(lc($main::defs{$d}{DEF} // ''), $u) >= 0);; "
            "return $d if (lc(ReadingsVal($d, 'address', '')) eq $u);; "
            "} return '';;"
        )
        return str(await fhem.sendCommandHash(self.hash, cmd) or "").strip()

    # --- devices deleted in FHEM ---

    async def _recheck_loop(self):
        while True:
            await asyncio.sleep(RECHECK_INTERVAL)
            try:
                await self.recheck()
            except asyncio.CancelledError:
                raise
            except Exception:
                self.logger.exception("Failed to check the existing devices")

    async def recheck(self):
        """Devices which exist(ed) in FHEM: deleted ones are offered again.
        Devices of a pairing (action set) stay as they are."""
        known = [
            c
            for c in self.candidates.values()
            if c["status"] in (STATUS_EXISTS, STATUS_CREATED) and c["action"] != "set"
        ]
        if not known:
            return
        names = sorted({c["device"] for c in known if c.get("device")})
        missing = set()
        if names:
            cmd = (
                "join(' ', grep { !defined($main::defs{$_}) } ("
                + ", ".join(fhem.perlString(n) for n in names)
                + "))"
            )
            missing = set(str(await fhem.sendCommandHash(self.hash, cmd) or "").split())
        changed = False
        for candidate in known:
            if candidate.get("device") and candidate["device"] not in missing:
                continue
            # deleted or renamed
            name = await self.exists(candidate, candidate.get("rule", {}))
            if name:
                candidate["device"] = name
                continue
            self.logger.info(f"{candidate['title']} was deleted, offered again")
            candidate.pop("device", None)
            candidate["deleted"] = True
            # no popup, the device was deleted on purpose
            self.shown.add(candidate["id"])
            self._set_open(candidate)
            changed = True
        if changed:
            await self._notify_frontends()

    def open_candidates(self):
        return [c for c in self.candidates.values() if c["status"] == STATUS_NEW]

    def forget_old(self):
        limit = time.time() - BLE_FORGET
        for key in [
            key
            for key, c in self.candidates.items()
            if c["source"] == "ble" and c["last_seen"] < limit
        ]:
            del self.candidates[key]

    # --- popup ---

    def _queue_popup(self, candidate_id):
        self._popup_queue.append(candidate_id)
        if self._popup_task is None or self._popup_task.done():
            self._popup_task = asyncio.create_task(self._popup_later())

    async def _popup_later(self):
        await asyncio.sleep(POPUP_DELAY)
        queue = self._popup_queue
        self._popup_queue = []
        try:
            await self.show_popup(queue)
        except Exception:
            self.logger.exception("Failed to show autodiscovery popup")

    async def show_popup(self, candidate_ids):
        # another fhempy (peer) might have shown it in the meantime
        await self.load_store()
        new = [
            self.candidates[cid]
            for cid in dict.fromkeys(candidate_ids)
            if cid in self.candidates
            and self.candidates[cid]["status"] == STATUS_NEW
            and cid not in self.shown
            and cid not in self.ignored
        ]
        if not new:
            return
        self.shown.update(c["id"] for c in new)
        await self.save_store()
        for frontend in self.frontends:
            if frontend.popup_enabled():
                await frontend.show_popup(new)
                break
        for frontend in self.frontends:
            await frontend.notify_phone(new)
            break

    # --- actions ---

    async def ignore(self, candidate_id):
        self.ignored.add(candidate_id)
        await self.save_store()
        if candidate_id in self.candidates:
            self.candidates[candidate_id]["status"] = STATUS_IGNORED
        await self._notify_frontends()

    async def unignore(self, candidate_id):
        self.ignored.discard(candidate_id)
        await self.save_store()
        candidate = self.candidates.get(candidate_id)
        if candidate is not None and candidate["status"] == STATUS_IGNORED:
            candidate["status"] = STATUS_NEW
        await self._notify_frontends()

    async def create(self, hash, candidate_id, name, params):
        """Creates the device, returns an error text or ''."""
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            return f"Device {candidate_id} isn't found (anymore)"
        missing = [
            prm["label"]
            for i, prm in enumerate(candidate["params"])
            if not prm.get("optional") and not params.get(i)
        ]
        if missing:
            return "Please fill in: " + ", ".join(missing)
        args = list(candidate["define"])
        for i in range(len(candidate["params"])):
            if params.get(i):
                args.append(params[i])
        if candidate["action"] == "callback":
            ret = await candidate["create"]()
        elif candidate["action"] == "set":
            ret = await self._create_with_set(hash, candidate, args)
        else:
            name = await self.free_name(hash, name or candidate["name"])
            definition = f"{name} fhempy {candidate['module']}"
            if args:
                definition += " " + " ".join(define_arg(arg) for arg in args)
            ret = await fhem.CommandDefine(hash, definition)
            candidate["device"] = name
        if ret:
            return str(ret)
        candidate.pop("deleted", None)
        candidate["status"] = STATUS_CREATED
        await self._notify_frontends()
        return ""

    async def recreate(self, candidate_id):
        """Sets up the existing device of the candidate again like a new
        device, its name in FHEM stays. Returns an error text or ''."""
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            return f"Device {candidate_id} isn't found (anymore)"
        if not candidate.get("recreate"):
            return f"{candidate['title']} can't be set up again"
        if candidate["status"] not in (STATUS_EXISTS, STATUS_CREATED) or not (
            candidate.get("device")
        ):
            return f"{candidate['title']} isn't in FHEM"
        ret = await candidate["recreate"](candidate["device"])
        return str(ret) if ret else ""

    def recreatable(self):
        """Devices in FHEM which can be set up again"""
        return [
            c
            for c in self.candidates.values()
            if c.get("recreate")
            and c.get("device")
            and c["status"] in (STATUS_EXISTS, STATUS_CREATED)
        ]

    async def _create_with_set(self, hash, candidate, params):
        """e.g. Matter: set <controller> pair <code>, the controller is created
        first if needed."""
        conf = candidate["set"]
        controller = await self.find_device(hash, conf["device"])
        args = list(conf.get("args", [])) + params
        command = " ".join([conf["command"], *(define_arg(a) for a in args)])
        if controller:
            candidate["device"] = controller
            return await fhem.sendCommandHash(
                hash, f"fhem({fhem.perlString(f'set {controller} {command}')}, 1)"
            )
        name = await self.free_name(hash, conf.get("name", conf["device"]))
        ret = await fhem.CommandDefine(hash, f"{name} fhempy {conf['device']}")
        if ret:
            return ret
        candidate["device"] = name
        self._run_later(self._set_when_ready(hash, name, command))
        return ""

    def _run_later(self, coro):
        # keep a reference, the event loop holds tasks only weakly
        task = asyncio.create_task(coro)
        self._background.add(task)
        task.add_done_callback(self._background.discard)

    async def _set_when_ready(self, hash, name, command, timeout=1800):
        """New controllers install their software first, up to some minutes."""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            await asyncio.sleep(10)
            state = await fhem.ReadingsVal(name, "state", "")
            if str(state).startswith("connected"):
                await fhem.sendCommandHash(
                    hash, f"fhem({fhem.perlString(f'set {name} {command}')}, 1)"
                )
                return
        self.logger.error(f"{name} didn't get ready, run: set {name} {command}")

    async def find_device(self, hash, fhempytype):
        cmd = (
            "my @d = grep { ($main::defs{$_}{FHEMPYTYPE} // '') eq "
            f"{fhem.perlString(fhempytype)} && "
            "($main::defs{$_}{DEF} // '') !~ /^\\S+\\s+\\S+\\s+\\S/ } "
            'sort keys %main::defs;; $d[0] // ""'
        )
        return str(await fhem.sendCommandHash(hash, cmd) or "").strip()

    async def free_name(self, hash, name):
        name = catalog.device_name(name, "device")
        cmd = (
            f"my $n = {fhem.perlString(name)};; my $c = $n;; my $i = 2;; "
            "while (defined($main::defs{$c})) { $c = $n . '_' . $i++ } $c"
        )
        free = str(await fhem.sendCommandHash(hash, cmd) or "").strip()
        return free or name


def define_arg(value):
    """FHEM define argument, quoted if needed"""
    value = str(value)
    if any(c.isspace() for c in value) or '"' in value:
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _decode(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def mdns_values(info):
    txt = {
        _decode(key): _decode(value) or ""
        for key, value in (info.properties or {}).items()
        if key is not None
    }
    addresses = info.parsed_addresses(IPVersion.V4Only)
    ip = ""
    for address in addresses:
        try:
            ipaddress.ip_address(address)
            ip = address
            break
        except ValueError:
            continue
    service_type = info.type
    name = info.name
    if name.endswith("." + service_type):
        name = name[: -len(service_type) - 1]
    return {
        "name": name,
        "host": (info.server or "").rstrip(".").removesuffix(".local"),
        "ip": ip,
        "port": info.port,
        "type": service_type,
        "txt": txt,
    }
