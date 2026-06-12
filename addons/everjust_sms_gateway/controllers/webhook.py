# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class SmsWebhookController(http.Controller):
    """Receive incoming SMS from TextBee and post them in Odoo chatter.

    TextBee sends a POST with JSON like::

        {
            "message": "Hey, is my order ready?",
            "phoneNumber": "+16505551234",
            "receivedAt": "2026-06-12T06:00:00Z"
        }

    We match the phone number to a partner and post the message body
    as an SMS-type chatter message on that partner's record.
    """

    @http.route(
        "/sms/incoming",
        type="http",
        auth="none",
        csrf=False,
        methods=["POST"],
    )
    def incoming_sms(self):
        try:
            data = json.loads(request.httprequest.get_data(as_text=True))
        except (json.JSONDecodeError, TypeError):
            return Response(
                json.dumps({"status": "error", "reason": "invalid JSON"}),
                content_type="application/json",
                status=400,
            )

        phone = data.get("phoneNumber") or data.get("from") or ""
        body = data.get("message") or data.get("body") or ""

        if not phone or not body:
            return Response(
                json.dumps({"status": "ignored", "reason": "missing phone or body"}),
                content_type="application/json",
                status=200,
            )

        # Verify the webhook key if one is configured.
        expected_key = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("everjust.sms_webhook_key")
        )
        if expected_key:
            provided_key = request.httprequest.headers.get("X-Webhook-Key", "")
            if provided_key != expected_key:
                _logger.warning("SMS webhook: invalid key from %s", phone)
                return Response(
                    json.dumps({"status": "error", "reason": "unauthorized"}),
                    content_type="application/json",
                    status=403,
                )

        # Reverse-lookup: find partner by phone or mobile.
        partner = (
            request.env["res.partner"]
            .sudo()
            .search(
                ["|", ("phone", "=", phone), ("mobile", "=", phone)],
                limit=1,
            )
        )

        if partner:
            partner.message_post(
                body=body,
                message_type="sms",
                subtype_xmlid="mail.mt_note",
                author_id=partner.id,
            )
            _logger.info(
                "SMS from %s -> partner %s (#%s)", phone, partner.name, partner.id
            )
        else:
            _logger.info("SMS from unknown number %s: %s", phone, body[:80])

        return Response(
            json.dumps(
                {"status": "ok", "partner_id": partner.id if partner else None}
            ),
            content_type="application/json",
            status=200,
        )
