# Phase 3: Alternative ERP Architectures Research

> Research date: 2026-06-14
> Context: Evaluating whether to build a proprietary ERP platform vs. continuing with the Odoo 19 Community (LGPL-3) fork

---

## 1. ERPNext / Frappe Framework Deep Dive

### Architecture

ERPNext is built on the **Frappe Framework**, a full-stack Python web framework purpose-built for business applications. The architecture centers on **DocTypes** -- metadata definitions that simultaneously describe:

- A database table (auto-created)
- A form UI (auto-generated in browser)
- A Python controller class (inherits from `frappe.model.document.Document`)
- REST/RPC API endpoints (auto-generated)
- Permissions (role-based, defined in the DocType JSON)

Each DocType lives in its own folder containing:
```
doctype_name/
  doctype_name.json   # Schema: fields, permissions, naming
  doctype_name.py     # Server controller (validate, on_submit, etc.)
  doctype_name.js     # Client-side logic
  test_doctype_name.py
```

**Controller inheritance hierarchy** eliminates code duplication across modules:
```
Document
  -> StatusUpdater (state machine transitions)
     -> TransactionBase (posting time, fiscal year validation)
        -> AccountsController (tax, multi-currency, GL)
           -> StockController (inventory ledger, warehouse)
              -> BuyingController (Purchase Order, Purchase Invoice)
              -> SellingController (Sales Order, Sales Invoice)
```

**Three parallel ledger systems** ensure consistency:
| Ledger | Purpose | Trigger |
|--------|---------|---------|
| General Ledger (GL Entry) | Financial accounting | Invoice/Payment submission |
| Stock Ledger (SLE) | Inventory movement | Stock Entry/Delivery Note |
| Payment Ledger | Outstanding tracking | Payment Entry |

**Tech stack:** Python 3 + MariaDB/PostgreSQL + Redis + Jinja2 + Gunicorn + WebSockets. Frontend is custom JS (not React/Vue).

### Extensibility

- **hooks.py** -- inject logic at document lifecycle stages without modifying core:
  ```python
  doc_events = {"Sales Order": {"validate": "myapp.custom.validate_so"}}
  ```
- **Custom DocTypes** -- create new data models via UI or code
- **Regional overrides** -- `@erpnext.allow_regional` decorator for country-specific behavior
- **Client scripts** -- per-DocType JS for form customization
- **Patches system** -- managed migrations via `patches.txt`

### Licensing

- **Frappe Framework:** MIT license (permissive)
- **ERPNext application:** GPL v3 (copyleft -- derivative works must be GPL)
- **New Frappe apps (post-2024):** Released under AGPL v3

This means: you can build proprietary apps ON the Frappe Framework (MIT), but if you fork ERPNext itself, your fork must remain GPL. This is a more restrictive copyleft than Odoo's LGPL-3.

### Codebase Comparison

| Metric | ERPNext | Odoo Community |
|--------|---------|---------------|
| Primary language | Python | Python |
| Frontend | Custom JS | Custom JS (OWL framework) |
| Database | MariaDB/Postgres | PostgreSQL |
| Module count | ~20 core modules | ~30 core + thousands of OCA |
| Architecture | Monolithic, single repo | Modular addons |
| Licensing | GPL v3 (stricter) | LGPL v3 (more permissive) |
| Community modules | 300+ | 40,000+ on apps.odoo.com |
| Hosted pricing | ~$10/user/mo | ~$25/user/mo (Enterprise) |

### Assessment for EverJust

**Pros:** Cleaner architecture than Odoo. DocType model is elegant. MIT-licensed framework means you could build proprietary apps on Frappe without the ERP. Controller inheritance pattern is well-designed.

**Cons:** GPL v3 on ERPNext is MORE restrictive than Odoo's LGPL-3. Smaller ecosystem (300 modules vs. 40,000). Less mature UI. Would still be building on someone else's framework. No significant advantage over current Odoo approach for multi-tenant SaaS.

---

## 2. Headless ERP Approaches

### The Concept

Headless ERP decouples business logic from the presentation layer. The backend exposes APIs (REST/GraphQL) for all ERP operations, and you build custom frontends independently. This addresses a core pain point: ERP UIs are notoriously rigid.

