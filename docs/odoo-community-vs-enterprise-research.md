# Odoo Community vs Enterprise: Comprehensive Research Report

**Date:** 2026-06-14
**Purpose:** Full quantitative + qualitative analysis for EVERJUST.APP architecture decisions

---

## 1. Company Overview & Financials

| Metric | Value | Source |
|---|---|---|
| Founded | 2005 (as TinyERP, renamed OpenERP 2008, Odoo 2014) | Wikipedia |
| Headquarters | Ramillies, Belgium | Wikipedia |
| Employees | 2,200+ (2023) | Wikipedia |
| Revenue | EUR 282M (2023), ~33% YoY growth | Wikipedia |
| Funding | $90M (2019), $500M (2024, Sequoia-led, $5B valuation) | Wikipedia + press |
| Users | 5M+ (2021 figure; likely 7-12M by 2026) | Wikipedia |
| Latest version | 19.0 (September 2025) | Official |
| License (Community) | LGPL-3 | Official |
| License (Enterprise) | Proprietary (Odoo Enterprise Edition License) | Official |

---

## 2. Pricing Model

### Current Plans (as of June 2026)

| Plan | Price | What's Included | Hosting |
|---|---|---|---|
| **One App Free** | $0/mo | 1 app + dependencies, unlimited users | Odoo Online only |
| **Standard** | $24.90/user/mo (annual) / $31.10 (monthly) | All apps | Odoo Online only |
| **Custom** | $49.00/user/mo (annual) / $61.00 (monthly) | All apps + Studio + Multi-Company + External API | Odoo Online, Odoo.sh, or On-Premise |

### Key Pricing Notes
- A "paying user" = employee with backend access. Portal/customer users are free.
- In-app purchases (SMS, lead enrichment, AI features) cost extra.
- Odoo.sh hosting is separate from the subscription.
- Implementation services not included.
- Geographic pricing variations exist (lower rates in developing markets).

### Community Edition
- **$0 forever.** Self-hosted only. No official support. No automatic upgrades.

---

## 3. Module Count: Community vs Enterprise

### Community (Open Source, LGPL-3)
- **625 addon directories** in the `odoo/odoo` GitHub repo (19.0 branch)
- Includes ~190+ localization modules (`l10n_*`)
- Core functional modules: ~100-120 (CRM, Sales, Purchase, Inventory, MRP, Accounting, HR basics, Website, eCommerce, POS, Project, Email Marketing, Events)

### Enterprise (Proprietary)
- The `odoo/enterprise` repository is **private** (not publicly accessible)
- Estimated **80-100 Enterprise-exclusive modules** based on feature listings
- These represent roughly 40-45% of the total functional surface area (by value, not count)

### Third-Party App Store
| Category | Count |
|---|---|
| Free/Open Source apps | 27,062 |
| Paid apps | 47,054 |
| **Total** | **~74,000+** |

Price range for paid apps: $10 - $1,500+ (most popular: $50-$600 range)

Most downloaded examples:
- "Odoo 19 Accounting Community" - 118,927 downloads (free)
- "Dashboard Ninja with AI" - 3,052 downloads ($598)
- "Shopify Odoo Connector" - 2,302 downloads ($465)

---

## 4. Feature-by-Feature Comparison

### FINANCE

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Invoicing | Full | Full | None |
| Basic accounting (journals, taxes, reconciliation) | Full | Full | None |
| Multi-currency | Full | Full | None |
| Bank reconciliation | Full | Full | None |
| P&L, Balance Sheet, Aged Receivable/Payable reports | Basic only | Full advanced | **HIGH** |
| Cash flow reporting | No | Yes | HIGH |
| Budget management | No | Yes | MEDIUM |
| Asset management (depreciation) | No | Yes | HIGH |
| Deferred revenues/expenses | No | Yes | MEDIUM |
| SEPA direct debit | No | Yes | LOW (EU-specific) |
| AI invoice digitization (OCR) | No | Yes (IAP) | MEDIUM |
| Live currency rates | No | Yes | LOW |
| Consolidation (multi-company) | No | Yes | HIGH (for multi-co) |
| Analytic accounting | Basic | Advanced | MEDIUM |

