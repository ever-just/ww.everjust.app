# -*- coding: utf-8 -*-
from . import models
from . import controllers


def _post_init_hook(env):
    """Create cron job for Ringover sync after module install."""
    model = env["ir.model"].search([("model", "=", "ringover.call")], limit=1)
    if model and not env["ir.cron"].search([("name", "=", "Ringover: Sync Calls")], limit=1):
        env["ir.cron"].create({
            "name": "Ringover: Sync Calls",
            "model_id": model.id,
            "state": "code",
            "code": "model.cron_sync_all()",
            "interval_number": 10,
            "interval_type": "minutes",
            "active": True,
            "numbercall": -1,
        })
