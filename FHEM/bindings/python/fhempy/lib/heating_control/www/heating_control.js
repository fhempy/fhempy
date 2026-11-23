(function() {
"use strict";
var T = {
  de: {
    heating: "Heizt", idle: "Bereit", warm: "Räume warm", summer: "Sommer – keine Heizung",
    frost: "Frostschutz", off: "Aus (misst nur)", vacation: "Urlaub", setup: "Einrichtung fehlt",
    auto: "Automatik", mode_off: "Aus", supply: "Wärmequelle", mixer: "Mischer", pump: "Pumpe",
    flow: "Vorlauf", ret: "Rücklauf", target: "Soll", house: "Haus", outdoor: "Außen",
    outdoor_eff: "mit Vorhersage", heat: "Wärme an das Haus", today: "heute", total: "gesamt",
    on: "an", off_: "aus", rooms: "Räume", comfort: "Komfort", eco: "Eco", manual: "Manuell",
    window: "Fenster offen", until: "bis", back_auto: "Zurück zum Zeitplan",
    schedule: "Zeitplan", save: "Speichern", cancel: "Abbrechen", copy_all: "Für alle Räume übernehmen",
    tap_hint: "Antippen oder darüber wischen: orange = Komfort, blau = Eco",
    workday: "Arbeitstag", home: "Ganzer Tag zuhause", always_eco: "Immer Eco", always_comfort: "Immer Komfort",
    weekdays: "Mo–Fr", weekend: "Sa–So", alldays: "Alle Tage",
    vac_title: "Urlaub", vac_start: "Urlaub starten", vac_end: "Urlaub beenden",
    vac_back: "Zurück am", vac_temp: "Temperatur im Urlaub", vac_active: "Urlaub bis",
    vac_hint: "Am Tag der Rückkehr ist das Haus wieder warm.", week1: "1 Woche", week2: "2 Wochen", weekend_btn: "Wochenende",
    chart: "Verlauf", hours6: "6 h", hours24: "24 h", heat_w: "Wärme W", mixer_pct: "Mischer %",
    curve: "Gelernte Heizkurve", curve_base: "Grundkurve", curve_learned: "Gelernt",
    curve_now: "jetzt", learned_h: "Stunden gelernt", setup_title: "Einrichtung",
    unused: "– nicht verwendet –", apply: "Übernehmen", suggestion: "Vorschlag",
    pump_model: "Pumpentyp (Grundfos ALPHA)", pump_setting: "Stufe / Modus", pump_power: "Leistung W (nur ohne Messung)",
    thermometer: "Thermometer im Raum", thermostat_only: "Thermostat misst", weather: "Wetter (Vorhersage)",
    weather_none: "Kein Wetter-Gerät gefunden – openmeteo_weather anlegen für die Vorhersage.",
    no_rooms: "Keine Thermostate gefunden.", valve: "Ventil", source_t: "Raumthermometer",
    source_s: "Thermostat", flow_lh: "l/h", now: "jetzt", setup_missing: "Bitte noch einrichten:",
    roles: {mixer: "Mischer (0–100 %)", pump: "Umwälzpumpe (an/aus)", flow_sensor: "Vorlauf-Temperatur",
      return_sensor: "Rücklauf-Temperatur", supply_sensor: "Wärmequelle (Temperatur vor dem Mischer)",
      outdoor_sensor: "Außentemperatur (sonst vom Wetter)"},
    days: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    source_type: "Art der Wärmequelle",
    sources: {buffer: "Pufferspeicher", heatpump: "Wärmepumpe", wood: "Holzofen", pellet: "Pelletkessel",
      gas: "Gastherme", oil: "Ölkessel", district: "Fernwärme", solar: "Solarthermie"},
    setup_mode: "Einrichtung – es wird noch nichts gesteuert",
    setup_hint: "Solange die Einrichtung läuft, schaltet das Modul nichts: kein Mischer, keine Pumpe, keine Thermostate. Es zeigt nur die Werte an.",
    room_create: "Eigenen Raum „Heizungssteuerung“ anlegen", room_open: "Raum öffnen",
    room_hint: "Im eigenen Raum erscheint nur diese Seite, ohne Readings und Attribute.",
    start: "Steuerung starten", save_only: "Nur speichern", change_setup: "Einrichtung ändern",
    saved: "Die Einrichtung ist gespeichert. Die Steuerung startet erst mit „Steuerung starten“.", start_missing: "Starten geht, sobald eingerichtet ist:",
    start_ask: "Mit „Steuerung starten“ beginnt das Modul, Mischer, Pumpe und diese Thermostate zu schalten.", start_yes: "Ja, Steuerung jetzt starten",
    thermostats: "Thermostate", back_setup: "Zur Einrichtung (nichts steuern)",
    search: "Tippen zum Suchen …", suggested: "Vorschlag – bitte prüfen", no_match: "Nichts gefunden",
    reading: "Wert (Reading)", optional: "optional", unknown: "– weiß nicht –", room: "Raum",
    step: "Schritt", back: "Zurück", next: "Weiter", finish: "Fertig", w_go: "Los geht's",
    w_welcome_t: "Willkommen bei der Heizungssteuerung",
    w_welcome: "Der Assistent geht in 6 kurzen Schritten alles durch: Wärmequelle, Mischer, Pumpe, Temperaturen, Räume und Wetter. Am Ende siehst du eine Übersicht und startest die Steuerung selbst.",
    w_source_t: "Wärmequelle", w_mixer_t: "Mischer", w_pump_t: "Umwälzpumpe", w_temps_t: "Vorlauf und Rücklauf",
    w_rooms_t: "Räume und Thermostate", w_outdoor_t: "Außentemperatur und Wetter", w_done_t: "Übersicht",
    w_mixer: "Das Gerät, das den Mischer 0–100 % stellt (z. B. ein Shelly).",
    w_invert: "Umgekehrt: 0 % bedeutet voll warm",
    w_pump: "Das Gerät, das die Umwälzpumpe ein- und ausschaltet. Misst es die Leistung, wird die Durchflussmenge daraus geschätzt.",
    w_power: "Nur nötig, wenn der Schalter keine Leistung misst: der Wert auf dem Display der Pumpe.",
    w_flow: "Temperatur nach dem Mischer, die zu den Heizkörpern geht.", w_return: "Für die Wärmeleistung in W (optional).",
    w_rooms: "Hake an, welche Thermostate gesteuert werden, und gib jedem einen Raum. Vorgeschlagen ist der FHEM-Raum, du kannst einen eigenen Namen eintippen. Thermostate mit demselben Raum werden zusammen gesteuert.",
    w_need_mixer: "Bitte den Mischer auswählen.", w_need_pump: "Bitte die Pumpe auswählen.",
    w_need_flow: "Bitte die Vorlauf-Temperatur auswählen."
  },
  en: {
    heating: "Heating", idle: "Ready", warm: "Rooms warm", summer: "Summer – no heating",
    frost: "Frost protection", off: "Off (measuring only)", vacation: "Vacation", setup: "Setup missing",
    auto: "Automatic", mode_off: "Off", supply: "Heat source", mixer: "Mixer", pump: "Pump",
    flow: "Flow", ret: "Return", target: "Target", house: "House", outdoor: "Outdoor",
    outdoor_eff: "with forecast", heat: "Heat to the house", today: "today", total: "total",
    on: "on", off_: "off", rooms: "Rooms", comfort: "Comfort", eco: "Eco", manual: "Manual",
    window: "Window open", until: "until", back_auto: "Back to schedule",
    schedule: "Schedule", save: "Save", cancel: "Cancel", copy_all: "Use for all rooms",
    tap_hint: "Tap or swipe: orange = comfort, blue = eco",
    workday: "Work day", home: "Home all day", always_eco: "Always eco", always_comfort: "Always comfort",
    weekdays: "Mo–Fr", weekend: "Sa–Su", alldays: "All days",
    vac_title: "Vacation", vac_start: "Start vacation", vac_end: "End vacation",
    vac_back: "Back on", vac_temp: "Temperature during vacation", vac_active: "Vacation until",
    vac_hint: "On the day you are back the house is warm again.", week1: "1 week", week2: "2 weeks", weekend_btn: "Weekend",
    chart: "History", hours6: "6 h", hours24: "24 h", heat_w: "Heat W", mixer_pct: "Mixer %",
    curve: "Learned heating curve", curve_base: "Base curve", curve_learned: "Learned",
    curve_now: "now", learned_h: "hours learned", setup_title: "Setup",
    unused: "– not used –", apply: "Apply", suggestion: "suggestion",
    pump_model: "Pump type (Grundfos ALPHA)", pump_setting: "Setting / mode", pump_power: "Power W (only without measuring)",
    thermometer: "Thermometer in the room", thermostat_only: "thermostat measures", weather: "Weather (forecast)",
    weather_none: "No weather device found – define openmeteo_weather for the forecast.",
    no_rooms: "No thermostats found.", valve: "Valve", source_t: "room thermometer",
    source_s: "thermostat", flow_lh: "l/h", now: "now", setup_missing: "Please set up:",
    roles: {mixer: "Mixer (0–100 %)", pump: "Circulation pump (on/off)", flow_sensor: "Flow temperature",
      return_sensor: "Return temperature", supply_sensor: "Heat source (temperature before the mixer)",
      outdoor_sensor: "Outdoor temperature (else from weather)"},
    days: ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    source_type: "Type of heat source",
    sources: {buffer: "Buffer tank", heatpump: "Heat pump", wood: "Wood stove", pellet: "Pellet boiler",
      gas: "Gas boiler", oil: "Oil boiler", district: "District heating", solar: "Solar thermal"},
    setup_mode: "Setup – nothing is controlled yet",
    setup_hint: "While the setup is running the module switches nothing: no mixer, no pump, no thermostats. It only shows the values.",
    room_create: "Create the room “Heating”", room_open: "Open room",
    room_hint: "The room of its own shows only this page, without readings and attributes.",
    start: "Start control", save_only: "Save only", change_setup: "Change setup",
    saved: "The setup is saved. The control starts only with “Start control”.", start_missing: "Starting is possible once this is set up:",
    start_ask: "With “Start control” the module begins to switch the mixer, the pump and these thermostats.", start_yes: "Yes, start the control now",
    thermostats: "Thermostats", back_setup: "Back to setup (control nothing)",
    search: "Type to search …", suggested: "Suggestion – please check", no_match: "Nothing found",
    reading: "Value (reading)", optional: "optional", unknown: "– don't know –", room: "Room",
    step: "Step", back: "Back", next: "Next", finish: "Done", w_go: "Let's go",
    w_welcome_t: "Welcome to the heating control",
    w_welcome: "The assistant goes through everything in 6 short steps: heat source, mixer, pump, temperatures, rooms and weather. At the end you see an overview and start the control yourself.",
    w_source_t: "Heat source", w_mixer_t: "Mixer", w_pump_t: "Circulation pump", w_temps_t: "Flow and return",
    w_rooms_t: "Rooms and thermostats", w_outdoor_t: "Outdoor temperature and weather", w_done_t: "Overview",
    w_mixer: "The device which sets the mixer 0–100 % (e.g. a Shelly).",
    w_invert: "Inverted: 0 % means fully hot",
    w_pump: "The device which switches the circulation pump on and off. If it measures the power, the flow is estimated from it.",
    w_power: "Only needed if the switch doesn't measure the power: the value on the display of the pump.",
    w_flow: "Temperature after the mixer which goes to the radiators.", w_return: "For the heat in W (optional).",
    w_rooms: "Tick the thermostats to control and give each one a room. The FHEM room is suggested, you can type your own name. Thermostats with the same room are controlled together.",
    w_need_mixer: "Please choose the mixer.", w_need_pump: "Please choose the pump.",
    w_need_flow: "Please choose the flow temperature."
  }
};
var L = T[window.FHC_LANG] || T.en;
var D = window.FHC_DATA || {};
var root = document.getElementById("fhc");
if (!root) return;
var DEV = D.name;
var hours = 6;
var editing = null;
var pending = {};
var dragging = false;

function esc(s) {
  return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function(c) {
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c];
  });
}
function num(v, d, unit) {
  if (v === null || v === undefined || isNaN(v)) return "–";
  return Number(v).toFixed(d === undefined ? 1 : d) + (unit || "");
}
function width() {
  return Math.max(300, Math.min(1080, (root.clientWidth || 860) - 26));
}
function deg(v) { return num(v, 1, " °C"); }
function hm(ts) {
  var t = new Date(ts * 1000);
  return ("0" + t.getHours()).slice(-2) + ":" + ("0" + t.getMinutes()).slice(-2);
}
function send(text, done) {
  FW_cmd(FW_root + "?cmd=" + encodeURIComponent(text) + "&XHR=1", function(r) {
    if (r && r.trim()) {
      if (!/^<html>/.test(r)) r = "<pre>" + FW_htmlQuote(r) + "</pre>";
      FW_okDialog(r);
    }
    if (done) done(r);
  });
}
function set(args, done) { send("set " + DEV + " " + args, done); }
function later(key, ms, fn) {
  if (pending[key]) clearTimeout(pending[key]);
  pending[key] = setTimeout(function() { delete pending[key]; fn(); }, ms);
}

