/* App catalog: live search + category filtering. Pure DOM, no deps. */
(function () {
  "use strict";

  var search = document.getElementById("app_search");
  var filters = document.getElementById("catalog_filters");
  var empty = document.getElementById("catalog_empty");
  var groups = Array.prototype.slice.call(document.querySelectorAll(".catalog-group"));
  var items = Array.prototype.slice.call(document.querySelectorAll(".catalog-item"));
  if (!search || !groups.length) return;

  var activeCat = "all";

  function apply() {
    var q = search.value.trim().toLowerCase();
    var anyVisible = false;

    items.forEach(function (item) {
      var group = item.closest(".catalog-group");
      var catOk = activeCat === "all" || group.getAttribute("data-cat") === activeCat;
      var hay = item.getAttribute("data-name") + " " + item.getAttribute("data-replaces");
      var qOk = !q || q.split(/\s+/).every(function (w) { return hay.indexOf(w) !== -1; });
      var show = catOk && qOk;
      item.hidden = !show;
      if (show) anyVisible = true;
    });

    // Hide a category heading when it has no visible items.
    groups.forEach(function (group) {
      var visible = group.querySelectorAll(".catalog-item:not([hidden])").length;
      group.hidden = visible === 0;
    });

    if (empty) {
      empty.hidden = anyVisible;
      if (!anyVisible) empty.querySelector("span").textContent = search.value.trim();
    }
  }

  search.addEventListener("input", apply);

  // Deep link: /apps#sales pre-selects that category filter.
  function activate(cat) {
    var btn = filters.querySelector('.chip[data-cat="' + cat + '"]');
    if (!btn) return;
    activeCat = cat;
    filters.querySelectorAll(".chip").forEach(function (c) {
      c.classList.toggle("is-active", c === btn);
    });
    apply();
  }
  if (location.hash) {
    var h = location.hash.slice(1);
    if (filters.querySelector('.chip[data-cat="' + h + '"]')) activate(h);
  }

  filters.addEventListener("click", function (e) {
    var btn = e.target.closest(".chip");
    if (!btn) return;
    activeCat = btn.getAttribute("data-cat");
    filters.querySelectorAll(".chip").forEach(function (c) {
      c.classList.toggle("is-active", c === btn);
    });
    apply();
  });
})();
