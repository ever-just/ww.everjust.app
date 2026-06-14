#!/usr/bin/env python3
"""Generate the per-app 3D product images and optimize them for the web.

Each app gets a soft glossy 3D render in the EVERJUST brand style (the frosted
lavender/purple "cube" look), themed to what the app does. Output is a small
webp at static/img/apps/<slug>.webp used as the app-page hero visual.

Renders are cached as PNGs in APPIMG_SRC (default /tmp/appimg) so re-runs don't
re-bill the API; delete a cached PNG to regenerate that app. Needs Pillow and
an OpenAI key at ~/.everjust_openai.key.

    python3 scripts/gen_app_images.py
"""
import base64
import json
import os
import pathlib
import time
import urllib.request

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = pathlib.Path(os.environ.get("APPIMG_SRC", "/tmp/appimg"))
OUT = ROOT / "static" / "img" / "apps"
SIZE = 480

STYLE = ("Soft glossy 3D render, translucent matte lavender-and-purple material with a "
         "subtle internal glow (same look as a frosted purple cube), floating and centered "
         "on a clean very-light lavender-white studio background, soft realistic shadows, "
         "minimal, premium product render, no text, no logos, high detail.")

SUBJECTS = {
    "crm-sales": "an upward-trending set of three rounded bars with a small pin marker on the tallest",
    "inventory": "a neat stack of three rounded shipping boxes",
    "chat": "two overlapping rounded chat speech bubbles",
    "projects": "a kanban board card with a checkmark",
    "documents": "a small stack of rounded document pages",
    "signatures": "a fountain pen signing a rounded document with a signature line",
    "wiki": "an open rounded book with a bookmark",
    "hr-time-off": "a rounded calendar page with a small palm leaf",
    "payroll": "a rounded paycheck with a stack of coins",
    "calls-sms": "a rounded phone handset with a small message bubble",
    "sales": "a rounded signed quote document with a checkmark",
    "pos": "a rounded point-of-sale card terminal",
    "invoicing": "a rounded invoice receipt with a dollar symbol",
    "expenses": "a rounded receipt with a single coin",
    "purchase": "a rounded shopping cart with a small box",
    "manufacturing": "three interlocking rounded gears",
    "maintenance": "a rounded wrench crossed with a small gear",
    "recruitment": "a rounded person profile badge with a magnifying glass",
    "fleet": "a cute rounded delivery truck",
    "email-marketing": "a rounded envelope with a small paper plane",
    "events": "a rounded calendar page with a star",
    "surveys": "a rounded clipboard with checkmarks and a star",
    "website": "a rounded browser window frame",
    "ecommerce": "a rounded shopping bag with a price tag",
    "blog": "a rounded page with a pencil writing",
    "courses": "a rounded graduation cap",
    "livechat": "a rounded chat bubble with a small headset",
    "calendar": "a single rounded calendar page",
    "contacts": "a rounded address-book card with a person silhouette",
}


def _generate(slug, subject, dst):
    key = pathlib.Path(os.path.expanduser("~/.everjust_openai.key")).read_text().strip()
    body = json.dumps({"model": "gpt-image-1", "prompt": f"{STYLE} Subject: {subject}.",
                       "size": "1024x1024", "quality": "medium", "n": 1}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=240))
            dst.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
            return
        except Exception as e:
            print("retry", slug, attempt, str(e)[:80]); time.sleep(5)
    raise SystemExit(f"generation failed: {slug}")


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for slug, subject in SUBJECTS.items():
        png = SRC / f"{slug}.png"
        if not png.exists():
            print("generating", slug)
            _generate(slug, subject, png)
        img = Image.open(png).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
        out = OUT / f"{slug}.webp"
        img.save(out, "WEBP", quality=82, method=6)
        total += out.stat().st_size
    print(f"wrote {len(SUBJECTS)} app images to {OUT.relative_to(ROOT)} ({total // 1024} KB total)")


if __name__ == "__main__":
    main()
