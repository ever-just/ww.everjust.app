# -*- coding: utf-8 -*-
"""Control-plane route tests (Stripe, Postgres, and provisioning mocked)."""
import html
import pathlib
from unittest import mock

import stripe

import main
import provisioning


# ── Pages ────────────────────────────────────────────────────────────────

def test_landing_page(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    assert "EVERJUST.APP" in body
    assert 'href="/signup"' in body
    assert 'href="/signin"' in body
    assert "$100" in body
    assert "Odoo" not in body and "odoo" not in body


def test_signup_page(client):
    r = client.get("/signup")
    assert r.status_code == 200
    assert 'action="/signup"' in r.text
    assert 'name="org_name"' in r.text
    assert 'name="subdomain"' in r.text
    assert 'name="email"' in r.text
    assert 'name="password"' in r.text


def test_signin_page(client):
    r = client.get("/signin")
    assert r.status_code == 200
    assert 'id="workspace"' in r.text
    assert "Create a workspace" in r.text


def test_login_alias_redirects_to_signin(client):
    r = client.get("/login", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "/signin"


def test_offline_page(client):
    r = client.get("/offline")
    assert r.status_code == 200
    assert "offline" in r.text.lower()


def test_welcome_page(client):
    r = client.get("/welcome", params={"s": "cs_123", "subdomain": "acme"})
    assert r.status_code == 200
    assert "acme.everjust.app" in r.text


def test_welcome_rejects_bad_subdomain(client):
    r = client.get("/welcome", params={"subdomain": "<script>"}, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/signup"


def test_security_headers_present(client):
    r = client.get("/")
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["X-Content-Type-Options"] == "nosniff"


# ── Signup flow ──────────────────────────────────────────────────────────

VALID_FORM = {
    "org_name": "New Co",
    "subdomain": "newco",
    "email": "owner@newco.com",
    "password": "hunter2hunter2",
}


def test_signup_happy_path_redirects_to_stripe(client):
    fake_session = mock.Mock(url="https://checkout.stripe.com/c/pay/cs_test_123")
    with mock.patch.object(
        stripe.checkout.Session, "create", return_value=fake_session
    ) as create:
        r = client.post("/signup", data=VALID_FORM, follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == fake_session.url

    kwargs = create.call_args.kwargs
    # Only the opaque token goes through Stripe — never the password.
    assert "admin_password" not in kwargs["metadata"]
    assert kwargs["metadata"]["signup_token"] in client.pending_signups
    assert kwargs["metadata"]["subdomain"] == "newco"
    assert kwargs["customer_email"] == "owner@newco.com"
    assert kwargs["subscription_data"]["metadata"] == kwargs["metadata"]
    assert "newco" in kwargs["success_url"]


def test_signup_rejects_taken_subdomain(client):
    form = dict(VALID_FORM, subdomain="acme")
    r = client.post("/signup", data=form)
    assert r.status_code == 400
    assert "already taken" in r.text
    # The form is re-rendered with the user's values preserved.
    assert 'value="New Co"' in r.text


def test_signup_rejects_invalid_subdomain(client):
    # Note: uppercase input is normalized to lowercase, so it's not invalid.
    for bad in ("a", "-dash", "www", "has space"):
        r = client.post("/signup", data=dict(VALID_FORM, subdomain=bad))
        assert r.status_code == 400, bad
        assert "workspace address" in r.text


def test_signup_rejects_short_password(client):
    r = client.post("/signup", data=dict(VALID_FORM, password="short"))
    assert r.status_code == 400
    assert "at least 8 characters" in r.text


def test_signup_rejects_bad_email(client):
    r = client.post("/signup", data=dict(VALID_FORM, email="not-an-email"))
    assert r.status_code == 400
    assert "valid email" in r.text


def test_signup_stripe_outage_shows_friendly_error(client):
    with mock.patch.object(
        stripe.checkout.Session, "create", side_effect=stripe.StripeError("boom")
    ):
        r = client.post("/signup", data=VALID_FORM)
    assert r.status_code == 502
    assert "Nothing was charged" in r.text


# ── APIs ─────────────────────────────────────────────────────────────────

def test_subdomain_check_available(client):
    r = client.get("/api/subdomain-check", params={"subdomain": "newco"})
    assert r.json() == {
        "subdomain": "newco", "domain": "everjust.app",
        "valid": True, "available": True,
    }


def test_subdomain_check_taken(client):
    d = client.get("/api/subdomain-check", params={"subdomain": "acme"}).json()
    assert d["valid"] is True
    assert d["available"] is False


def test_subdomain_check_invalid_and_reserved(client):
    for bad in ("", "Bad!", "www", "x"):
        d = client.get("/api/subdomain-check", params={"subdomain": bad}).json()
        assert d["valid"] is False, bad


def test_status_endpoint(client):
    assert client.get("/status/acme").json() == {"ready": True}
    assert client.get("/status/newco").json() == {"ready": False}
    assert client.get("/status/NOT-VALID!").json() == {"ready": False}


# ── Stripe webhook ───────────────────────────────────────────────────────

def _event(event_type, obj):
    return {"type": event_type, "data": {"object": obj}}


def test_webhook_rejects_bad_signature(client):
    r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "bad"})
    assert r.status_code == 400


def test_webhook_checkout_completed_provisions_from_token(client, monkeypatch):
    provisioned = {}

    def fake_provision(subdomain, admin_login, admin_password, **extra):
        provisioned.update(sub=subdomain, login=admin_login, pw=admin_password)
        return {"subdomain": subdomain}

    monkeypatch.setattr(provisioning, "provision_tenant", fake_provision)

    token = "tok_test"
    client.pending_signups[token] = {
        "org_name": "New Co", "subdomain": "newco",
        "admin_email": "owner@newco.com", "admin_password": "hunter2hunter2",
    }
    event = _event("checkout.session.completed", {"metadata": {"signup_token": token}})
    with mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.status_code == 200
    assert r.json() == {"provisioned": True}
    assert provisioned == {"sub": "newco", "login": "owner@newco.com", "pw": "hunter2hunter2"}
    assert token not in client.pending_signups  # consumed


def test_webhook_forwards_personalization_and_logs(client, monkeypatch, caplog):
    seen = {}

    def fake_provision(subdomain, admin_login, admin_password, personalization=None, **extra):
        seen["personalization"] = personalization
        return {"subdomain": subdomain}

    monkeypatch.setattr(provisioning, "provision_tenant", fake_provision)
    token = "tok_p"
    client.pending_signups[token] = {
        "subdomain": "acme", "admin_email": "o@acme.com", "admin_password": "hunter2hunter2",
        "industry": "retail", "website": "acme.com", "team_size": "10", "goals": "sell,invoice",
    }
    event = _event("checkout.session.completed", {"id": "cs_1", "metadata": {"signup_token": token}})
    with caplog.at_level("INFO"), mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.json() == {"provisioned": True}
    # The captured onboarding context reaches provisioning intact.
    assert seen["personalization"]["industry"] == "retail"
    assert seen["personalization"]["website"] == "acme.com"
    assert any("provisioned subdomain=acme" in m for m in caplog.messages)


def test_webhook_logs_critical_when_paid_customer_provision_fails(client, monkeypatch, caplog):
    def boom(*a, **k):
        raise RuntimeError("odoo init exploded")

    monkeypatch.setattr(provisioning, "provision_tenant", boom)
    token = "tok_boom"
    client.pending_signups[token] = {
        "subdomain": "doomed", "admin_email": "o@x.com", "admin_password": "hunter2hunter2",
    }
    event = _event("checkout.session.completed", {"id": "cs_2", "metadata": {"signup_token": token}})
    with caplog.at_level("CRITICAL"), mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.status_code == 500
    # A paid-but-unprovisioned customer must produce a CRITICAL alert.
    assert any(rec.levelname == "CRITICAL" and "PROVISION FAILED" in rec.message
               for rec in caplog.records)


def test_best_effort_branding_never_raises_and_logs(monkeypatch, caplog):
    # A branding failure must NOT break provisioning (the customer paid) but
    # must be visible in logs, not silently swallowed.
    import website_enrichment
    monkeypatch.setattr(website_enrichment, "enrich",
                        lambda url: (_ for _ in ()).throw(RuntimeError("dns boom")))
    with caplog.at_level("ERROR"):
        provisioning._apply_website_branding("acme", "acme.com")   # must not raise
    assert any("website branding failed" in m for m in caplog.messages)


def test_best_effort_app_install_never_raises_and_logs(monkeypatch, caplog):
    monkeypatch.setattr(provisioning.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("docker gone")))
    with caplog.at_level("ERROR"):
        provisioning._install_personalized_apps("acme", {"industry": "retail", "goals": ""})
    assert any("personalized app install failed" in m for m in caplog.messages)


def test_webhook_checkout_completed_legacy_metadata(client, monkeypatch):
    """Sessions created before the token store carry credentials in metadata."""
    seen = {}
    monkeypatch.setattr(
        provisioning, "provision_tenant",
        lambda subdomain, admin_login, admin_password, **extra: seen.update(sub=subdomain),
    )
    event = _event("checkout.session.completed", {"metadata": {
        "subdomain": "oldco", "admin_email": "o@oldco.com", "admin_password": "pw12345678",
    }})
    with mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.json() == {"provisioned": True}
    assert seen == {"sub": "oldco"}


def test_webhook_unknown_token_errors(client):
    event = _event("checkout.session.completed", {"metadata": {"signup_token": "nope"}})
    with mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.status_code == 500


def test_webhook_payment_failed_suspends_tenant(client, monkeypatch):
    suspended = []
    monkeypatch.setattr(provisioning, "suspend_tenant", suspended.append)
    event = _event("invoice.payment_failed", {"metadata": {"subdomain": "acme"}})
    with mock.patch.object(stripe.Webhook, "construct_event", return_value=event):
        r = client.post("/stripe/webhook", content=b"{}", headers={"stripe-signature": "x"})
    assert r.json() == {"received": True}
    assert suspended == ["acme"]


# ── PWA / static plumbing ────────────────────────────────────────────────

def test_manifest_served_at_root_scope(client):
    r = client.get("/manifest.webmanifest")
    assert r.status_code == 200
    assert "manifest" in r.headers["content-type"]
    data = r.json()
    assert data["name"] == "EVERJUST.APP"
    assert data["display"] == "standalone"
    assert {i["sizes"] for i in data["icons"]} >= {"192x192", "512x512"}


def test_service_worker_served_at_root(client):
    r = client.get("/sw.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"]
    assert "everjust" in r.text


def test_static_assets(client):
    assert client.get("/static/css/site.css").status_code == 200
    assert client.get("/static/js/signup.js").status_code == 200
    assert client.get("/favicon.ico").status_code == 200
    assert client.get("/apple-touch-icon.png").status_code == 200


def test_robots_and_sitemap(client):
    robots = client.get("/robots.txt").text
    assert "Allow: /" in robots
    assert "Sitemap: https://everjust.app/sitemap.xml" in robots
    assert "Disallow: /welcome" in robots

    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert "application/xml" in r.headers["content-type"]
    for path in ("/", "/signup", "/signin", "/docs", "/docs/getting-started",
                 "/docs/billing", "/docs/security"):
        assert f"<loc>https://everjust.app{path}</loc>" in r.text

    assert "https://everjust.app/signup" in client.get("/sitemap.txt").text


# ── Docs ─────────────────────────────────────────────────────────────────

def test_docs_index(client):
    r = client.get("/docs")
    assert r.status_code == 200
    for title in ("Getting started", "Invite your team", "Billing",
                  "Use it on your phone", "Security", "App guides",
                  "CRM & Sales", "Payroll"):
        assert html.escape(title, quote=False) in r.text
    assert 'id="docs_search"' in r.text  # docs search box


def test_docs_pages_render_with_nav(client):
    for slug in ("getting-started", "invite-team",
                 "billing", "mobile-app", "security"):
        r = client.get(f"/docs/{slug}")
        assert r.status_code == 200, slug
        assert "breadcrumb" in r.text, slug          # breadcrumb backlinks
        assert 'href="/docs"' in r.text, slug        # backlink to index


def test_apps_index(client):
    r = client.get("/apps")
    assert r.status_code == 200
    for slug, a in main.content.APPS.items():
        assert f'href="/apps/{slug}"' in r.text
        assert html.escape(a["name"], quote=False) in r.text


def test_app_detail_pages(client):
    og_dir = pathlib.Path(__file__).resolve().parents[1] / "static" / "img" / "og"
    for slug, a in main.content.APPS.items():
        r = client.get(f"/apps/{slug}")
        assert r.status_code == 200, slug
        assert html.escape(a["name"], quote=False) in r.text
        # Every app gets its own social card, and the file must exist on disk.
        assert f"/static/img/og/{slug}.jpg" in r.text, slug
        assert (og_dir / f"{slug}.jpg").exists(), slug
        # Every page carries the at-a-glance spec strip and the "one connected
        # workspace" diagram so no app page reads as thin/text-only.
        assert "app-specs" in r.text, slug
        assert "workspace-diagram" in r.text, slug
        # Detailed apps link their guide + show the workflow; lighter catalog
        # entries render cleanly without those sections.
        if a.get("guide"):
            assert f'/docs/{a["guide"]}' in r.text
            assert "How it works" in r.text
        if a.get("replaces"):
            assert "Replaces tools like" in r.text
    assert client.get("/apps/not-an-app").status_code == 404


def test_app_catalog_breadth_and_filter(client):
    body = client.get("/apps").text
    # The catalog must surface the full suite, not just 8 apps.
    assert len(main.content.APPS) >= 25
    assert "Point of Sale" in body and "Inventory" in body and "Manufacturing" in body
    # Category groups + search + filter chips are present.
    for cat in main.content.CATEGORIES.values():
        assert cat["name"] in body
    assert 'id="app_search"' in body
    assert 'id="catalog_filters"' in body
    assert "/static/js/catalog.js" in body


def test_landing_features_link_to_app_pages(client):
    body = client.get("/").text
    assert 'href="/apps/crm-sales"' in body
    assert 'href="/apps"' in body                       # explore-all link


def test_docs_guides_render(client):
    for slug, g in main.content.APP_GUIDES.items():
        r = client.get(f"/docs/{slug}")
        assert r.status_code == 200, slug
        assert html.escape(g["title"], quote=False) in r.text
        assert html.escape(g["sections"][0][0], quote=False) in r.text            # first section heading


def test_docs_apps_redirects_to_apps(client):
    r = client.get("/docs/apps", follow_redirects=False)
    assert r.status_code == 301
    assert r.headers["location"] == "/apps"


def test_docs_search_index(client):
    d = client.get("/docs/search-index.json").json()
    slugs = {i["slug"] for i in d["items"]}
    assert "getting-started" in slugs and "guide-payroll" in slugs
    guide = next(i for i in d["items"] if i["slug"] == "guide-crm-sales")
    assert guide["section"] == "App guides"
    assert guide["headings"]                            # headings indexed


def test_assets_are_cache_busted(client):
    body = client.get("/").text
    assert f"/static/css/site.css?v={main.ASSET_VERSION}" in body
    assert f"/static/js/consent.js?v={main.ASSET_VERSION}" in body
    # Sprite hidden Safari-safely (no display:none)
    assert 'class="svg-sprite"' in body
    assert 'style="display:none"' not in body


def test_sitemap_includes_app_pages(client):
    text = client.get("/sitemap.xml").text
    assert "<loc>https://everjust.app/apps</loc>" in text
    assert "<loc>https://everjust.app/apps/payroll</loc>" in text
    assert "<loc>https://everjust.app/docs/guide-documents</loc>" in text


def test_docs_unknown_slug_404(client):
    r = client.get("/docs/not-a-page")
    assert r.status_code == 404
    assert "Back to docs" in r.text


# ── UI framework / icons / SEO plumbing ──────────────────────────────────

def test_pages_use_bootstrap_and_icon_sprite(client):
    body = client.get("/").text
    assert "/static/vendor/bootstrap/bootstrap.min.css" in body
    assert '<use href="#i-' in body            # inline Lucide sprite in use
    assert "<symbol" in body                   # sprite symbols inlined
    assert client.get("/static/vendor/bootstrap/bootstrap.min.css").status_code == 200
    assert client.get("/static/vendor/lucide/sprite.svg").status_code == 200


def test_header_logo_and_mobile_menu(client):
    body = client.get("/").text
    header = body.split("</header>")[0]
    assert 'class="brand-logo"' in header
    assert "icon-192x192.png" in header           # brand logo image restored
    assert 'id="siteMenu"' in body                # bottom-sheet menu exists
    assert "offcanvas-bottom menu-sheet" in body  # ...as a bottom sheet
    assert "sheet-handle" in body                 # with a drag handle
    assert "sheet-list" in body                   # clean list, not tile grid
    assert "/static/vendor/bootstrap/bootstrap.bundle.min.js" in body


def test_menu_links_navigate(client):
    # Regression: data-bs-dismiss on an <a> makes Bootstrap call
    # preventDefault, which blocked the sheet's nav links from working.
    body = client.get("/").text
    sheet = body.split('class="sheet-list"')[1].split("</nav>")[0]
    assert 'href="/docs"' in sheet and 'href="/pricing"' in sheet
    assert "data-bs-dismiss" not in sheet         # links must navigate
    assert "/static/js/nav.js" in body            # JS closes the sheet instead


def test_docs_mobile_nav_collapsed(client):
    # The docs nav must be a tappable toggle (closed on mobile) so the
    # full link list doesn't bury the content on phones.
    body = client.get("/docs/billing").text
    assert 'id="docs_nav_toggle"' in body
    assert 'aria-expanded="false"' in body
    assert 'class="docs-nav-list"' in body


def test_mobile_tabbar(client):
    body = client.get("/").text
    assert 'class="mobile-tabbar d-lg-none"' in body
    assert 'data-bs-target="#siteMenu"' in body   # Menu tab opens the sheet
    assert "tab-cta-circle" in body               # raised Start action
    # Active state follows the current path.
    home_tab = body.split('aria-label="Quick navigation"')[1]
    assert 'class="tab-item active" href="/"' in home_tab
    apps_body = client.get("/apps").text
    assert 'class="tab-item active" href="/apps"' in apps_body
    docs_body = client.get("/docs").text
    assert 'class="tab-item active" href="/docs"' in docs_body


def test_landing_layout_rhythm(client):
    body = client.get("/").text
    assert body.count('class="eyebrow"') >= 4     # section divider labels
    assert "hero-points" in body                  # trust chip strip
    assert "steps-timeline" in body               # connected timeline steps
    assert "cta-band" in body and "btn-inverse" in body  # inverted closer


def test_landing_redesign_structure(client):
    body = client.get("/").text
    assert "hero-kicker" in body                   # redesigned hero
    assert "app-marquee" in body                   # breadth marquee (not a card)
    assert body.count('class="pillar') >= 3        # alternating feature pillars
    assert "replaces-strip" in body                # "replaces your stack"
    assert "cat-teaser" in body                    # category teaser (not cards)
    assert "data-reveal" in body and "reveal-ready" in body
    assert client.get("/static/js/nav.js").status_code == 200


def test_intentional_fonts_loaded(client):
    body = client.get("/").text
    assert "/static/fonts/space-grotesk.woff2" in body   # display face preloaded
    assert "/static/fonts/geist.woff2" in body           # body face preloaded
    css = client.get("/static/css/site.css").text
    assert "Space Grotesk" in css and "Geist" in css
    assert "Arial, sans-serif" not in css.split("--ej-body")[0]  # not the default stack
    assert client.get("/static/fonts/space-grotesk.woff2").status_code == 200


def test_zoom_and_overflow_css(client):
    css = client.get("/static/css/site.css").text
    assert "html { font-size: 15px; }" in css      # zoomed-out mobile root
    assert "font-size: 16px" in css                # inputs pinned (no iOS zoom)


def test_docs_layout_keeps_horizontal_padding(client):
    # Regression: the .docs-layout padding shorthand used to zero the
    # container's left/right padding, flushing docs to the screen edges
    # on mobile. It must only set vertical padding.
    css = client.get("/static/css/site.css").text
    assert ".docs-layout { padding-top: 1.5rem; padding-bottom: 4rem; }" in css
    assert ".docs-layout { padding: 1.5rem 0 4rem; }" not in css


def test_no_horizontal_overflow_guard(client):
    # Defends the fix for content being cut off / scrolling sideways on
    # phones: the global guard and the removal of the rail's negative margins.
    css = client.get("/static/css/site.css").text
    assert "overflow-x: clip" in css
    assert "margin-left: -1.25rem" not in css     # the old rail overflow source


def test_manifest_pwa_fields(client):
    data = client.get("/manifest.webmanifest").json()
    assert data["display_override"] == ["standalone", "minimal-ui"]
    assert "business" in data["categories"]


def test_consent_banner_wiring(client):
    body = client.get("/").text
    assert "/static/vendor/cookieconsent/cookieconsent.css" in body
    assert "/static/vendor/cookieconsent/cookieconsent.umd.js" in body
    assert "/static/js/consent.js" in body
    assert 'data-cc="show-preferencesModal"' in body  # footer reopen button
    assert client.get("/static/vendor/cookieconsent/cookieconsent.umd.js").status_code == 200
    assert client.get("/static/js/consent.js").status_code == 200


def test_privacy_page(client):
    r = client.get("/privacy")
    assert r.status_code == 200
    assert "ej_consent" in r.text                 # cookie table documented
    assert "recentWorkspaces" in r.text
    assert "<loc>https://everjust.app/privacy</loc>" in client.get("/sitemap.xml").text
    assert 'href="/privacy"' in client.get("/").text  # footer backlink


def test_canonical_and_structured_data(client):
    body = client.get("/").text
    assert '<link rel="canonical" href="https://everjust.app/">' in body
    assert "application/ld+json" in body
    assert 'property="og:locale" content="en_US"' in body
    assert '"contactPoint"' in body                       # Organization contact
    docs = client.get("/docs/billing").text
    assert '<link rel="canonical" href="https://everjust.app/docs/billing">' in docs


def test_breadcrumbs_and_og_type(client):
    # Breadcrumb structured data on the key page types (helps rich results).
    for path in ("/apps", "/pricing", "/apps/inventory", "/docs/billing"):
        assert '"@type": "BreadcrumbList"' in client.get(path).text, path
    # Docs are typed as articles, marketing pages as websites.
    assert 'property="og:type" content="article"' in client.get("/docs/billing").text
    assert 'property="og:type" content="website"' in client.get("/").text


def test_welcome_not_indexable(client):
    body = client.get("/welcome", params={"subdomain": "acme"}).text
    assert 'content="noindex"' in body


def test_signup_wizard_structure(client):
    body = client.get("/signup").text
    assert 'id="step1"' in body and 'id="step2"' in body
    assert "Checkout" in body                  # 3-step progress indicator
    assert 'data-error-step="1"' in body


def test_signup_error_opens_correct_wizard_step(client):
    # Subdomain problems live on step 2 of the wizard.
    r = client.post("/signup", data=dict(VALID_FORM, subdomain="acme"))
    assert 'data-error-step="2"' in r.text
    # Account problems live on step 1.
    r = client.post("/signup", data=dict(VALID_FORM, password="short"))
    assert 'data-error-step="1"' in r.text


def test_healthz(client):
    assert client.get("/healthz").json()["status"] == "ok"


def test_api_docs_disabled(client):
    # /docs serves our documentation, not FastAPI's Swagger UI.
    assert "swagger" not in client.get("/docs").text.lower()
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/redoc").status_code == 404


# ── Branding ─────────────────────────────────────────────────────────────

def test_no_upstream_branding_on_any_page(client):
    paths = ["/", "/signup", "/signin", "/offline", "/welcome?subdomain=acme",
             "/privacy", "/docs", "/docs/getting-started", "/docs/invite-team",
             "/docs/billing", "/docs/mobile-app", "/docs/security", "/apps"]
    paths += [f"/apps/{slug}" for slug in main.content.APPS]
    paths += [f"/docs/{slug}" for slug in main.content.APP_GUIDES]
    for path in paths:
        body = client.get(path).text
        assert "odoo" not in body.lower(), f"upstream branding leak on {path}"


def test_static_assets_are_compressed_and_cacheable(client):
    # Perf: text assets must gzip (Bootstrap CSS ~233KB -> ~31KB) and the
    # versioned static files must be long-cacheable.
    r = client.get("/static/vendor/bootstrap/bootstrap.min.css",
                   headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"
    assert "max-age=31536000" in r.headers.get("cache-control", "")

    # HTML pages compress too.
    h = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert h.headers.get("content-encoding") == "gzip"


def test_signup_captures_personalization(client):
    form = dict(VALID_FORM, industry="Software / technology",
                website="acme.com", team_size="6–20",
                goals="Sales & CRM, Marketing")
    fake_session = mock.Mock(url="https://checkout.stripe.com/c/pay/cs_x")
    with mock.patch.object(stripe.checkout.Session, "create", return_value=fake_session):
        r = client.post("/signup", data=form, follow_redirects=False)
    assert r.status_code == 303
    # The optional onboarding context is stored server-side under the token.
    rec = next(iter(client.pending_signups.values()))
    assert rec["industry"] == "Software / technology"
    assert rec["website"] == "acme.com"
    assert rec["team_size"] == "6–20"
    assert rec["goals"] == "Sales & CRM, Marketing"


def test_signup_personalization_optional(client):
    # Signup still works with no business context (all optional).
    fake_session = mock.Mock(url="https://checkout.stripe.com/c/pay/cs_y")
    with mock.patch.object(stripe.checkout.Session, "create", return_value=fake_session):
        r = client.post("/signup", data=VALID_FORM, follow_redirects=False)
    assert r.status_code == 303


def test_signup_page_has_business_step(client):
    body = client.get("/signup").text
    assert 'id="step3"' in body and 'name="industry"' in body
    assert 'name="website"' in body and 'name="goals"' in body
    assert "goal-chip" in body and "Business" in body  # 4-step progress


def test_social_card_and_structured_data(client):
    body = client.get("/").text
    assert "/static/img/og-card.jpg" in body            # social/OG card wired
    assert 'name="twitter:card" content="summary_large_image"' in body
    assert '"@type": "WebSite"' in body
    assert '"@type": "FAQPage"' in body                  # landing FAQ schema
    assert client.get("/static/img/og-card.jpg").status_code == 200


def test_html_sitemap_page(client):
    r = client.get("/sitemap")
    assert r.status_code == 200
    body = r.text
    # Real internal-linking depth: every app + every doc page linked.
    for slug in main.content.APPS:
        assert f'/apps/{slug}' in body
    for slug in main.DOCS_PAGES:
        assert f'/docs/{slug}' in body
    assert "<loc>https://everjust.app/sitemap</loc>" in client.get("/sitemap.xml").text


# ── Onboarding stage 2: industry/goals -> apps ──────────────────────────

def test_personalized_modules_by_industry():
    mods = provisioning.personalized_modules("Manufacturing", "")
    assert "mrp" in mods and "stock" in mods and "purchase" in mods


def test_personalized_modules_goals_add_and_dedupe():
    mods = provisioning.personalized_modules("Software / technology",
                                             "Marketing, Website & Store")
    assert "mass_mailing" in mods and "website_sale" in mods
    assert len(mods) == len(set(mods))           # de-duplicated


def test_personalized_modules_default_and_allowlist():
    # No context -> a sensible default starter set.
    assert provisioning.personalized_modules("", "") == \
        ["crm", "sale_management", "account", "contacts", "calendar"]
    # Unknown industry/goal can't inject arbitrary module names.
    mods = provisioning.personalized_modules("Hacker; rm -rf", "DROP TABLE")
    assert all(m in provisioning.ALLOWED_MODULES for m in mods)


# ── Onboarding stage 3: website enrichment + SSRF guard ─────────────────

import website_enrichment as we


def test_ssrf_ip_blocklist():
    for bad in ("127.0.0.1", "10.0.0.1", "192.168.1.5", "172.16.0.1",
                "169.254.169.254", "0.0.0.0", "::1", "fc00::1", "224.0.0.1"):
        assert we._ip_blocked(bad), bad
    for ok in ("8.8.8.8", "1.1.1.1", "93.184.216.34"):
        assert not we._ip_blocked(ok), ok


def test_ssrf_host_and_url_guards(monkeypatch):
    assert we._host_allowed("localhost") is False
    # Hostname resolving to a private IP is rejected (DNS-based SSRF).
    monkeypatch.setattr(we.socket, "getaddrinfo",
                        lambda h, p: [(2, 1, 6, "", ("10.1.2.3", 0))])
    assert we._host_allowed("evil.internal") is False
    assert we._url_allowed("http://evil.internal/") is False
    # Public resolution is allowed.
    monkeypatch.setattr(we.socket, "getaddrinfo",
                        lambda h, p: [(2, 1, 6, "", ("93.184.216.34", 0))])
    assert we._host_allowed("example.com") is True
    # Non-http schemes are refused outright.
    assert we._url_allowed("file:///etc/passwd") is False
    assert we._url_allowed("ftp://example.com/") is False


def test_extract_brand():
    html = (
        '<html><head><title>Acme Tools | Hardware</title>'
        '<meta name="description" content="We sell great hardware.">'
        '<meta name="theme-color" content="#1a73e8">'
        '<meta property="og:site_name" content="Acme Tools">'
        '<link rel="apple-touch-icon" href="/img/logo.png">'
        '</head><body></body></html>')
    b = we.extract_brand(html, "https://acme.example/")
    assert b["name"] == "Acme Tools"
    assert b["description"].startswith("We sell")
    assert b["theme_color"] == "#1a73e8"
    assert b["logo_url"] == "https://acme.example/img/logo.png"


def test_enrich_refuses_private_url(monkeypatch):
    # enrich() must return {} for a blocked target without fetching.
    monkeypatch.setattr(we.socket, "getaddrinfo",
                        lambda h, p: [(2, 1, 6, "", ("127.0.0.1", 0))])
    assert we.enrich("http://internal.local/") == {}


def test_savings_calculator(client):
    body = client.get("/").text
    assert 'id="savings"' in body and "calc-tool" in body
    assert 'id="calc_users"' in body and 'id="calc_savings"' in body
    assert "/static/js/calc.js" in body
    # Every configured tool renders a toggle.
    assert body.count('class="calc-tool"') == len(main.content.CALCULATOR_TOOLS)
    assert client.get("/static/js/calc.js").status_code == 200


def test_pricing_page(client):
    r = client.get("/pricing")
    assert r.status_code == 200
    body = r.text
    # Plan price, team-size table, calculator, and pricing FAQ all present.
    assert "$100" in body and "$15" in body
    assert "price-table" in body
    assert "$175" in body          # 10 users = 100 + 5*15
    assert "$775" in body          # 50 users = 100 + 45*15
    assert "calc-tool" in body and "/static/js/calc.js" in body
    assert "Pricing questions" in body
    # Wired into sitemap and nav.
    assert "/pricing" in client.get("/sitemap.xml").text
    assert 'href="/pricing"' in client.get("/").text


def test_docs_is_help_center_not_app_catalog(client):
    # Docs and the app catalog are separate concerns: docs covers the 8 in-depth
    # guides + account topics and points to /apps for the full list, rather than
    # re-listing all 29 apps (which duplicated the catalog and read confusingly).
    body = client.get("/docs").text
    assert "docs-catalog-link" in body               # single pointer to the catalog
    assert 'href="/apps"' in body
    assert 'id="every-app"' not in body              # no duplicated catalog
    assert "docs-applist" not in body
    # The 8 in-depth guides still surface as cards.
    for slug in main.content.APP_GUIDES:
        assert f'href="/docs/{slug}"' in body


def test_pwa_auto_reload_on_new_version(client):
    js = client.get("/static/js/pwa.js").text
    assert "controllerchange" in js                  # deploys auto-refresh
    assert "everjust-v7" in client.get("/sw.js").text


def test_footer_uses_real_logo_mark(client):
    # The actual EVERJUST mark (white variant) appears on the dark footer,
    # not just a text wordmark, and the asset is served.
    body = client.get("/").text
    assert "/static/img/logo-white.png" in body
    assert "footer-brand" in body
    assert client.get("/static/img/logo-white.png").status_code == 200


def test_analytics_is_cookieless_and_gated(client, monkeypatch):
    # The shim always loads; the provider script only when ANALYTICS_DOMAIN is set.
    home = client.get("/").text
    assert "/static/js/analytics.js" in home
    js = client.get("/static/js/analytics.js").text
    assert "ejTrack" in js and "doNotTrack" in js     # cookieless + DNT-aware
    assert "document.cookie" not in js                # never sets/reads cookies

    # Unset by default -> no third-party analytics script emitted.
    assert "data-domain=" not in home
    assert "plausible" not in home.lower()

    # Configured -> the cookieless provider script appears.
    monkeypatch.setattr(main, "ANALYTICS_DOMAIN", "everjust.app")
    on = client.get("/").text
    assert 'data-domain="everjust.app"' in on
    assert "plausible" in on.lower()


def test_signup_funnel_is_instrumented(client):
    signup = client.get("/signup").text
    for ev in ("signup_started", "signup_details", "signup_submitted"):
        assert f'data-track="{ev}"' in signup
    # Persistent CTA + completion view event.
    assert 'data-track="signup_cta"' in client.get("/").text
    welcome = client.get("/welcome?subdomain=acme").text
    assert 'data-track-view="signup_completed"' in welcome
