/* EVERJUST.APP service worker — precache the shell, cache-first for static
 * assets, network-first for pages with an offline fallback. */
"use strict";

const CACHE = "everjust-v1";
const OFFLINE_URL = "/offline";

const PRECACHE = [
  OFFLINE_URL,
  "/static/css/site.css",
  "/static/js/pwa.js",
  "/static/img/icon-192x192.png",
  "/static/img/icon-512x512.png",
  "/static/img/apple-touch-icon.png",
  "/static/img/favicon.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Never cache dynamic/billing endpoints.
  if (url.pathname.startsWith("/api/") ||
      url.pathname.startsWith("/status/") ||
      url.pathname.startsWith("/stripe/")) {
    return;
  }

  // Static assets: cache-first.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(req).then(
        (hit) => hit ||
          fetch(req).then((res) => {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
            return res;
          })
      )
    );
    return;
  }

  // Pages: network-first with offline fallback.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() =>
        caches.match(req).then((hit) => hit || caches.match(OFFLINE_URL))
      )
    );
  }
});
