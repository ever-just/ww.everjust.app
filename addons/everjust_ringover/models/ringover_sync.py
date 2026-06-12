# -*- coding: utf-8 -*-
import logging
import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class RingoverSync(models.AbstractModel):
    _name = "ringover.sync"
    _description = "Ringover API Sync Service"

    def _get_api_config(self):
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "url": (ICP.get_param("everjust.ringover_api_url") or "").rstrip("/"),
            "key": ICP.get_param("everjust.ringover_api_key") or "",
        }

    def _api_get(self, endpoint, params=None):
        config = self._get_api_config()
        if not config["url"] or not config["key"]:
            _logger.warning("Ringover API not configured")
            return None
        try:
            resp = requests.get(
                "%s%s" % (config["url"], endpoint),
                headers={"Authorization": config["key"]},
                params=params or {},
                timeout=15,
            )
            if resp.ok:
                return resp.json()
            _logger.warning("Ringover API %s returned %s", endpoint, resp.status_code)
            return None
        except requests.RequestException as exc:
            _logger.error("Ringover API error: %s", exc)
            return None

    def _api_post(self, endpoint, data=None):
        config = self._get_api_config()
        if not config["url"] or not config["key"]:
            return None
        try:
            resp = requests.post(
                "%s%s" % (config["url"], endpoint),
                headers={"Authorization": config["key"], "Content-Type": "application/json"},
                json=data or {},
                timeout=15,
            )
            if resp.ok:
                return resp.json()
            _logger.warning("Ringover API POST %s returned %s: %s", endpoint, resp.status_code, resp.text[:200])
            return None
        except requests.RequestException as exc:
            _logger.error("Ringover API error: %s", exc)
            return None

    @api.model
    def sync_calls(self, limit=100):
        """Fetch recent calls from Ringover and sync to Odoo."""
        data = self._api_get("/calls", {"limit_count": limit})
        if not data or "call_list" not in data:
            return 0
        CallModel = self.env["ringover.call"]
        count = 0
        for call_data in data["call_list"]:
            try:
                CallModel._sync_from_api_data(call_data)
                count += 1
            except Exception as exc:
                _logger.error("Failed to sync call %s: %s", call_data.get("cdr_id"), exc)
        _logger.info("Ringover: synced %s calls", count)
        return count

    @api.model
    def sync_conversations(self, limit=50):
        """Fetch recent SMS conversations and post to partner chatter."""
        data = self._api_get("/conversations", {"limit_count": limit})
        if not data or "conversations_list" not in data:
            return 0
        count = 0
        for conv in data.get("conversations_list", []):
            try:
                number = conv.get("number", "")
                if not number or len(number) < 10:
                    continue
                partner = self.env["res.partner"].search(
                    ["|", ("phone", "like", number[-10:]),
                     ("mobile", "like", number[-10:])],
                    limit=1,
                )
                if not partner:
                    continue
                # Get messages in this conversation
                conv_id = conv.get("conv_id")
                if not conv_id:
                    continue
                msg_data = self._api_get("/conversations/%s" % conv_id)
                if not msg_data:
                    continue
                for msg in msg_data.get("messages_list", []):
                    body = msg.get("body", "")
                    if not body:
                        continue
                    direction = msg.get("direction", "")
                    # Check if already posted (use ringover msg id as tracking)
                    msg_id = str(msg.get("message_id", ""))
                    existing = self.env["mail.message"].search([
                        ("body", "like", "ringover-msg-%s" % msg_id),
                        ("model", "=", "res.partner"),
                        ("res_id", "=", partner.id),
                    ], limit=1)
                    if existing:
                        continue
                    prefix = "SMS received" if direction == "in" else "SMS sent"
                    post_body = "<b>%s</b>: %s <!-- ringover-msg-%s -->" % (prefix, body, msg_id)
                    partner.message_post(
                        body=post_body,
                        message_type="sms",
                        subtype_xmlid="mail.mt_note",
                    )
                    count += 1
            except Exception as exc:
                _logger.error("Failed to sync conversation: %s", exc)
        _logger.info("Ringover: synced %s SMS messages", count)
        return count

    @api.model
    def send_sms(self, to_number, body, from_number=None):
        """Send an SMS through Ringover API."""
        payload = {"to_number": to_number, "message": body}
        if from_number:
            payload["from_number"] = from_number
        return self._api_post("/push/sms", payload)

    @api.model
    def cron_sync_all(self):
        """Cron job: sync calls + SMS from Ringover."""
        self.sync_calls(limit=50)
        self.sync_conversations(limit=20)
