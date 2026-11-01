// Starts the dashboard also while fhempy restarts: the app shell comes from
// the cache when the network fails, live values always come over the WebSocket.
var CACHE = "dashboard-v2";
var SHELL = ["./", "app.js", "app.css", "manifest.webmanifest", "icon.svg", "icon-192.png"];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

async function networkFirst(request) {
  try {
    var response = await fetch(request);
    var cache = await caches.open(CACHE);
    if (response.ok) { await cache.put(request, response.clone()); }
    return response;
  } catch {
    var hit = await caches.match(request, { ignoreSearch: true });
    return hit || caches.match("./");
  }
}

self.addEventListener("fetch", function (event) {
  var url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) {
    return;
  }
  event.respondWith(networkFirst(event.request));
});
