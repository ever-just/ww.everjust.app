# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP SMS Gateway",
    "version": "19.0.1.0.0",
    "summary": "Route SMS through TextBee instead of Odoo IAP — zero per-message cost.",
    "description": """
EVERJUST.APP SMS Gateway
========================
Replaces Odoo's default IAP-based SMS sending with a self-hosted TextBee
gateway. All existing SMS features continue to work (composer, templates,
phone field buttons, chatter threading, CRM/Sales/Events bridges, SMS
Marketing) — only the transport layer changes.

Also adds a webhook controller for receiving inbound SMS.
""",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Hidden/Tools",
    "depends": ["sms"],
    "data": [
        "data/config_params.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
