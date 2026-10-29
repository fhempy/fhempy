/*
 * fhempy autodiscovery for FHEMWEB.
 * fhempyDiscovery.popup(dev, devices): new devices were found, sent by the
 *   autodiscovery device to all open FHEMWEB pages
 * fhempyDiscovery.list(dev): all found devices (detail page button)
 * fhempyDiscovery.inline(dev, selector): found devices inside another dialog,
 *   e.g. the dialog after the fhempy installation
 * fhempyDiscovery.residents(dev): adds a resident with the phone in the
 *   network and via Bluetooth
 * fhempyDiscovery.tag(dev): adds a Bluetooth tag held next to the Raspberry Pi
 *
 * The device is created with set <dev> create <id> [name=...] [p0=...].
 * The list has a search, devices in FHEM and ignored devices are collapsed
 * below the new ones. Devices deleted in FHEM are new again.
 */
(function () {
  "use strict";

  var base = (typeof FW_root !== "undefined" ? FW_root : "/fhem") + "/fhempy/";
  var dev = "";
  var devices = [];
  /* id -> state of a tile: busy, created (device name), error */
  var state = {};
  /* text of the search field */
  var filter = "";

  function esc(t) { return $("<div>").text(t === undefined || t === null ? "" : String(t)).html(); }
  /* a click opens the detail page of the device */
  function deviceLink(name) {
    return '<a href="' + FW_root + "?detail=" + encodeURIComponent(name) + '">' + esc(name) + "</a>";
  }
  /* shows the link to the created resident or tag below the done message */
  function showCreated(d, kind) {
    cmd("get " + dev + " device " + kind, function (name) {
      name = (name || "").trim();
      if (name) d.find(".fdDone").first().after('<div class="fdDone">Open ' + deviceLink(name) + "</div>");
    });
  }

  /* FHEM command argument: quoted if needed, ; doubled for the command line */
  function arg(v) {
    v = String(v).replace(/;/g, ";;");
    return /[\s"]/.test(v) ? '"' + v.replace(/"/g, '\\"') + '"' : v;
  }

  function cmd(command, cb) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(command) + "&XHR=1", function (r) {
      cb((r || "").replace(/[\r\n]+$/, ""));
    });
  }

  function css() {
    if ($("#fhempyDiscoveryCss").length) return;
    $("head").append('<style id="fhempyDiscoveryCss">' +
      ".fhempyDiscovery{max-height:calc(100vh - 170px)!important;overflow-y:auto;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.35}" +
      ".fhempyDiscovery .fdIntro{margin:2px 0 12px}" +
      ".fhempyDiscovery .fdList{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}" +
      ".fhempyDiscovery .fdTile{border:1px solid rgba(128,128,128,0.35);border-radius:12px;padding:10px;display:flex;gap:10px;align-items:flex-start}" +
      ".fhempyDiscovery .fdOff{opacity:0.55}" +
      ".fhempyDiscovery .fdLogo{flex:none;width:44px;height:44px;border-radius:10px;background:#fff;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 0 0 1px rgba(128,128,128,0.25);font-size:24px;overflow:hidden}" +
      ".fhempyDiscovery .fdLogo img{width:34px;height:34px;object-fit:contain}" +
      ".fhempyDiscovery .fdTitle{font-weight:600;overflow:hidden;text-overflow:ellipsis}" +
      ".fhempyDiscovery .fdInfo{font-size:12px;opacity:0.7}" +
      ".fhempyDiscovery .fdHint{font-size:12px;opacity:0.85;margin-top:3px}" +
      ".fhempyDiscovery .fdBtns{margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}" +
      ".fhempyDiscovery .fdBtn{display:inline-block;padding:3px 12px;border-radius:12px;background:#4B8BBE;color:#fff;font-size:13px;cursor:pointer;border:none;white-space:nowrap}" +
      ".fhempyDiscovery .fdBtn.fdGrey{background:rgba(128,128,128,0.35);color:inherit}" +
      ".fhempyDiscovery .fdBtn[disabled]{opacity:0.6;cursor:default}" +
      ".fhempyDiscovery input[type=text],.fhempyDiscovery input[type=password]{width:100%;margin:3px 0 0;box-sizing:border-box;padding:5px 8px;border-radius:8px;border:1px solid rgba(128,128,128,0.45);font-size:13px;background:transparent;color:inherit}" +
      ".fhempyDiscovery label{font-size:12px;font-weight:600;display:block;margin-top:5px}" +
      ".fhempyDiscovery .fdDone{font-size:12px;color:#3fa34d;font-weight:600}" +
      ".fhempyDiscovery .fdDone a{color:inherit;text-decoration:underline}" +
      ".fhempyDiscovery .fdErr{font-size:12px;color:#d64545;white-space:pre-wrap}" +
      ".fhempyDiscovery .fdEmpty{opacity:0.75;margin:16px 0;text-align:center}" +
      ".fhempyDiscovery input.fdSearch{margin:0 0 10px}" +
      ".fhempyDiscovery details.fdMore{margin-top:12px}" +
      ".fhempyDiscovery details.fdMore summary{cursor:pointer;font-weight:600;font-size:13px;opacity:0.8;margin-bottom:8px}" +
      ".fhempyDiscovery .fdChoice{display:flex;gap:8px;align-items:center;padding:7px 9px;border:1px solid rgba(128,128,128,0.35);border-radius:10px;margin:6px 0;cursor:pointer}" +
      ".fhempyDiscovery .fdChoice input{margin:0}" +
      ".fhempyDiscovery .fdStep{font-weight:600;font-size:15px;margin:4px 0 8px}" +
      "@keyframes fdSpin{to{transform:rotate(360deg)}}" +
      ".fhempyDiscovery .fdSpin{display:inline-block;width:12px;height:12px;border-radius:50%;border:2px solid #4B8BBE;border-top-color:transparent;animation:fdSpin 1s linear infinite;vertical-align:-2px;margin-right:6px}" +
      "</style>");
  }

  function logo(d) {
    var inner = d.logo ? '<img src="' + base + d.logo + '" alt="">' : (d.icon || "🧩");
    return '<span class="fdLogo">' + inner + "</span>";
  }

  /* --- dialog --- */

  function dialog(id, title) {
    css();
    var d = $("#" + id);
    if (d.length && d.dialog("instance")) return d;
    d.remove();
    d = $('<div id="' + id + '" class="fhempyDiscovery"></div>');
    $("body").append(d);
    d.dialog({
      modal: true,
      title: title,
      width: Math.min(760, $(window).width() - 20),
      close: function () { $(this).remove(); }
    });
    return d;
  }

  function buttons(d, list) {
    if (!d.dialog("instance")) return;
    d.dialog("option", "buttons", list);
    d.dialog("option", "position", { my: "center", at: "center", of: window });
  }

  /* --- found devices --- */

  function tile(d, i) {
    var st = state[d.id] || {};
    var info = [d.kind, d.model, d.ip].filter(function (x) { return x && x != d.title; });
    var html = '<div class="fdTile' + (d.status == "ignored" ? " fdOff" : "") + '" data-i="' + i + '">' +
      logo(d) + '<div style="min-width:0;flex:1"><div class="fdTitle">' + esc(d.title) + "</div>" +
      '<div class="fdInfo">' + esc(info.join(" · ")) + "</div>";
    if (!st.created && (d.status == "exists" || d.status == "created")) {
      /* in FHEM already: link to the device, MQTT devices can be set up again */
      html += '<div class="fdDone">✓ ' + (st.recreated ? "set up again" : "in FHEM") + (d.device ? ": " + deviceLink(d.device) : "") + "</div>";
      if (d.can_recreate && d.device) {
        html += '<div class="fdBtns"><span class="fdBtn fdGrey fdRecreate" title="Readings, commands, state, alias and icon like a new device. ' +
          'The name and the other attributes (room, group...) stay.">' +
          (st.busy ? '<span class="fdSpin"></span>' : "") + "Set up again</span></div>" +
          (st.error ? '<div class="fdErr">' + esc(st.error) + "</div>" : "");
      }
      return html + "</div></div>";
    }
    html += (d.deleted && !st.created ? '<div class="fdHint">Deleted in FHEM, Create sets it up again.</div>' : "") +
      (d.hint ? '<div class="fdHint">' + esc(d.hint) + "</div>" : "");
    if (st.created) {
      /* a click on the link opens the new device */
      var done = d.action == "set" ? "pairing started, see the " + esc(d.kind) + " device" : "created, see the room fhempy";
      if (st.device) {
        var link = deviceLink(st.device);
        done = (d.action == "set" ? "pairing started, see " : "created: ") + link;
      }
      return html + '<div class="fdDone">✓ ' + done + "</div></div></div>";
    }
    if (d.status == "ignored") {
      return html + '<div class="fdBtns"><span class="fdBtn fdGrey fdUnignore">Offer again</span></div></div></div>';
    }
    (d.params || []).forEach(function (p, j) {
      html += "<label>" + esc(p.label) + (p.optional ? ' <span style="font-weight:normal;opacity:0.6">(optional)</span>' : "") +
        '<input type="' + (p.secret ? "password" : "text") + '" class="fdParam" data-j="' + j + '" placeholder="' + esc(p.placeholder) + '"' +
        (p.help ? ' title="' + esc(p.help) + '"' : "") + "></label>";
    });
    var label = d.action == "installer" ? "Set up..." : "Create";
    html += '<div class="fdBtns"><span class="fdBtn fdCreate">' +
      (st.busy ? '<span class="fdSpin" style="border-color:#fff;border-top-color:transparent"></span>' : "") + label +
      '</span><span class="fdBtn fdGrey fdIgnore">Ignore</span></div>' +
      (st.error ? '<div class="fdErr">' + esc(st.error) + "</div>" : "");
    return html + "</div></div>";
  }

  /* the device contains all words of the search */
  function matches(d) {
    var text = [d.title, d.kind, d.model, d.ip, d.module, d.device].join(" ").toLowerCase();
    return filter.toLowerCase().split(/\s+/).every(function (w) { return text.indexOf(w) >= 0; });
  }

  /* new devices on top, devices in FHEM and ignored devices collapsed below;
     tiles changed in this dialog stay where they are */
  function section(d) {
    if ((state[d.id] && !state[d.id].recreate) || d.status == "new") return "new";
    return d.status == "ignored" ? "ignored" : "fhem";
  }

  function render(container, empty) {
    var search = container.children(".fdSearch");
    var results = container.children(".fdResults");
    if (!results.length) {
      search = $('<input type="text" class="fdSearch" placeholder="Search (name, type, IP...)">').val(filter);
      results = $('<div class="fdResults"></div>');
      container.empty().append(search, results);
      search.on("input", function () {
        filter = $(this).val().trim();
        render(container, empty);
      });
    }
    var open = {};
    results.find("details.fdMore").each(function () { open[$(this).data("s")] = this.open; });
    search.toggle(devices.length > 1);
    if (!devices.length) {
      results.html('<div class="fdEmpty">' + (empty || "No new devices found yet.") + "</div>");
      return;
    }
    var groups = { "new": "", fhem: "", ignored: "" }, count = { "new": 0, fhem: 0, ignored: 0 };
    devices.forEach(function (d, i) {
      if (!matches(d)) return;
      var s = section(d);
      groups[s] += tile(d, i);
      count[s]++;
    });
    function more(s, title) {
      if (!count[s]) return "";
      /* opened by the search, otherwise as the user left it */
      var isOpen = filter ? true : open[s];
      return '<details class="fdMore" data-s="' + s + '"' + (isOpen ? " open" : "") + "><summary>" + title +
        " (" + count[s] + ")</summary>" + (s == "fhem" ? recreateAll() : "") + '<div class="fdList">' + groups[s] + "</div></details>";
    }
    function recreateAll() {
      var list = devices.filter(function (d) { return d.can_recreate && d.device && section(d) == "fhem" && matches(d); });
      if (list.length < 2) return "";
      return '<div class="fdBtns" style="margin:0 0 8px"><span class="fdBtn fdGrey fdRecreateAll" ' +
        'title="Sets up these MQTT devices again like new ones, the names stay.">Set up all ' + list.length + " again</span></div>";
    }
    var html = count["new"] ? '<div class="fdList">' + groups["new"] + "</div>" :
      '<div class="fdEmpty">' + (filter ? "No device matches the search." : (empty || "No new devices found yet.")) + "</div>";
    results.html(html + more("fhem", "Already in FHEM") + more("ignored", "Ignored"));
    results.find(".fdCreate").click(function () { create(container, devices[$(this).closest(".fdTile").data("i")]); });
    results.find(".fdRecreate").click(function () { recreate(container, devices[$(this).closest(".fdTile").data("i")], empty); });
    results.find(".fdRecreateAll").click(function () {
      devices.forEach(function (d) {
        if (d.can_recreate && d.device && section(d) == "fhem" && matches(d)) recreate(container, d, empty);
      });
    });
    results.find(".fdIgnore").click(function () {
      var d = devices[$(this).closest(".fdTile").data("i")];
      cmd("set " + dev + " ignore " + arg(d.id), function () {
        d.status = "ignored";
        delete state[d.id];
        render(container, empty);
      });
    });
    results.find(".fdUnignore").click(function () {
      var d = devices[$(this).closest(".fdTile").data("i")];
      cmd("set " + dev + " unignore " + arg(d.id), function () {
        d.status = "new";
        render(container, empty);
      });
    });
  }

  /* readings, commands and state like a new device, the name stays */
  function recreate(container, d, empty) {
    var st = state[d.id] = state[d.id] || {};
    if (st.busy) return;
    st.recreate = true;
    st.busy = true;
    st.error = "";
    render(container, empty);
    cmd("set " + dev + " recreate " + arg(d.id), function (r) {
      st.busy = false;
      if (r) st.error = r.replace(/<br>/g, "\n").replace(/<[^>]+>/g, "");
      else st.recreated = true;
      render(container, empty);
    });
  }

  function create(container, d) {
    var st = state[d.id] = state[d.id] || {};
    if (st.busy) return;
    if (d.action == "installer") {
      /* the module installer asks for the rest, e.g. keys of the account */
      $.getScript(FW_root + "/fhempy/modules.js", function () {
        $(".fhempyDiscovery").each(function () { if ($(this).dialog("instance")) $(this).dialog("close"); });
        fhempyModules("", { id: d.module, prefill: d.prefill || {} });
      });
      return;
    }
    var tileDiv = container.find('.fdTile[data-i="' + devices.indexOf(d) + '"]');
    var command = "set " + dev + " create " + arg(d.id);
    var missing = [];
    tileDiv.find(".fdParam").each(function () {
      var j = $(this).data("j"), v = $(this).val().trim();
      if (v) command += " p" + j + "=" + arg(v);
      else if (!d.params[j].optional) missing.push(d.params[j].label);
    });
    if (missing.length) {
      st.error = "Please fill in: " + missing.join(", ");
      render(container);
      return;
    }
    st.busy = true;
    st.error = "";
    render(container);
    cmd(command, function (r) {
      st.busy = false;
      if (r) {
        st.error = r.replace(/<br>/g, "\n").replace(/<[^>]+>/g, "");
        render(container);
        return;
      }
      st.created = true;
      render(container);
      cmd("get " + dev + " device " + arg(d.id), function (name) {
        st.device = (name || "").trim();
        if (st.device) render(container);
      });
    });
  }

  function createAll(container) {
    devices.forEach(function (d) {
      if (d.status == "new" && !(d.params || []).length && d.action == "define" && !(state[d.id] || {}).created) {
        create(container, d);
      }
    });
  }

  function load(cb) {
    cmd("get " + dev + " candidates", function (r) {
      try { devices = JSON.parse(r || "[]"); } catch (e) { devices = []; }
      cb();
    });
  }

  function showDevices(title, empty) {
    filter = "";
    var d = dialog("fhempyDiscoveryList", title);
    var container = $('<div class="fdIntro"></div>');
    d.html('<div class="fdIntro">These devices were found in your network and via Bluetooth. ' +
      'A click on Create sets them up in FHEM.</div>').append(container);
    render(container, empty);
    var list = [{ text: "Later", click: function () { $(this).dialog("close"); } }];
    var simple = devices.filter(function (x) { return x.status == "new" && !(x.params || []).length && x.action == "define"; });
    if (simple.length > 1) list.unshift({ text: "Create all", click: function () { createAll(container); } });
    buttons(d, list);
  }

  var api = {};

  api.popup = function (name, found) {
    dev = name;
    /* another popup is open already: add the new devices */
    var known = {};
    devices.forEach(function (d) { known[d.id] = 1; });
    if ($("#fhempyDiscoveryList").length) {
      found.forEach(function (d) { if (!known[d.id]) devices.push(d); });
    } else {
      devices = found;
    }
    showDevices(found.length == 1 ? "New device found" : "New devices found");
  };

  api.list = function (name) {
    dev = name;
    load(function () { showDevices("Found devices", "No new devices found. New devices show up here and as popup as soon as they are switched on."); });
  };

  /* found devices inside another dialog, refreshed while it is open */
  api.inline = function (name, selector) {
    dev = name;
    var container = $(selector);
    css();
    container.addClass("fhempyDiscovery").css("max-height", "none");
    filter = "";
    function refresh(count) {
      if (!document.body.contains(container[0])) return;
      load(function () {
        render(container, '<span class="fdSpin"></span>Searching your network and Bluetooth...');
        if (count < 40) setTimeout(function () { refresh(count + 1); }, 3000);
      });
    }
    refresh(0);
  };

  /* --- residents --- */

  function poll(kind, cb) {
    cmd("get " + dev + " search " + kind, function (r) {
      var res;
      try { res = JSON.parse(r); } catch (e) { res = { state: "failed", error: r }; }
      if (res.state == "searching") setTimeout(function () { poll(kind, cb); }, 1500);
      else cb(res);
    });
  }

  function search(kind, cb) {
    cmd("set " + dev + " search" + kind.charAt(0).toUpperCase() + kind.slice(1), function (r) {
      if (r) cb({ state: "failed", error: r });
      else setTimeout(function () { poll(kind, cb); }, 1500);
    });
  }

  function choices(list, label, extra) {
    if (!list.length) return "";
    return list.map(function (x, i) {
      return '<label class="fdChoice' + (x.used ? " fdOff" : "") + '" style="font-weight:normal;font-size:14px">' +
        '<input type="radio" name="fdChoice" value="' + i + '"' + (x.used ? " disabled" : "") + "> " +
        "<span><b>" + esc(label(x)) + '</b><br><span class="fdInfo">' + esc(extra(x)) +
        (x.used ? " · in use already" : "") + "</span></span></label>";
    }).join("");
  }

  api.residents = function (name) {
    dev = name;
    var d = dialog("fhempyDiscoveryResidents", "Add resident");
    var resident = { person: "", mac: "", bt: "" };

    function stepNetwork() {
      d.html('<div class="fdStep">1. Phone in the network</div>' +
        "<div><span class=\"fdSpin\"></span>Searching phones in your network...</div>");
      buttons(d, [{ text: "Cancel", click: function () { $(this).dialog("close"); } }]);
      search("phones", function (res) {
        var phones = res.result || [];
        d.html('<div class="fdStep">1. Phone in the network</div>' +
          '<label>Name of the resident<input type="text" id="fdPerson" placeholder="Anna" value="' + esc(resident.person) + '"></label>' +
          '<div class="fdIntro" style="margin-top:10px">Which phone belongs to this resident? The phone has to be in the WiFi.</div>' +
          (res.state == "failed" ? '<div class="fdErr">' + esc(res.error) + "</div>" : "") +
          (choices(phones, function (p) { return p.name; }, function (p) { return p.ip + " · " + p.mac; }) ||
            '<div class="fdEmpty">No phone found. Unlock the phone so it uses the WiFi and search again.</div>') +
          '<div class="fdErr" id="fdError"></div>');
        $("#fdPerson").focus();
        buttons(d, [
          { text: "Next", click: function () {
            resident.person = $("#fdPerson").val().trim();
            var i = $("input[name=fdChoice]:checked").val();
            resident.mac = i === undefined ? "" : phones[i].mac;
            if (!resident.person) { $("#fdError").text("Please enter the name of the resident"); return; }
            stepBluetooth();
          } },
          { text: "Search again", click: stepNetwork },
          { text: "Cancel", click: function () { $(this).dialog("close"); } }
        ]);
      });
    }

    function stepBluetooth() {
      d.html('<div class="fdStep">2. Phone via Bluetooth</div>' +
        "<div class=\"fdIntro\">With Bluetooth the resident is also detected while the phone's WiFi sleeps. " +
        "<b>Open the Bluetooth settings on the phone now</b> and keep them open, then click Search.</div>");
      buttons(d, [
        { text: "Search", click: function () {
          d.html('<div class="fdStep">2. Phone via Bluetooth</div>' +
            "<div><span class=\"fdSpin\"></span>Searching for 20 seconds, keep the Bluetooth settings of the phone open...</div>");
          buttons(d, []);
          search("bluetooth", function (res) {
            var list = res.result || [];
            d.html('<div class="fdStep">2. Phone via Bluetooth</div>' +
              (res.state == "failed" ? '<div class="fdErr">' + esc(res.error) + "</div>" : "") +
              (choices(list, function (b) { return b.name; }, function (b) { return b.address; }) ||
                '<div class="fdEmpty">No phone found. Are the Bluetooth settings open on the phone?</div>'));
            buttons(d, [
              { text: "Next", click: function () {
                var i = $("input[name=fdChoice]:checked").val();
                resident.bt = i === undefined ? "" : list[i].address;
                finish();
              } },
              { text: "Search again", click: stepBluetooth },
              { text: "Skip", click: function () { resident.bt = ""; finish(); } }
            ]);
          });
        } },
        { text: "Skip", click: function () { resident.bt = ""; finish(); } }
      ]);
    }

    function finish() {
      if (!resident.mac && !resident.bt) {
        d.html('<div class="fdErr">Please choose the phone in the network or via Bluetooth.</div>');
        buttons(d, [{ text: "Back", click: stepNetwork }]);
        return;
      }
      d.html("<div><span class=\"fdSpin\"></span>Creating the resident...</div>");
      buttons(d, []);
      var command = "set " + dev + " addResident person=" + arg(resident.person) +
        (resident.mac ? " mac=" + arg(resident.mac) : "") + (resident.bt ? " bt=" + arg(resident.bt) : "");
      cmd(command, function (r) {
        if (r) {
          d.html('<div class="fdErr">' + esc(r) + "</div>");
          buttons(d, [{ text: "Back", click: stepNetwork }]);
          return;
        }
        d.html('<div class="fdDone" style="font-size:16px;margin:10px 0">✓ ' + esc(resident.person) + " was added</div>" +
          "<div>" + esc(resident.person) + " is at home as soon as the phone is seen " +
          (resident.mac && resident.bt ? "in the network or via Bluetooth" : (resident.mac ? "in the network" : "via Bluetooth")) +
          ". The residents are in the room Residents.</div>");
        buttons(d, [
          { text: "Add another resident", click: function () { resident = { person: "", mac: "", bt: "" }; stepNetwork(); } },
          { text: "Close", click: function () { $(this).dialog("close"); } }
        ]);
        showCreated(d, "resident");
      });
    }

    stepNetwork();
  };

  /* --- Bluetooth tag --- */

  api.tag = function (name) {
    dev = name;
    var d = dialog("fhempyDiscoveryTag", "Add Bluetooth tag");
    function start() {
      d.html('<div class="fdIntro"><b>Hold the tag right next to the Raspberry Pi</b> ' +
        "(or the Bluetooth stick) and click Search. Press its button if it has one.</div>" +
        '<div class="fdInfo">AirTags, Samsung SmartTags and other Find My tags change their address ' +
        "all the time and can't be used.</div>");
      buttons(d, [
        { text: "Search", click: function () {
          d.html("<div><span class=\"fdSpin\"></span>Searching for 15 seconds, keep the tag next to the Raspberry Pi...</div>");
          buttons(d, []);
          search("tag", function (res) {
            var tag = res.result;
            if (!tag) {
              d.html('<div class="fdErr">' + esc(res.error || "No tag found, or several devices are equally close. Hold only the tag next to the Raspberry Pi.") + "</div>");
              buttons(d, [{ text: "Search again", click: start }, { text: "Cancel", click: function () { $(this).dialog("close"); } }]);
              return;
            }
            d.html('<div class="fdDone" style="font-size:15px">✓ Found ' + esc(tag.name || "a tag") + "</div>" +
              '<div class="fdInfo">' + esc(tag.address) + " · signal " + esc(tag.rssi) + " dBm" + (tag.used ? " · in use already" : "") + "</div>" +
              '<label>What is it attached to?<input type="text" id="fdTagTitle" placeholder="Keys Anna"></label><div class="fdErr" id="fdError"></div>');
            $("#fdTagTitle").focus();
            buttons(d, [
              { text: "Create", click: function () {
                var title = $("#fdTagTitle").val().trim();
                if (!title) { $("#fdError").text("Please enter a name"); return; }
                cmd("set " + dev + " addTag title=" + arg(title) + " address=" + arg(tag.address), function (r) {
                  if (r) { $("#fdError").text(r); return; }
                  d.html('<div class="fdDone" style="font-size:16px;margin:10px 0">✓ ' + esc(title) + " was added</div>");
                  buttons(d, [{ text: "Add another tag", click: start }, { text: "Close", click: function () { $(this).dialog("close"); } }]);
                  showCreated(d, "tag");
                });
              } },
              { text: "Search again", click: start }
            ]);
          });
        } },
        { text: "Cancel", click: function () { $(this).dialog("close"); } }
      ]);
    }
    start();
  };

  window.fhempyDiscovery = api;
})();
