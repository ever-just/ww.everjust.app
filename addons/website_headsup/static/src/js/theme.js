/** HeadsUp frontend: scroll-reveal + sticky CTA */
document.addEventListener("DOMContentLoaded", function () {
    // ── Scroll reveal ───────────────────────────────────────
    var els = document.querySelectorAll(".hu-reveal");
    if (els.length && "IntersectionObserver" in window) {
        var obs = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (e.isIntersecting) { e.target.classList.add("hu-visible"); obs.unobserve(e.target); }
            });
        }, { threshold: 0.12 });
        els.forEach(function (el) { obs.observe(el); });
    } else {
        els.forEach(function (el) { el.classList.add("hu-visible"); });
    }

    // ── Sticky CTA ──────────────────────────────────────────
    var cta = document.querySelector(".hu-sticky-cta");
    if (cta) {
        var shown = false;
        var threshold = window.innerHeight * 0.6;
        window.addEventListener("scroll", function () {
            var y = window.scrollY || window.pageYOffset;
            if (!shown && y > threshold) { cta.classList.add("hu-visible"); shown = true; }
        }, { passive: true });
    }
});
