"""Dependency index over all automations of FHEM (DOIF, notify, at, watchdog).

Which rule reads which device, which rule writes which device, the health
check, the day plan and the relation map are computed from it. The texts of
the results are composed by the frontend from "kind" and the parameters, so
German and English work the same way."""

import datetime
import re

from . import parser

RULE_TYPES = ("DOIF", "notify", "at", "watchdog")
TIMESTAMP_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})")
DEAD_DAYS = 90


def fhem_time(text):
    """FHEM time stamp 2026-11-02 18:00:00 -> epoch seconds"""
    try:
        return datetime.datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S").timestamp()
    except (TypeError, ValueError):
        return None


def doif_time(text):
    """DOIF time stamp 02.11.2026 18:00:00 -> datetime"""
    match = TIMESTAMP_RE.search(text or "")
    if not match:
        return None
    day, month, year, hour, minute, second = (int(x) for x in match.groups())
    try:
        return datetime.datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None


def split_event_regex(regex):
    """device part and event part of a notify regex like lamp:on"""
    regex = regex.strip()
    if regex.startswith("(") and regex.endswith(")"):
        regex = regex[1:-1]
    if ":" in regex:
        device, event = regex.split(":", 1)
        return device, event
    return regex, ".*"


def regex_devices(regex, names):
    """device names a notify/watchdog regex matches"""
    device, _ = split_event_regex(regex)
    try:
        pattern = re.compile("^(?:" + device + ")$")
    except re.error:
        return []
    return sorted(name for name in names if pattern.match(name))


class Rule:
    def __init__(self, info):
        self.name = info["NAME"]
        self.type = info["TYPE"]
        self.definition = info.get("DEF", "")
        self.attrs = info.get("attrs", {}) or {}
        self.readings = info.get("readings", {}) or {}
        self.times = info.get("times", {}) or {}
        self.internals = info.get("internals", {}) or {}
        self.room = self.attrs.get("room", "")
        self.alias = self.attrs.get("alias", "")
        self.disabled = self.attrs.get("disable", "0") not in ("", "0") or (
            self.readings.get("mode") == "disabled"
        )
        self.model = None
        self.triggers = set()  # (device, reading) or ("@regex", reading)
        self.checks = set()
        self.writes = {}  # device -> set of commands
        self.timers = []  # timer leaves of the parser model
        self.trigger_regex = []  # notify / watchdog regexes
        self.error = ""

    def last_run(self):
        """epoch seconds of the last execution or None"""
        if self.type == "DOIF":
            # after define or modify DOIF sets cmd 0 without executing
            if str(self.readings.get("cmd", "0")) in ("", "0"):
                return None
            return fhem_time(self.times.get("cmd") or self.times.get("cmd_nr"))
        if self.type in ("notify", "watchdog"):
            return fhem_time(
                self.times.get("triggeredByDev") or self.times.get("state")
            )
        if self.type == "at":
            return fhem_time(self.times.get("state"))
        return None

    def as_dict(self, short=True):
        result = {
            "name": self.name,
            "type": self.type,
            "alias": self.alias,
            "room": self.room,
            "disabled": self.disabled,
            "state": self.readings.get("state", ""),
            "last": self.last_run(),
            "reads": sorted({dev for dev, _ in self.triggers | self.checks}),
            "triggers": sorted({dev for dev, _ in self.triggers}),
            "writes": sorted(self.writes),
            "error": self.error,
        }
        if self.model is not None:
            visual, total = parser.visual_share(self.model)
            result["visual"] = visual
            result["total"] = total
            result["cases"] = len(self.model.get("cases", []))
            result["comment"] = next(
                (
                    c.get("comment")
                    for c in self.model.get("cases", [])
                    if c.get("comment")
                ),
                "",
            )
        if not short:
            result["def"] = self.definition
            result["attrs"] = self.attrs
            result["readings"] = self.readings
        return result


