/*
 * fhempy module installer for FHEMWEB.
 * Opened by the "Install modules" button of the local fhempy device
 * (devStateIcon of BindingsIo): fhempyModules()
 *
 * Every module of the catalog (modules.json, built from the manifest.json files
 * by manifest2modules.py) has a tile. "Set up" defines the device
 * right away, modules needing more parameters ask for them first.
 */
(function () {
  "use strict";

  var base = (typeof FW_root !== "undefined" ? FW_root : "/fhem") + "/fhempy/";
  var docs = "https://github.com/fhempy/fhempy/tree/master/FHEM/bindings/python/fhempy/lib/";

  var categories = [
    { id: "popular", title: "Popular", icon: "⭐" },
    { id: "home", title: "Smart home", icon: "🏠" },
    { id: "energy", title: "Energy & solar", icon: "☀️" },
    { id: "cars", title: "Cars", icon: "🚗" },
    { id: "bt", title: "Bluetooth", icon: "📶" },
    { id: "media", title: "Media", icon: "🎵" },
    { id: "presence", title: "Presence & discovery", icon: "🔍" },
    { id: "tools", title: "Information & tools", icon: "🧰" }
  ];
  var byCat = {};
  categories.forEach(function (c) { byCat[c.id] = c; });
  var popular = ["matter", "matter_bridge", "zigbee2mqtt", "mcp_server",
                 "tuya_smartlife", "googlecast", "esphome", "openmeteo_weather"];

  /*
   * The catalog is built from the "installer" section of the manifest.json of
   * every module by manifest2modules.py.
   * id: fhempy module, name: suggested device name, single: only one device needed,
   * params: define arguments, modes: alternative argument sets (args are fixed values)
   */
  var modules = [];
  var byId = {};

  /* device name -> fhempy module of the defined fhempy devices */
  var defined = {};
  var allNames = {};
  var view = { cat: "all", search: "" };

  function esc(t) { return $("<div>").text(t === undefined ? "" : String(t)).html(); }

  function css() {
    if ($("#fhempyModulesCss").length) return;
    $("head").append('<style id="fhempyModulesCss">' +
      "#fhempyModules{max-height:calc(100vh - 170px)!important;overflow-y:auto;font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif;line-height:1.35}" +
      "#fhempyModules .fmTop{display:flex;align-items:center;gap:12px;margin-bottom:10px}" +
      "#fhempyModules .fmSearch{flex:1;padding:8px 12px;border-radius:18px;border:1px solid rgba(128,128,128,0.45);font-size:14px;background:transparent;color:inherit}" +
      "#fhempyModules .fmChips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}" +
      "#fhempyModules .fmChip{padding:4px 11px;border-radius:14px;border:1px solid rgba(128,128,128,0.4);cursor:pointer;font-size:13px;user-select:none;white-space:nowrap}" +
      "#fhempyModules .fmChip.fmActive{background:#4B8BBE;border-color:#4B8BBE;color:#fff}" +
      "#fhempyModules .fmList{max-height:calc(100vh - 330px);overflow-y:auto;padding:2px 4px 4px 2px}" +
      "#fhempyModules .fmCat{font-weight:600;margin:14px 0 8px;font-size:15px}" +
      "#fhempyModules .fmCat:first-child{margin-top:2px}" +
      "#fhempyModules .fmGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:10px}" +
      "#fhempyModules .fmTile{border:1px solid rgba(128,128,128,0.35);border-radius:12px;padding:10px;cursor:pointer;display:flex;gap:10px;align-items:flex-start;transition:transform .15s,box-shadow .15s}" +
      "#fhempyModules .fmTile:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.15)}" +
      "#fhempyModules .fmLogo{position:relative;flex:none;width:44px;height:44px;border-radius:10px;background:#fff;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 0 0 1px rgba(128,128,128,0.25);font-size:24px}" +
      "#fhempyModules .fmLogo img{width:34px;height:34px;object-fit:contain}" +
      "#fhempyModules .fmLogo.fmBig{width:64px;height:64px;border-radius:14px;font-size:36px}" +
      "#fhempyModules .fmLogo.fmBig img{width:50px;height:50px}" +
      "#fhempyModules .fmBadge{position:absolute;right:-6px;bottom:-5px;background:#4B8BBE;color:#fff;border-radius:50%;width:18px;height:18px;font-size:11px;line-height:18px;text-align:center;border:2px solid #fff}" +
      "#fhempyModules .fmTitle{font-weight:600}" +
      "#fhempyModules .fmDesc{font-size:12px;opacity:0.75;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}" +
      "#fhempyModules .fmDone{font-size:12px;color:#3fa34d;font-weight:600;margin-top:3px}" +
      "#fhempyModules .fmBtn{display:inline-block;padding:3px 14px;border-radius:12px;background:#4B8BBE;color:#fff;font-size:13px;cursor:pointer;border:none}" +
      "#fhempyModules .fmBtn.fmBig{padding:7px 22px;font-size:15px;font-weight:600}" +
      "#fhempyModules .fmBtn[disabled]{opacity:0.6;cursor:default}" +
      "#fhempyModules .fmField{margin:10px 0}" +
      "#fhempyModules .fmField label{display:block;font-weight:600;margin-bottom:3px}" +
      "#fhempyModules .fmField input[type=text],#fhempyModules .fmField input[type=password],#fhempyModules .fmField select{width:100%;margin:0;box-sizing:border-box;padding:7px 10px;border-radius:8px;border:1px solid rgba(128,128,128,0.45);font-size:14px;background:transparent;color:inherit}" +
      "#fhempyModules .fmField select option{color:#000}" +
      "#fhempyModules .fmHelp{font-size:12px;opacity:0.7;margin-top:2px}" +
      "#fhempyModules .fmMode{display:block;margin:4px 0;cursor:pointer}" +
      "#fhempyModules .fmMode input{margin:0 6px 0 0;vertical-align:-1px}" +
      "#fhempyModules .fmError{color:#d64545;margin-top:8px;white-space:pre-wrap}" +
      "#fhempyModules .fmOk{color:#3fa34d;font-weight:600;font-size:16px;margin:10px 0}" +
      "#fhempyModules .fmEmpty{opacity:0.7;margin:20px 0;text-align:center}" +
      "@keyframes fmSpin{to{transform:rotate(360deg)}}" +
      "#fhempyModules .fmSpin{display:inline-block;width:12px;height:12px;border-radius:50%;border:2px solid #fff;border-top-color:transparent;animation:fmSpin 1s linear infinite;vertical-align:-2px;margin-right:6px}" +
      "</style>");
  }

  function logo(m, big) {
    var inner = m.logo ? '<img src="' + base + m.logo + '" alt="">' : (m.icon || "🧩");
    var badge = m.badge ? '<span class="fmBadge">' + m.badge + "</span>" : "";
    return '<span class="fmLogo' + (big ? " fmBig" : "") + '">' + inner + badge + "</span>";
  }

  function devicesOf(id) {
    var r = [];
    for (var n in defined) if (defined[n] == id) r.push(n);
    return r.sort();
  }

  function matches(m) {
    var s = view.search.toLowerCase();
    if (!s) return true;
    return (m.id + " " + m.title + " " + m.description).toLowerCase().indexOf(s) >= 0;
  }

  function tile(m) {
    var devs = devicesOf(m.id);
    var done = devs.length ? '<div class="fmDone">✓ ' +
      (devs.length == 1 ? esc(devs[0]) : devs.length + " devices") + "</div>" : "";
    return '<div class="fmTile" data-id="' + m.id + '">' + logo(m) +
      '<div style="min-width:0"><div class="fmTitle">' + esc(m.title) + "</div>" +
      '<div class="fmDesc">' + esc(m.description) + "</div>" + done + "</div></div>";
  }

  function renderList() {
    var html = "";
    var shown = 0;
    function section(cat, list) {
      list = list.filter(matches);
      if (!list.length) return;
      shown += list.length;
      html += '<div class="fmCat">' + cat.icon + " " + esc(cat.title) + '</div><div class="fmGrid">' +
        list.map(tile).join("") + "</div>";
    }
    categories.forEach(function (c) {
      if (view.cat != "all" && view.cat != c.id) return;
      /* while searching, every module shows up once in its own category */
      if (c.id == "popular") {
        if (!view.search) section(c, popular.map(function (id) { return byId[id]; }).filter(Boolean));
        return;
      }
      section(c, modules.filter(function (m) { return (byCat[m.category] ? m.category : "tools") == c.id; }));
    });
    if (!shown) html = '<div class="fmEmpty">No module found for “' + esc(view.search) +
      '”. <a href="https://github.com/fhempy/fhempy#-modules" target="_blank">All modules on GitHub</a></div>';
    $("#fhempyModules .fmList").html(html).scrollTop(0);
  }

  function renderMain() {
    var chips = '<span class="fmChip" data-cat="all">All</span>' + categories.map(function (c) {
      return '<span class="fmChip" data-cat="' + c.id + '">' + c.icon + " " + esc(c.title) + "</span>";
    }).join("");
    $("#fhempyModules").html(
      '<div class="fmTop"><input class="fmSearch" type="search" placeholder="🔍 Search ' +
      modules.length + ' modules, e.g. tuya, weather, car..." value="' + esc(view.search) + '"></div>' +
      '<div class="fmChips">' + chips + '</div><div class="fmList"></div>');
    $("#fhempyModules .fmChip[data-cat='" + view.cat + "']").addClass("fmActive");
    renderList();
    $("#fhempyModules .fmSearch").on("input", function () {
      view.search = $(this).val().trim();
      renderList();
    }).focus();
    $("#fhempyModules .fmChip").click(function () {
      view.cat = $(this).data("cat");
      $("#fhempyModules .fmChip").removeClass("fmActive");
      $(this).addClass("fmActive");
      renderList();
    });
    $("#fhempyModules .fmList").on("click", ".fmTile", function () {
      renderDetail(byId[$(this).data("id")]);
    });
    buttons([{ text: "Close", click: close }]);
  }

  function freeName(name) {
    var n = name, i = 2;
    while (allNames[n]) n = name + "_" + i++;
    return n;
  }

  function field(prm, i) {
    var id = "fmParam" + i;
    var label = esc(prm.label) + (prm.optional ? ' <span style="font-weight:normal;opacity:0.6">(optional)</span>' : "");
    var input;
    if (prm.options) {
      input = '<select id="' + id + '">' + (prm.optional ? '<option value=""></option>' : "") +
        prm.options.map(function (o) { return "<option>" + esc(o) + "</option>"; }).join("") + "</select>";
    } else {
      input = '<input id="' + id + '" type="' + (prm.secret ? "password" : "text") + '" placeholder="' +
        esc(prm.placeholder) + '" autocomplete="off">';
    }
    return '<div class="fmField"><label for="' + id + '">' + label + "</label>" + input +
      (prm.help ? '<div class="fmHelp">' + esc(prm.help) + "</div>" : "") + "</div>";
  }

  function modeOf(m) {
    if (!m.modes) return { args: m.args || [], params: m.params || [] };
    return m.modes[+$("input[name=fmMode]:checked").val() || 0];
  }

  function renderParams(m) {
    var mode = modeOf(m);
    $("#fhempyModules .fmParams").html(mode.params.map(field).join(""));
    center();
  }

  /* FHEM define argument: quoted if needed, ; doubled for the command line */
  function arg(v) {
    v = v.replace(/;/g, ";;");
    return /[\s"]/.test(v) ? '"' + v.replace(/"/g, '\\"') + '"' : v;
  }

  function renderDetail(m) {
    var devs = devicesOf(m.id);
    var existing = devs.length ? '<div class="fmDone" style="margin-top:6px">✓ Set up already: ' +
      devs.map(function (n) {
        return '<a href="' + FW_root + "?detail=" + encodeURIComponent(n) + '">' + esc(n) + "</a>";
      }).join(", ") + "</div>" : "";
    var modes = m.modes ? '<div class="fmField"><label>How do you want to connect?</label>' +
      m.modes.map(function (mo, i) {
        return '<label class="fmMode" style="font-weight:normal"><input type="radio" name="fmMode" value="' + i + '"' +
          (i ? "" : " checked") + "> " + esc(mo.label) + "</label>";
      }).join("") + "</div>" : "";
    $("#fhempyModules").html(
      '<div><a href="#" class="fmBack">← All modules</a></div>' +
      '<div style="display:flex;gap:14px;align-items:center;margin:12px 0">' + logo(m, true) +
      '<div><div class="fmTitle" style="font-size:18px">' + esc(m.title) + "</div>" +
      '<div style="font-size:13px;opacity:0.8">' + esc(m.description) + "</div>" +
      '<div style="font-size:12px;margin-top:3px"><a href="' + docs + m.id + '" target="_blank">Documentation</a> · module ' +
      esc(m.id) + "</div>" + existing + "</div></div>" +
      '<div class="fmForm">' + modes +
      '<div class="fmField"><label for="fmName">Device name in FHEM</label><input id="fmName" type="text" value="' +
      esc(freeName(m.name)) + '"></div><div class="fmParams"></div><div class="fmError"></div></div>');
    renderParams(m);
    $("#fhempyModules input[name=fmMode]").change(function () { renderParams(m); });
    $("#fhempyModules .fmBack").click(function (e) { e.preventDefault(); renderMain(); });
    $("#fhempyModules input").keydown(function (e) { if (e.which == 13) setup(m); });
    buttons([
      { text: "Set up", "class": "fmSetupBtn", click: function () { setup(m); } },
      { text: "Back", click: renderMain }
    ]);
    var first = $("#fhempyModules .fmParams input, #fhempyModules .fmParams select").first();
    (first.length ? first : $("#fmName")).focus();
  }

  function setup(m) {
    var btn = $(".fmSetupBtn");
    if (btn.prop("disabled")) return;
    var err = $("#fhempyModules .fmError");
    var name = $("#fmName").val().trim();
    if (!/^[A-Za-z0-9._]+$/.test(name)) {
      err.text("The device name may only contain letters, digits, . and _");
      return;
    }
    if (allNames[name]) {
      err.text("A device named " + name + " exists already, please choose another name.");
      return;
    }
    var mode = modeOf(m);
    var args = mode.args.slice();
    var missing = [];
    var empty = null;
    mode.params.forEach(function (prm, i) {
      var v = ($("#fmParam" + i).val() || "").trim();
      if (v === "") {
        if (!prm.optional) missing.push(prm.label);
        else if (!empty) empty = prm.label;
        return;
      }
      /* optional arguments are positional, a later one needs the earlier ones */
      if (empty) {
        missing.push(empty);
        empty = null;
      }
      if (prm.multi) v.split(/\s+/).forEach(function (x) { args.push(arg(x)); });
      else args.push(arg(v));
    });
    if (missing.length) {
      err.text("Please fill in: " + missing.join(", "));
      return;
    }
    err.text("");
    btn.prop("disabled", true).html('<span class="fmSpin"></span>Setting up...');
    /* new fhempy devices use the local fhempy on their own */
    var cmd = "define " + name + " fhempy " + m.id + (args.length ? " " + args.join(" ") : "");
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      r = (r || "").replace(/[\r\n]+$/, "");
      if (r !== "") {
        btn.prop("disabled", false).text("Set up");
        err.text(r.replace(/<br>/g, "\n").replace(/<[^>]+>/g, ""));
        return;
      }
      defined[name] = m.id;
      allNames[name] = 1;
      done(m, name);
    });
  }

  function done(m, name) {
    $("#fhempyModules").html(
      '<div style="text-align:center;padding:10px 0">' + logo(m, true) +
      '<div class="fmOk">✓ ' + esc(m.title) + " is set up</div>" +
      "<div>The device <b>" + esc(name) + "</b> was created" + (m.category == "bt" || m.id == "matter" || m.id == "zigbee2mqtt" ?
        ". The first start installs everything it needs, this can take a few minutes." : ".") + "</div>" +
      '<div style="margin-top:6px;font-size:13px"><a href="' + docs + m.id + '" target="_blank">What can ' + esc(m.title) + " do?</a></div></div>");
    buttons([
      { text: "Open " + name, click: function () { location.href = FW_root + "?detail=" + encodeURIComponent(name); } },
      { text: "Set up another module", click: renderMain },
      { text: "Close", click: close }
    ]);
  }

  function buttons(list) {
    var d = $("#fhempyModules");
    if (!d.dialog("instance")) return;
    d.dialog("option", "buttons", list);
    center();
  }

  /* the content changed, keep the dialog on the screen */
  function center() {
    var d = $("#fhempyModules");
    if (d.dialog("instance")) d.dialog("option", "position", { my: "center", at: "center", of: window });
  }

  function close() {
    $("#fhempyModules").dialog("close");
  }

  function loadCatalog(cb) {
    if (modules.length) return cb();
    $.ajax({ url: base + "modules.json", dataType: "json", cache: false })
      .done(function (list) {
        modules = list;
        byId = {};
        modules.forEach(function (m) { byId[m.id] = m; });
        cb();
      })
      .fail(function (xhr, status, error) { cb(error || status); });
  }

  function loadDefined(cb) {
    var cmd = '{join(",", map {$_.":".InternalVal($_,"FHEMPYTYPE","")} devspec2array("TYPE=fhempy"))."|".join(",", devspec2array(".*"))}';
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1", function (r) {
      var parts = (r || "").replace(/[\r\n]+$/, "").split("|");
      defined = {};
      allNames = {};
      (parts[0] || "").split(",").forEach(function (d) {
        var x = d.split(":");
        if (x[0] && x[1]) defined[x[0]] = x[1];
      });
      (parts[1] || "").split(",").forEach(function (n) { if (n) allNames[n] = 1; });
      cb();
    });
  }

  window.fhempyModules = function (search) {
    css();
    $("#fhempyModules").remove();
    view = { cat: "all", search: search || "" };
    var div = $('<div id="fhempyModules"></div>');
    $("body").append(div);
    div.html('<div class="fmEmpty">Loading modules...</div>');
    div.dialog({
      modal: true,
      title: "Install fhempy modules",
      width: Math.min(820, $(window).width() - 20),
      close: function () { $(this).remove(); }
    });
    loadCatalog(function (err) {
      if (err) {
        div.html('<div class="fmError">The module list could not be loaded: ' + esc(err) + "</div>");
        buttons([{ text: "Close", click: close }]);
        return;
      }
      loadDefined(renderMain);
    });
  };
})();
