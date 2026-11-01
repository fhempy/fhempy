// Starts the dashboard also while fhempy restarts: the app shell comes from
// the cache when the network fails, live values always come over the WebSocket.
var CACHE = "dashboard-v1";
var SHELL = ["./", "app.js", "app.css", "manifest.webmanifest", "icon.svg", "icon-192.png"];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) { return cache.addAll(SHELL); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }));
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  var url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.indexOf("/api/") === 0) {
    return;
  }
  event.respondWith(fetch(event.request).then(function (response) {
    var copy = response.clone();
    caches.open(CACHE).then(function (cache) { cache.put(event.request, copy); });
    return response;
  }).catch(function () {
    return caches.match(event.request, { ignoreSearch: true }).then(function (hit) {
      return hit || caches.match("./");
    });
  }));
});
