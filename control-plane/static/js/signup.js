/* Signup wizard: step navigation, slug suggestion, live availability
 * check, password strength. The form is a single POST — steps are a
 * client-side progressive enhancement (without JS both steps render). */
(function () {
  "use strict";

  var form = document.getElementById("signup_form");
  var step1 = document.getElementById("step1");
  var step2 = document.getElementById("step2");
  var toStep2 = document.getElementById("to_step2");
  var backStep1 = document.getElementById("back_step1");
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
      if (n < step) el.querySelector(".wdot").textContent = "✓";
      else el.querySelector(".wdot").textContent = String(n);
    });
  }

  function showStep(step) {
    step1.hidden = step !== 1;
    step2.hidden = step !== 2;
    setProgress(step);
    var first = (step === 1 ? step1 : step2).querySelector("input");
    if (first) first.focus({ preventScroll: false });
  }

  function step1Valid() {
    var fields = [email, pass];
    for (var i = 0; i < fields.length; i++) {
      if (!fields[i].checkValidity()) {
        fields[i].reportValidity();
        return false;
      }
    }
    return true;
  }

  toStep2.addEventListener("click", function () {
    if (step1Valid()) showStep(2);
  });

  backStep1.addEventListener("click", function () { showStep(1); });

  // If the server re-rendered with a validation error, open the step
  // the error belongs to so the user lands on the offending field.
  var initialStep = parseInt(form.getAttribute("data-error-step") || "1", 10);
  showStep(initialStep === 2 ? 2 : 1);

  // ── Slug suggestion + availability ────────────────────

  function slug(v) {
    return (v || "").toLowerCase().trim()
      .replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
  }

  var subEdited = !!sub.value;
  sub.addEventListener("input", function () { subEdited = true; });
  org.addEventListener("input", function () {
    if (!subEdited) {
      sub.value = slug(org.value);
      checkAvailability();
    }
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

  // ── Password helpers ──────────────────────────────────

  toggle.addEventListener("click", function () {
    var showing = pass.type === "text";
    pass.type = showing ? "password" : "text";
    toggle.textContent = showing ? "Show" : "Hide";
    toggle.setAttribute("aria-pressed", String(!showing));
    pass.focus();
  });

  pass.addEventListener("input", function () {
    var v = pass.value;
    var score = 0;
    if (v.length >= 8) score++;
    if (v.length >= 12) score++;
    if (/[0-9]/.test(v) && /[a-zA-Z]/.test(v)) score++;
    if (/[^a-zA-Z0-9]/.test(v)) score++;
    strength.className = "strength s" + score;
  });

  // ── Submit ────────────────────────────────────────────

  form.addEventListener("submit", function (e) {
    sub.value = slug(sub.value);
    if (!step1Valid()) {
      e.preventDefault();
      showStep(1);
      return;
    }
    if (!form.checkValidity()) {
      e.preventDefault();
      showStep(2);
      form.reportValidity();
      return;
    }
    submitBtn.disabled = true;
    submitBtn.textContent = "Redirecting to checkout…";
  });
})();
