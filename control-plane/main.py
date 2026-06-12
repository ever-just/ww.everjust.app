# -*- coding: utf-8 -*-
"""EVERJUST.APP control plane.

Handles the public signup flow, Stripe billing, and tenant provisioning.
Runs at everjust.app (root). Tenant instances live at <org>.everjust.app.
"""
import os
import stripe
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

import provisioning

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "price_1TflJNKL0p3ve1jHbCLlDNWS")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "everjust.app")

app = FastAPI(title="EVERJUST.APP")


SIGNUP_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<title>EVERJUST.APP</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;color:#000;
       display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}}
  .card{{width:400px;border:1px solid #000;border-radius:12px;padding:32px}}
  h1{{font-weight:800;letter-spacing:1px;margin:0 0 4px}}
  p{{color:#555;margin:0 0 24px}}
  label{{display:block;font-size:13px;margin:16px 0 4px;font-weight:600}}
  input{{width:100%;padding:10px;border:1px solid #000;border-radius:8px;box-sizing:border-box;
         font-size:14px}}
  .preview{{margin-top:8px;padding:10px 12px;border:1px dashed #bbb;border-radius:8px;
            background:#fafafa;font-size:14px;display:flex;align-items:center;gap:2px}}
  .preview .host{{font-weight:800}}
  .preview .suffix{{color:#888}}
  .preview .placeholder{{color:#bbb;font-weight:800}}
  button{{width:100%;margin-top:28px;padding:12px;background:#000;color:#fff;border:0;
          border-radius:8px;font-weight:700;cursor:pointer;font-size:15px}}
  .divider{{display:flex;align-items:center;gap:12px;margin:28px 0 0;color:#aaa;font-size:13px}}
  .divider::before,.divider::after{{content:'';flex:1;border-top:1px solid #ddd}}
  .login-section{{margin-top:20px}}
  .login-section p{{color:#555;margin:0 0 12px;font-size:14px}}
  .login-row{{display:flex;gap:8px}}
  .login-row input{{flex:1;margin:0}}
  .login-row button{{width:auto;margin:0;padding:10px 16px;white-space:nowrap;font-size:13px}}
  .login-suffix{{font-size:13px;color:#888;margin-top:4px}}
</style></head><body>
<div class="card">
<form method="post" action="/signup">
  <h1>EVERJUST.APP</h1>
  <p>Start your workspace</p>
  <label>Organization name</label>
  <input name="org_name" id="org_name" required>
  <label>Workspace address</label>
  <input name="subdomain" id="subdomain" pattern="[a-z0-9-]+" autocomplete="off"
         autocapitalize="off" spellcheck="false" required>
  <div class="preview" id="preview">
    <span class="placeholder">your-org</span><span class="suffix">.{domain}</span>
  </div>
  <label>Admin email</label>
  <input name="email" type="email" required>
  <label>Password</label>
  <input name="password" type="password" minlength="8" required>
  <button type="submit">Create workspace</button>
</form>
<div class="divider">or</div>
<div class="login-section">
  <p>Already have a workspace?</p>
  <div class="login-row">
    <input type="text" id="login_subdomain" placeholder="your-org" autocomplete="off"
           autocapitalize="off" spellcheck="false">
    <button type="button" id="login_btn">Log in &rarr;</button>
  </div>
  <div class="login-suffix">.{domain}</div>
</div>
</div>
<script>
  var sub = document.getElementById('subdomain');
  var org = document.getElementById('org_name');
  var preview = document.getElementById('preview');
  var SUFFIX = '.{domain}';
  function slug(v){{
    return (v||'').toLowerCase().trim()
      .replace(/[^a-z0-9-]+/g,'-').replace(/-+/g,'-').replace(/^-|-$/g,'');
  }}
  function render(){{
    var v = slug(sub.value);
    if(v){{
      preview.innerHTML = '<span class="host">'+v+'</span><span class="suffix">'+SUFFIX+'</span>';
    }} else {{
      preview.innerHTML = '<span class="placeholder">your-org</span><span class="suffix">'+SUFFIX+'</span>';
    }}
  }}
  sub.addEventListener('input', render);
  // Suggest a workspace address from the org name until the user edits it.
  var edited = false;
  sub.addEventListener('input', function(){{ edited = true; }});
  org.addEventListener('input', function(){{
    if(!edited){{ sub.value = slug(org.value); render(); }}
  }});
  // Normalize on submit so what the user previewed is what gets sent.
  sub.form.addEventListener('submit', function(){{ sub.value = slug(sub.value); }});
  // Login redirect
  var loginInput = document.getElementById('login_subdomain');
  var loginBtn = document.getElementById('login_btn');
  function goLogin(){{
    var ws = slug(loginInput.value);
    if(ws) window.location.href = 'https://' + ws + '.{domain}';
  }}
  loginBtn.addEventListener('click', goLogin);
  loginInput.addEventListener('keydown', function(e){{ if(e.key==='Enter') goLogin(); }});
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
def signup_page():
    return SIGNUP_PAGE.format(domain=BASE_DOMAIN)


@app.post("/signup")
def signup(org_name: str = Form(...), subdomain: str = Form(...),
           email: str = Form(...), password: str = Form(...)):
    subdomain = subdomain.lower().strip()
    if not provisioning.validate_subdomain(subdomain):
        raise HTTPException(400, "That workspace address is unavailable.")
    if provisioning.database_exists(subdomain):
        raise HTTPException(400, "That workspace address is taken.")

    tenant_meta = {
        "org_name": org_name,
        "subdomain": subdomain,
        "admin_email": email,
        # Password is passed through metadata only for the provisioning
        # step; replace with a one-time token store in production.
        "admin_password": password,
    }
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 5}],
        customer_email=email,
        # Let customers enter a promo code (e.g. 100%-off access codes).
        allow_promotion_codes=True,
        # If a coupon brings the total to $0, don't force card entry.
        payment_method_collection="if_required",
        success_url=f"https://{BASE_DOMAIN}/welcome?s={{CHECKOUT_SESSION_ID}}&subdomain={subdomain}",
        cancel_url=f"https://{BASE_DOMAIN}/",
        metadata=tenant_meta,
        # Carry tenant metadata onto the subscription so lifecycle webhooks
        # (payment_failed, subscription.deleted) can resolve the tenant.
        subscription_data={"metadata": tenant_meta},
    )
    return RedirectResponse(session.url, status_code=303)


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, f"Webhook signature failed: {e}")

    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        meta = s.get("metadata", {})
        try:
            provisioning.provision_tenant(
                subdomain=meta["subdomain"],
                admin_login=meta["admin_email"],
                admin_password=meta["admin_password"],
            )
        except Exception as e:
            return JSONResponse({"provisioned": False, "error": str(e)}, status_code=500)
        return {"provisioned": True}

    if event["type"] in ("invoice.payment_failed", "customer.subscription.deleted"):
        s = event["data"]["object"]
        sub_meta = s.get("metadata", {})
        if sub_meta.get("subdomain"):
            provisioning.suspend_tenant(sub_meta["subdomain"])

    return {"received": True}


WELCOME_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<title>EVERJUST.APP — Setting up your workspace</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;color:#000;
       display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0;text-align:center}}
  .card{{width:420px;padding:40px 32px}}
  h1{{font-weight:800;letter-spacing:1px;margin:0 0 32px}}
  .url{{font-weight:700;font-size:15px;color:#000;word-break:break-all}}
  .box{{border:1px solid #000;border-radius:12px;padding:24px;margin:24px 0}}
  .spinner{{width:36px;height:36px;border:3px solid #eee;border-top-color:#000;
            border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 20px}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  .status-text{{font-size:15px;color:#555;margin:0 0 8px}}
  .note{{font-size:13px;color:#888;margin:0}}
  .login-btn{{display:block;padding:14px;background:#000;color:#fff;text-decoration:none;
              border-radius:8px;font-weight:700;font-size:15px;margin-bottom:16px}}
  #state-ready,#state-timeout{{display:none}}
</style>
</head><body>
<div class="card">
  <h1>EVERJUST.APP</h1>

  <div id="state-loading">
    <div class="box">
      <div class="spinner"></div>
      <p class="status-text">Setting up <span class="url">{subdomain}.{domain}</span>&hellip;</p>
      <p class="note">This usually takes 1&ndash;2 minutes. Hold tight.</p>
    </div>
  </div>

  <div id="state-ready">
    <div class="box">
      <p class="status-text" style="margin-bottom:20px">Your workspace is ready.</p>
      <a class="login-btn" href="https://{subdomain}.{domain}">
        Log in to {subdomain}.{domain} &rarr;
      </a>
      <p class="note">No email confirmation needed &mdash; sign in with the email and password you just created.</p>
    </div>
  </div>

  <div id="state-timeout">
    <div class="box">
      <p class="status-text">Still setting up&hellip;</p>
      <p class="note" style="margin-bottom:16px">
        It&rsquo;s taking longer than usual. Try logging in at:<br>
        <a href="https://{subdomain}.{domain}" class="url">https://{subdomain}.{domain}</a>
      </p>
    </div>
  </div>
</div>
<script>
  var subdomain = {subdomain_js!r};
  var attempts = 0;
  var MAX = 60;
  function poll() {{
    fetch('/status/' + subdomain)
      .then(function(r) {{ return r.json(); }})
      .then(function(d) {{
        if (d.ready) {{
          document.getElementById('state-loading').style.display = 'none';
          document.getElementById('state-ready').style.display = 'block';
        }} else if (attempts++ < MAX) {{
          setTimeout(poll, 3000);
        }} else {{
          document.getElementById('state-loading').style.display = 'none';
          document.getElementById('state-timeout').style.display = 'block';
        }}
      }})
      .catch(function() {{
        if (attempts++ < MAX) setTimeout(poll, 3000);
      }});
  }}
  poll();
</script>
</body></html>
"""


@app.get("/status/{subdomain}")
def tenant_status(subdomain: str):
    return {"ready": provisioning.database_exists(subdomain)}


@app.get("/welcome", response_class=HTMLResponse)
def welcome(s: str = None, subdomain: str = None):
    sub = subdomain or "your-workspace"
    return WELCOME_PAGE.format(
        subdomain=sub,
        subdomain_js=sub,
        domain=BASE_DOMAIN,
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "everjust-control-plane"}
