# EVERJUST.APP — Site Revamp & Conversion Strategy

**Goal:** turn an underwhelming brochure site into a spectacular, competitive,
conversion-optimized product site — mirroring the *proven UX patterns* of
best-in-class all-in-one suites (Odoo, monday, HubSpot, Zoho One) while staying
100% EVERJUST-branded and original.

> Status: PLAN — decisions locked (see below). Build in progress.

### Decisions locked (2026-06-13)
- **D1 Pricing:** Reframe the flat plan + add a "cut your software bill"
  savings calculator. **No Stripe rework.**
- **D2 Mirror scope:** Mirror Odoo's *patterns/IA*; original EVERJUST copy &
  assets; zero Odoo branding (CI-enforced).
- **D3 Lead capture:** Dogfood — leads flow into our own EVERJUST CRM tenant
  (fallback: Postgres + email).
- **D4 Analytics/chat:** Self-hosted, privacy-first **analytics only** for now
  (Plausible/Umami, consent-aware); chat deferred.

---

## 0. Decisions to lock first (they change the architecture)

These are business/brand calls, not design details. The build branches on them.

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | **Pricing model** | A) Adopt Odoo's *structure* (Free 1-app · Standard all-apps/user · Custom +advanced/user, monthly/annual) with **our own numbers**. B) Keep flat $100/5-users +$15/user but **reframe & sell it harder**. C) Hybrid: flat base + a "replaces $N of tools" savings calculator. | **C** short-term (no Stripe rework, big perceived-value lift), with **A** as a fast-follow if we want per-app expansion revenue. |
| D2 | **"Mirror Odoo" scope** | Mirror their **page structure, IA, and interaction patterns** with **original copy + original/abstract visuals and zero Odoo branding** — vs literally copying their pages. | **Patterns + original assets.** Copying their copy/screenshots is a copyright + brand-leak risk and undoes the debranding work. Our `branding_lint` already blocks "odoo" leaks; keep it. |
| D3 | **Lead-capture backend** | A) Dogfood: form posts to control-plane → creates a lead in **our own EVERJUST CRM tenant**. B) Simple: store in Postgres + email `company@everjust.co`. C) Third-party (HubSpot free). | **A** (dogfooding the product *is* the pitch), with **B** as the v1 fallback. |
| D4 | **Analytics + chat** | Privacy-first self-hosted (**Plausible/Umami** + **Chatwoot**) vs GA4 + Intercom vs none. | **Self-hosted, consent-aware** — matches our privacy positioning and the cookie-consent system already shipped. |

§8 (pricing) and §6 (lead capture) detail each path.

---

## 1. Audit — why it currently underwhelms

Objective findings from the live site (everjust.app):

- **App coverage is thin.** Tenants get the full open-source suite (~30–40 apps:
  CRM, Sales, Invoicing, Subscriptions, Rental, POS, Purchase, Inventory,
  Manufacturing, Project, Timesheets, Field Service, Maintenance, Employees,
  Recruitment, Time Off, Appraisals, Expenses, Fleet, Payroll, Email/SMS
  Marketing, Events, Surveys, Website, eCommerce, Blog, Forum, eLearning, Live
  Chat, Documents, Sign, Knowledge, Discuss, Calendar, Approvals, VoIP…).
  The site markets **only 8**. Massive perceived-value gap.
- **No catalog taxonomy.** No categories, no search/filter, no "view all apps."
- **Hero is static.** A single non-animated mock; no product motion, no demo, no
  interactive app grid, no proof. Doesn't show the product *working*.
- **Pricing is one flat card.** No calculator, no comparison, no ROI/savings
  framing, no anchoring. Reads as cheap, not valuable.
- **Zero interactivity / engagement.** No product tour, no embedded demo, no
  calculator, no configurator, no video, no before/after.
- **Weak lead capture.** Only "sign up." No "book a demo," no email capture, no
  lead magnet, no chat, no newsletter, no exit-intent.
