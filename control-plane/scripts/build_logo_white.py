#!/usr/bin/env python3
"""Generate a white-on-transparent version of the EVERJUST mark for dark
surfaces (footer, social cards), from the black-on-white source icon.

The source is a black "EVER JUST" mark on a white background. We turn the
dark pixels into opaque white and the light background into transparency,
so the same logo reads correctly on a dark background.

Run: python3 scripts/build_logo_white.py
"""
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "static" / "img" / "icon-512x512.png"
OUT = ROOT / "static" / "img" / "logo-white.png"


def main():
    im = Image.open(SRC).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lum = (r * 299 + g * 587 + b * 114) // 1000   # 0=black, 255=white
            # Dark source pixels -> opaque white; light -> transparent.
            px[x, y] = (255, 255, 255, (255 - lum) * a // 255)
    im.save(OUT)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB, {w}x{h})")


if __name__ == "__main__":
    main()
