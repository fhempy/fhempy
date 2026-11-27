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
    chLight: "Licht", chClimate: "Klima", chBlinds: "Rollläden", chSecurity: "Sicherheit", chNOn: "{n} an", chAllOff: "alles aus", chNHeat: "{n} heizen", chOneHeat: "1 heizt", chNOpen: "{n} von {m} offen", chAllClosed: "alle zu", chSecOpen: "{n} offen", chSecOk: "alles zu", ovLight: "Was leuchtet", ovClimate: "Raumklima", ovBlinds: "Rollläden", ovSecurity: "Fenster, Türen und Schlösser", ovNoLight: "Alle Lichter sind aus.", ovSecOk: "Alles zu und verriegelt.", allUp: "Alle auf", allDown: "Alle zu", lightsOff: "Alle Lichter aus", heatsNow: "heizt", ovHeatNow: "Heizt gerade · {n}", ovOtherRooms: "Weitere Räume",
    pairTitle: "Tablet verbinden", pairText: "Öffne in FHEM das Gerät des Dashboards und scanne den QR-Code mit der Kamera dieses Tablets. Oder gib den Code ein, der dort steht.",
    pairButton: "Verbinden", pairWrong: "Der Code stimmt nicht oder ist abgelaufen. Lade die Seite in FHEM neu für einen neuen Code.",
    whereTitle: "Wo steht dieses Tablet?", whereText: "Wir haben {rooms} Räume und {tiles} Geräte gefunden. Wähle den Platz, den Rest machen wir.",
    chMaint: "Wartung", chMaintN: "{n} Geräte", ovMaint: "Wartung", ovMaintLead: "Diese Geräte brauchen Aufmerksamkeit.", mtUnreachable: "nicht erreichbar", mtSilent: "keine Werte {t}", mtOk: "Alles in Ordnung.", mtBattery: "Batterie schwach",
    offDone: "{n} Geräte aus.", offLeft: "Noch an: {names}", offAgain: "Nochmal",
    pinTitle: "PIN eingeben", pinLead: "Die Einstellungen sind mit einer PIN geschützt.", pinWrong: "Falsche PIN.", pinWait: "Zu viele Versuche. Bitte in 5 Minuten nochmal.", pinOpen: "Entsperrt für 10 Minuten.", pinLocked: "Gesperrt, bitte PIN eingeben.", pinOk: "OK",
    calTitle: "Heute", calTomorrow: "Morgen", calAllDay: "ganztags", calNow: "jetzt", binTitle: "Müll", binToday: "Heute: {what}", binTomorrow: "Morgen: {what}",
    ntTitle: "Meldung auf Zuhause", ntHint: "Zeigt den Text auf Zuhause, solange das Gerät an, offen oder ausgelöst ist. Mit dem Haken wird es zurückgesetzt.", ntText: "Text, z. B. Post ist da", ntSave: "Speichern", ntDone: "Erledigt", ntSaved: "Gespeichert",
    someone: "Jemand da", quietFor: "ruhig {t}",
    moTitle: "Darf offen sein", moHint: "In dieser Zeit warnt das Dashboard nicht, wenn offen ist, z. B. ein Hoftor tagsüber. Gilt für alle Tablets.", moFrom: "von", moTo: "bis", moUntil: "darf offen sein bis {t}", moAllowed: "Darf gerade offen sein",
    half: "50 %", pullWindow: "Ziehen zum Bewegen",
    valveOpen: "Ventil {n} %", valveShut: "Ventil zu", idleNow: "heizt gerade nicht",
    apWasher: "Waschmaschine", apDryer: "Trockner", apDishwasher: "Spülmaschine", apRuns: "läuft seit {t}", apLeft: "noch ca. {t}", apAlmost: "gleich fertig", apIdle: "seit {t} ohne Strom, Pause oder fertig", apEnd: "fertig um {t}", apNew: "neues Programm, wird gelernt", apDoneWasher: "Wäsche fertig", apDoneDryer: "Trockner fertig", apDoneDishwasher: "Geschirr fertig", apAgo: "seit {t}",
    apAsk: "Was hängt an „{name}“?", apAskLead: "Hier lief gerade ein langes Programm. Bei Waschmaschine, Trockner und Spülmaschine sagt das Tablet, wann es fertig ist.", apNone: "Nichts davon", apSeen: "Erledigt",
    apBigWasher: "Die Wäsche ist fertig", apBigDryer: "Der Trockner ist fertig", apBigDishwasher: "Das Geschirr ist fertig", apBigMany: "{n} Geräte sind fertig",
    apTipWasher: "Bitte bald ausräumen, dann riecht nichts muffig.", apTipDryer: "Am besten gleich ausräumen, dann knittert nichts.", apTipDishwasher: "Das Geschirr kann ausgeräumt werden.",
    apSayWasher: "Die Waschmaschine ist fertig.", apSayDryer: "Der Trockner ist fertig.", apSayDishwasher: "Die Spülmaschine ist fertig.",
    apByTip: "Die Meldung verschwindet auch von selbst, sobald {name} etwas meldet.", apClose: "Schließen", apDoneNow: "gerade eben",
    apSettings: "Waschmaschine & Co.", apSettingsValue: "{n} Geräte", apSettingsNone: "noch keine erkannt", apSettingsLead: "Ist ein Gerät fertig, zeigen die Tablets das 10 Minuten lang groß an, bis jemand auf Erledigt tippt. Ein Gerät kann die Meldung auch von selbst erledigen, z. B. der Türkontakt der Waschmaschine oder ein Bewegungsmelder im Raum. Gilt für alle Tablets.",
    apNoKnown: "Noch keine Waschmaschine, kein Trockner und keine Spülmaschine bekannt. Läuft an einer Steckdose mit Strommessung ein langes Programm, fragt das Tablet, was dort hängt.",
    apBy: "Erledigt durch", apByNone: "Nur mit dem Erledigt-Knopf", apBySuggest: "Vorschläge", apBySensors: "Kontakte und Bewegungsmelder", apByOther: "Weitere Geräte",
    speak: "Ansage", speakLead: "Sagt laut, wenn Waschmaschine & Co. fertig sind", speakTest: "Probe", speakNone: "Dieser Browser kann nicht sprechen",
    smoke: "Rauchmelder", water: "Wassermelder", calm: "ruhig", smokeNow: "Rauch!", waterNow: "Wasser!", alSmoke: "Rauchalarm", alWater: "Wasseralarm", alIntrusion: "Einbruchalarm", alAlarm: "Alarm", alMute: "Ton aus", alSound: "Ton an", alHide: "Ausblenden", alShow: "Anzeigen", alSystemOff: "Alarmanlage aus",
    alSmokeTip: "Alle raus, Türen schließen, 112 anrufen.", alWaterTip: "Wasser abdrehen, Strom in der Nähe abschalten.", alIntrusionTip: "Bleib ruhig und ruf im Zweifel 110 an.", alAllCalm: "{n} Melder, alle ruhig", alDetectors: "Rauch- und Wassermelder",
    asOff: "Unscharf", asHome: "Scharf (zuhause)", asAway: "Scharf (abwesend)", asTriggered: "Alarm!", asGoOff: "Aus", asGoHome: "Zuhause", asGoAway: "Abwesend", asSure: "Wirklich aus?", asPinTitle: "Alarmanlage aus", asPinLead: "PIN der Alarmanlage", asDone: "Alarmanlage: {mode}",
    colorTitle: "Farbe", whiteTitle: "Weiß", warm: "warm", cold: "kalt",
    wxTitle: "Wetter", wxHours: "Nächste 24 Stunden", wxDays: "Nächste Tage", wxSunrise: "Sonnenaufgang", wxSunset: "Sonnenuntergang", wxToday: "Heute", wxNone: "Keine Vorhersage, das Wetter-Gerät liefert keine Stunden oder Tage.",
    rtNight: "Gute Nacht", rtAway: "Haus verlassen", rtNightLead: "Das ist noch offen oder an. Mit „Gute Nacht“ gehen Licht und Musik aus und die Rollläden gehen zu.", rtAwayLead: "Das ist noch offen oder an. Beim Gehen geht alles aus, was nicht anbleiben soll.",
    rtAllFine: "Alles zu und aus.", rtBlinds: "{n} Rollläden offen", rtBlind: "1 Rollladen offen", rtBlindsSub: "gehen zu", rtGoNight: "Gute Nacht", rtGoAway: "Los geht’s", rtOff: "geht aus", rtSecOff: "Geht aus · {n}", rtSecClose: "Geht zu", rtSecStays: "Bleibt an · {n}", rtSecOpen: "Noch offen · {n}", rtOffTag: "Aus", rtGoIn: "Los geht’s · {n} s", rtGoNightIn: "Gute Nacht · {n} s", rtAutoStop: "Nicht automatisch", rtAutoHint: "Geht in {n} Sekunden von selbst los.", rtSecAlarm: "Alarmanlage", rtSecLock: "Wird verriegelt · {n}", rtSecVacuum: "Während du weg bist", rtSecHeat: "Es wird heiß · bis {t}°", rtHeatOffer: "gegen die Hitze schließen?", rtHeatClose: "Schließen", rtVacStart: "Saugen starten", rtVacStarted: "Saugt", rtLocks: "alle Türen sind zu", rtLockTag: "Zu", rtLockDoor: "Tür offen, bleibt offen", rtAlarmTag: "Scharf", rtAlarmTap: "antippen: unscharf lassen", rtAlarmStays: "Bleibt unscharf · antippen zum Scharfschalten",
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
    language: "Sprache",
    vwStart: "Starten", vwPause: "Pause", vwStop: "Stopp", vwDock: "Zur Station", vwLocate: "Suchen", vwBattery: "Akku", vwArea: "Fläche", vwDuration: "Dauer", vwFan: "Saugstärke", vwError: "Fehler", vwCleaning: "Saugt",
    vwSoc: "Akku", vwFuel: "Tank", vwRange: "Reichweite", vwCharging: "Lädt", vwNotCharging: "Lädt nicht", vwPlugged: "Eingesteckt", vwUnplugged: "Nicht eingesteckt", vwMileage: "Kilometerstand", vwLocked: "Verriegelt", vwUnlocked: "Offen",
    vwChargeStart: "Laden starten", vwChargeStop: "Laden stoppen", vwClimateStart: "Klima an", vwClimateStop: "Klima aus", vwUpdate: "Aktualisieren", vwLock: "Verriegeln", vwUnlock: "Entriegeln", vwUnlockSure: "Nochmal tippen zum Entriegeln", vwRemaining: "Noch",
    vwPower: "Ladeleistung", vwEnergy: "Geladen", vwMode: "Modus", vwFlow: "Vorlauf", vwReturn: "Rücklauf", vwOutside: "Außen", vwDhw: "Warmwasser", vwCompressor: "Verdichter", vwCop: "COP", vwHpPower: "Leistung", vwDhwBoost: "Warmwasser einmalig", vwCompOn: "läuft", vwCompOff: "aus",
    vwMoisture: "Bodenfeuchte", vwNext: "Nächster Start", vwWatering: "Bewässert", vwDry: "Trocken",
    vwViewAs: "Anzeigen als", vwViewLead: "Eigene Ansicht für Geräte, die mehr als ein Schalter sind. Erkannt an Befehlen und Readings, hier änderbar.", vwNormal: "Normal", vwvacuum: "Saugroboter", vwcar: "Auto", vwwallbox: "Wallbox", vwheatpump: "Wärmepumpe", vwirrigation: "Bewässerung", vwDetected: "erkannt",
    enTitle: "Energie", enDay: "Heute", enWeek: "7 Tage", enMonth: "30 Tage", enSolar: "Solar", enLoad: "Verbrauch", enImport: "Netzbezug", enExport: "Eingespeist", enAutarky: "Selbst versorgt", enCost: "Kosten", enRevenue: "Vergütung",
    enTop: "Größte Verbraucher", enTopLead: "Geräte, die ihre Leistung melden", enChart: "Verlauf", enNoTimeline: "Für Tage und Wochen braucht es das timeline-Modul in FHEM, es merkt sich die Leistung.", enEmpty: "Noch keine Werte für diesen Zeitraum.",
    enPrice: "Strompreis", enPriceLead: "Für die Kosten, in €/kWh. Ein Preis-Reading (z. B. tibber) hat Vorrang.", enFeedIn: "Einspeisung €/kWh (optional)", enPriceReading: "Preis vom Stromanbieter", enPriceSave: "Speichern", enPriceEdit: "Ändern", enPriceNone: "Kein Preis eingetragen", enFeedInShort: "Einspeisung",
    measure: "Nur messen", measureHint: "Für Kühlschrank oder Gefrierschrank: zeigt den Verbrauch, schaltet nie, auch nicht bei „Alles aus“. Gilt für alle Tablets.", measuring: "misst",
    baby: "Babyfon", babyEnd: "Babyfon beenden", babyRoom: "Raum",
    cameras: "Kameras", camStart: "Startseite", camStartAuto: "Automatisch", camStartCams: "Kameras", camNext: "Nächste Kamera", camPrev: "Vorherige Kamera",
    floors: "Etagen", floorsLead: "Fasst die Räume auf Zuhause nach Etagen zusammen, mit „Licht aus“ und „Rollläden zu“ pro Etage. Gilt für alle Tablets.", floorsValue: "{n} Etagen", floorsNone: "keine", floorAdd: "Etage hinzufügen", floorName: "Name, z. B. EG", floorNone: "–", floorSave: "Speichern", floorSuggest: "Vorschlag aus den Raumnamen: {list}", floorTake: "Übernehmen", floorLights: "Licht aus", floorBlinds: "Rollläden zu", floorOther: "Weitere Räume",
    tileSize: "Größe", headAdd: "Überschrift", headPlaceholder: "z. B. Decke, Fenster …", roomReset: "Raum zurücksetzen", editHint2: "1×1 neben dem × wechselt zwischen klein, breit, hoch und groß.",
    accent: "Akzentfarbe", accentLamps: "wie die Lampen", accentHint: "Bunt: der Hintergrund leuchtet in der Farbe der eingeschalteten Lampen",
    tourTitle: "So bedienst du das Dashboard", tourText: "Vier Handgriffe, mehr braucht es nicht.", tourGo: "Los geht’s", tourAgain: "So bedienst du das Dashboard",
    tourTap: "Tippen", tourTapList: ["Das runde Symbol schaltet an und aus", "Die Kachel zeigt Details und Verlauf", "Oben Wetter, Personen und Offen antippen"],
    tourDrag: "Ziehen", tourDragList: ["In den Details Helligkeit, Rollladen und Temperatur ziehen", "Im Raum-Popup ein Schieber für alle Rollläden"],
    tourHold: "Halten", tourHoldList: ["Lampe oder Steckdose halten: Ausschalt-Timer", "Beim Bearbeiten Kacheln halten und verschieben"],
    tourGear: "Einstellungen", tourGearList: ["Zahnrad oben rechts", "Design, Räume, Bildschirmschoner", "Kacheln bearbeiten und Räume ordnen"],
    worthLook: "Einen Blick wert", wlNoRoom: "{n} Geräte ohne Raum", wlNoRoom1: "1 Gerät ohne Raum", wlNoRoomSub: "Werden erst angezeigt, wenn sie einen Raum haben", wlIdle: "{n} Geräte lange nicht benutzt", wlIdle1: "1 Gerät lange nicht benutzt", wlIdleSub: "Seit über einem Monat keine Meldung", wlMaint: "{n} Geräte brauchen Aufmerksamkeit", wlMaintSub: "Batterie, nicht erreichbar oder still",
    setLead: "Oben gilt nur für dieses Tablet, unten für alle Tablets im Zuhause.", tabLead: "Gilt nur für dieses Tablet. Der Standort legt fest, womit es startet und ob es einen Bildschirmschoner hat.", showAll: "Alle zeigen ({n})",
    bugInfo: "Info für Fehlerbericht", bugLead: "Versionen und Browser, ohne Namen und Adressen. Zum Einfügen ins Forum oder in ein GitHub-Issue.", bugCopy: "Kopieren", bugCopied: "Kopiert",
    look: "Darstellung", lookAuto: "Automatisch", lookLite: "Einfach", lookFull: "Voll", lookHint: "Einfach: ohne Unschärfe, für ältere Tablets",
    saver: "Bildschirmschoner", saverOff: "Aus", saverMin: "{n} min",
    name: "Name", place: "Standort", room: "Raum", theme: "Design", auto: "Automatisch", dark: "Dunkel", light: "Hell",
    rooms: "Räume", editTiles: "Kacheln bearbeiten", editDone: "Bearbeiten beenden", reset: "Zurücksetzen",
    rpLight: "Licht", rpSwitches: "Schalter", rpBlinds: "Rollläden", rpMore: "Mehr in diesem Raum", rpOpenRoom: "Ganzen Raum öffnen", rpNofM: "{n} von {m} an", rpAllOffShort: "Alle aus", rpHeatsNow: "Heizt gerade", rpHoldRing: "Ring ziehen zum Einstellen", rpReached: "Soll erreicht", rpSetTo: "Soll {t}°",
    switchHttps: "Zu https wechseln (für Sprechen)", energy: "Energie", solar: "Solar", usage: "Verbrauch", voltage: "Spannung", current: "Strom", energyToday: "Heute", energyTotal: "Gesamt",
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
    chLight: "Light", chClimate: "Climate", chBlinds: "Blinds", chSecurity: "Security", chNOn: "{n} on", chAllOff: "all off", chNHeat: "{n} heating", chOneHeat: "1 heating", chNOpen: "{n} of {m} open", chAllClosed: "all closed", chSecOpen: "{n} open", chSecOk: "all closed", ovLight: "What is on", ovClimate: "Room climate", ovBlinds: "Blinds", ovSecurity: "Windows, doors and locks", ovNoLight: "All lights are off.", ovSecOk: "Everything closed and locked.", allUp: "All up", allDown: "All down", lightsOff: "All lights off", heatsNow: "heating", ovHeatNow: "Heating now · {n}", ovOtherRooms: "Other rooms",
    pairTitle: "Connect tablet", pairText: "Open the dashboard device in FHEM and scan the QR code with the camera of this tablet, or enter the code shown there.",
    pairButton: "Connect", pairWrong: "Wrong or expired code. Reload the page in FHEM for a new code.",
    whereTitle: "Where is this tablet?", whereText: "We found {rooms} rooms and {tiles} devices. Choose the place, we do the rest.",
    chMaint: "Maintenance", chMaintN: "{n} devices", ovMaint: "Maintenance", ovMaintLead: "These devices need attention.", mtUnreachable: "not reachable", mtSilent: "no values {t}", mtOk: "Everything is fine.", mtBattery: "battery low",
    offDone: "{n} devices off.", offLeft: "Still on: {names}", offAgain: "Try again",
    pinTitle: "Enter PIN", pinLead: "The settings are protected by a PIN.", pinWrong: "Wrong PIN.", pinWait: "Too many tries. Please try again in 5 minutes.", pinOpen: "Unlocked for 10 minutes.", pinLocked: "Locked, please enter the PIN.", pinOk: "OK",
    calTitle: "Today", calTomorrow: "Tomorrow", calAllDay: "all day", calNow: "now", binTitle: "Bins", binToday: "Today: {what}", binTomorrow: "Tomorrow: {what}",
    ntTitle: "Notice on Home", ntHint: "Shows the text on Home while the device is on, open or triggered. The tick resets it.", ntText: "Text, e.g. Mail is here", ntSave: "Save", ntDone: "Done", ntSaved: "Saved",
    someone: "Someone here", quietFor: "quiet {t}",
    moTitle: "May be open", moHint: "During this time the dashboard does not warn when it is open, e.g. a yard gate by day. Applies to all tablets.", moFrom: "from", moTo: "to", moUntil: "may be open until {t}", moAllowed: "May be open now",
    half: "50 %", pullWindow: "Drag to move",
    valveOpen: "valve {n} %", valveShut: "valve closed", idleNow: "not heating right now",
    apWasher: "Washing machine", apDryer: "Dryer", apDishwasher: "Dishwasher", apRuns: "running for {t}", apLeft: "about {t} left", apAlmost: "almost done", apIdle: "no power for {t}, paused or done", apEnd: "done at {t}", apNew: "new program, learning it", apDoneWasher: "Laundry done", apDoneDryer: "Dryer done", apDoneDishwasher: "Dishes done", apAgo: "for {t}",
    apAsk: "What is plugged into “{name}”?", apAskLead: "A long program just ran here. For a washing machine, dryer or dishwasher the tablet tells you when it is done.", apNone: "None of these", apSeen: "Done",
    apBigWasher: "The laundry is done", apBigDryer: "The dryer is done", apBigDishwasher: "The dishes are done", apBigMany: "{n} appliances are done",
    apTipWasher: "Please take it out soon, so nothing smells musty.", apTipDryer: "Take it out right away and nothing creases.", apTipDishwasher: "The dishes can be put away.",
    apSayWasher: "The washing machine is done.", apSayDryer: "The dryer is done.", apSayDishwasher: "The dishwasher is done.",
    apByTip: "The message also goes away by itself as soon as {name} reports something.", apClose: "Close", apDoneNow: "just now",
    apSettings: "Washing machine & co.", apSettingsValue: "{n} appliances", apSettingsNone: "none found yet", apSettingsLead: "When an appliance is done, the tablets show it large for 10 minutes until somebody taps Done. A device can also set it to done by itself, e.g. the door contact of the washing machine or a motion sensor in the room. For all tablets.",
    apNoKnown: "No washing machine, dryer or dishwasher known yet. When a long program runs on a plug which measures power, the tablet asks what is plugged in.",
    apBy: "Done by", apByNone: "Only with the Done button", apBySuggest: "Suggestions", apBySensors: "Contacts and motion sensors", apByOther: "More devices",
    speak: "Announcement", speakLead: "Says out loud when the washing machine & co. are done", speakTest: "Test", speakNone: "This browser cannot speak",
    smoke: "Smoke detector", water: "Water detector", calm: "calm", smokeNow: "Smoke!", waterNow: "Water!", alSmoke: "Smoke alarm", alWater: "Water alarm", alIntrusion: "Intrusion alarm", alAlarm: "Alarm", alMute: "Sound off", alSound: "Sound on", alHide: "Hide", alShow: "Show", alSystemOff: "Alarm system off",
    alSmokeTip: "Get everybody out, close the doors, call the fire brigade.", alWaterTip: "Turn off the water, switch off power nearby.", alIntrusionTip: "Stay calm and call the police if in doubt.", alAllCalm: "{n} detectors, all calm", alDetectors: "Smoke and water detectors",
    asOff: "Disarmed", asHome: "Armed (home)", asAway: "Armed (away)", asTriggered: "Alarm!", asGoOff: "Off", asGoHome: "Home", asGoAway: "Away", asSure: "Really off?", asPinTitle: "Alarm system off", asPinLead: "PIN of the alarm system", asDone: "Alarm system: {mode}",
    colorTitle: "Colour", whiteTitle: "White", warm: "warm", cold: "cold",
    wxTitle: "Weather", wxHours: "Next 24 hours", wxDays: "Next days", wxSunrise: "Sunrise", wxSunset: "Sunset", wxToday: "Today", wxNone: "No forecast, the weather device gives no hours or days.",
    rtNight: "Good night", rtAway: "Leave home", rtNightLead: "Still open or on. “Good night” switches the lights and music off and closes the blinds.", rtAwayLead: "Still open or on. Leaving switches off everything that should not stay on.",
    rtAllFine: "Everything closed and off.", rtBlinds: "{n} blinds open", rtBlind: "1 blind open", rtBlindsSub: "will close", rtGoNight: "Good night", rtGoAway: "Let’s go", rtOff: "goes off", rtSecOff: "Goes off · {n}", rtSecClose: "Will close", rtSecStays: "Stays on · {n}", rtSecOpen: "Still open · {n}", rtOffTag: "Off", rtGoIn: "Let’s go · {n} s", rtGoNightIn: "Good night · {n} s", rtAutoStop: "Not automatically", rtAutoHint: "Starts by itself in {n} seconds.", rtSecAlarm: "Alarm system", rtSecLock: "Will lock · {n}", rtSecVacuum: "While you are away", rtSecHeat: "It gets hot · up to {t}°", rtHeatOffer: "close them against the heat?", rtHeatClose: "Close", rtVacStart: "Start cleaning", rtVacStarted: "Cleaning", rtLocks: "all doors are closed", rtLockTag: "Lock", rtLockDoor: "a door is open, stays unlocked", rtAlarmTag: "Armed", rtAlarmTap: "tap to leave it disarmed", rtAlarmStays: "Stays disarmed · tap to arm",
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
    language: "Language",
    vwStart: "Start", vwPause: "Pause", vwStop: "Stop", vwDock: "Back to dock", vwLocate: "Locate", vwBattery: "Battery", vwArea: "Area", vwDuration: "Duration", vwFan: "Suction", vwError: "Error", vwCleaning: "Cleaning",
    vwSoc: "Battery", vwFuel: "Fuel", vwRange: "Range", vwCharging: "Charging", vwNotCharging: "Not charging", vwPlugged: "Plugged in", vwUnplugged: "Not plugged in", vwMileage: "Mileage", vwLocked: "Locked", vwUnlocked: "Unlocked",
    vwChargeStart: "Start charging", vwChargeStop: "Stop charging", vwClimateStart: "Climate on", vwClimateStop: "Climate off", vwUpdate: "Update", vwLock: "Lock", vwUnlock: "Unlock", vwUnlockSure: "Tap again to unlock", vwRemaining: "Left",
    vwPower: "Charging power", vwEnergy: "Charged", vwMode: "Mode", vwFlow: "Flow", vwReturn: "Return", vwOutside: "Outside", vwDhw: "Hot water", vwCompressor: "Compressor", vwCop: "COP", vwHpPower: "Power", vwDhwBoost: "Hot water once", vwCompOn: "running", vwCompOff: "off",
    vwMoisture: "Soil moisture", vwNext: "Next start", vwWatering: "Watering", vwDry: "Dry",
    vwViewAs: "Show as", vwViewLead: "Own view for devices which are more than a switch. Found by their commands and readings, changed here.", vwNormal: "Normal", vwvacuum: "Robot vacuum", vwcar: "Car", vwwallbox: "Wallbox", vwheatpump: "Heat pump", vwirrigation: "Irrigation", vwDetected: "detected",
    enTitle: "Energy", enDay: "Today", enWeek: "7 days", enMonth: "30 days", enSolar: "Solar", enLoad: "Usage", enImport: "From grid", enExport: "Fed in", enAutarky: "Self-supplied", enCost: "Cost", enRevenue: "Feed-in pay",
    enTop: "Biggest consumers", enTopLead: "Devices which report their power", enChart: "History", enNoTimeline: "Days and weeks need the timeline module in FHEM, it remembers the power.", enEmpty: "No values for this period yet.",
    enPrice: "Electricity price", enPriceLead: "For the cost, in €/kWh. A price reading (e.g. tibber) wins.", enFeedIn: "Feed-in €/kWh (optional)", enPriceReading: "Price of the supplier", enPriceSave: "Save", enPriceEdit: "Change", enPriceNone: "No price set", enFeedInShort: "Feed-in",
    measure: "Only measure", measureHint: "For a fridge or freezer: shows the power, never switches, also not with “All off”. Applies to all tablets.", measuring: "measures",
    baby: "Baby monitor", babyEnd: "End baby monitor", babyRoom: "Room",
    cameras: "Cameras", camStart: "Start page", camStartAuto: "Automatic", camStartCams: "Cameras", camNext: "Next camera", camPrev: "Previous camera",
    floors: "Floors", floorsLead: "Groups the rooms on Home by floor, with “Lights off” and “Blinds down” per floor. Applies to all tablets.", floorsValue: "{n} floors", floorsNone: "none", floorAdd: "Add floor", floorName: "Name, e.g. Ground floor", floorNone: "–", floorSave: "Save", floorSuggest: "Suggestion from the room names: {list}", floorTake: "Apply", floorLights: "Lights off", floorBlinds: "Blinds down", floorOther: "Other rooms",
    tileSize: "Size", headAdd: "Heading", headPlaceholder: "e.g. Ceiling, Windows …", roomReset: "Reset room", editHint2: "1×1 next to the × switches between small, wide, tall and big.",
    accent: "Accent colour", accentLamps: "like the lamps", accentHint: "Colourful: the background glows in the colour of the lamps which are on",
    tourTitle: "How to use the dashboard", tourText: "Four moves, that is all it takes.", tourGo: "Let’s go", tourAgain: "How to use the dashboard",
    tourTap: "Tap", tourTapList: ["The round icon switches on and off", "The tile shows details and history", "Tap weather, people and open at the top"],
    tourDrag: "Drag", tourDragList: ["Drag brightness, blinds and temperature in the details", "One slider for all blinds in the room popup"],
    tourHold: "Hold", tourHoldList: ["Hold a lamp or plug: switch-off timer", "While editing hold tiles to move them"],
    tourGear: "Settings", tourGearList: ["Gear at the top right", "Design, rooms, screensaver", "Edit tiles and arrange rooms"],
    worthLook: "Worth a look", wlNoRoom: "{n} devices without a room", wlNoRoom1: "1 device without a room", wlNoRoomSub: "They are shown once they have a room", wlIdle: "{n} devices not used for long", wlIdle1: "1 device not used for long", wlIdleSub: "No value for more than a month", wlMaint: "{n} devices need attention", wlMaintSub: "Battery, not reachable or silent",
    setLead: "The top applies to this tablet only, the bottom to all tablets at home.", tabLead: "Applies to this tablet only. The place sets what it starts with and whether it has a screensaver.", showAll: "Show all ({n})",
    bugInfo: "Info for a bug report", bugLead: "Versions and browser, without names and addresses. To paste into the forum or a GitHub issue.", bugCopy: "Copy", bugCopied: "Copied",
    look: "Display", lookAuto: "Automatic", lookLite: "Simple", lookFull: "Full", lookHint: "Simple: without blur, for older tablets",
    saver: "Screensaver", saverOff: "Off", saverMin: "{n} min",
    name: "Name", place: "Place", room: "Room", theme: "Design", auto: "Automatic", dark: "Dark", light: "Light",
    rooms: "Rooms", editTiles: "Edit tiles", editDone: "Done editing", reset: "Reset",
    rpLight: "Light", rpSwitches: "Switches", rpBlinds: "Blinds", rpMore: "More in this room", rpOpenRoom: "Open the whole room", rpNofM: "{n} of {m} on", rpAllOffShort: "All off", rpHeatsNow: "Heating now", rpHoldRing: "Drag the ring to set", rpReached: "Target reached", rpSetTo: "Set to {t}°",
    switchHttps: "Switch to https (for talking)", energy: "Energy", solar: "Solar", usage: "Usage", voltage: "Voltage", current: "Current", energyToday: "Today", energyTotal: "Total",
    grid: "Grid", storage: "Battery", price: "Price", surplus: "Surplus", fromGrid: "From grid",
    hiddenTiles: "Hidden, + brings them back", days: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    timerOff: "Switch off in", timerOn: "Switch on for", timerLeft: "{t} left", timerUntil: "goes off at {t}", timerStop: "End timer", min15: "15 min", min30: "30 min", h1: "1 h", h2: "2 h",
    away: "Away", quiet: "Nothing happened on this day.", lastDays: "days", climate: "Climate",
    now: "now", wasOn: "When it was on"
  };
  // more languages: lang.js of the server (lang/*.json, chosen in the settings
  // or by the browser), keys missing there are English
  var LANG = window.DASH_LANG || null;
  var T = LANG && LANG.code === "de" ? DE : LANG && LANG.code === "en" ? EN : /^de/i.test(navigator.language || "de") ? DE : EN;
  if (LANG && LANG.texts) {
    T = {}; Object.keys(EN).forEach(function (k) { T[k] = EN[k]; });
    Object.keys(LANG.texts).forEach(function (k) { T[k] = LANG.texts[k]; });
  }
  var GERMAN = T === DE;
  // decimal comma: German and most other languages of the dashboard
  var COMMA = GERMAN || !!(LANG && LANG.comma);
  var LANG_CODE = GERMAN ? "de" : T === EN ? "en" : LANG.code;
  try { document.documentElement.lang = LANG_CODE; } catch (e) { /* old browsers */ }
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
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
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
    person: '<circle cx="12" cy="7" r="3.2"/><path d="M5 21c0-4 3-7 7-7s7 3 7 7"/>',
    walk: '<circle cx="13" cy="4" r="2"/><path d="M9 21l2-6 3 3v3M11 15l1-5 3 3h3M8 10l3-2"/>',
    chev: '<path d="M9 6l6 6-6 6"/>',
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    battery: '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2M6 11v2"/>',
    film: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
    timer: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M10 2h4"/>',
    flame: '<path d="M12 22a7 7 0 0 0 7-7c0-4-3-6.5-4-10-2 1.5-3 3.5-3 5.5C11 9 10 8 9.5 6.5 7 9 5 11.5 5 15a7 7 0 0 0 7 7z"/><path d="M12 22a3 3 0 0 0 3-3c0-2-1.5-3-3-5-1.5 2-3 3-3 5a3 3 0 0 0 3 3z"/>',
    washer: '<rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="13" r="5"/><path d="M8 6h1M12 6h4M9.5 14.5c1.5-1 3.5 1 5-.5"/>',
    smoke: '<circle cx="12" cy="10" r="7"/><circle cx="12" cy="10" r="2"/><path d="M8 20c1-1 2 1 3 0s2 1 3 0 2 1 3 0"/>',
    shield: '<path d="M12 3 5 6v6c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6z"/>',
    left: '<path d="M15 6l-6 6 6 6"/>', right: '<path d="M9 6l6 6-6 6"/>',
    pencil: '<path d="M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', check: '<path d="M5 12l5 5 9-10"/>',
    grip: '<path d="M9 6h.01M15 6h.01M9 12h.01M15 12h.01M9 18h.01M15 18h.01" stroke-width="3.2"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    bed: '<path d="M3 18v-8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5M7 12.5a1.5 1.5 0 1 0 0-.01"/>',
    bath: '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3zM6 12V6a2 2 0 0 1 4 0M7 19l-1 2M17 19l1 2"/>',
    pot: '<path d="M4 10h16v6a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-6zM2 10h2M20 10h2M9 6c0-1 1-1 1-2M14 6c0-1 1-1 1-2"/>',
    desk: '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    robot: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="8.5" r="2.2"/><path d="M6.5 15h11"/>',
    evse: '<rect x="5" y="3" width="10" height="18" rx="2"/><path d="M10.5 7 8.5 11h3l-2 4M15 9h2.5a1 1 0 0 1 1 1v6.5a1.5 1.5 0 0 0 3 0V8"/>',
    heatpump: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="10" cy="12" r="4"/><path d="M10 8v8M6 12h8M17 9h1.5M17 12h1.5M17 15h1.5"/>',
    sprinkler: '<path d="M12 21v-8M8 21h8M12 13 6 7M12 13l6-6M12 13V4M4 9h.01M20 9h.01M7 3.5h.01M17 3.5h.01"/>',
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
    return COMMA ? s.replace(".", ",") : s;
  }
  // values of a metering plug: power, voltage, current, energy today / total
  function meterHtml(st, always) {
    var facts = [];
    function add(value, label) { facts.push('<div class="fact2"><b>' + esc(value) + "</b><span>" + esc(t(label)) + "</span></div>"); }
    if (always || st.power) { add(st.power !== undefined ? watt(st.power) : "–", "usage"); }
    if (st.voltage !== undefined) { add(Math.round(st.voltage) + " V", "voltage"); }
    if (st.current !== undefined) { add(num(st.current, 2) + " A", "current"); }
    if (st.energy_today !== undefined) { add(num(st.energy_today, 2) + " kWh", "energyToday"); }
    if (st.energy_total !== undefined) { add(num(st.energy_total, 1) + " kWh", "energyTotal"); }
    return facts.length ? '<div class="group"><div class="facts2">' + facts.join("") + "</div></div>" : "";
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
      S.rooms = m.rooms; S.tiles = m.tiles; S.scenes = m.scenes; S.header = m.header || {}; checkNotices();
      S.pending = {};
      if (m.type === "welcome") { S.connected = true; S.retry = 0; if (!S.tab) { S.tab = startTab(); } wakeLock(); checkBuild(m.build); }
      render(); loadSparks(true); tapHint(); return;
    }
    if (m.type === "rooms_setup") {
      var idle = 0; (m.rooms || []).forEach(function (r) { r.devices.forEach(function (d) { if (d.idle) { idle++; } }); });
      S.setupHints = { noRoom: (m.unassigned || []).length, idle: idle };
      if (!S.arrange && S.sheet && S.sheet.settings && !S.sheet.page) { renderSettings(); }
      if (S.arrange) { S.arrange.data = m; renderContent(); if (S.sheet && (S.sheet.arrange || S.sheet.addto !== undefined)) { renderSheet(); } } return; }
    if (m.type === "tablet") { S.tablet = m.tablet; applyTheme(); render(); return; }
    if (m.type === "tile") {
      S.tiles[m.tile.id] = m.tile; delete S.pending[m.tile.id];
      if (layout().accent === "lamps" && isLight(m.tile)) { applyAccent(); }
      updateTile(m.tile.id); if (S.sheet && (S.sheet.id === m.tile.id || S.sheet.room || S.sheet.overview || S.sheet.routine) && !S.sliding && !chartActive) { renderSheet(); }
      return;
    }
    if (m.type === "header") {
      var setupBefore = JSON.stringify((S.header && S.header.notice_setup) || {});
      S.header = m.header; checkNotices(); checkApplianceAlert();
      if (S.sheet && S.sheet.id && setupBefore !== JSON.stringify(m.header.notice_setup || {})) { renderSheet(); }
      renderHeader(); if (S.sheet && (S.sheet.batteries || S.sheet.people || S.sheet.routine || S.sheet.weather)) { renderSheet(); } if (S.tab === "home" && !(tdrag && tdrag.active)) { renderContent(); } if (S.saver) { renderSaver(); } return; }
    if (m.type === "bug_info") { S.bugInfo = m.info; if (S.sheet && S.sheet.page === "buginfo") { renderSettings(); } return; }
    if (m.type === "motion") {
      if (S.tablet && S.tablet.room && m.rooms.indexOf(S.tablet.room) >= 0) { wake(); }
      return;
    }
    if (m.type === "failed") { failed(m); return; }
    if (m.type === "all_off") { allOffResult(m); return; }
    if (m.type === "appliance_done") { applianceDone(m); return; }
    if (m.type === "unlocked") { pinAnswer(m); return; }
    if (m.type === "alarm_mode") { alarmModeAnswer(m); return; }
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
    if (layout().start === "cameras" && seesCameras()) { return "cameras"; }
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
  // the languages of lang.js, chosen per browser with a cookie the server reads
  var LANGS = [["auto", ""], ["de", "Deutsch"], ["en", "English"], ["fr", "Français"], ["it", "Italiano"], ["nl", "Nederlands"]];
  function langChoice() { var m = /(?:^|; )dashLang=([a-z]+)/.exec(document.cookie || ""); return m ? m[1] : "auto"; }
  function setLang(code) {
    document.cookie = "dashLang=" + (code === "auto" ? "; max-age=0" : code + "; max-age=315360000") + "; path=/; SameSite=Lax";
    location.reload();
  }
  function dateText(d) {
    if (GERMAN) { return T.weekdays[d.getDay()] + ", " + d.getDate() + ". " + T.months[d.getMonth()]; }
    if (T === EN) { return T.weekdays[d.getDay()] + ", " + T.months[d.getMonth()] + " " + d.getDate(); }
    return T.weekdays[d.getDay()] + " " + d.getDate() + " " + T.months[d.getMonth()];
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
  var KIND_ICON = { light: "bulb", dimmer: "bulb", switch: "power", outlet: "plug", blind: "blind", thermostat: "thermo", lock: "lock", contact: "win", motion: "walk", temperature: "thermo", humidity: "drop", media: "music", fan: "fan", inputs: "sliders", smoke: "smoke", water: "drop", vacuum: "robot", car: "car", wallbox: "evse", heatpump: "heatpump", irrigation: "sprinkler" };
  var TAP_TOGGLES = { light: 1, dimmer: 1, switch: 1, outlet: 1, blind: 1, fan: 1, irrigation: 1 };
  var VIEWS = ["vacuum", "car", "wallbox", "heatpump", "irrigation"];
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
  // plugs which only measure: no switch, the power large
  function measureTileBody(tile) {
    var p = tile.state.power, w = p === undefined ? ["–", ""] : watt(p).split(" ");
    return '<div class="n">' + esc(tile.name) + "</div>" +
      '<div class="cval"><span class="big">' + esc(w[0]) + (w[1] ? "<small>" + esc(w[1]) + "</small>" : "") + "</span></div>" +
      '<div class="s">' + I(KIND_ICON[tile.kind] || "plug", 14) + " " + esc(t("usage")) + "</div>";
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
    } else if (tile.measure) {
      sub = st.power !== undefined ? watt(st.power) : st.on ? t("on") : t("off");
    } else if (k === "switch" || k === "outlet") {
      if (st.on) { cls = "power"; sub = t("on") + (st.power ? " · " + watt(st.power) : ""); } else { sub = t("off"); }
    } else if (k === "blind") {
      cls = "blind";
      var p = st.position;
      sub = p === undefined ? "–" : p >= 99 ? t("open") : p <= 1 ? t("closed") : t("open") + " " + p + " %";
    } else if (k === "thermostat") {
      var heat = heats(tile);
      cls = heat ? "heat" : "cool";
      sub = (st.current !== undefined ? num(st.current) + "° · " : "") + t("target") + " " + num(st.target) + "°";
    } else if (k === "lock") {
      cls = st.locked ? "locked" : "warn"; icon = st.locked ? "lock" : "unlock";
      sub = st.locked ? t("locked") : st.locked === false ? t("unlocked") : "–";
    } else if (k === "contact") {
      icon = tile.door ? "door" : "win";
      if (st.closed === false) { cls = mayOpenNow(tile.may_open) ? "" : "warn"; sub = (st.tilted ? t("tilted") : t("open")) + " " + since(st.since); } else { sub = st.closed ? t("closed") : "–"; }
    } else if (k === "smoke" || k === "water") {
      if (st.alarm) { cls = "alarm"; sub = t(k + "Now") + " " + since(st.since); } else { sub = t("calm"); }
    } else if (k === "motion") {
      if (st.occupied) { cls = "move"; sub = t("motion"); } else { sub = t("nomotion") + (since(st.since) ? " · " + since(st.since) : ""); }
    } else if (k === "temperature") {
      sub = num(st.temperature) + "°" + (st.humidity !== undefined ? " · " + Math.round(st.humidity) + " %" : "");
    } else if (k === "humidity") {
      sub = Math.round(st.humidity) + " %";
    } else if (k === "inputs") {
      sub = inputsLine(tile) || st.state || "";
    } else if (k === "fan") {
      icon = "fan"; if (st.on) { cls = "fanon"; } sub = st.on ? fanText(st) : t("off");
    } else if (VIEWS.indexOf(k) >= 0) {
      var vl = viewLook(tile); cls = vl.cls; sub = vl.sub;
    } else if (k === "media") {
      if (st.playing) { cls = "playing"; sub = mediaLine(st) || t("playing"); } else { sub = st.paused ? [t("paused"), mediaLine(st)].filter(Boolean).join(" · ") : st.on ? t("idle") : t("off"); }
    }
    return { cls: cls, sub: sub, icon: icon, bar: bar };
  }

  // ---------- own views: robot vacuum, car, wallbox, heat pump, irrigation ----------
  function viewRunning(st) { return /clean|saug|running|spot|zone|room/i.test(st.status || "") && !/return|dock|charg|idle|pause/i.test(st.status || ""); }
  function viewLook(tile) {
    var st = tile.state || {}, k = tile.kind, cls = "", parts = [];
    if (k === "vacuum") {
      if (viewRunning(st)) { cls = "power"; }
      if (st.status) { parts.push(st.status); }
      if (has(st.battery)) { parts.push(Math.round(st.battery) + " %"); }
    } else if (k === "car") {
      if (st.charging) { cls = "power"; parts.push(t("vwCharging")); }
      if (has(st.soc)) { parts.push(Math.round(st.soc) + " %"); } else if (has(st.fuel)) { parts.push(Math.round(st.fuel) + " %"); }
      if (has(st.range)) { parts.push(Math.round(st.range) + " km"); }
      if (st.locked === false) { cls = "warn"; parts.push(t("vwUnlocked")); }
    } else if (k === "wallbox") {
      if (st.power > 0) { cls = "power"; parts.push(watt(st.power)); }
      if (st.plugged === true || st.plugged === false) { parts.push(t(st.plugged ? "vwPlugged" : "vwUnplugged")); } else if (st.plugged) { parts.push(st.plugged); }
      if (!parts.length && st.status) { parts.push(st.status); }
    } else if (k === "heatpump") {
      if (st.compressor) { cls = "heat"; }
      if (has(st.flow)) { parts.push(t("vwFlow") + " " + num(st.flow, 0) + "°"); }
      if (has(st.dhw)) { parts.push(t("vwDhw") + " " + num(st.dhw, 0) + "°"); }
      if (!parts.length && st.status) { parts.push(st.status); }
    } else if (k === "irrigation") {
      if (st.on) { cls = "cool"; parts.push(t("vwWatering")); } else { parts.push(t("off")); }
      if (has(st.moisture)) { parts.push(Math.round(st.moisture) + " %"); }
    }
    return { cls: cls, sub: parts.join(" · ") || "–" };
  }
  function viewFacts(tile) {
    var st = tile.state || {}, k = tile.kind, f = [];
    function add(cond, value, label) { if (cond) { f.push([value, label]); } }
    if (k === "vacuum") {
      add(st.status, st.status, ""); add(has(st.battery), Math.round(st.battery) + " %", t("vwBattery"));
      add(has(st.area), num(st.area, 0) + " m²", t("vwArea")); add(has(st.duration), Math.round(st.duration) + " min", t("vwDuration"));
      add(st.fan && !(tile.view && tile.view.modes), st.fan, t("vwFan"));
    } else if (k === "car") {
      add(has(st.soc), Math.round(st.soc) + " %", t("vwSoc")); add(has(st.fuel), Math.round(st.fuel) + " %", t("vwFuel"));
      add(has(st.range), Math.round(st.range) + " km", t("vwRange"));
      add(st.charging === true || st.charging === false, t(st.charging ? "vwCharging" : "vwNotCharging"), st.power ? watt(st.power) : "");
      add(has(st.remaining) && st.charging, Math.round(st.remaining) + " min", t("vwRemaining"));
      add(st.plugged === true || st.plugged === false, t(st.plugged ? "vwPlugged" : "vwUnplugged"), "");
      add(st.locked === true || st.locked === false, t(st.locked ? "vwLocked" : "vwUnlocked"), "");
      add(has(st.mileage), Math.round(st.mileage).toLocaleString(GERMAN ? "de-DE" : "en-GB") + " km", t("vwMileage"));
    } else if (k === "wallbox") {
      add(has(st.power), watt(st.power), t("vwPower")); add(has(st.energy), num(st.energy, 1) + " kWh", t("vwEnergy"));
      add(st.plugged !== undefined, st.plugged === true ? t("vwPlugged") : st.plugged === false ? t("vwUnplugged") : st.plugged, "");
      add(st.status, st.status, ""); add(st.mode && !(tile.view && tile.view.modes), st.mode, t("vwMode"));
    } else if (k === "heatpump") {
      add(has(st.flow), num(st.flow, 1) + "°", t("vwFlow")); add(has(st.return), num(st.return, 1) + "°", t("vwReturn"));
      add(has(st.outside), num(st.outside, 1) + "°", t("vwOutside")); add(has(st.dhw), num(st.dhw, 1) + "°", t("vwDhw"));
      add(st.compressor !== undefined, has(st.compressor_pct) ? Math.round(st.compressor_pct) + " %" : t(st.compressor ? "vwCompOn" : "vwCompOff"), t("vwCompressor"));
      add(has(st.cop), num(st.cop, 1), t("vwCop")); add(has(st.power), watt(st.power), t("vwHpPower"));
      add(st.status && (!tile.view || !tile.view.modes || tile.view.modes.indexOf(st.status) < 0), st.status, "");
    } else if (k === "irrigation") {
      add(has(st.moisture), Math.round(st.moisture) + " %", t("vwMoisture")); add(st.next, st.next, t("vwNext"));
      add(has(st.remaining) && st.on, Math.round(st.remaining) + " min", t("vwRemaining"));
    }
    add(st.error, st.error, t("vwError"));
    return f;
  }
  var VIEW_ACTIONS = { start: ["vwStart", "play"], pause: ["vwPause", "pause"], stop: ["vwStop", "x"], dock: ["vwDock", "home"], locate: ["vwLocate", "bell"], lock: ["vwLock", "lock"], unlock: ["vwUnlock", "unlock"],
    charge_start: ["vwChargeStart", "bolt"], charge_stop: ["vwChargeStop", "x"], climate_start: ["vwClimateStart", "fan"], climate_stop: ["vwClimateStop", "x"], update: ["vwUpdate", "clock"], dhw_boost: ["vwDhwBoost", "drop"] };
  function viewSheetHtml(tile) {
    var st = tile.state || {}, v = tile.view || {}, html = "", facts = viewFacts(tile), ro = S.tablet && S.tablet.readonly;
    if (facts.length) { html += '<div class="group facts2 vfacts">' + facts.map(function (f) { return '<div class="fact2"><b>' + esc(f[0]) + "</b><span>" + esc(f[1]) + "</span></div>"; }).join("") + "</div>"; }
    if (tile.kind === "irrigation" && !ro) {
      html += '<div class="group"><div class="actions"><button class="pill' + (st.on ? " on" : "") + '" data-do="on">' + I("drop", 20) + " " + esc(t("on")) + '</button><button class="pill' + (!st.on ? " on" : "") + '" data-do="off">' + esc(t("off")) + "</button></div></div>" + timerHtml(tile);
    }
    var acts = (v.actions || []).filter(function (a) { return VIEW_ACTIONS[a]; });
    if (acts.length && !ro) {
      html += '<div class="group"><div class="actions vacts">' + acts.map(function (a) {
        return '<button class="pill' + (a === "unlock" ? " danger" : "") + '" data-vact="' + a + '">' + I(VIEW_ACTIONS[a][1], 20) + " " + esc(t(VIEW_ACTIONS[a][0])) + "</button>";
      }).join("") + "</div></div>";
    }
    if (v.modes && v.modes.length && !ro) {
      var cur = tile.kind === "vacuum" ? st.fan : st.mode || st.status;
      html += '<div class="group"><div class="label">' + esc(t(tile.kind === "vacuum" ? "vwFan" : "vwMode")) + '</div><div class="seg">' + v.modes.map(function (m) {
        return '<button class="' + (String(cur) === m ? "on" : "") + '" data-vmode="' + esc(m) + '">' + esc(m) + "</button>";
      }).join("") + "</div></div>";
    }
    return html;
  }
  function viewChoiceHtml(tile) {
    var cur = VIEWS.indexOf(tile.kind) >= 0 ? tile.kind : "";
    var opts = [["", t("vwNormal")]].concat(VIEWS.map(function (v) { return [v, t("vw" + v)]; }));
    return '<div class="group"><div class="label">' + esc(t("vwViewAs")) + (cur && tile.detected ? ' <span class="sub">(' + esc(t("vwDetected")) + ")</span>" : "") + '</div><div class="lead vlead">' + esc(t("vwViewLead")) + '</div><div class="seg vchoice">' + opts.map(function (o) {
      return '<button class="' + (o[0] === cur ? "on" : "") + '" data-vview="' + o[0] + '">' + esc(o[1]) + "</button>";
    }).join("") + "</div></div>";
  }
  function viewClick(target) {
    var el, id = S.sheet && S.sheet.id; if (!id) { return false; }
    if ((el = closest(target, "data-vact"))) {
      var a = el.getAttribute("data-vact");
      if (a === "unlock" && !armed(el, "vunlock:" + id, t("vwUnlockSure"))) { return true; }
      act(id, a); return true;
    }
    if ((el = closest(target, "data-vmode"))) {
      var m = el.getAttribute("data-vmode"), tile = S.tiles[id];
      act(id, "mode", m, tile && tile.kind === "vacuum" ? { fan: m } : { mode: m }); renderSheet(); return true;
    }
    if ((el = closest(target, "data-vview"))) {
      var view = el.getAttribute("data-vview"), tl = S.tiles[id];
      // back to "Normal" on a detected device means: no own view
      if (!view && tl && tl.detected && VIEWS.indexOf(tl.kind) >= 0) { view = "none"; }
      send({ type: "device_view", id: id, view: view }); return true;
    }
    return false;
  }

  function tileHtml(id, editState) {
    var tile = S.tiles[id]; if (!tile) { return ""; }
    var look = tileLook(tile), size = tileSize(id), wide = size === "w" || size === "b", tall = size === "t" || size === "b";
    var body, climate = tile.kind === "thermostat" || tile.kind === "temperature" || tile.kind === "humidity";
    if (climate) {
      body = climateTileBody(id, tile, look, editState);
    } else if (tile.kind === "media") {
      body = mediaTileBody(id, tile, look, editState);
    } else if (tile.measure) {
      body = measureTileBody(tile);
    } else {
      body = '<div class="ic' + (TAP_TOGGLES[tile.kind] && !tile.measure ? " sw" : "") + '">' + (tile.kind === "blind" ? winMini(tile.state.position) : I(look.icon)) + '</div><div><div class="n">' + esc(tile.name) + '</div><div class="s">' + esc(look.sub) + "</div></div>";
    }
    var extra = "";
    if (look.bar !== null && look.bar !== undefined) { extra += '<div class="bar" style="width:' + look.bar + '%"></div>'; }
    if (tile.state.fan && tile.state.fan.mode && tile.state.fan.mode !== "off" && !editState) { extra += '<div class="fanbadge">' + I("fan", 18) + "</div>"; }
    if (timerLeft(tile) && !editState) { extra += '<div class="tbadge">' + I("timer", 15) + " " + esc(timerText(timerLeft(tile))) + "</div>"; }
    if (tile.color && tile.state.on && (tile.state.rgb || tile.state.ct) && !editState) { extra += '<div class="cdot" style="background:' + lampColor(tile.state) + '"></div>'; }
    if (tile.state.battery_low && !editState) { extra += '<div class="badge">' + I("battery", 18) + "</div>"; }
    if (editState) {
      extra += '<div class="edit" data-edit="' + (editState === "hidden" ? "show" : "hide") + '">' + I(editState === "hidden" ? "plus" : "x") + "</div>";
      if (editState === "shown") { extra += '<div class="szbtn" data-size="' + esc(id) + '" aria-label="' + esc(t("tileSize")) + '">' + SIZE_LABEL[size] + "</div>"; }
    }
    return '<button class="tile ' + look.cls + (climate ? " climate" : "") + (tile.measure && !climate && tile.kind !== "media" ? " measure" : "") + (tile.kind === "media" ? " media" + (tile.state.art ? " hascover" : "") : "") + (tile.kind === "dimmer" || tile.kind === "blind" || tile.kind === "fan" ? " slidable" : "") + (wide ? " wide" : "") + (tall ? " tall" : "") + (S.pending[id] ? " pending" : "") + (editState === "hidden" ? " hiddenTile" : "") +
      '" data-tile="' + esc(id) + '">' + body + extra + "</button>";
  }

  // size of a tile on this tablet: s small, w wide, t tall, b big
  var SIZES = ["s", "w", "t", "b"], SIZE_LABEL = { s: "1×1", w: "2×1", t: "1×2", b: "2×2" };
  function tileSize(id) {
    var size = (layout().tile_size || {})[id], tile = S.tiles[id];
    if (SIZES.indexOf(size) >= 0) { return size; }
    return tile && (tile.kind === "thermostat" || tile.kind === "media") ? "w" : "s";
  }
  // headings are entries "#Text" in the order of a room
  function withHeadings(ids, order) {
    var result = ids.slice();
    (order || []).forEach(function (entry, i) {
      if (entry.charAt(0) !== "#") { return; }
      var next = null;
      for (var j = i + 1; j < order.length; j++) { if (order[j].charAt(0) !== "#" && result.indexOf(order[j]) >= 0) { next = order[j]; break; } }
      var at = next === null ? result.length : result.indexOf(next);
      // headings right before this one stay in their order
      while (at > 0 && result[at - 1].charAt(0) === "#" && order.indexOf(result[at - 1]) > i) { at--; }
      result.splice(at, 0, entry);
    });
    return result;
  }
  function headHtml(entry, edit) {
    return '<div class="gh' + (edit ? " tile" : "") + '" ' + (edit ? "data-tile" : "data-head") + '="' + esc(entry) + '"><span>' + esc(entry.slice(1)) + "</span>" + (edit ? '<div class="edit" data-delhead="' + esc(entry) + '">' + I("x") + "</div>" : "") + "</div>";
  }
  function gridItem(id, editState) { return id.charAt(0) === "#" ? headHtml(id, !!editState) : tileHtml(id, editState); }
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
    if (!TAP_TOGGLES[tile.kind] || tile.measure) { openSheet(id); return; }
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
    if (S.tour) { renderTour(); return; }
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
    checkAlarm();
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
  // also devices in several rooms belong to each of them
  function inRoom(x, name) {
    var tl = S.tiles[x.id];
    return x.room === name || !!(tl && tl.rooms && tl.rooms.indexOf(name) >= 0);
  }
  function shownList(list) {
    var ids = shownIds();
    if (!ids) { return list || []; }
    var hidden = layout().hidden_rooms || [];
    return (list || []).filter(function (x) { return ids[x.id]; }).map(function (x) {
      // a device in several rooms is named by a room this tablet shows
      var tl = S.tiles[x.id], rooms = (tl && tl.rooms) || [];
      if (!x.room || hidden.indexOf(x.room) < 0) { return x; }
      var room = rooms.filter(function (r) { return hidden.indexOf(r) < 0; })[0];
      if (!room) { return x; }
      var copy = {};
      Object.keys(x).forEach(function (k) { copy[k] = x[k]; });
      copy.room = room;
      return copy;
    });
  }
  function warningText() {
    var open = warnOpen(S.header && S.header.open);
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
      var openHere = (S.header.open || []).some(function (o) { return inRoom(o, r.name) && !mayOpenNow(o.may_open); });
      tabs.push({ id: "room:" + r.name, name: r.name, dot: openHere });
    });
    if (seesCameras()) { tabs.push({ id: "cameras", name: t("cameras") }); } else if (S.tab === "cameras") { S.tab = "home"; }
    if (seesTimeline()) { tabs.push({ id: "history", name: t("history") }); } else if (S.tab === "history") { S.tab = "home"; }
    el.innerHTML = tabs.map(function (tb) {
      return '<button class="tab' + (tb.id === S.tab ? " on" : "") + '" data-tab="' + esc(tb.id) + '">' + esc(tb.name) + (tb.dot ? '<span class="dot"></span>' : "") + "</button>";
    }).join("");
    var on = el.querySelector(".tab.on"); if (on && on.scrollIntoView) { on.scrollIntoView({ inline: "nearest", block: "nearest" }); }
  }

  function renderContent() {
    var el = document.getElementById("content"); if (!el) { return; }
    var top = el.scrollTop;
    if (S.arrange) { el.innerHTML = arrangeHtml(); } else if (S.tab === "home") { el.innerHTML = homeHtml(); } else if (S.tab === "history") { el.innerHTML = historyHtml(); } else if (S.tab === "cameras") { el.innerHTML = camerasHtml(); camSnaps(); } else { el.innerHTML = roomHtml(roomByName(S.tab.slice(5))); }
    el.scrollTop = top;
    S.shownTab = S.tab;
  }

  function leaveHtml() {
    // plugs which only measure (fridge) are always on: not worth a line
    // a tap on a line opens the details of the device, a group opens its overview
    function tap(id) { return S.tiles[id] ? ' tap" data-ovopen="' + esc(id) : ""; }
    var chev = I("chev");
    var h = S.header, open = warnOpen(h.open), running = shownList(h.running).filter(function (r) { return !r.measure; }), rows = "";
    open.forEach(function (o) {
      rows += '<div class="row' + tap(o.id) + '"><div class="ic" style="background:rgba(255,138,61,.16);color:var(--amber2)">' + I(o.door ? "door" : "win") + '</div><div class="t"><b>' + esc(o.name) + "</b><span>" +
        esc([o.room, (o.tilted ? t("tilted") : t("open")) + " " + since(o.since)].filter(Boolean).join(" · ")) + "</span></div>" + (tap(o.id) ? chev : "") + "</div>";
    });
    var wasted = heatingOpenRooms();
    if (wasted.length) {
      var heatTap = wasted.length === 1 ? ' tap" data-roompop="' + esc(wasted[0]) : ' tap" data-overview="climate';
      rows += '<div class="row' + heatTap + '"><div class="ic" style="background:rgba(255,90,95,.16);color:var(--red)">' + I("thermo") + '</div><div class="t"><b>' + esc(t("heatingOpen")) + "</b><span>" + esc(wasted.join(", ")) + "</span></div>" + chev + "</div>";
    }
    var lights = running.filter(function (r) { return r.kind === "light" || r.kind === "dimmer"; });
    if (lights.length) {
      var rooms = []; lights.forEach(function (l) { if (l.room && rooms.indexOf(l.room) < 0) { rooms.push(l.room); } });
      var lightTap = lights.length === 1 ? tap(lights[0].id) : ' tap" data-overview="light';
      rows += '<div class="row' + lightTap + '"><div class="ic" style="background:rgba(255,181,71,.16);color:var(--amber)">' + I("bulb") + '</div><div class="t"><b>' +
        esc(lights.length === 1 ? lights[0].name : t("lightsOn", { n: lights.length })) + "</b><span>" + esc(rooms.join(", ")) + "</span></div>" + (lightTap ? chev : "") + "</div>";
    }
    running.filter(function (r) { return r.kind !== "light" && r.kind !== "dimmer"; }).forEach(function (r) {
      rows += '<div class="row' + tap(r.id) + '"><div class="ic" style="background:rgba(155,140,255,.16);color:var(--violet)">' + I("bolt") + '</div><div class="t"><b>' + esc(r.name) + "</b><span>" +
        esc([r.room, t("on") + (r.power ? " · " + watt(r.power) : ""), r.keep_on && !(S.tablet && S.tablet.arrange) ? t("staysOn") : ""].filter(Boolean).join(" · ")) + "</span></div>" +
        (S.tablet && S.tablet.arrange ? '<button class="pill keep' + (r.keep_on ? " kept" : "") + '" data-keepon="' + esc(r.id) + '">' + (r.keep_on ? I("check", 18) + " " + esc(t("staysOn")) : esc(t("keepBtn"))) + "</button>" : "") +
        '<button class="pill" data-off="' + esc(r.id) + '">' + esc(t("off")) + "</button></div>";
    });
    shownList(h.playing).forEach(function (r) {
      var what = [r.title, r.artist].filter(Boolean).join(" · "), mt = S.tiles[r.id], art = mt && mt.state.art;
      // the cover of what is playing, the note until it is loaded
      rows += '<div class="row' + tap(r.id) + '"><div class="ic' + (art ? " rcover" : "") + '" style="background:rgba(90,169,255,.16);color:var(--blue)">' + I("music") + (art ? coverImg(r.id, art, "rimg") : "") + '</div><div class="t"><b>' + esc(r.name) + "</b><span>" +
        esc([r.room, what || t("playing")].filter(Boolean).join(" · ")) + "</span></div>" +
        '<button class="pill" data-mpause="' + esc(r.id) + '">' + I("pause", 18) + " " + esc(t("vwPause")) + "</button></div>";
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
      var heating = r.tiles.some(function (id) { var tl = S.tiles[id]; return tl && tl.kind === "thermostat" && heats(tl); });
      if (heating && result.indexOf(r.name) < 0) { result.push(r.name); }
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
    return '<div class="leave enleave" data-energy="1"><div class="section" style="margin:0 0 12px"><span>' + esc(t("energy")) + "</span>" + (surplus ? '<span style="color:var(--green);text-transform:none;letter-spacing:0">' + esc(t("surplus")) + "</span>" : "") +
      '</div><div class="facts2">' + parts.map(function (p) { return '<div class="fact2"><b>' + esc(p[0]) + "</b><span>" + esc(p[1]) + "</span></div>"; }).join("") + "</div>" + energyDayHtml() + "</div>";
  }
  // the curve of today on the energy card: solar as area, usage as line
  function energyDayHtml() {
    if (!S.header.timeline) { return ""; }
    var c = S.enDay;
    if (!c || (!c.loading && Date.now() - c.at > 600000)) {
      S.enDay = { loading: true, at: Date.now(), data: c && c.data };
      api("api/energy?range=day").then(function (data) {
        S.enDay = { at: Date.now(), data: data };
        var el = document.getElementById("enday"); if (el) { el.outerHTML = energyDayHtml(); }
      }).catch(function () { S.enDay = { at: Date.now(), data: null }; });
    }
    var data = S.enDay && S.enDay.data, bars = (data && data.bars) || [];
    var now = Date.now() / 1000, past = bars.filter(function (b) { return b.at <= now; });
    var solar = past.some(function (b) { return b.solar > 0; }), use = past.some(function (b) { return has(b.load); });
    if (!past.length || (!solar && !use)) { return '<div id="enday"></div>'; }
    var w = 300, h = 54, n = bars.length, max = 0;
    past.forEach(function (b) { max = Math.max(max, b.solar || 0, b.load || 0); });
    if (!max) { return '<div id="enday"></div>'; }
    function x(i) { return (i + 0.5) / n * w; }
    function y(v) { return h - 2 - (v / max) * (h - 6); }
    var svg = '<svg class="endaysvg" viewBox="0 0 ' + w + " " + h + '" preserveAspectRatio="none">';
    if (solar) {
      var area = "M" + x(0).toFixed(1) + " " + (h - 2);
      past.forEach(function (b, i) { area += " L" + x(i).toFixed(1) + " " + y(b.solar || 0).toFixed(1); });
      area += " L" + x(past.length - 1).toFixed(1) + " " + (h - 2) + "Z";
      svg += '<path class="sol" d="' + area + '"/>';
    }
    if (use) { svg += '<polyline class="use" points="' + past.map(function (b, i) { return x(i).toFixed(1) + "," + y(b.load || 0).toFixed(1); }).join(" ") + '"/>'; }
    svg += "</svg>";
    var tot = data.totals || {}, label = [];
    if (solar && has(tot.solar)) { label.push('<i class="sol"></i>' + esc(kwh(tot.solar)) + " " + esc(t("solar"))); }
    if (use && has(tot.load)) { label.push('<i class="use"></i>' + esc(kwh(tot.load)) + " " + esc(t("usage"))); }
    return '<div id="enday" class="enday"><div class="endaylbl"><span>' + esc(t("enDay")) + "</span>" + label.join("") + "</div>" + svg + "</div>";
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
    var ids = roomTiles(room), lights = 0, temp = null, open = 0, other = 0, tempId = null, humid = null, co2 = null, motion = 0, someone = false, quiet = "";
    ids.forEach(function (id) {
      var tile = S.tiles[id], st = tile.state;
      if (tile.kind === "motion") { motion++; if (st.occupied) { someone = true; } else if (st.since && st.since > quiet) { quiet = st.since; } }
      if (tempId === null && (tile.kind === "thermostat" || tile.kind === "temperature") && climateOf(tile).temp !== undefined) { tempId = id; }
      if (humid === null && st.humidity !== undefined && st.humidity !== null) { humid = st.humidity; }
      if ((tile.kind === "light" || tile.kind === "dimmer") && st.on) { lights++; } else if ((tile.kind === "switch" || tile.kind === "outlet") && st.on && !tile.measure) { other++; }
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
    // somebody in the room: motion or presence sensors
    if (someone) { facts += '<span class="fact pres">' + I("person", 14) + " " + esc(t("someone")) + "</span>"; } else if (motion && quiet && since(quiet)) { facts += '<span class="fact">' + esc(t("quietFor", { t: since(quiet) })) + "</span>"; }
    if (editState) {
      return '<div class="tile roomcard' + (lights ? " light" : "") + (editState === "hidden" ? " hiddenTile" : "") + '" data-tile="room:' + esc(room.name) + '">' + climate + '<div class="n">' + esc(room.name) + '</div><div class="facts">' + facts + "</div>" +
        '<div class="edit" data-edit="' + (editState === "hidden" ? "show" : "hide") + '">' + I(editState === "hidden" ? "plus" : "x") + "</div></div>";
    }
    return '<button class="tile roomcard' + (lights ? " light" : "") + '" data-roompop="' + esc(room.name) + '">' + climate + '<div class="n">' + esc(room.name) + '</div><div class="facts">' + facts + "</div></button>";
  }

  function homeHtml() {
    var rooms = visibleRooms();
    if (!rooms.length) { return '<div class="empty">' + esc(t("noDevices")) + "</div>"; }
    var left = noticesHtml() + routinesHtml() + appliancesHtml() + leaveHtml() + calendarHtml() + energyHtml() + latelyHtml();
    var right;
    if (S.edit) {
      var hiddenT = layout().hidden_tiles || [], all = homeRooms(true);
      var shown = all.filter(function (r) { return hiddenT.indexOf("room:" + r.name) < 0; }), gone = all.filter(function (r) { return hiddenT.indexOf("room:" + r.name) >= 0; });
      right = '<div class="edithint">' + esc(t("editHint")) + '</div><div class="grid">' + shown.map(function (r) { return roomCardHtml(r, "shown"); }).join("") + "</div>" +
        (gone.length ? '<div class="section">' + esc(t("hiddenTiles")) + '</div><div class="grid">' + gone.map(function (r) { return roomCardHtml(r, "hidden"); }).join("") + "</div>" : "") +
        '<div class="actions"><button class="pill primary" data-editdone="1">' + I("check", 20) + " " + esc(t("editDone")) + "</button></div>";
    } else {
      right = floorsHomeHtml(homeRooms(false));
    }
    return statusChipsHtml() + '<div class="home split"><div style="display:flex;flex-direction:column;gap:16px">' + left + "</div><div>" + right + "</div></div>";
  }

  // ---------- floors: room cards grouped by floor ----------
  function floorList() { return (S.header && S.header.floors) || []; }
  function floorsHomeHtml(rooms) {
    var floors = floorList(), ro = S.tablet && S.tablet.readonly;
    if (!floors.length) { return '<div class="grid">' + rooms.map(function (r) { return roomCardHtml(r); }).join("") + "</div>"; }
    var used = {}, html = "";
    floors.forEach(function (f, i) {
      var here = rooms.filter(function (r) { return f.rooms.indexOf(r.name) >= 0; });
      if (!here.length) { return; }
      here.forEach(function (r) { used[r.name] = 1; });
      html += '<div class="floorhead"><span>' + esc(f.name) + "</span>" + (ro ? "" : '<button class="pill sm" data-floor="' + i + '" data-floorwhat="lights">' + I("bulb", 16) + " " + esc(t("floorLights")) + '</button><button class="pill sm" data-floor="' + i + '" data-floorwhat="down">' + I("blind", 16) + " " + esc(t("floorBlinds")) + "</button>") + "</div>" +
        '<div class="grid">' + here.map(function (r) { return roomCardHtml(r); }).join("") + "</div>";
    });
    var rest = rooms.filter(function (r) { return !used[r.name]; });
    if (rest.length) { html += '<div class="floorhead"><span>' + esc(t("floorOther")) + '</span></div><div class="grid">' + rest.map(function (r) { return roomCardHtml(r); }).join("") + "</div>"; }
    return html;
  }
  function floorAll(index, what) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var f = floorList()[index]; if (!f) { return; }
    visibleRooms().filter(function (r) { return f.rooms.indexOf(r.name) >= 0; }).forEach(function (r) {
      roomTiles(r).forEach(function (id) {
        var tl = S.tiles[id];
        if (what === "lights" && isLight(tl) && tl.state.on) { act(id, "off", null, { on: false }); }
        if (what === "down" && tl.kind === "blind" && tl.state.position !== 0) { act(id, "position", 0, { position: 0 }); }
      });
    });
  }
  // floors from room names like "EG Küche" or "OG.Bad": only a suggestion
  var FLOOR_RE = /^(UG|KG|EG|OG|DG|[0-9]\.?\s?OG|Keller|Erdgeschoss|Obergeschoss|Dachgeschoss|Basement|Ground|Upstairs|Attic)[\s._-]+/i;
  function floorSuggestion() {
    var result = [];
    S.rooms.forEach(function (r) {
      var m = FLOOR_RE.exec(r.name); if (!m) { return; }
      var name = m[1].toUpperCase().length <= 3 ? m[1].toUpperCase() : m[1];
      var f = result.filter(function (x) { return x.name === name; })[0];
      if (!f) { f = { name: name, rooms: [] }; result.push(f); }
      f.rooms.push(r.name);
    });
    return result;
  }
  function renderFloors() {
    var d = S.sheet.floors || (S.sheet.floors = JSON.parse(JSON.stringify(floorList())));
    var html = settingsHead(t("floors"), t("setHome"), true) + '<div class="hint" style="text-align:left;margin:4px 0 16px">' + esc(t("floorsLead")) + "</div>";
    var sug = floorSuggestion();
    if (!d.length && sug.length) {
      html += '<div class="group"><div class="list"><div class="item"><span class="grow">' + esc(t("floorSuggest", { list: sug.map(function (f) { return f.name + " (" + f.rooms.length + ")"; }).join(", ") })) + '</span><button class="pill" data-floortake="1">' + esc(t("floorTake")) + "</button></div></div></div>";
    }
    html += '<div class="group"><div class="list">' + d.map(function (f, i) {
      return '<div class="item"><input data-floorname="' + i + '" value="' + esc(f.name) + '" maxlength="40" style="flex:1"><button class="iconbtn" data-floordel="' + i + '">' + I("x") + "</button></div>";
    }).join("") + '<div class="item ntrow"><input id="newfloor" maxlength="40" placeholder="' + esc(t("floorName")) + '" style="flex:1"><button class="pill" data-flooradd="1">' + I("plus", 18) + " " + esc(t("floorAdd")) + "</button></div></div></div>";
    if (d.length) {
      html += '<div class="group"><div class="list">' + allRoomsOrdered().map(function (r) {
        var cur = -1; d.forEach(function (f, i) { if (f.rooms.indexOf(r.name) >= 0 && cur < 0) { cur = i; } });
        return '<div class="item"><span class="grow">' + esc(r.name) + '</span><div class="seg">' + '<button class="' + (cur < 0 ? "on" : "") + '" data-floorroom="' + esc(r.name) + '" data-floorto="-1">' + esc(t("floorNone")) + "</button>" +
          d.map(function (f, i) { return '<button class="' + (cur === i ? "on" : "") + '" data-floorroom="' + esc(r.name) + '" data-floorto="' + i + '">' + esc(f.name) + "</button>"; }).join("") + "</div></div>";
      }).join("") + "</div></div>";
    }
    html += '<div class="actions"><button class="pill primary" data-floorsave="1">' + esc(t("floorSave")) + "</button></div>";
    sheetShell(html);
  }
  function floorNames() {
    var d = S.sheet && S.sheet.floors; if (!d) { return; }
    Array.prototype.forEach.call(document.querySelectorAll("[data-floorname]"), function (el) { var f = d[+el.getAttribute("data-floorname")]; if (f && el.value.trim()) { f.name = el.value.trim(); } });
  }
  function floorClick(target) {
    var el, d = S.sheet && S.sheet.floors;
    if ((el = closest(target, "data-floor")) && !S.sheet) { floorAll(+el.getAttribute("data-floor"), el.getAttribute("data-floorwhat")); return true; }
    if (!d) { return false; }
    floorNames();
    if ((el = closest(target, "data-floortake"))) { S.sheet.floors = floorSuggestion(); renderFloors(); return true; }
    if ((el = closest(target, "data-flooradd"))) {
      var input = document.getElementById("newfloor"), name = input ? input.value.trim() : "";
      if (name && !d.some(function (f) { return f.name === name; })) { d.push({ name: name, rooms: [] }); }
      renderFloors(); return true;
    }
    if ((el = closest(target, "data-floordel"))) { d.splice(+el.getAttribute("data-floordel"), 1); renderFloors(); return true; }
    if ((el = closest(target, "data-floorroom"))) {
      var room = el.getAttribute("data-floorroom"), to = +el.getAttribute("data-floorto");
      d.forEach(function (f) { f.rooms = f.rooms.filter(function (x) { return x !== room; }); });
      if (to >= 0 && d[to]) { d[to].rooms.push(room); }
      renderFloors(); return true;
    }
    if ((el = closest(target, "data-floorsave"))) {
      if (!pinOk()) { askPin(null); return true; }
      send({ type: "floors", floors: d }); S.sheet.floors = null; S.sheet.page = ""; renderSettings(); return true;
    }
    return false;
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
    var ids = roomTiles(room, S.edit), order = (layout().tile_order || {})[room.name];
    if (S.edit) {
      var hidden = layout().hidden_tiles || [];
      var shown = withHeadings(ids.filter(function (id) { return hidden.indexOf(id) < 0; }), order);
      var gone = ids.filter(function (id) { return hidden.indexOf(id) >= 0; });
      html += '<div class="edithint">' + esc(t("editHint")) + " " + esc(t("editHint2")) + "</div>";
      html += '<div class="headadd"><input id="newhead" maxlength="40" placeholder="' + esc(t("headPlaceholder")) + '"><button class="pill" data-addhead="1">' + I("plus", 18) + " " + esc(t("headAdd")) + '</button><button class="linkbtn" data-roomreset="' + esc(room.name) + '">' + esc(t("roomReset")) + "</button></div>";
      html += '<div class="grid tgrid">' + shown.map(function (id) { return gridItem(id, "shown"); }).join("") + "</div>";
      if (gone.length) { html += '<div class="section">' + esc(t("hiddenTiles")) + '</div><div class="grid">' + gone.map(function (id) { return tileHtml(id, "hidden"); }).join("") + "</div>"; }
      html += '<div class="actions"><button class="pill primary" data-editdone="1">' + I("check", 20) + " " + esc(t("editDone")) + "</button></div>";
      return html;
    }
    html += '<div class="grid tgrid">' + withHeadings(ids, order).map(function (id) { return gridItem(id); }).join("") + "</div>";
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
    var old = d.firstChild, top = old ? old.scrollTop : 0, key = JSON.stringify([S.sheet && S.sheet.id, S.sheet && S.sheet.settings, S.sheet && S.sheet.page, S.sheet && S.sheet.batteries, S.sheet && S.sheet.arrange, S.sheet && S.sheet.rename, S.sheet && S.sheet.addto, S.sheet && S.sheet.people, S.sheet && S.sheet.room, S.sheet && S.sheet.overview, S.sheet && S.sheet.routine, S.sheet && S.sheet.weather, S.sheet && S.sheet.energy, S.sheet && S.sheet.pin !== undefined]);
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
    if (S.sheet.energy) { renderEnergy(); return; }
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
    } else if (tile.measure) {
      body += meterHtml(st, true);
      if (S.tablet && S.tablet.arrange) { body += measureHtml(tile); }
    } else if (k === "light" || k === "dimmer" || k === "switch" || k === "outlet") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.on ? " on" : "") + '" data-do="on">' + I("power", 20) + " " + esc(t("on")) + '</button><button class="pill' + (!st.on ? " on" : "") + '" data-do="off">' + esc(t("off")) + "</button></div></div>";
      body += meterHtml(st, false);
      if (tile.color) { body += colorHtml(tile); }
      body += timerHtml(tile);
      if (S.tablet && S.tablet.arrange) { body += keepOnHtml(tile) + (k === "switch" || k === "outlet" ? measureHtml(tile) : ""); }
    } else if (k === "blind") {
      var bp = st.position;
      body += '<div class="group"><div class="actions wbtns"><button class="pill' + (bp >= 99 ? " on" : "") + '" data-do="up">' + esc(t("up")) + '</button><button class="pill' + (bp >= 45 && bp <= 55 ? " on" : "") + '" data-half="1">' + esc(t("half")) + "</button>" +
        '<button class="pill' + (bp !== undefined && bp <= 1 ? " on" : "") + '" data-do="down">' + esc(t("down")) + "</button>" + (tile.stop ? '<button class="pill" data-do="stop">' + esc(t("stop")) + "</button>" : "") + "</div></div>";
    } else if (k === "thermostat") {
      body += '<div class="tring">' + climateHtml(tile) + "</div>";
    } else if (k === "lock") {
      body += '<div class="group"><div class="actions"><button class="pill' + (st.locked ? " on" : "") + '" data-do="lock">' + I("lock", 20) + " " + esc(t("lock")) + '</button><button class="pill danger" data-do="unlock">' + I("unlock", 20) + " " + esc(t("unlock")) + "</button></div></div>";
    } else if (k === "contact" && S.tablet && !S.tablet.readonly) {
      body += mayOpenHtml(tile);
    } else if (k === "temperature" || k === "humidity") {
      body += '<div class="group facts2">' + (st.temperature !== undefined ? '<div class="fact2"><b>' + num(st.temperature) + "°</b><span>" + esc(t("temperature")) + "</span></div>" : "") + (st.humidity !== undefined ? '<div class="fact2"><b>' + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span></div>" : "") + "</div>";
    }
    if (VIEWS.indexOf(k) >= 0) { body += viewSheetHtml(tile); }
    if (S.tablet && S.tablet.arrange && (VIEWS.indexOf(k) >= 0 || ((k === "switch" || k === "outlet") && !tile.measure))) { body += viewChoiceHtml(tile); }
    if (tile.fan && k !== "fan") { body += fanHtml(st.fan); }
    if (S.tablet && !S.tablet.readonly && k !== "media") { body += noticeEditHtml(tile); }
    body += sheetTrendsHtml() + sheetHistoryHtml();
    var cols = !!left;
    sheetShell(cols ? left + "<div>" + head + body + "</div>" : head + body, cols ? "cols" + (k === "media" ? " msheet" : "") : "");
  }
  function measureHtml(tile) {
    return '<div class="group"><div class="list"><div class="item"><div class="grow"><div>' + esc(t("measure")) + '</div><div class="hint" style="text-align:left;margin:2px 0 0">' + esc(t("measureHint")) + "</div></div>" +
      '<button class="tg' + (tile.measure ? "" : " off") + '" data-measure="' + esc(tile.id) + '" aria-label="' + esc(t("measure")) + '"></button></div></div></div>';
  }
  function keepOnHtml(tile) {
    return '<div class="group"><div class="list"><div class="item"><div class="grow"><div>' + esc(t("keepOn")) + '</div><div class="hint" style="text-align:left;margin:2px 0 0">' + esc(t("keepOnHint")) + "</div></div>" +
      '<button class="tg' + (tile.keep_on ? "" : " off") + '" data-keepon="' + esc(tile.id) + '" aria-label="' + esc(t("keepOn")) + '"></button></div></div></div>';
  }
  function keepOnListHtml() {
    var ids = Object.keys(S.tiles).filter(function (id) { var tl = S.tiles[id]; return tl.kind === "switch" || tl.kind === "outlet" || tl.keep_on; });
    if (!ids.length) { return ""; }
    ids.sort(function (a, b) { var ka = S.tiles[a].keep_on ? 0 : 1, kb = S.tiles[b].keep_on ? 0 : 1; return ka - kb || S.tiles[a].name.localeCompare(S.tiles[b].name); });
    // long lists: the ones left on first, the rest on request
    var all = ids.length, more = !S.sheet.all && all > 6 ? '<button class="linkbtn" data-showall="1">' + esc(t("showAll", { n: all })) + "</button>" : "";
    if (more) { ids = ids.slice(0, 6); }
    return '<div class="group"><div class="label">' + esc(t("keepOnList")) + '</div><div class="hint" style="text-align:left;margin:0 0 6px">' + esc(t("keepOnHint")) + '</div><div class="list">' + ids.map(function (id) {
      var tl = S.tiles[id];
      return '<div class="item"><span class="grow">' + esc(tl.name) + '<span style="color:var(--mu)"> · ' + esc(tl.rooms[0] || "") + '</span></span><button class="tg' + (tl.keep_on ? "" : " off") + '" data-keepon="' + esc(id) + '"></button></div>';
    }).join("") + "</div>" + more + "</div>";
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
      if (tl.kind === "light" || tl.kind === "dimmer") { g.light.push(id); } else if ((tl.kind === "switch" || tl.kind === "outlet") && !tl.measure) { g.switch.push(id); } else if (tl.kind === "blind") { g.blind.push(id); } else if (tl.kind === "thermostat" && (!g.climate || g.climate.kind !== "thermostat")) { if (g.climate) { g.more.push(g.climate.id); } g.climate = tl; } else if (tl.kind === "temperature" && !g.climate) { g.climate = tl; } else { g.more.push(id); }
    });
    return g;
  }
  var RING_SWEEP = 270;
  // the thermostat really heats: valve open or "heating", else a guess
  function heats(tl) {
    var st = (tl && tl.state) || {};
    if (st.heating !== undefined) { return !!st.heating; }
    return st.target !== undefined && st.current !== undefined && st.target > st.current + 0.3;
  }
  // the ring shows the useful part of the range: no 4.5 (off) or 30.5 (on)
  function ringLo(tl) { return Math.max(5, Math.min(15, tl && tl.min !== undefined ? tl.min : 10)); }
  function ringHi(tl) { return Math.min(30, Math.max(ringLo(tl) + 5, tl && tl.max !== undefined ? tl.max : 28)); }
  function ringPoint(frac, r, c) {
    var a = (135 + frac * RING_SWEEP) * Math.PI / 180;
    return [c + r * Math.cos(a), c + r * Math.sin(a)];
  }
  function ringArc(f0, f1, r, c) {
    var p0 = ringPoint(f0, r, c), p1 = ringPoint(f1, r, c), large = (f1 - f0) * RING_SWEEP > 180 ? 1 : 0;
    return "M" + p0[0].toFixed(1) + " " + p0[1].toFixed(1) + " A" + r + " " + r + " 0 " + large + " 1 " + p1[0].toFixed(1) + " " + p1[1].toFixed(1);
  }
  function ringFrac(v, tl) { var lo = ringLo(tl), hi = ringHi(tl); return Math.max(0, Math.min(1, (v - lo) / (hi - lo))); }
  function climateHtml(tl) {
    var st = tl.state;
    if (tl.kind !== "thermostat") {
      var cv = st.temperature;
      return '<div class="pclimate"><div class="pbig" style="color:' + tempColor(cv) + '">' + num(cv) + '°</div><div class="pctext">' + (st.humidity !== undefined ? "<b>" + Math.round(st.humidity) + " %</b><span>" + esc(t("humidity")) + "</span>" : "") + "</div></div>";
    }
    var cur = st.current, target = st.target, heating = heats(tl), color = heating ? "#FF8A3D" : tempColor(cur);
    var c = 90, r = 72, ft = ringFrac(target === undefined ? ringLo(tl) : target, tl), knob = ringPoint(ft, r, c);
    var valve = st.valve !== undefined ? (st.valve > 0 ? t("valveOpen", { n: Math.round(st.valve) }) : t("valveShut")) : "";
    var svg = '<svg viewBox="0 0 180 180" class="ringsvg"><path d="' + ringArc(0, 1, r, c) + '" class="rtrack"/>' +
      (target !== undefined ? '<path d="' + ringArc(0, Math.max(ft, 0.002), r, c) + '" class="rfill" style="stroke:' + color + '"/><circle cx="' + knob[0].toFixed(1) + '" cy="' + knob[1].toFixed(1) + '" r="11" class="rknob"/>' : "") + "</svg>";
    var side = heating ? '<div class="pcs"><b>' + I("flame", 18) + " " + esc(t("rpHeatsNow")) + "</b><span>" + esc(valve || t("rpHoldRing")) + "</span></div>" : st.heating === false && target !== undefined && cur !== undefined && target > cur + 0.3 ? '<div class="pcs"><b>' + esc(t("rpSetTo", { t: num(target) })) + "</b><span>" + esc([t("idleNow"), valve].filter(Boolean).join(" · ")) + "</span></div>" : '<div class="pcs"><b>' + esc(cur !== undefined && target !== undefined && Math.abs(cur - target) <= 0.3 ? t("rpReached") : t("rpSetTo", { t: num(target) })) + "</b><span>" + esc(t("rpHoldRing")) + "</span></div>";
    return '<div class="pclimate"><div class="ring" data-ring="' + esc(tl.id) + '">' + svg + '<div class="rval"><b style="color:' + tempColor(cur) + '">' + (cur !== undefined ? num(cur) + "°" : "–") + "</b><span>" + esc(t("rpSetTo", { t: num(target) })) + "</span></div></div>" +
      '<div class="pcside' + (heating ? " heats" : "") + '">' + side + '<div class="target small"><button class="round" data-step="-1" data-sid="' + esc(tl.id) + '">−</button><button class="round" data-step="1" data-sid="' + esc(tl.id) + '">+</button></div>' +
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
        return '<div class="prow"><button class="pic' + (tl.state.on ? (key === "light" ? " lit" : " pow") : "") + '" ' + (ro || tl.measure ? 'data-pdetail="' : 'data-ptoggle="') + esc(tl.id) + '">' + I(key === "light" ? "bulb" : tl.kind === "outlet" ? "plug" : "power", 18) + '</button><div class="pn" data-pdetail="' + esc(tl.id) + '">' + esc(tl.name) + "<span>" + esc(tileLook(tl).sub) + "</span></div>" +
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
      var lo = ringLo(tile), hi = ringHi(tile), before = value;
      value = Math.round((lo + rel / RING_SWEEP * (hi - lo)) / step) * step;
      value = Math.round(value * 10) / 10;
      if (value !== before && navigator.vibrate) { try { navigator.vibrate(4); } catch (err) { /* not allowed */ } }
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
  // ---------- energy over days ----------
  function openEnergy(span) {
    var keep = S.sheet && S.sheet.energy ? S.sheet : null;
    S.sheet = { energy: true, range: span || (keep && keep.range) || "day", data: keep && keep.range === span ? keep.data : null, editPrice: keep && keep.editPrice };
    renderSheet(); loadEnergy();
  }
  function loadEnergy() {
    var sh = S.sheet; if (!sh || !sh.energy) { return; }
    var span = sh.range;
    api("api/energy?range=" + span).then(function (data) {
      if (S.sheet && S.sheet.energy && S.sheet.range === span) { S.sheet.data = data; S.sheet.at = Date.now(); renderSheet(); }
    }).catch(function () {
      if (S.sheet && S.sheet.energy && S.sheet.range === span) { S.sheet.data = { error: "failed" }; renderSheet(); }
    });
  }
  function kwh(v) {
    if (!has(v)) { return "–"; }
    return (v >= 100 ? num(v, 0) : v >= 10 ? num(v, 1) : num(v, 2)) + " kWh";
  }
  function euro(v) { return has(v) ? num(v, 2) + " €" : "–"; }
  function energyBarLabel(at, span, i) {
    var d = new Date(at * 1000);
    if (span === "day") { return i % 6 === 0 ? two(d.getHours()) : ""; }
    if (span === "week") { return d.toLocaleDateString(GERMAN ? "de-DE" : "en-GB", { weekday: "short" }).slice(0, 2); }
    return i % 5 === 0 || i === 29 ? String(d.getDate()) : "";
  }
  function energySvg(data, span) {
    var bars = data.bars || [], max = 0;
    bars.forEach(function (b) { max = Math.max(max, b.load || 0, b.solar || 0, b.import || 0); });
    if (!max) { return ""; }
    var w = 640, h = 150, base = 146, axis = "", n = bars.length, slot = w / n, bw = Math.max(2, slot * (data.solarShown ? 0.36 : 0.62));
    var out = '<svg class="enchart" viewBox="0 0 ' + w + " " + h + '" preserveAspectRatio="none">';
    var now = Date.now() / 1000;
    bars.forEach(function (b, i) {
      var x = i * slot + slot / 2, use = has(b.load) ? b.load : b.import;
      if (has(use)) {
        var uh = use / max * (base - 10);
        out += '<rect class="enuse" x="' + (x - (data.solarShown ? bw : bw / 2)).toFixed(1) + '" y="' + (base - uh).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(uh, 0).toFixed(1) + '" rx="2"/>';
      }
      if (data.solarShown && has(b.solar)) {
        var sh = b.solar / max * (base - 10);
        out += '<rect class="ensol" x="' + x.toFixed(1) + '" y="' + (base - sh).toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(sh, 0).toFixed(1) + '" rx="2"/>';
      }
      var label = energyBarLabel(b.at, span, i);
      if (label) { axis += '<span style="left:' + (x / w * 100).toFixed(2) + '%">' + esc(label) + "</span>"; }
      if (span === "day" && b.at <= now && now < b.at + 3600) { out += '<line class="ennow" x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="4" y2="' + base + '"/>'; }
    });
    // labels outside of the stretched svg, so they keep their shape
    return '<div class="enwrap">' + out + '<line class="enbase" x1="0" x2="' + w + '" y1="' + base + '" y2="' + base + '"/></svg><div class="enaxis">' + axis + "</div></div>";
  }
  function energyPriceHtml(data, sh) {
    if (S.tablet && S.tablet.readonly) { return ""; }
    if (data.price === "reading" && !sh.editPrice) {
      return '<div class="enprice">' + I("bolt", 18) + "<span>" + esc(t("enPriceReading")) + "</span></div>";
    }
    var value = data.price_attr || "", parts = value.split(",");
    if (value && !sh.editPrice) {
      return '<div class="enprice">' + I("bolt", 18) + "<span>" + esc(t("enPrice")) + " <b>" + esc(num(parseFloat(parts[0]), 2)) + " €/kWh</b>" + (parts[1] ? " · " + esc(t("enFeedInShort")) + " " + esc(num(parseFloat(parts[1]), 2)) + " €/kWh" : "") +
        '</span><button class="pill" data-enprice="edit">' + esc(t("enPriceEdit")) + "</button></div>";
    }
    var fmt = function (v) { return v ? (GERMAN ? v.replace(".", ",") : v) : ""; };
    return '<div class="section">' + esc(t("enPrice")) + '</div><div class="lead">' + esc(t("enPriceLead")) + '</div><div class="enform">' +
      '<input id="enprice" inputmode="decimal" placeholder="0' + (GERMAN ? "," : ".") + '32" value="' + esc(fmt(parts[0])) + '">' +
      '<input id="enfeed" inputmode="decimal" placeholder="' + esc(t("enFeedIn")) + '" value="' + esc(fmt(parts[1])) + '">' +
      '<button class="pill" data-enprice="save">' + esc(t("enPriceSave")) + "</button></div>";
  }
  function renderEnergy() {
    var sh = S.sheet, span = sh.range, data = sh.data, body = "";
    body += '<div class="seg enseg">' + [["day", "enDay"], ["week", "enWeek"], ["month", "enMonth"]].map(function (r) {
      return '<button class="' + (r[0] === span ? "on" : "") + '" data-enrange="' + r[0] + '">' + esc(t(r[1])) + "</button>";
    }).join("") + "</div>";
    if (!data) {
      body += '<div class="lead">…</div>';
    } else if (data.error) {
      body += '<div class="lead">' + esc(data.error === "no timeline" ? t("enNoTimeline") : t("enEmpty")) + "</div>";
    } else {
      var tot = data.totals || {}, facts = [];
      data.solarShown = has(tot.solar);
      if (has(tot.solar)) { facts.push([kwh(tot.solar), t("enSolar"), "sol"]); }
      if (has(tot.load)) { facts.push([kwh(tot.load), t("enLoad"), "use"]); }
      if (has(tot.import)) { facts.push([kwh(tot.import), t("enImport"), ""]); }
      if (tot.export) { facts.push([kwh(tot.export), t("enExport"), ""]); }
      if (has(tot.autarky) && has(tot.solar)) { facts.push([tot.autarky + " %", t("enAutarky"), ""]); }
      if (has(tot.cost)) { facts.push([euro(tot.cost), t("enCost"), ""]); }
      if (tot.revenue) { facts.push([euro(tot.revenue), t("enRevenue"), ""]); }
      if (facts.length) {
        body += '<div class="facts2 enfacts">' + facts.map(function (f) { return '<div class="fact2' + (f[2] ? " en" + f[2] : "") + '"><b>' + esc(f[0]) + "</b><span>" + esc(f[1]) + "</span></div>"; }).join("") + "</div>";
      }
      var svg = energySvg(data, span);
      if (svg) {
        body += '<div class="section"><span>' + esc(t("enChart")) + '</span><span class="enlegend"><i class="use"></i>' + esc(t("enLoad")) + (data.solarShown ? ' <i class="sol"></i>' + esc(t("enSolar")) : "") + "</span></div>" + svg;
      }
      var top = data.consumers || [];
      if (top.length) {
        var most = top[0].kwh || 1;
        body += '<div class="section">' + esc(t("enTop")) + '</div><div class="lead">' + esc(t("enTopLead")) + '</div><div class="list entop">' + top.map(function (c) {
          return '<div class="item" data-tile="' + esc(c.id) + '"><span class="grow"><b>' + esc(c.name) + '</b><span class="enbar"><i style="width:' + Math.max(3, c.kwh / most * 100).toFixed(1) + '%"></i></span></span><span class="env"><b>' + esc(kwh(c.kwh)) + "</b>" + (has(c.cost) ? "<span>" + esc(euro(c.cost)) + "</span>" : "") + "</span></div>";
        }).join("") + "</div>";
      }
      if (!facts.length && !top.length) { body += '<div class="lead">' + esc(t("enEmpty")) + "</div>"; }
      body += energyPriceHtml(data, sh);
    }
    sheetShell('<div class="head"><div><h1>' + esc(t("enTitle")) + '</h1></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" + body, "ensheet");
  }
  function energyPriceClick(el) {
    var what = el.getAttribute("data-enprice");
    if (what === "edit") { S.sheet.editPrice = true; renderSheet(); return; }
    var price = (document.getElementById("enprice") || {}).value || "", feed = (document.getElementById("enfeed") || {}).value || "";
    send({ type: "energy_price", price: price.trim(), feed_in: feed.trim() });
    S.sheet.editPrice = false;
    setTimeout(loadEnergy, 600);
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
  // music players, speakers and TVs: off if they can be switched off, else paused when they play
  function mediaGoesOff(tile) {
    if (tile.kind !== "media") { return false; }
    return tile.media && tile.media.power ? !!tile.state.on : !!tile.state.playing;
  }
  // fans and the fans of ceiling lights
  function fanRuns(tile) {
    if (!tile.fan || tile.keep_on) { return false; }
    var st = tile.kind === "fan" ? tile.state : tile.state.fan || {};
    return (st.percent || 0) > 0;
  }
  // what the routine does: lights, switches, fans and music off, at night the blinds down
  function routinePlan(mode) {
    var all = shownTiles();
    var off = all.filter(function (x) { return (["light", "dimmer", "switch", "outlet"].indexOf(x.tile.kind) >= 0 && x.tile.state.on) || mediaGoesOff(x.tile) || fanRuns(x.tile); });
    var heat = mode === "away" ? hotSoon() : null, openBlinds = all.filter(function (x) { return x.tile.kind === "blind" && x.tile.state.position !== 0; });
    var blinds = mode === "night" || (heat && S.sheet && S.sheet.heatBlinds) ? openBlinds : [];
    // locks are locked when every door is closed, else they stay in the open list
    var doorOpen = all.some(function (x) { return x.tile.kind === "contact" && x.tile.door && x.tile.state.closed === false; });
    var locks = doorOpen ? [] : all.filter(function (x) { return x.tile.kind === "lock" && x.tile.state.locked === false; });
    var open = all.filter(function (x) { return secOpen(x.tile) && locks.indexOf(x) < 0; });
    // leaving home: robot vacuums which could clean now, only offered, never started by itself
    var vacuums = mode === "away" ? all.filter(function (x) { return x.tile.kind === "vacuum" && x.tile.view && x.tile.view.actions.indexOf("start") >= 0 && (!viewRunning(x.tile.state || {}) || (S.sheet && S.sheet.vacStarted && S.sheet.vacStarted[x.id])); }) : [];
    return { off: off, blinds: blinds, heat: heat && openBlinds.length ? { max: heat, blinds: openBlinds } : null, locks: locks, doorOpen: doorOpen, open: open, alarm: routineAlarm(mode), vacuums: vacuums };
  }
  function weatherWarn() {
    var w = S.header && S.header.weather, warn = w && w.warn;
    if (!warn) { return ""; }
    var windows = routinePlan("away").open.filter(function (x) { return x.tile.kind === "contact" && !x.tile.door; });
    if (!windows.length) { return ""; }
    return '<div class="rtwarn">' + I(warn.kind === "frost" ? "drop" : "rain", 22) + '<div class="t"><b>' + esc(t("warn" + warn.kind, { t: warn.at })) + "</b><span>" +
      esc(t("warnWindows", { names: windows.map(function (x) { return x.tile.name; }).join(", ") })) + "</span></div></div>";
  }
  // hot in the next hours (forecast or outside now): leaving home offers to close the blinds
  var HOT_C = 26, HOT_HOURS = 10;
  function hotSoon() {
    var w = S.header && S.header.weather; if (!w) { return null; }
    var temps = (w.hours || []).slice(0, HOT_HOURS).map(function (x) { return x.temp; }).concat([w.temperature]).filter(has);
    var max = temps.length ? Math.max.apply(null, temps) : null;
    return max !== null && max >= HOT_C ? max : null;
  }
  // the alarm system is armed too (home at night, away when leaving), one tap leaves it off
  function routineAlarm(mode) {
    var sys = alarmInfo().system, wanted = mode === "night" ? "home" : "away";
    if (!sys || sys.modes.indexOf(wanted) < 0 || sys.mode === wanted || sys.mode === "triggered") { return null; }
    return { name: sys.name, mode: wanted };
  }
  function rtAlarmOn() { return !(S.sheet && S.sheet.noAlarm); }
  // good night and leaving home start by themselves after this many seconds, unless stopped
  var RT_AUTO_S = 60, rtTimer = null;
  function routineOpen(mode) {
    var p = routinePlan(mode), offN = p.off.filter(function (x) { return !x.tile.keep_on; }).length;
    S.sheet = { routine: mode, autoAt: offN || p.blinds.length || p.locks.length || p.alarm ? Date.now() + RT_AUTO_S * 1000 : 0 };
    renderSheet();
    routineTick();
  }
  function routineLeft() { return Math.max(0, Math.ceil(((S.sheet && S.sheet.autoAt) - Date.now()) / 1000)); }
  function routineTick() {
    if (rtTimer) { clearTimeout(rtTimer); rtTimer = null; }
    if (!S.sheet || !S.sheet.routine || !S.sheet.autoAt) { return; }
    var left = routineLeft();
    if (left <= 0) { routineGo(S.sheet.routine); return; }
    var btn = document.querySelector("#sheet [data-rtgo]"), bar = document.querySelector("#sheet .rtbar i");
    if (btn) { var lbl = btn.querySelector(".lbl"); if (lbl) { lbl.textContent = t(S.sheet.routine === "night" ? "rtGoNightIn" : "rtGoIn", { n: left }); } }
    if (bar) { bar.style.width = Math.min(100, 100 * (1 - (S.sheet.autoAt - Date.now()) / (RT_AUTO_S * 1000))) + "%"; }
    rtTimer = setTimeout(routineTick, 250);
  }
  function renderRoutine() {
    var mode = S.sheet.routine, p = routinePlan(mode), body = "";
    var goes = p.off.filter(function (x) { return !x.tile.keep_on; }), stays = p.off.filter(function (x) { return x.tile.keep_on; });
    function section(text, cls) { return '<div class="section ovroom rtsec ' + (cls || "") + '">' + esc(text) + "</div>"; }
    // first and clearly marked: what is switched off
    if (goes.length) {
      body += section(t("rtSecOff", { n: goes.length }), "off");
      goes.forEach(function (x) {
        var media = x.tile.kind === "media", fan = x.tile.kind === "fan" || (fanRuns(x.tile) && !x.tile.state.on);
        body += ovRow(x, media ? "music" : fan ? "fan" : isLight(x.tile) ? "bulb" : "plug", media ? "#5AA9FF" : fan ? "#3DDBB8" : isLight(x.tile) ? "#FFB547" : "#9B8CFF", x.room, '<span class="rttag">' + I("power", 16) + " " + esc(t("rtOffTag")) + "</span>").replace('class="row tap"', 'class="row tap rtgoes"');
      });
    }
    if (p.heat && !p.blinds.length) {
      body += section(t("rtSecHeat", { t: num(p.heat.max, 0) })) + '<div class="row tap rtstays" data-rtheat="1"><div class="ic" style="background:#FF8A3D26;color:#FF8A3D">' + I("blind") + '</div><div class="t"><b>' + esc(p.heat.blinds.length === 1 ? t("rtBlind") : t("rtBlinds", { n: p.heat.blinds.length })) + "</b><span>" + esc(t("rtHeatOffer")) + '</span></div><span class="pill">' + esc(t("rtHeatClose")) + "</span></div>";
    }
    if (p.blinds.length) {
      var rooms = []; p.blinds.forEach(function (x) { if (rooms.indexOf(x.room) < 0) { rooms.push(x.room); } });
      body += section(t("rtSecClose"), "off") + '<div class="row rtgoes' + (p.heat ? ' tap" data-rtheat="1' : "") + '"><div class="ic" style="background:#3DDBB826;color:#3DDBB8">' + I("blind") + '</div><div class="t"><b>' + esc(p.blinds.length === 1 ? t("rtBlind") : t("rtBlinds", { n: p.blinds.length })) + "</b><span>" + esc(rooms.join(", ") + " · " + t("rtBlindsSub")) + "</span></div></div>";
    }
    if (p.locks.length) {
      body += section(t("rtSecLock", { n: p.locks.length }), "off");
      p.locks.forEach(function (x) { body += ovRow(x, "lock", "#34D399", [x.room, t("rtLocks")].join(" · "), '<span class="rttag">' + I("lock", 16) + " " + esc(t("rtLockTag")) + "</span>").replace('class="row tap"', 'class="row tap rtgoes"'); });
    }
    if (p.alarm) {
      var on = rtAlarmOn();
      body += section(t("rtSecAlarm"), on ? "off" : "stays") + '<div class="row tap ' + (on ? "rtgoes" : "rtstays") + '" data-rtalarm="1"><div class="ic" style="background:' + (on ? "#34D39926;color:#34D399" : "#8A93A626;color:#8A93A6") + '">' + I("shield") + '</div><div class="t"><b>' + esc(p.alarm.name) + "</b><span>" +
        esc(on ? alarmModeText(p.alarm.mode) + " · " + t("rtAlarmTap") : t("rtAlarmStays")) + "</span></div>" + (on ? '<span class="rttag">' + I("shield", 16) + " " + esc(t("rtAlarmTag")) + "</span>" : "") + "</div>";
    }
    if (p.vacuums.length) {
      body += section(t("rtSecVacuum"));
      p.vacuums.forEach(function (x) {
        var started = S.sheet.vacStarted && S.sheet.vacStarted[x.id];
        body += ovRow(x, "robot", "#5AA9FF", [x.room, viewLook(x.tile).sub].filter(Boolean).join(" · "), started ? '<span class="rttag">' + I("check", 16) + " " + esc(t("rtVacStarted")) + "</span>" : '<button class="pill" data-rtvac="' + esc(x.id) + '">' + esc(t("rtVacStart")) + "</button>");
      });
    }
    if (p.open.length) {
      body += section(t("rtSecOpen", { n: p.open.length }));
      p.open.forEach(function (x) {
        if (x.tile.kind === "lock") { body += ovRow(x, "unlock", "#FF8A3D", [x.room, t("unlocked"), p.doorOpen ? t("rtLockDoor") : ""].filter(Boolean).join(" · "), '<button class="pill" data-ovlock="' + esc(x.id) + '">' + esc(t("lock")) + "</button>"); return; }
        body += ovRow(x, x.tile.door ? "door" : "win", "#FF8A3D", [x.room, (x.tile.state.tilted ? t("tilted") : t("open")) + " " + since(x.tile.state.since)].join(" · "));
      });
    }
    if (stays.length) {
      body += section(t("rtSecStays", { n: stays.length }), "stays");
      stays.forEach(function (x) {
        body += ovRow(x, x.tile.kind === "media" ? "music" : isLight(x.tile) ? "bulb" : "plug", "#8A93A6", [x.room, t("staysOn")].join(" · ")).replace('class="row tap"', 'class="row tap rtstays"');
      });
    }
    var title = mode === "night" ? t("rtNight") : t("rtAway"), auto = S.sheet.autoAt ? routineLeft() : 0;
    var go = '<button class="pill primary' + (auto ? " rtauto" : "") + '" data-rtgo="' + mode + '">' + (auto ? '<span class="rtbar"><i></i></span>' : "") + I(mode === "night" ? "moon" : "walk", 20) + ' <span class="lbl">' + esc(auto ? t(mode === "night" ? "rtGoNightIn" : "rtGoIn", { n: auto }) : t(mode === "night" ? "rtGoNight" : "rtGoAway")) + "</span></button>";
    sheetShell('<div class="head"><div><h1>' + esc(title) + '</h1><div class="subtitle">' + esc(auto ? t("rtAutoHint", { n: RT_AUTO_S }) : body ? t(mode === "night" ? "rtNightLead" : "rtAwayLead") : "") + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      weatherWarn() + '<div class="blist ovlist">' + (body || '<div class="allclear">' + I("check", 26) + " " + esc(t("rtAllFine")) + "</div>") + "</div>" +
      '<div class="actions">' + (auto ? '<button class="pill" data-rtstop="1">' + esc(t("rtAutoStop")) + "</button>" : "") + go + "</div>");
  }
  function routineGo(mode) {
    if (rtTimer) { clearTimeout(rtTimer); rtTimer = null; }
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var p = routinePlan(mode);
    send({ type: "action", action: "routine", mode: mode, off: p.off.filter(function (x) { return !x.tile.keep_on; }).map(function (x) { return x.id; }), close: p.blinds.map(function (x) { return x.id; }), heat: mode === "away" && p.blinds.length > 0, lock: p.locks.map(function (x) { return x.id; }), alarm: p.alarm && rtAlarmOn() ? p.alarm.mode : null });
    closeSheet();
  }
  function routineDone(m) {
    var text = m.done ? t(m.mode === "night" ? "rtDoneNight" : "rtDoneAway", { n: m.done }) : t("rtDoneNone");
    if (m.alarm) { text += " " + t("asDone", { mode: alarmModeText(m.alarm) }); }
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

  // ---------- washing machine, dryer, dishwasher ----------
  var AP_NAME = { washer: "apWasher", dryer: "apDryer", dishwasher: "apDishwasher" };
  var AP_DONE = { washer: "apDoneWasher", dryer: "apDoneDryer", dishwasher: "apDoneDishwasher" };
  function minutesText(sec) { var m = Math.max(1, Math.round(sec / 60)); return m >= 60 ? Math.floor(m / 60) + " h " + (m % 60 ? (m % 60) + " min" : "") : m + " min"; }
  function appliancesHtml() {
    var a = (S.header && S.header.appliances) || {}, now = Date.now() / 1000, rows = "", ro = S.tablet && S.tablet.readonly;
    shownList(a.done).forEach(function (d) {
      rows += '<div class="row apdone"><div class="ic" style="background:#34D39926;color:#34D399">' + I("washer") + '</div><div class="t"><b>' + esc(t(AP_DONE[d.what])) + "</b><span>" +
        esc([d.name, t("apAgo", { t: minutesText(now - d.at) })].join(" · ")) + "</span></div>" + (ro ? "" : '<button class="pill" data-applseen="' + esc(d.id) + '">' + I("check", 18) + " " + esc(t("apSeen")) + "</button>") + "</div>";
    });
    shownList(a.running).forEach(function (r) {
      // end: predicted from the learned programs, typical: median of the last ones
      var ran = now - r.since, total = r.end ? r.end - r.since : r.typical, frac = total ? Math.min(0.97, ran / total) : null, left = total ? total - ran : null;
      // no power for a minute: a pause or the end, the time left is unsure
      var idle = r.idle && now - r.idle >= 60;
      var leftText = idle ? t("apIdle", { t: minutesText(now - r.idle) }) : r.new ? t("apNew") : left === null ? "" : left > 120 ? t("apLeft", { t: minutesText(left) }) + " · " + t("apEnd", { t: clockText(new Date((r.since + total) * 1000)) }) : t("apAlmost");
      rows += '<div class="row aprun"><div class="ic" style="background:#4DA3FF26;color:#4DA3FF">' + I("washer") + '</div><div class="t"><b>' + esc(t(AP_NAME[r.what])) + "</b><span>" +
        esc([t("apRuns", { t: minutesText(ran) }), leftText].filter(Boolean).join(" · ")) + "</span>" +
        (frac !== null ? '<div class="apbar"><i style="width:' + Math.round(frac * 100) + '%"></i></div>' : "") + "</div></div>";
    });
    if (!ro) {
      shownList(a.ask).forEach(function (q) {
        var order = ["washer", "dryer", "dishwasher"];
        if (q.guess) { order.splice(order.indexOf(q.guess), 1); order.unshift(q.guess); }
        rows += '<div class="apask"><div class="row"><div class="ic" style="background:#4DA3FF26;color:#4DA3FF">' + I("washer") + '</div><div class="t"><b>' + esc(t("apAsk", { name: q.name })) + "</b><span>" + esc(t("apAskLead")) + "</span></div></div>" +
          '<div class="actions">' + order.map(function (w, i) { return '<button class="pill' + (i === 0 && q.guess ? " primary" : "") + '" data-appl="' + esc(q.id) + "|" + w + '">' + esc(t(AP_NAME[w])) + "</button>"; }).join("") +
          '<button class="pill" data-appl="' + esc(q.id) + '|none">' + esc(t("apNone")) + "</button></div></div>";
      });
    }
    return rows ? '<div class="leave appl">' + rows + "</div>" : "";
  }
  var AP_BIG = { washer: "apBigWasher", dryer: "apBigDryer", dishwasher: "apBigDishwasher" };
  var AP_TIP = { washer: "apTipWasher", dryer: "apTipDryer", dishwasher: "apTipDishwasher" };
  var AP_SAY = { washer: "apSayWasher", dryer: "apSayDryer", dishwasher: "apSayDishwasher" };
  // the big message is shown this long, then the row on Zuhause stays
  var AP_ALERT_SECONDS = 600;
  function applianceDone(m) {
    wake(); chime();
    var shown = shownList([{ id: m.id }]).length;
    if (shown && layout().speak) { setTimeout(function () { say(t(AP_SAY[m.what] || "apSayWasher")); }, 1400); }
    checkApplianceAlert();
  }
  // done appliances of the last 10 minutes, not set to done yet
  function applianceAlerts() {
    var a = (S.header && S.header.appliances) || {}, now = Date.now() / 1000, gone = S.apClosed || {};
    return shownList(a.done).filter(function (d) { return now - d.at < AP_ALERT_SECONDS && !gone[d.id + ":" + d.at]; });
  }
  function checkApplianceAlert() {
    var list = applianceAlerts(), el = document.getElementById("apalert");
    clearTimeout(S.apTimer);
    if (!list.length) { if (el) { el.parentNode.removeChild(el); } return; }
    // hidden again after 10 minutes: one timer, no polling
    var now = Date.now() / 1000, next = Math.min.apply(null, list.map(function (d) { return d.at + AP_ALERT_SECONDS - now; }));
    S.apTimer = setTimeout(checkApplianceAlert, Math.max(1, next) * 1000 + 200);
    var key = list.map(function (d) { return d.id + ":" + d.at; }).join(",");
    if (!el) { el = document.createElement("div"); el.id = "apalert"; el.className = "apfull"; document.body.appendChild(el); wake(); }
    else if (el.getAttribute("data-key") === key) { updateApplianceAgo(el, list); return; }
    el.setAttribute("data-key", key);
    var ro = S.tablet && S.tablet.readonly, one = list[0], known = ((S.header.appliances || {}).known) || [];
    var byOf = function (id) { var k = known.filter(function (x) { return x.id === id; })[0]; return k && k.by ? k.by_name : ""; };
    var title = list.length === 1 ? t(AP_BIG[one.what] || "apBigWasher") : t("apBigMany", { n: list.length });
    var arts = list.slice(0, 3).map(function (d) { return '<div class="apart">' + applianceArt(d.what) + "</div>"; }).join("");
    var rows = list.map(function (d) {
      return '<div class="aprow"><b>' + esc(t(AP_NAME[d.what] || "apWasher")) + '</b><span data-apago="' + esc(String(d.at)) + '">' + esc([d.name, d.room, agoText(d.at)].filter(Boolean).join(" · ")) + "</span></div>";
    }).join("");
    var bys = list.map(function (d) { return byOf(d.id); }).filter(Boolean);
    var tip = list.length === 1 ? t(AP_TIP[one.what] || "apTipWasher") : "";
    el.innerHTML = '<div class="apin"><div class="aparts n' + Math.min(3, list.length) + '">' + arts + "</div><h1>" + esc(title) + "</h1>" +
      (tip ? '<div class="aptip">' + esc(tip) + "</div>" : "") + '<div class="aplist">' + rows + "</div>" +
      '<button class="apbtn" data-apdone="' + esc(list.map(function (d) { return d.id + ":" + d.at; }).join(",")) + '">' + I("check", 34) + " " + esc(t(ro ? "apClose" : "apSeen")) + "</button>" +
      (bys.length ? '<div class="apby">' + esc(t("apByTip", { name: bys.join(", ") })) + "</div>" : "") + "</div>";
  }
  function agoText(at) { var s = Date.now() / 1000 - at; return s < 60 ? t("apDoneNow") : t("apAgo", { t: minutesText(s) }); }
  function updateApplianceAgo(el, list) {
    list.forEach(function (d) {
      var span = el.querySelector('[data-apago="' + d.at + '"]');
      if (span) { span.textContent = [d.name, d.room, agoText(d.at)].filter(Boolean).join(" · "); }
    });
  }
  function applianceAlertDone(keys) {
    var ro = S.tablet && S.tablet.readonly; S.apClosed = S.apClosed || {};
    keys.split(",").forEach(function (k) {
      S.apClosed[k] = true;
      if (!ro) { send({ type: "appliance_seen", id: k.slice(0, k.lastIndexOf(":")) }); }
    });
    if (window.speechSynthesis) { try { speechSynthesis.cancel(); } catch (e) { /* nothing to stop */ } }
    checkApplianceAlert();
  }
  // a washing machine, dryer or dishwasher which is done: drawn, no image files
  function applianceArt(what) {
    var body = '<rect x="38" y="18" width="144" height="184" rx="24" fill="url(#apBody)"/><rect x="38" y="18" width="144" height="40" rx="24" fill="#dfe6ee"/><rect x="38" y="44" width="144" height="14" fill="#dfe6ee"/>' +
      '<rect x="54" y="32" width="38" height="12" rx="6" fill="#4DA3FF" opacity=".85"/><circle cx="160" cy="38" r="9" fill="#c4ceda"/><circle cx="160" cy="38" r="3" fill="#8b97a7"/><circle cx="136" cy="38" r="5" fill="#c4ceda"/>';
    var inner;
    if (what === "dishwasher") {
      inner = '<rect x="50" y="68" width="120" height="122" rx="14" fill="#d3dbe5"/><rect x="66" y="78" width="88" height="8" rx="4" fill="#aeb9c7"/>' +
        '<g class="applate"><circle cx="86" cy="138" r="30" fill="#fff" stroke="#c9d3df" stroke-width="3"/><circle cx="86" cy="138" r="18" fill="none" stroke="#e3e9f0" stroke-width="3"/></g>' +
        '<g class="applate p2"><path d="M128 112h26l-4 46a9 9 0 0 1-9 8h0a9 9 0 0 1-9-8z" fill="#cfe8ff" stroke="#9fc7ee" stroke-width="3"/><path d="M141 166v14M132 182h18" stroke="#9fc7ee" stroke-width="3" stroke-linecap="round"/></g>';
    } else {
      var drum = what === "dryer" ? "url(#apWarm)" : "url(#apWater)";
      inner = '<circle cx="110" cy="128" r="56" fill="#c9d3df"/><circle cx="110" cy="128" r="46" fill="#eef3f8"/>' +
        '<clipPath id="apDrum"><circle cx="110" cy="128" r="40"/></clipPath><g clip-path="url(#apDrum)"><rect x="60" y="80" width="100" height="100" fill="' + drum + '"/>' +
        (what === "dryer"
          ? '<g class="apswirl"><path d="M110 98c22 0 30 22 16 32s-30-4-22-16 26-2 22 14" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".75"/></g>'
          : '<path class="apwave" d="M40 130q15-10 30 0t30 0 30 0 30 0 30 0 30 0v60H40z" fill="#4DA3FF" opacity=".55"/><circle class="apbub" cx="96" cy="160" r="5" fill="#fff" opacity=".8"/><circle class="apbub b2" cx="122" cy="166" r="4" fill="#fff" opacity=".8"/><circle class="apbub b3" cx="110" cy="170" r="3" fill="#fff" opacity=".8"/>') +
        "</g>" + '<path d="M78 106a40 40 0 0 1 22-14" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none" opacity=".8"/>';
    }
    var spark = function (x, y, r, c) { return '<path class="apspark' + c + '" d="M' + x + " " + (y - r) + "Q" + x + " " + y + " " + (x + r) + " " + y + "Q" + x + " " + y + " " + x + " " + (y + r) + "Q" + x + " " + y + " " + (x - r) + " " + y + "Q" + x + " " + y + " " + x + " " + (y - r) + 'z" fill="#FFD66B"/>'; };
    return '<svg viewBox="0 0 220 230" aria-hidden="true"><defs><linearGradient id="apBody" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f9fc"/><stop offset="1" stop-color="#e4eaf1"/></linearGradient>' +
      '<linearGradient id="apWater" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6f3ff"/><stop offset="1" stop-color="#a9d4ff"/></linearGradient>' +
      '<linearGradient id="apWarm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe2b8"/><stop offset="1" stop-color="#ffb37a"/></linearGradient></defs>' +
      '<ellipse cx="110" cy="214" rx="78" ry="9" fill="#000" opacity=".18"/>' + body + inner +
      spark(24, 46, 12, "") + spark(200, 86, 9, " s2") + spark(30, 150, 7, " s3") +
      '<g class="apcheck"><circle cx="176" cy="186" r="28" fill="#34D399" stroke="#fff" stroke-width="5"/><path d="M163 186l9 9 17-18" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g></svg>';
  }
  // ---------- speech: the voice of the browser ----------
  function canSpeak() { return !!(window.speechSynthesis && window.SpeechSynthesisUtterance); }
  function say(text) {
    if (!canSpeak()) { return; }
    try {
      var u = new SpeechSynthesisUtterance(text), lang = (LANG && LANG.locale) || ({ de: "de-DE", en: "en-GB" }[LANG_CODE] || LANG_CODE);
      var nav = navigator.language || "";
      if (nav.slice(0, 2).toLowerCase() === LANG_CODE) { lang = nav; }
      u.lang = lang;
      var voices = speechSynthesis.getVoices() || [], exact = voices.filter(function (v) { return v.lang === lang || v.lang.replace("_", "-") === lang; });
      var same = exact.length ? exact : voices.filter(function (v) { return v.lang.slice(0, 2).toLowerCase() === LANG_CODE; });
      if (same.length) { u.voice = same.filter(function (v) { return v.localService; })[0] || same[0]; }
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) { /* no voice */ }
  }
  function speakRowHtml(lay) {
    if (!canSpeak()) { return '<div class="mrow"><span class="mic">' + I("speaker", 20) + '</span><span class="ml"><b>' + esc(t("speak")) + "</b><span>" + esc(t("speakNone")) + "</span></span></div>"; }
    return '<div class="mrow"><span class="mic">' + I("speaker", 20) + '</span><span class="ml"><b>' + esc(t("speak")) + "</b><span>" + esc(t("speakLead")) + '</span></span><div class="seg"><button class="' + (lay.speak ? "" : "on") + '" data-speak="0">' + esc(t("off")) + '</button><button class="' + (lay.speak ? "on" : "") + '" data-speak="1">' + esc(t("on")) + "</button></div>" +
      '<button class="pill" data-speaktest="1">' + esc(t("speakTest")) + "</button></div>";
  }
  // ---------- settings: which device sets an appliance to done ----------
  function renderAppliances() {
    var known = ((S.header && S.header.appliances) || {}).known || [];
    var rows = known.map(function (k) {
      var tl = S.tiles[k.id], room = k.room, ids = Object.keys(S.tiles).filter(function (id) { return id !== k.id; });
      var byName = function (a, b) { return S.tiles[a].name.localeCompare(S.tiles[b].name); };
      var suggest = ids.filter(function (id) { var x = S.tiles[id]; return (x.kind === "contact" || x.kind === "motion") && room && (x.rooms || []).indexOf(room) >= 0; }).sort(byName);
      var sensors = ids.filter(function (id) { var x = S.tiles[id]; return (x.kind === "contact" || x.kind === "motion") && suggest.indexOf(id) < 0; }).sort(byName);
      var opt = function (id) { var x = S.tiles[id]; return '<option value="' + esc(id) + '"' + (id === k.by ? " selected" : "") + ">" + esc(x.name + ((x.rooms || [])[0] ? " · " + x.rooms[0] : "")) + "</option>"; };
      var group = function (label, list) { return list.length ? '<optgroup label="' + esc(label) + '">' + list.map(opt).join("") + "</optgroup>" : ""; };
      var listed = suggest.concat(sensors);
      var others = ids.filter(function (id) { return listed.indexOf(id) < 0; }).sort(byName);
      var missing = k.by && !S.tiles[k.by] ? '<option value="' + esc(k.by) + '" selected>' + esc(k.by_name || k.by) + "</option>" : "";
      return '<div class="item apset"><span class="mic">' + I("washer", 20) + '</span><div class="grow"><b>' + esc(t(AP_NAME[k.what] || "apWasher")) + "</b><span>" + esc([tl ? tl.name : k.name, room].filter(Boolean).join(" · ")) + "</span>" +
        '<label class="aplabel">' + esc(t("apBy")) + '<select data-apby="' + esc(k.id) + '"><option value="">' + esc(t("apByNone")) + "</option>" + missing +
        group(t("apBySuggest"), suggest) + group(t("apBySensors"), sensors) + group(t("apByOther"), others) + "</select></label></div></div>";
    }).join("");
    sheetShell(settingsHead(t("apSettings"), t("setHome"), true) + '<div class="hint" style="text-align:left;margin:4px 0 16px">' + esc(t("apSettingsLead")) + "</div>" +
      (rows ? '<div class="group"><div class="list">' + rows + "</div></div>" : '<div class="group"><div class="hint" style="text-align:left">' + esc(t("apNoKnown")) + "</div></div>"));
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
  function secOpen(tl) { return (tl.kind === "contact" && tl.state.closed === false && !mayOpenNow(tl.may_open)) || (tl.kind === "lock" && tl.state.locked === false); }
  // ---------- doors and gates which may be open at some times ----------
  function mayOpenNow(win) {
    var m = /^(\d\d):(\d\d)-(\d\d):(\d\d)$/.exec(win || ""); if (!m) { return false; }
    var now = S.now || new Date(), n = now.getHours() * 60 + now.getMinutes(), a = +m[1] * 60 + +m[2], b = +m[3] * 60 + +m[4];
    return a < b ? n >= a && n < b : n >= a || n < b;
  }
  function warnOpen(list) { return shownList(list).filter(function (o) { return !mayOpenNow(o.may_open); }); }
  function mayOpenHtml(tile) {
    var on = !!tile.may_open, parts = (tile.may_open || "07:00-20:00").split("-");
    return '<div class="group ntedit"><div class="list"><div class="item"><div class="grow"><div>' + esc(t("moTitle")) + '</div><div class="hint" style="text-align:left;margin:2px 0 0">' + esc(t("moHint")) + "</div></div>" +
      '<button class="tg' + (on ? "" : " off") + '" data-mayopen="' + esc(tile.id) + '" aria-label="' + esc(t("moTitle")) + '"></button></div>' +
      (on ? '<div class="item ntrow"><span>' + esc(t("moFrom")) + '</span><input type="time" id="mofrom" value="' + esc(parts[0]) + '"><span>' + esc(t("moTo")) + '</span><input type="time" id="moto" value="' + esc(parts[1] === "24:00" ? "23:59" : parts[1]) + '"><button class="pill" data-mayopensave="' + esc(tile.id) + '">' + esc(t("ntSave")) + "</button></div>" : "") + "</div></div>";
  }
  function sendMayOpen(id, on) {
    if (!pinOk()) { askPin(null); return; }
    var from = document.getElementById("mofrom"), to = document.getElementById("moto");
    var win = !on ? "" : from && to && from.value && to.value ? from.value + "-" + to.value : "07:00-20:00";
    send({ type: "may_open", id: id, window: win });
  }
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
      c.heats = c.thermostat ? heats(S.tiles[c.thermostat]) : false;
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
    var sec = all.filter(function (x) { return SEC_KINDS[x.tile.kind]; }), sys = alarmInfo().system;
    if (sec.length || sys) {
      var open = sec.filter(function (x) { return secOpen(x.tile); }).length, alarms = alarmList().length;
      chips += chip("security", sys ? "shield" : "lock", alarms ? "alarm" : open ? "warn" : "", t("chSecurity"), alarms ? t("alAlarm") + "!" : open ? t("chSecOpen", { n: open }) : sys && sys.mode ? alarmModeText(sys.mode) : t("chSecOk"));
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
      // what heats right now comes first and stands out, like with good night
      var climates = roomClimates(), heating = climates.filter(function (c) { return c.heats; }), rest = climates.filter(function (c) { return !c.heats; });
      title = t("ovClimate"); lead = heating.length ? (heating.length === 1 ? t("chOneHeat") : t("chNHeat", { n: heating.length })) : "";
      if (heating.length) {
        body += '<div class="section ovroom rtsec heat"><span>' + I("flame", 18) + " " + esc(t("ovHeatNow", { n: heating.length })) + "</span></div>";
        body += heating.map(function (c) {
          var tl = S.tiles[c.thermostat], sub = [];
          if (tl && tl.name && tl.name !== c.room) { sub.push(tl.name); }
          if (c.target !== undefined) { sub.push(t("target") + " " + num(c.target) + "°"); }
          return '<div class="row tap ovheat" data-ovopen="' + esc(c.id) + '"><div class="ic">' + I("flame") + '</div><div class="t"><b>' + esc(c.room) + "</b><span>" + esc(sub.join(" · ")) + '</span></div><div class="ovtemp">' + num(c.temp) + "°</div>" + I("chev") + "</div>";
        }).join("");
        if (rest.length) { body += '<div class="section ovroom rtsec stays">' + esc(t("ovOtherRooms")) + "</div>"; }
      }
      body += rest.map(function (c) {
        var color = tempColor(c.temp), sub = [];
        if (c.target !== undefined) { sub.push(t("target") + " " + num(c.target) + "°"); }
        if (c.humidity !== undefined) { sub.push(Math.round(c.humidity) + " %"); }
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
      var sec = all.filter(function (x) { return secOpen(x.tile); }), detectors = all.filter(function (x) { return x.tile.kind === "smoke" || x.tile.kind === "water"; });
      var loud = detectors.filter(function (x) { return x.tile.state.alarm; });
      title = alarmInfo().system || detectors.length ? t("chSecurity") : t("ovSecurity");
      body = alarmSystemHtml(ro);
      if (loud.length) {
        body += byRoom(loud, function (x) { return ovRow(x, KIND_ICON[x.tile.kind], "#FF5A5F", t(x.tile.kind + "Now") + " " + since(x.tile.state.since)); });
      } else if (detectors.length) {
        body += '<div class="row"><div class="ic" style="background:#34D39926;color:#34D399">' + I("smoke") + '</div><div class="t"><b>' + esc(t("alDetectors")) + "</b><span>" + esc(t("alAllCalm", { n: detectors.length })) + "</span></div></div>";
      }
      body += sec.length ? byRoom(sec, function (x) {
        if (x.tile.kind === "lock") { return ovRow(x, "unlock", "#FF8A3D", t("unlocked"), ro ? "" : '<button class="pill" data-ovlock="' + esc(x.id) + '">' + esc(t("lock")) + "</button>"); }
        return ovRow(x, x.tile.door ? "door" : "win", "#FF8A3D", (x.tile.state.tilted ? t("tilted") : t("open")) + " " + since(x.tile.state.since));
      }) : '<div class="allclear">' + I("check", 26) + " " + esc(t("ovSecOk")) + "</div>";
      var allowed = all.filter(function (x) { return x.tile.kind === "contact" && x.tile.state.closed === false && mayOpenNow(x.tile.may_open); });
      if (allowed.length) {
        body += '<div class="section"><span>' + esc(t("moAllowed")) + "</span></div>" + byRoom(allowed, function (x) { return ovRow(x, x.tile.door ? "door" : "win", "#8E8E93", t("open") + " " + since(x.tile.state.since) + " · " + t("moUntil", { t: x.tile.may_open.split("-")[1] })); });
      }
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
  function openSettings() {
    if (!pinOk()) { askPin(openSettings); return; }
    S.sheet = { settings: true }; renderSettings();
    // devices without a room or idle: only tablets which arrange rooms
    if (S.tablet && S.tablet.arrange) { send({ type: "rooms_setup" }); }
  }

  // ---------- own notices, e.g. "Mail is here" ----------
  function noticesHtml() {
    var list = (S.header && S.header.notices) || [], ro = S.tablet && S.tablet.readonly;
    if (!list.length) { return ""; }
    return '<div class="notices">' + list.map(function (n) {
      return '<div class="notice"><div class="ic">' + I("bell", 22) + '</div><div class="t"><b>' + esc(n.text) + "</b><span>" + esc([n.room, since(n.since)].filter(Boolean).join(" · ")) + "</span></div>" +
        (ro ? "" : '<button class="round sm" data-noticedone="' + esc(n.id) + '" aria-label="' + esc(t("ntDone")) + '">' + I("check", 20) + "</button>") + "</div>";
    }).join("") + "</div>";
  }
  // a new notice chimes once on every tablet
  function checkNotices() {
    var ids = ((S.header && S.header.notices) || []).map(function (n) { return n.id + "|" + n.since; });
    if (S.noticeIds && ids.some(function (i) { return S.noticeIds.indexOf(i) < 0; })) { wake(); chime(); }
    S.noticeIds = ids;
  }
  function noticeEditHtml(tile) {
    var setup = (S.header && S.header.notice_setup) || {}, on = Object.prototype.hasOwnProperty.call(setup, tile.id);
    return '<div class="group ntedit"><div class="list"><div class="item"><div class="grow"><div>' + esc(t("ntTitle")) + '</div><div class="hint" style="text-align:left;margin:2px 0 0">' + esc(t("ntHint")) + "</div></div>" +
      '<button class="tg' + (on ? "" : " off") + '" data-notice="' + esc(tile.id) + '" aria-label="' + esc(t("ntTitle")) + '"></button></div>' +
      (on ? '<div class="item ntrow"><input id="nttext" maxlength="80" placeholder="' + esc(t("ntText")) + '" value="' + esc(setup[tile.id] || "") + '"><button class="pill" data-noticesave="' + esc(tile.id) + '">' + esc(t("ntSave")) + "</button></div>" : "") + "</div></div>";
  }
  function sendNotice(id, on) {
    if (!pinOk()) { askPin(null); return; }
    var input = document.getElementById("nttext"), text = input ? input.value : "";
    if (on && !input) { text = S.tiles[id] ? S.tiles[id].name : ""; }
    send({ type: "notice", id: id, on: on, text: text });
  }
  // ---------- smoke, water and the alarm system ----------
  var SEC_KINDS = { contact: 1, lock: 1, smoke: 1, water: 1 };
  function alarmInfo() { return (S.header && S.header.alarm) || { system: null, alarms: [] }; }
  function alarmList() { return alarmInfo().alarms || []; }
  function alarmModeText(mode) { return t({ off: "asOff", home: "asHome", away: "asAway", triggered: "asTriggered" }[mode] || "asOff"); }
  function alarmSystemHtml(ro) {
    var sys = alarmInfo().system; if (!sys) { return ""; }
    var color = sys.mode === "triggered" ? "#FF5A5F" : sys.mode === "off" || !sys.mode ? "#8C95A5" : "#34D399";
    var buttons = ro ? "" : sys.modes.filter(function (m) { return m !== sys.mode; }).map(function (m) {
      return '<button class="pill' + (m === "off" ? "" : " primary") + '" data-alarmmode="' + m + '">' + esc(t({ off: "asGoOff", home: "asGoHome", away: "asGoAway" }[m])) + "</button>";
    }).join("");
    return '<div class="row alsys"><div class="ic" style="background:' + color + "26;color:" + color + '">' + I("shield") + '</div><div class="t"><b>' + esc(sys.name) + "</b><span>" + esc([alarmModeText(sys.mode), since(sys.since)].filter(Boolean).join(" · ")) + "</span></div></div>" +
      (buttons ? '<div class="actions alsysb">' + buttons + "</div>" : "");
  }
  function alarmMode(el, mode) {
    if (S.tablet && S.tablet.readonly) { showBanner(t("readonly"), 3000); return; }
    var sys = alarmInfo().system; if (!sys) { return; }
    if (mode === "off" && sys.pin) {
      S.pinReturn = S.sheet && S.sheet.pin === undefined ? S.sheet : null; S.afterPin = null;
      S.sheet = { pin: "", error: "", alarm: mode }; renderSheet();
      if (alarmList().length) { S.alarmHidden = true; renderAlarm(); }
      return;
    }
    if (mode === "off" && el && !armed(el, "alarm:off", t("asSure"))) { return; }
    send({ type: "action", action: "alarm_mode", mode: mode });
  }
  function alarmModeAnswer(m) {
    var p = S.sheet;
    if (p && p.alarm) {
      if (m.wrong) { S.sheet = { pin: "", error: t(m.wait ? "pinWait" : "pinWrong"), alarm: p.alarm }; renderSheet(); return; }
      S.sheet = S.pinReturn; S.pinReturn = null;
      if (S.sheet) { renderSheet(); } else { closeSheet(); }
    }
    if (m.ok) { showToast(t("asDone", { mode: alarmModeText(m.mode) }), null, 3000); }
  }
  function checkAlarm() {
    var list = alarmList(), keys = list.map(function (a) { return a.kind + ":" + a.id; }), old = S.alarmKeys || [];
    if (!list.length) {
      S.alarmKeys = []; S.alarmMuted = false; S.alarmHidden = false; stopSiren();
      var el = document.getElementById("alarm"); if (el) { el.parentNode.removeChild(el); }
      return;
    }
    // a new alarm sounds and shows again, also when the last one was muted
    if (keys.some(function (k) { return old.indexOf(k) < 0; })) { S.alarmMuted = false; S.alarmHidden = false; wake(); }
    S.alarmKeys = keys;
    if (S.alarmMuted) { stopSiren(); } else { startSiren(); }
    renderAlarm();
  }
  function renderAlarm() {
    var list = alarmList(); if (!list.length) { return; }
    var el = document.getElementById("alarm");
    if (!el) { el = document.createElement("div"); el.id = "alarm"; document.body.appendChild(el); }
    var kinds = []; list.forEach(function (a) { if (kinds.indexOf(a.kind) < 0) { kinds.push(a.kind); } });
    var kind = kinds.length === 1 ? kinds[0] : "alarm", title = t({ smoke: "alSmoke", water: "alWater", intrusion: "alIntrusion" }[kind] || "alAlarm");
    var where = list.map(function (a) { return [a.name, a.room].filter(Boolean).join(" · "); }).join(", ");
    if (S.alarmHidden) {
      el.className = "ringbanner alarmbanner";
      el.innerHTML = '<span class="pulse"></span><b>' + esc(title) + "</b><span class=\"sub\">" + esc(where) + '</span><button class="pill primary" data-alarmshow="1">' + esc(t("alShow")) + "</button>";
      return;
    }
    var sys = alarmInfo().system, ro = S.tablet && S.tablet.readonly;
    var rows = list.map(function (a) {
      return '<div class="alrow">' + I(a.kind === "intrusion" ? "shield" : KIND_ICON[a.kind] || "bell", 26) + "<div><b>" + esc(a.name) + "</b><span>" + esc([a.room, since(a.since)].filter(Boolean).join(" · ")) + "</span></div></div>";
    }).join("");
    var tips = kinds.map(function (k) { return { smoke: t("alSmokeTip"), water: t("alWaterTip"), intrusion: t("alIntrusionTip") }[k]; }).filter(Boolean);
    el.className = "alarmfull " + kind;
    el.innerHTML = '<div class="alin"><div class="alic">' + I(kind === "intrusion" ? "shield" : kind === "water" ? "drop" : kind === "smoke" ? "smoke" : "bell", 72) + "</div><h1>" + esc(title) + '</h1><div class="allist">' + rows + "</div>" +
      (tips.length ? '<div class="altip">' + esc(tips.join(" ")) + "</div>" : "") +
      '<div class="alctrl"><button class="pill" data-alarmmute="1">' + I(S.alarmMuted ? "speaker" : "mute", 20) + " " + esc(S.alarmMuted ? t("alSound") : t("alMute")) + "</button>" +
      (kinds.indexOf("intrusion") >= 0 && sys && sys.modes.indexOf("off") >= 0 && !ro ? '<button class="pill primary" data-alarmmode="off">' + I("shield", 20) + " " + esc(t("alSystemOff")) + "</button>" : "") +
      '<button class="pill" data-alarmhide="1">' + esc(t("alHide")) + "</button></div></div>";
  }
  function siren() {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext; if (!Ctx) { return; }
      var ctx = S.audio || (S.audio = new Ctx());
      [[960, 0], [720, 0.45]].forEach(function (n) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "square"; o.frequency.value = n[0];
        g.gain.setValueAtTime(0.0001, ctx.currentTime + n[1]);
        g.gain.exponentialRampToValueAtTime(0.25, ctx.currentTime + n[1] + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + n[1] + 0.42);
        o.connect(g); g.connect(ctx.destination); o.start(ctx.currentTime + n[1]); o.stop(ctx.currentTime + n[1] + 0.45);
      });
    } catch (e) { /* no sound */ }
  }
  function startSiren() { if (S.sirenTimer) { return; } siren(); S.sirenTimer = setInterval(siren, 1000); }
  function stopSiren() { clearInterval(S.sirenTimer); S.sirenTimer = null; }

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
    sheetShell('<div class="head"><div><h1>' + esc(t(p.alarm ? "asPinTitle" : "pinTitle")) + '</h1><div class="subtitle">' + esc(p.error || t(p.alarm ? "asPinLead" : "pinLead")) + '</div></div><button class="iconbtn" data-close="1">' + I("x") + "</button></div>" +
      '<div class="pinpad"><div class="pdots' + (p.error ? " bad" : "") + '">' + dots + '</div><div class="pkeys">' + keys + "</div></div>", "pinsheet");
  }
  function pinKey(k) {
    var p = S.sheet; if (!p || p.pin === undefined || p.busy) { return; }
    if (k === "del") { p.pin = p.pin.slice(0, -1); }
    else if (k === "ok") { if (p.pin.length >= 4) { p.busy = true; send(p.alarm ? { type: "action", action: "alarm_mode", mode: p.alarm, pin: p.pin } : { type: "unlock", pin: p.pin }); } }
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
    if (page === "floors") { renderFloors(); return; }
    if (page === "buginfo") { renderBugInfo(); return; }
    if (page === "rooms") { renderSettingsRooms(); return; }
    if (page === "appliances") { renderAppliances(); return; }
    if (page === "keepon") { sheetShell(settingsHead(t("keepOnList"), t("setHome"), true) + keepOnListHtml()); return; }
    var themes = ["auto", "dark", "light"].map(function (p) { return '<button class="' + ((lay.theme || "auto") === p ? "on" : "") + '" data-theme="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var hidden = lay.hidden_rooms || [], shown = S.rooms.filter(function (r) { return hidden.indexOf(r.name) < 0; }).length;
    var kept = Object.keys(S.tiles).filter(function (id) { return S.tiles[id].keep_on; }).length;
    var html = settingsHead(t("settings"), tb.name + (tb.readonly ? " · " + t("readonly") : ""), false) +
      '<div class="hint" style="text-align:left;margin:4px 0 16px">' + esc(t("setLead")) + "</div>" + worthLookHtml() +
      '<div class="group"><div class="label">' + esc(t("setTablet")) + '</div><div class="menu">' +
      settingsRow('data-setpage="tablet"', "frame", t("setNamePlace"), [t(tb.place), tb.room].filter(Boolean).join(" · ")) +
      '<div class="mrow"><span class="mic">' + I("sun", 20) + '</span><span class="ml"><b>' + esc(t("theme")) + '</b></span><div class="seg">' + themes + "</div></div>" + accentHtml() +
      '<div class="mrow"><span class="mic">' + I("globe", 20) + '</span><span class="ml"><b>' + esc(t("language")) + '</b></span><select id="langsel" data-lang="1">' + LANGS.map(function (l) { return '<option value="' + l[0] + '"' + (langChoice() === l[0] ? " selected" : "") + ">" + esc(l[0] === "auto" ? t("auto") : l[1]) + "</option>"; }).join("") + "</select></div>" +
      (seesCameras() ? '<div class="mrow"><span class="mic">' + I("film", 20) + '</span><span class="ml"><b>' + esc(t("camStart")) + '</b></span><div class="seg"><button class="' + (lay.start !== "cameras" ? "on" : "") + '" data-camstart="">' + esc(t("camStartAuto")) + '</button><button class="' + (lay.start === "cameras" ? "on" : "") + '" data-camstart="cameras">' + esc(t("camStartCams")) + "</button></div></div>" : "") +
      liteRowHtml(lay) +
      '<div class="mrow"><span class="mic">' + I("clock", 20) + '</span><span class="ml"><b>' + esc(t("saver")) + '</b></span><div class="seg">' + [0, 2, 5, 10, 15, 30].map(function (m) { return '<button class="' + (saverMinutes() === m ? "on" : "") + '" data-saver="' + m + '">' + esc(m ? t("saverMin", { n: m }) : t("saverOff")) + "</button>"; }).join("") + "</div></div>" +
      speakRowHtml(lay) +
      settingsRow('data-setpage="rooms"', "home", t("setRooms"), t("setRoomsValue", { n: shown, m: S.rooms.length })) +
      settingsRow('data-edit="1"', "plus", t("editTiles"), "") + "</div></div>";
    if (tb.arrange) {
      html += '<div class="group"><div class="label">' + esc(t("setHome")) + '</div><div class="menu">' +
        settingsRow('data-arrange="1"', "home", t("arrange"), t("setArrangeValue")) +
        settingsRow('data-setpage="keepon"', "power", t("keepOnList"), kept ? t("setKeepValue", { n: kept }) : t("setKeepNone")) +
        settingsRow('data-setpage="floors"', "stairs", t("floors"), floorList().length ? t("floorsValue", { n: floorList().length }) : t("floorsNone")) + "</div></div>";
    }
    if (!tb.readonly) {
      var nAp = (((S.header && S.header.appliances) || {}).known || []).length;
      html += '<div class="group"><div class="menu">' + settingsRow('data-setpage="appliances"', "washer", t("apSettings"), nAp ? t("apSettingsValue", { n: nAp }) : t("apSettingsNone")) + "</div></div>";
    }
    if (tb.https && location.protocol !== "https:") {
      html += '<div class="group"><div class="menu"><a class="mrow" href="' + esc(tb.https) + "#t=" + encodeURIComponent(S.token) + '"><span class="mic">' + I("mic", 20) + '</span><span class="ml"><b>' + esc(t("setTalk")) + "</b><span>" + esc(t("switchHttps")) + "</span></span>" + I("chev", 18) + "</a></div></div>";
    }
    html += '<div class="group"><div class="menu">' + settingsRow('data-tour="1"', "star", t("tourAgain"), "") + "</div></div>";
    html += '<div class="group"><div class="menu">' + settingsRow('data-buginfo="1"', "gear", t("bugInfo"), "") + "</div></div>";
    html += '<div class="group"><button class="linkbtn" data-resetlayout="1">' + esc(t("resetView")) + "</button></div>";
    sheetShell(html);
  }
  // things to sort out: devices without a room, idle ones, maintenance
  function worthLookHtml() {
    var rows = "", h = S.setupHints, todo = maintenance().length;
    if (h && h.noRoom) { rows += settingsRow('data-arrange="1"', "home", h.noRoom === 1 ? t("wlNoRoom1") : t("wlNoRoom", { n: h.noRoom }), t("wlNoRoomSub")); }
    if (h && h.idle) { rows += settingsRow('data-arrange="1"', "clock", h.idle === 1 ? t("wlIdle1") : t("wlIdle", { n: h.idle }), t("wlIdleSub")); }
    if (todo) { rows += settingsRow('data-overview="maintenance"', "battery", t("wlMaint", { n: todo }), t("wlMaintSub")); }
    return rows ? '<div class="group"><div class="label">' + esc(t("worthLook")) + '</div><div class="menu">' + rows + "</div></div>" : "";
  }
  // ---------- info for a bug report ----------
  function bugText() {
    var i = S.bugInfo || {}, lay = layout(), lines = [
      "fhempy " + (i.fhempy || "?") + " · dashboard " + (i.build || "?"),
      "Python " + (i.python || "?") + " · " + (i.system || "?"),
      "Devices " + i.devices + " · tiles " + i.tiles + " · rooms " + i.rooms,
      "Kinds " + Object.keys(i.kinds || {}).map(function (k) { return k + " " + i.kinds[k]; }).join(", "),
      "Tablets " + i.tablets + " · connected " + i.connected + " · https " + (i.https ? "on" : "off"),
      "Attributes " + ((i.attrs || []).join(", ") || "none"),
      "This tablet: " + place() + (S.tablet && S.tablet.readonly ? ", read-only" : "") + (S.tablet && S.tablet.rooms && S.tablet.rooms.length ? ", restricted" : "") + " · theme " + (lay.theme || "auto") + " · " + (document.body.classList.contains("lite") ? "simple" : "full") + " display · " + location.protocol.replace(":", ""),
      "Browser " + navigator.userAgent,
      "Screen " + screen.width + "×" + screen.height + " @" + (window.devicePixelRatio || 1) + " · window " + window.innerWidth + "×" + window.innerHeight + " · " + (navigator.language || "") + " · cores " + (navigator.hardwareConcurrency || "?")
    ];
    return lines.join("\n");
  }
  function renderBugInfo() {
    sheetShell(settingsHead(t("bugInfo"), t("bugLead"), true) +
      '<div class="group"><textarea id="bugtext" readonly rows="10" style="width:100%;font:13px/1.45 ui-monospace,monospace;user-select:text;-webkit-user-select:text">' + esc(S.bugInfo ? bugText() : "…") + "</textarea></div>" +
      '<div class="actions"><button class="pill primary" data-bugcopy="1">' + esc(t("bugCopy")) + "</button></div>");
  }
  function copyBugInfo() {
    var area = document.getElementById("bugtext"); if (!area) { return; }
    var done = function () { showToast(t("bugCopied"), null, 2000); };
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(area.value).then(done, function () { area.select(); }); return; }
    // http: the old way
    area.removeAttribute("readonly"); area.select();
    try { if (document.execCommand("copy")) { done(); } } catch (e) { /* select by hand */ }
    area.setAttribute("readonly", "");
  }
  function renderSettingsTablet() {
    var tb = S.tablet;
    var places = ["wall", "couch", "door"].map(function (p) { return '<button class="' + (tb.place === p ? "on" : "") + '" data-place="' + p + '">' + esc(t(p)) + "</button>"; }).join("");
    var roomOpts = '<option value="">' + esc(t("noRoom")) + "</option>" + S.rooms.map(function (r) { return '<option' + (r.name === tb.room ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    sheetShell(settingsHead(t("setNamePlace"), tb.name, true) + '<div class="hint" style="text-align:left;margin:4px 0 16px">' + esc(t("tabLead")) + "</div>" +
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
  // change the order of the room shown, starting from what is on screen
  function editRoomOrder(fn) {
    var room = S.tab.indexOf("room:") === 0 && roomByName(S.tab.slice(5)); if (!room) { return; }
    var lay = copyLayout(), cur = (lay.tile_order || {})[room.name];
    if (!cur || !cur.length) { cur = roomTiles(room, true); }
    lay.tile_order = lay.tile_order || {}; lay.tile_order[room.name] = fn(cur.slice()); saveLayout(lay);
  }

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
    // place, rooms (only with rooms), how to use it
    var steps = S.rooms.length ? [1, 2, 3] : [1, 3];
    return '<div class="steps">' + steps.map(function (n) { return '<span class="' + (n === step ? "on" : n < step ? "done" : "") + '"></span>'; }).join("") + "</div>";
  }
  // third step of the setup, also from the settings: tap, drag, hold, gear
  function renderTour() {
    var cards = [["tourTap", "power"], ["tourDrag", "blind"], ["tourHold", "clock"], ["tourGear", "gear"]].map(function (c) {
      return '<div class="pl tour"><div class="pi">' + I(c[1]) + "</div><h3>" + esc(t(c[0])) + "</h3><ul>" + T[c[0] + "List"].map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>";
    }).join("");
    app.innerHTML = '<div class="ob"><div class="obbox"><div class="logo"><div class="m"></div>' + esc(t("home")) + "</div>" + (S.tour === "setup" ? setupSteps(3) : "") + "<h1>" + esc(t("tourTitle")) + '</h1><p class="l">' + esc(t("tourText")) +
      '</p><div class="places tours">' + cards + '</div><div class="found"><button class="pill primary" data-tourdone="1">' + esc(t("tourGo")) + "</button></div></div></div>";
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
    send({ type: "setup", place: pl, room: room, name: (room ? room + " " : "") + (T !== EN ? label : pl) });
    if (S.setupHidden) {
      var lay = copyLayout(); lay.hidden_rooms = S.setupHidden.slice();
      S.tablet.layout = lay; send({ type: "layout", layout: lay });
    }
    S.tablet.place = pl; S.tablet.room = room; S.setupStep = null; S.tab = startTab(); S.tour = "setup"; render(); applyTheme(); wakeLock();
  }

  // ---------- screensaver, idle, wake ----------
  function idleCheck() {
    var idle = (Date.now() - S.lastTouch) / 1000;
    if (S.ring || alarmList().length || !S.tablet || !S.tablet.place) { return; }
    // a live picture left open on a normal tablet ends after two minutes
    if (idle > 120 && S.camView && !S.camView.baby && layout().start !== "cameras") { closeCam(); }
    if (idle > 120 && (S.sheet || S.edit || S.tab !== startTab())) {
      closeSheet(); S.edit = false; S.tab = startTab(); S.historyDay = null; renderTabs(); renderContent();
    }
    var after = saverMinutes();
    if (after && idle > after * 60 && layout().start !== "cameras" && !(S.camView && S.camView.baby) && !S.saver) { S.saver = true; renderSaver(); }
  }
  // minutes until the screensaver, 0: never. Default 5, on the couch never
  function saverMinutes() {
    var m = layout().saver;
    if (typeof m === "number") { return m; }
    return place() === "couch" ? 0 : 5;
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
    var open = warnOpen(h.open);
    if (open.length) { items += '<div class="x o">' + I("win", 20) + " " + esc(open.length <= 3 ? open.map(function (o) { return o.name; }).join(", ") + " " + t("open").toLowerCase() : t("openCount", { n: open.length })) + "</div>"; }
    else { items += '<div class="x">' + I("lock", 20) + " " + esc(t("allClosed")) + "</div>"; }
    binTexts().forEach(function (b) { items += '<div class="x o">' + I("trash", 20) + " " + esc(b) + "</div>"; });
    // what is still coming today
    ((h.calendar && h.calendar.entries) || []).filter(function (e) { return e.day === 0 && !e.now; }).slice(0, 3).forEach(function (e) {
      items += '<div class="x">' + I("clock", 20) + " " + esc((e.allday ? t("calAllDay") : e.at) + " " + e.summary) + "</div>";
    });
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
    applyAccent();
  }
  // ---------- accent colour of a tablet, or the colour of the lamps ----------
  var ACCENTS = { amber: "#FFB547", teal: "#3DDBB8", blue: "#5AA9FF", violet: "#9B8CFF", pink: "#FF7EB6", green: "#34D399" };
  function rgbOf(hex) { var n = parseInt(String(hex).slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(","); }
  // coloured lamps which are on, not white ones
  function litColors() {
    var result = [];
    Object.keys(S.tiles).forEach(function (id) {
      var tl = S.tiles[id], st = tl.state;
      if (!isLight(tl) || !st.on || !st.rgb || st.rgb === "#000000") { return; }
      var c = rgbOf(st.rgb).split(",").map(Number), max = Math.max.apply(null, c), min = Math.min.apply(null, c);
      if (max - min < 40) { return; }
      if (result.indexOf(st.rgb) < 0) { result.push(st.rgb); }
    });
    return result;
  }
  function applyAccent() {
    var key = layout().accent || "amber", color = ACCENTS[key] || ACCENTS.amber, b = document.body.style;
    var glow1 = "rgba(" + rgbOf(color) + ",.14)", glow2 = "rgba(90,140,255,.12)";
    if (key === "amber") { glow1 = "rgba(255,170,90,.14)"; }
    if (key === "lamps") {
      var lit = litColors();
      if (lit.length) { glow1 = "rgba(" + rgbOf(lit[0]) + ",.26)"; glow2 = "rgba(" + rgbOf(lit[1] || lit[0]) + ",.2)"; }
    }
    b.setProperty("--accent", color); b.setProperty("--accent-soft", "rgba(" + rgbOf(color) + ",.16)");
    b.setProperty("--glow1", glow1); b.setProperty("--glow2", glow2);
    if (ACCENTS[key] && key !== "amber") { b.setProperty("--tg", color); } else { b.removeProperty("--tg"); }
  }
  function accentHtml() {
    var cur = layout().accent || "amber";
    return '<div class="mrow"><span class="mic">' + I("star", 20) + '</span><span class="ml"><b>' + esc(t("accent")) + "</b>" + (cur === "lamps" ? "<span>" + esc(t("accentHint")) + "</span>" : "") + '</span><div class="swatches accent">' +
      Object.keys(ACCENTS).map(function (k) { return '<button class="' + (cur === k ? "on" : "") + '" data-accent="' + k + '" style="background:' + ACCENTS[k] + '" aria-label="' + k + '"></button>'; }).join("") +
      '<button class="lamps' + (cur === "lamps" ? " on" : "") + '" data-accent="lamps" aria-label="' + esc(t("accentLamps")) + '" title="' + esc(t("accentLamps")) + '"></button></div></div>';
    var look = layout().lite || "auto";
    document.body.classList.toggle("lite", look === "on" || (look === "auto" && store("dashSlow") === "1"));
  }
  // simple display for slow tablets (old wall tablets): few cores or a low
  // frame rate while the page is idle. Measured once after each start.
  function liteRowHtml(lay) {
    var cur = lay.lite || "auto";
    var opts = [["auto", "lookAuto"], ["on", "lookLite"], ["off", "lookFull"]];
    var btns = opts.map(function (o) {
      return '<button class="' + (cur === o[0] ? "on" : "") + '" data-lite="' + o[0] + '">' + esc(t(o[1])) + "</button>";
    }).join("");
    return '<div class="mrow"><span class="mic">' + I("frame", 20) + '</span><span class="ml"><b>' + esc(t("look")) +
      "</b><span>" + esc(t("lookHint")) + '</span></span><div class="seg">' + btns + "</div></div>";
  }
  var speed = { frames: 0, first: 0 };
  function speedFrame(ts) {
    if (!speed.first) { speed.first = ts; }
    speed.frames++;
    if (ts - speed.first < 2000) { requestAnimationFrame(speedFrame); return; }
    // hidden pages get no frames, then nothing is learned
    if (document.hidden) { return; }
    var fps = speed.frames * 1000 / (ts - speed.first);
    store("dashSlow", fps < 30 ? "1" : "0");
    applyTheme();
  }
  function measureSpeed() {
    if (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2) {
      store("dashSlow", "1");
      applyTheme();
      return;
    }
    if (!window.requestAnimationFrame) { return; }
    speed = { frames: 0, first: 0 };
    requestAnimationFrame(speedFrame);
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
    if (S.camView) { closeCam(); }
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
  // ---------- camera page: all cameras, tap for live, swipe to the next ----------
  var camPc = null;
  function cameraList() { return (S.header && S.header.door && S.header.door.cameras) || []; }
  // restricted tablets (only some rooms) see no camera page
  function seesCameras() { return cameraList().length > 0 && !(S.tablet && S.tablet.rooms && S.tablet.rooms.length); }
  function camerasHtml() {
    S.camSnap = S.camSnap || {};
    return '<div class="camgrid">' + cameraList().map(function (c, i) {
      return '<button class="camcard" data-cam="' + i + '"><img data-camimg="' + esc(c) + '" alt=""' + (S.camSnap[c] ? ' src="' + S.camSnap[c] + '"' : "") + '><span>' + esc(c) + "</span></button>";
    }).join("") + "</div>";
  }
  // still pictures every 2 s while the page is shown, one camera after the other
  function camSnaps() {
    if (S.camTimer) { return; }
    var list = cameraList(), i = 0;
    function next() {
      S.camTimer = null;
      if (S.tab !== "cameras" || S.saver || S.camView || document.hidden || !list.length) { return; }
      var c = list[i % list.length]; i++;
      fetch("api/snapshot?stream=" + encodeURIComponent(c) + "&t=" + Date.now(), { headers: { Authorization: "Bearer " + S.token } })
        .then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.blob(); })
        .then(function (b) {
          var old = S.camSnap[c]; S.camSnap[c] = URL.createObjectURL(b);
          var img = document.querySelector('[data-camimg="' + cssEsc(c) + '"]'); if (img) { img.src = S.camSnap[c]; }
          if (old) { URL.revokeObjectURL(old); }
        })
        .catch(function () { /* camera offline */ })
        .then(function () { S.camTimer = setTimeout(next, Math.max(300, 2000 / list.length)); });
    }
    S.camTimer = setTimeout(next, 10);
  }
  function openCam(i) {
    var list = cameraList(); if (!list.length) { return; }
    S.camView = { i: (i + list.length) % list.length }; renderCam();
  }
  function renderCam() {
    var v = S.camView, list = cameraList(), el = document.getElementById("camview");
    if (!v) { if (el) { el.parentNode.removeChild(el); } closeCamLive(); camSnaps(); return; }
    if (!el) { el = document.createElement("div"); el.id = "camview"; el.className = "camview"; document.body.appendChild(el); }
    var c = list[v.i];
    el.className = "camview" + (v.baby ? " baby" + (isNight() ? " night" : "") : "");
    el.innerHTML = '<video id="camvideo" autoplay playsinline' + (v.baby ? "" : " muted") + '></video><img id="camsnap" alt=""' + (S.camSnap && S.camSnap[c] ? ' src="' + S.camSnap[c] + '"' : "") + '>' +
      '<div class="camtop"><span>' + esc(c) + "</span>" + (list.length > 1 && !v.baby ? "<span>" + (v.i + 1) + " / " + list.length + "</span>" : "") +
      '<button class="pill' + (v.baby ? " on" : "") + '" data-baby="1">' + I("moon", 18) + " " + esc(v.baby ? t("babyEnd") : t("baby")) + '</button><button class="iconbtn" data-camclose="1">' + I("x") + "</button></div>" +
      (v.baby ? babyHtml() : "") +
      (list.length > 1 && !v.baby ? '<button class="camnav l" data-camstep="-1" aria-label="' + esc(t("camPrev")) + '">' + I("left") + '</button><button class="camnav r" data-camstep="1" aria-label="' + esc(t("camNext")) + '">' + I("chev") + "</button>" : "");
    camLive(c);
  }
  function camLive(stream) {
    closeCamLive();
    var video = document.getElementById("camvideo");
    if (!window.RTCPeerConnection || !video) { return; }
    var conn = camPc = new RTCPeerConnection({ iceServers: [] });
    conn.addTransceiver("video", { direction: "recvonly" });
    conn.addTransceiver("audio", { direction: "recvonly" });
    conn.ontrack = function (ev) { if (video.srcObject !== ev.streams[0]) { video.srcObject = ev.streams[0] || new MediaStream([ev.track]); video.classList.add("on"); } };
    conn.createOffer().then(function (offer) { return conn.setLocalDescription(offer); }).then(function () { return waitIce(conn); }).then(function () {
      return fetch("api/webrtc?stream=" + encodeURIComponent(stream), { method: "POST", headers: { Authorization: "Bearer " + S.token, "Content-Type": "application/sdp" }, body: conn.localDescription.sdp });
    }).then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.text(); })
      .then(function (sdp) { if (conn === camPc) { return conn.setRemoteDescription({ type: "answer", sdp: sdp }); } })
      .catch(function () { /* the still picture stays */ });
  }
  function closeCamLive() { if (camPc) { try { camPc.close(); } catch (e) { /* closed */ } camPc = null; } }
  function closeCam() { S.camView = null; renderCam(); }
  // ---------- baby monitor: live picture with sound, no time limit, dark at night ----------
  function babyRoomName() {
    var name = store("dashBabyRoom") || (S.tablet && S.tablet.room) || "";
    return roomByName(name) ? name : (S.rooms[0] ? S.rooms[0].name : "");
  }
  function roomClimate(name) {
    var room = roomByName(name), temp = null, humid = null;
    if (room) {
      room.tiles.forEach(function (id) {
        var tl = S.tiles[id]; if (!tl) { return; }
        var c = climateOf(tl);
        if (temp === null && c.temp !== undefined && c.temp !== null) { temp = c.temp; }
        if (humid === null && tl.state.humidity !== undefined && tl.state.humidity !== null) { humid = tl.state.humidity; }
      });
    }
    return { temp: temp, humid: humid };
  }
  function babyHtml() {
    var name = babyRoomName(), c = roomClimate(name);
    var opts = S.rooms.map(function (r) { return "<option" + (r.name === name ? " selected" : "") + ">" + esc(r.name) + "</option>"; }).join("");
    return '<div class="babybar"><b>' + clockText(new Date()) + "</b>" + (c.temp !== null ? "<span>" + I("thermo", 20) + " " + num(c.temp) + "°</span>" : "") + (c.humid !== null ? "<span>" + I("drop", 20) + " " + Math.round(c.humid) + " %</span>" : "") +
      '<select id="babyroom" aria-label="' + esc(t("babyRoom")) + '">' + opts + "</select></div>";
  }
  function toggleBaby() {
    var v = S.camView; if (!v) { return; }
    v.baby = !v.baby;
    if (v.baby && navigator.wakeLock && !lock) { navigator.wakeLock.request("screen").then(function (l) { lock = l; l.addEventListener("release", function () { lock = null; }); }).catch(function () { /* not allowed */ }); }
    renderCam();
  }
  // clock, climate and night dimming stay current
  function babyTick() {
    var v = S.camView; if (!v || !v.baby) { return; }
    var el = document.getElementById("camview"), bar = el && el.querySelector(".babybar");
    if (el) { el.classList.toggle("night", isNight()); }
    if (bar) { var sel = document.getElementById("babyroom"), open = sel && document.activeElement === sel; if (!open) { var tmp = document.createElement("div"); tmp.innerHTML = babyHtml(); bar.parentNode.replaceChild(tmp.firstChild, bar); } }
  }
  document.addEventListener("change", function (ev) { if (ev.target && ev.target.id === "babyroom") { store("dashBabyRoom", ev.target.value); babyTick(); } });
  // swipe in the live view
  document.addEventListener("pointerdown", function (ev) { if (S.camView && ev.target.closest && ev.target.closest("#camview")) { S.camView.sx = ev.clientX; } }, true);
  document.addEventListener("pointerup", function (ev) {
    var v = S.camView; if (!v || v.sx === undefined) { return; }
    var dx = ev.clientX - v.sx; v.sx = undefined;
    if (Math.abs(dx) > 60 && cameraList().length > 1) { openCam(v.i + (dx < 0 ? 1 : -1)); }
  }, true);

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
    if ((el = closest(target, "data-measure"))) {
      if (!pinOk()) { askPin(null); return; }
      var mt = S.tiles[el.getAttribute("data-measure")]; if (!mt) { return; }
      send({ type: "measure_only", id: mt.id, measure: !mt.measure }); return;
    }
    if ((el = closest(target, "data-camclose"))) { closeCam(); return; }
    if ((el = closest(target, "data-baby"))) { toggleBaby(); return; }
    if ((el = closest(target, "data-camstep")) && S.camView) { openCam(S.camView.i + +el.getAttribute("data-camstep")); return; }
    if ((el = closest(target, "data-cam"))) { openCam(+el.getAttribute("data-cam")); return; }
    if ((el = closest(target, "data-camstart"))) { var lc = copyLayout(); lc.start = el.getAttribute("data-camstart") || undefined; if (!lc.start) { delete lc.start; } saveLayout(lc); return; }
    if (floorClick(target)) { return; }
    if ((el = closest(target, "data-size"))) {
      var sid = el.getAttribute("data-size"), ls = copyLayout(); ls.tile_size = ls.tile_size || {};
      ls.tile_size[sid] = SIZES[(SIZES.indexOf(tileSize(sid)) + 1) % SIZES.length]; saveLayout(ls); return;
    }
    if ((el = closest(target, "data-delhead"))) { editRoomOrder(function (o) { return o.filter(function (x) { return x !== el.getAttribute("data-delhead"); }); }); return; }
    if ((el = closest(target, "data-addhead"))) {
      var input = document.getElementById("newhead"), text = input ? input.value.replace(/[\u0000-\u001f]/g, "").trim() : "";
      if (text) { editRoomOrder(function (o) { return o.indexOf("#" + text) >= 0 ? o : ["#" + text].concat(o); }); }
      return;
    }
    if ((el = closest(target, "data-roomreset"))) {
      var rr = roomByName(el.getAttribute("data-roomreset")), lr = copyLayout();
      if (rr) {
        if (lr.tile_order) { delete lr.tile_order[rr.name]; }
        if (lr.tile_size) { rr.tiles.forEach(function (x) { delete lr.tile_size[x]; }); }
        lr.hidden_tiles = (lr.hidden_tiles || []).filter(function (x) { return rr.tiles.indexOf(x) < 0; });
        saveLayout(lr);
      }
      return;
    }
    if ((el = closest(target, "data-pinkey"))) { pinKey(el.getAttribute("data-pinkey")); return; }
    if ((el = closest(target, "data-mayopen"))) { sendMayOpen(el.getAttribute("data-mayopen"), el.classList.contains("off")); return; }
    if ((el = closest(target, "data-mayopensave"))) { sendMayOpen(el.getAttribute("data-mayopensave"), true); showToast(t("ntSaved"), null, 2000); return; }
    if ((el = closest(target, "data-noticedone"))) { send({ type: "action", action: "notice_done", id: el.getAttribute("data-noticedone") }); el.closest(".notice").style.opacity = ".4"; return; }
    if ((el = closest(target, "data-notice"))) { sendNotice(el.getAttribute("data-notice"), el.classList.contains("off")); return; }
    if ((el = closest(target, "data-noticesave"))) { sendNotice(el.getAttribute("data-noticesave"), true); showToast(t("ntSaved"), null, 2000); return; }
    if ((el = closest(target, "data-half")) && S.sheet && S.tiles[S.sheet.id]) { act(S.sheet.id, "position", 50, { position: 50 }); renderSheet(); return; }
    if ((el = closest(target, "data-appl"))) {
      if (!pinOk()) { askPin(null); return; }
      var ap = el.getAttribute("data-appl").split("|"); send({ type: "appliance", id: ap[0], what: ap[1] }); el.closest(".apask").style.opacity = ".4"; return;
    }
    if ((el = closest(target, "data-apdone"))) { applianceAlertDone(el.getAttribute("data-apdone")); return; }
    if ((el = closest(target, "data-speaktest"))) { say(t("apSayWasher")); return; }
    if ((el = closest(target, "data-speak"))) {
      var l3 = copyLayout(); l3.speak = el.getAttribute("data-speak") === "1"; saveLayout(l3);
      // the first words after a tap: browsers speak only after the user touched the page
      if (l3.speak) { say(t("apSayWasher")); }
      return;
    }
    if ((el = closest(target, "data-applseen"))) { send({ type: "appliance_seen", id: el.getAttribute("data-applseen") }); el.closest(".row").style.opacity = ".4"; return; }
    if ((el = closest(target, "data-alarmmode"))) { alarmMode(el, el.getAttribute("data-alarmmode")); return; }
    if ((el = closest(target, "data-alarmmute"))) { S.alarmMuted = !S.alarmMuted; checkAlarm(); return; }
    if ((el = closest(target, "data-alarmhide"))) { S.alarmHidden = true; renderAlarm(); return; }
    if ((el = closest(target, "data-alarmshow"))) { S.alarmHidden = false; renderAlarm(); return; }
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
    if ((el = closest(target, "data-mpause"))) {
      var pid = el.getAttribute("data-mpause");
      if (S.tiles[pid]) { act(pid, "pause", null, { playing: false }); }
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
    if (viewClick(target)) { return; }
    if ((el = closest(target, "data-do"))) {
      var sid = S.sheet.id, what = el.getAttribute("data-do");
      if (what === "unlock" && !armed(el, "unlock:" + sid, t("unlockSure"))) { return; }
      if (what === "on") { act(sid, "on", null, { on: true }); } else if (what === "off") { act(sid, "off", null, { on: false }); } else if (what === "up") { act(sid, "position", 100, { position: 100 }); } else if (what === "down") { act(sid, "position", 0, { position: 0 }); } else if (what === "stop") { act(sid, "stop"); } else { act(sid, what, null, { locked: what === "lock" }); }
      renderSheet(); return;
    }
    if ((el = closest(target, "data-step"))) {
      var tile = S.tiles[el.getAttribute("data-sid") || S.sheet.id], step = (tile.step || 0.5) * Number(el.getAttribute("data-step"));
      var next = Math.round(Math.max(tile.min !== undefined ? tile.min : 4.5, Math.min(tile.max !== undefined ? tile.max : 30, (tile.state.target || 20) + step)) * 10) / 10;
      tile.state.target = next; if (S.sheet) { renderSheet(); } updateTile(tile.id);
      clearTimeout(S.stepTimer); S.stepTimer = setTimeout(function () { act(tile.id, "target", next, { target: next }); }, 700);
      return;
    }
    if ((el = closest(target, "data-settings"))) { openSettings(); return; }
    if ((el = closest(target, "data-setpage")) && S.sheet && S.sheet.settings) { S.sheet.page = el.getAttribute("data-setpage"); renderSettings(); return; }
    if ((el = closest(target, "data-batteries"))) { openBatteries(); return; }
    if ((el = closest(target, "data-weather"))) { S.sheet = { weather: true }; renderSheet(); return; }
    if ((el = closest(target, "data-energy"))) { openEnergy("day"); return; }
    if ((el = closest(target, "data-enrange"))) { openEnergy(el.getAttribute("data-enrange")); return; }
    if ((el = closest(target, "data-enprice"))) { energyPriceClick(el); return; }
    if ((el = closest(target, "data-routine"))) { routineOpen(el.getAttribute("data-routine")); return; }
    if ((el = closest(target, "data-rtvac"))) { var vid = el.getAttribute("data-rtvac"); act(vid, "start", null, null); if (S.sheet) { S.sheet.vacStarted = S.sheet.vacStarted || {}; S.sheet.vacStarted[vid] = true; renderSheet(); } return; }
    if ((el = closest(target, "data-rtheat"))) { if (S.sheet) { S.sheet.heatBlinds = !S.sheet.heatBlinds; } renderSheet(); return; }
    if ((el = closest(target, "data-rtalarm"))) { if (S.sheet) { S.sheet.noAlarm = rtAlarmOn(); } renderSheet(); return; }
    if ((el = closest(target, "data-rtstop"))) { if (S.sheet) { S.sheet.autoAt = 0; } routineTick(); renderSheet(); return; }
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
    if ((el = closest(target, "data-accent"))) { var l5 = copyLayout(); l5.accent = el.getAttribute("data-accent"); saveLayout(l5); return; }
    if ((el = closest(target, "data-showall")) && S.sheet) { S.sheet.all = true; renderSheet(); return; }
    if ((el = closest(target, "data-buginfo"))) { S.sheet = { settings: true, page: "buginfo" }; send({ type: "bug_info" }); renderSettings(); return; }
    if ((el = closest(target, "data-bugcopy"))) { copyBugInfo(); return; }
    if ((el = closest(target, "data-lite"))) { var l3 = copyLayout(); l3.lite = el.getAttribute("data-lite"); saveLayout(l3); return; }
    if ((el = closest(target, "data-saver"))) { var l2 = copyLayout(); l2.saver = +el.getAttribute("data-saver"); saveLayout(l2); return; }
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
    if ((el = closest(target, "data-tourdone"))) { S.tour = null; store("dashTapHint", "1"); render(); return; }
    if ((el = closest(target, "data-tour"))) { closeSheet(); S.tour = "again"; render(); return; }
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
    if (ev.target.id === "langsel") { setLang(ev.target.value); return; }
    if (ev.target.getAttribute && ev.target.getAttribute("data-apby") !== null) { send({ type: "appliance_done_by", id: ev.target.getAttribute("data-apby"), by: ev.target.value }); return; }
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
    renderHeader(); idleCheck(); loadSparks(); tickTimers(); babyTick();
    // a door which may be open by day warns again in the evening
    var mo = Object.keys(S.tiles).filter(function (id) { return mayOpenNow(S.tiles[id].may_open); }).join("\n");
    if (S.moKey !== undefined && mo !== S.moKey) { renderContent(); }
    S.moKey = mo;
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
    setTimeout(measureSpeed, 5000);
    setInterval(function () { var c = document.getElementById("ringclock"); if (c && S.ring) { tick(); } }, 1000);
    if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
      navigator.serviceWorker.register("sw.js").catch(function () { /* optional */ });
    }
  }
  start();
})();
