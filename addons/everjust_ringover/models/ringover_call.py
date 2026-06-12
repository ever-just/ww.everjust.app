# -*- coding: utf-8 -*-
import logging
import requests

from datetime import datetime

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
    ringover_user_id = fields.Char(readonly=True)
    ringover_user_name = fields.Char(string="Agent", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Contact", readonly=True)
    lead_id = fields.Many2one("crm.lead", string="Opportunity", readonly=True)
    user_id = fields.Many2one("res.users", string="Odoo User", readonly=True)

    @staticmethod
    def _parse_dt(val):
        """Convert ISO 8601 datetime string to Odoo-compatible format."""
        if not val:
            return False
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return False

    @api.model
    def _sync_from_api_data(self, call_data):
        """Create or update a call record from Ringover API response data."""
        cdr_id = str(call_data.get("cdr_id", ""))
        existing = self.search([("cdr_id", "=", cdr_id)], limit=1)

        contact_number = call_data.get("contact_number", "")
        partner = self.env["res.partner"]
        if contact_number and len(contact_number) >= 10:
            partner = self.env["res.partner"].search(
                [("phone", "like", contact_number[-10:])], limit=1,
            )

        ringover_user = call_data.get("user") or {}
        odoo_user = self.env["res.users"]
        if ringover_user.get("email"):
            odoo_user = self.env["res.users"].search(
                [("login", "=", ringover_user["email"])], limit=1,
            )

        # Also find CRM lead linked to this partner
        lead = self.env["crm.lead"]
        if partner and "crm.lead" in self.env:
            lead = self.env["crm.lead"].search(
                [("partner_id", "=", partner.id), ("active", "=", True)],
                order="id desc", limit=1,
            )

        vals = {
            "cdr_id": cdr_id,
            "call_id": call_data.get("call_id", ""),
            "direction": call_data.get("direction", ""),
            "contact_number": contact_number,
            "from_number": call_data.get("from_number", ""),
            "to_number": call_data.get("to_number", ""),
            "start_time": self._parse_dt(call_data.get("start_time")),
            "end_time": self._parse_dt(call_data.get("end_time")),
            "duration": call_data.get("incall_duration") or 0,
            "is_answered": call_data.get("is_answered", False),
            "state": call_data.get("last_state", ""),
            "hangup_by": call_data.get("hangup_by", ""),
            "recording_url": call_data.get("record") or "",
            "voicemail_url": "",
            "ringover_user_id": str(ringover_user.get("user_id", "")),
            "ringover_user_name": ringover_user.get("concat_name", ""),
            "partner_id": partner.id if partner else False,
            "lead_id": lead.id if lead else False,
            "user_id": odoo_user.id if odoo_user else False,
        }

        if existing:
            existing.write(vals)
            return existing

        record = self.create(vals)
        # Post to partner AND lead chatter
        direction = "Incoming" if vals["direction"] == "in" else "Outgoing"
        dur = vals["duration"]
        body = "<b>%s call</b> — %s (%dm %ds)" % (direction, contact_number, dur // 60, dur % 60)
        if vals["recording_url"]:
            body += '<br/><a href="%s" target="_blank">Listen to recording</a>' % vals["recording_url"]
        if partner:
            partner.message_post(body=body, message_type="notification", subtype_xmlid="mail.mt_note")
        if lead:
            lead.message_post(body=body, message_type="notification", subtype_xmlid="mail.mt_note")
        return record

    # --- API helpers ---

    @api.model
    def _ringover_api_get(self, endpoint, params=None):
        ICP = self.env["ir.config_parameter"].sudo()
        url = (ICP.get_param("everjust.ringover_api_url") or "").rstrip("/")
        key = ICP.get_param("everjust.ringover_api_key") or ""
        if not url or not key:
            return None
        try:
            resp = requests.get(
                "%s%s" % (url, endpoint),
                headers={"Authorization": key},
                params=params or {},
                timeout=15,
            )
            return resp.json() if resp.ok else None
        except requests.RequestException as exc:
            _logger.error("Ringover API error: %s", exc)
            return None

    @api.model
    def cron_sync_all(self):
        """Cron: sync recent calls from Ringover."""
        data = self._ringover_api_get("/calls", {"limit_count": 50})
        if not data or "call_list" not in data:
            return
        count = 0
        for cd in data["call_list"]:
            try:
                self._sync_from_api_data(cd)
                count += 1
            except Exception as exc:
                _logger.error("Failed to sync call %s: %s", cd.get("cdr_id"), exc)
        _logger.info("Ringover: synced %s calls", count)

    @api.model
    def initiate_call(self, from_number, to_number):
        """Initiate a callback via Ringover API — rings the agent first,
        then auto-dials the recipient when agent picks up."""
        ICP = self.env["ir.config_parameter"].sudo()
        url = (ICP.get_param("everjust.ringover_api_url") or "").rstrip("/")
        key = ICP.get_param("everjust.ringover_api_key") or ""
        if not url or not key:
            return {"error": "Ringover API not configured"}
        try:
            resp = requests.post(
                "%s/callback" % url,
                headers={"Authorization": key, "Content-Type": "application/json"},
                json={"from_number": from_number, "to_number": to_number},
                timeout=15,
            )
            if resp.ok:
                return {"success": True}
            return {"error": "Ringover API returned %s" % resp.status_code}
        except requests.RequestException as exc:
            return {"error": str(exc)}
