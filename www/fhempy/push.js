/*
 * Push notifications for FHEMWEB, used on the detail page of the fhempy
 * module push. fhempyPush(cfg) shows the next step for this browser:
 * open the https address, add to home screen (iPhone), enable notifications.
 * cfg: {dev, key, devices: [{id, name}], addresses: [{url, kind, qr, ca}],
 *       remote_access, history: [{id, ts, title, body, image, url, to,
 *       actions, used, delivered, total}]}
 * fhempyPushHistory shows the sent messages of the last 7 days.
 */
(function () {
  "use strict";

  var cfg;
  var box;

  function esc(t) {
    return String(t === undefined || t === null ? "" : t).replace(/&/g, "&amp;")
      .replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function css() {
    if ($("#fhempyPushCss").length) return;
    $("head").append('<style id="fhempyPushCss">' +
      "#fhempyPush{line-height:1.4;max-width:720px}" +
      "#fhempyPush .fpBtn{display:inline-block;padding:9px 18px;margin:6px 6px 6px 0;border-radius:8px;border:0;background:#2a6ebb;color:#fff!important;font-weight:bold;font-size:15px;cursor:pointer;text-decoration:none}" +
      "#fhempyPush .fpBtn.fpGrey{background:#888}" +
      "#fhempyPush .fpBtn[disabled]{opacity:.6;cursor:default}" +
      "#fhempyPush .fpOk{color:#3fa34d;font-weight:bold}" +
      "#fhempyPush .fpErr{color:#d64545;white-space:pre-wrap}" +
      "#fhempyPush .fpHint{font-size:12px;opacity:.75}" +
      "#fhempyPush .fpStep{margin:10px 0}" +
      "#fhempyPush .fpNum{display:inline-block;width:22px;height:22px;border-radius:50%;background:#2a6ebb;color:#fff;text-align:center;font-weight:bold;margin-right:6px}" +
      "#fhempyPush .fpOption{border:1px solid rgba(128,128,128,.35);border-radius:10px;padding:10px 12px;margin:10px 0}" +
      "#fhempyPush .fpOption table td{vertical-align:top;padding-right:14px}" +
      "#fhempyPush input.fpName{font-size:15px;padding:6px;width:14em;max-width:90%}" +
      "#fhempyPush ol{margin:4px 0;padding-left:22px}" +
      /* messages of the last 7 days */
      "#fhempyPushHistory{max-width:720px;line-height:1.4}" +
      "#fhempyPushHistory .fhHead{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:4px 0 10px}" +
      "#fhempyPushHistory .fhCount{opacity:.7;flex:1;min-width:10em}" +
      "#fhempyPushHistory .fhSearch{font-size:15px;padding:7px 12px;border-radius:18px;border:1px solid rgba(128,128,128,.45);background:transparent;color:inherit;width:13em;max-width:100%}" +
      "#fhempyPushHistory .fhDay{font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:.06em;opacity:.6;margin:16px 4px 6px}" +
      "#fhempyPushHistory .fhMsg{display:flex;gap:12px;padding:12px;margin:0 0 8px;border-radius:14px;background:rgba(128,128,128,.10);transition:background .6s}" +
      "#fhempyPushHistory .fhMsg.fhNew{background:rgba(42,110,187,.30)}" +
      "#fhempyPushHistory .fhAvatar{flex:0 0 38px;height:38px;border-radius:50%;color:#fff;font-weight:bold;font-size:17px;display:flex;align-items:center;justify-content:center}" +
      "#fhempyPushHistory .fhMain{flex:1;min-width:0}" +
      "#fhempyPushHistory .fhTop{display:flex;gap:8px;align-items:baseline}" +
      "#fhempyPushHistory .fhTitle{font-weight:bold;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
      "#fhempyPushHistory .fhTime{font-size:12px;opacity:.65;white-space:nowrap}" +
      "#fhempyPushHistory .fhBody{white-space:pre-wrap;overflow-wrap:anywhere;margin-top:2px}" +
      "#fhempyPushHistory .fhBody.fhClamp{display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;cursor:pointer}" +
      "#fhempyPushHistory .fhBody a{font-size:inherit;overflow-wrap:anywhere}" +
      "#fhempyPushHistory .fhMore{font-size:12px;opacity:.7;cursor:pointer;text-decoration:underline}" +
      "#fhempyPushHistory .fhImg{display:block;margin-top:8px;max-width:100%;max-height:220px;border-radius:10px}" +
      "#fhempyPushHistory .fhChips{margin-top:8px}" +
      "#fhempyPushHistory .fhChip{display:inline-block;font-size:13px;padding:3px 10px;margin:0 6px 4px 0;border-radius:12px;border:1px solid rgba(128,128,128,.45)}" +
      "#fhempyPushHistory .fhChip.fhUsed{border-color:#3fa34d;background:rgba(63,163,77,.15)}" +
      "#fhempyPushHistory .fhMeta{font-size:12px;opacity:.65;margin-top:6px}" +
      "#fhempyPushHistory .fhMeta .fhWarn{color:#d64545;opacity:1;font-weight:bold}" +
      "#fhempyPushHistory .fhMeta a{color:inherit}" +
      "#fhempyPushHistory .fhEmpty{text-align:center;padding:26px 10px;opacity:.85}" +
      "#fhempyPushHistory .fhBell{font-size:40px;width:76px;height:76px;line-height:76px;border-radius:50%;background:rgba(128,128,128,.12);margin:0 auto 10px}" +
      "#fhempyPushHistory .fhFoot{text-align:right;margin-top:6px}" +
      "#fhempyPushHistory .fhLink{background:none;border:0;color:inherit;opacity:.6;text-decoration:underline;cursor:pointer;font-size:12px}" +
      "</style>");
  }

  function cmd(text, callback) {
    FW_cmd(FW_root + "?cmd=" + encodeURIComponent(text) + "&XHR=1", function (resp) {
      if (callback) callback(resp || "");
    });
  }

  var ua = navigator.userAgent;
  var isIOS = /iPad|iPhone|iPod/.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var isAndroid = /Android/.test(ua);

  function standalone() {
    return window.navigator.standalone === true ||
      (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches);
  }

  /* the home screen app of the iPhone needs a web app manifest */
  function addManifest() {
    if (!$("link[rel=manifest]").length) {
      $("head").append('<link rel="manifest" href="' + FW_root + '/fhempy/push_manifest.json">');
    }
    if (!$("link[rel=apple-touch-icon]").length) {
      $("head").append('<link rel="apple-touch-icon" href="' + FW_root +
        '/images/default/fhemicon_ios.png">');
    }
    if (!$("meta[name=apple-mobile-web-app-capable]").length) {
      $("head").append('<meta name="apple-mobile-web-app-capable" content="yes">');
    }
  }

  function guessName() {
    var m = ua.match(/Android [^;)]*;\s*([^;)]+?)(?:\sBuild|[;)])/);
    if (m && m[1] && m[1] !== "K") return m[1];
    if (/iPad/.test(ua) || (isIOS && !/iPhone|iPod/.test(ua))) return "iPad";
    if (/iPhone|iPod/.test(ua)) return "iPhone";
    if (isAndroid) return /Mobile/.test(ua) ? "Android phone" : "Android tablet";
    var browser = /Edg\//.test(ua) ? "Edge" : /Firefox\//.test(ua) ? "Firefox" :
      /Chrome\//.test(ua) ? "Chrome" : /Safari\//.test(ua) ? "Safari" : "Browser";
    var os = /Windows/.test(ua) ? "Windows" : /Mac OS/.test(ua) ? "Mac" :
      /Linux/.test(ua) ? "Linux" : "";
    return (browser + " " + os).trim();
  }

  function keyBytes(key) {
    var b64 = (key + "===".slice((key.length + 3) % 4)).replace(/-/g, "+").replace(/_/g, "/");
    var raw = atob(b64);
    var out = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
    return out;
  }

  function b64url(text) {
    var bytes = new TextEncoder().encode(text);
    var bin = "";
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  function deviceId(endpoint) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(endpoint)).then(function (h) {
      return Array.prototype.map.call(new Uint8Array(h), function (b) {
        return ("0" + b.toString(16)).slice(-2);
      }).join("").slice(0, 12);
    });
  }

  function findDevice(id) {
    for (var i = 0; i < cfg.devices.length; i++) {
      if (cfg.devices[i].id === id) return cfg.devices[i];
    }
    return null;
  }

  var swUrl = function () { return FW_root + "/fhempy/push_sw.js"; };
  var swScope = function () { return FW_root + "/fhempy/"; };

  function waitActive(reg) {
    return new Promise(function (resolve) {
      var sw = reg.installing || reg.waiting || reg.active;
      if (reg.active) return resolve(reg);
      sw.addEventListener("statechange", function () {
        if (sw.state === "activated") resolve(reg);
      });
    });
  }

  function registration() {
    return navigator.serviceWorker.register(swUrl(), { scope: swScope() }).then(waitActive);
  }

  function currentSubscription() {
    return navigator.serviceWorker.getRegistration(swScope()).then(function (reg) {
      return reg ? reg.pushManager.getSubscription() : null;
    });
  }

  /* --- sections of the page --- */

  function devicesHtml(thisId) {
    if (!cfg.devices.length) return "";
    var names = cfg.devices.map(function (d) {
      return esc(d.name) + (d.id === thisId ? " <i>(this device)</i>" : "");
    }).join(", ");
    return '<div class="fpStep">Notifications go to: <b>' + names + "</b><br>" +
      '<button class="fpBtn fpGrey" id="fpTest">Send test message</button></div>' +
      '<div class="fpHint">In notify or DOIF: <code>set ' + esc(cfg.dev) +
      " message Washing machine is done</code> or <code>{fhempy_push(\"Text\")}</code></div>";
  }

  function bindTest() {
    $("#fpTest").on("click", function () {
      var b = $(this).prop("disabled", true).text("Sending...");
      cmd("set " + cfg.dev + " test", function (resp) {
        b.prop("disabled", false).text(resp ? "Send test message" : "Sent ✓");
        if (resp) FW_okDialog(esc(resp));
      });
    });
  }

  function show(html) {
    box.html(html);
    bindTest();
  }

  function caSteps(addr) {
    var ca = FW_root + "/" + addr.ca;
    var android = "<ol><li>" + '<a class="fpBtn" href="' + esc(ca) + '" download>Download certificate</a></li>' +
      "<li>Settings → Security (and privacy) → More security settings → Encryption &amp; " +
      "credentials → <b>Install a certificate</b> → <b>CA certificate</b> → choose the " +
      "downloaded file</li></ol>";
    var ios = "<ol><li>" + '<a class="fpBtn" href="' + esc(ca) + '">Download certificate</a> → Allow</li>' +
      "<li>Settings → <b>Profile downloaded</b> → Install</li>" +
      "<li>Settings → General → About → <b>Certificate Trust Settings</b> → switch on " +
      "the fhempy certificate</li></ol>";
    if (isIOS) return ios;
    if (isAndroid) return android;
    return "<b>Android:</b>" + android + "<b>iPhone/iPad:</b>" + ios;
  }

  var mobile = isIOS || isAndroid;

  function addressHtml(addr) {
    var link = '<a href="' + esc(addr.url) + '" style="font-size:1.1em">' + esc(addr.url) + "</a>";
    var steps;
    if (addr.kind === "remote") {
      steps = '<div class="fpStep"><b>From anywhere (remote access):</b><br>' +
        (mobile ? "Open this address and tap <i>Enable notifications</i> there:<br>" :
          "Scan the QR code with the phone and tap <i>Enable notifications</i> there:<br>") +
        link + "</div>";
    } else {
      var detail = '<span class="fpNum">1</span>Install the certificate of your FHEM once:' +
        caSteps(addr) +
        '<span class="fpNum">2</span>Open the https address and tap <i>Enable notifications</i> there:<br>' +
        link;
      steps = '<div class="fpStep"><b>In the home network (local https):</b><br>' +
        (mobile ? detail :
          "Scan the QR code with the phone, it shows the steps there: install the certificate " +
          "of your FHEM once, then open the https address." +
          '<details style="margin-top:6px"><summary>Show the steps here</summary>' + detail + "</details>") +
        "</div>";
    }
    return '<div class="fpOption"><table><tr><td>' + steps + "</td>" +
      (mobile ? "" : "<td>" + addr.qr + "</td>") + "</tr></table></div>";
  }

  function insecureHtml() {
    var html = "<div>Phones show notifications only for <b>https</b> pages.</div>";
    if (cfg.addresses.length) {
      cfg.addresses.forEach(function (a) { html += addressHtml(a); });
    }
    var hasRemote = cfg.addresses.some(function (a) { return a.kind === "remote"; });
    var hasLocal = cfg.addresses.some(function (a) { return a.kind === "local"; });
    if (!hasRemote) {
      html += '<div class="fpOption"><b>From anywhere (recommended):</b> ' +
        "the module remote_access gives FHEM an https address via Tailscale (free).<br>" +
        (cfg.remote_access ?
          "Finish the setup of your remote_access device, then reload this page." :
          '<button class="fpBtn" id="fpRemote">Set up remote access</button>') + "</div>";
    }
    if (!hasLocal) {
      html += '<div class="fpOption"><b>Only in the home network:</b> ' +
        "FHEM gets an own https address, each phone needs to install a certificate once.<br>" +
        '<button class="fpBtn fpGrey" id="fpLocal">Create local https address</button></div>';
    }
    return html;
  }

  function bindInsecure() {
    $("#fpRemote").on("click", function () {
      $(this).prop("disabled", true);
      cmd("define remote fhempy remote_access", function (resp) {
        if (resp) return FW_okDialog(esc(resp));
        location.href = FW_root + "?detail=remote";
      });
    });
    $("#fpLocal").on("click", function () {
      var b = $(this).prop("disabled", true).text("Creating...");
      cmd("set " + cfg.dev + " local_https " + location.hostname, function (resp) {
        if (resp) {
          b.prop("disabled", false).text("Create local https address");
          return FW_okDialog(esc(resp));
        }
        location.reload();
      });
    });
  }

  function enableHtml(error) {
    return '<div class="fpStep">Name of this device: <input class="fpName" id="fpName" value="' +
      esc(guessName()) + '"><br><button class="fpBtn" id="fpEnable">🔔 Enable notifications</button></div>' +
      (error ? '<div class="fpErr">' + esc(error) + "</div>" : "");
  }

  function enable() {
    var name = $("#fpName").val();
    $("#fpEnable").prop("disabled", true).text("Enabling...");
    var perm = Notification.requestPermission();
    Promise.resolve(perm).then(function (state) {
      if (state !== "granted") throw new Error("Notifications were not allowed.");
      return registration();
    }).then(function (reg) {
      var options = { userVisibleOnly: true, applicationServerKey: keyBytes(cfg.key) };
      return reg.pushManager.getSubscription().then(function (old) {
        /* a subscription for another key (other FHEM) has to go first */
        return old ? old.unsubscribe() : true;
      }).then(function () {
        return reg.pushManager.subscribe(options);
      });
    }).then(function (sub) {
      var data = b64url(JSON.stringify({ name: name, sub: sub.toJSON() }));
      cmd("set " + cfg.dev + " register " + data, function (resp) {
        if (resp) return render(resp);
        location.reload();
      });
    }).catch(function (err) {
      render(err && err.message ? err.message : String(err));
    });
  }

  function enabledHtml(dev) {
    return '<div class="fpStep"><span class="fpOk">✓ This device receives notifications</span> as <b>' +
      esc(dev.name) + '</b><br><button class="fpBtn fpGrey" id="fpDisable">Turn off on this device</button></div>';
  }

  function disable(dev) {
    currentSubscription().then(function (sub) {
      return sub ? sub.unsubscribe() : true;
    }).catch(function () { return true; }).then(function () {
      cmd("set " + cfg.dev + " unregister " + dev.id, function () { location.reload(); });
    });
  }

  function render(error) {
    if (!window.isSecureContext) {
      show(insecureHtml() + devicesHtml());
      bindInsecure();
      return;
    }
    if (!("serviceWorker" in navigator) || !("PushManager" in window) || !window.Notification) {
      if (isIOS && !standalone()) {
        show(devicesHtml() +
          '<div class="fpStep"><b>iPhone/iPad (iOS 16.4 or newer):</b> notifications work in the home screen app.' +
          "<ol><li>Tap <b>Share</b> (square with arrow) in Safari</li>" +
          "<li>Tap <b>Add to Home Screen</b> → Add</li>" +
          "<li>Open <b>FHEM</b> on the home screen, this page opens, tap <i>Enable notifications</i></li></ol></div>");
      } else {
        show(devicesHtml() + '<div class="fpErr">This browser can\'t receive notifications. ' +
          "Use Chrome, Firefox, Edge, Samsung Internet or the iPhone home screen app.</div>");
      }
      return;
    }
    if (Notification.permission === "denied") {
      show(devicesHtml() + '<div class="fpErr">Notifications are blocked for this page. ' +
        "Allow them in the site settings of the browser (lock icon next to the address), then reload.</div>");
      return;
    }
    currentSubscription().then(function (sub) {
      return sub ? deviceId(sub.endpoint) : null;
    }).catch(function () { return null; }).then(function (id) {
      var dev = id ? findDevice(id) : null;
      if (dev) {
        /* keeps the service worker up to date */
        registration().catch(function () {});
        show(enabledHtml(dev) + devicesHtml(id));
        $("#fpDisable").on("click", function () { disable(dev); });
      } else {
        show(enableHtml(error) + devicesHtml());
        $("#fpEnable").on("click", enable);
      }
    });
  }

  /* fallback of the notification buttons if the phone couldn't reach FHEM */
  function pendingAction() {
    var m = location.hash.match(/fhempy_push_action=([\w-]+)/);
    if (!m) return;
    history.replaceState(null, "", location.pathname + location.search);
    cmd("set " + cfg.dev + " action " + m[1], function (resp) {
      FW_okDialog(resp ? esc(resp) : "Done ✓");
    });
  }

  /* --- messages of the last 7 days --- */

  var hist = { list: [], query: "", highlight: null };

  function avatarColor(text) {
    var h = 0;
    for (var i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) % 360;
    return "hsl(" + h + ",55%,45%)";
  }

  function startOfDay(date) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
  }

  function dayLabel(date) {
    var days = Math.round((startOfDay(new Date()) - startOfDay(date)) / 86400000);
    if (days < 2 && window.Intl && Intl.RelativeTimeFormat) {
      var text = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" }).format(-days, "day");
      return text.charAt(0).toUpperCase() + text.slice(1);
    }
    return date.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
  }

  function timeText(ts) {
    return new Date(ts * 1000).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  }

  /* text with clickable web addresses */
  function linkify(text) {
    return esc(text).replace(/https?:\/\/[^\s<>"']*[^\s<>"'.,;:!?)\]]/g, function (url) {
      return '<a href="' + url + '" target="_blank" rel="noopener">' + url + "</a>";
    });
  }

  function safeUrl(url) {
    return /^https?:\/\//i.test(url || "") ? url : "";
  }

  function messageHtml(m) {
    var title = m.title || "FHEM";
    var body = m.body || "";
    var long = body.length > 220 || body.split("\n").length > 4;
    var html = '<div class="fhMsg" id="fhMsg-' + esc(m.id) + '">' +
      '<div class="fhAvatar" style="background:' + avatarColor(title) + '">' +
      esc(Array.from(title)[0].toUpperCase()) + "</div>" +
      '<div class="fhMain"><div class="fhTop"><span class="fhTitle">' + esc(title) + "</span>" +
      '<span class="fhTime" title="' + esc(new Date(m.ts * 1000).toLocaleString()) + '">' +
      esc(timeText(m.ts)) + "</span></div>";
    if (body) {
      html += '<div class="fhBody' + (long ? " fhClamp" : "") + '">' + linkify(body) + "</div>";
      if (long) html += '<span class="fhMore">Show more</span>';
    }
    var image = safeUrl(m.image);
    if (image) {
      html += '<a href="' + esc(image) + '" target="_blank" rel="noopener">' +
        '<img class="fhImg" loading="lazy" alt="" src="' + esc(image) + '"></a>';
    }
    if (m.actions && m.actions.length) {
      html += '<div class="fhChips">' + m.actions.map(function (label) {
        var used = m.used && m.used.label === label;
        return '<span class="fhChip' + (used ? " fhUsed" : "") + '">' +
          (used ? "✓ " : "") + esc(label) + (used ? " · " + esc(timeText(m.used.ts)) : "") + "</span>";
      }).join("") + "</div>";
    }
    var meta = [];
    if (m.to && m.to.length) meta.push("to " + esc(m.to.join(", ")));
    if (m.total !== undefined) {
      if (m.delivered === m.total) {
        meta.push(m.total === 1 ? "✓ delivered" : "✓ delivered to " + m.total + " devices");
      } else {
        meta.push('<span class="fhWarn">⚠ delivered to ' + m.delivered + " of " + m.total + "</span>");
      }
    }
    var url = safeUrl(m.url);
    if (url) meta.push('<a href="' + esc(url) + '" target="_blank" rel="noopener">opens a page</a>');
    if (meta.length) html += '<div class="fhMeta">' + meta.join(" · ") + "</div>";
    return html + "</div></div>";
  }

  function matches(m, query) {
    if (!query) return true;
    var text = ((m.title || "") + " " + (m.body || "") + " " + (m.actions || []).join(" ")).toLowerCase();
    return query.split(/\s+/).every(function (word) { return text.indexOf(word) >= 0; });
  }

  function historyListHtml() {
    var query = hist.query.trim().toLowerCase();
    var list = hist.list.filter(function (m) { return matches(m, query); });
    if (!hist.list.length) {
      return '<div class="fhEmpty"><div class="fhBell">🔔</div>' +
        "<b>No messages in the last 7 days</b><br>" +
        '<span class="fpHint">Every message of <code>set ' + esc(cfg.dev) +
        " message ...</code> appears here.</span></div>";
    }
    if (!list.length) {
      return '<div class="fhEmpty"><b>No message found</b><br><span class="fpHint">' +
        "Search for another word.</span></div>";
    }
    var html = "";
    var lastDay = null;
    list.slice().reverse().forEach(function (m) {
      var date = new Date(m.ts * 1000);
      var day = startOfDay(date);
      if (day !== lastDay) {
        html += '<div class="fhDay">' + esc(dayLabel(date)) + "</div>";
        lastDay = day;
      }
      html += messageHtml(m);
    });
    return html;
  }

  function renderHistoryList() {
    $("#fhList").html(historyListHtml());
    $("#fhCount").text(hist.list.length === 1 ? "1 message in the last 7 days" :
      hist.list.length + " messages in the last 7 days");
    $("#fhClear").toggle(hist.list.length > 0);
    if (hist.highlight) {
      var el = document.getElementById("fhMsg-" + hist.highlight);
      hist.highlight = null;
      if (el) {
        el.scrollIntoView({ block: "center" });
        $(el).addClass("fhNew");
        setTimeout(function () { $(el).removeClass("fhNew"); }, 2500);
      }
    }
  }

  function renderHistory() {
    var area = $("#fhempyPushHistory");
    if (!area.length) return;
    area.html('<div class="fhHead"><span class="fhCount" id="fhCount"></span>' +
      '<input type="search" class="fhSearch" id="fhSearch" placeholder="🔍 Search" ' +
      'autocomplete="off"></div><div id="fhList"></div>' +
      '<div class="fhFoot"><button class="fhLink" id="fhClear">Clear list</button></div>');
    $("#fhSearch").val(hist.query).on("input", function () {
      hist.query = $(this).val();
      renderHistoryList();
    });
    area.on("click", ".fhMore, .fhClamp", function () {
      var msg = $(this).closest(".fhMsg");
      msg.find(".fhBody").removeClass("fhClamp");
      msg.find(".fhMore").remove();
    });
    $("#fhClear").on("click", function () {
      $("<div>Delete the list of sent messages?</div>").dialog({
        modal: true, dialogClass: "no-close", width: "auto",
        buttons: [
          { text: "Delete", click: function () {
            $(this).dialog("close").remove();
            cmd("set " + cfg.dev + " clear_history", reloadHistory);
          } },
          { text: "Cancel", click: function () { $(this).dialog("close").remove(); } }
        ]
      });
    });
    renderHistoryList();
  }

  function reloadHistory() {
    cmd("set " + cfg.dev + " history", function (resp) {
      try {
        var list = JSON.parse(resp);
        if (!Array.isArray(list)) return;
        var known = {};
        hist.list.forEach(function (m) { known[m.id] = true; });
        var added = list.filter(function (m) { return !known[m.id]; });
        hist.list = list;
        renderHistoryList();
        /* new messages light up shortly */
        added.forEach(function (m) {
          var el = $(document.getElementById("fhMsg-" + m.id)).addClass("fhNew");
          setTimeout(function () { el.removeClass("fhNew"); }, 2500);
        });
      } catch (e) { /* FHEM answered with an error text */ }
    });
  }

  /* FHEMWEB updates the reading history on every change of the list */
  function watchHistory() {
    var watch = document.getElementById("fhWatch");
    if (watch) watch.setValueFn = reloadHistory;
  }

  window.fhempyPush = function (config) {
    cfg = config;
    box = $("#fhempyPush");
    hist.list = cfg.history || [];
    var m = location.hash.match(/fhempy_push_msg=([\w-]+)/);
    if (m) {
      hist.highlight = m[1];
      history.replaceState(null, "", location.pathname + location.search);
    }
    css();
    addManifest();
    render();
    renderHistory();
    watchHistory();
    pendingAction();
  };
})();
