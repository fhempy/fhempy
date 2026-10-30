/*
 * Device dialog of the Matter bridge for FHEMWEB.
 * fhempyMatterBridgeLoad(bridge): reads the FHEM devices (set choose_devices)
 * fhempyMatterBridgeDevices(bridge, data): shows them, sent by the bridge.
 *   Search, filter by module/room, select all results, save adds and removes
 *   all changed devices with set <bridge> add/remove/add_type.
 */
(function () {
  "use strict";

  var bridge = "";
  var devices = [];
  var types = [];
  var rules = [];
  /* name -> true if the device should be in the Matter apps */
  var selected = {};
  /* name -> matterType chosen in the dialog */
  var chosenType = {};
  var filter = { text: "", module: "", room: "", supported: false };
  var autoAdd = false;
  /* error of the last save, shown after the devices were read again */
  var pendingError = "";

  var icons = {
    "switch": "🔘", outlet: "🔌", light: "💡", dimmer: "💡", blind: "🪟", thermostat: "🌡️",
    lock: "🔐", contact: "🚪", motion: "🏃", temperature: "🌡️", humidity: "💧"
  };

  function esc(t) { return $("<div>").text(t === undefined ? "" : String(t)).html(); }

  function css() {
    if ($("#fhempyMbCss").length) return;
    $("head").append('<style id="fhempyMbCss">' +
      "#fhempyMb{max-height:calc(100vh - 170px)!important;overflow-y:auto;line-height:1.35}" +
      "#fhempyMb .mbSearch{width:100%;box-sizing:border-box;font-size:16px;padding:8px 10px;border:1px solid #888;border-radius:4px}" +
      "#fhempyMb .mbChips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px;align-items:center}" +
      "#fhempyMb .mbLab{font-size:12px;opacity:.7;margin-right:2px}" +
      "#fhempyMb .mbChip{border:1px solid rgba(128,128,128,.5);border-radius:14px;padding:2px 10px;font-size:13px;cursor:pointer;white-space:nowrap}" +
      "#fhempyMb .mbChip.mbOn{background:#278727;color:#fff;border-color:#278727}" +
      "#fhempyMb .mbAll{display:flex;align-items:center;gap:8px;padding:8px 6px;border-bottom:2px solid rgba(128,128,128,.35);font-weight:bold;cursor:pointer}" +
      "#fhempyMb .mbRow{display:flex;align-items:center;gap:10px;padding:6px;border-bottom:1px solid rgba(128,128,128,.2);cursor:pointer}" +
      "#fhempyMb .mbRow.mbOff{cursor:default;opacity:.75}" +
      "#fhempyMb input[type=checkbox]{width:18px;height:18px;flex:none;accent-color:#278727}" +
      "#fhempyMb .mbName{flex:1;min-width:0}" +
      "#fhempyMb .mbInfo{display:block;font-size:12px;opacity:.65;overflow:hidden;text-overflow:ellipsis}" +
      "#fhempyMb .mbIn{font-size:11px;color:#278727;border:1px solid #278727;border-radius:8px;padding:0 5px;margin-left:6px;white-space:nowrap}" +
      "#fhempyMb .mbType{font-size:12px;border-radius:10px;padding:2px 8px;background:rgba(39,135,39,.12);white-space:nowrap}" +
      "#fhempyMb .mbType.mbNo{background:rgba(214,120,40,.15)}" +
      "#fhempyMb .mbType select{font-size:12px}" +
      "#fhempyMb .mbAuto{display:flex;align-items:center;gap:8px;margin:10px 0 2px;font-size:14px;cursor:pointer}" +
      "#fhempyMb .mbEmpty{opacity:.75;margin:20px 0;text-align:center}" +
      "#fhempyMb .mbError{color:#d64545;white-space:pre-wrap;margin:8px 0}" +
      "#fhempyMb .mbSum{font-size:14px;margin-top:10px}" +
      "@keyframes mbSpin{to{transform:rotate(360deg)}}" +
      "#fhempyMb .mbSpin{display:inline-block;width:28px;height:28px;border-radius:50%;border:3px solid #278727;border-top-color:transparent;animation:mbSpin 1s linear infinite;margin-bottom:10px}" +
      "</style>");
  }

  function dialog() {
    css();
    var d = $("#fhempyMb");
    if (!d.length || !d.dialog("instance")) {
      d.remove();
      d = $('<div id="fhempyMb"></div>');
      $("body").append(d);
      d.dialog({
        modal: true,
        title: "Matter devices",
        width: Math.min(800, $(window).width() - 20),
        close: function () { $(this).remove(); }
      });
    }
    return d;
  }

  function close() { $("#fhempyMb").dialog("close"); }

  function buttons(list) {
    var d = $("#fhempyMb");
    if (!d.dialog("instance")) return;
    d.dialog("option", "buttons", list);
    d.dialog("option", "position", { my: "center", at: "center", of: window });
  }

  function typeOf(dev) { return chosenType[dev.name] || dev.type; }

  function canSelect(dev) { return dev.via !== "rule" && !!typeOf(dev); }

  function matches(dev) {
    if (filter.module && dev.module !== filter.module) return false;
    if (filter.room && dev.rooms.indexOf(filter.room) < 0) return false;
    if (filter.supported && !typeOf(dev)) return false;
    var words = filter.text.toLowerCase().split(/\s+/).filter(Boolean);
    var text = [dev.name, dev.alias, dev.module, dev.rooms.join(" "), typeOf(dev)].join(" ").toLowerCase();
    return words.every(function (w) { return text.indexOf(w) >= 0; });
  }

  /* value -> count, most used first */
  function counts(key) {
    var c = {};
    devices.forEach(function (dev) {
      [].concat(dev[key]).forEach(function (v) { if (v) c[v] = (c[v] || 0) + 1; });
    });
    return Object.keys(c).sort(function (a, b) { return c[b] - c[a] || a.localeCompare(b); })
      .map(function (v) { return { value: v, count: c[v] }; });
  }

  function chips(label, key, list) {
    var html = '<span class="mbLab">' + label + "</span>";
    list.slice(0, 12).forEach(function (x) {
      html += '<span class="mbChip' + (filter[key] === x.value ? " mbOn" : "") + '" data-k="' + key +
        '" data-v="' + esc(x.value) + '">' + esc(x.value) + " (" + x.count + ")</span>";
    });
    return html;
  }

  function changes() {
    var add = [], remove = [];
    devices.forEach(function (dev) {
      var wasIn = dev.via !== "";
      if (selected[dev.name] && !wasIn) add.push(dev);
      if (!selected[dev.name] && wasIn && dev.via !== "rule") remove.push(dev);
    });
    if (autoAdd && filter.module)
      add = add.filter(function (dev) { return dev.module !== filter.module || chosenType[dev.name]; });
    return { add: add, remove: remove, rule: autoAdd && filter.module ? filter.module : "" };
  }

  function row(dev) {
    var t = typeOf(dev);
    var type;
    if (dev.type) {
      type = '<span class="mbType">' + (icons[t] || "") + " " + esc(t) + "</span>";
    } else {
      type = '<span class="mbType mbNo">type <select class="mbSel" data-n="' + esc(dev.name) + '"><option value="">choose…</option>' +
        types.map(function (x) { return "<option" + (x === t ? " selected" : "") + ">" + x + "</option>"; }).join("") +
        "</select></span>";
    }
    var info = [dev.alias ? dev.name : "", dev.module, dev.rooms.join(", ") || "no room"].filter(Boolean).join(" · ");
    if (dev.via === "rule") info += " · added by attribute devices";
    return '<div class="mbRow' + (canSelect(dev) ? "" : " mbOff") + '" data-n="' + esc(dev.name) + '">' +
      '<input type="checkbox"' + (selected[dev.name] ? " checked" : "") + (canSelect(dev) ? "" : " disabled") + ">" +
      '<div class="mbName">' + esc(dev.alias || dev.name) + (dev.via ? '<span class="mbIn">in Matter</span>' : "") +
      '<span class="mbInfo">' + esc(info) + "</span></div>" + type + "</div>";
  }

  function render(error) {
    var d = dialog();
    var focus = $("#fhempyMb .mbSearch").is(":focus");
    var html = "";
    if (error) html += '<div class="mbError">' + esc(error) + "</div>";
    html += '<input class="mbSearch" type="search" placeholder="Search name, room, module or type" value="' + esc(filter.text) + '">' +
      '<div class="mbChips">' + chips("Module", "module", counts("module")) + "</div>" +
      '<div class="mbChips">' + chips("Room", "room", counts("rooms")) +
      '<span class="mbChip' + (filter.supported ? " mbOn" : "") + '" data-k="supported">Only supported</span></div>' +
      '<div class="mbList"></div>';
    d.html(html);
    renderList();
    d.find(".mbSearch").on("input", function () { filter.text = $(this).val(); renderList(); });
    if (focus) d.find(".mbSearch").focus();
    d.find(".mbChip").click(function () {
      var k = $(this).data("k");
      if (k === "supported") filter.supported = !filter.supported;
      else filter[k] = filter[k] === String($(this).data("v")) ? "" : String($(this).data("v"));
      render(error);
    });
  }

  function renderList() {
    var d = $("#fhempyMb");
    var shown = devices.filter(matches);
    var selectable = shown.filter(canSelect);
    var allOn = selectable.length && selectable.every(function (dev) { return selected[dev.name]; });
    var html = "";
    if (selectable.length)
      html += '<label class="mbAll"><input type="checkbox" class="mbAllBox"' + (allOn ? " checked" : "") + "> Select all " +
        selectable.length + " results</label>";
    if (!shown.length) html += '<div class="mbEmpty">No FHEM device found.</div>';
    html += shown.map(row).join("");
    if (filter.module)
      html += '<label class="mbAuto"><input type="checkbox" class="mbAutoBox"' + (autoAdd ? " checked" : "") +
        "> Add all " + esc(filter.module) + " devices, also new ones automatically later</label>";
    if (rules.length) html += '<div class="mbSum">Attribute devices: ' + esc(rules.join(", ")) + "</div>";
    var c = changes();
    var parts = [];
    if (c.add.length) parts.push("<b>+" + c.add.length + " add</b>");
    if (c.remove.length) parts.push("<b>−" + c.remove.length + " remove</b>");
    if (c.rule) parts.push("<b>all " + esc(c.rule) + " devices</b>");
    var missing = shown.filter(function (dev) { return !typeOf(dev); }).length;
    if (missing) parts.push(missing + " need a type");
    html += '<div class="mbSum">' + (parts.join(" · ") || "No changes") + "</div>";
    d.find(".mbList").html(html);

    d.find(".mbRow").click(function (e) {
      if ($(e.target).is("select, option")) return;
      var dev = find($(this).data("n"));
      if (!dev || !canSelect(dev)) return;
      selected[dev.name] = !selected[dev.name];
      renderList();
    });
    d.find(".mbSel").on("click", function (e) { e.stopPropagation(); }).change(function () {
      var name = String($(this).data("n"));
      if ($(this).val()) {
        chosenType[name] = $(this).val();
        selected[name] = true;
      } else {
        delete chosenType[name];
        selected[name] = false;
      }
      renderList();
    });
    d.find(".mbAllBox").click(function (e) {
      e.preventDefault();
      selectable.forEach(function (dev) { selected[dev.name] = !allOn; });
      renderList();
    });
    d.find(".mbAutoBox").change(function () { autoAdd = this.checked; renderList(); });

    var count = c.add.length + c.remove.length + (c.rule ? 1 : 0);
    buttons([
      { text: "Cancel", click: close },
      { text: "Save" + (count ? " (" + count + ")" : ""), disabled: !count, click: save }
    ]);
  }

  function find(name) {
    name = String(name);
    for (var i = 0; i < devices.length; i++) if (devices[i].name === name) return devices[i];
    return null;
  }

  function command(cmd, cb) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      cb((r || "").replace(/[\r\n]+$/, "").replace(/<br>/g, "\n").replace(/<[^>]+>/g, ""));
    });
  }

  function save() {
    var c = changes();
    var cmds = [];
    if (c.add.length)
      cmds.push("set " + bridge + " add " + c.add.map(function (dev) {
        return dev.name + (chosenType[dev.name] ? ":" + chosenType[dev.name] : "");
      }).join(","));
    if (c.remove.length)
      cmds.push("set " + bridge + " remove " + c.remove.map(function (dev) { return dev.name; }).join(","));
    if (c.rule) cmds.push("set " + bridge + " add_type " + c.rule);
    var d = dialog();
    d.html('<div class="mbEmpty"><span class="mbSpin"></span><br><b>Saving...</b></div>');
    buttons([]);
    var errors = [];
    var next = function () {
      if (!cmds.length) {
        if (errors.length) {
          load(errors.join("\n"));
        } else {
          d.html('<div class="mbEmpty"><b>Saved.</b><br>The devices show up in your Matter apps in a few seconds.</div>');
          buttons([{ text: "Close", click: close }]);
          setTimeout(function () { location.reload(); }, 3000);
        }
        return;
      }
      command(cmds.shift(), function (r) { if (r) errors.push(r); next(); });
    };
    next();
  }

  function load(error) {
    var d = dialog();
    d.html('<div class="mbEmpty"><span class="mbSpin"></span><br><b>Reading your FHEM devices...</b></div>');
    buttons([{ text: "Close", click: close }]);
    command("set " + bridge + " choose_devices", function (r) {
      if (r) d.html('<div class="mbError">' + esc(r) + "</div>");
    });
    pendingError = error || "";
  }

  window.fhempyMatterBridgeLoad = function (name) {
    bridge = name;
    load();
  };

  window.fhempyMatterBridgeDevices = function (name, data) {
    bridge = name;
    devices = (data.devices || []).slice().sort(function (a, b) {
      return (a.alias || a.name).localeCompare(b.alias || b.name);
    });
    types = data.types || [];
    rules = data.rules || [];
    selected = {};
    chosenType = {};
    autoAdd = false;
    devices.forEach(function (dev) { selected[dev.name] = dev.via !== ""; });
    var error = pendingError;
    pendingError = "";
    render(error);
  };
})();
