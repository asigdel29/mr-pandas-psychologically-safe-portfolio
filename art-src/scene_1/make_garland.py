"""Draw a Tibetan prayer-flag (lungta) garland texture for Scene One.

A drooping cord strung across the sky with triangular flags in the five lungta
colours, hand-drawn doodle style (wobbly dark outline, flat fills, faint paper
ruling) to match the paper-cutout world. Transparent background. This replaces
the flying dragon, which is hidden in SceneOne.jsx.

    python3 make_garland.py garland.png
    python3 ../ktx_tools.py encode garland.png ../../public/textures/prayer_flags.ktx2
"""

from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw

LUNGTA = [(43, 108, 176), (240, 240, 234), (196, 54, 44),
          (42, 168, 96), (244, 198, 22)]
INK = (60, 58, 56)

W, H = 4096, 384


def _cord_y(x: float) -> float:
    """Two gentle sags across the width (a doubly-strung garland)."""
    a = 30 * math.sin(x / W * math.pi)             # gentle overall droop
    b = 18 * math.sin(x / W * math.pi * 9 + 0.6)   # little ripples between poles
    return 96 + a + b


def make(out_png: str) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # the cord
    pts = [(x, _cord_y(x)) for x in range(20, W - 20, 6)]
    d.line(pts, fill=INK, width=7, joint="curve")

    # square cloth flags hanging from the cord (authentic Tibetan lungta)
    n = 38
    margin = 40
    half = 38          # half-width
    drop = 150         # flag height
    for i in range(n):
        x = margin + (W - 2 * margin) * i / (n - 1)
        y = _cord_y(x)
        col = LUNGTA[i % len(LUNGTA)]
        sway = 9 * math.sin(i * 1.7)        # gentle cloth sway
        billow = 14 * math.sin(i * 0.9)     # bottom-edge wave
        top_l = (x - half, y + 4)
        top_r = (x + half, y + 4)
        bot_r = (x + half + sway, y + drop)
        bot_l = (x - half + sway, y + drop + billow)
        d.polygon([top_l, top_r, bot_r, bot_l], fill=col, outline=INK)
        d.line([top_l, top_r, bot_r, bot_l, top_l], fill=INK, width=5,
               joint="curve")
        # a faint vertical fold for the cloth look
        d.line([(x + sway * 0.3, y + 10), (x + sway * 0.7, y + drop - 6)],
               fill=(255, 255, 255, 80), width=4)

    img.save(out_png)
    print(f"garland -> {out_png} ({n} flags)")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 make_garland.py <out.png>")
        return 2
    make(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
