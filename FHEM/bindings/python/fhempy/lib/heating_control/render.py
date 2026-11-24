"""Detail page: hydraulic diagram with live values, chart, rooms with
schedules, vacation, learned heating curve and the setup. All drawing
happens in the browser (www.js), the module pushes new values with
FW_runJavascript (fhcLive) so nothing polls."""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}


def js_json(data):
    """JSON which is safe inside a <script> element"""
    return (
        json.dumps(data, separators=(",", ":"), default=str)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _asset(name):
    path = os.path.join(_HERE, "www", name)
    mtime = os.path.getmtime(path)
    cached = _CACHE.get(name)
    if cached and cached[0] == mtime:
        return cached[1]
    with open(path, encoding="utf-8") as file:
        text = file.read()
    _CACHE[name] = (mtime, text)
    return text


def page(view, language="EN", room=False):
    """room: the page in the room of its own instead of the detail page"""
    lang = "de" if str(language).upper().startswith("DE") else "en"
    return (
        "<style>"
        + _asset("heating_control.css")
        + "</style>"
        + '<div id="fhc" class="fhc"></div>'
        + "<script>window.FHC_ROOM="
        + ("true" if room else "false")
        + ";window.FHC_LANG="
        + js_json(lang)
        + ";window.FHC_DATA="
        + js_json(view)
        + ";</script><script>"
        + _asset("heating_control.js")
        + "</script>"
    )
