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
      gas: "Gastherme", oil: "Ölkessel", district: "Fernwärme", solar: "Solarthermie"}
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
      gas: "Gas boiler", oil: "Oil boiler", district: "District heating", solar: "Solar thermal"}
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
  var h = '<div class="top"><span class="pill ' + esc(s) + '">' + esc(text) + '</span>';
  h += '<span class="seg"><button data-mode="auto" class="' + (D.mode === "auto" ? "on" : "") + '">' +
    L.auto + '</button><button data-mode="off" class="' + (D.mode === "off" ? "on" : "") + '">' +
    L.mode_off + '</button></span>';
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

// --- setup ---
function select(id, value, options, suggestion) {
  var found = !value;
  var h = '<select id="' + id + '"><option value="">' + L.unused + '</option>';
  options.forEach(function(o) {
    var sel = o[0] === value || (!value && o[0] === suggestion);
    if (o[0] === value) found = true;
    h += '<option value="' + esc(o[0]) + '"' + (sel ? " selected" : "") + '>' + esc(o[1]) +
      (o[0] === suggestion ? " ★ " + L.suggestion : "") + '</option>';
  });
  if (!found) h += '<option value="' + esc(value) + '" selected>' + esc(value) + '</option>';
  return h + '</select>';
}
// sensor: first the device, then one of its number readings
var readingCache = null;
function readingsOf(device) {
  if (!readingCache) readingCache = {};
  return readingCache[device];
}
function sensorPicker(id, value, suggestion) {
  var current = value || suggestion || "";
  var device = current.split(":")[0], reading = current.split(":").slice(1).join(":");
  var st = D.setup;
  var h = '<select id="' + id + '_dev" data-sensor="' + id + '"><option value="">' + L.unused + '</option>';
  var found = !device;
  (st.devices || []).forEach(function(d) {
    if (d[0] === device) found = true;
    h += '<option value="' + esc(d[0]) + '"' + (d[0] === device ? " selected" : "") + '>' + esc(d[1]) + '</option>';
  });
  if (!found) h += '<option value="' + esc(device) + '" selected>' + esc(device) + '</option>';
  h += '</select> <select id="' + id + '_rd">' + readingOptions(device, reading) + '</select>';
  if (!value && suggestion) h += ' <span class="sugg">★ ' + L.suggestion + '</span>';
  return h;
}
function readingOptions(device, reading) {
  if (!device) return '<option value=""></option>';
  var list = readingsOf(device);
  if (!list) {
    loadReadings(device, reading);
    return '<option value="' + esc(reading) + '">' + esc(reading || "…") + '</option>';
  }
  var h = "", found = !reading;
  list.forEach(function(r) {
    if (r[0] === reading) found = true;
    h += '<option value="' + esc(r[0]) + '"' + (r[0] === reading ? " selected" : "") + '>' + esc(r[0]) +
      (r[1] !== null && r[1] !== undefined ? " = " + esc(r[1]) : "") + '</option>';
  });
  if (!found) h += '<option value="' + esc(reading) + '" selected>' + esc(reading) + '</option>';
  return h || '<option value="">–</option>';
}
var loading = {};
function loadReadings(device, reading) {
  if (loading[device]) return;
  loading[device] = true;
  FW_cmd(FW_root + "?cmd=" + encodeURIComponent("get " + DEV + " readings " + device) + "&XHR=1", function(r) {
    delete loading[device];
    var list = [];
    try { list = JSON.parse(r); } catch (e) { list = []; }
    readingsOf(device);
    readingCache[device] = list;
    root.querySelectorAll('select[data-sensor]').forEach(function(sel) {
      if (sel.value !== device) return;
      var rd = document.getElementById(sel.dataset.sensor + "_rd");
      rd.innerHTML = readingOptions(device, rd.value || reading);
    });
  });
}
var setupDirty = false;
root.addEventListener("change", function(ev) {
  var sel = ev.target;
  if (sel.closest && sel.closest(".setup")) setupDirty = true;
  if (!sel.dataset || !sel.dataset.sensor) return;
  var rd = document.getElementById(sel.dataset.sensor + "_rd");
  rd.innerHTML = readingOptions(sel.value, "");
});
function sensorValue(id) {
  var dev = document.getElementById(id + "_dev"), rd = document.getElementById(id + "_rd");
  if (!dev || !dev.value) return "";
  return rd && rd.value ? dev.value + ":" + rd.value : dev.value;
}
var setupOpen = null;
function setup() {
  var st = D.setup;
  if (!st) return "";
  if (setupOpen === null) setupOpen = st.missing && st.missing.length > 0;
  var h = '<h3><a href="#" data-setup="toggle">' + (setupOpen ? "▾ " : "▸ ") + L.setup_title + '</a></h3>';
  if (!setupOpen) return h;
  h += '<div class="card setup">';
  if (st.missing && st.missing.length) h += '<div class="sugg">' + L.setup_missing + " " + esc(st.missing.join(", ")) + '</div>';
  h += '<table>';
  Object.keys(L.roles).forEach(function(attr) {
    var control;
    if (st.sensors && st.sensors[attr]) {
      control = sensorPicker("fhcA_" + attr, st.sensors[attr].value, st.sensors[attr].suggestion);
    } else {
      var r = st.roles[attr] || {value: "", options: []};
      control = select("fhcA_" + attr, r.value, r.options, r.suggestion);
    }
    h += '<tr><td>' + L.roles[attr] + '</td><td>' + control +
      '</td><td><button data-attr="' + attr + '">' + L.apply + '</button></td></tr>';
  });
  h += '<tr><td>' + L.source_type + '</td><td>' + select("fhcA_heat_source", D.heat_source,
    Object.keys(L.sources).map(function(k) { return [k, L.sources[k]]; }), "") +
    '</td><td><button data-attr="heat_source">' + L.apply + '</button></td></tr>';
  h += '<tr><td>' + L.pump_model + '</td><td>' + select("fhcA_pump_model", st.pump_model,
    st.pump_models.map(function(m) { return [m, m]; }), "") + '</td><td><button data-attr="pump_model">' + L.apply + '</button></td></tr>';
  h += '<tr><td>' + L.pump_setting + '</td><td>' + select("fhcA_pump_setting", st.pump_setting,
    st.pump_settings.map(function(m) { return [m, m]; }), "") + '</td><td><button data-attr="pump_setting">' + L.apply + '</button></td></tr>';
  h += '<tr><td>' + L.pump_power + '</td><td><input id="fhcA_pump_power" type="number" min="0" max="100" step="1" value="' +
    esc(st.pump_power) + '" style="width:80px"></td><td><button data-attr="pump_power">' + L.apply + '</button></td></tr>';
  h += '<tr><td>' + L.weather + '</td><td colspan="2">' + (st.weather.used ? esc(st.weather.used) : '<span class="muted">' +
    L.weather_none + '</span>') + '</td></tr>';
  (D.rooms || []).forEach(function(room) {
    var t = st.thermometers[room.key] || {value: "", suggestion: ""};
    h += '<tr><td>' + L.thermometer + ": " + esc(room.name) + '</td><td>' +
      sensorPicker("fhcT_" + room.key, t.value, t.suggestion) + '</td><td><button data-therm="1">' + L.apply + '</button></td></tr>';
  });
  return h + '</table></div>';
}
function attrCmd(attr, value) {
  send(value ? "attr " + DEV + " " + attr + " " + value : "deleteattr " + DEV + " " + attr);
}
function setupClick(btn) {
  if (btn.dataset.setup) { setupOpen = !setupOpen; render(); return; }
  if (btn.dataset.attr) {
    var attr = btn.dataset.attr, el = document.getElementById("fhcA_" + attr);
    var value = el ? el.value.trim() : sensorValue("fhcA_" + attr);
    if (attr === "pump_model") value = value.replace(/ /g, "_");
    setupDirty = false;
    attrCmd(attr, value);
  } else if (btn.dataset.therm) {
    var parts = [];
    (D.rooms || []).forEach(function(room) {
      var value = sensorValue("fhcT_" + room.key);
      if (value) parts.push(room.key + "=" + value);
    });
    setupDirty = false;
    attrCmd("thermometers", parts.join(","));
  }
}

// --- page ---
function render() {
  root.className = "fhc" + (D.house && D.house.pump ? " running" : "");
  root.innerHTML = top() + scheme() + rooms() + vacation() + charts() + curveChart() + setup();
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

window.fhcLive = function(data) {
  if (!data || data.name !== DEV) return;
  var point = data.point;
  ["mode", "heat_source", "state", "house", "rooms", "vacation", "now"].forEach(function(k) { if (k in data) D[k] = data[k]; });
  D.history = D.history || [];
  if (point && (!D.history.length || D.history[D.history.length - 1][0] < point[0])) D.history.push(point);
  if (D.curve && D.house) D.curve.current = [D.house.outdoor_eff, D.house.flow_target];
  // keep what is typed into the vacation and setup fields
  var active = document.activeElement;
  if (active && root.contains(active) && /INPUT|SELECT/.test(active.tagName)) return;
  if (setupDirty && setupOpen) return;
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
