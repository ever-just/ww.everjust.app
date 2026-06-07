# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Theme",
    "version": "19.0.1.0.0",
    "summary": "Black & white default theme for EVERJUST.APP. Users can change colors in Settings.",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Theme",
    "depends": ["web"],
    "assets": {
        # Primary variables must load into the SCSS variable bundle so they
        # override the upstream palette before compilation.
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "everjust_theme/static/src/scss/primary_variables.scss",
            ),
        ],
        "web.assets_backend": [
            "everjust_theme/static/src/scss/theme.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
