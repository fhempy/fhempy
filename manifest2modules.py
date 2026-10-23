"""Builds the catalog of the fhempy module installer (www/fhempy/modules.json).

Every module describes its tile in the "installer" section of its manifest.json:
title, description, category, order (within the category), name (suggested
device name), single, logo (file in www/fhempy) or icon, badge, args, params
and modes. Parameters can use a preset, e.g. {"type": "mac"}, other keys of the
parameter override the preset.

Run it after changing an installer section: python3 manifest2modules.py
Use --check to only verify that modules.json is up to date.
"""

import json
import os
import sys

LIB_DIR = "FHEM/bindings/python/fhempy/lib"
WWW_DIR = "www/fhempy"
OUTPUT = WWW_DIR + "/modules.json"

MAC_HELP = (
    "Bluetooth address, e.g. A4:C1:38:12:34:56. "
    "The module discover_ble lists the devices nearby."
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


def read_installer(lib_dir, module):
    path = os.path.join(lib_dir, module, "manifest.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as manifest_file:
        return json.load(manifest_file).get("installer")


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


def main():
    catalog = build()
    current = None
    if os.path.isfile(OUTPUT):
        with open(OUTPUT, encoding="utf-8") as catalog_file:
            current = catalog_file.read()
    if "--check" in sys.argv:
        if current != catalog:
            print(f"{OUTPUT} is outdated, run: python3 manifest2modules.py")
            return 1
        return 0
    if current != catalog:
        with open(OUTPUT, "w", encoding="utf-8") as catalog_file:
            catalog_file.write(catalog)
        print(f"{OUTPUT} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
