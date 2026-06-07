# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Inject EVERJUST.APP branding into the web client session.

        The web client reads ``server_version`` and various branding strings
        from session_info on boot. Overriding here ensures the browser title
        and about dialog never expose the upstream product name.
        """
        result = super().session_info()
        result["server_version"] = "EVERJUST.APP"
        result["server_version_info"] = [19, 0, 0, "final", 0, ""]
        return result
