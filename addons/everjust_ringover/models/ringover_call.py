# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RingoverCall(models.Model):
    _name = "ringover.call"
    _description = "Ringover Call Log"
    _order = "start_time desc"
    _rec_name = "contact_number"

    cdr_id = fields.Char(string="CDR ID", index=True, readonly=True)
    call_id = fields.Char(string="Call ID", readonly=True)
    direction = fields.Selection(
        [("in", "Incoming"), ("out", "Outgoing")],
        readonly=True,
    )
    contact_number = fields.Char(readonly=True)
    from_number = fields.Char(readonly=True)
    to_number = fields.Char(readonly=True)
    start_time = fields.Datetime(readonly=True)
    end_time = fields.Datetime(readonly=True)
    duration = fields.Integer(string="Duration (sec)", readonly=True)
    is_answered = fields.Boolean(readonly=True)
    state = fields.Char(readonly=True)
    hangup_by = fields.Char(readonly=True)
    recording_url = fields.Char(string="Recording", readonly=True)
    voicemail_url = fields.Char(string="Voicemail", readonly=True)

    # Ringover user
    ringover_user_id = fields.Char(readonly=True)
    ringover_user_name = fields.Char(string="Agent", readonly=True)

    # Odoo links
    partner_id = fields.Many2one("res.partner", string="Contact", readonly=True)
    user_id = fields.Many2one("res.users", string="Odoo User", readonly=True)

    _sql_constraints = []

    @api.model
    def _sync_from_api_data(self, call_data):
        """Create or update a call record from Ringover API response data."""
        cdr_id = str(call_data.get("cdr_id", ""))
        existing = self.search([("cdr_id", "=", cdr_id)], limit=1)

        # Match partner by phone number
        contact_number = call_data.get("contact_number", "")
        partner = self.env["res.partner"].search(
            ["|", ("phone", "like", contact_number[-10:]),
             ("mobile", "like", contact_number[-10:])],
            limit=1,
        ) if contact_number and len(contact_number) >= 10 else self.env["res.partner"]

        # Match Odoo user by email
        ringover_user = call_data.get("user", {})
        odoo_user = self.env["res.users"].search(
            [("login", "=", ringover_user.get("email", ""))], limit=1
        ) if ringover_user.get("email") else self.env["res.users"]

        vals = {
            "cdr_id": cdr_id,
            "call_id": call_data.get("call_id", ""),
            "direction": call_data.get("direction", ""),
            "contact_number": contact_number,
            "from_number": call_data.get("from_number", ""),
            "to_number": call_data.get("to_number", ""),
            "start_time": call_data.get("start_time"),
            "end_time": call_data.get("end_time"),
            "duration": call_data.get("incall_duration") or 0,
            "is_answered": call_data.get("is_answered", False),
            "state": call_data.get("last_state", ""),
            "hangup_by": call_data.get("hangup_by", ""),
            "recording_url": call_data.get("record", ""),
            "voicemail_url": (call_data.get("voicemail") or {}).get("url", "")
            if isinstance(call_data.get("voicemail"), dict) else "",
            "ringover_user_id": str(ringover_user.get("user_id", "")),
            "ringover_user_name": ringover_user.get("concat_name", ""),
            "partner_id": partner.id if partner else False,
            "user_id": odoo_user.id if odoo_user else False,
        }

        if existing:
            existing.write(vals)
            return existing
        else:
            record = self.create(vals)
            # Post to partner chatter if matched
            if partner:
                direction = "Incoming" if vals["direction"] == "in" else "Outgoing"
                duration_str = "%dm %ds" % (vals["duration"] // 60, vals["duration"] % 60)
                body = "<b>%s call</b> — %s (%s)" % (direction, contact_number, duration_str)
                if vals["recording_url"]:
                    body += '<br/><a href="%s" target="_blank">Listen to recording</a>' % vals["recording_url"]
                partner.message_post(body=body, message_type="notification", subtype_xmlid="mail.mt_note")
            return record
