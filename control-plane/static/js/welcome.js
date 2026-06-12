/* Welcome page: poll provisioning status and advance the progress stepper. */
(function () {
  "use strict";

  var card = document.getElementById("welcome_card");
  if (!card) return;
  var subdomain = card.getAttribute("data-subdomain");
  var domain = card.getAttribute("data-domain");

  var loading = document.getElementById("state-loading");
  var ready = document.getElementById("state-ready");
  var timeout = document.getElementById("state-timeout");
  var steps = {
    provision: document.querySelector('[data-step="provision"]'),
    ready: document.querySelector('[data-step="ready"]'),
  };

  var attempts = 0;
  var MAX_ATTEMPTS = 60; // ~3 minutes at 3s intervals

  function markReady() {
    steps.provision.className = "done";
    steps.provision.querySelector(".marker").innerHTML = "&#10003;";
    steps.ready.className = "done";
    steps.ready.querySelector(".marker").innerHTML = "&#10003;";
    loading.hidden = true;
    ready.hidden = false;
    // Remember this workspace for the sign-in page.
    try {
      var KEY = "everjust.recentWorkspaces";
      var list = JSON.parse(localStorage.getItem(KEY) || "[]");
      list = [subdomain].concat(list.filter(function (s) { return s !== subdomain; }));
      localStorage.setItem(KEY, JSON.stringify(list.slice(0, 3)));
    } catch (e) { /* storage unavailable */ }
  }

  function markTimeout() {
    loading.hidden = true;
    timeout.hidden = false;
  }

  function poll() {
    fetch("/status/" + encodeURIComponent(subdomain))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ready) {
          markReady();
        } else if (attempts++ < MAX_ATTEMPTS) {
          setTimeout(poll, 3000);
        } else {
          markTimeout();
        }
      })
      .catch(function () {
        if (attempts++ < MAX_ATTEMPTS) setTimeout(poll, 3000);
        else markTimeout();
      });
  }

  poll();
})();
