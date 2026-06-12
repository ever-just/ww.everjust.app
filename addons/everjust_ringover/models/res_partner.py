# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_ringover_call(self):
        """Initiate a call to this contact via Ringover callback API."""
        self.ensure_one()
        number = self.phone or self.mobile
        if not number:
            raise UserError("No phone number on this contact.")
        # Get the current user's Ringover number from their latest call
        # or fall back to the first number in the Ringover account
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
