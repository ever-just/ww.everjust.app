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
