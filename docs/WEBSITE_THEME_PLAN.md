# Website Theme Plan — HeadsUp (and future tenants)

## Problem

The HeadsUp website at `headsup.everjust.app` currently serves a standalone Next.js/Vercel site that completely bypasses Odoo's website engine. This means:
- No login/sign-in link in the header
- No portal access for customers (`/my`)
- No website builder (drag-and-drop editing)
- No blog, forms, event pages, e-commerce
- No SEO tools, contact forms → CRM leads
- No integration with any Odoo app

## Goal

Rebuild the HeadsUp website as a proper Odoo website theme module (`website_headsup`) that:
1. Recreates the HeadsUp brand (green palette, layout, copy)
2. Uses Odoo's `website.layout` so header/footer/nav/login work natively
3. Is fully editable via the Odoo website builder
4. Supports portal login, blog, forms, events
5. Serves as a template for how future tenants build their websites

## Design Tokens (from current HeadsUp site)

| Token | Value |
|---|---|
| Primary color | `rgb(22, 106, 11)` — green |
| Primary darker | `rgb(14, 69, 7)` |
| Primary lighter | `rgb(30, 143, 15)` |
| Secondary | `rgb(142, 165, 141)` |
| Background | white |
| Contrast text | white |
| Border radius | 8px |
| Typography | System fonts (to be replaced with brand fonts) |

## Module Structure

```
addons/website_headsup/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── menu.xml                    # Website menu items (Home, Services, About, Contact)
│   └── pages/
│       └── home.xml                # Homepage content
├── static/
│   ├── description/
│   │   └── icon.png               # App icon
│   ├── src/
│   │   ├── img/                    # Hero images, service icons, team photos
│   │   ├── js/
│   │   │   └── theme.js           # Scroll effects, navbar transparency
│   │   └── scss/
│   │       ├── primary_variables.scss  # Color palette + fonts (loaded before Bootstrap)
│   │       ├── bootstrap_overridden.scss  # Border radius, shadows
│   │       ├── font.scss           # Google Fonts import
│   │       └── theme.scss          # Custom component styles
│   └── snippets/                   # Custom building blocks for the builder
│       ├── s_headsup_hero/
│       ├── s_headsup_services/
│       ├── s_headsup_testimonial/
│       └── s_headsup_cta/
└── views/
    ├── website_templates.xml       # Header, footer, layout overrides
    ├── snippets.xml                # Register snippets in the builder
    └── portal_templates.xml        # Portal page customizations (optional)
```

## Manifest

```python
{
    "name": "HeadsUp Website Theme",
    "version": "19.0.1.0.0",
    "category": "Website/Theme",
    "summary": "Custom website theme for Heads Up Outdoor Services",
    "author": "EVERJUST",
    "license": "LGPL-3",
    "depends": ["website"],
    "data": [
        "data/menu.xml",
        "data/pages/home.xml",
        "views/website_templates.xml",
        "views/snippets.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            ("prepend", "website_headsup/static/src/scss/primary_variables.scss"),
        ],
        "web._assets_frontend_helpers": [
            "website_headsup/static/src/scss/bootstrap_overridden.scss",
        ],
        "web.assets_frontend": [
            "website_headsup/static/src/scss/font.scss",
            "website_headsup/static/src/scss/theme.scss",
            "website_headsup/static/src/js/theme.js",
        ],
    },
    "application": False,
}
```

## Implementation Steps

### Step 1: Color Palette + Fonts (SCSS)

`primary_variables.scss` — define the HeadsUp green palette using Odoo's color system:
- `o-color-1`: white (background)
- `o-color-2`: light gray (#f8f8f8)
- `o-color-3`: HeadsUp green (#166A0B)
- `o-color-4`: dark green (#0E4507)
- `o-color-5`: secondary (#8EA58D)

Register fonts via `$o-theme-font-configs` for website builder integration.

### Step 2: Header with Login

`views/website_templates.xml` — inherit `website.layout`, customize the navbar:
- HeadsUp logo on the left
- Menu items: Home, Services, About, Contact
- **Sign In** link on the right (via `portal.placeholder_user_sign_in`)
- User dropdown when logged in (via `portal.user_dropdown`)
- Green background with white text
- Transparent → solid on scroll (JS)

### Step 3: Homepage

`data/pages/home.xml` — replace the default homepage with:
- Hero section (big heading, CTA button, background image)
- Services grid (lawn care, landscaping, snow removal, etc.)
- Why choose us / testimonials
- Contact form (auto-creates CRM lead)
- Footer with company info, links, social icons

All sections use `oe_structure` class so they're editable in the website builder.

### Step 4: Footer

Inherit `website.footer_default` or create custom:
- Company name, address, phone
- Quick links
- Social media icons
- "Powered by EVERJUST.APP" (optional)

### Step 5: Custom Snippets

Build reusable building blocks for the website builder:
- `s_headsup_hero` — full-width hero with image + CTA
- `s_headsup_services` — service cards grid
- `s_headsup_testimonial` — customer quote card
- `s_headsup_cta` — call-to-action banner

Register each in the snippet panel so the user can drag them onto any page.

### Step 6: Remove the Old Next.js Site

The current `headsup_website` module (if it exists on the server) needs to be uninstalled. The Odoo website module should serve the pages directly.

### Step 7: Portal Pages

The portal (`/my`) automatically works once the website theme is in place. Customers can:
- View invoices at `/my/invoices`
- View projects at `/my/tasks`
- Sign documents at `/my/sign` (via sign_oca)
- Download files at `/my/documents` (via DMS portal)

## What the User Gets

| Feature | Before (Next.js) | After (Odoo Theme) |
|---|---|---|
| Custom design | Yes | Yes — same brand, rebuilt in Odoo |
| Login / Sign In | No | Yes — native in header |
| Website builder | No | Yes — drag-and-drop editing |
| Portal (invoices, projects) | No | Yes — `/my` |
| Blog | No | Yes — install `website_blog` |
| Contact form → CRM | No | Yes — native |
| SEO tools | No | Yes — per-page meta tags, sitemap |
| E-commerce | No | Yes — install `website_sale` |
| Event pages | No | Yes — install `website_event` |
| Multi-language | No | Yes — built-in |
| Mobile responsive | Yes | Yes — Bootstrap 5 |

## Estimated Effort

| Task | Time |
|---|---|
| SCSS palette + fonts | 1 hour |
| Header + footer templates | 2 hours |
| Homepage recreation | 3-4 hours |
| Custom snippets (4) | 2-3 hours |
| JS scroll effects | 1 hour |
| Testing + polish | 2 hours |
| **Total** | **~1-2 days** |

## For Future Tenants

This module serves as the template. When a new tenant wants a custom website:
1. Copy `website_headsup` → `website_<tenant>`
2. Change colors in `primary_variables.scss`
3. Replace images and copy
4. Install on the tenant's database

The Odoo website builder lets tenants further customize pages without code changes.