- **Value prop is feature-listy, not outcome-led.** Lists what apps *are*, not
  the business outcomes or the "replace your $X stack" story. No social proof.
- **Detail/sub-pages are template-uniform.** No screenshots, no real depth.
- **No measurement.** No analytics, no funnel instrumentation, no SEO baseline,
  so we're flying blind on conversion and understandability.

---

## 2. Research plan — what, how, where, and what we do with it

### 2a. Competitive & pattern research
- **Targets:** Odoo (home, /pricing, app pages, app store taxonomy), monday.com,
  HubSpot, Zoho One, Notion, Linear & Stripe (craft/interaction benchmarks),
  Bitrix24, Microsoft 365.
- **Extract (structure, NOT copy):** section sequences, interaction patterns
  (calculators, carousels, product tours, hover/scroll motion), pricing
  mechanics, lead-capture flows, trust/social-proof patterns, copy *frameworks*
  (JTBD, PAS, outcome headlines), app-catalog taxonomies.
- **How/where:** `WebFetch` for structural teardown (already started — see
  appendix), Playwright to **screenshot** competitor flows for a visual swipe
  file, the **deep-research** skill for fact-checked market claims and
  competitor pricing, keyword tools for SEO demand.
- **Output → action:** a *pattern library* + *swipe file* → translated into
  **original EVERJUST components**. A *category taxonomy* → drives the app
  catalog. A *keyword map* → drives page/section targeting and comparison pages.

### 2b. Product/app inventory research (internal)
- Enumerate the **actual installed + installable modules** per tenant (audit
  `provisioning.py` + the Odoo Community app registry).
- For each app: name, category, one-line JTBD, 3 key features, a screenshot, an
  honest "what it replaces" mapping (e.g., CRM↔Salesforce/HubSpot).
- **Output → action:** the structured `content.py` catalog powering the apps
  index, per-app pages, and the savings calculator.

### 2c. Audience & message research
- Define ICP(s) and Jobs-To-Be-Done; mine real buyer language (review sites,
  forums, search queries) for the words customers actually use.
- **Output → action:** positioning statement, message hierarchy, and the copy
  for hero/pricing/app pages.

---

## 3. Positioning & messaging — making it *sell*

- **Core promise (draft):** "Run your whole company in one place — and stop
  paying for ten tools that don't talk to each other." Owned, isolated data;
  flat, predictable price; live in minutes; no lock-in.
- **Differentiators to hammer:** (1) all-in-one vs point tools; (2) flat price
  vs per-seat-per-tool creep; (3) your own private database + address; (4) no
  lock-in / export anytime; (5) instant provisioning.
- **Frameworks:** outcome-led headlines, Problem-Agitate-Solve, Before-After-
  Bridge, quantified value ("replace ~$X/mo of software"), and proof beside
  every claim.
- **Test:** 5-second comprehension tests + message A/B on the hero.

---

## 4. Information architecture (new sitemap)

```
/                     Home (redesigned, interactive)
/apps                 App catalog — searchable, filter by category
/apps/<app>           Per-app page (richer: demo, screenshots, use cases)
/solutions/<role>     Solutions by role/industry (CRM for sales teams, etc.)
/pricing              Plans + interactive savings/ROI calculator
/compare/<x>          "EVERJUST vs <competitor>" SEO pages
/resources            Docs (have) + guides + blog
/demo                 Book-a-demo / interactive product tour
/about, /contact, /privacy (have)
```

- **App taxonomy** (mirrors proven category grouping, populated from *our* real
  modules): Finance · Sales · Operations · HR · Marketing · Website ·
  Productivity · Communication.

---

## 5. Page-by-page redesign blueprint

### Home (the centerpiece)
1. **Hero** — outcome headline + product motion (looping product preview or
   interactive app-grid that previews an app on hover/tap) + dual CTA
   (Start free / Book demo) + trust strip.
2. **"Replaces your stack"** — animated logos of tools we replace + calculator
   teaser ("see what you'd save →").
