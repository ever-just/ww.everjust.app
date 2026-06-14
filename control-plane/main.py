# -*- coding: utf-8 -*-
"""EVERJUST.APP control plane.

Public site (landing, signup, sign-in), Stripe billing, and tenant
provisioning. Runs at everjust.app (root); tenant workspaces live at
<org>.everjust.app.
"""
import datetime
import os
import pathlib
import time

import stripe
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.gzip import GZipMiddleware

import content
import provisioning
import signup_store

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "price_1TflJNKL0p3ve1jHbCLlDNWS")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "everjust.app")

# Cookieless, privacy-first analytics. Set ANALYTICS_DOMAIN to the site's
# domain registered in a (hosted or self-hosted) Plausible-compatible instance
# to switch it on; unset = no analytics script is emitted at all.
ANALYTICS_DOMAIN = os.environ.get("ANALYTICS_DOMAIN", "")
ANALYTICS_SRC = os.environ.get("ANALYTICS_SRC", "https://plausible.io/js/script.js")

BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Cache-busting token appended to static asset URLs (?v=...). A new value
# per process start means every deploy invalidates stale service-worker
# and browser caches — fixes phones pinning old CSS/JS after a release.
ASSET_VERSION = os.environ.get("ASSET_VERSION") or str(int(time.time()))

app = FastAPI(title="EVERJUST.APP", docs_url=None, redoc_url=None, openapi_url=None)
# Compress text responses (HTML/CSS/JS/SVG/JSON) for clients that accept it.
# Cuts the homepage's CSS+JS transfer ~75% (e.g. Bootstrap CSS 233KB -> ~30KB).
app.add_middleware(GZipMiddleware, minimum_size=512, compresslevel=6)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Documentation pages: slug -> sidebar metadata, grouped into sections.
# Order defines the sidebar and prev/next links. Static pages have a
# template at templates/docs/<slug>.html; guide-* pages render from
# content.APP_GUIDES via templates/docs/_guide.html.
_STATIC_DOCS = {
    "getting-started": {
        "title": "Getting started", "icon": "rocket",
        "blurb": "Create your workspace, sign in, and find your way around.",
    },
    "invite-team": {
        "title": "Invite your team", "icon": "user-plus",
        "blurb": "Add users, set per-app access rights, manage seats.",
    },
    "mobile-app": {
        "title": "Use it on your phone", "icon": "smartphone",
        "blurb": "Install the workspace on iPhone or Android.",
    },
    "billing": {
        "title": "Billing", "icon": "credit-card",
        "blurb": "Pricing, promo codes, invoices, and cancellation.",
    },
    "security": {
        "title": "Security & data", "icon": "shield-check",
        "blurb": "Isolation, encryption, backups, and data ownership.",
    },
}

_GUIDE_DOCS = {
    slug: {"title": g["title"], "icon": g["icon"], "blurb": g["blurb"]}
    for slug, g in content.APP_GUIDES.items()
}

DOCS_SECTIONS = [
    ("Start here", ["getting-started", "invite-team", "mobile-app"]),
    ("App guides", list(content.APP_GUIDES.keys())),
    ("Account", ["billing", "security"]),
]

# Flat, ordered map used for prev/next links and the sitemap.
DOCS_PAGES = {}
for _title, _slugs in DOCS_SECTIONS:
    for _slug in _slugs:
        DOCS_PAGES[_slug] = {**_STATIC_DOCS, **_GUIDE_DOCS}[_slug]


