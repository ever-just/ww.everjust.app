# -*- coding: utf-8 -*-
{
    "name": "EVERJUST.APP Phone",
    "version": "19.0.1.0.0",
    "summary": "Embedded phone system — calls, SMS, recordings via Twilio Voice SDK.",
    "author": "EVERJUST",
    "website": "https://everjust.app",
    "category": "Productivity/Phone",
    "depends": ["mail", "contacts", "crm", "sms", "phone_validation"],
    "external_dependencies": {"python": ["twilio"]},
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/config.xml",
        "views/phone_call_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "everjust_phone/static/src/services/phone_service.js",
            "everjust_phone/static/src/components/phone/phone.js",
            "everjust_phone/static/src/components/phone/phone.xml",
            "everjust_phone/static/src/components/phone/phone.scss",
            "everjust_phone/static/src/widgets/phone_field.js",
            "everjust_phone/static/src/widgets/phone_field.xml",
        ],
        "everjust_phone.twilio_assets": [
            "everjust_phone/static/lib/twilio.min.js",
        ],
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
