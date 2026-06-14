#!/usr/bin/env python3
"""Build the web brand assets from the source logos in static/img/brand/.

Sources (the real EVERJUST brand files):
  brand/wordmark.webp   horizontal "EVERJUST" wordmark, black on white
  brand/cube.webp       purple 3D "EVER JUST" cube, transparent bg
  brand/mark-square.png black stacked "EVER JUST" square mark, transparent

Generates:
  wordmark.png          trimmed wordmark, black on transparent  (light header)
  wordmark-white.png    trimmed wordmark, white on transparent  (dark footer / cards)
  icon-192x192.png      cube on white   (PWA)
  icon-512x512.png      cube on white   (PWA)
  apple-touch-icon.png  cube on white   (iOS home screen, opaque)
  favicon.ico           cube on white, multi-size (16/32/48)

Run: python3 scripts/build_brand_assets.py
"""
import pathlib

from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parents[1]
IMG = ROOT / "static" / "img"
BRAND = IMG / "brand"


def _wordmark(rgb, thresh=45):
    """Black-on-white wordmark -> rgb-on-transparent, trimmed to content."""
    im = Image.open(BRAND / "wordmark.webp").convert("RGB")
    alpha = ImageChops.invert(im.convert("L")).point(lambda a: a if a >= thresh else 0)
    solid = Image.new("RGBA", im.size, rgb + (0,))
    solid.putalpha(alpha)
    return solid.crop(solid.getbbox())


def _cube_icon(size, pad_ratio=0.10, bg=(255, 255, 255, 255)):
    cube = Image.open(BRAND / "cube.webp").convert("RGBA")
    cube = cube.crop(cube.getbbox())
    canvas = Image.new("RGBA", (size, size), bg)
    inner = int(size * (1 - 2 * pad_ratio))
    w, h = cube.size
    s = inner / max(w, h)
    r = cube.resize((int(w * s), int(h * s)), Image.LANCZOS)
    canvas.alpha_composite(r, ((size - r.size[0]) // 2, (size - r.size[1]) // 2))
    return canvas


def main():
    _wordmark((17, 17, 19)).save(IMG / "wordmark.png")
    _wordmark((255, 255, 255)).save(IMG / "wordmark-white.png")

    _cube_icon(192).convert("RGB").save(IMG / "icon-192x192.png")
    _cube_icon(512).convert("RGB").save(IMG / "icon-512x512.png")
    _cube_icon(180).convert("RGB").save(IMG / "apple-touch-icon.png")
    ico = _cube_icon(48).convert("RGB")
    ico.save(IMG / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    print("brand assets written to", IMG.relative_to(ROOT))


if __name__ == "__main__":
    main()