class Index:
    def __init__(self, rules, devices, editor="", values=()):
        """rules and devices: lists of infos from FHEM (see doif_editor.py)"""
        self.devices = {info["NAME"]: info for info in devices}
        self.editor = editor
        self.values = list(values)
        self.rules = {}
        for info in rules:
            if info.get("TYPE") not in RULE_TYPES:
                continue
            rule = Rule(info)
            self._analyse(rule)
            self.rules[rule.name] = rule
        self.reverse_reads = {}
        self.reverse_writes = {}
        for rule in self.rules.values():
            for device, _ in rule.triggers | rule.checks:
                self.reverse_reads.setdefault(device, set()).add(rule.name)
            for device in rule.writes:
                self.reverse_writes.setdefault(device, set()).add(rule.name)

    # --- analysis -----------------------------------------------------------

    def _analyse(self, rule):
        names = self.devices.keys()
        if rule.type == "DOIF":
            rule.model = parser.parse_rule(rule.definition, rule.attrs)
            rule.model["name"] = rule.name
            rule.error = rule.model.get("error", "")
            triggers, checks, writes, timers = parser.reads_and_writes(rule.model)
            rule.triggers = {self._self(rule, pair) for pair in triggers}
            rule.checks = {self._self(rule, pair) for pair in checks}
            rule.writes = writes
            rule.timers = timers
            # aggregations [#"regex"...] read all matching devices
            for device, reading in list(rule.triggers):
                if device.startswith("@"):
                    rule.trigger_regex.append(device[1:])
                    for name in regex_devices(device[1:], names):
                        rule.triggers.add((name, reading))
        elif rule.type == "notify":
            regex, _, command = rule.definition.partition(" ")
            rule.trigger_regex.append(regex)
            for name in regex_devices(regex, names):
                rule.triggers.add((name, "state"))
            self._writes_from_text(rule, command)
        elif rule.type == "watchdog":
            parts = rule.definition.split(None, 3)
            if len(parts) == 4:
                regex1, timeout, regex2, command = parts
                rule.trigger_regex.extend([regex1, regex2])
                for name in regex_devices(regex1, names) + regex_devices(regex2, names):
                    rule.triggers.add((name, "state"))
                rule.timers.append({"t": "watchdog", "timeout": timeout})
                self._writes_from_text(rule, command)
        elif rule.type == "at":
            spec, _, command = rule.definition.partition(" ")
            rule.timers.append({"t": "at", "spec": spec})
            self._writes_from_text(rule, command)

    def _self(self, rule, pair):
        return (rule.name, pair[1]) if pair[0] == "$SELF" else pair

    @staticmethod
    def _writes_from_text(rule, text):
        for device, value in parser.writes_in_text(text):
            rule.writes.setdefault(device, set()).add(value)

    # --- questions ----------------------------------------------------------

    def device_box(self, device):
        """'Who controls this?' for a device page"""
        controls = []
        for name in sorted(self.reverse_writes.get(device, ())):
            rule = self.rules[name]
            controls.append(
                {
                    "rule": name,
                    "type": rule.type,
                    "alias": rule.alias,
                    "values": sorted(rule.writes.get(device, ())),
                    "disabled": rule.disabled,
                    "last": rule.last_run(),
                }
            )
        uses = []
        for name in sorted(self.reverse_reads.get(device, ())):
            rule = self.rules[name]
            readings = sorted(
                {r for d, r in rule.triggers | rule.checks if d == device}
            )
            uses.append(
                {
                    "rule": name,
                    "type": rule.type,
                    "alias": rule.alias,
                    "readings": readings,
                    "trigger": any(d == device for d, _ in rule.triggers),
                    "disabled": rule.disabled,
                }
            )
        conflict = len([c for c in controls if not c["disabled"]]) > 1
        return {
            "device": device,
            "controls": controls,
            "uses": uses,
            "conflict": conflict,
        }

    def overview(self):
        return [
            rule.as_dict()
            for rule in sorted(self.rules.values(), key=lambda r: r.name.lower())
        ]

    def graph(self, focus_kind="house", focus=""):
        """relation map: inputs -> rules -> devices around a focus.
        focus_kind: device, rule, room or house"""
        selected = set()
        if focus_kind == "rule" and focus in self.rules:
            selected.add(focus)
            # rules that react on what this rule writes and rules that write
            # what this rule reads
            rule = self.rules[focus]
            for device in rule.writes:
                selected |= self.reverse_reads.get(device, set())
            for device, _ in rule.triggers:
                selected |= self.reverse_writes.get(device, set())
        elif focus_kind == "device":
            selected |= self.reverse_reads.get(focus, set())
            selected |= self.reverse_writes.get(focus, set())
        elif focus_kind == "room":
            for rule in self.rules.values():
                rooms = set(rule.room.split(","))
                devices = {d for d, _ in rule.triggers | rule.checks} | set(rule.writes)
                if focus in rooms or any(
                    focus in self._rooms(device) for device in devices
                ):
                    selected.add(rule.name)
        else:
            selected = set(self.rules)
        nodes = {}
        edges = []
        for name in sorted(selected):
            rule = self.rules[name]
            nodes["rule:" + name] = {
                "id": "rule:" + name,
                "kind": "rule",
                "name": name,
                "type": rule.type,
                "alias": rule.alias,
                "disabled": rule.disabled,
            }
            for device, reading in sorted(rule.triggers | rule.checks):
                if device.startswith("@"):
                    continue
                trigger = (device, reading) in rule.triggers
                nodes.setdefault("dev:" + device, self._device_node(device))
                edges.append(
                    {
                        "from": "dev:" + device,
                        "to": "rule:" + name,
                        "reading": reading,
                        "trigger": trigger,
                    }
                )
            for device, commands in sorted(rule.writes.items()):
                nodes.setdefault("dev:" + device, self._device_node(device))
                edges.append(
                    {
                        "from": "rule:" + name,
                        "to": "dev:" + device,
                        "values": sorted(commands),
                    }
                )
            if rule.timers:
                nodes.setdefault("time", {"id": "time", "kind": "time", "name": "time"})
                edges.append({"from": "time", "to": "rule:" + name, "trigger": True})
        # merge duplicated edges (several readings of one device)
        merged = {}
        for edge in edges:
            key = (edge["from"], edge["to"])
            if key in merged:
                old = merged[key]
                if "reading" in edge:
                    old["readings"] = sorted(
                        set(old.get("readings", [])) | {edge["reading"]}
                    )
                    old["trigger"] = old.get("trigger") or edge.get("trigger")
            else:
                edge = dict(edge)
                if "reading" in edge:
                    edge["readings"] = [edge.pop("reading")]
                merged[key] = edge
        return {"nodes": list(nodes.values()), "edges": list(merged.values())}

    def _rooms(self, device):
        info = self.devices.get(device) or {}
        return set((info.get("attrs", {}) or {}).get("room", "").split(","))

    def _device_node(self, device):
        info = self.devices.get(device)
        node = {"id": "dev:" + device, "kind": "device", "name": device}
        if info is None:
            node["missing"] = device not in self.rules
            if device in self.rules:
                node["kind"] = "rule-device"
        else:
            node["alias"] = (info.get("attrs", {}) or {}).get("alias", "")
            node["type"] = info.get("TYPE", "")
            node["state"] = (info.get("readings", {}) or {}).get("state", "")
        return node

    # --- health check -------------------------------------------------------

    def health(self, now=None, flaps=None):
        """list of findings {kind, severity, rules, devices, params}.
        flaps: {device: number of fast changes} from the timeline"""
        now = now or datetime.datetime.now().timestamp()
        findings = []
        findings.extend(self._conflicts(flaps or {}))
        findings.extend(self._loops())
        findings.extend(self._missing())
        findings.extend(self._dead(now))
        findings.extend(self._duplicates())
        findings.extend(self._errors())
        findings.extend(self._unused_values())
        order = {"error": 0, "warn": 1, "info": 2}
        findings.sort(key=lambda f: (order.get(f["severity"], 3), f["kind"]))
        return findings

    def _conflicts(self, flaps):
        result = []
        for device, names in sorted(self.reverse_writes.items()):
            active = sorted(n for n in names if not self.rules[n].disabled)
            if len(active) < 2:
                continue
            values = {}
            for name in active:
                for command in self.rules[name].writes.get(device, ()):
                    values.setdefault(command.split(" ")[0], set()).add(name)
            if len(values) < 2:
                continue
            # rules that already have a precedence ([?winner:cmd_nr])
            if self._has_precedence(active):
                continue
            doifs = [n for n in active if self.rules[n].type == "DOIF"]
            result.append(
                {
                    "kind": "conflict",
                    "severity": "warn",
                    "rules": active,
                    "devices": [device],
                    "params": {
                        "values": {v: sorted(r) for v, r in sorted(values.items())},
                        "flaps": flaps.get(device, 0),
                        "doifs": doifs,
                    },
                    "fix": "precedence" if len(doifs) > 1 else None,
                }
            )
        return result

    def _has_precedence(self, names):
        for name in names:
            rule = self.rules[name]
            others = [n for n in names if n != name]
            if any(f"[?{other}:cmd_nr]" in rule.definition for other in others):
                return True
        return False

    def _rule_edges(self):
        edges = {}
        for rule in self.rules.values():
            if rule.disabled:
                continue
            targets = set()
            for device in rule.writes:
                for name in self.reverse_reads.get(device, ()):
                    other = self.rules[name]
                    if other.disabled:
                        continue
                    if any(d == device for d, _ in other.triggers):
                        targets.add(name)
            edges[rule.name] = targets
        return edges

    def _loops(self):
        edges = self._rule_edges()
        result = []
        for component in strongly_connected(edges):
            if len(component) == 1:
                name = next(iter(component))
                if name not in edges.get(name, ()):
                    continue
                rule = self.rules[name]
                devices = sorted(
                    d for d in rule.writes if any(t == d for t, _ in rule.triggers)
                )
                # a DOIF without "do always" does not repeat the same case
                if (
                    rule.type == "DOIF"
                    and not rule.attrs.get("do") == "always"
                    and (len(rule.model.get("cases", [])) <= 1)
                ):
                    continue
            else:
                devices = sorted(
                    {
                        d
                        for name in component
                        for d in self.rules[name].writes
                        if any(
                            any(t == d for t, _ in self.rules[o].triggers)
                            for o in component
                        )
                    }
                )
            result.append(
                {
                    "kind": "loop",
                    "severity": "error" if len(component) > 1 else "warn",
                    "rules": sorted(component),
                    "devices": devices,
                    "params": {},
                    "fix": None,
                }
            )
        return result

    def _missing(self):
        result = []
        known = set(self.devices) | set(self.rules)
        for rule in sorted(self.rules.values(), key=lambda r: r.name):
            if rule.type not in ("DOIF", "at", "notify", "watchdog"):
                continue
            used = {d for d, _ in rule.triggers | rule.checks if not d.startswith("@")}
            used |= set(rule.writes)
            missing = sorted(
                d for d in used if d not in known and d != self.editor and _plain(d)
            )
            if missing:
                result.append(
                    {
                        "kind": "missing",
                        "severity": "error",
                        "rules": [rule.name],
                        "devices": missing,
                        "params": {},
                        "fix": None,
                    }
                )
        return result

    def _dead(self, now):
        result = []
        for rule in sorted(self.rules.values(), key=lambda r: r.name):
            if rule.disabled or rule.type == "at":
                continue
            last = rule.last_run()
            if last is not None and now - last < DEAD_DAYS * 86400:
                continue
            if last is None:
                # never executed: only a problem for an old rule, DOIF sets
                # its state when it is defined
                since = fhem_time(rule.times.get("state"))
                if rule.type != "DOIF" or since is None:
                    continue
                if now - since < DEAD_DAYS * 86400:
                    continue
            result.append(
                {
                    "kind": "dead",
                    "severity": "info",
                    "rules": [rule.name],
                    "devices": [],
                    "params": {"last": last, "days": DEAD_DAYS},
                    "fix": "disable",
                }
            )
        return result

    def _duplicates(self):
        seen = {}
        for rule in self.rules.values():
            key = (rule.type, parser.norm(parser.mask_comments(rule.definition)))
            seen.setdefault(key, []).append(rule.name)
        return [
            {
                "kind": "duplicate",
                "severity": "warn",
                "rules": sorted(names),
                "devices": [],
                "params": {},
                "fix": None,
            }
            for names in seen.values()
            if len(names) > 1
        ]

    def _errors(self):
        result = []
        for rule in sorted(self.rules.values(), key=lambda r: r.name):
            state = str(rule.readings.get("state", ""))
            error = rule.error or (state if state.lower().startswith("error") else "")
            if rule.type == "DOIF" and rule.readings.get("error"):
                error = rule.readings["error"]
            if error:
                result.append(
                    {
                        "kind": "error",
                        "severity": "error",
                        "rules": [rule.name],
                        "devices": [],
                        "params": {"text": error[:300]},
                        "fix": None,
                    }
                )
        return result

    def _unused_values(self):
        result = []
        if not self.editor:
            return result
        texts = [
            r.definition + " " + " ".join(r.attrs.values()) for r in self.rules.values()
        ]
        for value in self.values:
            name = value.get("name", "")
            if not name:
                continue
            pattern = re.compile(
                rf"\[\??{re.escape(self.editor)}:{re.escape(name)}(_s)?[\]:]"
            )
            used_by_values = any(
                (row.get("amount", {}).get("source", {}) or {}).get("name") == name
                for other in self.values
                for row in other.get("rows", [])
            )
            if not used_by_values and not any(pattern.search(text) for text in texts):
                result.append(
                    {
                        "kind": "unused_value",
                        "severity": "info",
                        "rules": [],
                        "devices": [],
                        "params": {"value": name, "title": value.get("title", name)},
                        "fix": None,
                    }
                )
        return result

    # --- day plan -----------------------------------------------------------

    def plan(self, now, past=()):
        """what happens today: [{ts, rule, kind, text}] sorted by time.
        past: [(ts, rule, case)] executions of today from the timeline"""
        start = datetime.datetime.combine(now.date(), datetime.time())
        end = start + datetime.timedelta(days=1)
        entries = []
        for rule in self.rules.values():
            if rule.disabled:
                continue
            if rule.type == "DOIF":
                for reading, value in rule.readings.items():
                    if reading.startswith("timer_") or reading == "wait_timer":
                        moment = doif_time(value)
                        if (
                            moment is None
                            or not start <= moment < end + datetime.timedelta(hours=6)
                        ):
                            continue
                        entry = {
                            "ts": moment.timestamp(),
                            "rule": rule.name,
                            "alias": rule.alias,
                            "kind": "wait" if reading == "wait_timer" else "timer",
                            "reading": reading,
                            "future": moment >= now,
                        }
                        if reading == "wait_timer":
                            match = re.search(r"cmd_(\d+)", value)
                            entry["case"] = int(match.group(1)) - 1 if match else None
                        else:
                            entry["case"] = _timer_case(reading)
                            if "|" in value:
                                entry["days"] = value.split("|", 1)[1]
                        entries.append(entry)
            elif rule.type == "at":
                trigger = rule.internals.get("TRIGGERTIME")
                try:
                    moment = datetime.datetime.fromtimestamp(float(trigger))
                except (TypeError, ValueError):
                    continue
                if start <= moment < end + datetime.timedelta(hours=6):
                    entries.append(
                        {
                            "ts": moment.timestamp(),
                            "rule": rule.name,
                            "alias": rule.alias,
                            "kind": "at",
                            "future": moment >= now,
                        }
                    )
        for ts, name, case in past:
            rule = self.rules.get(name)
            entries.append(
                {
                    "ts": ts,
                    "rule": name,
                    "alias": rule.alias if rule else "",
                    "kind": "done",
                    "case": case,
                    "future": False,
                }
            )
        for entry in entries:
            rule = self.rules.get(entry["rule"])
            if rule is not None:
                entry["writes"] = self._case_writes(rule, entry.get("case"))
        entries.sort(key=lambda e: e["ts"])
        return entries

    @staticmethod
    def _case_writes(rule, case):
        if rule.model is None or rule.model.get("mode") != "fhem":
            return sorted(
                f"{d} {' / '.join(sorted(v))}" for d, v in rule.writes.items()
            )
        cases = rule.model.get("cases", [])
        if case is None or not 0 <= case < len(cases):
            return []
        result = []
        for block in cases[case].get("blocks", []):
            for command in block.get("cmds", []):
                result.append(parser.command_text(command))
        return result


