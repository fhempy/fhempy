"""Reads and writes DOIF definitions for the visual editor.

parse_rule() turns the DEF and attributes of a DOIF into the model of the
editor (cases with conditions and command blocks), generate_rule() turns the
model back into DEF and attributes. Everything the editor doesn't understand
is kept as code with its original text, and every case which wasn't changed
in the editor is written back character by character (round trip).

The block structure follows 98_DOIF.pm (CmdDoIf, GetBlockDoIf,
GetCommandDoIf): comments start with ## and end at the line end, a case is
(condition) followed by command blocks (...) or {...}, cases are separated by
DOELSEIF, DOELSE has only command blocks.
"""

import copy
import re

COMMENT_RE = re.compile(r"##.*")
# attributes with one value per case, separated by ":" (cmdState by "|")
CASE_ATTRS = ("repeatsame", "repeatcmd", "cmdpause", "waitsame", "waitdel")
CASE_ATTR_SEP = {"cmdState": "|"}
ALL_CASE_ATTRS = CASE_ATTRS + ("cmdState",)

NAME = r"[A-Za-z0-9._]+|\$SELF"
READING = r"[A-Za-z0-9._\-/]+"
FORMAT = r"[A-Za-z][A-Za-z0-9]*"
OPS = ("==", "!=", "<=", ">=", "<", ">", "eq", "ne", "lt", "gt", "le", "ge", "=~", "!~")
TEXT_OPS = ("eq", "ne", "lt", "gt", "le", "ge", "=~", "!~")
OP_RE = r"(==|!=|<=|>=|=~|!~|<|>|\beq\b|\bne\b|\blt\b|\bgt\b|\ble\b|\bge\b)"
VALUE_RE = r'("(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?|\[[^\[\]]+\])'
READ_RE = rf"\[(\??)({NAME})(?::({READING}))?(?::({FORMAT}))?\]"
TIME_RE = r"\d{1,2}:\d{2}(?::\d{2})?"
SUN_RE = r"\{(sunset|sunrise)(?:_abs)?\((-?\d*)\)\}"
DAYS_RE = r"[0-9A-Za-zäöüÄÖÜ ]+|\[[^\[\]]+\]"


class ParseError(Exception):
    pass


# --- low level helpers ------------------------------------------------------


def mask_comments(text):
    """text with comments replaced by spaces, same length and positions"""
    return COMMENT_RE.sub(lambda m: " " * len(m.group(0)), text)


def block_end(text, start, open_char, close_char):
    """index after the bracket closing the block opened at start, counting
    only these brackets like GetBlockDoIf of DOIF"""
    depth = 0
    for i in range(start, len(text)):
        char = text[i]
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return i + 1
            if depth < 0:
                raise ParseError("right bracket without left bracket")
    raise ParseError(f"no right bracket for {open_char} at {start}")


def split_top(text, separator):
    """splits at separator outside of (), [], {} and "" like GetCommandDoIf.
    Returns [(start, end)] spans"""
    spans = []
    start = 0
    i = 0
    while i < len(text):
        char = text[i]
        if char == separator:
            spans.append((start, i))
            start = i + 1
        elif char in "([{":
            close = {"(": ")", "[": "]", "{": "}"}[char]
            try:
                i = block_end(text, i, char, close) - 1
            except ParseError:
                i = len(text) - 1
        elif char == '"':
            end = text.find('"', i + 1)
            if end != -1:
                i = end
        i += 1
    spans.append((start, len(text)))
    return spans


def split_values(text, separator):
    if text is None or text == "":
        return []
    return [text[a:b] for a, b in split_top(text, separator)]


def norm(text):
    """whitespace normalized text to compare generated with original code"""
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"\(\s+", "(", text)
    return re.sub(r"\s+\)", ")", text)


def skip_space(masked, pos):
    while pos < len(masked) and masked[pos].isspace():
        pos += 1
    return pos


# --- the definition -----------------------------------------------------------


def is_perl_mode(definition):
    masked = mask_comments(definition or "").strip()
    return masked != "" and not masked.startswith("(")


