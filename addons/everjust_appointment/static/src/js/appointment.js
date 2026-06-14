/** @odoo-module **/

/**
 * EverJust Appointments — Public Booking Page
 *
 * Vanilla JS. No jQuery dependency.
 * Handles: calendar navigation, date selection, slot fetching via AJAX,
 * time selection, and form validation.
 */

(function () {
    "use strict";

    // ── Helpers ──────────────────────────────────────────────────────

    var MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ];

    function pad(n) {
        return n < 10 ? "0" + n : "" + n;
    }

    function dateStr(d) {
        return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
    }

    function formatDisplay(d) {
        var day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        return day[d.getDay()] + ", " + MONTHS[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
    }

    // ── State ────────────────────────────────────────────────────────

    var calendarEl = document.querySelector(".ej-calendar");
    if (!calendarEl) return; // Not on a booking page

    var typeId = calendarEl.dataset.typeId;
    var availableWeekdays = JSON.parse(calendarEl.dataset.availableWeekdays || "[]");
    var minDate = new Date(calendarEl.dataset.minDate + "T00:00:00");
    var maxDate = new Date(calendarEl.dataset.maxDate + "T00:00:00");
    var today = new Date();
    today.setHours(0, 0, 0, 0);

    var currentMonth = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
    var selectedDate = null;
    var selectedSlot = null;

    // ── DOM refs ─────────────────────────────────────────────────────

    var monthLabel = calendarEl.querySelector(".ej-calendar-month-label");
    var daysContainer = calendarEl.querySelector(".ej-calendar-days");
    var prevBtn = calendarEl.querySelector(".ej-calendar-prev");
    var nextBtn = calendarEl.querySelector(".ej-calendar-next");

    var stepDate = document.getElementById("step-date");
    var stepTime = document.getElementById("step-time");
    var stepForm = document.getElementById("step-form");

    var slotsGrid = document.querySelector(".ej-slots-grid");
    var slotsEmpty = document.querySelector(".ej-slots-empty");
    var slotsLoading = document.querySelector(".ej-slots-loading");
    var selectedDateLabel = document.querySelector(".ej-selected-date-label");
    var selectedSummary = document.querySelector(".ej-selected-summary");

    var slotDatetimeInput = document.getElementById("slot_datetime");
    var bookingForm = document.getElementById("booking-form");
    var submitBtn = document.getElementById("btn-submit");

    var steps = document.querySelectorAll(".ej-appt-step");

    // ── Step management ──────────────────────────────────────────────

    function setStep(n) {
        // n is 1, 2, or 3
        stepDate.style.display = n === 1 ? "" : "none";
        stepTime.style.display = n === 2 ? "" : "none";
        stepForm.style.display = n === 3 ? "" : "none";

        for (var i = 0; i < steps.length; i++) {
            var s = steps[i];
            var stepNum = parseInt(s.dataset.step, 10);
            s.classList.remove("active", "completed");
            if (stepNum === n) {
                s.classList.add("active");
            } else if (stepNum < n) {
                s.classList.add("completed");
            }
        }
    }

    // ── Calendar rendering ───────────────────────────────────────────

    function renderCalendar() {
        var year = currentMonth.getFullYear();
        var month = currentMonth.getMonth();
        monthLabel.textContent = MONTHS[month] + " " + year;

        daysContainer.innerHTML = "";

        // First day of month (0=Sun, convert to Mon=0)
        var firstDay = new Date(year, month, 1).getDay();
        firstDay = (firstDay + 6) % 7; // Mon=0

        var daysInMonth = new Date(year, month + 1, 0).getDate();

        // Empty cells
        for (var e = 0; e < firstDay; e++) {
            var empty = document.createElement("span");
            empty.className = "ej-calendar-day empty";
            daysContainer.appendChild(empty);
        }

        for (var d = 1; d <= daysInMonth; d++) {
            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "ej-calendar-day";
            btn.textContent = d;

            var cellDate = new Date(year, month, d);
            cellDate.setHours(0, 0, 0, 0);
            var cellWeekday = (cellDate.getDay() + 6) % 7; // Mon=0

            var isAvailableDay = availableWeekdays.indexOf(cellWeekday) !== -1;
            var isInRange = cellDate >= minDate && cellDate <= maxDate;

            if (cellDate.getTime() === today.getTime()) {
                btn.classList.add("today");
            }

            if (isAvailableDay && isInRange) {
                btn.classList.add("available");
                btn.dataset.date = dateStr(cellDate);
                btn.addEventListener("click", onDateClick);
            } else {
                btn.classList.add("disabled");
            }

            if (selectedDate && cellDate.getTime() === selectedDate.getTime()) {
                btn.classList.add("selected");
            }

            daysContainer.appendChild(btn);
        }
    }

    // ── Calendar navigation ──────────────────────────────────────────

    prevBtn.addEventListener("click", function () {
        currentMonth.setMonth(currentMonth.getMonth() - 1);
        renderCalendar();
    });

    nextBtn.addEventListener("click", function () {
        currentMonth.setMonth(currentMonth.getMonth() + 1);
        renderCalendar();
    });

    // ── Date click ───────────────────────────────────────────────────

    function onDateClick(e) {
        var ds = e.currentTarget.dataset.date;
        selectedDate = new Date(ds + "T00:00:00");
        selectedSlot = null;
        renderCalendar();
        fetchSlots(ds);
        setStep(2);
    }

    // ── Fetch available slots ────────────────────────────────────────

    function fetchSlots(ds) {
        slotsGrid.innerHTML = "";
        slotsEmpty.style.display = "none";
        slotsLoading.style.display = "";
        selectedDateLabel.textContent = formatDisplay(new Date(ds + "T00:00:00"));

        var formData = new FormData();
        formData.append("date", ds);

        fetch("/appointment/" + typeId + "/slots", {
            method: "POST",
            body: formData,
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                slotsLoading.style.display = "none";
                var slots = data.slots || [];
                if (slots.length === 0) {
                    slotsEmpty.style.display = "";
                    return;
                }
                slots.forEach(function (slot) {
                    var btn = document.createElement("button");
                    btn.type = "button";
                    btn.className = "ej-slot-btn";
                    btn.textContent = slot.display;
                    btn.dataset.datetime = slot.datetime;
                    btn.addEventListener("click", onSlotClick);
                    slotsGrid.appendChild(btn);
                });
            })
            .catch(function () {
                slotsLoading.style.display = "none";
                slotsEmpty.style.display = "";
                slotsEmpty.textContent = "Unable to load available times. Please try again.";
            });
    }

    // ── Slot click ───────────────────────────────────────────────────

    function onSlotClick(e) {
        // Deselect previous
        var prev = slotsGrid.querySelector(".ej-slot-btn.selected");
        if (prev) prev.classList.remove("selected");

        e.currentTarget.classList.add("selected");
        selectedSlot = {
            datetime: e.currentTarget.dataset.datetime,
            display: e.currentTarget.textContent,
        };

        slotDatetimeInput.value = selectedSlot.datetime;
        selectedSummary.textContent =
            formatDisplay(selectedDate) + " at " + selectedSlot.display;
        setStep(3);
    }

    // ── Back buttons ─────────────────────────────────────────────────

    var backDateBtn = document.querySelector(".ej-btn-back-date");
    if (backDateBtn) {
        backDateBtn.addEventListener("click", function () {
            setStep(1);
        });
    }

    var backTimeBtn = document.querySelector(".ej-btn-back-time");
    if (backTimeBtn) {
        backTimeBtn.addEventListener("click", function () {
            setStep(2);
        });
    }

    // ── Form validation ──────────────────────────────────────────────

    if (bookingForm) {
        bookingForm.addEventListener("submit", function (e) {
            var name = bookingForm.querySelector("#name").value.trim();
            var email = bookingForm.querySelector("#email").value.trim();
            var slotVal = slotDatetimeInput.value;

            if (!name || !email || !slotVal) {
                e.preventDefault();
                alert("Please fill in all required fields.");
                return false;
            }

            // Basic email check
            if (email.indexOf("@") === -1 || email.indexOf(".") === -1) {
                e.preventDefault();
                alert("Please enter a valid email address.");
                return false;
            }

            // Disable button to prevent double-submit
            submitBtn.disabled = true;
            submitBtn.textContent = "Booking...";
        });
    }

    // ── Init ─────────────────────────────────────────────────────────

    renderCalendar();
    setStep(1);
})();