**OCA Alternative Quality: 7/10** - The `account_financial_report` OCA repo provides P&L, Balance Sheet, and partner statement reports. `mis_builder` handles cash flow. Budget management exists via `project_budget`. Asset management is the biggest gap with no mature OCA replacement.

### CRM

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Leads & Opportunities | Full | Full | None |
| Pipeline management | Full | Full | None |
| Activities & scheduling | Full | Full | None |
| Email integration | Full | Full | None |
| Lead scoring (predictive) | No | Yes | MEDIUM |
| Lead enrichment (company data via IAP) | No | Yes (paid IAP) | LOW |
| SMS integration | No | Yes | MEDIUM |
| VoIP click-to-call | No | Yes | MEDIUM |
| Partner geo-assignment | No | Yes | LOW |
| Advanced dashboards/spreadsheet | No | Yes | MEDIUM |

**OCA Alternative Quality: 5/10** - CRM is mostly complete in Community. The Enterprise extras are "nice to have" (scoring, enrichment) rather than critical. VoIP can be solved with the `everjust_phone` Twilio integration we already built.

### SALES

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Quotations & Sales Orders | Full | Full | None |
| Product variants | Full | Full | None |
| Pricelists | Full | Full | None |
| Subscriptions | No | Yes | HIGH |
| Rental management | No | Yes | MEDIUM |
| Amazon connector | No | Yes | LOW |
| Shopee/Lazada connectors | No | Yes | LOW |

**OCA Alternative Quality: 4/10** - Subscriptions is a real gap. The `contract` OCA module provides recurring invoicing but lacks the full subscription lifecycle (trial, upgrade, downgrade, churn metrics). Third-party apps on the store fill this partially ($200-500).

### INVENTORY & WAREHOUSE

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Stock management | Full | Full | None |
| Multi-warehouse | Full | Full | None |
| Lot/serial tracking | Full | Full | None |
| Delivery carriers (base) | Full | Full | None |
| Routes & rules | Full | Full | None |
| Barcode scanning app | No | Yes | **HIGH** |
| Batch/wave picking | No | Yes | HIGH |
| Dropshipping | Partial | Full | MEDIUM |
| Quality control integration | No | Yes | MEDIUM |
| IoT integration (scales, printers) | No | Yes | MEDIUM |
| Enterprise carrier connectors (DHL, FedEx, UPS, USPS) | No | Yes | HIGH |

**OCA Alternative Quality: 6/10** - `stock_cycle_count`, `stock_location_zone`, and warehouse security modules are solid. Barcode scanning is the biggest pain point -- the Enterprise barcode app is excellent. OCA has `stock_barcodes` but it's not nearly as polished. Third-party barcode apps exist ($100-400).

### MANUFACTURING (MRP)

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Bills of Materials | Full | Full | None |
| Manufacturing Orders | Full | Full | None |
| Work Centers | Full | Full | None |
| Subcontracting | Full | Full | None |
| Repair orders | Full | Full | None |
| Master Production Schedule (MPS) | No | Yes | HIGH |
| PLM (Product Lifecycle Management) | No | Yes | HIGH |
| Work order IoT integration | No | Yes | MEDIUM |
| Quality checks at work orders | No | Yes | MEDIUM |
| Shop floor module | No | Yes | HIGH |

**OCA Alternative Quality: 6/10** - `mrp_multi_level` provides MRP-like demand planning. `quality_control_oca` handles quality checks. PLM is a real gap with no good community alternative. The 56 OCA manufacturing modules cover a lot of ground.

