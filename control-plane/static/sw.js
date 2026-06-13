/* EVERJUST.APP service worker — precache the shell, stale-while-revalidate
 * for static assets (so deploys propagate without users pinning old CSS/JS),
 * network-first for pages with an offline fallback. */
"use strict";

const CACHE = "everjust-v5";
const OFFLINE_URL = "/offline";

const PRECACHE = [
  OFFLINE_URL,
  "/static/vendor/bootstrap/bootstrap.min.css",
  "/static/vendor/bootstrap/bootstrap.bundle.min.js",
  "/static/vendor/cookieconsent/cookieconsent.css",
  "/static/vendor/cookieconsent/cookieconsent.umd.js",
  "/static/css/site.css",
  "/static/js/consent.js",
  "/static/js/docs.js",
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

  // Static assets: stale-while-revalidate. Serve from cache for speed but
  // always refresh in the background so a deploy can't strand stale CSS/JS
  // on installed PWAs. Versioned URLs (?v=) make updates immediate.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.open(CACHE).then((cache) =>
        cache.match(req).then((hit) => {
          const refresh = fetch(req)
            .then((res) => {
              if (res && res.ok) cache.put(req, res.clone());
              return res;
            })
            .catch(() => hit);
          return hit || refresh;
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
