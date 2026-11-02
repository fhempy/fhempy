/* Regeln: visual editor for DOIF and overview of all automations (fhempy doif_editor) */
/* global FW_cmd, FW_root, $ */
(function () {
  "use strict";

  var T = {
    DE: {
      title: "Regeln", rules: "Regeln", values: "Werte", map: "Zusammenhänge", plan: "Tagesplan", changes: "Änderungen",
      newRule: "Neue Regel", search: "Suchen…", edit: "Bearbeiten", back: "Zurück", save: "Speichern", saved: "Gespeichert",
      cancel: "Abbrechen", ok: "Übernehmen", del: "Löschen", code: "Code", visual: "Ansicht", test: "Testen",
      when: "WENN", and: "UND", or: "ODER", then: "DANN", elseif: "SONST WENN", else: "SONST", oneOf: "eine davon",
      allOf: "alle davon", caseN: "Fall {n}", comment: "Beschreibung (optional)", addCond: "Bedingung", addGroup: "Gruppe",
      addCmd: "Befehl", addStep: "Danach", addCase: "Sonst-wenn-Fall", addElse: "Sonst-Fall", wait: "nach {t}",
      waitEdit: "Warten vor diesem Schritt", noWait: "sofort", trigger: "Löst aus: Änderung startet die Regel",
      check: "Nur prüfen: startet die Regel nicht", chooseDevice: "Gerät wählen", reading: "Wert", value: "Vergleichswert",
      changes_: "ändert sich", isTrue: "ist wahr", reports: "meldet", anyEvent: "Ereignis", at: "um", between: "zwischen",
      every: "alle", everyIn: "alle {t}", not: "NICHT", days: "Tage", allDays: "jeden Tag", weekend: "Wochenende",
      workday: "Werktag", sunrise: "Sonnenaufgang", sunset: "Sonnenuntergang", offset: "Versatz (Minuten)",
      clock: "Uhrzeit", fromReading: "aus einem Reading", timeKind: "Art", condKind: "Art der Bedingung",
      k_cmp: "Gerät hat Wert", k_change: "Gerät ändert sich", k_event: "Gerät meldet Ereignis", k_time: "Uhrzeit",
      k_range: "Zeitraum", k_every: "Regelmäßig", k_code: "Perl-Ausdruck", k_agg: "Mehrere Geräte",
      command: "Befehl", args: "Wert / Parameter", setreading: "Reading setzen", fhemcmd: "FHEM-Befehl", perl: "Perl",
      cmdKind: "Art des Befehls", k_set: "Gerät schalten", k_setreading: "Reading setzen", k_fhem: "FHEM-Befehl",
      k_perl: "Perl-Code", advanced: "Erweitert", nowQ: "Was würde jetzt passieren?", nowWould: "Jetzt würde {c} ausgeführt.",
      nowNothing: "Jetzt würde nichts ausgeführt.", nowBlocked: "{c} ist schon ausgeführt worden, DOIF wiederholt ihn nicht (siehe Erweitert).",
      nowUnknown: "Ein Teil ist Perl-Code und kann hier nicht ausgewertet werden.", nowDisabled: "Die Regel ist ausgeschaltet.",
      waiting: "Wartet: {t}", lastTrigger: "Zuletzt ausgelöst durch: {t}", simulate: "Was wäre passiert?",
      simDays: "letzte {n} Tage", simNone: "In diesem Zeitraum wäre nichts ausgeführt worden.",
      simCount: "{n} Ausführungen", simUnknown: "{n} Auslöser konnten wegen Perl-Code nicht ausgewertet werden.",
      noHistory: "Für die Simulation wird ein Timeline-Gerät gebraucht (define timeline fhempy timeline).",
      versions: "Versionen", restore: "Wiederherstellen", noVersions: "Noch keine gespeicherten Versionen.",
      runNow: "Jetzt ausführen", on: "an", off: "aus", enabled: "eingeschaltet", disabled: "ausgeschaltet",
      lastRun: "zuletzt {t}", never: "noch nie", codeParts: "{n} Code-Teile", allVisual: "komplett visuell",
      perlMode: "Perl-Modus: jeder Block wird bei seinen Auslösern ausgeführt.", block: "Block", name: "Name",
      alias: "Anzeigename", room: "Raum", ruleName: "Name in FHEM", template: "Vorlage", t_empty: "Leere Regel",
      t_motion: "Licht bei Bewegung", t_schedule: "Zeitplan", t_window: "Fenster offen: Heizung runter",
      t_notify: "Benachrichtigung", t_irrigation: "Bewässerung nach Wetter", t_cook: "Kochzeit mit Erinnerung",
      health: "Gesundheitscheck", healthOk: "Keine Probleme gefunden.", hints: "{n} Hinweise",
      h_conflict: "{d} wird von mehreren Regeln unterschiedlich geschaltet.", h_flaps: "{n}× schnell hin und her in 7 Tagen.",
      h_loop: "Diese Regeln lösen sich gegenseitig aus (Schleife).", h_selfloop: "Diese Regel schaltet ein Gerät, das sie selbst auslöst.",
      h_missing: "Gerät fehlt: {d}", h_dead: "Seit über {n} Tagen nicht mehr ausgeführt.", h_deadNever: "Wurde noch nie ausgeführt.",
      h_duplicate: "Diese Regeln sind identisch.", h_error: "Fehler: {t}", h_unused_value: "Wert „{t}“ wird von keiner Regel benutzt.",
      wins: "{r} hat Vorrang", disableRule: "Ausschalten", focus: "Blick auf", house: "ganzes Haus", inputs: "Auslöser und Abfragen",
      outputs: "Geschaltete Geräte", time: "Zeit", why: "Warum ist das so?", whyQ: "Warum hat ein Gerät seinen Zustand?",
      whyCause: "{r} hat um {t} geschaltet", whyTrigger: "ausgelöst durch {t}", whyManual: "Keine Regel hat zu dieser Zeit geschaltet: vermutlich von Hand, per App oder vom Gerät selbst.",
      whyNoChange: "Keine Änderung in den letzten 24 Stunden gefunden.", candidates: "Diese Regeln können es schalten:",
      planEmpty: "Heute ist nichts mehr geplant.", nowLine: "jetzt", planTimer: "Zeitpunkt", planWait: "Wartezeit endet",
      planDone: "ausgeführt", planAt: "at", noChanges: "Noch keine Änderungen.", c_created: "angelegt", c_saved: "gespeichert",
      c_modified: "in FHEM geändert", c_defined: "in FHEM angelegt", c_deleted: "gelöscht", c_renamed: "umbenannt",
      c_restored: "wiederhergestellt", c_enabled: "eingeschaltet", c_disabled: "ausgeschaltet", c_value: "Wert gespeichert",
      c_value_deleted: "Wert gelöscht", newValue: "Neuer Wert", valueTitle: "Bezeichnung", unit: "Einheit",
      start: "Start mit", mul: "× Faktor", add: "+ dazu", sub: "− weg", set: "= ersetzen durch", fixed: "fester Wert",
      dependsOn: "je nach", onlyIf: "nur wenn", src_reading: "Gerät", src_history: "Verlauf", src_time: "Uhrzeit/Tag",
      src_input: "Eingabe", src_value: "anderer Wert", m_direct: "direkt", m_per: "pro Einheit", m_steps: "Stufen",
      m_values: "Texte", m_linear: "gleitend", from: "von", to: "bis", result: "Ergebnis", otherwise: "sonst",
      limits: "Grenzen", min: "mindestens", max: "höchstens", round: "runden auf", useIn: "In Regeln: {a} (bei Warten: {b})",
      f_sum: "Summe", f_min: "Minimum", f_max: "Maximum", f_avg: "Durchschnitt", f_count: "Anzahl Änderungen",
      f_since: "Sekunden seit letzter Änderung", hours: "der letzten Stunden", hour: "Stunde", weekday: "Wochentag",
      month: "Monat", addRow: "Zeile", inputsT: "Eingaben", newInput: "Neue Eingabe", inputKind: "Art", number: "Zahl",
      choice: "Auswahl", options: "Auswahl (mit Komma)", current: "aktuell", unknown: "unbekannt", noValues: "Noch keine berechneten Werte.",
      valuesHelp: "Ein Wert wird wie ein Kassenzettel von oben nach unten gerechnet. fhempy schreibt das Ergebnis als Reading, jede Regel kann es benutzen.",
      empty: "leer", needDevice: "Bitte in jedem Baustein ein Gerät wählen.", error: "Fehler", confirmDelete: "„{n}“ wirklich löschen? Es bleibt als Version erhalten.",
      kinds_all: "Alle", kinds_light: "Licht", kinds_switch: "Schalter", kinds_sensor: "Sensoren", kinds_climate: "Heizung",
      kinds_blind: "Rollläden", kinds_rule: "Regeln", stateR: "Status", applyCode: "In Ansicht übernehmen",
      codeHelp: "Definition und Attribute wie in FHEM. Unveränderte Teile bleiben beim Speichern genau so erhalten.",
      attrsT: "Attribute", q_do: "Bei jedem Auslöser ausführen, auch wenn derselbe Fall schon ausgeführt wurde",
      q_resetwait: "Wartezeit bei erneutem Auslösen neu starten (do resetwait)", q_checkall: "Bei Ereignissen und Zeiten alle Fälle prüfen",
      q_selftrigger: "Darf sich selbst auslösen", q_timerWithWait: "Zeiten erst nach der Wartezeit neu planen",
      q_initialize: "Status beim Start", q_repeatsame: "Höchstens so oft hintereinander", q_cmdpause: "Danach Pause (Sekunden)",
      q_waitsame: "Nur wenn innerhalb von Sekunden zweimal ausgelöst", q_waitdel: "Wartezeit abbrechen, wenn neu ausgelöst (Sekunden)",
      q_cmdState: "Status-Text dieses Falls", q_state: "Status der Regel (Ausdruck)", q_startup: "Beim Start ausführen",
      perCase: "Für diesen Fall", forRule: "Für die ganze Regel", nothingYet: "Noch keine Regeln. Lege die erste an!",
      p_no_trigger: "Fall {c} hat keinen Auslöser (nur Prüfungen) und wird nie ausgeführt.",
      p_single_case: "Nur ein Fall: DOIF führt ihn erst wieder aus, wenn die Bedingung dazwischen falsch war.",
      p_wait_always: "Mit „bei jedem Auslöser ausführen“ startet die Wartezeit bei jedem Ereignis neu.",
      p_self_trigger: "Die Regel schaltet {d} und wird auch von {d} ausgelöst.", fixElse: "Sonst-Fall hinzufügen", fixAlways: "Jedes Mal ausführen",
      sec: "Sek.", mins: "Min.", hrs: "Std.", computed: "berechneter Wert", loading: "Lädt…", device: "Gerät",
      deviceBox: "Wer steuert das?", controlledBy: "Geschaltet von", usedBy: "Benutzt von", noRules: "Keine Regel benutzt dieses Gerät.",
      editVisual: "Visuell bearbeiten", conflictHint: "Mehrere Regeln schalten dieses Gerät.", open: "öffnen", today: "Heute",
      noRoom: "Ohne Raum"
    },
    EN: {
      title: "Rules", rules: "Rules", values: "Values", map: "Relations", plan: "Day plan", changes: "Changes",
      newRule: "New rule", search: "Search…", edit: "Edit", back: "Back", save: "Save", saved: "Saved",
      cancel: "Cancel", ok: "Apply", del: "Delete", code: "Code", visual: "Visual", test: "Test",
      when: "WHEN", and: "AND", or: "OR", then: "THEN", elseif: "ELSE IF", else: "ELSE", oneOf: "one of",
      allOf: "all of", caseN: "Case {n}", comment: "Description (optional)", addCond: "Condition", addGroup: "Group",
      addCmd: "Command", addStep: "Then", addCase: "Else-if case", addElse: "Else case", wait: "after {t}",
      waitEdit: "Wait before this step", noWait: "immediately", trigger: "Trigger: a change starts the rule",
      check: "Check only: doesn't start the rule", chooseDevice: "Choose device", reading: "Reading", value: "Value",
      changes_: "changes", isTrue: "is true", reports: "reports", anyEvent: "Event", at: "at", between: "between",
      every: "every", everyIn: "every {t}", not: "NOT", days: "Days", allDays: "every day", weekend: "weekend",
      workday: "workday", sunrise: "sunrise", sunset: "sunset", offset: "Offset (minutes)",
      clock: "Time", fromReading: "from a reading", timeKind: "Kind", condKind: "Kind of condition",
      k_cmp: "Device has value", k_change: "Device changes", k_event: "Device reports event", k_time: "Time",
      k_range: "Period", k_every: "Regularly", k_code: "Perl expression", k_agg: "Several devices",
      command: "Command", args: "Value / parameters", setreading: "Set reading", fhemcmd: "FHEM command", perl: "Perl",
      cmdKind: "Kind of command", k_set: "Switch device", k_setreading: "Set reading", k_fhem: "FHEM command",
      k_perl: "Perl code", advanced: "Advanced", nowQ: "What would happen now?", nowWould: "Now {c} would be executed.",
      nowNothing: "Now nothing would be executed.", nowBlocked: "{c} was already executed, DOIF doesn't repeat it (see Advanced).",
      nowUnknown: "A part is Perl code and can't be evaluated here.", nowDisabled: "The rule is switched off.",
      waiting: "Waiting: {t}", lastTrigger: "Last triggered by: {t}", simulate: "What would have happened?",
      simDays: "last {n} days", simNone: "Nothing would have been executed in this period.",
      simCount: "{n} executions", simUnknown: "{n} triggers couldn't be evaluated because of Perl code.",
      noHistory: "The simulation needs a timeline device (define timeline fhempy timeline).",
      versions: "Versions", restore: "Restore", noVersions: "No saved versions yet.",
      runNow: "Run now", on: "on", off: "off", enabled: "on", disabled: "off",
      lastRun: "last {t}", never: "never", codeParts: "{n} code parts", allVisual: "fully visual",
      perlMode: "Perl mode: each block runs on its own triggers.", block: "Block", name: "Name",
      alias: "Display name", room: "Room", ruleName: "Name in FHEM", template: "Template", t_empty: "Empty rule",
      t_motion: "Light on motion", t_schedule: "Schedule", t_window: "Window open: heating down",
      t_notify: "Notification", t_irrigation: "Irrigation by weather", t_cook: "Cooking time with reminder",
      health: "Health check", healthOk: "No problems found.", hints: "{n} hints",
      h_conflict: "{d} is switched differently by several rules.", h_flaps: "{n}× fast back and forth in 7 days.",
      h_loop: "These rules trigger each other (loop).", h_selfloop: "This rule switches a device that triggers it.",
      h_missing: "Device missing: {d}", h_dead: "Not executed for more than {n} days.", h_deadNever: "Never executed.",
      h_duplicate: "These rules are identical.", h_error: "Error: {t}", h_unused_value: "Value “{t}” isn't used by any rule.",
      wins: "{r} wins", disableRule: "Switch off", focus: "Focus", house: "whole house", inputs: "Triggers and checks",
      outputs: "Switched devices", time: "Time", why: "Why is it so?", whyQ: "Why does a device have its state?",
      whyCause: "{r} switched at {t}", whyTrigger: "triggered by {t}", whyManual: "No rule switched at this time: probably by hand, an app or the device itself.",
      whyNoChange: "No change found in the last 24 hours.", candidates: "These rules can switch it:",
      planEmpty: "Nothing more planned for today.", nowLine: "now", planTimer: "Time", planWait: "Wait ends",
      planDone: "executed", planAt: "at", noChanges: "No changes yet.", c_created: "created", c_saved: "saved",
      c_modified: "changed in FHEM", c_defined: "created in FHEM", c_deleted: "deleted", c_renamed: "renamed",
      c_restored: "restored", c_enabled: "switched on", c_disabled: "switched off", c_value: "value saved",
      c_value_deleted: "value deleted", newValue: "New value", valueTitle: "Title", unit: "Unit",
      start: "Start with", mul: "× factor", add: "+ add", sub: "− subtract", set: "= replace by", fixed: "fixed value",
      dependsOn: "depending on", onlyIf: "only if", src_reading: "Device", src_history: "History", src_time: "Time/day",
      src_input: "Input", src_value: "other value", m_direct: "direct", m_per: "per unit", m_steps: "steps",
      m_values: "texts", m_linear: "sliding", from: "from", to: "to", result: "Result", otherwise: "otherwise",
      limits: "Limits", min: "at least", max: "at most", round: "round to", useIn: "In rules: {a} (for waiting: {b})",
      f_sum: "Sum", f_min: "Minimum", f_max: "Maximum", f_avg: "Average", f_count: "Number of changes",
      f_since: "Seconds since last change", hours: "of the last hours", hour: "Hour", weekday: "Weekday",
      month: "Month", addRow: "Row", inputsT: "Inputs", newInput: "New input", inputKind: "Kind", number: "Number",
      choice: "Choice", options: "Choices (comma separated)", current: "current", unknown: "unknown", noValues: "No computed values yet.",
      valuesHelp: "A value is calculated like a receipt from top to bottom. fhempy writes the result as reading, every rule can use it.",
      empty: "empty", needDevice: "Please choose a device in every part.", error: "Error", confirmDelete: "Really delete “{n}”? It is kept as version.",
      kinds_all: "All", kinds_light: "Lights", kinds_switch: "Switches", kinds_sensor: "Sensors", kinds_climate: "Heating",
      kinds_blind: "Blinds", kinds_rule: "Rules", stateR: "State", applyCode: "Apply to visual view",
      codeHelp: "Definition and attributes as in FHEM. Unchanged parts are kept exactly when saving.",
      attrsT: "Attributes", q_do: "Execute on every trigger, even if the same case was executed before",
      q_resetwait: "Restart the waiting time on a new trigger (do resetwait)", q_checkall: "Check all cases on events and times",
      q_selftrigger: "May trigger itself", q_timerWithWait: "Plan times again only after the waiting time",
      q_initialize: "State at start", q_repeatsame: "At most this many times in a row", q_cmdpause: "Pause afterwards (seconds)",
      q_waitsame: "Only if triggered twice within seconds", q_waitdel: "Cancel the waiting time when triggered again (seconds)",
      q_cmdState: "State text of this case", q_state: "State of the rule (expression)", q_startup: "Execute at start",
      perCase: "For this case", forRule: "For the whole rule", nothingYet: "No rules yet. Create the first one!",
      p_no_trigger: "Case {c} has no trigger (only checks) and is never executed.",
      p_single_case: "Only one case: DOIF executes it again only after the condition was false in between.",
      p_wait_always: "With “execute on every trigger” the waiting time restarts on every event.",
      p_self_trigger: "The rule switches {d} and is triggered by {d} as well.", fixElse: "Add else case", fixAlways: "Execute every time",
      sec: "s", mins: "min", hrs: "h", computed: "computed value", loading: "Loading…", device: "Device",
      deviceBox: "Who controls this?", controlledBy: "Switched by", usedBy: "Used by", noRules: "No rule uses this device.",
      editVisual: "Edit visually", conflictHint: "Several rules switch this device.", open: "open", today: "Today",
      noRoom: "Without room"
    }
  };

  var OPS = {
    DE: { "==": "ist", "!=": "ist nicht", "<": "kleiner als", ">": "größer als", "<=": "höchstens", ">=": "mindestens",
      eq: "ist", ne: "ist nicht", lt: "vor (Text)", gt: "nach (Text)", le: "bis (Text)", ge: "ab (Text)", "=~": "enthält", "!~": "enthält nicht" },
    EN: { "==": "is", "!=": "is not", "<": "less than", ">": "greater than", "<=": "at most", ">=": "at least",
      eq: "is", ne: "is not", lt: "before (text)", gt: "after (text)", le: "up to (text)", ge: "from (text)", "=~": "contains", "!~": "doesn't contain" }
  };
  var DAYNAMES = { DE: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"], EN: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"] };

  var S = { device: "", lang: "DE", tab: "rules", overview: null, catalog: null, rule: null, model: null, orig: null,
    view: "visual", now: null, sim: null, dirty: false, filter: "", focus: { kind: "house", id: "" }, value: null };

  function t(key, params) {
    var text = (T[S.lang] && T[S.lang][key]) || T.EN[key] || key;
    if (params) Object.keys(params).forEach(function (k) { text = text.split("{" + k + "}").join(params[k]); });
    return text;
  }
  function translit(v) {
    var map = { "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss" };
    return String(v).replace(/[äöüÄÖÜß]/g, function (c) { return map[c]; });
  }
  function esc(v) { return $("<div>").text(v === undefined || v === null ? "" : String(v)).html(); }
  function attr(v) { return esc(v).replace(/"/g, "&quot;"); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function b64(obj) {
    var bytes = new TextEncoder().encode(JSON.stringify(obj)), bin = "";
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    // base64url without padding: FHEM takes "a=b" as named argument
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function cmd(command, cb) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(command) + "&XHR=1", function (r) { if (cb) cb(r); });
  }
  function getJSON(sub, cb) {
    cmd("get " + S.device + " " + sub, function (r) {
      var data;
      try { data = JSON.parse(r); } catch (e) { data = { error: String(r || "") }; }
      cb(data);
    });
  }
  function setCmd(sub, cb) {
    cmd("set " + S.device + " " + sub, function (r) {
      var data = null;
      try { data = JSON.parse(r); } catch (e) { data = null; }
      if (data && data.ok) { cb(null, data); return; }
      if (!r || !String(r).trim()) { cb(null, {}); return; }
      cb(String(r), null);
    });
  }
  // sets with data: FHEM replies empty when fhempy needs longer than 50 ms,
  // then the result is fetched with get reply <rid>
  function setData(sub, data, cb) {
    data = Object.assign({}, data, { rid: Math.random().toString(36).slice(2) });
    cmd("set " + S.device + " " + sub + " " + b64(data), function (r) {
      if (r && String(r).trim()) { finish(String(r)); return; }
      var tries = 0;
      (function poll() {
        getJSON("reply " + data.rid, function (res) {
          if (res.pending && ++tries < 60) { setTimeout(poll, 250); return; }
          finish(res.pending ? "" : res.reply === undefined ? (res.error || "") : String(res.reply || ""));
        });
      })();
    });
    function finish(text) {
      var parsed = null;
      try { parsed = JSON.parse(text); } catch (e) { parsed = null; }
      if (parsed && parsed.ok) cb(null, parsed);
      else if (!text.trim()) cb(null, {});
      else cb(text, null);
    }
  }
  function storageGet(key) { try { return window.localStorage.getItem("fhempyRegeln." + key); } catch (e) { return null; } }
  function storageSet(key, v) { try { window.localStorage.setItem("fhempyRegeln." + key, v); } catch (e) { /* private */ } }
  function ago(ts) {
    if (!ts) return t("never");
    var d = new Date(ts * 1000), now = new Date();
    var hm = pad(d.getHours()) + ":" + pad(d.getMinutes());
    if (d.toDateString() === now.toDateString()) return hm;
    return pad(d.getDate()) + "." + pad(d.getMonth() + 1) + ". " + hm;
  }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function clockOf(ts) { var d = new Date(ts * 1000); return pad(d.getHours()) + ":" + pad(d.getMinutes()); }
  function dayOf(ts) { var d = new Date(ts * 1000); return DAYNAMES[S.lang][d.getDay()] + " " + pad(d.getDate()) + "." + pad(d.getMonth() + 1) + "."; }

  var ICONS = {
    bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>', plus: '<path d="M12 5v14M5 12h14"/>', x: '<path d="M6 6l12 12M18 6 6 18"/>',
    back: '<path d="M15 18l-6-6 6-6"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    code: '<path d="m8 8-5 4 5 4M16 8l5 4-5 4"/>', play: '<path d="M7 5v14l11-7z"/>', check: '<path d="M5 12l5 5 9-10"/>',
    warn: '<path d="M12 3 2 20h20zM12 10v4M12 17v.5"/>', info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.5"/>',
    light: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    plug: '<path d="M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0zM12 17v5"/>', sensor: '<circle cx="12" cy="12" r="3"/><path d="M5 5a10 10 0 0 0 0 14M19 5a10 10 0 0 1 0 14"/>',
    temp: '<path d="M14 14V5a2 2 0 0 0-4 0v9a4 4 0 1 0 4 0z"/>', blind: '<path d="M4 4h16M5 4v12h14V4M5 8h14M5 12h14M12 16v4"/>',
    rule: '<path d="M4 6h10M4 12h16M4 18h7"/><circle cx="18" cy="6" r="2"/>', dev: '<rect x="5" y="3" width="14" height="18" rx="3"/><path d="M10 17h4"/>',
    hist: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5"/>', edit: '<path d="M4 20h4L19 9l-4-4L4 16zM14 6l4 4"/>',
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>', search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    up: '<path d="M6 15l6-6 6 6"/>', down: '<path d="M6 9l6 6 6-6"/>'
  };
  function icon(name, cls) {
    return '<svg class="rg-i ' + (cls || "") + '" viewBox="0 0 24 24">' + (ICONS[name] || "") + "</svg>";
  }
  function kindIcon(kind) {
    return { light: "light", dimmer: "light", switch: "plug", outlet: "plug", blind: "blind", thermostat: "temp",
      temperature: "temp", humidity: "temp", contact: "sensor", motion: "sensor", lock: "sensor" }[kind] || "dev";
  }

  /* ------------------------------------------------------------------ css */

  function css() {
    if ($("#fhempyRegelnCss").length) return;
    $("head").append('<style id="fhempyRegelnCss">' +
      ".rg,.rg-modal-dim{--pg:#EEF0F3;--card:#fff;--line:#E3E6EB;--line2:#EEF0F3;--tx:#1C2128;--mu:#69717D;--mu2:#9AA1AC;--blue:#3D7FC4;--blue2:#E8F1FB;--blue3:#C9DDF3;" +
      "--green:#1E9E5A;--green2:#E5F6EC;--amber:#C77700;--amber2:#FFF4DF;--amber3:#F4D49A;--violet:#6B5BD6;--violet2:#EEEBFD;--red:#D2453F;--red2:#FCE9E8;" +
      "}" +
      ".rg{font-family:Inter,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--tx);font-size:14px;background:var(--pg);border-radius:16px;padding:16px;margin:0 0 16px;max-width:1200px;line-height:1.4;text-align:left}" +
      ".rg *,.rg-modal *{box-sizing:border-box}" +
      ".rg-i{width:18px;height:18px;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none;vertical-align:middle}" +
      ".rg-i,.rg-i *{fill:none!important;stroke:currentColor!important}" +
      ".rg-i.s{width:15px;height:15px}" +
      ".rg-head{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}" +
      ".rg-head h2{font-size:22px;font-weight:700;margin:0;letter-spacing:-.3px}" +
      ".rg-tabs{display:inline-flex;background:#E2E5EA;border-radius:18px;padding:3px;gap:2px;flex-wrap:wrap}" +
      ".rg-tabs a{height:30px;padding:0 14px;border-radius:15px;display:flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--mu);cursor:pointer;text-decoration:none}" +
      ".rg-tabs a.on{background:#fff;color:var(--tx);box-shadow:0 1px 2px rgba(0,0,0,.12)}" +
      ".rg-btn{height:34px;padding:0 14px;border-radius:17px;display:inline-flex;align-items:center;gap:6px;font-size:13.5px;font-weight:600;border:1px solid var(--line);background:#fff;color:var(--tx);white-space:nowrap;cursor:pointer;font-family:inherit}" +
      ".rg-btn.p{background:var(--blue);border-color:var(--blue);color:#fff}.rg-btn.g{background:var(--green);border-color:var(--green);color:#fff}" +
      ".rg-btn.q{background:transparent;border-color:transparent;color:var(--blue)}.rg-btn.sm{height:28px;padding:0 10px;font-size:12.5px}" +
      ".rg-btn.r{color:var(--red)}.rg-btn[disabled]{opacity:.5;cursor:default}" +
      ".rg-ml{margin-left:auto}.rg-mu{color:var(--mu)}.rg-small{font-size:12.5px}" +
      ".rg-card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin-bottom:12px}" +
      ".rg-sh{font-size:12px;color:var(--mu);text-transform:uppercase;letter-spacing:.07em;font-weight:700;margin:14px 0 8px}" +
      ".rg-input,.rg select,.rg textarea,.rg-modal select,.rg-modal textarea{height:34px;border:1px solid var(--line);border-radius:10px;padding:0 10px;font-size:14px;background:#fff;color:var(--tx);font-family:inherit;max-width:100%}" +
      ".rg textarea,.rg-modal textarea{height:auto;padding:8px 10px;font-family:'DejaVu Sans Mono',monospace;font-size:12.5px;width:100%;min-height:70px}" +
      ".rg-list .rg-item{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line2);cursor:pointer}" +
      ".rg-list .rg-item:last-child{border-bottom:0}.rg-list .rg-item:hover{background:#F7F9FB}" +
      ".rg-item .n{font-weight:600}.rg-item .d{color:var(--mu);font-size:12.5px;margin-top:2px}" +
      ".rg-badge{display:inline-flex;align-items:center;gap:5px;height:22px;padding:0 9px;border-radius:11px;font-size:12px;font-weight:600;white-space:nowrap;background:#EDEFF2;color:var(--mu)}" +
      ".rg-badge.g{background:var(--green2);color:var(--green)}.rg-badge.a{background:var(--amber2);color:var(--amber)}.rg-badge.b{background:var(--blue2);color:var(--blue)}.rg-badge.r{background:var(--red2);color:var(--red)}.rg-badge.v{background:var(--violet2);color:var(--violet)}" +
      ".rg-toggle{width:40px;height:24px;border-radius:12px;background:#CBD0D7;position:relative;flex:none;cursor:pointer;border:0}" +
      ".rg-toggle::after{content:'';position:absolute;width:18px;height:18px;border-radius:50%;background:#fff;top:3px;left:3px;box-shadow:0 1px 2px rgba(0,0,0,.2);transition:left .15s}" +
      ".rg-toggle.on{background:var(--green)}.rg-toggle.on::after{left:19px}" +
      ".rg-case{background:#fff;border:1px solid var(--line);border-radius:16px;margin-bottom:12px}" +
      ".rg-case.active{border-color:var(--green);box-shadow:0 0 0 3px rgba(30,158,90,.12)}" +
      ".rg-case .hd{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line2);flex-wrap:wrap}" +
      ".rg-case .hd input{border:0;background:transparent;font-size:13px;color:var(--mu);flex:1;min-width:120px;height:28px}" +
      ".rg-row{display:flex;align-items:center;gap:7px;padding:8px 14px;min-height:46px;flex-wrap:wrap}" +
      ".rg-row+.rg-row{border-top:1px dashed var(--line2)}" +
      ".rg-kw{width:58px;flex:none;font-size:11px;font-weight:800;letter-spacing:.08em;color:var(--mu);cursor:default}" +
      ".rg-kw.then{color:var(--blue)}.rg-kw.click{cursor:pointer;text-decoration:underline dotted}" +
      ".rg-tok{display:inline-flex;align-items:center;gap:6px;min-height:30px;padding:3px 10px;border-radius:9px;font-size:14px;font-weight:600;background:#F2F4F7;border:1px solid transparent;cursor:pointer;max-width:100%;overflow-wrap:anywhere}" +
      ".rg-tok.dev{background:var(--blue2);color:#1F5E9E}.rg-tok.val{background:#fff;border:1px solid var(--line);border-bottom:2px solid var(--blue3)}" +
      ".rg-tok.time{background:var(--violet2);color:#4C3FB0}.rg-tok.act{background:var(--blue);color:#fff}.rg-tok.wait{background:var(--amber2);color:#8A5300}" +
      ".rg-tok.code{background:#2A2F37;color:#E6E9EE;font-family:'DejaVu Sans Mono',monospace;font-weight:400;font-size:12.5px;white-space:pre-wrap}" +
      ".rg-tok.add{background:transparent;border:1px dashed #C4CAD3;color:var(--mu);font-weight:500}.rg-tok.miss{background:var(--red2);color:var(--red)}" +
      ".rg-op{color:var(--mu);font-size:14px}" +
      ".rg-trig{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;flex:none;cursor:pointer;border:0}" +
      ".rg-trig.on{background:#FFF1C9;color:#B07800}.rg-trig.off{background:#F2F4F7;color:#B3B9C2}" +
      ".rg-res{margin-left:auto;display:flex;align-items:center;gap:6px;color:var(--mu);font-size:12.5px}" +
      ".rg-res .ok{color:var(--green)}.rg-res .no{color:var(--red)}" +
      ".rg-x{border:0;background:transparent;color:var(--mu2);cursor:pointer;padding:2px;display:inline-flex}" +
      ".rg-x:hover{color:var(--red)}" +
      ".rg-group{border:1px dashed var(--line);border-radius:12px;padding:4px 0;flex:1;min-width:260px}" +
      ".rg-group .rg-row{padding:5px 10px;min-height:40px}" +
      ".rg-hint{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border-radius:12px;background:var(--amber2);border:1px solid var(--amber3);color:#6E4300;font-size:13px;margin-bottom:8px;flex-wrap:wrap}" +
      ".rg-hint.info{background:var(--blue2);border-color:var(--blue3);color:#1F4F80}.rg-hint.err{background:var(--red2);border-color:#F2C2BF;color:#8A2420}.rg-hint.ok{background:var(--green2);border-color:#BFE6CF;color:#145F38}" +
      ".rg-grid{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:16px;align-items:start}" +
      ".rg-side .rg-card{padding:12px 14px}" +
      ".rg-codep{background:#1F242C;color:#D7DCE3;border-radius:14px;padding:12px;font-family:'DejaVu Sans Mono',monospace;font-size:12.5px}" +
      ".rg-codep textarea{background:#262C35;color:#E6E9EE;border-color:#39414D;min-height:180px}" +
      ".rg-modal-dim{position:fixed;inset:0;background:rgba(28,33,40,.42);z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px}" +
      ".rg-modal{background:#fff;border-radius:18px;box-shadow:0 30px 80px rgba(0,0,0,.28);width:640px;max-width:100%;max-height:92vh;display:flex;flex-direction:column;overflow:hidden;font-family:Inter,-apple-system,'Segoe UI',Roboto,sans-serif;color:#1C2128;font-size:14px;text-align:left}" +
      ".rg-modal .mh{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid #E3E6EB;background:#F7F8FA}.rg-modal .mh h3{font-size:17px;margin:0}" +
      ".rg-modal .mb{padding:14px 18px;overflow:auto;flex:1}.rg-modal .mf{display:flex;gap:10px;padding:12px 18px;border-top:1px solid #E3E6EB;justify-content:flex-end}" +
      ".rg-modal label{display:block;font-size:12px;font-weight:700;color:#69717D;margin:10px 0 4px;text-transform:uppercase;letter-spacing:.05em}" +
      ".rg-modal .rg-input,.rg-modal select{width:100%}" +
      ".rg-modal label.chk{text-transform:none;letter-spacing:0;font-size:14px;font-weight:500;color:#1C2128;display:flex;gap:8px;align-items:center}" +
      ".rg-chips{display:flex;flex-wrap:wrap;gap:6px}.rg-chip{height:32px;padding:0 12px;border-radius:16px;border:1px solid #E3E6EB;display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:#3B434E;background:#fff;cursor:pointer}" +
      ".rg-chip.on{background:#3D7FC4;border-color:#3D7FC4;color:#fff}" +
      ".rg-devs .room{font-size:12px;font-weight:700;color:#69717D;text-transform:uppercase;letter-spacing:.06em;padding:10px 4px 4px}" +
      ".rg-dev{display:flex;align-items:center;gap:10px;padding:7px 8px;border-radius:12px;cursor:pointer}.rg-dev:hover{background:#E8F1FB}" +
      ".rg-dev .ic{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#F2F4F7;color:#59616D;flex:none}" +
      ".rg-dev .t{color:#69717D;font-size:12px}.rg-dev .v{margin-left:auto;font-weight:600;font-size:12.5px;color:#3B434E;white-space:nowrap;max-width:40%;overflow:hidden;text-overflow:ellipsis}" +
      ".rg-receipt .rr{display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px dashed var(--line);flex-wrap:wrap}" +
      ".rg-receipt .rr .sum{margin-left:auto;font-weight:700;font-variant-numeric:tabular-nums}" +
      ".rg-receipt .tot{display:flex;padding:10px 0 0;font-weight:800;font-size:16px}.rg-receipt .tot span:last-child{margin-left:auto}" +
      ".rg-map svg{width:100%;display:block}.rg-map .node{cursor:pointer}" +
      ".rg-plan .pe{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid var(--line2);align-items:center;flex-wrap:wrap}" +
      ".rg-plan .pe.past{opacity:.55}.rg-plan .tm{font-weight:700;width:52px;font-variant-numeric:tabular-nums}" +
      ".rg-plan .nowl{border-top:2px solid var(--red);margin:6px 0;position:relative}.rg-plan .nowl span{position:absolute;top:-10px;left:0;background:var(--red);color:#fff;font-size:11px;font-weight:700;padding:1px 6px;border-radius:6px}" +
      ".rg-sim .se{display:flex;gap:10px;padding:6px 0;border-bottom:1px solid var(--line2);font-size:13px;flex-wrap:wrap}" +
      ".rg-flex{display:flex;gap:8px;align-items:center;flex-wrap:wrap}" +
      ".rg-q{display:flex;gap:10px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line2);flex-wrap:wrap}.rg-q span{flex:1;min-width:200px}" +
      ".rg-msg{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1C2128;color:#fff;padding:10px 16px;border-radius:12px;z-index:10001;font-size:14px;max-width:90vw}" +
      "@media (max-width:820px){.rg-item{flex-wrap:wrap}.rg-item>div{flex-basis:calc(100% - 60px)!important}.rg-item>.rg-badge:first-of-type{margin-left:52px}.rg{padding:10px;border-radius:0;margin:0 0 12px;max-width:calc(100vw - 8px);box-sizing:border-box;overflow:hidden}.rg-grid{grid-template-columns:1fr}.rg-kw{width:auto;flex-basis:100%}.rg-row{padding:8px 10px}" +
      ".rg-head h2{font-size:19px}.rg-tabs{width:100%;overflow:auto;flex-wrap:nowrap}.rg-tabs a{padding:0 10px}.rg-modal-dim{padding:0;align-items:flex-end}.rg-modal{border-radius:18px 18px 0 0;max-height:94vh}}" +
      "</style>");
  }

  /* ---------------------------------------------------------------- modal */

  function modal(title, body, onOk, okText, extraClass) {
    var $dim = $('<div class="rg-modal-dim"><div class="rg-modal ' + (extraClass || "") + '"><div class="mh"><h3>' + esc(title) +
      '</h3><button class="rg-x rg-ml" data-close>' + icon("x") + '</button></div><div class="mb">' + body +
      '</div><div class="mf">' + '<button class="rg-btn" data-close>' + esc(t("cancel")) + "</button>" +
      (onOk ? '<button class="rg-btn p" data-ok>' + esc(okText || t("ok")) + "</button>" : "") + "</div></div></div>");
    $("body").append($dim);
    $dim.on("click", "[data-close]", function () { $dim.remove(); });
    $dim.on("click", function (e) { if (e.target === $dim[0]) $dim.remove(); });
    $dim.on("click", "[data-ok]", function () { if (onOk($dim.find(".mb")) !== false) $dim.remove(); });
    return $dim;
  }
  function toast(text) {
    var $m = $('<div class="rg-msg">' + esc(text) + "</div>");
    $("body").append($m);
    setTimeout(function () { $m.remove(); }, 3500);
  }

  /* -------------------------------------------------------------- catalog */

  function withCatalog(cb) {
    if (S.catalog) { cb(S.catalog); return; }
    getJSON("catalog", function (data) {
      S.catalog = data.devices || [];
      cb(S.catalog);
    });
  }
  function devInfo(name) {
    if (!S.catalog) return null;
    for (var i = 0; i < S.catalog.length; i++) if (S.catalog[i].name === name) return S.catalog[i];
    return null;
  }
  function devLabel(name) {
    if (!name) return t("chooseDevice");
    if (name === "$SELF") return S.lang === "DE" ? "diese Regel" : "this rule";
    if (name === S.device) return t("computed");
    var info = devInfo(name);
    return info && info.alias ? info.alias : name;
  }

  var KINDS = { light: ["light", "dimmer"], switch: ["switch", "outlet"], sensor: ["contact", "motion", "temperature", "humidity", "lock"],
    climate: ["thermostat"], blind: ["blind"] };

  function pickDevice(cb, opts) {
    opts = opts || {};
    withCatalog(function (devices) {
      var kind = "all", query = "";
      var body = '<div class="rg-flex" style="margin-bottom:10px"><input class="rg-input" data-q placeholder="' + attr(t("search")) +
        '" style="flex:1"></div><div class="rg-chips" data-kinds>' +
        ["all", "light", "switch", "sensor", "climate", "blind", "rule"].map(function (k) {
          return '<span class="rg-chip' + (k === "all" ? " on" : "") + '" data-k="' + k + '">' + esc(t("kinds_" + k)) + "</span>";
        }).join("") + '</div><div class="rg-devs" data-list></div>';
      var $m = modal(opts.title || t("chooseDevice"), body, null);
      function draw() {
        var q = query.toLowerCase(), rooms = {};
        devices.forEach(function (d) {
          if (kind === "rule" ? !d.rule : (kind !== "all" && KINDS[kind].indexOf(d.kind) < 0)) return;
          if (q && (d.name + " " + d.alias + " " + d.room + " " + d.type).toLowerCase().indexOf(q) < 0) return;
          var room = (d.room || "-").split(",")[0];
          (rooms[room] = rooms[room] || []).push(d);
        });
        var html = "";
        if (opts.self) html += '<div class="rg-dev" data-dev="' + attr(S.device) + '"><div class="ic">' + icon("rule") + '</div><div><div class="n">' + esc(t("computed")) + '</div><div class="t">' + esc(S.device) + "</div></div></div>";
        Object.keys(rooms).sort().forEach(function (room) {
          html += '<div class="room">' + esc(room) + "</div>";
          rooms[room].slice(0, 200).forEach(function (d) {
            html += '<div class="rg-dev" data-dev="' + attr(d.name) + '"><div class="ic">' + icon(d.rule ? "rule" : kindIcon(d.kind)) +
              '</div><div><div class="n">' + esc(d.alias || d.name) + '</div><div class="t">' + esc(d.alias ? d.name + " · " + d.type : d.type) +
              '</div></div><div class="v">' + esc(d.state) + "</div></div>";
          });
        });
        $m.find("[data-list]").html(html || '<div class="rg-mu">–</div>');
      }
      $m.on("input", "[data-q]", function () { query = this.value; draw(); });
      $m.on("click", "[data-k]", function () { kind = $(this).data("k"); $m.find("[data-k]").removeClass("on"); $(this).addClass("on"); draw(); });
      $m.on("click", "[data-dev]", function () { var n = $(this).attr("data-dev"); $m.remove(); cb(n); });
      draw();
      $m.find("[data-q]").focus();
    });
  }

  function readingOptions(dev, selected) {
    var info = devInfo(dev), names = ["state"];
    if (dev === S.device && S.overview) {
      names = [];
      (S.overview.values || []).forEach(function (v) { names.push(v.name); if (["min", "h"].indexOf(v.unit) >= 0) names.push(v.name + "_s"); });
      (S.overview.inputs || []).forEach(function (v) { names.push(v.name); });
    } else if (info) {
      Object.keys(info.readings || {}).sort().forEach(function (r) { if (r !== "state") names.push(r); });
    }
    if (selected && names.indexOf(selected) < 0) names.push(selected);
    return names.map(function (r) {
      var cur = info && info.readings ? info.readings[r] : "";
      return '<option value="' + attr(r) + '"' + (r === (selected || "state") ? " selected" : "") + ">" + esc(r) + (cur ? " (" + esc(String(cur).slice(0, 30)) + ")" : "") + "</option>";
    }).join("");
  }
  function valueSuggestions(dev, reading) {
    var info = devInfo(dev), list = [];
    if (info) {
      var cur = (info.readings || {})[reading || "state"];
      if (cur !== undefined) list.push(cur);
      if (!reading || reading === "state") info.sets.forEach(function (s) { if (!s.options || s.options === "noArg") list.push(s.cmd); });
    }
    return list.filter(function (v, i) { return list.indexOf(v) === i; }).slice(0, 30)
      .map(function (v) { return '<option value="' + attr(v) + '">'; }).join("");
  }

  /* ----------------------------------------------------- condition model */

  function leafKind(leaf) { return leaf ? leaf.t : ""; }
  function isGroup(n) { return n && (n.t === "and" || n.t === "or"); }
  function nodeAt(tree, path) {
    var node = tree;
    for (var i = 0; i < path.length; i++) node = node.items[path[i]];
    return node;
  }
  function timeLabel(tm) {
    if (!tm) return "?";
    if (tm.k === "clock") return tm.v;
    if (tm.k === "sun") {
      var off = Math.round((tm.offset || 0) / 60);
      return t(tm.event) + (off ? (off > 0 ? " +" : " ") + off + " " + t("mins") : "");
    }
    if (tm.k === "reading") return devLabel(tm.dev) + ":" + tm.reading;
    return tm.v || "?";
  }
  function daysLabel(days) {
    if (!days) return "";
    var parts = String(days).split(/[\s,]+/).filter(Boolean), out = [];
    parts.forEach(function (p) {
      if (/^\d+$/.test(p)) {
        p.split("").forEach(function (c) {
          var n = parseInt(c, 10);
          out.push(n < 7 ? DAYNAMES[S.lang][n] : n === 7 ? t("weekend") : t("workday"));
        });
      } else out.push(p);
    });
    return out.join(", ");
  }
  function valueLabel(v) {
    if (!v) return "?";
    if (v.k === "text") return "„" + v.v + "“";
    if (v.k === "reading") return devLabel(v.dev) + (v.reading ? ":" + v.reading : "");
    return v.v;
  }
  function durationLabel(text) {
    text = String(text || "").trim();
    if (!text || text === "0") return t("noWait");
    if (/^\d+$/.test(text)) {
      var s = parseInt(text, 10);
      if (s % 3600 === 0) return s / 3600 + " " + t("hrs");
      if (s % 60 === 0) return s / 60 + " " + t("mins");
      return s + " " + t("sec");
    }
    var m = text.match(/^\[\??([^:\]]+):([^\]:]+)\]$/);
    if (m) return devLabel(m[1]) === t("computed") ? m[2].replace(/_s$/, "") : devLabel(m[1]) + ":" + m[2];
    return text;
  }

  function leafTokens(leaf, path, res) {
    var p = attr(JSON.stringify(path)), h = "";
    var trigger = ["cmp", "change", "event", "time", "range", "every", "agg"].indexOf(leaf.t) >= 0;
    if (trigger && leaf.t !== "every") {
      h += '<button class="rg-trig ' + (leaf.check ? "off" : "on") + '" data-act="trig" data-path="' + p + '" title="' + attr(leaf.check ? t("check") : t("trigger")) + '">' + icon("bolt", "s") + "</button>";
    }
    if (leaf.not) h += '<span class="rg-op"><b>' + esc(t("not")) + "</b></span>";
    var tok = function (cls, text) { return '<span class="rg-tok ' + cls + '" data-act="leaf" data-path="' + p + '">' + esc(text) + "</span>"; };
    var reading = function () { return leaf.reading && leaf.reading !== "state" ? tok("", leaf.reading) : ""; };
    switch (leaf.t) {
      case "cmp":
        h += tok(leaf.dev ? "dev" : "miss", devLabel(leaf.dev)) + reading() + '<span class="rg-op">' + esc(OPS[S.lang][leaf.op] || leaf.op) + "</span>" + tok("val", valueLabel(leaf.value));
        break;
      case "change":
        h += tok(leaf.dev ? "dev" : "miss", devLabel(leaf.dev)) + reading() + '<span class="rg-op">' + esc(leaf.check ? t("isTrue") : t("changes_")) + "</span>";
        break;
      case "event":
        h += tok(leaf.dev ? "dev" : "miss", devLabel(leaf.dev)) + '<span class="rg-op">' + esc(t("reports")) + "</span>" + tok("val", leaf.regex);
        break;
      case "anyevent":
        h += tok("", t("anyEvent")) + tok("val", leaf.regex);
        break;
      case "time":
        h += '<span class="rg-op">' + esc(t("at")) + "</span>" + tok("time", timeLabel(leaf.at));
        break;
      case "range":
        h += '<span class="rg-op">' + esc(t("between")) + "</span>" + tok("time", timeLabel(leaf.from)) + '<span class="rg-op">' + (S.lang === "DE" ? "und" : "and") + "</span>" + tok("time", timeLabel(leaf.to));
        if (leaf.every) h += tok("time", t("everyIn", { t: timeLabel(leaf.every) }));
        break;
      case "every":
        h += '<span class="rg-op">' + esc(t("every")) + "</span>" + tok("time", timeLabel(leaf.every));
        break;
      case "agg":
        h += tok("dev", (leaf.mode || "#") + " “" + leaf.regex + "”" + (leaf.reading ? ":" + leaf.reading : "") + (leaf.cond ? " (" + leaf.cond + ")" : ""));
        if (leaf.op) h += '<span class="rg-op">' + esc(OPS[S.lang][leaf.op] || leaf.op) + "</span>" + tok("val", valueLabel(leaf.value));
        break;
      default:
        h += '<span class="rg-tok code" data-act="leaf" data-path="' + p + '">' + esc(leaf.text || "") + "</span>";
    }
    if (leaf.days) h += '<span class="rg-tok time" data-act="leaf" data-path="' + p + '">' + esc(daysLabel(leaf.days)) + "</span>";
    if (res) h += '<span class="rg-res">' + (res.current !== null && res.current !== undefined ? esc(String(res.current).slice(0, 40)) : "") +
      (res.result === true ? ' <span class="ok">' + icon("check", "s") + "</span>" : res.result === false ? ' <span class="no">' + icon("x", "s") + "</span>" : "") + "</span>";
    h += '<button class="rg-x" data-act="delleaf" data-path="' + p + '">' + icon("x", "s") + "</button>";
    return h;
  }

  function flattenResults(tree, results) {
    // explain() returns leaves in walk order, assign them to paths
    var map = {}, i = 0;
    (function walk(node, path) {
      if (!node) return;
      if (isGroup(node)) { node.items.forEach(function (it, k) { walk(it, path.concat([k])); }); return; }
      map[JSON.stringify(path)] = results ? results[i++] : null;
    })(tree, []);
    return map;
  }

  function condRows(caseIdx, tree, label, results) {
    var html = "", res = flattenResults(tree, results);
    if (!tree) return "";
    function group(node, path, depth) {
      var out = "";
      node.items.forEach(function (item, k) {
        var p = path.concat([k]);
        var kw = k === 0 ? (depth === 0 ? label : "") : t(node.t);
        var kwHtml = '<span class="rg-kw' + (k > 0 ? " click" : "") + '"' + (k > 0 ? ' data-act="andor" data-path="' + attr(JSON.stringify(path)) + '"' : "") + ">" + esc(kw) + "</span>";
        if (isGroup(item)) {
          out += '<div class="rg-row">' + kwHtml + '<div class="rg-group"><div class="rg-row rg-mu rg-small" style="min-height:24px">' +
            esc(item.t === "or" ? t("oneOf") : t("allOf")) + (item.not ? " (" + esc(t("not")) + ")" : "") +
            '<button class="rg-x rg-ml" data-act="delleaf" data-path="' + attr(JSON.stringify(p)) + '">' + icon("x", "s") + "</button></div>" +
            group(item, p, depth + 1) + '<div class="rg-row"><span class="rg-tok add" data-act="addleaf" data-path="' + attr(JSON.stringify(p)) + '">' + icon("plus", "s") + esc(t("addCond")) + "</span></div></div></div>";
        } else {
          out += '<div class="rg-row">' + kwHtml + leafTokens(item, p, res[JSON.stringify(p)]) + "</div>";
        }
      });
      return out;
    }
    if (isGroup(tree)) html += group(tree, [], 0);
    else html += '<div class="rg-row"><span class="rg-kw">' + esc(label) + "</span>" + leafTokens(tree, [], res["[]"]) + "</div>";
    return html.replace(/data-path="/g, 'data-case="' + caseIdx + '" data-path="');
  }

  /* -------------------------------------------------------- leaf editing */

  function newLeaf(kind) {
    switch (kind) {
      case "cmp": return { t: "cmp", check: false, dev: "", reading: "", fmt: "", op: "eq", value: { k: "text", v: "on" } };
      case "change": return { t: "change", check: false, dev: "", reading: "", fmt: "" };
      case "event": return { t: "event", check: false, dev: "", regex: "on" };
      case "time": return { t: "time", at: { k: "clock", v: "07:00" } };
      case "range": return { t: "range", from: { k: "clock", v: "08:00" }, to: { k: "clock", v: "22:00" }, check: true };
      case "every": return { t: "every", every: { k: "clock", v: "00:15" } };
      default: return { t: "code", text: "1" };
    }
  }

  function timeEditor(key, tm) {
    tm = tm || { k: "clock", v: "07:00" };
    var kind = tm.k === "sun" ? tm.event : tm.k;
    return '<div class="rg-flex" data-time="' + key + '"><select data-tk>' +
      ["clock", "sunrise", "sunset", "reading"].map(function (k) {
        return '<option value="' + k + '"' + (k === kind ? " selected" : "") + ">" + esc(t(k === "reading" ? "fromReading" : k)) + "</option>";
      }).join("") + '</select><input class="rg-input" data-tv style="width:140px" value="' +
      attr(tm.k === "clock" ? tm.v : tm.k === "sun" ? Math.round((tm.offset || 0) / 60) : tm.k === "reading" ? tm.dev + ":" + tm.reading : tm.v || "") +
      '" placeholder="' + attr(tm.k === "sun" ? t("offset") : "07:00") + '"></div>';
  }
  function readTime($root, key) {
    var $b = $root.find('[data-time="' + key + '"]'), k = $b.find("[data-tk]").val(), v = $.trim($b.find("[data-tv]").val());
    if (k === "clock") return { k: "clock", v: v || "00:00" };
    if (k === "reading") { var p = v.split(":"); return { k: "reading", dev: p[0] || "", reading: p[1] || "state" }; }
    var off = parseInt(v, 10) || 0;
    return { k: "sun", event: k, offset: off * 60, raw: "{" + k + "(" + (off ? off * 60 : "") + ")}" };
  }
  function daysEditor(days) {
    var set = String(days || "").replace(/[^0-9]/g, "");
    var opts = [1, 2, 3, 4, 5, 6, 0, 7, 8];
    return '<div class="rg-chips" data-days>' + opts.map(function (n) {
      var label = n < 7 ? DAYNAMES[S.lang][n] : n === 7 ? t("weekend") : t("workday");
      return '<span class="rg-chip' + (set.indexOf(String(n)) >= 0 ? " on" : "") + '" data-day="' + n + '">' + esc(label) + "</span>";
    }).join("") + "</div>";
  }
  function readDays($root) {
    var out = "";
    $root.find("[data-day].on").each(function () { out += $(this).data("day"); });
    return out;
  }

  function editLeaf(leaf, onDone, isNew) {
    withCatalog(function () {
      var kinds = ["cmp", "change", "event", "time", "range", "every", "code"];
      var body = "<label>" + esc(t("condKind")) + '</label><select data-kind>' + kinds.map(function (k) {
        return '<option value="' + k + '"' + (k === leaf.t ? " selected" : "") + ">" + esc(t("k_" + k)) + "</option>";
      }).join("") + (leaf.t === "agg" || leaf.t === "anyevent" ? '<option value="' + leaf.t + '" selected>' + esc(t("k_agg")) + "</option>" : "") +
        '</select><div data-form></div><label class="chk"><input type="checkbox" data-not' + (leaf.not ? " checked" : "") + "> " + esc(t("not")) + "</label>";
      var $m = modal(t("addCond"), body, function ($b) {
        var kind = $b.find("[data-kind]").val(), out = { t: kind };
        if (kind === "cmp" || kind === "change" || kind === "event") {
          out.dev = $b.find("[data-dev]").attr("data-value") || "";
          out.check = !$b.find("[data-trigger]").is(":checked");
          if (kind !== "event") { out.reading = $b.find("[data-reading]").val() || ""; if (out.reading === "state") out.reading = ""; out.fmt = leaf.fmt || ""; }
          if (kind === "cmp") {
            out.op = $b.find("[data-op]").val();
            var raw = $b.find("[data-value]").val();
            var isNum = /^-?\d+(\.\d+)?$/.test(raw) && ["==", "!=", "<", ">", "<=", ">="].indexOf(out.op) >= 0;
            var refm = raw.match(/^\[(\??)([^:\]]+)(?::([^:\]]+))?\]$/);
            out.value = refm ? { k: "reading", dev: refm[2], reading: refm[3] || "", fmt: "", check: refm[1] === "?" } : isNum ? { k: "number", v: raw } : { k: "text", v: raw };
            if (isNum && ["eq", "ne"].indexOf(out.op) >= 0) out.value = { k: "text", v: raw };
          }
          if (kind === "event") out.regex = $b.find("[data-value]").val();
          if (!out.dev) { toast(t("needDevice")); return false; }
        } else if (kind === "time") {
          out.at = readTime($b, "at"); out.check = !$b.find("[data-trigger]").is(":checked");
        } else if (kind === "range") {
          out.from = readTime($b, "from"); out.to = readTime($b, "to"); out.check = !$b.find("[data-trigger]").is(":checked");
          var ev = $.trim($b.find("[data-every]").val() || "");
          if (ev) out.every = { k: "clock", v: ev };
        } else if (kind === "every") {
          out.every = { k: "clock", v: $.trim($b.find("[data-every]").val() || "00:15") };
        } else if (kind === "agg" || kind === "anyevent") {
          out = leaf;
        } else {
          out.text = $b.find("[data-code]").val();
        }
        if (["time", "range", "every"].indexOf(kind) >= 0) { var d = readDays($b); if (d) out.days = d; }
        if (!out.check) delete out.check;
        if (["cmp", "change", "event"].indexOf(kind) >= 0) out.check = !$b.find("[data-trigger]").is(":checked");
        if ($b.find("[data-not]").is(":checked")) out.not = true;
        onDone(out);
      });
      function form() {
        var kind = $m.find("[data-kind]").val(), l = kind === leaf.t ? leaf : newLeaf(kind), h = "";
        var trig = '<label class="chk"><input type="checkbox" data-trigger' + (l.check ? "" : " checked") + "> " + esc(t("trigger")) + "</label>";
        if (kind === "cmp" || kind === "change" || kind === "event") {
          h += "<label>" + esc(t("device")) + '</label><span class="rg-tok ' + (l.dev ? "dev" : "miss") + '" data-dev data-value="' + attr(l.dev) + '">' + esc(l.dev ? devLabel(l.dev) + " (" + l.dev + ")" : t("chooseDevice")) + "</span>";
          if (kind !== "event") h += "<label>" + esc(t("reading")) + '</label><select data-reading>' + readingOptions(l.dev, l.reading || "state") + "</select>";
          if (kind === "cmp") {
            h += "<label>" + esc(t("value")) + '</label><div class="rg-flex"><select data-op style="width:auto">' + Object.keys(OPS[S.lang]).map(function (o) {
              return '<option value="' + attr(o) + '"' + (o === l.op ? " selected" : "") + ">" + esc(OPS[S.lang][o] + " (" + o + ")") + "</option>";
            }).join("") + '</select><input class="rg-input" data-value list="rgSugg" style="flex:1" value="' + attr(l.value ? (l.value.k === "reading" ? "[" + (l.value.check ? "?" : "") + l.value.dev + (l.value.reading ? ":" + l.value.reading : "") + "]" : l.value.v) : "") + '"></div><datalist id="rgSugg">' + valueSuggestions(l.dev, l.reading) + "</datalist>";
          }
          if (kind === "event") h += "<label>" + esc(t("value")) + ' (regex)</label><input class="rg-input" data-value value="' + attr(l.regex) + '">';
          h += trig;
        } else if (kind === "time") {
          h += "<label>" + esc(t("clock")) + "</label>" + timeEditor("at", l.at) + "<label>" + esc(t("days")) + "</label>" + daysEditor(l.days) + trig;
        } else if (kind === "range") {
          h += "<label>" + esc(t("from")) + "</label>" + timeEditor("from", l.from) + "<label>" + esc(t("to")) + "</label>" + timeEditor("to", l.to) +
            "<label>" + esc(t("every")) + ' (HH:MM, optional)</label><input class="rg-input" data-every value="' + attr(l.every ? l.every.v || "" : "") + '">' +
            "<label>" + esc(t("days")) + "</label>" + daysEditor(l.days) + trig;
        } else if (kind === "every") {
          h += "<label>" + esc(t("every")) + ' (HH:MM)</label><input class="rg-input" data-every value="' + attr(l.every ? l.every.v : "00:15") + '">' +
            "<label>" + esc(t("days")) + "</label>" + daysEditor(l.days);
        } else if (kind === "agg" || kind === "anyevent") {
          h += '<p class="rg-mu">' + esc(t("codeHelp")) + "</p>";
        } else {
          h += "<label>" + esc(t("k_code")) + '</label><textarea data-code>' + esc(l.text || "") + "</textarea>";
        }
        $m.find("[data-form]").html(h);
      }
      $m.on("change", "[data-kind]", form);
      $m.on("click", "[data-day]", function () { $(this).toggleClass("on"); });
      $m.on("change", "[data-tk]", function () {
        var k = $(this).val(), $v = $(this).siblings("[data-tv]");
        $v.attr("placeholder", k === "clock" ? "07:00" : k === "reading" ? "device:reading" : t("offset"));
        if (k === "clock") $v.val("07:00"); else if (k === "reading") $v.val(""); else $v.val("0");
      });
      $m.on("click", "[data-dev]", function () {
        var $tok = $(this);
        pickDevice(function (name) {
          $tok.attr("data-value", name).removeClass("miss").addClass("dev").text(devLabel(name) + " (" + name + ")");
          $m.find("[data-reading]").html(readingOptions(name, "state"));
          $m.find("#rgSugg").html(valueSuggestions(name, "state"));
        }, { self: true });
      });
      $m.on("change", "[data-reading]", function () {
        $m.find("#rgSugg").html(valueSuggestions($m.find("[data-dev]").attr("data-value"), $(this).val()));
      });
      form();
      if (["cmp", "change", "event"].indexOf(leaf.t) >= 0 && !leaf.dev) $m.find("[data-dev]").trigger("click");
    });
  }

  function chooseLeafKind(cb) {
    var kinds = ["cmp", "change", "event", "time", "range", "every", "code"];
    var $m = modal(t("addCond"), '<div class="rg-chips">' + kinds.map(function (k) {
      return '<span class="rg-chip" data-k="' + k + '">' + esc(t("k_" + k)) + "</span>";
    }).join("") + "</div>", null);
    $m.on("click", "[data-k]", function () { var k = $(this).data("k"); $m.remove(); cb(k); });
  }

  /* ------------------------------------------------------ command editing */

  function cmdTokens(c, ci, bi, k) {
    var p = 'data-case="' + ci + '" data-block="' + bi + '" data-cmd="' + k + '"';
    var h = "";
    if (c.t === "set") {
      h = '<span class="rg-tok ' + (c.dev ? "dev" : "miss") + '" data-act="cmd" ' + p + ">" + esc(devLabel(c.dev)) + '</span><span class="rg-tok act" data-act="cmd" ' + p + ">" + esc(c.cmd + (c.args ? " " + c.args : "")) + "</span>";
    } else if (c.t === "setreading") {
      h = '<span class="rg-tok dev" data-act="cmd" ' + p + ">" + esc(devLabel(c.dev)) + '</span><span class="rg-op">' + esc(c.reading) + ' =</span><span class="rg-tok val" data-act="cmd" ' + p + ">" + esc(c.value) + "</span>";
    } else {
      h = '<span class="rg-tok code" data-act="cmd" ' + p + ">" + esc(c.t === "perl" ? "{" + c.text + "}" : c.text) + "</span>";
    }
    return h + '<button class="rg-x" data-act="delcmd" ' + p + ">" + icon("x", "s") + "</button>";
  }

  function editCommand(c, onDone, isNew) {
    withCatalog(function () {
      var kinds = ["set", "setreading", "fhem", "perl"];
      var body = "<label>" + esc(t("cmdKind")) + '</label><select data-kind>' + kinds.map(function (k) {
        return '<option value="' + k + '"' + (k === c.t ? " selected" : "") + ">" + esc(t("k_" + k)) + "</option>";
      }).join("") + "</select><div data-form></div>";
      var $m = modal(t("command"), body, function ($b) {
        var kind = $b.find("[data-kind]").val(), out = { t: kind };
        if (kind === "set" || kind === "setreading") {
          out.dev = $b.find("[data-dev]").attr("data-value") || "";
          if (!out.dev) { toast(t("needDevice")); return false; }
          if (kind === "set") { out.cmd = $b.find("[data-cmd]").val() || "on"; out.args = $.trim($b.find("[data-args]").val() || ""); }
          else { out.reading = $.trim($b.find("[data-reading]").val()) || "state"; out.value = $b.find("[data-value]").val(); }
        } else out.text = $b.find("[data-code]").val();
        onDone(out);
      });
      function setOptions(dev, selected) {
        var info = devInfo(dev), sets = info ? info.sets : [];
        var list = sets.map(function (s) { return s.cmd; });
        if (selected && list.indexOf(selected) < 0) list.unshift(selected);
        if (!list.length) list = ["on", "off"];
        return list.map(function (s) { return '<option value="' + attr(s) + '"' + (s === selected ? " selected" : "") + ">" + esc(s) + "</option>"; }).join("");
      }
      function argsHint(dev, command) {
        var info = devInfo(dev);
        if (!info) return "";
        for (var i = 0; i < info.sets.length; i++) {
          if (info.sets[i].cmd === command && info.sets[i].options && info.sets[i].options !== "noArg") {
            var o = info.sets[i].options;
            if (/^slider/.test(o)) { var p = o.split(","); return '<option value="' + attr(p[1] || 0) + '"><option value="' + attr(p[3] || 100) + '">'; }
            return o.split(",").slice(0, 40).map(function (v) { return '<option value="' + attr(v) + '">'; }).join("");
          }
        }
        return "";
      }
      function form() {
        var kind = $m.find("[data-kind]").val(), l = kind === c.t ? c : { t: kind, dev: c.dev || "", cmd: "on", args: "", reading: "", value: "", text: "" }, h = "";
        if (kind === "set" || kind === "setreading") {
          h += "<label>" + esc(t("device")) + '</label><span class="rg-tok ' + (l.dev ? "dev" : "miss") + '" data-dev data-value="' + attr(l.dev) + '">' + esc(l.dev ? devLabel(l.dev) + " (" + l.dev + ")" : t("chooseDevice")) + "</span>";
          if (kind === "set") {
            h += "<label>" + esc(t("command")) + '</label><select data-cmd>' + setOptions(l.dev, l.cmd) + "</select><label>" + esc(t("args")) +
              '</label><input class="rg-input" data-args list="rgArgs" value="' + attr(l.args || "") + '"><datalist id="rgArgs">' + argsHint(l.dev, l.cmd) + "</datalist>";
          } else {
            h += "<label>" + esc(t("reading")) + '</label><input class="rg-input" data-reading value="' + attr(l.reading) + '"><label>' + esc(t("value")) + '</label><input class="rg-input" data-value value="' + attr(l.value) + '">';
          }
        } else {
          h += "<label>" + esc(kind === "perl" ? t("k_perl") : t("k_fhem")) + '</label><textarea data-code>' + esc(l.text || "") + "</textarea>";
        }
        $m.find("[data-form]").html(h);
      }
      $m.on("change", "[data-kind]", form);
      $m.on("click", "[data-dev]", function () {
        var $tok = $(this);
        pickDevice(function (name) {
          $tok.attr("data-value", name).removeClass("miss").addClass("dev").text(devLabel(name) + " (" + name + ")");
          $m.find("[data-cmd]").html(setOptions(name, $m.find("[data-cmd]").val()));
          $m.find("#rgArgs").html(argsHint(name, $m.find("[data-cmd]").val()));
        });
      });
      $m.on("change", "[data-cmd]", function () { $m.find("#rgArgs").html(argsHint($m.find("[data-dev]").attr("data-value"), $(this).val())); });
      form();
      if (!c.dev && c.t === "set") $m.find("[data-dev]").trigger("click");
    });
  }

  function editWait(current, onDone) {
    var text = String(current || "").trim(), unit = "s", num = "";
    if (/^\d+$/.test(text)) {
      var s = parseInt(text, 10);
      if (s && s % 3600 === 0) { unit = "h"; num = s / 3600; } else if (s && s % 60 === 0) { unit = "min"; num = s / 60; } else num = s || "";
    }
    var valueOpts = '<option value="">–</option>';
    ((S.overview && S.overview.values) || []).forEach(function (v) {
      var ref = "[" + S.device + ":" + v.name + (["min", "h"].indexOf(v.unit) >= 0 ? "_s" : "") + "]";
      valueOpts += '<option value="' + attr(ref) + '"' + (ref === text ? " selected" : "") + ">" + esc(v.title || v.name) + "</option>";
    });
    var body = "<label>" + esc(t("waitEdit")) + '</label><div class="rg-flex"><input class="rg-input" data-n type="number" min="0" style="width:120px" value="' + attr(num) +
      '"><select data-u><option value="s"' + (unit === "s" ? " selected" : "") + ">" + esc(t("sec")) + '</option><option value="min"' + (unit === "min" ? " selected" : "") + ">" +
      esc(t("mins")) + '</option><option value="h"' + (unit === "h" ? " selected" : "") + ">" + esc(t("hrs")) + "</option></select></div><label>" + esc(t("computed")) +
      '</label><select data-v>' + valueOpts + "</select><label>" + esc(t("code")) + ' (z.B. [dev:reading])</label><input class="rg-input" data-raw value="' +
      attr(/^\d+$/.test(text) ? "" : text) + '">';
    modal(t("waitEdit"), body, function ($b) {
      var v = $b.find("[data-v]").val(), raw = $.trim($b.find("[data-raw]").val()), n = parseFloat($b.find("[data-n]").val());
      if (v) onDone(v);
      else if (raw) onDone(raw);
      else if (n > 0) onDone(String(Math.round(n * { s: 1, min: 60, h: 3600 }[$b.find("[data-u]").val()])));
      else onDone("");
    });
  }

  /* -------------------------------------------------------------- loading */

  function loadOverview(cb) {
    getJSON("overview", function (data) {
      if (data.error) { $("#fhempyRegeln").html('<div class="rg"><div class="rg-hint err">' + esc(data.error) + "</div></div>"); return; }
      S.overview = data;
      S.lang = data.lang || "DE";
      if (cb) cb();
    });
  }

  function render() {
    var $root = $("#fhempyRegeln");
    if (S.rule) { renderEditor($root); return; }
    var tabs = ["rules", "values", "map", "plan", "changes"];
    var health = (S.overview.health || []).filter(function (f) { return f.severity !== "info"; }).length;
    var html = '<div class="rg"><div class="rg-head"><h2>' + esc(t("title")) + '</h2><div class="rg-tabs">' + tabs.map(function (tab) {
      return '<a class="' + (S.tab === tab ? "on" : "") + '" data-tab="' + tab + '">' + esc(t(tab)) + (tab === "map" && health ? ' <span class="rg-badge a">' + health + "</span>" : "") + "</a>";
    }).join("") + '</div>' + (S.tab === "rules" ? '<button class="rg-btn p rg-ml" data-act="new">' + icon("plus", "s") + esc(t("newRule")) + "</button>" : "") +
      (S.tab === "values" ? '<button class="rg-btn p rg-ml" data-act="newvalue">' + icon("plus", "s") + esc(t("newValue")) + "</button>" : "") +
      '</div><div data-body></div></div>';
    $root.html(html);
    var $body = $root.find("[data-body]");
    if (S.tab === "rules") renderRules($body);
    else if (S.tab === "values") renderValues($body);
    else if (S.tab === "map") renderMap($body);
    else if (S.tab === "plan") renderPlan($body);
    else renderChanges($body);
  }

  /* ----------------------------------------------------------- rule list */

  function renderRules($body) {
    var rules = S.overview.rules || [];
    var q = S.filter.toLowerCase();
    var health = S.overview.health || [];
    var html = "";
    var warn = health.filter(function (f) { return f.severity !== "info"; });
    if (warn.length) html += '<div class="rg-hint" data-act="tab" data-tab="map" style="cursor:pointer">' + icon("warn") + "<span>" + esc(t("health")) + ": " + esc(t("hints", { n: warn.length })) + "</span></div>";
    html += '<div class="rg-flex" style="margin-bottom:10px"><input class="rg-input" data-filter placeholder="' + attr(t("search")) + '" value="' + attr(S.filter) + '" style="flex:1;max-width:420px"></div>';
    if (!rules.length) html += '<div class="rg-card rg-mu">' + esc(t("nothingYet")) + "</div>";
    var groups = {};
    rules.forEach(function (r) {
      var text = (r.name + " " + r.alias + " " + r.comment + " " + r.room + " " + r.reads.join(" ") + " " + r.writes.join(" ")).toLowerCase();
      if (q && text.indexOf(q) < 0) return;
      var room = (r.room || "").split(",").filter(function (x) { return x && x !== "Regeln" && x !== "fhempy"; })[0] || t("noRoom");
      (groups[room] = groups[room] || []).push(r);
    });
    Object.keys(groups).sort().forEach(function (room) {
      html += '<div class="rg-sh">' + esc(room) + '</div><div class="rg-card rg-list" style="padding:0">';
      groups[room].forEach(function (r) {
        var problems = health.filter(function (f) { return f.rules.indexOf(r.name) >= 0 && f.severity !== "info"; }).length;
        var share = r.type === "DOIF" ? (r.visual === r.total ? '<span class="rg-badge g">' + esc(t("allVisual")) + "</span>" : '<span class="rg-badge">' + esc(t("codeParts", { n: r.total - r.visual })) + "</span>") : '<span class="rg-badge v">' + esc(r.type) + "</span>";
        html += '<div class="rg-item" data-act="open" data-rule="' + attr(r.name) + '"><button class="rg-toggle' + (r.disabled ? "" : " on") + '" data-act="toggle" data-rule="' + attr(r.name) + '"></button>' +
          '<div style="min-width:0;flex:1"><div class="n">' + esc(r.alias || r.name) + (r.alias ? ' <span class="rg-mu rg-small">' + esc(r.name) + "</span>" : "") + '</div><div class="d">' +
          esc(r.comment || (r.reads.slice(0, 3).map(devLabel).join(", ") + (r.writes.length ? " → " + r.writes.slice(0, 3).map(devLabel).join(", ") : ""))) + "</div></div>" +
          (problems ? '<span class="rg-badge a">' + icon("warn", "s") + problems + "</span>" : "") + share +
          '<span class="rg-mu rg-small" style="white-space:nowrap">' + esc(t("lastRun", { t: ago(r.last) })) + "</span></div>";
      });
      html += "</div>";
    });
    $body.html(html);
    $body.find("[data-filter]").on("input", function () {
      S.filter = this.value;
      var pos = this.selectionStart;
      renderRules($body);
      var el = $body.find("[data-filter]")[0];
      el.focus(); el.setSelectionRange(pos, pos);
    });
  }

  /* ------------------------------------------------------------- editor */

  function openRule(name) {
    withCatalog(function () {
      getJSON("rule " + name, function (data) {
        if (data.error) { toast(data.error); return; }
        S.rule = data;
        S.model = data.model ? clone(data.model) : null;
        S.orig = JSON.stringify(S.model);
        S.view = data.type === "DOIF" ? "visual" : "code";
        S.code = { def: data.def, attrs: data.attrs };
        S.now = null; S.sim = null; S.dirty = false;
        try { history.replaceState(null, "", "#rule=" + encodeURIComponent(name)); } catch (e) { /* ignore */ }
        render();
        if (S.model && S.model.mode === "fhem") checkNow();
      });
    });
  }

  function closeRule() {
    S.rule = null; S.model = null;
    try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* ignore */ }
    loadOverview(render);
  }

  function markDirty() { S.dirty = true; S.now = null; renderEditor($("#fhempyRegeln")); scheduleNow(); }
  var nowTimer = null;
  function scheduleNow() { clearTimeout(nowTimer); nowTimer = setTimeout(checkNow, 600); }

  function checkNow() {
    if (!S.model || S.model.mode !== "fhem") return;
    getJSON("now " + b64({ model: S.model }), function (data) {
      if (!S.rule) return;
      S.now = data;
      renderEditor($("#fhempyRegeln"));
    });
  }

  function caseName(i) {
    var c = S.model.cases[i];
    return c && c.comment ? "„" + c.comment + "“" : t("caseN", { n: i + 1 });
  }

  function renderEditor($root) {
    var r = S.rule, m = S.model;
    var html = '<div class="rg"><div class="rg-head"><button class="rg-btn q" data-act="close">' + icon("back") + esc(t("back")) + "</button><h2>" +
      esc(r.attrs.alias || r.name) + '</h2><span class="rg-mu rg-small">' + esc(r.type + " · " + r.name) + "</span>";
    if (r.type === "DOIF") {
      html += '<div class="rg-tabs rg-ml"><a class="' + (S.view === "visual" ? "on" : "") + '" data-view="visual">' + esc(t("visual")) + '</a><a class="' + (S.view === "code" ? "on" : "") + '" data-view="code">' + icon("code", "s") + esc(t("code")) + "</a></div>";
    } else html += '<span class="rg-ml"></span>';
    html += '<button class="rg-btn' + (S.dirty || r.isNew ? " p" : "") + '" data-act="save">' + esc(t("save")) + "</button></div>";
    if (r.isNew) {
      html += '<div class="rg-card rg-flex"><label class="rg-mu rg-small">' + esc(t("alias")) + '</label><input class="rg-input" data-meta="alias" value="' + attr(r.attrs.alias || "") + '" style="flex:1;min-width:160px">' +
        '<label class="rg-mu rg-small">' + esc(t("ruleName")) + '</label><input class="rg-input" data-meta="name" value="' + attr(r.name) + '" style="width:200px">' +
        '<label class="rg-mu rg-small">' + esc(t("room")) + '</label><input class="rg-input" data-meta="room" list="rgRooms" value="' + attr(r.attrs.room || "") + '" style="width:160px"><datalist id="rgRooms">' +
        (S.overview.rooms || []).map(function (x) { return '<option value="' + attr(x) + '">'; }).join("") + "</datalist></div>";
    }
    html += '<div class="rg-grid"><div>';
    if (S.view === "code" || !m) html += codeView();
    else if (m.mode === "perl") html += perlView();
    else if (m.error) html += '<div class="rg-hint err">' + esc(m.error) + "</div>" + codeView();
    else html += casesView();
    html += '</div><div class="rg-side">' + sideView() + "</div></div></div>";
    $root.html(html);
  }

  function casesView() {
    var m = S.model, now = S.now || {}, html = "";
    m.cases.forEach(function (c, i) {
      var kind = i === 0 ? "if" : c.cond ? "elseif" : "else";
      var active = now.case === i;
      var results = now.cases && now.cases[i] ? now.cases[i].leaves : null;
      html += '<div class="rg-case' + (active ? " active" : "") + '"><div class="hd"><b>' + esc(t("caseN", { n: i + 1 })) + '</b><input data-act="comment" data-case="' + i + '" placeholder="' + attr(t("comment")) + '" value="' + attr(c.comment || "") + '">' +
        (S.rule.isNew ? "" : '<button class="rg-btn sm q" data-act="run" data-case="' + i + '" title="' + attr(t("runNow")) + '">' + icon("play", "s") + "</button>") +
        (i > 0 ? '<button class="rg-btn sm q" data-act="caseup" data-case="' + i + '">' + icon("up", "s") + "</button>" : "") +
        (m.cases.length > 1 ? '<button class="rg-x" data-act="delcase" data-case="' + i + '">' + icon("trash", "s") + "</button>" : "") + "</div>";
      if (kind !== "else") {
        html += condRows(i, c.cond, i === 0 ? t("when") : t("elseif"), results);
        html += '<div class="rg-row"><span class="rg-kw"></span><span class="rg-tok add" data-act="addleaf" data-case="' + i + '" data-path="[]">' + icon("plus", "s") + esc(t("addCond")) +
          '</span><span class="rg-tok add" data-act="addgroup" data-case="' + i + '">' + icon("plus", "s") + esc(t("addGroup")) + "</span></div>";
      } else {
        html += '<div class="rg-row"><span class="rg-kw">' + esc(t("else")) + '</span><span class="rg-mu rg-small">' + esc(S.lang === "DE" ? "wenn keiner der Fälle davor zutrifft" : "if none of the cases before applies") + "</span></div>";
      }
      c.blocks.forEach(function (b, bi) {
        html += '<div class="rg-row"><span class="rg-kw then">' + esc(bi === 0 ? t("then") : "") + "</span>" +
          '<span class="rg-tok wait" data-act="wait" data-case="' + i + '" data-block="' + bi + '">' + icon("clock", "s") + esc(b.wait && b.wait !== "0" ? t("wait", { t: durationLabel(b.wait) }) : t("noWait")) + "</span>";
        b.cmds.forEach(function (cm, k) { html += cmdTokens(cm, i, bi, k); });
        html += '<span class="rg-tok add" data-act="addcmd" data-case="' + i + '" data-block="' + bi + '">' + icon("plus", "s") + esc(t("addCmd")) + "</span>" +
          (c.blocks.length > 1 ? '<button class="rg-x" data-act="delblock" data-case="' + i + '" data-block="' + bi + '">' + icon("trash", "s") + "</button>" : "") + "</div>";
      });
      html += '<div class="rg-row"><span class="rg-kw"></span><span class="rg-tok add" data-act="addblock" data-case="' + i + '">' + icon("plus", "s") + esc(t("addStep")) + "</span></div>";
      html += caseAdvanced(c, i);
      html += "</div>";
    });
    var hasElse = m.cases.length > 1 && !m.cases[m.cases.length - 1].cond;
    html += '<div class="rg-flex"><button class="rg-btn" data-act="addcase">' + icon("plus", "s") + esc(t("addCase")) + "</button>" +
      (hasElse ? "" : '<button class="rg-btn" data-act="addelse">' + icon("plus", "s") + esc(t("addElse")) + "</button>") + "</div>";
    html += ruleAdvanced();
    return html;
  }

  var CASE_Q = ["repeatsame", "cmdpause", "waitsame", "waitdel", "cmdState"];
  function caseAdvanced(c, i) {
    var a = c.attrs || {}, open = CASE_Q.some(function (k) { return a[k]; });
    var h = '<details style="padding:4px 14px 10px"' + (open ? " open" : "") + '><summary class="rg-mu rg-small" style="cursor:pointer">' + esc(t("advanced")) + " · " + esc(t("perCase")) + "</summary>";
    CASE_Q.forEach(function (k) {
      h += '<div class="rg-q"><span>' + esc(t("q_" + k)) + '</span><input class="rg-input" data-act="caseattr" data-case="' + i + '" data-attr="' + k + '" value="' + attr(a[k] || "") + '" style="width:140px"></div>';
    });
    return h + "</details>";
  }

  function ruleAdvanced() {
    var a = S.model.attrs || {};
    var doVal = a["do"] || "";
    var h = '<details class="rg-card" style="margin-top:12px"' + (doVal || a.checkall || a.selftrigger ? " open" : "") + '><summary style="cursor:pointer;font-weight:600">' + esc(t("advanced")) + " · " + esc(t("forRule")) + "</summary>";
    h += '<div class="rg-q"><span>' + esc(t("q_do")) + '</span><input type="checkbox" data-act="attrcheck" data-attr="do" data-on="always"' + (/always/.test(doVal) ? " checked" : "") + "></div>";
    h += '<div class="rg-q"><span>' + esc(t("q_resetwait")) + '</span><input type="checkbox" data-act="attrcheck" data-attr="do" data-on="resetwait"' + (/resetwait/.test(doVal) ? " checked" : "") + "></div>";
    h += '<div class="rg-q"><span>' + esc(t("q_checkall")) + '</span><select data-act="attrset" data-attr="checkall">' + ["", "event", "timer", "all"].map(function (v) {
      return '<option value="' + v + '"' + ((a.checkall || "") === v ? " selected" : "") + ">" + esc(v || "–") + "</option>";
    }).join("") + "</select></div>";
    h += '<div class="rg-q"><span>' + esc(t("q_selftrigger")) + '</span><select data-act="attrset" data-attr="selftrigger">' + ["", "wait", "all"].map(function (v) {
      return '<option value="' + v + '"' + ((a.selftrigger || "") === v ? " selected" : "") + ">" + esc(v || "–") + "</option>";
    }).join("") + "</select></div>";
    h += '<div class="rg-q"><span>' + esc(t("q_timerWithWait")) + '</span><input type="checkbox" data-act="attrcheck" data-attr="timerWithWait" data-on="1"' + (a.timerWithWait ? " checked" : "") + "></div>";
    ["initialize", "state", "startup"].forEach(function (k) {
      h += '<div class="rg-q"><span>' + esc(t("q_" + k)) + '</span><input class="rg-input" data-act="attrset" data-attr="' + k + '" value="' + attr(a[k] || "") + '" style="width:220px"></div>';
    });
    var other = Object.keys(a).filter(function (k) { return ["do", "checkall", "selftrigger", "timerWithWait", "initialize", "state", "startup"].indexOf(k) < 0; });
    if (other.length) {
      h += '<div class="rg-sh">' + esc(t("attrsT")) + "</div>";
      other.forEach(function (k) {
        h += '<div class="rg-q"><span class="rg-small"><b>' + esc(k) + '</b></span><input class="rg-input" data-act="attrset" data-attr="' + attr(k) + '" value="' + attr(a[k]) + '" style="flex:2;min-width:200px"></div>';
      });
    }
    return h + "</details>";
  }

  function perlView() {
    var html = '<div class="rg-hint info">' + icon("info") + "<span>" + esc(t("perlMode")) + "</span></div>";
    S.model.blocks.forEach(function (b, i) {
      html += '<div class="rg-case"><div class="hd"><b>' + esc(t("block") + " " + (b.name || i + 1)) + "</b></div>";
      if (b.visual) {
        html += condRows("p" + i, b.visual.cond, t("when"), null).replace(/data-act="[a-z]+"/g, "");
        html += '<div class="rg-row"><span class="rg-kw then">' + esc(t("then")) + "</span>" + b.visual.cmds.map(function (c) { return cmdTokens(c, "p", i, 0).replace(/data-act="[a-z]+"/g, ""); }).join("") + "</div>";
      }
      html += '<div style="padding:8px 14px 12px"><textarea data-act="perlcode" data-block="' + i + '" rows="6">' + esc(b.code) + "</textarea></div></div>";
    });
    return html;
  }

  function codeView() {
    var code = S.code || { def: "", attrs: {} };
    var attrs = Object.keys(code.attrs || {}).filter(function (k) { return code.attrs[k] !== null && code.attrs[k] !== "" && (S.rule.type !== "DOIF" || DOIF_ATTRS.indexOf(k) >= 0); })
      .map(function (k) { return k + " " + code.attrs[k]; }).join("\n");
    return '<div class="rg-codep"><div class="rg-mu rg-small" style="color:#9AA3AF;margin-bottom:8px">' + esc(t("codeHelp")) + '</div><textarea data-code="def" rows="12">' + esc(code.def) +
      '</textarea><div class="rg-small" style="color:#9AA3AF;margin:10px 0 6px">' + esc(t("attrsT")) + ' (Name Wert)</div><textarea data-code="attrs" rows="5" style="min-height:90px">' + esc(attrs) + "</textarea>" +
      (S.rule.type === "DOIF" ? '<div style="margin-top:10px"><button class="rg-btn sm" data-act="applycode">' + esc(t("applyCode")) + "</button></div>" : "") + "</div>";
  }
  var DOIF_ATTRS = ["do", "checkall", "initialize", "selftrigger", "timerevent", "timerWithWait", "notexist", "checkReadingEvent", "addStateEvent", "startup", "state", "setList",
    "readingList", "uiTable", "uiState", "DOIF_Readings", "event_Readings", "weekdays", "wait", "repeatsame", "repeatcmd", "cmdpause", "waitsame", "waitdel", "cmdState"];

  function readCodeView() {
    var $r = $("#fhempyRegeln"), def = $r.find('[data-code="def"]').val(), attrs = {};
    if (def === undefined) return null;
    String($r.find('[data-code="attrs"]').val() || "").split("\n").forEach(function (line) {
      var m = line.match(/^\s*(\S+)\s+([\s\S]*)$/);
      if (m) attrs[m[1]] = m[2];
    });
    return { def: def, attrs: attrs };
  }

  function sideView() {
    var r = S.rule, now = S.now, h = "";
    if (S.model && S.model.mode === "fhem" && !S.model.error) {
      h += '<div class="rg-card"><div class="rg-flex"><b>' + esc(t("nowQ")) + '</b><button class="rg-btn sm q rg-ml" data-act="now">' + icon("hist", "s") + "</button></div>";
      if (!now) h += '<div class="rg-mu rg-small">' + esc(t("loading")) + "</div>";
      else {
        if (now.disabled) h += '<div class="rg-hint">' + esc(t("nowDisabled")) + "</div>";
        if (now.case === "unknown") h += '<div class="rg-hint info">' + esc(t("nowUnknown")) + "</div>";
        else if (typeof now.case === "number") {
          h += '<div class="rg-hint ' + (now.blocked ? "info" : "ok") + '">' + esc(now.blocked ? t("nowBlocked", { c: caseName(now.case) }) : t("nowWould", { c: caseName(now.case) })) + "</div>";
        } else h += '<div class="rg-hint info">' + esc(t("nowNothing")) + "</div>";
        if (now.wait_timer && now.wait_timer !== "no timer") h += '<div class="rg-hint">' + icon("clock") + esc(t("waiting", { t: now.wait_timer })) + "</div>";
        if (now.cmd_event) h += '<div class="rg-mu rg-small">' + esc(t("lastTrigger", { t: now.cmd_event })) + "</div>";
        (now.hints || []).forEach(function (p) {
          h += '<div class="rg-hint">' + icon("warn") + "<span>" + esc(t("p_" + p.kind, { c: (p["case"] || 0) + 1, d: devLabel(p.device) })) + "</span>" +
            (p.fix === "do_always" ? '<button class="rg-btn sm" data-act="fixelse">' + esc(t("fixElse")) + '</button><button class="rg-btn sm" data-act="fixalways">' + esc(t("fixAlways")) + "</button>" : "") + "</div>";
        });
      }
      h += "</div>";
      h += '<div class="rg-card rg-sim"><div class="rg-flex"><b>' + esc(t("simulate")) + '</b><select data-act="simdays" class="rg-ml">' + [1, 3, 7, 14].map(function (d) {
        return '<option value="' + d + '"' + ((S.simDays || 7) === d ? " selected" : "") + ">" + esc(t("simDays", { n: d })) + "</option>";
      }).join("") + '</select><button class="rg-btn sm" data-act="simulate">' + icon("play", "s") + esc(t("test")) + "</button></div>" + simView() + "</div>";
    }
    if (!r.isNew) {
      h += '<div class="rg-card"><div class="rg-flex"><b>' + esc(t("versions")) + '</b><button class="rg-btn sm q rg-ml" data-act="versions">' + icon("hist", "s") + esc(r.versions || 0) + "</button></div><div data-versions></div>" +
        '<div class="rg-flex" style="margin-top:10px"><button class="rg-btn sm r" data-act="delrule">' + icon("trash", "s") + esc(t("del")) + "</button></div></div>";
    }
    return h;
  }

  function simView() {
    var sim = S.sim;
    if (!sim) return "";
    if (sim.loading) return '<div class="rg-mu rg-small">' + esc(t("loading")) + "</div>";
    if (sim.error) return '<div class="rg-hint info">' + esc(sim.error === "no_history" ? t("noHistory") : sim.error) + "</div>";
    var h = '<div class="rg-mu rg-small" style="margin:8px 0">' + esc(sim.count ? t("simCount", { n: sim.count }) : t("simNone")) + "</div>";
    if (sim.unknown) h += '<div class="rg-hint info rg-small">' + esc(t("simUnknown", { n: sim.unknown })) + "</div>";
    var lastDay = "";
    sim.executions.slice(-80).reverse().forEach(function (e) {
      var day = dayOf(e.ts);
      if (day !== lastDay) { h += '<div class="rg-sh">' + esc(day) + "</div>"; lastDay = day; }
      h += '<div class="se"><b>' + esc(clockOf(e.ts)) + "</b><span>" + esc(caseName(e["case"])) + '</span><span class="rg-mu">' + esc(e.trigger) + "</span>" +
        '<span class="rg-small" style="flex-basis:100%;color:#1F5E9E">' + esc((sim.commands[e["case"]] || []).join("; ")) + "</span></div>";
    });
    return h;
  }

  /* --------------------------------------------------------- editor actions */

  function bindEditor($root) {
    $root.on("click", "[data-act]", function (e) {
      if (!S.rule) return;
      var $t = $(this), act = $t.data("act"), ci = $t.data("case"), m = S.model;
      var path = $t.attr("data-path") ? JSON.parse($t.attr("data-path")) : null;
      var c = m && m.cases && typeof ci === "number" ? m.cases[ci] : null;
      e.stopPropagation();
      switch (act) {
        case "close":
          if (S.dirty && !window.confirm(S.lang === "DE" ? "Änderungen verwerfen?" : "Discard changes?")) return;
          closeRule(); break;
        case "save": saveRule(); break;
        case "trig":
          var lf = nodeAt(c.cond, path); lf.check = !lf.check; markDirty(); break;
        case "leaf":
          editLeaf(clone(nodeAt(c.cond, path)), function (leaf) { replaceNode(c, path, leaf); markDirty(); }); break;
        case "delleaf": removeNode(c, path); markDirty(); break;
        case "andor":
          var g = path.length ? nodeAt(c.cond, path) : c.cond; g.t = g.t === "and" ? "or" : "and"; markDirty(); break;
        case "addleaf":
          chooseLeafKind(function (kind) {
            editLeaf(newLeaf(kind), function (leaf) { addNode(c, path || [], leaf); markDirty(); }, true);
          }); break;
        case "addgroup":
          addNode(c, [], { t: "or", items: [] }); markDirty(); break;
        case "cmd":
          var bc = m.cases[ci].blocks[$t.data("block")].cmds, k = $t.data("cmd");
          editCommand(clone(bc[k]), function (cmdv) { bc[k] = cmdv; markDirty(); }); break;
        case "delcmd": m.cases[ci].blocks[$t.data("block")].cmds.splice($t.data("cmd"), 1); markDirty(); break;
        case "addcmd":
          var blk = m.cases[ci].blocks[$t.data("block")];
          editCommand({ t: "set", dev: "", cmd: "on", args: "" }, function (cmdv) { blk.cmds.push(cmdv); markDirty(); }, true); break;
        case "wait":
          var b = m.cases[ci].blocks[$t.data("block")];
          editWait(b.wait, function (w) { b.wait = w; markDirty(); }); break;
        case "addblock": c.blocks.push({ cmds: [], wait: "" }); markDirty(); break;
        case "delblock": c.blocks.splice($t.data("block"), 1); markDirty(); break;
        case "addcase":
          var pos = m.cases.length && !m.cases[m.cases.length - 1].cond && m.cases.length > 1 ? m.cases.length - 1 : m.cases.length;
          m.cases.splice(pos, 0, { kind: "elseif", cond: { t: "and", items: [] }, blocks: [{ cmds: [], wait: "" }], comment: "", attrs: {} });
          markDirty(); break;
        case "addelse":
        case "fixelse":
          m.cases.push({ kind: "else", cond: null, blocks: [{ cmds: [], wait: "" }], comment: "", attrs: {} }); markDirty(); break;
        case "fixalways": m.attrs = m.attrs || {}; m.attrs["do"] = "always"; markDirty(); break;
        case "delcase": m.cases.splice(ci, 1); fixKinds(); markDirty(); break;
        case "caseup":
          var moved = m.cases.splice(ci, 1)[0]; m.cases.splice(ci - 1, 0, moved); fixKinds(); markDirty(); break;
        case "run":
          setCmd("run " + S.rule.name + " " + (ci + 1), function (err) { toast(err || "cmd_" + (ci + 1)); setTimeout(checkNow, 800); }); break;
        case "now": checkNow(); break;
        case "simulate": simulate(); break;
        case "versions": showVersions(); break;
        case "delrule":
          if (!window.confirm(t("confirmDelete", { n: S.rule.name }))) return;
          setCmd("delete_rule " + S.rule.name, function (err) { if (err) toast(err); else closeRule(); }); break;
        case "applycode":
          var code = readCodeView();
          getJSON("parse " + b64({ def: code.def, attrs: code.attrs, name: S.rule.name }), function (data) {
            if (data.model) { S.model = data.model; S.view = "visual"; S.code = code; markDirty(); }
          }); break;
        case "restore":
          setCmd("restore " + S.rule.name + " " + $t.data("version"), function (err) { if (err) toast(err); else { toast(t("saved")); openRule(S.rule.name); } }); break;
      }
    });
    $root.on("click", "[data-view]", function () {
      var view = $(this).data("view");
      if (view === S.view) return;
      if (view === "code" && S.model) {
        getJSON("code " + b64({ model: S.model }), function (data) { S.code = { def: data.def, attrs: data.attrs }; S.view = "code"; renderEditor($root); });
      } else {
        var code = readCodeView();
        if (code && S.code && (code.def !== S.code.def || JSON.stringify(code.attrs) !== JSON.stringify(cleanAttrs(S.code.attrs)))) {
          getJSON("parse " + b64({ def: code.def, attrs: code.attrs, name: S.rule.name }), function (data) {
            S.model = data.model; S.code = code; S.view = "visual"; markDirty();
          });
        } else { S.view = "visual"; renderEditor($root); }
      }
    });
    $root.on("change", "[data-act=comment]", function () { S.model.cases[$(this).data("case")].comment = this.value; S.dirty = true; });
    $root.on("change", "[data-act=caseattr]", function () {
      var c = S.model.cases[$(this).data("case")]; c.attrs = c.attrs || {};
      if (this.value) c.attrs[$(this).data("attr")] = this.value; else delete c.attrs[$(this).data("attr")];
      markDirty();
    });
    $root.on("change", "[data-act=attrset]", function () {
      S.model.attrs = S.model.attrs || {};
      if (this.value) S.model.attrs[$(this).data("attr")] = this.value; else delete S.model.attrs[$(this).data("attr")];
      markDirty();
    });
    $root.on("change", "[data-act=attrcheck]", function () {
      var a = S.model.attrs = S.model.attrs || {}, name = $(this).data("attr"), on = $(this).data("on");
      if (name === "do") {
        var parts = (a["do"] || "").split(/\s+/).filter(function (x) { return x && x !== on; });
        if (this.checked) parts.push(on);
        if (parts.length) a["do"] = parts.join(" "); else delete a["do"];
      } else if (this.checked) a[name] = String(on); else delete a[name];
      markDirty();
    });
    $root.on("change", "[data-act=perlcode]", function () {
      var b = S.model.blocks[$(this).data("block")]; b.code = this.value; b.visual = null; S.dirty = true;
    });
    $root.on("change", "[data-act=simdays]", function () { S.simDays = parseInt(this.value, 10); });
    $root.on("input", "[data-code]", function () { S.dirty = true; });
    $root.on("change", "[data-meta]", function () {
      var k = $(this).data("meta");
      if (k === "name") S.rule.name = this.value.replace(/[^A-Za-z0-9._]/g, "_");
      else S.rule.attrs[k] = this.value;
    });
  }

  function cleanAttrs(attrs) {
    var out = {};
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] !== null && attrs[k] !== "" && (S.rule.type !== "DOIF" || DOIF_ATTRS.indexOf(k) >= 0)) out[k] = attrs[k]; });
    return out;
  }

  function fixKinds() {
    S.model.cases.forEach(function (c, i) {
      if (i === 0 && !c.cond) c.cond = { t: "and", items: [] };
      c.kind = i === 0 ? "if" : c.cond ? "elseif" : "else";
    });
  }
  function replaceNode(c, path, node) {
    if (!path.length) { c.cond = node; return; }
    var parent = nodeAt(c.cond, path.slice(0, -1));
    parent.items[path[path.length - 1]] = node;
  }
  function removeNode(c, path) {
    if (!path.length) { c.cond = { t: "and", items: [] }; return; }
    var parent = nodeAt(c.cond, path.slice(0, -1));
    parent.items.splice(path[path.length - 1], 1);
    if (parent === c.cond && parent.items.length === 1 && !parent.not) c.cond = parent.items[0];
  }
  function addNode(c, path, node) {
    if (!c.cond) { c.cond = node; return; }
    var target = path.length ? nodeAt(c.cond, path) : c.cond;
    if (isGroup(target)) { target.items.push(node); return; }
    c.cond = { t: "and", items: [c.cond, node] };
  }

  function missingDevices() {
    var missing = false;
    (function walk(n) {
      if (!n) return;
      if (isGroup(n)) { n.items.forEach(walk); if (!n.items.length) missing = true; return; }
      if (["cmp", "change", "event"].indexOf(n.t) >= 0 && !n.dev) missing = true;
    })(null);
    S.model.cases.forEach(function (c, i) {
      (function walk(n) {
        if (!n) { if (i === 0) missing = true; return; }
        if (isGroup(n)) { if (!n.items.length) missing = true; n.items.forEach(walk); return; }
        if (["cmp", "change", "event"].indexOf(n.t) >= 0 && !n.dev) missing = true;
      })(c.cond === undefined ? null : c.cond);
      c.blocks.forEach(function (b) { b.cmds.forEach(function (cm) { if ((cm.t === "set" || cm.t === "setreading") && !cm.dev) missing = true; }); });
    });
    return missing;
  }

  function saveRule() {
    var r = S.rule, data = { name: r.name, type: r.type, "new": !!r.isNew, title: r.attrs.alias || r.name };
    if (r.isNew) { data.alias = r.attrs.alias || ""; data.room = r.attrs.room || ""; }
    if (S.view === "code" || !S.model) {
      var code = readCodeView();
      data.def = code.def; data.attrs = code.attrs;
      if (S.model && S.model.mode === "fhem") {
        // keep attributes the editor manages but the user removed in the text
        DOIF_ATTRS.forEach(function (k) { if (!(k in data.attrs)) data.attrs[k] = null; });
      }
    } else {
      if (S.model.mode === "fhem" && missingDevices()) { toast(t("needDevice")); return; }
      data.model = S.model;
    }
    setData("save", data, function (err, result) {
      if (err) { modal(t("error"), '<div class="rg-hint err" style="white-space:pre-wrap">' + esc(err) + "</div>", null); return; }
      toast(t("saved"));
      S.catalog = null;
      openRule(result && result.name ? result.name : r.name);
    });
  }

  function simulate() {
    S.sim = { loading: true };
    renderEditor($("#fhempyRegeln"));
    getJSON("simulate " + b64({ model: S.model, days: S.simDays || 7 }), function (data) {
      S.sim = data;
      renderEditor($("#fhempyRegeln"));
    });
  }

  function showVersions() {
    getJSON("versions " + S.rule.name, function (data) {
      var list = data.versions || [];
      var h = list.length ? "" : '<div class="rg-mu">' + esc(t("noVersions")) + "</div>";
      list.slice().reverse().forEach(function (v, i) {
        var idx = list.length - 1 - i;
        h += '<details class="rg-card" style="padding:8px 12px"><summary class="rg-flex" style="cursor:pointer"><b>' + esc(ago(v.ts)) + "</b> <span class=\"rg-mu rg-small\">" + esc(v.note || "") +
          '</span></summary><pre style="white-space:pre-wrap;font-size:12px;background:#F6F7F9;padding:8px;border-radius:8px">' + esc(v.def) + "\n" +
          esc(Object.keys(v.attrs || {}).map(function (k) { return "attr " + k + " " + v.attrs[k]; }).join("\n")) + '</pre><button class="rg-btn sm" data-restore="' + idx + '">' + esc(t("restore")) + "</button></details>";
      });
      var $m = modal(t("versions") + " · " + S.rule.name, h, null);
      $m.on("click", "[data-restore]", function () {
        var idx = $(this).data("restore");
        $m.remove();
        setCmd("restore " + S.rule.name + " " + idx, function (err) { if (err) toast(err); else { toast(t("saved")); openRule(S.rule.name); } });
      });
    });
  }

  /* ------------------------------------------------------------ new rules */

  function L(dev, reading, op, value, check) {
    var num = /^-?\d+(\.\d+)?$/.test(value) && ["==", "!=", "<", ">", "<=", ">="].indexOf(op) >= 0;
    return { t: "cmp", check: !!check, dev: dev, reading: reading || "", fmt: "", op: op, value: num ? { k: "number", v: value } : { k: "text", v: value } };
  }
  function C(kind, cond, blocks, comment) {
    return { kind: kind, cond: cond, blocks: blocks.map(function (b) { return { cmds: b.cmds, wait: b.wait || "" }; }), comment: comment || "", attrs: {} };
  }
  function SET(dev, c, args) { return { t: "set", dev: dev, cmd: c, args: args || "" }; }

  function templates() {
    var ed = S.device;
    return {
      empty: { cases: [C("if", { t: "and", items: [] }, [{ cmds: [] }])] },
      motion: { cases: [
        C("if", L("", "", "eq", "motion"), [{ cmds: [SET("", "on")] }], S.lang === "DE" ? "Bewegung: Licht an" : "Motion: light on"),
        C("else", null, [{ cmds: [SET("", "off")], wait: "120" }], S.lang === "DE" ? "Keine Bewegung: nach 2 Minuten aus" : "No motion: off after 2 minutes")] },
      schedule: { cases: [
        C("if", { t: "time", at: { k: "clock", v: "07:00" }, days: "8" }, [{ cmds: [SET("", "on")] }], S.lang === "DE" ? "Werktags morgens" : "Workday mornings"),
        C("elseif", { t: "time", at: { k: "clock", v: "22:00" } }, [{ cmds: [SET("", "off")] }], S.lang === "DE" ? "Abends aus" : "Off in the evening")] },
      window: { cases: [
        C("if", L("", "", "eq", "open"), [{ cmds: [SET("", "desired-temp", "5")], wait: "60" }], S.lang === "DE" ? "Fenster eine Minute offen" : "Window open for a minute"),
        C("else", null, [{ cmds: [SET("", "desired-temp", "21")] }])] },
      notify: { cases: [C("if", L("", "", "eq", "open"), [{ cmds: [{ t: "fhem", text: "set push message " + (S.lang === "DE" ? "Achtung" : "Attention") }], wait: "600" }])],
        attrs: {} },
      irrigation: { cases: [C("if", { t: "and", items: [{ t: "time", at: { k: "clock", v: "06:00" } }, L(ed, "Regen_48h", "<", "1", true)] },
        [{ cmds: [SET("", "on")] }, { cmds: [SET("", "off")], wait: "[" + ed + ":Bewaesserung_s]" }], S.lang === "DE" ? "Morgens, wenn es 2 Tage nicht geregnet hat" : "Mornings without rain for 2 days")],
        attrs: { "do": "always" },
        values: [
          { title: "Regen 48h", name: "Regen_48h", unit: "mm", rows: [{ op: "start", amount: { k: "source", source: { k: "history", dev: "", reading: "rain", func: "sum", hours: 48 }, map: { mode: "direct" } } }] },
          { title: "Bewässerung", name: "Bewaesserung", unit: "min", min: "5", max: "40", round: "1", rows: [
            { op: "start", amount: { k: "fixed", v: 20 } },
            { op: "mul", amount: { k: "source", source: { k: "reading", dev: "", reading: "condition" }, map: { mode: "values", values: [{ value: "sunny", v: 100 }, { value: "cloudy", v: 80 }], "else": 90 } } },
            { op: "add", amount: { k: "source", source: { k: "reading", dev: "", reading: "temperature" }, map: { mode: "steps", steps: [{ from: "", to: "15", v: -5 }, { from: "28", to: "", v: 10 }], "else": 0 } } }] }] },
      cook: { cases: [C("if", L(ed, "Kochen", "eq", "an"), [{ cmds: [{ t: "fhem", text: "set push message " + (S.lang === "DE" ? "Fertig gekocht" : "Cooking done") }], wait: "[" + ed + ":Kochzeit_s]" }])],
        inputs: [{ name: "Kochen", title: S.lang === "DE" ? "Kochen" : "Cooking", kind: "choice", options: "an,aus", "default": "aus" }],
        values: [{ title: "Kochzeit", name: "Kochzeit", unit: "min", rows: [{ op: "start", amount: { k: "fixed", v: 8 } },
          { op: "add", amount: { k: "source", source: { k: "input", name: "Groesse" }, map: { mode: "values", values: [{ value: "L", v: 1 }, { value: "XL", v: 2 }], "else": 0 } } }] }] }
    };
  }

  function newRule() {
    var names = ["empty", "motion", "schedule", "window", "notify", "irrigation", "cook"];
    var h = '<div class="rg-devs">' + names.map(function (n) {
      return '<div class="rg-dev" data-tpl="' + n + '"><div class="ic">' + icon(n === "irrigation" || n === "cook" ? "temp" : n === "schedule" ? "clock" : n === "motion" ? "light" : "rule") + '</div><div class="n">' + esc(t("t_" + n)) + "</div></div>";
    }).join("") + "</div>";
    var $m = modal(t("newRule"), h, null);
    $m.on("click", "[data-tpl]", function () {
      var tpl = templates()[$(this).data("tpl")], title = t("t_" + $(this).data("tpl"));
      $m.remove();
      var pending = (tpl.values || []).filter(function (v) { return !(S.overview.values || []).some(function (x) { return x.name === v.name; }); });
      var inputs = (tpl.inputs || []).filter(function (v) { return !(S.overview.inputs || []).some(function (x) { return x.name === v.name; }); });
      (function next() {
        if (inputs.length) { setData("input_save", { input: inputs.shift() }, next); return; }
        if (pending.length) { setData("value_save", { value: pending.shift() }, next); return; }
        loadOverview(function () {
          withCatalog(function () {
            S.rule = { name: "di_" + translit(title).replace(/[^A-Za-z0-9]+/g, "_").replace(/^_|_$/g, ""), type: "DOIF", attrs: { alias: title, room: "" }, isNew: true, versions: 0, readings: {} };
            S.model = { mode: "fhem", def: "", error: "", cases: tpl.cases, attrs: tpl.attrs || {}, tail: "", name: "" };
            S.view = "visual"; S.now = null; S.sim = null; S.dirty = true;
            render();
          });
        });
      })();
    });
  }

  /* --------------------------------------------------------------- values */

  function renderValues($body) {
    var vals = S.overview.values || [], res = S.overview.results || {}, h = '<div class="rg-hint info">' + icon("info") + "<span>" + esc(t("valuesHelp")) + "</span></div>";
    h += '<div class="rg-card rg-list" style="padding:0">';
    if (!vals.length) h += '<div class="rg-item rg-mu">' + esc(t("noValues")) + "</div>";
    vals.forEach(function (v) {
      h += '<div class="rg-item" data-act="openvalue" data-name="' + attr(v.name) + '"><div class="ic" style="color:var(--violet)">' + icon("temp") + '</div><div style="flex:1"><div class="n">' + esc(v.title || v.name) +
        '</div><div class="d">[' + esc(S.device + ":" + v.name) + "]</div></div><b>" + esc(res[v.name] !== undefined ? res[v.name] : "?") + " " + esc(v.unit || "") + "</b></div>";
    });
    h += '</div><div class="rg-flex" style="margin:16px 0 8px"><div class="rg-sh" style="margin:0">' + esc(t("inputsT")) + '</div><button class="rg-btn sm rg-ml" data-act="newinput">' + icon("plus", "s") + esc(t("newInput")) + "</button></div>";
    h += '<div class="rg-card">';
    (S.overview.inputs || []).forEach(function (inp) {
      var cur = res[inp.name] !== undefined ? res[inp.name] : inp["default"] || "";
      var control = inp.kind === "choice" ? '<select data-input="' + attr(inp.name) + '">' + String(inp.options || "").split(",").map(function (o) {
        return '<option' + (o === cur ? " selected" : "") + ">" + esc(o) + "</option>";
      }).join("") + "</select>" : '<input class="rg-input" data-input="' + attr(inp.name) + '" value="' + attr(cur) + '" style="width:120px">';
      h += '<div class="rg-q"><span><b>' + esc(inp.title || inp.name) + '</b> <span class="rg-mu rg-small">[' + esc(S.device + ":" + inp.name) + "]</span></span>" + control +
        '<button class="rg-x" data-act="delinput" data-name="' + attr(inp.name) + '">' + icon("trash", "s") + "</button></div>";
    });
    if (!(S.overview.inputs || []).length) h += '<div class="rg-mu">–</div>';
    $body.html(h + "</div>");
  }

  function openValue(name) {
    var v = (S.overview.values || []).filter(function (x) { return x.name === name; })[0];
    S.value = v ? clone(v) : { title: "", name: "", unit: "min", rows: [{ op: "start", amount: { k: "fixed", v: 10 } }], min: "", max: "", round: "" };
    S.valueOld = v ? v.name : "";
    withCatalog(function () { renderValueEditor(); });
  }

  function amountHtml(row, ri) {
    var a = row.amount || { k: "fixed", v: 0 }, h = '<select data-vf="kind" data-row="' + ri + '"><option value="fixed"' + (a.k === "fixed" ? " selected" : "") + ">" + esc(t("fixed")) +
      '</option><option value="source"' + (a.k === "source" ? " selected" : "") + ">" + esc(t("dependsOn")) + "</option></select>";
    if (a.k === "fixed") return h + '<input class="rg-input" data-vf="fixed" data-row="' + ri + '" value="' + attr(a.v) + '" style="width:90px">';
    var s = a.source || { k: "reading" }, mp = a.map || { mode: "direct" };
    h += '<select data-vf="src" data-row="' + ri + '">' + ["reading", "history", "time", "input", "value"].map(function (k) {
      return '<option value="' + k + '"' + (s.k === k ? " selected" : "") + ">" + esc(t("src_" + k)) + "</option>";
    }).join("") + "</select>";
    if (s.k === "reading" || s.k === "history") {
      h += '<span class="rg-tok ' + (s.dev ? "dev" : "miss") + '" data-vf="dev" data-row="' + ri + '">' + esc(devLabel(s.dev)) + '</span><select data-vf="reading" data-row="' + ri + '">' + readingOptions(s.dev, s.reading || "state") + "</select>";
      if (s.k === "history") {
        h += '<select data-vf="func" data-row="' + ri + '">' + ["sum", "min", "max", "avg", "count", "since"].map(function (f) {
          return '<option value="' + f + '"' + (s.func === f ? " selected" : "") + ">" + esc(t("f_" + f)) + "</option>";
        }).join("") + '</select><input class="rg-input" data-vf="hours" data-row="' + ri + '" value="' + attr(s.hours || 24) + '" style="width:70px"><span class="rg-mu rg-small">' + esc(t("hours")) + "</span>";
      }
    } else if (s.k === "time") {
      h += '<select data-vf="part" data-row="' + ri + '">' + ["hour", "weekday", "month"].map(function (p) {
        return '<option value="' + p + '"' + (s.part === p ? " selected" : "") + ">" + esc(t(p)) + "</option>";
      }).join("") + "</select>";
    } else {
      var list = s.k === "input" ? (S.overview.inputs || []) : (S.overview.values || []).filter(function (x) { return x.name !== S.value.name; });
      h += '<select data-vf="sname" data-row="' + ri + '"><option value=""></option>' + list.map(function (x) {
        return '<option value="' + attr(x.name) + '"' + (s.name === x.name ? " selected" : "") + ">" + esc(x.title || x.name) + "</option>";
      }).join("") + "</select>";
    }
    h += '<select data-vf="mode" data-row="' + ri + '">' + ["direct", "per", "steps", "values", "linear"].map(function (k) {
      return '<option value="' + k + '"' + (mp.mode === k ? " selected" : "") + ">" + esc(t("m_" + k)) + "</option>";
    }).join("") + "</select>";
    if (mp.mode === "per") h += '<span class="rg-op">×</span><input class="rg-input" data-vf="per" data-row="' + ri + '" value="' + attr(mp.v || "") + '" style="width:80px">';
    if (mp.mode === "steps" || mp.mode === "values" || mp.mode === "linear") {
      var items = mp.mode === "steps" ? mp.steps || [] : mp.mode === "values" ? mp.values || [] : (mp.points || []).map(function (p) { return { x: p[0], v: p[1] }; });
      h += '<div style="flex-basis:100%;padding-left:20px">';
      items.forEach(function (it, k) {
        h += '<div class="rg-flex" style="margin:4px 0">';
        if (mp.mode === "steps") h += '<span class="rg-mu rg-small">' + esc(t("from")) + '</span><input class="rg-input" data-vm="from" data-row="' + ri + '" data-k="' + k + '" value="' + attr(it.from) + '" style="width:70px"><span class="rg-mu rg-small">' + esc(t("to")) + '</span><input class="rg-input" data-vm="to" data-row="' + ri + '" data-k="' + k + '" value="' + attr(it.to) + '" style="width:70px">';
        else if (mp.mode === "values") h += '<input class="rg-input" data-vm="value" data-row="' + ri + '" data-k="' + k + '" value="' + attr(it.value) + '" style="width:140px">';
        else h += '<input class="rg-input" data-vm="x" data-row="' + ri + '" data-k="' + k + '" value="' + attr(it.x) + '" style="width:70px">';
        h += '<span class="rg-op">→</span><input class="rg-input" data-vm="v" data-row="' + ri + '" data-k="' + k + '" value="' + attr(it.v) + '" style="width:80px"><button class="rg-x" data-vact="delitem" data-row="' + ri + '" data-k="' + k + '">' + icon("x", "s") + "</button></div>";
      });
      h += '<div class="rg-flex"><span class="rg-tok add" data-vact="additem" data-row="' + ri + '">' + icon("plus", "s") + "</span>";
      if (mp.mode !== "linear") h += '<span class="rg-mu rg-small">' + esc(t("otherwise")) + '</span><input class="rg-input" data-vf="else" data-row="' + ri + '" value="' + attr(mp["else"] === undefined ? "" : mp["else"]) + '" style="width:80px">';
      h += "</div></div>";
    }
    return h;
  }

  function onlyIfText(tree) {
    if (!tree) return "";
    var parts = [];
    (function walk(n) {
      if (!n) return;
      if (isGroup(n)) { n.items.forEach(walk); return; }
      if (n.t === "cmp") parts.push(devLabel(n.dev) + (n.reading ? ":" + n.reading : "") + " " + (OPS[S.lang][n.op] || n.op) + " " + valueLabel(n.value));
      else if (n.t === "range") parts.push(t("between") + " " + timeLabel(n.from) + "–" + timeLabel(n.to));
      else parts.push(n.t);
    })(tree);
    return parts.join(" " + t("and").toLowerCase() + " ");
  }

  function renderValueEditor(receipt) {
    var v = S.value, $root = $("#fhempyRegeln");
    var h = '<div class="rg"><div class="rg-head"><button class="rg-btn q" data-vact="back">' + icon("back") + esc(t("back")) + "</button><h2>" + esc(v.title || t("newValue")) +
      '</h2><button class="rg-btn p rg-ml" data-vact="save">' + esc(t("save")) + "</button></div><div class=\"rg-grid\"><div>";
    h += '<div class="rg-card rg-flex"><label class="rg-mu rg-small">' + esc(t("valueTitle")) + '</label><input class="rg-input" data-vf="title" value="' + attr(v.title) + '" style="flex:1;min-width:160px">' +
      '<label class="rg-mu rg-small">' + esc(t("unit")) + '</label><select data-vf="unit">' + ["", "s", "min", "h", "%", "°C", "mm", "kWh"].map(function (u) {
        return '<option value="' + attr(u) + '"' + ((v.unit || "") === u ? " selected" : "") + ">" + esc(u || "–") + "</option>";
      }).join("") + "</select></div>";
    h += '<div class="rg-card rg-receipt">';
    v.rows.forEach(function (row, ri) {
      var step = receipt && receipt.steps ? receipt.steps[ri] : null;
      h += '<div class="rr"><select data-vf="op" data-row="' + ri + '">' + ["start", "mul", "add", "sub", "set"].map(function (o) {
        return '<option value="' + o + '"' + (row.op === o ? " selected" : "") + ">" + esc(t(o)) + "</option>";
      }).join("") + "</select>" + amountHtml(row, ri) +
        '<span class="rg-tok add rg-small" data-vact="onlyif" data-row="' + ri + '">' + esc(t("onlyIf")) + (row.only_if ? ": " + esc(onlyIfText(row.only_if)) : "") + "</span>" +
        (row.only_if ? '<button class="rg-x" data-vact="delonlyif" data-row="' + ri + '">' + icon("x", "s") + "</button>" : "") +
        '<span class="sum">' + (step ? (step.error ? '<span class="rg-badge r">' + esc(t("unknown")) + "</span>" : step.skipped ? '<span class="rg-mu">–</span>' :
          esc((step.raw !== null && step.raw !== undefined && row.amount.k === "source" ? "(" + String(step.raw).slice(0, 16) + ") " : "") + fmt(step.result))) : "") + "</span>" +
        (v.rows.length > 1 ? '<button class="rg-x" data-vact="delrow" data-row="' + ri + '">' + icon("trash", "s") + "</button>" : "") + "</div>";
    });
    h += '<div class="rg-flex" style="margin-top:8px"><span class="rg-tok add" data-vact="addrow">' + icon("plus", "s") + esc(t("addRow")) + "</span></div>";
    h += '<div class="rg-flex" style="margin-top:12px"><span class="rg-mu rg-small">' + esc(t("limits")) + ": " + esc(t("min")) + '</span><input class="rg-input" data-vf="min" value="' + attr(v.min || "") + '" style="width:70px">' +
      '<span class="rg-mu rg-small">' + esc(t("max")) + '</span><input class="rg-input" data-vf="max" value="' + attr(v.max || "") + '" style="width:70px"><span class="rg-mu rg-small">' + esc(t("round")) +
      '</span><input class="rg-input" data-vf="round" value="' + attr(v.round || "") + '" style="width:70px"></div>';
    h += '<div class="tot"><span>' + esc(t("result")) + "</span><span>" + esc(receipt ? (receipt.result === null ? t("unknown") : receipt.text + " " + (v.unit || "")) : "…") + "</span></div></div>";
    var name = v.name || (v.title ? v.title.replace(/[äöüÄÖÜß]/g, function (c) { return { "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss" }[c]; }).replace(/[^A-Za-z0-9_]+/g, "_").replace(/^_|_$/g, "") : "Name");
    h += '<div class="rg-hint info rg-small">' + esc(t("useIn", { a: "[" + S.device + ":" + name + "]", b: "[" + S.device + ":" + name + (["min", "h"].indexOf(v.unit) >= 0 ? "_s" : "") + "]" })) + "</div>";
    h += "</div><div class=\"rg-side\">" + (S.valueOld ? '<div class="rg-card"><button class="rg-btn sm r" data-vact="delete">' + icon("trash", "s") + esc(t("del")) + "</button></div>" : "") + "</div></div></div>";
    $root.html(h);
    if (!receipt) previewValue();
  }
  function fmt(n) { return n === null || n === undefined ? "" : Math.round(n * 100) / 100; }
  var previewTimer = null;
  function previewValue() {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(function () {
      getJSON("value_preview " + b64({ value: S.value }), function (data) { if (S.value) renderValueEditor(data); });
    }, 300);
  }

  function bindValues($root) {
    $root.on("change", "[data-vf]", function () {
      if (!S.value) return;
      var f = $(this).data("vf"), ri = $(this).data("row"), v = S.value, row = typeof ri === "number" ? v.rows[ri] : null, val = $(this).val();
      var src = row && row.amount && row.amount.source;
      switch (f) {
        case "title": case "unit": case "min": case "max": case "round": v[f] = val; break;
        case "op": row.op = val; break;
        case "kind": row.amount = val === "fixed" ? { k: "fixed", v: 0 } : { k: "source", source: { k: "reading", dev: "", reading: "state" }, map: { mode: "direct" } }; break;
        case "fixed": row.amount.v = parseFloat(String(val).replace(",", ".")) || 0; break;
        case "src": row.amount.source = { k: val, dev: src.dev || "", reading: src.reading || "state", func: "sum", hours: 24, part: "hour", name: "" }; break;
        case "reading": src.reading = val; break;
        case "func": src.func = val; break;
        case "hours": src.hours = parseFloat(val) || 24; break;
        case "part": src.part = val; break;
        case "sname": src.name = val; break;
        case "mode":
          row.amount.map = { mode: val, v: 1, steps: [{ from: "", to: "", v: 0 }], values: [{ value: "", v: 100 }], points: [[0, 0], [10, 10]], "else": "" }; break;
        case "per": row.amount.map.v = parseFloat(val) || 0; break;
        case "else": row.amount.map["else"] = val; break;
      }
      renderValueEditor();
    });
    $root.on("change", "[data-vm]", function () {
      var ri = $(this).data("row"), k = $(this).data("k"), f = $(this).data("vm"), mp = S.value.rows[ri].amount.map, val = $(this).val();
      if (mp.mode === "linear") { mp.points[k][f === "x" ? 0 : 1] = parseFloat(val) || 0; }
      else { var list = mp.mode === "steps" ? mp.steps : mp.values; list[k][f] = f === "v" ? parseFloat(val) || 0 : val; }
      renderValueEditor();
    });
    $root.on("click", "[data-vact],[data-vf=dev]", function (e) {
      if (!S.value) return;
      e.stopPropagation();
      var act = $(this).data("vact") || "dev", ri = $(this).data("row"), v = S.value, row = typeof ri === "number" ? v.rows[ri] : null;
      switch (act) {
        case "back": S.value = null; loadOverview(render); break;
        case "save":
          setData("value_save", { value: v, old_name: S.valueOld }, function (err) {
            if (err) { toast(err); return; }
            toast(t("saved")); S.value = null; loadOverview(render);
          }); break;
        case "delete":
          if (!window.confirm(t("confirmDelete", { n: v.title || v.name }))) return;
          setCmd("value_delete " + S.valueOld, function () { S.value = null; loadOverview(render); }); break;
        case "dev": pickDevice(function (name) { row.amount.source.dev = name; row.amount.source.reading = "state"; renderValueEditor(); }); break;
        case "addrow": v.rows.push({ op: "add", amount: { k: "fixed", v: 0 } }); renderValueEditor(); break;
        case "delrow": v.rows.splice(ri, 1); renderValueEditor(); break;
        case "additem":
          var mp = row.amount.map;
          if (mp.mode === "steps") mp.steps.push({ from: "", to: "", v: 0 });
          else if (mp.mode === "values") mp.values.push({ value: "", v: 0 });
          else mp.points.push([0, 0]);
          renderValueEditor(); break;
        case "delitem":
          var m2 = row.amount.map, list = m2.mode === "steps" ? m2.steps : m2.mode === "values" ? m2.values : m2.points;
          list.splice($(this).data("k"), 1); renderValueEditor(); break;
        case "onlyif":
          var tree = row.only_if ? (isGroup(row.only_if) ? row.only_if.items[0] : row.only_if) : newLeaf("cmp");
          editLeaf(clone(tree), function (leaf) { leaf.check = true; row.only_if = leaf; renderValueEditor(); }, !row.only_if); break;
        case "delonlyif": delete row.only_if; renderValueEditor(); break;
      }
    });
  }

  function newInput() {
    var body = "<label>" + esc(t("valueTitle")) + '</label><input class="rg-input" data-f="title"><label>' + esc(t("inputKind")) + '</label><select data-f="kind"><option value="number">' +
      esc(t("number")) + '</option><option value="choice">' + esc(t("choice")) + "</option></select><label>" + esc(t("options")) + '</label><input class="rg-input" data-f="options" placeholder="S,M,L">' +
      "<label>" + esc(t("current")) + '</label><input class="rg-input" data-f="default">';
    modal(t("newInput"), body, function ($b) {
      var item = { title: $b.find('[data-f="title"]').val(), kind: $b.find('[data-f="kind"]').val(), options: $b.find('[data-f="options"]').val(), "default": $b.find('[data-f="default"]').val() };
      setData("input_save", { input: item }, function (err) { if (err) toast(err); loadOverview(render); });
    });
  }

  /* ------------------------------------------------------------------ map */

  function renderMap($body) {
    var h = '<div class="rg-grid"><div><div class="rg-card"><div class="rg-flex" style="margin-bottom:8px"><b>' + esc(t("focus")) + '</b><select data-focus>' +
      '<option value="house:">' + esc(t("house")) + "</option>" + (S.overview.rooms || []).map(function (r) {
        return '<option value="room:' + attr(r) + '"' + (S.focus.kind === "room" && S.focus.id === r ? " selected" : "") + ">" + esc(t("room") + ": " + r) + "</option>";
      }).join("") + (S.focus.kind === "device" || S.focus.kind === "rule" ? '<option selected value="' + attr(S.focus.kind + ":" + S.focus.id) + '">' + esc(devLabel(S.focus.id)) + "</option>" : "") +
      '</select><button class="rg-btn sm" data-act="focusdev">' + icon("search", "s") + esc(t("device")) + '</button></div><div class="rg-map" data-map><div class="rg-mu">' + esc(t("loading")) + "</div></div></div>" +
      '<div class="rg-card"><b>' + esc(t("whyQ")) + '</b><div class="rg-flex" style="margin-top:8px"><button class="rg-btn sm" data-act="why">' + icon("search", "s") + esc(t("chooseDevice")) + '</button></div><div data-why></div></div></div><div class="rg-side">' +
      '<div class="rg-card"><b>' + esc(t("health")) + "</b>" + healthView(S.overview.health || []) + "</div></div></div>";
    $body.html(h);
    getJSON("graph " + S.focus.kind + (S.focus.id ? " " + S.focus.id : ""), function (data) { $body.find("[data-map]").html(graphSvg(data)); });
  }

  function healthView(list) {
    if (!list.length) return '<div class="rg-hint ok" style="margin-top:8px">' + icon("check") + esc(t("healthOk")) + "</div>";
    return list.map(function (f, i) {
      var cls = f.severity === "error" ? "err" : f.severity === "warn" ? "" : "info", text = "";
      switch (f.kind) {
        case "conflict": text = t("h_conflict", { d: devLabel(f.devices[0]) }) + (f.params.flaps ? " " + t("h_flaps", { n: f.params.flaps }) : ""); break;
        case "loop": text = f.rules.length > 1 ? t("h_loop") : t("h_selfloop"); break;
        case "missing": text = t("h_missing", { d: f.devices.join(", ") }); break;
        case "dead": text = f.params.last ? t("h_dead", { n: f.params.days }) : t("h_deadNever"); break;
        case "duplicate": text = t("h_duplicate"); break;
        case "error": text = t("h_error", { t: f.params.text }); break;
        case "unused_value": text = t("h_unused_value", { t: f.params.title }); break;
        default: text = f.kind;
      }
      var h = '<div class="rg-hint ' + cls + '" style="margin-top:8px;flex-direction:column;align-items:stretch">' + "<span>" + esc(text) + '</span><div class="rg-chips">' +
        f.rules.map(function (r) { return '<span class="rg-chip" data-act="open" data-rule="' + attr(r) + '">' + esc(devLabel(r)) + "</span>"; }).join("") + "</div>";
      if (f.fix === "precedence") {
        h += '<div class="rg-chips">' + (f.params.doifs || f.rules).map(function (r) {
          return '<button class="rg-btn sm" data-act="precedence" data-winner="' + attr(r) + '" data-f="' + i + '">' + esc(t("wins", { r: devLabel(r) })) + "</button>";
        }).join("") + "</div>";
      }
      if (f.fix === "disable") h += '<div><button class="rg-btn sm" data-act="toggle" data-rule="' + attr(f.rules[0]) + '">' + esc(t("disableRule")) + "</button></div>";
      return h + "</div>";
    }).join("");
  }

  function graphSvg(data) {
    var nodes = data.nodes || [], edges = data.edges || [];
    if (!nodes.length) return '<div class="rg-mu">–</div>';
    var written = {}, read = {};
    edges.forEach(function (e) { if (e.from.indexOf("rule:") === 0) written[e.to] = true; else read[e.from] = true; });
    var cols = [[], [], []];
    nodes.forEach(function (n) {
      if (n.kind === "rule") cols[1].push(n);
      else if (written[n.id]) cols[2].push(n);
      else cols[0].push(n);
    });
    cols.forEach(function (c) { c.sort(function (a, b) { return (a.alias || a.name).localeCompare(b.alias || b.name); }); });
    var rowH = 38, width = 760, colX = [4, 274, 544], boxW = 212;
    var height = Math.max(cols[0].length, cols[1].length, cols[2].length) * rowH + 40;
    var pos = {};
    cols.forEach(function (c, ci) {
      var offset = (height - 30 - c.length * rowH) / 2 + 30;
      c.forEach(function (n, k) { pos[n.id] = { x: colX[ci], y: offset + k * rowH, col: ci }; });
    });
    var svg = '<svg viewBox="0 0 ' + width + " " + height + '" style="min-height:' + Math.min(height, 200) + 'px">';
    [t("inputs"), t("rules"), t("outputs")].forEach(function (label, ci) {
      svg += '<text x="' + (colX[ci] + 4) + '" y="16" font-size="12" font-weight="700" fill="#69717D">' + esc(label.toUpperCase()) + "</text>";
    });
    edges.forEach(function (e) {
      var a = pos[e.from], b = pos[e.to];
      if (!a || !b) return;
      var x1 = a.x + boxW, y1 = a.y + 15, x2 = b.x, y2 = b.y + 15, back = a.col >= b.col;
      if (back) { x1 = a.x; x2 = b.x + boxW; }
      var mx = (x1 + x2) / 2, d = back ? "M" + x1 + "," + y1 + " C" + (x1 - 60) + "," + y1 + " " + (x2 + 60) + "," + y2 + " " + x2 + "," + y2 : "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2;
      var color = e.from.indexOf("rule:") === 0 ? "#3D7FC4" : e.trigger ? "#C77700" : "#9AA1AC";
      svg += '<path d="' + d + '" fill="none" stroke="' + color + '" stroke-width="1.6"' + (e.trigger || e.from.indexOf("rule:") === 0 ? "" : ' stroke-dasharray="4 4"') + ' opacity=".8"><title>' +
        esc((e.readings || []).join(", ") + (e.values || []).join(", ")) + "</title></path>";
    });
    nodes.forEach(function (n) {
      var p = pos[n.id], fill = n.kind === "rule" ? (n.disabled ? "#EDEFF2" : "#EEEBFD") : n.missing ? "#FCE9E8" : n.kind === "time" ? "#FFF4DF" : "#E8F1FB";
      var label = n.kind === "time" ? t("time") : (n.alias || n.name);
      var act = n.kind === "rule" ? "maprule" : n.kind === "time" ? "" : "mapdev";
      svg += '<g class="node" data-act="' + act + '" data-id="' + attr(n.name) + '"><rect x="' + p.x + '" y="' + p.y + '" width="' + boxW + '" height="30" rx="9" fill="' + fill + '" stroke="#E3E6EB"/>' +
        '<text x="' + (p.x + 10) + '" y="' + (p.y + 19) + '" font-size="12.5" font-weight="600" fill="#1C2128">' + esc(label.length > 26 ? label.slice(0, 25) + "…" : label) + "</text>" +
        (n.state !== undefined && n.kind !== "rule" ? '<text x="' + (p.x + boxW - 8) + '" y="' + (p.y + 19) + '" font-size="11" text-anchor="end" fill="#69717D">' + esc(String(n.state).slice(0, 10)) + "</text>" : "") + "</g>";
    });
    return svg + "</svg>";
  }

  function showWhy($target, device) {
    $target.html('<div class="rg-mu">' + esc(t("loading")) + "</div>");
    getJSON("why " + device, function (w) {
      var h = '<div style="margin-top:8px"><b>' + esc(devLabel(device)) + "</b>: " + esc(w.value || "?") + ' <span class="rg-mu rg-small">' + esc(ago(w.ts)) + "</span></div>";
      if (w.causes && w.causes.length) {
        w.causes.forEach(function (c) {
          h += '<div class="rg-hint ok" style="margin-top:6px;flex-direction:column;align-items:stretch"><span>' + esc(t("whyCause", { r: devLabel(c.rule), t: ago(c.ts) })) + (c.cmd ? " (" + esc(c.cmd) + ")" : "") + "</span>" +
            (c.trigger ? '<span class="rg-small">' + esc(t("whyTrigger", { t: c.trigger })) + "</span>" : "") + '<div><span class="rg-chip" data-act="open" data-rule="' + attr(c.rule) + '">' + esc(t("open")) + "</span></div></div>";
        });
      } else if (w.manual) h += '<div class="rg-hint info" style="margin-top:6px">' + esc(t("whyManual")) + "</div>";
      else h += '<div class="rg-hint info" style="margin-top:6px">' + esc(t("whyNoChange")) + "</div>";
      if (w.candidates && w.candidates.length) {
        h += '<div class="rg-small rg-mu" style="margin-top:8px">' + esc(t("candidates")) + '</div><div class="rg-chips">' + w.candidates.map(function (c) {
          return '<span class="rg-chip" data-act="open" data-rule="' + attr(c.rule) + '">' + esc(devLabel(c.rule)) + " → " + esc(c.values.join(" / ")) + "</span>";
        }).join("") + "</div>";
      }
      $target.html(h);
    });
  }

  /* ----------------------------------------------------------------- plan */

  function renderPlan($body) {
    $body.html('<div class="rg-card rg-mu">' + esc(t("loading")) + "</div>");
    getJSON("plan", function (data) {
      var list = data.plan || [], now = data.now, h = '<div class="rg-card rg-plan"><div class="rg-sh" style="margin-top:0">' + esc(t("today")) + "</div>", drawn = false;
      list.forEach(function (e) {
        if (!drawn && e.ts >= now) { h += '<div class="nowl"><span>' + esc(t("nowLine") + " " + clockOf(now)) + "</span></div>"; drawn = true; }
        var kind = e.kind === "done" ? t("planDone") : e.kind === "wait" ? t("planWait") : e.kind === "at" ? t("planAt") : t("planTimer");
        h += '<div class="pe' + (e.ts < now ? " past" : "") + '"><span class="tm">' + esc(clockOf(e.ts)) + '</span><span class="rg-chip" data-act="open" data-rule="' + attr(e.rule) + '">' + esc(e.alias || e.rule) +
          '</span><span class="rg-badge ' + (e.kind === "done" ? "g" : e.kind === "wait" ? "a" : "v") + '">' + esc(kind) + "</span>" + (e["case"] !== null && e["case"] !== undefined ? '<span class="rg-mu rg-small">' + esc(t("caseN", { n: e["case"] + 1 })) + "</span>" : "") +
          '<span class="rg-small" style="color:#1F5E9E">' + esc((e.writes || []).join("; ")) + "</span>" + (e.days ? '<span class="rg-mu rg-small">' + esc(daysLabel(e.days)) + "</span>" : "") + "</div>";
      });
      if (!drawn) h += '<div class="nowl"><span>' + esc(t("nowLine") + " " + clockOf(now)) + "</span></div>";
      if (!list.filter(function (e) { return e.ts >= now; }).length) h += '<div class="rg-mu" style="margin-top:12px">' + esc(t("planEmpty")) + "</div>";
      $body.html(h + "</div>");
    });
  }

  function renderChanges($body) {
    getJSON("changes", function (data) {
      var list = data.changes || [], h = '<div class="rg-card rg-list" style="padding:0">';
      if (!list.length) h += '<div class="rg-item rg-mu">' + esc(t("noChanges")) + "</div>";
      list.forEach(function (c) {
        h += '<div class="rg-item" data-act="open" data-rule="' + attr(c.rule) + '"><span class="rg-mu rg-small" style="width:110px">' + esc(ago(c.ts)) + '</span><b>' + esc(devLabel(c.rule)) +
          '</b><span class="rg-badge">' + esc(t("c_" + c.action)) + '</span><span class="rg-mu rg-small">' + esc(c.detail || "") + "</span></div>";
      });
      $body.html(h + "</div>");
    });
  }

  /* --------------------------------------------------------------- global */

  function bindList($root) {
    $root.on("click", "[data-tab]", function () { S.tab = $(this).data("tab"); storageSet("tab", S.tab); render(); });
    $root.on("click", "[data-act]", function (e) {
      if (S.rule || S.value) return;
      var $t = $(this), act = $t.data("act");
      switch (act) {
        case "open":
          if ($t.data("rule") === S.device) { S.tab = "values"; render(); return; }
          e.stopPropagation(); openRule($t.attr("data-rule")); break;
        case "toggle":
          e.stopPropagation();
          var r = (S.overview.rules || []).filter(function (x) { return x.name === $t.attr("data-rule"); })[0];
          setCmd((r && r.disabled ? "enable " : "disable ") + $t.attr("data-rule"), function (err) { if (err) toast(err); loadOverview(render); }); break;
        case "new": newRule(); break;
        case "newvalue": openValue(""); break;
        case "openvalue": openValue($t.attr("data-name")); break;
        case "newinput": newInput(); break;
        case "delinput":
          e.stopPropagation(); setCmd("input_delete " + $t.attr("data-name"), function () { loadOverview(render); }); break;
        case "focusdev":
          pickDevice(function (name) { var info = devInfo(name); S.focus = { kind: info && info.rule ? "rule" : "device", id: name }; render(); }); break;
        case "maprule": S.focus = { kind: "rule", id: $t.attr("data-id") }; render(); break;
        case "mapdev": S.focus = { kind: "device", id: $t.attr("data-id") }; render(); break;
        case "why": pickDevice(function (name) { showWhy($root.find("[data-why]"), name); }); break;
        case "precedence":
          e.stopPropagation();
          var f = (S.overview.health || [])[$t.data("f")], winner = $t.attr("data-winner");
          var losers = (f.params.doifs || f.rules).filter(function (x) { return x !== winner; });
          (function next() {
            if (!losers.length) { toast(t("saved")); loadOverview(render); return; }
            setData("precedence", { winner: winner, loser: losers.shift(), device: f.devices[0] }, function (err) { if (err) toast(err); next(); });
          })(); break;
      }
    });
    $root.on("change", "[data-focus]", function () {
      var v = $(this).val().split(":"), kind = v.shift();
      S.focus = { kind: kind, id: v.join(":") }; render();
    });
    $root.on("change", "[data-input]", function () {
      setCmd("input " + $(this).data("input") + " " + String($(this).val()).replace(/\s+/g, "_"), function (err) { if (err) toast(err); else toast(t("saved")); });
    });
  }

  window.fhempyRegeln = function (device) {
    S.device = device;
    S.tab = storageGet("tab") || "rules";
    css();
    var $root = $("#fhempyRegeln");
    $root.off();
    bindList($root);
    bindEditor($root);
    bindValues($root);
    loadOverview(function () {
      var m = location.hash.match(/^#rule=(.+)$/);
      if (m) openRule(decodeURIComponent(m[1]));
      else render();
    });
  };
})();
