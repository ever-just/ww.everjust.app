# EVERJUST.APP — Agent Context Guide

This file is for AI agents (Claude, Cascade/Windsurf, Devin, etc.) working in this repo.
It tells you what this project is, where things live, and how to access infrastructure.

**Do not store real secrets here. All actual credentials live in `.env` (gitignored) or in the private HEADSUP repo.**

---

## What This Project Is

EVERJUST.APP is a self-hosted, multi-tenant SaaS built on a fully debranded fork of **Odoo 19 Community** (LGPL-3).
- Each tenant gets their own isolated Postgres database
- Custom addons in `addons/` handle branding, signup, and theming
- Control plane (`control-plane/`) handles tenant provisioning, Stripe billing, DNS automation
- Deployment is Docker Compose on AWS EC2

---

## Repository Layout

```
ww.everjust.app/
├── addons/
│   ├── everjust_brand/          # Debrand: removes all Odoo references (auto_install)
│   ├── everjust_home/           # App grid home screen replacing Discuss default (auto_install)
│   ├── everjust_phone/          # Embedded Twilio softphone — calls, SMS, recordings (WebRTC)
│   ├── everjust_ringover/       # Ringover API integration — call sync, webhook, CRM link
│   ├── everjust_sms_gateway/    # SMS routing: TextBee / Twilio / Ringover (auto_install)
│   ├── everjust_signup/         # Self-service tenant signup flow (Phase 2)
│   ├── everjust_theme/          # Default black/white UI theme
│   ├── voip_oca/                # OCA SIP softphone (for non-Twilio PBX setups)
│   ├── dms/                     # Document Management System (ported from OCA 18→19)
│   ├── document_knowledge/      # OCA knowledge base framework
│   ├── document_page/           # OCA wiki-style document pages
│   ├── document_page_partner/   # Link wiki pages to contacts
│   ├── document_url/            # URL-based document references
│   ├── attachment_zipped_download/ # Download attachments as ZIP
│   └── website_tcsw/            # TCSW tenant-specific branding
├── control-plane/               # FastAPI provisioning service
│   ├── main.py                  # Landing page, signup, Stripe, welcome page
│   └── provisioning.py          # Tenant DB creation, module install, DNS, mail, branding
├── deployment/
│   ├── docker-compose.yml       # Odoo 19 + Postgres 16 + Nginx + control-plane
│   ├── odoo.conf                # dbfilter = ^%d$, list_db = False, 6 workers
│   ├── nginx/everjust.conf      # Wildcard SSL + subdomain routing
│   └── scripts/                 # provision_tenant, backup_all, debrand_check
├── .github/workflows/
│   └── deploy.yml               # CI/CD: push to master → SSH → pull → rebuild → restart
├── docs/
│   ├── TELEPHONY_PLAN.md        # Phone system architecture + Enterprise parity map
│   ├── TWILIO_EMBEDDED_PLAN.md  # Twilio Voice SDK implementation plan
│   └── DMS_PORT_PLAN.md         # Document management port plan (18→19)
├── .env.example
├── MASTER_PLAN.md               # Full architecture and product plan — READ THIS FIRST
└── CLAUDE.md                    # This file
```

---

## Custom Modules Summary

| Module | Auto-install | What it does |
|---|---|---|
| `everjust_brand` | Yes | Full debranding — tab title, favicon, login, footers, user menu |
| `everjust_home` | Yes | App grid home screen + navbar home button |
| `everjust_phone` | No | Embedded Twilio softphone (WebRTC calls, SMS, recordings) |
| `everjust_ringover` | No | Ringover API sync (calls, recordings → chatter, cron every 10min) |
| `everjust_sms_gateway` | Yes | SMS routing override: TextBee/Ringover/Twilio providers |
| `voip_oca` | No | OCA SIP.js softphone (for FusionPBX/Ringover SIP setups) |
| `dms` | No | File management: folders, upload, RBAC, tags, portal sharing |
| `document_page` | No | Wiki articles, categories, version history |

## CI/CD

Push to `master` → GitHub Actions → SSH into EC2 → git pull → rebuild control-plane → restart Odoo → health check. Secrets scoped to `production` environment. Action pinned to commit SHA.

## Active Tenants

| Tenant | URL |
|---|---|
| HeadsUp | `headsup.everjust.app` |
| TCSW | `tcstartupweek.everjust.app` |

## SSH Access

Direct SSH may be blocked by fail2ban after rapid sessions. Use EC2 Instance Connect Endpoint as fallback:
```bash
ssh -o ProxyCommand='aws ec2-instance-connect open-tunnel --instance-id i-04e066c8b55698c81 --region us-east-1' ubuntu@i-04e066c8b55698c81
```

## Odoo 19 Gotchas

- `type='json'` in controllers → use `type='jsonrpc'` or `type='http'`
- `groups_id` → `group_ids`, `users` → `user_ids` on `res.groups`
- `category_id` → `privilege_id` with new `res.groups.privilege` model
- `expand="0"` and `string="Group By"` removed from search `<group>` elements
- `t-if` forbidden in form views → use `invisible` attribute
- `_sql_constraints` deprecated → use `models.Constraint`
- `web_editor` renamed to `html_builder`
- `external_dependencies: {"python": [...]}` blocks install if package missing — use lazy imports
- `docker compose run --rm` pip installs don't persist — add to docker-compose command

---

## Production Server Access

> **Real credentials are NOT stored here.** See the private `HEADSUP` repo for full details.
> GitHub: `https://github.com/ever-just/HEADSUP` (private — requires access)

