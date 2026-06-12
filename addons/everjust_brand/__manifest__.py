# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Branding",
    "version": "19.0.1.2.0",
    "summary": "Full white-label rebrand to EVERJUST.APP. Removes all upstream branding.",
    "description": """
EVERJUST.APP Branding
=====================
Replaces every upstream branding touchpoint with EVERJUST.APP:
- Browser tab title and favicon
- Login page logo and text
- "Powered by" footers (backend, portal, website, email)
- Document/report headers and footers
- User menu external links (account, documentation, support)
- Enterprise upgrade banners and upsell prompts (hidden)
""",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Theme",
    "depends": ["web", "mail"],
    "data": [
        "data/branding_params.xml",
        "views/login_templates.xml",
        "views/brand_templates.xml",
        "views/report_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "everjust_brand/static/src/scss/debrand.scss",
            "everjust_brand/static/src/js/debrand.js",
        ],
        "web.assets_frontend": [
            "everjust_brand/static/src/scss/debrand.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
