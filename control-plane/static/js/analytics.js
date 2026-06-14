/* Privacy-first, cookieless analytics shim.
 *
 * Keeps the site's promise of "no tracking or advertising cookies": this sets
 * no cookies and no persistent identifiers, and honours Do Not Track. It is a
 * thin wrapper over a Plausible-compatible `window.plausible` queue, which is
 * only present when an analytics domain is configured server-side. When no
 * provider is configured, every call here is a silent no-op.
 *
 * Usage:
 *   window.ejTrack("signup_submitted", { plan: "flat" });
 * Declarative:
 *   <button data-track="signup_cta">…</button>         // fires on click
 *   <div data-track-view="signup_completed"></div>     // fires on page load
 */
(function () {
  "use strict";

  var DNT = navigator.doNotTrack === "1" ||
            window.doNotTrack === "1" ||
            navigator.msDoNotTrack === "1";

  window.ejTrack = function (name, props) {
    if (DNT || !name) return;
    try {
      if (typeof window.plausible === "function") {
        window.plausible(name, props ? { props: props } : undefined);
      }
    } catch (e) { /* analytics must never break the page */ }
  };

  // Delegated click tracking for [data-track].
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest && ev.target.closest("[data-track]");
    if (!el) return;
    window.ejTrack(el.getAttribute("data-track"),
                   { from: el.getAttribute("data-track-from") || location.pathname });
  }, true);

  // Fire view events for [data-track-view] once the DOM is ready.
  function fireViews() {
    var els = document.querySelectorAll("[data-track-view]");
    for (var i = 0; i < els.length; i++) {
      window.ejTrack(els[i].getAttribute("data-track-view"), { path: location.pathname });
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fireViews);
  } else {
    fireViews();
  }
})();
