# Technical Verification Results

**Date:** 2026-06-14
**Method:** Direct source code reading from Odoo 19.0 GitHub branch + local repo analysis
**Purpose:** Eliminate assumptions before building — replace "I think" with "I verified"

---

## V1: SCSS Variable Inventory

**Source:** `addons/web/static/src/scss/primary_variables.scss` (Odoo 19.0)

**Result: ALL CONFIRMED.** Every variable uses `!default` (fully overridable by addons).

### Key Variables for the Rebrand

| Variable | Default | Overridable | Our Value |
|---|---|---|---|
| `$o-brand-primary` | `$o-community-color` (`#71639e`) | Yes (`!default`) | `#000000` |
| `$o-brand-odoo` | `$o-community-color` (`#71639e`) | Yes (`!default`) | `#000000` |
| `$o-community-color` | `#71639e` | Yes (`!default`) | `#000000` |
| `$o-brand-secondary` | `#8f8f8f` | Yes (`!default`) | TBD |
| `$o-action` | `$o-brand-primary` | Yes (`!default`) | Inherits |
| `$o-font-family-sans-serif` | System fonts | Yes (`!default`) | `'Inter', ...` |
| `$o-headings-font-family` | `"SF Pro Display", ...` | Yes (`!default`) | `'DM Sans', ...` |
| `$o-font-family-monospace` | `SFMono-Regular, ...` | Yes (`!default`) | `'JetBrains Mono', ...` |
| `$o-font-size-base` | `o-to-rem(14px)` | Yes (`!default`) | Keep 14px |
| `$o-border-radius` | `o-to-rem(4px)` | Yes (`!default`) | `6px` |
| `$o-border-radius-lg` | `o-to-rem(6px)` | Yes (`!default`) | `10px` |

### Bootstrap Variable Mapping (confirmed in `bootstrap_overridden.scss`)

| Bootstrap Variable | Mapped From |
|---|---|
| `$primary` | `$o-brand-primary` |
| `$body-color` | `$o-main-text-color` |
| `$font-family-sans-serif` | `$o-font-family-sans-serif` |
| `$headings-font-family` | `$o-headings-font-family` |
| `$border-radius` | `$o-border-radius` |
| `$link-color` | `$o-main-link-color` (darken primary 5%) |
| `$input-focus-border-color` | `$o-brand-primary` |

Notable: `$enable-dark-mode: false`, `$variable-prefix: ''` (empty, not `bs-`), `$font-weight-bold` maps to `$o-font-weight-medium` (500, not 700).

Total overridable variables: **80+**, all with `!default`.

---

## V2: Bootstrap Version

**Result: Bootstrap 5.3.3**

Confirmed from `addons/web/static/lib/bootstrap/dist/css/bootstrap.css` header comment. This is modern and widely compatible.

---

## V3: Tabler Compatibility

**Result: INCOMPATIBLE for SCSS import. Pre-compiled CSS is fallback.**

| Factor | Detail |
|---|---|
| Tabler requires | Bootstrap 5.3.7 |
| Odoo ships | Bootstrap 5.3.3 |
| Tabler prefix | `$prefix: "tblr-"` (generates `--tblr-*` properties) |
| Tabler imports | 79 `@import` statements, expects `node_modules/` pathing |
| Odoo's importer | Custom libsass resolver expecting addon-relative paths |
| `@use`/`@forward` | Not supported (Odoo uses libsass, not Dart Sass) |

**Tabler SCSS will not compile inside Odoo's asset pipeline.** The import resolution paths are fundamentally incompatible.

**Fallback options:**
- Pre-compiled `tabler.min.css` (536KB) as static CSS — viable but adds bloat
- External pre-compilation — viable but complex build step
- **Skip Tabler entirely** — use pure custom SCSS (odoo-style-pro proves this works in 2,250 lines)

---

## V4: Odoo Asset Pipeline

**Result: libsass with custom import resolver. No modern Sass.**

| Feature | Supported |
|---|---|
| `@import` | Yes |
| `@use` / `@forward` | No (libsass limitation) |
| Custom importer | Yes — resolves addon-relative paths via `file_path()` |
| Fallback resolution | `web/static/lib/bootstrap/scss/` directory |
| Bundle compilation order | `_assets_primary_variables` → `_assets_secondary_variables` → `_assets_helpers` → `_assets_bootstrap` → `assets_backend` |

