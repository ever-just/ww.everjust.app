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

EVERJUST_MODULES = "base,everjust_brand,everjust_theme,everjust_home,voip_oca,everjust_sms_gateway"

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


def provision_tenant(subdomain: str, admin_login: str, admin_password: str) -> dict:
    """Create and initialize a new tenant database."""
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
    ensure_dns(subdomain)

    return {
        "subdomain": subdomain,
        "url": f"https://{subdomain}.{BASE_DOMAIN}",
        "status": "active",
    }


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
