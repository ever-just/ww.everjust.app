# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class RingoverWebhookController(http.Controller):
    """Receive real-time webhooks from Ringover for calls and SMS."""

    @http.route("/ringover/webhook", type="http", auth="none", csrf=False, methods=["POST"])
    def ringover_webhook(self):
        try:
            data = json.loads(request.httprequest.get_data(as_text=True))
        except (json.JSONDecodeError, TypeError):
            return Response('{"error":"invalid json"}', content_type="application/json", status=400)

        event_type = data.get("event", data.get("type", ""))
        _logger.info("Ringover webhook: %s", event_type)

        # Verify webhook secret if configured
        expected = request.env["ir.config_parameter"].sudo().get_param("everjust.ringover_webhook_secret")
        if expected:
            provided = request.httprequest.headers.get("X-Ringover-Signature", "")
            if provided != expected:
                return Response('{"error":"unauthorized"}', content_type="application/json", status=403)

        # Handle call events
        if "call" in event_type.lower() or data.get("cdr_id"):
            try:
                request.env["ringover.call"].sudo()._sync_from_api_data(data)
            except Exception as exc:
                _logger.error("Ringover webhook call sync error: %s", exc)

        # Handle SMS events
        if "sms" in event_type.lower() or data.get("message_id"):
            try:
                self._handle_sms_event(data)
            except Exception as exc:
                _logger.error("Ringover webhook SMS error: %s", exc)

        return Response('{"status":"ok"}', content_type="application/json", status=200)

    def _handle_sms_event(self, data):
        number = data.get("from_number") or data.get("to_number") or data.get("number", "")
        body = data.get("body") or data.get("message", "")
        direction = data.get("direction", "")
        msg_id = str(data.get("message_id", data.get("conv_id", "")))

        if not number or not body:
            return

        partner = request.env["res.partner"].sudo().search(
            ["|", ("phone", "like", number[-10:]),
             ("mobile", "like", number[-10:])],
            limit=1,
        ) if len(number) >= 10 else None

        if partner:
            existing = request.env["mail.message"].sudo().search([
                ("body", "like", "ringover-msg-%s" % msg_id),
                ("model", "=", "res.partner"),
                ("res_id", "=", partner.id),
            ], limit=1)
            if not existing:
                prefix = "SMS received" if direction == "in" else "SMS sent"
                post_body = "<b>%s</b>: %s <!-- ringover-msg-%s -->" % (prefix, body, msg_id)
                partner.message_post(body=post_body, message_type="sms", subtype_xmlid="mail.mt_note")
                _logger.info("Ringover SMS from %s posted to partner %s", number, partner.id)
