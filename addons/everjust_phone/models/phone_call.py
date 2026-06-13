# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PhoneCall(models.Model):
    _name = "everjust.phone.call"
    _description = "Phone Call"
    _order = "start_time desc"
    _rec_name = "display_name"

    call_sid = fields.Char(string="Call SID", index=True, readonly=True)
    direction = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        readonly=True,
    )
    from_number = fields.Char(readonly=True)
    to_number = fields.Char(readonly=True)
    status = fields.Selection(
        [
            ("queued", "Queued"),
            ("ringing", "Ringing"),
            ("in-progress", "In Progress"),
            ("completed", "Completed"),
            ("busy", "Busy"),
            ("no-answer", "No Answer"),
            ("canceled", "Canceled"),
            ("failed", "Failed"),
        ],
        default="queued",
        readonly=True,
    )
    start_time = fields.Datetime(readonly=True)
    end_time = fields.Datetime(readonly=True)
    duration = fields.Integer(string="Duration (sec)", readonly=True)
    recording_url = fields.Char(string="Recording", readonly=True)
    recording_sid = fields.Char(readonly=True)
    transcription = fields.Text(readonly=True)

    partner_id = fields.Many2one("res.partner", string="Contact", readonly=True)
    user_id = fields.Many2one("res.users", string="User", readonly=True,
                              default=lambda self: self.env.user)

    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("direction", "from_number", "to_number", "partner_id")
    def _compute_display_name(self):
        for rec in self:
            name = rec.partner_id.name if rec.partner_id else (
                rec.from_number if rec.direction == "inbound" else rec.to_number
            )
            rec.display_name = "%s — %s" % (
                "Incoming" if rec.direction == "inbound" else "Outgoing",
                name or "Unknown",
            )

    @api.model
    def get_twilio_token(self):
        """Generate a Twilio access token for the current user's browser."""
        ICP = self.env["ir.config_parameter"].sudo()
        account_sid = ICP.get_param("everjust_phone.account_sid")
        api_key = ICP.get_param("everjust_phone.api_key")
        api_secret = ICP.get_param("everjust_phone.api_secret")
        twiml_app_sid = ICP.get_param("everjust_phone.twiml_app_sid")
        if not all([account_sid, api_key, api_secret, twiml_app_sid]):
            return {"error": "Twilio not configured"}
        try:
            from twilio.jwt.access_token import AccessToken
            from twilio.jwt.access_token.grants import VoiceGrant
            identity = self.env.user.login.replace("@", "_at_").replace(".", "_")
            token = AccessToken(account_sid, api_key, api_secret, identity=identity, ttl=3600)
            token.add_grant(VoiceGrant(outgoing_application_sid=twiml_app_sid, incoming_allow=True))
            return {"token": token.to_jwt(), "identity": identity}
        except Exception as exc:
            return {"error": str(exc)}

    @api.model
    def log_call_from_webhook(self, data):
        """Create or update a call record from Twilio webhook data."""
        call_sid = data.get("CallSid", "")
        existing = self.search([("call_sid", "=", call_sid)], limit=1)

        # Determine direction
        ICP = self.env["ir.config_parameter"].sudo()
        our_number = ICP.get_param("everjust_phone.phone_number") or ""
        from_num = data.get("From", "")
        to_num = data.get("To", "")
        direction = "inbound" if to_num == our_number else "outbound"

        # Match partner
        contact_num = from_num if direction == "inbound" else to_num
        partner = self.env["res.partner"]
        if contact_num and len(contact_num) >= 10:
            partner = self.env["res.partner"].search(
                [("phone", "like", contact_num[-10:])], limit=1
            )

        # Match CRM lead
        lead = self.env["crm.lead"]
        if partner:
            lead = self.env["crm.lead"].search(
                [("partner_id", "=", partner.id), ("active", "=", True)],
                order="id desc", limit=1,
            )

        vals = {
            "call_sid": call_sid,
            "direction": direction,
            "from_number": from_num,
            "to_number": to_num,
            "status": data.get("CallStatus", "queued"),
            "duration": int(data.get("CallDuration", 0) or 0),
            "recording_url": data.get("RecordingUrl", ""),
            "recording_sid": data.get("RecordingSid", ""),
            "partner_id": partner.id if partner else False,
            "lead_id": lead.id if lead else False,
        }

        if existing:
            existing.write(vals)
            record = existing
        else:
            from datetime import datetime
            vals["start_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            record = self.create(vals)

        # Post to chatter when call completes
        if vals["status"] == "completed" and (partner or lead):
            dur = vals["duration"]
            body = "<b>%s call</b> — %s (%dm %ds)" % (
                "Incoming" if direction == "inbound" else "Outgoing",
                contact_num,
                dur // 60, dur % 60,
            )
            if vals["recording_url"]:
                body += '<br/><a href="%s" target="_blank">Listen to recording</a>' % vals["recording_url"]
            if partner:
                partner.message_post(body=body, message_type="notification",
                                     subtype_xmlid="mail.mt_note")
            if lead:
                lead.message_post(body=body, message_type="notification",
                                  subtype_xmlid="mail.mt_note")

        return record
