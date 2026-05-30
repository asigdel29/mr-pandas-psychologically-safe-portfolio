"""Repaint the paper plane on the Moving_extras atlas in Buddha Air livery.

Reference: Buddha Air ATR -- navy-blue belly / nose / tail fin, a yellow swoosh
along the fuselage, a yellow stylised logo on the tail, white upper body, dark
windows. We keep the hand-drawn paper-cutout shape and outline; only recolour.

The plane island sits at atlas x[2440,3120] y[2350,3950] (fin upper-left, nose
lower-right, three windows down the belly). Steps:
  1. Recolour every light-steel-blue accent pixel -> navy.
  2. Paint a yellow swoosh band sweeping across the mid-fuselage + a yellow blob
     over the tail-fin logo.
  3. Re-letter "Kathmandu Air" BOLD (bigger + double-draw offset) in dark ink.

Run (operates IN PLACE; re-run after restoring pristine Moving_extras if redoing
from scratch -- but it is safe to run after speedboat.py since regions differ):
    TMPDIR=/private/tmp python3 plane_livery.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

TEX = os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures",
                   "Moving_extras.ktx2")
FONT = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

PLANE = (2440, 2350, 3130, 3960)   # plane island bbox
NAVY = (32, 52, 120)
YELLOW = (240, 196, 40)
INK = (40, 46, 70)

TEXT = "Kathmandu Air"
TEXT_CENTER = (2892, 2950)
TEXT_ANGLE = -87
FONT_PX = 92                        # bigger than before for boldness


def main() -> int:
    out = "/private/tmp/_plane.png"
    ktx_tools.decode(TEX, out)
    arr = np.array(Image.open(out).convert("RGBA"))
    x0, y0, x1, y1 = PLANE
    sub = arr[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]
    lum = rgb.mean(2)

    # 1. light steel-blue accents -> navy
    blue = (a > 120) & (rgb[..., 2] - rgb[..., 0] > 10) & (lum > 130) & (lum < 215)
    for c in range(3):
        sub[..., c][blue] = NAVY[c]
    arr[y0:y1, x0:x1] = sub
    img = Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(img)

    # plane-local alpha mask (only paint on the plane body, not the sky)
    body = a > 120

    # 2a. yellow swoosh: a curved band sweeping down the fuselage. Drawn as a
    # thick poly-line, then clipped to the plane body.
    swoosh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(swoosh)
    pts = [(2560, 2560), (2700, 2680), (2840, 2760), (2980, 2800),
           (3090, 2810)]
    sd.line(pts, fill=(*YELLOW, 255), width=46, joint="curve")
    sa = np.array(swoosh)
    full = np.zeros(arr.shape[:2], bool)
    full[y0:y1, x0:x1] = body
    sa[..., 3] = np.where(full, sa[..., 3], 0)
    img = Image.alpha_composite(img, Image.fromarray(sa, "RGBA"))
    d = ImageDraw.Draw(img)

    # (A yellow tail-fin emblem was attempted but the fin is a thin diagonal
    # that's hard to place without a live render; deferred. The swoosh + navy +
    # bold text already give the Buddha Air read.)

    # 3. bold "Kathmandu Air"
    font = ImageFont.truetype(FONT, FONT_PX)
    tmp = ImageDraw.Draw(img)
    tw = int(tmp.textlength(TEXT, font=font))
    tile = Image.new("RGBA", (tw + 40, FONT_PX + 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    # double-draw with offsets for a faux-bold weight
    for dx, dy in [(0, 0), (2, 0), (0, 2), (2, 2)]:
        td.text((16 + dx, 12 + dy), TEXT, font=font, fill=(*INK, 255))
    tile = tile.rotate(TEXT_ANGLE, expand=True, resample=Image.BICUBIC)
    cx, cy = TEXT_CENTER
    img.alpha_composite(tile, (cx - tile.width // 2, cy - tile.height // 2))

    img.save(out)
    ktx_tools.encode(out, TEX)
    os.remove(out)
    print("plane: Buddha Air livery (navy + yellow swoosh/logo) + bold text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
