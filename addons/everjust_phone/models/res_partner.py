# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_phone_call(self):
        """Open softphone with this contact's number pre-filled."""
        self.ensure_one()
        number = self.phone or self.mobile
        if not number:
            raise UserError("No phone number on this contact.")
        return {
            "type": "ir.actions.client",
            "tag": "everjust_phone.dial",
            "params": {"number": number, "partner_id": self.id},
        }

    def action_phone_sms(self):
        """Open SMS composer for this contact."""
        self.ensure_one()
        number = self.phone or self.mobile
        if not number:
            raise UserError("No phone number on this contact.")
        return {
            "type": "ir.actions.client",
            "tag": "everjust_phone.sms",
            "params": {"number": number, "partner_id": self.id},
        }
