# -*- coding: utf-8 -*-
{
    "name": "HeadsUp Website Theme",
    "version": "19.0.1.1.0",
    "category": "Website/Theme",
    "summary": "Custom website theme for Heads Up Outdoor Services",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "license": "LGPL-3",
    "depends": ["website", "website_crm", "website_blog"],
    "data": [
        "views/website_templates.xml",
        "views/snippets.xml",
        "data/menu.xml",
        "data/pages/home.xml",
        "data/pages/services.xml",
        "data/pages/about.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            ("prepend", "website_headsup/static/src/scss/primary_variables.scss"),
        ],
        "web.assets_frontend": [
            "website_headsup/static/src/scss/theme.scss",
            "website_headsup/static/src/js/theme.js",
        ],
    },
    "application": False,
}
