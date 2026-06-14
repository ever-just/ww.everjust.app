# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, time

from odoo import http, fields
from odoo.http import request


class AppointmentController(http.Controller):

    @http.route("/appointment", type="http", auth="public", website=True)
    def appointment_list(self, **kwargs):
        """List all published appointment types."""
        types = (
            request.env["appointment.type"]
            .sudo()
            .search([("is_published", "=", True)], order="sequence, name")
        )
        return request.render(
            "everjust_appointment.appointment_list_page",
            {"appointment_types": types},
        )

    @http.route(
        "/appointment/<int:type_id>",
        type="http",
        auth="public",
        website=True,
    )
    def appointment_booking_page(self, type_id, **kwargs):
        """Show the booking page for a specific appointment type."""
        appt_type = (
            request.env["appointment.type"]
            .sudo()
            .browse(type_id)
        )
        if not appt_type.exists() or not appt_type.is_published:
            return request.redirect("/appointment")

        # Build the list of available weekdays from slots
        available_weekdays = list(
            set(int(s.weekday) for s in appt_type.slot_ids)
        )

        # Date range
        now = fields.Datetime.now()
        min_date = now + timedelta(hours=appt_type.min_schedule_hours)
        max_date = now + timedelta(days=appt_type.max_schedule_days)

        return request.render(
            "everjust_appointment.appointment_booking_page",
            {
                "appt_type": appt_type,
                "available_weekdays": json.dumps(available_weekdays),
                "min_date": min_date.strftime("%Y-%m-%d"),
                "max_date": max_date.strftime("%Y-%m-%d"),
            },
        )

    @http.route(
        "/appointment/<int:type_id>/slots",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_available_slots(self, type_id, **kwargs):
        """Return available time slots for a given date as JSON."""
        date_str = kwargs.get("date")
        if not date_str:
            return request.make_json_response({"error": "Missing date parameter"}, status=400)

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return request.make_json_response({"error": "Invalid date format"}, status=400)

        appt_type = (
            request.env["appointment.type"]
            .sudo()
            .browse(type_id)
        )
        if not appt_type.exists() or not appt_type.is_published:
            return request.make_json_response({"error": "Appointment type not found"}, status=404)

        # Get the weekday (Monday=0)
        weekday = str(selected_date.weekday())

        # Find matching slot configs for this weekday
        slots = appt_type.slot_ids.filtered(lambda s: s.weekday == weekday)
        if not slots:
            return request.make_json_response({"slots": []})

        duration_hours = appt_type.duration or 1.0
        duration_td = timedelta(hours=duration_hours)
        now = fields.Datetime.now()

        available = []
        staff_users = appt_type._get_available_staff()

        for slot in slots:
            # Generate time slots at 30-minute intervals within the slot window
            current_minutes = int(slot.start_hour * 60)
            end_minutes = int(slot.end_hour * 60)
            interval = max(int(duration_hours * 60), 30)

            while current_minutes + int(duration_hours * 60) <= end_minutes:
                hour = current_minutes // 60
                minute = current_minutes % 60
                slot_start = datetime.combine(
                    selected_date, time(hour, minute)
                )
                slot_end = slot_start + duration_td

                # Skip slots in the past (including min_schedule_hours)
                min_start = now + timedelta(hours=appt_type.min_schedule_hours)
                if slot_start < min_start:
                    current_minutes += interval
                    continue

                # Check if at least one staff member is available
                has_available_staff = False
                for user in staff_users:
                    # Check existing calendar events
                    conflicting_event = (
                        request.env["calendar.event"]
                        .sudo()
                        .search(
                            [
                                ("user_id", "=", user.id),
                                ("start", "<", fields.Datetime.to_string(slot_end)),
                                ("stop", ">", fields.Datetime.to_string(slot_start)),
                            ],
                            limit=1,
                        )
                    )
                    # Check existing bookings
                    conflicting_booking = (
                        request.env["appointment.booking"]
                        .sudo()
                        .search(
                            [
                                ("staff_user_id", "=", user.id),
                                ("start_datetime", "<", fields.Datetime.to_string(slot_end)),
                                ("end_datetime", ">", fields.Datetime.to_string(slot_start)),
                                ("state", "in", ["draft", "confirmed"]),
                            ],
                            limit=1,
                        )
                    )
                    if not conflicting_event and not conflicting_booking:
                        has_available_staff = True
                        break

                if has_available_staff:
                    available.append(
                        {
                            "time": slot_start.strftime("%H:%M"),
                            "display": slot_start.strftime("%-I:%M %p"),
                            "datetime": slot_start.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                current_minutes += interval

        return request.make_json_response({"slots": available})

    @http.route(
        "/appointment/<int:type_id>/book",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def submit_booking(self, type_id, **kwargs):
        """Process a booking submission."""
        appt_type = (
            request.env["appointment.type"]
            .sudo()
            .browse(type_id)
        )
        if not appt_type.exists() or not appt_type.is_published:
            return request.redirect("/appointment")

        name = kwargs.get("name", "").strip()
        email = kwargs.get("email", "").strip()
        phone = kwargs.get("phone", "").strip()
        address = kwargs.get("address", "").strip()
        notes = kwargs.get("notes", "").strip()
        slot_datetime_str = kwargs.get("slot_datetime", "").strip()

        if not name or not email or not slot_datetime_str:
            return request.redirect(f"/appointment/{type_id}")

        try:
            slot_datetime = datetime.strptime(
                slot_datetime_str, "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            return request.redirect(f"/appointment/{type_id}")

        # Find or create partner
        partner = (
            request.env["res.partner"]
            .sudo()
            .search([("email", "=ilike", email)], limit=1)
        )
        if not partner:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create({"name": name, "email": email, "phone": phone})
            )
        elif phone and not partner.phone:
            partner.sudo().write({"phone": phone})

        # Find first available staff member for this slot
        staff_user = False
        duration_td = timedelta(hours=appt_type.duration or 1.0)
        slot_end = slot_datetime + duration_td
        staff_users = appt_type._get_available_staff()

        for user in staff_users:
            conflicting_event = (
                request.env["calendar.event"]
                .sudo()
                .search(
                    [
                        ("user_id", "=", user.id),
                        ("start", "<", fields.Datetime.to_string(slot_end)),
                        ("stop", ">", fields.Datetime.to_string(slot_datetime)),
                    ],
                    limit=1,
                )
            )
            conflicting_booking = (
                request.env["appointment.booking"]
                .sudo()
                .search(
                    [
                        ("staff_user_id", "=", user.id),
                        ("start_datetime", "<", fields.Datetime.to_string(slot_end)),
                        ("end_datetime", ">", fields.Datetime.to_string(slot_datetime)),
                        ("state", "in", ["draft", "confirmed"]),
                    ],
                    limit=1,
                )
            )
            if not conflicting_event and not conflicting_booking:
                staff_user = user
                break

        # Create the booking
        booking = (
            request.env["appointment.booking"]
            .sudo()
            .create(
                {
                    "appointment_type_id": appt_type.id,
                    "partner_id": partner.id,
                    "staff_user_id": staff_user.id if staff_user else False,
                    "start_datetime": fields.Datetime.to_string(slot_datetime),
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "notes": notes,
                }
            )
        )

        # Auto-confirm
        booking.action_confirm()

        return request.redirect(
            f"/appointment/confirmation?booking_id={booking.id}"
        )

    @http.route(
        "/appointment/confirmation",
        type="http",
        auth="public",
        website=True,
    )
    def appointment_confirmation(self, **kwargs):
        """Show the confirmation page."""
        booking_id = kwargs.get("booking_id")
        booking = False
        if booking_id:
            try:
                booking = (
                    request.env["appointment.booking"]
                    .sudo()
                    .browse(int(booking_id))
                )
                if not booking.exists():
                    booking = False
            except (ValueError, TypeError):
                booking = False

        return request.render(
            "everjust_appointment.appointment_confirmation_page",
            {"booking": booking},
        )
