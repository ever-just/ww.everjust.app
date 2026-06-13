# -*- coding: utf-8 -*-
"""Server-side store for pending signups.

Signup details (including the admin password needed to initialize the
tenant) are held here under a random token; only the token travels through
Stripe metadata. Rows are deleted once the tenant is provisioned and
expire automatically so abandoned checkouts leave nothing behind.

Beyond the credentials, we keep optional onboarding context (industry,
website, team size, goals) used to personalize the provisioned workspace.
"""
import secrets

import provisioning

TABLE = "everjust_pending_signups"
TTL_DAYS = 7

_DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    token       TEXT PRIMARY KEY,
    org_name    TEXT NOT NULL,
    subdomain   TEXT NOT NULL,
    admin_email TEXT NOT NULL,
    admin_password TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

# Personalization columns, added idempotently so an existing table migrates.
_PERSONALIZATION_COLS = ("industry", "website", "team_size", "goals")


def _conn():
    return provisioning._pg_connect()


def _ensure_table(cur):
    cur.execute(_DDL)
    for col in _PERSONALIZATION_COLS:
        cur.execute(f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {col} TEXT")
    cur.execute(f"DELETE FROM {TABLE} WHERE created_at < now() - interval '{TTL_DAYS} days'")


def create(org_name: str, subdomain: str, admin_email: str, admin_password: str,
           industry: str = "", website: str = "", team_size: str = "",
           goals: str = "") -> str:
    """Persist a pending signup and return its opaque token."""
    token = secrets.token_urlsafe(32)
    conn = _conn()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            _ensure_table(cur)
            cur.execute(
                f"INSERT INTO {TABLE} (token, org_name, subdomain, admin_email,"
                " admin_password, industry, website, team_size, goals)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (token, org_name, subdomain, admin_email, admin_password,
                 industry or "", website or "", team_size or "", goals or ""),
            )
    finally:
        conn.close()
    return token


def pop(token: str) -> dict | None:
    """Fetch and delete a pending signup. Returns None if unknown/expired."""
    if not token:
        return None
    conn = _conn()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            _ensure_table(cur)
            cur.execute(
                f"DELETE FROM {TABLE} WHERE token = %s"
                " RETURNING org_name, subdomain, admin_email, admin_password,"
                " industry, website, team_size, goals",
                (token,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return None
    return {
        "org_name": row[0],
        "subdomain": row[1],
        "admin_email": row[2],
        "admin_password": row[3],
        "industry": row[4] or "",
        "website": row[5] or "",
        "team_size": row[6] or "",
        "goals": row[7] or "",
    }
