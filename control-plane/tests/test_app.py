# -*- coding: utf-8 -*-
"""Control-plane route tests (Stripe, Postgres, and provisioning mocked)."""
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

    def fake_provision(subdomain, admin_login, admin_password):
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


def test_webhook_checkout_completed_legacy_metadata(client, monkeypatch):
    """Sessions created before the token store carry credentials in metadata."""
    seen = {}
    monkeypatch.setattr(
        provisioning, "provision_tenant",
        lambda subdomain, admin_login, admin_password: seen.update(sub=subdomain),
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
    assert "Allow: /" in client.get("/robots.txt").text
    assert "https://everjust.app/signup" in client.get("/sitemap.txt").text


def test_healthz(client):
    assert client.get("/healthz").json()["status"] == "ok"


def test_api_docs_disabled(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


# ── Branding ─────────────────────────────────────────────────────────────

def test_no_upstream_branding_on_any_page(client):
    for path in ("/", "/signup", "/signin", "/offline", "/welcome?subdomain=acme"):
        body = client.get(path).text
        assert "odoo" not in body.lower(), f"upstream branding leak on {path}"
