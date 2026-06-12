# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_ringover_call(self):
        """Initiate a call to this lead's phone via Ringover."""
        self.ensure_one()
        number = self.phone or (self.partner_id and self.partner_id.phone)
        if not number:
            raise UserError("No phone number on this lead.")
        ICP = self.env["ir.config_parameter"].sudo()
        from_number = ICP.get_param("everjust.ringover_from_number") or ""
        if not from_number:
            raise UserError(
                "Set your Ringover phone number in Settings > General Settings > "
                "Ringover Integration (everjust.ringover_from_number system parameter)."
            )
        result = self.env["ringover.call"].initiate_call(from_number, number)
        if result.get("error"):
            raise UserError("Ringover call failed: %s" % result["error"])
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Calling...",
                "message": "Ringover is calling %s" % number,
                "type": "info",
                "sticky": False,
            },
        }