| Field | Value |
|---|---|
| Provider | AWS EC2 |
| Instance name | everjust-app |
| Public IP | 18.209.206.116 |
| SSH user | ubuntu |
| Key pair | odoo-tcsw-key |
| Key file location | `~/.ssh/odoo-tcsw-key.pem` (local only, never in any repo) |
| Region | us-east-1d |
| Instance type | t3.large |

```bash
# SSH to production
ssh -i ~/.ssh/odoo-tcsw-key.pem ubuntu@18.209.206.116
```

**If the `.pem` file is missing locally:** it cannot be re-downloaded from AWS. A new key pair must be created and the instance updated. Ask the repo owner.

---

## Running Locally (Dev)

```bash
# 1. Set up env
cp .env.example deployment/.env
# Edit deployment/.env with local values (simple passwords, localhost DB)

# 2. Start Odoo + Postgres
cd deployment
docker compose up -d db odoo

# Odoo UI: http://localhost:8069
# First run: create a DB at http://localhost:8069/web/database/manager
```

---

## MCP — Connecting AI Agents to Odoo Directly

The Windsurf/Cascade MCP config lives at `~/.codeium/windsurf/mcp_config.json`.

To connect Cascade to the **local** Odoo instance, add this to that file:

```json
{
  "mcpServers": {
    "odoo-local": {
      "command": "uvx",
      "args": ["mcp-odoo"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "everjust",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "<your_local_admin_password>"
      }
    }
  }
}
```

To connect to **production** Odoo, use `ODOO_URL: https://everjust.app` instead.
Full MCP config files (without passwords) are in the `HEADSUP` repo at `mcp/`.

> Install `uv` first if needed: `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## Key Env Variables (Reference Only)

See `.env.example` for the full list. Real values are in `deployment/.env` (gitignored).

| Variable | Purpose |
|---|---|
| `POSTGRES_USER/PASSWORD/DB` | Postgres credentials |
| `ODOO_MASTER_PASSWORD` | Odoo database manager master password |
| `STRIPE_SECRET_KEY` | Stripe live secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `RESEND_API_KEY` | Transactional email via Resend |
| `GODADDY_API_KEY/SECRET` | DNS automation for tenant subdomains |
| `CONTROL_PLANE_SECRET` | FastAPI session secret |

---

## Important Notes for Agents

- **Never commit `.env`** — it is gitignored. Never write real credentials into any tracked file.
- **Never commit `.pem` files** — SSH keys are gitignored.
- Read `MASTER_PLAN.md` before making architectural decisions.
- The Odoo version is **19.0 Community (LGPL-3)** — not Enterprise. No Odoo.sh, no license fees.
- All tenants share one Odoo binary but have isolated Postgres databases.
- Custom modules go in `addons/` and must be LGPL-3 compatible.
- The `control-plane/` is a FastAPI service, not part of Odoo.

---

## Marketing site / control-plane frontend (conventions)

The `control-plane/` FastAPI app also renders the public marketing pages (landing,
app catalog, per-app pages, `/pricing`, `/docs`) with Jinja2 + a self-hosted design
system. When working on those pages, follow these conventions:

- **Run the checks:**
  ```bash
  cd control-plane && python3 -m pytest tests/test_app.py -q   # conftest sets dummy env
  bash deployment/scripts/branding_lint.sh                     # fails on user-facing "Odoo"
  cd control-plane && python3 scripts/build_sprite.py          # after adding an icon to ICONS
  cd control-plane && python3 scripts/build_og_image.py && python3 scripts/build_app_og_images.py
  ```
- **Content is data-driven.** Add/edit apps in `content.py` (`APPS`, `APP_DEPTH`,
  `CATEGORIES`), not by hand-writing per-app templates. `apps/detail.html` renders
  from the data; every app gets the same depth (features + workflow + diagram).
- **Brand voice** lives in `docs/BRAND_VOICE.md` — plainspoken operator, no AI/buzzword
  filler, every claim literally true. Apply it to all copy.
- **Visuals are diagrams + icons, not images.** The product is debranded, so we don't
  ship product screenshots. On-page "visuals" are CSS/SVG (spec strips, the connected-
  workspace diagram, step-flows, the price table). Real raster images are **social-share
  cards only** (`static/img/og/*.jpg`), surfaced via per-page `og:image`.
- **`og:image`:** override the `og_image` block per page; `twitter:image` follows it via
  `self.og_image()` — never hardcode the two separately.
- **Asset versioning + PWA freshness:** static URLs get `?v={{ asset_v }}`; the service
  worker (`static/sw.js`) is stale-while-revalidate with a `controllerchange` auto-reload,
  so deploys go live without manual cache clearing. Bump the SW cache name when editing it.
- **Docs vs Apps:** `/apps` is the catalog (what each app does); `/docs` is the help center
  (in-depth guides + account topics). Keep them separate — don't re-list the catalog in docs.
- **Security:** the OpenAI key used by the OG-card scripts lives **outside the repo**
  (`~/.everjust_openai.key`) and is never committed. `website_enrichment.py` fetches
  customer-supplied URLs and is **SSRF-guarded** — keep that guard intact.
- **CI:** `pull_request` events are unreliable here; the CI workflow also has a
  `workflow_dispatch` trigger — dispatch it manually and poll the run for status.

### Reusable techniques → `ever-just/agentskills`

Patterns from this repo are extracted as standalone Claude Code skills in
`ever-just/agentskills`: headless visual verification, OG-card generation, SSRF-safe
fetch, PWA deploy freshness, debrand lint, inline SVG icon sprite, CSS diagrams without
images, and anti-AI-tell web copy. Reach for those when a task matches.