3. **App catalog carousel by category** — all apps, not 8, grouped, swipeable.
4. **Feature showcases** — 3–4 alternating sections, each with an **embedded
   demo** (GIF/short video/interactive hotspot) showing the product working.
5. **Outcomes / ROI** — quantified value + (later) real metrics.
6. **Social proof** — logos, stats, testimonial carousel (as we earn them).
7. **Interactive moment** — product tour or "build your workspace" configurator.
8. **Pricing teaser → FAQ → final CTA band.**

### Apps index — searchable, filterable catalog (category tabs + search).
### App detail — screenshots/demo, feature deep-dive, "what it replaces," use
cases, related apps, in-context CTA, FAQ, structured data.
### Pricing — plan cards + **interactive calculator** (pick the tools you'd
replace → live savings; user slider; monthly/annual toggle) + comparison + FAQ.
### Solutions/compare pages — SEO + persona-targeted.

---

## 6. Engagement & lead capture

- **CTA ladder:** Start free · Book a demo · Get a workspace plan (3 intents).
- **Lead magnets:** ROI/savings calculator (optionally email-gated for the full
  report), "build your workspace" configurator, downloadable guides, newsletter.
- **Mechanisms:** inline forms, sticky CTA bar, exit-intent modal, scheduling
  embed (Cal.com self-hosted), live chat (Chatwoot self-hosted), all
  **consent-aware** via the cookie system already shipped.
- **Backend (per D3):** form → control-plane endpoint → lead stored + (ideally)
  pushed into our **own EVERJUST CRM tenant** (dogfooding) + notification email.

---

## 7. Interactivity & "spectacular" — libraries (all MIT/ISC, vendored)

| Need | Library | Why |
|---|---|---|
| Carousels / app rails | **Swiper** | Touch, accessible, no jank |
| Product/feature motion | **Lottie-web** | Crisp vector animation, light |
| Scroll reveal | (already have, IntersectionObserver) | Keep, tasteful |
| Product tour | **Shepherd.js** | Guided clickable tour |
| Calculator viz | **Chart.js** | Savings/ROI charts |
| Light interactivity | **Alpine.js** | Reactivity without a SPA/build step |
| Scheduling | **Cal.com** embed | Book-a-demo |
| Live chat | **Chatwoot** (self-host) | Privacy-friendly |
| Analytics | **Plausible/Umami** (self-host) | Consent-aware, lightweight |

Guardrail: **performance budget** — lazy-load demos, keep Core Web Vitals green;
interactivity must not tank LCP/INP.

---

## 8. Pricing strategy & calculator (branches on D1)

- **Option C (recommended first):** keep the flat plan but **reframe** with a
  "Cut your software bill" calculator: user checks the tools they pay for today
  → live total → vs EVERJUST flat price → **annual savings**. Massive perceived
  value, **zero Stripe changes**.
- **Option A (fast-follow):** restructure into Free (1 app) / Standard (all
  apps, $X/user) / Custom (+advanced, $Y/user) with monthly/annual toggle —
  mirrors the proven model, adds expansion revenue. **Requires Stripe product +
  webhook + provisioning rework** (staged, tested, feature-flagged).
- Either way: build the calculator, plan cards with anchoring, and a 10–12 item
  pricing FAQ accordion.

---

## 9. SEO & indexability

