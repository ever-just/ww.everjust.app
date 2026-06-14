# Sources, Assumptions, and Unknowns

**Date:** 2026-06-14

---

## Research Methodology

This plan was developed through five phases of research followed by 10 targeted source-code verifications:

1. **Phase 1:** Legal feasibility (LGPL-3 SaaS obligations, clean-room precedent, AI copyright)
2. **Phase 2:** Functional specification extraction (Odoo core models, workflows, module architecture)
3. **Phase 3:** Alternative architecture evaluation (ERPNext, Frappe, headless ERP, build-from-scratch)
4. **Phase 4:** AI agent generation feasibility (ERPClaw precedent, spec formats, training data risks)
5. **Phase 5:** White-label deep dive (automated debranding tools, Flectra's approach, AST transforms)

Followed by 10 verifications reading actual Odoo 19.0 source code from GitHub.

---

## Verified Facts (High Confidence)

These were confirmed by reading actual source files, not documentation:

| Fact | Source | Confidence |
|---|---|---|
| All 80+ SCSS variables use `!default` | `primary_variables.scss` on GitHub | 99% |
| Bootstrap version is 5.3.3 | `bootstrap.css` header in Odoo 19 source | 100% |
| Tabler requires Bootstrap 5.3.7 | Tabler `package.json` on GitHub | 100% |
| Tabler SCSS won't compile in Odoo's pipeline | Odoo's `assetsbundle.py` import resolver analysis | 95% |
| Odoo uses libsass (no `@use`/`@forward`) | `assetsbundle.py` source code | 100% |
| web_responsive is maintained for v19 | OCA/web GitHub, last commit 2026-05-12 | 100% |
| odoo-style-pro works on v19 | GitHub repo, last updated 2026-06-10 | 95% |
| Database manager is disabled in production | `deployment/odoo.conf` → `list_db = False` | 100% |
| FA 4.7 is deeply embedded | Grep of user's addons + Odoo source analysis | 95% |
| Color combinations are website-only | `html_editor.common.scss` analysis | 98% |
| Report CSS uses separate bundle | `report_templates.xml` analysis | 99% |
| PDF reports won't be affected by backend theme | Separate `web.report_assets_common` bundle | 99% |

---

## Assumptions Still in Effect (Medium Confidence)

These are reasonable assumptions based on research but not directly verified:

| Assumption | Basis | Confidence | Risk if Wrong | How to Verify |
|---|---|---|---|---|
| Self-hosted WOFF2 fonts will load correctly from addon `static/` | odoo-style-pro does this successfully | 90% | Fonts don't render, fall back to system fonts | Test with one font in local dev |
| `!important` specificity on body font won't cascade to unexpected elements | odoo-style-pro uses this pattern | 85% | Unexpected font changes in widgets/embedded content | Test + visually inspect all view types |
| web_responsive's responsive improvements work independently of its app menu | Code review suggests modular structure | 80% | Must take all-or-nothing | Test by installing and patching out app menu |
| Odoo minor updates (19.0.x) won't break template inherits | Template IDs are stable within major versions | 85% | Debranding partially reverts on update | Pin Docker image version, test after updates |
| The tag softening gradient technique works with all Odoo tag colors | odoo-style-pro uses it | 90% | Some tags look odd | Visual inspection during QA |
| CSS transitions won't interfere with Odoo's JS-driven animations | Separate concern (CSS vs JS) | 85% | Janky animations on transitions | Test with action navigation |

---

## Known Unknowns (Gaps to Close During Implementation)

| Unknown | Impact | When We'll Know |
|---|---|---|
| Exact `!important` count needed for full theme coverage | Code quality metric | After Stage 2 (components) |
| Whether `everjust_home` can coexist with web_responsive's app menu patches | Determines dependency strategy | Decision needed before Stage 4 |
| CSS bundle size increase after full theme | Performance impact | After Stage 5 (polish) |
| How many unique template IDs need overriding for debranding P1 items | Effort for satellite modules | During satellite module implementation |
| Whether Odoo's service worker interferes with theme CSS caching | Users might see stale styles | Test during QA, mitigate with SW cache name bump |
| Mobile touch target sizes after responsive changes | WCAG compliance | Test on real devices during QA |

---

## What We Explicitly Decided NOT To Do

| Decision | Reason |
|---|---|
| **Not replacing FontAwesome icons** | Deeply embedded in XML/JS, not Odoo-branded, high risk for zero debranding benefit |
| **Not using Tabler SCSS** | Incompatible with Odoo's libsass pipeline, would add complexity and bloat |
| **Not modifying backend Python/ORM** | All changes are frontend-only for upgrade safety |
| **Not debranding the database manager** | Disabled in production via `list_db = False` |
| **Not renaming CSS `o_*` class prefixes** | Internal naming, not user-visible, would break everything |
| **Not renaming `window.odoo` JS global** | Would break the entire frontend framework |
| **Not removing LGPL license headers** | Legally required, not user-visible |
| **Not replacing Odoo's OWL framework** | That's a rebuild, not a rebrand |
| **Not building a custom mobile app** | CSS responsive is sufficient for current needs |

---

## Risk Register

### Catastrophic Risks (stop work)

| Risk | Likelihood | Mitigation |
|---|---|---|
| SCSS compilation failure breaks entire backend | Low (patterns proven by odoo-style-pro) | Test every SCSS change locally first. Keep known-good state to revert. |
| Asset cache serves stale CSS after deploy | Medium | Bump SW cache name. Use `?v=` busters. Document cache-clearing. |

### Serious Risks (breaks features)

| Risk | Likelihood | Mitigation |
|---|---|---|
| OWL component patch fails silently after Odoo update | Low-Medium | Pin Docker image version. Write startup health check. |
| Template inherit breaks on Odoo major update | Low (within 19.x) | Keep template inherit inventory. Test after updates. |
| web_responsive conflicts with everjust modules | Medium | Resolve before implementation: choose Option A, B, or C. |

### Cosmetic Risks (visual glitches)

| Risk | Likelihood | Mitigation |
|---|---|---|
| CSS specificity wars | Medium | Follow odoo-style-pro's patterns. Match original selector depth. |
| Third-party OCA module styling conflicts | Medium | Test all installed OCA modules after theme. |
| Print stylesheet issues (Ctrl+P) | Low | Test. `web.assets_web_print` includes backend CSS — may need `@media print` scoping. |

---

## Sources

### Primary Sources (Read Directly)

- Odoo 19.0 source code (`github.com/odoo/odoo`, branch `19.0`)
  - `addons/web/static/src/scss/primary_variables.scss`
  - `addons/web/static/src/scss/bootstrap_overridden.scss`
  - `addons/web/static/lib/bootstrap/dist/css/bootstrap.css`
  - `odoo/addons/base/models/assetsbundle.py`
  - `addons/web/controllers/database.py`
  - `addons/web/views/report_templates.xml`
  - `addons/web/__manifest__.py`
  - `addons/html_editor/static/src/scss/html_editor.variables.scss`
- OCA/web repository (`github.com/OCA/web`, branch `19.0`)
  - `web_responsive/__manifest__.py` and full module source
- pantalytics/odoo-style-pro (`github.com/pantalytics/odoo-style-pro`)
  - Full module source (18 SCSS files, 5 JS files, 3 Python models)
- Tabler (`github.com/tabler/tabler`)
  - `package.json`, `scss/_core.scss`, `scss/_variables.scss`
- User's repo (`/Users/cloudaistudio/Desktop/ww.everjust.app/`)
  - `addons/everjust_brand/` (all files)
  - `addons/everjust_theme/` (all files)
  - `deployment/odoo.conf`

### Secondary Sources (Web Research)

- GNU LGPL-3 FAQ and SaaS loophole analysis (gnu.org, mend.io, revenera.com)
- Flectra vs Odoo lawsuit documentation (odoo.com, flectrahq.com)
- Clean-room legal precedent (Compaq v IBM, Oracle v Google, Computer Associates v Altai)
- AI clean-room analysis (Heather Meeker, Simon Willison, chardet 7.0.0 case)
- ERPClaw case study (erpclaw.ai, hackernoon.com)
- Odoo Community vs Enterprise comparisons (cybrosys.com, gloriumtech.com, odoo.com)
- OCA module statistics (github.com/OCA, odoo-community.org)
- Addy Osmani on AI agent specifications (addyosmani.com)
- OEC.sh Odoo hosting platform (oec.sh)
- WebKul, SoftHealer, IT Projects Labs debranding modules (apps.odoo.com)

### Quantitative Data Sources

- Odoo 19 codebase metrics: `cloc` analysis of `odoo/odoo` repo
- User repo metrics: `cloc` analysis of local repo
- GitHub API: star/fork/commit counts
- Odoo App Store: module count statistics
- OCA GitHub: repository and contributor counts
