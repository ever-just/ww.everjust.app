# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PhoneTokenController(http.Controller):
    """Generate short-lived Twilio access tokens for the Voice JS SDK.

    The browser requests a token on page load. The token authorizes the
    browser to connect to Twilio's signaling servers and make/receive calls
    through the configured TwiML App.
    """

    @http.route("/phone/token", type="jsonrpc", auth="user")
    def get_token(self):
        ICP = request.env["ir.config_parameter"].sudo()
        account_sid = ICP.get_param("everjust_phone.account_sid")
        api_key = ICP.get_param("everjust_phone.api_key")
        api_secret = ICP.get_param("everjust_phone.api_secret")
        twiml_app_sid = ICP.get_param("everjust_phone.twiml_app_sid")

        if not all([account_sid, api_key, api_secret, twiml_app_sid]):
            return {"error": "Twilio not configured. Set credentials in Settings > Phone."}

        try:
            from twilio.jwt.access_token import AccessToken
            from twilio.jwt.access_token.grants import VoiceGrant

            # Identity = Odoo user login (unique per user)
            identity = request.env.user.login.replace("@", "_at_").replace(".", "_")

            token = AccessToken(
                account_sid,
                api_key,
                api_secret,
                identity=identity,
                ttl=3600,  # 1 hour
            )

            voice_grant = VoiceGrant(
                outgoing_application_sid=twiml_app_sid,
                incoming_allow=True,
            )
            token.add_grant(voice_grant)

            return {
                "token": token.to_jwt(),
                "identity": identity,
            }
        except ImportError:
            return {"error": "twilio Python package not installed"}
        except Exception as exc:
            _logger.error("Failed to generate Twilio token: %s", exc)
            return {"error": str(exc)}
