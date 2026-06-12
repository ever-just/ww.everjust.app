# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP SMS Gateway",
    "version": "19.0.1.2.0",
    "summary": "Route SMS through TextBee — zero per-message cost.",
    "description": """
EVERJUST.APP SMS Gateway
========================
Replaces the default metered SMS sending with a self-hosted TextBee
gateway. All existing SMS features continue to work (composer, templates,
phone field buttons, chatter threading, CRM/Sales/Events bridges, SMS
Marketing) — only the transport layer changes.

Also adds a webhook controller for receiving inbound SMS.
""",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Hidden/Tools",
    "depends": ["sms", "sms_twilio", "voip_oca", "base_setup"],
    "data": [
        "data/config_params.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