### Traditional vs. Headless

| Aspect | Traditional ERP | Headless ERP |
|--------|----------------|-------------|
| UI | Server-rendered, one-size-fits-all | Custom per user role |
| Integration | Batch-based, 24hr lag | Real-time, API-driven |
| Page load | 1.5-4 seconds | 100-300ms (after initial) |
| Upgrades | Break customizations | Frontend/backend upgrade independently |
| Initial cost | Lower | 20-40% higher |
| 18-month TCO | Higher (re-customization) | 15-25% lower |

### Implementation Pattern

```
[React/Next.js Frontend(s)]
         |
    [BFF Layer - auth, caching, aggregation]
         |
    [ERP API Layer - business operations]
         |
    [PostgreSQL + Redis]
```

### Candidate Base Frameworks

**Directus** (most promising for ERP-like use):
- Wraps any existing SQL database with instant REST + GraphQL APIs
- Auto-generates admin UI from database schema
- Extension system for custom endpoints, hooks, interfaces
- 34.5k GitHub stars, used by Tripadvisor, Adobe
- Native MCP server (v11.13+) for AI tool integration
- Collaborative editing with live presence (v11.15+)
- **License:** GPL v3 for self-hosted, BSL for cloud
- **Verdict:** Best "headless backend" option. Could serve as the API layer if building a custom ERP, but you'd still need to write all the business logic (accounting, inventory, etc.)

**Payload CMS (v3/v4):**
- Next.js-native, TypeScript-first
- Rich hook system: beforeOperation, beforeValidate, beforeChange, afterChange, etc.
- Plugin ecosystem growing (analytics, soft delete, audit fields)
- v4.0.0-beta.0 released April 2026
- **License:** MIT
- **Verdict:** Great for content-heavy apps, but no ERP domain logic. Would be starting from zero on accounting/inventory/HR.

**Strapi:**
- Content-type builder (similar concept to DocTypes)
- Plugin marketplace
- REST + GraphQL out of the box
- **License:** MIT (community), proprietary (enterprise)
- **Verdict:** Same gap as Payload -- CMS-first, not ERP-first.

### Assessment for EverJust

A headless approach using Directus or Payload as the base would give you full UI control and modern developer experience, but you'd need to build ALL ERP domain logic from scratch: double-entry accounting, inventory valuation, tax engines, payroll calculations. This is 2-5 years of work for a small team. The CMS frameworks provide data modeling and APIs but zero business logic.

---

## 3. Modern Full-Stack ERP Alternatives

### Tryton

- **Origin:** Fork of TinyERP (same ancestor as Odoo, split in 2008)
- **Language:** Python
- **Database:** PostgreSQL, SQLite
- **License:** GPL v3
- **Architecture:** Clean, Pythonic, modular. Emphasizes correctness over features.
- **Modules:** 300+ community modules covering accounting, sales, purchase, inventory, manufacturing
- **Community:** Small but dedicated. Strong European localization.
- **Strengths:** Excellent module isolation. Strong accounting fundamentals. Well-tested codebase.
- **Weaknesses:** Small ecosystem. No native CRM or marketing. Limited UI polish. Tiny community means slow feature development.
- **Assessment:** Clean base for a custom build, but the small community is a risk. If you're going to fork something, Tryton's cleaner code is appealing, but you'd have even less ecosystem support than Odoo.

### iDempiere

- **Origin:** Compiere -> ADempiere -> iDempiere (lineage dates to 1999)
- **Language:** Java (Eclipse RCP / ZK Web)
- **Database:** PostgreSQL, Oracle
- **License:** GPL v2
- **Architecture:** "Application Dictionary" -- metadata-driven like Frappe's DocTypes but in Java
- **Strengths:** Enterprise-grade multi-company, multi-currency, multi-org. Extremely configurable.
- **Weaknesses:** Dated UI. Steep learning curve. Java ecosystem is heavy. GPL v2 (copyleft).
- **Assessment:** Too enterprise/legacy for a modern SaaS play. The Java stack would make it hard to attract developers.

