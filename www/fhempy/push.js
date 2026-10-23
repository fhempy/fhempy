/*
 * Push notifications for FHEMWEB, used on the detail page of the fhempy
 * module push. fhempyPush(cfg) shows the next step for this browser:
 * open the https address, add to home screen (iPhone), enable notifications.
 * cfg: {dev, key, devices: [{id, name}], addresses: [{url, kind, qr, ca}],
 *       remote_access}
 */
(function () {
  "use strict";

  var cfg;
  var box;

  function esc(t) { return $("<div>").text(t === undefined ? "" : String(t)).html(); }

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

  window.fhempyPush = function (config) {
    cfg = config;
    box = $("#fhempyPush");
    css();
    addManifest();
    render();
    pendingAction();
  };
})();
