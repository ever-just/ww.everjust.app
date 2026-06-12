/* Sign-in page: workspace lookup + recent-workspace shortcuts (localStorage). */
(function () {
  "use strict";

  var DOMAIN = document.querySelector(".input-group .addon").textContent.replace(/^\./, "");
  var STORAGE_KEY = "everjust.recentWorkspaces";
  var form = document.getElementById("signin_form");
  var input = document.getElementById("workspace");
  var status = document.getElementById("lookup_status");
  var btn = document.getElementById("continue_btn");
  var recentList = document.getElementById("recent_list");

  function slug(v) {
    return (v || "").toLowerCase().trim()
      .replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  }

  function getRecents() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list.filter(function (s) { return typeof s === "string"; }) : [];
    } catch (e) { return []; }
  }

  function saveRecent(ws) {
    try {
      var list = getRecents().filter(function (s) { return s !== ws; });
      list.unshift(ws);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, 3)));
    } catch (e) { /* storage unavailable */ }
  }

  function go(ws) {
    saveRecent(ws);
    window.location.href = "https://" + ws + "." + DOMAIN;
  }

  function setStatus(cls, text) {
    status.className = "availability" + (cls ? " " + cls : "");
    status.textContent = text || "";
  }

  // Render recent workspaces as one-tap shortcuts.
  var recents = getRecents();
  if (recents.length) {
    recents.forEach(function (ws) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "recent-item";
      var label = document.createElement("span");
      var bold = document.createElement("b");
      bold.textContent = ws;
      var suffix = document.createElement("span");
      suffix.className = "suffix";
      suffix.textContent = "." + DOMAIN;
      label.appendChild(bold);
      label.appendChild(suffix);
      var arrow = document.createElement("span");
      arrow.className = "arrow";
      arrow.textContent = "→";
      b.appendChild(label);
      b.appendChild(arrow);
      b.addEventListener("click", function () { go(ws); });
      recentList.appendChild(b);
    });
    recentList.hidden = false;
    if (!input.value) input.value = "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var ws = slug(input.value);
    if (!ws) {
      input.setAttribute("aria-invalid", "true");
      setStatus("bad", "Enter your workspace address to continue.");
      input.focus();
      return;
    }
    input.removeAttribute("aria-invalid");
    btn.disabled = true;
    setStatus("checking", "Finding your workspace…");

    // Verify the workspace exists so users get a friendly message here
    // instead of a browser error on a dead subdomain.
    fetch("/api/subdomain-check?subdomain=" + encodeURIComponent(ws))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.valid && !d.available) {
          // Taken == an existing workspace — exactly what we want here.
          setStatus("ok", "Taking you to " + ws + "." + DOMAIN + "…");
          go(ws);
        } else {
          btn.disabled = false;
          input.setAttribute("aria-invalid", "true");
          setStatus("bad", "We couldn’t find a workspace named “" + ws + "”. Check the spelling, or create one below.");
        }
      })
      .catch(function () {
        // If the check itself fails, fall back to navigating directly.
        go(ws);
      });
  });
})();