### Dolibarr

- **Language:** PHP + MySQL/MariaDB/PostgreSQL
- **License:** GPL v3
- **Modules:** 1,000+ community modules, 5,500+ GitHub stars
- **Strengths:** Dead simple to install. Runs on basic PHP hosting. Low resource requirements. Good for micro-businesses.
- **Weaknesses:** Basic accounting. Limited manufacturing. PHP ecosystem aging.
- **Assessment:** Too simple for EverJust's ambitions. Not a viable base for a multi-tenant SaaS platform.

### Apache OFBiz

- **Language:** Java
- **License:** Apache 2.0 (permissive!)
- **Strengths:** Flexible framework for custom enterprise apps. Tight ERP + ecommerce integration. Apache 2.0 license means no copyleft restrictions.
- **Weaknesses:** Complex Java stack. Small community. Documentation gaps. Feels abandoned compared to competitors.
- **Assessment:** The Apache 2.0 license is attractive (most permissive of all options), but the Java stack and small community make it impractical.

### Summary Table

| Platform | Language | License | Community | UI Quality | ERP Depth | Viable Base? |
|----------|----------|---------|-----------|------------|-----------|-------------|
| Odoo CE | Python | LGPL-3 | Huge | Good (OWL) | Deep | Current choice |
| ERPNext | Python | GPL-3 | Medium | OK | Deep | No (stricter license) |
| Tryton | Python | GPL-3 | Small | Basic | Good | Maybe (clean code) |
| iDempiere | Java | GPL-2 | Small | Dated | Very Deep | No (Java, dated) |
| Dolibarr | PHP | GPL-3 | Medium | Basic | Shallow | No (too simple) |
| OFBiz | Java | Apache-2.0 | Tiny | Dated | Medium | No (Java, tiny community) |

---

## 4. Build-from-Scratch with Modern Stack

### What a Modern ERP Would Look Like (2026)

Based on real-world examples of companies that built custom ERPs:

**Recommended stack:**

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React/Next.js + TypeScript | Dominant framework, huge talent pool |
| State mgmt | Zustand or TanStack Query | Lightweight, performant |
| Styling | Tailwind CSS | Rapid UI development |
| Backend | FastAPI (Python) or NestJS (TypeScript) | async, auto-docs, type safety |
| Database | PostgreSQL | ACID, RLS, schemas, JSON, mature |
| Cache/Queue | Redis + Bull | Real-time features, job processing |
| Real-time | WebSockets (Socket.io) | Live dashboards |
| Event bus | Apache Kafka or RabbitMQ | Cross-module communication |
| Auth | KeyCloak or custom (BetterAuth) | SSO, RBAC, multi-tenant |
| Monitoring | Prometheus + Grafana + Sentry | Observability |
| Search | Elasticsearch or Meilisearch | Full-text across entities |
| Infra | Docker + Kubernetes | Container orchestration |

### Real-World Case Study: Custom ERP at Scale

One documented case (Node.js/NestJS + React + PostgreSQL):
- Started as monolith, evolved to domain-driven microservices
- 50+ integrated modules
- 10M+ daily transactions
- 99.95% uptime, sub-200ms p95 response times
- Key lesson: "Start simple, evolve gradually" -- avoid over-engineering for scale initially
- Critical mistake: Missing database indexes caused 30+ second queries on millions of records

### Cost and Timeline Estimates

| Approach | Timeline | Team Size | Cost (Year 1) |
|----------|----------|-----------|---------------|
| Fork Odoo CE (current) | Already done | 1-2 devs | $0-10K |
| Build on Frappe Framework | 6-12 months to MVP | 2-3 devs | $50-100K |
| Build from scratch (full) | 18-36 months to MVP | 4-8 devs | $200K-500K |
| Headless on Directus | 12-18 months to MVP | 3-5 devs | $100-200K |

### What You'd Need to Build from Scratch

The ERP domain is deceptively deep. Core modules that must work correctly from day one:

