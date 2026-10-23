/*
 * Service worker of the fhempy module push: shows the notifications and runs
 * the buttons of a notification. Data of a message (JSON):
 * {title, body, image, url, tag, dev, actions: [{action: token, title}]}
 */
"use strict";

/* scope is <FW_root>/fhempy/, FHEM itself is one level up */
function fhemRoot() {
  return new URL("..", self.registration.scope).href.replace(/\/$/, "");
}

self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("push", function (event) {
  var msg = {};
  try {
    msg = event.data ? event.data.json() : {};
  } catch (e) {
    msg = { body: event.data ? event.data.text() : "" };
  }
  var options = {
    body: msg.body || "",
    icon: fhemRoot() + "/images/default/fhemicon_ios.png",
    tag: msg.tag,
    data: { url: msg.url || "", dev: msg.dev || "" },
    timestamp: Date.now()
  };
  if (msg.image) options.image = msg.image;
  if (msg.actions && msg.actions.length) options.actions = msg.actions;
  event.waitUntil(self.registration.showNotification(msg.title || "FHEM", options));
});

/* a tap on the message: back to an open FHEM window or open a new one */
function openPage(url) {
  return self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    if (url === fhemRoot()) {
      for (var i = 0; i < list.length; i++) {
        if (list[i].url.indexOf(fhemRoot()) === 0 && "focus" in list[i]) return list[i].focus();
      }
    }
    return self.clients.openWindow(url);
  });
}

/* runs "set <dev> action <token>" in FHEM, FHEMWEB needs its csrf token */
function runAction(dev, token) {
  var root = fhemRoot();
  var opts = { credentials: "include", cache: "no-store" };
  return fetch(root + "/fhempy/push_manifest.json", opts).then(function (resp) {
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    var csrf = resp.headers.get("X-FHEM-csrfToken") || "";
    var cmd = "set " + dev + " action " + token;
    return fetch(root + "?cmd=" + encodeURIComponent(cmd) + "&XHR=1&fwcsrf=" +
      encodeURIComponent(csrf), { method: "POST", credentials: "include", cache: "no-store" });
  }).then(function (resp) {
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    return resp.text();
  }).then(function (text) {
    /* an answer of FHEM is an error message, e.g. button already used */
    if (text.trim()) {
      return self.registration.showNotification("FHEM", { body: text.trim().slice(0, 300) });
    }
    return null;
  }).catch(function () {
    /* e.g. password of FHEMWEB needed: FHEM opens and runs it there */
    return self.clients.openWindow(root + "?detail=" + encodeURIComponent(dev) +
      "#fhempy_push_action=" + token);
  });
}

self.addEventListener("notificationclick", function (event) {
  var note = event.notification;
  var data = note.data || {};
  note.close();
  if (event.action) {
    event.waitUntil(runAction(data.dev, event.action));
    return;
  }
  event.waitUntil(openPage(data.url || fhemRoot()));
});