function stateName(s) {
  if (!s) return "";
  if (s.indexOf("setup") === 0) return "setup";
  return s;
}

// --- top line ---
function top() {
  var s = stateName(D.state);
  var text = s === "off" ? L.off : (L[s] || s);
  if (D.mode === "setup") {
    return '<div class="top"><span class="pill setup">' + esc(L.setup_mode) + '</span></div>';
  }
  var h = '<div class="top"><span class="pill ' + esc(s) + '">' + esc(text) + '</span>';
  h += '<span class="seg"><button data-mode="auto" class="' + (D.mode === "auto" ? "on" : "") + '">' +
    L.auto + '</button><button data-mode="off" class="' + (D.mode === "off" ? "on" : "") + '">' +
    L.mode_off + '</button></span>';
  if (D.control_room && !window.FHC_ROOM) {
    h += '<a class="chip" href="' + FW_root + '?room=' + encodeURIComponent(D.control_room) + '">🏠 ' +
      esc(L.room_open) + ": " + esc(D.control_room) + '</a>';
  }
  if (D.vacation && D.vacation.active) {
    h += '<span class="chip vacation">' + L.vac_active + " " + esc(dateText(D.vacation.until)) + '</span>';
  }
  h += '</div>';
  return h;
}

function dateText(iso) {
  if (!iso) return "";
  var p = iso.split("-");
  return p.length === 3 ? p[2] + "." + p[1] + "." + p[0] : iso;
}

