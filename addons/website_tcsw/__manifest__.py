# -*- coding: utf-8 -*-
{
    "name": "TCSW Premium Theme",
    "version": "19.0.1.0.0",
    "summary": "Premium design layer for the Twin Cities Startup Week website and event microsite.",
    "description": """
TCSW Premium Theme
==================
A design system layered on top of the EVERJUST platform for the Twin Cities
Startup Week tenant only:
- Typography: Space Grotesk (display) + Inter (body), loaded from Google Fonts
- Type scale, weights, and tracking tuned for a premium editorial feel
- Pill buttons, card shadow system, section rhythm, sticky CTAs
- Hero, duotone imagery, stat bands, and helper classes used by the pages
This module injects styles only. It does not replace the active website theme.
""",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Theme",
    "depends": ["website", "website_event"],
    "data": [
        "views/fonts.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "website_tcsw/static/src/scss/primary_variables.scss",
        ],
        "web.assets_frontend": [
            "website_tcsw/static/src/scss/theme.scss",
            "website_tcsw/static/src/js/tcsw_frontend.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
