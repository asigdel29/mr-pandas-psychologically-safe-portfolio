"""Re-theme the airplane on the Moving_extras atlas: subtle aging + new text.

Subtle "old rustic" pass (keeps the paper-cutout look):
  * The plane's "Codrops Airways" livery is blue handwriting + light steel-blue
    accent panels, all inside the Actual_Plane UV island
    (NF box ~ x[2566,3994] y[1551,3164]).
  * Aging = desaturate + warm the blue accents toward a faded grey-blue
    (not a full recolor -- user asked for subtle).
  * Text = erase the blue "Codrops Airways" handwriting (replace with the paper
    white it sits on) and re-letter "Kathmandu Air" along the same diagonal.

The "Codrops" text runs diagonally up the fuselage; in atlas space the island
is rotated, so we letter onto a rotated tile and composite it back.

    python3 ../ktx_tools.py decode ../../public/textures/Moving_extras.ktx2 mv_base.png
    python3 age_plane.py mv_base.png mv_painted.png
    python3 ../ktx_tools.py encode mv_painted.png ../../public/textures/Moving_extras.ktx2
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

# Actual_Plane UV island (NF pixels).
PLANE = (2566, 1551, 3994, 3164)

# Aged accent target: faded steel grey-blue.
AGED = np.array([150, 158, 168], dtype=np.float32)

# New livery text (aged ink colour, slightly faded blue-grey).
TEXT = "Kathmandu Air"
TEXT_INK = (96, 110, 130)


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    """Grow a boolean mask by ``radius`` px (square), numpy-only."""
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
            sh[ys, xs] = mask[sy, sx]
            out |= sh
    return out


def _boxblur(mask: np.ndarray, radius: int) -> np.ndarray:
    """Mean filter over a (2*radius+1) window via a summed-area table."""
    pad = np.pad(mask, radius + 1, mode="edge")
    sat = pad.cumsum(0).cumsum(1)
    h, w = mask.shape
    k = 2 * radius + 1
    ys = np.arange(h) + radius + 1
    xs = np.arange(w) + radius + 1
    y0 = ys - radius - 1
    y1 = ys + radius
    x0 = xs - radius - 1
    x1 = xs + radius
    out = (sat[np.ix_(y1, x1)] - sat[np.ix_(y0, x1)]
           - sat[np.ix_(y1, x0)] + sat[np.ix_(y0, x0)])
    return out / (k * k)


def age_plane(in_png: str, out_png: str) -> None:
    img = Image.open(in_png).convert("RGBA")
    arr = np.array(img)
    x0, y0, x1, y1 = PLANE
    sub = arr[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]

    # --- classify blue pixels inside the plane island ---
    blue = (rgb[..., 2] - rgb[..., 0] > 18) & (rgb[..., 2] > 120) & (a > 60)
    # The "Codrops Airways" handwriting sits on the WHITE FUSELAGE, inside an
    # oriented strip running diagonally up the body. The accent panel is the
    # left wedge, OUTSIDE that strip. So: erase every blue pixel that falls in
    # the text strip (catches all the text regardless of stroke thickness),
    # and age the blue everywhere else (the panels).
    # The accent panel is the dense blue WEDGE in the upper-left of the island
    # (local x < 620 AND y < 1250). The "Codrops Airways" handwriting is all the
    # other blue: thin strokes on the white fuselage (lower / right). Erase that.
    hh, ww = blue.shape
    yy, xx = np.mgrid[0:hh, 0:ww]
    wedge = (xx < 640) & (yy < 1300)
    text_blue = blue & ~wedge
    panel_blue = blue & wedge

    # --- erase the old text: fill with the fuselage paper colour ---
    # Sample the actual paper (light, non-blue, opaque pixels on the fuselage)
    # so the patch is invisible, and dilate the text mask a few px to swallow the
    # antialiased halo that otherwise reads as a faint ghost.
    light = (rgb.min(2) > 200) & (a > 120) & ~blue
    paper = (tuple(int(v) for v in np.median(sub[..., :3][light], axis=0))
             if light.any() else (248, 247, 243))
    text_fill = _dilate(text_blue, 4)
    for c in range(3):
        sub[..., c][text_fill] = paper[c]

    # --- age the accent panels: blend toward faded grey-blue ---
    f = 0.55  # blend strength
    panel = sub[..., :3].astype(np.float32)
    for c in range(3):
        chan = panel[..., c]
        chan[panel_blue] = (1 - f) * chan[panel_blue] + f * AGED[c]
    sub[..., :3] = np.clip(panel, 0, 255).astype(np.uint8)
    arr[y0:y1, x0:x1] = sub

    # --- re-letter "Kathmandu Air" along the diagonal of the old text ---
    # Old "Codrops Airways" runs bottom-left -> upper-right at ~ -68 deg in atlas
    # space (reads diagonally up the fuselage). Draw on a tile then rotate.
    tile_w, tile_h = 900, 150
    tile = Image.new("RGBA", (tile_w, tile_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    font = ImageFont.truetype(FONT, 96)
    td.text((6, 18), TEXT, font=font, fill=(*TEXT_INK, 255))
    tile = tile.rotate(68, expand=True, resample=Image.BICUBIC)

    img = Image.fromarray(arr, "RGBA")
    # Anchor near where "Codrops Airways" began (lower-left of the island).
    paste_x = x0 + 30
    paste_y = y0 + 760
    img.alpha_composite(tile, (paste_x, paste_y))

    img.save(out_png)
    print(f"aged plane + '{TEXT}': {in_png} -> {out_png} "
          f"(text px erased: {int(text_blue.sum())}, panels aged: {int(panel_blue.sum())})")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 age_plane.py <in.png> <out.png>")
        return 2
    age_plane(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
