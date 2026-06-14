# -*- coding: utf-8 -*-
{
    "name": "EverJust Appointments",
    "version": "19.0.1.0.0",
    "category": "Services",
    "summary": "Online appointment booking with calendar integration",
    "description": """
EverJust Appointments
=====================
Provides online appointment booking for all EverJust tenants.
Replaces the Enterprise-only appointment module.

Features:
- Configurable appointment types with weekly time slots
- Public booking page (no login required)
- Calendar integration — auto-creates calendar events
- Optional CRM lead creation per appointment type
- Double-booking prevention via staff calendar checks
- Email confirmation to customers
- Backend management views (tree, form, calendar)
""",
    "author": "EverJust",
    "website": "https://everjust.app",
    "license": "LGPL-3",
    "depends": ["calendar", "website", "crm", "mail", "contacts"],
    "data": [
        "security/appointment_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "data/appointment_data.xml",
        "views/appointment_type_views.xml",
        "views/appointment_booking_views.xml",
        "views/appointment_menus.xml",
        "views/appointment_website_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "everjust_appointment/static/src/css/appointment.css",
            "everjust_appointment/static/src/js/appointment.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
}
