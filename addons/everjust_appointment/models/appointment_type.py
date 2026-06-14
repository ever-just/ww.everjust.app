# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AppointmentType(models.Model):
    _name = "appointment.type"
    _description = "Appointment Type"
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    duration = fields.Float(string="Duration (hours)", default=1.0, required=True)
    description = fields.Html(string="Description")
    staff_user_ids = fields.Many2many(
        "res.users",
        "appointment_type_staff_rel",
        "appointment_type_id",
        "user_id",
        string="Staff Members",
    )
    location = fields.Char(string="Location")
    is_published = fields.Boolean(string="Published on Website", default=False)
    color = fields.Integer(string="Color")
    min_schedule_hours = fields.Float(
        string="Minimum Advance Booking (hours)",
        default=24.0,
        help="Customers must book at least this many hours in advance.",
    )
    max_schedule_days = fields.Integer(
        string="Maximum Advance Booking (days)",
        default=30,
        help="How far in the future customers can book.",
    )
    create_lead = fields.Boolean(
        string="Create CRM Lead",
        default=False,
        help="Automatically create a CRM lead when a booking is confirmed.",
    )
    slot_ids = fields.One2many(
        "appointment.slot", "appointment_type_id", string="Available Slots"
    )

    def _get_available_staff(self):
        """Return staff users, or all internal users if none configured."""
        self.ensure_one()
        if self.staff_user_ids:
            return self.staff_user_ids
        return self.env["res.users"].search([("share", "=", False)])
