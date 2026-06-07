# EVERJUST.APP — Master Build Plan

A self-hosted, multi-tenant SaaS platform built on a fully-debranded fork of Odoo 19 Community.

**Repo:** `ww.everjust.app`
**Base:** Odoo 19 Community (forked, debranded, themed)
**Model:** True multi-tenant SaaS — self-service org/user signup, Stripe billing, per-tenant database isolation
**Brand:** EVERJUST.APP (all caps when referred to) — zero Odoo references anywhere
**Default theme:** Black / white (users can change via marketplace)
**Pricing:** $100/mo base (up to 5 users) + $15/user beyond 5

---

## Decision: Why self-hosted Community, not Odoo.sh

| Option | Open source | Forkable | Debrandable | License-free | Verdict |
|---|---|---|---|---|---|
| Odoo Online | No | No | No | No | Rejected |
| **Odoo.sh** | **No** | No | No | Requires Enterprise sub | **Rejected** |
| **Odoo 19 Community (self-hosted)** | **Yes (LGPL-3)** | **Yes** | **Yes** | **Yes** | **Selected** |

Odoo.sh is a paid hosting product that requires an active Enterprise subscription. It cannot run Community and cannot be self-hosted. Self-hosted Community v19 is the only base that can be forked, fully rebranded, and run without license locks.

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │   *.everjust.app  (wildcard DNS)     │
                    └──────────────────┬──────────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   Nginx / Traefik         │
                          │   wildcard SSL (LE)       │
                          │   subdomain → DB routing  │
                          └────────────┬──────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                         │
     ┌────────▼────────┐    ┌──────────▼──────────┐   ┌──────────▼─────────┐
     │  CONTROL PLANE   │    │   EVERJUST (Odoo 19) │   │   PostgreSQL       │
     │  signup portal   │    │   one binary,         │   │   db: control      │
     │  Stripe billing  │    │   shared workers      │   │   db: tcsw         │
     │  provisioning    │───▶│   custom addons:      │──▶│   db: acme         │
     │  (FastAPI)       │    │   - everjust_brand    │   │   db: <tenant>     │
     └──────────────────┘    │   - everjust_theme    │   └────────────────────┘
              │              │   - everjust_signup   │
              │              └───────────────────────┘
       ┌──────▼──────┐
       │   Stripe     │
       │   webhooks   │
       └──────────────┘