def parse_definition(definition):
    """cases with their exact text: each case gets lead (text before its
    condition, including DOELSEIF/DOELSE and comments), cond_raw and blocks
    (each with gap before it). Joining them gives the definition again."""
    text = definition or ""
    masked = mask_comments(text)
    cases = []
    pos = 0
    kind = "if"
    lead_start = 0
    while True:
        pos = skip_space(masked, pos)
        if pos >= len(masked):
            if kind == "else":
                cases.append(
                    {
                        "kind": "else",
                        "lead": text[lead_start:],
                        "cond_raw": None,
                        "blocks": [],
                    }
                )
                return cases, ""
            if kind != "if":
                raise ParseError(f"nothing after {kind.upper()}")
            return cases, text[lead_start:]
        cond_raw = None
        if kind != "else":
            if masked[pos] != "(":
                raise ParseError("no left bracket of condition")
            end = block_end(masked, pos, "(", ")")
            cond_raw = text[pos + 1 : end - 1]
            lead = text[lead_start:pos]
            pos = end
        blocks = []
        block_start = pos
        while True:
            next_pos = skip_space(masked, pos)
            if next_pos < len(masked) and masked[next_pos] in "({":
                bracket = masked[next_pos]
                close = ")" if bracket == "(" else "}"
                end = block_end(masked, next_pos, bracket, close)
                blocks.append(
                    {
                        "gap": text[pos:next_pos],
                        "bracket": bracket,
                        "raw": text[next_pos + 1 : end - 1],
                    }
                )
                pos = end
            else:
                break
        if kind == "else":
            lead = text[lead_start:block_start]
        cases.append(
            {"kind": kind, "lead": lead, "cond_raw": cond_raw, "blocks": blocks}
        )
        after = skip_space(masked, pos)
        if after >= len(masked):
            return cases, text[pos:]
        if kind == "else":
            raise ParseError("text after DOELSE")
        rest = masked[after:]
        match = re.match(r"DOELSEIF\b", rest)
        if match:
            kind = "elseif"
            lead_start = pos
            pos = after + match.end()
            continue
        match = re.match(r"DOELSE\b", rest)
        if match:
            kind = "else"
            lead_start = pos
            pos = after + match.end()
            continue
        raise ParseError("expected DOELSEIF or DOELSE")


def join_definition(cases, tail):
    parts = []
    for case in cases:
        parts.append(case["lead"])
        if case["cond_raw"] is not None:
            parts.append("(" + case["cond_raw"] + ")")
        for block in case["blocks"]:
            close = ")" if block["bracket"] == "(" else "}"
            parts.append(block["gap"] + block["bracket"] + block["raw"] + close)
    parts.append(tail)
    return "".join(parts)


def comment_of(text):
    """first ## comment in text, without ##"""
    match = COMMENT_RE.search(text or "")
    if not match:
        return ""
    return match.group(0)[2:].strip()


# --- conditions ---------------------------------------------------------------


def _tokens(cond):
    """top level tokens of a condition: ("(", inner), ("op", and|or),
    ("not", ""), ("atom", text)"""
    masked = mask_comments(cond)
    tokens = []
    atom_start = None
    i = 0

    def flush(end):
        nonlocal atom_start
        if atom_start is not None:
            atom = cond[atom_start:end]
            if mask_comments(atom).strip():
                tokens.append(("atom", atom))
            atom_start = None

    while i < len(masked):
        char = masked[i]
        if char.isspace() and atom_start is None:
            i += 1
            continue
        word = re.match(r"(and|or|not)\b|&&|\|\||!(?!=|~)", masked[i:])
        prev = masked[i - 1] if i > 0 else " "
        if word and (prev.isspace() or prev in "()" or not word.group(0).isalpha()):
            op = word.group(0)
            if op in ("!", "not") and atom_start is not None:
                # "!" inside an atom like "!IsDisabled(...)" stays in the atom
                pass
            else:
                flush(i)
                if op in ("and", "&&"):
                    tokens.append(("op", "and"))
                elif op in ("or", "||"):
                    tokens.append(("op", "or"))
                else:
                    tokens.append(("not", op))
                i += len(op)
                continue
        if char == "(" and atom_start is None:
            end = block_end(masked, i, "(", ")")
            tokens.append(("(", cond[i + 1 : end - 1]))
            i = end
            continue
        if atom_start is None:
            atom_start = i
        if char in "([{":
            close = {"(": ")", "[": "]", "{": "}"}[char]
            i = block_end(masked, i, char, close)
            continue
        if char == '"':
            end = masked.find('"', i + 1)
            i = (end + 1) if end != -1 else len(masked)
            continue
        i += 1
    flush(len(masked))
    return tokens


