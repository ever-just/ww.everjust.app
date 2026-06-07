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

ODOO_CONTAINER = os.environ.get("ODOO_CONTAINER", "deployment-odoo-1")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "everjust.app")
GODADDY_KEY = os.environ.get("GODADDY_API_KEY", "")
GODADDY_SECRET = os.environ.get("GODADDY_API_SECRET", "")

EVERJUST_MODULES = "base,everjust_brand,everjust_theme"

SUBDOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")
RESERVED = {"www", "app", "api", "admin", "mail", "ftp", "staging", "test"}


def validate_subdomain(sub: str) -> bool:
    sub = (sub or "").lower()
    return bool(SUBDOMAIN_RE.match(sub)) and sub not in RESERVED


def database_exists(name: str) -> bool:
    result = subprocess.run(
        ["docker", "exec", ODOO_CONTAINER, "psql", "-U", "everjust", "-tAc",
         f"SELECT 1 FROM pg_database WHERE datname='{name}'"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() == "1"


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
         "-i", EVERJUST_MODULES,
         "--load-language=en_US",
         "--stop-after-init",
         "--no-http"],
        check=True,
    )

    _set_admin_credentials(subdomain, admin_login, admin_password)
    ensure_dns(subdomain)

    return {
        "subdomain": subdomain,
        "url": f"https://{subdomain}.{BASE_DOMAIN}",
        "status": "active",
    }


def _set_admin_credentials(db: str, login: str, password: str) -> None:
    """Point the default admin user at the signup email + password."""
    sql = (
        f"UPDATE res_users SET login='{login}' WHERE id=2; "
    )
    subprocess.run(
        ["docker", "exec", ODOO_CONTAINER, "psql", "-U", "everjust", "-d", db, "-c", sql],
        check=True,
    )
    # Password is hashed by Odoo; set it through the ORM shell for safety.
    py = (
        "env['res.users'].browse(2).write({'password': %r}); env.cr.commit()" % password
    )
    subprocess.run(
        ["docker", "exec", ODOO_CONTAINER, "odoo", "shell", "-d", db, "--no-http"],
        input=py, text=True, check=False,
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
    sql = "UPDATE res_users SET active=false WHERE id!=1;"
    subprocess.run(
        ["docker", "exec", ODOO_CONTAINER, "psql", "-U", "everjust", "-d", subdomain, "-c", sql],
        check=False,
    )
