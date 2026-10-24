"""Builds the catalog of the fhempy module installer (www/fhempy/modules.json)
and the catalog of autodiscovery (lib/autodiscovery/discovery.json).

Every module describes its tile in the "installer" section of its manifest.json:
title, description, category, order (within the category), name (suggested
device name), single, logo (file in www/fhempy) or icon, badge, args, params
and modes. Parameters can use a preset, e.g. {"type": "mac"}, other keys of the
parameter override the preset.

The "discovery" section (one rule or a list of rules) says how autodiscovery
recognizes the devices of a module: mdns, ssdp, ble or search (the module's own
search() in discovery.py), see lib/autodiscovery/README.md.

Run it after changing an installer or discovery section:
python3 manifest2modules.py
Use --check to only verify that both files are up to date.
"""

import json
import os
import sys

LIB_DIR = "FHEM/bindings/python/fhempy/lib"
WWW_DIR = "www/fhempy"
OUTPUT = WWW_DIR + "/modules.json"
DISCOVERY_OUTPUT = LIB_DIR + "/autodiscovery/discovery.json"

MAC_HELP = (
    "Bluetooth address, e.g. A4:C1:38:12:34:56. "
    "Autodiscovery finds most devices on its own."
)
PRESETS = {
    "mac": {
        "label": "Bluetooth address (MAC)",
        "placeholder": "AA:BB:CC:DD:EE:FF",
        "help": MAC_HELP,
    },
    "username": {"label": "Username / e-mail", "placeholder": "me@example.com"},
    "password": {"label": "Password", "secret": True},
    "ip": {"label": "IP address", "placeholder": "192.168.1.50"},
}


def expand_params(module, params):
    result = []
    for param in params:
        param = dict(param)
        preset = param.pop("type", None)
        if preset is not None:
            if preset not in PRESETS:
                raise ValueError(f"{module}: unknown parameter type {preset}")
            param = {**PRESETS[preset], **param}
        if "label" not in param:
            raise ValueError(f"{module}: parameter without label")
        result.append(param)
    return result


def read_manifest(lib_dir, module):
    path = os.path.join(lib_dir, module, "manifest.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def read_installer(lib_dir, module):
    return read_manifest(lib_dir, module).get("installer")


def catalog_entry(module, installer, www_dir):
    for key in ("title", "description", "category", "name"):
        if key not in installer:
            raise ValueError(f"{module}: installer needs {key}")
    logo = installer.get("logo")
    if logo and not os.path.isfile(os.path.join(www_dir, logo)):
        raise ValueError(f"{module}: logo {www_dir}/{logo} not found")
    entry = {"id": module, **installer}
    if "params" in entry:
        entry["params"] = expand_params(module, entry["params"])
    if "modes" in entry:
        entry["modes"] = [
            {**mode, "params": expand_params(module, mode.get("params", []))}
            for mode in entry["modes"]
        ]
    return entry


def build(lib_dir=LIB_DIR, www_dir=WWW_DIR):
    modules = []
    for module in sorted(os.listdir(lib_dir)):
        installer = read_installer(lib_dir, module)
        if installer is not None:
            modules.append(catalog_entry(module, installer, www_dir))
    modules.sort(key=lambda m: (m.get("order", 1000), m["title"].lower()))
    for entry in modules:
        entry.pop("order", None)
    return json.dumps(modules, indent=1, ensure_ascii=False) + "\n"


DISCOVERY_SOURCES = ("mdns", "ssdp", "ble", "search")
DISCOVERY_ACTIONS = ("define", "set", "installer")


def discovery_rule(module, rule, lib_dir):
    sources = [source for source in DISCOVERY_SOURCES if rule.get(source)]
    if not sources:
        raise ValueError(f"{module}: discovery rule needs one of {DISCOVERY_SOURCES}")
    if "search" in sources and not os.path.isfile(
        os.path.join(lib_dir, module, "discovery.py")
    ):
        raise ValueError(f"{module}: search needs {module}/discovery.py")
    rule = dict(rule)
    if "mdns" in rule:
        rule["mdns"] = [
            {"type": matcher} if isinstance(matcher, str) else matcher
            for matcher in rule["mdns"]
        ]
        for matcher in rule["mdns"]:
            if not matcher.get("type", "").endswith(".local."):
                raise ValueError(f"{module}: mdns type must end with .local.")
    action = rule.get("action", "define")
    if action not in DISCOVERY_ACTIONS:
        raise ValueError(f"{module}: unknown discovery action {action}")
    if action == "set" and "command" not in rule.get("set", {}):
        raise ValueError(f"{module}: discovery action set needs set.command")
    if "unique" not in rule and not rule.get("single") and "search" not in sources:
        raise ValueError(f"{module}: discovery rule needs unique or single")
    if "params" in rule:
        rule["params"] = expand_params(module, rule["params"])
    return rule


def discovery_entry(module, manifest, lib_dir):
    discovery = manifest["discovery"]
    installer = manifest.get("installer", {})
    entry = {
        "module": module,
        "title": installer.get("title", module),
        "name": installer.get("name", module),
    }
    for key in ("logo", "icon"):
        if key in installer:
            entry[key] = installer[key]
    if isinstance(discovery, dict):
        discovery = [discovery]
    entry["rules"] = [discovery_rule(module, rule, lib_dir) for rule in discovery]
    return entry


def build_discovery(lib_dir=LIB_DIR):
    entries = []
    for module in sorted(os.listdir(lib_dir)):
        manifest = read_manifest(lib_dir, module)
        if "discovery" in manifest:
            entries.append(discovery_entry(module, manifest, lib_dir))
    return json.dumps(entries, indent=1, ensure_ascii=False) + "\n"


def update(output, content, check):
    current = None
    if os.path.isfile(output):
        with open(output, encoding="utf-8") as current_file:
            current = current_file.read()
    if current == content:
        return 0
    if check:
        print(f"{output} is outdated, run: python3 manifest2modules.py")
        return 1
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write(content)
    print(f"{output} updated")
    return 0


def main():
    check = "--check" in sys.argv
    ret = update(OUTPUT, build(), check)
    ret |= update(DISCOVERY_OUTPUT, build_discovery(), check)
    return ret


if __name__ == "__main__":
    sys.exit(main())