def parse_condition(cond):
    """condition text into a tree: {"t": "and"/"or", "items": [...]} or a
    leaf. Unknown parts become {"t": "code", "text": ...}"""
    if cond is None:
        return None
    try:
        tokens = _tokens(cond)
        tree, rest = _parse_or(tokens, 0)
        if rest != len(tokens):
            raise ParseError("unexpected token")
    except (ParseError, IndexError):
        return {"t": "code", "text": cond.strip()}
    return tree


def _parse_or(tokens, pos):
    items = []
    item, pos = _parse_and(tokens, pos)
    items.append(item)
    while pos < len(tokens) and tokens[pos] == ("op", "or"):
        item, pos = _parse_and(tokens, pos + 1)
        items.append(item)
    return (items[0] if len(items) == 1 else {"t": "or", "items": items}), pos


def _parse_and(tokens, pos):
    items = []
    item, pos = _parse_unary(tokens, pos)
    items.append(item)
    while pos < len(tokens) and tokens[pos] == ("op", "and"):
        item, pos = _parse_unary(tokens, pos + 1)
        items.append(item)
    return (items[0] if len(items) == 1 else {"t": "and", "items": items}), pos


def _parse_unary(tokens, pos):
    kind, value = tokens[pos]
    if kind == "not":
        item, pos = _parse_unary(tokens, pos + 1)
        item = copy.deepcopy(item)
        item["not"] = not item.get("not", False)
        return item, pos
    if kind == "(":
        inner = parse_condition(value)
        if inner["t"] in ("and", "or"):
            return inner, pos + 1
        # brackets around a single leaf: keep the leaf
        return inner, pos + 1
    if kind == "atom":
        return parse_leaf(value), pos + 1
    raise ParseError(f"unexpected {kind}")


def _time(text):
    """time of a timer: clock, sunrise/sunset or [device:reading]"""
    text = text.strip()
    if re.fullmatch(TIME_RE, text):
        return {"k": "clock", "v": text}
    match = re.fullmatch(SUN_RE, text)
    if match:
        offset = int(match.group(2)) if match.group(2) else 0
        return {"k": "sun", "event": match.group(1), "offset": offset, "raw": text}
    match = re.fullmatch(rf"\[({NAME}):({READING})\]", text)
    if match:
        return {"k": "reading", "dev": match.group(1), "reading": match.group(2)}
    return {"k": "code", "v": text}


def time_text(time):
    kind = time.get("k")
    if kind == "clock":
        return time["v"]
    if kind == "sun":
        if (
            time.get("raw")
            and _time(time["raw"]).get("offset") == time.get("offset")
            and _time(time["raw"]).get("event") == time.get("event")
        ):
            return time["raw"]
        offset = int(time.get("offset") or 0)
        return "{" + time["event"] + "(" + (str(offset) if offset else "") + ")}"
    if kind == "reading":
        return f"[{time['dev']}:{time['reading']}]"
    return time.get("v", "")


def _timer_leaf(inner, check):
    """inside of [...] of a timer, None if it is no timer"""
    days = None
    body = inner
    if "|" in inner:
        spans = split_top(inner, "|")
        if len(spans) == 2:
            body = inner[spans[0][0] : spans[0][1]]
            days = inner[spans[1][0] : spans[1][1]].strip()
            if not re.fullmatch(DAYS_RE, days):
                return None
    every = None
    parts = split_values(body, ",")
    if len(parts) == 2 and parts[1].strip().startswith("+"):
        body = parts[0]
        every = parts[1].strip()[1:]
    elif len(parts) != 1:
        return None
    body = body.strip()
    leaf = None
    if body.startswith("+"):
        if every is not None:
            return None
        leaf = {"t": "every", "every": _time(body[1:])}
    else:
        range_parts = _split_range(body)
        if range_parts:
            leaf = {
                "t": "range",
                "from": _time(range_parts[0]),
                "to": _time(range_parts[1]),
            }
        else:
            time = _time(body)
            if time["k"] == "code" or time["k"] == "reading" and body.startswith("["):
                if time["k"] == "code":
                    return None
            leaf = {"t": "time", "at": time}
    if leaf["t"] != "range" and every is not None:
        return None
    if every is not None:
        leaf["every"] = _time(every)
    if any(
        part.get("k") == "code"
        for part in (leaf.get("at"), leaf.get("from"), leaf.get("to"))
        if part
    ):
        return None
    if days:
        leaf["days"] = days
    if check:
        leaf["check"] = True
    return leaf