1. **Double-entry accounting** -- GL, AP, AR, bank reconciliation, multi-currency, tax
2. **Inventory management** -- stock valuation (FIFO/LIFO/average), warehouses, serial/batch tracking
3. **Sales pipeline** -- leads, opportunities, quotations, orders, invoicing
4. **Purchase management** -- RFQs, purchase orders, vendor bills, goods receipt
5. **Contact management** -- customers, vendors, addresses, communication history
6. **Reporting** -- P&L, balance sheet, aged receivables, cash flow
7. **User/role management** -- RBAC with field-level security
8. **Workflow engine** -- approval chains, status machines, notifications
9. **Document management** -- attachments, templates, print formats
10. **Multi-tenancy** -- isolation, provisioning, per-tenant config

Each of these is months of work to get right. Accounting alone (with all the edge cases around partial payments, credit notes, foreign exchange gains/losses, tax jurisdictions) is easily 6-12 months of focused development.

### Assessment for EverJust

Building from scratch would give you full control and zero licensing concerns, but the timeline is prohibitive. An 18-36 month MVP timeline means you'd be shipping nothing new for 1.5-3 years. The Odoo fork, for all its LGPL baggage, gives you a working ERP TODAY with deep functionality that would take years to replicate.

---

## 5. Multi-Tenancy Patterns

### Three Models Compared