### PURCHASE

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Purchase Orders | Full | Full | None |
| Vendor Bills | Full | Full | None |
| RFQs | Full | Full | None |
| Purchase agreements (blanket orders) | No | Yes | MEDIUM |
| Intrastat reporting | No | Yes | LOW (EU-specific) |
| Approval workflows | No | Yes | MEDIUM |

**OCA Alternative Quality: 7/10** - `purchase_blanket_order` OCA module exists. Approval workflows available via `purchase_approval` and similar.

### HUMAN RESOURCES

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Employee records | Full | Full | None |
| Departments & org chart | Full | Full | None |
| Skills tracking | Full | Full | None |
| Attendance | Full | Full | None |
| Time off (leave management) | Full | Full | None |
| Expenses | Full | Full | None |
| Recruitment | Full | Full | None |
| **Payroll** | **No** | **Yes** | **CRITICAL** |
| Appraisals / Performance | No | Yes | MEDIUM |
| Shift planning (Gantt) | No | Yes | HIGH |
| Contract configurator | No | Yes | MEDIUM |
| AI expense extraction (OCR) | No | Yes | LOW |
| Employee referrals | No | Yes | LOW |
| Fleet management | Full | Full | None |

**OCA Alternative Quality: 3/10** - Payroll is the single biggest Enterprise lock-in feature. The OCA `hr-payroll` repo existed historically but has been inconsistently maintained for recent versions. Third-party payroll modules are available ($200-800) but localization-dependent and often mediocre. Most Community deployments integrate with external payroll systems (ADP, Gusto, etc.).

### PROJECT & SERVICES

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Projects & Tasks | Full | Full | None |
| Timesheets | Full | Full | None |
| Task dependencies | Full | Full | None |
| **Gantt view** | **No** | **Yes** | **HIGH** |
| Resource forecasting | No | Yes | HIGH |
| Budget integration | No | Yes | MEDIUM |
| **Helpdesk** | **No** | **Yes** | **HIGH** |
| **Field Service** | **No** | **Yes** | **HIGH** |
| **Planning (shift scheduling)** | **No** | **Yes** | **HIGH** |

**OCA Alternative Quality: 7/10** - This is where OCA shines. `helpdesk_mgmt` (33+ modules) is a comprehensive helpdesk with SLA, ratings, portal, CRM/project integration. `fieldservice` (38+ modules) includes territories, skills, vehicles, routes, portal, even geoengine mapping. `project_timeline` provides a Gantt-like view. `project_forecast_line` handles demand planning. These are genuinely good alternatives.

### WEBSITE & eCOMMERCE

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Website builder | Full | Full | None |
| Blog | Full | Full | None |
| Forum | Full | Full | None |
| eCommerce (basic) | Full | Full | None |
| eLearning | Full | Full | None |
| AI website generator | No | Yes | LOW |
| Live Chat | No | Yes | MEDIUM |
| Appointment booking (online) | No | Yes | MEDIUM |
| Online rental/subscription sales | No | Yes | MEDIUM |

**OCA Alternative Quality: 5/10** - Live chat can be replaced with Tawk.to, Crisp, or similar. Appointment booking has third-party solutions. The website builder itself is the same in both editions.

### MARKETING

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Email Marketing | Full | Full | None |
| Events management | Full | Full | None |
| **SMS Marketing** | **No** | **Yes** | **MEDIUM** |
| **Social Media Marketing** | **No** | **Yes** | **MEDIUM** |
| **Marketing Automation** | **No** | **Yes** | **HIGH** |
| Surveys | No | Yes | MEDIUM |
| Push notifications | No | Yes | LOW |

**OCA Alternative Quality: 3/10** - Marketing automation is a genuine gap. No good OCA equivalent exists. SMS can be solved with `everjust_sms_gateway` (our module). Social marketing has no community alternative -- most people use standalone tools (Buffer, Hootsuite). Third-party survey modules exist.

### POINT OF SALE

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Basic POS | Full | Full | None |
| Restaurant mode | No | Yes | HIGH (for restaurants) |
| Self-ordering | No | Yes | MEDIUM |
| Loyalty programs | No | Yes | MEDIUM |
| Kitchen display | No | Yes | HIGH (for restaurants) |
| IoT integration | No | Yes | MEDIUM |