def _split_range(body):
    """'08:00-10:00', '{sunset()}-23:00', '[a:b]-[c:d]' into two times"""
    masked = body
    depth = 0
    for i, char in enumerate(masked):
        if char in "[{(":
            depth += 1
        elif char in "]})":
            depth -= 1
        elif char == "-" and depth == 0 and i > 0:
            left, right = body[:i], body[i + 1 :]
            if _time(left)["k"] != "code" and _time(right)["k"] != "code":
                return left, right
    return None


def parse_leaf(text):
    raw = text.strip()
    leaf = _parse_leaf(raw)
    if leaf is None or norm(leaf_text(leaf)) != norm(raw):
        return {"t": "code", "text": raw}
    return leaf


def _value(text):
    text = text.strip()
    if text.startswith('"'):
        return {"k": "text", "v": text[1:-1]}
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return {"k": "number", "v": text}
    match = re.fullmatch(READ_RE, text)
    if match:
        return {
            "k": "reading",
            "dev": match.group(2),
            "reading": match.group(3) or "",
            "fmt": match.group(4) or "",
            "check": match.group(1) == "?",
        }
    return {"k": "code", "v": text}


def value_text(value):
    kind = value.get("k")
    if kind == "text":
        return '"' + value.get("v", "") + '"'
    if kind == "reading":
        out = "[" + ("?" if value.get("check") else "") + value["dev"]
        if value.get("reading"):
            out += ":" + value["reading"]
        if value.get("fmt"):
            out += ":" + value["fmt"]
        return out + "]"
    return str(value.get("v", ""))


def _parse_leaf(raw):
    # [time], [time-time], [+interval], with |days
    match = re.fullmatch(r"\[(\??)(.+)\]", raw, re.S)
    # [07:30] also looks like [device:reading], DOIF takes it as time
    if match and (
        not re.fullmatch(READ_RE, raw) or re.fullmatch(TIME_RE, match.group(2))
    ):
        inner = match.group(2)
        if not inner.startswith(("@", "#", '"')):
            leaf = _timer_leaf(inner, match.group(1) == "?")
            if leaf:
                return leaf
    # [device:reading] op value
    match = re.fullmatch(rf"{READ_RE}\s*{OP_RE}\s*{VALUE_RE}", raw)
    if match:
        return {
            "t": "cmp",
            "check": match.group(1) == "?",
            "dev": match.group(2),
            "reading": match.group(3) or "",
            "fmt": match.group(4) or "",
            "op": match.group(5),
            "value": _value(match.group(6)),
        }
    # [device:reading] alone: any change, true if the value is true
    match = re.fullmatch(READ_RE, raw)
    if match:
        return {
            "t": "change",
            "check": match.group(1) == "?",
            "dev": match.group(2),
            "reading": match.group(3) or "",
            "fmt": match.group(4) or "",
        }
    # [device:"regexp"] event of a device
    match = re.fullmatch(rf'\[(\??)({NAME}):"([^"]*)"\]', raw)
    if match:
        return {
            "t": "event",
            "check": match.group(1) == "?",
            "dev": match.group(2),
            "regex": match.group(3),
        }
    # ["regexp"] any event
    match = re.fullmatch(r'\["([^"]*)"\]', raw)
    if match:
        return {"t": "anyevent", "regex": match.group(1)}
    # aggregation [#"regexp":reading:condition,default] op value
    match = re.fullmatch(
        r'\[(\??)([#@](?:sum|max|min|average|median|maxsum|minsum)?)"([^"]*)"'
        r"(?::([^:\],]*))?(?::([^\],]*))?(?:,([^\]]*))?\]"
        rf"(?:\s*{OP_RE}\s*{VALUE_RE})?",
        raw,
    )
    if match:
        leaf = {
            "t": "agg",
            "check": match.group(1) == "?",
            "mode": match.group(2),
            "regex": match.group(3),
            "reading": match.group(4) or "",
            "cond": match.group(5) or "",
            "default": match.group(6) if match.group(6) is not None else None,
        }
        if match.group(7):
            leaf["op"] = match.group(7)
            leaf["value"] = _value(match.group(8))
        return leaf
    return None


