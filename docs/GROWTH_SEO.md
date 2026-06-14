# Growth / SEO plan

Where everjust.app stands on SEO and what moves the needle next. On-page
technical SEO is in good shape; the remaining levers are off-site and content,
most of which need an account or a decision from the owner.

## Done (on-page / technical)
- Canonical URLs, per-page titles + unique meta descriptions, `robots` directives.
- Open Graph + Twitter cards on every page; per-page social images; `og:locale`,
  per-type `og:type` (articles for docs).
- Structured data: `Organization` (+ contactPoint), `WebSite`, `SoftwareApplication`
  (per app), `Product` (pricing), `FAQPage` (landing), and `BreadcrumbList` on apps,
  app detail, pricing, and docs.
- `sitemap.xml` + `sitemap.txt` (all indexable routes), `robots.txt` → sitemap.
- Performance/CWV: gzip, self-hosted fonts with preload, asset versioning, PWA,
  mobile-first responsive. (Core Web Vitals are a ranking factor — keep them green.)

## Needs the owner (off-site / accounts) — highest leverage
1. **Search Console + Bing Webmaster.** Verify ownership and submit the sitemap so
   pages actually get crawled/indexed. I can drop a verification `<meta>` tag the
   moment you paste the token; you do the submit.
2. **Real social profiles.** If EVERJUST has X/LinkedIn/etc., send the URLs and I'll
   add them to `Organization.sameAs` (helps entity/knowledge-panel association). Don't
   want to invent any.
3. **Backlinks.** SaaS directories and "all-in-one business software" / "self-hosted
   Odoo alternative" listings, plus the two live tenants (HeadsUp, TCSW) as linked
   case studies *with their permission*. This is the biggest off-page lever.

## Content engine (needs topic + claim sign-off, then I build)
A `/blog` or `/guides` section targeting real search intent is the durable growth
play. I can build the engine (data-driven like the app catalog, same design system)
quickly; the gating item is **content that's literally true** — so I need direction:
- **Comparison/alternative pages** ("running your business on one workspace vs N point
  tools") — high intent, but every claim must be accurate to what we actually ship.
- **Industry guides** mapped to the personalization industries we already support.
- **"How-to" guides** that extend the existing docs (already strong) outward to search.

Tell me 3–5 topics (or approve a proposed set) and I'll draft them in the brand voice
for your review before anything publishes.

## Guardrails
- No fabricated stats, ratings, testimonials, or `aggregateRating` markup — it violates
  the brand-voice "every claim literally true" rule and risks structured-data penalties.
- Keep the debrand lint green: no upstream vendor name in any published content.
