/* Docs enhancements: heading anchors, on-page TOC, and client-side search
 * over /docs/search-index.json. */
(function () {
  "use strict";

  var article = document.getElementById("docs_article");
  var toc = document.getElementById("docs_toc");

  function slugify(text) {
    return text.toLowerCase().trim()
      .replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-").slice(0, 60);
  }

  // ── Heading anchors + TOC ─────────────────────────────
  if (article) {
    var headings = article.querySelectorAll("h2");
    var items = [];
    headings.forEach(function (h) {
      if (!h.id) h.id = slugify(h.textContent) || "section-" + items.length;
      var a = document.createElement("a");
      a.className = "docs-anchor";
      a.href = "#" + h.id;
      a.setAttribute("aria-label", "Link to this section");
      a.textContent = "#";
      h.appendChild(a);
      items.push({ id: h.id, text: h.textContent.replace(/#$/, "").trim() });
    });

    if (toc && items.length > 1) {
      var ul = toc.querySelector("ul");
      items.forEach(function (it) {
        var li = document.createElement("li");
        var link = document.createElement("a");
        link.href = "#" + it.id;
        link.textContent = it.text;
        li.appendChild(link);
        ul.appendChild(li);
      });
      toc.hidden = false;

      // Highlight the section currently in view.
      if ("IntersectionObserver" in window) {
        var links = ul.querySelectorAll("a");
        var byId = {};
        links.forEach(function (l) { byId[l.getAttribute("href").slice(1)] = l; });
        var observer = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) {
              links.forEach(function (l) { l.classList.remove("active"); });
              var l = byId[e.target.id];
              if (l) l.classList.add("active");
            }
          });
        }, { rootMargin: "-80px 0px -70% 0px" });
        headings.forEach(function (h) { observer.observe(h); });
      }
    }
  }

  // ── Search ────────────────────────────────────────────
  var input = document.getElementById("docs_search");
  var results = document.getElementById("docs_search_results");
  if (!input || !results) return;

  var index = null;

  function load() {
    if (index) return Promise.resolve(index);
    return fetch("/docs/search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { index = d.items || []; return index; })
      .catch(function () { return []; });
  }

  function renderResults(matches, q) {
    results.textContent = "";
    if (!q) { results.hidden = true; return; }
    if (!matches.length) {
      var none = document.createElement("p");
      none.className = "docs-search-empty";
      none.textContent = "No results for “" + q + "”";
      results.appendChild(none);
      results.hidden = false;
      return;
    }
    matches.slice(0, 8).forEach(function (m) {
      var a = document.createElement("a");
      a.href = "/docs/" + m.slug;
      var t = document.createElement("b");
      t.textContent = m.title;
      var s = document.createElement("span");
      s.textContent = m.section + " — " + m.blurb;
      a.appendChild(t);
      a.appendChild(s);
      results.appendChild(a);
    });
    results.hidden = false;
  }

  var timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    var q = input.value.trim().toLowerCase();
    timer = setTimeout(function () {
      if (!q) { renderResults([], ""); return; }
      load().then(function (items) {
        var matches = items.filter(function (it) {
          var hay = (it.title + " " + it.blurb + " " + it.section + " " +
                     (it.headings || []).join(" ")).toLowerCase();
          return q.split(/\s+/).every(function (w) { return hay.indexOf(w) !== -1; });
        });
        renderResults(matches, input.value.trim());
      });
    }, 150);
  });

  document.addEventListener("click", function (e) {
    if (!results.contains(e.target) && e.target !== input) results.hidden = true;
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { results.hidden = true; input.blur(); }
  });
})();