def leaf_text(leaf):
    kind = leaf.get("t")
    prefix = "!" if leaf.get("not") else ""
    out = _leaf_body(leaf)
    if prefix:
        if kind in ("and", "or") or " " in out:
            return f"!({out})"
        return "!" + out
    return out


def _days(leaf):
    return "|" + leaf["days"] if leaf.get("days") else ""


def _leaf_body(leaf):
    kind = leaf.get("t")
    check = "?" if leaf.get("check") else ""
    if kind == "code":
        return leaf.get("text", "")
    if kind == "time":
        return f"[{check}{time_text(leaf['at'])}{_days(leaf)}]"
    if kind == "range":
        every = f",+{time_text(leaf['every'])}" if leaf.get("every") else ""
        return (
            f"[{check}{time_text(leaf['from'])}-{time_text(leaf['to'])}"
            f"{every}{_days(leaf)}]"
        )
    if kind == "every":
        return f"[{check}+{time_text(leaf['every'])}{_days(leaf)}]"
    if kind in ("cmp", "change"):
        out = "[" + check + leaf["dev"]
        if leaf.get("reading"):
            out += ":" + leaf["reading"]
        if leaf.get("fmt"):
            out += ":" + leaf["fmt"]
        out += "]"
        if kind == "cmp":
            out += f" {leaf['op']} {value_text(leaf['value'])}"
        return out
    if kind == "event":
        return f'[{check}{leaf["dev"]}:"{leaf["regex"]}"]'
    if kind == "anyevent":
        return f'["{leaf["regex"]}"]'
    if kind == "agg":
        out = f'[{check}{leaf["mode"]}"{leaf["regex"]}"'
        if leaf.get("reading") or leaf.get("cond"):
            out += ":" + leaf.get("reading", "")
        if leaf.get("cond"):
            out += ":" + leaf["cond"]
        if leaf.get("default") is not None:
            out += "," + leaf["default"]
        out += "]"
        if leaf.get("op"):
            out += f" {leaf['op']} {value_text(leaf['value'])}"
        return out
    if kind in ("and", "or"):
        return condition_text(leaf)
    return leaf.get("text", "")


def condition_text(tree, parent=None):
    if tree is None:
        return ""
    kind = tree.get("t")
    if kind in ("and", "or"):
        inner = f" {kind} ".join(
            condition_text(item, kind) for item in tree.get("items", [])
        )
        if tree.get("not"):
            return f"!({inner})"
        if parent is not None:
            return f"({inner})"
        return inner
    text = leaf_text(tree)
    if (
        kind == "code"
        and parent is not None
        and re.search(r"\b(and|or)\b|&&|\|\|", text)
    ):
        return f"({text})"
    return text


# --- commands -------------------------------------------------------------------


def parse_block(block):
    """command block into commands. {perl} blocks become one perl command"""
    raw = block.get("raw", "")
    if block.get("bracket") == "{":
        return [{"t": "perl", "text": raw}]
    commands = []
    for start, end in split_top(raw, ","):
        text = raw[start:end]
        if not mask_comments(text).strip():
            continue
        commands.append(parse_command(text))
    return commands


def parse_command(text):
    raw = text.strip()
    command = _parse_command(raw)
    if command is None or norm(command_text(command)) != norm(raw):
        return {"t": "fhem", "text": raw}
    return command


def _parse_command(raw):
    match = re.fullmatch(r"\{(.*)\}", raw, re.S)
    if match:
        return {"t": "perl", "text": match.group(1)}
    match = re.fullmatch(r"set\s+(\S+)\s+(\S+)(?:\s+(.+))?", raw, re.S)
    if match:
        return {
            "t": "set",
            "dev": match.group(1),
            "cmd": match.group(2),
            "args": (match.group(3) or "").strip(),
        }
    match = re.fullmatch(r"setreading\s+(\S+)\s+(\S+)\s+(.+)", raw, re.S)
    if match:
        return {
            "t": "setreading",
            "dev": match.group(1),
            "reading": match.group(2),
            "value": match.group(3).strip(),
        }
    return {"t": "fhem", "text": raw}


