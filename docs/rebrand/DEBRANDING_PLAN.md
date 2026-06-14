# Deep Debranding Plan

## Current Coverage

The existing `everjust_brand` module covers 14 touchpoints:

1. Browser tab title (JS interval + config param)
2. Login page logo
3. Login "Powered by" footer
4. Favicon (.ico + .svg)
5. Apple-touch-icon
6. Backend "Powered by" promotion
7. PDF report footer (company tagline div)
8. Company report_footer field
9. Session version string ("EVERJUST.APP")
10. PWA manifest (name, icons, colors)
11. User menu links (docs, support, account, shortcuts blocked)
12. Enterprise upsell banner (SCSS hide)
13. Default home action (cleared for admin)
14. Login page logo styling

---

## Gap Inventory: 53 Total Touchpoints

### P0 — User-Visible, Must Fix (22 items)

| # | Touchpoint | Location | Technique | Effort | Module |
|---|---|---|---|---|---|
| 1 | "Odoo Session Expired" dialog | `web/static/src/core/errors/error_dialogs.xml` | XML template override | Small | everjust_brand |
| 2 | "Odoo Push notifications blocked" | `web/static/src/views/widgets/notification_alert/notification_alert.xml` | XML template override | Small | everjust_brand |
| 3 | Settings "Odoo 19.0 (Community Edition)" label | `web/static/src/webclient/settings_form_view/widgets/res_config_edition.xml` + `.js` | OWL patch or XML override | Small | everjust_brand |
| 4 | Upgrade dialog ("Get Odoo Enterprise!") | `web/static/src/webclient/settings_form_view/fields/upgrade_dialog.xml` + `.js` | Patch UpgradeDialog to no-op or SCSS hide | Medium | everjust_brand |
| 5 | Upgrade boolean fields (13+ modules) | `web/static/src/webclient/settings_form_view/fields/upgrade_boolean_field.js` | Patch to act as normal boolean | Medium | everjust_brand |
| 6 | Email footers "Powered by Odoo" | `mail/data/mail_templates_email_layouts.xml` | Data XML override on `mail_notification_layout` + `_light` | Small | everjust_brand |
| 7 | Auth signup emails "Welcome to Odoo" | `auth_signup/data/mail_template_data.xml` (4 templates) | Data XML override | Medium | everjust_brand |
| 8 | Portal sidebar "Powered by Odoo" | `portal/views/portal_templates.xml` — `portal_record_sidebar` | XML template inherit | Small | everjust_brand |
| 9 | Portal API docs link to odoo.com | `portal/views/portal_templates.xml` — `portal_my_security` | XML template inherit | Small | everjust_brand |
| 10 | OdooBot name + welcome messages | `mail_bot/models/res_users.py` + `mail_bot.py` | Python override or disable `mail_bot` | Medium | everjust_brand |
| 11 | OdooBot email `odoobot@example.com` | `base/data/res_partner_data.xml` — `base.partner_root` | Data record override | Small | everjust_brand |
| 12 | `support_url` hardcoded to `odoo.com/buy` | `web/models/ir_http.py` | Add to existing `session_info()` override | Tiny | everjust_brand |
| 13 | Brand colors: Odoo purple `#71639e` | `web/static/src/scss/primary_variables.scss` | SCSS override of `$o-brand-odoo`, `$o-brand-primary`, `$o-community-color` | Small | everjust_theme |
| 14 | Theme-color meta tag `#71639e` | `web/views/webclient_templates.xml` | XML template inherit | Tiny | everjust_brand |
| 15 | Database manager page | `web/static/src/public/database_manager.qweb.html` | **SKIP** — disabled in production (`list_db = False`) | N/A | — |
| 16 | Documentation link widget → odoo.com | `web/static/src/views/widgets/documentation_link/documentation_link.js` | JS patch to redirect to own docs URL | Small | everjust_brand |
| 17 | `/web/session/account` redirect to accounts.odoo.com | `web/controllers/session.py` | Controller override or block route | Small | everjust_brand |
| 18 | Scoped app install "Odoo S.A." attribution | `web/static/src/core/install_scoped_app/install_scoped_app.xml` | XML template override | Tiny | everjust_brand |
| 19 | Digest email footers + mobile promo | `digest/data/digest_data.xml` | Data XML override | Medium | everjust_brand_digest |
| 20 | Website footer "Create a free website" → odoo.com | `website/views/website_templates.xml` — `brand_promotion` | XML template inherit | Small | everjust_brand_website |
| 21 | Odoo logo images referenced in templates | `web/static/img/odoo_logo.svg`, etc. | Override template paths | Small | everjust_brand |
| 22 | Default company logo on fresh install | `base.main_company` | Data record override | Small | everjust_brand |

### P1 — Visible but Rare (19 items)

