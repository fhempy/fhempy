#!/usr/bin/env python3
"""Copy the BLE parser of custom-components/ble_monitor into fhempy.

bleparser on PyPI is no longer released, new devices and fixes only land in
the ble_parser folder of the Home Assistant component ble_monitor. This
script copies that folder from a release tag into
fhempy/lib/ble_monitor/ble_parser and extracts MEASUREMENT_DICT of its
const.py (which imports Home Assistant) into upstream_const.py.

Usage: python3 tools/sync_ble_parser.py [TAG|latest]   (default: tag in UPSTREAM)

"latest" takes the newest release tag of ble_monitor and does nothing when
it is already copied. .github/workflows/ble_parser_sync.yml runs it monthly.

fhempy specific changes belong into fhempy/lib/ble_monitor/parser.py, never
into the copied files, they are overwritten by the next sync.
"""

import ast
import pprint
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "custom-components/ble_monitor"
SRC = "custom_components/ble_monitor/"
MODULE = (
    Path(__file__).resolve().parent.parent
    / "FHEM/bindings/python/fhempy/lib/ble_monitor"
)
TARGET = MODULE / "ble_parser"
UPSTREAM_CONST = MODULE / "upstream_const.py"
TABLES = ("MEASUREMENT_DICT", "MANUFACTURER_DICT")
# helper script that needs bleak, not used by the parser
SKIP = {"get_beacon_key.py"}
# the only Home Assistant import of the parser
REPLACE = {
    "from homeassistant.util import datetime\n": "from datetime import datetime\n",
}
TAG_RE = re.compile(r"^\d+\.\d+\.\d+$")


def current_tag():
    text = (TARGET / "UPSTREAM").read_text(encoding="utf-8")
    return re.search(r"tag (\S+)", text).group(1)


def latest_tag():
    """Newest x.y.z tag of ble_monitor."""
    out = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", f"https://github.com/{REPO}.git"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    tags = [line.rsplit("/", 1)[-1] for line in out.splitlines()]
    tags = [t for t in tags if TAG_RE.match(t)]
    return max(tags, key=lambda t: tuple(int(x) for x in t.split(".")))


def upstream_files(tag):
    """Clone the tag and return LICENSE and the component files."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["git", "-c", "advice.detachedHead=false", "clone", "-q", "--depth", "1", "--branch", tag,
             f"https://github.com/{REPO}.git", tmp],
            check=True,
        )
        root = Path(tmp)
        files = {"LICENSE": (root / "LICENSE").read_bytes()}
        for path in (root / SRC).rglob("*.py"):
            files[path.relative_to(root).as_posix()] = path.read_bytes()
        return files


def write_parser(files, tag):
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir()
    prefix = SRC + "ble_parser/"
    count = 0
    for rel, content in sorted(files.items()):
        if not rel.startswith(prefix):
            continue
        name = rel[len(prefix) :]
        if "/" in name or not name.endswith(".py") or name in SKIP:
            continue
        text = content.decode("utf-8")
        for old, new in REPLACE.items():
            text = text.replace(old, new)
        if "homeassistant" in text:
            raise SystemExit(f"{name} imports Home Assistant, extend REPLACE")
        (TARGET / name).write_text(text, encoding="utf-8")
        count += 1
    (TARGET / "LICENSE").write_bytes(files["LICENSE"])
    (TARGET / "UPSTREAM").write_text(
        f"Copied from https://github.com/{REPO} tag {tag}\n"
        f"({SRC}ble_parser) by tools/sync_ble_parser.py, do not edit.\n",
        encoding="utf-8",
    )
    return count


def write_tables(files, tag):
    tree = ast.parse(files[SRC + "const.py"])
    tables = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            if name in TABLES:
                tables[name] = ast.literal_eval(node.value)
    missing = set(TABLES) - set(tables)
    if missing:
        raise SystemExit(f"const.py misses {sorted(missing)}")
    lines = [
        f'"""Tables from {REPO} {tag} const.py, written by',
        'tools/sync_ble_parser.py, do not edit."""',
        "",
    ]
    for name in TABLES:
        lines.append(f"{name} = {pprint.pformat(tables[name], width=88, sort_dicts=False)}")
        lines.append("")
    UPSTREAM_CONST.write_text("\n".join(lines), encoding="utf-8")


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else current_tag()
    if tag == "latest":
        tag = latest_tag()
        if tag == current_tag():
            print(f"ble_parser {tag} is up to date")
            return
    if not TAG_RE.match(tag):
        raise SystemExit("TAG must look like 14.7.0")
    files = upstream_files(tag)
    count = write_parser(files, tag)
    write_tables(files, tag)
    print(f"ble_parser {tag}: {count} files copied")


if __name__ == "__main__":
    main()
