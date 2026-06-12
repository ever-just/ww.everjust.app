/* Register the EVERJUST.APP service worker (PWA install + offline support). */
(function () {
  "use strict";
  if (!("serviceWorker" in navigator)) return;
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () {
      /* Service worker is progressive enhancement only. */
    });
  });
})();
