"""The tools the AI can use: read devices, switch them, create automations.

Everything goes through FHEM with Perl code built from perlString(), values
from the AI never end up unquoted in Perl. Passwords and other secrets are
removed before anything is returned to the AI, see SECRET_NAME/mask_text.
"""

import json
import re

from .. import fhem
from .protocol import Tool, ToolError

AUTOMATION_TYPES = ("DOIF", "notify", "at", "watchdog")
# devices the AI never sees: FHEM itself, logs, interfaces, fhempy
INTERNAL_TYPES = (
    "FHEMWEB",
    "telnet",
    "Global",
    "allowed",
    "autocreate",
    "eventTypes",
    "FileLog",
    "DbLog",
    "DbRep",
    "logProxy",
    "SVG",
    "weblink",
    "notice",
    "SingleFileLog",
    "BindingsIo",
    "fhempyServer",
    "PythonBinding",
    "MQTT2_SERVER",
    "msgConfig",
)
# only these attributes are sent to the AI, others might contain passwords
VISIBLE_ATTRS = (
    "alias",
    "room",
    "group",
    "comment",
    "genericDeviceType",
    "webCmd",
    "eventMap",
    "setList",
    "disable",
)
# attributes the AI may not set on its automations: they would bypass the
# approval or run Perl code even while the automation is disabled
PROTECTED_ATTRS = (
    "disable",
    "disabledForIntervals",
    "disabledAfterTrigger",
    "userattr",
    "userReadings",
    "stateFormat",
    "devStateIcon",
    "devStateStyle",
    "uiTable",
    "uiState",
)
ATTR_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
SECRET_NAME = re.compile(
    r"pass|pwd|token|secret|api_?key|credential|auth|cookie|session|private"
    r"|(^|[_-])pin($|[_-]|code)",
    re.IGNORECASE,
)
_URL_CREDENTIALS = re.compile(r"(://)[^/\s:@]+:[^/\s@]+@")
_KEY_VALUE = re.compile(
    r"((?:password|passwd|pwd|token|apikey|api_key|secret)\s*[=:]\s*[\"']?)"
    r"[^\s\"',;)}]+",
    re.IGNORECASE,
)
NAME_RE = re.compile(r"^[A-Za-z0-9._]+$")
MASK = "***"
MAX_DEVICES = 500
MAX_READINGS = 300
MAX_VALUE = 500
MAX_DEFINITION = 10000


def mask_text(text):
    """Remove credentials from a text, e.g. https://user:pw@host, pass=x"""
    if not isinstance(text, str):
        return text
    text = _URL_CREDENTIALS.sub(r"\1" + MASK + ":" + MASK + "@", text)
    return _KEY_VALUE.sub(r"\1" + MASK, text)


def mask_value(name, value):
    if SECRET_NAME.search(name or ""):
        return MASK
    if isinstance(value, str):
        value = mask_text(value)
        if len(value) > MAX_VALUE:
            value = value[:MAX_VALUE] + "..."
    return value


def check_name(name, what="device"):
    name = str(name or "").strip()
    if not NAME_RE.match(name) or len(name) > 100:
        raise ToolError(
            f"Invalid {what} name '{name}': use only letters, digits, '.' and '_'"
        )
    return name


def one_line(text, limit=300):
    return " ".join(str(text or "").split())[:limit]


def _list_contains(csv, value):
    return value.lower() in [v.strip().lower() for v in str(csv or "").split(",")]


def _types_regex(types):
    return "|".join(re.escape(t) for t in types)


