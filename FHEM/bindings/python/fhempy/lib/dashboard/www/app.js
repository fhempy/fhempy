/* fhempy tablet dashboard. Plain JavaScript, no build step, runs on old
   iPads too. The server (dashboard.py) sends rooms, tiles and the header,
   live changes come over the WebSocket. */
(function () {
  "use strict";
  // replaced by the server with the version of the app files
  var BUILD = "__DASHBOARD_BUILD__";

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
    chLight: "Licht", chClimate: "Klima", chBlinds: "Rollläden", chSecurity: "Sicherheit", chNOn: "{n} an", chAllOff: "alles aus", chNHeat: "{n} heizen", chOneHeat: "1 heizt", chNOpen: "{n} von {m} offen", chAllClosed: "alle zu", chSecOpen: "{n} offen", chSecOk: "alles zu", ovLight: "Was leuchtet", ovClimate: "Raumklima", ovBlinds: "Rollläden", ovSecurity: "Fenster, Türen und Schlösser", ovNoLight: "Alle Lichter sind aus.", ovSecOk: "Alles zu und verriegelt.", allUp: "Alle auf", allDown: "Alle zu", lightsOff: "Alle Lichter aus", heatsNow: "heizt",
    pairTitle: "Tablet verbinden", pairText: "Öffne in FHEM das Gerät des Dashboards und scanne den QR-Code mit der Kamera dieses Tablets. Oder gib den Code ein, der dort steht.",
    pairButton: "Verbinden", pairWrong: "Der Code stimmt nicht oder ist abgelaufen. Lade die Seite in FHEM neu für einen neuen Code.",
    whereTitle: "Wo steht dieses Tablet?", whereText: "Wir haben {rooms} Räume und {tiles} Geräte gefunden. Wähle den Platz, den Rest machen wir.",
    chMaint: "Wartung", chMaintN: "{n} Geräte", ovMaint: "Wartung", ovMaintLead: "Diese Geräte brauchen Aufmerksamkeit.", mtUnreachable: "nicht erreichbar", mtSilent: "keine Werte {t}", mtOk: "Alles in Ordnung.", mtBattery: "Batterie schwach",
    offDone: "{n} Geräte aus.", offLeft: "Noch an: {names}", offAgain: "Nochmal",
    pinTitle: "PIN eingeben", pinLead: "Die Einstellungen sind mit einer PIN geschützt.", pinWrong: "Falsche PIN.", pinWait: "Zu viele Versuche. Bitte in 5 Minuten nochmal.", pinOpen: "Entsperrt für 10 Minuten.", pinLocked: "Gesperrt, bitte PIN eingeben.", pinOk: "OK",
    calTitle: "Heute", calTomorrow: "Morgen", calAllDay: "ganztags", calNow: "jetzt", binTitle: "Müll", binToday: "Heute: {what}", binTomorrow: "Morgen: {what}",
    half: "50 %", pullWindow: "Ziehen zum Bewegen",
    colorTitle: "Farbe", whiteTitle: "Weiß", warm: "warm", cold: "kalt",
    wxTitle: "Wetter", wxHours: "Nächste 24 Stunden", wxDays: "Nächste Tage", wxSunrise: "Sonnenaufgang", wxSunset: "Sonnenuntergang", wxToday: "Heute", wxNone: "Keine Vorhersage, das Wetter-Gerät liefert keine Stunden oder Tage.",
    rtNight: "Gute Nacht", rtAway: "Haus verlassen", rtNightLead: "Das ist noch offen oder an. Mit „Gute Nacht“ geht das Licht aus und die Rollläden gehen zu.", rtAwayLead: "Das ist noch offen oder an. Beim Gehen geht alles aus, was nicht anbleiben soll.",
    rtAllFine: "Alles zu und aus.", rtBlinds: "{n} Rollläden offen", rtBlind: "1 Rollladen offen", rtBlindsSub: "gehen zu", rtGoNight: "Gute Nacht", rtGoAway: "Los geht’s", rtOff: "geht aus",
    warnrain: "Regen ab {t}", warnstorm: "Sturm oder Gewitter ab {t}", warnfrost: "Frost ab {t}", warnWindows: "Fenster offen: {names}",
    rtDoneNight: "Gute Nacht! {n} Geräte aus.", rtDoneAway: "Tschüss! {n} Geräte aus.", rtDoneNone: "Alles war schon aus.", rtFailed: "Nicht reagiert: {names}", undo: "Rückgängig", undone: "Wieder wie vorher.",
    wall: "An der Wand", couch: "Bei der Couch", door: "Bei der Tür",
    wallList: ["Immer an, Bildschirmschoner mit Uhr", "Startet mit dem ganzen Zuhause", "Wacht auf bei Bewegung im Raum", "Warnungen groß oben"],
    couchList: ["Startet im eigenen Raum", "Licht, Szenen, Rollläden zuerst", "Kein Bildschirmschoner", "Tagsüber hell, abends dunkel"],
    doorList: ["Klingel übernimmt den Bildschirm", "Kamera, Sprechen, Tür öffnen", "Beim Gehen: was noch offen ist", "Alles aus mit einem Tipp"],
    roomOfTablet: "Raum für dieses Tablet:", next: "Weiter", noRoom: "Kein Raum",
    pickTitle: "Welche Räume soll dieses Tablet zeigen?", pickText: "Tippe die Räume an, die du hier brauchst. Du kannst das später in den Einstellungen ändern.",
    pickAll: "Alle", pickNone: "Keine", pickDone: "Fertig", pickCount: "{n} von {m} Räumen", pickDevices: "{n} Geräte", pickDevice: "1 Gerät", pickBack: "Zurück", roomsDragHint: "Zum Sortieren an ⠿ ziehen. Der Schalter blendet einen Raum auf diesem Tablet aus.",
    newVersion: "Neue Version des Dashboards.", reloadNow: "Neu laden",
    connLost: "Verbindung weg, versuche neu …", readonly: "Dieses Tablet darf nur anzeigen.",
    tapHint: "Tipp auf das Symbol schaltet, Tipp auf die Kachel zeigt die Details.", confirmTap: "Nochmal tippen", unlockSure: "Nochmal tippen zum Entriegeln",
    noReaction: "„{name}“ hat nicht reagiert.", failed: "„{name}“ ging nicht: {reason}", retry: "Nochmal",
    inputsHint: "Werte dieser Automatik", inputSet: "Übernehmen", inputRun: "Ausführen",
    fan: "Ventilator", fanOff: "Aus", fanLow: "Niedrig", fanMedium: "Mittel", fanHigh: "Hoch", pullToFan: "Ziehen für die Stufe",
    playing: "Spielt", paused: "Pausiert", idle: "Bereit", nothingPlays: "Gerade läuft nichts", volume: "Lautstärke", presets: "Senderspeicher", prevTrack: "Zurück", nextTrack: "Weiter", playPause: "Abspielen oder Pause",
    pullToDim: "Ziehen zum Dimmen", pullToMove: "Ziehen zum Bewegen", up: "Auf", down: "Zu", stop: "Stopp",
    lock: "Verriegeln", unlock: "Entriegeln", today: "Heute", peopleTitle: "Wer ist zu Hause?", peopleHome: "Zu Hause", peopleAway: "Unterwegs", arrived: "angekommen {t}", left: "weg seit {t}", atTime: "{t}", yesterdayAt: "gestern {t}", dayAt: "{d}, {t}", setTablet: "Dieses Tablet", setHome: "Ganzes Zuhause · alle Tablets", setNamePlace: "Name, Standort und Raum", setRooms: "Räume anzeigen und sortieren", setRoomsValue: "{n} von {m} sichtbar", setKeepValue: "{n} Geräte", setKeepNone: "keine", setArrangeValue: "Geräte den Räumen zuordnen", resetView: "Ansicht dieses Tablets zurücksetzen", back: "Einstellungen", setTalk: "Sprechen an der Tür", editHint: "Kacheln ziehen zum Verschieben (am Tablet kurz halten), × blendet sie aus.", keepOn: "Bei „Alles aus“ anlassen", keepOnHint: "Für Heizung, Wärmepumpe, Kühlschrank oder Router. Gilt für alle Tablets.", keepOnList: "Bei „Alles aus“ anlassen", staysOn: "bleibt an", keepBtn: "Anlassen", arrange: "Räume ordnen", arrangeLead: "Ziehe ein Gerät in einen Raum oder tippe es an. × nimmt es aus dem Raum. Die Räume gelten in FHEM und auf allen Tablets.", arrangeDone: "Fertig", unassigned: "Ohne Raum", applyAll: "Alle Vorschläge übernehmen ({n})", chooseRoom: "Raum wählen", moveTo: "In Raum verschieben", newRoom: "Neuer Raum", create: "Anlegen", removeFrom: "Aus {room} entfernen", dropHere: "Hierher ziehen: ohne Raum", addDevice: "Gerät", idleTitle: "Lange nicht benutzt", idleLead: "Seit über einem Monat keine neue Meldung. Vielleicht kaputt, Batterie leer oder nicht mehr vorhanden.", idleFor: "seit {t}", idleDays: "{n} Tagen", idleMonths: "{n} Monaten", idleDaysShort: "{n} T.", idleMonthsShort: "{n} Mon.", deleteDevice: "Löschen", deleteSure: "Wirklich löschen?", deleteHint: "Löscht das Gerät in FHEM. Endgültig wird es mit save, bis dahin bringt ein Neustart von FHEM es zurück.", addTo: "Gerät zu {room}", searchDevice: "Name eingeben …", noMatch: "Kein passendes Gerät", fromRoom: "aus {room}", alreadyHere: "schon hier", renameRoom: "Raum umbenennen", save: "Speichern", nowIn: "Jetzt: {room}", alsoIn: "auch {rooms}", allSorted: "Alle Geräte haben einen Raum.", badRoom: "Bitte ohne Komma, Semikolon und Anführungszeichen", morning: "Guten Morgen", day: "Hallo", evening: "Guten Abend", night: "Gute Nacht", airOut: "Lüften", heatingOpen: "Heizung läuft, Fenster offen", heatingOpenSub: "{rooms}", min: "min.", max: "max.", targetTemp: "Soll", times: "{n}× an", total: "zusammen {t}",
    noTimeline: "Lege ein Timeline-Gerät an (Install modules), dann siehst du hier, was passiert ist.",
    noDevices: "Hier ist noch nichts. Gib deinen Geräten in FHEM einen Raum (Attribut room).",
    happened: "Gerade passiert", lately: "Zuletzt passiert", showAll: "Alles", yesterday: "gestern", ringing: "Es klingelt", ringingAt: "Es klingelt: {name}",
    talk: "Sprechen", mute: "Stumm", unmute: "Ton an", hangup: "Beenden", slideOpen: "Zum Öffnen schieben →",
    opened: "Tür geöffnet", view: "Ansehen", needHttps: "Sprechen geht nur über https, siehe Einstellungen.",
    noMic: "Kein Zugriff aufs Mikrofon.", noCamera: "Keine Kamera eingerichtet", camConnecting: "Kamera wird verbunden …",
    name: "Name", place: "Standort", room: "Raum", theme: "Design", auto: "Automatisch", dark: "Dunkel", light: "Hell",
    rooms: "Räume", editTiles: "Kacheln bearbeiten", editDone: "Bearbeiten beenden", reset: "Zurücksetzen",
    rpLight: "Licht", rpSwitches: "Schalter", rpBlinds: "Rollläden", rpMore: "Mehr in diesem Raum", rpOpenRoom: "Ganzen Raum öffnen", rpNofM: "{n} von {m} an", rpAllOffShort: "Alle aus", rpHeatsNow: "Heizt gerade", rpHoldRing: "Ring ziehen zum Einstellen", rpReached: "Soll erreicht", rpSetTo: "Soll {t}°",
    switchHttps: "Zu https wechseln (für Sprechen)", energy: "Energie", solar: "Solar", usage: "Verbrauch",
    grid: "Netz", storage: "Speicher", price: "Preis", surplus: "Überschuss", fromGrid: "Netzbezug",
    hiddenTiles: "Ausgeblendet, + zum Zurückholen", days: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
    months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    weekdays: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
    timerOff: "Ausschalten in", timerOn: "Einschalten für", timerLeft: "noch {t}", timerUntil: "geht aus um {t}", timerStop: "Timer beenden", min15: "15 min", min30: "30 min", h1: "1 h", h2: "2 h",
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
    chLight: "Light", chClimate: "Climate", chBlinds: "Blinds", chSecurity: "Security", chNOn: "{n} on", chAllOff: "all off", chNHeat: "{n} heating", chOneHeat: "1 heating", chNOpen: "{n} of {m} open", chAllClosed: "all closed", chSecOpen: "{n} open", chSecOk: "all closed", ovLight: "What is on", ovClimate: "Room climate", ovBlinds: "Blinds", ovSecurity: "Windows, doors and locks", ovNoLight: "All lights are off.", ovSecOk: "Everything closed and locked.", allUp: "All up", allDown: "All down", lightsOff: "All lights off", heatsNow: "heating",
    pairTitle: "Connect tablet", pairText: "Open the dashboard device in FHEM and scan the QR code with the camera of this tablet, or enter the code shown there.",
    pairButton: "Connect", pairWrong: "Wrong or expired code. Reload the page in FHEM for a new code.",
    whereTitle: "Where is this tablet?", whereText: "We found {rooms} rooms and {tiles} devices. Choose the place, we do the rest.",
    chMaint: "Maintenance", chMaintN: "{n} devices", ovMaint: "Maintenance", ovMaintLead: "These devices need attention.", mtUnreachable: "not reachable", mtSilent: "no values {t}", mtOk: "Everything is fine.", mtBattery: "battery low",
    offDone: "{n} devices off.", offLeft: "Still on: {names}", offAgain: "Try again",
    pinTitle: "Enter PIN", pinLead: "The settings are protected by a PIN.", pinWrong: "Wrong PIN.", pinWait: "Too many tries. Please try again in 5 minutes.", pinOpen: "Unlocked for 10 minutes.", pinLocked: "Locked, please enter the PIN.", pinOk: "OK",
    calTitle: "Today", calTomorrow: "Tomorrow", calAllDay: "all day", calNow: "now", binTitle: "Bins", binToday: "Today: {what}", binTomorrow: "Tomorrow: {what}",
    half: "50 %", pullWindow: "Drag to move",
    colorTitle: "Colour", whiteTitle: "White", warm: "warm", cold: "cold",
    wxTitle: "Weather", wxHours: "Next 24 hours", wxDays: "Next days", wxSunrise: "Sunrise", wxSunset: "Sunset", wxToday: "Today", wxNone: "No forecast, the weather device gives no hours or days.",
    rtNight: "Good night", rtAway: "Leave home", rtNightLead: "Still open or on. “Good night” switches the lights off and closes the blinds.", rtAwayLead: "Still open or on. Leaving switches off everything that should not stay on.",
    rtAllFine: "Everything closed and off.", rtBlinds: "{n} blinds open", rtBlind: "1 blind open", rtBlindsSub: "will close", rtGoNight: "Good night", rtGoAway: "Let’s go", rtOff: "goes off",
    warnrain: "Rain from {t}", warnstorm: "Storm or thunder from {t}", warnfrost: "Frost from {t}", warnWindows: "Windows open: {names}",
    rtDoneNight: "Good night! {n} devices off.", rtDoneAway: "Bye! {n} devices off.", rtDoneNone: "Everything was off already.", rtFailed: "Did not react: {names}", undo: "Undo", undone: "Back as before.",
    wall: "On the wall", couch: "At the couch", door: "At the door",
    wallList: ["Always on, screensaver with clock", "Starts with the whole home", "Wakes up on motion in the room", "Warnings big at the top"],
    couchList: ["Starts in its own room", "Lights, scenes, blinds first", "No screensaver", "Bright by day, dark at night"],
    doorList: ["Doorbell takes over the screen", "Camera, talk, open the door", "When leaving: what is still open", "All off with one tap"],
    roomOfTablet: "Room of this tablet:", next: "Next", noRoom: "No room",
    pickTitle: "Which rooms should this tablet show?", pickText: "Tap the rooms you need here. You can change this later in the settings.",
    pickAll: "All", pickNone: "None", pickDone: "Done", pickCount: "{n} of {m} rooms", pickDevices: "{n} devices", pickDevice: "1 device", pickBack: "Back", roomsDragHint: "Drag ⠿ to sort. The switch hides a room on this tablet.",
    newVersion: "New version of the dashboard.", reloadNow: "Reload",
    connLost: "Connection lost, retrying …", readonly: "This tablet may only show.",
    tapHint: "Tap the icon to switch, tap the tile for the details.", confirmTap: "Tap again", unlockSure: "Tap again to unlock",
    noReaction: "“{name}” didn't react.", failed: "“{name}” didn't work: {reason}", retry: "Try again",
    inputsHint: "Values of this automation", inputSet: "Apply", inputRun: "Run",
    fan: "Fan", fanOff: "Off", fanLow: "Low", fanMedium: "Medium", fanHigh: "High", pullToFan: "Drag to set the speed",
    playing: "Playing", paused: "Paused", idle: "Ready", nothingPlays: "Nothing is playing", volume: "Volume", presets: "Presets", prevTrack: "Previous", nextTrack: "Next", playPause: "Play or pause",
    pullToDim: "Drag to dim", pullToMove: "Drag to move", up: "Up", down: "Down", stop: "Stop",
    lock: "Lock", unlock: "Unlock", today: "Today", peopleTitle: "Who is at home?", peopleHome: "At home", peopleAway: "Away", arrived: "arrived {t}", left: "away since {t}", atTime: "{t}", yesterdayAt: "yesterday {t}", dayAt: "{d}, {t}", setTablet: "This tablet", setHome: "Whole home · all tablets", setNamePlace: "Name, place and room", setRooms: "Show and order rooms", setRoomsValue: "{n} of {m} shown", setKeepValue: "{n} devices", setKeepNone: "none", setArrangeValue: "Assign devices to rooms", resetView: "Reset the view of this tablet", back: "Settings", setTalk: "Talking at the door", editHint: "Drag tiles to move them (on tablets hold briefly), × hides them.", keepOn: "Leave on with “All off”", keepOnHint: "For heating, heat pump, fridge or router. Applies to all tablets.", keepOnList: "Leave on with “All off”", staysOn: "stays on", keepBtn: "Leave on", arrange: "Arrange rooms", arrangeLead: "Drag a device to a room or tap it. × takes it out of the room. Rooms apply in FHEM and on all tablets.", arrangeDone: "Done", unassigned: "Without room", applyAll: "Apply all suggestions ({n})", chooseRoom: "Choose room", moveTo: "Move to room", newRoom: "New room", create: "Create", removeFrom: "Remove from {room}", dropHere: "Drop here: without room", addDevice: "Device", idleTitle: "Not used for long", idleLead: "No new value for more than a month. Maybe broken, battery empty or gone.", idleFor: "for {t}", idleDays: "{n} days", idleMonths: "{n} months", idleDaysShort: "{n} d", idleMonthsShort: "{n} mo", deleteDevice: "Delete", deleteSure: "Really delete?", deleteHint: "Deletes the device in FHEM. It is gone for good with save, until then a restart of FHEM brings it back.", addTo: "Device to {room}", searchDevice: "Type a name …", noMatch: "No matching device", fromRoom: "from {room}", alreadyHere: "already here", renameRoom: "Rename room", save: "Save", nowIn: "Now: {room}", alsoIn: "also {rooms}", allSorted: "Every device has a room.", badRoom: "Please without comma, semicolon and quotes", morning: "Good morning", day: "Hello", evening: "Good evening", night: "Good night", airOut: "Air out", heatingOpen: "Heating with the window open", heatingOpenSub: "{rooms}", min: "min", max: "max", targetTemp: "target", times: "{n}× on", total: "{t} in total",
    noTimeline: "Create a timeline device (Install modules) to see what happened here.",
    noDevices: "Nothing here yet. Give your devices a room in FHEM (attribute room).",
    happened: "Just happened", lately: "Lately at home", showAll: "All", yesterday: "yesterday", ringing: "Somebody rings", ringingAt: "Somebody rings: {name}",
    talk: "Talk", mute: "Mute", unmute: "Sound on", hangup: "End", slideOpen: "Slide to open →",
    opened: "Door opened", view: "View", needHttps: "Talking needs https, see settings.",
    noMic: "No access to the microphone.", noCamera: "No camera set up", camConnecting: "Connecting camera …",
    name: "Name", place: "Place", room: "Room", theme: "Design", auto: "Automatic", dark: "Dark", light: "Light",
    rooms: "Rooms", editTiles: "Edit tiles", editDone: "Done editing", reset: "Reset",
    rpLight: "Light", rpSwitches: "Switches", rpBlinds: "Blinds", rpMore: "More in this room", rpOpenRoom: "Open the whole room", rpNofM: "{n} of {m} on", rpAllOffShort: "All off", rpHeatsNow: "Heating now", rpHoldRing: "Drag the ring to set", rpReached: "Target reached", rpSetTo: "Set to {t}°",
    switchHttps: "Switch to https (for talking)", energy: "Energy", solar: "Solar", usage: "Usage",
    grid: "Grid", storage: "Battery", price: "Price", surplus: "Surplus", fromGrid: "From grid",
    hiddenTiles: "Hidden, + brings them back", days: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    timerOff: "Switch off in", timerOn: "Switch on for", timerLeft: "{t} left", timerUntil: "goes off at {t}", timerStop: "End timer", min15: "15 min", min30: "30 min", h1: "1 h", h2: "2 h",
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
    sliders: '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    fan: '<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 1-7 4-7s3 4-2 7M14 12c4 0 7 1 7 4s-4 3-7-2M12 14c0 4-1 7-4 7s-3-4 2-7M10 12c-4 0-7-1-7-4s4-3 7 2"/>',
    music: '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    play: '<path d="M7 4.5v15l12.5-7.5z" fill="currentColor"/>',
    pause: '<path d="M7 4h3.5v16H7zM13.5 4H17v16h-3.5z" fill="currentColor"/>',
    skipnext: '<path d="M5 5v14l10-7zM18 5v14" fill="currentColor"/>',
    skipprev: '<path d="M19 5v14L9 12zM6 5v14" fill="currentColor"/>',
    vol: '<path d="M4 9h4l5-4v14l-5-4H4zM16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/>',
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
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    battery: '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2M6 11v2"/>',
    film: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
    timer: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M10 2h4"/>',
    left: '<path d="M15 6l-6 6 6 6"/>', right: '<path d="M9 6l6 6-6 6"/>',
    pencil: '<path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', check: '<path d="M5 12l5 5 9-10"/>',
    grip: '<path d="M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01" stroke-width="3.2"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    bed: '<path d="M3 18v-8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5M7 12.5a1.5 1.5 0 1 0 0-.01"/>',
    bath: '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3zM6 12V6a2 2 0 0 1 4 0M7 19l-1 2M17 19l1 2"/>',
    pot: '<path d="M4 10h16v6a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-6zM2 10h2M20 10h2M9 6c0-1 1-1 1-2M14 6c0-1 1-1 1-2"/>',
    desk: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    car: '<path d="M5 16V12l2-5h10l2 5v4M3 16h18v2H3zM5 12h14M7 18v2M17 18v2"/>',
    tree: '<path d="M12 3l6 9h-3l4 6H5l4-6H6l6-9zM12 18v3"/>',
    star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    stairs: '<path d="M3 20h5v-4h4v-4h4V8h5"/>'
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
    lastTouch: Date.now(), saver: false, ring: null, pending: {}, last: {}, arm: null, timeline: {},
    history: null, historyDay: null, usage: {}, banner: null, now: new Date(), sparks: {}, sparksAt: 0
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
  // after an update of fhempy the server has newer app files than the code
  // running here (also when it came from the cache of the service worker)
  function checkBuild(build) {
    if (!build || BUILD.indexOf("__") === 0 || build === BUILD) { S.newBuild = false; return; }
    S.newBuild = true;
    // nobody is using a wall tablet in the screensaver: just take the new version
    if (S.saver) { location.reload(); }
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
      if (m.type === "welcome") { S.connected = true; S.retry = 0; if (!S.tab) { S.tab = startTab(); } wakeLock(); checkBuild(m.build); }
      render(); loadSparks(true); tapHint(); return;
    }
    if (m.type === "rooms_setup") { if (S.arrange) { S.arrange.data = m; renderContent(); if (S.sheet && (S.sheet.arrange || S.sheet.addto !== undefined)) { renderSheet(); } } return; }
    if (m.type === "tablet") { S.tablet = m.tablet; applyTheme(); render(); return; }
    if (m.type === "tile") {
      S.tiles[m.tile.id] = m.tile; delete S.pending[m.tile.id];
      updateTile(m.tile.id); if (S.sheet && (S.sheet.id === m.tile.id || S.sheet.room || S.sheet.overview || S.sheet.routine) && !S.sliding && !chartActive) { renderSheet(); }
      return;
    }
    if (m.type === "header") { S.header = m.header; renderHeader(); if (S.sheet && (S.sheet.batteries || S.sheet.people || S.sheet.routine || S.sheet.weather)) { renderSheet(); } if (S.tab === "home" && !(tdrag && tdrag.active)) { renderContent(); } if (S.saver) { renderSaver(); } return; }
    if (m.type === "motion") {
      if (S.tablet && S.tablet.room && m.rooms.indexOf(S.tablet.room) >= 0) { wake(); }
      return;
    }
    if (m.type === "failed") { failed(m); return; }
    if (m.type === "all_off") { allOffResult(m); return; }
    if (m.type === "unlocked") { pinAnswer(m); return; }
    if (m.type === "locked") { S.unlockedUntil = 0; showToast(t("pinLocked"), null, 4000); return; }
    if (m.type === "routine") { routineDone(m); return; }
    if (m.type === "undone") { showToast(m.failed && m.failed.length ? t("rtFailed", { names: m.failed.join(", ") }) : t("undone"), null, 5000); return; }
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
  function greeting(d) {
    var h = d.getHours();
    return t(h >= 5 && h < 11 ? "morning" : h < 17 && h >= 11 ? "day" : h >= 17 && h < 22 ? "evening" : "night");
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
  var KIND_ICON = { light: "bulb", dimmer: "bulb", switch: "power", outlet: "plug", blind: "blind", thermostat: "thermo", lock: "lock", contact: "win", motion: "walk", temperature: "thermo", humidity: "drop", media: "music", fan: "fan", inputs: "sliders" };
  var TAP_TOGGLES = { light: 1, dimmer: 1, switch: 1, outlet: 1, blind: 1, fan: 1 };
  var FAN_MODES = ["off", "low", "medium", "high"];
  function fanText(f) { return f && f.mode ? t("fan" + f.mode.charAt(0).toUpperCase() + f.mode.slice(1)) + (f.percent && f.mode !== "off" ? " · " + f.percent + " %" : "") : "–"; }
  function fanHtml(f) {
    return '<div class="group"><div class="label">' + esc(t("fan")) + '</div><div class="seg fanseg">' + FAN_MODES.map(function (m) {
      return '<button class="' + ((f && f.mode) === m ? "on" : "") + '" data-fanmode="' + m + '">' + esc(t("fan" + m.charAt(0).toUpperCase() + m.slice(1))) + "</button>";
    }).join("") + "</div></div>";
  }

  // temperature and humidity of today in the tiles, from the timeline
  function loadSparks(force) {
    if (!S.header.timeline || !S.token || (!force && Date.now() - S.sparksAt < 10 * 60000)) { return; }
    S.sparksAt = Date.now();
    api("api/sparks").then(function (data) {
      if (JSON.stringify(data) === JSON.stringify(S.sparks)) { return; }
      S.sparks = data || {};
      if (S.tab !== "history") { renderContent(); }
    }).catch(function () { /* no timeline */ });
  }
  function climateOf(tile) {
    var st = tile.state || {};
    var temp = tile.kind === "thermostat" ? st.current : st.temperature;
    return { temp: temp === null ? undefined : temp, humidity: st.humidity === null ? undefined : st.humidity };
  }
  function sparkOf(id, key) { var sp = S.sparks[id]; return sp && sp[key]; }
  // comfort colour: cold blue, pleasant teal, warm amber
  function tempColor(v) { return v === undefined ? "var(--mu)" : v < 18 ? "#5AA9FF" : v <= 23.5 ? "#3DDBB8" : "#FF8A3D"; }
  // rising or falling over the last two hours, with the current value as end
  function tempArrow(points, now) {
    var known = (points || []).map(function (v, i) { return [i, v]; }).filter(function (p) { return p[1] !== null && p[1] !== undefined; });
    if (!known.length || now === undefined) { return ""; }
    var hour = new Date().getHours(), before = null;
    known.forEach(function (p) { if (p[0] <= hour - 2) { before = p[1]; } });
    if (before === null) { return ""; }
    var diff = now - before;
    return diff >= 0.4 ? "↑" : diff <= -0.4 ? "↓" : "";
  }
  function sparkSvg(points, color, current) {
    var pts = (points || []).map(function (v, i) { return [i, v]; }).filter(function (p) { return p[1] !== null && p[1] !== undefined; });
    if (current !== undefined && pts.length) { pts.push([Math.min(23, new Date().getHours() + new Date().getMinutes() / 60), current]); }
    if (pts.length < 2) { return ""; }
    var vals = pts.map(function (p) { return p[1]; });
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), pad = Math.max(0.6, (hi - lo) * 0.2);
    lo -= pad; hi += pad;
    var w = 200, h = 60, line = "";
    pts.forEach(function (p, i) { line += (i ? "L" : "M") + (p[0] / 23 * w).toFixed(1) + "," + (h - (p[1] - lo) / (hi - lo) * h).toFixed(1); });
    var end = pts[pts.length - 1], area = line + "L" + (end[0] / 23 * w).toFixed(1) + "," + h + "L" + (pts[0][0] / 23 * w).toFixed(1) + "," + h + "Z";
    var id = "s" + Math.random().toString(36).slice(2, 8);
    return '<svg class="spark" viewBox="0 0 ' + w + " " + h + '" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="' + color + '" stop-opacity=".32"/><stop offset="1" stop-color="' + color + '" stop-opacity="0"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#' + id + ')"/><path d="' + line + '" fill="none" stroke="' + color + '" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/>' +
      '<circle cx="' + (end[0] / 23 * w).toFixed(1) + '" cy="' + (h - (end[1] - lo) / (hi - lo) * h).toFixed(1) + '" r="3" fill="' + color + '" vector-effect="non-scaling-stroke"/></svg>';
  }
  function climateTileBody(id, tile, look, editState) {
    var c = climateOf(tile), st = tile.state, humidOnly = c.temp === undefined;
    var main = humidOnly ? (c.humidity === undefined ? "–" : Math.round(c.humidity) + "<small>%</small>") : num(c.temp) + "<small>°</small>";
    var key = humidOnly ? "h" : "t", pts = sparkOf(id, key), now = humidOnly ? c.humidity : c.temp;
    var color = humidOnly ? "#5AA9FF" : tile.kind === "thermostat" && look.cls === "heat" ? "#FF8A3D" : tempColor(c.temp);
    var arrow = humidOnly ? "" : tempArrow(pts, now), thermostat = tile.kind === "thermostat" && st.target !== undefined;
    var side = !humidOnly && c.humidity !== undefined ? I("drop", 14) + Math.round(c.humidity) + " %" : "";
    var steps = thermostat && !editState ? '<div class="tsteps"><span class="round" data-step="-1" data-sid="' + esc(id) + '">−</span><span class="tval">' + num(st.target) + "°<small>" + esc(t("target")) + '</small></span><span class="round" data-step="1" data-sid="' + esc(id) + '">+</span></div>' : "";
    return sparkSvg(pts, color, now) + '<div class="ctop"><div class="n">' + esc(tile.name) + "</div>" + (side ? '<span class="cside">' + side + "</span>" : "") + "</div>" +
      '<div class="cval"><span class="big" style="color:' + (humidOnly ? "var(--tx)" : color) + '">' + main + "</span>" + (arrow ? '<span class="arrow">' + arrow + "</span>" : "") +
      (thermostat ? '<span class="tgt">' + esc(t("target") + " " + num(st.target) + "°") + "</span>" : "") + "</div>" + steps;
  }

  // ---------- DOIF inputs (readingList/setList) ----------
  function inputsLine(tile) {
    var vals = (tile.state && tile.state.values) || {};
    return (tile.inputs || []).filter(function (i) { return vals[i.name] !== undefined && vals[i.name] !== ""; }).slice(0, 3)
      .map(function (i) { return i.name + " " + vals[i.name]; }).join(" · ");
  }
  function inputsHtml(tile) {
    var vals = (tile.state && tile.state.values) || {}, id = tile.id;
    return '<div class="group"><div class="label">' + esc(t("inputsHint")) + '</div><div class="inputs">' + (tile.inputs || []).map(function (i, n) {
      var v = vals[i.name] === undefined ? "" : String(vals[i.name]), ctl = "", key = esc(i.name);
      if (i.type === "slider") {
        var num = isNaN(parseFloat(v)) ? i.min : parseFloat(v);
        ctl = '<input type="range" data-inslider="' + key + '" min="' + i.min + '" max="' + i.max + '" step="' + i.step + '" value="' + num + '"><span class="inval" id="inval' + n + '">' + esc(String(num)) + "</span>";
      } else if (i.type === "select" || i.type === "switch") {
        ctl = '<div class="seg">' + i.options.map(function (o) { return '<button class="' + (o === v ? "on" : "") + '" data-inopt="' + key + '" data-val="' + esc(o) + '">' + esc(o) + "</button>"; }).join("") + "</div>";
      } else if (i.type === "time") {
        ctl = '<input type="time" data-intime="' + key + '" value="' + esc(v.slice(0, 5)) + '">';
      } else if (i.type === "button") {
        ctl = '<button class="pill" data-inbtn="' + key + '">' + esc(t("inputRun")) + "</button>";
      } else {
        ctl = '<input type="text" maxlength="100" data-intext="' + key + '" value="' + esc(v) + '"><button class="pill" data-intextset="' + key + '">' + esc(t("inputSet")) + "</button>";
      }
      return '<div class="inrow"><div class="inname">' + esc(i.name) + '</div><div class="inctl" data-inidx="' + n + '">' + ctl + "</div></div>";
    }).join("") + "</div></div>";
  }
  function setInput(name, value) {
    var tile = S.tiles[S.sheet && S.sheet.id]; if (!tile) { return; }
    var values = JSON.parse(JSON.stringify(tile.state.values || {}));
    values[name] = value;
    act(tile.id, "input", { name: name, value: value }, { values: values });
  }

  // ---------- music players ----------
  // covers come through fhempy (api/image), the tablet needs the token for it
  var images = {};
  function mediaLine(st) { return [st.title, st.artist || st.station].filter(Boolean).join(" · "); }
  function imageUrl(id, key, preset) {
    if (!key) { return ""; }
    var cached = images[key];
    if (cached && cached !== "loading" && cached !== "failed") { return cached; }
    if (!cached) {
      images[key] = "loading";
      // f=2: browsers cached covers cut off by older fhempy versions for a day
      fetch("api/image?id=" + encodeURIComponent(id) + "&v=" + key + "&f=2" + (preset ? "&preset=" + preset : ""), { headers: { Authorization: "Bearer " + S.token } })
        .then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.blob(); })
        .then(function (b) {
          images[key] = URL.createObjectURL(b);
          Array.prototype.forEach.call(document.querySelectorAll('[data-img="' + key + '"]'), function (el) { el.src = images[key]; el.classList.add("ok"); });
        })
        .catch(function () { images[key] = "failed"; });
    }
    return "";
  }
  function coverImg(id, key, cls, preset) {
    if (!key) { return ""; }
    var src = imageUrl(id, key, preset);
    return '<img class="' + cls + (src ? " ok" : "") + '" data-img="' + key + '" alt=""' + (src ? ' src="' + src + '"' : "") + ">";
  }
  function initials(name) {
    var words = String(name || "").replace(/[^\w\u00C0-\u024F ]+/g, " ").trim().split(/\s+/);
    return (words.length > 1 ? words[0].charAt(0) + words[1].charAt(0) : String(name || "").slice(0, 2)).toUpperCase();
  }
  function mediaTileBody(id, tile, look, editState) {
    var st = tile.state, playBtn = editState ? "" : '<span class="mplay" data-mplay="' + esc(id) + '" aria-label="' + esc(t("playPause")) + '">' + I(st.playing ? "pause" : "play", 26) + "</span>";
    var logo = st.logo ? coverImg(id, st.logo, "mlogo", "logo") : "";
    var thumb = st.art ? '<div class="mthumb">' + I("music") + coverImg(id, st.art, "mimg") + logo + "</div>" : '<div class="ic">' + I("music") + "</div>";
    return coverImg(id, st.art, "mcover") + thumb + '<div class="mtext"><div class="n">' + esc(tile.name) + '</div><div class="s">' + esc(look.sub) + "</div></div>" + playBtn;
  }
  function mediaSheet(tile) {
    var st = tile.state, f = tile.media || {}, id = tile.id;
    var art = st.art ? coverImg(id, st.art, "bigcover") + (st.logo ? coverImg(id, st.logo, "mlogo", "logo") : "") : "";
    var left = '<div class="mart">' + (art || '<div class="noart">' + I("music", 64) + "</div>") + "</div>";
    var body = '<div class="group mnow"><b>' + esc(st.title || (st.on ? t("nothingPlays") : t("off"))) + "</b>" +
      (st.artist ? "<span>" + esc(st.artist) + "</span>" : "") + (st.album || st.station ? '<span class="mu">' + esc(st.album || st.station) + "</span>" : "") + "</div>";
    body += '<div class="group mctl">' + (f.prev ? '<button class="round" data-media="prev" aria-label="' + esc(t("prevTrack")) + '">' + I("skipprev", 28) + "</button>" : "") +
      '<button class="round big' + (st.playing ? " on" : "") + '" data-media="toggle" aria-label="' + esc(t("playPause")) + '">' + I(st.playing ? "pause" : "play", 34) + "</button>" +
      (f.next ? '<button class="round" data-media="next" aria-label="' + esc(t("nextTrack")) + '">' + I("skipnext", 28) + "</button>" : "") + "</div>";
    if (f.volume) {
      var v = Math.round(st.volume || 0);
      body += '<div class="group mvol">' + I("vol", 22) + '<input type="range" id="mvol" min="0" max="100" step="1" value="' + v + '" aria-label="' + esc(t("volume")) + '"><span id="mvoltxt">' + v + "</span></div>";
    }
    var presets = st.presets || [];
    if (presets.length) {
      body += '<div class="group"><div class="label">' + esc(t("presets")) + '</div><div class="presets">' + presets.map(function (p) {
        var logo = p.art ? coverImg(id, p.art, "plogo", p.n) : "";
        return '<button class="preset' + (st.channel === p.n && st.on ? " on" : "") + '" data-preset="' + p.n + '"><span class="plg"><span class="pini">' + esc(initials(p.name)) + "</span>" + logo + '</span><span class="pn"><small>' + p.n + "</small>" + esc(p.name) + "</span></button>";
      }).join("") + "</div></div>";
    }
    if (f.power) {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.on ? " on" : "") + '" data-do="on">' + I("power", 20) + " " + esc(t("on")) + '</button><button class="pill' + (!st.on ? " on" : "") + '" data-do="off">' + esc(t("off")) + "</button></div></div>";
    }
    return { left: left, body: body };
  }

  function tileLook(tile) {
    var st = tile.state || {}, k = tile.kind, cls = "", sub = "", icon = KIND_ICON[k] || "power", bar = null;
    if (k === "light" || k === "dimmer") {
      if (st.on) { cls = "light"; sub = t("on") + (st.level !== undefined && k === "dimmer" ? " · " + st.level + " %" : ""); bar = k === "dimmer" ? st.level : null; } else { sub = t("off"); }
      if (st.fan && st.fan.mode && st.fan.mode !== "off") { sub += " · " + t("fan") + " " + fanText({ mode: st.fan.mode }); }
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
    } else if (k === "inputs") {
      sub = inputsLine(tile) || st.state || "";
    } else if (k === "fan") {
      icon = "fan"; if (st.on) { cls = "fanon"; } sub = st.on ? fanText(st) : t("off");
    } else if (k === "media") {
      if (st.playing) { cls = "playing"; sub = mediaLine(st) || t("playing"); } else { sub = st.paused ? [t("paused"), mediaLine(st)].filter(Boolean).join(" · ") : st.on ? t("idle") : t("off"); }
    }
    return { cls: cls, sub: sub, icon: icon, bar: bar };
  }

  function tileHtml(id, editState) {
    var tile = S.tiles[id]; if (!tile) { return ""; }
    var look = tileLook(tile), wide = tile.kind === "thermostat" || tile.kind === "media";
    var body, climate = tile.kind === "thermostat" || tile.kind === "temperature" || tile.kind === "humidity";
    if (climate) {
      body = climateTileBody(id, tile, look, editState);
    } else if (tile.kind === "media") {
      body = mediaTileBody(id, tile, look, editState);
    } else {
      body = '<div class="ic' + (TAP_TOGGLES[tile.kind] ? " sw" : "") + '">' + (tile.kind === "blind" ? winMini(tile.state.position) : I(look.icon)) + '</div><div><div class="n">' + esc(tile.name) + '</div><div class="s">' + esc(look.sub) + "</div></div>";
    }
    var extra = "";
    if (look.bar !== null && look.bar !== undefined) { extra += '<div class="bar" style="width:' + look.bar + '%"></div>'; }
    if (tile.state.fan && tile.state.fan.mode && tile.state.fan.mode !== "off" && !editState) { extra += '<div class="fanbadge">' + I("fan", 18) + "</div>"; }
    if (timerLeft(tile) && !editState) { extra += '<div class="tbadge">' + I("timer", 15) + " " + esc(timerText(timerLeft(tile))) + "</div>"; }
    if (tile.color && tile.state.on && (tile.state.rgb || tile.state.ct) && !editState) { extra += '<div class="cdot" style="background:' + lampColor(tile.state) + '"></div>'; }
    if (tile.state.battery_low && !editState) { extra += '<div class="badge">' + I("battery", 18) + "</div>"; }
    if (editState) {
      extra += '<div class="edit" data-edit="' + (editState === "hidden" ? "show" : "hide") + '">' + I(editState === "hidden" ? "plus" : "x") + "</div>";
    }
    return '<button class="tile ' + look.cls + (climate ? " climate" : "") + (tile.kind === "media" ? " media" + (tile.state.art ? " hascover" : "") : "") + (tile.kind === "dimmer" || tile.kind === "blind" || tile.kind === "fan" ? " slidable" : "") + (wide ? " wide" : "") + (S.pending[id] ? " pending" : "") + (editState === "hidden" ? " hiddenTile" : "") +
      '" data-tile="' + esc(id) + '">' + body + extra + "</button>";
  }

  function updateTile(id) {
    if (S.sliding && press && press.id === id) { return; }
    var el = app.querySelector('[data-tile="' + cssEsc(id) + '"]');
    if (el) {
      var div = document.createElement("div");
      div.innerHTML = tileHtml(id, S.edit ? editStateOf(id) : null);
      if (div.firstChild) { el.parentNode.replaceChild(div.firstChild, el); }
    }
    if (S.tab === "home" && !(tdrag && tdrag.active)) { renderContent(); }
  }
  function cssEsc(s) { return String(s).replace(/["\\]/g, "\\$&"); }
  function editStateOf(id) { return (layout().hidden_tiles || []).indexOf(id) >= 0 ? "hidden" : "shown"; }

  // ---------- timers: switch off in 15 min ... (FHEM runs them) ----------
  function timerLeft(tile) {
    if (!tile.timer || !tile.state.on) { return 0; }
    var left = tile.timer * 1000 - Date.now();
    return left > 0 ? left : 0;
  }
  function timerText(ms) {
    var m = Math.max(1, Math.ceil(ms / 60000));
    return m < 60 ? m + " min" : Math.floor(m / 60) + ":" + two(m % 60) + " h";
  }
  function timerHtml(tile) {
    if (S.tablet && S.tablet.readonly) { return ""; }
    var left = timerLeft(tile), opts = [[15, "min15"], [30, "min30"], [60, "h1"], [120, "h2"]];
    var html = '<div class="group"><div class="label tl">' + I("timer", 16) + " " + esc(t(tile.state.on ? "timerOff" : "timerOn")) +
      (left ? '<span class="tleft">' + esc(t("timerUntil", { t: clockText(new Date(tile.timer * 1000)) })) + "</span>" : "") + '</div><div class="actions timers">';
    html += opts.map(function (o) { return '<button class="pill" data-timer="' + o[0] + '">' + esc(t(o[1])) + "</button>"; }).join("");
    if (left) { html += '<button class="pill" data-timer="0">' + esc(t("timerStop")) + "</button>"; }
    return html + "</div></div>";
  }
  function setTimer(id, minutes) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var tile = S.tiles[id]; if (!tile) { return; }
    if (minutes > 0) { tile.timer = Math.round(Date.now() / 1000) + minutes * 60; tile.state.on = true; } else { delete tile.timer; }
    send({ type: "action", action: "timer", id: id, value: minutes });
    updateTile(id); if (S.sheet && S.sheet.id === id) { renderSheet(); }
  }
  function tickTimers() {
    Object.keys(S.tiles).forEach(function (id) {
      var tile = S.tiles[id];
      if (tile.timer) { updateTile(id); if (!timerLeft(tile) && tile.timer * 1000 < Date.now() - 120000) { delete tile.timer; } }
    });
  }

  // optimistic: show the new state at once, the server confirms within 3 s
  function act(id, action, value, optimistic) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var tile = S.tiles[id];
    S.last[id] = { action: action, value: value, optimistic: optimistic };
    if (tile && optimistic) {
      var before = JSON.parse(JSON.stringify(tile.state));
      // thermostats on batteries take minutes, a value that was already set sends no event
      var tell = tile.kind !== "thermostat" && Object.keys(optimistic).some(function (k) { return JSON.stringify(before[k]) !== JSON.stringify(optimistic[k]); });
      clearTimeout(S.pending[id]);
      Object.keys(optimistic).forEach(function (k) { tile.state[k] = optimistic[k]; });
      S.pending[id] = setTimeout(function () {
        if (S.pending[id]) {
          tile.state = before; delete S.pending[id]; updateTile(id); if (S.sheet && S.sheet.id === id) { renderSheet(); }
          if (tell) { showToast(t("noReaction", { name: tile.name }), id); }
        }
      }, 4000);
      updateTile(id);
    }
    send({ type: "action", id: id, action: action, value: value });
    used(id);
  }

  function tap(id) {
    var tile = S.tiles[id]; if (!tile) { return; }
    if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not allowed */ } }
    if (!TAP_TOGGLES[tile.kind]) { openSheet(id); return; }
    var st = tile.state;
    if (tile.kind === "fan") {
      act(id, "toggle", null, st.on ? { on: false, mode: "off", percent: 0 } : { on: true, mode: "medium", percent: 66 });
    } else if (tile.kind === "blind") {
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
      (S.connected ? "" : '<div class="banner">' + esc(t("connLost")) + "</div>") +
      (S.newBuild ? '<div class="banner update"><span>' + esc(t("newVersion")) + '</span><button class="pill" data-reload="1">' + I("check", 18) + " " + esc(t("reloadNow")) + "</button></div>" : "");
    document.body.classList.toggle("offline", !S.connected);
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
      chips += '<button class="chip" data-weather="1">' + I(weatherIcon(h.weather.condition)) + " " + num(h.weather.temperature, 0) + '° <span class="sub">' + esc(h.weather.condition || "") +
        (h.weather.high !== null && h.weather.high !== undefined ? " · " + num(h.weather.low, 0) + "° / " + num(h.weather.high, 0) + "°" : "") + "</span></button>";
    }
    if (h.presence) {
      var home = h.presence.home || [];
      var avs = home.slice(0, 4).map(function (p, i) { return '<div class="av" style="background:' + ["#FFB547", "#5AA9FF", "#3DDBB8", "#9B8CFF"][i % 4] + '">' + esc(p.initial) + "</div>"; }).join("");
      chips += '<button class="chip" data-people="1">' + (avs ? '<div class="avs">' + avs + "</div>" : I("home")) + ' <span class="lbl">' + esc(home.length ? t("atHome", { n: home.length }) : t("nobody")) + "</span></button>";
    }
    var warn = warningText();
    if (warn) { chips += '<button class="chip warn" data-go="home">' + I("win") + " " + esc(warn) + "</button>"; }
    if ((h.battery || []).length) { chips += '<button class="chip warn" data-batteries="1" aria-label="' + esc(t("batteriesTitle")) + '">' + I("battery") + " " + h.battery.length + "</button>"; }
    chips += '<button class="iconbtn" data-settings="1">' + I("gear") + "</button>";
    el.innerHTML = '<div class="top"><div><div class="clock">' + clockText(now) + '</div><div class="date">' + esc(greeting(now) + " · " + dateText(now)) + '</div></div><div class="chips">' + chips + "</div></div>";
  }
  // open windows and running devices only of the rooms this tablet shows
  function shownIds() {
    if (!(layout().hidden_rooms || []).length) { return null; }
    var ids = {};
    visibleRooms().forEach(function (r) { r.tiles.forEach(function (id) { ids[id] = 1; }); });
    return ids;
  }
  function shownList(list) {
    var ids = shownIds();
    return (list || []).filter(function (x) { return !ids || ids[x.id]; });
  }
  function warningText() {
    var open = shownList(S.header && S.header.open);
    if (!open.length) { return ""; }
    if (open.length <= 3) { return t("openNames", { names: open.map(function (o) { return shortName(o.name); }).join(", ") }); }
    return t("openCount", { n: open.length });
  }
  // "Fenster Garten" -> "Garten" in the chip, when the rest is unique
  function shortName(name) {
    var s = String(name).replace(/^(fenster|window|tür|door|kontakt|contact)[\s_-]+/i, "");
    return s || name;
  }
  function weatherIcon(cond, day) {
    cond = String(cond || "").toLowerCase();
    if (/regen|rain|schauer|shower|drizzle|niesel|gewitter|thunder/.test(cond)) { return "rain"; }
    if (/klar|sonn|clear|sunny/.test(cond)) { return day || isDay() ? "sun" : "moon"; }
    return "cloud";
  }

  function renderTabs() {
    var el = document.getElementById("tabs"); if (!el) { return; }
    var tabs = [{ id: "home", name: t("home") }];
    visibleRooms().forEach(function (r) {
      var openHere = (S.header.open || []).some(function (o) { return o.room === r.name; });
      tabs.push({ id: "room:" + r.name, name: r.name, dot: openHere });
    });
    if (seesTimeline()) { tabs.push({ id: "history", name: t("history") }); } else if (S.tab === "history") { S.tab = "home"; }
    el.innerHTML = tabs.map(function (tb) {
      return '<button class="tab' + (tb.id === S.tab ? " on" : "") + '" data-tab="' + esc(tb.id) + '">' + esc(tb.name) + (tb.dot ? '<span class="dot"></span>' : "") + "</button>";
    }).join("");
    var on = el.querySelector(".tab.on"); if (on && on.scrollIntoView) { on.scrollIntoView({ inline: "nearest", block: "nearest" }); }
  }

  function renderContent() {
    var el = document.getElementById("content"); if (!el) { return; }
    var top = el.scrollTop;
    if (S.arrange) { el.innerHTML = arrangeHtml(); } else if (S.tab === "home") { el.innerHTML = homeHtml(); } else if (S.tab === "history") { el.innerHTML = historyHtml(); } else { el.innerHTML = roomHtml(roomByName(S.tab.slice(5))); }
    el.scrollTop = top;
    S.shownTab = S.tab;
  }

  function leaveHtml() {
    var h = S.header, open = shownList(h.open), running = shownList(h.running), rows = "";
    open.forEach(function (o) {
      rows += '<div class="row"><div class="ic" style="background:rgba(255,138,61,.16);color:var(--amber2)">' + I(o.door ? "door" : "win") + '</div><div class="t"><b>' + esc(o.name) + "</b><span>" +
        esc([o.room, (o.tilted ? t("tilted") : t("open")) + " " + since(o.since)].filter(Boolean).join(" · ")) + "</span></div></div>";
    });
    var wasted = heatingOpenRooms();
    if (wasted.length) {
      rows += '<div class="row"><div class="ic" style="background:rgba(255,90,95,.16);color:var(--red)">' + I("thermo") + '</div><div class="t"><b>' + esc(t("heatingOpen")) + "</b><span>" + esc(wasted.join(", ")) + "</span></div></div>";
    }
    var lights = running.filter(function (r) { return r.kind === "light" || r.kind === "dimmer"; });
    if (lights.length) {
      var rooms = []; lights.forEach(function (l) { if (l.room && rooms.indexOf(l.room) < 0) { rooms.push(l.room); } });
      rows += '<div class="row"><div class="ic" style="background:rgba(255,181,71,.16);color:var(--amber)">' + I("bulb") + '</div><div class="t"><b>' +
        esc(lights.length === 1 ? lights[0].name : t("lightsOn", { n: lights.length })) + "</b><span>" + esc(rooms.join(", ")) + "</span></div></div>";
    }
    running.filter(function (r) { return r.kind !== "light" && r.kind !== "dimmer"; }).forEach(function (r) {
      rows += '<div class="row"><div class="ic" style="background:rgba(155,140,255,.16);color:var(--violet)">' + I("bolt") + '</div><div class="t"><b>' + esc(r.name) + "</b><span>" +
        esc([r.room, t("on") + (r.power ? " · " + watt(r.power) : ""), r.keep_on && !(S.tablet && S.tablet.arrange) ? t("staysOn") : ""].filter(Boolean).join(" · ")) + "</span></div>" +
        (S.tablet && S.tablet.arrange ? '<button class="pill keep' + (r.keep_on ? " kept" : "") + '" data-keepon="' + esc(r.id) + '">' + (r.keep_on ? I("check", 18) + " " + esc(t("staysOn")) : esc(t("keepBtn"))) + "</button>" : "") +
        '<button class="pill" data-off="' + esc(r.id) + '">' + esc(t("off")) + "</button></div>";
    });
    var door = place() === "door";
    var title = door ? t("beforeLeave") : t("nowOn");
    if (!rows) {
      return '<div class="leave"><h2>' + esc(title) + '</h2><div class="allclear">' + I("check", 26) + " " + esc(t("allClosed")) + "</div></div>";
    }
    var count = running.filter(function (r) { return !r.keep_on; }).length;
    return '<div class="leave"><h2>' + esc(title) + "</h2>" + (door ? '<div class="lead">' + esc(t("stillOpen")) + "</div>" : "") + rows +
      (count ? '<div class="actions"><button class="pill primary" data-alloff="" data-ids="' + esc(running.filter(function (r) { return !r.keep_on; }).map(function (r) { return r.id; }).join("\n")) + '">' + I("power", 20) + " " + esc(t("allOffN", { n: count })) + "</button></div>" : "") + "</div>";
  }

  // rooms where a thermostat heats while a window is open
  function heatingOpenRooms() {
    var openRooms = shownList(S.header.open).map(function (o) { return o.room; }), result = [];
    visibleRooms().forEach(function (r) {
      if (openRooms.indexOf(r.name) < 0) { return; }
      var heats = r.tiles.some(function (id) { var tl = S.tiles[id]; return tl && tl.kind === "thermostat" && tl.state.target > tl.state.current + 0.3; });
      if (heats && result.indexOf(r.name) < 0) { result.push(r.name); }
    });
    return result;
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

  // room cards of the home page: own order and hidden cards, independent of the room order (layout key HOME)
  var HOME = "__home__";
  function homeRooms(withHidden) {
    var lay = layout(), hidden = lay.hidden_tiles || [], manual = (lay.tile_order || {})[HOME] || [];
    var rooms = visibleRooms().filter(function (r) { return withHidden || hidden.indexOf("room:" + r.name) < 0; });
    if (manual.length) {
      var base = rooms.slice();
      rooms.sort(function (a, b) {
        var ia = manual.indexOf("room:" + a.name), ib = manual.indexOf("room:" + b.name);
        return (ia < 0 ? 1000 + base.indexOf(a) : ia) - (ib < 0 ? 1000 + base.indexOf(b) : ib);
      });
    }
    return rooms;
  }
  function roomCardHtml(room, editState) {
    var ids = roomTiles(room), lights = 0, temp = null, open = 0, other = 0, tempId = null, humid = null, co2 = null;
    ids.forEach(function (id) {
      var tile = S.tiles[id], st = tile.state;
      if (tempId === null && (tile.kind === "thermostat" || tile.kind === "temperature") && climateOf(tile).temp !== undefined) { tempId = id; }
      if (humid === null && st.humidity !== undefined && st.humidity !== null) { humid = st.humidity; }
      if ((tile.kind === "light" || tile.kind === "dimmer") && st.on) { lights++; } else if ((tile.kind === "switch" || tile.kind === "outlet") && st.on) { other++; }
      if (temp === null && tile.kind === "thermostat" && st.current !== undefined) { temp = st.current; }
      if (temp === null && tile.kind === "temperature" && st.temperature !== undefined) { temp = st.temperature; }
      if (tile.kind === "contact" && st.closed === false) { open++; }
      if (st.co2 !== undefined && st.co2 !== null && (co2 === null || st.co2 > co2)) { co2 = st.co2; }
    });
    var facts = "", climate = "";
    if (temp !== null) {
      var pts = tempId && sparkOf(tempId, "t"), arrow = tempArrow(pts, temp), color = tempColor(temp);
      climate = (pts ? sparkSvg(pts, color, temp) : "") + '<div class="rtemp" style="color:' + color + '">' + num(temp) + "°" + (arrow ? '<span class="arrow">' + arrow + "</span>" : "") +
        (humid !== null ? '<span class="rhum">' + Math.round(humid) + " %</span>" : "") + "</div>";
    }
    // stale air: humid or much CO2, not while a window is open already
    if (((humid !== null && humid >= 65) || (co2 !== null && co2 >= 1400)) && !open) { facts += '<span class="fact warn">' + esc(t("airOut")) + (co2 !== null && co2 >= 1400 ? " · " + Math.round(co2) + " ppm" : "") + "</span>"; }
    if (lights) { facts += '<span class="fact on">' + esc(lights === 1 ? t("lightOn") : t("lightsOn", { n: lights })) + "</span>"; }
    if (other) { facts += '<span class="fact on">' + esc(other === 1 ? t("deviceOn") : t("devicesOn", { n: other })) + "</span>"; }
    if (open) { facts += '<span class="fact warn">' + esc(t("doorsOpen", { n: open })) + "</span>"; }
    if (editState) {
      return '<div class="tile roomcard' + (lights ? " light" : "") + (editState === "hidden" ? " hiddenTile" : "") + '" data-tile="room:' + esc(room.name) + '">' + climate + '<div class="n">' + esc(room.name) + '</div><div class="facts">' + facts + "</div>" +
        '<div class="edit" data-edit="' + (editState === "hidden" ? "show" : "hide") + '">' + I(editState === "hidden" ? "plus" : "x") + "</div></div>";
    }
    return '<button class="tile roomcard' + (lights ? " light" : "") + '" data-roompop="' + esc(room.name) + '">' + climate + '<div class="n">' + esc(room.name) + '</div><div class="facts">' + facts + "</div></button>";
  }

  function homeHtml() {
    var rooms = visibleRooms();
    if (!rooms.length) { return '<div class="empty">' + esc(t("noDevices")) + "</div>"; }
    var left = routinesHtml() + leaveHtml() + calendarHtml() + energyHtml() + latelyHtml();
    var right;
    if (S.edit) {
      var hiddenT = layout().hidden_tiles || [], all = homeRooms(true);
      var shown = all.filter(function (r) { return hiddenT.indexOf("room:" + r.name) < 0; }), gone = all.filter(function (r) { return hiddenT.indexOf("room:" + r.name) >= 0; });
      right = '<div class="edithint">' + esc(t("editHint")) + '</div><div class="grid">' + shown.map(function (r) { return roomCardHtml(r, "shown"); }).join("") + "</div>" +
        (gone.length ? '<div class="section">' + esc(t("hiddenTiles")) + '</div><div class="grid">' + gone.map(function (r) { return roomCardHtml(r, "hidden"); }).join("") + "</div>" : "") +
        '<div class="actions"><button class="pill primary" data-editdone="1">' + I("check", 20) + " " + esc(t("editDone")) + "</button></div>";
    } else {
      right = '<div class="grid">' + homeRooms(false).map(function (r) { return roomCardHtml(r); }).join("") + "</div>";
    }
    return statusChipsHtml() + '<div class="home split"><div style="display:flex;flex-direction:column;gap:16px">' + left + "</div><div>" + right + "</div></div>";
  }

  function scenesHtml(room) {
    var scenes = S.scenes.filter(function (s) { return s.room === room.name; });
    var on = roomTiles(room).filter(function (id) { var tl = S.tiles[id]; return ["light", "dimmer", "switch", "outlet"].indexOf(tl.kind) >= 0 && tl.state.on && !tl.keep_on; }).length;
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
      html += '<div class="edithint">' + esc(t("editHint")) + "</div>";
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
      if (S.tab === "home" || S.tab === "history" || S.tab.indexOf("room:") === 0) { renderContent(); }
    }).catch(function () { S.timeline[day] = { at: Date.now(), data: null }; });
  }
  function entryTime(e) { var d = new Date(e.ts * 1000); return clockText(d); }
  function entryColor(e) {
    return { security: "#FF8A3D", alert: "#FF5A5F", presence: "#34D399", light: "#FFB547", climate: "#5AA9FF", energy: "#9B8CFF", device: "#9B8CFF" }[e.category] || "#8C95A5";
  }
  // a timeline device exists and FHEM allows this tablet to see it (set tablet_timeline)
  function seesTimeline() { return !!S.header.timeline && !(S.tablet && S.tablet.timeline === false); }
  function happenedHtml(roomName) {
    if (!seesTimeline()) { return ""; }
    var day = today(); loadDay(day);
    var data = S.timeline[day] && S.timeline[day].data; if (!data || !data.entries) { return ""; }
    var list = data.entries.filter(function (e) { return ("," + (e.room || "") + ",").indexOf("," + roomName + ",") >= 0; }).slice(-6).reverse();
    if (!list.length) { return ""; }
    return '<div class="section">' + esc(t("happened")) + '</div><div class="leave" style="padding:10px 22px">' + list.map(function (e) {
      return '<div class="row" style="padding:10px 0"><span style="color:var(--mu);width:46px;font-variant-numeric:tabular-nums">' + entryTime(e) + '</span><span style="width:9px;height:9px;border-radius:50%;background:' + entryColor(e) + '"></span><div class="t"><span style="color:var(--tx);font-size:15px">' + esc(e.text) + "</span></div></div>";
    }).join("") + "</div>";
  }

  // the last events of the whole home, today and if it was quiet also yesterday
  function latelyHtml() {
    if (!seesTimeline()) { return ""; }
    var day = today(), d = new Date(), y = new Date(d.getFullYear(), d.getMonth(), d.getDate() - 1);
    var yday = y.getFullYear() + "-" + two(y.getMonth() + 1) + "-" + two(y.getDate());
    loadDay(day);
    var data = S.timeline[day] && S.timeline[day].data; if (!data || !data.entries) { return ""; }
    var list = data.entries.slice(-6).reverse().map(function (e) { return [e, false]; });
    if (list.length < 6) {
      loadDay(yday);
      var old = S.timeline[yday] && S.timeline[yday].data;
      if (old && old.entries) { list = list.concat(old.entries.slice(-(6 - list.length)).reverse().map(function (e) { return [e, true]; })); }
    }
    if (!list.length) { return ""; }
    return '<div class="leave lately"><div class="section"><span>' + esc(t("lately")) + '</span><button class="linkbtn" data-tab="history">' + esc(t("showAll")) + " " + I("chev", 14) + "</button></div>" + list.map(function (x) {
      var e = x[0], room = e.room ? String(e.room).split(",")[0] : "";
      return '<div class="lrow"><span class="lt">' + (x[1] ? esc(t("yesterday")) + " " : "") + entryTime(e) + '</span><span class="ld" style="background:' + entryColor(e) + '"></span><span class="lx">' + esc(e.text) + (e.count > 1 ? " · " + e.count + "×" : "") + "</span>" + (room ? '<span class="fact">' + esc(room) + "</span>" : "") + "</div>";
    }).join("") + "</div>";
  }

  function historyHtml() {
    if (!seesTimeline()) { return '<div class="empty">' + esc(t("noTimeline")) + "</div>"; }
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
    var marks = [];
    (tr.points || []).forEach(function (p, i) {
      var v = pts[i]; if (v === null || isNaN(v)) { return; }
      var ts = p && typeof p === "object" ? p[0] : null;
      marks.push({ fx: i / (n - 1), fy: (h - (v - lo) / (hi - lo) * h) / (h + 4), label: ts ? clockText(new Date(ts * 1000)) : two(Math.round(i * 24 / n)) + ":00", text: num(v) + (tr.unit ? " " + tr.unit : "") });
    });
    return '<div class="leave" style="padding:16px 20px"><div class="section" style="margin:0 0 10px"><span>' + esc(tr.text) + '</span><span style="text-transform:none;letter-spacing:0;color:var(--tx)">' + esc(num(last) + (tr.unit ? " " + tr.unit : "")) + "</span></div>" +
      chartWrap("trend:" + (tr.device || "") + ":" + (tr.reading || tr.text), marks, col, '<svg viewBox="0 0 ' + w + " " + (h + 4) + '" style="width:100%;height:84px;display:block" preserveAspectRatio="none"><path d="' + path + '" fill="none" stroke="' + col + '" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>') + "</div>";
  }

  // charts: touch or hover shows the value at that time
  var charts = {};
  function chartWrap(key, marks, color, svg) {
    charts[key] = { marks: marks, color: color };
    return '<div class="chart" data-chart="' + esc(key) + '">' + svg + '<div class="cline"></div><div class="cdot" style="background:' + color + '"></div><div class="ctip"></div></div>';
  }
  function chartShow(el, clientX) {
    var c = charts[el.getAttribute("data-chart")]; if (!c || !c.marks.length) { return; }
    var r = el.getBoundingClientRect(), fx = (clientX - r.left) / r.width, best = c.marks[0];
    c.marks.forEach(function (m) { if (Math.abs(m.fx - fx) < Math.abs(best.fx - fx)) { best = m; } });
    var svg = el.querySelector("svg"), sh = svg ? svg.getBoundingClientRect().height : r.height;
    var px = best.fx * r.width, py = best.fy * sh;
    el.classList.add("on");
    el.querySelector(".cline").style.left = px + "px";
    var dot = el.querySelector(".cdot"); dot.style.left = px + "px"; dot.style.top = py + "px";
    var tip = el.querySelector(".ctip"); tip.innerHTML = "<b>" + esc(best.text) + "</b><span>" + esc(best.label) + "</span>";
    var tw = tip.offsetWidth || 120;
    tip.style.left = Math.max(0, Math.min(r.width - tw, px - tw / 2)) + "px";
    clearTimeout(el._hide);
  }
  function chartHide(el, later) {
    clearTimeout(el._hide);
    el._hide = setTimeout(function () { el.classList.remove("on"); }, later ? 2500 : 0);
  }
  var chartActive = null;
  document.addEventListener("pointerdown", function (ev) {
    var el = closest(ev.target, "data-chart"); if (!el) { return; }
    chartActive = el; chartShow(el, ev.clientX);
  });
  document.addEventListener("pointermove", function (ev) {
    if (chartActive) { chartShow(chartActive, ev.clientX); return; }
    if (ev.pointerType === "mouse") {
      var el = closest(ev.target, "data-chart");
      if (el) { chartShow(el, ev.clientX); }
      document.querySelectorAll(".chart.on").forEach(function (c) { if (c !== el) { chartHide(c); } });
    }
  });
  function chartEnd() { if (chartActive) { chartHide(chartActive, true); chartActive = null; } }
  document.addEventListener("pointerup", chartEnd);
  document.addEventListener("pointercancel", chartEnd);

  // ---------- details sheet ----------
  function openSheet(id) { S.sheet = { id: id }; renderSheet(); loadHistory(id); }
  function closeSheet() { S.sheet = null; S.sliding = false; var d = document.getElementById("sheet"); if (d) { d.parentNode.removeChild(d); } }
  function loadHistory(id) {
    if (!S.header.timeline) { return; }
    api("api/history?id=" + encodeURIComponent(id)).then(function (data) {
      if (S.sheet && S.sheet.id === id) { S.sheet.history = data; renderSheet(); }
    }).catch(function () { /* no history */ });
  }
  function sheetShell(inner, cls) {
    var d = document.getElementById("sheet");
    if (!d) { d = document.createElement("div"); d.id = "sheet"; d.className = "dim"; document.body.appendChild(d); }
    var old = d.firstChild, top = old ? old.scrollTop : 0, key = JSON.stringify([S.sheet && S.sheet.id, S.sheet && S.sheet.settings, S.sheet && S.sheet.page, S.sheet && S.sheet.batteries, S.sheet && S.sheet.arrange, S.sheet && S.sheet.rename, S.sheet && S.sheet.addto, S.sheet && S.sheet.people, S.sheet && S.sheet.room, S.sheet && S.sheet.overview, S.sheet && S.sheet.routine, S.sheet && S.sheet.weather, S.sheet && S.sheet.pin !== undefined]);
    if (d.getAttribute("data-key") === key && old) {
      // the same sheet again (new values): keep the box, so it doesn't pop up again and flicker
      old.className = "sheet " + (cls || ""); old.innerHTML = inner; old.scrollTop = top;
    } else {
      d.innerHTML = '<div class="sheet ' + (cls || "") + '">' + inner + "</div>";
    }
    d.setAttribute("data-key", key);
    return d;
  }
  function renderSheet() {
    if (!S.sheet) { return; }
    if (S.sheet.settings) { renderSettings(); return; }
    if (S.sheet.batteries) { renderBatteries(); return; }
    if (S.sheet.arrange) { renderPick(); return; }
    if (S.sheet.rename) { renderRename(); return; }
    if (S.sheet.people) { renderPeople(); return; }
    if (S.sheet.room) { renderRoomPop(); return; }
    if (S.sheet.overview) { renderOverview(); return; }
    if (S.sheet.pin !== undefined) { renderPin(); return; }
    if (S.sheet.routine) { renderRoutine(); return; }
    if (S.sheet.weather) { renderWeather(); return; }
    if (S.sheet.addto !== undefined) { renderAdd(); return; }
    var tile = S.tiles[S.sheet.id]; if (!tile) { closeSheet(); return; }
    var st = tile.state, k = tile.kind, look = tileLook(tile);
    var head = '<div class="head"><div><h1>' + esc(tile.name) + '</h1><div class="subtitle">' + esc([tile.rooms[0], look.sub].filter(Boolean).join(" · ")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>";
    var left = "", body = "";
    if (k === "blind") {
      left = "<div>" + winHtml(st.position || 0) + '<div class="hint">' + esc(t("pullWindow")) + "</div></div>";
    } else if (k === "dimmer" || k === "fan") {
      var value = k === "dimmer" ? (st.on ? (st.level || 0) : 0) : k === "fan" ? (st.percent || 0) : (st.position || 0);
      left = '<div><div class="vs' + (k === "blind" || k === "fan" ? " teal" : "") + '" data-slider="' + (k === "dimmer" ? "level" : k === "fan" ? "fan" : "position") + '"><div class="f" style="height:' + value + '%"></div><div class="k" style="bottom:' + value + '%"></div><div class="lbl">' + value + ' %</div></div><div class="hint">' + esc(k === "dimmer" ? t("pullToDim") : k === "fan" ? t("pullToFan") : t("pullToMove")) + "</div></div>";
    }
    if (k === "fan") { body += fanHtml(st) + timerHtml(tile); }
    if (k === "inputs") { body += inputsHtml(tile); }
    if (k === "media") {
      var ms = mediaSheet(tile); left = ms.left; body += ms.body;
    } else if (k === "light" || k === "dimmer" || k === "switch" || k === "outlet") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.on ? " on" : "") + '" data-do="on">' + I("power", 20) + " " + esc(t("on")) + '</button><button class="pill' + (!st.on ? " on" : "") + '" data-do="off">' + esc(t("off")) + "</button></div></div>";
      if (st.power) { body += '<div class="group"><div class="facts2"><div class="fact2"><b>' + watt(st.power) + "</b><span>" + esc(t("usage")) + "</span></div></div></div>"; }
      if (tile.color) { body += colorHtml(tile); }
      body += timerHtml(tile);
      if (S.tablet && S.tablet.arrange) { body += keepOnHtml(tile); }
    } else if (k === "blind") {
      var bp = st.position;
      body += '<div class="group"><div class="actions wbtns"><button class="pill' + (bp >= 99 ? " on" : "") + '" data-do="up">' + esc(t("up")) + '</button><button class="pill' + (bp >= 45 && bp <= 55 ? " on" : "") + '" data-half="1">' + esc(t("half")) + "</button>" +
        '<button class="pill' + (bp !== undefined && bp <= 1 ? " on" : "") + '" data-do="down">' + esc(t("down")) + "</button>" + (tile.stop ? '<button class="pill" data-do="stop">' + esc(t("stop")) + "</button>" : "") + "</div></div>";
    } else if (k === "thermostat") {
      body += '<div class="target"><button class="round" data-step="-1">−</button><div class="val">' + num(st.target) + '°</div><button class="round" data-step="1">+</button></div>';
      body += '<div class="facts2">' + (st.current !== undefined ? '<div class="fact2"><b>' + num(st.current) + "°</b><span>" + esc(t("room")) + "</span></div>" : "") + (st.humidity !== undefined ? '<div class="fact2"><b>' + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span></div>" : "") + "</div>";
    } else if (k === "lock") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.locked ? " on" : "") + '" data-do="lock">' + I("lock", 20) + " " + esc(t("lock")) + '</button><button class="pill danger" data-do="unlock">' + I("unlock", 20) + " " + esc(t("unlock")) + "</button></div></div>";
    } else if (k === "temperature" || k === "humidity") {
      body += '<div class="group facts2">' + (st.temperature !== undefined ? '<div class="fact2"><b>' + num(st.temperature) + "°</b><span>" + esc(t("temperature")) + "</span></div>" : "") + (st.humidity !== undefined ? '<div class="fact2"><b>' + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span></div>" : "") + "</div>";
    }
    if (tile.fan && k !== "fan") { body += fanHtml(st.fan); }
    body += sheetTrendsHtml() + sheetHistoryHtml();
    var cols = !!left;
    sheetShell(cols ? left + "<div>" + head + body + "</div>" : head + body, cols ? "cols" + (k === "media" ? " msheet" : "") : "");
  }
  function keepOnHtml(tile) {
    return '<div class="group"><div class="list"><div class="item"><div class="grow"><div>' + esc(t("keepOn")) + '</div><div class="hint" style="text-align:left;margin:2px 0 0">' + esc(t("keepOnHint")) + "</div></div>" +
      '<button class="tg' + (tile.keep_on ? "" : " off") + '" data-keepon="' + esc(tile.id) + '" aria-label="' + esc(t("keepOn")) + '"></button></div></div></div>';
  }
  function keepOnListHtml() {
    var ids = Object.keys(S.tiles).filter(function (id) { var tl = S.tiles[id]; return tl.kind === "switch" || tl.kind === "outlet" || tl.keep_on; });
    if (!ids.length) { return ""; }
    ids.sort(function (a, b) { return S.tiles[a].name.localeCompare(S.tiles[b].name); });
    return '<div class="group"><div class="label">' + esc(t("keepOnList")) + '</div><div class="hint" style="text-align:left;margin:0 0 6px">' + esc(t("keepOnHint")) + '</div><div class="list">' + ids.map(function (id) {
      var tl = S.tiles[id];
      return '<div class="item"><span class="grow">' + esc(tl.name) + '<span style="color:var(--mu)"> · ' + esc(tl.rooms[0] || "") + '</span></span><button class="tg' + (tl.keep_on ? "" : " off") + '" data-keepon="' + esc(id) + '"></button></div>';
    }).join("") + "</div></div>";
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
    // temperature always on top, then humidity
    function rank(tr) { var r = String(tr.reading || ""); return /humid/i.test(r) ? 1 : /dewpoint/i.test(r) ? 2 : 0; }
    return hist.trends.filter(function (tr) { return /temp|humid|dewpoint/i.test(tr.reading || ""); })
      .map(function (tr, i) { return [rank(tr), i, tr]; }).sort(function (a, b) { return a[0] - b[0] || a[1] - b[1]; }).map(function (x) { return x[2]; }).slice(0, 2)
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
    var u = unit === "%" ? " %" : unit ? (unit.charAt(0) === "°" ? unit : " " + unit) : "";
    var marks = pts.map(function (p) {
      var tv = null; target.forEach(function (q) { if (q[0] <= p[0]) { tv = q[1]; } });
      return { fx: Number(x(p[0])) / w, fy: Number(y(p[1])) / h, label: clockText(new Date(p[0] * 1000)), text: fmt(p[1]) + u + (tv !== null ? " · " + t("targetTemp") + " " + fmt(tv) + u : "") };
    });
    svg = chartWrap("sheet:" + tr.reading, marks, col, svg);
    return '<div class="group"><div class="label" style="display:flex;justify-content:space-between"><span>' + esc(tr.name || tr.reading) + " · " + esc(t("today")) +
      '</span><span style="text-transform:none;letter-spacing:0;color:var(--tx)">' + esc(fmt(last) + (unit ? " " + unit : "")) + "</span></div>" + svg +
      '<div style="display:flex;justify-content:space-between;color:var(--mu2);font-size:12px;margin-top:6px"><span>0</span><span>6</span><span>12</span><span>18</span><span>24</span></div>' +
      '<div class="hint" style="text-align:left;margin-top:4px">' + info + "</div></div>";
  }

  // a window whose blind moves like the real one: 100 open, 0 closed
  function posText(p) { return p >= 99 ? t("open") : p <= 1 ? t("closed") : p + " %"; }
  function winHtml(pos) {
    var hour = new Date().getHours(), night = hour < 7 || hour >= 19;
    return '<div class="win' + (night ? " night" : "") + '" data-slider="position"><div class="wsky"></div><div class="wsill"></div><div class="wshut" style="height:' + (100 - pos) + '%"><i></i></div><div class="lbl">' + esc(posText(pos)) + "</div></div>";
  }
  function winMini(pos, size) {
    var h = Math.round(16 * (100 - (pos || 0)) / 100), lines = "";
    for (var y = 6; y < 3 + h; y += 3) { lines += "M6 " + y + "h12"; }
    return '<svg class="i" viewBox="0 0 24 24"' + (size ? ' style="width:' + size + 'px;height:' + size + 'px"' : "") + '><rect x="4" y="3" width="16" height="18" rx="2"/>' +
      (h > 0 ? '<rect x="4" y="3" width="16" height="' + h + '" rx="2" fill="currentColor" stroke="none" opacity=".35"/>' + (lines ? '<path d="' + lines + '" opacity=".7"/>' : "") : '<path d="M12 3v18M4 12h16" opacity=".5"/>') + "</svg>";
  }
  // dragging the big slider of dimmers and the window of blinds
  function sliderDrag(el, ev) {
    var kind = el.getAttribute("data-slider"), id = S.sheet.id, value = 0, win = el.classList.contains("win");
    S.sliding = true;
    if (win) { el.classList.add("drag"); }
    function move(e) {
      var r = el.getBoundingClientRect(), y = (e.touches ? e.touches[0].clientY : e.clientY);
      value = Math.round(Math.max(0, Math.min(100, (r.bottom - y) / r.height * 100)));
      if (win) { el.querySelector(".wshut").style.height = (100 - value) + "%"; el.querySelector(".lbl").textContent = posText(value); } else { el.querySelector(".f").style.height = value + "%"; el.querySelector(".k").style.bottom = value + "%"; el.querySelector(".lbl").textContent = value + " %"; }
      e.preventDefault();
    }
    function up() {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      S.sliding = false; el.classList.remove("drag");
      if (kind === "level") { act(id, "level", value, value > 0 ? { on: true, level: value } : { on: false }); } else if (kind === "fan") { act(id, "fan_percent", value, { percent: value, on: value > 0, mode: fanModeOf(value) }); } else { act(id, "position", value, { position: value }); }
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
    move(ev);
  }

  // ---------- room popup: a tap on a room card on Home ----------
  function roomGroups(room) {
    var g = { light: [], switch: [], blind: [], climate: null, more: [] };
    roomTiles(room).forEach(function (id) {
      var tl = S.tiles[id];
      if (tl.kind === "light" || tl.kind === "dimmer") { g.light.push(id); } else if (tl.kind === "switch" || tl.kind === "outlet") { g.switch.push(id); } else if (tl.kind === "blind") { g.blind.push(id); } else if (tl.kind === "thermostat" && (!g.climate || g.climate.kind !== "thermostat")) { if (g.climate) { g.more.push(g.climate.id); } g.climate = tl; } else if (tl.kind === "temperature" && !g.climate) { g.climate = tl; } else { g.more.push(id); }
    });
    return g;
  }
  var RING_MIN = 10, RING_MAX = 28, RING_SWEEP = 270;
  function ringPoint(frac, r, c) {
    var a = (135 + frac * RING_SWEEP) * Math.PI / 180;
    return [c + r * Math.cos(a), c + r * Math.sin(a)];
  }
  function ringArc(f0, f1, r, c) {
    var p0 = ringPoint(f0, r, c), p1 = ringPoint(f1, r, c), large = (f1 - f0) * RING_SWEEP > 180 ? 1 : 0;
    return "M" + p0[0].toFixed(1) + " " + p0[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 1 " + p1[0].toFixed(1) + " " + p1[1].toFixed(1);
  }
  function ringFrac(v) { return Math.max(0, Math.min(1, (v - RING_MIN) / (RING_MAX - RING_MIN))); }
  function climateHtml(tl) {
    var st = tl.state;
    if (tl.kind !== "thermostat") {
      var cv = st.temperature;
      return '<div class="pclimate"><div class="pbig" style="color:' + tempColor(cv) + '">' + num(cv) + '°</div><div class="pctext">' + (st.humidity !== undefined ? "<b>" + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span>" : "") + "</div></div>";
    }
    var cur = st.current, target = st.target, heats = target !== undefined && cur !== undefined && target > cur + 0.3, color = heats ? "#FF8A3D" : tempColor(cur);
    var c = 90, r = 72, ft = ringFrac(target === undefined ? RING_MIN : target), knob = ringPoint(ft, r, c);
    var svg = '<svg viewBox="0 0 180 180" class="ringsvg"><path d="' + ringArc(0, 1, r, c) + '" class="rtrack"/>' +
      (target !== undefined ? '<path d="' + ringArc(0, Math.max(ft, 0.002), r, c) + '" class="rfill" style="stroke:' + color + '"/><circle cx="' + knob[0].toFixed(1) + '" cy="' + knob[1].toFixed(1) + '" r="11" class="rknob"/>' : "") + "</svg>";
    var side = heats ? '<div class="pcs"><b>' + I("thermo", 18) + " " + esc(t("rpHeatsNow")) + "</b><span>" + esc(t("rpHoldRing")) + "</span></div>" : '<div class="pcs"><b>' + esc(cur !== undefined && target !== undefined && Math.abs(cur - target) <= 0.3 ? t("rpReached") : t("rpSetTo", { t: num(target) })) + "</b><span>" + esc(t("rpHoldRing")) + "</span></div>";
    return '<div class="pclimate"><div class="ring" data-ring="' + esc(tl.id) + '">' + svg + '<div class="rval"><b style="color:' + tempColor(cur) + '">' + (cur !== undefined ? num(cur) + "°" : "–") + "</b><span>" + esc(t("rpSetTo", { t: num(target) })) + "</span></div></div>" +
      '<div class="pcside' + (heats ? " heats" : "") + '">' + side + '<div class="target small"><button class="round" data-step="-1" data-sid="' + esc(tl.id) + '">−</button><button class="round" data-step="1" data-sid="' + esc(tl.id) + '">+</button></div>' +
      (st.humidity !== undefined ? '<div class="phum">' + I("drop", 16) + " " + Math.round(st.humidity) + " %</div>" : "") + "</div></div>";
  }
  function hslideHtml(kind, ids, value, teal) {
    return '<div class="hslide' + (teal ? " teal" : "") + '" data-hslide="' + kind + '" data-ids="' + esc(ids.join("\n")) + '"><div class="hf" style="width:' + value + '%"></div><span class="hl">' + value + " %</span></div>";
  }
  function avg(list) { return list.length ? Math.round(list.reduce(function (a, b) { return a + b; }, 0) / list.length) : 0; }
  function groupHtml(key, icon, title, ids, ro) {
    var open = S.sheet.open[key], tiles = ids.map(function (id) { return S.tiles[id]; }), sub = "", head = "", rows = "", cls = "";
    if (key === "blind") {
      var pos = avg(tiles.map(function (tl) { return tl.state.position || 0; }));
      sub = pos >= 99 ? t("open") : pos <= 1 ? t("closed") : t("open") + " " + pos + " %";
      head = ro ? "" : hslideHtml("position", ids, pos, true) + '<button class="round sm" data-pgroup="up" aria-label="' + esc(t("up")) + '">' + I("chev", 18).replace("<svg", '<svg style="transform:rotate(-90deg)"') + '</button><button class="round sm" data-pgroup="down" aria-label="' + esc(t("down")) + '">' + I("chev", 18).replace("<svg", '<svg style="transform:rotate(90deg)"') + "</button>";
      rows = tiles.map(function (tl) {
        return '<div class="prow"><button class="pic teal" data-pdetail="' + esc(tl.id) + '">' + winMini(tl.state.position, 20) + '</button><div class="pn" data-pdetail="' + esc(tl.id) + '">' + esc(tl.name) + "</div>" + (ro ? "" : hslideHtml("position", [tl.id], tl.state.position || 0, true)) + "</div>";
      }).join("");
    } else {
      var on = tiles.filter(function (tl) { return tl.state.on; });
      var levels = on.filter(function (tl) { return tl.kind === "dimmer" && tl.state.level; }).map(function (tl) { return tl.state.level; });
      sub = (on.length ? t("rpNofM", { n: on.length, m: tiles.length }) : t("off")) + (levels.length ? " · " + avg(levels) + " %" : "");
      cls = on.length ? (key === "light" ? " lit" : " pow") : "";
      head = ro ? "" : '<button class="round sm pwr' + (on.length ? " on" : "") + '" data-pgroup="' + key + '" aria-label="' + esc(on.length ? t("rpAllOffShort") : t("on")) + '">' + I("power", 18) + "</button>";
      rows = tiles.map(function (tl) {
        var lv = tl.kind === "dimmer" ? (tl.state.on ? tl.state.level || 0 : 0) : null;
        return '<div class="prow"><button class="pic' + (tl.state.on ? (key === "light" ? " lit" : " pow") : "") + '" ' + (ro ? 'data-pdetail="' : 'data-ptoggle="') + esc(tl.id) + '">' + I(key === "light" ? "bulb" : tl.kind === "outlet" ? "plug" : "power", 18) + '</button><div class="pn" data-pdetail="' + esc(tl.id) + '">' + esc(tl.name) + "<span>" + esc(tileLook(tl).sub) + "</span></div>" +
          (lv !== null && !ro ? hslideHtml("level", [tl.id], lv) : "") + "</div>";
      }).join("");
    }
    return '<div class="pgroup' + cls + (open ? " open" : "") + '"><div class="phead"><span class="pgi">' + I(icon, 20) + '</span><button class="pgt" data-pexp="' + key + '"><b>' + esc(title) + "</b><span>" + esc(sub) + "</span></button>" + head +
      '<button class="round sm exp" data-pexp="' + key + '">' + I("chev", 18) + "</button></div>" + (open ? '<div class="prows">' + rows + "</div>" : "") + "</div>";
  }
  function renderRoomPop() {
    var room = roomByName(S.sheet.room); if (!room) { closeSheet(); return; }
    var g = roomGroups(room), ro = S.tablet && S.tablet.readonly, body = "";
    if (g.climate) { body += climateHtml(g.climate); }
    if (g.light.length) { body += groupHtml("light", "bulb", t("rpLight"), g.light, ro); }
    if (g.blind.length) { body += groupHtml("blind", "blind", t("rpBlinds"), g.blind, ro); }
    if (g.switch.length) { body += groupHtml("switch", "plug", t("rpSwitches"), g.switch, ro); }
    body += scenesHtml(room);
    if (g.more.length) { body += '<div class="section">' + esc(t("rpMore")) + '</div><div class="grid pgrid">' + g.more.map(function (id) { return tileHtml(id); }).join("") + "</div>"; }
    body += '<div class="actions"><button class="pill" data-gotab="room:' + esc(room.name) + '">' + esc(t("rpOpenRoom")) + "</button></div>";
    sheetShell('<div class="head"><div><h1>' + esc(room.name) + '</h1></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" + '<div class="rpop">' + body + "</div>", "roompop");
  }
  function roomGroupAction(what) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var g = roomGroups(roomByName(S.sheet.room));
    if (what === "up" || what === "down") {
      var v = what === "up" ? 100 : 0;
      g.blind.forEach(function (id) { act(id, "position", v, { position: v }); });
    } else {
      var ids = g[what] || [], anyOn = ids.some(function (id) { return S.tiles[id].state.on; });
      ids.forEach(function (id) { if (!!S.tiles[id].state.on === anyOn) { act(id, anyOn ? "off" : "on", null, { on: !anyOn }); } });
    }
    renderSheet();
  }
  function hslideDrag(el, ev) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var kind = el.getAttribute("data-hslide"), ids = el.getAttribute("data-ids").split("\n"), value = null, sx = ev.clientX, moved = false;
    S.sliding = true;
    function calc(x) { var r = el.getBoundingClientRect(); return Math.round(Math.max(0, Math.min(100, (x - r.left) / r.width * 100))); }
    function move(e) {
      if (Math.abs(e.clientX - sx) > 4) { moved = true; }
      value = calc(e.clientX);
      el.querySelector(".hf").style.width = value + "%"; el.querySelector(".hl").textContent = value + " %";
      if (e.cancelable) { e.preventDefault(); }
    }
    function up(e) {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      S.sliding = false; dragEnded = Date.now();
      if (!moved) { value = calc(e.clientX); }
      ids.forEach(function (id) {
        if (!S.tiles[id]) { return; }
        if (kind === "level") { act(id, "level", value, value > 0 ? { on: true, level: value } : { on: false }); } else { act(id, "position", value, { position: value }); }
      });
      renderSheet();
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
    ev.preventDefault();
  }
  function ringDrag(el, ev) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var id = el.getAttribute("data-ring"), tile = S.tiles[id]; if (!tile) { return; }
    var step = tile.step || 0.5, value = tile.state.target;
    S.sliding = true;
    function move(e) {
      var live = document.querySelector("#sheet [data-ring]") || el, r = live.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      var a = Math.atan2(e.clientY - cy, e.clientX - cx) * 180 / Math.PI;
      var rel = ((a - 135) % 360 + 360) % 360;
      if (rel > RING_SWEEP) { rel = rel - RING_SWEEP < (360 - RING_SWEEP) / 2 ? RING_SWEEP : 0; }
      value = Math.round((RING_MIN + rel / RING_SWEEP * (RING_MAX - RING_MIN)) / step) * step;
      tile.state.target = value;
      var box = document.querySelector("#sheet .pclimate"); if (box && box.parentNode) { var d = document.createElement("div"); d.innerHTML = climateHtml(tile); box.parentNode.replaceChild(d.firstChild, box); }
      if (e.cancelable) { e.preventDefault(); }
    }
    function up() {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      S.sliding = false; dragEnded = Date.now();
      if (value !== undefined) { act(id, "target", value, { target: value }); }
      renderSheet();
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
    ev.preventDefault();
  }

  // ---------- colour and white of lights ----------
  function hx2(n) { return ("0" + n.toString(16)).slice(-2); }
  var SWATCHES = ["#ff3b30", "#ff8a3d", "#ffcc00", "#34c759", "#30d5c8", "#007aff", "#7d5cff", "#ff2d92"];
  function hueHex(h) {
    function f(n) { var k = (n + h / 60) % 6, v = 1 - Math.max(0, Math.min(k, 4 - k, 1)); return hx2(Math.round(v * 255)); }
    return "#" + f(5) + f(3) + f(1);
  }
  function hexHue(hex) {
    var r = parseInt(hex.substr(1, 2), 16) / 255, g = parseInt(hex.substr(3, 2), 16) / 255, b = parseInt(hex.substr(5, 2), 16) / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    if (!d) { return null; }
    var h = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return (h * 60 + 360) % 360;
  }
  // colour of a white light in kelvin, roughly
  function kelvinHex(k) {
    var f = Math.max(0, Math.min(1, (k - 2000) / 4500));
    var r = 255, g = Math.round(170 + f * 80), b = Math.round(90 + f * 165);
    return "#" + hx2(r) + hx2(g) + hx2(b);
  }
  function lampColor(st) { return st.rgb && st.rgb !== "#000000" ? st.rgb : st.ct ? kelvinHex(st.ct) : "transparent"; }
  function colorHtml(tile) {
    var c = tile.color, st = tile.state, html = "";
    if (c.rgb) {
      var hue = st.rgb ? hexHue(st.rgb) : null;
      html += '<div class="group"><div class="label">' + esc(t("colorTitle")) + '</div><div class="swatches">' +
        SWATCHES.map(function (h) { return '<button class="swatch' + (st.rgb === h ? " on" : "") + '" data-swatch="' + h + '" style="background:' + h + '"></button>'; }).join("") + "</div>" +
        '<div class="cstrip hue" data-cstrip="hue">' + (hue !== null ? '<div class="ck" style="left:' + (hue / 360 * 100).toFixed(1) + "%;background:" + st.rgb + '"></div>' : "") + "</div></div>";
    }
    if (c.ct) {
      var lo = c.ct[0], hi = c.ct[1], k = st.ct;
      var pos = k ? Math.max(0, Math.min(1, (k - lo) / (hi - lo))) : null;
      html += '<div class="group"><div class="label tl2"><span>' + esc(t("whiteTitle")) + "</span>" + (k ? "<span>" + k + " K</span>" : "") + '</div>' +
        '<div class="cstrip ct" data-cstrip="ct" style="background:linear-gradient(90deg,' + kelvinHex(lo) + "," + kelvinHex(hi) + ')">' + (pos !== null ? '<div class="ck" style="left:' + (pos * 100).toFixed(1) + "%;background:" + kelvinHex(k) + '"></div>' : "") + "</div>" +
        '<div class="cends"><span>' + esc(t("warm")) + "</span><span>" + esc(t("cold")) + "</span></div></div>";
    }
    return html;
  }
  function colorDrag(el, ev) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var kind = el.getAttribute("data-cstrip"), id = S.sheet && S.sheet.id, tile = S.tiles[id]; if (!tile) { return; }
    var value = null;
    S.sliding = true;
    function move(e) {
      var r = el.getBoundingClientRect(), f = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
      var knob = el.querySelector(".ck"); if (!knob) { knob = document.createElement("div"); knob.className = "ck"; el.appendChild(knob); }
      if (kind === "hue") { value = hueHex(f * 359); knob.style.background = value; } else { value = Math.round((tile.color.ct[0] + f * (tile.color.ct[1] - tile.color.ct[0])) / 50) * 50; knob.style.background = kelvinHex(value); }
      knob.style.left = (f * 100).toFixed(1) + "%";
      if (e.cancelable) { e.preventDefault(); }
    }
    function up() {
      document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
      S.sliding = false;
      if (value === null) { return; }
      if (kind === "hue") { act(id, "rgb", value, { rgb: value, on: true }); } else { act(id, "ct", value, { ct: value, on: true }); }
      renderSheet();
    }
    document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
    move(ev);
  }

  // ---------- weather details ----------
  function has(v) { return v !== null && v !== undefined; }
  // temperature curve with rain bars of the next hours
  function hoursSvg(hours) {
    var pts = hours.filter(function (x) { return has(x.temp); });
    if (pts.length < 2) { return ""; }
    var W = 720, H = 170, top = 30, bottom = 130, step = W / hours.length;
    var lo = Math.min.apply(null, pts.map(function (x) { return x.temp; })), hi = Math.max.apply(null, pts.map(function (x) { return x.temp; }));
    if (hi - lo < 4) { var mid = (hi + lo) / 2; lo = mid - 2; hi = mid + 2; }
    function y(v) { return bottom - (v - lo) / (hi - lo) * (bottom - top); }
    var bars = "", line = "", labels = "";
    hours.forEach(function (x, i) {
      var cx = step * i + step / 2;
      if (has(x.rain) && x.rain > 0) { var bh = x.rain / 100 * 40; bars += '<rect x="' + (cx - step * 0.3).toFixed(1) + '" y="' + (H - 18 - bh).toFixed(1) + '" width="' + (step * 0.6).toFixed(1) + '" height="' + bh.toFixed(1) + '" rx="2" class="wxrain"/>'; }
      if (has(x.temp)) { line += (line ? "L" : "M") + cx.toFixed(1) + " " + y(x.temp).toFixed(1); }
      if (i % 3 === 0) {
        labels += '<text x="' + cx.toFixed(1) + '" y="' + (H - 2) + '" class="wxat">' + esc(x.at) + "</text>";
        if (has(x.temp)) { labels += '<text x="' + cx.toFixed(1) + '" y="' + (y(x.temp) - 10).toFixed(1) + '" class="wxt">' + num(x.temp, 0) + "°</text>"; }
      }
    });
    return '<div class="wxscroll"><svg class="wxsvg" viewBox="0 0 ' + W + " " + H + '">' + bars + '<path d="' + line + '" class="wxline"/>' + labels + "</svg></div>";
  }
  function renderWeather() {
    var w = (S.header && S.header.weather) || {}, sun = S.header && S.header.sun, hours = w.hours || [], days = w.days || [], body = "";
    body += '<div class="wxnow">' + I(weatherIcon(w.condition), 44) + '<div><b>' + (has(w.temperature) ? num(w.temperature, 0) + "°" : "–") + "</b><span>" + esc(w.condition || "") + (has(w.high) ? " · " + num(w.low, 0) + "° / " + num(w.high, 0) + "°" : "") + "</span></div>" +
      (sun ? '<div class="wxsun"><span>' + I("sun", 18) + " " + esc(t("wxSunrise")) + " <b>" + esc(sun.rise) + "</b></span><span>" + I("moon", 18) + " " + esc(t("wxSunset")) + " <b>" + esc(sun.set) + "</b></span></div>" : "") + "</div>";
    if (w.warn) { body += '<div class="rtwarn">' + I(w.warn.kind === "frost" ? "drop" : "rain", 22) + '<div class="t"><b>' + esc(t("warn" + w.warn.kind, { t: w.warn.at })) + "</b></div></div>"; }
    var svg = hoursSvg(hours);
    if (svg) { body += '<div class="section">' + esc(t("wxHours")) + "</div>" + svg; }
    if (days.length) {
      var lo = Math.min.apply(null, days.filter(function (d) { return has(d.low); }).map(function (d) { return d.low; }));
      var hi = Math.max.apply(null, days.filter(function (d) { return has(d.high); }).map(function (d) { return d.high; }));
      body += '<div class="section">' + esc(t("wxDays")) + '</div><div class="wxdays">' + days.map(function (d, i) {
        var bar = has(d.low) && has(d.high) && hi > lo ? '<div class="wxbar"><i style="left:' + ((d.low - lo) / (hi - lo) * 100).toFixed(1) + "%;right:" + ((hi - d.high) / (hi - lo) * 100).toFixed(1) + '%"></i></div>' : '<div class="wxbar"></div>';
        return '<div class="wxday"><b>' + esc(i === 0 ? t("wxToday") : d.name.slice(0, 2)) + "</b>" + I(weatherIcon(d.condition, true), 22) + '<span class="wxr">' + (has(d.rain) && d.rain >= 10 ? I("drop", 14) + Math.round(d.rain) + " %" : "") + "</span>" +
          '<span class="wxl">' + (has(d.low) ? num(d.low, 0) + "°" : "") + "</span>" + bar + '<span class="wxh">' + (has(d.high) ? num(d.high, 0) + "°" : "") + "</span></div>";
      }).join("") + "</div>";
    }
    if (!svg && !days.length) { body += '<div class="lead">' + esc(t("wxNone")) + "</div>"; }
    sheetShell('<div class="head"><div><h1>' + esc(t("wxTitle")) + '</h1></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" + body);
  }
  // the next hours in the screensaver
  function saverHours(w) {
    var hours = ((w && w.hours) || []).filter(function (x, i) { return i > 0 && i % 2 === 0 && has(x.temp); }).slice(0, 5);
    if (!hours.length) { return ""; }
    return '<div class="sh">' + hours.map(function (x) { return "<div>" + "<span>" + esc(x.at) + "</span>" + I(weatherIcon(x.condition), 22) + "<b>" + num(x.temp, 0) + "°</b>" + (has(x.rain) && x.rain >= 30 ? "<i>" + Math.round(x.rain) + " %</i>" : "") + "</div>"; }).join("") + "</div>";
  }

  // ---------- good night and leaving home ----------
  function routinesHtml() {
    if (S.tablet && S.tablet.readonly) { return ""; }
    return '<div class="routines"><button class="routine" data-routine="night">' + I("moon", 22) + " " + esc(t("rtNight")) + '</button><button class="routine" data-routine="away">' + I("walk", 22) + " " + esc(t("rtAway")) + "</button>" +
      (S.undoUntil && Date.now() < S.undoUntil * 1000 ? '<button class="routine" data-undo="1">' + I("left", 22) + " " + esc(t("undo")) + "</button>" : "") + "</div>";
  }
  // what the routine does: lights and switches off, at night the blinds down
  function routinePlan(mode) {
    var all = shownTiles();
    var off = all.filter(function (x) { return ["light", "dimmer", "switch", "outlet"].indexOf(x.tile.kind) >= 0 && x.tile.state.on; });
    var blinds = mode === "night" ? all.filter(function (x) { return x.tile.kind === "blind" && x.tile.state.position !== 0; }) : [];
    return { off: off, blinds: blinds, open: all.filter(function (x) { return secOpen(x.tile); }) };
  }
  function weatherWarn() {
    var w = S.header && S.header.weather, warn = w && w.warn;
    if (!warn) { return ""; }
    var windows = routinePlan("away").open.filter(function (x) { return x.tile.kind === "contact" && !x.tile.door; });
    if (!windows.length) { return ""; }
    return '<div class="rtwarn">' + I(warn.kind === "frost" ? "drop" : "rain", 22) + '<div class="t"><b>' + esc(t("warn" + warn.kind, { t: warn.at })) + "</b><span>" +
      esc(t("warnWindows", { names: windows.map(function (x) { return x.tile.name; }).join(", ") })) + "</span></div></div>";
  }
  function renderRoutine() {
    var mode = S.sheet.routine, p = routinePlan(mode), body = "";
    p.open.forEach(function (x) {
      if (x.tile.kind === "lock") { body += ovRow(x, "unlock", "#FF8A3D", [x.room, t("unlocked")].join(" · "), '<button class="pill" data-ovlock="' + esc(x.id) + '">' + esc(t("lock")) + "</button>"); return; }
      body += ovRow(x, x.tile.door ? "door" : "win", "#FF8A3D", [x.room, (x.tile.state.tilted ? t("tilted") : t("open")) + " " + since(x.tile.state.since)].join(" · "));
    });
    p.off.forEach(function (x) {
      body += ovRow(x, isLight(x.tile) ? "bulb" : "plug", isLight(x.tile) ? "#FFB547" : "#9B8CFF", [x.room, x.tile.keep_on ? t("staysOn") : t("rtOff")].join(" · "));
    });
    if (p.blinds.length) {
      var rooms = []; p.blinds.forEach(function (x) { if (rooms.indexOf(x.room) < 0) { rooms.push(x.room); } });
      body += '<div class="row"><div class="ic" style="background:#3DDBB826;color:#3DDBB8">' + I("blind") + '</div><div class="t"><b>' + esc(p.blinds.length === 1 ? t("rtBlind") : t("rtBlinds", { n: p.blinds.length })) + "</b><span>" + esc(rooms.join(", ") + " · " + t("rtBlindsSub")) + "</span></div></div>";
    }
    var title = mode === "night" ? t("rtNight") : t("rtAway");
    sheetShell('<div class="head"><div><h1>' + esc(title) + '</h1><div class="subtitle">' + esc(body ? t(mode === "night" ? "rtNightLead" : "rtAwayLead") : "") + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      weatherWarn() + '<div class="blist ovlist">' + (body || '<div class="allclear">' + I("check", 26) + " " + esc(t("rtAllFine")) + "</div>") + "</div>" +
      '<div class="actions"><button class="pill primary" data-rtgo="' + mode + '">' + I(mode === "night" ? "moon" : "walk", 20) + " " + esc(t(mode === "night" ? "rtGoNight" : "rtGoAway")) + "</button></div>");
  }
  function routineGo(mode) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var p = routinePlan(mode);
    send({ type: "action", action: "routine", mode: mode, off: p.off.filter(function (x) { return !x.tile.keep_on; }).map(function (x) { return x.id; }), close: p.blinds.map(function (x) { return x.id; }) });
    closeSheet();
  }
  function routineDone(m) {
    var text = m.done ? t(m.mode === "night" ? "rtDoneNight" : "rtDoneAway", { n: m.done }) : t("rtDoneNone");
    if (m.failed && m.failed.length) { text += " " + t("rtFailed", { names: m.failed.join(", ") }); }
    var ms = Math.max(5000, Math.min(60000, (m.until || 0) * 1000 - Date.now()));
    S.undoUntil = m.undo ? m.until : 0;
    if (S.tab === "home") { renderContent(); }
    showToast(text, null, ms, m.undo ? '<button class="pill" data-undo="1">' + esc(t("undo")) + "</button>" : "");
  }

  // ---------- settings ----------
  // ---------- calendar and waste collection ----------
  function binTexts() {
    var bins = (S.header && S.header.calendar && S.header.calendar.bins) || [], seen = {}, out = [];
    bins.forEach(function (b) { var key = b.day + "|" + b.what; if (!seen[key]) { seen[key] = true; out.push(b); } });
    out.sort(function (a, b) { return a.day - b.day; });
    return out.map(function (b) { return t(b.day === 0 ? "binToday" : "binTomorrow", { what: b.what }); });
  }
  function binChipHtml() {
    var texts = binTexts();
    if (!texts.length) { return ""; }
    return '<div class="schip warn"><span class="sic">' + I("trash", 20) + '</span><span class="st"><b>' + esc(t("binTitle")) + "</b><span>" + esc(texts.join(" · ")) + "</span></span></div>";
  }
  function calendarHtml() {
    var entries = (S.header && S.header.calendar && S.header.calendar.entries) || [];
    if (!entries.length) { return ""; }
    var html = "", last = -1;
    entries.forEach(function (e) {
      if (e.day !== last) { html += '<div class="section">' + esc(e.day === 0 ? t("calTitle") : t("calTomorrow")) + "</div>"; last = e.day; }
      html += '<div class="lrow"><span class="lt">' + esc(e.allday ? t("calAllDay") : e.now ? t("calNow") : e.at) + '</span><span class="ld" style="background:' + (e.now ? "var(--amber)" : "#5AA9FF") + '"></span><span class="lx">' + esc(e.summary) + "</span></div>";
    });
    return '<div class="leave lately cal">' + html + "</div>";
  }

  // ---------- status chips on Home and their overviews ----------
  // every device of the rooms this tablet shows, once, with the room it is shown in
  function shownTiles() {
    var seen = {}, result = [];
    visibleRooms().forEach(function (room) {
      room.tiles.forEach(function (id) { var tl = S.tiles[id]; if (tl && !seen[id]) { seen[id] = true; result.push({ id: id, tile: tl, room: room.name }); } });
    });
    return result;
  }
  function isLight(tl) { return tl.kind === "light" || tl.kind === "dimmer"; }
  function secOpen(tl) { return (tl.kind === "contact" && tl.state.closed === false) || (tl.kind === "lock" && tl.state.locked === false); }
  // devices which need attention: not reachable, a sensor without values for
  // two days, a low battery
  function maintenance() {
    var result = [], limit = Date.now() - 48 * 3600 * 1000;
    shownTiles().forEach(function (x) {
      var st = x.tile.state;
      if (st.unreachable) { result.push({ id: x.id, tile: x.tile, room: x.room, why: "unreachable" }); return; }
      if (st.seen) {
        var when = new Date(st.seen.replace(" ", "T") + ":00:00").getTime();
        if (when && when < limit) { result.push({ id: x.id, tile: x.tile, room: x.room, why: "silent", since: st.seen + ":00:00" }); return; }
      }
      if (st.battery_low) { result.push({ id: x.id, tile: x.tile, room: x.room, why: "battery" }); }
    });
    return result;
  }
  function roomClimates() {
    return visibleRooms().map(function (room) {
      var c = { room: room.name };
      room.tiles.forEach(function (id) {
        var tl = S.tiles[id]; if (!tl) { return; }
        if (tl.kind === "thermostat" && c.thermostat === undefined) {
          c.thermostat = id; c.target = tl.state.target;
          if (tl.state.current !== undefined) { c.temp = tl.state.current; c.id = id; }
          if (tl.state.humidity !== undefined && c.humidity === undefined) { c.humidity = tl.state.humidity; }
        }
        if (tl.kind === "temperature" && c.temp === undefined && tl.state.temperature !== undefined) { c.temp = tl.state.temperature; c.id = id; if (tl.state.humidity !== undefined) { c.humidity = tl.state.humidity; } }
        if (tl.kind === "humidity" && c.humidity === undefined) { c.humidity = tl.state.humidity; }
      });
      if (c.thermostat) { c.id = c.thermostat; }
      c.heats = c.target !== undefined && c.temp !== undefined && c.target > c.temp + 0.3;
      return c;
    }).filter(function (c) { return c.temp !== undefined; });
  }
  function statusChipsHtml() {
    var all = shownTiles(), chips = binChipHtml();
    function chip(kind, icon, cls, title, sub) {
      return '<button class="schip ' + cls + '" data-overview="' + kind + '"><span class="sic">' + I(icon, 20) + '</span><span class="st"><b>' + esc(title) + "</b><span>" + esc(sub) + "</span></span></button>";
    }
    var lights = all.filter(function (x) { return isLight(x.tile); });
    if (lights.length) {
      var on = lights.filter(function (x) { return x.tile.state.on; }).length;
      chips += chip("light", "bulb", on ? "lit" : "", t("chLight"), on ? t("chNOn", { n: on }) : t("chAllOff"));
    }
    var climates = roomClimates();
    if (climates.length) {
      var heat = climates.filter(function (c) { return c.heats; }).length, temps = climates.map(function (c) { return c.temp; });
      var lo = Math.min.apply(null, temps), hi = Math.max.apply(null, temps);
      chips += chip("climate", "thermo", heat ? "heat" : "", t("chClimate"), heat ? (heat === 1 ? t("chOneHeat") : t("chNHeat", { n: heat })) : num(lo, 0) + (hi - lo >= 0.5 ? "–" + num(hi, 0) : "") + "°");
    }
    var blinds = all.filter(function (x) { return x.tile.kind === "blind"; });
    if (blinds.length) {
      var up = blinds.filter(function (x) { return (x.tile.state.position || 0) > 1; }).length;
      chips += chip("blinds", "blind", "", t("chBlinds"), up ? t("chNOpen", { n: up, m: blinds.length }) : t("chAllClosed"));
    }
    var sec = all.filter(function (x) { return x.tile.kind === "contact" || x.tile.kind === "lock"; });
    if (sec.length) {
      var open = sec.filter(function (x) { return secOpen(x.tile); }).length;
      chips += chip("security", "lock", open ? "warn" : "", t("chSecurity"), open ? t("chSecOpen", { n: open }) : t("chSecOk"));
    }
    // only when something needs to be done
    var todo = maintenance();
    if (todo.length) { chips += chip("maintenance", "gear", "warn", t("chMaint"), t("chMaintN", { n: todo.length })); }
    return chips ? '<div class="schips">' + chips + "</div>" : "";
  }
  function ovRow(x, icon, color, sub, button) {
    return '<div class="row tap" data-ovopen="' + esc(x.id) + '"><div class="ic" style="background:' + color + "26;color:" + color + '">' + I(icon) + '</div><div class="t"><b>' + esc(x.tile.name) + "</b><span>" + esc(sub) + "</span></div>" + (button || I("chev")) + "</div>";
  }
  function byRoom(list, rowFn) {
    var html = "", last = null;
    list.forEach(function (x) {
      if (x.room !== last) { html += '<div class="section ovroom">' + esc(x.room) + "</div>"; last = x.room; }
      html += rowFn(x);
    });
    return html;
  }
  function renderOverview() {
    var kind = S.sheet.overview, all = shownTiles(), title = "", lead = "", body = "", actions = "", ro = S.tablet && S.tablet.readonly;
    if (kind === "light") {
      var on = all.filter(function (x) { return isLight(x.tile) && x.tile.state.on; });
      title = t("ovLight"); lead = on.length ? t("chNOn", { n: on.length }) : "";
      body = on.length ? byRoom(on, function (x) {
        return ovRow(x, "bulb", "#FFB547", x.tile.kind === "dimmer" && x.tile.state.level ? x.tile.state.level + " %" : t("on"), ro ? "" : '<button class="pill" data-off="' + esc(x.id) + '">' + esc(t("off")) + "</button>");
      }) : '<div class="allclear">' + I("check", 26) + " " + esc(t("ovNoLight")) + "</div>";
      if (on.length > 1 && !ro) { actions = '<button class="pill primary" data-ovall="lights">' + I("power", 20) + " " + esc(t("lightsOff")) + "</button>"; }
    } else if (kind === "climate") {
      title = t("ovClimate");
      body = roomClimates().map(function (c) {
        var color = tempColor(c.temp), sub = [];
        if (c.target !== undefined) { sub.push(t("target") + " " + num(c.target) + "°"); }
        if (c.humidity !== undefined) { sub.push(Math.round(c.humidity) + " %"); }
        if (c.heats) { sub.push(t("heatsNow")); }
        return '<div class="row tap" data-ovopen="' + esc(c.id) + '"><div class="ic" style="background:' + color + "26;color:" + color + '">' + I("thermo") + '</div><div class="t"><b>' + esc(c.room) + "</b><span>" + esc(sub.join(" · ")) + '</span></div><div class="ovtemp" style="color:' + color + '">' + num(c.temp) + "°</div>" + I("chev") + "</div>";
      }).join("");
    } else if (kind === "blinds") {
      var blinds = all.filter(function (x) { return x.tile.kind === "blind"; });
      title = t("ovBlinds");
      body = byRoom(blinds, function (x) {
        var p = x.tile.state.position;
        var sub = p === undefined ? "–" : p >= 99 ? t("open") : p <= 1 ? t("closed") : t("open") + " " + p + " %";
        return ovRow(x, "blind", "#3DDBB8", sub, ro ? "" : '<button class="pill" data-ovpos="' + esc(x.id) + '|100">' + esc(t("up")) + '</button><button class="pill" data-ovpos="' + esc(x.id) + '|0">' + esc(t("down")) + "</button>");
      });
      if (!ro) { actions = '<button class="pill" data-ovall="up">' + esc(t("allUp")) + '</button><button class="pill" data-ovall="down">' + esc(t("allDown")) + "</button>"; }
    } else if (kind === "maintenance") {
      var todo = maintenance();
      title = t("ovMaint"); lead = todo.length ? t("ovMaintLead") : "";
      body = todo.length ? byRoom(todo, function (x) {
        return ovRow(x, x.why === "battery" ? "battery" : x.why === "silent" ? "clock" : "x", "#FF8A3D",
          x.why === "battery" ? t("mtBattery") : x.why === "silent" ? t("mtSilent", { t: since(x.since) }) : t("mtUnreachable"));
      }) : '<div class="allclear">' + I("check", 26) + " " + esc(t("mtOk")) + "</div>";
    } else if (kind === "security") {
      var sec = all.filter(function (x) { return secOpen(x.tile); });
      title = t("ovSecurity");
      body = sec.length ? byRoom(sec, function (x) {
        if (x.tile.kind === "lock") { return ovRow(x, "unlock", "#FF8A3D", t("unlocked"), ro ? "" : '<button class="pill" data-ovlock="' + esc(x.id) + '">' + esc(t("lock")) + "</button>"); }
        return ovRow(x, x.tile.door ? "door" : "win", "#FF8A3D", (x.tile.state.tilted ? t("tilted") : t("open")) + " " + since(x.tile.state.since));
      }) : '<div class="allclear">' + I("check", 26) + " " + esc(t("ovSecOk")) + "</div>";
    }
    sheetShell('<div class="head"><div><h1>' + esc(title) + "</h1>" + (lead ? '<div class="subtitle">' + esc(lead) + "</div>" : "") + '</div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="blist ovlist">' + body + "</div>" + (actions ? '<div class="actions">' + actions + "</div>" : ""));
  }
  function overviewAll(what) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    shownTiles().forEach(function (x) {
      var tl = x.tile;
      if (what === "lights" && isLight(tl) && tl.state.on) { act(x.id, "off", null, { on: false }); }
      if ((what === "up" || what === "down") && tl.kind === "blind") { var v = what === "up" ? 100 : 0; if (tl.state.position !== v) { act(x.id, "position", v, { position: v }); } }
    });
  }
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
  function openSettings() { if (!pinOk()) { askPin(openSettings); return; } S.sheet = { settings: true }; renderSettings(); }

  // ---------- PIN for the settings ----------
  function pinOk() { return !(S.tablet && S.tablet.pin) || Date.now() < (S.unlockedUntil || 0) * 1000; }
  function askPin(then) {
    S.pinReturn = S.sheet && !S.sheet.pin ? S.sheet : null; S.afterPin = then || null;
    S.sheet = { pin: "", error: "" }; renderSheet();
  }
  function renderPin() {
    var p = S.sheet, dots = "";
    for (var i = 0; i < Math.max(4, p.pin.length); i++) { dots += '<i class="' + (i < p.pin.length ? "on" : "") + '"></i>'; }
    var keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "del", "0", "ok"].map(function (k) {
      if (k === "del") { return '<button class="pkey fn" data-pinkey="del" aria-label="⌫">' + I("left", 22) + "</button>"; }
      if (k === "ok") { return '<button class="pkey fn ok" data-pinkey="ok"' + (p.pin.length >= 4 ? "" : " disabled") + ">" + esc(t("pinOk")) + "</button>"; }
      return '<button class="pkey" data-pinkey="' + k + '">' + k + "</button>";
    }).join("");
    sheetShell('<div class="head"><div><h1>' + esc(t("pinTitle")) + '</h1><div class="subtitle">' + esc(p.error || t("pinLead")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="pinpad"><div class="pdots' + (p.error ? " bad" : "") + '">' + dots + '</div><div class="pkeys">' + keys + "</div></div>", "pinsheet");
  }
  function pinKey(k) {
    var p = S.sheet; if (!p || p.pin === undefined || p.busy) { return; }
    if (k === "del") { p.pin = p.pin.slice(0, -1); }
    else if (k === "ok") { if (p.pin.length >= 4) { p.busy = true; send({ type: "unlock", pin: p.pin }); } }
    else if (p.pin.length < 8) { p.pin += k; p.error = ""; }
    renderSheet();
  }
  function pinAnswer(m) {
    if (!S.sheet || S.sheet.pin === undefined) { return; }
    if (!m.ok) { S.sheet = { pin: "", error: t(m.wait ? "pinWait" : "pinWrong") }; renderSheet(); return; }
    S.unlockedUntil = m.until;
    var then = S.afterPin; S.sheet = S.pinReturn; S.afterPin = null; S.pinReturn = null;
    if (then) { closeSheet(); then(); } else if (S.sheet) { renderSheet(); } else { closeSheet(); }
    showToast(t("pinOpen"), null, 3000);
  }
  function settingsRow(attr, icon, label, value, extra) {
    return '<button class="mrow" ' + attr + '><span class="mic">' + I(icon, 20) + '</span><span class="ml"><b>' + esc(label) + "</b>" + (value ? "<span>" + esc(value) + "</span>" : "") + "</span>" + (extra || I("chev", 18)) + "</button>";
  }
  function settingsHead(title, sub, page) {
    return '<div class="head">' + (page ? '<button class="iconbtn" data-setpage="" aria-label="' + esc(t("back")) + '">' + I("left") + "</button>" : "") +
      "<div><h1>" + esc(title) + '</h1><div class="subtitle">' + esc(sub) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>";
  }
  function renderSettings() {
    var tb = S.tablet, lay = layout(), page = S.sheet.page || "";
    if (page === "tablet") { renderSettingsTablet(); return; }
    if (page === "rooms") { renderSettingsRooms(); return; }
    if (page === "keepon") { sheetShell(settingsHead(t("keepOnList"), t("setHome"), true) + keepOnListHtml()); return; }
    var themes = ["auto", "dark", "light"].map(function (p) { return '<button class="' + ((lay.theme || "auto") === p ? "on" : "") + '" data-theme="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var hidden = lay.hidden_rooms || [], shown = S.rooms.filter(function (r) { return hidden.indexOf(r.name) < 0; }).length;
    var kept = Object.keys(S.tiles).filter(function (id) { return S.tiles[id].keep_on; }).length;
    var html = settingsHead(t("settings"), tb.name + (tb.readonly ? " · " + t("readonly") : ""), false) +
      '<div class="group"><div class="label">' + esc(t("setTablet")) + '</div><div class="menu">' +
      settingsRow('data-setpage="tablet"', "frame", t("setNamePlace"), [t(tb.place), tb.room].filter(Boolean).join(" · ")) +
      '<div class="mrow"><span class="mic">' + I("sun", 20) + '</span><span class="ml"><b>' + esc(t("theme")) + '</b></span><div class="seg">' + themes + "</div></div>" +
      settingsRow('data-setpage="rooms"', "home", t("setRooms"), t("setRoomsValue", { n: shown, m: S.rooms.length })) +
      settingsRow('data-edit="1"', "plus", t("editTiles"), "") + "</div></div>";
    if (tb.arrange) {
      html += '<div class="group"><div class="label">' + esc(t("setHome")) + '</div><div class="menu">' +
        settingsRow('data-arrange="1"', "home", t("arrange"), t("setArrangeValue")) +
        settingsRow('data-setpage="keepon"', "power", t("keepOnList"), kept ? t("setKeepValue", { n: kept }) : t("setKeepNone")) + "</div></div>";
    }
    if (tb.https && location.protocol !== "https:") {
      html += '<div class="group"><div class="menu"><a class="mrow" href="' + esc(tb.https) + "#t=" + encodeURIComponent(S.token) + '"><span class="mic">' + I("mic", 20) + '</span><span class="ml"><b>' + esc(t("setTalk")) + "</b><span>" + esc(t("switchHttps")) + "</span></span>" + I("chev", 18) + "</a></div></div>";
    }
    html += '<div class="group"><button class="linkbtn" data-resetlayout="1">' + esc(t("resetView")) + "</button></div>";
    sheetShell(html);
  }
  function renderSettingsTablet() {
    var tb = S.tablet;
    var places = ["wall", "couch", "door"].map(function (p) { return '<button class="' + (tb.place === p ? "on" : "") + '" data-place="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var roomOpts = '<option value="">' + esc(t("noRoom")) + "</option>" + S.rooms.map(function (r) { return '<option' + (r.name === tb.room ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    sheetShell(settingsHead(t("setNamePlace"), tb.name, true) +
      '<div class="group"><div class="label">' + esc(t("name")) + '</div><input id="tabname" value="' + esc(tb.name) + '" maxlength="40" style="width:100%"></div>' +
      '<div class="group"><div class="label">' + esc(t("place")) + '</div><div class="seg">' + places + "</div></div>" +
      '<div class="group"><div class="label">' + esc(t("room")) + '</div><select id="tabroom" style="width:100%">' + roomOpts + "</select></div>");
  }
  function renderSettingsRooms() {
    var hidden = layout().hidden_rooms || [];
    var roomList = allRoomsOrdered().map(function (r, i) {
      var on = hidden.indexOf(r.name) < 0;
      return '<div class="item roomitem" data-roomitem="' + esc(r.name) + '"><span class="grip" data-roomgrip="1">' + I("grip", 22) + '</span><span class="grow">' + esc(r.name) + '</span><button class="tg' + (on ? "" : " off") + '" data-roomtoggle="' + esc(r.name) + '"></button></div>';
    }).join("");
    sheetShell(settingsHead(t("setRooms"), S.tablet.name, true) + '<div class="group"><div class="hint" style="text-align:left;margin-bottom:6px">' + esc(t("roomsDragHint")) + '</div><div class="list">' + roomList + "</div></div>");
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

  // ---------- arranging rooms (FHEM attribute room, for all tablets) ----------
  function startArrange() {
    closeSheet(); S.edit = false; S.arrange = { data: null };
    send({ type: "rooms_setup" }); renderTabs(); renderContent();
    document.getElementById("content").scrollTop = 0;
  }
  function arrangeHtml() {
    var d = S.arrange.data;
    var html = '<div class="arrhead"><div><h2>' + esc(t("arrange")) + '</h2><div class="lead">' + esc(t("arrangeLead")) + '</div></div><button class="pill primary" data-arrangedone="1">' + I("check", 20) + " " + esc(t("arrangeDone")) + "</button></div>";
    if (!d) { return html + '<div class="empty">…</div>'; }
    var free = d.unassigned || [], sug = free.filter(function (x) { return x.suggestion; });
    if (free.length) {
      html += '<div class="leave arrfree" data-droproom=""><div class="section" style="margin:0 0 6px"><span>' + esc(t("unassigned")) + " · " + free.length + "</span>" +
        (sug.length > 1 ? '<button class="pill" data-applyall="1">' + esc(t("applyAll", { n: sug.length })) + "</button>" : "") + "</div>" +
        free.map(function (x) {
          var quick = recentRooms().filter(function (r) { return r !== x.suggestion; }).slice(0, 3).map(function (r) {
            return '<button class="pill quick" data-moveid="' + esc(x.id) + '" data-movefrom="" data-moveto="' + esc(r) + '">' + esc(r) + "</button>";
          }).join("");
          return '<div class="row" ' + dragAttrs(x, "") + '><div class="ic">' + I(KIND_ICON[x.kind] || "power") + '</div><div class="t"><b>' + esc(x.name) + "</b><span>" + esc(x.id) + "</span>" + (x.idle ? '<em class="idletag">' + I("clock", 12) + " " + esc(t("idleFor", { t: idleText(x.idle) })) + "</em>" : "") + "</div>" +
            '<div class="qbtns">' + (x.suggestion ? '<button class="pill sug" data-moveid="' + esc(x.id) + '" data-movefrom="" data-moveto="' + esc(x.suggestion) + '">' + I("right", 18) + " " + esc(x.suggestion) + "</button>" : "") + quick +
            '<button class="pill" data-pick="' + esc(x.id) + '" data-from="">' + esc(t("chooseRoom")) + "</button></div></div>";
        }).join("") + "</div>";
    } else {
      html += '<div class="leave arrfree" data-droproom=""><div class="allclear">' + I("check", 26) + " " + esc(t("allSorted")) + '</div><div class="drophint">' + esc(t("dropHere")) + "</div></div>";
    }
    html += idleHtml();
    html += '<div class="arrgrid">' + (d.rooms || []).map(function (r) {
      return '<div class="leave arrroom" data-droproom="' + esc(r.name) + '"><div class="arrtitle"><b>' + esc(r.name) + "</b><span>" + r.devices.length + '</span><button class="mini" data-renameroom="' + esc(r.name) + '" aria-label="' + esc(t("renameRoom")) + '">' + I("pencil", 18) + "</button></div>" +
        '<div class="dchips">' + r.devices.map(function (x) {
          var other = x.rooms.filter(function (n) { return n !== r.name; });
          return '<button class="dchip' + (x.idle ? " idle" : "") + '" data-pick="' + esc(x.id) + '" data-from="' + esc(r.name) + '" ' + dragAttrs(x, r.name) + ">" + I(KIND_ICON[x.kind] || "power", 16) + " " + esc(x.name) +
            (x.idle ? '<em class="idletag">' + I("clock", 12) + " " + esc(idleText(x.idle, true)) + "</em>" : "") +
            (other.length ? "<small>" + esc(t("alsoIn", { rooms: other.join(", ") })) + "</small>" : "") +
            '<span class="dx" role="button" aria-label="' + esc(t("removeFrom", { room: r.name })) + '" data-moveid="' + esc(x.id) + '" data-movefrom="' + esc(r.name) + '" data-moveto="">' + I("x", 14) + "</span></button>";
        }).join("") + '<button class="dchip add" data-addto="' + esc(r.name) + '">' + I("plus", 16) + " " + esc(t("addDevice")) + "</button></div></div>";
    }).join("") + "</div>";
    return html;
  }
  function idleText(days, short) {
    return days >= 60 ? t(short ? "idleMonthsShort" : "idleMonths", { n: Math.floor(days / 30) }) : t(short ? "idleDaysShort" : "idleDays", { n: days });
  }
  function deleteButton(id) {
    var sure = S.arrange && S.arrange.confirm === id;
    return '<button class="pill' + (sure ? " danger" : "") + '" data-delete="' + esc(id) + '">' + I("x", 16) + " " + esc(sure ? t("deleteSure") : t("deleteDevice")) + "</button>";
  }
  function idleHtml() {
    var list = allArrangeDevices().filter(function (x) { return x.idle; });
    if (!list.length) { return ""; }
    list.sort(function (a, b) { return b.idle - a.idle; });
    return '<div class="leave arridle"><div class="section" style="margin:0 0 4px"><span>' + esc(t("idleTitle")) + " · " + list.length + '</span></div><div class="lead">' + esc(t("idleLead")) + "</div>" +
      list.map(function (x) {
        return '<div class="row"><div class="ic">' + I(KIND_ICON[x.kind] || "power") + '</div><div class="t"><b>' + esc(x.name) + "</b><span>" + esc([x.id, x.rooms.join(", ") || t("unassigned"), t("idleFor", { t: idleText(x.idle) })].join(" · ")) + "</span></div>" + deleteButton(x.id) + "</div>";
      }).join("") + '<div class="hint" style="text-align:left;margin-top:8px">' + esc(t("deleteHint")) + "</div></div>";
  }
  function arrangeDevice(id) {
    var d = S.arrange && S.arrange.data; if (!d) { return null; }
    var all = (d.unassigned || []).concat.apply(d.unassigned || [], (d.rooms || []).map(function (r) { return r.devices; }));
    return all.filter(function (x) { return x.id === id; })[0] || null;
  }
  function renderPick() {
    var pick = S.sheet.arrange, dev = arrangeDevice(pick.id); if (!dev) { closeSheet(); return; }
    var rooms = (S.arrange.data.rooms || []).map(function (r) { return r.name; });
    var pills = rooms.map(function (n) {
      return '<button class="pill' + (n === pick.from ? " on" : "") + '" data-moveid="' + esc(dev.id) + '" data-movefrom="' + esc(pick.from) + '" data-moveto="' + esc(n) + '">' + esc(n) + "</button>";
    }).join("");
    sheetShell('<div class="head"><div><h1>' + esc(dev.name) + '</h1><div class="subtitle">' + esc(t("nowIn", { room: pick.from || t("unassigned") })) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="group"><div class="label">' + esc(t("moveTo")) + '</div><div class="roompills">' + pills + "</div></div>" +
      '<div class="group"><div class="label">' + esc(t("newRoom")) + '</div><div class="inrow"><input id="newroom" maxlength="40" placeholder="' + esc(t("newRoom")) + '"><button class="pill primary" data-newroom="1">' + esc(t("create")) + "</button></div></div>" +
      (pick.from ? '<div class="group actions"><button class="pill danger" data-moveid="' + esc(dev.id) + '" data-movefrom="' + esc(pick.from) + '" data-moveto="">' + esc(t("removeFrom", { room: pick.from })) + "</button></div>" : "") +
      (dev.idle ? '<div class="group"><div class="label">' + esc(t("idleTitle")) + " · " + esc(t("idleFor", { t: idleText(dev.idle) })) + '</div><div class="actions">' + deleteButton(dev.id) + "</div></div>" : ""));
  }
  // type-ahead: add any device to a room
  function allArrangeDevices() {
    var d = S.arrange && S.arrange.data, seen = {}, list = [];
    if (!d) { return list; }
    (d.unassigned || []).concat.apply(d.unassigned || [], (d.rooms || []).map(function (r) { return r.devices; })).forEach(function (x) {
      if (!seen[x.id]) { seen[x.id] = true; list.push(x); }
    });
    return list;
  }
  function addMatches(room, query) {
    var q = String(query || "").toLowerCase().trim(), words = q.split(/\s+/).filter(Boolean);
    var list = allArrangeDevices().filter(function (x) {
      var text = (x.name + " " + x.id + " " + (x.rooms || []).join(" ")).toLowerCase();
      return words.every(function (w) { return text.indexOf(w) >= 0; });
    });
    // devices without a room first, then by name
    list.sort(function (a, b) { return (a.rooms.length ? 1 : 0) - (b.rooms.length ? 1 : 0) || a.name.localeCompare(b.name); });
    return list.slice(0, 40);
  }
  function addResultsHtml(room, query) {
    var list = addMatches(room, query);
    if (!list.length) { return '<div class="empty" style="padding:20px 0">' + esc(t("noMatch")) + "</div>"; }
    return list.map(function (x) {
      var here = x.rooms.indexOf(room) >= 0, from = here ? room : (x.rooms[0] || "");
      var sub = here ? t("alreadyHere") : x.rooms.length ? t("fromRoom", { room: x.rooms.join(", ") }) : t("unassigned");
      return '<button class="row addrow' + (here ? " here" : "") + '"' + (here ? " disabled" : ' data-moveid="' + esc(x.id) + '" data-movefrom="' + esc(from) + '" data-moveto="' + esc(room) + '"') + '><div class="ic">' + I(KIND_ICON[x.kind] || "power") + '</div><div class="t"><b>' + esc(x.name) + "</b><span>" + esc(x.id + " · " + sub) + "</span></div>" + (here ? I("check", 18) : I("plus", 18)) + "</button>";
    }).join("");
  }
  function renderAdd() {
    var room = S.sheet.addto, input = document.getElementById("addsearch"), query = input ? input.value : "";
    if (input && document.getElementById("addresults")) { document.getElementById("addresults").innerHTML = addResultsHtml(room, query); return; }
    sheetShell('<div class="head"><div><h1>' + esc(t("addTo", { room: room })) + '</h1></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="group"><input id="addsearch" autocomplete="off" placeholder="' + esc(t("searchDevice")) + '" style="width:100%"></div><div class="group" id="addresults">' + addResultsHtml(room, "") + "</div>");
    var el = document.getElementById("addsearch");
    el.addEventListener("input", function () { document.getElementById("addresults").innerHTML = addResultsHtml(room, el.value); });
    el.addEventListener("keydown", function (ev) {
      if (ev.key !== "Enter") { return; }
      var first = document.querySelector("#addresults [data-moveto]");
      if (first) { first.click(); }
    });
    setTimeout(function () { el.focus(); }, 50);
  }
  // who is at home since when, who is away since when
  function whenText(text) {
    var d = parseTime(text); if (!d) { return ""; }
    var now = new Date(), y = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1), clock = clockText(d);
    if (d.toDateString() === now.toDateString()) { return clock; }
    if (d.toDateString() === y.toDateString()) { return t("yesterdayAt", { t: clock }); }
    return t("dayAt", { d: T.weekdays[d.getDay()].slice(0, 2) + " " + d.getDate() + "." + (d.getMonth() + 1) + ".", t: clock });
  }
  function renderPeople() {
    var people = (S.header.presence && S.header.presence.people) || [], colors = ["#FFB547", "#5AA9FF", "#3DDBB8", "#9B8CFF"];
    function rows(list, home) {
      return list.map(function (p, i) {
        var when = p.since ? t(home ? "arrived" : "left", { t: whenText(p.since) }) + " · " + since(p.since) : "";
        return '<div class="row"><div class="av big" style="background:' + (home ? colors[i % 4] : "var(--card2)") + ";color:" + (home ? "#0B0E13" : "var(--mu)") + '">' + esc(p.initial) + '</div><div class="t"><b>' + esc(p.name) + "</b><span>" + esc(when) + "</span></div></div>";
      }).join("");
    }
    var home = people.filter(function (p) { return p.home; }), away = people.filter(function (p) { return !p.home; });
    sheetShell('<div class="head"><div><h1>' + esc(t("peopleTitle")) + '</h1><div class="subtitle">' + esc(home.length ? t("atHome", { n: home.length }) : t("nobody")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      (home.length ? '<div class="group"><div class="label">' + esc(t("peopleHome")) + '</div><div class="list">' + rows(home, true) + "</div></div>" : "") +
      (away.length ? '<div class="group"><div class="label">' + esc(t("peopleAway")) + '</div><div class="list">' + rows(away, false) + "</div></div>" : ""));
  }
  function renderRename() {
    var room = S.sheet.rename;
    sheetShell('<div class="head"><div><h1>' + esc(t("renameRoom")) + '</h1><div class="subtitle">' + esc(room) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="group"><div class="inrow"><input id="renameroom" maxlength="40" value="' + esc(room) + '"><button class="pill primary" data-renamesave="1">' + esc(t("save")) + "</button></div></div>");
  }
  function validRoom(name) {
    name = String(name || "").trim();
    if (!name || /[,;|"\\]/.test(name)) { showBanner(t("badRoom"), 4000); return ""; }
    return name;
  }
  function dragAttrs(x, from) {
    return 'data-dragid="' + esc(x.id) + '" data-dragfrom="' + esc(from) + '" data-dragname="' + esc(x.name) + '" data-dragkind="' + esc(x.kind) + '"';
  }
  // the last rooms chosen on this tablet, offered for devices without a room
  function recentRooms() {
    try { var list = JSON.parse(store("dashRecentRooms") || "[]"); return Array.isArray(list) ? list : []; } catch (e) { return []; }
  }
  function rememberRoom(room) {
    var list = [room].concat(recentRooms().filter(function (r) { return r !== room; })).slice(0, 6);
    store("dashRecentRooms", JSON.stringify(list));
  }
  function moveDevice(id, from, to) {
    if (!id || from === to) { return; }
    if (to) { rememberRoom(to); }
    send({ type: "move_device", id: id, from: from, to: to });
    if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not allowed */ } }
  }
  // dragging devices between rooms: mouse at once, touch after holding
  var drag = null, dragEnded = 0;
  function dragStart(ev) {
    var src = S.arrange && !closest(ev.target, "data-moveto") ? closest(ev.target, "data-dragid") : null;
    if (!src) { return false; }
    drag = { id: src.getAttribute("data-dragid"), from: src.getAttribute("data-dragfrom"), name: src.getAttribute("data-dragname"), kind: src.getAttribute("data-dragkind"), x: ev.clientX, y: ev.clientY, mouse: ev.pointerType === "mouse", active: false };
    if (!drag.mouse) { drag.timer = setTimeout(function () { if (drag && !drag.active) { dragActivate(drag.x, drag.y); } }, 280); }
    return true;
  }
  function dragActivate(x, y) {
    drag.active = true;
    if (navigator.vibrate) { try { navigator.vibrate(10); } catch (e) { /* not allowed */ } }
    var g = document.createElement("div"); g.className = "dragghost"; g.innerHTML = I(KIND_ICON[drag.kind] || "power", 16) + " " + esc(drag.name);
    document.body.appendChild(g); drag.ghost = g; document.body.classList.add("dragging"); dragMove(x, y);
  }
  function dragTarget(x, y) {
    var el = document.elementFromPoint(x, y);
    return el ? closest(el, "data-droproom") : null;
  }
  function dragMove(x, y) {
    drag.ghost.style.transform = "translate(" + (x + 12) + "px," + (y + 12) + "px)";
    var over = dragTarget(x, y);
    Array.prototype.forEach.call(document.querySelectorAll("[data-droproom].over"), function (el) { if (el !== over) { el.classList.remove("over"); } });
    if (over) { over.classList.add("over"); }
  }
  function dragEnd(x, y, cancel) {
    if (!drag) { return; }
    clearTimeout(drag.timer);
    if (drag.active) {
      var over = cancel ? null : dragTarget(x, y);
      if (over) { moveDevice(drag.id, drag.from, over.getAttribute("data-droproom")); }
      drag.ghost.parentNode.removeChild(drag.ghost); document.body.classList.remove("dragging");
      Array.prototype.forEach.call(document.querySelectorAll("[data-droproom].over"), function (el) { el.classList.remove("over"); });
      dragEnded = Date.now();
    }
    drag = null;
  }
  document.addEventListener("pointermove", function (ev) {
    if (!drag) { return; }
    if (drag.active) { dragMove(ev.clientX, ev.clientY); ev.preventDefault(); return; }
    if (Math.abs(ev.clientX - drag.x) + Math.abs(ev.clientY - drag.y) > 8) {
      if (drag.mouse) { dragActivate(ev.clientX, ev.clientY); } else { clearTimeout(drag.timer); drag = null; }
    }
  });
  document.addEventListener("pointerup", function (ev) { dragEnd(ev.clientX, ev.clientY, false); });
  document.addEventListener("pointercancel", function () { dragEnd(0, 0, true); });
  document.addEventListener("touchmove", function (ev) { if (drag && drag.active) { ev.preventDefault(); } }, { passive: false });

  // edit mode: drag tiles to a new place in the room (order per tablet)
  var tdrag = null;
  function tileDragStart(ev) {
    var el = S.edit && !closest(ev.target, "data-edit") ? closest(ev.target, "data-tile") : null;
    if (!el || el.classList.contains("hiddenTile")) { return false; }
    tdrag = { el: el, x: ev.clientX, y: ev.clientY, mouse: ev.pointerType === "mouse", active: false };
    if (!tdrag.mouse) { tdrag.timer = setTimeout(function () { if (tdrag && !tdrag.active) { tileDragActivate(); } }, 250); }
    return true;
  }
  function tileDragActivate() {
    tdrag.active = true; tdrag.el.classList.add("dragtile"); document.body.classList.add("dragging");
    if (navigator.vibrate) { try { navigator.vibrate(10); } catch (e) { /* not allowed */ } }
  }
  function tileDragMove(x, y) {
    var over = document.elementFromPoint(x, y), target = over ? closest(over, "data-tile") : null;
    if (!target || target === tdrag.el || target.parentNode !== tdrag.el.parentNode || target.classList.contains("hiddenTile")) { return; }
    var r = target.getBoundingClientRect(), after = y > r.bottom || (y >= r.top && x > r.left + r.width / 2);
    target.parentNode.insertBefore(tdrag.el, after ? target.nextSibling : target);
  }
  function tileDragEnd() {
    if (!tdrag) { return; }
    clearTimeout(tdrag.timer);
    if (tdrag.active) {
      var grid = tdrag.el.parentNode, room = roomByName(S.tab.slice(5)), key = S.tab === "home" ? HOME : room && room.name;
      tdrag.el.classList.remove("dragtile"); document.body.classList.remove("dragging");
      if (key) {
        var ids = Array.prototype.map.call(grid.querySelectorAll("[data-tile]"), function (el) { return el.getAttribute("data-tile"); });
        var lay = copyLayout(); lay.tile_order = lay.tile_order || {}; lay.tile_order[key] = ids; saveLayout(lay);
      }
      dragEnded = Date.now();
    }
    tdrag = null;
  }
  document.addEventListener("pointermove", function (ev) {
    if (!tdrag) { return; }
    if (tdrag.active) { tileDragMove(ev.clientX, ev.clientY); ev.preventDefault(); return; }
    if (Math.abs(ev.clientX - tdrag.x) + Math.abs(ev.clientY - tdrag.y) > 8) {
      if (tdrag.mouse) { tileDragActivate(); } else { clearTimeout(tdrag.timer); tdrag = null; }
    }
  });
  document.addEventListener("pointerup", tileDragEnd);

  // order of the rooms in the settings: drag the handle of a row
  var rdrag = null;
  function roomDragStart(ev) {
    var grip = closest(ev.target, "data-roomgrip"); if (!grip) { return false; }
    var row = closest(grip, "data-roomitem"); if (!row) { return false; }
    rdrag = { el: row }; row.classList.add("dragrow"); document.body.classList.add("dragging");
    if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not allowed */ } }
    ev.preventDefault();
    return true;
  }
  document.addEventListener("pointermove", function (ev) {
    if (!rdrag) { return; }
    ev.preventDefault();
    var over = document.elementFromPoint(ev.clientX, ev.clientY), target = over ? closest(over, "data-roomitem") : null;
    if (!target || target === rdrag.el || target.parentNode !== rdrag.el.parentNode) { return; }
    var r = target.getBoundingClientRect();
    target.parentNode.insertBefore(rdrag.el, ev.clientY > r.top + r.height / 2 ? target.nextSibling : target);
  });
  function roomDragEnd() {
    if (!rdrag) { return; }
    var list = rdrag.el.parentNode;
    rdrag.el.classList.remove("dragrow"); document.body.classList.remove("dragging"); rdrag = null; dragEnded = Date.now();
    var names = Array.prototype.map.call(list.querySelectorAll("[data-roomitem]"), function (el) { return el.getAttribute("data-roomitem"); });
    var lay = copyLayout(); lay.room_order = names; saveLayout(lay);
  }
  document.addEventListener("pointerup", roomDragEnd);
  document.addEventListener("pointercancel", roomDragEnd);
  document.addEventListener("touchmove", function (ev) { if (rdrag) { ev.preventDefault(); } }, { passive: false });
  document.addEventListener("pointercancel", tileDragEnd);
  document.addEventListener("touchmove", function (ev) { if (tdrag && tdrag.active) { ev.preventDefault(); } }, { passive: false });

  function arrangeClick(target) {
    var el;
    if ((el = closest(target, "data-arrange"))) { startArrange(); return true; }
    if (!S.arrange) { return false; }
    if ((el = closest(target, "data-arrangedone"))) { S.arrange = null; renderTabs(); renderContent(); return true; }
    if ((el = closest(target, "data-applyall"))) {
      (S.arrange.data.unassigned || []).filter(function (x) { return x.suggestion; }).forEach(function (x) { moveDevice(x.id, "", x.suggestion); });
      return true;
    }
    if ((el = closest(target, "data-moveto"))) {
      moveDevice(el.getAttribute("data-moveid"), el.getAttribute("data-movefrom"), el.getAttribute("data-moveto"));
      // adding devices to a room: the search stays open for the next one
      if (!(S.sheet && S.sheet.addto !== undefined)) { closeSheet(); }
      return true;
    }
    if ((el = closest(target, "data-pick"))) { S.sheet = { arrange: { id: el.getAttribute("data-pick"), from: el.getAttribute("data-from") } }; renderSheet(); return true; }
    if ((el = closest(target, "data-renameroom"))) { S.sheet = { rename: el.getAttribute("data-renameroom") }; renderSheet(); return true; }
    if ((el = closest(target, "data-delete"))) {
      var did = el.getAttribute("data-delete");
      if (S.arrange.confirm === did) { S.arrange.confirm = null; send({ type: "delete_device", id: did }); closeSheet(); return true; }
      S.arrange.confirm = did; renderContent(); if (S.sheet) { renderSheet(); }
      return true;
    }
    if ((el = closest(target, "data-addto"))) { S.sheet = { addto: el.getAttribute("data-addto") }; renderSheet(); return true; }
    return arrangeSheetClick(target);
  }
  function arrangeSheetClick(target) {
    if (closest(target, "data-newroom")) {
      var room = validRoom(document.getElementById("newroom").value), pick = S.sheet && S.sheet.arrange;
      if (room && pick) { moveDevice(pick.id, pick.from, room); closeSheet(); }
      return true;
    }
    if (closest(target, "data-renamesave")) {
      var to = validRoom(document.getElementById("renameroom").value), from = S.sheet && S.sheet.rename;
      if (to && from && to !== from) { send({ type: "rename_room", from: from, to: to }); }
      closeSheet(); return true;
    }
    return false;
  }

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
    if (S.setupStep === "rooms" && S.rooms.length) { renderSetupRooms(); return; }
    var chosen = S.setupPlace || "wall";
    var suggested = S.setupRoom !== undefined ? S.setupRoom : (S.rooms[0] ? S.rooms[0].name : "");
    if (S.rooms.length) { S.setupRoom = suggested; }
    var cards = [["wall", "frame"], ["couch", "sofa"], ["door", "bell"]].map(function (p) {
      return '<button class="pl' + (chosen === p[0] ? " on" : "") + '" data-setupplace="' + p[0] + '"><div class="pi">' + I(p[1]) + "</div><h3>" + esc(t(p[0])) + "</h3><ul>" + T[p[0] + "List"].map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></button>";
    }).join("");
    var roomOpts = '<option value="">' + esc(t("noRoom")) + "</option>" + S.rooms.map(function (r) { return "<option" + (r.name === suggested ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    app.innerHTML = '<div class="ob"><div class="obbox"><div class="logo"><div class="m"></div>' + esc(t("home")) + "</div>" + setupSteps(1) + "<h1>" + esc(t("whereTitle")) + '</h1><p class="l">' +
      esc(t("whereText", { rooms: S.rooms.length, tiles: Object.keys(S.tiles).length })) + '</p><div class="places">' + cards + '</div><div class="found">' + I("home") + " " + esc(t("roomOfTablet")) +
      ' <select id="setuproom">' + roomOpts + '</select><button class="pill primary" data-setupdone="1">' + esc(t(S.rooms.length ? "next" : "pickDone")) + "</button></div></div></div>";
  }
  function setupSteps(step) {
    if (!S.rooms.length) { return ""; }
    return '<div class="steps"><span class="' + (step === 1 ? "on" : "done") + '"></span><span class="' + (step === 2 ? "on" : "") + '"></span></div>';
  }
  // icon from the room name, for the big room tiles of the setup
  var ROOM_ICONS = [
    ["bed", /schlaf|bed|gäste|guest/], ["star", /kind|kid|baby|nursery/], ["bath", /bad|bath|wc|toilet|dusch|shower/],
    ["pot", /küche|kueche|kitchen|koch/], ["sofa", /wohn|living|lounge|stube/], ["desk", /büro|buero|office|arbeit|study/],
    ["car", /garage|carport|auto/], ["tree", /garten|garden|terrass|balkon|balcony|außen|aussen|outdoor|hof/],
    ["stairs", /flur|diele|gang|hall|treppe|stair|eingang|entrance/], ["film", /kino|cinema|media|tv/],
    ["gear", /keller|technik|tech|basement|heiz|server|hwr|wasch|laundry/], ["pot", /ess|dining/]
  ];
  function roomIcon(name) {
    var n = String(name).toLowerCase();
    for (var i = 0; i < ROOM_ICONS.length; i++) { if (ROOM_ICONS[i][1].test(n)) { return ROOM_ICONS[i][0]; } }
    return "home";
  }
  function renderSetupRooms() {
    var hidden = S.setupHidden || [], rooms = allRoomsOrdered();
    var shown = rooms.filter(function (r) { return hidden.indexOf(r.name) < 0; }).length;
    var tiles = rooms.map(function (r) {
      var on = hidden.indexOf(r.name) < 0, n = roomTiles(r, true).length;
      return '<button class="rpick' + (on ? " on" : "") + '" data-pickroom="' + esc(r.name) + '" aria-pressed="' + on + '"><span class="ck">' + I("check", 18) + '</span><span class="ri">' + I(roomIcon(r.name), 40) + '</span><b>' + esc(r.name) + "</b><span>" + esc(n === 1 ? t("pickDevice") : t("pickDevices", { n: n })) + "</span></button>";
    }).join("");
    app.innerHTML = '<div class="ob"><div class="obbox"><div class="logo"><div class="m"></div>' + esc(t("home")) + "</div>" + setupSteps(2) + "<h1>" + esc(t("pickTitle")) + '</h1><p class="l">' + esc(t("pickText")) +
      '</p><div class="rpicks">' + tiles + '</div><div class="found pickbar"><button class="pill" data-setupback="1">' + I("left", 18) + " " + esc(t("pickBack")) + '</button><span class="cnt">' + esc(t("pickCount", { n: shown, m: rooms.length })) + '</span><button class="pill" data-pickall="' + (shown === rooms.length ? "0" : "1") + '">' + esc(t(shown === rooms.length ? "pickNone" : "pickAll")) +
      '</button><button class="pill primary" data-setupfinish="1"' + (shown ? "" : " disabled") + ">" + esc(t("pickDone")) + "</button></div></div></div>";
  }
  function finishSetup() {
    var room = S.setupRoom || "", pl = S.setupPlace || "wall";
    var label = { wall: "Wand", couch: "Couch", door: "Tür" }[pl];
    send({ type: "setup", place: pl, room: room, name: (room ? room + " " : "") + (GERMAN ? label : pl) });
    if (S.setupHidden) {
      var lay = copyLayout(); lay.hidden_rooms = S.setupHidden.slice();
      S.tablet.layout = lay; send({ type: "layout", layout: lay });
    }
    S.tablet.place = pl; S.tablet.room = room; S.setupStep = null; S.tab = startTab(); render(); applyTheme(); wakeLock();
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
    var open = shownList(h.open);
    if (open.length) { items += '<div class="x o">' + I("win", 20) + " " + esc(open.length <= 3 ? open.map(function (o) { return o.name; }).join(", ") + " " + t("open").toLowerCase() : t("openCount", { n: open.length })) + "</div>"; }
    else { items += '<div class="x">' + I("lock", 20) + " " + esc(t("allClosed")) + "</div>"; }
    binTexts().forEach(function (b) { items += '<div class="x o">' + I("trash", 20) + " " + esc(b) + "</div>"; });
    var nextCal = ((h.calendar && h.calendar.entries) || []).filter(function (e) { return e.day === 0 && !e.allday && !e.now; })[0];
    if (nextCal) { items += '<div class="x">' + I("clock", 20) + " " + esc(nextCal.at + " " + nextCal.summary) + "</div>"; }
    if (h.energy && h.energy.solar) { items += '<div class="x" style="margin-left:auto">' + I("bolt", 20) + " " + watt(h.energy.solar) + " " + esc(t("solar")) + "</div>"; }
    var shift = (now.getMinutes() % 5) * 6 - 12;
    el.className = "ss" + (isNight() ? " night" : "");
    el.innerHTML = '<div class="wrap" style="transform:translate(' + shift + "px," + (-shift) + 'px)"><div class="t">' + clockText(now) + '</div><div class="d">' + esc(dateText(now)) + "</div>" +
      (w && w.temperature !== null && w.temperature !== undefined ? '<div class="w"><b>' + num(w.temperature, 0) + "°</b><span>" + esc(w.condition || "") + "</span>" + (w.high !== null && w.high !== undefined ? "<span>" + num(w.low, 0) + "° / " + num(w.high, 0) + "°</span>" : "") + "</div>" + saverHours(w) : "") +
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

  // a short message at the bottom, optionally with "Try again"
  function showToast(text, retryId, ms, button) {
    var el = document.getElementById("toast");
    if (!el) { el = document.createElement("div"); el.id = "toast"; document.body.appendChild(el); }
    el.className = retryId || button ? "warn" : "";
    el.innerHTML = "<span>" + esc(text) + "</span>" + (retryId ? '<button class="pill" data-retry="' + esc(retryId) + '">' + esc(t("retry")) + "</button>" : "") + (button || "");
    clearTimeout(S.toastTimer);
    S.toastTimer = setTimeout(hideToast, ms || 7000);
  }
  // "All off" switches in groups and then tells which devices stayed on
  function allOffResult(m) {
    var left = m.left || [];
    if (!left.length) { if (m.done > 1) { showToast(t("offDone", { n: m.done }), null, 3000); } return; }
    showToast(t("offLeft", { names: left.map(function (x) { return x.name; }).join(", ") }), null, 15000,
      '<button class="pill" data-alloffagain="' + esc(left.map(function (x) { return x.id; }).join("\n")) + '">' + esc(t("offAgain")) + "</button>");
  }
  function hideToast() { var el = document.getElementById("toast"); if (el && el.parentNode) { el.parentNode.removeChild(el); } }
  function failed(m) {
    if (m.id && S.pending[m.id]) { clearTimeout(S.pending[m.id]); delete S.pending[m.id]; }
    showToast(t("failed", { name: m.name || "", reason: m.reason || "" }), m.id && S.last[m.id] ? m.id : null, 10000);
  }
  function retry(id) {
    hideToast();
    var l = S.last[id]; if (!l || !S.tiles[id]) { return; }
    act(id, l.action, l.value, l.optimistic);
  }
  function tapHint() {
    if (!S.tablet || !S.tablet.place || S.tablet.readonly || store("dashTapHint")) { return; }
    store("dashTapHint", "1"); showToast(t("tapHint"), null, 9000);
  }
  // scenes and unlocking need a second tap within 4 s
  function armed(el, key, label) {
    var a = S.arm;
    if (a && a.key === key && Date.now() - a.at < 4000) { disarm(); return true; }
    disarm();
    S.arm = { key: key, at: Date.now(), el: el, html: el.innerHTML };
    el.classList.add("arm"); el.innerHTML = I("check", 20) + " " + esc(label);
    if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not allowed */ } }
    S.arm.timer = setTimeout(disarm, 4000);
    return false;
  }
  function disarm() {
    var a = S.arm; if (!a) { return; }
    S.arm = null; clearTimeout(a.timer);
    if (a.el && a.el.isConnected) { a.el.classList.remove("arm"); a.el.innerHTML = a.html; }
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
    if (dragStart(ev) || tileDragStart(ev) || roomDragStart(ev)) { return; }
    var slider = closest(ev.target, "data-slider"); if (slider) { sliderDrag(slider, ev); return; }
    var cs = closest(ev.target, "data-cstrip"); if (cs) { colorDrag(cs, ev); return; }
    var hs = closest(ev.target, "data-hslide"); if (hs) { hslideDrag(hs, ev); return; }
    var ring = closest(ev.target, "data-ring"); if (ring) { ringDrag(ring, ev); return; }
    var slide = closest(ev.target, "data-slide") || (ev.target.closest ? ev.target.closest("#slide") : null); if (slide) { slideDrag(slide, ev); return; }
    var tile = closest(ev.target, "data-tile");
    if (tile && !S.edit) {
      var id = tile.getAttribute("data-tile");
      var pk = S.tiles[id] && S.tiles[id].kind;
      press = { id: id, x: ev.clientX, y: ev.clientY, long: false, dim: pk === "dimmer" || pk === "blind" || pk === "fan", el: tile };
      press.timer = setTimeout(function () { if (press && press.id === id) { press.long = true; if (navigator.vibrate) { navigator.vibrate(10); } openSheet(id); } }, 480);
    }
  }, { passive: false });
  document.addEventListener("pointermove", function (ev) {
    if (press && press.sliding) { tileSlideMove(ev); return; }
    var dx = press ? Math.abs(ev.clientX - press.x) : 0, dy = press ? Math.abs(ev.clientY - press.y) : 0;
    if (press && press.id && press.dim && !press.long && dx > 12 && dx > dy * 1.5) { clearTimeout(press.timer); tileSlideStart(ev); return; }
    if (press && press.id && (dx > 10 || dy > 10)) { clearTimeout(press.timer); press = null; }
  });
  document.addEventListener("pointerup", function () {
    if (press && press.timer) { clearTimeout(press.timer); }
    if (press && press.sliding) { tileSlideEnd(); }
  });
  document.addEventListener("pointercancel", function () { if (press && press.sliding) { tileSlideEnd(); } });

  // dimmers and blinds: swipe sideways on the tile, like a slider over the whole tile
  function tileValue(tile) { return tile.kind === "dimmer" ? (tile.state.on ? (tile.state.level || 0) : 0) : tile.kind === "fan" ? (tile.state.percent || 0) : (tile.state.position || 0); }
  function fanModeOf(v) { return v <= 0 ? "off" : v <= 33 ? "low" : v <= 66 ? "medium" : "high"; }
  function tileSlideStart(ev) {
    var tile = S.tiles[press.id]; if (!tile || !press.el) { press = null; return; }
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); press = null; return; }
    press.sliding = true; press.start = tileValue(tile); press.value = press.start; press.x = ev.clientX;
    press.width = press.el.getBoundingClientRect().width || 200;
    press.el.classList.add("sliding");
    if (!press.el.querySelector(".slidefill")) { var f = document.createElement("div"); f.className = "slidefill" + (tile.kind === "blind" || tile.kind === "fan" ? " teal" : ""); press.el.insertBefore(f, press.el.firstChild); }
    S.sliding = true;
    if (navigator.vibrate) { try { navigator.vibrate(6); } catch (e) { /* not allowed */ } }
    tileSlideMove(ev);
  }
  function tileSlideMove(ev) {
    // the whole tile width is 100 %, starting from the current value
    var v = Math.round(Math.max(0, Math.min(100, press.start + (ev.clientX - press.x) / press.width * 100)));
    press.value = v;
    var f = press.el.querySelector(".slidefill"); if (f) { f.style.width = v + "%"; }
    var sub = press.el.querySelector(".s"); if (sub) { sub.textContent = v + " %"; }
    if (ev.cancelable) { ev.preventDefault(); }
  }
  function tileSlideEnd() {
    var id = press.id, v = press.value, tile = S.tiles[id];
    press = null; S.sliding = false; dragEnded = Date.now();
    if (!tile) { return; }
    if (tile.kind === "dimmer") { act(id, "level", v, v > 0 ? { on: true, level: v } : { on: false }); } else if (tile.kind === "fan") { act(id, "fan_percent", v, { percent: v, on: v > 0, mode: fanModeOf(v) }); } else { act(id, "position", v, { position: v }); }
  }

  document.addEventListener("click", function (ev) {
    if (press && press.saver) { var fresh = Date.now() - press.saver < 800; press = null; if (fresh) { return; } }
    var target = ev.target, el;
    if (Date.now() - dragEnded < 400) { return; }
    if (arrangeClick(target)) { return; }
    if ((el = closest(target, "data-pinkey"))) { pinKey(el.getAttribute("data-pinkey")); return; }
    if ((el = closest(target, "data-half")) && S.sheet && S.tiles[S.sheet.id]) { act(S.sheet.id, "position", 50, { position: 50 }); renderSheet(); return; }
    if ((el = closest(target, "data-keepon"))) {
      if (!pinOk()) { askPin(null); return; }
      var kid = el.getAttribute("data-keepon"), kt = S.tiles[kid];
      if (kt) {
        kt.keep_on = !kt.keep_on; send({ type: "keep_on", id: kid, keep: kt.keep_on });
        (S.header.running || []).forEach(function (r) { if (r.id === kid) { r.keep_on = kt.keep_on; } });
        renderContent(); if (S.sheet) { renderSheet(); }
      }
      return;
    }
    if ((el = closest(target, "data-mplay")) && !S.edit) {
      var mid = el.getAttribute("data-mplay"), mt = S.tiles[mid];
      if (mt) { act(mid, "toggle", null, { playing: !mt.state.playing }); }
      press = null; return;
    }
    if ((el = closest(target, "data-media"))) {
      var mw = el.getAttribute("data-media"), ms2 = S.tiles[S.sheet.id];
      act(S.sheet.id, mw, null, mw === "toggle" && ms2 ? { playing: !ms2.state.playing } : null);
      if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not allowed */ } }
      renderSheet(); return;
    }
    if ((el = closest(target, "data-inopt")) && S.sheet) { setInput(el.getAttribute("data-inopt"), el.getAttribute("data-val")); renderSheet(); return; }
    if ((el = closest(target, "data-inbtn")) && S.sheet) { act(S.sheet.id, "input", { name: el.getAttribute("data-inbtn"), value: null }); el.classList.add("on"); setTimeout(function () { el.classList.remove("on"); }, 800); return; }
    if ((el = closest(target, "data-intextset")) && S.sheet) {
      var tn = el.getAttribute("data-intextset"), tf = document.querySelector('#sheet [data-intext="' + cssEsc(tn) + '"]');
      if (tf) { S.sliding = false; setInput(tn, tf.value.trim()); renderSheet(); } return;
    }
    if ((el = closest(target, "data-fanmode")) && S.sheet) {
      var fm = el.getAttribute("data-fanmode"), ft = S.tiles[S.sheet.id], fp = { off: 0, low: 33, medium: 66, high: 100 }[fm];
      if (ft) {
        if (ft.kind === "fan") { act(ft.id, "fan_mode", fm, { mode: fm, percent: fp, on: fp > 0 }); } else { act(ft.id, "fan_mode", fm, { fan: { mode: fm, percent: fp } }); }
      }
      renderSheet(); return;
    }
    if ((el = closest(target, "data-swatch")) && S.sheet) { var sw = el.getAttribute("data-swatch"); act(S.sheet.id, "rgb", sw, { rgb: sw, on: true }); renderSheet(); return; }
    if ((el = closest(target, "data-timer")) && S.sheet) { setTimer(S.sheet.id, Number(el.getAttribute("data-timer"))); return; }
    if ((el = closest(target, "data-preset"))) {
      var pn = Number(el.getAttribute("data-preset"));
      act(S.sheet.id, "preset", pn, { channel: pn, on: true }); renderSheet(); return;
    }
    if ((el = closest(target, "data-tile")) && !closest(target, "data-edit") && !closest(target, "data-step")) {
      var id = el.getAttribute("data-tile");
      if (S.edit) { return; }
      if (press && press.long) { press = null; return; }
      press = null;
      // the icon switches, the rest of the tile opens the details
      var tt = S.tiles[id];
      if (tt && TAP_TOGGLES[tt.kind] && !(target.closest && target.closest(".ic"))) { openSheet(id); return; }
      tap(id); return;
    }
    if ((el = closest(target, "data-edit"))) {
      var tileEl = closest(el, "data-tile");
      if (tileEl) {
        var lay = copyLayout(), hidden = lay.hidden_tiles || [], tid = tileEl.getAttribute("data-tile");
        if (el.getAttribute("data-edit") === "hide") { if (hidden.indexOf(tid) < 0) { hidden.push(tid); } } else { hidden = hidden.filter(function (x) { return x !== tid; }); }
        lay.hidden_tiles = hidden; saveLayout(lay); return;
      }
      S.edit = true; closeSheet(); if (S.tab === "history") { var first = visibleRooms()[0]; if (first) { S.tab = "room:" + first.name; } } renderTabs(); renderContent(); return;
    }
    if ((el = closest(target, "data-editdone"))) { S.edit = false; renderContent(); return; }
    if ((el = closest(target, "data-roompop"))) { if (S.edit) { return; } S.sheet = { room: el.getAttribute("data-roompop"), open: {} }; renderSheet(); return; }
    if ((el = closest(target, "data-pexp")) && S.sheet && S.sheet.room) { var pg = el.getAttribute("data-pexp"); S.sheet.open[pg] = !S.sheet.open[pg]; renderSheet(); return; }
    if ((el = closest(target, "data-pgroup")) && S.sheet && S.sheet.room) { roomGroupAction(el.getAttribute("data-pgroup")); return; }
    if ((el = closest(target, "data-ptoggle"))) { tap(el.getAttribute("data-ptoggle")); return; }
    if ((el = closest(target, "data-pdetail"))) { openSheet(el.getAttribute("data-pdetail")); return; }
    if ((el = closest(target, "data-gotab"))) { closeSheet(); S.tab = el.getAttribute("data-gotab"); renderTabs(); renderContent(); document.getElementById("content").scrollTop = 0; return; }
    if ((el = closest(target, "data-tab"))) { S.arrange = null; S.tab = el.getAttribute("data-tab"); renderTabs(); renderContent(); document.getElementById("content").scrollTop = 0; return; }
    if ((el = closest(target, "data-go"))) { S.tab = el.getAttribute("data-go"); renderTabs(); renderContent(); return; }
    if ((el = closest(target, "data-day"))) { S.historyDay = el.getAttribute("data-day"); renderContent(); return; }
    if ((el = closest(target, "data-scene"))) { if (S.tablet.readonly) { showBanner(t("readonly"), 3000); return; } if (!armed(el, "scene:" + el.getAttribute("data-scene"), t("confirmTap"))) { return; } send({ type: "action", action: "scene", id: el.getAttribute("data-scene") }); el.classList.add("on"); setTimeout(function () { el.classList.remove("on"); }, 800); return; }
    if ((el = closest(target, "data-alloffagain"))) { send({ type: "action", action: "all_off", room: null, ids: el.getAttribute("data-alloffagain").split("\n") }); hideToast(); return; }
    if ((el = closest(target, "data-alloff"))) { if (S.tablet.readonly) { showBanner(t("readonly"), 3000); return; } var ids = el.getAttribute("data-ids"); send({ type: "action", action: "all_off", room: el.getAttribute("data-alloff") || null, ids: ids ? ids.split("\n") : null }); return; }
    if ((el = closest(target, "data-off"))) { act(el.getAttribute("data-off"), "off", null, { on: false }); return; }
    if ((el = closest(target, "data-close"))) { closeSheet(); return; }
    if (target.id === "sheet") { closeSheet(); return; }
    if ((el = closest(target, "data-reload"))) { location.reload(); return; }
    if ((el = closest(target, "data-retry"))) { retry(el.getAttribute("data-retry")); return; }
    if ((el = closest(target, "data-do"))) {
      var sid = S.sheet.id, what = el.getAttribute("data-do");
      if (what === "unlock" && !armed(el, "unlock:" + sid, t("unlockSure"))) { return; }
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
    if ((el = closest(target, "data-setpage")) && S.sheet && S.sheet.settings) { S.sheet.page = el.getAttribute("data-setpage"); renderSettings(); return; }
    if ((el = closest(target, "data-batteries"))) { openBatteries(); return; }
    if ((el = closest(target, "data-weather"))) { S.sheet = { weather: true }; renderSheet(); return; }
    if ((el = closest(target, "data-routine"))) { S.sheet = { routine: el.getAttribute("data-routine") }; renderSheet(); return; }
    if ((el = closest(target, "data-rtgo"))) { routineGo(el.getAttribute("data-rtgo")); return; }
    if ((el = closest(target, "data-undo"))) { send({ type: "action", action: "undo" }); S.undoUntil = 0; hideToast(); if (S.tab === "home") { renderContent(); } return; }
    if ((el = closest(target, "data-overview"))) { S.sheet = { overview: el.getAttribute("data-overview") }; renderSheet(); return; }
    if ((el = closest(target, "data-ovpos"))) { var pv = el.getAttribute("data-ovpos").split("|"); act(pv[0], "position", Number(pv[1]), { position: Number(pv[1]) }); return; }
    if ((el = closest(target, "data-ovall"))) { overviewAll(el.getAttribute("data-ovall")); return; }
    if ((el = closest(target, "data-ovlock"))) { act(el.getAttribute("data-ovlock"), "lock", null, { locked: true }); return; }
    if ((el = closest(target, "data-ovopen"))) { openSheet(el.getAttribute("data-ovopen")); return; }
    if ((el = closest(target, "data-people"))) { S.sheet = { people: true }; renderSheet(); return; }
    if ((el = closest(target, "data-batt"))) { openSheet(el.getAttribute("data-batt")); return; }
    if ((el = closest(target, "data-place"))) { send({ type: "setup", place: el.getAttribute("data-place") }); S.tablet.place = el.getAttribute("data-place"); renderSettings(); return; }
    if ((el = closest(target, "data-theme"))) { var l1 = copyLayout(); l1.theme = el.getAttribute("data-theme"); saveLayout(l1); return; }
    if ((el = closest(target, "data-roomtoggle"))) {
      var l2 = copyLayout(), hr = l2.hidden_rooms || [], name = el.getAttribute("data-roomtoggle");
      l2.hidden_rooms = hr.indexOf(name) >= 0 ? hr.filter(function (x) { return x !== name; }) : hr.concat([name]); saveLayout(l2); return;
    }
    if ((el = closest(target, "data-resetlayout"))) { var l4 = { theme: layout().theme }; S.usage = {}; store("dashUsage", "{}"); saveLayout(l4); return; }
    if ((el = closest(target, "data-pair"))) { pair(document.getElementById("code").value); return; }
    if ((el = closest(target, "data-setupplace"))) { S.setupPlace = el.getAttribute("data-setupplace"); S.setupRoom = document.getElementById("setuproom").value; renderSetup(); return; }
    if ((el = closest(target, "data-setupdone"))) {
      S.setupRoom = document.getElementById("setuproom").value;
      if (!S.rooms.length) { finishSetup(); return; }
      if (!S.setupHidden) { S.setupHidden = (layout().hidden_rooms || []).slice(); }
      S.setupStep = "rooms"; renderSetup(); return;
    }
    if ((el = closest(target, "data-setupback"))) { S.setupStep = null; renderSetup(); return; }
    if ((el = closest(target, "data-pickroom"))) {
      var pr = el.getAttribute("data-pickroom"), sh = S.setupHidden || [];
      S.setupHidden = sh.indexOf(pr) >= 0 ? sh.filter(function (x) { return x !== pr; }) : sh.concat([pr]);
      if (navigator.vibrate) { try { navigator.vibrate(8); } catch (e) { /* not supported */ } }
      renderSetup(); return;
    }
    if ((el = closest(target, "data-pickall"))) { S.setupHidden = el.getAttribute("data-pickall") === "1" ? [] : S.rooms.map(function (r) { return r.name; }); renderSetup(); return; }
    if ((el = closest(target, "data-setupfinish"))) { finishSetup(); return; }
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
    if (ev.target.getAttribute && S.sheet) {
      var ins = ev.target.getAttribute("data-inslider"), itm = ev.target.getAttribute("data-intime");
      if (ins) { S.sliding = false; setInput(ins, ev.target.value); }
      if (itm && ev.target.value) { S.sliding = false; setInput(itm, ev.target.value); }
    }
    if (ev.target.id === "mvol" && S.sheet) { S.sliding = false; var vv = Number(ev.target.value); act(S.sheet.id, "volume", vv, { volume: vv }); }
  });
  document.addEventListener("input", function (ev) {
    if (ev.target.getAttribute && ev.target.getAttribute("data-inslider")) {
      S.sliding = true; var row = ev.target.parentNode, lab = row && row.querySelector(".inval"); if (lab) { lab.textContent = ev.target.value; }
    }
    if (ev.target.getAttribute && ev.target.getAttribute("data-intext")) { S.sliding = true; }
    if (ev.target.id === "mvol") { S.sliding = true; var vt = document.getElementById("mvoltxt"); if (vt) { vt.textContent = ev.target.value; } }
  });
  document.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && ev.target.id === "code") { pair(ev.target.value); } });

  // ---------- start ----------
  function tick() {
    S.now = new Date();
    renderHeader(); idleCheck(); loadSparks(); tickTimers();
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