def command_text(command):
    kind = command.get("t")
    if kind == "set":
        out = f"set {command['dev']} {command['cmd']}"
        if command.get("args"):
            out += " " + command["args"]
        return out
    if kind == "setreading":
        return f"setreading {command['dev']} {command['reading']} {command['value']}"
    if kind == "perl":
        return "{" + command.get("text", "") + "}"
    return command.get("text", "")


def block_text(block):
    commands = block.get("cmds", [])
    if (
        len(commands) == 1
        and commands[0].get("t") == "perl"
        and block.get("bracket") == "{"
    ):
        return "{" + commands[0].get("text", "") + "}"
    return "(" + ", ".join(command_text(command) for command in commands) + ")"


# --- perl mode --------------------------------------------------------------------


def parse_perl_blocks(definition):
    """Perl mode DEF: name {block} name {block}, the name is optional"""
    text = definition or ""
    masked = mask_comments(text)
    blocks = []
    pos = 0
    while True:
        start = pos
        pos = skip_space(masked, pos)
        if pos >= len(masked):
            return blocks, text[start:]
        match = re.match(r"([A-Za-z0-9_]*)\s*\{", masked[pos:])
        if not match:
            raise ParseError("expected {block}")
        brace = pos + match.end() - 1
        end = block_end(masked, brace, "{", "}")
        code = text[brace + 1 : end - 1]
        blocks.append(
            {
                "lead": text[start:brace],
                "name": match.group(1),
                "code": code,
                "visual": parse_perl_if(code),
            }
        )
        pos = end


PERL_IF_RE = re.compile(
    r"\s*if\s*\((?P<cond>.*)\)\s*\{\s*"
    r'(?P<cmds>(?:fhem_set\s*\(\s*"[^"]*"\s*\)\s*;?\s*)+)\}\s*',
    re.S,
)


def parse_perl_if(code):
    """if (condition) {fhem_set("...")} as condition and set commands"""
    match = PERL_IF_RE.fullmatch(mask_comments(code))
    if not match:
        return None
    cond = code[match.start("cond") : match.end("cond")]
    commands = [
        parse_command("set " + text)
        for text in re.findall(r'fhem_set\s*\(\s*"([^"]*)"\s*\)', match.group("cmds"))
    ]
    tree = parse_condition(cond)
    return {"cond": tree, "cmds": commands}


def perl_if_text(visual):
    cond = condition_text(visual.get("cond"))
    sets = " ".join(
        'fhem_set("' + command_text(command)[4:] + '");'
        for command in visual.get("cmds", [])
        if command.get("t") == "set"
    )
    return f"if ({cond}) {{{sets}}}"


def perl_block_text(block):
    lead = block.get("lead")
    if lead is None or not re.fullmatch(
        r"\s*" + re.escape(block.get("name", "")) + r"\s*", lead
    ):
        lead = ("\n" if block.get("index") else "") + (
            block["name"] + " " if block.get("name") else ""
        )
    return lead + "{" + block.get("code", "") + "}"


# --- whole rule -------------------------------------------------------------------


def parse_rule(definition, attrs=None):
    """model of a DOIF for the editor"""
    attrs = dict(attrs or {})
    rule = {"mode": "fhem", "def": definition or "", "error": "", "attrs": {}}
    if is_perl_mode(definition):
        rule["mode"] = "perl"
        try:
            blocks, tail = parse_perl_blocks(definition)
        except ParseError as exc:
            rule["error"] = str(exc)
            blocks, tail = [], ""
        rule["blocks"] = blocks
        rule["tail"] = tail
        rule["attrs"] = attrs
        return rule
    try:
        cases, tail = parse_definition(definition or "")
    except ParseError as exc:
        rule["error"] = str(exc)
        rule["cases"] = []
        rule["tail"] = ""
        rule["attrs"] = attrs
        return rule
    waits = [
        split_values(part, ",") for part in split_values(attrs.get("wait", ""), ":")
    ]
    case_values = {
        name: split_values(attrs.get(name, ""), CASE_ATTR_SEP.get(name, ":"))
        for name in ALL_CASE_ATTRS
    }
    for index, case in enumerate(cases):
        case["comment"] = comment_of(case["lead"]) or comment_of(case["cond_raw"])
        case["cond"] = parse_condition(case["cond_raw"])
        case_waits = waits[index] if index < len(waits) else []
        for number, block in enumerate(case["blocks"]):
            block["cmds"] = parse_block(block)
            block["wait"] = (
                case_waits[number].strip() if number < len(case_waits) else ""
            )
        case["attrs"] = {
            name: values[index].strip()
            for name, values in case_values.items()
            if index < len(values) and values[index].strip() != ""
        }
        case["orig"] = index
    rule["cases"] = cases
    rule["tail"] = tail
    rule["attrs"] = {
        name: value
        for name, value in attrs.items()
        if name not in ALL_CASE_ATTRS and name != "wait"
    }
    rule["case_attrs_raw"] = {
        name: attrs[name] for name in ALL_CASE_ATTRS + ("wait",) if name in attrs
    }
    return rule