class FhemTools:
    def __init__(self, module):
        # module: the mcp_server FhemModule (attributes, approval list)
        self.module = module

    @property
    def hash(self):
        return self.module.hash

    # --- FHEM access ---

    def scope_perl(self):
        """Perl code which fills %scope with all devices the AI may see:
        attribute devices (all if empty) and all automations, without
        hidden_devices, FHEM internals and the mcp_server devices"""
        spec = str(self.module._attr_devices or "").strip()
        hidden = str(self.module._attr_hidden_devices or "").strip()
        internal = _types_regex(INTERNAL_TYPES)
        return (
            "my %scope; {"
            f" my $spec = {fhem.perlString(spec)};"
            f" my $hide = {fhem.perlString(hidden)};"
            " my %h = map { $_ => 1 } ($hide ne '' ? devspec2array($hide) : ());"
            " my @c = $spec eq '' ? keys %defs : (devspec2array($spec),"
            " grep { defined($defs{$_}{TYPE})"
            f" && $defs{{$_}}{{TYPE}} =~ /^(?:{_types_regex(AUTOMATION_TYPES)})$/ }}"
            " keys %defs);"
            " foreach my $d (@c) {"
            " next if (!defined($defs{$d}) || $h{$d}); my $x = $defs{$d};"
            " next if ($x->{TEMPORARY} || defined($x->{SNIPPET}));"
            f" next if (($x->{{TYPE}} // '') =~ /^(?:{internal})$/);"
            " next if (($x->{FHEMPYTYPE} // '') eq 'mcp_server');"
            " $scope{$d} = 1 } }"
        )

    async def perl(self, code):
        return await fhem.sendCommandHash(self.hash, code)

    async def perl_json(self, code):
        result = await self.perl(code)
        try:
            return json.loads(result)
        except (TypeError, ValueError):
            if result in ("not_found", "automation"):
                return result
            self.module.logger.error(f"Unexpected answer from FHEM: {result}")
            raise ToolError("FHEM did not answer, is it running and connected?")

    # --- read tools ---

    async def list_rooms(self):
        devices = await self._devices()
        rooms = {}
        for dev in devices:
            for room in str(dev.get("room") or "").split(","):
                room = room.strip()
                if room and room != "hidden":
                    rooms[room] = rooms.get(room, 0) + 1
        return {
            "rooms": [{"room": r, "devices": n} for r, n in sorted(rooms.items())],
            "devices_without_room": sum(1 for d in devices if not d.get("room")),
        }

    async def _devices(self):
        auto = _types_regex(AUTOMATION_TYPES)
        code = (
            self.scope_perl() + " my @r; foreach my $d (sort keys %scope) {"
            f" my $x = $defs{{$d}}; next if ($x->{{TYPE}} =~ /^(?:{auto})$/);"
            " push @r, {name => $d, type => $x->{TYPE},"
            " alias => AttrVal($d, 'alias', ''), room => AttrVal($d, 'room', ''),"
            " genericDeviceType => AttrVal($d, 'genericDeviceType', ''),"
            " state => ($x->{STATE} // '')} } to_json(\\@r)"
        )
        devices = await self.perl_json(code)
        if not isinstance(devices, list):
            return []
        return [
            {
                k: mask_value(k, dev.get(k)) if k == "state" else dev.get(k)
                for k in ("name", "alias", "type", "room", "genericDeviceType", "state")
                if dev.get(k) not in (None, "")
            }
            for dev in devices
            if dev.get("name")
        ]

    async def list_devices(self, room="", type="", search=""):
        devices = await self._devices()
        room, type_, search = (str(v or "").strip() for v in (room, type, search))
        if room:
            devices = [d for d in devices if _list_contains(d.get("room"), room)]
        if type_:
            t = type_.lower()
            devices = [
                d
                for d in devices
                if t
                in (str(d.get("type")).lower(), str(d.get("genericDeviceType")).lower())
            ]
        if search:
            s = search.lower()
            devices = [
                d
                for d in devices
                if s in d["name"].lower() or s in str(d.get("alias")).lower()
            ]
        result = {"count": len(devices), "devices": devices[:MAX_DEVICES]}
        if len(devices) > MAX_DEVICES:
            result["note"] = (
                f"Only the first {MAX_DEVICES} devices are shown, filter by room, "
                "type or search."
            )
        return result

    async def get_device(self, name):
        name = check_name(name)
        attrs = ",".join(fhem.perlString(a) for a in VISIBLE_ATTRS)
        auto = _types_regex(AUTOMATION_TYPES)
        code = (
            self.scope_perl() + f" my $d = {fhem.perlString(name)};"
            " return 'not_found' if (!$scope{$d}); my $x = $defs{$d}; my %rd;"
            " foreach my $k (keys %{$x->{READINGS} // {}}) { next if ($k =~ /^\\./);"
            " $rd{$k} = {value => $x->{READINGS}{$k}{VAL},"
            " time => $x->{READINGS}{$k}{TIME}} }"
            f" my @ak = $x->{{TYPE}} =~ /^(?:{auto})$/"
            " ? keys %{$attr{$d} // {}} : (" + attrs + ");"
            " my %a; foreach my $k (@ak) {"
            " my $v = AttrVal($d, $k, undef); $a{$k} = $v if (defined($v)) }"
            " to_json({name => $d, type => $x->{TYPE}, state => ($x->{STATE} // ''),"
            f" definition => ($x->{{TYPE}} =~ /^(?:{auto})$/ ? $x->{{DEF}} : undef),"
            " readings => \\%rd, attributes => \\%a,"
            " commands => (getAllSets($d) // '')})"
        )
        dev = await self.perl_json(code)
        if dev == "not_found" or not isinstance(dev, dict):
            raise ToolError(
                f"Device '{name}' not found. Use list_devices to get the names, "
                "they are case sensitive."
            )
        readings = dev.get("readings") or {}
        dev = {k: dev.get(k) for k in ("name", "type", "state", "definition")} | {
            "attributes": dev.get("attributes") or {},
            "commands": dev.get("commands") or "",
        }
        dev["readings"] = {
            k: {"value": mask_value(k, v.get("value")), "time": v.get("time")}
            for k, v in sorted(readings.items())[:MAX_READINGS]
        }
        dev["attributes"] = {k: mask_value(k, v) for k, v in dev["attributes"].items()}
        dev["state"] = mask_value("state", dev.get("state"))
        if dev.get("definition") is None:
            dev.pop("definition", None)
        else:
            dev["definition"] = mask_text(dev["definition"])
        dev["commands"] = mask_text(dev["commands"]).strip()
        dev["commands_help"] = (
            "Commands for set_device, ':' lists the possible values, "
            "e.g. 'pct:slider,0,1,100' means 'pct 0' to 'pct 100'."
        )
        return dev

    async def list_automations(self):
        auto = _types_regex(AUTOMATION_TYPES)
        code = (
            self.scope_perl() + " my @r; foreach my $d (sort keys %scope) {"
            f" my $x = $defs{{$d}}; next if ($x->{{TYPE}} !~ /^(?:{auto})$/);"
            " push @r, {name => $d, type => $x->{TYPE},"
            " definition => ($x->{DEF} // ''), state => ($x->{STATE} // ''),"
            " disabled => AttrVal($d, 'disable', '0'),"
            " room => AttrVal($d, 'room', ''),"
            " comment => AttrVal($d, 'comment', '')} } to_json(\\@r)"
        )
        automations = await self.perl_json(code)
        if not isinstance(automations, list):
            automations = []
        await self.module.forget_missing([a["name"] for a in automations])
        automations = [
            {
                "name": a["name"],
                "type": a["type"],
                "definition": mask_text(a["definition"]),
                "comment": mask_text(a["comment"]),
                "room": a["room"],
                "state": mask_value("state", a["state"]),
                "disabled": a["disabled"] not in ("0", ""),
                "created_by_you": a["name"] in self.module.created,
                "waiting_for_approval": a["name"] in self.module.pending,
            }
            for a in automations
        ]
        return {"count": len(automations), "automations": automations}

    # --- write tools ---

    async def set_device(self, name, command):
        name = check_name(name)
        command = str(command or "").strip()
        if not command or "\n" in command or len(command) > 500:
            raise ToolError("command must be one line, e.g. 'on', 'off' or 'pct 50'")
        auto = _types_regex(AUTOMATION_TYPES)
        code = (
            self.scope_perl() + f" my $d = {fhem.perlString(name)};"
            " return 'not_found' if (!$scope{$d});"
            f" return 'automation' if ($defs{{$d}}{{TYPE}} =~ /^(?:{auto})$/);"
            f" my $e = CommandSet(undef, $d . ' ' . {fhem.perlString(command)});"
            " to_json({error => $e, state => ($defs{$d} ? $defs{$d}{STATE} : '')})"
        )
        result = await self.perl_json(code)
        if result == "not_found":
            raise ToolError(f"Device '{name}' not found, use list_devices.")
        if result == "automation":
            raise ToolError(
                "Automations can't be switched with set_device, use "
                "change_automation for automations you created."
            )
        error = result.get("error")
        if error:
            raise ToolError(f"FHEM: {mask_text(error)}")
        await self.module.log_action(f"set {name} {command}")
        return {
            "result": "ok",
            "state_now": mask_value("state", result.get("state")),
            "note": "Some devices update their state only a few seconds later.",
        }

    def _check_definition(self, definition):
        definition = str(definition or "").strip()
        if not definition:
            raise ToolError("definition is empty")
        if len(definition) > MAX_DEFINITION:
            raise ToolError("definition is too long")
        return definition

    def _approval_note(self, name, needs_approval):
        if needs_approval:
            return (
                f"The automation '{name}' is waiting for approval and does "
                "nothing yet. Tell the user to open the FHEM device "
                f"'{self.module.hash['NAME']}' in FHEMWEB and click 'Approve' "
                f"(or: set {self.module.hash['NAME']} approve {name})."
            )
        return f"The automation '{name}' is active."

    async def create_automation(self, name, type, definition, description=""):
        name = check_name(name, "automation")
        if type not in AUTOMATION_TYPES:
            raise ToolError(f"type must be one of {', '.join(AUTOMATION_TYPES)}")
        definition = self._check_definition(definition)
        approval = bool(self.module._attr_require_approval)
        room = one_line(self.module._attr_automation_room, 100)
        comment = one_line(description) or "created by AI"
        comment_attr = fhem.perlString(f"{name} comment AI: {comment}")
        code = (
            f"my $n = {fhem.perlString(name)};"
            " return to_json({error => 'A device with this name already exists,"
            " choose another name'}) if (defined($defs{$n}));"
            " my $e = CommandDefine(undef, "
            + fhem.perlString(f"{name} {type} {definition}")
            + "); return to_json({error => $e}) if (defined($e) && $e ne '');"
            " return to_json({error => 'FHEM did not create the device'})"
            " if (!defined($defs{$n}));"
            + (
                f" CommandAttr(undef, {fhem.perlString(name + ' disable 1')});"
                if approval
                else ""
            )
            + (
                f" CommandAttr(undef, {fhem.perlString(name + ' room ' + room)});"
                if room
                else ""
            )
            + f" CommandAttr(undef, {comment_attr});"
            " to_json({error => undef})"
        )
        result = await self.perl_json(code)
        if not isinstance(result, dict):
            raise ToolError("FHEM did not answer")
        if result.get("error"):
            raise ToolError(f"FHEM: {mask_text(result['error'])}")
        await self.module.add_created(name, approval)
        await self.module.log_action(f"created {type} {name}")
        return {"result": "ok", "note": self._approval_note(name, approval)}

    def _check_own(self, name):
        if name not in self.module.created:
            raise ToolError(
                f"'{name}' was not created by you. You may only change or delete "
                "automations you created, create a new one instead."
            )

    async def change_automation(self, name, definition, description=""):
        name = check_name(name, "automation")
        self._check_own(name)
        definition = self._check_definition(definition)
        approval = bool(self.module._attr_require_approval)
        comment = one_line(description)
        comment_attr = fhem.perlString(f"{name} comment AI: {comment}")
        code = (
            f"my $n = {fhem.perlString(name)};"
            " return to_json({error => 'not found'}) if (!defined($defs{$n})"
            f" || $defs{{$n}}{{TYPE}} !~ /^(?:{_types_regex(AUTOMATION_TYPES)})$/);"
            f" my $e = CommandModify(undef, {fhem.perlString(f'{name} {definition}')});"
            " return to_json({error => $e}) if (defined($e) && $e ne '');"
            + (
                f" CommandAttr(undef, {fhem.perlString(name + ' disable 1')});"
                if approval
                else ""
            )
            + (f" CommandAttr(undef, {comment_attr});" if comment else "")
            + " to_json({error => undef})"
        )
        result = await self.perl_json(code)
        if not isinstance(result, dict):
            raise ToolError("FHEM did not answer")
        if result.get("error") == "not found":
            await self.module.forget(name)
            raise ToolError(f"'{name}' doesn't exist anymore")
        if result.get("error"):
            raise ToolError(f"FHEM: {mask_text(result['error'])}")
        await self.module.add_created(name, approval)
        await self.module.log_action(f"changed {name}")
        return {"result": "ok", "note": self._approval_note(name, approval)}

    async def delete_automation(self, name):
        name = check_name(name, "automation")
        self._check_own(name)
        if not await self.module.delete_automation(name):
            raise ToolError(f"'{name}' doesn't exist anymore")
        await self.module.log_action(f"deleted {name}")
        return {"result": "ok", "note": f"'{name}' was deleted."}

    async def set_automation_attribute(self, name, attribute, value=""):
        name = check_name(name, "automation")
        self._check_own(name)
        attribute = str(attribute or "").strip()
        if not ATTR_NAME_RE.match(attribute) or len(attribute) > 100:
            raise ToolError(f"Invalid attribute name '{attribute}'")
        if attribute in PROTECTED_ATTRS:
            raise ToolError(
                f"The attribute '{attribute}' can only be set by the user in FHEM."
            )
        value = str(value if value is not None else "").strip()
        if len(value) > MAX_DEFINITION:
            raise ToolError("value is too long")
        approval = bool(self.module._attr_require_approval)
        if value:
            command = (
                f"CommandAttr(undef, {fhem.perlString(f'{name} {attribute} {value}')})"
            )
        else:
            command = (
                f"CommandDeleteAttr(undef, {fhem.perlString(f'{name} {attribute}')})"
            )
        code = (
            f"my $n = {fhem.perlString(name)};"
            " return to_json({error => 'not found'}) if (!defined($defs{$n})"
            f" || $defs{{$n}}{{TYPE}} !~ /^(?:{_types_regex(AUTOMATION_TYPES)})$/);"
            # disable first, the attribute must not act before the approval
            + (
                f" CommandAttr(undef, {fhem.perlString(name + ' disable 1')});"
                if approval
                else ""
            )
            + f" my $e = {command};"
            " to_json({error => (defined($e) && $e ne '' ? $e : undef),"
            f" value => AttrVal($n, {fhem.perlString(attribute)}, undef)}})"
        )
        result = await self.perl_json(code)
        if not isinstance(result, dict):
            raise ToolError("FHEM did not answer")
        if result.get("error") == "not found":
            await self.module.forget(name)
            raise ToolError(f"'{name}' doesn't exist anymore")
        await self.module.add_created(name, approval)
        if result.get("error"):
            raise ToolError(f"FHEM: {mask_text(result['error'])}")
        action = "set" if value else "deleted"
        await self.module.log_action(f"{action} attribute {attribute} of {name}")
        return {
            "result": "ok",
            "value_now": mask_value(attribute, result.get("value")),
            "note": self._approval_note(name, approval),
        }

    async def fhem_command(self, command):
        command = str(command or "").strip()
        if not command:
            raise ToolError("command is empty")
        code = (
            f"my $r = AnalyzeCommandChain(undef, {fhem.perlString(command)});"
            " defined($r) ? $r : ''"
        )
        result = await self.perl(code)
        await self.module.log_action(f"command {one_line(command, 100)}")
        return mask_text(str(result or "")) or "ok, no output"

    # --- tool list ---

    def tools(self):
        m = self.module
        tools = [
            Tool(
                "list_rooms",
                "List the rooms in FHEM with the number of devices in each room.",
                self.list_rooms,
                title="List rooms",
                read_only=True,
            ),
            Tool(
                "list_devices",
                "List FHEM devices with name, alias, type, room, "
                "genericDeviceType and current state. All filters are optional "
                "and case insensitive.",
                self.list_devices,
                {
                    "room": {"type": "string", "description": "only this room"},
                    "type": {
                        "type": "string",
                        "description": "FHEM TYPE (e.g. HUEDevice, dummy, "
                        "PRESENCE) or genericDeviceType (e.g. light, switch, "
                        "blind, thermostat)",
                    },
                    "search": {
                        "type": "string",
                        "description": "part of the name or alias, e.g. 'lamp'",
                    },
                },
                title="List devices",
                read_only=True,
            ),
            Tool(
                "get_device",
                "Details of one FHEM device or automation: readings (values "
                "with time), attributes and the commands it supports (for "
                "set_device and automations).",
                self.get_device,
                {"name": {"type": "string", "description": "exact device name"}},
                ["name"],
                title="Get device",
                read_only=True,
            ),
            Tool(
                "list_automations",
                "List the automations in FHEM (DOIF, notify, at, watchdog) with "
                "their definition, whether you created them and whether they "
                "are waiting for the user's approval.",
                self.list_automations,
                title="List automations",
                read_only=True,
            ),
        ]
        if m._attr_allow_set:
            tools.append(
                Tool(
                    "set_device",
                    "Switch or control a device, like 'set <name> <command>' in "
                    "FHEM. Use a command listed by get_device, e.g. 'on', 'off', "
                    "'toggle', 'pct 50', 'desired-temp 21'.",
                    self.set_device,
                    {
                        "name": {"type": "string", "description": "exact device name"},
                        "command": {
                            "type": "string",
                            "description": "command with its value, e.g. 'pct 50'",
                        },
                    },
                    ["name", "command"],
                    title="Control device",
                    destructive=True,
                )
            )
        if m._attr_allow_automations:
            tools += [
                Tool(
                    "create_automation",
                    "Create an automation (rule) in FHEM, e.g. 'switch off all "
                    "lights when everybody left'. Read the server instructions "
                    "for the syntax. The result says whether the user has to "
                    "approve it first.",
                    self.create_automation,
                    {
                        "name": {
                            "type": "string",
                            "description": "new unique device name, letters, "
                            "digits and _ only, e.g. ai_lights_off_absent",
                        },
                        "type": {
                            "type": "string",
                            "enum": list(AUTOMATION_TYPES),
                            "description": "DOIF (recommended), notify, at or watchdog",
                        },
                        "definition": {
                            "type": "string",
                            "description": "everything after "
                            "'define <name> <type> ', e.g. for DOIF "
                            "'([Home] eq \"absent\") (set Lamp1 off, set Lamp2 off)'",
                        },
                        "description": {
                            "type": "string",
                            "description": "one sentence what it does, shown "
                            "to the user",
                        },
                    },
                    ["name", "type", "definition"],
                    title="Create automation",
                    destructive=True,
                ),
                Tool(
                    "change_automation",
                    "Change the definition of an automation you created. The "
                    "type stays the same.",
                    self.change_automation,
                    {
                        "name": {"type": "string"},
                        "definition": {
                            "type": "string",
                            "description": "new definition (everything after "
                            "'define <name> <type> ')",
                        },
                        "description": {"type": "string"},
                    },
                    ["name", "definition"],
                    title="Change automation",
                    destructive=True,
                ),
                Tool(
                    "set_automation_attribute",
                    "Set or delete an attribute of an automation you created, "
                    "e.g. for DOIF 'do' = 'always', 'wait' = '300', 'cmdState', "
                    "'repeatsame', 'checkReadingEvent'. get_device shows the "
                    "current attributes. Not allowed: "
                    + ", ".join(PROTECTED_ATTRS)
                    + ".",
                    self.set_automation_attribute,
                    {
                        "name": {"type": "string"},
                        "attribute": {"type": "string", "description": "e.g. do"},
                        "value": {
                            "type": "string",
                            "description": "e.g. always; empty deletes the "
                            "attribute",
                        },
                    },
                    ["name", "attribute"],
                    title="Set automation attribute",
                    destructive=True,
                ),
                Tool(
                    "delete_automation",
                    "Delete an automation you created.",
                    self.delete_automation,
                    {"name": {"type": "string"}},
                    ["name"],
                    title="Delete automation",
                    destructive=True,
                ),
            ]
        if m._attr_allow_fhem_command:
            tools.append(
                Tool(
                    "fhem_command",
                    "Run any FHEM command (like in the FHEMWEB command field), "
                    "e.g. 'list TYPE=dummy' or 'attr Lamp1 alias Lamp'. Prefer "
                    "the other tools.",
                    self.fhem_command,
                    {"command": {"type": "string"}},
                    ["command"],
                    title="FHEM command",
                    destructive=True,
                )
            )
        return tools


