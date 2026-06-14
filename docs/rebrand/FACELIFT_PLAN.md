# UI/UX Facelift Plan

## Architecture Decision: Pure Custom SCSS (Not Tabler)

### Why Not Tabler

Tabler was the initial recommendation, but technical verification proved it incompatible:

1. **Odoo uses libsass** (old C implementation) — no `@use`/`@forward` support
2. **Import resolution mismatch** — Tabler's `@import "bootstrap/scss/functions"` expects `node_modules/` paths; Odoo's custom importer expects addon-relative paths
3. **Bootstrap version gap** — Tabler requires 5.3.7; Odoo ships 5.3.3
4. **Pre-compiled CSS fallback** adds 536KB of bloat with scoping complexity

### Why Pure Custom SCSS

Proven by `pantalytics/odoo-style-pro` (Odoo 19, LGPL-3, actively maintained):
- Complete facelift in **2,250 lines of SCSS** — no dependencies
- Uses **CSS custom properties** (`--pan-*` tokens) instead of fragile SCSS variable mutation
- **Does NOT touch `web._assets_primary_variables`** for styling — only uses it for the minimum (brand colors, fonts)
- Runtime-configurable via JS service that injects tokens from `ir.config_parameter`
- Explicitly guards `.oi` and `.fa` icon font families with `!important`

---

## Design System

### Colors

| Token | Value | Purpose |
|---|---|---|
| `--ej-accent` | `#000000` | Primary action color (buttons, links, active states) |
| `--ej-accent-hover` | `#1a1a1a` | Hover variant |
| `--ej-bg` | `#ffffff` | Page background |
| `--ej-surface` | `#f8f9fa` | Card/sheet background |
| `--ej-border` | `#e5e5e5` | Borders |
| `--ej-text` | `#111111` | Body text |
| `--ej-text-muted` | `#6b7280` | Secondary text |
| `--ej-navbar-bg` | `#000000` | Top navbar |
| `--ej-navbar-text` | `#ffffff` | Navbar text |
| `--ej-success` | `#16a34a` | Success states |
| `--ej-warning` | `#f59e0b` | Warning states |
| `--ej-danger` | `#dc2626` | Error states |
| `--ej-info` | `#0284c7` | Info states |
| `--ej-radius` | `6px` | Border radius |
| `--ej-radius-lg` | `10px` | Large radius (cards, modals) |
| `--ej-shadow` | `0 1px 3px rgba(0,0,0,.08)` | Default shadow |
| `--ej-shadow-lg` | `0 4px 12px rgba(0,0,0,.1)` | Elevated shadow |
| `--ej-transition` | `150ms ease` | Default transition |

### Fonts

| Role | Font | Weight | Source |
|---|---|---|---|
| Body / UI | Inter | 400, 500, 700 | Self-hosted WOFF2 |
| Headings | DM Sans | 700 | Self-hosted WOFF2 |
| Monospace | JetBrains Mono | 400 | Self-hosted WOFF2 |

SCSS variable overrides (in `web._assets_primary_variables`):
```scss
$o-font-family-sans-serif: 'Inter', -apple-system, sans-serif !default;
$o-headings-font-family: 'DM Sans', -apple-system, sans-serif !default;
$o-font-family-monospace: 'JetBrains Mono', monospace !default;
```

Critical: preserve icon font families:
```scss
.oi { font-family: 'odoo_ui_icons' !important; }
.fa { font-family: 'FontAwesome' !important; }
```

### Icons

**Keep FontAwesome 4.7.** FA is deeply embedded in XML `icon=` attributes, inline elements, and JS strings across every module. It is not branded as "Odoo." Replacing it would break virtually every module for no debranding benefit.

For new custom UI elements, use Bootstrap Icons (2,000+, MIT, already compatible with Bootstrap 5.3.3) or Tabler Icons as a standalone SVG set (not compiled via SCSS).

---

## Module Structure

```
addons/everjust_theme/
├── __manifest__.py                    # depends: web
├── models/
│   ├── __init__.py
│   ├── ir_http.py                     # Inject --ej-* tokens via session_info()
│   └── res_config_settings.py         # Optional: admin color config
├── static/
│   └── src/
│       ├── fonts/
│       │   ├── inter-latin-var.woff2
│       │   ├── dm-sans-700-latin.woff2
│       │   └── jetbrains-mono-400-latin.woff2
│       ├── scss/
│       │   ├── primary_variables.scss # $o-brand-primary, $o-brand-odoo, fonts
│       │   ├── _tokens.scss           # :root { --ej-* } design tokens
│       │   ├── _fonts.scss            # @font-face declarations + icon guards
│       │   ├── _typography.scss       # Body, headings, mono, sizes
│       │   ├── _layout.scss           # Navbar, sidebar, content area
│       │   ├── _components.scss       # Buttons, badges, inputs, cards, tables
│       │   ├── _forms.scss            # Form view: sheet, groups, notebooks
│       │   ├── _list.scss             # List view: headers, rows, sticky
│       │   ├── _kanban.scss           # Kanban: cards, columns, progress
│       │   ├── _statusbar.scss        # Pill-style (remove chevron clip-path)
│       │   ├── _chatter.scss          # Messaging thread
│       │   ├── _control_panel.scss    # Search bar, breadcrumbs, actions
│       │   ├── _modals.scss           # Dialogs
│       │   ├── _dropdowns.scss        # Dropdown menus
│       │   ├── _notifications.scss    # Toast messages
│       │   ├── _settings.scss         # Settings page
│       │   ├── _animations.scss       # Transitions, hover states
│       │   ├── _mobile.scss           # Responsive overrides
│       │   ├── _login.scss            # Login page redesign
│       │   └── theme.scss             # Master import
│       ├── js/
│       │   └── theme_service.js       # Runtime token injection
│       └── xml/
│           └── templates.xml          # Template overrides if needed
└── views/
    └── res_config_settings_views.xml  # Optional: theme settings UI
```

