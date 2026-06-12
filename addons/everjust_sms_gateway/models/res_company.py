# -*- coding: utf-8 -*-
import logging
import requests

from odoo import fields, models
from odoo.addons.sms.tools.sms_api import SmsApiBase

_logger = logging.getLogger(__name__)


class SmsApiTextBee(SmsApiBase):
    """Send SMS through a self-hosted TextBee gateway instead of Odoo IAP.

    TextBee exposes a REST API at ``POST /api/messages/send`` that accepts
    ``{recipients: [{phone}], message}`` and returns a result per recipient.
    The gateway URL and API key are stored in ``ir.config_parameter``.

    This class follows the same contract as the core ``SmsApi`` so that
    ``sms.sms._send_with_api`` works unchanged — every existing SMS feature
    (composer, templates, phone-field buttons, chatter threading, marketing
    campaigns, CRM/Sales/Events bridges) continues to work transparently.
    """

    PROVIDER_TO_SMS_FAILURE_TYPE = SmsApiBase.PROVIDER_TO_SMS_FAILURE_TYPE | {
        "gateway_error": "sms_server",
    }

    def __init__(self, env, account=None):
        super().__init__(env, account=account)
        ICP = env["ir.config_parameter"].sudo()
        self._gateway_url = (ICP.get_param("everjust.sms_gateway_url") or "").rstrip("/")
        self._api_key = ICP.get_param("everjust.sms_gateway_key") or ""

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        """Send a batch of SMS messages through TextBee.

        :param messages: list of dicts ``{content, numbers: [{uuid, number}]}``
        :return: list of dicts ``{uuid, state}`` — one per recipient number
        """
        if not self._gateway_url:
            _logger.warning("everjust_sms_gateway: no gateway URL configured — messages will fail")
            return [
                {"uuid": n["uuid"], "state": "server_error"}
                for msg in messages for n in msg["numbers"]
            ]

        results = []
        headers = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        for msg in messages:
            content = msg["content"]
            for recipient in msg["numbers"]:
                uuid = recipient["uuid"]
                number = recipient["number"]
                try:
                    resp = requests.post(
                        f"{self._gateway_url}/api/messages/send",
                        json={
                            "message": content,
                            "recipients": [{"phone_number": number}],
                        },
                        headers=headers,
                        timeout=15,
                    )
                    if resp.ok:
                        results.append({"uuid": uuid, "state": "success"})
                    else:
                        _logger.warning(
                            "TextBee SMS to %s failed: %s %s",
                            number, resp.status_code, resp.text[:200],
                        )
                        results.append({"uuid": uuid, "state": "server_error"})
                except requests.RequestException as exc:
                    _logger.error("TextBee SMS to %s exception: %s", number, exc)
                    results.append({"uuid": uuid, "state": "server_error"})

        return results


class ResCompany(models.Model):
    _inherit = "res.company"

    sms_provider = fields.Selection(
        selection_add=[
            ("textbee", "Send via TextBee (self-hosted)"),
            ("ringover", "Send via Ringover"),
        ],
        ondelete={"textbee": "set default", "ringover": "set default"},
    )

    def _get_sms_api_class(self):
        """Return the TextBee SMS API class when provider is 'textbee'.

        Also auto-selects TextBee when no explicit provider is chosen but
        the gateway URL is configured, so it works out of the box.
        """
        self.ensure_one()
        if self.sms_provider == "textbee":
            return SmsApiTextBee
        # Fallback: if no provider explicitly set but gateway URL exists, use TextBee
        if not self.sms_provider or self.sms_provider == "iap":
            gateway_url = self.env["ir.config_parameter"].sudo().get_param(
                "everjust.sms_gateway_url"
            )
            if gateway_url:
                return SmsApiTextBee
        return super()._get_sms_api_class()
