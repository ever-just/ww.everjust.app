/* Signup page: slug suggestion, live availability check, password strength. */
(function () {
  "use strict";

  var org = document.getElementById("org_name");
  var sub = document.getElementById("subdomain");
  var availability = document.getElementById("availability");
  var pass = document.getElementById("password");
  var toggle = document.getElementById("toggle_pass");
  var strength = document.getElementById("strength");
  var form = document.getElementById("signup_form");
  var submitBtn = document.getElementById("submit_btn");

  function slug(v) {
    return (v || "").toLowerCase().trim()
      .replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  }

  // Suggest a workspace address from the org name until the user edits it.
  var subEdited = !!sub.value;
  sub.addEventListener("input", function () { subEdited = true; });
  org.addEventListener("input", function () {
    if (!subEdited) {
      sub.value = slug(org.value);
      checkAvailability();
    }
  });

  // Debounced availability check against /api/subdomain-check.
  var timer = null;
  var lastChecked = "";

  function setStatus(cls, text) {
    availability.className = "availability" + (cls ? " " + cls : "");
    availability.textContent = text || "";
  }

  function checkAvailability() {
    clearTimeout(timer);
    var v = slug(sub.value);
    if (!v) { setStatus("", ""); return; }
    setStatus("checking", "Checking availability…");
    timer = setTimeout(function () {
      lastChecked = v;
      fetch("/api/subdomain-check?subdomain=" + encodeURIComponent(v))
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (slug(sub.value) !== lastChecked) return; // stale response
          if (!d.valid) {
            sub.setAttribute("aria-invalid", "true");
            setStatus("bad", d.reason || "That address can’t be used.");
          } else if (!d.available) {
            sub.setAttribute("aria-invalid", "true");
            setStatus("bad", v + "." + d.domain + " is already taken.");
          } else {
            sub.removeAttribute("aria-invalid");
            setStatus("ok", v + "." + d.domain + " is available ✓");
          }
        })
        .catch(function () { setStatus("", ""); });
    }, 350);
  }

  sub.addEventListener("input", checkAvailability);
  if (sub.value) checkAvailability();

  // Show/hide password.
  toggle.addEventListener("click", function () {
    var showing = pass.type === "text";
    pass.type = showing ? "password" : "text";
    toggle.textContent = showing ? "Show" : "Hide";
    toggle.setAttribute("aria-pressed", String(!showing));
    pass.focus();
  });

  // Lightweight strength meter (length + character variety).
  pass.addEventListener("input", function () {
    var v = pass.value;
    var score = 0;
    if (v.length >= 8) score++;
    if (v.length >= 12) score++;
    if (/[0-9]/.test(v) && /[a-zA-Z]/.test(v)) score++;
    if (/[^a-zA-Z0-9]/.test(v)) score++;
    strength.className = "strength s" + score;
  });

  // Normalize the slug on submit so what was previewed is what gets sent,
  // and guard against double submission.
  form.addEventListener("submit", function (e) {
    sub.value = slug(sub.value);
    if (!form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = "Redirecting to checkout…";
  });
})();
