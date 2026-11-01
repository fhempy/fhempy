/* fhempy tablet dashboard. Plain JavaScript, no build step, runs on old
   iPads too. The server (dashboard.py) sends rooms, tiles and the header,
   live changes come over the WebSocket. */
(function () {
  "use strict";

  // ---------- texts ----------
  var DE = {
    home: "Zuhause", history: "Verlauf", settings: "Einstellungen",
    on: "An", off: "Aus", open: "Offen", closed: "Zu", tilted: "Gekippt",
    locked: "Verriegelt", unlocked: "Entriegelt", motion: "Bewegung", nomotion: "Ruhig",
    target: "Ziel", heating: "Heizt", sinceMin: "seit {n} min", sinceH: "seit {n} h",
    sinceD: "seit {n} Tagen", openNames: "Offen: {names}", openCount: "{n} Fenster offen",
    doorsOpen: "{n} offen", battery: "Batterie leer", batteriesTitle: "Batterien tauschen", batteriesLead: "Diese Geräte melden eine schwache Batterie.", batteriesOk: "Alle Batterien sind in Ordnung.", batteryLow: "schwach", allOff: "Alles aus",
    allOffN: "Alles aus ({n})", beforeLeave: "Bevor du gehst", stillOpen: "Das ist noch offen oder an.",
    allClosed: "Alles zu, alles aus.", nowOn: "Gerade offen und an", lightsOn: "{n} Lichter an",
    lightOn: "1 Licht an", deviceOn: "1 Gerät an", devicesOn: "{n} Geräte an", humidity: "Luftfeuchte", atHome: "{n} zu Hause", nobody: "Niemand zu Hause",
    pairTitle: "Tablet verbinden", pairText: "Öffne in FHEM das Gerät des Dashboards und scanne den QR-Code mit der Kamera dieses Tablets. Oder gib den Code ein, der dort steht.",
    pairButton: "Verbinden", pairWrong: "Der Code stimmt nicht oder ist abgelaufen. Lade die Seite in FHEM neu für einen neuen Code.",
    whereTitle: "Wo steht dieses Tablet?", whereText: "Wir haben {rooms} Räume und {tiles} Geräte gefunden. Wähle den Platz, den Rest machen wir.",
    wall: "An der Wand", couch: "Bei der Couch", door: "Bei der Tür",
    wallList: ["Immer an, Bildschirmschoner mit Uhr", "Startet mit dem ganzen Zuhause", "Wacht auf bei Bewegung im Raum", "Warnungen groß oben"],
    couchList: ["Startet im eigenen Raum", "Licht, Szenen, Rollläden zuerst", "Kein Bildschirmschoner", "Tagsüber hell, abends dunkel"],
    doorList: ["Klingel übernimmt den Bildschirm", "Kamera, Sprechen, Tür öffnen", "Beim Gehen: was noch offen ist", "Alles aus mit einem Tipp"],
    roomOfTablet: "Raum für dieses Tablet:", next: "Fertig", noRoom: "Kein Raum",
    connLost: "Verbindung weg, versuche neu …", readonly: "Dieses Tablet darf nur anzeigen.",
    pullToDim: "Ziehen zum Dimmen", pullToMove: "Ziehen zum Bewegen", up: "Auf", down: "Zu", stop: "Stopp",
    lock: "Verriegeln", unlock: "Entriegeln", today: "Heute", min: "min.", max: "max.", targetTemp: "Soll", times: "{n}× an", total: "zusammen {t}",
    noTimeline: "Lege ein Timeline-Gerät an (Install modules), dann siehst du hier, was passiert ist.",
    noDevices: "Hier ist noch nichts. Gib deinen Geräten in FHEM einen Raum (Attribut room).",
    happened: "Gerade passiert", ringing: "Es klingelt", ringingAt: "Es klingelt: {name}",
    talk: "Sprechen", mute: "Stumm", unmute: "Ton an", hangup: "Beenden", slideOpen: "Zum Öffnen schieben →",
    opened: "Tür geöffnet", view: "Ansehen", needHttps: "Sprechen geht nur über https, siehe Einstellungen.",
    noMic: "Kein Zugriff aufs Mikrofon.", noCamera: "Keine Kamera eingerichtet", camConnecting: "Kamera wird verbunden …",
    name: "Name", place: "Standort", room: "Raum", theme: "Design", auto: "Automatisch", dark: "Dunkel", light: "Hell",
    rooms: "Räume", editTiles: "Kacheln bearbeiten", editDone: "Bearbeiten beenden", reset: "Zurücksetzen",
    switchHttps: "Zu https wechseln (für Sprechen)", energy: "Energie", solar: "Solar", usage: "Verbrauch",
    grid: "Netz", storage: "Speicher", price: "Preis", surplus: "Überschuss", fromGrid: "Netzbezug",
    hiddenTiles: "Ausgeblendet, + zum Zurückholen", days: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
    months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    weekdays: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
    away: "Abwesend", quiet: "Keine Ereignisse an diesem Tag.", lastDays: "Tage", climate: "Klima", temperature: "Temperatur",
    now: "jetzt", wasOn: "Wann war es an"
  };
  var EN = {
    home: "Home", history: "History", settings: "Settings",
    on: "On", off: "Off", open: "Open", closed: "Closed", tilted: "Tilted",
    locked: "Locked", unlocked: "Unlocked", motion: "Motion", nomotion: "Clear",
    target: "Target", heating: "Heating", sinceMin: "for {n} min", sinceH: "for {n} h",
    sinceD: "for {n} days", openNames: "Open: {names}", openCount: "{n} windows open",
    doorsOpen: "{n} open", battery: "Battery low", batteriesTitle: "Replace batteries", batteriesLead: "These devices report a weak battery.", batteriesOk: "All batteries are fine.", batteryLow: "weak", allOff: "All off",
    allOffN: "All off ({n})", beforeLeave: "Before you leave", stillOpen: "Still open or on.",
    allClosed: "Everything closed and off.", nowOn: "Open and on right now", lightsOn: "{n} lights on", deviceOn: "1 device on", devicesOn: "{n} devices on", humidity: "Humidity", temperature: "Temperature",
    lightOn: "1 light on", atHome: "{n} at home", nobody: "Nobody at home",
    pairTitle: "Connect tablet", pairText: "Open the dashboard device in FHEM and scan the QR code with the camera of this tablet, or enter the code shown there.",
    pairButton: "Connect", pairWrong: "Wrong or expired code. Reload the page in FHEM for a new code.",
    whereTitle: "Where is this tablet?", whereText: "We found {rooms} rooms and {tiles} devices. Choose the place, we do the rest.",
    wall: "On the wall", couch: "At the couch", door: "At the door",
    wallList: ["Always on, screensaver with clock", "Starts with the whole home", "Wakes up on motion in the room", "Warnings big at the top"],
    couchList: ["Starts in its own room", "Lights, scenes, blinds first", "No screensaver", "Bright by day, dark at night"],
    doorList: ["Doorbell takes over the screen", "Camera, talk, open the door", "When leaving: what is still open", "All off with one tap"],
    roomOfTablet: "Room of this tablet:", next: "Done", noRoom: "No room",
    connLost: "Connection lost, retrying …", readonly: "This tablet may only show.",
    pullToDim: "Drag to dim", pullToMove: "Drag to move", up: "Up", down: "Down", stop: "Stop",
    lock: "Lock", unlock: "Unlock", today: "Today", min: "min", max: "max", targetTemp: "target", times: "{n}× on", total: "{t} in total",
    noTimeline: "Create a timeline device (Install modules) to see what happened here.",
    noDevices: "Nothing here yet. Give your devices a room in FHEM (attribute room).",
    happened: "Just happened", ringing: "Somebody rings", ringingAt: "Somebody rings: {name}",
    talk: "Talk", mute: "Mute", unmute: "Sound on", hangup: "End", slideOpen: "Slide to open →",
    opened: "Door opened", view: "View", needHttps: "Talking needs https, see settings.",
    noMic: "No access to the microphone.", noCamera: "No camera set up", camConnecting: "Connecting camera …",
    name: "Name", place: "Place", room: "Room", theme: "Design", auto: "Automatic", dark: "Dark", light: "Light",
    rooms: "Rooms", editTiles: "Edit tiles", editDone: "Done editing", reset: "Reset",
    switchHttps: "Switch to https (for talking)", energy: "Energy", solar: "Solar", usage: "Usage",
    grid: "Grid", storage: "Battery", price: "Price", surplus: "Surplus", fromGrid: "From grid",
    hiddenTiles: "Hidden, + brings them back", days: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    away: "Away", quiet: "Nothing happened on this day.", lastDays: "days", climate: "Climate",
    now: "now", wasOn: "When it was on"
  };
  var T = /^de/i.test(navigator.language || "de") ? DE : EN;
  var GERMAN = T === DE;
  function t(key, vars) {
    var s = T[key] !== undefined ? T[key] : key;
    if (vars) { Object.keys(vars).forEach(function (k) { s = String(s).split("{" + k + "}").join(vars[k]); }); }
    return s;
  }

  // ---------- icons ----------
  var P = {
    bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    plug: '<path d="M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0zM12 17v5"/>',
    blind: '<path d="M4 3h16M5 3v11M19 3v11M5 7h14M5 11h14M5 14h14M12 14v4"/><circle cx="12" cy="19.5" r="1.5"/>',
    thermo: '<path d="M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0z"/>',
    win: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M12 3v18M4 12h16"/>',
    door: '<path d="M5 21V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v17M3 21h18"/><circle cx="15" cy="12" r="1"/>',
    bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    cloud: '<path d="M7 18h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.3 1.5A3.3 3.3 0 0 0 7 18z"/>',
    rain: '<path d="M7 15h10a4 4 0 0 0 .5-8 6 6 0 0 0-11.3 1.5A3.3 3.3 0 0 0 7 15zM8 19l-1 2M12 19l-1 2M16 19l-1 2"/>',
    power: '<path d="M12 3v9M6.3 6.3a8 8 0 1 0 11.4 0"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    key: '<circle cx="8" cy="15" r="4"/><path d="m11 12 9-9M17 6l3 3M15 8l2 2"/>',
    mute: '<path d="M11 5 6 9H3v6h3l5 4V5zM22 9l-6 6M16 9l6 6"/>',
    speaker: '<path d="M11 5 6 9H3v6h3l5 4V5zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>',
    x: '<path d="M6 6l12 12M18 6 6 18"/>',
    drop: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    sofa: '<path d="M4 11V8a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v3M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2v-5zM5 18v2M19 18v2"/>',
    frame: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 18h8"/>',
    bell: '<path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    unlock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 7.5-2"/>',
    home: '<path d="M3 11 12 4l9 7M5 10v10h14V10"/>',
    walk: '<circle cx="13" cy="4" r="2"/><path d="M9 21l2-6 3 3v3M11 15l1-5 3 3h3M8 10l3-2"/>',
    chev: '<path d="M9 6l6 6-6 6"/>',
    battery: '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2M6 11v2"/>',
    film: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    timer: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M10 2h4"/>',
    left: '<path d="M15 6l-6 6 6 6"/>', right: '<path d="M9 6l6 6-6 6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', check: '<path d="M5 12l5 5 9-10"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'
  };
  function I(name, size) {
    return '<svg class="i" viewBox="0 0 24 24"' + (size ? ' style="width:' + size + 'px;height:' + size + 'px"' : "") + ">" + (P[name] || "") + "</svg>";
  }
  function esc(s) {
    return String(s === undefined || s === null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(v, digits) {
    if (v === null || v === undefined || isNaN(v)) { return "–"; }
    var s = Number(v).toFixed(digits === undefined ? 1 : digits);
    return GERMAN ? s.replace(".", ",") : s;
  }
  function watt(w) {
    if (w === null || w === undefined) { return "–"; }
    return Math.abs(w) >= 1000 ? num(w / 1000, 1) + " kW" : Math.round(w) + " W";
  }

  // ---------- storage ----------
  function store(key, value) {
    try {
      if (value === undefined) { return localStorage.getItem(key); }
      if (value === null) { localStorage.removeItem(key); } else { localStorage.setItem(key, value); }
    } catch (e) { /* private mode */ }
    return null;
  }
  function hashParams() {
    var out = {};
    (location.hash || "").replace(/^#/, "").split("&").forEach(function (p) {
      var kv = p.split("=");
      if (kv[0]) { out[kv[0]] = decodeURIComponent(kv[1] || ""); }
    });
    return out;
  }

  // ---------- state ----------
  var S = {
    token: null, tablet: null, rooms: [], tiles: {}, scenes: [], header: {},
    tab: null, sheet: null, edit: false, ws: null, connected: false, retry: 0,
    lastTouch: Date.now(), saver: false, ring: null, pending: {}, timeline: {},
    history: null, historyDay: null, usage: {}, banner: null, now: new Date()
  };
  try { S.usage = JSON.parse(store("dashUsage") || "{}") || {}; } catch (e) { S.usage = {}; }
  var app = document.getElementById("app");

  // ---------- connection ----------
  function wsUrl() { return (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/api/ws"; }

  function connect() {
    if (!S.token) { return; }
    var ws;
    try { ws = new WebSocket(wsUrl()); } catch (e) { reconnect(); return; }
    S.ws = ws;
    ws.onopen = function () { ws.send(JSON.stringify({ type: "hello", token: S.token })); };
    ws.onmessage = function (ev) {
      var m;
      try { m = JSON.parse(ev.data); } catch (e) { return; }
      handle(m);
    };
    ws.onclose = function () {
      if (S.ws !== ws) { return; }
      S.connected = false; S.ws = null;
      setTimeout(function () { if (!S.connected) { render(); } }, 3000);
      reconnect();
    };
  }
  function reconnect() {
    S.retry = Math.min(S.retry + 1, 6);
    setTimeout(connect, Math.min(15000, 500 * Math.pow(2, S.retry)));
  }
  function send(m) { if (S.ws && S.connected) { S.ws.send(JSON.stringify(m)); return true; } return false; }

  function handle(m) {
    if (m.type === "unknown") {
      store("dashToken", null); S.token = null; S.ws = null;
      if (location.hash.indexOf("t=") >= 0) { history.replaceState(null, "", location.pathname); }
      render(); return;
    }
    if (m.type === "welcome" || m.type === "model") {
      if (m.tablet) { S.tablet = m.tablet; }
      S.rooms = m.rooms; S.tiles = m.tiles; S.scenes = m.scenes; S.header = m.header || {};
      S.pending = {};
      if (m.type === "welcome") { S.connected = true; S.retry = 0; if (!S.tab) { S.tab = startTab(); } wakeLock(); }
      render(); return;
    }
    if (m.type === "tablet") { S.tablet = m.tablet; applyTheme(); render(); return; }
    if (m.type === "tile") {
      S.tiles[m.tile.id] = m.tile; delete S.pending[m.tile.id];
      updateTile(m.tile.id); if (S.sheet && S.sheet.id === m.tile.id) { renderSheet(); }
      return;
    }
    if (m.type === "header") { S.header = m.header; renderHeader(); if (S.sheet && S.sheet.batteries) { renderBatteries(); } if (S.tab === "home") { renderContent(); } if (S.saver) { renderSaver(); } return; }
    if (m.type === "motion") {
      if (S.tablet && S.tablet.room && m.rooms.indexOf(S.tablet.room) >= 0) { wake(); }
      return;
    }
    if (m.type === "push") { showBanner(m.text, place() === "wall" ? 30 * 60000 : 10000); wake(); return; }
    if (m.type === "ring") { startRing(m); }
  }

  // ---------- helpers ----------
  function place() { return (S.tablet && S.tablet.place) || "wall"; }
  function layout() { return (S.tablet && S.tablet.layout) || {}; }
  function startTab() {
    if (place() === "couch" && S.tablet.room && roomByName(S.tablet.room)) { return "room:" + S.tablet.room; }
    return "home";
  }
  function roomByName(name) { for (var i = 0; i < S.rooms.length; i++) { if (S.rooms[i].name === name) { return S.rooms[i]; } } return null; }
  function visibleRooms() {
    var lay = layout(), hidden = lay.hidden_rooms || [], order = lay.room_order || [];
    var rooms = S.rooms.filter(function (r) { return hidden.indexOf(r.name) < 0; });
    rooms.sort(function (a, b) {
      var ia = order.indexOf(a.name), ib = order.indexOf(b.name);
      if (ia < 0) { ia = 1000 + S.rooms.indexOf(a); }
      if (ib < 0) { ib = 1000 + S.rooms.indexOf(b); }
      return ia - ib;
    });
    if (S.tablet && S.tablet.room) {
      var own = rooms.filter(function (r) { return r.name === S.tablet.room; });
      if (own.length && order.length === 0) { rooms = own.concat(rooms.filter(function (r) { return r.name !== S.tablet.room; })); }
    }
    return rooms;
  }
  function roomTiles(room, withHidden) {
    var lay = layout(), hidden = lay.hidden_tiles || [], manual = (lay.tile_order || {})[room.name];
    var ids = room.tiles.filter(function (id) { return S.tiles[id] && (withHidden || hidden.indexOf(id) < 0); });
    if (manual && manual.length) {
      ids.sort(function (a, b) {
        var ia = manual.indexOf(a), ib = manual.indexOf(b);
        return (ia < 0 ? 999 : ia) - (ib < 0 ? 999 : ib);
      });
    } else {
      // tiles used often move to the front (learned on this tablet)
      var base = room.tiles;
      ids.sort(function (a, b) {
        var ua = bucket(S.usage[a]), ub = bucket(S.usage[b]);
        return ub - ua || base.indexOf(a) - base.indexOf(b);
      });
    }
    return ids;
  }
  function bucket(n) { return n >= 5 ? Math.floor(Math.log(n) / Math.log(3)) : 0; }
  function used(id) {
    S.usage[id] = (S.usage[id] || 0) + 1;
    store("dashUsage", JSON.stringify(S.usage));
  }
  function since(text) {
    if (!text) { return ""; }
    var d = parseTime(text); if (!d) { return ""; }
    var min = Math.max(0, Math.round((Date.now() - d.getTime()) / 60000));
    if (min < 90) { return t("sinceMin", { n: Math.max(1, min) }); }
    if (min < 48 * 60) { return t("sinceH", { n: Math.round(min / 60) }); }
    return t("sinceD", { n: Math.round(min / 1440) });
  }
  function parseTime(text) {
    var m = /^(\d{4})-(\d\d)-(\d\d)[ T](\d\d):(\d\d):?(\d\d)?/.exec(text || "");
    return m ? new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) : null;
  }
  function two(n) { return (n < 10 ? "0" : "") + n; }
  function clockText(d) { return two(d.getHours()) + ":" + two(d.getMinutes()); }
  function dateText(d) {
    return GERMAN ? T.weekdays[d.getDay()] + ", " + d.getDate() + ". " + T.months[d.getMonth()]
      : T.weekdays[d.getDay()] + ", " + T.months[d.getMonth()] + " " + d.getDate();
  }
  function isNight() {
    var h = new Date().getHours();
    return h >= 22 || h < 6;
  }
  function isDay() {
    var sun = S.header.sun, now = new Date(), hm = two(now.getHours()) + ":" + two(now.getMinutes());
    if (sun && sun.rise && sun.set) { return hm >= sun.rise && hm < sun.set; }
    return now.getHours() >= 7 && now.getHours() < 19;
  }

  // ---------- tiles ----------
  var KIND_ICON = { light: "bulb", dimmer: "bulb", switch: "power", outlet: "plug", blind: "blind", thermostat: "thermo", lock: "lock", contact: "win", motion: "walk", temperature: "thermo", humidity: "drop" };
  var TAP_TOGGLES = { light: 1, dimmer: 1, switch: 1, outlet: 1, blind: 1 };

  function tileLook(tile) {
    var st = tile.state || {}, k = tile.kind, cls = "", sub = "", icon = KIND_ICON[k] || "power", bar = null;
    if (k === "light" || k === "dimmer") {
      if (st.on) { cls = "light"; sub = t("on") + (st.level !== undefined && k === "dimmer" ? " · " + st.level + " %" : ""); bar = k === "dimmer" ? st.level : null; } else { sub = t("off"); }
    } else if (k === "switch" || k === "outlet") {
      if (st.on) { cls = "power"; sub = t("on") + (st.power ? " · " + watt(st.power) : ""); } else { sub = t("off"); }
    } else if (k === "blind") {
      cls = "blind";
      var p = st.position;
      sub = p === undefined ? "–" : p >= 99 ? t("open") : p <= 1 ? t("closed") : t("open") + " " + p + " %";
    } else if (k === "thermostat") {
      var heat = st.target !== undefined && st.current !== undefined && st.target > st.current + 0.3;
      cls = heat ? "heat" : "cool";
      sub = (st.current !== undefined ? num(st.current) + "° · " : "") + t("target") + " " + num(st.target) + "°";
    } else if (k === "lock") {
      cls = st.locked ? "locked" : "warn"; icon = st.locked ? "lock" : "unlock";
      sub = st.locked ? t("locked") : st.locked === false ? t("unlocked") : "–";
    } else if (k === "contact") {
      icon = tile.door ? "door" : "win";
      if (st.closed === false) { cls = "warn"; sub = (st.tilted ? t("tilted") : t("open")) + " " + since(st.since); } else { sub = st.closed ? t("closed") : "–"; }
    } else if (k === "motion") {
      if (st.occupied) { cls = "move"; sub = t("motion"); } else { sub = t("nomotion"); }
    } else if (k === "temperature") {
      sub = num(st.temperature) + "°" + (st.humidity !== undefined ? " · " + Math.round(st.humidity) + " %" : "");
    } else if (k === "humidity") {
      sub = Math.round(st.humidity) + " %";
    }
    return { cls: cls, sub: sub, icon: icon, bar: bar };
  }

  function tileHtml(id, editState) {
    var tile = S.tiles[id]; if (!tile) { return ""; }
    var look = tileLook(tile), wide = tile.kind === "thermostat";
    var body;
    if (tile.kind === "thermostat") {
      body = '<div class="ic">' + I(look.icon) + '</div><div><div class="n">' + esc(tile.name) + '</div><div class="thermo"><span class="big">' + num(tile.state.target) + '°</span></div><div class="s">' +
        (tile.state.current !== undefined ? num(tile.state.current) + "°" : "") + (tile.state.humidity !== undefined ? " · " + Math.round(tile.state.humidity) + " %" : "") + "</div></div>" +
        (editState ? "" : '<div class="tsteps"><span class="round" data-step="-1" data-sid="' + esc(id) + '">−</span><span class="round" data-step="1" data-sid="' + esc(id) + '">+</span></div>');
    } else {
      body = '<div class="ic">' + I(look.icon) + '</div><div><div class="n">' + esc(tile.name) + '</div><div class="s">' + esc(look.sub) + "</div></div>";
    }
    var extra = "";
    if (look.bar !== null && look.bar !== undefined) { extra += '<div class="bar" style="width:' + look.bar + '%"></div>'; }
    if (tile.state.battery_low && !editState) { extra += '<div class="badge">' + I("battery", 18) + "</div>"; }
    if (editState) {
      extra += '<div class="edit" data-edit="' + (editState === "hidden" ? "show" : "hide") + '">' + I(editState === "hidden" ? "plus" : "x") + "</div>";
    }
    return '<button class="tile ' + look.cls + (wide ? " wide" : "") + (S.pending[id] ? " pending" : "") + (editState === "hidden" ? " hiddenTile" : "") +
      '" data-tile="' + esc(id) + '">' + body + extra + "</button>";
  }

  function updateTile(id) {
    var el = app.querySelector('[data-tile="' + cssEsc(id) + '"]');
    if (el) {
      var div = document.createElement("div");
      div.innerHTML = tileHtml(id, S.edit ? editStateOf(id) : null);
      if (div.firstChild) { el.parentNode.replaceChild(div.firstChild, el); }
    }
    if (S.tab === "home") { renderContent(); }
  }
  function cssEsc(s) { return String(s).replace(/["\\]/g, "\\$&"); }
  function editStateOf(id) { return (layout().hidden_tiles || []).indexOf(id) >= 0 ? "hidden" : "shown"; }

  // optimistic: show the new state at once, the server confirms within 3 s
  function act(id, action, value, optimistic) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var tile = S.tiles[id];
    if (tile && optimistic) {
      var before = JSON.parse(JSON.stringify(tile.state));
      Object.keys(optimistic).forEach(function (k) { tile.state[k] = optimistic[k]; });
      S.pending[id] = setTimeout(function () {
        if (S.pending[id]) { tile.state = before; delete S.pending[id]; updateTile(id); if (S.sheet && S.sheet.id === id) { renderSheet(); } }
      }, 4000);
      updateTile(id);
    }
    send({ type: "action", id: id, action: action, value: value });
    used(id);
  }

  function tap(id) {
    var tile = S.tiles[id]; if (!tile) { return; }
    if (!TAP_TOGGLES[tile.kind]) { openSheet(id); return; }
    var st = tile.state;
    if (tile.kind === "blind") {
      var target = (st.position || 0) > 0 ? 0 : 100;
      act(id, "position", target, { position: target });
    } else {
      act(id, "toggle", null, { on: !st.on });
    }
  }

  // ---------- rendering ----------
  function render() {
    applyTheme();
    if (!S.token) { renderPair(); return; }
    if (!S.tablet) { app.innerHTML = '<div class="ob"><div class="empty">' + (S.connected ? "" : t("connLost")) + "</div></div>"; return; }
    if (!S.tablet.place) { renderSetup(); return; }
    if (!S.tab || (S.tab.indexOf("room:") === 0 && !roomByName(S.tab.slice(5)))) { S.tab = startTab(); }
    // drawing everything again must not jump back to the top
    var old = document.getElementById("content"), top = old ? old.scrollTop : 0, shownTab = S.shownTab;
    app.innerHTML = '<div id="hdr"></div><div id="tabs" class="tabs"></div><div id="content" class="content"></div>' +
      (S.connected ? "" : '<div class="banner">' + esc(t("connLost")) + "</div>");
    renderHeader(); renderTabs(); renderContent();
    if (shownTab === S.tab) { document.getElementById("content").scrollTop = top; }
    if (S.sheet) { renderSheet(); }
    if (S.saver) { renderSaver(); }
    if (S.ring) { renderRing(); }
  }

  function renderHeader() {
    var el = document.getElementById("hdr"); if (!el) { return; }
    var h = S.header || {}, now = new Date(), chips = "";
    if (h.weather && h.weather.temperature !== null && h.weather.temperature !== undefined) {
      chips += '<div class="chip">' + I(weatherIcon(h.weather.condition)) + " " + num(h.weather.temperature, 0) + '° <span class="sub">' + esc(h.weather.condition || "") +
        (h.weather.high !== null && h.weather.high !== undefined ? " · " + num(h.weather.low, 0) + "° / " + num(h.weather.high, 0) + "°" : "") + "</span></div>";
    }
    if (h.presence) {
      var home = h.presence.home || [];
      var avs = home.slice(0, 4).map(function (p, i) { return '<div class="av" style="background:' + ["#FFB547", "#5AA9FF", "#3DDBB8", "#9B8CFF"][i % 4] + '">' + esc(p.initial) + "</div>"; }).join("");
      chips += '<div class="chip">' + (avs ? '<div class="avs">' + avs + "</div>" : I("home")) + ' <span class="lbl">' + esc(home.length ? t("atHome", { n: home.length }) : t("nobody")) + "</span></div>";
    }
    var warn = warningText();
    if (warn) { chips += '<button class="chip warn" data-go="home">' + I("win") + " " + esc(warn) + "</button>"; }
    if ((h.battery || []).length) { chips += '<button class="chip warn" data-batteries="1" aria-label="' + esc(t("batteriesTitle")) + '">' + I("battery") + " " + h.battery.length + "</button>"; }
    chips += '<button class="iconbtn" data-settings="1">' + I("gear") + "</button>";
    el.innerHTML = '<div class="top"><div><div class="clock">' + clockText(now) + '</div><div class="date">' + esc(dateText(now)) + '</div></div><div class="chips">' + chips + "</div></div>";
  }
  function warningText() {
    var open = (S.header && S.header.open) || [];
    if (!open.length) { return ""; }
    if (open.length <= 3) { return t("openNames", { names: open.map(function (o) { return shortName(o.name); }).join(", ") }); }
    return t("openCount", { n: open.length });
  }
  // "Fenster Garten" -> "Garten" in the chip, when the rest is unique
  function shortName(name) {
    var s = String(name).replace(/^(fenster|window|tür|door|kontakt|contact)[\s_-]+/i, "");
    return s || name;
  }
  function weatherIcon(cond) {
    cond = String(cond || "").toLowerCase();
    if (/regen|rain|schauer|shower|drizzle|niesel|gewitter|thunder/.test(cond)) { return "rain"; }
    if (/klar|sonn|clear|sunny/.test(cond)) { return isDay() ? "sun" : "moon"; }
    return "cloud";
  }

  function renderTabs() {
    var el = document.getElementById("tabs"); if (!el) { return; }
    var tabs = [{ id: "home", name: t("home") }];
    visibleRooms().forEach(function (r) {
      var openHere = (S.header.open || []).some(function (o) { return o.room === r.name; });
      tabs.push({ id: "room:" + r.name, name: r.name, dot: openHere });
    });
    if (S.header.timeline) { tabs.push({ id: "history", name: t("history") }); }
    el.innerHTML = tabs.map(function (tb) {
      return '<button class="tab' + (tb.id === S.tab ? " on" : "") + '" data-tab="' + esc(tb.id) + '">' + esc(tb.name) + (tb.dot ? '<span class="dot"></span>' : "") + "</button>";
    }).join("");
    var on = el.querySelector(".tab.on"); if (on && on.scrollIntoView) { on.scrollIntoView({ inline: "nearest", block: "nearest" }); }
  }

  function renderContent() {
    var el = document.getElementById("content"); if (!el) { return; }
    var top = el.scrollTop;
    if (S.tab === "home") { el.innerHTML = homeHtml(); } else if (S.tab === "history") { el.innerHTML = historyHtml(); } else { el.innerHTML = roomHtml(roomByName(S.tab.slice(5))); }
    el.scrollTop = top;
    S.shownTab = S.tab;
  }

  function leaveHtml() {
    var h = S.header, open = h.open || [], running = h.running || [], rows = "";
    open.forEach(function (o) {
      rows += '<div class="row"><div class="ic" style="background:rgba(255,138,61,.16);color:var(--amber2)">' + I(o.door ? "door" : "win") + '</div><div class="t"><b>' + esc(o.name) + "</b><span>" +
        esc([o.room, (o.tilted ? t("tilted") : t("open")) + " " + since(o.since)].filter(Boolean).join(" · ")) + "</span></div></div>";
    });
    var lights = running.filter(function (r) { return r.kind === "light" || r.kind === "dimmer"; });
    if (lights.length) {
      var rooms = []; lights.forEach(function (l) { if (l.room && rooms.indexOf(l.room) < 0) { rooms.push(l.room); } });
      rows += '<div class="row"><div class="ic" style="background:rgba(255,181,71,.16);color:var(--amber)">' + I("bulb") + '</div><div class="t"><b>' +
        esc(lights.length === 1 ? lights[0].name : t("lightsOn", { n: lights.length })) + "</b><span>" + esc(rooms.join(", ")) + "</span></div></div>";
    }
    running.filter(function (r) { return r.kind !== "light" && r.kind !== "dimmer"; }).forEach(function (r) {
      rows += '<div class="row"><div class="ic" style="background:rgba(155,140,255,.16);color:var(--violet)">' + I("bolt") + '</div><div class="t"><b>' + esc(r.name) + "</b><span>" +
        esc([r.room, t("on") + (r.power ? " · " + watt(r.power) : "")].filter(Boolean).join(" · ")) + '</span></div><button class="pill" data-off="' + esc(r.id) + '">' + esc(t("off")) + "</button></div>";
    });
    var door = place() === "door";
    var title = door ? t("beforeLeave") : t("nowOn");
    if (!rows) {
      return '<div class="leave"><h2>' + esc(title) + '</h2><div class="allclear">' + I("check", 26) + " " + esc(t("allClosed")) + "</div></div>";
    }
    var count = running.length;
    return '<div class="leave"><h2>' + esc(title) + "</h2>" + (door ? '<div class="lead">' + esc(t("stillOpen")) + "</div>" : "") + rows +
      (count ? '<div class="actions"><button class="pill primary" data-alloff="">' + I("power", 20) + " " + esc(t("allOffN", { n: count })) + "</button></div>" : "") + "</div>";
  }

  function energyHtml() {
    var e = S.header.energy; if (!e) { return ""; }
    var parts = [];
    if (e.solar !== undefined) { parts.push([watt(e.solar), t("solar")]); }
    if (e.load !== undefined) { parts.push([watt(e.load), t("usage")]); }
    if (e.grid !== undefined) { parts.push([watt(Math.abs(e.grid)), e.grid < 0 ? t("surplus") : t("fromGrid")]); }
    if (e.battery !== undefined) { parts.push([Math.round(e.battery) + " %", t("storage")]); }
    if (e.price !== undefined) { parts.push([num(e.price * 100, 1) + " ct", t("price")]); }
    var surplus = e.solar !== undefined && e.load !== undefined && e.solar > e.load;
    return '<div class="leave"><div class="section" style="margin:0 0 12px"><span>' + esc(t("energy")) + "</span>" + (surplus ? '<span style="color:var(--green);text-transform:none;letter-spacing:0">' + esc(t("surplus")) + "</span>" : "") +
      '</div><div class="facts2">' + parts.map(function (p) { return '<div class="fact2"><b>' + esc(p[0]) + "</b><span>" + esc(p[1]) + "</span></div>"; }).join("") + "</div></div>";
  }

  function roomCardHtml(room) {
    var ids = roomTiles(room), lights = 0, temp = null, open = 0, other = 0;
    ids.forEach(function (id) {
      var tile = S.tiles[id], st = tile.state;
      if ((tile.kind === "light" || tile.kind === "dimmer") && st.on) { lights++; } else if ((tile.kind === "switch" || tile.kind === "outlet") && st.on) { other++; }
      if (temp === null && tile.kind === "thermostat" && st.current !== undefined) { temp = st.current; }
      if (temp === null && tile.kind === "temperature" && st.temperature !== undefined) { temp = st.temperature; }
      if (tile.kind === "contact" && st.closed === false) { open++; }
    });
    var facts = "";
    if (temp !== null) { facts += '<span class="fact">' + num(temp) + "°</span>"; }
    if (lights) { facts += '<span class="fact on">' + esc(lights === 1 ? t("lightOn") : t("lightsOn", { n: lights })) + "</span>"; }
    if (other) { facts += '<span class="fact on">' + esc(other === 1 ? t("deviceOn") : t("devicesOn", { n: other })) + "</span>"; }
    if (open) { facts += '<span class="fact warn">' + esc(t("doorsOpen", { n: open })) + "</span>"; }
    return '<button class="tile roomcard' + (lights ? " light" : "") + '" data-tab="room:' + esc(room.name) + '"><div class="n">' + esc(room.name) + '</div><div class="facts">' + facts + "</div></button>";
  }

  function homeHtml() {
    var rooms = visibleRooms();
    if (!rooms.length) { return '<div class="empty">' + esc(t("noDevices")) + "</div>"; }
    var left = leaveHtml() + energyHtml();
    var right = '<div class="grid">' + rooms.map(roomCardHtml).join("") + "</div>";
    return '<div class="home split"><div style="display:flex;flex-direction:column;gap:16px">' + left + "</div><div>" + right + "</div></div>";
  }

  function scenesHtml(room) {
    var scenes = S.scenes.filter(function (s) { return s.room === room.name; });
    var on = roomTiles(room).filter(function (id) { var tl = S.tiles[id]; return ["light", "dimmer", "switch", "outlet"].indexOf(tl.kind) >= 0 && tl.state.on; }).length;
    var html = scenes.map(function (s) { return '<button class="scene" data-scene="' + esc(s.id) + '">' + I(/film|kino|movie|tv/i.test(s.name) ? "film" : /nacht|night/i.test(s.name) ? "moon" : "sun") + " " + esc(s.name) + "</button>"; }).join("");
    if (on) { html += '<button class="scene" data-alloff="' + esc(room.name) + '">' + I("power") + " " + esc(t("allOffN", { n: on })) + "</button>"; }
    return html ? '<div class="scenes">' + html + "</div>" : "";
  }

  function roomHtml(room) {
    if (!room) { return ""; }
    var html = scenesHtml(room);
    var ids = roomTiles(room, S.edit);
    if (S.edit) {
      var hidden = layout().hidden_tiles || [];
      var shown = ids.filter(function (id) { return hidden.indexOf(id) < 0; });
      var gone = ids.filter(function (id) { return hidden.indexOf(id) >= 0; });
      html += '<div class="grid">' + shown.map(function (id) { return tileHtml(id, "shown"); }).join("") + "</div>";
      if (gone.length) { html += '<div class="section">' + esc(t("hiddenTiles")) + '</div><div class="grid">' + gone.map(function (id) { return tileHtml(id, "hidden"); }).join("") + "</div>"; }
      html += '<div class="actions"><button class="pill primary" data-editdone="1">' + I("check", 20) + " " + esc(t("editDone")) + "</button></div>";
      return html;
    }
    html += '<div class="grid">' + ids.map(function (id) { return tileHtml(id); }).join("") + "</div>";
    html += happenedHtml(room.name);
    return html;
  }

  // ---------- timeline ----------
  function api(path) {
    return fetch(path, { headers: { Authorization: "Bearer " + S.token } }).then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.json(); });
  }
  function today() { var d = new Date(); return d.getFullYear() + "-" + two(d.getMonth() + 1) + "-" + two(d.getDate()); }
  function loadDay(day, force) {
    var cached = S.timeline[day];
    if (cached && !force && (cached.loading || Date.now() - cached.at < 60000)) { return; }
    S.timeline[day] = { loading: true, at: Date.now(), data: cached && cached.data };
    api("api/timeline?day=" + day).then(function (data) {
      S.timeline[day] = { at: Date.now(), data: data };
      if (S.tab === "history" || S.tab.indexOf("room:") === 0) { renderContent(); }
    }).catch(function () { S.timeline[day] = { at: Date.now(), data: null }; });
  }
  function entryTime(e) { var d = new Date(e.ts * 1000); return clockText(d); }
  function entryColor(e) {
    return { security: "#FF8A3D", alert: "#FF5A5F", presence: "#34D399", light: "#FFB547", climate: "#5AA9FF", energy: "#9B8CFF", device: "#9B8CFF" }[e.category] || "#8C95A5";
  }
  function happenedHtml(roomName) {
    if (!S.header.timeline) { return ""; }
    var day = today(); loadDay(day);
    var data = S.timeline[day] && S.timeline[day].data; if (!data || !data.entries) { return ""; }
    var list = data.entries.filter(function (e) { return ("," + (e.room || "") + ",").indexOf("," + roomName + ",") >= 0; }).slice(-6).reverse();
    if (!list.length) { return ""; }
    return '<div class="section">' + esc(t("happened")) + '</div><div class="leave" style="padding:10px 22px">' + list.map(function (e) {
      return '<div class="row" style="padding:10px 0"><span style="color:var(--mu);width:46px;font-variant-numeric:tabular-nums">' + entryTime(e) + '</span><span style="width:9px;height:9px;border-radius:50%;background:' + entryColor(e) + '"></span><div class="t"><span style="color:var(--tx);font-size:15px">' + esc(e.text) + "</span></div></div>";
    }).join("") + "</div>";
  }

  function historyHtml() {
    if (!S.header.timeline) { return '<div class="empty">' + esc(t("noTimeline")) + "</div>"; }
    var day = S.historyDay || today(); loadDay(day);
    var chips = "", d = new Date();
    for (var i = 6; i >= 0; i--) {
      var x = new Date(d.getFullYear(), d.getMonth(), d.getDate() - i);
      var id = x.getFullYear() + "-" + two(x.getMonth() + 1) + "-" + two(x.getDate());
      chips += '<button class="tab' + (id === day ? " on" : "") + '" data-day="' + id + '">' + esc(i === 0 ? t("today") : T.days[x.getDay()] + " " + x.getDate() + ".") + "</button>";
    }
    var entry = S.timeline[day], data = entry && entry.data;
    var html = '<div class="scenes">' + chips + "</div>";
    if (!data) { return html + '<div class="empty">…</div>'; }
    var periods = (data.periods || []).slice(-2).map(function (p) { return '<span class="fact">' + esc(t("away")) + " " + esc(p.start.slice(8, 10) + "." + p.start.slice(5, 7) + ". – " + p.end.slice(8, 10) + "." + p.end.slice(5, 7) + ".") + "</span>"; }).join(" ");
    var entries = (data.entries || []).slice().reverse();
    var list = entries.length ? entries.map(function (e) {
      var sub = e.children ? e.children.map(function (c) { return c.short || c.text; }).slice(0, 4).join(", ") : (e.end ? clockText(new Date(e.ts * 1000)) + " – " + clockText(new Date(e.end * 1000)) : "");
      return '<div class="row"><span style="color:var(--mu);width:52px;text-align:right;font-variant-numeric:tabular-nums">' + entryTime(e) + '</span><div class="ic" style="background:' + entryColor(e) + '26;color:' + entryColor(e) + '">' + I(categoryIcon(e)) +
        '</div><div class="t"><b style="font-size:16px;font-weight:500">' + esc(e.text) + (e.count > 1 ? " · " + e.count + "×" : "") + "</b><span>" + esc(sub) + "</span></div>" + (e.room ? '<span class="fact">' + esc(String(e.room).split(",")[0]) + "</span>" : "") + "</div>";
    }).join("") : '<div class="empty">' + esc(t("quiet")) + "</div>";
    var trends = (data.trends || []).slice(0, 6).map(trendHtml).join("");
    return html + (periods ? '<div style="margin-bottom:12px">' + periods + "</div>" : "") +
      '<div class="home split"><div class="leave" style="padding:6px 22px">' + list + '</div><div style="display:flex;flex-direction:column;gap:14px">' + trends + "</div></div>";
  }
  function categoryIcon(e) {
    return { security: "door", presence: "home", light: "bulb", climate: "thermo", energy: "bolt", alert: "bell" }[e.category] || "clock";
  }
  function trendHtml(tr) {
    var pts = (tr.points || []).map(function (p) { return p === null || p === undefined ? null : (typeof p === "object" ? p[1] : p); });
    var vals = pts.filter(function (v) { return v !== null && !isNaN(v); });
    if (vals.length < 2) { return ""; }
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals); if (hi - lo < 1) { hi = lo + 1; }
    var w = 360, h = 80, path = "", n = pts.length;
    pts.forEach(function (v, i) { if (v === null) { return; } path += (path ? "L" : "M") + (i / (n - 1) * w).toFixed(1) + "," + (h - (v - lo) / (hi - lo) * h).toFixed(1); });
    var col = tr.category === "energy" ? "#9B8CFF" : "#FF8A3D", last = vals[vals.length - 1];
    return '<div class="leave" style="padding:16px 20px"><div class="section" style="margin:0 0 10px"><span>' + esc(tr.text) + '</span><span style="text-transform:none;letter-spacing:0;color:var(--tx)">' + esc(num(last) + (tr.unit ? " " + tr.unit : "")) + "</span></div>" +
      '<svg viewBox="0 0 ' + w + " " + (h + 4) + '" style="width:100%;height:84px" preserveAspectRatio="none"><path d="' + path + '" fill="none" stroke="' + col + '" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg></div>';
  }

  // ---------- details sheet ----------
  function openSheet(id) { S.sheet = { id: id }; renderSheet(); loadHistory(id); }
  function closeSheet() { S.sheet = null; var d = document.getElementById("sheet"); if (d) { d.parentNode.removeChild(d); } }
  function loadHistory(id) {
    if (!S.header.timeline) { return; }
    api("api/history?id=" + encodeURIComponent(id)).then(function (data) {
      if (S.sheet && S.sheet.id === id) { S.sheet.history = data; renderSheet(); }
    }).catch(function () { /* no history */ });
  }
  function sheetShell(inner, cls) {
    var d = document.getElementById("sheet");
    if (!d) { d = document.createElement("div"); d.id = "sheet"; d.className = "dim"; document.body.appendChild(d); }
    var old = d.firstChild, top = old ? old.scrollTop : 0, key = JSON.stringify([S.sheet && S.sheet.id, S.sheet && S.sheet.settings, S.sheet && S.sheet.batteries]);
    d.innerHTML = '<div class="sheet ' + (cls || "") + '">' + inner + "</div>";
    if (d.getAttribute("data-key") === key) { d.firstChild.scrollTop = top; }
    d.setAttribute("data-key", key);
    return d;
  }
  function renderSheet() {
    if (!S.sheet) { return; }
    if (S.sheet.settings) { renderSettings(); return; }
    if (S.sheet.batteries) { renderBatteries(); return; }
    var tile = S.tiles[S.sheet.id]; if (!tile) { closeSheet(); return; }
    var st = tile.state, k = tile.kind, look = tileLook(tile);
    var head = '<div class="head"><div><h1>' + esc(tile.name) + '</h1><div class="subtitle">' + esc([tile.rooms[0], look.sub].filter(Boolean).join(" · ")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>";
    var left = "", body = "";
    if (k === "dimmer" || k === "blind") {
      var value = k === "dimmer" ? (st.on ? (st.level || 0) : 0) : (st.position || 0);
      left = '<div><div class="vs' + (k === "blind" ? " teal" : "") + '" data-slider="' + (k === "dimmer" ? "level" : "position") + '"><div class="f" style="height:' + value + '%"></div><div class="k" style="bottom:' + value + '%"></div><div class="lbl">' + value + ' %</div></div><div class="hint">' + esc(k === "dimmer" ? t("pullToDim") : t("pullToMove")) + "</div></div>";
    }
    if (k === "light" || k === "dimmer" || k === "switch" || k === "outlet") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.on ? " on" : "") + '" data-do="on">' + I("power", 20) + " " + esc(t("on")) + '</button><button class="pill' + (!st.on ? " on" : "") + '" data-do="off">' + esc(t("off")) + "</button></div></div>";
      if (st.power) { body += '<div class="group"><div class="facts2"><div class="fact2"><b>' + watt(st.power) + "</b><span>" + esc(t("usage")) + "</span></div></div></div>"; }
    } else if (k === "blind") {
      body += '<div class="group"><div class="actions"><button class="pill" data-do="up">' + esc(t("up")) + "</button>" + (tile.stop ? '<button class="pill" data-do="stop">' + esc(t("stop")) + "</button>" : "") + '<button class="pill" data-do="down">' + esc(t("down")) + "</button></div></div>";
    } else if (k === "thermostat") {
      body += '<div class="target"><button class="round" data-step="-1">−</button><div class="val">' + num(st.target) + '°</div><button class="round" data-step="1">+</button></div>';
      body += '<div class="facts2">' + (st.current !== undefined ? '<div class="fact2"><b>' + num(st.current) + "°</b><span>" + esc(t("room")) + "</span></div>" : "") + (st.humidity !== undefined ? '<div class="fact2"><b>' + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span></div>" : "") + "</div>";
    } else if (k === "lock") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.locked ? " on" : "") + '" data-do="lock">' + I("lock", 20) + " " + esc(t("lock")) + '</button><button class="pill danger" data-do="unlock">' + I("unlock", 20) + " " + esc(t("unlock")) + "</button></div></div>";
    } else if (k === "temperature" || k === "humidity") {
      body += '<div class="group facts2">' + (st.temperature !== undefined ? '<div class="fact2"><b>' + num(st.temperature) + "°</b><span>" + esc(t("temperature")) + "</span></div>" : "") + (st.humidity !== undefined ? '<div class="fact2"><b>' + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span></div>" : "") + "</div>";
    }
    body += sheetTrendsHtml() + sheetHistoryHtml();
    var cols = !!left;
    sheetShell(cols ? left + "<div>" + head + body + "</div>" : head + body, cols ? "cols" : "");
  }
  function sheetHistoryHtml() {
    var hist = S.sheet && S.sheet.history; if (!hist || !hist.activity) { return ""; }
    var act = hist.activity[0]; if (!act || !act.segments) { return ""; }
    var start = hist.to - 86400, span = 86400, bars = "";
    act.segments.forEach(function (s) {
      var a = Math.max(0, (s[0] - start) / span * 100), b = Math.min(100, ((s[1] || Date.now() / 1000) - start) / span * 100);
      if (b > a) { bars += '<div style="position:absolute;top:0;bottom:0;left:' + a + "%;width:" + Math.max(0.6, b - a) + '%;background:linear-gradient(180deg,#FFC266,#FF8A3D);border-radius:3px"></div>'; }
    });
    return '<div class="group"><div class="label" style="display:flex;justify-content:space-between"><span>' + esc(t("today")) + '</span><span style="text-transform:none;letter-spacing:0">' + esc(act.text || "") + "</span></div>" +
      '<div style="position:relative;height:34px;border-radius:8px;background:rgba(255,255,255,.05);overflow:hidden">' + bars + '</div><div style="display:flex;justify-content:space-between;color:var(--mu2);font-size:12px;margin-top:6px"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div></div>';
  }

  // temperature and humidity of today in the details of a device
  function sheetTrendsHtml() {
    var hist = S.sheet && S.sheet.history; if (!hist || !hist.trends || !hist.to) { return ""; }
    return hist.trends.filter(function (tr) { return /temp|humid|dewpoint/i.test(tr.reading || ""); }).slice(0, 2)
      .map(function (tr) { return sheetTrendHtml(tr, hist.to - 86400); }).join("");
  }
  function trendValues(points) {
    return (points || []).filter(function (p) { return p && p[1] !== null && !isNaN(p[1]); });
  }
  function sheetTrendHtml(tr, start) {
    var pts = trendValues(tr.points), target = tr.target ? trendValues(tr.target.points) : [];
    if (pts.length < 2) { return ""; }
    var all = pts.concat(target).map(function (p) { return p[1]; });
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all), pad = Math.max(0.5, (hi - lo) * 0.15);
    lo -= pad; hi += pad;
    var w = 480, h = 120;
    function x(ts) { return (Math.max(0, Math.min(1, (ts + 1800 - start) / 86400)) * w).toFixed(1); }
    function y(v) { return (h - (v - lo) / (hi - lo) * h).toFixed(1); }
    function line(list, step) {
      return list.map(function (p, i) {
        var xy = x(p[0]) + "," + y(p[1]);
        return i === 0 ? "M" + xy : (step ? "H" + x(p[0]) + "V" + y(p[1]) : "L" + xy);
      }).join("");
    }
    var humid = /humid/i.test(tr.reading), col = humid ? "#5AC8FA" : "#FF8A3D", gid = "g" + String(tr.reading).replace(/\W/g, "");
    var path = line(pts), area = path + "L" + x(pts[pts.length - 1][0]) + "," + h + "L" + x(pts[0][0]) + "," + h + "Z";
    var fmt = humid ? Math.round : num;
    var vals = pts.map(function (p) { return p[1]; }), last = vals[vals.length - 1], unit = tr.unit || (humid ? "%" : "");
    var info = esc(t("min") + " " + fmt(Math.min.apply(null, vals)) + " · " + t("max") + " " + fmt(Math.max.apply(null, vals)));
    var svg = '<svg viewBox="0 0 ' + w + " " + (h + 2) + '" style="width:100%;height:120px;display:block" preserveAspectRatio="none">' +
      '<defs><linearGradient id="' + gid + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + col + '" stop-opacity=".35"/><stop offset="1" stop-color="' + col + '" stop-opacity="0"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#' + gid + ')"/>' +
      (target.length ? '<path d="' + line(target, true) + '" fill="none" stroke="var(--mu)" stroke-width="1.5" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/>' : "") +
      '<path d="' + path + '" fill="none" stroke="' + col + '" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>';
    if (target.length) { info += " · - - " + esc(t("targetTemp")); }
    return '<div class="group"><div class="label" style="display:flex;justify-content:space-between"><span>' + esc(tr.name || tr.reading) + " · " + esc(t("today")) +
      '</span><span style="text-transform:none;letter-spacing:0;color:var(--tx)">' + esc(fmt(last) + (unit ? " " + unit : "")) + "</span></div>" + svg +
      '<div style="display:flex;justify-content:space-between;color:var(--mu2);font-size:12px;margin-top:6px"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>' +
      '<div class="hint" style="text-align:left;margin-top:4px">' + info + "</div></div>";
  }

  // dragging the big slider of dimmers and blinds
  function sliderDrag(el, ev) {
    var kind = el.getAttribute("data-slider"), id = S.sheet.id, value = 0;
    function move(e) {
      var r = el.getBoundingClientRect(), y = (e.touches ? e.touches[0].clientY : e.clientY);
      value = Math.round(Math.max(0, Math.min(100, (r.bottom - y) / r.height * 100)));
      el.querySelector(".f").style.height = value + "%"; el.querySelector(".k").style.bottom = value + "%"; el.querySelector(".lbl").textContent = value + " %";
      e.preventDefault();
    }
    function up() {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      if (kind === "level") { act(id, "level", value, value > 0 ? { on: true, level: value } : { on: false }); } else { act(id, "position", value, { position: value }); }
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
    move(ev);
  }

  // ---------- settings ----------
  function openBatteries() { S.sheet = { batteries: true }; renderBatteries(); }
  function renderBatteries() {
    var list = (S.header && S.header.battery) || [];
    var rows = list.map(function (b) {
      var level = b.level !== null && b.level !== undefined && b.level > 1 ? Math.round(b.level) + " %" : t("batteryLow");
      var tile = S.tiles[b.id];
      return '<div class="row' + (tile ? " tap" : "") + '"' + (tile ? ' data-batt="' + esc(b.id) + '"' : "") + '><div class="ic" style="background:rgba(255,138,61,.16);color:var(--amber2)">' + I("battery") + '</div><div class="t"><b>' + esc(b.name) + "</b><span>" +
        esc([b.room, level, since(b.since)].filter(Boolean).join(" · ")) + "</span></div>" + (tile ? I("chev") : "") + "</div>";
    }).join("");
    sheetShell('<div class="head"><div><h1>' + esc(t("batteriesTitle")) + '</h1><div class="subtitle">' + esc(list.length ? t("batteriesLead") : t("batteriesOk")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      (rows ? '<div class="blist">' + rows + "</div>" : '<div class="allclear">' + I("check", 26) + " " + esc(t("batteriesOk")) + "</div>"));
  }
  function openSettings() { S.sheet = { settings: true }; renderSettings(); }
  function renderSettings() {
    var tb = S.tablet, lay = layout(), hidden = lay.hidden_rooms || [];
    var places = ["wall", "couch", "door"].map(function (p) { return '<button class="' + (tb.place === p ? "on" : "") + '" data-place="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var themes = ["auto", "dark", "light"].map(function (p) { return '<button class="' + ((lay.theme || "auto") === p ? "on" : "") + '" data-theme="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var roomOpts = '<option value="">' + esc(t("noRoom")) + "</option>" + S.rooms.map(function (r) { return '<option' + (r.name === tb.room ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    var order = allRoomsOrdered();
    var roomList = order.map(function (r, i) {
      var on = hidden.indexOf(r.name) < 0;
      return '<div class="item"><span class="grow">' + esc(r.name) + '</span><button class="mini" data-roomup="' + i + '">' + I("left", 18).replace("<svg", '<svg style="transform:rotate(90deg)"') + '</button><button class="mini" data-roomdown="' + i + '">' + I("left", 18).replace("<svg", '<svg style="transform:rotate(-90deg)"') + '</button><button class="tg' + (on ? "" : " off") + '" data-roomtoggle="' + esc(r.name) + '"></button></div>';
    }).join("");
    var https = tb.https && location.protocol !== "https:" ? '<div class="group"><a class="pill" style="text-decoration:none" href="' + esc(tb.https) + "#t=" + encodeURIComponent(S.token) + '">' + esc(t("switchHttps")) + "</a></div>" : "";
    sheetShell('<div class="head"><div><h1>' + esc(t("settings")) + '</h1><div class="subtitle">' + esc(tb.name) + (tb.readonly ? " · " + esc(t("readonly")) : "") + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="group"><div class="label">' + esc(t("name")) + '</div><input id="tabname" value="' + esc(tb.name) + '" maxlength="40"></div>' +
      '<div class="group"><div class="label">' + esc(t("place")) + '</div><div class="seg">' + places + "</div></div>" +
      '<div class="group"><div class="label">' + esc(t("room")) + '</div><select id="tabroom">' + roomOpts + "</select></div>" +
      '<div class="group"><div class="label">' + esc(t("theme")) + '</div><div class="seg">' + themes + "</div></div>" +
      '<div class="group"><div class="label">' + esc(t("rooms")) + '</div><div class="list">' + roomList + "</div></div>" +
      '<div class="group actions"><button class="pill primary" data-edit="1">' + esc(t("editTiles")) + '</button><button class="pill" data-resetlayout="1">' + esc(t("reset")) + "</button></div>" + https);
  }
  function allRoomsOrdered() {
    var order = layout().room_order || [];
    var rooms = S.rooms.slice();
    rooms.sort(function (a, b) {
      var ia = order.indexOf(a.name), ib = order.indexOf(b.name);
      return (ia < 0 ? 1000 + S.rooms.indexOf(a) : ia) - (ib < 0 ? 1000 + S.rooms.indexOf(b) : ib);
    });
    return rooms;
  }
  function saveLayout(lay) {
    S.tablet.layout = lay;
    send({ type: "layout", layout: lay });
    renderTabs(); renderContent(); applyTheme();
    if (S.sheet && S.sheet.settings) { renderSettings(); }
  }
  function copyLayout() { return JSON.parse(JSON.stringify(layout())); }

  // ---------- pairing and setup ----------
  function renderPair(error) {
    app.innerHTML = '<div class="ob"><div class="obbox"><div class="logo"><div class="m"></div>' + esc(t("home")) + "</div><h1>" + esc(t("pairTitle")) + '</h1><p class="l">' + esc(t("pairText")) +
      '</p><div class="code"><input id="code" inputmode="numeric" maxlength="6" autocomplete="one-time-code" placeholder="000000"><button class="pill primary" data-pair="1" style="height:64px;padding:0 28px">' + esc(t("pairButton")) + "</button></div>" +
      (error ? '<div class="err">' + esc(t("pairWrong")) + "</div>" : "") + "</div></div>";
  }
  function pair(code) {
    var device = /iPad/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1) ? "iPad" : /Android/.test(navigator.userAgent) ? "Android" : "Browser";
    fetch("api/pair", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code: String(code).trim(), device: device }) })
      .then(function (r) { if (!r.ok) { throw new Error("code"); } return r.json(); })
      .then(function (data) {
        S.token = data.token; S.tablet = data.tablet; store("dashToken", data.token);
        // the token in the address survives "Add to Home Screen" on iOS
        history.replaceState(null, "", location.pathname + "#t=" + encodeURIComponent(data.token));
        connect(); render();
      })
      .catch(function () { history.replaceState(null, "", location.pathname); renderPair(true); });
  }
  function renderSetup() {
    var tb = S.tablet, chosen = S.setupPlace || "wall";
    var suggested = S.setupRoom !== undefined ? S.setupRoom : (S.rooms[0] ? S.rooms[0].name : "");
    if (S.rooms.length) { S.setupRoom = suggested; }
    var cards = [["wall", "frame"], ["couch", "sofa"], ["door", "bell"]].map(function (p) {
      return '<button class="pl' + (chosen === p[0] ? " on" : "") + '" data-setupplace="' + p[0] + '"><div class="pi">' + I(p[1]) + "</div><h3>" + esc(t(p[0])) + "</h3><ul>" + T[p[0] + "List"].map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></button>";
    }).join("");
    var roomOpts = '<option value="">' + esc(t("noRoom")) + "</option>" + S.rooms.map(function (r) { return "<option" + (r.name === suggested ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    app.innerHTML = '<div class="ob"><div class="obbox"><div class="logo"><div class="m"></div>' + esc(t("home")) + "</div><h1>" + esc(t("whereTitle")) + '</h1><p class="l">' +
      esc(t("whereText", { rooms: S.rooms.length, tiles: Object.keys(S.tiles).length })) + '</p><div class="places">' + cards + '</div><div class="found">' + I("home") + " " + esc(t("roomOfTablet")) +
      ' <select id="setuproom">' + roomOpts + '</select><button class="pill primary" data-setupdone="1">' + esc(t("next")) + "</button></div></div></div>";
    if (!tb) { return; }
  }

  // ---------- screensaver, idle, wake ----------
  function idleCheck() {
    var idle = (Date.now() - S.lastTouch) / 1000;
    if (S.ring || !S.tablet || !S.tablet.place) { return; }
    if (idle > 120 && (S.sheet || S.edit || S.tab !== startTab())) {
      closeSheet(); S.edit = false; S.tab = startTab(); S.historyDay = null; renderTabs(); renderContent();
    }
    if (idle > 300 && place() !== "couch" && !S.saver) { S.saver = true; renderSaver(); }
  }
  function wake() {
    S.lastTouch = Date.now();
    if (S.saver) { S.saver = false; var el = document.getElementById("saver"); if (el) { el.parentNode.removeChild(el); } }
  }
  function renderSaver() {
    if (!S.saver) { return; }
    var el = document.getElementById("saver");
    if (!el) { el = document.createElement("div"); el.id = "saver"; el.className = "ss"; document.body.appendChild(el); }
    var now = new Date(), h = S.header || {}, w = h.weather, items = "";
    if (h.presence) { items += '<div class="x">' + I("home", 20) + " " + esc((h.presence.home || []).length ? t("atHome", { n: h.presence.home.length }) : t("nobody")) + "</div>"; }
    var inside = insideTemp(); if (inside !== null) { items += '<div class="x">' + I("thermo", 20) + " " + num(inside) + "°</div>"; }
    var open = h.open || [];
    if (open.length) { items += '<div class="x o">' + I("win", 20) + " " + esc(open.length <= 3 ? open.map(function (o) { return o.name; }).join(", ") + " " + t("open").toLowerCase() : t("openCount", { n: open.length })) + "</div>"; }
    else { items += '<div class="x">' + I("lock", 20) + " " + esc(t("allClosed")) + "</div>"; }
    if (h.energy && h.energy.solar) { items += '<div class="x" style="margin-left:auto">' + I("bolt", 20) + " " + watt(h.energy.solar) + " " + esc(t("solar")) + "</div>"; }
    var shift = (now.getMinutes() % 5) * 6 - 12;
    el.className = "ss" + (isNight() ? " night" : "");
    el.innerHTML = '<div class="wrap" style="transform:translate(' + shift + "px," + (-shift) + 'px)"><div class="t">' + clockText(now) + '</div><div class="d">' + esc(dateText(now)) + "</div>" +
      (w && w.temperature !== null && w.temperature !== undefined ? '<div class="w"><b>' + num(w.temperature, 0) + "°</b><span>" + esc(w.condition || "") + "</span>" + (w.high !== null && w.high !== undefined ? "<span>" + num(w.low, 0) + "° / " + num(w.high, 0) + "°</span>" : "") + "</div>" : "") +
      '<div class="b">' + items + "</div></div>";
  }
  function insideTemp() {
    var room = S.tablet && S.tablet.room, best = null;
    Object.keys(S.tiles).forEach(function (id) {
      var tile = S.tiles[id];
      if (best !== null && tile.rooms.indexOf(room) < 0) { return; }
      var v = tile.kind === "thermostat" ? tile.state.current : tile.kind === "temperature" ? tile.state.temperature : undefined;
      if (v !== undefined && (best === null || tile.rooms.indexOf(room) >= 0)) { best = v; }
    });
    return best;
  }
  var lock = null;
  function wakeLock() {
    if (place() === "couch" || !navigator.wakeLock || lock) { return; }
    navigator.wakeLock.request("screen").then(function (l) { lock = l; l.addEventListener("release", function () { lock = null; }); }).catch(function () { /* not allowed */ });
  }
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "visible") { wakeLock(); if (S.token && !S.ws) { connect(); } } });

  function applyTheme() {
    var theme = layout().theme || "auto";
    var light = theme === "light" || (theme === "auto" && place() === "couch" && isDay());
    document.body.classList.toggle("light", !!light);
  }

  // ---------- banner ----------
  function showBanner(text, ms) {
    var el = document.getElementById("pushbanner");
    if (!el) { el = document.createElement("button"); el.id = "pushbanner"; el.className = "banner push"; document.body.appendChild(el); }
    el.innerHTML = I("bell", 18) + " " + esc(text);
    clearTimeout(S.bannerTimer);
    if (ms) { S.bannerTimer = setTimeout(function () { if (el.parentNode) { el.parentNode.removeChild(el); } }, ms); }
  }

  // ---------- doorbell ----------
  var pc = null, mic = null;
  function startRing(m) {
    wake();
    S.ring = { name: m.name, camera: m.camera, opener: m.opener, started: Date.now(), full: place() === "door" || place() === "wall", muted: false, talking: false };
    chime();
    render();
    clearTimeout(S.ringTimer);
    S.ringTimer = setTimeout(endRing, 120000);
  }
  function endRing(byUser) {
    clearTimeout(S.ringTimer);
    if (!S.ring) { return; }
    S.ring = null; stopVideo();
    var el = document.getElementById("ring"); if (el) { el.parentNode.removeChild(el); }
    if (byUser === true) { S.lastTouch = Date.now(); }
  }
  function chime() {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext; if (!Ctx) { return; }
      var ctx = S.audio || (S.audio = new Ctx());
      [[659.3, 0], [523.3, 0.45]].forEach(function (n) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "sine"; o.frequency.value = n[0];
        g.gain.setValueAtTime(0.0001, ctx.currentTime + n[1]);
        g.gain.exponentialRampToValueAtTime(0.4, ctx.currentTime + n[1] + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + n[1] + 1.2);
        o.connect(g); g.connect(ctx.destination); o.start(ctx.currentTime + n[1]); o.stop(ctx.currentTime + n[1] + 1.3);
      });
    } catch (e) { /* no sound */ }
  }
  function renderRing() {
    var r = S.ring; if (!r) { return; }
    var el = document.getElementById("ring");
    if (!r.full) {
      if (!el) { el = document.createElement("div"); el.id = "ring"; document.body.appendChild(el); }
      el.className = "ringbanner";
      el.innerHTML = '<span class="pulse"></span><b>' + esc(t("ringingAt", { name: r.name })) + '</b><button class="pill primary" data-ringview="1">' + esc(t("view")) + '</button><button class="iconbtn" data-hangup="1">' + I("x") + "</button>";
      return;
    }
    if (!el) { el = document.createElement("div"); el.id = "ring"; document.body.appendChild(el); }
    el.className = "ringfull";
    var media = r.camera ? '<div class="nocam">' + I("bell", 64) + "<span>" + esc(t("camConnecting")) + '</span></div><video id="ringvideo" autoplay playsinline' + (r.muted ? " muted" : "") + '></video><img id="ringsnap" alt="">' : '<div class="nocam">' + I("bell", 64) + "<span>" + esc(t("noCamera")) + "</span></div>";
    el.innerHTML = media + '<div class="ringtop"><span class="pulse"></span> ' + esc(t("ringingAt", { name: r.name })) + ' <span class="sub" id="ringclock"></span></div>' +
      '<div class="ringctrl"><button class="rb" data-mute="1"><span class="c">' + I(r.muted ? "speaker" : "mute") + "</span>" + esc(r.muted ? t("unmute") : t("mute")) + "</button>" +
      (r.camera ? '<button class="rb talk' + (r.talking ? " on" : "") + '" data-talk="1"><span class="c">' + I("mic") + "</span>" + esc(t("talk")) + "</button>" : "") +
      (r.opener ? '<div class="slide" id="slide"><div class="k">' + I("key") + '</div><span>' + esc(r.opened ? t("opened") : t("slideOpen")) + "</span></div>" : "") +
      '<button class="rb end" data-hangup="1"><span class="c">' + I("x") + "</span>" + esc(t("hangup")) + "</button></div>";
    if (r.camera) { startVideo(r.camera, r.talking); }
  }
  function startVideo(stream, withMic) {
    stopVideo();
    var video = document.getElementById("ringvideo");
    if (!window.RTCPeerConnection || !video) { snapshotLoop(stream); return; }
    pc = new RTCPeerConnection({ iceServers: [] });
    pc.addTransceiver("video", { direction: "recvonly" });
    var audio = pc.addTransceiver("audio", { direction: withMic && mic ? "sendrecv" : "recvonly" });
    if (withMic && mic) { audio.sender.replaceTrack(mic.getAudioTracks()[0]); }
    pc.ontrack = function (ev) { if (video.srcObject !== ev.streams[0]) { video.srcObject = ev.streams[0] || new MediaStream([ev.track]); } };
    pc.createOffer().then(function (offer) { return pc.setLocalDescription(offer); }).then(function () {
      return waitIce(pc);
    }).then(function () {
      return fetch("api/webrtc?stream=" + encodeURIComponent(stream), { method: "POST", headers: { Authorization: "Bearer " + S.token, "Content-Type": "application/sdp" }, body: pc.localDescription.sdp });
    }).then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.text(); })
      .then(function (sdp) { return pc.setRemoteDescription({ type: "answer", sdp: sdp }); })
      .catch(function () { snapshotLoop(stream); });
  }
  function waitIce(conn) {
    return new Promise(function (resolve) {
      if (conn.iceGatheringState === "complete") { resolve(); return; }
      var done = function () { if (conn.iceGatheringState === "complete") { resolve(); } };
      conn.addEventListener("icegatheringstatechange", done);
      setTimeout(resolve, 1500);
    });
  }
  function snapshotLoop(stream) {
    var img = document.getElementById("ringsnap"); if (!img || !S.ring) { return; }
    img.style.display = "block";
    fetch("api/snapshot?stream=" + encodeURIComponent(stream) + "&t=" + Date.now(), { headers: { Authorization: "Bearer " + S.token } })
      .then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.blob(); })
      .then(function (b) { var old = img.src; img.src = URL.createObjectURL(b); if (old && old.indexOf("blob:") === 0) { URL.revokeObjectURL(old); } })
      .catch(function () { /* camera offline */ })
      .then(function () { S.snapTimer = setTimeout(function () { snapshotLoop(stream); }, 1000); });
  }
  function stopVideo() {
    clearTimeout(S.snapTimer);
    if (pc) { try { pc.close(); } catch (e) { /* closed */ } pc = null; }
  }
  function talk() {
    var r = S.ring; if (!r) { return; }
    if (r.talking) { r.talking = false; if (mic) { mic.getTracks().forEach(function (tr) { tr.stop(); }); mic = null; } renderRing(); return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { showBanner(t("needHttps"), 5000); return; }
    navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } }).then(function (s) {
      mic = s; r.talking = true; r.muted = false; renderRing();
    }).catch(function () { showBanner(t("noMic"), 4000); });
  }
  function slideDrag(el, ev) {
    var knob = el.querySelector(".k"), r = el.getBoundingClientRect(), startX = ev.clientX, max = r.width - knob.offsetWidth - 16, x = 0;
    function move(e) { x = Math.max(0, Math.min(max, e.clientX - startX)); knob.style.transform = "translateX(" + x + "px)"; e.preventDefault(); }
    function up() {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      if (x >= max * 0.9) {
        if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); } else {
          send({ type: "action", action: "open_door", ringing: true }); S.ring.opened = true; renderRing();
        }
      } else { knob.style.transform = ""; }
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
  }

  // ---------- input ----------
  var press = null;
  function closest(el, attr) { while (el && el !== document) { if (el.getAttribute && el.getAttribute(attr) !== null) { return el; } el = el.parentNode; } return null; }

  document.addEventListener("pointerdown", function (ev) {
    if (S.audio && S.audio.state === "suspended") { S.audio.resume(); }
    var wasSaver = S.saver; wake();
    if (wasSaver) { press = { saver: Date.now() }; ev.preventDefault(); return; }
    var slider = closest(ev.target, "data-slider"); if (slider) { sliderDrag(slider, ev); return; }
    var slide = closest(ev.target, "data-slide") || (ev.target.closest ? ev.target.closest("#slide") : null); if (slide) { slideDrag(slide, ev); return; }
    var tile = closest(ev.target, "data-tile");
    if (tile && !S.edit) {
      var id = tile.getAttribute("data-tile");
      press = { id: id, x: ev.clientX, y: ev.clientY, long: false };
      press.timer = setTimeout(function () { if (press && press.id === id) { press.long = true; if (navigator.vibrate) { navigator.vibrate(10); } openSheet(id); } }, 480);
    }
  }, { passive: false });
  document.addEventListener("pointermove", function (ev) {
    if (press && press.id && (Math.abs(ev.clientX - press.x) > 10 || Math.abs(ev.clientY - press.y) > 10)) { clearTimeout(press.timer); press = null; }
  });
  document.addEventListener("pointerup", function () { if (press && press.timer) { clearTimeout(press.timer); } });

  document.addEventListener("click", function (ev) {
    if (press && press.saver) { var fresh = Date.now() - press.saver < 800; press = null; if (fresh) { return; } }
    var target = ev.target, el;
    if ((el = closest(target, "data-tile")) && !closest(target, "data-edit") && !closest(target, "data-step")) {
      var id = el.getAttribute("data-tile");
      if (S.edit) { return; }
      if (press && press.long) { press = null; return; }
      press = null; tap(id); return;
    }
    if ((el = closest(target, "data-edit"))) {
      var tileEl = closest(el, "data-tile");
      if (tileEl) {
        var lay = copyLayout(), hidden = lay.hidden_tiles || [], tid = tileEl.getAttribute("data-tile");
        if (el.getAttribute("data-edit") === "hide") { if (hidden.indexOf(tid) < 0) { hidden.push(tid); } } else { hidden = hidden.filter(function (x) { return x !== tid; }); }
        lay.hidden_tiles = hidden; saveLayout(lay); return;
      }
      S.edit = true; closeSheet(); if (S.tab === "home" || S.tab === "history") { var first = visibleRooms()[0]; if (first) { S.tab = "room:" + first.name; } } renderTabs(); renderContent(); return;
    }
    if ((el = closest(target, "data-editdone"))) { S.edit = false; renderContent(); return; }
    if ((el = closest(target, "data-tab"))) { S.tab = el.getAttribute("data-tab"); renderTabs(); renderContent(); document.getElementById("content").scrollTop = 0; return; }
    if ((el = closest(target, "data-go"))) { S.tab = el.getAttribute("data-go"); renderTabs(); renderContent(); return; }
    if ((el = closest(target, "data-day"))) { S.historyDay = el.getAttribute("data-day"); renderContent(); return; }
    if ((el = closest(target, "data-scene"))) { if (S.tablet.readonly) { showBanner(t("readonly"), 3000); return; } send({ type: "action", action: "scene", id: el.getAttribute("data-scene") }); el.classList.add("on"); setTimeout(function () { el.classList.remove("on"); }, 800); return; }
    if ((el = closest(target, "data-alloff"))) { if (S.tablet.readonly) { showBanner(t("readonly"), 3000); return; } send({ type: "action", action: "all_off", room: el.getAttribute("data-alloff") || null }); return; }
    if ((el = closest(target, "data-off"))) { act(el.getAttribute("data-off"), "off", null, { on: false }); return; }
    if ((el = closest(target, "data-close"))) { closeSheet(); return; }
    if (target.id === "sheet") { closeSheet(); return; }
    if ((el = closest(target, "data-do"))) {
      var sid = S.sheet.id, what = el.getAttribute("data-do");
      if (what === "on") { act(sid, "on", null, { on: true }); } else if (what === "off") { act(sid, "off", null, { on: false }); } else if (what === "up") { act(sid, "position", 100, { position: 100 }); } else if (what === "down") { act(sid, "position", 0, { position: 0 }); } else if (what === "stop") { act(sid, "stop"); } else { act(sid, what, null, { locked: what === "lock" }); }
      renderSheet(); return;
    }
    if ((el = closest(target, "data-step"))) {
      var tile = S.tiles[el.getAttribute("data-sid") || S.sheet.id], step = (tile.step || 0.5) * Number(el.getAttribute("data-step"));
      var next = Math.max(4.5, Math.min(30, (tile.state.target || 20) + step));
      tile.state.target = next; if (S.sheet) { renderSheet(); } updateTile(tile.id);
      clearTimeout(S.stepTimer); S.stepTimer = setTimeout(function () { act(tile.id, "target", next, { target: next }); }, 700);
      return;
    }
    if ((el = closest(target, "data-settings"))) { openSettings(); return; }
    if ((el = closest(target, "data-batteries"))) { openBatteries(); return; }
    if ((el = closest(target, "data-batt"))) { openSheet(el.getAttribute("data-batt")); return; }
    if ((el = closest(target, "data-place"))) { send({ type: "setup", place: el.getAttribute("data-place") }); S.tablet.place = el.getAttribute("data-place"); renderSettings(); return; }
    if ((el = closest(target, "data-theme"))) { var l1 = copyLayout(); l1.theme = el.getAttribute("data-theme"); saveLayout(l1); return; }
    if ((el = closest(target, "data-roomtoggle"))) {
      var l2 = copyLayout(), hr = l2.hidden_rooms || [], name = el.getAttribute("data-roomtoggle");
      l2.hidden_rooms = hr.indexOf(name) >= 0 ? hr.filter(function (x) { return x !== name; }) : hr.concat([name]); saveLayout(l2); return;
    }
    if ((el = closest(target, "data-roomup")) || (el = closest(target, "data-roomdown"))) {
      var up = el.getAttribute("data-roomup") !== null, i = Number(el.getAttribute(up ? "data-roomup" : "data-roomdown"));
      var names = allRoomsOrdered().map(function (r) { return r.name; }), j = up ? i - 1 : i + 1;
      if (j < 0 || j >= names.length) { return; }
      var tmp = names[i]; names[i] = names[j]; names[j] = tmp;
      var l3 = copyLayout(); l3.room_order = names; saveLayout(l3); return;
    }
    if ((el = closest(target, "data-resetlayout"))) { var l4 = { theme: layout().theme }; S.usage = {}; store("dashUsage", "{}"); saveLayout(l4); return; }
    if ((el = closest(target, "data-pair"))) { pair(document.getElementById("code").value); return; }
    if ((el = closest(target, "data-setupplace"))) { S.setupPlace = el.getAttribute("data-setupplace"); S.setupRoom = document.getElementById("setuproom").value; renderSetup(); return; }
    if ((el = closest(target, "data-setupdone"))) {
      var room = document.getElementById("setuproom").value, pl = S.setupPlace || "wall";
      var label = { wall: "Wand", couch: "Couch", door: "Tür" }[pl];
      send({ type: "setup", place: pl, room: room, name: (room ? room + " " : "") + (GERMAN ? label : pl) });
      S.tablet.place = pl; S.tablet.room = room; S.tab = startTab(); render(); wakeLock(); return;
    }
    if ((el = closest(target, "data-ringview"))) { S.ring.full = true; renderRing(); return; }
    if ((el = closest(target, "data-hangup"))) { endRing(true); return; }
    if ((el = closest(target, "data-mute"))) { S.ring.muted = !S.ring.muted; var v = document.getElementById("ringvideo"); if (v) { v.muted = S.ring.muted; } renderRing(); return; }
    if ((el = closest(target, "data-talk"))) { talk(); return; }
    if (target.closest && target.closest("#pushbanner")) { var b = document.getElementById("pushbanner"); b.parentNode.removeChild(b); }
  });
  document.addEventListener("change", function (ev) {
    if (ev.target.id === "tabroom") { send({ type: "setup", room: ev.target.value }); S.tablet.room = ev.target.value; }
    if (ev.target.id === "tabname" && ev.target.value.trim()) { send({ type: "setup", name: ev.target.value.trim() }); }
    if (ev.target.id === "setuproom") { S.setupRoom = ev.target.value; }
  });
  document.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && ev.target.id === "code") { pair(ev.target.value); } });

  // ---------- start ----------
  function tick() {
    S.now = new Date();
    renderHeader(); idleCheck();
    if (S.saver) { renderSaver(); }
    var clock = document.getElementById("ringclock");
    if (clock && S.ring) { var s = Math.round((Date.now() - S.ring.started) / 1000); clock.textContent = "· " + Math.floor(s / 60) + ":" + two(s % 60); }
    applyTheme();
  }
  function start() {
    var hp = hashParams();
    S.token = hp.t || store("dashToken");
    if (hp.t) { store("dashToken", hp.t); }
    if (hp.pair && !S.token) { render(); pair(hp.pair); } else { render(); connect(); }
    if (S.token && !hp.t) { history.replaceState(null, "", location.pathname + "#t=" + encodeURIComponent(S.token)); }
    setInterval(tick, 1000 * 15);
    setInterval(function () { var c = document.getElementById("ringclock"); if (c && S.ring) { tick(); } }, 1000);
    if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
      navigator.serviceWorker.register("sw.js").catch(function () { /* optional */ });
    }
  }
  start();
})();