// --- hydraulic diagram ---
var SOURCE_ICONS = {
  buffer: '<rect x="-15" y="-24" width="30" height="48" rx="15" class="ic"/><path d="M-15 -6 H15 M-15 8 H15" class="ic thin"/>',
  heatpump: '<rect x="-24" y="-18" width="48" height="36" rx="8" class="ic"/><circle cx="-6" cy="0" r="11" class="ic"/>' +
    '<path d="M-6 -11 V11 M-17 0 H5" class="ic thin"/><path d="M12 -8 H18 M12 0 H18 M12 8 H18" class="ic thin"/>',
  wood: '<path d="M0 -24 C10 -12 14 -6 10 4 C8 10 4 12 0 12 C-4 12 -9 9 -10 3 C-12 -6 -4 -10 0 -24 Z" class="ic"/>' +
    '<path d="M-18 18 L18 24 M-18 24 L18 18" class="ic"/>',
  pellet: '<path d="M0 -22 C10 -10 13 -4 9 6 C7 11 4 13 0 13 C-4 13 -9 10 -10 4 C-12 -4 -4 -8 0 -22 Z" class="ic"/>' +
    '<circle cx="-10" cy="21" r="2.5" class="icf"/><circle cx="0" cy="22" r="2.5" class="icf"/><circle cx="10" cy="21" r="2.5" class="icf"/>',
  gas: '<path d="M0 -24 C12 -10 16 -2 12 8 C9 16 4 18 0 18 C-4 18 -11 15 -12 7 C-14 -4 -4 -10 0 -24 Z" class="ic"/>' +
    '<path d="M0 0 C5 6 5 12 0 14 C-5 12 -5 6 0 0 Z" class="ic thin"/>',
  oil: '<path d="M0 -24 C10 -8 16 0 16 8 C16 17 9 22 0 22 C-9 22 -16 17 -16 8 C-16 0 -10 -8 0 -24 Z" class="ic"/>',
  district: '<rect x="-22" y="-6" width="16" height="28" rx="3" class="ic"/><rect x="-2" y="-20" width="22" height="42" rx="3" class="ic"/>' +
    '<path d="M4 -10 H14 M4 0 H14 M4 10 H14" class="ic thin"/>',
  solar: '<circle cx="-8" cy="-12" r="7" class="ic"/><path d="M-22 22 L-12 4 H22 L12 22 Z M-17 13 H17 M5 4 L-5 22" class="ic thin"/>'
};
function pill(x, y, label, value, cls) {
  // on a phone the drawing is scaled down, its texts are bigger (css)
  var k = 1;
  var w = k * (38 + label.length * 7 + value.length * 9.5), hh = 30 * k;
  return '<g class="pillg" transform="translate(' + (x - w / 2) + ' ' + (y - hh / 2) + ')"><rect width="' + w + '" height="' + hh +
    '" rx="' + hh / 2 + '" class="pill ' + (cls || "") + '"/><text x="' + 14 * k + '" y="' + 20 * k + '" class="pl">' +
    esc(label) + '</text><text x="' + (w - 14 * k) + '" y="' + 20 * k + '" text-anchor="end" class="pv">' + esc(value) + '</text></g>';
}
function arc(cx, cy, r, pct) {
  pct = Math.max(0, Math.min(100, pct || 0));
  if (pct >= 99.9) return '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" class="ring on"/>';
  var a = pct / 100 * 2 * Math.PI, x = cx + r * Math.sin(a), y = cy - r * Math.cos(a);
  return '<path class="ring on" d="M' + cx + ' ' + (cy - r) + ' A' + r + ' ' + r + ' 0 ' + (pct > 50 ? 1 : 0) +
    ' 1 ' + x.toFixed(1) + ' ' + y.toFixed(1) + '"/>';
}
function heatText(w) {
  if (w === null || w === undefined) return "–";
  return w >= 1000 ? num(w / 1000, 2, " kW") : num(w, 0, " W");
}
function scheme() {
  var h = D.house || {};
  var src = SOURCE_ICONS[D.heat_source] ? D.heat_source : "buffer";
  var pumpText = h.pump ? (h.pump_power ? num(h.pump_power, 0, " W") : L.on) : L.off_;
  var flowText = h.pump && h.flow_lh ? num(h.flow_lh, 0, " " + L.flow_lh) : "";
  var s = '<svg viewBox="0 0 860 300" role="img" aria-label="' + esc(L.heat) + '"><defs>' +
    '<linearGradient id="fhcHot" gradientUnits="userSpaceOnUse" x1="190" x2="290"><stop offset="0" stop-color="#f03e3e"/><stop offset="1" stop-color="#fd7e14"/></linearGradient>' +
    '<linearGradient id="fhcWarm" gradientUnits="userSpaceOnUse" x1="330" x2="640"><stop offset="0" stop-color="#fd7e14"/><stop offset="1" stop-color="#fab005"/></linearGradient>' +
    '<linearGradient id="fhcCold" gradientUnits="userSpaceOnUse" x1="640" x2="300"><stop offset="0" stop-color="#4dabf7"/><stop offset="1" stop-color="#1c7ed6"/></linearGradient>' +
    '<linearGradient id="fhcSrc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff8787" stop-opacity=".35"/>' +
    '<stop offset="1" stop-color="#fd7e14" stop-opacity=".12"/></linearGradient>' +
    '<linearGradient id="fhcHouse" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd8a8" stop-opacity=".45"/>' +
    '<stop offset="1" stop-color="#ffa94d" stop-opacity=".12"/></linearGradient>' +
    '<radialGradient id="fhcGlow"><stop offset="0" stop-color="#ff922b" stop-opacity=".55"/><stop offset="1" stop-color="#ff922b" stop-opacity="0"/></radialGradient>' +
    '</defs>';
  // pipes first, everything else on top
  s += '<path class="pipe" stroke="url(#fhcHot)" d="M190 90 H266"/>';
  s += '<path class="pipe" stroke="url(#fhcWarm)" d="M334 90 H640"/>';
  s += '<path class="pipe" stroke="url(#fhcCold)" d="M640 230 H300 V124"/>';
  s += '<path class="pipe" stroke="#1c7ed6" d="M300 230 H190"/>';
  ["M190 90 H266", "M334 90 H640", "M640 230 H300 V124", "M300 230 H190"].forEach(function(d) {
    s += '<path class="flowdash" d="' + d + '"/>';
  });
  // heat source
  s += '<rect x="20" y="30" width="170" height="240" rx="24" class="tile" fill="url(#fhcSrc)"/>';
  s += '<g transform="translate(105 88)">' + SOURCE_ICONS[src] + '</g>';
  s += '<text x="105" y="150" text-anchor="middle" class="tl">' + esc(L.sources[src]) + '</text>';
  s += '<text x="105" y="190" text-anchor="middle" class="tv">' + num(h.supply, 1, "°") + '</text>';
  // mixer: valve with a ring for its position
  s += '<circle cx="300" cy="90" r="34" class="node"/><circle cx="300" cy="90" r="34" class="ring"/>' + arc(300, 90, 34, h.mixer);
  s += '<path d="M284 80 L300 90 L284 100 Z M316 80 L300 90 L316 100 Z M290 112 L300 90 L310 112 Z" class="valve"/>';
  s += '<text x="300" y="22" text-anchor="middle" class="tl">' + L.mixer + '</text>';
  s += '<text x="300" y="46" text-anchor="middle" class="tv sm">' + num(h.mixer, 0, " %") + '</text>';
  // pump with a turning impeller
  s += '<circle cx="420" cy="90" r="30" class="node pumpnode"/>';
  s += '<g class="impeller" style="transform-origin:420px 90px"><path d="M420 90 L420 68 M420 90 L439 101 M420 90 L401 101" class="blade"/>' +
    '<circle cx="420" cy="90" r="5" class="hub"/></g>';
  s += '<text x="420" y="22" text-anchor="middle" class="tl">' + L.pump + '</text>';
  s += '<text x="420" y="46" text-anchor="middle" class="tv sm">' + esc(pumpText) + '</text>';
  if (flowText) s += '<text x="420" y="146" text-anchor="middle" class="tl">' + esc(flowText) + '</text>';
  s += pill(540, 90, L.flow, num(h.flow, 1, "°"), "hot");
  s += pill(470, 230, L.ret, num(h["return"], 1, "°"), "cold");
  // house
  s += '<circle cx="740" cy="170" r="110" fill="url(#fhcGlow)" class="glow"/>';
  s += '<path d="M640 128 Q640 118 648 112 L732 48 Q740 42 748 48 L832 112 Q840 118 840 128 V256 Q840 270 826 270 H654 Q640 270 640 256 Z"' +
    ' class="tile" fill="url(#fhcHouse)"/>';
  [668, 718, 768].forEach(function(x) {
    s += '<g class="radiator">';
    for (var i = 0; i < 5; i++) s += '<rect x="' + (x + i * 8) + '" y="222" width="6" height="28" rx="3"/>';
    s += '</g>';
  });
  s += '<text x="740" y="124" text-anchor="middle" class="tl">' + L.heat + '</text>';
  s += '<text x="740" y="166" text-anchor="middle" class="tv">' + heatText(h.heat_w) + '</text>';
  s += '<text x="740" y="196" text-anchor="middle" class="tl">' + L.target + " " + L.flow + " " + num(h.flow_target, 1, "°") + '</text>';
  s += '</svg>';
  var k = '<div class="kpi">';
  // on a phone the drawing only shows pictures, the values are here
  k += '<div class="mob">' + L.flow + '<b>' + deg(h.flow) + '</b></div>';
  k += '<div class="mob">' + L.ret + '<b>' + deg(h["return"]) + '</b></div>';
  k += '<div class="mob">' + esc(L.sources[src]) + '<b>' + deg(h.supply) + '</b></div>';
  k += '<div class="mob">' + L.mixer + '<b>' + num(h.mixer, 0, " %") + '</b></div>';
  k += '<div class="mob">' + L.pump + '<b>' + esc(pumpText) + (flowText ? " · " + esc(flowText) : "") + '</b></div>';
  k += '<div class="mob">' + L.heat + '<b>' + heatText(h.heat_w) + '</b></div>';
  k += '<div>' + L.today + '<b>' + num(h.heat_today, 1, " kWh") + '</b></div>';
  k += '<div>' + L.outdoor + '<b>' + deg(h.outdoor) + '</b></div>';
  k += '<div>' + L.outdoor + " " + L.outdoor_eff + '<b>' + deg(h.outdoor_eff) + '</b></div>';
  k += '<div>' + L.flow + " " + L.target + '<b>' + deg(h.flow_target) + '</b></div>';
  k += '</div>';
  return '<div class="scheme card"><div class="wide">' + s + '</div>' + k + '</div>';
}

