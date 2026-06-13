/* Signup wizard: 3-step navigation, slug suggestion, live availability
 * check, password strength, and the optional "about your business" step.
 * The form is a single POST — steps are progressive enhancement (without
 * JS every step renders stacked and still submits). */
(function () {
  "use strict";

  var form = document.getElementById("signup_form");
  var steps = {
    1: document.getElementById("step1"),
    2: document.getElementById("step2"),
    3: document.getElementById("step3"),
  };
  var progress = document.getElementById("wizard_progress");

  var email = document.getElementById("email");
  var pass = document.getElementById("password");
  var toggle = document.getElementById("toggle_pass");
  var strength = document.getElementById("strength");

  var org = document.getElementById("org_name");
  var sub = document.getElementById("subdomain");
  var availability = document.getElementById("availability");
  var submitBtn = document.getElementById("submit_btn");

  // ── Wizard navigation ─────────────────────────────────

  function setProgress(step) {
    progress.querySelectorAll(".wstep[data-wstep]").forEach(function (el) {
      var n = parseInt(el.getAttribute("data-wstep"), 10);
      el.classList.toggle("done", n < step);
      el.classList.toggle("active", n === step);
      el.querySelector(".wdot").textContent = n < step ? "✓" : String(n);
    });
  }

  function showStep(step) {
    for (var n = 1; n <= 3; n++) steps[n].hidden = n !== step;
    setProgress(step);
    var first = steps[step].querySelector("input, select");
    if (first) first.focus({ preventScroll: false });
  }

  function step1Valid() {
    return [email, pass].every(function (f) {
      if (f.checkValidity()) return true;
      f.reportValidity();
      return false;
    });
  }

  function step2Valid() {
    return [org, sub].every(function (f) {
      if (f.checkValidity()) return true;
      f.reportValidity();
      return false;
    });
  }

  document.getElementById("to_step2").addEventListener("click", function () {
    if (step1Valid()) showStep(2);
  });
  document.getElementById("to_step3").addEventListener("click", function () {
    sub.value = slug(sub.value);
    if (step2Valid()) showStep(3);
  });
  document.getElementById("back_step1").addEventListener("click", function () { showStep(1); });
  document.getElementById("back_step2").addEventListener("click", function () { showStep(2); });

  // ── Slug suggestion + availability ────────────────────

  function slug(v) {
    return (v || "").toLowerCase().trim()
      .replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  }

  var subEdited = !!sub.value;
  sub.addEventListener("input", function () { subEdited = true; });
  org.addEventListener("input", function () {
    if (!subEdited) { sub.value = slug(org.value); checkAvailability(); }
  });

  var timer = null;
  var lastChecked = "";

  function setStatus(cls, text) {
    availability.className = "availability mb-0" + (cls ? " " + cls : "");
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
          if (slug(sub.value) !== lastChecked) return;
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

  // ── Password helpers ──────────────────────────────────

  toggle.addEventListener("click", function () {
    var showing = pass.type === "text";
    pass.type = showing ? "password" : "text";
    toggle.textContent = showing ? "Show" : "Hide";
    toggle.setAttribute("aria-pressed", String(!showing));
    pass.focus();
  });

  pass.addEventListener("input", function () {
    var v = pass.value, score = 0;
    if (v.length >= 8) score++;
    if (v.length >= 12) score++;
    if (/[0-9]/.test(v) && /[a-zA-Z]/.test(v)) score++;
    if (/[^a-zA-Z0-9]/.test(v)) score++;
    strength.className = "strength s" + score;
  });

  // ── Goal chips (multi-select → hidden comma-joined input) ──

  var goalsInput = document.getElementById("goals");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".goal-chip"));
  function syncGoals() {
    goalsInput.value = chips
      .filter(function (c) { return c.classList.contains("is-active"); })
      .map(function (c) { return c.getAttribute("data-goal"); })
      .join(", ");
  }
  chips.forEach(function (c) {
    c.setAttribute("aria-pressed", "false");
    c.addEventListener("click", function () {
      var on = c.classList.toggle("is-active");
      c.setAttribute("aria-pressed", String(on));
      syncGoals();
    });
  });

  // ── Submit ────────────────────────────────────────────

  form.addEventListener("submit", function (e) {
    sub.value = slug(sub.value);
    if (!step1Valid()) { e.preventDefault(); showStep(1); return; }
    if (!step2Valid()) { e.preventDefault(); showStep(2); return; }
    if (!form.checkValidity()) {
      e.preventDefault();
      showStep(3);
      form.reportValidity();
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = "Redirecting to checkout…";
  });

  // Open the step the server flagged (errors are step 1 or 2).
  var initialStep = parseInt(form.getAttribute("data-error-step") || "1", 10);
  showStep(initialStep === 2 ? 2 : 1);
})();
