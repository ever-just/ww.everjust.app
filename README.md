# EVERJUST.APP

A self-hosted, multi-tenant SaaS platform. Organizations sign up, pay, and get an isolated workspace at `<org>.everjust.app` — fully branded as EVERJUST.APP with zero upstream references.

Built on a debranded Odoo 19 Community base, extended through modules (not a core fork) so it stays upgradeable.

## How it works

- **Platform + signup:** `everjust.app` (the control plane)
- **Tenants:** `<org>.everjust.app`, each backed by its own isolated PostgreSQL database
- **Routing:** Nginx + Odoo `dbfilter` map each subdomain to its database
- **Billing:** Stripe — $100/mo base (up to 5 users) + $15/user beyond
- **Branding:** every upstream reference replaced with EVERJUST.APP; default theme is black & white

## Architecture

```
*.everjust.app  →  Nginx (wildcard SSL)  →  ┌─ everjust.app      → control-plane (signup, Stripe)
                                            └─ <org>.everjust.app → Odoo 19 (dbfilter → DB <org>)
                                                                         │
                                                              PostgreSQL: one DB per tenant
```

## Repo layout

```
ww.everjust.app/
├── addons/
│   ├── everjust_brand/     Full debranding (auto-installed on every tenant)
│   ├── everjust_theme/     Black & white default theme
│   └── everjust_signup/    Self-service org signup (Phase 2)
├── control-plane/          FastAPI: signup page, Stripe checkout, webhooks, provisioning
├── deployment/
│   ├── docker-compose.yml  odoo 19 + postgres 16 + nginx + control-plane
│   ├── odoo.conf           dbfilter = ^%d$, list_db = False
│   ├── nginx/everjust.conf wildcard + subdomain routing
│   └── scripts/            provision_tenant, backup_all, debrand_check
├── docs/                   EVERJUST.APP documentation
├── MASTER_PLAN.md          Full build plan (A: plan, B: build, C: TCSW onboarding)
└── .env.example
```

## Why modules, not a core fork

Debranding and theming are done entirely through add-on modules layered on the official `odoo:19` image. This keeps the platform fully customizable while remaining upgradeable — no 1 GB core fork to maintain. If deep core changes are ever needed, we fork at that point.

## Branding coverage

`everjust_brand` is `auto_install` and replaces every touchpoint:

- Browser tab title and favicon
- Login page (EVERJUST.APP wordmark, upstream logo removed)
- "Powered by" footers (backend, portal, reports, email)
- User menu external links (account, docs, support) removed
- Enterprise upgrade banners and upsell prompts hidden
- Database manager UI disabled (`list_db = False`)

Run `deployment/scripts/debrand_check.sh <tenant>` to scan a live tenant for leaks.

## Stripe

- Product: `EVERJUST.APP` (`prod_Uf5UgyXUPN8UpT`)
- Price: graduated tiered (`price_1TflJNKL0p3ve1jHbCLlDNWS`) — first 5 seats $100 flat, $15/seat after
- Live mode

## Deployment

See `MASTER_PLAN.md` for the full sequence. Quick version:

```bash
cp .env.example .env          # fill in secrets
cd deployment
docker compose up -d
# provision a tenant
./scripts/provision_tenant.sh acme admin@acme.com 'strong-pass'
```

## CI/CD

Automated via GitHub Actions. Every push to `master` triggers a production deploy.

**Pipeline:** `.github/workflows/deploy.yml`

```
push to master → GitHub Actions → SSH into EC2 → git pull → rebuild control-plane → restart compose → health check
```

**Security hardening:**

| Measure | Detail |
|---|---|
| Action pinned to SHA | `appleboy/ssh-action@0ff420...` prevents tag-hijack supply-chain attacks |
| Minimal workflow permissions | `permissions: {}` — no GitHub token access granted |
| Environment-scoped secrets | `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` live on the `production` environment, not repo-level |
| Branch-restricted environment | `production` environment only allows deploys from `master` |
| Concurrency guard | Only one deploy runs at a time; queued pushes wait |
| Health check | Post-deploy verification that the control-plane responds 200 |

**Required GitHub secrets** (set on the `production` environment):

| Secret | Value |
|---|---|
| `DEPLOY_HOST` | EC2 public IP |
| `DEPLOY_USER` | `ubuntu` |
| `DEPLOY_SSH_KEY` | Contents of the EC2 SSH private key (PEM) |

**Server prerequisites:**

- Repo cloned at `/opt/everjust/platform`
- Docker and Docker Compose installed
- SSH user has passwordless `sudo`
- `.env` populated with runtime secrets (Stripe, Postgres, Resend, etc.)

## Status

- [x] Plan, architecture, Stripe products
- [x] Debranding + theme modules
- [x] Deployment config (compose, nginx, odoo.conf)
- [x] Control plane (signup, Stripe, provisioning)
- [x] AWS EC2 + wildcard DNS + SSL
- [x] First tenant: TCSW (`tcsw.everjust.app`)
- [x] CI/CD pipeline (GitHub Actions → EC2)
- [ ] Self-service signup automation (Phase 2)
