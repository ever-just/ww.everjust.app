/** TCSW Premium Theme — Frontend enhancements */
(function () {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') fn();
        else document.addEventListener('DOMContentLoaded', fn);
    }

    ready(function () {
        // Scroll-reveal via IntersectionObserver
        const revealEls = document.querySelectorAll('.tcsw-reveal');
        if (revealEls.length && 'IntersectionObserver' in window) {
            const obs = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) {
                        e.target.classList.add('tcsw-visible');
                        obs.unobserve(e.target);
                    }
                });
            }, { threshold: 0.12 });
            revealEls.forEach(function (el) { obs.observe(el); });
        } else {
            revealEls.forEach(function (el) { el.classList.add('tcsw-visible'); });
        }

        // Sticky register CTA — show after scrolling past first viewport
        var cta = document.querySelector('.tcsw-sticky-cta');
        if (cta) {
            var shown = false;
            window.addEventListener('scroll', function () {
                var past = window.scrollY > window.innerHeight * 0.6;
                if (past !== shown) {
                    cta.style.display = past ? '' : 'none';
                    shown = past;
                }
            }, { passive: true });
            cta.style.display = 'none';
        }

        // Transparent-to-solid navbar
        var header = document.querySelector('#wrapwrap > header');
        if (header) {
            function updateNav() {
                if (window.scrollY > 40) {
                    header.classList.add('o_top_fixed_element');
                } else {
                    header.classList.remove('o_top_fixed_element');
                }
            }
            window.addEventListener('scroll', updateNav, { passive: true });
            updateNav();
        }
    });
})();