def _plain(name):
    return re.fullmatch(r"[A-Za-z0-9._]+", name) is not None


def _timer_case(reading):
    match = re.match(r"timer_\d+_c(\d+)", reading)
    return int(match.group(1)) - 1 if match else None


def strongly_connected(edges):
    """Tarjan: components of the graph {node: set(targets)}"""
    index = {}
    low = {}
    stack = []
    on_stack = set()
    result = []
    counter = [0]

    def visit(start):
        work = [(start, iter(sorted(edges.get(start, ()))))]
        index[start] = low[start] = counter[0]
        counter[0] += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter[0]
                    counter[0] += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(sorted(edges.get(child, ())))))
                    advanced = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component = set()
                while True:
                    item = stack.pop()
                    on_stack.discard(item)
                    component.add(item)
                    if item == node:
                        break
                result.append(component)

    for node in sorted(edges):
        if node not in index:
            visit(node)
    return result


def cases_writing(model, device):
    """1-based numbers of the cases of model that write device"""
    numbers = []
    for number, case in enumerate(model.get("cases", []), 1):
        for block in case.get("blocks", []):
            for command in block.get("cmds", []):
                if command.get("dev") == device or any(
                    d == device
                    for d, _ in parser.writes_in_text(parser.command_text(command))
                ):
                    numbers.append(number)
                    break
            else:
                continue
            break
    return numbers


def precedence_leaf(winner, number):
    return {
        "t": "cmp",
        "check": True,
        "dev": winner,
        "reading": "cmd_nr",
        "fmt": "",
        "op": "!=",
        "value": {"k": "number", "v": str(number)},
    }


def add_precedence(model, winner, winner_cases, device):
    """the cases of model that write device only act while the winner is not
    in one of its cases that write the device: [?winner:cmd_nr] != N"""
    changed = 0
    numbers = set(cases_writing(model, device))
    for number, case in enumerate(model.get("cases", []), 1):
        if number not in numbers or case.get("cond") is None:
            continue
        leaves = [precedence_leaf(winner, n) for n in winner_cases]
        cond = case["cond"]
        if cond.get("t") == "and":
            cond["items"].extend(leaves)
        else:
            case["cond"] = {"t": "and", "items": [cond] + leaves}
        changed += 1
    return changed
