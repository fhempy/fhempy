"""Music players on the tablets: play/pause, next/previous, volume, presets
and the cover of what is playing. Works with fhempy googlecast and dlna_dmr
and with FHEM modules like BOSEST or SONOSPLAYER, the commands are chosen
from the set list of the device, so nothing has to be configured.

Pure functions, no FHEM access.
"""

import hashlib
import re

from ..matter_bridge import devices as kinds

MEDIA_FHEMPY_TYPES = ("googlecast", "dlna_dmr")
MEDIA_TYPES = (
    "BOSEST",
    "SONOSPLAYER",
    "SB_PLAYER",
    "DLNARenderer",
    "MPD",
    "HEOSPlayer",
    "YAMAHA_MC",
    "MUSICCAST",
    "BRAVIA",
)
MEDIA_GENERIC_TYPES = ("media", "speaker", "audio", "mediaplayer")

TITLE_READINGS = ("mediaTitle", "media_title", "track", "currentTitle", "title")
ARTIST_READINGS = ("mediaArtist", "media_artist", "artist", "currentArtist")
ALBUM_READINGS = ("mediaAlbum", "media_album", "album", "currentAlbum")
STATION_READINGS = ("stationName", "contentItemItemName", "currentSender")
ART_READINGS = (
    "mediaImageUrl",
    "media_image_url",
    "art",
    "currentAlbumArtURL",
    "cover",
)
PLAY_READINGS = ("playStatus", "transportState", "state")
PRESETS = 6
PRESET_READINGS = tuple(f"channel_{n:02d}" for n in range(1, PRESETS + 1))
READINGS = (
    TITLE_READINGS
    + ARTIST_READINGS
    + ALBUM_READINGS
    + STATION_READINGS
    + ART_READINGS
    + PRESET_READINGS
    + ("playStatus", "transportState", "artStatus", "channel", "volume", "mute")
)

NEXT_SETS = ("next", "nextTrack", "next_track", "skip", "forward")
PREV_SETS = ("prev", "prevTrack", "previous", "previousTrack", "previous_track")
OFF_WORDS = ("off", "offline", "standby", "disconnected", "absent", "unavailable")
EMPTY_PRESETS = ("", "-", "none", "empty", "leer")
_URL = re.compile(r"^https?://[^\s\"'<>]+$", re.IGNORECASE)


def _reading(info, *names):
    readings = info.get("readings") or {}
    for name in names:
        value = readings.get(name)
        if value not in (None, ""):
            return value
    return None


def is_media(info):
    attrs = info.get("attrs") or {}
    if attrs.get("matterType"):
        return False
    if info.get("FHEMPYTYPE") in MEDIA_FHEMPY_TYPES:
        return True
    if info.get("TYPE") in MEDIA_TYPES:
        return True
    if str(attrs.get("genericDeviceType", "")).lower() in MEDIA_GENERIC_TYPES:
        return True
    sets = kinds.set_names(info.get("sets"))
    plays = "playpause" in sets or {"play", "pause"} <= sets
    return plays and bool(sets & set(NEXT_SETS))


def _words(info):
    return [str(_reading(info, name) or "").strip().lower() for name in PLAY_READINGS]


def _playing(info):
    for word in _words(info):
        if word.startswith("pause"):
            return False
        if word.startswith("play") or word in ("buffering", "buffering_state"):
            return True
    return False


def _paused(info):
    return any(word.startswith("pause") for word in _words(info))


def _off(info):
    state = str(_reading(info, "state") or "").strip().lower()
    if _playing(info) or _paused(info):
        return False
    # BOSEST: 'online' means switched off but reachable
    return state in OFF_WORDS or (state == "online" and info.get("TYPE") == "BOSEST")


def art_url(info):
    """cover of what plays now, only http(s) URLs"""
    if str(_reading(info, "artStatus") or "IMAGE_PRESENT").upper() not in (
        "IMAGE_PRESENT",
        "",
    ):
        return None
    url = str(_reading(info, *ART_READINGS) or "").strip()
    return url if _URL.match(url) else None


