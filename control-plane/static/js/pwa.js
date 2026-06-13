/* Register the EVERJUST.APP service worker (PWA install + offline support),
 * and auto-reload once when a new version takes over so a deploy always
 * shows fresh content on the next visit (no manual cache clearing). */
(function () {
  "use strict";
  if (!("serviceWorker" in navigator)) return;

  // When a new SW activates and claims the page, reload once to pick up the
  // fresh assets. Guarded against reload loops.
  var refreshing = false;
  navigator.serviceWorker.addEventListener("controllerchange", function () {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () {
      /* Service worker is progressive enhancement only. */
    });
  });
})();
