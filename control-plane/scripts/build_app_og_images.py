#!/usr/bin/env python3
"""Build a per-app social/OG share card for every catalog app.

Each app gets its own 1200x630 card (static/img/og/<slug>.jpg) built on the
same branded backdrop as the primary og-card: the subtle monochrome texture
under a dark scrim, with the EVERJUST.APP wordmark, the app's category as an
eyebrow, the app name as the headline, and its tagline beneath. This way a
link to /apps/inventory unfurls as an Inventory card, not the generic one.

Run: python3 scripts/build_app_og_images.py
Needs: Pillow, a Space Grotesk TTF at /tmp/sg.ttf, and either a cached
texture at /tmp/ej_texture.png or an OpenAI key at ~/.everjust_openai.key
(the texture is generated once and reused for every card).
"""
import base64
import json
import os
import pathlib
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import content  # noqa: E402

OUT_DIR = ROOT / "static" / "img" / "og"
TTF = "/tmp/sg.ttf"
TEXTURE = pathlib.Path("/tmp/ej_texture.png")
W, H = 1200, 630
MARGIN = 80


_LOGO_CACHE = None


def _logo(size: int = 50) -> Image.Image:
    """The white-on-transparent mark, resized once and reused per card."""
    global _LOGO_CACHE
    if _LOGO_CACHE is None or _LOGO_CACHE.size != (size, size):
        path = ROOT / "static" / "img" / "logo-white.png"
        _LOGO_CACHE = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    return _LOGO_CACHE


def _texture() -> Image.Image:
    if TEXTURE.exists():
        return Image.open(TEXTURE).convert("RGB")
    key = pathlib.Path(os.path.expanduser("~/.everjust_openai.key")).read_text().strip()
    prompt = ("Minimal abstract monochrome background texture, pure black and white, "
              "fine architectural geometric lines, premium high-end, lots of negative "
              "space, no text, no logos, subtle editorial matte.")
    body = json.dumps({"model": "gpt-image-1", "prompt": prompt,
                       "size": "1536x1024", "quality": "low", "n": 1}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req, timeout=180))
    TEXTURE.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
    return Image.open(TEXTURE).convert("RGB")


def _font(px: int, weight: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(TTF, px)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def _wrap(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = (line + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def _backdrop() -> Image.Image:
    """The shared darkened, scrimmed texture — built once, copied per card."""
    tex = _texture()
    scale = max(W / tex.width, H / tex.height)
    tex = tex.resize((int(tex.width * scale), int(tex.height * scale)))
    left = (tex.width - W) // 2
    top = (tex.height - H) // 2
    tex = tex.crop((left, top, left + W, top + H))
    tex = ImageEnhance.Brightness(tex).enhance(0.45)
    img = Image.new("RGB", (W, H), (8, 8, 10))
    img.paste(tex, (0, 0))
    scrim = Image.new("RGBA", (W, H), (8, 8, 10, 195))
    return Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")


def _card(base: Image.Image, app_name: str, category: str, tagline: str) -> Image.Image:
    img = base.copy()
    draw = ImageDraw.Draw(img)
    white = (255, 255, 255)
    grey = (200, 201, 208)
    faint = (150, 151, 160)

    # Logo mark + wordmark lockup (top-left).
    mark = _logo()
    img.paste(mark, (MARGIN, MARGIN - 2), mark)
    wm = _font(34, 600)
    draw.text((MARGIN + 62, MARGIN + 8), "EVERJUST.APP", font=wm, fill=white)

    # Category eyebrow (top-right, upper-cased), spaced for an editorial feel.
    eye = _font(26, 600)
    label = " ".join(category.upper())
    draw.text((W - MARGIN - draw.textlength(label, font=eye), MARGIN + 4),
              label, font=eye, fill=faint)

    # App name headline — size steps down if it would wrap past two lines.
    for px, step in ((104, 112), (84, 92), (66, 74)):
        head = _font(px, 700)
        lines = _wrap(draw, app_name, head, W - 2 * MARGIN)
        if len(lines) <= 2:
            break
    block_h = step * len(lines)
    y = (H - block_h) // 2 - 20
    for ln in lines:
        draw.text((MARGIN, y), ln, font=head, fill=white)
        y += step

    # Tagline beneath the headline.
    sub = _font(36, 500)
    for ln in _wrap(draw, tagline, sub, W - 2 * MARGIN):
        draw.text((MARGIN, y + 8), ln, font=sub, fill=grey)
        y += 46

    # Footer cue, bottom-left.
    foot = _font(28, 500)
    draw.text((MARGIN, H - MARGIN - 30), "One workspace. One price.",
              font=foot, fill=faint)
    return img


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = _backdrop()
    cats = content.CATEGORIES
    total = 0
    for slug, a in content.APPS.items():
        cat_slug = a.get("category", "")
        cat_name = cats.get(cat_slug, {}).get("name", cat_slug) if cat_slug else "App"
        img = _card(base, a["name"], cat_name, a.get("tagline", ""))
        out = OUT_DIR / f"{slug}.jpg"
        img.save(out, "JPEG", quality=84, optimize=True, progressive=True)
        total += out.stat().st_size
    print(f"wrote {len(content.APPS)} cards to {OUT_DIR.relative_to(ROOT)} "
          f"({total // 1024} KB total)")


if __name__ == "__main__":
    main()