def render(request: Request, name: str, status_code: int = 200, **ctx) -> HTMLResponse:
    ctx.setdefault("domain", BASE_DOMAIN)
    ctx.setdefault("year", datetime.date.today().year)
    ctx.setdefault("docs_pages", DOCS_PAGES)
    ctx.setdefault("docs_sections", DOCS_SECTIONS)
    ctx.setdefault("apps", content.APPS)
    ctx.setdefault("categories", content.CATEGORIES)
    ctx.setdefault("apps_by_category", content.apps_by_category())
    ctx.setdefault("calculator_tools", content.CALCULATOR_TOOLS)
    ctx.setdefault("asset_v", ASSET_VERSION)
    ctx.setdefault("analytics_domain", ANALYTICS_DOMAIN)
    ctx.setdefault("analytics_src", ANALYTICS_SRC)
    return templates.TemplateResponse(
        request=request, name=name, context=ctx, status_code=status_code
    )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    # Static assets are content-addressed via the ?v= cache-buster, so they
    # can be cached aggressively. sw.js/manifest set their own headers.
    path = request.url.path
    if path.startswith("/static/"):
        response.headers.setdefault("Cache-Control", "public, max-age=31536000, immutable")
    return response


# ── Pages ────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return render(request, "landing.html")


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return render(request, "signup.html")


@app.get("/signin", response_class=HTMLResponse)
def signin_page(request: Request):
    return render(request, "signin.html")


@app.get("/login")
def login_alias():
    return RedirectResponse("/signin", status_code=307)


@app.get("/offline", response_class=HTMLResponse)
def offline(request: Request):
    return render(request, "offline.html")


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return render(request, "privacy.html")


@app.get("/sitemap", response_class=HTMLResponse)
def sitemap_page(request: Request):
    return render(request, "sitemap.html")


@app.get("/apps", response_class=HTMLResponse)
def apps_index(request: Request):
    return render(request, "apps/index.html")


@app.get("/pricing", response_class=HTMLResponse)
def pricing(request: Request):
    return render(request, "pricing.html")


@app.get("/apps/{slug}", response_class=HTMLResponse)
def app_page(request: Request, slug: str):
    if slug not in content.APPS:
        return render(
            request, "error.html", status_code=404,
            message="That app page doesn’t exist.",
            back_url="/apps", back_label="Browse all apps",
        )
    return render(request, "apps/detail.html", slug=slug, app_data=content.APPS[slug])


@app.get("/docs", response_class=HTMLResponse)
def docs_index(request: Request):
    return render(request, "docs/index.html", active="index")


@app.get("/docs/search-index.json")
def docs_search_index():
    items = [{"slug": "", "title": "Docs overview",
              "blurb": "All EVERJUST.APP documentation.", "section": "Docs"}]
    for section_title, slugs in DOCS_SECTIONS:
        for slug in slugs:
            meta = DOCS_PAGES[slug]
            headings = [h for h, _ in content.APP_GUIDES.get(slug, {}).get("sections", [])]
            items.append({
                "slug": slug,
                "title": meta["title"],
                "blurb": meta["blurb"],
                "section": section_title,
                "headings": headings,
            })
    return {"items": items}


@app.get("/docs/{slug}", response_class=HTMLResponse)
def docs_page(request: Request, slug: str):
    if slug == "apps":  # pre-restructure URL; content now lives at /apps
        return RedirectResponse("/apps", status_code=301)
    if slug in content.APP_GUIDES:
        return render(request, "docs/_guide.html", active=slug,
                      guide=content.APP_GUIDES[slug])
    if slug not in DOCS_PAGES:
        return render(
            request, "error.html", status_code=404,
            message="That documentation page doesn’t exist.",
            back_url="/docs", back_label="Back to docs",
        )
    return render(request, f"docs/{slug}.html", active=slug)


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request, s: str = None, subdomain: str = None):
    sub = (subdomain or "").lower().strip()
    if not provisioning.validate_subdomain(sub):
        return RedirectResponse("/signup", status_code=303)
    return render(request, "welcome.html", subdomain=sub)


# ── Signup flow ──────────────────────────────────────────────────────────

def _signup_error(request: Request, message: str, step: int = 1, **form_values) -> HTMLResponse:
    # `step` tells the wizard which step the offending field lives on.
    return render(request, "signup.html", status_code=400,
                  error=message, error_step=step, **form_values)


