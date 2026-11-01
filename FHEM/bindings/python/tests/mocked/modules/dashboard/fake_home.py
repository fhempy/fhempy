"""A small demo home and a fake FHEM which answers the Perl commands of the
dashboard module like FHEM would."""

import copy
import json
import re
import time

NOW = time.time()


def ts(minutes_ago=0):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(NOW - minutes_ago * 60))


def device(type_, room, sets="", readings=None, alias="", fhempytype="", attrs=None):
    return {
        "TYPE": type_,
        "FHEMPYTYPE": fhempytype,
        "alias": alias,
        "room": room,
        "sets": sets,
        "readings": readings or {},
        "attrs": attrs or {},
    }


DIM = "on off pct:slider,0,1,100"
BLIND = "up down stop pct:slider,0,1,100"
THERMO = "desired-temp:slider,4.5,0.5,30"

DEVICES = {
    "wz_Deckenlicht": device("HUEDevice", "Wohnzimmer", DIM, {"state": "on", "pct": "70"}),
    "wz_Stehlampe": device(
        "dummy", "Wohnzimmer", "on off", {"state": "on"}, alias="Stehlampe"
    ),
    "wz_Leselampe": device("dummy", "Wohnzimmer", "on off", {"state": "off"}),
    "wz_Fernseher": device(
        "dummy",
        "Wohnzimmer",
        "on off",
        {"state": "off", "power": "0"},
        attrs={"genericDeviceType": "outlet"},
        alias="Fernseher",
    ),
    "wz_Rollladen": device(
        "dummy", "Wohnzimmer", BLIND, {"pct": "60"}, alias="Rollladen Terrasse"
    ),
    "wz_Heizung": device(
        "CUL_HM",
        "Wohnzimmer",
        THERMO,
        {"desired-temp": "22.0", "measured-temp": "21.3", "humidity": "48"},
        alias="Heizung",
    ),
    "wz_Fenster": device(
        "dummy", "Wohnzimmer", "", {"contact": "open"}, alias="Fenster Garten"
    ),
    "wz_Bewegung": device(
        "dummy", "Wohnzimmer", "", {"motion": "nomotion"}, alias="Bewegung Wohnzimmer"
    ),
    "wz_Szenen": device(
        "LightScene", "Wohnzimmer", "scene:Filmabend,Gemütlich,Hell", {"state": "Hell"}
    ),
    "ku_Licht": device("dummy", "Küche", "on off", {"state": "on"}, alias="Licht Küche"),
    "ku_Kaffeemaschine": device(
        "dummy",
        "Küche",
        "on off",
        {"state": "on", "power": "1180"},
        attrs={"genericDeviceType": "outlet"},
        alias="Kaffeemaschine",
    ),
    "ku_Fenster": device("dummy", "Küche", "", {"contact": "closed"}, alias="Fenster Küche"),
    "ku_Klima": device(
        "dummy", "Küche", "", {"temperature": "22.4", "humidity": "51"}, alias="Klima Küche"
    ),
    "sz_Licht": device("dummy", "Schlafzimmer", DIM, {"state": "off", "pct": "0"}, alias="Nachtlicht"),
    "sz_Rollladen": device("dummy", "Schlafzimmer", BLIND, {"pct": "0"}, alias="Rollladen"),
    "sz_Heizung": device(
        "CUL_HM",
        "Schlafzimmer",
        THERMO,
        {"desired-temp": "18.0", "measured-temp": "18.4"},
        alias="Heizung",
    ),
    "bad_Fenster": device("dummy", "Bad", "", {"state": "tilted"}, alias="Fenster Bad"),
    "bad_Heizung": device(
        "CUL_HM",
        "Bad",
        THERMO,
        {"desired-temp": "23.0", "measured-temp": "22.1", "battery": "low"},
        alias="Heizung Bad",
    ),
    "fl_Licht": device("dummy", "Flur", DIM, {"state": "on", "pct": "40"}, alias="Licht Flur"),
    "fl_Haustuer": device(
        "dummy", "Flur", "lock unlock", {"lock": "locked"}, alias="Haustür"
    ),
    "fl_Klingel": device("dummy", "Flur", "", {"state": "idle"}, alias="Klingel"),
    "ga_Licht": device("dummy", "Garten", "on off", {"state": "off"}, alias="Licht Terrasse"),
    "ga_Pumpe": device(
        "dummy",
        "Garten",
        "on off",
        {"state": "off"},
        attrs={"genericDeviceType": "outlet"},
        alias="Teichpumpe",
    ),
    "ga_Aussen": device("dummy", "Garten", "", {"temperature": "9.2"}, alias="Außentemperatur"),
    "rr_Anna": device("ROOMMATE", "", "", {"state": "home"}, alias="Anna"),
    "rr_Max": device("ROOMMATE", "", "", {"state": "home"}, alias="Max"),
    "rr_Lea": device("ROOMMATE", "", "", {"state": "absent"}, alias="Lea"),
    "Wetter": device(
        "fhempy",
        "",
        "",
        {
            "cur_temperature": "9",
            "cur_weather": "Leicht bewölkt",
            "next_days_0_max_temp": "13",
            "next_days_0_min_temp": "4",
        },
        fhempytype="openmeteo_weather",
    ),
    "PV": device(
        "fhempy",
        "",
        "",
        {"inverter_output_power": "3.4", "electrical_load": "1.2", "battery_soc": "82"},
        fhempytype="fusionsolar",
    ),
    "push": device("fhempy", "", "", {"message": "-"}, fhempytype="push"),
}
# minutes ago of the last change
AGES = {"wz_Fenster": 25, "bad_Fenster": 64}


class FakeFhem:
    def __init__(self, devices=None):
        self.devices = copy.deepcopy(devices or DEVICES)
        self.sets = []
        self.module = None

    def infos(self, names):
        result = {}
        for name in names:
            d = self.devices.get(name)
            if d is None:
                continue
            age = AGES.get(name, 90)
            result[name] = {
                "NAME": name,
                "TYPE": d["TYPE"],
                "FHEMPYTYPE": d["FHEMPYTYPE"],
                "alias": d["alias"],
                "room": d["room"],
                "sets": d["sets"],
                "readings": dict(d["readings"]),
                "times": {r: ts(age) for r in d["readings"]},
                "attrs": dict(d["attrs"]),
            }
        return result

    async def send(self, hash, code):
        if "my %w = map" in code:
            names = re.findall(r"'([^']+)'", code.split("foreach my $d (", 1)[1])
            return json.dumps(self.infos(names))
        if "devspec2array" in code:
            return ",".join(sorted(self.devices))
        if "sunrise_abs" in code:
            return "07:02:00,16:45:00"
        match = re.search(r"CommandSet\(undef, '([^']+)'\)", code)
        if match:
            definition = match.group(1)
            self.sets.append(definition)
            name, _, args = definition.partition(" ")
            if name not in self.devices:
                return f"Please define {name} first"
            if self.module is not None:
                await self.apply(name, args)
            return ""
        return ""

    async def apply(self, name, args):
        """FHEM sends events for the new values"""
        words = args.split(" ")
        if words[0] in ("on", "off"):
            events = [("state", words[0])]
        elif words[0] in ("pct", "desired-temp"):
            events = [(words[0], words[1])]
        elif words[0] in ("lock", "unlock"):
            events = [("lock", words[0] + "ed")]
        else:
            return
        for reading, value in events:
            self.devices[name]["readings"][reading] = value
            await self.module.handle_event(name, reading, value)


async def set_event_devices(hash, devices):
    return True


async def set_default_attrs(hash, attrs):
    return None