def visual_share(rule):
    """(visual parts, all parts) of a rule for the list"""
    total = 0
    visual = 0
    if rule.get("error"):
        return 0, 1
    if rule.get("mode") == "perl":
        for block in rule.get("blocks", []):
            total += 1
            if block.get("visual"):
                visual += 1
        return visual, max(total, 1)

    def count(tree):
        nonlocal total, visual
        if tree is None:
            return
        if tree.get("t") in ("and", "or"):
            for item in tree.get("items", []):
                count(item)
            return
        total += 1
        if tree.get("t") != "code":
            visual += 1

    for case in rule.get("cases", []):
        count(case.get("cond"))
        for block in case.get("blocks", []):
            for command in block.get("cmds", []):
                total += 1
                if command.get("t") in ("set", "setreading"):
                    visual += 1
    return visual, max(total, 1)


def code_parts(rule):
    """number of parts the editor shows as code"""
    visual, total = visual_share(rule)
    return total - visual


def generate_case(case, index, count):
    """text of one case at position index of count cases"""
    kind = case_kind(index, count, case)
    lead = case.get("lead")
    if lead is None or _lead_kind(lead) != kind:
        comment = case.get("comment", "")
        keyword = {"if": "", "elseif": "\nDOELSEIF ", "else": "\nDOELSE "}[kind]
        lead = keyword
        if comment:
            lead = (keyword.rstrip() + " " if keyword else "") + "## " + comment + "\n"
            if kind != "if":
                lead = "\n" + lead.lstrip("\n")
    elif case.get("comment") is not None and comment_of(lead) != case.get(
        "comment", ""
    ):
        lead = re.sub(r"##.*", "", lead).rstrip(" ")
        if case.get("comment"):
            lead = (
                lead.rstrip("\n")
                + (" " if lead.strip() else "")
                + "## "
                + case["comment"]
                + "\n"
            )
    parts = [lead]
    if kind != "else":
        cond_raw = case.get("cond_raw")
        if cond_raw is not None and parse_condition(cond_raw) == _strip_ui(
            case.get("cond")
        ):
            parts.append("(" + cond_raw + ")")
        else:
            parts.append("(" + condition_text(case.get("cond")) + ")")
    for number, block in enumerate(case.get("blocks", [])):
        gap = block.get("gap")
        if gap is None:
            gap = "" if "".join(parts).endswith(("\n", " ")) else " "
        raw = block.get("raw")
        if raw is not None and parse_block(block) == _strip_ui(block.get("cmds")):
            close = ")" if block.get("bracket") == "(" else "}"
            parts.append(gap + block.get("bracket", "(") + raw + close)
        else:
            parts.append(gap + block_text(block))
    return "".join(parts)


def _strip_ui(value):
    """model without keys the frontend adds (ids, open state)"""
    if isinstance(value, dict):
        return {
            key: _strip_ui(item)
            for key, item in value.items()
            if not key.startswith("_")
        }
    if isinstance(value, list):
        return [_strip_ui(item) for item in value]
    return value


def case_kind(index, count, case):
    if index == 0:
        return "if"
    if case.get("kind") == "else" or case.get("cond") is None and index == count - 1:
        return "else"
    return "elseif"


def _lead_kind(lead):
    masked = mask_comments(lead)
    if re.search(r"\bDOELSEIF\b", masked):
        return "elseif"
    if re.search(r"\bDOELSE\b", masked):
        return "else"
    return "if"


def generate_definition(rule):
    if rule.get("mode") == "perl":
        parts = []
        for index, block in enumerate(rule.get("blocks", [])):
            block = dict(block)
            block["index"] = index
            visual = block.get("visual")
            if visual and parse_perl_if(block.get("code", "")) != _strip_ui(visual):
                block["code"] = perl_if_text(visual)
            parts.append(perl_block_text(block))
        return "".join(parts) + (rule.get("tail") or "")
    cases = rule.get("cases", [])
    text = "".join(
        generate_case(case, index, len(cases)) for index, case in enumerate(cases)
    )
    return text + (rule.get("tail") or "")