// --- line chart ---
function chart(points, series, opts) {
  var W = width(), H = opts.height || 220, left = 40, right = 12, topPad = 10, bottom = 22;
  var now = D.now || Date.now() / 1000;
  var start = now - hours * 3600;
  var pts = points.filter(function(p) { return p[0] >= start; });
  var vals = [];
  series.forEach(function(s) {
    if (s.right) return;
    pts.forEach(function(p) { if (p[s.i] !== null && p[s.i] !== undefined) vals.push(p[s.i]); });
  });
  if (!pts.length || (!vals.length && !opts.onlyRight)) return '<div class="muted">–</div>';
  var lo = 0, hi = 100, unit = opts.onlyRight ? "%" : "°";
  if (!opts.onlyRight) {
    lo = Math.floor(Math.min.apply(null, vals) / 5) * 5;
    hi = Math.ceil(Math.max.apply(null, vals) / 5) * 5;
    if (hi - lo < 10) hi = lo + 10;
  }
  var rmax = opts.rightMax || 100;
  function x(t) { return left + (W - left - right) * (t - start) / (now - start); }
  function y(v) { return topPad + (H - topPad - bottom) * (hi - v) / (hi - lo); }
  function yr(v) { return topPad + (H - topPad - bottom) * (1 - v / rmax); }
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '">';
  var gstep = opts.onlyRight ? 50 : (hi - lo > 40 ? 10 : 5);
  for (var g = lo; g <= hi; g += gstep) {
    s += '<line class="gl" x1="' + left + '" x2="' + (W - right) + '" y1="' + y(g) + '" y2="' + y(g) + '"/>';
    s += '<text x="' + (left - 4) + '" y="' + (y(g) + 4) + '" text-anchor="end">' + g + unit + '</text>';
  }
  var step = (hours <= 6 ? 3600 : 3 * 3600) * (W < 600 ? 2 : 1);
  for (var t = Math.ceil(start / step) * step; t <= now; t += step) {
    s += '<text x="' + x(t) + '" y="' + (H - 5) + '" text-anchor="middle">' + hm(t) + '</text>';
  }
  if (opts.pump) {
    pts.forEach(function(p, i) {
      if (!p[7] || i === pts.length - 1) return;
      var w = Math.max(x(pts[i + 1][0]) - x(p[0]), 0.5);
      s += '<rect x="' + x(p[0]) + '" y="' + topPad + '" width="' + w + '" height="' + (H - topPad - bottom) +
        '" fill="var(--ok)" opacity=".07"/>';
    });
  }
  series.forEach(function(se) {
    var d = "", gap = true;
    pts.forEach(function(p) {
      var v = p[se.i];
      if (v === null || v === undefined) { gap = true; return; }
      d += (gap ? "M" : "L") + x(p[0]).toFixed(1) + " " + (se.right ? yr(v) : y(v)).toFixed(1);
      gap = false;
    });
    if (se.area && d) {
      s += '<path class="area" fill="' + se.c + '" d="' + d + ' L' + x(pts[pts.length - 1][0]) + ' ' + yr(0) +
        ' L' + x(pts[0][0]) + ' ' + yr(0) + ' Z"/>';
    }
    s += '<path class="l" stroke="' + se.c + '" d="' + d + '"' + (se.dash ? ' stroke-dasharray="5 4"' : "") + '/>';
  });
  s += '</svg>';
  var lg = '<div class="legend">' + series.map(function(se) {
    return '<span style="--c:' + se.c + '">' + esc(se.n) + '</span>';
  }).join("") + '</div>';
  return lg + s;
}

function charts() {
  var hist = D.history || [];
  var h = '<h3>' + L.chart + ' <span class="seg"><button data-hours="6" class="' + (hours === 6 ? "on" : "") +
    '">' + L.hours6 + '</button><button data-hours="24" class="' + (hours === 24 ? "on" : "") + '">' +
    L.hours24 + '</button></span></h3>';
  h += '<div class="chart card">' + chart(hist, [
    {i: 1, n: L.flow, c: "#e8590c"},
    {i: 2, n: L.flow + " " + L.target, c: "#e8590c", dash: true},
    {i: 3, n: L.ret, c: "#1971c2"},
    {i: 4, n: L.supply, c: "#c92a2a"},
    {i: 5, n: L.outdoor, c: "#2b8a3e"}
  ], {pump: true});
  var maxHeat = 1000;
  hist.forEach(function(p) { if (p[8] > maxHeat) maxHeat = p[8]; });
  maxHeat = Math.ceil(maxHeat / 1000) * 1000;
  var scaled = hist.map(function(p) {
    return [p[0], null, null, null, null, null, p[6], p[7], p[8] === null ? null : p[8] / maxHeat * 100];
  });
  h += chart(scaled, [
    {i: 8, n: L.heat_w + " (max " + maxHeat + " W)", c: "#f08c00", right: true, area: true},
    {i: 6, n: L.mixer_pct, c: "#7048e8", right: true}
  ], {height: 130, pump: true, onlyRight: true});
  h += '</div>';
  return h;
}

// --- rooms ---
function todayBar(room, cls) {
  var day = (new Date().getDay() + 6) % 7;
  var periods = (room.week || {})[String(day)] || [];
  var h = '<div class="bar ' + (cls || "") + '">';
  for (var i = 0; i < 48; i++) {
    var c = periods.some(function(p) { return p[0] <= i * 30 && i * 30 < p[1]; });
    h += '<i class="' + (c ? "c" : "") + '"></i>';
  }
  var now = new Date();
  h += '<b style="left:' + ((now.getHours() * 60 + now.getMinutes()) / 1440 * 100).toFixed(2) + '%"></b>';
  return h + '</div><div class="hours"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>';
}

function stateChip(room) {
  var s = room.state;
  var text = L[s] || s;
  if (s === "manual" && room.override_until) text += " " + L.until + " " + hm(room.override_until);
  return '<span class="chip ' + esc(s) + '">' + esc(text) + '</span>';
}

function roomCard(room) {
  var open = editing && editing.key === room.key;
  var h = '<div class="card room' + (open ? " editing" : "") + '" data-room="' + esc(room.key) + '">';
  h += '<div class="head"><span class="name">' + esc(room.name) + '</span>' + stateChip(room) + '</div>';
  h += '<div class="temp">' + deg(room.actual) + '</div>';
  h += '<div class="muted">' + (room.source === "thermometer" ? L.source_t : L.source_s) +
    (room.valve !== null && room.valve !== undefined ? " · " + L.valve + " " + num(room.valve, 0, " %") : "") + '</div>';
  h += '<div class="target"><button class="round" data-step="-0.5" aria-label="-">−</button>' +
    '<span class="val">' + num(room.target, 1, "°") + '</span>' +
    '<button class="round" data-step="0.5" aria-label="+">+</button></div>';
  h += todayBar(room);
  h += '<div class="row" style="margin-top:8px"><button data-edit="1">' + L.schedule + '</button>';
  if (room.state === "manual") h += '<button data-auto="1">' + L.back_auto + '</button>';
  h += '</div>';
  if (editing && editing.key === room.key) h += editor(room);
  h += '</div>';
  return h;
}

function rooms() {
  var list = D.rooms || [];
  var h = '<h3>' + L.rooms + '</h3>';
  if (!list.length) return h + '<div class="muted">' + L.no_rooms + '</div>';
  return h + '<div class="grid">' + list.map(roomCard).join("") + '</div>';
}

// --- schedule editor ---
function startEdit(room) {
  var week = {};
  for (var d = 0; d < 7; d++) week[d] = ((room.week || {})[String(d)] || []).map(function(p) { return p.slice(); });
  var today = (new Date().getDay() + 6) % 7;
  editing = {key: room.key, week: week, days: today < 5 ? [0, 1, 2, 3, 4] : [5, 6],
    comfort: room.comfort, eco: room.eco};
}

function slots(periods) {
  var a = [];
  for (var i = 0; i < 48; i++) a.push(periods.some(function(p) { return p[0] <= i * 30 && i * 30 < p[1]; }));
  return a;
}
function periodsOf(a) {
  var out = [], start = null;
  for (var i = 0; i <= 48; i++) {
    if (i < 48 && a[i]) { if (start === null) start = i; }
    else if (start !== null) { out.push([start * 30, i * 30]); start = null; }
  }
  return out;
}
function hhmm(m) { return ("0" + Math.floor(m / 60)).slice(-2) + ":" + ("0" + m % 60).slice(-2); }
function weekText(week) {
  var parts = [];
  for (var d = 0; d < 7; d++) {
    var p = week[d].map(function(x) { return hhmm(x[0]) + "-" + hhmm(x[1]); }).join(",");
    parts.push(T.en.days[d] + " " + (p || "-"));
  }
  return parts.join("; ");
}

function editor(room) {
  var e = editing, first = e.days[0];
  var a = slots(e.week[first]);
  var h = '<div class="editor">';
  h += '<div class="row days"><button data-group="wd">' + L.weekdays + '</button><button data-group="we">' +
    L.weekend + '</button><button data-group="all">' + L.alldays + '</button></div>';
  h += '<div class="row days" style="margin-top:6px">';
  for (var d = 0; d < 7; d++) {
    h += '<button data-day="' + d + '" class="' + (e.days.indexOf(d) >= 0 ? "on" : "") + '">' + L.days[d] + '</button>';
  }
  h += '</div><div class="bar edit" data-bar="1" style="margin-top:10px">';
  for (var i = 0; i < 48; i++) h += '<i data-slot="' + i + '" class="' + (a[i] ? "c" : "") + '"></i>';
  h += '</div><div class="hours"><span>0</span><span>3</span><span>6</span><span>9</span><span>12</span>' +
    '<span>15</span><span>18</span><span>21</span><span>24</span></div>';
  h += '<div class="muted">' + L.tap_hint + '</div>';
  h += '<div class="row" style="margin-top:6px">' +
    '<button data-preset="work">' + L.workday + '</button><button data-preset="home">' + L.home +
    '</button><button data-preset="eco">' + L.always_eco + '</button><button data-preset="comfort">' +
    L.always_comfort + '</button></div>';
  h += '<div class="row" style="margin-top:10px">' + stepper("comfort", L.comfort, e.comfort) +
    stepper("eco", L.eco, e.eco) + '</div>';
  h += '<div class="row" style="margin-top:10px"><button class="primary" data-save="1">' + L.save +
    '</button><button data-copy="1">' + L.copy_all + '</button><button data-close="1">' + L.cancel + '</button></div>';
  return h + '</div>';
}
function stepper(kind, label, value) {
  return '<span class="stepper"><span class="chip ' + kind + '">' + label + '</span>' +
    '<button class="round" data-lvl="' + kind + '" data-d="-0.5">−</button><b>' + num(value, 1, "°") +
    '</b><button class="round" data-lvl="' + kind + '" data-d="0.5">+</button></span>';
}

