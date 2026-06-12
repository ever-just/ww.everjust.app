# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Ringover Integration",
    "version": "19.0.1.0.0",
    "summary": "Native Ringover integration — call logging, SMS, recordings synced to Odoo.",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Productivity/VOIP",
    "depends": ["mail", "contacts", "voip_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "views/res_config_settings_views.xml",
        "views/ringover_call_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