@app.post("/signup")
def signup(request: Request,
           org_name: str = Form(...), subdomain: str = Form(...),
           email: str = Form(...), password: str = Form(...),
           industry: str = Form(""), website: str = Form(""),
           team_size: str = Form(""), goals: str = Form("")):
    org_name = org_name.strip()
    subdomain = subdomain.lower().strip()
    email = email.strip()
    # Optional onboarding context — used later to personalize the workspace.
    # Capped and sanitised; never required, never blocks checkout.
    industry = (industry or "").strip()[:60]
    website = (website or "").strip()[:200]
    team_size = (team_size or "").strip()[:20]
    goals = (goals or "").strip()[:200]
    keep = {"org_name": org_name, "subdomain": subdomain, "email": email}

    if "@" not in email or "." not in email.split("@")[-1]:
        return _signup_error(request, "Please enter a valid email address.", step=1, **keep)
    if len(password) < 8:
        return _signup_error(request, "Your password must be at least 8 characters.",
                             step=1, **keep)
    if not org_name:
        return _signup_error(request, "Please enter your organization name.", step=2, **keep)
    if not provisioning.validate_subdomain(subdomain):
        return _signup_error(
            request,
            "That workspace address can’t be used. Use 3–40 lowercase letters, "
            "numbers, or dashes (it can’t start or end with a dash).",
            step=2, **keep,
        )
    if provisioning.database_exists(subdomain):
        return _signup_error(
            request,
            f"{subdomain}.{BASE_DOMAIN} is already taken — try another address.",
            step=2, **keep,
        )

    # Keep signup details (incl. the tenant admin password) server-side;
    # only an opaque token travels through Stripe metadata.
    token = signup_store.create(org_name, subdomain, email, password,
                                industry=industry, website=website,
                                team_size=team_size, goals=goals)
    meta = {"signup_token": token, "subdomain": subdomain, "org_name": org_name}

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 5}],
            customer_email=email,
            # Let customers enter a promo code (e.g. 100%-off access codes).
            allow_promotion_codes=True,
            # If a coupon brings the total to $0, don't force card entry.
            payment_method_collection="if_required",
            success_url=f"https://{BASE_DOMAIN}/welcome?s={{CHECKOUT_SESSION_ID}}&subdomain={subdomain}",
            cancel_url=f"https://{BASE_DOMAIN}/signup",
            metadata=meta,
            # Carry tenant metadata onto the subscription so lifecycle webhooks
            # (payment_failed, subscription.deleted) can resolve the tenant.
            subscription_data={"metadata": meta},
        )
    except stripe.StripeError:
        return render(
            request, "error.html", status_code=502,
            message="We couldn’t reach our payment provider. Nothing was charged — "
                    "please try again in a minute.",
            back_url="/signup", back_label="Back to signup",
        )
    return RedirectResponse(session.url, status_code=303)


# ── APIs ─────────────────────────────────────────────────────────────────

@app.get("/api/subdomain-check")
def subdomain_check(subdomain: str = ""):
    sub = (subdomain or "").lower().strip()
    if not provisioning.validate_subdomain(sub):
        return {
            "subdomain": sub, "domain": BASE_DOMAIN,
            "valid": False, "available": False,
            "reason": "Use 3–40 lowercase letters, numbers, or dashes.",
        }
    try:
        taken = provisioning.database_exists(sub)
    except Exception:
        # If the DB check fails, don't block the user here — POST /signup
        # re-validates authoritatively.
        return {"subdomain": sub, "domain": BASE_DOMAIN, "valid": True, "available": True}
    return {"subdomain": sub, "domain": BASE_DOMAIN, "valid": True, "available": not taken}


@app.get("/status/{subdomain}")
def tenant_status(subdomain: str):
    if not provisioning.validate_subdomain(subdomain):
        return {"ready": False}
    return {"ready": provisioning.database_exists(subdomain)}


