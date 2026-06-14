# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AppointmentSlot(models.Model):
    _name = "appointment.slot"
    _description = "Appointment Slot"
    _order = "weekday, start_hour"

    appointment_type_id = fields.Many2one(
        "appointment.type",
        string="Appointment Type",
        required=True,
        ondelete="cascade",
    )
    weekday = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Day of Week",
        required=True,
    )
    start_hour = fields.Float(string="Start Time", required=True, default=9.0)
    end_hour = fields.Float(string="End Time", required=True, default=17.0)

    @api.constrains("start_hour", "end_hour")
    def _check_hours(self):
        for slot in self:
            if slot.start_hour >= slot.end_hour:
                raise models.ValidationError(
                    "End time must be after start time."
                )
            if slot.start_hour < 0 or slot.end_hour > 24:
                raise models.ValidationError(
                    "Hours must be between 0 and 24."
                )