**OCA Alternative Quality: 4/10** - Restaurant POS is a major gap for that vertical. Some third-party modules exist but quality varies.

### PRODUCTIVITY & COLLABORATION

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| Discuss (internal messaging) | Full | Full | None |
| Calendar | Full | Full | None |
| To-do | Full | Full | None |
| **Documents (DMS)** | **No** | **Yes** | **HIGH** |
| **Sign (e-signatures)** | **No** | **Yes** | **HIGH** |
| **Knowledge (wiki)** | **No** | **Yes** | **MEDIUM** |
| Approvals (configurable) | No | Yes | MEDIUM |
| **VoIP** | **No** | **Yes** | **MEDIUM** |
| WhatsApp integration | No | Yes | MEDIUM |
| Data cleaning/dedup | No | Yes | LOW |
| Spreadsheet (collaborative) | No | Yes | MEDIUM |
| Dashboards (advanced) | No | Yes | MEDIUM |

**OCA Alternative Quality: 7/10** - We already use OCA modules for this: `dms` (document management), `document_page` (wiki/knowledge with 16 modules), `sign_oca` (e-signatures), `attachment_zipped_download`. Our `everjust_phone` module handles VoIP via Twilio. The OCA alternatives are genuinely functional.

### CUSTOMIZATION & PLATFORM

| Feature | Community | Enterprise | Gap Severity |
|---|---|---|---|
| **Studio (no-code builder)** | **No** | **Yes** | **HIGH** |
| **Odoo.sh (PaaS hosting)** | **No** | **Yes** | **MEDIUM** |
| Multi-company | Basic | Advanced | MEDIUM |
| External API | Full | Full | None |
| Official support (SLA) | No | Yes | MEDIUM |
| Automatic upgrades | No | Yes | HIGH |
| Security patches (priority) | No | Yes | MEDIUM |
| **Map view** | **No** | **Yes** | **LOW** |

**OCA Alternative Quality: 2/10** - Studio has no real community equivalent. You can customize Odoo with code (which is what we do), but there's no drag-and-drop builder. `OpenUpgrade` (OCA) provides version migration tooling as an alternative to automatic upgrades, but it requires technical expertise.

---

## 5. Enterprise-Only Applications (No Community Equivalent)

These are **entire applications** that exist only in Enterprise:

| App | OCA Alternative? | Alt Quality (0-10) | Build Custom Time |
|---|---|---|---|
| **Payroll** | Partial (abandoned) | 2 | 3-6 months per country |
| **Helpdesk** | `helpdesk_mgmt` | **8** | Already built |
| **Field Service** | `fieldservice` | **8** | Already built |
| **Planning** | `project_forecast_line` | 5 | 2-4 weeks |
| **Documents** | `dms` (OCA) | **7** | Already in our stack |
| **Sign** | `sign_oca` | 6 | Already exists |
| **Knowledge** | `document_page` (OCA) | **7** | Already in our stack |
| **Studio** | None | 0 | Not feasible |
| **Subscriptions** | `contract` (OCA) | 5 | 4-8 weeks for full |
| **Rental** | None | 1 | 2-4 weeks |
| **VoIP** | `everjust_phone` (ours) | **8** | Already built |
| **Marketing Automation** | None | 1 | 6-12 weeks |
| **Social Marketing** | None | 0 | Not worth building |
| **WhatsApp** | `mail_gateway_whatsapp` (OCA) | 4 | 2-3 weeks |
| **Approvals** | Various OCA | 5 | 1-2 weeks |
| **Data Cleaning** | None | 1 | 2-3 weeks |
| **Consolidation** | None | 0 | Very complex |
| **IoT** | None | 0 | Hardware-dependent |
| **Barcode (mobile app)** | `stock_barcodes` | 4 | 4-6 weeks |
| **ESG** | None | 0 | Niche |
| **Frontdesk** | None | 0 | 1 week |
| **Appointment (online)** | Third-party | 5 | 2-3 weeks |
| **Spreadsheet** | None | 0 | Not feasible |
| **Quality** | `quality_control_oca` | 6 | 2-3 weeks |

