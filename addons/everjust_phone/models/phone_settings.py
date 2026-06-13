# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    twilio_account_sid = fields.Char(
        string="Twilio Account SID",
        config_parameter="everjust_phone.account_sid",
    )
    twilio_auth_token = fields.Char(
        string="Twilio Auth Token",
        config_parameter="everjust_phone.auth_token",
    )
    twilio_api_key = fields.Char(
        string="Twilio API Key SID",
        config_parameter="everjust_phone.api_key",
    )
    twilio_api_secret = fields.Char(
        string="Twilio API Secret",
        config_parameter="everjust_phone.api_secret",
    )
    twilio_twiml_app_sid = fields.Char(
        string="TwiML App SID",
        config_parameter="everjust_phone.twiml_app_sid",
    )
    twilio_phone_number = fields.Char(
        string="Twilio Phone Number",
        config_parameter="everjust_phone.phone_number",
        help="Your Twilio number in E.164 format, e.g. +19525551234",
    )
