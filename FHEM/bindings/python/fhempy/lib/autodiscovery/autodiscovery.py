import html
import json

from .. import fhem, generic
from . import residents
from .engine import STATUS_IGNORED, STATUS_NEW, Engine

USAGE = "Usage: define fhempy_discovery fhempy autodiscovery"
MAX_PARAMS = 6


def js_value(value):
    return json.dumps(value, ensure_ascii=False).replace("<", generic._JS_ESCAPED_LT)


class autodiscovery(generic.FhemModule):
    """Finds devices in the network and via Bluetooth and offers to create
    them in a popup. All autodiscovery devices of a fhempy share one engine."""

    def __init__(self, logger):
        super().__init__(logger)
        self.engine = None
        self._attr_popup = 1
        self._attr_ble = "continuous"
        self._attr_ble_interval = 300
        self._attr_notify = ""
        self._attr_mqtt = "auto"
        self._attr_mqtt_username = ""
        self._attr_mqtt_password = ""
        self._search = {}
        # devices created by the resident and tag dialogs, for the link
        self._created = {}

    @staticmethod
    def validate_define(args, argsh):
        if len(args) != 3 or argsh:
            return USAGE
        return None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        error = self.validate_define(args, argsh)
        if error:
            return error
        await super().Define(hash, args, argsh)
        await self.set_attr_config(
            {
                "popup": {
                    "default": 1,
                    "format": "int",
                    "options": "0,1",
                    "help": "Show a popup on all open FHEMWEB pages when a new "
                    "device is found (default 1).",
                },
                "ble": {
                    "default": "continuous",
                    "options": "continuous,interval,off",
                    "help": "Bluetooth scan: continuous (default, pauses while "
                    "modules connect), interval (10s every ble_interval seconds) "
                    "or off.",
                },
                "ble_interval": {
                    "default": 300,
                    "format": "int",
                    "help": "Seconds between two Bluetooth scans with ble interval "
                    "(default 300). The scan falls back to it for an hour after "
                    "the Bluetooth adapter had to be reset.",
                },
                "notify": {
                    "default": "",
                    "help": "Name of a push device, new devices are also sent "
                    "to the phones.",
                },
                "mqtt": {
                    "default": "auto",
                    "help": "MQTT broker for Home Assistant MQTT discovery: auto "
                    "(default: broker on this computer, brokers announced via "
                    "mDNS and of mqtt_ha_discovery), off or host[:port].",
                },
                "mqtt_username": {
                    "default": "",
                    "help": "Username of the MQTT broker, if needed.",
                },
                "mqtt_password": {
                    "default": "",
                    "help": "Password of the MQTT broker, if needed.",
                },
            }
        )
        await self.set_set_config(
            {
                "scan": {"help": "Search for devices right now."},
                "create": {
                    "args": ["id"],
                    "argsh": ["name"] + [f"p{i}" for i in range(MAX_PARAMS)],
                    "help": "Creates a found device: create &lt;id&gt; "
                    "[name=&lt;device name&gt;] [p0=&lt;value&gt;...]",
                },
                "createAll": {
                    "help": "Creates all found devices which need no input."
                },
                "ignore": {"args": ["id"], "help": "Don't offer this device again."},
                "unignore": {
                    "args": ["id"],
                    "help": "Offer an ignored device again.",
                },
                "searchPhones": {
                    "help": "Searches the phones in the network, see Add resident."
                },
                "searchBluetooth": {
                    "help": "Searches visible Bluetooth phones for 20s."
                },
                "searchTag": {
                    "help": "Searches the Bluetooth tag held next to the "
                    "Raspberry Pi for 15s."
                },
                "addResident": {
                    "argsh": ["person", "mac", "bt"],
                    "help": "addResident person=&lt;name&gt; [mac=&lt;MAC&gt;] "
                    "[bt=&lt;Bluetooth address&gt;]: creates a ROOMMATE "
                    "with the phone in the network and via Bluetooth.",
                },
                "addTag": {
                    "argsh": ["title", "address"],
                    "help": "addTag title=&lt;name&gt; address=&lt;address&gt;: "
                    "presence of a Bluetooth tag.",
                },
            }
        )
        await self.set_get_config(
            {
                "candidates": {"help": "Found devices as JSON."},
                "device": {
                    "args": ["id"],
                    "help": "Name of the FHEM device created for a found device "
                    "(id), or the last added resident or tag.",
                },
                "search": {
                    "args": ["kind"],
                    "help": "Result of searchPhones, searchBluetooth or searchTag "
                    "as JSON.",
                },
            }
        )
        await self.set_icon("rc_SEARCH")
        self.engine = Engine.get_instance(self.logger)
        await self.engine.add_frontend(self)

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await super().Undefine(hash)
        if self.engine is not None:
            await self.engine.remove_frontend(self)

    # --- used by the engine ---

    def ble_mode(self):
        return self._attr_ble

    def ble_interval(self):
        return self._attr_ble_interval

    def popup_enabled(self):
        return self._attr_popup == 1

    def mqtt_settings(self):
        return (self._attr_mqtt, self._attr_mqtt_username, self._attr_mqtt_password)

    async def candidates_changed(self):
        self.engine.forget_old()
        count = len(self.engine.open_candidates())
        await fhem.readingsBeginUpdate(self.hash)
        try:
            await fhem.readingsBulkUpdateIfChanged(
                self.hash,
                "state",
                {0: "no new devices", 1: "1 new device"}.get(
                    count, f"{count} new devices"
                ),
            )
            await fhem.readingsBulkUpdateIfChanged(self.hash, "new_devices", count)
            ble = self.engine.ble_state
            scanner = self.engine.ble_scanner
            if scanner is not None and scanner.scanning:
                ble += f" ({scanner.scanning})"
            await fhem.readingsBulkUpdateIfChanged(self.hash, "bluetooth", ble)
            await fhem.readingsBulkUpdateIfChanged(
                self.hash, "bluetooth_warning", self.ble_warning() or "none"
            )
        finally:
            await fhem.readingsEndUpdate(self.hash, 1)

    def ble_warning(self):
        """Text if the Bluetooth scan can't run passively, '' otherwise"""
        scanner = self.engine.ble_scanner if self.engine else None
        problem = scanner.passive_problem if scanner is not None else ""
        if not problem:
            return ""
        # bleak is a requirement of this module, imported only when needed
        from ..core import ble_scanner

        if problem == ble_scanner.PASSIVE_NEEDS_EXPERIMENTAL:
            return (
                "BlueZ runs without --experimental, Bluetooth is scanned actively. "
                "That disturbs WiFi and connected Bluetooth devices more."
            )
        if problem == ble_scanner.PASSIVE_NEEDS_KERNEL:
            return (
                "Linux kernel older than 5.10, Bluetooth is scanned actively. "
                "Update the operating system to scan passively."
            )
        return ""

    def ble_warning_html(self):
        warning = self.ble_warning()
        if not warning:
            return ""
        box = (
            '<div style="margin:0 0 12px;padding:10px 14px;border-radius:10px;'
            'border:1px solid #e0a000;background:rgba(224,160,0,0.12)">'
            f"<b>&#9888; {html.escape(warning)}</b>"
        )
        from ..core import ble_scanner

        if self.engine.ble_scanner.passive_problem != (
            ble_scanner.PASSIVE_NEEDS_EXPERIMENTAL
        ):
            return box + "</div>"
        command = ble_scanner.EXPERIMENTAL_COMMAND
        copy = (
            "var t=document.getElementById('fhempyBlueZCmd');t.select();"
            "if(navigator.clipboard){navigator.clipboard.writeText(t.value)}"
            "else{document.execCommand('copy')}"
            "this.innerText='Copied';return false;"
        )
        return (
            box
            + "<div style='margin:6px 0'>Run this once in a terminal of the "
            "Raspberry Pi, it starts BlueZ with --experimental, also after a "
            "reboot. fhempy switches to the passive scan within an hour, or right "
            "away after a restart of fhempy.</div>"
            '<textarea id="fhempyBlueZCmd" readonly rows="4" '
            'style="width:100%;box-sizing:border-box;font-family:monospace;'
            'font-size:12px">'
            f"{html.escape(command)}</textarea>"
            f'<a href="#" onclick="{html.escape(copy)}" style="display:inline-block;'
            "margin-top:6px;padding:3px 12px;border-radius:12px;background:#4B8BBE;"
            'color:#fff;text-decoration:none">Copy command</a></div>'
        )

    def popup_javascript(self, function, *args):
        params = ",".join(js_value(arg) for arg in (self.hash["NAME"], *args))
        return (
            'jQuery.getScript(FW_root+"/fhempy/discovery.js",'
            f"function(){{fhempyDiscovery.{function}({params})}})"
        )

    async def show_popup(self, candidates):
        await fhem.FW_runJavascript(
            self.hash, self.popup_javascript("popup", public(candidates))
        )

    async def notify_phone(self, candidates):
        if not self._attr_notify:
            return
        names = ", ".join(f"{c['title']} ({c['kind']})" for c in candidates)
        url = f"?detail={self.hash['NAME']}"
        command = (
            f"set {self._attr_notify} message title=\"New device found\" "
            f"url={url} {names}"
        )
        await fhem.sendCommandHash(
            self.hash, f"fhem({fhem.perlString(command)}, 1)"
        )

    # --- attributes ---

    async def set_attr_ble(self, hash):
        if self.engine is not None and self.engine.running:
            await self.engine.update_ble()

    async def set_attr_ble_interval(self, hash):
        await self.set_attr_ble(hash)

    async def set_attr_mqtt(self, hash):
        if self.engine is not None and self.engine.running:
            self.engine.update_mqtt()

    async def set_attr_mqtt_username(self, hash):
        await self.set_attr_mqtt(hash)

    async def set_attr_mqtt_password(self, hash):
        await self.set_attr_mqtt(hash)

    # --- set ---

    async def set_scan(self, hash, params):
        self.create_async_task(self.engine.search_all())

    async def set_create(self, hash, params):
        values = {}
        for i in range(MAX_PARAMS):
            if params.get(f"p{i}"):
                values[i] = str(params[f"p{i}"])
        return await self.engine.create(
            self.hash, params["id"], params.get("name", ""), values
        )

    async def set_createAll(self, hash, params):
        errors = []
        for candidate in self.engine.open_candidates():
            if candidate["params"] or candidate["action"] != "define":
                continue
            ret = await self.engine.create(self.hash, candidate["id"], "", {})
            if ret:
                errors.append(f"{candidate['title']}: {ret}")
        return "\n".join(errors)

    async def set_ignore(self, hash, params):
        await self.engine.ignore(params["id"])

    async def set_unignore(self, hash, params):
        await self.engine.unignore(params["id"])

    def _start_search(self, kind, coro):
        previous = self._search.get(kind)
        if previous and previous.get("task") and not previous["task"].done():
            coro.close()
            return
        entry = {"state": "searching", "result": None}
        self._search[kind] = entry

        async def run():
            try:
                entry["result"] = await coro
                entry["state"] = "done"
            except Exception as exc:
                self.logger.exception(f"{kind} search failed")
                entry["state"] = "failed"
                entry["error"] = str(exc) or exc.__class__.__name__

        entry["task"] = self.create_async_task(run())

    async def set_searchPhones(self, hash, params):
        self._start_search("phones", residents.find_phones(self.hash, self.logger))

    async def set_searchBluetooth(self, hash, params):
        self._start_search(
            "bluetooth",
            residents.find_bluetooth_phones(
                self.hash, self.logger, self.engine.ble_scanner
            ),
        )

    async def set_searchTag(self, hash, params):
        scanner = self.engine.ble_scanner
        if scanner is None:
            return "Bluetooth scan is off or not available (attribute ble)"
        self._start_search("tag", residents.find_tag(self.hash, scanner))

    async def set_addResident(self, hash, params):
        error, name = await residents.create_resident(
            self.hash,
            params.get("person", ""),
            params.get("mac", ""),
            params.get("bt", ""),
        )
        self._created["resident"] = name
        return error

    async def set_addTag(self, hash, params):
        if not params.get("address"):
            return "address missing"
        error, name = await residents.create_tag(
            self.hash, params.get("title") or "tag", params["address"]
        )
        self._created["tag"] = name
        return error

    # --- get ---

    async def get_candidates(self, hash, params):
        listed = [
            c
            for c in self.engine.candidates.values()
            if c["status"] in (STATUS_NEW, STATUS_IGNORED)
        ]
        return json.dumps(public(listed), ensure_ascii=False)

    async def get_device(self, hash, params):
        """Name of the created device: candidate id, resident or tag"""
        candidate = self.engine.candidates.get(params["id"]) or {}
        return candidate.get("device") or self._created.get(params["id"], "")

    async def get_search(self, hash, params):
        entry = self._search.get(params["kind"])
        if entry is None:
            return json.dumps({"state": "idle"})
        return json.dumps(
            {
                "state": entry["state"],
                "result": entry.get("result"),
                "error": entry.get("error", ""),
            },
            ensure_ascii=False,
        )

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        detail = await super().FW_detailFn(hash, args, argsh)
        button = (
            '<a href="#" onclick="{js};return false;" style="display:inline-block;'
            "margin:0 10px 10px 0;padding:4px 14px;border-radius:14px;"
            'background:#4B8BBE;text-decoration:none;white-space:nowrap">'
            '<span style="color:#fff;font-weight:600">{text}</span></a>'
        )
        count = len(self.engine.open_candidates()) if self.engine else 0
        buttons = [
            (self.popup_javascript("list"), f"&#128269; Found devices ({count})"),
            (self.popup_javascript("residents"), "&#127968; Add resident"),
            (self.popup_javascript("tag"), "&#127991; Add Bluetooth tag"),
        ]
        ret = "".join(
            button.format(js=html.escape(js), text=text) for js, text in buttons
        )
        return (
            self.ble_warning_html()
            + f'<div id="fhempyDiscoveryButtons">{ret}</div>'
            + str(detail)
        )


def public(candidates):
    """The values of the candidates the browser needs"""
    keys = (
        "id",
        "module",
        "title",
        "model",
        "kind",
        "name",
        "ip",
        "action",
        "params",
        "hint",
        "logo",
        "icon",
        "prefill",
        "status",
        "source",
    )
    return [{k: c[k] for k in keys if k in c} for c in candidates]