# ── Stripe webhooks ──────────────────────────────────────────────────────

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        return JSONResponse({"error": f"Webhook signature failed: {e}"}, status_code=400)

    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        meta = s.get("metadata", {}) or {}
        pending = signup_store.pop(meta.get("signup_token"))
        if pending is None and meta.get("admin_password"):
            # Checkout sessions created before the token store carried the
            # credentials directly in metadata.
            pending = {
                "subdomain": meta.get("subdomain"),
                "admin_email": meta.get("admin_email"),
                "admin_password": meta.get("admin_password"),
            }
        if not pending:
            return JSONResponse(
                {"provisioned": False, "error": "Unknown or expired signup token"},
                status_code=500,
            )
        try:
            provisioning.provision_tenant(
                subdomain=pending["subdomain"],
                admin_login=pending["admin_email"],
                admin_password=pending["admin_password"],
                personalization={
                    "industry": pending.get("industry", ""),
                    "website": pending.get("website", ""),
                    "team_size": pending.get("team_size", ""),
                    "goals": pending.get("goals", ""),
                },
            )
        except Exception as e:
            return JSONResponse({"provisioned": False, "error": str(e)}, status_code=500)
        return {"provisioned": True}

    if event["type"] in ("invoice.payment_failed", "customer.subscription.deleted"):
        s = event["data"]["object"]
        sub_meta = s.get("metadata", {}) or {}
        if sub_meta.get("subdomain"):
            provisioning.suspend_tenant(sub_meta["subdomain"])

    return {"received": True}


# ── PWA / well-known files ───────────────────────────────────────────────

@app.get("/manifest.webmanifest", include_in_schema=False)
def webmanifest():
    return FileResponse(
        STATIC_DIR / "manifest.webmanifest", media_type="application/manifest+json"
    )


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    # Served from the root so the service worker scope covers the whole site.
    return FileResponse(
        STATIC_DIR / "sw.js", media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(STATIC_DIR / "img" / "favicon.ico")


@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
def apple_touch_icon():
    return FileResponse(STATIC_DIR / "img" / "apple-touch-icon.png")


@app.get("/robots.txt", include_in_schema=False)
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /welcome\n"
        "Disallow: /offline\n"
        "Disallow: /status/\n"
        "Disallow: /api/\n"
        f"Sitemap: https://{BASE_DOMAIN}/sitemap.xml\n"
    )
    return HTMLResponse(body, media_type="text/plain")


# Indexable pages: path -> (changefreq, priority).
SITEMAP_PAGES = {
    "/": ("weekly", "1.0"),
    "/signup": ("monthly", "0.9"),
    "/signin": ("monthly", "0.8"),
    "/apps": ("weekly", "0.9"),
    **{f"/apps/{slug}": ("monthly", "0.8") for slug in content.APPS},
    "/pricing": ("monthly", "0.9"),
    "/docs": ("weekly", "0.8"),
    **{f"/docs/{slug}": ("monthly", "0.7") for slug in DOCS_PAGES},
    "/sitemap": ("monthly", "0.3"),
    "/privacy": ("yearly", "0.4"),
}


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    today = datetime.date.today().isoformat()
    urls = "".join(
        "<url>"
        f"<loc>https://{BASE_DOMAIN}{path}</loc>"
        f"<lastmod>{today}</lastmod>"
        f"<changefreq>{freq}</changefreq>"
        f"<priority>{prio}</priority>"
        "</url>"
        for path, (freq, prio) in SITEMAP_PAGES.items()
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return HTMLResponse(body, media_type="application/xml")


@app.get("/sitemap.txt", include_in_schema=False)
def sitemap_txt():
    body = "\n".join(f"https://{BASE_DOMAIN}{p}" for p in SITEMAP_PAGES) + "\n"
    return HTMLResponse(body, media_type="text/plain")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "everjust-control-plane"}