### Asset Bundle Targeting

```python
'assets': {
    'web._assets_primary_variables': [
        ('after', 'web/static/src/scss/primary_variables.scss',
         'everjust_theme/static/src/scss/primary_variables.scss'),
    ],
    'web.assets_backend': [
        'everjust_theme/static/src/scss/theme.scss',
        'everjust_theme/static/src/js/theme_service.js',
    ],
    'web.assets_frontend': [
        'everjust_theme/static/src/scss/_login.scss',
    ],
},
```

---

## Implementation Stages

### Stage 1: Foundation (Days 1-2)

1. SCSS variable overrides (`$o-brand-primary: #000000`, `$o-brand-odoo: #000000`, font families)
2. Design tokens (`:root { --ej-* }`)
3. `@font-face` declarations (Inter, DM Sans, JetBrains Mono)
4. Icon font guards (`.oi`, `.fa`)
5. **Verify:** Page loads with new colors and fonts. Everything else visually unchanged.

### Stage 2: Components (Days 3-5)

1. Buttons (primary → black, radius, transitions)
2. Inputs (focus glow, border styles)
3. Badges and tags (pill-style, softened colors)
4. Cards (radius, shadow, hover)
5. Tables (header styling, subtle borders)
6. Modals (radius, shadow, backdrop)
7. Dropdowns (radius, shadow, padding)
8. Notifications/toasts (left-border by type)
9. **Verify:** Open form view — buttons, inputs, tags differ. Open dialog — modal styled.

### Stage 3: Views (Days 5-8)

1. Form views (sheet bg, groups, notebooks with underline tabs)
2. List views (uppercase headers, hover highlights, sticky header/footer)
3. Kanban views (card layout, column headers, progress bars)
4. Status bar (remove chevron clip-path, rounded pills)
5. Chatter (messaging thread, composer, activities)
6. Control panel (search bar focus ring, breadcrumbs, view switcher)
7. **Verify:** CRM pipeline, contact form, and contact list all look cohesive.

### Stage 4: Layout (Days 8-10)

1. Top navbar (black bg, white text, accent active state)
2. Sidebar / app menu
3. Home screen / app grid
4. Login page (gradient bg, accent buttons, card styling)
5. **Verify:** Overall "feel" is different. Navigation is cohesive.

### Stage 5: Polish (Days 10-12)

1. CSS transitions (hover states, modal entry, dropdown animation)
2. Loading states
3. Mobile responsive (touch targets, sidebar collapse, responsive kanban)
4. **Verify:** Interactions feel smooth. Mobile is usable.

### Stage 6: QA (Days 12-14)

1. Visual regression (screenshot comparison for every key page)
2. Functional smoke tests (create lead, send email, generate PDF)
3. Brand grep (curl every page, grep for "odoo")
4. Cross-browser (Chrome, Firefox, Safari, mobile)
5. PDF verification (generate invoice, confirm it renders correctly)
6. Performance (CSS bundle size before/after)

---

## Key Patterns from odoo-style-pro

| Pattern | What It Does | Why It Matters |
|---|---|---|
| CSS custom properties | All values flow from `:root { --pan-* }` tokens | Runtime-configurable, no SCSS recompilation needed |
| No `_assets_primary_variables` for styling | Only uses it for `$o-brand-primary` and fonts | Avoids fragile SCSS variable layer |
| Icon font guards | `!important` on `.oi` and `.fa` font-family | Prevents body font from breaking icons |
| Tag softening | `background-image: linear-gradient(rgba(255,255,255,0.72)...)` | Softens inline-colored tags without knowing the color |
| Statusbar pills | Removes chevron `clip-path`, replaces with `border-radius: 9999px` | Dramatic visual improvement |
| Chatter resize | Draggable divider between form sheet and chatter | Novel UX with localStorage persistence |

---

## Conflict Resolution

### web_responsive vs everjust_home

Both replace the app launcher. Options:

- **A)** Drop `everjust_home`, adopt web_responsive's full-page app menu (more features: fuzzy search, keyboard nav, drag-and-drop)
- **B)** Keep `everjust_home`, skip web_responsive, write own responsive CSS (+2 days)
- **C)** Use web_responsive but patch out its app menu, keeping only responsive improvements

**Recommendation:** Option A — web_responsive's app menu is more feature-rich. Absorb its responsive improvements as a dependency.

### everjust_theme vs everjust_brand SCSS

Both modules have SCSS. Coordinate by:
- `everjust_brand` SCSS: only hides Enterprise upsell elements (`.o_upgrade_dialog { display: none }`)
- `everjust_theme` SCSS: all visual styling
- Load order: `everjust_brand` before `everjust_theme` (alphabetical default works)

---

## Upgrade Safety (most → least stable)

1. **SCSS variables** (`$o-brand-primary`, etc.) — guaranteed across versions
2. **CSS custom properties** (`--ej-*`) — your own namespace, fully safe
3. **Component SCSS** (`.o_*` classes) — rarely change in minor versions
4. **Data records** (`base.partner_root`) — record IDs never change
5. **Python model inheritance** — core extension mechanism, stable
6. **QWeb template overrides** — can break in major upgrades (XPath dependent)
7. **JS OWL patches** — most fragile, component APIs can change