```

**How a signup works:**

1. User visits `everjust.app`, picks a plan, enters org name + email
2. Control plane creates a Stripe customer + subscription ($100/mo base)
3. On payment success (Stripe webhook), control plane provisions a new Postgres DB named after the subdomain
4. Odoo initializes the DB with base modules + everjust addons + black/white theme
5. Nginx routes `<org>.everjust.app` → that DB via `dbfilter`
6. User gets a login link; they're in, fully branded as EVERJUST.APP

**Scaling path:**

- Start: 1 server (control plane + Odoo + Postgres via Docker Compose)
- Grow: split Postgres to managed DB (DigitalOcean Managed Postgres / RDS), add Odoo worker replicas
- Scale: move heavy tenants to dedicated containers (Traefik per-tenant routing)

---

## PART A — Plan (this document)

Status: complete. Architecture, debranding strategy, theming, billing, and provisioning all defined below.

---

## PART B — Build & configure the SaaS platform

### B1. Repo scaffolding (`ww.everjust.app`)

```
ww.everjust.app/
├── odoo/                      # Odoo 19 Community fork (submodule or shallow clone)
├── addons/
│   ├── everjust_brand/        # Full debranding: name, logo, favicon, titles, "powered by"
│   ├── everjust_theme/        # Black/white default theme (primary_variables.scss)
│   └── everjust_signup/       # Self-service org signup flow
├── control-plane/             # FastAPI app: signup, Stripe, provisioning
│   ├── main.py
│   ├── provisioning.py        # creates DB, inits Odoo, configures routing
│   ├── stripe_webhooks.py
│   └── requirements.txt
├── deployment/
│   ├── docker-compose.yml     # odoo + postgres + nginx + control-plane
│   ├── nginx/
│   │   └── everjust.conf      # wildcard + subdomain routing
│   ├── odoo.conf              # dbfilter = ^%d$, list_db = False
│   └── scripts/
│       ├── provision_tenant.sh
│       ├── backup_all.sh
│       └── debrand_check.sh
├── docs/                      # EVERJUST.APP docs (rebranded, no Odoo refs)
├── .env.example
└── README.md
```

### B2. Fork Odoo 19 Community

```bash
git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git odoo
```

License: LGPL-3.0 — permits forking, modification, rebranding, and commercial SaaS use. Must retain LGPL notices in the Odoo source files themselves (not user-facing).

### B3. Build `everjust_brand` (full debranding)

Every Odoo reference replaced with EVERJUST.APP. Checklist of every touchpoint:

| Touchpoint | How |
|---|---|
| Browser tab title ("Odoo") | Override `web.layout` title, set `ir.config_parameter` `web.base.title` |
| Favicon | Replace `web/static/img/favicon.ico` via theme assets + `res.company.favicon` |
| Login page "Odoo" logo | Override `web.login_layout` QWeb template |
| "Powered by Odoo" footer | Override `web.brand_promotion` / `portal.portal_back_in_edit_mode` templates → empty or EVERJUST |
| Backend top-left logo | Override `web.menu_secondary` / navbar brand asset |
| "My Odoo.com account" menu | Remove via `web.UserMenu` patch + `disable_odoo_online` approach |
| Apps store / "Odoo Apps" | Hide via menu access rules |
| Email footers ("Sent by Odoo") | Override `mail.mail_notification_*` templates |
| Document titles in PDFs/reports | Override `web.external_layout` |
| "Odoo" in page `<meta>` | Override website templates |
| Database manager page | Disabled entirely (`list_db = False`) |
| About dialog version string | Override `web.client_action` / patch `webclient` |
| Settings > "Odoo" upgrade banners | Hide Enterprise upsell via CSS + remove `web_enterprise` |

Method: a custom module that (1) overrides QWeb templates via `<template inherit_id>`, (2) sets system parameters on install, (3) injects CSS to hide residual references, (4) patches JS for the user menu / about dialog.

### B4. Hide everything under license lock

Odoo Community already excludes Enterprise code. Remaining "upgrade to Enterprise" prompts come from CTA banners and the Apps store. Remove by:

- Not installing `web_enterprise` (it's Enterprise-only anyway)
- Uninstalling/hiding `mail_bot`, `iap` (in-app-purchase prompts)
- CSS rules to hide `.o_enterprise_label`, upgrade ribbons
- Menu access rules to hide the Apps store's paid listings

Result: users never see a locked feature or an upsell.

### B5. Build `everjust_theme` (black/white default)

```scss
// addons/everjust_theme/static/src/scss/primary_variables.scss
$o-brand-primary: #000000;
$o-brand-secondary: #1a1a1a;
$o-community-color: #000000;
$o-main-text-color: #111111;
$body-bg: #ffffff;
// Navbar, buttons, accents → black on white
```

Applied as a default on every new tenant. Users can switch themes/colors later via Settings (the "marketplace" = the theme picker we expose).

### B6. Build `everjust_signup` (self-service org + user signup)

- Public signup page at `everjust.app`: org name → desired subdomain → admin email/password → plan
- Hands off to control plane for Stripe + provisioning
- Email verification + welcome email (EVERJUST-branded)

### B7. Control plane (FastAPI)

- `POST /signup` → validate subdomain availability, create Stripe customer + checkout session
- `POST /stripe/webhook` → on `checkout.session.completed` / `invoice.paid` → call `provisioning.py`
- `provisioning.py` → create DB, init Odoo (`-d <sub> --init=base,everjust_brand,everjust_theme --stop-after-init`), confirm routing
- Lifecycle: suspend on failed payment, reactivate on recovery, delete after retention

### B8. Stripe billing (via Stripe MCP)

- Product: **EVERJUST.APP**
- Price 1: $100/mo flat (includes 5 seats) — recurring monthly
- Price 2: $15/mo per additional user — metered/graduated tier beginning at seat 6
- Webhooks → control plane for provisioning + seat enforcement

### B9. Deployment

- Provision server (decision pending — see Open Decisions)
- Wildcard DNS `*.everjust.app` → server IP (GoDaddy API)
- Wildcard SSL via Let's Encrypt DNS-01 challenge
- `docker compose up` — odoo + postgres + nginx + control-plane

---

## PART C — Onboard TCSW as the first tenant

1. Provision tenant `tcsw` → database `tcsw`, reachable at `tcsw.everjust.app`
2. Migrate existing TCSW data (68 orgs, 600 speakers, 8 events, 67 CRM opps) from the current self-hosted instance into the new tenant DB
3. Apply TCSW-specific branding on top of EVERJUST base (the existing `tcsw_branding` colors) — TCSW gets its own look within EVERJUST
4. Create the TCSW admin user/org (you provide credentials, or I create and hand them over)
5. **Replace** `INFRASTRUCTURE/` in the `twincitiesstartupweek` repo: remove the self-hosted Odoo files, replace with thin MCP-based access config pointing at `tcsw.everjust.app`

After this, the TCSW repo no longer hosts infrastructure — it just connects to the TCSW instance on the EVERJUST.APP platform.

---

## Decisions (resolved)

1. **Hosting** — New AWS EC2 (separate from the existing TCSW EC2).
2. **Stripe mode** — Live mode. Product + tiered price created in the live account.
3. **GitHub repo** — Scaffold `ww.everjust.app` locally, then push to a new GitHub repo.
4. **Domains** — Platform/signup at `everjust.app` (root); tenants at `*.everjust.app`; TCSW at `tcsw.everjust.app`. Wildcard DNS via GoDaddy, wildcard SSL via Let's Encrypt DNS-01.

---

## Reality check on scope

A production multi-tenant SaaS with automated provisioning and billing is a multi-week build (industry estimate: 3–6 months for full automation). Recommended sequencing:

- **Phase 1 (now):** Plan + Stripe products + fork + debrand + theme + single-tenant deploy with TCSW. Manual tenant provisioning.
- **Phase 2:** Self-service signup + automated provisioning + Stripe webhooks.
- **Phase 3:** Lifecycle automation, scaling, monitoring, backups, tenant self-service portal.

This gets TCSW live on the rebranded EVERJUST.APP platform fast, then layers in full self-service SaaS.
