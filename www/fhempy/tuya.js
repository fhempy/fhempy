/*
 * Tuya device dialog for FHEMWEB.
 * fhempyTuyaScan(setupName): starts scan_devices of the tuya setup device
 * fhempyTuyaDevices(setupName, devices, error): shows the found devices,
 *   opened by the setup device after each scan. A click on a device creates
 *   it with set <setupName> create_device <id>.
 */
(function () {
  "use strict";

  var setup = "";
  var devices = [];
  /* tuya device id -> FHEM device name */
  var created = {};

  function esc(t) { return $("<div>").text(t === undefined ? "" : String(t)).html(); }

  function css() {
    if ($("#fhempyTuyaCss").length) return;
    $("head").append('<style id="fhempyTuyaCss">' +
      "#fhempyTuya{max-height:calc(100vh - 170px)!important;overflow-y:auto;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.35}" +
      "#fhempyTuya .ftIntro{margin:2px 0 12px}" +
      "#fhempyTuya .ftCat{font-weight:600;margin:16px 0 8px;font-size:15px}" +
      "#fhempyTuya .ftCat:first-child{margin-top:2px}" +
      "#fhempyTuya .ftGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}" +
      "#fhempyTuya .ftTile{border:1px solid rgba(128,128,128,0.35);border-radius:12px;padding:10px;display:flex;gap:10px;align-items:center;transition:transform .15s,box-shadow .15s}" +
      "#fhempyTuya .ftNew{cursor:pointer}" +
      "#fhempyTuya .ftNew:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15);border-color:#4B8BBE}" +
      "#fhempyTuya .ftOff{opacity:0.55}" +
      "#fhempyTuya .ftLogo{flex:none;width:44px;height:44px;border-radius:10px;background:#fff;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 0 0 1px rgba(128,128,128,0.25);font-size:24px;overflow:hidden}" +
      "#fhempyTuya .ftLogo img{width:38px;height:38px;object-fit:contain}" +
      "#fhempyTuya .ftTitle{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
      "#fhempyTuya .ftInfo{font-size:12px;opacity:0.7}" +
      "#fhempyTuya .ftAdd{font-size:12px;color:#4B8BBE;font-weight:600;margin-top:3px}" +
      "#fhempyTuya .ftDone{font-size:12px;color:#3fa34d;font-weight:600;margin-top:3px}" +
      "#fhempyTuya .ftErr{font-size:12px;color:#d64545;margin-top:3px;white-space:pre-wrap}" +
      "#fhempyTuya .ftError{color:#d64545;white-space:pre-wrap;margin:10px 0}" +
      "#fhempyTuya .ftEmpty{opacity:0.75;margin:20px 0;text-align:center}" +
      "#fhempyTuya .ftHint{font-size:12px;opacity:0.7;margin:-4px 0 8px}" +
      "@keyframes ftSpin{to{transform:rotate(360deg)}}" +
      "#fhempyTuya .ftSpin{display:inline-block;width:12px;height:12px;border-radius:50%;border:2px solid #4B8BBE;border-top-color:transparent;animation:ftSpin 1s linear infinite;vertical-align:-2px;margin-right:6px}" +
      "#fhempyTuya .ftSpin.ftBig{width:28px;height:28px;border-width:3px;margin:0 0 10px}" +
      "</style>");
  }

  function dialog() {
    css();
    var d = $("#fhempyTuya");
    if (!d.length || !d.dialog("instance")) {
      d.remove();
      d = $('<div id="fhempyTuya"></div>');
      $("body").append(d);
      d.dialog({
        modal: true,
        title: "Tuya devices",
        width: Math.min(800, $(window).width() - 20),
        close: function () { $(this).remove(); }
      });
    }
    return d;
  }

  function buttons(list) {
    var d = $("#fhempyTuya");
    if (!d.dialog("instance")) return;
    d.dialog("option", "buttons", list);
    d.dialog("option", "position", { my: "center", at: "center", of: window });
  }

  function close() { $("#fhempyTuya").dialog("close"); }

  function detailLink(name) {
    return '<a href="' + FW_root + "?detail=" + encodeURIComponent(name) + '">Open</a>';
  }

  /* tuya category -> icon if the device picture can't be loaded */
  var catIcons = {
    cz: "🔌", pc: "🔌", dj: "💡", dd: "💡", dc: "💡", xdd: "💡", fwd: "💡", tgq: "💡", kg: "🎚️", tdq: "🎚️",
    wsdcg: "🌡️", wk: "🌡️", wkf: "🌡️", qn: "🔥", rs: "🔥", kt: "❄️", fs: "🌀", cl: "🪟", clkg: "🪟",
    mcs: "🚪", pir: "🏃", ywbj: "🚨", sj: "💧", jsq: "💧", cs: "💧", sp: "📷", sd: "🧹", ms: "🔐",
    zndb: "⚡", dlq: "⚡", wg2: "📡", ckmkzq: "🚗", kj: "🍃", cwwsq: "🐾", bh: "☕", znrb: "🔥"
  };

  function tile(dev, i) {
    var fallback = catIcons[dev.category] || "📦";
    var logo = dev.icon ? '<img src="' + esc(dev.icon) + '" alt="" onerror="$(this).parent().text($(this).data(\'f\'))" data-f="' +
      fallback + '">' : fallback;
    var state;
    if (created[dev.id]) state = '<div class="ftDone" title="' + esc(created[dev.id]) + '">✓ In FHEM · ' + detailLink(created[dev.id]) + "</div>";
    else if (dev.online) state = '<div class="ftAdd">+ Create in FHEM</div>';
    else state = "";
    var cls = created[dev.id] ? "" : dev.online ? " ftNew" : " ftOff";
    return '<div class="ftTile' + cls + '" data-i="' + i + '"><span class="ftLogo">' + logo + "</span>" +
      '<div style="min-width:0"><div class="ftTitle" title="' + esc(dev.name) + '">' + esc(dev.name) + "</div>" +
      '<div class="ftInfo">' + (dev.online ? esc(dev.ip) + " · v" + esc(dev.version) : "not reachable") + "</div>" +
      state + "</div></div>";
  }

  function render(error) {
    var d = dialog();
    var online = [], offline = [];
    devices.forEach(function (dev, i) { (dev.online ? online : offline).push(tile(dev, i)); });
    var open = devices.filter(function (dev) { return dev.online && !created[dev.id]; });
    var html = "";
    if (error) html += '<div class="ftError">' + esc(error) + "</div>";
    if (online.length) {
      html += '<div class="ftIntro">' + online.length + (online.length == 1 ? " device was" : " devices were") +
        " found in your network. " + (open.length ? "Click a device to create it in FHEM." : "All of them are in FHEM already.") + "</div>" +
        '<div class="ftGrid">' + online.join("") + "</div>";
    } else if (!error) {
      html += '<div class="ftEmpty">No Tuya device was found in your network.<br>' +
        "fhempy has to run in the same network as the devices, the devices have to be switched on.</div>";
    }
    if (offline.length) {
      html += '<div class="ftCat">Not found in your network (' + offline.length + ")</div>" +
        '<div class="ftHint">Switched off, battery powered or connected to a gateway. Switch them on and search again.</div>' +
        '<div class="ftGrid">' + offline.join("") + "</div>";
    }
    d.html(html);
    d.find(".ftNew").click(function () { create($(this)); });
    var list = [];
    if (open.length > 1)
      list.push({ text: "Create all (" + open.length + ")", "class": "ftAllBtn", click: createAll });
    list.push({ text: "Search again", click: scan });
    list.push({ text: "Close", click: close });
    buttons(list);
  }

  function create(el, cb) {
    var dev = devices[el.data("i")];
    if (!dev || el.hasClass("ftBusy")) return;
    el.addClass("ftBusy").find(".ftAdd, .ftErr").replaceWith('<div class="ftAdd"><span class="ftSpin"></span>Creating...</div>');
    var cmd = "set " + setup + " create_device " + dev.id;
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      r = (r || "").replace(/[\r\n]+$/, "");
      el.removeClass("ftBusy");
      if (r !== "") {
        el.find(".ftAdd").replaceWith('<div class="ftErr">' + esc(r.replace(/<br>/g, "\n").replace(/<[^>]+>/g, "")) + "</div>");
      } else {
        created[dev.id] = "tuya_local_" + dev.id;
        el.replaceWith(tile(dev, el.data("i")));
      }
      if (cb) cb();
      else if (r === "") render();
    });
  }

  function createAll() {
    $(".ftAllBtn").button("disable");
    var next = function () {
      var el = $("#fhempyTuya .ftNew:not(.ftBusy)").filter(function () {
        return !created[devices[$(this).data("i")].id] && !$(this).find(".ftErr").length;
      }).first();
      if (el.length) create(el, next);
      else render();
    };
    next();
  }

  /* fhempy devices with the internal DEVICEID, tuya devices created before */
  function loadCreated(cb) {
    var cmd = '{join(",", map {InternalVal($_,"DEVICEID","").":".$_} devspec2array("TYPE=fhempy"))}';
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      created = {};
      (r || "").replace(/[\r\n]+$/, "").split(",").forEach(function (x) {
        var p = x.split(":");
        if (p[0] && p[0] !== "0" && p[1]) created[p[0]] = p[1];
      });
      cb();
    });
  }

  function scan() {
    var d = dialog();
    d.html('<div class="ftEmpty"><span class="ftSpin ftBig"></span><br><b>Searching for Tuya devices...</b><br>' +
      "This takes about a minute, the devices are read from the Tuya cloud and searched in your network.<br><br>" +
      '<span informId="' + esc(setup) + '-state"></span></div>');
    buttons([{ text: "Close", click: close }]);
    var cmd = "set " + setup + " scan_devices";
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      r = (r || "").replace(/[\r\n]+$/, "");
      if (r !== "") render(r);
    });
  }

  window.fhempyTuyaScan = function (name) {
    setup = name;
    scan();
  };

  window.fhempyTuyaDevices = function (name, list, error) {
    setup = name;
    devices = (list || []).slice().sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });
    loadCreated(function () { render(error); });
  };
})();
