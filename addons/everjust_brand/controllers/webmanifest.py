# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.webmanifest import WebManifest


class EverJustWebManifest(WebManifest):

    def _get_webmanifest(self):
        manifest = super()._get_webmanifest()
        manifest['name'] = 'EVERJUST.APP'
        manifest['short_name'] = 'EVERJUST'
        manifest['background_color'] = '#000000'
        manifest['theme_color'] = '#000000'
        manifest['icons'] = [
            {
                'src': '/everjust_brand/static/img/icon-192x192.png',
                'sizes': '192x192',
                'type': 'image/png',
            },
            {
                'src': '/everjust_brand/static/img/icon-512x512.png',
                'sizes': '512x512',
                'type': 'image/png',
            },
        ]
        return manifest

    def _icon_path(self):
        return 'everjust_brand/static/img/icon-192x192.png'