function applySlots(a) {
  editing.days.forEach(function(d) { editing.week[d] = periodsOf(a); });
}

function bindEditor(card) {
  var bar = card.querySelector("[data-bar]");
  if (!bar) return;
  var paint = null;
  function cellAt(ev) {
    var r = bar.getBoundingClientRect();
    var i = Math.floor((ev.clientX - r.left) / r.width * 48);
    return Math.max(0, Math.min(47, i));
  }
  function apply(i) {
    var cell = bar.children[i];
    if (!cell) return;
    cell.className = paint ? "c" : "";
  }
  bar.addEventListener("pointerdown", function(ev) {
    var i = cellAt(ev);
    paint = !bar.children[i].classList.contains("c");
    dragging = true;
    apply(i);
    bar.setPointerCapture(ev.pointerId);
    ev.preventDefault();
  });
  bar.addEventListener("pointermove", function(ev) { if (paint !== null) apply(cellAt(ev)); });
  function done() {
    if (paint === null) return;
    paint = null;
    dragging = false;
    var a = [];
    for (var i = 0; i < 48; i++) a.push(bar.children[i].classList.contains("c"));
    applySlots(a);
  }
  bar.addEventListener("pointerup", done);
  bar.addEventListener("pointercancel", done);
}

var PRESETS = {
  work: [[360, 480], [960, 1320]],
  home: [[420, 1350]],
  eco: [],
  comfort: [[0, 1440]]
};

function editorClick(btn, room) {
  var e = editing;
  if (btn.dataset.group) {
    e.days = btn.dataset.group === "wd" ? [0, 1, 2, 3, 4] : btn.dataset.group === "we" ? [5, 6] : [0, 1, 2, 3, 4, 5, 6];
  } else if (btn.dataset.day) {
    var d = Number(btn.dataset.day), i = e.days.indexOf(d);
    if (i >= 0 && e.days.length > 1) e.days.splice(i, 1);
    else if (i < 0) e.days.push(d);
    e.days.sort(function(a, b) { return a - b; });
  } else if (btn.dataset.preset) {
    applySlots(slots(PRESETS[btn.dataset.preset]));
  } else if (btn.dataset.lvl) {
    e[btn.dataset.lvl] = Math.max(5, Math.min(30, Number(e[btn.dataset.lvl]) + Number(btn.dataset.d)));
  } else if (btn.dataset.save) {
    set("comfort_temp " + room.key + " " + e.comfort, function() {
      set("eco_temp " + room.key + " " + e.eco, function() {
        set("schedule " + room.key + " " + weekText(e.week));
      });
    });
    editing = null;
  } else if (btn.dataset.copy) {
    var key = room.key, text = weekText(e.week), c = e.comfort, ec = e.eco;
    set("comfort_temp " + key + " " + c, function() {
      set("eco_temp " + key + " " + ec, function() {
        set("schedule " + key + " " + text, function() { set("copy_schedule " + key + " all"); });
      });
    });
    editing = null;
  } else if (btn.dataset.close) {
    editing = null;
  } else {
    return false;
  }
  return true;
}

function roomClick(btn, card) {
  var key = card.dataset.room;
  var room = (D.rooms || []).filter(function(r) { return r.key === key; })[0];
  if (!room) return;
  if (editing && editing.key === key && editorClick(btn, room)) { render(); return; }
  if (btn.dataset.step) {
    room.target = Math.max(5, Math.min(30, (room.target || 20) + Number(btn.dataset.step)));
    room.state = "manual";
    render();
    later("room" + key, 900, function() { set("room_temp " + key + " " + room.target); });
  } else if (btn.dataset.auto) {
    set("room_temp " + key + " auto");
  } else if (btn.dataset.edit) {
    if (editing && editing.key === key) editing = null; else startEdit(room);
    render();
  }
}

// --- vacation ---
var vacOpen = false;
function isoDay(offset) {
  var t = new Date(Date.now() + offset * 86400000);
  return t.getFullYear() + "-" + ("0" + (t.getMonth() + 1)).slice(-2) + "-" + ("0" + t.getDate()).slice(-2);
}
function nextMonday() {
  var d = new Date().getDay();
  return isoDay(((8 - d) % 7) || 7);
}
function vacation() {
  var v = D.vacation || {};
  var h = '<h3>' + L.vac_title + '</h3><div class="card">';
  if (v.active) {
    h += '<div class="row"><b>' + L.vac_active + " " + esc(dateText(v.until)) + " · " + num(v.temp, 1, " °C") +
      '</b><button class="primary" data-vac="off">' + L.vac_end + '</button></div>';
  } else if (!vacOpen) {
    h += '<button class="primary" data-vac="open">' + L.vac_start + '</button> <span class="muted">' + L.vac_hint + '</span>';
  } else {
    h += '<div class="row"><button data-vacday="' + nextMonday() + '">' + L.weekend_btn + '</button>' +
      '<button data-vacday="' + isoDay(7) + '">' + L.week1 + '</button><button data-vacday="' + isoDay(14) +
      '">' + L.week2 + '</button></div>';
    h += '<label class="f">' + L.vac_back + '</label><input type="date" id="fhcVacDay" min="' + isoDay(1) +
      '" value="' + isoDay(7) + '">';
    h += '<label class="f">' + L.vac_temp + '</label><input type="number" id="fhcVacTemp" min="5" max="25" step="0.5" value="' +
      esc(v.temp || 16) + '" style="width:80px"> °C';
    h += '<div class="row" style="margin-top:10px"><button class="primary" data-vac="start">' + L.vac_start +
      '</button><button data-vac="close">' + L.cancel + '</button></div><div class="muted">' + L.vac_hint + '</div>';
  }
  return h + '</div>';
}
function vacClick(btn) {
  if (btn.dataset.vacday) {
    document.getElementById("fhcVacDay").value = btn.dataset.vacday;
    return;
  }
  var a = btn.dataset.vac;
  if (a === "open") { vacOpen = true; render(); }
  else if (a === "close") { vacOpen = false; render(); }
  else if (a === "off") set("vacation_off");
  else if (a === "start") {
    var day = document.getElementById("fhcVacDay").value;
    var temp = document.getElementById("fhcVacTemp").value;
    if (!day) return;
    vacOpen = false;
    set("vacation " + day + (temp ? " " + temp : ""));
  }
}

// --- learned curve ---
function curveChart() {
  var c = D.curve;
  if (!c || !c.points) return "";
  var W = width(), H = 220, left = 40, right = 20, topPad = 10, bottom = 26;
  var lo = 20, hi = 20;
  c.points.forEach(function(p) { hi = Math.max(hi, p[1], p[2]); lo = Math.min(lo, p[1], p[2]); });
  lo = Math.floor(lo / 5) * 5; hi = Math.ceil(hi / 5) * 5;
  function x(o) { return left + (W - left - right) * (o + 15) / 35; }
  function y(v) { return topPad + (H - topPad - bottom) * (hi - v) / Math.max(hi - lo, 1); }
  var s = '<svg viewBox="0 0 ' + W + ' ' + H + '">';
  for (var g = lo; g <= hi; g += 5) {
    s += '<line class="gl" x1="' + left + '" x2="' + (W - right) + '" y1="' + y(g) + '" y2="' + y(g) + '"/>' +
      '<text x="' + (left - 4) + '" y="' + (y(g) + 4) + '" text-anchor="end">' + g + '°</text>';
  }
  for (var o = -15; o <= 20; o += (W < 600 ? 10 : 5)) {
    s += '<text x="' + x(o) + '" y="' + (H - 8) + '" text-anchor="middle">' + o + '°</text>';
  }
  ["1", "2"].forEach(function(k, n) {
    var d = c.points.map(function(p, i) { return (i ? "L" : "M") + x(p[0]).toFixed(1) + " " + y(p[n + 1]).toFixed(1); }).join("");
    s += '<path class="l" stroke="' + (n ? "#e8590c" : "#868e96") + '" d="' + d + '"' + (n ? "" : ' stroke-dasharray="5 4"') + '/>';
  });
  if (c.current && c.current[0] !== null && c.current[1] !== null) {
    s += '<circle cx="' + x(Math.max(-15, Math.min(20, c.current[0]))) + '" cy="' + y(c.current[1]) + '" r="6" fill="#c92a2a"/>';
  }
  s += '</svg>';
  return '<h3>' + L.curve + '</h3><div class="card"><div class="legend"><span style="--c:#868e96">' + L.curve_base +
    '</span><span style="--c:#e8590c">' + L.curve_learned + '</span><span style="--c:#c92a2a">' + L.curve_now +
    '</span><span class="muted">' + num(c.hours, 0, " " + L.learned_h) + '</span></div>' + s + '</div>';
}

