# -*- coding: utf-8 -*-
import os
import sys
import pathlib

# Make the control-plane package importable and provide required env vars
# before `main` is imported.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_dummy")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_dummy")
os.environ.setdefault("BASE_DOMAIN", "everjust.app")

import pytest
from fastapi.testclient import TestClient

import main
import provisioning
import signup_store


@pytest.fixture
def existing_dbs():
    """Mutable set standing in for the tenant database list."""
    return {"acme", "headsup"}


@pytest.fixture
def client(monkeypatch, existing_dbs):
    monkeypatch.setattr(provisioning, "database_exists", lambda name: name in existing_dbs)

    pending = {}

    def fake_create(org_name, subdomain, admin_email, admin_password, **extra):
        token = f"tok_{len(pending)}"
        pending[token] = {
            "org_name": org_name,
            "subdomain": subdomain,
            "admin_email": admin_email,
            "admin_password": admin_password,
            **extra,
        }
        return token

    monkeypatch.setattr(signup_store, "create", fake_create)
    monkeypatch.setattr(signup_store, "pop", lambda token: pending.pop(token, None))

    client = TestClient(main.app)
    client.pending_signups = pending
    return client
