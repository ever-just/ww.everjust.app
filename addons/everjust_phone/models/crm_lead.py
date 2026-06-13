# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_phone_call(self):
        self.ensure_one()
        number = self.phone or (self.partner_id and self.partner_id.phone)
        if not number:
            raise UserError("No phone number on this lead.")
        return {
            "type": "ir.actions.client",
            "tag": "everjust_phone.dial",
            "params": {"number": number, "partner_id": self.partner_id.id if self.partner_id else False},
        }