// --- setup assistant: step by step, nothing is controlled until the end ---
var STEPS = ["welcome", "source", "mixer", "pump", "temps", "rooms", "outdoor", "done"];
var W = null; // {step, v: chosen values, saved: values on the server, err}
var setupOpen = false;
function suggested(o) { return o ? (o.value || o.suggestion || "") : ""; }
function wizStart(step) {
  var st = D.setup, v = {}, saved = {};
  ["mixer", "pump"].forEach(function(a) {
    v[a] = suggested(st.roles[a]); saved[a] = st.roles[a].value || "";
  });
  ["flow_sensor", "return_sensor", "supply_sensor", "outdoor_sensor"].forEach(function(a) {
    v[a] = suggested(st.sensors[a]); saved[a] = st.sensors[a].value || "";
  });
  v.heat_source = saved.heat_source = D.heat_source || "buffer";
  v.mixer_invert = saved.mixer_invert = st.mixer_invert ? "1" : "0";
  v.pump_model = saved.pump_model = st.pump_model || "";
  v.pump_setting = saved.pump_setting = st.pump_setting || "";
  v.pump_power = saved.pump_power = st.pump_power ? String(st.pump_power) : "";
  v.exclude = saved.exclude = (st.thermostats || []).filter(function(t) { return !t.used; })
    .map(function(t) { return t.name; }).join(",");
  v.rooms = {};
  (st.thermostats || []).forEach(function(t) { v.rooms[t.name] = t.room; });
  saved.thermostat_rooms = roomsText(v.rooms);
  v.thermometers = {}; saved.thermometers = "";
  var parts = [];
  Object.keys(st.thermometers || {}).forEach(function(key) {
    var t = st.thermometers[key];
    v.thermometers[key] = suggested(t);
    if (t.value) parts.push(key + "=" + t.value);
  });
  saved.thermometers = parts.join(",");
  W = {step: step || 0, v: v, saved: saved, err: ""};
}
function roomKey(name) {
  var map = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"};
  var key = String(name).replace(/[äöüßÄÖÜ]/g, function(c) { return map[c]; })
    .replace(/[^A-Za-z0-9_]/g, "_").replace(/^_+|_+$/g, "");
  return key || "room";
}
// own rooms: only where they differ from the FHEM room
function roomsText(rooms) {
  return (D.setup.thermostats || []).filter(function(t) { return rooms[t.name] && rooms[t.name] !== t.fhem_room; })
    .map(function(t) { return t.name + "=" + rooms[t.name]; }).join(",");
}
// rooms with at least one controlled thermostat: [[name, key]]
function usedRooms() {
  var off = W.v.exclude ? W.v.exclude.split(",") : [], seen = {}, list = [];
  (D.setup.thermostats || []).forEach(function(t) {
    var name = W.v.rooms[t.name] || t.room;
    if (off.indexOf(t.name) >= 0 || seen[name]) return;
    seen[name] = true;
    list.push([name, roomKey(name)]);
  });
  return list.sort(function(a, b) { return a[0].localeCompare(b[0]); });
}
function thermometersText() {
  return usedRooms().filter(function(r) { return W.v.thermometers[r[1]]; })
    .map(function(r) { return r[1] + "=" + W.v.thermometers[r[1]]; }).join(",");
}
var STEP_ATTRS = {
  source: ["heat_source", "supply_sensor"], mixer: ["mixer", "mixer_invert"],
  pump: ["pump", "pump_model", "pump_setting", "pump_power"], temps: ["flow_sensor", "return_sensor"],
  rooms: ["thermostat_rooms", "exclude_thermostats", "thermometers"], outdoor: ["outdoor_sensor"]
};
function wizValue(attr) {
  if (attr === "exclude_thermostats") return W.v.exclude;
  if (attr === "thermometers") return thermometersText();
  if (attr === "thermostat_rooms") return roomsText(W.v.rooms);
  if (attr === "pump_model") return W.v.pump_model.replace(/ /g, "_");
  return W.v[attr] || "";
}
function wizSaved(attr) {
  if (attr === "exclude_thermostats") return W.saved.exclude;
  if (attr === "pump_model") return (W.saved.pump_model || "").replace(/ /g, "_");
  return W.saved[attr] || "";
}
function wizSave(name) {
  (STEP_ATTRS[name] || []).forEach(function(attr) {
    var value = wizValue(attr);
    if (value === wizSaved(attr)) return;
    if (attr === "mixer_invert" && value === "0" && !wizSaved(attr)) return;
    attrCmd(attr, value);
    if (attr === "exclude_thermostats") W.saved.exclude = value;
    else W.saved[attr] = attr === "pump_model" ? W.v.pump_model : value;
    if (attr === "heat_source") D.heat_source = value;
  });
}
function wizMissing() {
  var m = [];
  var all = (D.setup.thermostats || []).length;
  var excluded = W.v.exclude ? W.v.exclude.split(",").length : 0;
  if (!all || excluded >= all) m.push(L.thermostats);
  if (!W.v.mixer) m.push(L.mixer);
  if (!W.v.pump) m.push(L.pump);
  if (!W.v.flow_sensor) m.push(L.flow);
  return m;
}
function attrCmd(attr, value) {
  send(value ? "attr " + DEV + " " + attr + " " + value : "deleteattr " + DEV + " " + attr);
}

// type-ahead device field
var combos = {};
function labelOf(options, value) {
  for (var i = 0; i < options.length; i++) if (options[i][0] === value) return options[i][1];
  return value || "";
}
function combo(key, options, value, suggestion) {
  var id = "fhcW_" + key;
  combos[id] = {key: key, options: options};
  return '<div class="combo"><input type="text" id="' + id + '" data-combo="' + id + '" autocomplete="off" ' +
    'spellcheck="false" placeholder="' + esc(L.search) + '" value="' + esc(labelOf(options, value)) + '">' +
    '<div class="combo-list" hidden></div></div>' +
    (value && value === suggestion ? '<div class="sugg">★ ' + esc(L.suggested) + '</div>' : '');
}
function withAll(first) {
  var seen = {}, list = [];
  first.forEach(function(o) { seen[o[0].split(":")[0]] = true; list.push(o); });
  (D.setup.devices || []).forEach(function(d) { if (!seen[d[0]]) list.push(d); });
  return list;
}
function comboFill(input, all) {
  var c = combos[input.dataset.combo], box = input.nextElementSibling;
  var words = all ? [] : input.value.toLowerCase().split(/\s+/).filter(Boolean);
  var hits = c.options.filter(function(o) {
    var text = (o[0] + " " + o[1]).toLowerCase();
    return words.every(function(w) { return text.indexOf(w) >= 0; });
  }).slice(0, 60);
  c.hits = hits; c.active = -1;
  box.innerHTML = hits.length ? hits.map(function(o, i) {
    return '<div class="opt" data-i="' + i + '">' + esc(o[1]) + '</div>';
  }).join("") : '<div class="none">' + esc(L.no_match) + '</div>';
  box.hidden = false;
}
function comboPick(input, i) {
  var c = combos[input.dataset.combo], o = c.hits && c.hits[i];
  input.nextElementSibling.hidden = true;
  if (!o) return;
  setWizValue(c.key, o[0]);
  render();
}
function setWizValue(key, value) {
  if (key.indexOf("therm_") === 0) W.v.thermometers[key.slice(6)] = value;
  else W.v[key] = value;
}
function getWizValue(key) {
  return key.indexOf("therm_") === 0 ? W.v.thermometers[key.slice(6)] || "" : W.v[key] || "";
}
root.addEventListener("focusin", function(ev) {
  var input = ev.target;
  if (!input.dataset || !input.dataset.combo) return;
  input.select();
  comboFill(input, true);
});
root.addEventListener("input", function(ev) {
  var el = ev.target;
  if (el.dataset && el.dataset.combo) comboFill(el, false);
  if (el.dataset && el.dataset.wiz && W) W.v[el.dataset.wiz] = el.value.trim();
});
root.addEventListener("keydown", function(ev) {
  var input = ev.target;
  if (!input.dataset || !input.dataset.combo) return;
  var c = combos[input.dataset.combo], box = input.nextElementSibling;
  if (!c.hits) return;
  if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
    ev.preventDefault();
    c.active = Math.max(0, Math.min(c.hits.length - 1, c.active + (ev.key === "ArrowDown" ? 1 : -1)));
    box.querySelectorAll(".opt").forEach(function(el, i) {
      el.classList.toggle("act", i === c.active);
      if (i === c.active) el.scrollIntoView({block: "nearest"});
    });
  } else if (ev.key === "Enter") {
    ev.preventDefault();
    comboPick(input, c.active >= 0 ? c.active : 0);
  } else if (ev.key === "Escape") {
    box.hidden = true;
  }
});
root.addEventListener("mousedown", function(ev) {
  var opt = ev.target.closest(".combo-list .opt");
  if (!opt) return;
  ev.preventDefault();
  comboPick(opt.closest(".combo").querySelector("input"), Number(opt.dataset.i));
});
root.addEventListener("focusout", function(ev) {
  var input = ev.target;
  if (!input.dataset || !input.dataset.combo || !W) return;
  var c = combos[input.dataset.combo];
  setTimeout(function() {
    if (!input.isConnected) return;
    input.nextElementSibling.hidden = true;
    if (!input.value.trim()) { setWizValue(c.key, ""); render(); return; }
    input.value = labelOf(c.options, getWizValue(c.key).split(":")[0]) ||
      labelOf(c.options, getWizValue(c.key));
  }, 150);
});