- **Technical (build on what's shipped):** sitemap ✓, canonical ✓, Org/SoftwareApp
  JSON-LD ✓ → **add** `Product`, `FAQPage`, `BreadcrumbList`, per-app
  `SoftwareApplication`, and `Offer` schema. Lighthouse CI for Core Web Vitals.
  Image optimization + lazy-load. Pre-render/SSR is already server-rendered ✓.
- **Content:** keyword research → per-app and per-category landing SEO,
  **"alternative to <X>"** and **"<competitor> vs EVERJUST"** pages, a resources/
  blog for top-of-funnel.
- **Measurement:** Search Console + sitemap submission + indexation tracking +
  rank tracking on target keywords.

---

## 10. Success metrics — objective & instrumented

**Instrument first** (privacy-friendly analytics + event tracking), then target.

- **Conversion funnel:** visit → signup-start → checkout → provisioned; measure
  per-step drop-off. Track CTA clicks, calculator usage, app-page views, demo
  plays, form starts/completes.
- **Understandability:** 5-second tests, Flesch readability scores, moderated
  task-success usability tests, consent-aware heatmaps/session replay.
- **Indexability:** % pages indexed, Core Web Vitals pass rate, Lighthouse SEO
  score (target ≥95), keyword rankings.
- **Experimentation:** A/B test hero, pricing presentation, and primary CTA.
- **Baselines & targets:** capture current numbers in week 1; set targets per
  funnel step after baseline (e.g., +X% signup-start rate, ≥95 Lighthouse).

---

## 11. Agent skills / tools / repos needed

- **Skills:** `deep-research` (market/competitor/keyword research),
  `frontend-design` (already applied), `webapp-testing` (verify interactive
  flows in a real browser), `run`/`verify` (drive the app + screenshots),
  `code-review` (quality gate), `brand-guidelines`/`theme-factory` (design
  system).
- **Tools:** `WebSearch`/`WebFetch` (research), **Playwright** (competitor
  screenshots, visual QA, automated interaction tests), **Lighthouse** (perf/SEO
  baselines).
- **Repos/libs:** Swiper, Lottie-web, Shepherd.js, Chart.js, Alpine.js,
  Plausible/Umami, Chatwoot, Cal.com (all vendored, permissively licensed).

---

## 12. Phased roadmap (each phase = PR → CI → deploy, as today)

- **Phase 0 — Decisions (D1–D4)** *(blocks the rest)*.
- **Phase 1 — Research & baseline:** deep-research sprint, competitor swipe file,
  keyword map, analytics + Lighthouse baseline.
- **Phase 2 — IA + content model:** full app taxonomy from real modules,
  positioning/messaging, expanded `content.py`.
- **Phase 3 — Design system + Home redesign + core interactivity** (hero motion,
  app carousel, scroll craft).
- **Phase 4 — App catalog + per-app pages + solutions/compare pages.**
- **Phase 5 — Pricing + savings calculator** (+ Stripe rework if Option A).
- **Phase 6 — Lead capture + chat + scheduling + analytics instrumentation +
  SEO structured data/keyword pages.**
- **Phase 7 — Measure, A/B test, iterate.**

---

## 13. Risks & guardrails

- **IP / brand:** mirror *patterns*, not content; original copy + assets; keep
  **zero Odoo references** (enforced by `branding_lint` in CI).
- **Pricing change = billing risk:** any Stripe/provisioning change is staged,
  feature-flagged, and tested end-to-end before going live.
- **Perf vs interactivity:** strict JS/perf budget; lazy-load; keep CWV green.
- **Privacy:** analytics/chat must be consent-gated (cookie system already live).

---

## Appendix A — Competitor structural teardown (research already started)

**Odoo home (pattern skeleton):** sticky nav by category → hero w/ pricing
callout + CTA → advisor/booking → app-grid carousel (20+) → value narrative w/
exec quote → feature showcases w/ embedded demos → AI section → 6-col benefits
grid → big user-count stat → testimonial carousel → final free-trial CTA →
multi-column footer. *Interactions:* app carousel, animated product GIFs,
appointment scheduler, live chat, testimonial carousel.

**Odoo pricing (model mechanics):** 3 tiers (Free 1-app / all-apps-per-user /
+advanced-per-user), monthly↔annual toggle, and a **savings calculator** —
pick the competitor tools you'd replace + user count → live "you save $X/yr."
FAQ accordion. *Takeaway for us:* the savings calculator is the single
highest-leverage borrowed mechanic; build an original version in Phase 5.
