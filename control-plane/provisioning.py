# -*- coding: utf-8 -*-
"""Tenant provisioning for EVERJUST.APP.

Each tenant gets its own PostgreSQL database, initialized with the base
modules plus the EVERJUST branding and theme modules. Subdomain routing is
handled by Nginx + Odoo's dbfilter, so no per-tenant Nginx change is needed.
"""
import os
import re
import subprocess
import httpx
import psycopg2

ODOO_CONTAINER = os.environ.get("ODOO_CONTAINER", "deployment-odoo-1")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "everjust.app")
GODADDY_KEY = os.environ.get("GODADDY_API_KEY", "")
GODADDY_SECRET = os.environ.get("GODADDY_API_SECRET", "")

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_USER = os.environ.get("POSTGRES_USER", "everjust")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")


def _pg_connect(dbname: str = "postgres"):
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, dbname=dbname, connect_timeout=10,
    )

EVERJUST_MODULES = "base,everjust_brand,everjust_theme,everjust_home,voip_oca,everjust_sms_gateway,everjust_phone,document_page,document_page_partner,document_url,attachment_zipped_download,dms,payroll,sign_oca,hr_holidays,hr_timesheet"

# ── Onboarding personalization: industry/goals -> Community app modules ──
# So a new workspace lands shaped for the customer instead of empty. Values
# are Odoo Community technical module names; only names in ALLOWED_MODULES
# are ever installed (the captured industry/goal strings can't inject other
# modules).
INDUSTRY_MODULES = {
    "Professional services / agency": ["crm", "sale_management", "account", "project", "hr_timesheet"],
    "Retail / eCommerce": ["website", "website_sale", "stock", "point_of_sale", "account"],
    "Software / technology": ["crm", "project", "hr_timesheet", "account"],
    "Manufacturing": ["stock", "purchase", "mrp", "sale_management", "account"],
    "Hospitality / food": ["point_of_sale", "stock", "purchase", "hr"],
    "Construction / trades": ["project", "stock", "purchase", "account", "fleet"],
    "Healthcare": ["crm", "calendar", "account", "hr"],
    "Nonprofit": ["crm", "account", "event", "mass_mailing"],
}
GOAL_MODULES = {
    "Sales & CRM": ["crm", "sale_management"],
    "Invoicing & Finance": ["account", "hr_expense"],
    "Projects & Operations": ["project", "hr_timesheet", "stock"],
    "HR & Payroll": ["hr", "hr_holidays"],
    "Marketing": ["mass_mailing", "event"],
    "Website & Store": ["website", "website_sale"],
}
DEFAULT_MODULES = ["crm", "sale_management", "account", "contacts", "calendar"]
ALLOWED_MODULES = (
    set(DEFAULT_MODULES)
    | {m for mods in INDUSTRY_MODULES.values() for m in mods}
    | {m for mods in GOAL_MODULES.values() for m in mods}
)


def personalized_modules(industry: str = "", goals: str = "") -> list[str]:
    """Resolve captured industry + goals into a de-duplicated, allow-listed
    list of Community modules to switch on for a new tenant."""
    picks = list(INDUSTRY_MODULES.get((industry or "").strip(), []))
    for goal in (g.strip() for g in (goals or "").split(",") if g.strip()):
        picks += GOAL_MODULES.get(goal, [])
    if not picks:
        picks = list(DEFAULT_MODULES)
    seen, out = set(), []
    for m in picks:
        if m in ALLOWED_MODULES and m not in seen:
            seen.add(m)
            out.append(m)
    return out


SUBDOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")
RESERVED = {"www", "app", "api", "admin", "mail", "ftp", "staging", "test"}


def validate_subdomain(sub: str) -> bool:
    sub = (sub or "").lower()
    return bool(SUBDOMAIN_RE.match(sub)) and sub not in RESERVED


