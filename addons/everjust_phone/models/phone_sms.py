# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PhoneSms(models.Model):
    _name = "everjust.phone.sms"
    _description = "Phone SMS Message"
    _order = "create_date desc"

    message_sid = fields.Char(index=True, readonly=True)
    direction = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        readonly=True,
    )
    from_number = fields.Char(readonly=True)
    to_number = fields.Char(readonly=True)
    body = fields.Text(readonly=True)
    status = fields.Char(readonly=True)
    partner_id = fields.Many2one("res.partner", string="Contact", readonly=True)
    user_id = fields.Many2one("res.users", string="User", readonly=True,
                              default=lambda self: self.env.user)

    @api.model
    def log_sms_from_webhook(self, data):
        """Create an SMS record from Twilio webhook and post to chatter."""
        msg_sid = data.get("MessageSid", data.get("SmsSid", ""))
        if msg_sid and self.search_count([("message_sid", "=", msg_sid)]):
            return  # Already logged

        from_num = data.get("From", "")
        to_num = data.get("To", "")
        body = data.get("Body", "")

        ICP = self.env["ir.config_parameter"].sudo()
        our_number = ICP.get_param("everjust_phone.phone_number") or ""
        direction = "inbound" if to_num == our_number else "outbound"
        contact_num = from_num if direction == "inbound" else to_num

        partner = self.env["res.partner"]
        if contact_num and len(contact_num) >= 10:
            partner = self.env["res.partner"].search(
                [("phone", "like", contact_num[-10:])], limit=1
            )

        record = self.create({
            "message_sid": msg_sid,
            "direction": direction,
            "from_number": from_num,
            "to_number": to_num,
            "body": body,
            "status": data.get("SmsStatus", ""),
            "partner_id": partner.id if partner else False,
        })

        if partner and body:
            prefix = "SMS received" if direction == "inbound" else "SMS sent"
            partner.message_post(
                body="<b>%s</b>: %s" % (prefix, body),
                message_type="sms",
                subtype_xmlid="mail.mt_note",
            )

        return record

    @api.model
    def send_sms(self, to_number, body):
        """Send an SMS via Twilio REST API."""
        ICP = self.env["ir.config_parameter"].sudo()
        sid = ICP.get_param("everjust_phone.account_sid")
        token = ICP.get_param("everjust_phone.auth_token")
        from_number = ICP.get_param("everjust_phone.phone_number")
        if not all([sid, token, from_number]):
            return {"error": "Twilio not configured"}
        try:
            from twilio.rest import Client
            client = Client(sid, token)
            msg = client.messages.create(body=body, from_=from_number, to=to_number)
            self.create({
                "message_sid": msg.sid,
                "direction": "outbound",
                "from_number": from_number,
                "to_number": to_number,
                "body": body,
                "status": msg.status,
            })
            return {"success": True, "sid": msg.sid}
        except Exception as exc:
            _logger.error("Twilio SMS error: %s", exc)
            return {"error": str(exc)}