---

## 6. OCA (Odoo Community Association) Deep Dive

### Organization Stats
| Metric | Value |
|---|---|
| GitHub repositories | 260 |
| Total modules | 20,000+ (across all versions) |
| Contributors | 1,117 |
| Members | 664 |
| Countries represented | 62 |
| Sponsors | 38 |
| Headquarters | Lausanne, Switzerland |
| License | AGPL-3.0 (typically) |
| GitHub followers | 4,700+ |
| Key project: OCB (Community Backports) | 367 stars, 33,178 forks |
| Key project: OpenUpgrade | 953 stars, 814 forks |

### OCA Repos That Fill Enterprise Gaps

| OCA Repository | Modules | Enterprise Feature Replaced | Maturity |
|---|---|---|---|
| `helpdesk` | 33+ | Helpdesk | Mature |
| `field-service` | 38+ | Field Service | Mature |
| `account-financial-reporting` | 7 | Advanced accounting reports | Mature |
| `reporting-engine` | 40+ | BI/reporting | Mature |
| `knowledge` | 16 | Knowledge + Documents | Mature |
| `sign` | 3 | Sign | Growing |
| `project` | 30+ | Planning/Gantt features | Mature |
| `manufacture` | 56 | MPS/PLM/Quality | Mature |
| `stock-logistics-warehouse` | 40+ | Barcode/batch picking | Mature |
| `web` | 76 | UI/dashboard improvements | Mature |
| `social` | 3 | WhatsApp/Telegram gateways | Growing |

### OCA Quality Assessment
- **Strengths:** Code review process, CI/CD, consistent coding standards, multi-version support, real-world tested by integrators
- **Weaknesses:** Maintenance can lag behind major versions, some modules abandoned, less polished UI than Enterprise, no official support
- **Overall:** For 60-70% of Enterprise gaps, OCA provides a workable (if rougher) alternative

---

## 7. The Enterprise Gap -- What Actually Matters

### Gaps That Are CRITICAL (hard to work around)

1. **Payroll** -- Country-specific, legally complex, constantly changing. No good community path. Most Community deployments integrate external payroll (ADP, Gusto, Deel, etc.).

2. **Studio** -- No community equivalent. If you want non-technical users to customize forms/views, Enterprise is the only option. Code-savvy teams (like ours) don't need it.

