/** HeadsUp frontend: scroll-reveal animations. */
document.addEventListener("DOMContentLoaded", function () {
    var els = document.querySelectorAll(".x_reveal");
    if (!els.length) return;

    if ("IntersectionObserver" in window) {
        var obs = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) {
                        e.target.classList.add("x_visible");
                        obs.unobserve(e.target);
                    }
                });
            },
            { threshold: 0.15 }
        );
        els.forEach(function (el) { obs.observe(el); });
    } else {
        // Fallback: show everything immediately
        els.forEach(function (el) { el.classList.add("x_visible"); });
    }
});