// sensor: first the device, then one of its number readings
var readingCache = {};
function sensorField(key, suggestion) {
  var cur = getWizValue(key), dev = cur.split(":")[0], rd = cur.split(":").slice(1).join(":");
  var options = withAll([]);
  var h = combo(key, options, dev, (suggestion || "").split(":")[0]);
  if (!dev) return h;
  var list = readingCache[dev];
  if (!list) { loadReadings(dev); return h + '<div class="muted">…</div>'; }
  if (!rd && list.length) { rd = list[0][0]; setWizValue(key, dev + ":" + rd); }
  h += '<label class="f">' + esc(L.reading) + '</label><select data-rd="' + esc(key) + '">';
  var found = !rd;
  list.forEach(function(r) {
    if (r[0] === rd) found = true;
    h += '<option value="' + esc(r[0]) + '"' + (r[0] === rd ? " selected" : "") + '>' + esc(r[0]) +
      (r[1] !== null && r[1] !== undefined ? " = " + esc(r[1]) : "") + '</option>';
  });
  if (!found) h += '<option value="' + esc(rd) + '" selected>' + esc(rd) + '</option>';
  return h + '</select>';
}
var loading = {};
function loadReadings(device) {
  if (loading[device]) return;
  loading[device] = true;
  FW_cmd(FW_root + "?cmd=" + encodeURIComponent("get " + DEV + " readings " + device) + "&XHR=1", function(r) {
    delete loading[device];
    var list = [];
    try { list = JSON.parse(r); } catch (e) { list = []; }
    readingCache[device] = list;
    var active = document.activeElement;
    if (!(active && root.contains(active) && /INPUT|SELECT/.test(active.tagName))) render();
  });
}
root.addEventListener("change", function(ev) {
  var el = ev.target;
  if (!W || !el.dataset) return;
  if (el.dataset.rd) {
    var key = el.dataset.rd, dev = getWizValue(key).split(":")[0];
    setWizValue(key, dev + ":" + el.value);
  } else if (el.dataset.wiz) {
    W.v[el.dataset.wiz] = el.type === "checkbox" ? (el.checked ? "1" : "0") : el.value;
    if (el.dataset.wiz === "pump_model") render();
  } else if (el.dataset.troom) {
    var t = (D.setup.thermostats || []).filter(function(x) { return x.name === el.dataset.troom; })[0];
    W.v.rooms[el.dataset.troom] = el.value.replace(/[,=]/g, " ").trim() || (t ? t.fhem_room : "");
    render();
  } else if (el.dataset.therm) {
    var off = W.v.exclude ? W.v.exclude.split(",") : [];
    off = off.filter(function(n) { return n !== el.dataset.therm; });
    if (!el.checked) off.push(el.dataset.therm);
    W.v.exclude = off.join(",");
    render();
  }
});
function field(label, body, hint) {
  return '<div class="wf"><label class="f">' + esc(label) + '</label>' + body +
    (hint ? '<div class="muted hint">' + esc(hint) + '</div>' : '') + '</div>';
}
function plainSelect(key, value, options) {
  var h = '<select data-wiz="' + key + '">', found = false;
  options.forEach(function(o) {
    if (o[0] === value) found = true;
    h += '<option value="' + esc(o[0]) + '"' + (o[0] === value ? " selected" : "") + '>' + esc(o[1]) + '</option>';
  });
  if (!found) h = h.replace('<select data-wiz="' + key + '">', '<select data-wiz="' + key + '"><option value="" selected></option>');
  return h + '</select>';
}
function stepBody(name) {
  var st = D.setup, v = W.v, h = "";
  if (name === "welcome") return '<p>' + esc(L.w_welcome) + '</p><p class="muted">' + esc(L.setup_hint) + '</p>';
  if (name === "source") {
    h += '<div class="srcs">';
    Object.keys(L.sources).forEach(function(k) {
      h += '<button class="src' + (v.heat_source === k ? " on" : "") + '" data-src="' + k + '">' +
        '<svg viewBox="-30 -30 60 60" width="54" height="54">' + SOURCE_ICONS[k] + '</svg><span>' +
        esc(L.sources[k]) + '</span></button>';
    });
    h += '</div>';
    return h + field(L.roles.supply_sensor, sensorField("supply_sensor", st.sensors.supply_sensor.suggestion), L.optional);
  }
  if (name === "mixer") {
    h += field(L.roles.mixer, combo("mixer", withAll(st.roles.mixer.options), v.mixer, st.roles.mixer.suggestion), L.w_mixer);
    return h + '<label class="chk"><input type="checkbox" data-wiz="mixer_invert"' + (v.mixer_invert === "1" ? " checked" : "") +
      '> ' + esc(L.w_invert) + '</label>';
  }
  if (name === "pump") {
    h += field(L.roles.pump, combo("pump", withAll(st.roles.pump.options), v.pump, st.roles.pump.suggestion), L.w_pump);
    h += field(L.pump_model, plainSelect("pump_model", v.pump_model,
      [["", L.unknown]].concat(st.pump_models.map(function(m) { return [m, m]; }))));
    var settings = (st.pump_settings_all || []).filter(function(s) {
      return s !== "AUTOADAPT" || (st.no_autoadapt || []).indexOf(v.pump_model) < 0;
    });
    h += field(L.pump_setting, plainSelect("pump_setting", v.pump_setting, [["", L.unknown]].concat(
      settings.map(function(s) { return [s, s]; }))));
    if (v.pump && v.pump.indexOf(":") < 0) {
      h += field(L.pump_power, '<input type="number" min="0" max="100" step="1" data-wiz="pump_power" value="' +
        esc(v.pump_power) + '" style="width:90px"> W', L.w_power);
    }
    return h;
  }
  if (name === "temps") {
    return field(L.roles.flow_sensor, sensorField("flow_sensor", st.sensors.flow_sensor.suggestion), L.w_flow) +
      field(L.roles.return_sensor, sensorField("return_sensor", st.sensors.return_sensor.suggestion), L.w_return);
  }
  if (name === "rooms") {
    var off = v.exclude ? v.exclude.split(","): [], names = {};
    var list = (st.thermostats || []).slice();
    if (!list.length) return '<p class="sugg">' + esc(L.no_rooms) + '</p>';
    list.forEach(function(t) { names[t.fhem_room] = 1; names[v.rooms[t.name] || t.room] = 1; });
    h += '<p class="muted">' + esc(L.w_rooms) + '</p><datalist id="fhcRoomNames">' +
      Object.keys(names).sort(function(a, b) { return a.localeCompare(b); }).map(function(n) { return '<option value="' + esc(n) + '">'; }).join("") + '</datalist>';
    h += '<div class="wtherm">';
    list.forEach(function(t) {
      var used = off.indexOf(t.name) < 0;
      h += '<div class="trow' + (used ? "" : " off") + '"><label class="chk"><input type="checkbox" data-therm="' + esc(t.name) + '"' +
        (used ? " checked" : "") + '> ' + esc(t.label) +
        (t.temp !== null && t.temp !== undefined ? ' <span class="muted">' + num(t.temp, 1, " °C") + '</span>' : '') +
        '</label><input type="text" list="fhcRoomNames" data-troom="' + esc(t.name) + '" value="' +
        esc(v.rooms[t.name] || t.room) + '" placeholder="' + esc(L.room) + '"' + (used ? "" : " disabled") + '></div>';
    });
    h += '</div>';
    var used = usedRooms();
    if (used.length) h += '<h4>' + esc(L.thermometer) + ' <span class="muted">(' + esc(L.optional) + ')</span></h4>';
    used.forEach(function(r) {
      if (v.thermometers[r[1]] === undefined) {
        v.thermometers[r[1]] = (st.thermometers[r[1]] || {}).suggestion || (st.room_thermometers || {})[r[0]] || "";
      }
      var sugg = (st.thermometers[r[1]] || {}).suggestion || (st.room_thermometers || {})[r[0]] || "";
      h += field(r[0], sensorField("therm_" + r[1], sugg), "");
    });
    return h;
  }
  if (name === "outdoor") {
    h += '<p>' + esc(L.weather) + ': ' + (st.weather.used ? '<b>' + esc(st.weather.used) + '</b>' :
      '<span class="sugg">' + esc(L.weather_none) + '</span>') + '</p>';
    return h + field(L.roles.outdoor_sensor, sensorField("outdoor_sensor", st.sensors.outdoor_sensor.suggestion), L.optional);
  }
  // done: summary and start
  var rows = [
    [L.supply, L.sources[v.heat_source] || v.heat_source],
    [L.mixer, labelOf(withAll(st.roles.mixer.options), v.mixer)],
    [L.pump, labelOf(withAll(st.roles.pump.options), v.pump)],
    [L.flow, v.flow_sensor], [L.ret, v.return_sensor],
    [L.rooms, usedRooms().map(function(r) { return r[0]; }).join(", ")],
    [L.thermostats, (st.thermostats || []).filter(function(t) {
      return (v.exclude ? v.exclude.split(",") : []).indexOf(t.name) < 0;
    }).map(function(t) { return t.label; }).join(", ")]
  ];
  h += '<table class="sum">' + rows.map(function(r) {
    return '<tr><td>' + esc(r[0]) + '</td><td><b>' + esc(r[1] || "–") + '</b></td></tr>';
  }).join("") + '</table>';
  if (D.mode !== "setup") return h;
  var missing = wizMissing();
  if (missing.length) return h + '<p class="sugg">' + esc(L.start_missing) + " " + esc(missing.join(", ")) + '</p>';
  return h + '<p><b>' + esc(L.start_ask) + '</b></p>';
}
function wizard() {
  var name = STEPS[W.step], n = STEPS.length - 1;
  var h = '<div class="card setup wiz"><div class="wsteps">';
  for (var i = 1; i <= n; i++) h += '<i class="' + (i < W.step ? "d" : i === W.step ? "c" : "") + '"></i>';
  h += '</div><div class="muted">' + (W.step ? esc(L.step + " " + W.step + " / " + n) : "") + '</div>';
  h += '<h3>' + esc(L["w_" + name + "_t"]) + '</h3>' + stepBody(name);
  if (W.err) h += '<p class="sugg err">' + esc(W.err) + '</p>';
  h += '<div class="row wnav">';
  if (W.step > 0) h += '<button data-wnav="back">' + esc(L.back) + '</button>';
  if (name === "welcome") h += '<button class="primary" data-wnav="next">' + esc(L.w_go) + '</button>';
  else if (name !== "done") h += '<button class="primary" data-wnav="next">' + esc(L.next) + '</button>';
  else if (D.mode === "setup") {
    h += '<button data-wnav="save">' + esc(L.save_only) + '</button>' +
      '<button class="primary" data-wnav="start"' + (wizMissing().length ? " disabled" : "") + '>' + esc(L.start) + '</button>';
  } else h += '<button class="primary" data-wnav="close">' + esc(L.finish) + '</button>';
  return h + '</div></div>';
}
// saved: the setup is stored, the control is started later
var saved = null;
function setup() {
  if (!D.setup) return "";
  if (D.mode === "setup" && !W) {
    if (saved === null) saved = !(D.setup.missing || []).length;
    if (!saved) wizStart(0);
  }
  if (W) return '<h3>' + L.setup_title + '</h3>' + wizard();
  if (D.mode === "setup") {
    var missing = savedMissing();
    return '<h3>' + L.setup_title + '</h3><div class="card setup wiz"><p><b>' + esc(L.saved) + '</b></p><p class="muted">' +
      esc(L.setup_hint) + '</p>' + (missing.length ? '<p class="sugg">' + esc(L.start_missing) + " " +
      esc(missing.join(", ")) + '</p>' : '') + '<div class="row wnav"><button data-setup="open">' + esc(L.change_setup) +
      '</button><button class="primary" data-wnav="start"' + (missing.length ? " disabled" : "") + '>' +
      esc(L.start) + '</button></div></div>' + roomOffer();
  }
  return '<h3><a href="#" data-setup="open">▸ ' + L.setup_title + '</a></h3>' + roomOffer();
}
function roomOffer() {
  if (D.control_room || window.FHC_ROOM) return "";
  return '<div class="row roomoffer"><button data-room="create">🏠 ' + esc(L.room_create) + '</button><span class="muted">' +
    esc(L.room_hint) + '</span></div>';
}
var lastMissing = null;
function savedMissing() { return lastMissing || (D.setup.missing || []); }
var REQUIRED = {mixer: ["mixer", "w_need_mixer"], pump: ["pump", "w_need_pump"], temps: ["flow_sensor", "w_need_flow"]};
function setupClick(btn) {
  if (btn.dataset.setup) { wizStart(1); render(); return; }
  if (btn.dataset.room) {
    set("create_room", function(r) {
      if (r && r.trim()) return;
      D.control_room = window.FHC_LANG === "de" ? "Heizungssteuerung" : "Heating";
      render();
    });
    return;
  }
  if (btn.dataset.wnav === "start") {
    btn.disabled = true;
    set("mode auto", function(r) {
      if (r && r.trim()) { btn.disabled = false; return; }
      D.mode = "auto"; D.state = ""; W = null; render();
      refreshLive();
    });
    return;
  }
  if (!W) return;
  if (btn.dataset.src) { W.v.heat_source = btn.dataset.src; render(); return; }
  var nav = btn.dataset.wnav, name = STEPS[W.step];
  if (!nav) return;
  W.err = "";
  if (nav === "back") { W.step = Math.max(0, W.step - 1); render(); return; }
  if (nav === "next") {
    var need = REQUIRED[name];
    if (need && !W.v[need[0]]) { W.err = L[need[1]]; render(); return; }
    wizSave(name);
    W.step = Math.min(STEPS.length - 1, W.step + 1);
    render();
    root.scrollIntoView({block: "start"});
    return;
  }
  if (nav === "save") { lastMissing = wizMissing(); saved = true; }
  if (nav === "close" || nav === "save") { W = null; render(); }
}

