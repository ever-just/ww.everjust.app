# EVERJUST Rebrand: Deep Debrand + UI/UX Facelift

**Status:** Planning Complete — Ready to Build
**Confidence:** 92%
**Estimated Duration:** 2.5 weeks (debranding + facelift in parallel)
**Last Updated:** 2026-06-14

---

## What This Is

A comprehensive plan to transform the EVERJUST platform from a recognizably-reskinned Odoo into a product that looks, feels, and behaves like a completely original SaaS application. Two parallel workstreams:

1. **Deep Debranding** — Remove every trace of Odoo branding: text, dialogs, upgrade prompts, email footers, logos, colors, icons, and technical headers
2. **UI/UX Facelift** — New design system with custom fonts, design tokens, restyled components, modernized views, and responsive mobile experience

## Why This Matters

- **Brand Identity:** Tenants pay for EVERJUST, not "Odoo with a different logo." Every "Odoo Session Expired" dialog or "Upgrade to Enterprise" prompt undermines trust.
- **Competitive Differentiation:** A distinctive UI separates EVERJUST from the thousands of white-label Odoo deployments that all look the same.
- **Tenant Confidence:** Enterprise upsell prompts make tenants question whether they're using an incomplete product. Removing them removes doubt.
- **Valuation / IP:** While the LGPL-3 license doesn't constrain SaaS deployments, a fully differentiated product presentation increases perceived (and real) value.

## Desired End State

When this work is complete:

1. **No user — admin, employee, or portal visitor — will ever see the word "Odoo"** in the UI, emails, PDFs, browser tabs, notifications, or error messages
2. **No upgrade prompts, Enterprise teasers, or Odoo.com links** will appear anywhere in the application
3. **The visual design will be distinctly different** from default Odoo: different fonts, colors, component styling, spacing, animations, and layout patterns
4. **The backend Python/ORM will be completely untouched** — all changes are frontend-only (SCSS, JS, XML templates, data records)
5. **PDF reports will continue to render correctly** — the report CSS pipeline is confirmed separate from the backend theme
6. **Mobile experience will be usable** with appropriate touch targets and responsive layouts
7. **The platform will feel like a product built from scratch**, not a framework with a theme applied

## What Success Looks Like

### Quantitative
- Zero instances of "Odoo" in any rendered page (login, backend, portal, email, PDF)
- `branding_lint.sh` and `debrand_check.sh` pass with zero findings
- CSS bundle size increase < 60KB over baseline
- No `!important` count increase > 50% over odoo-style-pro's baseline

### Qualitative
- A new user shown the product cannot identify it as Odoo-based
- The design feels cohesive — every view uses the same font, color, and component language
- Navigation feels intentional, not "default framework with overrides"
- Mobile is usable for checking CRM, contacts, and calendar on a phone

## File Index

| File | Purpose |
|---|---|
| [README.md](README.md) | This file — overview, goals, success criteria |
| [DEBRANDING_PLAN.md](DEBRANDING_PLAN.md) | Complete inventory of 53 branding touchpoints with priorities, techniques, and effort |
| [FACELIFT_PLAN.md](FACELIFT_PLAN.md) | UI/UX architecture, component library decision, module structure, implementation stages |
| [SOURCES_AND_ASSUMPTIONS.md](SOURCES_AND_ASSUMPTIONS.md) | Research sources, verified facts, remaining unknowns, and risk register |
| [VERIFICATION_RESULTS.md](VERIFICATION_RESULTS.md) | Results of 10 technical verifications against Odoo 19 source code |