def generate_attrs(rule):
    """attributes of the rule: {name: value or None to delete}"""
    attrs = dict(rule.get("attrs", {}))
    if rule.get("mode") == "perl":
        return attrs
    cases = rule.get("cases", [])
    original = rule.get("case_attrs_raw", {})
    # wait: per case, per block
    wait_cases = []
    for case in cases:
        waits = [
            str(block.get("wait") or "").strip() for block in case.get("blocks", [])
        ]
        while waits and waits[-1] in ("", "0"):
            waits.pop()
        wait_cases.append(",".join(wait or "0" for wait in waits))
    while wait_cases and wait_cases[-1] == "":
        wait_cases.pop()
    attrs["wait"] = _join_cases(
        [value or "0" for value in wait_cases], ":", original.get("wait")
    )
    for name in ALL_CASE_ATTRS:
        values = [case.get("attrs", {}).get(name, "") for case in cases]
        attrs[name] = _join_cases(
            values, CASE_ATTR_SEP.get(name, ":"), original.get(name)
        )
    return attrs


def _join_cases(values, separator, original):
    while values and values[-1] == "":
        values = values[:-1]
    if not values:
        return None
    text = separator.join(values)
    if original is not None and norm(original) == norm(text):
        return original
    return text


def reads_and_writes(rule):
    """devices a rule reads (triggers and checks) and writes"""
    triggers, checks, writes = set(), set(), {}
    times = []

    def walk(tree):
        if tree is None:
            return
        kind = tree.get("t")
        if kind in ("and", "or"):
            for item in tree.get("items", []):
                walk(item)
            return
        if kind in ("cmp", "change", "event"):
            (checks if tree.get("check") else triggers).add(
                (tree["dev"], tree.get("reading") or "state")
            )
            value = tree.get("value") or {}
            if value.get("k") == "reading":
                checks.add((value["dev"], value.get("reading") or "state"))
        elif kind in ("time", "range", "every"):
            times.append(tree)
            for key in ("at", "from", "to"):
                part = tree.get(key) or {}
                if part.get("k") == "reading":
                    triggers.add((part["dev"], part["reading"]))
        elif kind == "agg":
            triggers.add(("@" + tree.get("regex", ""), tree.get("reading") or "state"))
        elif kind == "code":
            for match in re.finditer(READ_RE, tree.get("text", "")):
                (checks if match.group(1) else triggers).add(
                    (match.group(2), match.group(3) or "state")
                )

    def commands(cmds):
        for command in cmds:
            if command.get("t") == "set":
                writes.setdefault(command["dev"], set()).add(
                    (command["cmd"] + " " + command.get("args", "")).strip()
                )
            elif command.get("t") == "setreading":
                writes.setdefault(command["dev"], set()).add(
                    command["reading"] + " " + command["value"]
                )
            else:
                for dev, value in writes_in_text(command_text(command)):
                    writes.setdefault(dev, set()).add(value)

    if rule.get("mode") == "perl":
        for block in rule.get("blocks", []):
            code = block.get("code", "")
            for match in re.finditer(READ_RE, code):
                (checks if match.group(1) else triggers).add(
                    (match.group(2), match.group(3) or "state")
                )
            for match in re.finditer(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]", code):
                times.append({"t": "time", "at": {"k": "clock", "v": match.group(1)}})
            for dev, value in writes_in_text(code):
                writes.setdefault(dev, set()).add(value)
    else:
        for case in rule.get("cases", []):
            walk(case.get("cond"))
            for block in case.get("blocks", []):
                commands(block.get("cmds", []))
    return triggers, checks, writes, times


SET_IN_TEXT = re.compile(
    r'(?:\bset\s+|fhem_set\s*\(\s*"|fhem\s*\(\s*"set\s+)([A-Za-z0-9._,]+)\s+([^",;)]*)'
)


def writes_in_text(text):
    result = []
    for match in SET_IN_TEXT.finditer(text or ""):
        for dev in match.group(1).split(","):
            if dev and dev != "$SELF":
                result.append((dev, match.group(2).strip()))
    return result