// --- page ---
function render() {
  root.className = "fhc" + (D.house && D.house.pump ? " running" : "");
  root.innerHTML = D.mode === "setup"
    ? top() + setup() + scheme()
    : top() + scheme() + rooms() + vacation() + charts() + curveChart() + setup();
  if (editing) {
    var card = root.querySelector('.room[data-room="' + editing.key + '"]');
    if (card) bindEditor(card);
  }
}

root.addEventListener("click", function(ev) {
  var btn = ev.target.closest("button, a[data-setup]");
  if (!btn || !root.contains(btn)) return;
  ev.preventDefault();
  var card = btn.closest(".room");
  if (card) return roomClick(btn, card);
  if (btn.dataset.mode) return set("mode " + btn.dataset.mode);
  if (btn.dataset.hours) { hours = Number(btn.dataset.hours); render(); return; }
  if (btn.dataset.vac || btn.dataset.vacday) return vacClick(btn);
  setupClick(btn);
});

// values come with fhcLive every 10 s, if they don't (e.g. a filter of
// FHEMWEB), the page asks for them
var lastLive = Date.now();
setInterval(function() {
  if (Date.now() - lastLive < 40000 || !document.body.contains(root)) return;
  refreshLive();
}, 30000);
function refreshLive() {
  lastLive = Date.now();
  FW_cmd(FW_root + "?cmd=" + encodeURIComponent("get " + DEV + " live") + "&XHR=1", function(r) {
    var data = null;
    try { data = JSON.parse(r); } catch (e) { data = null; }
    if (data) window.fhcLive(data);
  });
}
window.fhcLive = function(data) {
  if (!data || data.name !== DEV) return;
  lastLive = Date.now();
  var point = data.point;
  ["mode", "heat_source", "state", "house", "rooms", "vacation", "now", "control_room"].forEach(function(k) { if (k in data) D[k] = data[k]; });
  D.history = D.history || [];
  if (point && (!D.history.length || D.history[D.history.length - 1][0] < point[0])) D.history.push(point);
  if (D.curve && D.house) D.curve.current = [D.house.outdoor_eff, D.house.flow_target];
  // keep what is typed into the vacation and setup fields
  var active = document.activeElement;
  if (active && root.contains(active) && /INPUT|SELECT/.test(active.tagName)) return;
  // the assistant keeps its values itself, a new drawing doesn't lose them
  if (W && root.querySelector(".combo-list:not([hidden])")) return;
  if (dragging || vacOpen || Object.keys(pending).some(function(k) { return k !== "resize"; })) return;
  render();
};
var lastWidth = 0;
window.addEventListener("resize", function() {
  if (Math.abs(root.clientWidth - lastWidth) < 40 || dragging) return;
  lastWidth = root.clientWidth;
  later("resize", 300, render);
});
lastWidth = root.clientWidth;
render();
})();
