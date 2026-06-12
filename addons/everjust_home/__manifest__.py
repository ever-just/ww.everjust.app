# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Home Menu",
    "version": "19.0.1.1.0",
    "summary": "App grid home screen — replaces the default Discuss landing.",
    "description": """
EVERJUST.APP Home Menu
======================
Adds a fullscreen app grid as the default landing page after login,
with one tile per installed app. Patches the WebClient so all
users see the grid instead of being dropped into the first app
(typically Discuss).

Part of the EVERJUST.APP platform.
""",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Hidden/Tools",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "everjust_home/static/src/home_menu/home_menu.js",
            "everjust_home/static/src/home_menu/home_menu.xml",
            "everjust_home/static/src/home_menu/home_menu.scss",
            "everjust_home/static/src/home_button/home_button.js",
            "everjust_home/static/src/home_button/home_button.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
