# -*- coding: utf-8 -*-
"""EVERJUST.APP control plane.

Public site (landing, signup, sign-in), Stripe billing, and tenant
provisioning. Runs at everjust.app (root); tenant workspaces live at
<org>.everjust.app.
"""
import datetime
import os
import pathlib

import stripe
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import provisioning
import signup_store

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "price_1TflJNKL0p3ve1jHbCLlDNWS")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "everjust.app")

BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="EVERJUST.APP", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def render(request: Request, name: str, status_code: int = 200, **ctx) -> HTMLResponse:
    ctx.setdefault("domain", BASE_DOMAIN)
    ctx.setdefault("year", datetime.date.today().year)
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


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request, s: str = None, subdomain: str = None):
    sub = (subdomain or "").lower().strip()
    if not provisioning.validate_subdomain(sub):
        return RedirectResponse("/signup", status_code=303)
    return render(request, "welcome.html", subdomain=sub)


# ── Signup flow ──────────────────────────────────────────────────────────

def _signup_error(request: Request, message: str, **form_values) -> HTMLResponse:
    return render(request, "signup.html", status_code=400, error=message, **form_values)


@app.post("/signup")
def signup(request: Request,
           org_name: str = Form(...), subdomain: str = Form(...),
           email: str = Form(...), password: str = Form(...)):
    org_name = org_name.strip()
    subdomain = subdomain.lower().strip()
    email = email.strip()
    keep = {"org_name": org_name, "subdomain": subdomain, "email": email}

    if not org_name:
        return _signup_error(request, "Please enter your organization name.", **keep)
    if not provisioning.validate_subdomain(subdomain):
        return _signup_error(
            request,
            "That workspace address can’t be used. Use 3–40 lowercase letters, "
            "numbers, or dashes (it can’t start or end with a dash).",
            **keep,
        )
    if "@" not in email or "." not in email.split("@")[-1]:
        return _signup_error(request, "Please enter a valid email address.", **keep)
    if len(password) < 8:
        return _signup_error(request, "Your password must be at least 8 characters.", **keep)
    if provisioning.database_exists(subdomain):
        return _signup_error(
            request,
            f"{subdomain}.{BASE_DOMAIN} is already taken — try another address.",
            **keep,
        )

    # Keep signup details (incl. the tenant admin password) server-side;
    # only an opaque token travels through Stripe metadata.
    token = signup_store.create(org_name, subdomain, email, password)
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
    body = f"User-agent: *\nAllow: /\nSitemap: https://{BASE_DOMAIN}/sitemap.txt\n"
    return HTMLResponse(body, media_type="text/plain")


@app.get("/sitemap.txt", include_in_schema=False)
def sitemap():
    pages = ["", "signup", "signin"]
    body = "\n".join(f"https://{BASE_DOMAIN}/{p}" for p in pages) + "\n"
    return HTMLResponse(body, media_type="text/plain")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "everjust-control-plane"}
