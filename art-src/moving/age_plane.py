"""Re-letter the hanging paper plane on the Moving_extras atlas to "Kathmandu Air".

The plane sits in the LOWER-RIGHT of the 4096x4096 atlas (tail + water-drop
logo at the top, nose at the bottom, three windows down the belly). Its original
livery reads "Kathmandu" (dark blue) + "Airways" (light blue) hand-written
diagonally up the fuselage at ~61 deg. The user wants it to read just
"Kathmandu Air" and nothing else.

So we, within the fuselage text band only:
  1. Erase every bluish midtone ink stroke (both words) -> fill fuselage paper.
     Dark pixels (outline, windows) and bright paper are left untouched.
  2. Letter a single "Kathmandu Air" along the same ~61 deg diagonal in the
     fuselage's own denim-blue ink, centred where the old livery sat.

The water-drop tail logo and the steel-blue accent panels are left alone.

    python3 ../ktx_tools.py decode ../../public/textures/Moving_extras.ktx2 mv_base.png
    python3 age_plane.py mv_base.png mv_painted.png
    python3 ../ktx_tools.py encode mv_painted.png ../../public/textures/Moving_extras.ktx2
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

# The whole plane island (atlas px), clear of the elephant on its left.
PLANE = (2080, 1980, 3030, 3960)

TEXT = "Kathmandu Air"
# The livery's own ink (sampled from the original handwriting): muted denim.
TEXT_INK = (95, 110, 127)
# Fuselage paper (sampled light belly).
PAPER = (222, 222, 222)

# The old "Codrops Airways" ran nearly straight down the fuselage (first letter
# at the top); on the rendered horizontal plane that reads left-to-right. Lay
# "Kathmandu Air" along the same near-vertical path.
TEXT_CENTER = (2892, 2950)
TEXT_ANGLE = -87  # deg CCW; first letter at the top, slight rightward lean
FONT_PX = 66


def _morph(mask: np.ndarray, radius: int, grow: bool) -> np.ndarray:
    """Dilate (grow=True) or erode (grow=False) a boolean mask by ``radius``."""
    out = mask.copy()
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dy == 0 and dx == 0:
                continue
            sh = np.zeros_like(mask)
            ys = slice(max(0, dy), mask.shape[0] + min(0, dy))
            xs = slice(max(0, dx), mask.shape[1] + min(0, dx))
            sy = slice(max(0, -dy), mask.shape[0] + min(0, -dy))
            sx = slice(max(0, -dx), mask.shape[1] + min(0, -dx))
            if grow:
                sh[ys, xs] = mask[sy, sx]
                out |= sh
            else:
                sh[sy, sx] = mask[ys, xs]
                out &= sh
    return out


def age_plane(in_png: str, out_png: str) -> None:
    img = Image.open(in_png).convert("RGBA")
    arr = np.array(img)
    x0, y0, x1, y1 = PLANE
    sub = arr[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]
    lum = rgb.mean(2)

    # --- isolate the handwriting from the solid panels/outline ---
    # bluish strokes (text + steel panels + faint ruling), never the dark
    # outline (lum<80) or bright paper (lum>=200).
    bluish = ((rgb[..., 2] - rgb[..., 0] > 8) & (lum > 80) & (lum < 200)
              & (a > 120))
    # solid accent panels survive an opening; thin handwriting does not.
    panels = _morph(_morph(bluish, 9, False), 9, True)
    text = bluish & ~_morph(panels, 5, True)
    for c in range(3):
        sub[..., c][text] = PAPER[c]
    arr[y0:y1, x0:x1] = sub
    img = Image.fromarray(arr, "RGBA")

    # --- letter "Kathmandu Air" along the fuselage diagonal ---
    font = ImageFont.truetype(FONT, FONT_PX)
    tmp = ImageDraw.Draw(img)
    tw = int(tmp.textlength(TEXT, font=font))
    tile = Image.new("RGBA", (tw + 24, FONT_PX + 28), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((12, 8), TEXT, font=font, fill=(*TEXT_INK, 255))
    tile = tile.rotate(TEXT_ANGLE, expand=True, resample=Image.BICUBIC)
    cx, cy = TEXT_CENTER
    img.alpha_composite(tile, (cx - tile.width // 2, cy - tile.height // 2))

    img.save(out_png)
    print(f"plane -> '{TEXT}': {in_png} -> {out_png} "
          f"(erased {int(text.sum())} ink px)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 age_plane.py <in.png> <out.png>")
        return 2
    age_plane(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
