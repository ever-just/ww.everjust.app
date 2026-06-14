# -*- coding: utf-8 -*-
from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _everjust_apply_defaults(self):
        """Set EVERJUST.APP document footer defaults on every company.

        Called from data file on install so new tenant databases start
        fully branded with no upstream references in reports or emails.
        """
        for company in self.search([]):
            if not company.report_footer or "odoo" in (company.report_footer or "").lower():
                company.report_footer = "EVERJUST.APP"

    @api.model
    def _everjust_rename_apps(self):
        """Rename apps whose default names are Odoo coinages to EVERJUST's
        names, matching the marketing site (Discuss→Chat, Knowledge→Wiki,
        Sign→Signatures, eLearning→Courses).

        Defensive and idempotent: a module that isn't installed is simply
        skipped (env.ref with raise_if_not_found=False), so this can never
        break a tenant's load. Safe to re-run after new apps are installed.
        """
        renames = {
            "Chat": ["mail.menu_root_discuss"],
            "Wiki": ["knowledge.knowledge_menu_root", "knowledge.knowledge_menu_home"],
            "Signatures": ["sign.menu_sign_root", "sign.sign_request_menu", "sign.sign_menu"],
            "Courses": ["website_slides.website_slides_menu_root",
                        "website_slides.website_slides_menu_courses_all"],
        }
        for name, xmlids in renames.items():
            for xmlid in xmlids:
                menu = self.env.ref(xmlid, raise_if_not_found=False)
                if menu:
                    menu.sudo().name = name
                    break
