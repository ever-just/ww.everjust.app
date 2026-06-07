# everjust_signup (Phase 2)

In-Odoo self-service signup enhancements.

For Phase 1, signup is handled by the FastAPI control plane at `everjust.app`
(`control-plane/`), which creates the Stripe subscription and provisions the
tenant database. This module is reserved for Phase 2 work: in-app plan
upgrades, seat management UI, and a tenant self-service portal.