def art_key(url):
    """short id of an image, so the tablets know when it changes"""
    if not url:
        return None
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]


def channel(info):
    number = kinds.number(_reading(info, "channel"))
    if number is None or not 1 <= number <= PRESETS:
        return None
    return int(number)


def presets(info):
    """the presets 1-6 of the device (BOSEST channel_01..06), with the
    logo learned while the preset played (info['preset_art'])"""
    sets = kinds.set_names(info.get("sets"))
    if "channel" not in sets:
        return []
    known = info.get("preset_art") or {}
    result = []
    for n, reading in enumerate(PRESET_READINGS, start=1):
        name = str(_reading(info, reading) or "").strip()
        if name.lower() in EMPTY_PRESETS:
            continue
        entry = {"n": n, "name": name}
        key = art_key(known.get(str(n)))
        if key:
            entry["art"] = key
        result.append(entry)
    return result


def state(info):
    playing = _playing(info)
    title = _reading(info, *TITLE_READINGS)
    station = _reading(info, *STATION_READINGS)
    if not title and station:
        title, station = station, None
    if station and station == title:
        station = None
    result = {
        "playing": playing,
        "paused": _paused(info),
        "on": not _off(info),
        "title": title,
        "artist": _reading(info, *ARTIST_READINGS),
        "album": _reading(info, *ALBUM_READINGS),
        "station": station,
        "art": art_key(art_url(info)) if not _off(info) else None,
        "volume": kinds.number(_reading(info, "volume")),
        "muted": str(_reading(info, "mute") or "").lower() in ("on", "1", "true"),
        "channel": channel(info),
    }
    return result


def features(info):
    """what the tile can do, from the set list of the device"""
    sets = kinds.set_names(info.get("sets"))
    return {
        "next": any(s in sets for s in NEXT_SETS),
        "prev": any(s in sets for s in PREV_SETS),
        "volume": "volume" in sets,
        "power": "on" in sets and "off" in sets,
    }


def _first(names, sets):
    return next((name for name in names if name in sets), None)


# action -> set commands to try, the first one the device has is sent
SIMPLE_ACTIONS = {
    "play": ("play", "playpause"),
    "pause": ("pause", "playpause", "stop"),
    "next": NEXT_SETS,
    "prev": PREV_SETS,
    "on": ("on",),
    "off": ("off",),
}


def _volume_command(sets, value):
    number = kinds.number(value)
    if number is None or "volume" not in sets:
        return []
    return [f"volume {int(max(0, min(100, round(number))))}"]


def _preset_command(info, sets, value):
    number = kinds.number(value)
    if number is None or not 1 <= number <= PRESETS:
        return []
    n = int(number)
    if "channel" in sets and any(p["n"] == n for p in presets(info)):
        return [f"channel {n}"]
    if "playFavorite" in sets:
        return [f"playFavorite {n}"]
    return []


def command(info, action, value=None):
    """FHEM set arguments for a tablet action on a music player"""
    sets = kinds.set_names(info.get("sets"))
    if action == "toggle":
        action = "pause" if _playing(info) else "play"
    if action == "play" and _off(info) and "on" in sets:
        return ["on"]
    if action == "volume":
        return _volume_command(sets, value)
    if action == "preset":
        return _preset_command(info, sets, value)
    name = _first(SIMPLE_ACTIONS.get(action, ()), sets)
    return [name] if name else []


def learn_preset_art(known, info, changed_recently):
    """remember the cover of a preset while it plays (BOSEST has no preset
    logos). known: {"1": url} of the device, changed in place.
    changed_recently: the preset was just chosen, so the first cover is the
    station logo, later covers of a playlist don't replace it.
    Returns True if something changed."""
    n = channel(info)
    url = art_url(info)
    if n is None or url is None or not _playing(info):
        return False
    key = str(n)
    if known.get(key) == url or (key in known and not changed_recently):
        return False
    known[key] = url
    return True