| Aspect | DB-per-Tenant (Odoo's approach) | Schema-per-Tenant | Shared Schema (tenant_id + RLS) |
|--------|------|------|------|
| **Data isolation** | Strongest (physical) | Strong (logical) | Weakest (row-level) |
| **Compliance** | Easiest | Easier | Harder |
| **Cost per tenant** | Highest | Medium | Lowest |
| **Migration complexity** | High (N databases) | Medium (N schemas) | Low (one schema) |
| **Connection pooling** | Worst (N * max_conn) | Medium | Best (shared pool) |
| **Onboarding speed** | Minutes (create DB) | Seconds | Instant (insert row) |
| **Backup granularity** | Per-tenant easy | Per-schema possible | Whole DB only |
| **Scaling limit** | ~500 tenants practical | ~10,000 tenants | Millions of tenants |
| **Query performance** | Best (no filter overhead) | Good | Good with indexes (1-5% RLS overhead) |

### Current Best Practice (2026)

The industry consensus for most B2B SaaS in 2026 is **shared schema with tenant_id column + PostgreSQL Row-Level Security (RLS)**. Key findings:

- RLS overhead is 1-5% with proper composite indexes (`tenant_id` as leading column)
- With composite indexes, policy evaluation averages 0.3ms on 50M rows across 10K tenants
- `SET LOCAL` call adds under 0.1ms
- Missing composite indexes are the #1 performance killer -- without `tenant_id` leading, RLS is two orders of magnitude slower

### Decision Framework

**Use DB-per-tenant (current Odoo approach) when:**
- < 500 tenants
- Enterprise customers demanding physical isolation
- Strict regulatory requirements (HIPAA, SOC2 per-client audits)
- Tenants need independent backup/restore
- Tenants have wildly different schema customizations

**Use shared schema + RLS when:**
- Targeting thousands of tenants
- Need fast onboarding (self-service signup)
- Cost efficiency matters
- Uniform schema across tenants
- Want simpler operations (one DB to monitor, backup, migrate)

### Critical Safety Mechanisms

Six pitfalls to avoid with shared-schema multi-tenancy:
1. Missing RLS on new tables (every new table needs a policy)
2. Inadequate isolation testing (test that tenant A cannot see tenant B data)
3. Connection pool exhaustion (100 tenants * 20 conn = 2000 connections)
4. Tenant-unaware caching (Redis keys MUST include tenant ID)
5. Running migrations during peak traffic
6. Hardcoded tenant resolution strategies

### Assessment for EverJust

Odoo's DB-per-tenant model is actually well-suited for EverJust's current scale (2 active tenants, likely < 100 in the medium term). The operational overhead only becomes painful at scale (500+ tenants). If EverJust were building from scratch for high-volume self-service SaaS, shared-schema + RLS would be the right default. But for the current B2B model with a small number of tenants, DB-per-tenant provides the strongest isolation with the least risk.

---

## 6. Plugin/Module Systems in Modern Frameworks

### Comparison of Extensibility Approaches

**Odoo Addons (current):**
- Modules are Python packages with `__manifest__.py`
- Can override any model, view, controller via inheritance
- XML-based view extension (xpath)
- Hook into any lifecycle event via `@api.onchange`, `write()`, `create()` overrides
- 40,000+ third-party modules
- **Strength:** Most powerful override system of any ERP
- **Weakness:** Upgrades frequently break addons; monkey-patching is fragile

**Frappe/ERPNext Hooks:**
- `hooks.py` per app defines event subscriptions
- `doc_events` dict maps DocType + event to handler functions
- `override_whitelisted_methods` for API overrides
- Regional override decorator for country-specific logic
- **Strength:** Cleaner than Odoo's inheritance-everywhere pattern
- **Weakness:** Less granular than Odoo (can't override arbitrary view elements)

**Medusa.js 2.0 Modules:**
- Self-contained units with service layer, data models, API routes
- Service injection pattern -- override any service without modifying base
- Clear separation of concerns per module
- **Strength:** Modern TypeScript, clean DI architecture
- **Weakness:** E-commerce only; pattern is inspiring but domain is narrow

**Payload CMS Plugins:**
- Hook system: `beforeOperation`, `beforeValidate`, `beforeChange`, `afterChange`, `beforeRead`, `afterRead`, `beforeDelete`, `afterDelete`
- Collection-level, global-level, and field-level granularity
- Cross-plugin discovery via slug system (v3.83+)
- **Strength:** Comprehensive lifecycle hooks, TypeScript-first
- **Weakness:** No model inheritance; plugins can't modify existing collection schemas

**Directus Extensions:**
- Four types: interfaces (UI), displays, layouts, modules
- API extensions: endpoints, hooks
- Wraps existing database -- extensions add behavior, not schema
- **Strength:** Database-first philosophy; works with existing data
- **Weakness:** No model-level override; extension API is shallow compared to Odoo

### Ranking by Extensibility Power

1. **Odoo** -- most powerful (can override anything, including other addons)
2. **Frappe** -- strong (event-driven hooks, but less view-level control)
3. **Medusa.js** -- good (service DI, clean module boundaries)
4. **Payload CMS** -- good (comprehensive hooks, growing plugin API)
5. **Directus** -- moderate (extension types are well-defined but shallow)

### What a Modern Module System Should Look Like

If building from scratch, take the best from each:

```
From Odoo:      Model inheritance (extend existing models in other modules)
From Frappe:    Event-driven hooks via declarative config (not monkey-patching)
From Medusa:    Dependency injection for service layer overrides
From Payload:   Typed lifecycle hooks at multiple granularity levels
From Directus:  Database-first philosophy (schema IS the API)
```

**Ideal pattern:**
```python
# Module manifest
{
    "name": "custom_invoicing",
    "depends": ["accounting", "contacts"],
    "hooks": {
        "accounting.Invoice": {
            "before_validate": "custom_invoicing.hooks.check_credit_limit",
            "after_submit": "custom_invoicing.hooks.send_notification"
        }
    },
    "extends": {
        "accounting.Invoice": {
            "fields": [{"name": "custom_field", "type": "varchar"}],
            "methods": {"calculate_tax": "custom_invoicing.tax.regional_tax"}
        }
    }
}
```

---

## Recommendations

### Keep the Odoo Fork (Recommended)

**Rationale:** After researching all alternatives, the Odoo 19 CE fork remains the strongest position for EverJust:

1. **LGPL-3 is actually the MOST permissive** ERP license available. ERPNext (GPL-3), Tryton (GPL-3), Dolibarr (GPL-3), iDempiere (GPL-2) are all MORE restrictive. Only Apache OFBiz (Apache-2.0) is more permissive, and its community is effectively dead.

2. **Building from scratch is 18-36 months** before reaching feature parity with what you have today. The ERP domain (accounting, inventory, tax engines) is deceptively deep.

3. **The ecosystem matters.** 40,000+ modules vs. 300 (ERPNext) or fewer. Even if 95% are low quality, the remaining 5% save months of development.

4. **DB-per-tenant is correct** for EverJust's scale. The operational overhead concern only applies at 500+ tenants.

5. **The debranding is already done.** `everjust_brand` removes all Odoo references. Users don't know or care what's underneath.

### If You Must Move Away from Odoo (Plan B)

Build on the **Frappe Framework** (MIT license) WITHOUT using ERPNext code:

1. Use Frappe's DocType system, hooks, and multi-tenancy as the foundation
2. Write your own business modules (accounting, CRM, etc.) from scratch
3. These modules would be YOUR proprietary code (Frappe is MIT)
4. Timeline: 12-18 months to a usable MVP with basic accounting + CRM
5. Risk: You're still dependent on Frappe's development trajectory

### If Starting Completely Fresh (Plan C)

**FastAPI + Next.js + PostgreSQL + Redis:**
- FastAPI backend with auto-generated OpenAPI docs
- Next.js frontend with TypeScript
- PostgreSQL with RLS for multi-tenancy (shared schema)
- Redis for caching and job queues
- Medusa-style module system with DI and lifecycle hooks
- Timeline: 24-36 months to production-ready ERP
- Team: 4-6 full-stack engineers minimum

This only makes sense if EverJust raises significant funding and pivots to becoming primarily a software company rather than using ERP as infrastructure for client services.

---

## Sources

- [ERPNext Deep Dive 2026](https://devdiligent.com/blog/erpnext-deep-dive/)
- [ERPNext DeepWiki Architecture](https://deepwiki.com/frappe/erpnext)
- [Frappe Framework Guide 2025](https://medium.com/@the.scideas/frappe-framework-guide-features-architecture-use-cases-benefits-2025-edition-9d0af8a3c047)
- [Odoo vs ERPNext 2026](https://www.erpresearch.com/compare/erpnext-vs-odoo)
- [Odoo vs ERPNext: Real Cost of Open Source](https://finbyz.tech/erpnext/insights/odoo-vs-erpnext-2026-comparison)
- [ERPNext License and Trademark](https://erpnext.com/license-trademark)
- [Headless ERP: API-First Architecture](https://ecosire.com/blog/headless-erp-api-first-architecture)
- [Odoo Headless in 2026](https://www.captivea.com/blog/captivea-blog-4/odoo-headless-in-2026-build-your-erp-roadmap-at-your-own-pace-1072)
- [Open Source ERP Top 10 Comparison 2026](https://ecosire.com/blog/open-source-erp-top-10-comparison-2026)
- [Top Open Source ERP Frameworks 2025](https://www.noitechnologies.com/top-10-open-source-erp-frameworks-to-consider-in-2025/)
- [Custom ERP: Tech Stack & Lessons Learned](https://dev.to/abhishek_pundir_beb087d2b/how-we-built-a-custom-erp-system-tech-stack-lessons-learned-5c35)
- [Why JetRuby Built a Custom ERP](https://jetruby.com/blog/why-we-built-custom-erp-system/)
- [Multi-Tenant Architecture: DB Per Tenant vs Shared Schema](https://dev.to/young_gao/multi-tenant-architecture-database-per-tenant-vs-shared-schema-1n2e)
- [PostgreSQL RLS for Multi-Tenant SaaS](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres)
- [Multi-Tenant Database Patterns Explained](https://www.bytebase.com/blog/multi-tenant-database-architecture-patterns-explained/)
- [Designing Multi-Tenancy in PostgreSQL](https://dohost.us/index.php/2026/06/12/designing-for-multi-tenancy-scalable-data-isolation-patterns-in-postgresql/)
- [Medusa.js Commerce Modules](https://medusajs.com/modules/)
- [Exploring Medusa 2.0 Modules](https://www.rigbyjs.com/blog/medusa-modules)
- [Best Payload CMS Plugins](https://www.buildwithmatija.com/blog/best-payload-cms-plugins)
- [Directus: Database-Native Backend](https://leadai.dev/cms/directus)
- [Directus CMS Guide](https://techsy.io/blog/directus-cms-guide)
- [Frappe Licensing Discussion](https://discuss.frappe.io/t/frappe-licensing-software-architecture/120722)
