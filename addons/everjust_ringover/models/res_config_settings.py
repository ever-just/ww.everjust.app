# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ringover_api_key = fields.Char(
        string="Ringover API Key",
        config_parameter="everjust.ringover_api_key",
    )
    ringover_api_url = fields.Char(
        string="Ringover API URL",
        config_parameter="everjust.ringover_api_url",
        default="https://public-api-us.ringover.com/v2",
    )
    ringover_webhook_secret = fields.Char(
        string="Ringover Webhook Secret",
        config_parameter="everjust.ringover_webhook_secret",
    )