def database_exists(name: str) -> bool:
    conn = _pg_connect()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (name,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def provision_tenant(subdomain: str, admin_login: str, admin_password: str,
                     personalization: dict | None = None) -> dict:
    """Create and initialize a new tenant database.

    ``personalization`` (industry, website, team_size, goals) is captured at
    signup. Stage 1 records it so it travels with provisioning; later stages
    use it to install the industry/goal app set and apply branding from the
    website. It is always best-effort and never blocks base provisioning.
    """
    if not validate_subdomain(subdomain):
        raise ValueError(f"Invalid or reserved subdomain: {subdomain}")
    if database_exists(subdomain):
        raise ValueError(f"Tenant already exists: {subdomain}")

    # Initialize the database with EVERJUST modules via the Odoo CLI.
    subprocess.run(
        ["docker", "exec", ODOO_CONTAINER, "odoo",
         "-d", subdomain,
         "--db_user", DB_USER,
         "--db_password", DB_PASSWORD,
         "-i", EVERJUST_MODULES,
         "--load-language=en_US",
         "--stop-after-init",
         "--no-http"],
        check=True,
    )

    _set_admin_credentials(subdomain, admin_login, admin_password)
    _configure_mail(subdomain)
    _configure_dms(subdomain)
    _record_personalization(subdomain, personalization or {})
    _install_personalized_apps(subdomain, personalization or {})
    _apply_website_branding(subdomain, (personalization or {}).get("website", ""))
    ensure_dns(subdomain)

    return {
        "subdomain": subdomain,
        "url": f"https://{subdomain}.{BASE_DOMAIN}",
        "status": "active",
    }


def _apply_website_branding(subdomain: str, website: str) -> None:
    """Brand the tenant from its website (name, website, logo, theme color).

    SSRF-guarded fetch via website_enrichment; everything is best-effort and
    wrapped so a failure never affects the provisioned workspace."""
    if not website:
        return
    try:
        import base64
        import website_enrichment

        brand = website_enrichment.enrich(website)
        if not brand:
            return

        logo_b64 = ""
        logo_url = brand.get("logo_url")
        if logo_url:
            got = website_enrichment.safe_get(logo_url)
            if got:
                _url, data = got
                # Only accept real raster/vector image bytes, capped in size.
                magic = data[:12]
                is_img = (magic.startswith(b"\x89PNG") or magic.startswith(b"\xff\xd8")
                          or magic.startswith(b"GIF8") or magic[:4] == b"RIFF"
                          or b"<svg" in data[:200].lower())
                if is_img and len(data) <= 512 * 1024:
                    logo_b64 = base64.b64encode(data).decode()

        color = brand.get("theme_color", "")
        py = (
            "company = env['res.company'].browse(1)\n"
            "vals = {}\n"
            "if %(web)r: vals['website'] = %(web)r\n"
            "if %(logo)r: vals['logo'] = %(logo)r\n"
            "if vals: company.write(vals)\n"
            "if %(color)r: env['ir.config_parameter'].sudo()"
            ".set_param('everjust.brand.color', %(color)r)\n"
            "env.cr.commit()\n"
            % {"web": website, "logo": logo_b64, "color": color}
        )
        subprocess.run(
            ["docker", "exec", "-i", ODOO_CONTAINER, "odoo", "shell",
             "-d", subdomain, "--db_user", DB_USER,
             "--db_password", DB_PASSWORD, "--no-http"],
            input=py, text=True, check=False, timeout=120,
        )
    except Exception:
        pass


def _install_personalized_apps(subdomain: str, data: dict) -> None:
    """Switch on the apps that match the captured industry/goals, so the
    workspace lands ready to use. Best-effort and allow-listed; a failure
    here never affects the already-provisioned base tenant."""
    modules = personalized_modules(data.get("industry", ""), data.get("goals", ""))
    if not modules:
        return
    try:
        subprocess.run(
            ["docker", "exec", ODOO_CONTAINER, "odoo",
             "-d", subdomain,
             "--db_user", DB_USER,
             "--db_password", DB_PASSWORD,
             "-i", ",".join(modules),
             "--stop-after-init",
             "--no-http"],
            check=False, timeout=900,
        )
    except Exception:
        pass


def _record_personalization(subdomain: str, data: dict) -> None:
    """Persist the onboarding context as company config params on the tenant.

    Stage 1: store the captured signals (industry, website, team size, goals)
    as ir.config_parameter values so a later configuration pass can read them.
    Best-effort; failures never affect the base tenant.
    """
    if not any(data.values()):
        return
    py = (
        "P = env['ir.config_parameter'].sudo()\n"
        "for k, v in %r.items():\n"
        "    if v:\n"
        "        P.set_param('everjust.onboarding.' + k, v)\n"
        "env.cr.commit()\n" % {k: str(v) for k, v in data.items()}
    )
    try:
        subprocess.run(
            ["docker", "exec", "-i", ODOO_CONTAINER, "odoo", "shell",
             "-d", subdomain, "--db_user", DB_USER,
             "--db_password", DB_PASSWORD, "--no-http"],
            input=py, text=True, check=False, timeout=120,
        )
    except Exception:
        pass


def _set_admin_credentials(db: str, login: str, password: str) -> None:
    """Point the default admin user at the signup email + password.

    Login is set via SQL; the password is hashed by Odoo so it is written
    through the ORM shell, which also resets the company/admin defaults.
    """
    py = (
        "env['res.users'].browse(2).write({'login': %r, 'password': %r, 'action_id': False}); "
        "env.cr.commit()" % (login, password)
    )
    subprocess.run(
        ["docker", "exec", "-i", ODOO_CONTAINER, "odoo", "shell",
         "-d", db, "--db_user", DB_USER, "--db_password", DB_PASSWORD, "--no-http"],
        input=py, text=True, check=False,
    )


MAIL_DOMAIN = os.environ.get("MAIL_DOMAIN", "everjust.co")

# Configures outgoing mail for a freshly provisioned tenant so every instance
# sends through Resend and every message comes from the verified domain.
# Runs inside the Odoo container, which already has RESEND_API_KEY in its env
# (via env_file), so the secret is never interpolated into the command string.
_MAIL_SETUP_PY = """
import os
key = os.environ.get('RESEND_API_KEY')
domain = os.environ.get('MAIL_DOMAIN', 'everjust.co')
Server = env['ir.mail_server']
if key and not Server.search([]):
    Server.create({
        'name': 'Resend (EVERJUST.APP)',
        'smtp_host': 'smtp.resend.com',
        'smtp_port': 465,
        'smtp_encryption': 'ssl',
        'smtp_authentication': 'login',
        'smtp_user': 'resend',
        'smtp_pass': key,
        'from_filter': domain,
        'sequence': 5,
    })
Dom = env['mail.alias.domain']
dom = Dom.search([('name', '=', domain)], limit=1)
if not dom:
    dom = Dom.create({
        'name': domain,
        'bounce_alias': 'bounce',
        'catchall_alias': 'catchall',
        'default_from': 'noreply',
    })
for company in env['res.company'].search([]):
    company.alias_domain_id = dom.id
env['ir.config_parameter'].sudo().set_param('mail.catchall.domain', domain)
env['ir.config_parameter'].sudo().set_param('mail.default.from', 'noreply')
env.cr.commit()
"""


def _configure_mail(db: str) -> None:
    """Wire the tenant to Resend + the verified everjust.co sending domain."""
    subprocess.run(
        ["docker", "exec", "-i", ODOO_CONTAINER, "odoo", "shell",
         "-d", db, "--db_user", DB_USER, "--db_password", DB_PASSWORD, "--no-http"],
        input=_MAIL_SETUP_PY, text=True, check=False,
    )


_DMS_SETUP_PY = """
# Add admin to DMS Manager group and create default storage + directory
dms_mgr = env.ref('dms.group_dms_manager', raise_if_not_found=False)
admin = env['res.users'].browse(2)
if dms_mgr and dms_mgr.id not in admin.group_ids.ids:
    admin.write({'group_ids': [(4, dms_mgr.id)]})

# Create default storage and root directory with full-access group
if not env['dms.storage'].search([], limit=1):
    storage = env['dms.storage'].create({'name': 'Default Storage', 'save_type': 'database'})
    root_dir = env['dms.directory'].create({
        'name': 'Documents',
        'storage_id': storage.id,
        'is_root_directory': True,
    })
    if dms_mgr:
        access_group = env['dms.access.group'].create({
            'name': 'Full Access',
            'perm_create': True,
            'perm_write': True,
            'perm_unlink': True,
            'group_ids': [(4, dms_mgr.id)],
        })
        root_dir.write({'group_ids': [(4, access_group.id)]})
env.cr.commit()
"""


def _configure_dms(db: str) -> None:
    """Set up DMS with default storage, root directory, and admin permissions."""
    subprocess.run(
        ["docker", "exec", "-i", ODOO_CONTAINER, "odoo", "shell",
         "-d", db, "--db_user", DB_USER, "--db_password", DB_PASSWORD, "--no-http"],
        input=_DMS_SETUP_PY, text=True, check=False,
    )


def ensure_dns(subdomain: str) -> None:
    """Ensure <subdomain>.everjust.app resolves. With a wildcard A record
    already in place this is a no-op; included for explicit per-tenant records."""
    if not (GODADDY_KEY and GODADDY_SECRET):
        return
    server_ip = os.environ.get("SERVER_IP")
    if not server_ip:
        return
    headers = {"Authorization": f"sso-key {GODADDY_KEY}:{GODADDY_SECRET}"}
    url = f"https://api.godaddy.com/v1/domains/{BASE_DOMAIN}/records/A/{subdomain}"
    body = [{"data": server_ip, "ttl": 600}]
    httpx.put(url, headers=headers, json=body, timeout=20)


def suspend_tenant(subdomain: str) -> None:
    """Stop serving a tenant (e.g. on failed payment) without deleting data."""
    if not database_exists(subdomain):
        return
    conn = _pg_connect(subdomain)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("UPDATE res_users SET active=false WHERE id NOT IN (1, 2)")
    finally:
        conn.close()
