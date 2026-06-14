#!/usr/bin/env python3
"""Build the social/OG share card (static/img/og-card.jpg).

A premium 1200x630 card: a subtle AI-generated monochrome texture backdrop
(via the OpenAI Images API) under a heavy dark scrim — so the crisp
Space Grotesk text on top is always legible regardless of the texture.

Run: python3 scripts/build_og_image.py
Needs: Pillow, a Space Grotesk TTF at /tmp/sg.ttf, and either a cached
texture at /tmp/ej_texture.png or an OpenAI key at ~/.everjust_openai.key.
"""
import base64
import json
import os
import pathlib
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "img" / "og-card.jpg"
TTF = "/tmp/sg.ttf"
TEXTURE = pathlib.Path("/tmp/ej_texture.png")
W, H = 1200, 630
MARGIN = 80


def _texture() -> Image.Image:
    """Return the backdrop texture, generating it once if not cached."""
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


def main():
    # Backdrop: texture cropped to cover, darkened, scrimmed to near-black.
    tex = _texture()
    scale = max(W / tex.width, H / tex.height)
    tex = tex.resize((int(tex.width * scale), int(tex.height * scale)))
    left = (tex.width - W) // 2
    top = (tex.height - H) // 2
    tex = tex.crop((left, top, left + W, top + H))
    tex = ImageEnhance.Brightness(tex).enhance(0.45)
    img = Image.new("RGB", (W, H), (8, 8, 10))
    img.paste(tex, (0, 0))
    scrim = Image.new("RGBA", (W, H), (8, 8, 10, 190))
    img = Image.alpha_composite(img.convert("RGBA"), scrim).convert("RGB")

    draw = ImageDraw.Draw(img)
    white = (255, 255, 255)
    grey = (200, 201, 208)

    # Logo mark + wordmark lockup (top-left).
    mark = Image.open(ROOT / "static" / "img" / "logo-white.png").convert("RGBA").resize((50, 50), Image.LANCZOS)
    img.paste(mark, (MARGIN, MARGIN - 2), mark)
    wm = _font(34, 600)
    draw.text((MARGIN + 62, MARGIN + 8), "EVERJUST.APP", font=wm, fill=white)

    # Headline.
    head = _font(78, 700)
    lines = _wrap(draw, "Run your whole company in one place.", head, W - 2 * MARGIN)
    y = 250
    for ln in lines:
        draw.text((MARGIN, y), ln, font=head, fill=white)
        y += 88

    # Sub-line near the bottom.
    sub = _font(32, 500)
    draw.text((MARGIN, H - MARGIN - 36), "29 apps. One workspace. One price.",
              font=sub, fill=grey)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB, {W}x{H})")


if __name__ == "__main__":
    main()
