# -*- coding: utf-8 -*-
import base64
from odoo import api, models
from odoo.tools import file_open


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _everjust_apply_defaults(self):
        """Set EVERJUST.APP document footer defaults on every company.

        Called from data file on install so new tenant databases start
        fully branded with no upstream references in reports or emails.
        """
        favicon_b64 = None
        try:
            with file_open('everjust_brand/static/img/favicon.ico', 'rb') as f:
                favicon_b64 = base64.b64encode(f.read())
        except Exception:
            pass

        for company in self.search([]):
            if not company.report_footer or "odoo" in (company.report_footer or "").lower():
                company.report_footer = "EVERJUST.APP"
            if favicon_b64:
                company.favicon = favicon_b64