| # | Touchpoint | Module Required | Technique | Satellite Module |
|---|---|---|---|---|
| 23 | POS receipt "Powered by Odoo" | point_of_sale | XML template inherit | everjust_brand_pos |
| 24 | POS customer display "Powered by Odoo" | point_of_sale | XML template inherit | everjust_brand_pos |
| 25 | HR Attendance kiosk "Powered by Odoo" | hr_attendance | XML template inherit | everjust_brand_hr_attendance |
| 26 | CRM PLS tooltip → odoo.com docs | crm | XML template inherit | everjust_brand |
| 27 | Auth TOTP pages → odoo.com | auth_totp_mail/portal | XML template inherit | everjust_brand |
| 28 | Marketing card "Powered by Odoo" | marketing_card | XML template inherit | everjust_brand |
| 29 | Website event exhibitor report | website_event_exhibitor | XML template inherit | everjust_brand_website |
| 30 | Sale portal → odoo.com/documentation | sale | XML template inherit | everjust_brand |
| 31 | Purchase portal → odoo.com/documentation | purchase | XML template inherit | everjust_brand |
| 32 | Website links help → odoo.com | website_links | XML template inherit | everjust_brand_website |
| 33 | Gamification email templates | gamification | Data override | everjust_brand |
| 34 | Lunch email templates | lunch | Data override | everjust_brand |
| 35 | Website profile email templates | website_profile | Data override | everjust_brand_website |
| 36 | Website slides email templates | website_slides | Data override | everjust_brand_website |
| 37 | Livechat email templates | im_livechat | Data override | everjust_brand_livechat |
| 38 | Livechat "Powered by Odoo" | im_livechat | XML template inherit | everjust_brand_livechat |
| 39 | CRM mail template demo data | crm | Demo data — ignore | — |
| 40 | Odoo logo images on disk | web | Override template paths | everjust_brand |
| 41 | `/odoo` URL path | web | **SKIP** — internal route, cannot remove | — |

### P2 — Technical / Developer-Visible (12 items)

| # | Touchpoint | Action |
|---|---|---|
| 42 | `X-Odoo-Objects` email header | Python override to rename or remove |
| 43 | `odoo.release.product_name` = "Odoo" | Monkey-patch at module load (fragile) — consider skipping |
| 44 | `/web/webclient/version_info` endpoint | Controller override to mask |
| 45 | `exp_about()` returns openerp.com | Monkey-patch — low priority |
| 46 | Session cookie name `session_id` | **SKIP** — generic, not branded |
| 47 | `odoobot@example.com` in partner_root | Covered by P0 #11 |
| 48 | CSS class prefixes `o_*` | **SKIP** — internal, not user-visible |
| 49 | `window.odoo` JS global | **SKIP** — breaking to rename |
| 50 | `@odoo-module` directive | **SKIP** — internal tooling |
| 51 | Python `odoo.*` imports | **SKIP** — core framework |
| 52 | `noreply@odoo.com` test email | **SKIP** — not user-visible |
| 53 | LGPL license headers | **SKIP** — legally required |

---

## Module Architecture

### Core module: `everjust_brand` (depends: web, mail)
Handles all P0 items except brand colors (handled by everjust_theme) and module-specific items.

### Satellite modules (auto_install):
| Module | Auto-installs when | Handles |
|---|---|---|
| `everjust_brand_website` | everjust_brand + website | Website footer, event, links, slides, profile |
| `everjust_brand_pos` | everjust_brand + point_of_sale | POS receipt + customer display |
| `everjust_brand_digest` | everjust_brand + digest | Digest email footers |
| `everjust_brand_hr_attendance` | everjust_brand + hr_attendance | Kiosk branding |
| `everjust_brand_livechat` | everjust_brand + im_livechat | Livechat pages + templates |

---

## Implementation Grouping by Technique

### XML Template Overrides (~60% of touchpoints)
Files: `views/web_templates.xml`, `views/mail_templates.xml`
Covers: #1, #2, #3, #6, #7, #8, #9, #14, #18, #20-22, #26-37

### JS Component Patches (~15%)
File: `static/src/js/debrand.js` (expand existing)
Covers: #4, #5, #16

### SCSS Overrides (~10%)
File: `static/src/scss/debrand.scss` (expand existing)
Covers: #13 (brand colors in everjust_theme)

### Python Model Overrides (~10%)
Files: `models/ir_http.py` (expand), `models/mail_bot.py` (new)
Covers: #10, #12, #17, #42

### Data Records (~5%)
File: `data/branding_data.xml` (new)
Covers: #11, #22

---

## Effort Estimate

| Priority | Items | Effort |
|---|---|---|
| P0 (must fix) | 22 (1 skipped) | 3-4 days |
| P1 (rare) | 19 (1 skipped, 1 ignored) | 1-2 days |
| P2 (technical) | 12 (8 skipped) | 0.5 day |
| Satellites | 5 modules | Included above |
| **Total** | | **5-6 days** |