def instructions(device_name, approval):
    if approval:
        approval_text = (
            "New and changed automations are created DISABLED. The user has to "
            f"approve them: FHEMWEB, device '{device_name}', button 'Approve'. "
            "Always tell the user what you created and that it needs approval."
        )
    else:
        approval_text = "New and changed automations are active immediately."
    return f"""You are connected to FHEM, a home automation server.

How to work:
1. Find devices with list_devices (filter by room, type or search) or list_rooms.
   Device names are case sensitive. The alias is the name the user knows.
2. Call get_device before you control a device or use it in an automation: it
   shows the readings and the supported commands.
3. set_device controls a device right now, e.g. command 'on', 'off', 'pct 50'.
   Ask the user before you switch many devices at once.
4. For rules ("when X happens, do Y") use create_automation, preferably DOIF.
   Check list_automations first to avoid duplicates. {approval_text}
   You may only change or delete automations you created yourself, and set
   their attributes with set_automation_attribute (e.g. DOIF: do always,
   wait 300).

Presence: look for devices of type PRESENCE, ROOMMATE, GUEST, RESIDENTS,
GEOFANCY or a dummy named like home/presence/Anwesenheit; their state is e.g.
present/absent, home/absent/gone. Lights: genericDeviceType light, or type
HUEDevice, or 'lamp', 'light', 'Licht', 'Lampe' in name or alias.

DOIF definition: (condition) (commands) DOELSEIF (condition) (commands) ...
- [Device] is the state, [Device:reading] a reading. Text with eq/ne, numbers
  with == < > (e.g. [Sensor:temperature] > 25).
- Times: [08:00] (at 08:00), [08:00-22:00] (between), [+00:30] (every 30 min).
  Weekdays: [08:00|8] for workdays, [08:00|7] for weekends.
- Commands are FHEM commands separated by commas, so write one set per
  device: (set Lamp1 off, set Lamp2 off). Never write set Lamp1,Lamp2 in a DOIF.
- A DOIF only reacts on devices in [ ]. It runs a command once when its
  condition becomes true, not again while it stays true.
- Example: ([Residents] eq "absent") (set Lamp_kitchen off, set Lamp_living off)
- Example: ([Sensor:motion] eq "on" and [18:00-23:00]) (set Lamp1 on)
notify definition: <device regex>:<event regex> <command>
- Example: Residents:absent set Lamp1,Lamp2 off
at definition: *08:00 set Lamp1 on (daily), +00:10:00 set Lamp1 off (once)

After an automation ran, get_device shows its readings; DOIF writes failed
commands into the reading 'error'.

Answer in the language of the user. Use the alias when talking to the user."""
