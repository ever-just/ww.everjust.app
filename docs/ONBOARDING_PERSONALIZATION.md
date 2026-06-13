# Onboarding & Workspace Personalization

**Goal:** the new-user experience captures real context and uses it to hand
the customer a workspace already shaped for *their* business — the right apps
switched on, their branding applied, sensible defaults set — instead of an
empty shell.

## What we capture (at signup)

| Field | Use |
|---|---|
| **Industry** | Maps to a default app/module set + sample config. |
| **Company website** (optional) | Enrichment source: name, logo, colors, what they do, contact. |
| **Team size** | Seat expectations, which HR/approval features to enable. |
| **Primary goals** ("what do you want to run first?") | Multi-select of app areas → drives which apps install first. |

All optional/skippable — we never block checkout with a survey (CRO: no
friction before payment). Captured pre-payment so provisioning has it
synchronously.

## Pipeline

```
Signup (capture) ──► signup_store (token) ──► Stripe ──► webhook
                                                           │
                                       provision base tenant (always)
                                                           │
                                   personalize(industry, website, goals)
                                       ├─ enrich(website)   [Stage 2]
                                       ├─ install mapped modules
                                       ├─ apply branding (name/logo/colors)
                                       └─ seed sensible defaults
```

## Industry → modules (starter map)

- **Professional services / agency:** CRM, Sales, Invoicing, Projects, Timesheets
- **Retail / eCommerce:** Website, eCommerce, Inventory, POS, Invoicing
- **Software / tech:** CRM, Projects, Timesheets, Knowledge, Invoicing
- **Manufacturing:** Inventory, Purchase, Manufacturing, Sales, Invoicing
- **Hospitality / food:** POS, Inventory, Purchase, HR
- **Construction / trades:** Projects, Inventory, Purchase, Invoicing, Fleet
- **Default:** CRM, Sales, Invoicing, Contacts, Calendar

Goals refine the set (e.g. "Marketing" adds Email Marketing/Events).

## Website enrichment (Stage 2)

Fetch the homepage and extract: company name (`og:site_name`/`<title>`),
description (`meta description`/`og:description`), logo (`og:image`/favicon/
`<link rel=icon>`), theme color (`theme-color`, dominant brand color), and
contact (mailto/tel). Optionally a deeper multi-page/deep-research pass for
richer copy and structure.

### Security (non-negotiable — SSRF protection)
The website URL is attacker-controllable, so the fetcher must:
- Accept only `http(s)://`, public hostnames.
- Resolve DNS and **reject private/loopback/link-local ranges** (10/8,
  172.16/12, 192.168/16, 127/8, 169.254/16, ::1, fc00::/7, metadata IPs).
- Cap redirects, timeout, and response size; strip on failure (best-effort,
  never blocks provisioning).

## Applying branding to the tenant

Through the ORM during provisioning: set `res.company` name, email, phone,
website, and logo (downloaded, validated image); set theme colors via the
existing `everjust_theme` parameters where applicable. All best-effort and
reversible by the admin.

## Build stages (each a tested PR)

1. **Capture (this PR):** premium multi-step signup collects industry,
   website, team size, goals; stored in `signup_store`; carried into
   `provision_tenant` (recorded, not yet acted on). Zero new network surface.
2. **Module mapping:** provisioning installs the industry/goal app set.
3. **Website enrichment + branding:** the SSRF-safe fetcher + applying
   name/logo/colors.
4. **Deep research (optional):** richer enrichment for copy/structure.

## Why pre-payment capture

Keeps provisioning synchronous and robust (all inputs known at webhook time),
avoids an async post-provision config dance, and the questions double as a
commitment/《investment》 step that *increases* completion when framed as
"we'll set this up for you."
