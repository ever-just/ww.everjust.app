/* "Cut your software bill" calculator. Pure client-side; no deps.
 * Current stack cost (per-user + flat tools x team size) vs the flat
 * EVERJUST plan ($100 incl. 5 users, +$15/user after). */
(function () {
  "use strict";

  var tools = Array.prototype.slice.call(document.querySelectorAll(".calc-tool"));
  var usersInput = document.getElementById("calc_users");
  if (!tools.length || !usersInput) return;

  var elCurrent = document.getElementById("calc_current");
  var elOurs = document.getElementById("calc_ours");
  var elSavings = document.getElementById("calc_savings");

  function money(n) { return "$" + Math.round(n).toLocaleString(); }
  function ours(users) { return 100 + Math.max(0, users - 5) * 15; }

  function recompute() {
    var users = parseInt(usersInput.value, 10);
    if (isNaN(users)) users = 1;
    users = Math.max(1, Math.min(500, users));

    var current = 0;
    tools.forEach(function (t) {
      if (!t.classList.contains("is-active")) return;
      var price = parseFloat(t.getAttribute("data-price")) || 0;
      current += t.getAttribute("data-type") === "user" ? price * users : price;
    });

    var o = ours(users);
    elCurrent.textContent = money(current) + "/mo";
    elOurs.textContent = money(o) + "/mo";
    var saveYear = Math.max(0, current - o) * 12;
    elSavings.innerHTML = money(saveYear) + "<small>/year</small>";
  }

  tools.forEach(function (t) {
    t.addEventListener("click", function () {
      var on = t.classList.toggle("is-active");
      t.setAttribute("aria-pressed", String(on));
      recompute();
    });
  });
  usersInput.addEventListener("input", recompute);
  recompute();
})();
