/* Automations (fhempy doif_editor): box "Who controls this?" on every device page
   and the button "Edit visually" on DOIF pages. FHEMWEB loads this script on
   every page as extension, the editor device is given in the script url. */
/* global FW_cmd, FW_root, $ */
(function () {
  "use strict";
  var script = document.currentScript ? document.currentScript.src : "";
  var match = script.match(/[?&]editor=([^&]+)/);
  if (!match) return;
  var editor = decodeURIComponent(match[1]);

  var T = {
    DE: { box: "Wer steuert das?", by: "Geschaltet von", uses: "Benutzt von", none: "Keine Regel benutzt dieses Gerät.",
      conflict: "Mehrere Regeln schalten dieses Gerät.", edit: "Visuell bearbeiten", why: "Warum ist das so?", all: "Alle Regeln",
      trigger: "löst aus", check: "prüft", off: "aus", cause: "{r} hat um {t} geschaltet", manual: "Keine Regel hat zuletzt geschaltet: vermutlich von Hand, per App oder vom Gerät selbst.",
      nochange: "Keine Änderung in den letzten 24 Stunden." },
    EN: { box: "Who controls this?", by: "Switched by", uses: "Used by", none: "No rule uses this device.",
      conflict: "Several rules switch this device.", edit: "Edit visually", why: "Why is it so?", all: "All rules",
      trigger: "triggers", check: "checks", off: "off", cause: "{r} switched at {t}", manual: "No rule switched recently: probably by hand, an app or the device itself.",
      nochange: "No change in the last 24 hours." }
  };

  function esc(v) { return $("<div>").text(v === undefined || v === null ? "" : String(v)).html(); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function time(ts) { var d = new Date(ts * 1000); return pad(d.getHours()) + ":" + pad(d.getMinutes()); }

  function get(sub, cb) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent("get " + editor + " " + sub) + "&XHR=1", function (r) {
      try { cb(JSON.parse(r)); } catch (e) { /* editor not ready */ }
    });
  }

  function css() {
    if ($("#fhempyRegelnBoxCss").length) return;
    $("head").append('<style id="fhempyRegelnBoxCss">' +
      ".rgbox{clear:both;font-family:Inter,-apple-system,'Segoe UI',Roboto,sans-serif;background:#fff;color:#1C2128;border:1px solid #E3E6EB;border-radius:14px;padding:12px 14px;margin:10px 0;max-width:720px;font-size:14px;text-align:left}" +
      ".rgbox .hd{margin:0 0 8px;font-size:15px;font-weight:700}.rgbox .sh{font-size:11px;color:#69717D;text-transform:uppercase;letter-spacing:.07em;font-weight:700;margin:8px 0 4px}" +
      ".rgbox a.r{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 10px;border-radius:14px;background:#EEEBFD;color:#4C3FB0;font-weight:600;font-size:13px;margin:2px 4px 2px 0;text-decoration:none}" +
      ".rgbox a.r.off{background:#EDEFF2;color:#69717D}.rgbox .v{color:#69717D;font-size:12px}.rgbox .w{background:#FFF4DF;color:#6E4300;border-radius:10px;padding:8px 10px;margin:6px 0;font-size:13px}" +
      ".rgbox .b{height:30px;padding:0 12px;border-radius:15px;border:1px solid #E3E6EB;background:#fff;font-weight:600;font-size:13px;cursor:pointer;margin-right:6px;color:#1C2128}" +
      ".rgbox .b.p{background:#3D7FC4;border-color:#3D7FC4;color:#fff}.rgbox .i{background:#E8F1FB;color:#1F4F80;border-radius:10px;padding:8px 10px;margin:6px 0;font-size:13px}" +
      "</style>");
  }

  function show(device) {
    get("devicebox " + device, function (box) {
      var tr = T[box.lang] || T.EN;
      var link = function (rule, off, extra) {
        return '<a class="r' + (off ? " off" : "") + '" href="' + FW_root + "?detail=" + encodeURIComponent(editor) + "#rule=" + encodeURIComponent(rule) + '">' + esc(rule) + (extra ? ' <span class="v">' + esc(extra) + "</span>" : "") + "</a>";
      };
      var h = '<div class="rgbox" id="fhempyRegelnBox"><div class="hd">' + esc(tr.box) + "</div>";
      if (box.type === "DOIF") {
        h += '<div><button class="b p" data-rg="edit">' + esc(tr.edit) + "</button></div>";
      }
      if (box.conflict) h += '<div class="w">' + esc(tr.conflict) + "</div>";
      if (box.controls && box.controls.length) {
        h += '<div class="sh">' + esc(tr.by) + "</div>" + box.controls.map(function (c) { return link(c.rule, c.disabled, c.values.join(" / ")); }).join("");
      }
      if (box.uses && box.uses.length) {
        h += '<div class="sh">' + esc(tr.uses) + "</div>" + box.uses.map(function (c) { return link(c.rule, c.disabled, c.trigger ? tr.trigger : tr.check); }).join("");
      }
      if (!(box.controls || []).length && !(box.uses || []).length && box.type !== "DOIF") h += '<div class="v">' + esc(tr.none) + "</div>";
      if ((box.controls || []).length) h += '<div style="margin-top:8px"><button class="b" data-rg="why">' + esc(tr.why) + '</button></div><div data-rg-why></div>';
      h += "</div>";
      var $box = $(h);
      // above the internals, below the set/get lines
      var $anchor = $("#content div.makeTable.internals").first();
      if ($anchor.length) $anchor.before($box);
      else $("#content").append($box);
      $box.on("click", "[data-rg=edit]", function () {
        location.href = FW_root + "?detail=" + encodeURIComponent(editor) + "#rule=" + encodeURIComponent(device);
      });
      $box.on("click", "[data-rg=why]", function () {
        get("why " + device, function (w) {
          var out = "";
          if (w.causes && w.causes.length) out = w.causes.map(function (c) { return '<div class="i">' + esc(tr.cause.replace("{r}", c.rule).replace("{t}", time(c.ts))) + (c.trigger ? " (" + esc(c.trigger) + ")" : "") + "</div>"; }).join("");
          else out = '<div class="i">' + esc(w.manual ? tr.manual : tr.nochange) + "</div>";
          $box.find("[data-rg-why]").html(out);
        });
      });
    });
  }

  $(function () {
    var params = new URLSearchParams(location.search);
    var device = params.get("detail");
    if (!device || device === editor || $("#fhempyRegelnBox").length) return;
    css();
    show(device);
  });
})();
