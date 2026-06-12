# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Ringover Integration",
    "version": "19.0.1.0.0",
    "summary": "Native Ringover integration — call logging, SMS, recordings synced to Odoo.",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Productivity/VOIP",
    "depends": ["mail", "contacts", "crm", "voip_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "views/res_config_settings_views.xml",
        "views/ringover_call_views.xml",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "everjust_ringover/static/src/ringover_agent_patch.esm.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "_post_init_hook",
    "license": "LGPL-3",
}