Key finding: `web._assets_primary_variables` is compiled into the context of ALL other bundles. Variables set here cascade everywhere (backend, frontend, login, reports).

---

## V5: OCA web_responsive (v19)

**Result: Maintained and working. Conflicts with everjust_home.**

| Detail | Status |
|---|---|
| v19 branch | Exists, actively maintained |
| Last update | 2026-05-12 (compatibility fix) |
| Migration date | 2025-11-04 |
| Status | Production/Stable |
| Dependencies | web, web_tour, mail |
| Excludes | web_enterprise |

**Features:** Full-page app menu with fuzzy search, sticky list headers/footers, enlarged checkboxes, responsive chatter, keyboard shortcuts, 12 OWL component patches.

**Conflict:** web_responsive replaces the apps dropdown with a full-page menu. `everjust_home` also replaces the home screen. Both cannot coexist without coordination.

---

## V6: odoo-style-pro Code Review

**Result: Excellent reference. Pure custom SCSS, proven on v19.**

| Metric | Value |
|---|---|
| Total SCSS | ~2,250 lines across 18 files |
| JS files | 5 (theme service, chatter resizer, home menu, kanban patch) |
| Dependencies | `web` only |
| Third-party libs | None |
| License | LGPL-3 |
| Last updated | 4 days ago (2026-06-10) |

**Architecture:** CSS custom properties (`--pan-*` tokens) in `:root`, injected at runtime via a JS service that reads from `ir.config_parameter`. Does NOT mutate `web._assets_primary_variables` for styling — only the minimal SCSS variable overrides go there.

**Key patterns:** Icon font guards (`.oi`, `.fa` with `!important`), tag softening via gradient overlay, statusbar pill redesign, chatter resize handle with localStorage persistence, full Enterprise-parity home menu.

---

## V7: Database Manager

**Result: Non-issue. Disabled in production.**

The page is served by a controller loading standalone QWeb HTML files (not inheritable via `t-inherit`). However, production config has `list_db = False` in `deployment/odoo.conf`, which disables the page entirely. No debranding needed.

---

## V8: FontAwesome Icon Audit

**Result: FA 4.7 is deeply embedded. Do not replace.**

| Fact | Detail |
|---|---|
| FA version | 4.7.0 (self-hosted, no CDN) |
| Odoo UI Icons | 69 custom icons (`.oi-*` classes), supplementary |
| FA in user's addons | 49 unique icon classes, ~100 occurrences |
| Reference methods | XML `icon=` attribute, inline `<i class="fa fa-*">`, JS strings |
| Heaviest usage | dms (~30), voip_oca (~25), everjust_phone (~12) |

FA is not branded as "Odoo" — there is no debranding motivation to replace it. Replacing would break virtually every module.

---

## V9: Color Combination System

**Result: Website-only. No impact on backend theme.**

Color combinations (CC1-CC5) are a website builder feature defined in `html_editor` and `website` modules. They use a separate palette system (`o-color-1` through `o-color-5`), not `$o-brand-primary`.

| Question | Answer |
|---|---|
| Used in backend? | No |
| Affected by `$o-brand-primary`? | No |
| Used in kanban/badges? | No |
| Need to override? | No (unless customizing website snippets) |

---

## V10: Report CSS Pipeline

**Result: Fully separate from backend. Theme is PDF-safe.**

| Bundle | Used By | Includes Backend CSS? |
|---|---|---|
| `web.assets_backend` | Backend UI | N/A (this IS the backend) |
| `web.report_assets_common` | PDF reports (wkhtmltopdf) | **No** |
| `web.report_assets_pdf` | PDF reports (reset only) | **No** |
| `web.assets_web_print` | Browser print (Ctrl+P) | Yes (includes assets_backend) |

**Custom SCSS added to `web.assets_backend` will NOT affect PDF report output.** Reports use their own separate bundle with their own Bootstrap overrides (`bootstrap_overridden_report.scss`).

If we want to customize report styling, we would extend `web.report_assets_common` separately. But the default report styling will continue to work correctly regardless of backend theme changes.
