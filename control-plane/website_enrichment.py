# -*- coding: utf-8 -*-
"""Best-effort website enrichment for onboarding personalization.

Given a customer's website URL (captured at signup), fetch the homepage and
extract brand signals — company name, description, logo, theme color — used
to brand the freshly provisioned workspace.

SECURITY: the URL is attacker-controllable, so every fetch is guarded
against SSRF — only public http(s) hosts are allowed, and every resolved IP
(including across redirects) is checked against private/loopback/link-local/
reserved ranges before we connect. Failures are swallowed: enrichment never
blocks or breaks provisioning.
"""
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse

import httpx

MAX_BYTES = 512 * 1024
MAX_REDIRECTS = 3
TIMEOUT = 8.0


def _ip_blocked(ip_str: str) -> bool:
    """True if an IP must not be fetched (private, loopback, link-local,
    reserved, multicast, unspecified — e.g. cloud metadata 169.254.169.254)."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified)


def _host_allowed(host: str) -> bool:
    """Resolve a hostname and require every address to be public."""
    if not host or host.lower() == "localhost":
        return False
    # A literal IP host is checked directly.
    try:
        ipaddress.ip_address(host)
        return not _ip_blocked(host)
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    addrs = {info[4][0] for info in infos}
    return bool(addrs) and all(not _ip_blocked(a) for a in addrs)


def _url_allowed(url: str) -> bool:
    p = urlparse(url)
    return p.scheme in ("http", "https") and bool(p.hostname) and _host_allowed(p.hostname)


def safe_get(url: str) -> tuple[str, bytes] | None:
    """Fetch a URL with SSRF guards, manual redirect re-validation, and a
    size cap. Returns (final_url, body) or None. Never raises."""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        current = url
        for _ in range(MAX_REDIRECTS + 1):
            if not _url_allowed(current):
                return None
            with httpx.Client(follow_redirects=False, timeout=TIMEOUT,
                              headers={"User-Agent": "EverjustBot/1.0"}) as client:
                resp = client.get(current)
            if resp.is_redirect:
                loc = resp.headers.get("location")
                if not loc:
                    return None
                current = urljoin(current, loc)
                continue
            if resp.status_code != 200:
                return None
            return current, resp.content[:MAX_BYTES]
        return None
    except Exception:
        return None


def _meta(html: str, *, prop=None, name=None) -> str | None:
    attr, val = ("property", prop) if prop else ("name", name)
    m = re.search(
        r'<meta[^>]+%s=["\']%s["\'][^>]+content=["\']([^"\']+)["\']' % (attr, re.escape(val)),
        html, re.I)
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+%s=["\']%s["\']' % (attr, re.escape(val)),
            html, re.I)
    return m.group(1).strip() if m else None


def extract_brand(html: str, base_url: str) -> dict:
    """Pull brand signals from homepage HTML. All fields best-effort."""
    html = html if isinstance(html, str) else html.decode("utf-8", "replace")
    out: dict = {}

    name = _meta(html, prop="og:site_name")
    if not name:
        t = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        if t:
            name = re.split(r"\s[|\-–—]\s", t.group(1).strip())[0].strip()
    if name:
        out["name"] = name[:80]

    desc = _meta(html, name="description") or _meta(html, prop="og:description")
    if desc:
        out["description"] = desc[:200]

    color = _meta(html, name="theme-color")
    if color and re.match(r"^#?[0-9a-fA-F]{3,8}$", color.strip()):
        out["theme_color"] = color.strip()

    # Logo candidates, best first: apple-touch-icon, sized icon, og:image.
    logo = None
    for rel in ("apple-touch-icon", "icon", "shortcut icon"):
        m = re.search(r'<link[^>]+rel=["\'][^"\']*%s[^"\']*["\'][^>]+href=["\']([^"\']+)["\']'
                      % re.escape(rel), html, re.I)
        if m:
            logo = urljoin(base_url, m.group(1))
            break
    if not logo:
        og = _meta(html, prop="og:image")
        if og:
            logo = urljoin(base_url, og)
    # Extraction is pure parsing; the SSRF guard runs when the logo is
    # actually fetched (safe_get) before it's applied.
    if logo and logo.startswith(("http://", "https://")):
        out["logo_url"] = logo

    return out


def enrich(url: str) -> dict:
    """Fetch + extract brand signals for a website. Returns {} on any failure."""
    if not url:
        return {}
    got = safe_get(url)
    if not got:
        return {}
    final_url, body = got
    try:
        return extract_brand(body, final_url)
    except Exception:
        return {}
