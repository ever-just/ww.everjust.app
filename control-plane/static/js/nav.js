/* Mobile nav glue + tasteful scroll reveals. */
(function () {
  "use strict";

  // ── Bottom-sheet menu: close on link tap (navigation still proceeds).
  // We deliberately avoid data-bs-dismiss on the <a>s because Bootstrap
  // calls preventDefault() on anchor dismiss triggers, which would stop
  // the link from navigating at all.
  var sheet = document.getElementById("siteMenu");
  if (sheet && window.bootstrap && window.bootstrap.Offcanvas) {
    sheet.querySelectorAll(".sheet-list a").forEach(function (a) {
      a.addEventListener("click", function () {
        var inst = window.bootstrap.Offcanvas.getInstance(sheet);
        if (inst) inst.hide();
      });
    });
  }

  // ── Scroll reveal: gently fade/rise elements as they enter view.
  // Progressive enhancement — without JS (or with reduced motion) every
  // element is simply visible.
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;

  if (reduce || !("IntersectionObserver" in window)) {
    targets.forEach(function (el) { el.classList.add("is-revealed"); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });

  targets.forEach(function (el) { observer.observe(el); });
})();
