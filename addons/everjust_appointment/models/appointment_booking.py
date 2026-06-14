# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import timedelta


class AppointmentBooking(models.Model):
    _name = "appointment.booking"
    _description = "Appointment Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc"

    name = fields.Char(
        string="Name", compute="_compute_name", store=True, readonly=False
    )
    appointment_type_id = fields.Many2one(
        "appointment.type",
        string="Appointment Type",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", tracking=True
    )
    staff_user_id = fields.Many2one(
        "res.users", string="Staff Member", tracking=True
    )
    start_datetime = fields.Datetime(
        string="Start", required=True, tracking=True
    )
    end_datetime = fields.Datetime(
        string="End", compute="_compute_end_datetime", store=True
    )
    duration = fields.Float(
        string="Duration (hours)", related="appointment_type_id.duration"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    calendar_event_id = fields.Many2one(
        "calendar.event", string="Calendar Event", readonly=True
    )
    lead_id = fields.Many2one("crm.lead", string="CRM Lead", readonly=True)
    notes = fields.Text(string="Customer Notes")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Service Address")
    location = fields.Char(
        string="Location", related="appointment_type_id.location", readonly=True
    )
    color = fields.Integer(
        string="Color", related="appointment_type_id.color", readonly=True
    )

    @api.depends("appointment_type_id", "partner_id")
    def _compute_name(self):
        for booking in self:
            parts = []
            if booking.appointment_type_id:
                parts.append(booking.appointment_type_id.name)
            if booking.partner_id:
                parts.append(booking.partner_id.name)
            booking.name = " — ".join(parts) if parts else "New Booking"

    @api.depends("start_datetime", "appointment_type_id.duration")
    def _compute_end_datetime(self):
        for booking in self:
            if booking.start_datetime and booking.appointment_type_id:
                hours = booking.appointment_type_id.duration or 1.0
                booking.end_datetime = booking.start_datetime + timedelta(
                    hours=hours
                )
            else:
                booking.end_datetime = False

    def action_confirm(self):
        """Confirm the booking: create calendar event & optionally a CRM lead."""
        for booking in self:
            if booking.state != "draft":
                continue
            booking.state = "confirmed"
            booking._create_calendar_event()
            if booking.appointment_type_id.create_lead:
                booking._create_crm_lead()
            booking._send_confirmation_email()

    def action_done(self):
        for booking in self:
            booking.state = "done"

    def action_cancel(self):
        for booking in self:
            booking.state = "cancelled"
            if booking.calendar_event_id:
                booking.calendar_event_id.unlink()

    def action_reset_draft(self):
        for booking in self:
            booking.state = "draft"

    def _create_calendar_event(self):
        """Create a calendar.event linked to this booking."""
        self.ensure_one()
        attendee_partner_ids = []
        if self.partner_id:
            attendee_partner_ids.append(self.partner_id.id)
        if self.staff_user_id and self.staff_user_id.partner_id:
            attendee_partner_ids.append(self.staff_user_id.partner_id.id)

        event_vals = {
            "name": self.name or "Appointment",
            "start": self.start_datetime,
            "stop": self.end_datetime,
            "user_id": self.staff_user_id.id if self.staff_user_id else self.env.uid,
            "partner_ids": [(6, 0, attendee_partner_ids)],
            "description": self.notes or "",
            "location": self.address or self.location or "",
        }
        event = self.env["calendar.event"].sudo().create(event_vals)
        self.calendar_event_id = event

    def _create_crm_lead(self):
        """Create a CRM lead linked to this booking."""
        self.ensure_one()
        lead_vals = {
            "name": f"Appointment: {self.appointment_type_id.name}",
            "partner_id": self.partner_id.id if self.partner_id else False,
            "user_id": self.staff_user_id.id if self.staff_user_id else False,
            "phone": self.phone,
            "email_from": self.email,
            "street": self.address or False,
            "description": (
                f"Appointment: {self.appointment_type_id.name}\n"
                f"Date: {self.start_datetime}\n"
                f"Address: {self.address or 'N/A'}\n"
                f"Notes: {self.notes or ''}"
            ),
        }
        lead = self.env["crm.lead"].sudo().create(lead_vals)
        self.lead_id = lead

    def _send_confirmation_email(self):
        """Send the booking confirmation email."""
        self.ensure_one()
        template = self.env.ref(
            "everjust_appointment.mail_template_booking_confirmation",
            raise_if_not_found=False,
        )
        if template and self.partner_id and self.partner_id.email:
            template.sudo().send_mail(self.id, force_send=True)

    def _check_staff_availability(self):
        """Check that the staff member doesn't have a conflicting calendar event."""
        self.ensure_one()
        if not self.staff_user_id or not self.start_datetime or not self.end_datetime:
            return True
        conflicting = self.env["calendar.event"].sudo().search([
            ("user_id", "=", self.staff_user_id.id),
            ("start", "<", self.end_datetime),
            ("stop", ">", self.start_datetime),
        ], limit=1)
        if conflicting:
            raise ValidationError(
                f"{self.staff_user_id.name} already has a calendar event "
                f"from {conflicting.start} to {conflicting.stop}. "
                "Please choose another time or staff member."
            )
        # Also check other confirmed bookings
        conflicting_booking = self.search([
            ("id", "!=", self.id if isinstance(self.id, int) else 0),
            ("staff_user_id", "=", self.staff_user_id.id),
            ("start_datetime", "<", self.end_datetime),
            ("end_datetime", ">", self.start_datetime),
            ("state", "in", ["draft", "confirmed"]),
        ], limit=1)
        if conflicting_booking:
            raise ValidationError(
                f"{self.staff_user_id.name} already has a booking at that time. "
                "Please choose another slot."
            )
        return True