3. **Automatic version upgrades** -- Enterprise users get Odoo-managed upgrades. Community users must handle migrations manually (OCA's OpenUpgrade helps but requires expertise). This is a significant ongoing cost.

4. **Advanced accounting reports** -- P&L, Balance Sheet, Cash Flow, Aged reports are severely limited in Community. OCA's `account_financial_report` covers the basics but isn't as polished. For serious accounting, this is a real pain point.

### Gaps That Are HIGH but Solvable

5. **Barcode/mobile warehouse app** -- Third-party apps exist; OCA `stock_barcodes` works; or build custom with the API.

6. **Gantt views** -- `web_timeline` OCA provides similar functionality. Not identical but functional.

7. **Helpdesk / Field Service / Planning** -- OCA alternatives are genuinely good (7-8/10).

8. **Documents & Sign** -- OCA `dms` + `sign_oca` work. We already use them.

### Gaps That Are Marketing Fluff

9. **AI website generator** -- Gimmick. Not a business decision factor.
10. **Lead enrichment** -- Nice, but works via IAP (pay-per-use anyway). Can use Clearbit/Apollo directly.
11. **Social marketing** -- Everyone uses standalone tools (Buffer, Hootsuite, Later).
12. **ESG tracking** -- Extremely niche.
13. **Data cleaning** -- Useful but can be done with SQL or Python scripts.
14. **Frontdesk** -- A simple visitor log. Trivial to build.

---

## 8. Cost Comparison: Enterprise vs Community + OCA

### Scenario: 25-user company

| | Enterprise (Standard) | Enterprise (Custom) | Community + OCA |
|---|---|---|---|
| Annual license | $7,470 (25 x $24.90 x 12) | $14,700 (25 x $49 x 12) | $0 |
| Hosting | Included (Odoo Online) | Odoo.sh ~$100-300/mo | Self-hosted $50-200/mo |
| Third-party apps | N/A | N/A | $500-3,000 one-time |
| Implementation | $5,000-50,000 | $5,000-50,000 | $5,000-50,000 |
| Annual maintenance | Included | Included | $2,000-10,000/yr (dev time) |
| Upgrades | Included | Included | $3,000-15,000 per version |
| **Year 1 Total** | ~$12,500-57,500 | ~$20,000-65,000 | ~$7,500-63,000 |
| **Year 2+ Annual** | ~$7,500-8,000 | ~$15,000-18,000 | ~$2,000-10,000 |

### Scenario: 100-user company

| | Enterprise (Standard) | Community + OCA |
|---|---|---|
| Annual license | $29,880 | $0 |
| **5-year license cost** | **$149,400** | **$0** |

The break-even point is clear: if you have the technical team to maintain Community, the savings compound massively over time. If you lack technical resources, Enterprise is the rational choice.

---

## 9. What This Means for EVERJUST.APP

### Our Position: Community is the Right Call

EVERJUST runs on debranded Odoo 19 Community. Here's why that works:

**We've already filled the critical gaps:**
- VoIP: `everjust_phone` (Twilio WebRTC) -- better than Enterprise VoIP
- SMS: `everjust_sms_gateway` (multi-provider routing)
- Documents: `dms` + `document_page` (OCA, already integrated)
- Branding: `everjust_brand` (full debrand, auto-install)

**Gaps we accept:**
- Payroll: Our tenants use external payroll systems (standard for SMBs)
- Studio: Our tenants are not building custom apps; we handle customization
- Marketing automation: Tenants use standalone marketing tools
- Automatic upgrades: We manage upgrades via CI/CD + OpenUpgrade

**Gaps that could matter for future tenants:**
- Advanced accounting reports: Should integrate OCA `account_financial_report`
- Helpdesk: Should offer OCA `helpdesk_mgmt` as an installable option
- Field Service: OCA `fieldservice` for service-industry tenants
- Barcode: If any tenant needs warehouse scanning

### Enterprise Features We'll Never Need
- Odoo.sh (we self-host on AWS)
- Studio (we write code)
- Social Marketing (standalone tools are better)
- IoT (too niche)
- ESG (too niche)
- Consolidation (single-entity tenants)

---

## 10. Summary Statistics

| Dimension | Number |
|---|---|
| Community modules (in repo) | 625 |
| Enterprise-exclusive modules (estimated) | 80-100 |
| Third-party apps (total store) | 74,000+ |
| Third-party free apps | 27,062 |
| Third-party paid apps | 47,054 |
| OCA repositories | 260 |
| OCA total modules (all versions) | 20,000+ |
| OCA contributors | 1,117 |
| Enterprise features with good OCA alt (7+/10) | ~35% |
| Enterprise features with partial OCA alt (4-6/10) | ~30% |
| Enterprise features with no OCA alt (<4/10) | ~35% |
| Enterprise annual cost (25 users, Standard) | ~$7,500/yr |
| Enterprise annual cost (100 users, Standard) | ~$30,000/yr |
| Community annual cost (self-hosted) | $0 license + hosting + dev time |

---

*This research is based on data gathered from odoo.com, GitHub (odoo/odoo, OCA/*), apps.odoo.com, Wikipedia, Cybrosys comparison, and OCA official sources. All figures are as of June 2026.*
